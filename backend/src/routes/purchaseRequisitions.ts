import { Router, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { AppError } from '../middleware/errorHandler';
import { createPRSchema, updateSourcingSchema, canTransition, LineItemStatus } from '../lib/constants';
import { createAuditLog } from '../lib/audit';
import { notifyPRRaised } from '../lib/notifications';

export const purchaseRequisitionsRouter = Router();
purchaseRequisitionsRouter.use(authenticate);

// POST /api/v1/purchase-requisitions — Create PR linked to line items
purchaseRequisitionsRouter.post(
  '/',
  authorize('Supply Chain Officer', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const parsed = createPRSchema.parse(req.body);

      // Validate all line items are in Approved status
      const lineItems = await prisma.procurementPlanLineItem.findMany({
        where: { id: { in: parsed.line_item_ids }, deletedAt: null },
      });

      if (lineItems.length !== parsed.line_item_ids.length) {
        throw new AppError('One or more line items not found', 404);
      }

      const notApproved = lineItems.filter((li) => li.status !== 'Approved');
      if (notApproved.length > 0) {
        throw new AppError(
          `Cannot raise PR: the following items are not Approved: ${notApproved.map((li) => li.lineItemRef).join(', ')}`,
          400
        );
      }

      const result = await prisma.$transaction(async (tx) => {
        // Create PR
        const pr = await tx.purchaseRequisition.create({
          data: {
            prNumber: parsed.pr_number,
            submittedDate: new Date(parsed.submitted_date),
            submittedBy: req.user!.id,
            notes: parsed.notes,
            status: 'Open',
          },
        });

        // Link line items via join table
        await tx.prLineItem.createMany({
          data: parsed.line_item_ids.map((liId) => ({
            prId: pr.id,
            lineItemId: liId,
          })),
        });

        // Update line item statuses to "PR Raised"
        await tx.procurementPlanLineItem.updateMany({
          where: { id: { in: parsed.line_item_ids } },
          data: {
            status: 'PR Raised',
            statusChangedAt: new Date(),
            prNumber: parsed.pr_number,
            prSubmittedDate: new Date(parsed.submitted_date),
          },
        });

        return pr;
      });

      // Audit logs
      await createAuditLog({
        entityType: 'purchase_requisition',
        entityId: result.id,
        action: 'CREATE',
        performedBy: req.user!.id,
        ipAddress: req.ip,
      });

      for (const liId of parsed.line_item_ids) {
        await createAuditLog({
          entityType: 'line_item',
          entityId: liId,
          action: 'STATUS_CHANGE',
          fieldName: 'status',
          oldValue: 'Approved',
          newValue: 'PR Raised',
          performedBy: req.user!.id,
        });
      }

      // Notify plan creators about PR raised
      const prLineItems = await prisma.procurementPlanLineItem.findMany({
        where: { id: { in: parsed.line_item_ids } },
        select: { id: true, lineItemRef: true, headerId: true, createdBy: true, status: true },
      });
      for (const pli of prLineItems) {
        notifyPRRaised({
          lineItemId: pli.id,
          lineItemRef: pli.lineItemRef,
          headerId: pli.headerId,
          createdById: pli.createdBy,
          prNumber: parsed.pr_number,
        }).catch(() => {});
      }

      // Fetch linked items for response
      const linkedItems = prLineItems;

      res.status(201).json({
        id: result.id,
        pr_number: result.prNumber,
        submitted_date: result.submittedDate,
        status: result.status,
        linked_line_items: linkedItems.map((li) => ({
          id: li.id,
          ref: li.lineItemRef,
          status: li.status,
        })),
      });
    } catch (err) {
      next(err);
    }
  }
);

// GET /api/v1/purchase-requisitions — List PRs (Supply Chain, Admin only)
purchaseRequisitionsRouter.get(
  '/',
  authorize('Supply Chain Officer', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { status, page = '1', limit = '20' } = req.query;
    const skip = (Number(page) - 1) * Number(limit);
    const take = Number(limit);

    const where: Record<string, unknown> = {};
    if (status) where.status = status;

    const [prs, total] = await Promise.all([
      prisma.purchaseRequisition.findMany({
        where: where as any,
        include: {
          submitter: { select: { id: true, fullName: true } },
          prLineItems: {
            include: {
              lineItem: {
                select: { id: true, lineItemRef: true, itemDescription: true, status: true, estimatedTotalCost: true, currencyCode: true },
              },
            },
          },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take,
      }),
      prisma.purchaseRequisition.count({ where: where as any }),
    ]);

    res.json({
      data: prs,
      pagination: { page: Number(page), limit: take, total, totalPages: Math.ceil(total / take) },
    });
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/purchase-requisitions/:id
purchaseRequisitionsRouter.get('/:id', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const pr = await prisma.purchaseRequisition.findUnique({
      where: { id: req.params.id as string },
      include: {
        submitter: { select: { id: true, fullName: true, email: true } },
        prLineItems: {
          include: {
            lineItem: {
              include: {
                location: true,
                materialGroup: true,
                sourcingMethod: true,
              },
            },
          },
        },
      },
    });
    if (!pr) throw new AppError('Purchase requisition not found', 404);
    res.json(pr);
  } catch (err) {
    next(err);
  }
});

// PUT /api/v1/purchase-requisitions/:id/sourcing — Update sourcing details
purchaseRequisitionsRouter.put(
  '/:id/sourcing',
  authorize('Supply Chain Officer', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const pr = await prisma.purchaseRequisition.findUnique({ where: { id: req.params.id as string } });
      if (!pr) throw new AppError('Purchase requisition not found', 404);

      const parsed = updateSourcingSchema.parse(req.body);

      const updatedItems = [];

      for (const item of parsed.line_items) {
        const li = await prisma.procurementPlanLineItem.findUnique({
          where: { id: item.line_item_id, deletedAt: null },
        });
        if (!li) throw new AppError(`Line item ${item.line_item_id} not found`, 404);

        const data: Record<string, unknown> = {};
        if (item.sourcing_method_id) data.sourcingMethodId = item.sourcing_method_id;
        if (item.lta_reference_number !== undefined) data.ltaReferenceNumber = item.lta_reference_number;
        if (item.sourcing_location !== undefined) data.sourcingLocation = item.sourcing_location;
        if (item.sourcing_plan !== undefined) data.sourcingPlan = item.sourcing_plan;
        if (item.estimated_delivery_date) data.estimatedDeliveryDate = new Date(item.estimated_delivery_date);

        // Status transition if requested
        if (item.status) {
          const userRoles = req.user!.roles.map((r) => r.roleName);
          if (!canTransition(li.status as LineItemStatus, item.status as LineItemStatus, userRoles)) {
            throw new AppError(`Cannot transition ${li.lineItemRef} from ${li.status} to ${item.status}`, 400);
          }
          data.status = item.status;
          data.statusChangedAt = new Date();
        }

        const updated = await prisma.procurementPlanLineItem.update({
          where: { id: item.line_item_id },
          data: data as any,
          include: { sourcingMethod: true },
        });

        await createAuditLog({
          entityType: 'line_item',
          entityId: item.line_item_id,
          action: item.status ? 'STATUS_CHANGE' : 'UPDATE',
          performedBy: req.user!.id,
        });

        updatedItems.push({
          id: updated.id,
          ref: updated.lineItemRef,
          status: updated.status,
          sourcing_method: updated.sourcingMethod?.methodName,
          lta_reference_number: updated.ltaReferenceNumber,
        });
      }

      res.json({
        pr_number: pr.prNumber,
        updated_items: updatedItems,
      });
    } catch (err) {
      next(err);
    }
  }
);
