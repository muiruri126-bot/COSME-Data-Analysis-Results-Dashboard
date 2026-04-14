import { Router, Response, NextFunction } from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import prisma from '../lib/prisma';
import { authenticate, AuthRequest } from '../middleware/auth';
import { AppError } from '../middleware/errorHandler';

// Configure uploads directory
const uploadsDir = path.join(process.cwd(), 'uploads');
if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, uploadsDir),
  filename: (_req, file, cb) => {
    const unique = `${Date.now()}-${Math.round(Math.random() * 1e9)}`;
    const ext = path.extname(file.originalname);
    cb(null, `${unique}${ext}`);
  },
});

const ALLOWED_MIMES = [
  'application/pdf',
  'image/jpeg', 'image/png', 'image/gif',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
  'text/csv',
];

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
  fileFilter: (_req, file, cb) => {
    if (ALLOWED_MIMES.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error(`File type ${file.mimetype} not allowed`));
    }
  },
});

export const attachmentsRouter = Router();
attachmentsRouter.use(authenticate);

// POST /api/v1/attachments
attachmentsRouter.post(
  '/',
  upload.single('file'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      if (!req.file) throw new AppError('File is required', 400);

      const { entity_type, entity_id, display_name } = req.body;
      if (!entity_type || !entity_id) {
        throw new AppError('entity_type and entity_id are required', 400);
      }

      // Validate entity_type
      const validTypes = ['procurement_plan', 'line_item', 'purchase_requisition', 'delivery', 'stock_asset'];
      if (!validTypes.includes(entity_type)) {
        throw new AppError(`entity_type must be one of: ${validTypes.join(', ')}`, 400);
      }

      const attachment = await prisma.attachment.create({
        data: {
          entityType: entity_type,
          entityId: entity_id,
          fileName: display_name || req.file.originalname,
          mimeType: req.file.mimetype,
          fileSize: req.file.size,
          filePath: req.file.path,
          uploadedBy: req.user!.id,
        },
      });

      res.status(201).json({
        id: attachment.id,
        file_name: attachment.fileName,
        mime_type: attachment.mimeType,
        file_size: attachment.fileSize,
        uploaded_at: attachment.createdAt,
      });
    } catch (err) {
      next(err);
    }
  }
);

// GET /api/v1/attachments?entity_type=line_item&entity_id=xxx
attachmentsRouter.get('/', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { entity_type, entity_id } = req.query;
    if (!entity_type || !entity_id) {
      throw new AppError('entity_type and entity_id are required', 400);
    }

    const attachments = await prisma.attachment.findMany({
      where: { entityType: entity_type as string, entityId: entity_id as string },
      include: { uploader: { select: { id: true, fullName: true } } },
      orderBy: { createdAt: 'desc' },
    });

    res.json(attachments);
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/attachments/:id/download
attachmentsRouter.get('/:id/download', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const attachment = await prisma.attachment.findUnique({ where: { id: req.params.id as string } });
    if (!attachment) throw new AppError('Attachment not found', 404);

    if (!fs.existsSync(attachment.filePath)) {
      throw new AppError('File no longer exists on disk', 404);
    }

    res.download(attachment.filePath, attachment.fileName);
  } catch (err) {
    next(err);
  }
});

// DELETE /api/v1/attachments/:id
attachmentsRouter.delete('/:id', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const attachmentId = req.params.id as string;
    const attachment = await prisma.attachment.findUnique({ where: { id: attachmentId } });
    if (!attachment) throw new AppError('Attachment not found', 404);

    // Only uploader or Admin can delete
    if (attachment.uploadedBy !== req.user!.id && !req.user!.roles.some((r) => r.roleName === 'System Admin')) {
      throw new AppError('Only the uploader or admin can delete this attachment', 403);
    }

    // Remove file from disk
    if (fs.existsSync(attachment.filePath)) {
      fs.unlinkSync(attachment.filePath);
    }

    await prisma.attachment.delete({ where: { id: attachmentId } });

    res.json({ message: 'Attachment deleted' });
  } catch (err) {
    next(err);
  }
});
