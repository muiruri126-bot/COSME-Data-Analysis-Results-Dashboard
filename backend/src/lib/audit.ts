import prisma from './prisma';

export async function createAuditLog(params: {
  entityType: string;
  entityId: string;
  action: string;
  fieldName?: string;
  oldValue?: string;
  newValue?: string;
  performedBy: string;
  ipAddress?: string;
  userAgent?: string;
}): Promise<void> {
  await prisma.auditLog.create({
    data: {
      entityType: params.entityType,
      entityId: params.entityId,
      action: params.action,
      fieldName: params.fieldName,
      oldValue: params.oldValue,
      newValue: params.newValue,
      performedBy: params.performedBy,
      ipAddress: params.ipAddress,
      userAgent: params.userAgent,
    },
  });
}

export async function createAuditLogForUpdate(params: {
  entityType: string;
  entityId: string;
  performedBy: string;
  changes: Record<string, { old: unknown; new: unknown }>;
  ipAddress?: string;
}): Promise<void> {
  const entries = Object.entries(params.changes);
  if (entries.length === 0) return;

  await prisma.auditLog.createMany({
    data: entries.map(([field, vals]) => ({
      entityType: params.entityType,
      entityId: params.entityId,
      action: 'UPDATE',
      fieldName: field,
      oldValue: vals.old != null ? String(vals.old) : null,
      newValue: vals.new != null ? String(vals.new) : null,
      performedBy: params.performedBy,
      ipAddress: params.ipAddress,
    })),
  });
}
