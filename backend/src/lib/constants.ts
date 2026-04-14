import { z } from 'zod';

// ============================================================================
// Line Item Statuses
// ============================================================================

export const LINE_ITEM_STATUSES = [
  'Draft',
  'Submitted for Approval',
  'Returned for Correction',
  'Approved',
  'PR Raised',
  'Sourcing',
  'Ordered/Contracted',
  'Delivery In Progress',
  'Delivered/Closed',
  'Cancelled',
] as const;

export type LineItemStatus = (typeof LINE_ITEM_STATUSES)[number];

export const HEADER_STATUSES = ['Draft', 'Active', 'Closed'] as const;
export type HeaderStatus = (typeof HEADER_STATUSES)[number];

// ============================================================================
// Allowed Transitions
// ============================================================================

export const ALLOWED_TRANSITIONS: Record<LineItemStatus, LineItemStatus[]> = {
  'Draft': ['Submitted for Approval', 'Cancelled'],
  'Submitted for Approval': ['Returned for Correction', 'Approved', 'Cancelled'],
  'Returned for Correction': ['Draft', 'Submitted for Approval', 'Cancelled'],
  'Approved': ['PR Raised', 'Cancelled'],
  'PR Raised': ['Sourcing', 'Cancelled'],
  'Sourcing': ['Ordered/Contracted', 'Cancelled'],
  'Ordered/Contracted': ['Delivery In Progress', 'Cancelled'],
  'Delivery In Progress': ['Delivered/Closed', 'Cancelled'],
  'Delivered/Closed': [],
  'Cancelled': [],
};

// ============================================================================
// Role-based Transition Permissions
// ============================================================================

export const TRANSITION_ROLES: Record<string, string[]> = {
  'Draft->Submitted for Approval': ['Project/Department Requester'],
  'Submitted for Approval->Approved': ['Project/Department Manager'],
  'Submitted for Approval->Returned for Correction': ['Project/Department Manager', 'Supply Chain Officer'],
  'Returned for Correction->Draft': ['Project/Department Requester'],
  'Returned for Correction->Submitted for Approval': ['Project/Department Requester'],
  'Approved->PR Raised': ['Supply Chain Officer'],
  'PR Raised->Sourcing': ['Supply Chain Officer'],
  'Sourcing->Ordered/Contracted': ['Supply Chain Officer'],
  'Ordered/Contracted->Delivery In Progress': ['Supply Chain Officer', 'Stores/Inventory Officer'],
  'Delivery In Progress->Delivered/Closed': ['Stores/Inventory Officer'],
  '*->Cancelled': ['Project/Department Manager', 'Supply Chain Officer', 'System Admin'],
};

export function canTransition(
  currentStatus: LineItemStatus,
  targetStatus: LineItemStatus,
  userRoles: string[]
): boolean {
  const allowed = ALLOWED_TRANSITIONS[currentStatus];
  if (!allowed.includes(targetStatus)) return false;

  // Check cancel permission
  if (targetStatus === 'Cancelled') {
    const cancelRoles = TRANSITION_ROLES['*->Cancelled'];
    return userRoles.some((r) => cancelRoles.includes(r) || r === 'System Admin');
  }

  const key = `${currentStatus}->${targetStatus}`;
  const requiredRoles = TRANSITION_ROLES[key];
  if (!requiredRoles) return false;

  return userRoles.some((r) => requiredRoles.includes(r));
}

// ============================================================================
// Quarter Derivation — COSME Fiscal Year (Jul–Jun)
// Q1 = Jul/Aug/Sep, Q2 = Oct/Nov/Dec, Q3 = Jan/Feb/Mar, Q4 = Apr/May/Jun
// ============================================================================

export function deriveQuarter(month: number): string {
  if (month >= 7 && month <= 9) return 'Q1';
  if (month >= 10 && month <= 12) return 'Q2';
  if (month >= 1 && month <= 3) return 'Q3';
  return 'Q4';
}

export function isQuarterConsistent(month: number, quarter: string): boolean {
  return deriveQuarter(month) === quarter;
}

// ============================================================================
// Header Status Derivation
// ============================================================================

export function deriveHeaderStatus(
  lineItemStatuses: string[]
): HeaderStatus {
  if (lineItemStatuses.length === 0) return 'Draft';
  if (lineItemStatuses.every((s) => s === 'Draft')) return 'Draft';
  if (lineItemStatuses.every((s) => s === 'Delivered/Closed' || s === 'Cancelled'))
    return 'Closed';
  return 'Active';
}

// ============================================================================
// Validation Schemas (Zod)
// ============================================================================

export const PLAN_TYPES = ['Project', 'Department'] as const;
export type PlanType = (typeof PLAN_TYPES)[number];

export const createPlanHeaderSchema = z.object({
  tracking_no: z.string().min(1).max(50),
  global_regional_hub: z.string().max(200).optional(),
  country_office: z.string().max(200).optional(),
  project_id: z.string().uuid(),
  type_of_procurement_plan: z.enum(['Project', 'Department']),
  department_manager_id: z.string().uuid(),
  fad_spad_number: z.string().max(100).optional(),
  project_code_cost_centre: z.string().min(1).max(100),
  funding_source_id: z.string().uuid(),
  donor_name: z.string().max(200).optional(),
  financial_year: z.string().max(10).optional(),
  currency: z.string().max(3).default('KES'),
  start_date: z.string().refine((d) => !isNaN(Date.parse(d)), 'Invalid date'),
  end_date: z.string().refine((d) => !isNaN(Date.parse(d)), 'Invalid date'),
});

export const createLineItemSchema = z.object({
  line_item_ref: z.string().min(1).max(50),
  location_id: z.string().uuid(),
  activity_number: z.string().max(100).optional(),
  material_group_id: z.string().uuid(),
  item_description: z.string().min(1),
  uom_id: z.string().uuid(),
  quantity: z.number().positive(),
  currency_code: z.enum(['KES', 'EUR']).default('KES'),
  estimated_unit_price: z.number().min(0),
  estimated_warehousing_cost: z.number().min(0).default(0),
  estimated_transport_cost: z.number().min(0).default(0),
  month: z.number().int().min(1).max(12),
  quarter: z.enum(['Q1', 'Q2', 'Q3', 'Q4']),
  fiscal_year: z.string().min(1).max(10),
  item_type: z.enum(['Stock', 'Asset', 'Service']).optional(),
  is_stock_on_hand_available: z.boolean().default(false),
  quantity_available: z.number().min(0).default(0),
});

export const createPlanWithItemsSchema = createPlanHeaderSchema.extend({
  line_items: z.array(createLineItemSchema).min(1),
});

export const approvalActionSchema = z.object({
  comment: z.string().optional(),
});

export const returnActionSchema = z.object({
  comment: z.string().min(1, 'Comment is mandatory when returning an item'),
});

export const cancelActionSchema = z.object({
  reason: z.string().min(1, 'Reason is mandatory when cancelling an item'),
});

export const createPRSchema = z.object({
  pr_number: z.string().min(1).max(50),
  submitted_date: z.string().refine((d) => !isNaN(Date.parse(d)), 'Invalid date'),
  line_item_ids: z.array(z.string().uuid()).min(1),
  notes: z.string().optional(),
});

export const recordDeliverySchema = z.object({
  delivery_date: z.string().refine((d) => !isNaN(Date.parse(d)), 'Invalid date'),
  quantity_delivered: z.number().positive(),
  delivery_note_ref: z.string().optional(),
  condition_notes: z.string().optional(),
  pr_id: z.string().uuid().optional(),
});

export const updateSourcingSchema = z.object({
  line_items: z.array(
    z.object({
      line_item_id: z.string().uuid(),
      sourcing_method_id: z.string().uuid().optional(),
      lta_reference_number: z.string().optional(),
      sourcing_location: z.string().optional(),
      sourcing_plan: z.string().optional(),
      estimated_delivery_date: z.string().optional(),
      status: z.enum(['Sourcing', 'Ordered/Contracted']).optional(),
    })
  ).min(1),
});
