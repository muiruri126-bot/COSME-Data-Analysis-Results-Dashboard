import { Router, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { AppError } from '../middleware/errorHandler';
import { approvalActionSchema, returnActionSchema, cancelActionSchema, canTransition, LineItemStatus } from '../lib/constants';
import { createAuditLog } from '../lib/audit';
import { notifyApproved, notifyReturned, notifyCancelled } from '../lib/notifications';

export const approvalsRouter = Router();
approvalsRouter.use(authenticate);

// POST /api/v1/line-items/:id/approve
approvalsRouter.post(
  '/:id/approve',
  authorize('Project/Department Manager', 'Finance/Grants'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const li = await prisma.procurementPlanLineItem.findUnique({
        where: { id: req.params.id as string, deletedAt: null },
        include: { header: true },
      });
      if (!li) throw new AppError('Line item not found', 404);

      const userRoles = req.user!.roles.map((r) => r.roleName);
      if (!canTransition(li.status as LineItemStatus, 'Approved', userRoles)) {
        throw new AppError(`Cannot approve item in status ${li.status}`, 403);
      }

      const parsed = approvalActionSchema.parse(req.body);

      // Find the applicable approval rule and step
      const step = await findNextApprovalStep(li);
      if (!step) throw new AppError('No approval step configured for this item', 400);

      // Record approval decision (append-only)
      const approval = await prisma.lineItemApproval.create({
        data: {
          lineItemId: li.id,
          stepId: step.id,
          approverId: req.user!.id,
          decision: 'Approved',
          comments: parsed.comment,
        },
      });

      // Check if all steps are completed
      const allStepsCompleted = await areAllStepsCompleted(li.id, step.ruleId);

      if (allStepsCompleted) {
        await prisma.procurementPlanLineItem.update({
          where: { id: li.id },
          data: { status: 'Approved', statusChangedAt: new Date() },
        });
      }

      await createAuditLog({
        entityType: 'line_item',
        entityId: li.id,
        action: 'APPROVAL',
        fieldName: 'status',
        oldValue: li.status,
        newValue: allStepsCompleted ? 'Approved' : li.status,
        performedBy: req.user!.id,
        ipAddress: req.ip,
      });

      // Notify requester when fully approved
      if (allStepsCompleted) {
        notifyApproved({
          lineItemId: li.id,
          lineItemRef: li.lineItemRef,
          headerId: li.headerId,
          approvedBy: req.user!.fullName,
          createdById: li.createdBy,
          comment: parsed.comment,
        }).catch(() => {});
      }

      res.json({
        id: li.id,
        line_item_ref: li.lineItemRef,
        status: allStepsCompleted ? 'Approved' : li.status,
        approval: {
          id: approval.id,
          step: step.stepOrder,
          approver: req.user!.fullName,
          decision: 'Approved',
          decided_at: approval.decidedAt,
          comment: parsed.comment,
        },
        all_steps_completed: allStepsCompleted,
      });
    } catch (err) {
      next(err);
    }
  }
);

// POST /api/v1/line-items/:id/return
approvalsRouter.post(
  '/:id/return',
  authorize('Project/Department Manager', 'Supply Chain Officer', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const li = await prisma.procurementPlanLineItem.findUnique({
        where: { id: req.params.id as string, deletedAt: null },
      });
      if (!li) throw new AppError('Line item not found', 404);

      const userRoles = req.user!.roles.map((r) => r.roleName);
      if (!canTransition(li.status as LineItemStatus, 'Returned for Correction', userRoles)) {
        throw new AppError(`Cannot return item in status ${li.status}`, 403);
      }

      const parsed = returnActionSchema.parse(req.body);

      const step = await findNextApprovalStep(li);
      if (!step) throw new AppError('No approval step configured for this item', 400);

      const approval = await prisma.lineItemApproval.create({
        data: {
          lineItemId: li.id,
          stepId: step.id,
          approverId: req.user!.id,
          decision: 'Returned',
          comments: parsed.comment,
        },
      });

      await prisma.procurementPlanLineItem.update({
        where: { id: li.id },
        data: { status: 'Returned for Correction', statusChangedAt: new Date() },
      });

      await createAuditLog({
        entityType: 'line_item',
        entityId: li.id,
        action: 'APPROVAL',
        fieldName: 'status',
        oldValue: li.status,
        newValue: 'Returned for Correction',
        performedBy: req.user!.id,
      });

      // Notify requester
      notifyReturned({
        lineItemId: li.id,
        lineItemRef: li.lineItemRef,
        headerId: li.headerId,
        returnedBy: req.user!.fullName,
        createdById: li.createdBy,
        comment: parsed.comment,
      }).catch(() => {});

      res.json({
        id: li.id,
        line_item_ref: li.lineItemRef,
        status: 'Returned for Correction',
        approval: {
          id: approval.id,
          approver: req.user!.fullName,
          decision: 'Returned',
          decided_at: approval.decidedAt,
          comment: parsed.comment,
        },
      });
    } catch (err) {
      next(err);
    }
  }
);

// POST /api/v1/line-items/:id/cancel
approvalsRouter.post(
  '/:id/cancel',
  authorize('Project/Department Manager', 'Supply Chain Officer', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const li = await prisma.procurementPlanLineItem.findUnique({
        where: { id: req.params.id as string, deletedAt: null },
      });
      if (!li) throw new AppError('Line item not found', 404);

      if (['Delivered/Closed', 'Cancelled'].includes(li.status)) {
        throw new AppError(`Cannot cancel item in status ${li.status}`, 400);
      }

      const parsed = cancelActionSchema.parse(req.body);

      const step = await findNextApprovalStep(li);
      if (!step) throw new AppError('No approval step configured for this item', 400);

      await prisma.lineItemApproval.create({
        data: {
          lineItemId: li.id,
          stepId: step.id,
          approverId: req.user!.id,
          decision: 'Cancelled',
          comments: parsed.reason,
        },
      });

      await prisma.procurementPlanLineItem.update({
        where: { id: li.id },
        data: {
          status: 'Cancelled',
          statusChangedAt: new Date(),
          cancellationReason: parsed.reason,
        },
      });

      await createAuditLog({
        entityType: 'line_item',
        entityId: li.id,
        action: 'STATUS_CHANGE',
        fieldName: 'status',
        oldValue: li.status,
        newValue: 'Cancelled',
        performedBy: req.user!.id,
      });

      // Notify requester
      notifyCancelled({
        lineItemId: li.id,
        lineItemRef: li.lineItemRef,
        headerId: li.headerId,
        cancelledBy: req.user!.fullName,
        createdById: li.createdBy,
        reason: parsed.reason,
      }).catch(() => {});

      res.json({
        id: li.id,
        line_item_ref: li.lineItemRef,
        status: 'Cancelled',
        cancellation_reason: parsed.reason,
      });
    } catch (err) {
      next(err);
    }
  }
);

// POST /api/v1/line-items/:id/delegate
approvalsRouter.post(
  '/:id/delegate',
  authorize('Project/Department Manager', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const { delegate_to_id, comment } = req.body;
      if (!delegate_to_id) throw new AppError('delegate_to_id is required', 400);

      const li = await prisma.procurementPlanLineItem.findUnique({
        where: { id: req.params.id as string, deletedAt: null },
      });
      if (!li) throw new AppError('Line item not found', 404);

      if (li.status !== 'Submitted for Approval') {
        throw new AppError('Can only delegate items pending approval', 400);
      }

      const delegate = await prisma.user.findUnique({ where: { id: delegate_to_id, isActive: true } });
      if (!delegate) throw new AppError('Delegate user not found', 404);

      const step = await findNextApprovalStep(li);
      if (!step) throw new AppError('No approval step configured for this item', 400);

      await prisma.lineItemApproval.create({
        data: {
          lineItemId: li.id,
          stepId: step.id,
          approverId: delegate_to_id,
          delegatedFromId: req.user!.id,
          decision: 'Escalated',
          comments: comment || `Delegated from ${req.user!.fullName}`,
        },
      });

      await createAuditLog({
        entityType: 'line_item',
        entityId: li.id,
        action: 'APPROVAL',
        fieldName: 'delegation',
        oldValue: req.user!.id,
        newValue: delegate_to_id,
        performedBy: req.user!.id,
      });

      res.json({
        id: li.id,
        line_item_ref: li.lineItemRef,
        delegated_to: delegate.fullName,
        delegated_from: req.user!.fullName,
      });
    } catch (err) {
      next(err);
    }
  }
);

// POST /api/v1/line-items/bulk-approve
approvalsRouter.post(
  '/bulk-approve',
  authorize('Project/Department Manager'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const { line_item_ids, comment } = req.body;
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
          if (!canTransition(li.status as LineItemStatus, 'Approved', userRoles)) {
            errors.push({ id, ref: li.lineItemRef, error: `Cannot approve from status ${li.status}` });
            continue;
          }

          const step = await findNextApprovalStep(li);
          if (!step) { errors.push({ id, ref: li.lineItemRef, error: 'No approval step configured' }); continue; }

          await prisma.lineItemApproval.create({
            data: {
              lineItemId: li.id,
              stepId: step.id,
              approverId: req.user!.id,
              decision: 'Approved',
              comments: comment,
            },
          });

          const allDone = await areAllStepsCompleted(li.id, step.ruleId);
          if (allDone) {
            await prisma.procurementPlanLineItem.update({
              where: { id },
              data: { status: 'Approved', statusChangedAt: new Date() },
            });
          }

          await createAuditLog({
            entityType: 'line_item',
            entityId: id,
            action: 'APPROVAL',
            oldValue: li.status,
            newValue: allDone ? 'Approved' : li.status,
            performedBy: req.user!.id,
          });

          // Notify requester
          if (allDone) {
            notifyApproved({
              lineItemId: id,
              lineItemRef: li.lineItemRef,
              headerId: li.headerId,
              approvedBy: req.user!.fullName,
              createdById: li.createdBy,
              comment,
            }).catch(() => {});
          }

          results.push({ id, ref: li.lineItemRef, status: allDone ? 'Approved' : 'Pending next step' });
        } catch (e: any) {
          errors.push({ id, error: e.message });
        }
      }

      res.json({ approved: results, errors });
    } catch (err) {
      next(err);
    }
  }
);

// Helper: Find next approval step for a line item
async function findNextApprovalStep(li: any) {
  // Find applicable rule
  const rules = await prisma.lineItemApprovalRule.findMany({
    where: { isActive: true },
    orderBy: { priority: 'desc' },
    include: { steps: { orderBy: { stepOrder: 'asc' } } },
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

    if (matches) {
      // Find the first step not yet approved
      const existingApprovals = await prisma.lineItemApproval.findMany({
        where: { lineItemId: li.id, decision: 'Approved' },
        select: { stepId: true },
      });
      const approvedStepIds = new Set(existingApprovals.map((a) => a.stepId));

      for (const step of rule.steps) {
        if (!approvedStepIds.has(step.id)) return step;
      }

      return rule.steps[rule.steps.length - 1]; // Fallback to last step
    }
  }

  // Default: return the first step of the default rule
  const defaultRule = await prisma.lineItemApprovalRule.findFirst({
    where: { isActive: true, priority: 0 },
    include: { steps: { orderBy: { stepOrder: 'asc' }, take: 1 } },
  });

  return defaultRule?.steps[0] || null;
}

// Helper: Check if all approval steps are completed
async function areAllStepsCompleted(lineItemId: string, ruleId: string): Promise<boolean> {
  const totalSteps = await prisma.lineItemApprovalStep.count({
    where: { ruleId },
  });

  const approvedSteps = await prisma.lineItemApproval.findMany({
    where: { lineItemId, decision: 'Approved' },
    select: { stepId: true },
  });

  const uniqueApprovedSteps = new Set(approvedSteps.map((a) => a.stepId));
  return uniqueApprovedSteps.size >= totalSteps;
}
