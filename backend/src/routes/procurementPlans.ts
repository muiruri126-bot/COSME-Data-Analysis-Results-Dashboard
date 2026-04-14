import { Router, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { authenticate, authorize, AuthRequest, hasBroadVisibility } from '../middleware/auth';
import { AppError } from '../middleware/errorHandler';
import { createPlanWithItemsSchema, createPlanHeaderSchema, deriveQuarter, isQuarterConsistent } from '../lib/constants';
import { createAuditLog } from '../lib/audit';
import { Decimal } from '@prisma/client/runtime/library';

export const plansRouter = Router();

// All routes require authentication
plansRouter.use(authenticate);

// GET /api/v1/procurement-plans — List all plans
plansRouter.get('/', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const {
      project_id, status, header_status, fiscal_year, donor_name, search,
      page = '1', limit = '20',
    } = req.query;

    const skip = (Number(page) - 1) * Number(limit);
    const take = Number(limit);

    const where: Record<string, unknown> = { deletedAt: null };
    if (project_id) where.projectId = project_id;
    const effectiveStatus = header_status || status;
    if (effectiveStatus) where.headerStatus = effectiveStatus;
    if (fiscal_year) where.financialYear = fiscal_year;
    if (donor_name) where.donorName = { contains: donor_name as string, mode: 'insensitive' };
    if (search) where.trackingNo = { contains: search as string, mode: 'insensitive' };

    // Role-based data filtering: non-Manager/non-Admin users see only their own plans
    if (!hasBroadVisibility(req.user)) {
      where.OR = [
        { createdBy: req.user!.id },
        { departmentManagerId: req.user!.id },
      ];
    }

    const [plans, total] = await Promise.all([
      prisma.procurementPlanHeader.findMany({
        where: where as any,
        include: {
          project: true,
          departmentManager: { select: { id: true, fullName: true, email: true } },
          fundingSource: true,
          _count: { select: { lineItems: true } },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take,
      }),
      prisma.procurementPlanHeader.count({ where: where as any }),
    ]);

    const results = plans.map((p) => ({
      ...p,
      days_remaining_until_project_end_date: Math.max(
        0,
        Math.ceil((new Date(p.endDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
      ),
    }));

    res.json({
      data: results,
      pagination: { page: Number(page), limit: take, total, totalPages: Math.ceil(total / take) },
    });
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/procurement-plans/:id — Get plan with line items
plansRouter.get('/:id', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const plan = await prisma.procurementPlanHeader.findUnique({
      where: { id: req.params.id as string, deletedAt: null },
      include: {
        project: true,
        departmentManager: { select: { id: true, fullName: true, email: true } },
        fundingSource: true,
        lineItems: {
          where: { deletedAt: null },
          include: {
            location: true,
            materialGroup: true,
            uom: true,
            sourcingMethod: true,
            approvals: {
              include: {
                approver: { select: { id: true, fullName: true } },
              },
              orderBy: { decidedAt: 'desc' },
            },
          },
          orderBy: { lineItemRef: 'asc' },
        },
      },
    });

    if (!plan) throw new AppError('Procurement plan not found', 404);

    // Role-based access: non-Manager/non-Admin can only view their own plans
    if (!hasBroadVisibility(req.user)) {
      if (plan.createdBy !== req.user!.id && plan.departmentManagerId !== req.user!.id) {
        throw new AppError('Insufficient permissions to view this plan', 403);
      }
    }

    // Compute summary
    const statusCounts: Record<string, number> = {};
    plan.lineItems.forEach((li) => {
      statusCounts[li.status] = (statusCounts[li.status] || 0) + 1;
    });

    res.json({
      ...plan,
      days_remaining_until_project_end_date: Math.max(
        0,
        Math.ceil((new Date(plan.endDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
      ),
      line_item_status_summary: statusCounts,
      total_line_items: plan.lineItems.length,
    });
  } catch (err) {
    next(err);
  }
});

// POST /api/v1/procurement-plans — Create plan with line items
plansRouter.post(
  '/',
  authorize('Project/Department Requester', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const parsed = createPlanWithItemsSchema.parse(req.body);

      // Validate quarter consistency for each line item
      for (const item of parsed.line_items) {
        if (!isQuarterConsistent(item.month, item.quarter)) {
          throw new AppError(
            `Line item ${item.line_item_ref}: Quarter ${item.quarter} is inconsistent with month ${item.month}. Expected ${deriveQuarter(item.month)}.`,
            400
          );
        }
      }

      // Check for stock warnings
      const stockWarnings: string[] = [];
      parsed.line_items.forEach((item) => {
        if (item.is_stock_on_hand_available && item.quantity_available >= item.quantity) {
          stockWarnings.push(
            `${item.line_item_ref}: Stock available (${item.quantity_available} of ${item.quantity} needed). Acknowledge before submission.`
          );
        }
      });

      const plan = await prisma.$transaction(async (tx) => {
        const header = await tx.procurementPlanHeader.create({
          data: {
            trackingNo: parsed.tracking_no,
            globalRegionalHub: parsed.global_regional_hub,
            countryOffice: parsed.country_office,
            projectId: parsed.project_id,
            typeOfProcurementPlan: parsed.type_of_procurement_plan,
            departmentManagerId: parsed.department_manager_id,
            fadSpadNumber: parsed.fad_spad_number,
            projectCodeCostCentre: parsed.project_code_cost_centre,
            fundingSourceId: parsed.funding_source_id,
            donorName: parsed.donor_name,
            financialYear: parsed.financial_year,
            currency: parsed.currency,
            startDate: new Date(parsed.start_date),
            endDate: new Date(parsed.end_date),
            headerStatus: 'Draft',
            createdBy: req.user!.id,
          },
        });

        const lineItems = await Promise.all(
          parsed.line_items.map((item) =>
            tx.procurementPlanLineItem.create({
              data: {
                headerId: header.id,
                lineItemRef: item.line_item_ref,
                locationId: item.location_id,
                activityNumber: item.activity_number,
                materialGroupId: item.material_group_id,
                itemDescription: item.item_description,
                uomId: item.uom_id,
                quantity: new Decimal(item.quantity),
                currencyCode: item.currency_code,
                estimatedUnitPrice: new Decimal(item.estimated_unit_price),
                estimatedWarehousingCost: new Decimal(item.estimated_warehousing_cost),
                estimatedTransportCost: new Decimal(item.estimated_transport_cost),
                month: item.month,
                quarter: item.quarter,
                fiscalYear: item.fiscal_year,
                status: 'Draft',
                itemType: item.item_type,
                isStockOnHandAvailable: item.is_stock_on_hand_available,
                quantityAvailable: new Decimal(item.quantity_available),
                createdBy: req.user!.id,
              },
            })
          )
        );

        return { header, lineItems };
      });

      // Create audit logs
      await createAuditLog({
        entityType: 'procurement_plan_header',
        entityId: plan.header.id,
        action: 'CREATE',
        performedBy: req.user!.id,
        ipAddress: req.ip,
      });

      for (const li of plan.lineItems) {
        await createAuditLog({
          entityType: 'line_item',
          entityId: li.id,
          action: 'CREATE',
          performedBy: req.user!.id,
          ipAddress: req.ip,
        });
      }

      res.status(201).json({
        id: plan.header.id,
        tracking_no: plan.header.trackingNo,
        header_status: plan.header.headerStatus,
        days_remaining_until_project_end_date: Math.max(
          0,
          Math.ceil((new Date(plan.header.endDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
        ),
        line_items: plan.lineItems.map((li) => ({
          id: li.id,
          line_item_ref: li.lineItemRef,
          item_description: li.itemDescription,
          estimated_total_item_service_cost: li.estimatedTotalItemServiceCost,
          estimated_total_cost: li.estimatedTotalCost,
          currency_code: li.currencyCode,
          status: li.status,
        })),
        stock_warnings: stockWarnings.length > 0 ? stockWarnings : undefined,
      });
    } catch (err) {
      next(err);
    }
  }
);

// PUT /api/v1/procurement-plans/:id — Update plan header
plansRouter.put(
  '/:id',
  authorize('Project/Department Requester', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const plan = await prisma.procurementPlanHeader.findUnique({
        where: { id: req.params.id as string, deletedAt: null },
      });
      if (!plan) throw new AppError('Procurement plan not found', 404);

      if (plan.headerStatus !== 'Draft' && !req.user!.roles.some((r) => r.roleName === 'System Admin')) {
        throw new AppError('Can only edit header when status is Draft', 403);
      }

      const parsed = createPlanHeaderSchema.partial().parse(req.body);

      const updated = await prisma.procurementPlanHeader.update({
        where: { id: req.params.id as string },
        data: {
          ...(parsed.tracking_no && { trackingNo: parsed.tracking_no }),
          ...(parsed.global_regional_hub !== undefined && { globalRegionalHub: parsed.global_regional_hub }),
          ...(parsed.country_office !== undefined && { countryOffice: parsed.country_office }),
          ...(parsed.project_id && { projectId: parsed.project_id }),
          ...(parsed.type_of_procurement_plan && { typeOfProcurementPlan: parsed.type_of_procurement_plan }),
          ...(parsed.department_manager_id && { departmentManagerId: parsed.department_manager_id }),
          ...(parsed.fad_spad_number !== undefined && { fadSpadNumber: parsed.fad_spad_number }),
          ...(parsed.project_code_cost_centre && { projectCodeCostCentre: parsed.project_code_cost_centre }),
          ...(parsed.funding_source_id && { fundingSourceId: parsed.funding_source_id }),
          ...(parsed.donor_name !== undefined && { donorName: parsed.donor_name }),
          ...(parsed.financial_year !== undefined && { financialYear: parsed.financial_year }),
          ...(parsed.currency !== undefined && { currency: parsed.currency }),
          ...(parsed.start_date && { startDate: new Date(parsed.start_date) }),
          ...(parsed.end_date && { endDate: new Date(parsed.end_date) }),
        },
      });

      await createAuditLog({
        entityType: 'procurement_plan_header',
        entityId: updated.id,
        action: 'UPDATE',
        performedBy: req.user!.id,
        ipAddress: req.ip,
      });

      res.json(updated);
    } catch (err) {
      next(err);
    }
  }
);

// DELETE /api/v1/procurement-plans/:id — Soft delete
plansRouter.delete(
  '/:id',
  authorize('System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const planId = req.params.id as string;
      const plan = await prisma.procurementPlanHeader.findUnique({
        where: { id: planId, deletedAt: null },
      });
      if (!plan) throw new AppError('Procurement plan not found', 404);

      await prisma.$transaction([
        prisma.procurementPlanHeader.update({
          where: { id: planId },
          data: { deletedAt: new Date() },
        }),
        prisma.procurementPlanLineItem.updateMany({
          where: { headerId: planId },
          data: { deletedAt: new Date() },
        }),
      ]);

      await createAuditLog({
        entityType: 'procurement_plan_header',
        entityId: planId,
        action: 'DELETE',
        performedBy: req.user!.id,
        ipAddress: req.ip,
      });

      res.json({ message: 'Procurement plan soft-deleted' });
    } catch (err) {
      next(err);
    }
  }
);
