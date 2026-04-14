import { Router, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { AppError } from '../middleware/errorHandler';
import { createAuditLog } from '../lib/audit';
import bcrypt from 'bcryptjs';

export const adminRouter = Router();
adminRouter.use(authenticate);

// ─── USERS ────────────────────────────────────────────────────────

// GET /api/v1/admin/users
adminRouter.get('/users', authorize('System Admin'), async (_req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const users = await prisma.user.findMany({
      include: { userRoles: { include: { role: true } } },
      orderBy: { fullName: 'asc' },
    });
    const sanitized = users.map(({ passwordHash: _, ...u }) => u);
    res.json(sanitized);
  } catch (err) {
    next(err);
  }
});

// POST /api/v1/admin/users
adminRouter.post('/users', authorize('System Admin'), async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { email, full_name, password, role_ids, location_id, is_active = true } = req.body;
    if (!email || !full_name || !password) {
      throw new AppError('email, full_name, and password are required', 400);
    }

    const exists = await prisma.user.findUnique({ where: { email } });
    if (exists) throw new AppError('User with this email already exists', 409);

    const passwordHash = await bcrypt.hash(password, 12);

    const user = await prisma.user.create({
      data: {
        email,
        fullName: full_name,
        passwordHash,
        isActive: is_active,
        userRoles: role_ids && role_ids.length > 0
          ? { createMany: { data: role_ids.map((rid: string) => ({ roleId: rid })) } }
          : undefined,
      },
      include: { userRoles: { include: { role: true } } },
    });

    await createAuditLog({
      entityType: 'user',
      entityId: user.id,
      action: 'CREATE',
      performedBy: req.user!.id,
    });

    const { passwordHash: _, ...safe } = user;
    res.status(201).json(safe);
  } catch (err) {
    next(err);
  }
});

// PUT /api/v1/admin/users/:id
adminRouter.put('/users/:id', authorize('System Admin'), async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { email, full_name, location_id, is_active, role_ids } = req.body;
    const userId = req.params.id as string;
    const existing = await prisma.user.findUnique({ where: { id: userId } });
    if (!existing) throw new AppError('User not found', 404);

    const data: Record<string, unknown> = {};
    if (email) data.email = email;
    if (full_name) data.fullName = full_name;
    if (is_active !== undefined) data.isActive = is_active;

    const user = await prisma.$transaction(async (tx) => {
      const u = await tx.user.update({
        where: { id: userId },
        data: data as any,
        include: { userRoles: { include: { role: true } } },
      });

      if (role_ids) {
        await tx.userRole.deleteMany({ where: { userId: u.id } });
        if (role_ids.length > 0) {
          await tx.userRole.createMany({
            data: role_ids.map((rid: string) => ({ userId: u.id, roleId: rid })),
          });
        }
      }

      return tx.user.findUnique({ where: { id: u.id }, include: { userRoles: { include: { role: true } } } });
    });

    await createAuditLog({
      entityType: 'user',
      entityId: userId,
      action: 'UPDATE',
      performedBy: req.user!.id,
    });

    const { passwordHash: _, ...safe } = user as any;
    res.json(safe);
  } catch (err) {
    next(err);
  }
});

// ─── ROLES ────────────────────────────────────────────────────────

// GET /api/v1/admin/roles
adminRouter.get('/roles', async (_req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const roles = await prisma.role.findMany({
      include: { permissions: true },
      orderBy: { roleName: 'asc' },
    });
    res.json(roles);
  } catch (err) {
    next(err);
  }
});

// ─── APPROVAL RULES ──────────────────────────────────────────────

// GET /api/v1/admin/approval-rules
adminRouter.get('/approval-rules', authorize('System Admin'), async (_req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const rules = await prisma.lineItemApprovalRule.findMany({
      include: { steps: { orderBy: { stepOrder: 'asc' } } },
      orderBy: { priority: 'desc' },
    });
    res.json(rules);
  } catch (err) {
    next(err);
  }
});

// POST /api/v1/admin/approval-rules
adminRouter.post('/approval-rules', authorize('System Admin'), async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const {
      rule_name, item_type, sourcing_method_id, material_group_id, location_id,
      cost_threshold_min, cost_threshold_max, cost_threshold_currency, priority, steps,
    } = req.body;

    if (!rule_name) throw new AppError('rule_name is required', 400);

    const rule = await prisma.lineItemApprovalRule.create({
      data: {
        ruleName: rule_name,
        itemType: item_type,
        sourcingMethodId: sourcing_method_id,
        materialGroupId: material_group_id,
        locationId: location_id,
        costThresholdMin: cost_threshold_min,
        costThresholdMax: cost_threshold_max,
        costThresholdCurrency: cost_threshold_currency,
        priority: priority || 0,
        isActive: true,
        steps: steps && steps.length > 0
          ? {
              createMany: {
                data: steps.map((s: any, i: number) => ({
                  stepOrder: s.step_order || i + 1,
                  approverRoleId: s.approver_role_id,
                  specificApproverId: s.specific_approver_id,
                  isParallel: s.is_parallel || false,
                  canDelegate: s.can_delegate !== false,
                })),
              },
            }
          : undefined,
      },
      include: { steps: true },
    });

    res.status(201).json(rule);
  } catch (err) {
    next(err);
  }
});

// ─── LOOKUPS ─────────────────────────────────────────────────────

// GET /api/v1/admin/projects
adminRouter.get('/projects', async (_req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const projects = await prisma.project.findMany({
      include: { fundingSource: true },
      orderBy: { projectName: 'asc' },
    });
    res.json(projects);
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/admin/managers — lightweight list of users (for dropdowns, no admin required)
adminRouter.get('/managers', async (_req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const users = await prisma.user.findMany({
      where: { isActive: true },
      select: { id: true, fullName: true, email: true },
      orderBy: { fullName: 'asc' },
    });
    res.json(users);
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/admin/locations
adminRouter.get('/locations', async (_req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const locations = await prisma.location.findMany({ orderBy: { locationName: 'asc' } });
    res.json(locations);
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/admin/material-groups
adminRouter.get('/material-groups', async (_req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const groups = await prisma.materialGroup.findMany({
      include: { defaultSourcingMethod: true },
      orderBy: { groupName: 'asc' },
    });
    res.json(groups);
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/admin/next-tracking-no — Auto-generate next tracking number
adminRouter.get('/next-tracking-no', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { type, fy } = req.query;
    if (!type || !fy) throw new AppError('type and fy query params are required', 400);

    const prefix = type === 'Project' ? 'PP' : 'DP';
    const pattern = `${prefix}${fy}-%`;

    const existing = await prisma.procurementPlanHeader.findMany({
      where: { trackingNo: { startsWith: `${prefix}${fy}-` }, deletedAt: null },
      select: { trackingNo: true },
    });

    const maxSeq = existing.reduce((max, p) => {
      const parts = p.trackingNo.split('-');
      const seq = parseInt(parts[parts.length - 1], 10);
      return isNaN(seq) ? max : Math.max(max, seq);
    }, 0);

    const nextSeq = String(maxSeq + 1).padStart(3, '0');
    res.json({ tracking_no: `${prefix}${fy}-${nextSeq}` });
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/admin/units-of-measure
adminRouter.get('/units-of-measure', async (_req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const uoms = await prisma.unitOfMeasure.findMany({ orderBy: { uomName: 'asc' } });
    res.json(uoms);
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/admin/sourcing-methods
adminRouter.get('/sourcing-methods', async (_req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const methods = await prisma.sourcingMethod.findMany({ orderBy: { methodName: 'asc' } });
    res.json(methods);
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/admin/funding-sources
adminRouter.get('/funding-sources', async (_req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const sources = await prisma.fundingSource.findMany({ orderBy: { sourceName: 'asc' } });
    res.json(sources);
  } catch (err) {
    next(err);
  }
});

// ─── AUDIT LOG ───────────────────────────────────────────────────

// GET /api/v1/admin/audit-log
adminRouter.get('/audit-log', authorize('System Admin'), async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { entity_type, entity_id, user_id, action, from_date, to_date, page = '1', limit = '50' } = req.query;
    const skip = (Number(page) - 1) * Number(limit);
    const take = Number(limit);

    const where: Record<string, unknown> = {};
    if (entity_type) where.entityType = entity_type;
    if (entity_id) where.entityId = entity_id;
    if (user_id) where.performedBy = user_id;
    if (action) where.action = action;
    if (from_date || to_date) {
      where.performedAt = {};
      if (from_date) (where.performedAt as any).gte = new Date(from_date as string);
      if (to_date) (where.performedAt as any).lte = new Date(to_date as string);
    }

    const [logs, total] = await Promise.all([
      prisma.auditLog.findMany({
        where: where as any,
        include: { performer: { select: { id: true, fullName: true } } },
        orderBy: { performedAt: 'desc' },
        skip,
        take,
      }),
      prisma.auditLog.count({ where: where as any }),
    ]);

    res.json({
      data: logs,
      pagination: { page: Number(page), limit: take, total, totalPages: Math.ceil(total / take) },
    });
  } catch (err) {
    next(err);
  }
});
