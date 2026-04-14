import { Router, Response, NextFunction } from 'express';
import crypto from 'crypto';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import prisma from '../lib/prisma';
import { AppError } from '../middleware/errorHandler';
import { authenticate, AuthRequest } from '../middleware/auth';

export const authRouter = Router();

authRouter.post('/login', async (req, res: Response, next: NextFunction) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      throw new AppError('Email and password are required', 400);
    }

    const user = await prisma.user.findUnique({
      where: { email, isActive: true },
      include: {
        userRoles: { include: { role: true } },
      },
    });

    if (!user) {
      throw new AppError('Invalid credentials', 401);
    }

    const isValid = await bcrypt.compare(password, user.passwordHash);
    if (!isValid) {
      throw new AppError('Invalid credentials', 401);
    }

    const secret = process.env.JWT_SECRET;
    if (!secret) throw new AppError('JWT secret not configured', 500);

    const token = jwt.sign(
      { userId: user.id },
      secret,
      { expiresIn: process.env.JWT_EXPIRES_IN || '8h' } as jwt.SignOptions
    );

    await prisma.user.update({
      where: { id: user.id },
      data: { lastLogin: new Date() },
    });

    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        fullName: user.fullName,
        roles: user.userRoles.map((ur) => ({
          roleName: ur.role.roleName,
          projectId: ur.projectId,
        })),
      },
    });
  } catch (err) {
    next(err);
  }
});

authRouter.get('/me', authenticate, async (req: AuthRequest, res: Response) => {
  res.json({ user: req.user });
});

// ─── REGISTER ─────────────────────────────────────────────────────
authRouter.post('/register', async (req, res: Response, next: NextFunction) => {
  try {
    const { email, full_name, password, confirm_password } = req.body;

    if (!email || !full_name || !password || !confirm_password) {
      throw new AppError('All fields are required', 400);
    }

    if (password.length < 8) {
      throw new AppError('Password must be at least 8 characters', 400);
    }

    if (password !== confirm_password) {
      throw new AppError('Passwords do not match', 400);
    }

    // Email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      throw new AppError('Invalid email format', 400);
    }

    const existing = await prisma.user.findUnique({ where: { email: email.toLowerCase().trim() } });
    if (existing) {
      throw new AppError('An account with this email already exists', 409);
    }

    const passwordHash = await bcrypt.hash(password, 10);

    // Get default role — "Project/Department Requester"
    const defaultRole = await prisma.role.findFirst({
      where: { roleName: { contains: 'Requester' } },
    });

    const user = await prisma.user.create({
      data: {
        email: email.toLowerCase().trim(),
        fullName: full_name.trim(),
        passwordHash,
        isActive: true,
        userRoles: defaultRole
          ? { create: { roleId: defaultRole.id } }
          : undefined,
      },
      include: { userRoles: { include: { role: true } } },
    });

    const secret = process.env.JWT_SECRET;
    if (!secret) throw new AppError('JWT secret not configured', 500);

    const token = jwt.sign(
      { userId: user.id },
      secret,
      { expiresIn: process.env.JWT_EXPIRES_IN || '8h' } as jwt.SignOptions,
    );

    res.status(201).json({
      token,
      user: {
        id: user.id,
        email: user.email,
        fullName: user.fullName,
        roles: user.userRoles.map((ur) => ({
          roleName: ur.role.roleName,
          projectId: ur.projectId,
        })),
      },
    });
  } catch (err) {
    next(err);
  }
});

// ─── FORGOT PASSWORD ──────────────────────────────────────────────
authRouter.post('/forgot-password', async (req, res: Response, next: NextFunction) => {
  try {
    const { email } = req.body;
    if (!email) throw new AppError('Email is required', 400);

    const user = await prisma.user.findUnique({ where: { email: email.toLowerCase().trim() } });

    // Always return success to prevent email enumeration
    if (!user || !user.isActive) {
      res.json({ message: 'If an account with that email exists, a reset code has been generated.' });
      return;
    }

    // Generate a 6-digit reset code
    const resetCode = crypto.randomInt(100000, 999999).toString();
    const resetTokenHash = await bcrypt.hash(resetCode, 10);
    const expiry = new Date(Date.now() + 15 * 60 * 1000); // 15 minutes

    await prisma.user.update({
      where: { id: user.id },
      data: { resetToken: resetTokenHash, resetTokenExpiry: expiry },
    });

    // In production, this would send an email. For now, log it and return it for development.
    console.log(`[RESET CODE] ${user.email}: ${resetCode}`);

    res.json({
      message: 'If an account with that email exists, a reset code has been generated.',
      // DEV ONLY — remove in production
      _dev_reset_code: resetCode,
    });
  } catch (err) {
    next(err);
  }
});

// ─── RESET PASSWORD ──────────────────────────────────────────────
authRouter.post('/reset-password', async (req, res: Response, next: NextFunction) => {
  try {
    const { email, reset_code, new_password, confirm_password } = req.body;

    if (!email || !reset_code || !new_password || !confirm_password) {
      throw new AppError('All fields are required', 400);
    }

    if (new_password.length < 8) {
      throw new AppError('Password must be at least 8 characters', 400);
    }

    if (new_password !== confirm_password) {
      throw new AppError('Passwords do not match', 400);
    }

    const user = await prisma.user.findUnique({
      where: { email: email.toLowerCase().trim() },
    });

    if (!user || !user.resetToken || !user.resetTokenExpiry) {
      throw new AppError('Invalid or expired reset code', 400);
    }

    if (new Date() > user.resetTokenExpiry) {
      // Clear expired token
      await prisma.user.update({
        where: { id: user.id },
        data: { resetToken: null, resetTokenExpiry: null },
      });
      throw new AppError('Reset code has expired. Please request a new one.', 400);
    }

    const isValidCode = await bcrypt.compare(reset_code, user.resetToken);
    if (!isValidCode) {
      throw new AppError('Invalid reset code', 400);
    }

    const passwordHash = await bcrypt.hash(new_password, 10);

    await prisma.user.update({
      where: { id: user.id },
      data: {
        passwordHash,
        resetToken: null,
        resetTokenExpiry: null,
      },
    });

    res.json({ message: 'Password reset successful. You can now sign in with your new password.' });
  } catch (err) {
    next(err);
  }
});
