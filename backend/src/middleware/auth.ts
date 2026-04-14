import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import prisma from '../lib/prisma';
import { AppError } from './errorHandler';

export interface AuthRequest extends Request {
  user?: {
    id: string;
    email: string;
    fullName: string;
    roles: Array<{
      roleId: string;
      roleName: string;
      projectId: string | null;
    }>;
  };
}

export async function authenticate(
  req: AuthRequest,
  _res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader?.startsWith('Bearer ')) {
      throw new AppError('Authentication required', 401);
    }

    const token = authHeader.substring(7);
    const secret = process.env.JWT_SECRET;
    if (!secret) {
      throw new AppError('JWT secret not configured', 500);
    }

    const decoded = jwt.verify(token, secret) as { userId: string };

    const user = await prisma.user.findUnique({
      where: { id: decoded.userId, isActive: true },
      include: {
        userRoles: {
          include: { role: true },
        },
      },
    });

    if (!user) {
      throw new AppError('User not found or inactive', 401);
    }

    req.user = {
      id: user.id,
      email: user.email,
      fullName: user.fullName,
      roles: user.userRoles.map((ur) => ({
        roleId: ur.role.id,
        roleName: ur.role.roleName,
        projectId: ur.projectId,
      })),
    };

    next();
  } catch (err) {
    if (err instanceof AppError) {
      next(err);
    } else if (err instanceof jwt.JsonWebTokenError) {
      next(new AppError('Invalid token', 401));
    } else {
      next(err);
    }
  }
}

export function authorize(...allowedRoles: string[]) {
  return (req: AuthRequest, _res: Response, next: NextFunction): void => {
    if (!req.user) {
      next(new AppError('Authentication required', 401));
      return;
    }

    const hasRole = req.user.roles.some(
      (r) => allowedRoles.includes(r.roleName) || r.roleName === 'System Admin' ||
        allowedRoles.some((allowed) => r.roleName.includes(allowed))
    );

    if (!hasRole) {
      next(new AppError('Insufficient permissions', 403));
      return;
    }

    next();
  };
}

/**
 * Check whether a user has a "broad visibility" role (Manager or System Admin).
 * These roles can see records across all users/projects.
 */
export function hasBroadVisibility(user: AuthRequest['user']): boolean {
  if (!user) return false;
  return user.roles.some(
    (r) =>
      r.roleName === 'System Admin' ||
      r.roleName === 'Project/Department Manager'
  );
}
