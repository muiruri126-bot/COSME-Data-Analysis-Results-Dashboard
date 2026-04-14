import { Router, Response, NextFunction } from 'express';
import prisma from '../lib/prisma';
import { authenticate, AuthRequest, hasBroadVisibility } from '../middleware/auth';

export const reportsRouter = Router();
reportsRouter.use(authenticate);

// GET /api/v1/reports/dashboard
reportsRouter.get('/dashboard', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { project_id, fiscal_year, location_id, donor_name } = req.query;

    const where: Record<string, unknown> = { deletedAt: null };
    if (fiscal_year) where.fiscalYear = fiscal_year;
    if (location_id) where.locationId = location_id;

    // Project filter via header
    const headerWhere: Record<string, unknown> = { deletedAt: null };
    if (project_id) headerWhere.projectId = project_id;
    if (donor_name) headerWhere.donorName = { contains: donor_name as string, mode: 'insensitive' };

    // Role-based data filtering: non-Manager/non-Admin see only their own plans' data
    if (!hasBroadVisibility(req.user)) {
      headerWhere.OR = [
        { createdBy: req.user!.id },
        { departmentManagerId: req.user!.id },
      ];
    }

    const lineItems = await prisma.procurementPlanLineItem.findMany({
      where: {
        ...where as any,
        header: headerWhere as any,
      },
      select: {
        status: true,
        estimatedTotalCost: true,
        currencyCode: true,
        statusChangedAt: true,
        estimatedDeliveryDate: true,
        quantity: true,
        deliveredQuantity: true,
        lineItemRef: true,
        itemDescription: true,
        isStockOnHandAvailable: true,
        quantityAvailable: true,
        header: {
          select: {
            trackingNo: true,
            departmentManager: { select: { fullName: true } },
          },
        },
        location: { select: { locationName: true } },
      },
    });

    // Status summary
    const statusSummary: Record<string, { count: number; value_kes: number; value_eur: number }> = {};
    let totalKes = 0;
    let totalEur = 0;

    for (const li of lineItems) {
      const cost = Number(li.estimatedTotalCost || 0);
      if (!statusSummary[li.status]) {
        statusSummary[li.status] = { count: 0, value_kes: 0, value_eur: 0 };
      }
      statusSummary[li.status].count++;
      if (li.currencyCode === 'KES') {
        statusSummary[li.status].value_kes += cost;
        totalKes += cost;
      } else {
        statusSummary[li.status].value_eur += cost;
        totalEur += cost;
      }
    }

    // Approval ageing
    const pendingItems = lineItems.filter((li) =>
      ['Submitted for Approval', 'Returned for Correction'].includes(li.status)
    );
    const ageingItems = pendingItems.map((li) => ({
      ref: li.lineItemRef,
      status: li.status,
      days_pending: li.statusChangedAt ? Math.ceil(
        (Date.now() - new Date(li.statusChangedAt).getTime()) / (1000 * 60 * 60 * 24)
      ) : 0,
      approver: li.header.departmentManager.fullName,
      value: Number(li.estimatedTotalCost),
      currency: li.currencyCode,
    }));

    const avgDaysSubmitted = ageingItems.filter((a) => a.status === 'Submitted for Approval');
    const avgDaysReturned = ageingItems.filter((a) => a.status === 'Returned for Correction');

    // Overdue deliveries
    const now = new Date();
    const overdueItems = lineItems
      .filter(
        (li) =>
          li.estimatedDeliveryDate &&
          new Date(li.estimatedDeliveryDate) < now &&
          !['Delivered/Closed', 'Cancelled'].includes(li.status)
      )
      .map((li) => ({
        ref: li.lineItemRef,
        item_description: li.itemDescription,
        estimated_delivery_date: li.estimatedDeliveryDate,
        days_overdue: Math.ceil(
          (now.getTime() - new Date(li.estimatedDeliveryDate!).getTime()) / (1000 * 60 * 60 * 24)
        ),
        delivered_pct: Number(li.quantity) > 0
          ? Math.round((Number(li.deliveredQuantity) / Number(li.quantity)) * 1000) / 10
          : 0,
        location: li.location.locationName,
      }))
      .sort((a, b) => b.days_overdue - a.days_overdue);

    // Top 10 cost items
    const top10 = [...lineItems]
      .filter((li) => li.status !== 'Cancelled')
      .sort((a, b) => Number(b.estimatedTotalCost) - Number(a.estimatedTotalCost))
      .slice(0, 10)
      .map((li) => ({
        ref: li.lineItemRef,
        description: li.itemDescription,
        estimated_total_cost: Number(li.estimatedTotalCost),
        currency: li.currencyCode,
      }));

    // Stock avoided
    const stockAvoided = lineItems.filter(
      (li) => li.isStockOnHandAvailable && Number(li.quantityAvailable) >= Number(li.quantity)
    );

    // Partial approval summary per plan
    const planMap = new Map<string, Record<string, number>>();
    for (const li of lineItems) {
      const key = li.header.trackingNo;
      if (!planMap.has(key)) {
        planMap.set(key, { total: 0 });
      }
      const entry = planMap.get(key)!;
      entry.total++;
      const simplified = li.status.replace(/ /g, '_').toLowerCase();
      entry[simplified] = (entry[simplified] || 0) + 1;
    }

    // Exchange rate for conversion
    const latestRate = await prisma.exchangeRate.findFirst({
      where: { fromCurrency: 'KES', toCurrency: 'EUR', effectiveDate: { lte: now } },
      orderBy: { effectiveDate: 'desc' },
    });

    const totalEurConverted = latestRate
      ? totalEur + totalKes * Number(latestRate.rate)
      : totalEur;

    res.json({
      summary: {
        total_planned_cost_kes: Math.round(totalKes * 100) / 100,
        total_planned_cost_eur: Math.round(totalEur * 100) / 100,
        total_planned_cost_eur_converted: Math.round(totalEurConverted * 100) / 100,
        exchange_rate_used: latestRate
          ? { KES_to_EUR: Number(latestRate.rate), effective_date: latestRate.effectiveDate }
          : null,
        line_items_by_status: statusSummary,
      },
      approval_ageing: {
        avg_days_in_submitted:
          avgDaysSubmitted.length > 0
            ? Math.round((avgDaysSubmitted.reduce((s, a) => s + a.days_pending, 0) / avgDaysSubmitted.length) * 10) / 10
            : 0,
        avg_days_in_returned:
          avgDaysReturned.length > 0
            ? Math.round((avgDaysReturned.reduce((s, a) => s + a.days_pending, 0) / avgDaysReturned.length) * 10) / 10
            : 0,
        items_pending_over_5_days: ageingItems.filter((a) => a.days_pending > 5),
      },
      overdue_deliveries: overdueItems,
      top_10_cost_items: top10,
      stock_avoided: {
        count: stockAvoided.length,
        total_value_kes: stockAvoided
          .filter((li) => li.currencyCode === 'KES')
          .reduce((s, li) => s + Number(li.estimatedTotalCost), 0),
        total_value_eur: stockAvoided
          .filter((li) => li.currencyCode === 'EUR')
          .reduce((s, li) => s + Number(li.estimatedTotalCost), 0),
      },
      partial_approval_summary: Array.from(planMap.entries()).map(([tracking_no, counts]) => ({
        tracking_no,
        ...counts,
      })),
    });
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/reports/approval-ageing
reportsRouter.get('/approval-ageing', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const headerFilter: Record<string, unknown> = {};
    // Role-based data filtering
    if (!hasBroadVisibility(req.user)) {
      headerFilter.OR = [
        { createdBy: req.user!.id },
        { departmentManagerId: req.user!.id },
      ];
    }

    const items = await prisma.procurementPlanLineItem.findMany({
      where: {
        status: { in: ['Submitted for Approval', 'Returned for Correction'] },
        deletedAt: null,
        header: headerFilter as any,
      },
      include: {
        header: {
          include: {
            project: true,
            departmentManager: { select: { fullName: true } },
          },
        },
        location: true,
      },
      orderBy: { statusChangedAt: 'asc' },
    });

    const result = items.map((li) => ({
      id: li.id,
      line_item_ref: li.lineItemRef,
      item_description: li.itemDescription,
      status: li.status,
      estimated_total_cost: Number(li.estimatedTotalCost),
      currency_code: li.currencyCode,
      days_in_status: li.statusChangedAt ? Math.ceil(
        (Date.now() - new Date(li.statusChangedAt).getTime()) / (1000 * 60 * 60 * 24)
      ) : 0,
      tracking_no: li.header.trackingNo,
      project_name: li.header.project.projectName,
      approver: li.header.departmentManager.fullName,
      location: li.location.locationName,
    }));

    res.json(result);
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/reports/overdue-deliveries
reportsRouter.get('/overdue-deliveries', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const now = new Date();
    const headerFilter: Record<string, unknown> = {};
    // Role-based data filtering
    if (!hasBroadVisibility(req.user)) {
      headerFilter.OR = [
        { createdBy: req.user!.id },
        { departmentManagerId: req.user!.id },
      ];
    }

    const items = await prisma.procurementPlanLineItem.findMany({
      where: {
        estimatedDeliveryDate: { lt: now },
        status: { notIn: ['Delivered/Closed', 'Cancelled'] },
        deletedAt: null,
        header: headerFilter as any,
      },
      include: {
        header: { include: { project: true } },
        location: true,
      },
      orderBy: { estimatedDeliveryDate: 'asc' },
    });

    res.json(
      items.map((li) => ({
        id: li.id,
        line_item_ref: li.lineItemRef,
        item_description: li.itemDescription,
        estimated_delivery_date: li.estimatedDeliveryDate,
        days_overdue: Math.ceil(
          (now.getTime() - new Date(li.estimatedDeliveryDate!).getTime()) / (1000 * 60 * 60 * 24)
        ),
        quantity: Number(li.quantity),
        delivered_quantity: Number(li.deliveredQuantity),
        delivery_pct: Number(li.quantity) > 0
          ? Math.round((Number(li.deliveredQuantity) / Number(li.quantity)) * 1000) / 10
          : 0,
        estimated_total_cost: Number(li.estimatedTotalCost),
        currency: li.currencyCode,
        location: li.location.locationName,
        tracking_no: li.header.trackingNo,
        project: li.header.project.projectName,
      }))
    );
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/reports/pipeline
reportsRouter.get('/pipeline', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { fiscal_year, project_id } = req.query;

    const where: Record<string, unknown> = { deletedAt: null };
    if (fiscal_year) where.fiscalYear = fiscal_year;

    const headerWhere: Record<string, unknown> = { deletedAt: null };
    if (project_id) headerWhere.projectId = project_id;

    // Role-based data filtering
    if (!hasBroadVisibility(req.user)) {
      headerWhere.OR = [
        { createdBy: req.user!.id },
        { departmentManagerId: req.user!.id },
      ];
    }

    const items = await prisma.procurementPlanLineItem.findMany({
      where: {
        ...where as any,
        header: headerWhere as any,
      },
      select: { status: true, estimatedTotalCost: true, currencyCode: true },
    });

    const pipeline: Record<string, { count: number; value_kes: number; value_eur: number }> = {};
    for (const li of items) {
      if (!pipeline[li.status]) pipeline[li.status] = { count: 0, value_kes: 0, value_eur: 0 };
      pipeline[li.status].count++;
      if (li.currencyCode === 'KES') {
        pipeline[li.status].value_kes += Number(li.estimatedTotalCost);
      } else {
        pipeline[li.status].value_eur += Number(li.estimatedTotalCost);
      }
    }

    res.json(pipeline);
  } catch (err) {
    next(err);
  }
});

// GET /api/v1/reports/stock-avoided
reportsRouter.get('/stock-avoided', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const headerFilter: Record<string, unknown> = {};
    // Role-based data filtering
    if (!hasBroadVisibility(req.user)) {
      headerFilter.OR = [
        { createdBy: req.user!.id },
        { departmentManagerId: req.user!.id },
      ];
    }

    const items = await prisma.procurementPlanLineItem.findMany({
      where: {
        isStockOnHandAvailable: true,
        deletedAt: null,
        header: headerFilter as any,
      },
      include: { location: true },
    });

    const avoided = items.filter((li) => Number(li.quantityAvailable) >= Number(li.quantity));

    res.json({
      count: avoided.length,
      total_value_kes: avoided
        .filter((li) => li.currencyCode === 'KES')
        .reduce((s, li) => s + Number(li.estimatedTotalCost), 0),
      total_value_eur: avoided
        .filter((li) => li.currencyCode === 'EUR')
        .reduce((s, li) => s + Number(li.estimatedTotalCost), 0),
      items: avoided.map((li) => ({
        line_item_ref: li.lineItemRef,
        item_description: li.itemDescription,
        quantity: Number(li.quantity),
        quantity_available: Number(li.quantityAvailable),
        estimated_total_cost: Number(li.estimatedTotalCost),
        currency: li.currencyCode,
        location: li.location.locationName,
      })),
    });
  } catch (err) {
    next(err);
  }
});
