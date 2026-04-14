import { Router, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { AppError } from '../middleware/errorHandler';
import { recordDeliverySchema } from '../lib/constants';
import { createAuditLog } from '../lib/audit';
import { notifyDelivered } from '../lib/notifications';
import { Decimal } from '@prisma/client/runtime/library';

export const deliveriesRouter = Router();
deliveriesRouter.use(authenticate);

// POST /api/v1/line-items/:lineItemId/deliveries — Record delivery (partial)
deliveriesRouter.post(
  '/line-item/:lineItemId',
  authorize('Supply Chain Officer', 'Stores/Inventory Officer', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const li = await prisma.procurementPlanLineItem.findUnique({
        where: { id: req.params.lineItemId as string, deletedAt: null },
      });
      if (!li) throw new AppError('Line item not found', 404);

      if (!['Ordered/Contracted', 'Delivery In Progress'].includes(li.status)) {
        throw new AppError(`Cannot record delivery for item in status ${li.status}`, 400);
      }

      const parsed = recordDeliverySchema.parse(req.body);

      const totalDelivered = Number(li.deliveredQuantity) + parsed.quantity_delivered;
      if (totalDelivered > Number(li.quantity)) {
        throw new AppError(
          `Total delivered (${totalDelivered}) would exceed planned quantity (${li.quantity}). Current delivered: ${li.deliveredQuantity}.`,
          400
        );
      }

      const delivery = await prisma.$transaction(async (tx) => {
        const del = await tx.delivery.create({
          data: {
            lineItemId: li.id,
            prId: parsed.pr_id,
            deliveryDate: new Date(parsed.delivery_date),
            quantityDelivered: new Decimal(parsed.quantity_delivered),
            receivedBy: req.user!.id,
            deliveryNoteRef: parsed.delivery_note_ref,
            conditionNotes: parsed.condition_notes,
          },
        });

        // Update delivered quantity
        const newDelivered = new Decimal(totalDelivered);
        const updateData: Record<string, unknown> = {
          deliveredQuantity: newDelivered,
        };

        // Auto-transition status
        if (li.status === 'Ordered/Contracted') {
          updateData.status = 'Delivery In Progress';
          updateData.statusChangedAt = new Date();
        }

        if (totalDelivered >= Number(li.quantity)) {
          updateData.status = 'Delivered/Closed';
          updateData.statusChangedAt = new Date();
          updateData.actualDeliveryDate = new Date(parsed.delivery_date);
        }

        await tx.procurementPlanLineItem.update({
          where: { id: li.id },
          data: updateData as any,
        });

        return del;
      });

      await createAuditLog({
        entityType: 'delivery',
        entityId: delivery.id,
        action: 'CREATE',
        performedBy: req.user!.id,
        ipAddress: req.ip,
      });

      // Notify plan creator about delivery
      notifyDelivered({
        lineItemId: li.id,
        lineItemRef: li.lineItemRef,
        headerId: li.headerId,
        createdById: li.createdBy,
        quantity: parsed.quantity_delivered,
      }).catch(() => {});

      res.status(201).json({
        delivery_id: delivery.id,
        line_item_id: li.id,
        line_item_ref: li.lineItemRef,
        delivery_date: parsed.delivery_date,
        quantity_delivered: parsed.quantity_delivered,
        total_delivered_to_date: totalDelivered,
        planned_quantity: Number(li.quantity),
        remaining_quantity: Number(li.quantity) - totalDelivered,
        delivery_percentage: Math.round((totalDelivered / Number(li.quantity)) * 1000) / 10,
        line_item_status: totalDelivered >= Number(li.quantity) ? 'Delivered/Closed' : 'Delivery In Progress',
      });
    } catch (err) {
      next(err);
    }
  }
);

// GET /api/v1/deliveries/line-item/:lineItemId — List deliveries for a line item (Supply Chain, Stores, Admin)
deliveriesRouter.get(
  '/line-item/:lineItemId',
  authorize('Supply Chain Officer', 'Stores/Inventory Officer', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const deliveries = await prisma.delivery.findMany({
        where: { lineItemId: req.params.lineItemId as string },
        include: {
          receiver: { select: { id: true, fullName: true } },
        },
        orderBy: { deliveryDate: 'desc' },
      });

      const li = await prisma.procurementPlanLineItem.findUnique({
        where: { id: req.params.lineItemId as string },
        select: { quantity: true, deliveredQuantity: true, lineItemRef: true },
      });

      res.json({
        line_item_ref: li?.lineItemRef,
        planned_quantity: li ? Number(li.quantity) : 0,
        total_delivered: li ? Number(li.deliveredQuantity) : 0,
        deliveries,
      });
    } catch (err) {
      next(err);
    }
  }
);
