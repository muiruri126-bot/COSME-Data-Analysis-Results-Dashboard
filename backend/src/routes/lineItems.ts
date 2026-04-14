import { Router, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { AppError } from '../middleware/errorHandler';
import { createLineItemSchema, deriveQuarter, isQuarterConsistent, canTransition, LineItemStatus } from '../lib/constants';
import { createAuditLog, createAuditLogForUpdate } from '../lib/audit';
import { notifySubmitted } from '../lib/notifications';
import { Decimal } from '@prisma/client/runtime/library';

export const lineItemsRouter = Router();
lineItemsRouter.use(authenticate);

// POST /api/v1/procurement-plans/:planId/line-items — Add line item(s)
lineItemsRouter.post(
  '/plan/:planId',
  authorize('Project/Department Requester', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const plan = await prisma.procurementPlanHeader.findUnique({
        where: { id: req.params.planId as string, deletedAt: null },
      });
      if (!plan) throw new AppError('Procurement plan not found', 404);

      const items = Array.isArray(req.body) ? req.body : [req.body];
      const results = [];

      for (const raw of items) {
        const parsed = createLineItemSchema.parse(raw);

        if (!isQuarterConsistent(parsed.month, parsed.quarter)) {
          throw new AppError(
            `Line item ${parsed.line_item_ref}: Quarter ${parsed.quarter} is inconsistent with month ${parsed.month}. Expected ${deriveQuarter(parsed.month)}.`,
            400
          );
        }

        const li = await prisma.procurementPlanLineItem.create({
          data: {
            headerId: plan.id,
            lineItemRef: parsed.line_item_ref,
            locationId: parsed.location_id,
            activityNumber: parsed.activity_number,
            materialGroupId: parsed.material_group_id,
            itemDescription: parsed.item_description,
            uomId: parsed.uom_id,
            quantity: new Decimal(parsed.quantity),
            currencyCode: parsed.currency_code,
            estimatedUnitPrice: new Decimal(parsed.estimated_unit_price),
            estimatedWarehousingCost: new Decimal(parsed.estimated_warehousing_cost),
            estimatedTransportCost: new Decimal(parsed.estimated_transport_cost),
            month: parsed.month,
            quarter: parsed.quarter,
            fiscalYear: parsed.fiscal_year,
            status: 'Draft',
            itemType: parsed.item_type,
            isStockOnHandAvailable: parsed.is_stock_on_hand_available,
            quantityAvailable: new Decimal(parsed.quantity_available),
            createdBy: req.user!.id,
          },
        });

        await createAuditLog({
          entityType: 'line_item',
          entityId: li.id,
          action: 'CREATE',
          performedBy: req.user!.id,
          ipAddress: req.ip,
        });

        results.push(li);
      }

      res.status(201).json({ line_items: results });
    } catch (err) {
      next(err);
    }
  }
);

// GET /api/v1/line-items/approved — List approved line items available for PR
lineItemsRouter.get('/approved/available', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const items = await prisma.procurementPlanLineItem.findMany({
      where: { status: 'Approved', deletedAt: null },
      select: {
        id: true,
        lineItemRef: true,
        itemDescription: true,
        estimatedTotalCost: true,
        currencyCode: true,
        header: { select: { trackingNo: true } },
        location: { select: { locationName: true } },
      },
      orderBy: { lineItemRef: 'asc' },
    });
    res.json(items);
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/line-items/:id — Get single line item
lineItemsRouter.get('/:id', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const li = await prisma.procurementPlanLineItem.findUnique({
      where: { id: req.params.id as string, deletedAt: null },
      include: {
        header: {
          include: {
            project: true,
            departmentManager: { select: { id: true, fullName: true, email: true } },
            fundingSource: true,
          },
        },
        location: true,
        materialGroup: true,
        uom: true,
        sourcingMethod: true,
        approvals: {
          include: {
            approver: { select: { id: true, fullName: true } },
            step: true,
          },
          orderBy: { decidedAt: 'desc' },
        },
        prLineItems: {
          include: { pr: true },
        },
        deliveries: {
          orderBy: { deliveryDate: 'desc' },
        },
      },
    });

    if (!li) throw new AppError('Line item not found', 404);

    const daysRemaining = Math.max(
      0,
      Math.ceil((new Date(li.header.endDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    );

    const isOverdue =
      li.estimatedDeliveryDate &&
      new Date(li.estimatedDeliveryDate) < new Date() &&
      !['Delivered/Closed', 'Cancelled'].includes(li.status);

    const daysOverdue = isOverdue
      ? Math.ceil((Date.now() - new Date(li.estimatedDeliveryDate!).getTime()) / (1000 * 60 * 60 * 24))
      : 0;

    const deliveryPercentage = Number(li.quantity) > 0
      ? Math.round((Number(li.deliveredQuantity) / Number(li.quantity)) * 1000) / 10
      : 0;

    res.json({
      ...li,
      days_remaining_until_project_end_date: daysRemaining,
      is_overdue: !!isOverdue,
      days_overdue: daysOverdue,
      delivery_percentage: deliveryPercentage,
    });
  } catch (err) {
    next(err);
  }
});

// PUT /api/v1/line-items/:id — Update line item
lineItemsRouter.put('/:id', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const li = await prisma.procurementPlanLineItem.findUnique({
      where: { id: req.params.id as string, deletedAt: null },
    });
    if (!li) throw new AppError('Line item not found', 404);

    const userRoles = req.user!.roles.map((r) => r.roleName);
    const isAdmin = userRoles.includes('System Admin');

    // Field-level permission enforcement
    const planningFields = [
      'item_description', 'quantity', 'estimated_unit_price', 'estimated_warehousing_cost',
      'estimated_transport_cost', 'location_id', 'activity_number', 'material_group_id',
      'uom_id', 'month', 'quarter', 'fiscal_year', 'item_type',
      'is_stock_on_hand_available', 'quantity_available',
    ];
    const supplyChainFields = [
      'pr_number', 'pr_submitted_date', 'estimated_delivery_date', 'sourcing_location',
      'sourcing_method_id', 'lta_reference_number', 'estimated_delivery_needed',
      'sourcing_plan', 'actual_delivery_date', 'stock_on_hand_asset_post',
    ];

    const requestFields = Object.keys(req.body);

    if (!isAdmin) {
      if (userRoles.includes('Project/Department Requester')) {
        if (!['Draft', 'Returned for Correction'].includes(li.status)) {
          throw new AppError('Can only edit planning fields when item is Draft or Returned for Correction', 403);
        }
        const forbidden = requestFields.filter((f) => !planningFields.includes(f));
        if (forbidden.length > 0) {
          throw new AppError(`Cannot edit fields: ${forbidden.join(', ')}`, 403);
        }
      } else if (userRoles.includes('Supply Chain Officer')) {
        if (!['Approved', 'PR Raised', 'Sourcing', 'Ordered/Contracted', 'Delivery In Progress'].includes(li.status)) {
          throw new AppError('Can only edit supply chain fields when item is Approved or beyond', 403);
        }
        const forbidden = requestFields.filter((f) => !supplyChainFields.includes(f));
        if (forbidden.length > 0) {
          throw new AppError(`Cannot edit fields: ${forbidden.join(', ')}`, 403);
        }
      } else if (!userRoles.includes('Stores/Inventory Officer')) {
        throw new AppError('Insufficient permissions to edit this item', 403);
      }
    }

    // Build update data
    const data: Record<string, unknown> = {};

    if (req.body.item_description !== undefined) data.itemDescription = req.body.item_description;
    if (req.body.location_id !== undefined) data.locationId = req.body.location_id;
    if (req.body.activity_number !== undefined) data.activityNumber = req.body.activity_number;
    if (req.body.material_group_id !== undefined) data.materialGroupId = req.body.material_group_id;
    if (req.body.uom_id !== undefined) data.uomId = req.body.uom_id;
    if (req.body.month !== undefined) data.month = req.body.month;
    if (req.body.quarter !== undefined) data.quarter = req.body.quarter;
    if (req.body.fiscal_year !== undefined) data.fiscalYear = req.body.fiscal_year;
    if (req.body.item_type !== undefined) data.itemType = req.body.item_type;
    if (req.body.is_stock_on_hand_available !== undefined) data.isStockOnHandAvailable = req.body.is_stock_on_hand_available;

    if (req.body.quantity !== undefined) {
      if (req.body.quantity <= 0) throw new AppError('Quantity must be positive', 400);
      data.quantity = new Decimal(req.body.quantity);
    }
    if (req.body.estimated_unit_price !== undefined) {
      if (req.body.estimated_unit_price < 0) throw new AppError('Estimated unit price cannot be negative', 400);
      data.estimatedUnitPrice = new Decimal(req.body.estimated_unit_price);
    }
    if (req.body.estimated_warehousing_cost !== undefined) {
      if (req.body.estimated_warehousing_cost < 0) throw new AppError('Warehousing cost cannot be negative', 400);
      data.estimatedWarehousingCost = new Decimal(req.body.estimated_warehousing_cost);
    }
    if (req.body.estimated_transport_cost !== undefined) {
      if (req.body.estimated_transport_cost < 0) throw new AppError('Transport cost cannot be negative', 400);
      data.estimatedTransportCost = new Decimal(req.body.estimated_transport_cost);
    }
    if (req.body.quantity_available !== undefined) {
      if (req.body.quantity_available < 0) throw new AppError('Quantity available cannot be negative', 400);
      data.quantityAvailable = new Decimal(req.body.quantity_available);
    }

    // estimatedTotalItemServiceCost and estimatedTotalCost are DB-generated columns
    // They are computed automatically by PostgreSQL — do not set them explicitly

    // Supply chain fields
    if (req.body.pr_number !== undefined) data.prNumber = req.body.pr_number;
    if (req.body.pr_submitted_date !== undefined) data.prSubmittedDate = req.body.pr_submitted_date ? new Date(req.body.pr_submitted_date) : null;
    if (req.body.estimated_delivery_date !== undefined) data.estimatedDeliveryDate = req.body.estimated_delivery_date ? new Date(req.body.estimated_delivery_date) : null;
    if (req.body.sourcing_location !== undefined) data.sourcingLocation = req.body.sourcing_location;
    if (req.body.sourcing_method_id !== undefined) data.sourcingMethodId = req.body.sourcing_method_id;
    if (req.body.lta_reference_number !== undefined) data.ltaReferenceNumber = req.body.lta_reference_number;
    if (req.body.estimated_delivery_needed !== undefined) data.estimatedDeliveryNeeded = req.body.estimated_delivery_needed;
    if (req.body.sourcing_plan !== undefined) data.sourcingPlan = req.body.sourcing_plan;
    if (req.body.actual_delivery_date !== undefined) data.actualDeliveryDate = req.body.actual_delivery_date ? new Date(req.body.actual_delivery_date) : null;
    if (req.body.stock_on_hand_asset_post !== undefined) data.stockOnHandAssetPost = req.body.stock_on_hand_asset_post;

    // Validate quarter consistency
    const month = (data.month as number) || li.month;
    const quarter = (data.quarter as string) || li.quarter;
    if (!isQuarterConsistent(month, quarter)) {
      throw new AppError(`Quarter ${quarter} is inconsistent with month ${month}. Expected ${deriveQuarter(month)}.`, 400);
    }

    const updated = await prisma.procurementPlanLineItem.update({
      where: { id: req.params.id as string },
      data: data as any,
    });

    await createAuditLog({
      entityType: 'line_item',
      entityId: updated.id,
      action: 'UPDATE',
      performedBy: req.user!.id,
      ipAddress: req.ip,
    });

    res.json(updated);
  } catch (err) {
    next(err);
  }
});

// POST /api/v1/line-items/:id/submit — Submit for approval
lineItemsRouter.post(
  '/:id/submit',
  authorize('Project/Department Requester', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const li = await prisma.procurementPlanLineItem.findUnique({
        where: { id: req.params.id as string, deletedAt: null },
        include: { header: true },
      });
      if (!li) throw new AppError('Line item not found', 404);

      const userRoles = req.user!.roles.map((r) => r.roleName);
      if (!canTransition(li.status as LineItemStatus, 'Submitted for Approval', userRoles)) {
        throw new AppError(`Cannot transition from ${li.status} to Submitted for Approval`, 403);
      }

      // Stock check warning
      if (li.isStockOnHandAvailable && Number(li.quantityAvailable) >= Number(li.quantity)) {
        if (!req.body.stock_acknowledged) {
          throw new AppError(
            `Stock available (${li.quantityAvailable} of ${li.quantity} needed). Set stock_acknowledged=true to proceed.`,
            400
          );
        }
      }

      const updated = await prisma.procurementPlanLineItem.update({
        where: { id: req.params.id as string },
        data: {
          status: 'Submitted for Approval',
          statusChangedAt: new Date(),
        },
      });

      await createAuditLog({
        entityType: 'line_item',
        entityId: li.id,
        action: 'STATUS_CHANGE',
        fieldName: 'status',
        oldValue: li.status,
        newValue: 'Submitted for Approval',
        performedBy: req.user!.id,
        ipAddress: req.ip,
      });

      // Notify department manager
      notifySubmitted({
        lineItemId: li.id,
        lineItemRef: li.lineItemRef,
        headerId: li.headerId,
        submittedBy: req.user!.fullName,
        departmentManagerId: li.header.departmentManagerId,
      }).catch(() => {});

      // Find pending approvers
      const approvalRule = await findApplicableRule(li);
      const pendingSteps = approvalRule
        ? await prisma.lineItemApprovalStep.findMany({
            where: { ruleId: approvalRule.id },
            include: { approverRole: true, specificApprover: true },
            orderBy: { stepOrder: 'asc' },
          })
        : [];

      res.json({
        id: updated.id,
        line_item_ref: updated.lineItemRef,
        status: updated.status,
        submitted_at: updated.statusChangedAt,
        submitted_by: req.user!.fullName,
        pending_approvers: pendingSteps.map((s) => ({
          step: s.stepOrder,
          role: s.approverRole?.roleName,
          approver: s.specificApprover?.fullName,
        })),
      });
    } catch (err) {
      next(err);
    }
  }
);

// POST /api/v1/line-items/bulk-submit — Bulk submit
lineItemsRouter.post(
  '/bulk-submit',
  authorize('Project/Department Requester', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const { line_item_ids, stock_acknowledged } = req.body;
      if (!Array.isArray(line_item_ids) || line_item_ids.length === 0) {
        throw new AppError('line_item_ids array is required', 400);
      }

      const results = [];
      const errors = [];

      for (const id of line_item_ids) {
        try {
          const li = await prisma.procurementPlanLineItem.findUnique({
            where: { id, deletedAt: null },
          });
          if (!li) { errors.push({ id, error: 'Not found' }); continue; }

          const userRoles = req.user!.roles.map((r) => r.roleName);
          if (!canTransition(li.status as LineItemStatus, 'Submitted for Approval', userRoles)) {
            errors.push({ id, ref: li.lineItemRef, error: `Cannot submit from status ${li.status}` });
            continue;
          }

          if (li.isStockOnHandAvailable && Number(li.quantityAvailable) >= Number(li.quantity) && !stock_acknowledged) {
            errors.push({ id, ref: li.lineItemRef, error: 'Stock available - acknowledge required' });
            continue;
          }

          await prisma.procurementPlanLineItem.update({
            where: { id },
            data: { status: 'Submitted for Approval', statusChangedAt: new Date() },
          });

          await createAuditLog({
            entityType: 'line_item',
            entityId: id,
            action: 'STATUS_CHANGE',
            fieldName: 'status',
            oldValue: li.status,
            newValue: 'Submitted for Approval',
            performedBy: req.user!.id,
          });

          // Notify manager
          const header = await prisma.procurementPlanHeader.findUnique({ where: { id: li.headerId }, select: { departmentManagerId: true } });
          if (header) {
            notifySubmitted({
              lineItemId: id,
              lineItemRef: li.lineItemRef,
              headerId: li.headerId,
              submittedBy: req.user!.fullName,
              departmentManagerId: header.departmentManagerId,
            }).catch(() => {});
          }

          results.push({ id, ref: li.lineItemRef, status: 'Submitted for Approval' });
        } catch (e: any) {
          errors.push({ id, error: e.message });
        }
      }

      res.json({ submitted: results, errors });
    } catch (err) {
      next(err);
    }
  }
);

// DELETE /api/v1/line-items/:id — Soft delete
lineItemsRouter.delete(
  '/:id',
  authorize('System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const itemId = req.params.id as string;
      await prisma.procurementPlanLineItem.update({
        where: { id: itemId },
        data: { deletedAt: new Date() },
      });

      await createAuditLog({
        entityType: 'line_item',
        entityId: itemId,
        action: 'DELETE',
        performedBy: req.user!.id,
      });

      res.json({ message: 'Line item soft-deleted' });
    } catch (err) {
      next(err);
    }
  }
);

// Helper: Find applicable approval rule for a line item
async function findApplicableRule(li: any) {
  const rules = await prisma.lineItemApprovalRule.findMany({
    where: { isActive: true },
    orderBy: { priority: 'desc' },
  });

  for (const rule of rules) {
    let matches = true;

    if (rule.costThresholdMin && rule.costThresholdCurrency === li.currencyCode) {
      if (Number(li.estimatedTotalCost) < Number(rule.costThresholdMin)) matches = false;
    }
    if (rule.costThresholdMax && rule.costThresholdCurrency === li.currencyCode) {
      if (Number(li.estimatedTotalCost) > Number(rule.costThresholdMax)) matches = false;
    }
    if (rule.itemType && rule.itemType !== li.itemType) matches = false;
    if (rule.sourcingMethodId && rule.sourcingMethodId !== li.sourcingMethodId) matches = false;
    if (rule.materialGroupId && rule.materialGroupId !== li.materialGroupId) matches = false;
    if (rule.locationId && rule.locationId !== li.locationId) matches = false;

    if (matches) return rule;
  }

  return null;
}
