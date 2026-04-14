import { Router, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { AppError } from '../middleware/errorHandler';
import { Decimal } from '@prisma/client/runtime/library';

export const exchangeRatesRouter = Router();
exchangeRatesRouter.use(authenticate);

// GET /api/v1/exchange-rates (Finance, Admin only)
exchangeRatesRouter.get(
  '/',
  authorize('Finance/Grants', 'System Admin'),
  async (_req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const rates = await prisma.exchangeRate.findMany({
      orderBy: [{ fromCurrency: 'asc' }, { effectiveDate: 'desc' }],
      include: { creator: { select: { fullName: true } } },
    });
    res.json(rates);
  } catch (err) {
    next(err);
  }
});

// POST /api/v1/exchange-rates
exchangeRatesRouter.post(
  '/',
  authorize('System Admin', 'Finance/Grants'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const { from_currency, to_currency, rate, effective_date } = req.body;

      if (!from_currency || !to_currency || !rate || !effective_date) {
        throw new AppError('from_currency, to_currency, rate, and effective_date are required', 400);
      }
      if (from_currency === to_currency) {
        throw new AppError('from_currency and to_currency must be different', 400);
      }
      if (rate <= 0) {
        throw new AppError('Rate must be positive', 400);
      }

      const er = await prisma.exchangeRate.create({
        data: {
          fromCurrency: from_currency,
          toCurrency: to_currency,
          rate: new Decimal(rate),
          effectiveDate: new Date(effective_date),
          createdBy: req.user!.id,
        },
      });

      res.status(201).json(er);
    } catch (err) {
      next(err);
    }
  }
);

// GET /api/v1/exchange-rates/convert (Finance, Admin only)
exchangeRatesRouter.get(
  '/convert',
  authorize('Finance/Grants', 'System Admin'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { from, to, amount, date } = req.query;

    if (!from || !to || !amount) {
      throw new AppError('from, to, and amount query params are required', 400);
    }

    const effectiveDate = date ? new Date(date as string) : new Date();

    const rate = await prisma.exchangeRate.findFirst({
      where: {
        fromCurrency: from as string,
        toCurrency: to as string,
        effectiveDate: { lte: effectiveDate },
      },
      orderBy: { effectiveDate: 'desc' },
    });

    if (!rate) {
      throw new AppError(`No exchange rate found for ${from} to ${to} as of ${effectiveDate.toISOString().split('T')[0]}`, 404);
    }

    const converted = Number(amount) * Number(rate.rate);

    res.json({
      from_currency: from,
      to_currency: to,
      original_amount: Number(amount),
      converted_amount: Math.round(converted * 100) / 100,
      rate_used: Number(rate.rate),
      effective_date: rate.effectiveDate,
    });
  } catch (err) {
    next(err);
  }
});
