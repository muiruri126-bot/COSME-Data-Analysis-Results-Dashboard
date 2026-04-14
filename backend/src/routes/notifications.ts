import { Router, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { authenticate, AuthRequest } from '../middleware/auth';

export const notificationsRouter = Router();
notificationsRouter.use(authenticate);

// GET /api/v1/notifications — List current user's notifications
notificationsRouter.get(
  '/',
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const page = Math.max(1, parseInt(req.query.page as string) || 1);
      const limit = Math.min(50, Math.max(1, parseInt(req.query.limit as string) || 20));
      const unreadOnly = req.query.unread === 'true';

      const where: any = { userId: req.user!.id };
      if (unreadOnly) where.isRead = false;

      const [data, total] = await Promise.all([
        prisma.notification.findMany({
          where,
          orderBy: { createdAt: 'desc' },
          skip: (page - 1) * limit,
          take: limit,
        }),
        prisma.notification.count({ where }),
      ]);

      res.json({
        data: data.map((n) => ({
          id: n.id,
          type: n.type,
          title: n.title,
          message: n.message,
          line_item_id: n.lineItemId,
          header_id: n.headerId,
          is_read: n.isRead,
          created_at: n.createdAt,
        })),
        pagination: { page, limit, total, totalPages: Math.ceil(total / limit) },
      });
    } catch (err) {
      next(err);
    }
  }
);

// GET /api/v1/notifications/unread-count
notificationsRouter.get(
  '/unread-count',
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const count = await prisma.notification.count({
        where: { userId: req.user!.id, isRead: false },
      });
      res.json({ count });
    } catch (err) {
      next(err);
    }
  }
);

// PATCH /api/v1/notifications/:id/read — Mark single notification as read
notificationsRouter.patch(
  '/:id/read',
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      await prisma.notification.updateMany({
        where: { id: req.params.id as string, userId: req.user!.id },
        data: { isRead: true },
      });
      res.json({ success: true });
    } catch (err) {
      next(err);
    }
  }
);

// PATCH /api/v1/notifications/read-all — Mark all as read
notificationsRouter.patch(
  '/read-all',
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const result = await prisma.notification.updateMany({
        where: { userId: req.user!.id, isRead: false },
        data: { isRead: true },
      });
      res.json({ marked: result.count });
    } catch (err) {
      next(err);
    }
  }
);
