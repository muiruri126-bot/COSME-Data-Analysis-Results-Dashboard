import { Tag } from 'antd';

const STATUS_CONFIG: Record<string, { color: string }> = {
  'Draft': { color: 'default' },
  'Submitted for Approval': { color: 'processing' },
  'Approved': { color: 'success' },
  'Returned for Correction': { color: 'warning' },
  'Cancelled': { color: 'error' },
  'PR Raised': { color: 'purple' },
  'Ordered/Contracted': { color: 'cyan' },
  'Delivery In Progress': { color: 'gold' },
  'Delivered/Closed': { color: 'green' },
  'On Hold': { color: 'orange' },
  // Header statuses
  'Active': { color: 'blue' },
  'Closed': { color: 'green' },
  // Template simple statuses
  'Not started': { color: 'default' },
  'In progress': { color: 'processing' },
  'Modified': { color: 'warning' },
  'Completed': { color: 'success' },
  'Sourcing': { color: 'geekblue' },
};

export function StatusTag({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] || { color: 'default' };
  return <Tag color={config.color}>{status}</Tag>;
}

export function formatCurrency(amount: number, currency = 'KES'): string {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return '—';
  return new Date(date).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}
