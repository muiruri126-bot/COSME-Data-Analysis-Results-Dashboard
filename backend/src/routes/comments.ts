import { Router, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { authenticate, AuthRequest } from '../middleware/auth';
import { AppError } from '../middleware/errorHandler';

export const commentsRouter = Router();
commentsRouter.use(authenticate);

// POST /api/v1/comments
commentsRouter.post('/', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { entity_type, entity_id, comment_text } = req.body;
    if (!entity_type || !entity_id || !comment_text?.trim()) {
      throw new AppError('entity_type, entity_id, and comment_text are required', 400);
    }

    const validTypes = ['procurement_plan', 'line_item', 'purchase_requisition', 'delivery'];
    if (!validTypes.includes(entity_type)) {
      throw new AppError(`entity_type must be one of: ${validTypes.join(', ')}`, 400);
    }

    const comment = await prisma.comment.create({
      data: {
        entityType: entity_type,
        entityId: entity_id,
        commentText: comment_text.trim(),
        authorId: req.user!.id,
      },
      include: { author: { select: { id: true, fullName: true } } },
    });

    res.status(201).json(comment);
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/comments?entity_type=line_item&entity_id=xxx
commentsRouter.get('/', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { entity_type, entity_id } = req.query;
    if (!entity_type || !entity_id) {
      throw new AppError('entity_type and entity_id are required', 400);
    }

    const comments = await prisma.comment.findMany({
      where: { entityType: entity_type as string, entityId: entity_id as string },
      include: { author: { select: { id: true, fullName: true } } },
      orderBy: { createdAt: 'asc' },
    });

    res.json(comments);
  } catch (err) {
    next(err);
  }
});
