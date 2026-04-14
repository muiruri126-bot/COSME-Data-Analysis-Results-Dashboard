import { Router, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { AppError } from '../middleware/errorHandler';
import { Decimal } from '@prisma/client/runtime/library';

export const stockAssetsRouter = Router();
stockAssetsRouter.use(authenticate);

// GET /api/v1/stock-assets (Stores/Inventory, Admin only)
stockAssetsRouter.get(
  '/',
  authorize('Stores/Inventory Officer', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { location_id, item_type, page = '1', limit = '20' } = req.query;
    const skip = (Number(page) - 1) * Number(limit);
    const take = Number(limit);

    const where: Record<string, unknown> = {};
    if (location_id) where.locationId = location_id;
    if (item_type) where.itemType = item_type;

    const [assets, total] = await Promise.all([
      prisma.stockAsset.findMany({
        where: where as any,
        include: {
          location: true,
          lineItem: { select: { lineItemRef: true, itemDescription: true } },
          updatedByUser: { select: { fullName: true } },
        },
        orderBy: { updatedAt: 'desc' },
        skip,
        take,
      }),
      prisma.stockAsset.count({ where: where as any }),
    ]);

    res.json({
      data: assets,
      pagination: { page: Number(page), limit: take, total, totalPages: Math.ceil(total / take) },
    });
  } catch (err) {
    next(err);
  }
});

// POST /api/v1/stock-assets
stockAssetsRouter.post(
  '/',
  authorize('Stores/Inventory Officer', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const { line_item_id, item_description, item_type, quantity_on_hand, location_id, asset_tag } = req.body;

      if (!item_description || !item_type) {
        throw new AppError('item_description and item_type are required', 400);
      }

      const asset = await prisma.stockAsset.create({
        data: {
          lineItemId: line_item_id,
          itemDescription: item_description,
          itemType: item_type,
          quantityOnHand: new Decimal(quantity_on_hand || 0),
          locationId: location_id,
          lastCheckedDate: new Date(),
          lastUpdatedBy: req.user!.id,
          assetTag: asset_tag,
        },
      });

      res.status(201).json(asset);
    } catch (err) {
      next(err);
    }
  }
);

// PUT /api/v1/stock-assets/:id
stockAssetsRouter.put(
  '/:id',
  authorize('Stores/Inventory Officer', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const existing = await prisma.stockAsset.findUnique({ where: { id: req.params.id as string } });
      if (!existing) throw new AppError('Stock/asset record not found', 404);

      const data: Record<string, unknown> = {};
      if (req.body.quantity_on_hand !== undefined) data.quantityOnHand = new Decimal(req.body.quantity_on_hand);
      if (req.body.item_description !== undefined) data.itemDescription = req.body.item_description;
      if (req.body.location_id !== undefined) data.locationId = req.body.location_id;
      if (req.body.asset_tag !== undefined) data.assetTag = req.body.asset_tag;
      data.lastCheckedDate = new Date();
      data.lastUpdatedBy = req.user!.id;

      const updated = await prisma.stockAsset.update({
        where: { id: req.params.id as string },
        data: data as any,
      });

      res.json(updated);
    } catch (err) {
      next(err);
    }
  }
);
