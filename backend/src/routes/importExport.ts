import { Router, Response, NextFunction } from 'express';
import multer from 'multer';
import ExcelJS from 'exceljs';
import csvParser from 'csv-parser';
import { Readable } from 'stream';
import prisma from '../lib/prisma';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { AppError } from '../middleware/errorHandler';
import { Decimal } from '@prisma/client/runtime/library';
import { createAuditLog } from '../lib/audit';

const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 5 * 1024 * 1024 } });

export const importExportRouter = Router();
importExportRouter.use(authenticate);

// ─── EXPORT ───────────────────────────────────────────────────────

// GET /api/v1/import-export/export/:planId
importExportRouter.get(
  '/export/:planId',
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const plan = await prisma.procurementPlanHeader.findUnique({
        where: { id: req.params.planId as string, deletedAt: null },
        include: {
          project: true,
          departmentManager: { select: { fullName: true } },
          fundingSource: true,
          lineItems: {
            where: { deletedAt: null },
            include: {
              materialGroup: true,
              location: true,
              uom: true,
              sourcingMethod: true,
              approvals: {
                include: {
                  approver: { select: { fullName: true } },
                  step: true,
                },
                orderBy: { decidedAt: 'asc' },
              },
            },
            orderBy: { lineItemRef: 'asc' },
          },
        },
      });
      if (!plan) throw new AppError('Procurement plan not found', 404);

      const workbook = new ExcelJS.Workbook();
      workbook.creator = 'COSME Procurement Tracker';
      workbook.created = new Date();

      // Sheet 1: Plan Header
      const headerSheet = workbook.addWorksheet('Plan Header');
      headerSheet.columns = [
        { header: 'Field', key: 'field', width: 30 },
        { header: 'Value', key: 'value', width: 50 },
      ];
      headerSheet.addRows([
        { field: 'Tracking No', value: plan.trackingNo },
        { field: 'Type', value: plan.typeOfProcurementPlan },
        { field: 'Project', value: plan.project.projectName },
        { field: 'Project Code / Cost Centre', value: plan.projectCodeCostCentre },
        { field: 'Funding Source', value: plan.fundingSource.sourceName },
        { field: 'Donor', value: plan.donorName },
        { field: 'Department Manager', value: plan.departmentManager?.fullName },
        { field: 'Header Status', value: plan.headerStatus },
        { field: 'Start Date', value: plan.startDate.toISOString().split('T')[0] },
        { field: 'End Date', value: plan.endDate.toISOString().split('T')[0] },
        { field: 'Total Items', value: plan.lineItems.length },
        { field: 'Created', value: plan.createdAt.toISOString() },
      ]);

      // Sheet 2: Line Items
      const itemsSheet = workbook.addWorksheet('Line Items');
      itemsSheet.columns = [
        { header: 'Ref', key: 'lineItemRef', width: 18 },
        { header: 'Material Group', key: 'materialGroup', width: 20 },
        { header: 'Item Type', key: 'itemType', width: 12 },
        { header: 'Description', key: 'itemDescription', width: 40 },
        { header: 'Qty', key: 'quantity', width: 8 },
        { header: 'UoM', key: 'uom', width: 10 },
        { header: 'Unit Price', key: 'unitPrice', width: 12 },
        { header: 'Currency', key: 'currency', width: 8 },
        { header: 'Warehousing Cost', key: 'warehousing', width: 16 },
        { header: 'Transport Cost', key: 'transport', width: 14 },
        { header: 'Est. Total Item/Svc', key: 'estItemSvc', width: 16 },
        { header: 'Est. Total Cost', key: 'estTotal', width: 16 },
        { header: 'Month', key: 'month', width: 6 },
        { header: 'Quarter', key: 'quarter', width: 8 },
        { header: 'Fiscal Year', key: 'fiscalYear', width: 10 },
        { header: 'Status', key: 'status', width: 22 },
        { header: 'Sourcing Method', key: 'sourcingMethod', width: 18 },
        { header: 'Location', key: 'location', width: 18 },
        { header: 'Est. Delivery Date', key: 'estDelivery', width: 16 },
        { header: 'Delivered Qty', key: 'deliveredQty', width: 12 },
        { header: 'PR Number', key: 'prNumber', width: 14 },
        { header: 'Stock Available?', key: 'stockAvailable', width: 14 },
      ];

      for (const li of plan.lineItems) {
        itemsSheet.addRow({
          lineItemRef: li.lineItemRef,
          materialGroup: li.materialGroup?.groupName,
          itemType: li.itemType,
          itemDescription: li.itemDescription,
          quantity: Number(li.quantity),
          uom: li.uom?.uomName,
          unitPrice: Number(li.estimatedUnitPrice),
          currency: li.currencyCode,
          warehousing: Number(li.estimatedWarehousingCost),
          transport: Number(li.estimatedTransportCost),
          estItemSvc: Number(li.estimatedTotalItemServiceCost),
          estTotal: Number(li.estimatedTotalCost),
          month: li.month,
          quarter: li.quarter,
          fiscalYear: li.fiscalYear,
          status: li.status,
          sourcingMethod: li.sourcingMethod?.methodName,
          location: li.location?.locationName,
          estDelivery: li.estimatedDeliveryDate?.toISOString().split('T')[0],
          deliveredQty: Number(li.deliveredQuantity),
          prNumber: li.prNumber,
          stockAvailable: li.isStockOnHandAvailable ? 'Yes' : 'No',
        });
      }

      // Style header row
      itemsSheet.getRow(1).font = { bold: true };
      itemsSheet.getRow(1).fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FF4472C4' },
      };
      itemsSheet.getRow(1).font = { bold: true, color: { argb: 'FFFFFFFF' } };

      // Sheet 3: Approval Trail
      const approvalSheet = workbook.addWorksheet('Approval Trail');
      approvalSheet.columns = [
        { header: 'Line Item Ref', key: 'ref', width: 18 },
        { header: 'Step', key: 'step', width: 6 },
        { header: 'Approver', key: 'approver', width: 25 },
        { header: 'Decision', key: 'decision', width: 14 },
        { header: 'Date', key: 'date', width: 20 },
        { header: 'Comments', key: 'comments', width: 40 },
      ];

      for (const li of plan.lineItems) {
        for (const a of li.approvals) {
          approvalSheet.addRow({
            ref: li.lineItemRef,
            step: a.step?.stepOrder,
            approver: a.approver?.fullName,
            decision: a.decision,
            date: a.decidedAt.toISOString(),
            comments: a.comments,
          });
        }
      }

      approvalSheet.getRow(1).font = { bold: true };

      // Send workbook
      res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
      res.setHeader('Content-Disposition', `attachment; filename="PP_${plan.trackingNo}_export.xlsx"`);

      await workbook.xlsx.write(res);
      res.end();
    } catch (err) {
      next(err);
    }
  }
);

// ─── IMPORT ───────────────────────────────────────────────────────

// POST /api/v1/import-export/import/:planId — Import line items from CSV/Excel
importExportRouter.post(
  '/import/:planId',
  authorize('Requester', 'Supply Chain Officer', 'System Admin'),
  upload.single('file'),
  async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      if (!req.file) throw new AppError('File is required', 400);

      const plan = await prisma.procurementPlanHeader.findUnique({
        where: { id: req.params.planId as string, deletedAt: null },
        include: { lineItems: { where: { deletedAt: null }, orderBy: { lineItemRef: 'desc' }, take: 1 } },
      });
      if (!plan) throw new AppError('Procurement plan not found', 404);

      let rows: Record<string, string>[] = [];

      // Parse based on file type
      if (req.file.mimetype === 'text/csv' || req.file.originalname.endsWith('.csv')) {
        rows = await parseCsv(req.file.buffer as any);
      } else if (
        req.file.mimetype === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        req.file.originalname.endsWith('.xlsx')
      ) {
        rows = await parseExcel(req.file.buffer as any);
      } else {
        throw new AppError('Only CSV and XLSX files are supported for import', 400);
      }

      // Determine next line item ref number
      const lastRef = plan.lineItems[0]?.lineItemRef;
      let nextNum = 1;
      if (lastRef) {
        const parts = lastRef.split('-');
        const lastNum = parseInt(parts[parts.length - 1]);
        if (!isNaN(lastNum)) nextNum = lastNum + 1;
      }

      const results: { row: number; status: 'created' | 'error'; ref?: string; error?: string }[] = [];

      // Load lookups
      const materialGroups = await prisma.materialGroup.findMany();
      const uoms = await prisma.unitOfMeasure.findMany();
      const sourcingMethods = await prisma.sourcingMethod.findMany();
      const locations = await prisma.location.findMany();

      const mgMap = new Map(materialGroups.map((m) => [m.groupName.toLowerCase(), m.id]));
      const uomMap = new Map(uoms.map((u) => [u.uomName.toLowerCase(), u.id]));
      const smMap = new Map(sourcingMethods.map((s) => [s.methodName.toLowerCase(), s.id]));
      const locMap = new Map(locations.map((l) => [l.locationName.toLowerCase(), l.id]));

      // Get a default location from the first existing line item of this plan
      const existingItem = await prisma.procurementPlanLineItem.findFirst({
        where: { headerId: plan.id, deletedAt: null },
        select: { locationId: true, fiscalYear: true, quarter: true, month: true },
      });

      for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        try {
          const itemDescription = row['item_description'] || row['description'];
          if (!itemDescription?.trim()) {
            results.push({ row: i + 1, status: 'error', error: 'item_description is required' });
            continue;
          }

          const quantity = parseFloat(row['quantity'] || '1');
          const unitPrice = parseFloat(row['unit_price'] || row['estimated_unit_price'] || '0');
          const warehousing = parseFloat(row['warehousing_cost'] || row['estimated_warehousing_cost'] || '0');
          const transport = parseFloat(row['transport_cost'] || row['estimated_transport_cost'] || '0');
          const currency = (row['currency'] || row['currency_code'] || 'KES').toUpperCase();
          const month = parseInt(row['month'] || String(existingItem?.month || 1));
          const quarter = row['quarter'] || existingItem?.quarter || 'Q1';
          const fiscalYear = row['fiscal_year'] || existingItem?.fiscalYear || new Date().getFullYear().toString();

          if (isNaN(quantity) || quantity <= 0) {
            results.push({ row: i + 1, status: 'error', error: 'Invalid quantity' });
            continue;
          }

          const materialGroupId = row['material_group'] ? mgMap.get(row['material_group'].toLowerCase()) : materialGroups[0]?.id;
          const uomId = row['uom'] || row['unit_of_measure'] ? uomMap.get((row['uom'] || row['unit_of_measure']).toLowerCase()) : uoms[0]?.id;
          const sourcingMethodId = row['sourcing_method'] ? smMap.get(row['sourcing_method'].toLowerCase()) : undefined;
          const locationId = row['location'] ? locMap.get(row['location'].toLowerCase()) : existingItem?.locationId;

          if (!materialGroupId) {
            results.push({ row: i + 1, status: 'error', error: 'material_group is required or no default available' });
            continue;
          }
          if (!uomId) {
            results.push({ row: i + 1, status: 'error', error: 'uom is required or no default available' });
            continue;
          }
          if (!locationId) {
            results.push({ row: i + 1, status: 'error', error: 'location is required or no default available' });
            continue;
          }

          const lineRef = `${plan.trackingNo}-${String(nextNum).padStart(3, '0')}`;

          await prisma.procurementPlanLineItem.create({
            data: {
              headerId: plan.id,
              lineItemRef: lineRef,
              locationId,
              materialGroupId,
              itemType: row['item_type'] || 'Good',
              itemDescription: itemDescription.trim(),
              uomId,
              quantity: new Decimal(quantity),
              currencyCode: currency,
              estimatedUnitPrice: new Decimal(unitPrice),
              estimatedWarehousingCost: new Decimal(warehousing),
              estimatedTransportCost: new Decimal(transport),
              month,
              quarter,
              fiscalYear,
              status: 'Draft',
              sourcingMethodId: sourcingMethodId || undefined,
              isStockOnHandAvailable: (row['stock_available'] || '').toLowerCase() === 'yes',
              createdBy: req.user!.id,
            },
          });

          results.push({ row: i + 1, status: 'created', ref: lineRef });
          nextNum++;
        } catch (err: any) {
          results.push({ row: i + 1, status: 'error', error: err.message });
        }
      }

      const created = results.filter((r) => r.status === 'created').length;
      const errors = results.filter((r) => r.status === 'error').length;

      if (created > 0) {
        await createAuditLog({
          entityType: 'procurement_plan',
          entityId: plan.id,
          action: 'IMPORT',
          fieldName: 'line_items',
          newValue: `${created} items imported from ${req.file.originalname}`,
          performedBy: req.user!.id,
        });
      }

      res.json({
        total_rows: rows.length,
        created,
        errors,
        details: results,
      });
    } catch (err) {
      next(err);
    }
  }
);

// CSV parser helper
function parseCsv(buffer: any): Promise<Record<string, string>[]> {
  return new Promise((resolve, reject) => {
    const rows: Record<string, string>[] = [];
    const stream = Readable.from(buffer);
    stream
      .pipe(csvParser())
      .on('data', (row) => rows.push(row))
      .on('end', () => resolve(rows))
      .on('error', reject);
  });
}

// Excel parser helper
async function parseExcel(buffer: any): Promise<Record<string, string>[]> {
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.load(buffer);
  const sheet = workbook.worksheets[0];

  if (!sheet || sheet.rowCount < 2) return [];

  const headers: string[] = [];
  sheet.getRow(1).eachCell((cell, colNumber) => {
    headers[colNumber - 1] = String(cell.value || '')
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '_');
  });

  const rows: Record<string, string>[] = [];
  for (let i = 2; i <= sheet.rowCount; i++) {
    const row: Record<string, string> = {};
    sheet.getRow(i).eachCell((cell, colNumber) => {
      const header = headers[colNumber - 1];
      if (header) {
        row[header] = String(cell.value ?? '');
      }
    });
    if (Object.values(row).some((v) => v.trim())) {
      rows.push(row);
    }
  }

  return rows;
}
