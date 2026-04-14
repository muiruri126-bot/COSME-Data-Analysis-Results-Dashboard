# COSME Procurement Tracking System — Complete System Design

---

## A) Solution Overview

The COSME Procurement Tracking System (CPTS) is a web-based, multi-currency procurement lifecycle management platform designed for the COSME donor-funded project (components: COSME NBS, COSME Economic Empowerment, COSME GEI, COSME MERL). It tracks procurement from initial planning through delivery and stock receipt, with line-item-level approvals, full audit trails, and donor-ready reporting (GAC and other donors).

The system enforces Role-Based Access Control (RBAC) with field-level edit permissions across six core roles (Project/Department Requester, Project/Department Manager, Supply Chain Officer, Stores/Inventory Officer, Finance/Grants, System Admin). Its distinguishing architecture decision is **line-item-level approval**: each procurement plan may contain many line items, and each line item independently progresses through its own approval workflow and lifecycle — from Draft through Delivered/Closed — with configurable multi-step approval rules based on cost thresholds, procurement type, sourcing method, material group, and location (Kilifi Office, Kwale Office). The plan header status is derived automatically from the aggregate state of its line items, ensuring accurate mixed-state visibility (e.g., "10 approved, 2 returned, 1 draft"). All monetary values support dual-currency (KES/EUR) with date-effective exchange rates and automatic roll-up conversions for donor reporting.

---

## B) Data Model

### B.1 Entity/Table List

| # | Table Name | Purpose |
|---|-----------|---------|
| 1 | `projects` | Project/department master (COSME NBS, COSME EE, COSME GEI, COSME MERL) |
| 2 | `locations` | Delivery/implementation locations (Kilifi Office, Kwale Office, etc.) |
| 3 | `funding_sources` | Funding source/donor master (Grant, GAC, etc.) |
| 4 | `material_groups` | Material group lookup (consultancy, travel, equipment, seedlings, etc.) |
| 5 | `units_of_measure` | UoM lookup (each, lot, day, trip, kg, etc.) |
| 6 | `users` | System users with authentication |
| 7 | `roles` | Role definitions |
| 8 | `user_roles` | User-role assignments (M:N) |
| 9 | `permissions` | Granular permissions per role |
| 10 | `procurement_plan_headers` | Procurement plan metadata (tracking no., project, dates, funding) |
| 11 | `procurement_plan_line_items` | Individual line items with planning/budgeting data and lifecycle status |
| 12 | `line_item_approval_rules` | Configurable approval routing rules (thresholds, type, method, etc.) |
| 13 | `line_item_approval_steps` | Defined approval steps per rule (sequential/parallel) |
| 14 | `line_item_approvals` | Actual approval decisions per line item per step (append-only history) |
| 15 | `purchase_requisitions` | PR records raised by Supply Chain |
| 16 | `pr_line_items` | Join table: PR ↔ line items (M:N) |
| 17 | `deliveries` | Delivery records (partial deliveries allowed per line item) |
| 18 | `stock_assets` | Stock on-hand / asset tracking post-delivery |
| 19 | `exchange_rates` | Date-effective exchange rates (KES/EUR) |
| 20 | `attachments` | File uploads per line item or PR |
| 21 | `comments` | Comments per line item, PR, or approval action |
| 22 | `audit_log` | Immutable audit trail for all changes |
| 23 | `fiscal_periods` | Month/Quarter/FY definitions |
| 24 | `sourcing_methods` | Sourcing method lookup (LTA, competitive quotation, direct, etc.) |

### B.2 ERD Description (Relationships)

```
projects 1──∞ procurement_plan_headers
locations 1──∞ procurement_plan_line_items
funding_sources 1──∞ procurement_plan_headers
material_groups 1──∞ procurement_plan_line_items
units_of_measure 1──∞ procurement_plan_line_items
sourcing_methods 1──∞ procurement_plan_line_items

procurement_plan_headers 1──∞ procurement_plan_line_items

procurement_plan_line_items 1──∞ line_item_approvals
procurement_plan_line_items ∞──∞ purchase_requisitions (via pr_line_items)
procurement_plan_line_items 1──∞ deliveries
procurement_plan_line_items 1──∞ stock_assets
procurement_plan_line_items 1──∞ attachments
procurement_plan_line_items 1──∞ comments

line_item_approval_rules 1──∞ line_item_approval_steps
line_item_approval_steps 1──∞ line_item_approvals

purchase_requisitions 1──∞ pr_line_items
purchase_requisitions 1──∞ attachments
purchase_requisitions 1──∞ comments

users 1──∞ line_item_approvals (as approver)
users 1──∞ audit_log (as actor)
users ∞──∞ roles (via user_roles)
roles 1──∞ permissions

exchange_rates (standalone; queried by date + currency pair)
fiscal_periods (standalone; queried by month)
```

### B.3 Key Fields Per Table

#### `projects`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_name | VARCHAR(200) NOT NULL | e.g., "COSME NBS" |
| project_code | VARCHAR(50) NOT NULL UNIQUE | e.g., "FECNO" |
| department_manager_id | UUID FK → users | |
| start_date | DATE | |
| end_date | DATE | |
| is_active | BOOLEAN DEFAULT true | |
| created_at / updated_at | TIMESTAMPTZ | |

#### `locations`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| location_name | VARCHAR(200) NOT NULL UNIQUE | e.g., "Kilifi Office" |
| is_active | BOOLEAN DEFAULT true | |

#### `funding_sources`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| source_name | VARCHAR(200) NOT NULL | e.g., "Grant" |
| donor_name | VARCHAR(200) | e.g., "GAC" |
| is_active | BOOLEAN DEFAULT true | |

#### `material_groups`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| group_number | VARCHAR(50) NOT NULL UNIQUE | Material Group Number |
| group_name | VARCHAR(200) NOT NULL | e.g., "Consultancy/Professional Services" |
| is_active | BOOLEAN DEFAULT true | |

#### `units_of_measure`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| uom_code | VARCHAR(20) NOT NULL UNIQUE | e.g., "EA", "LOT", "DAY" |
| uom_name | VARCHAR(100) NOT NULL | |

#### `procurement_plan_headers`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tracking_no | VARCHAR(50) NOT NULL UNIQUE | "Procurement Plan Reference Tracking No." e.g., PP0374 |
| project_id | UUID FK → projects NOT NULL | "Project/ Department Name" |
| type_of_procurement_plan | VARCHAR(100) NOT NULL | "Type of Procurement Plan" |
| department_manager_id | UUID FK → users NOT NULL | "Dept./ Project Manager" |
| fad_spad_number | VARCHAR(100) | "FAD/SPAD Number" |
| project_code_cost_centre | VARCHAR(100) NOT NULL | "Project Code/ Cost Centre" e.g., FECNO |
| funding_source_id | UUID FK → funding_sources NOT NULL | "Funding Source" |
| donor_name | VARCHAR(200) | "Donor Name" (denormalized for flexibility) |
| start_date | DATE NOT NULL | "Start Date" |
| end_date | DATE NOT NULL | "End Date" |
| header_status | VARCHAR(20) DEFAULT 'Draft' | Derived: Draft / Active / Closed |
| created_by | UUID FK → users | |
| created_at | TIMESTAMPTZ DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ DEFAULT NOW() | |
| deleted_at | TIMESTAMPTZ NULL | Soft delete |

**Calculated (virtual/view):**
- `days_remaining_until_project_end_date` = `end_date - CURRENT_DATE` (exposed in API/view, not stored)

**Indexes:**
- UNIQUE on `tracking_no`
- INDEX on `project_id`, `funding_source_id`, `header_status`, `start_date`, `end_date`
- INDEX on `donor_name`

#### `procurement_plan_line_items`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | System-generated "Line Item ID" |
| header_id | UUID FK → procurement_plan_headers NOT NULL | |
| line_item_ref | VARCHAR(50) NOT NULL | e.g., "PP0374-001" (unique per header) |
| location_id | UUID FK → locations NOT NULL | "Implementation or Delivery Location" |
| activity_number | VARCHAR(100) | "Activity Number" |
| material_group_id | UUID FK → material_groups NOT NULL | "Material Group" |
| item_description | TEXT NOT NULL | "Item Description" |
| uom_id | UUID FK → units_of_measure NOT NULL | "UoM" |
| quantity | DECIMAL(15,4) NOT NULL CHECK (quantity > 0) | "Quantity" |
| currency_code | VARCHAR(3) NOT NULL DEFAULT 'KES' | 'KES' or 'EUR' |
| estimated_unit_price | DECIMAL(18,4) NOT NULL CHECK (≥ 0) | "Estimated Unit Price" |
| estimated_total_item_service_cost | DECIMAL(18,4) GENERATED ALWAYS AS (quantity * estimated_unit_price) STORED | "Estimated Total Item/Service Cost" |
| estimated_warehousing_cost | DECIMAL(18,4) DEFAULT 0 CHECK (≥ 0) | "Estimated Warehousing Cost" |
| estimated_transport_cost | DECIMAL(18,4) DEFAULT 0 CHECK (≥ 0) | "Estimated Transport Cost" |
| estimated_total_cost | DECIMAL(18,4) GENERATED ALWAYS AS (quantity * estimated_unit_price + estimated_warehousing_cost + estimated_transport_cost) STORED | "Estimated Total Cost" |
| month | INTEGER NOT NULL CHECK (1-12) | "Month" |
| quarter | VARCHAR(5) NOT NULL | "Quarter" (Q1-Q4) |
| fiscal_year | VARCHAR(10) NOT NULL | "FY" e.g., "FY2025" |
| status | VARCHAR(30) NOT NULL DEFAULT 'Draft' | Line item lifecycle status |
| pr_number | VARCHAR(50) | "PR Number" (denormalized for quick access) |
| pr_submitted_date | DATE | "PR Submitted Date" |
| estimated_delivery_date | DATE | "Estimated Delivery Date" |
| is_stock_on_hand_available | BOOLEAN DEFAULT false | "Is there available Stock on-hand/Asset?" |
| quantity_available | DECIMAL(15,4) DEFAULT 0 | "Quantity Available" |
| item_type | VARCHAR(50) | "Type" (Stock/Asset/Service) |
| sourcing_location | VARCHAR(200) | "Sourcing Location" |
| sourcing_method_id | UUID FK → sourcing_methods | "Sourcing Method" |
| lta_reference_number | VARCHAR(100) | "LTA Reference Number" |
| estimated_delivery_needed | TEXT | "Estimated Delivery Needed" |
| actual_delivery_date | DATE | "Actual Delivery" |
| stock_on_hand_asset_post | TEXT | "Stock on-hand/Asset" (post-delivery update) |
| sourcing_plan | TEXT | "Sourcing Plan" |
| delivered_quantity | DECIMAL(15,4) DEFAULT 0 | Internal tracker (partial delivery sum) |
| created_by | UUID FK → users | |
| created_at | TIMESTAMPTZ DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ DEFAULT NOW() | |
| deleted_at | TIMESTAMPTZ NULL | Soft delete |

**Constraints:**
- UNIQUE (header_id, line_item_ref)
- CHECK quantity > 0
- CHECK estimated_unit_price >= 0
- CHECK estimated_warehousing_cost >= 0
- CHECK estimated_transport_cost >= 0
- CHECK quantity_available >= 0
- CHECK delivered_quantity >= 0
- CHECK month BETWEEN 1 AND 12
- CHECK quarter IN ('Q1','Q2','Q3','Q4')
- CHECK currency_code IN ('KES','EUR')
- CHECK status IN ('Draft','Submitted for Approval','Returned for Correction','Approved','PR Raised','Sourcing','Ordered/Contracted','Delivery In Progress','Delivered/Closed','Cancelled')

**Auto-calculations (enforced):**
- `estimated_total_item_service_cost` = `quantity * estimated_unit_price` (generated column)
- `estimated_total_cost` = `estimated_total_item_service_cost + estimated_warehousing_cost + estimated_transport_cost` (generated column)
- Quarter auto-derived from Month in application layer; validated for consistency

**Indexes:**
- INDEX on (header_id)
- UNIQUE on (header_id, line_item_ref)
- INDEX on status
- INDEX on month, quarter, fiscal_year
- INDEX on location_id
- INDEX on material_group_id
- INDEX on pr_number
- INDEX on currency_code
- INDEX on sourcing_method_id
- INDEX on estimated_delivery_date (for overdue queries)

#### `line_item_approval_rules`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| rule_name | VARCHAR(200) NOT NULL | |
| cost_threshold_min | DECIMAL(18,4) | Match if estimated_total_cost >= this |
| cost_threshold_max | DECIMAL(18,4) | Match if estimated_total_cost <= this |
| cost_threshold_currency | VARCHAR(3) | Currency for threshold comparison |
| item_type | VARCHAR(50) | Match by Type (Stock/Asset/Service) |
| sourcing_method_id | UUID FK → sourcing_methods | Match by sourcing method |
| material_group_id | UUID FK → material_groups | Match by material group |
| location_id | UUID FK → locations | Match by location |
| priority | INTEGER DEFAULT 0 | Higher = evaluated first |
| is_active | BOOLEAN DEFAULT true | |
| created_at / updated_at | TIMESTAMPTZ | |

#### `line_item_approval_steps`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| rule_id | UUID FK → line_item_approval_rules NOT NULL | |
| step_order | INTEGER NOT NULL | Sequence (1, 2, 3…) |
| approver_role_id | UUID FK → roles | Role that can approve at this step |
| specific_approver_id | UUID FK → users | Specific approver (optional, overrides role) |
| is_parallel | BOOLEAN DEFAULT false | If true, all parallel steps at same order must approve |
| can_delegate | BOOLEAN DEFAULT true | Allow delegation at this step |
| created_at | TIMESTAMPTZ | |

#### `line_item_approvals`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| line_item_id | UUID FK → procurement_plan_line_items NOT NULL | |
| step_id | UUID FK → line_item_approval_steps NOT NULL | |
| approver_id | UUID FK → users NOT NULL | Who actually approved |
| delegated_from_id | UUID FK → users | Original approver if delegated |
| decision | VARCHAR(20) NOT NULL | 'Approved', 'Returned', 'Cancelled', 'Escalated' |
| comments | TEXT | Mandatory for Return/Cancel |
| decided_at | TIMESTAMPTZ NOT NULL DEFAULT NOW() | |
| created_at | TIMESTAMPTZ DEFAULT NOW() | |

**Append-only** — no updates or deletes to preserve history.

**Indexes:**
- INDEX on line_item_id
- INDEX on approver_id
- INDEX on decided_at
- INDEX on decision

#### `purchase_requisitions`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| pr_number | VARCHAR(50) NOT NULL UNIQUE | "PR Number" |
| submitted_date | DATE NOT NULL | "PR Submitted Date" |
| submitted_by | UUID FK → users NOT NULL | |
| status | VARCHAR(30) DEFAULT 'Open' | Open / Sourcing / Ordered / Closed / Cancelled |
| notes | TEXT | |
| created_at / updated_at | TIMESTAMPTZ | |

#### `pr_line_items` (join table)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| pr_id | UUID FK → purchase_requisitions NOT NULL | |
| line_item_id | UUID FK → procurement_plan_line_items NOT NULL | |
| created_at | TIMESTAMPTZ DEFAULT NOW() | |

**Constraint:** UNIQUE (pr_id, line_item_id)

#### `deliveries`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| line_item_id | UUID FK → procurement_plan_line_items NOT NULL | |
| pr_id | UUID FK → purchase_requisitions | If linked to PR |
| delivery_date | DATE NOT NULL | |
| quantity_delivered | DECIMAL(15,4) NOT NULL CHECK (> 0) | |
| received_by | UUID FK → users | Stores/Inventory Officer |
| delivery_note_ref | VARCHAR(200) | |
| condition_notes | TEXT | |
| created_at | TIMESTAMPTZ DEFAULT NOW() | |

**Trigger/application logic:** After INSERT, update `procurement_plan_line_items.delivered_quantity` += quantity_delivered.

#### `stock_assets`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| line_item_id | UUID FK → procurement_plan_line_items | |
| item_description | TEXT NOT NULL | |
| item_type | VARCHAR(50) NOT NULL | Stock / Asset |
| quantity_on_hand | DECIMAL(15,4) NOT NULL DEFAULT 0 | |
| location_id | UUID FK → locations | |
| last_checked_date | DATE | |
| last_updated_by | UUID FK → users | |
| asset_tag | VARCHAR(100) | For assets |
| created_at / updated_at | TIMESTAMPTZ | |

#### `exchange_rates`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| from_currency | VARCHAR(3) NOT NULL | e.g., 'EUR' |
| to_currency | VARCHAR(3) NOT NULL | e.g., 'KES' |
| rate | DECIMAL(18,6) NOT NULL CHECK (> 0) | |
| effective_date | DATE NOT NULL | |
| created_by | UUID FK → users | |
| created_at | TIMESTAMPTZ DEFAULT NOW() | |

**Constraint:** UNIQUE (from_currency, to_currency, effective_date)
**Index:** INDEX on (from_currency, to_currency, effective_date DESC)

#### `attachments`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| entity_type | VARCHAR(50) NOT NULL | 'line_item', 'purchase_requisition', 'delivery' |
| entity_id | UUID NOT NULL | FK to relevant table |
| file_name | VARCHAR(500) NOT NULL | |
| file_path | VARCHAR(1000) NOT NULL | Server/S3 path |
| file_size | BIGINT | |
| mime_type | VARCHAR(100) | |
| uploaded_by | UUID FK → users NOT NULL | |
| created_at | TIMESTAMPTZ DEFAULT NOW() | |

**Index:** INDEX on (entity_type, entity_id)

#### `comments`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| entity_type | VARCHAR(50) NOT NULL | 'line_item', 'purchase_requisition', 'approval' |
| entity_id | UUID NOT NULL | |
| author_id | UUID FK → users NOT NULL | |
| comment_text | TEXT NOT NULL | |
| created_at | TIMESTAMPTZ DEFAULT NOW() | |

**Index:** INDEX on (entity_type, entity_id)

#### `audit_log`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| entity_type | VARCHAR(50) NOT NULL | Table name affected |
| entity_id | UUID NOT NULL | Record ID |
| action | VARCHAR(20) NOT NULL | 'CREATE', 'UPDATE', 'DELETE', 'STATUS_CHANGE', 'APPROVAL' |
| field_name | VARCHAR(100) | Which field changed |
| old_value | TEXT | |
| new_value | TEXT | |
| performed_by | UUID FK → users NOT NULL | |
| performed_at | TIMESTAMPTZ DEFAULT NOW() | |
| ip_address | VARCHAR(45) | |
| user_agent | TEXT | |

**Index:** INDEX on (entity_type, entity_id, performed_at)
**Partition:** Consider partitioning by month for large volumes.

#### `users`, `roles`, `user_roles`, `permissions`
Standard RBAC tables:
- `users`: id, email, full_name, password_hash, is_active, last_login, created_at
- `roles`: id, role_name (Project/Department Requester, Project/Department Manager, Supply Chain Officer, Stores/Inventory Officer, Finance/Grants, System Admin)
- `user_roles`: id, user_id FK, role_id FK, project_id FK (optional, for project-scoped roles)
- `permissions`: id, role_id FK, resource (table/entity), action (create/read/update/delete/approve/submit), field_restrictions (JSONB — list of fields editable)

#### `fiscal_periods`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| month | INTEGER NOT NULL | 1-12 |
| quarter | VARCHAR(5) NOT NULL | Q1-Q4 |
| fiscal_year | VARCHAR(10) NOT NULL | FY2025, FY2026 |
| start_date | DATE NOT NULL | |
| end_date | DATE NOT NULL | |

#### `sourcing_methods`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| method_name | VARCHAR(200) NOT NULL UNIQUE | e.g., "LTA", "Competitive Quotation", "Direct Procurement" |
| is_active | BOOLEAN DEFAULT true | |

---

## C) Workflow

### C.1 Line Item Status Definitions

| Status | Meaning | Who Sets |
|--------|---------|----------|
| **Draft** | Line item created, planning data being entered | Project/Department Requester |
| **Submitted for Approval** | Sent to approver(s) for review | Project/Department Requester |
| **Returned for Correction** | Approver found issues; returned with comments | Project/Department Manager or higher approver |
| **Approved** | All required approval steps completed | Last approver in chain |
| **PR Raised** | Supply Chain has created a PR for this item | Supply Chain Officer |
| **Sourcing** | Active sourcing/quotation process | Supply Chain Officer |
| **Ordered/Contracted** | PO or contract issued | Supply Chain Officer |
| **Delivery In Progress** | Goods/services dispatched, awaiting receipt | Supply Chain / Stores |
| **Delivered/Closed** | Fully received and confirmed | Stores Officer |
| **Cancelled** | Cancelled with reason recorded | Any authorized approver/admin |

### C.2 Header Derived Status Logic

```
IF all line items are in Draft status → Header Status = "Draft"
ELSE IF all line items are in (Delivered/Closed OR Cancelled) → Header Status = "Closed"
ELSE → Header Status = "Active"
```

The header status is **never set manually** — it is computed from the aggregate state of its line items whenever queried or via a database trigger/view.

### C.3 Allowed Transitions (Matrix)

| From → To | Draft | Submitted | Returned | Approved | PR Raised | Sourcing | Ordered | Delivery IP | Delivered | Cancelled |
|-----------|-------|-----------|----------|----------|-----------|----------|---------|-------------|-----------|-----------|
| **Draft** | – | ✅ | – | – | – | – | – | – | – | ✅ |
| **Submitted** | – | – | ✅ | ✅ | – | – | – | – | – | ✅ |
| **Returned** | ✅ | ✅ | – | – | – | – | – | – | – | ✅ |
| **Approved** | – | – | – | – | ✅ | – | – | – | – | ✅ |
| **PR Raised** | – | – | – | – | – | ✅ | – | – | – | ✅ |
| **Sourcing** | – | – | – | – | – | – | ✅ | – | – | ✅ |
| **Ordered** | – | – | – | – | – | – | – | ✅ | – | ✅ |
| **Delivery IP** | – | – | – | – | – | – | – | – | ✅ | ✅ |
| **Delivered** | – | – | – | – | – | – | – | – | – | – |
| **Cancelled** | – | – | – | – | – | – | – | – | – | – |

### C.4 Role Permissions Per Transition

| Transition | Allowed Roles |
|-----------|---------------|
| Draft → Submitted for Approval | Project/Department Requester |
| Submitted → Approved | Project/Department Manager (or configured approver chain) |
| Submitted → Returned for Correction | Project/Department Manager, Supply Chain Officer |
| Returned → Draft | Project/Department Requester |
| Returned → Submitted for Approval | Project/Department Requester |
| Approved → PR Raised | Supply Chain Officer |
| PR Raised → Sourcing | Supply Chain Officer |
| Sourcing → Ordered/Contracted | Supply Chain Officer |
| Ordered/Contracted → Delivery In Progress | Supply Chain Officer, Stores/Inventory Officer |
| Delivery In Progress → Delivered/Closed | Stores/Inventory Officer |
| Any → Cancelled | Project/Department Manager, Supply Chain Officer, System Admin |

### C.5 Field-Level Edit Permissions

| Field Group | Draft / Returned | Submitted | Approved+ |
|------------|-----------------|-----------|-----------|
| **Planning fields** (Item Description, Qty, Unit Price, Costs, Location, Material Group, Month/Quarter/FY, Activity No.) | Project/Dept Requester: ✅ edit | ❌ locked | ❌ locked |
| **Approval fields** (decision, comments) | – | Approver: ✅ | – |
| **Supply Chain fields** (PR Number, PR Date, Sourcing Method, LTA Ref, Sourcing Location, Sourcing Plan) | ❌ | ❌ | Supply Chain: ✅ |
| **Delivery fields** (Actual Delivery Date, Delivery Qty, Stock post-delivery) | ❌ | ❌ | Stores: ✅ |
| **All fields** | System Admin: ✅ | System Admin: ✅ | System Admin: ✅ |
| **Read/Report** | Finance: 👁️ | Finance: 👁️ | Finance: 👁️ |

---

## D) API Design (REST)

Base URL: `/api/v1`

### D.1 Core Endpoints

#### Procurement Plan Headers
```
POST   /api/v1/procurement-plans                    Create plan (with line items)
GET    /api/v1/procurement-plans                    List plans (filterable)
GET    /api/v1/procurement-plans/:id                Get plan detail + all line items
PUT    /api/v1/procurement-plans/:id                Update plan header
DELETE /api/v1/procurement-plans/:id                Soft delete plan
```

#### Line Items
```
POST   /api/v1/procurement-plans/:planId/line-items              Add line item(s)
GET    /api/v1/procurement-plans/:planId/line-items              List line items for plan
GET    /api/v1/line-items/:id                                    Get single line item detail
PUT    /api/v1/line-items/:id                                    Update line item
DELETE /api/v1/line-items/:id                                    Soft delete line item
```

#### Line Item Approval Actions
```
POST   /api/v1/line-items/:id/submit                Submit for approval
POST   /api/v1/line-items/:id/approve               Approve
POST   /api/v1/line-items/:id/return                Return for correction
POST   /api/v1/line-items/:id/cancel                Cancel
POST   /api/v1/line-items/:id/delegate               Delegate approval
POST   /api/v1/line-items/bulk-submit                Bulk submit
POST   /api/v1/line-items/bulk-approve               Bulk approve
```

#### Purchase Requisitions
```
POST   /api/v1/purchase-requisitions                Create PR (link to line items)
GET    /api/v1/purchase-requisitions                List PRs
GET    /api/v1/purchase-requisitions/:id            Get PR detail + linked items
PUT    /api/v1/purchase-requisitions/:id            Update PR
PUT    /api/v1/purchase-requisitions/:id/sourcing   Update sourcing details
```

#### Deliveries
```
POST   /api/v1/line-items/:id/deliveries            Record delivery (partial)
GET    /api/v1/line-items/:id/deliveries            List deliveries for item
```

#### Stock/Assets
```
GET    /api/v1/stock-assets                         List stock/assets
POST   /api/v1/stock-assets                         Create/update stock record
PUT    /api/v1/stock-assets/:id                     Update stock record
```

#### Exchange Rates
```
GET    /api/v1/exchange-rates                       List rates
POST   /api/v1/exchange-rates                       Add rate
GET    /api/v1/exchange-rates/convert               Convert amount (query params)
```

#### Reporting
```
GET    /api/v1/reports/dashboard                    Dashboard KPIs
GET    /api/v1/reports/approval-ageing              Approval ageing report
GET    /api/v1/reports/overdue-deliveries           Overdue deliveries
GET    /api/v1/reports/pipeline                     Pipeline by status
GET    /api/v1/reports/planned-vs-delivered          Progress report
GET    /api/v1/reports/top-cost-items               Top 10 highest cost items
GET    /api/v1/reports/stock-avoided                 Stock-avoided procurement
GET    /api/v1/reports/plan-approval-summary         Partial approval summaries
GET    /api/v1/reports/export                       Export to Excel/CSV
```

#### Import/Export
```
POST   /api/v1/import/procurement-plans             Import CSV/Excel
GET    /api/v1/export/procurement-plans              Export to CSV/Excel
```

#### Admin
```
CRUD   /api/v1/admin/users
CRUD   /api/v1/admin/roles
CRUD   /api/v1/admin/approval-rules
CRUD   /api/v1/admin/approval-steps
CRUD   /api/v1/admin/lookups/:type                  (locations, material-groups, uom, sourcing-methods, funding-sources)
GET    /api/v1/admin/audit-log                      Query audit log
```

#### Attachments & Comments
```
POST   /api/v1/attachments                          Upload file (entity_type + entity_id)
GET    /api/v1/attachments?entity_type=&entity_id=  List attachments
POST   /api/v1/comments                             Add comment
GET    /api/v1/comments?entity_type=&entity_id=     List comments
```

### D.2 Request/Response Examples

#### 1) Create Plan + Line Items
```http
POST /api/v1/procurement-plans
Content-Type: application/json
Authorization: Bearer <token>

{
  "tracking_no": "PP0374",
  "project_id": "uuid-cosme-nbs",
  "type_of_procurement_plan": "Annual Procurement Plan",
  "department_manager_id": "uuid-manager-1",
  "fad_spad_number": "FAD-2025-001",
  "project_code_cost_centre": "FECNO",
  "funding_source_id": "uuid-grant",
  "donor_name": "GAC",
  "start_date": "2025-01-01",
  "end_date": "2027-12-31",
  "line_items": [
    {
      "line_item_ref": "PP0374-001",
      "location_id": "uuid-kilifi",
      "activity_number": "ACT-1.1",
      "material_group_id": "uuid-consultancy",
      "item_description": "Lead Consultant – NBS Technical Assessment",
      "uom_id": "uuid-day",
      "quantity": 30,
      "currency_code": "EUR",
      "estimated_unit_price": 500.00,
      "estimated_warehousing_cost": 0,
      "estimated_transport_cost": 200.00,
      "month": 3,
      "quarter": "Q1",
      "fiscal_year": "FY2025",
      "item_type": "Service"
    },
    {
      "line_item_ref": "PP0374-002",
      "location_id": "uuid-kwale",
      "activity_number": "ACT-2.3",
      "material_group_id": "uuid-equipment",
      "item_description": "Solar-powered irrigation kits",
      "uom_id": "uuid-each",
      "quantity": 50,
      "currency_code": "KES",
      "estimated_unit_price": 45000.00,
      "estimated_warehousing_cost": 25000.00,
      "estimated_transport_cost": 15000.00,
      "month": 6,
      "quarter": "Q2",
      "fiscal_year": "FY2025",
      "item_type": "Stock",
      "is_stock_on_hand_available": true,
      "quantity_available": 10
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-plan-1",
  "tracking_no": "PP0374",
  "header_status": "Draft",
  "days_remaining_until_project_end_date": 1001,
  "line_items": [
    {
      "id": "uuid-li-001",
      "line_item_ref": "PP0374-001",
      "item_description": "Lead Consultant – NBS Technical Assessment",
      "estimated_total_item_service_cost": 15000.00,
      "estimated_total_cost": 15200.00,
      "currency_code": "EUR",
      "status": "Draft"
    },
    {
      "id": "uuid-li-002",
      "line_item_ref": "PP0374-002",
      "item_description": "Solar-powered irrigation kits",
      "estimated_total_item_service_cost": 2250000.00,
      "estimated_total_cost": 2290000.00,
      "currency_code": "KES",
      "status": "Draft",
      "stock_warning": "Stock available (10 of 50 needed). Acknowledge before submission."
    }
  ]
}
```

#### 2) Submit a Line Item for Approval
```http
POST /api/v1/line-items/uuid-li-001/submit
Authorization: Bearer <token>

{
  "comment": "Ready for review – consultant terms validated with HR."
}
```

**Response (200 OK):**
```json
{
  "id": "uuid-li-001",
  "line_item_ref": "PP0374-001",
  "status": "Submitted for Approval",
  "submitted_at": "2025-03-15T09:30:00Z",
  "submitted_by": "Jane Mwangi",
  "pending_approvers": [
    { "step": 1, "role": "Project/Department Manager", "approver": "Dr. Kamau" }
  ]
}
```

#### 3) Approve / Return a Line Item
**Approve:**
```http
POST /api/v1/line-items/uuid-li-001/approve
Authorization: Bearer <token>

{
  "comment": "Approved. Proceed with sourcing."
}
```

**Response (200 OK):**
```json
{
  "id": "uuid-li-001",
  "line_item_ref": "PP0374-001",
  "status": "Approved",
  "approval": {
    "step": 1,
    "approver": "Dr. Kamau",
    "decision": "Approved",
    "decided_at": "2025-03-16T14:00:00Z",
    "comment": "Approved. Proceed with sourcing."
  }
}
```

**Return:**
```http
POST /api/v1/line-items/uuid-li-002/return
Authorization: Bearer <token>

{
  "comment": "Unit price appears high for irrigation kits. Please obtain updated quotation from supplier."
}
```

**Response (200 OK):**
```json
{
  "id": "uuid-li-002",
  "line_item_ref": "PP0374-002",
  "status": "Returned for Correction",
  "approval": {
    "step": 1,
    "approver": "Dr. Kamau",
    "decision": "Returned",
    "decided_at": "2025-03-16T14:05:00Z",
    "comment": "Unit price appears high for irrigation kits. Please obtain updated quotation from supplier."
  }
}
```

#### 4) Raise PR Linked to Multiple Line Items
```http
POST /api/v1/purchase-requisitions
Authorization: Bearer <token>

{
  "pr_number": "PR-2025-0042",
  "submitted_date": "2025-03-20",
  "line_item_ids": ["uuid-li-001", "uuid-li-003", "uuid-li-005"],
  "notes": "Combined PR for Q1 consultancy services – Kilifi Office"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-pr-1",
  "pr_number": "PR-2025-0042",
  "submitted_date": "2025-03-20",
  "status": "Open",
  "linked_line_items": [
    { "id": "uuid-li-001", "ref": "PP0374-001", "status": "PR Raised" },
    { "id": "uuid-li-003", "ref": "PP0374-003", "status": "PR Raised" },
    { "id": "uuid-li-005", "ref": "PP0374-005", "status": "PR Raised" }
  ]
}
```

#### 5) Update Sourcing
```http
PUT /api/v1/purchase-requisitions/uuid-pr-1/sourcing
Authorization: Bearer <token>

{
  "line_items": [
    {
      "line_item_id": "uuid-li-001",
      "sourcing_method_id": "uuid-lta",
      "lta_reference_number": "LTA-COSME-2025-007",
      "sourcing_location": "Kilifi Office",
      "sourcing_plan": "Use existing LTA with approved supplier.",
      "status": "Sourcing"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "pr_number": "PR-2025-0042",
  "updated_items": [
    {
      "id": "uuid-li-001",
      "ref": "PP0374-001",
      "status": "Sourcing",
      "sourcing_method": "LTA",
      "lta_reference_number": "LTA-COSME-2025-007"
    }
  ]
}
```

#### 6) Record Delivery (Partial)
```http
POST /api/v1/line-items/uuid-li-002/deliveries
Authorization: Bearer <token>

{
  "delivery_date": "2025-06-10",
  "quantity_delivered": 20,
  "delivery_note_ref": "DN-2025-0088",
  "condition_notes": "20 of 50 kits received in good condition. Remaining 30 expected by June 25."
}
```

**Response (201 Created):**
```json
{
  "delivery_id": "uuid-del-1",
  "line_item_id": "uuid-li-002",
  "line_item_ref": "PP0374-002",
  "delivery_date": "2025-06-10",
  "quantity_delivered": 20,
  "total_delivered_to_date": 20,
  "planned_quantity": 50,
  "remaining_quantity": 30,
  "delivery_percentage": 40.0,
  "line_item_status": "Delivery In Progress"
}
```

#### 7) Dashboard Query (Approval Ageing + Overdue)
```http
GET /api/v1/reports/dashboard?project_id=uuid-cosme-nbs&fiscal_year=FY2025&currency=EUR
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "summary": {
    "total_planned_cost_kes": 45600000.00,
    "total_planned_cost_eur": 285000.00,
    "total_planned_cost_eur_converted": 291428.57,
    "exchange_rate_used": { "KES_to_EUR": 0.0064, "effective_date": "2025-03-01" },
    "line_items_by_status": {
      "Draft": { "count": 5, "value_kes": 1200000, "value_eur": 8000 },
      "Submitted for Approval": { "count": 3, "value_kes": 800000, "value_eur": 15000 },
      "Approved": { "count": 12, "value_kes": 15000000, "value_eur": 95000 },
      "PR Raised": { "count": 8, "value_kes": 10000000, "value_eur": 62000 },
      "Sourcing": { "count": 4, "value_kes": 5000000, "value_eur": 30000 },
      "Ordered/Contracted": { "count": 6, "value_kes": 8000000, "value_eur": 45000 },
      "Delivery In Progress": { "count": 3, "value_kes": 3000000, "value_eur": 20000 },
      "Delivered/Closed": { "count": 15, "value_kes": 2000000, "value_eur": 8000 },
      "Cancelled": { "count": 2, "value_kes": 600000, "value_eur": 2000 }
    }
  },
  "approval_ageing": {
    "avg_days_in_submitted": 3.2,
    "avg_days_in_returned": 5.1,
    "items_pending_over_5_days": [
      { "ref": "PP0374-008", "days_pending": 7, "approver": "Dr. Kamau", "value": 125000, "currency": "KES" }
    ]
  },
  "overdue_deliveries": [
    {
      "ref": "PP0374-002",
      "item_description": "Solar-powered irrigation kits",
      "estimated_delivery_date": "2025-06-01",
      "days_overdue": 15,
      "delivered_pct": 40,
      "location": "Kwale Office"
    }
  ],
  "top_10_cost_items": [
    { "ref": "PP0374-002", "description": "Solar-powered irrigation kits", "estimated_total_cost": 2290000, "currency": "KES" }
  ],
  "stock_avoided": {
    "count": 3,
    "total_value_kes": 450000,
    "total_value_eur": 2800
  },
  "partial_approval_summary": [
    {
      "tracking_no": "PP0374",
      "total_items": 15,
      "approved": 10,
      "returned": 2,
      "draft": 1,
      "submitted": 1,
      "cancelled": 1
    }
  ]
}
```

---

## E) UI/UX Modules

### E.1 Key Screens by Role

#### All Roles — Common Navigation
- **Dashboard** (role-specific KPIs and action items)
- **Global Search** (by Tracking No., PR Number, Line Item Ref, Item Description)
- **Notifications** (pending approvals, returned items, overdue alerts)

#### Project/Department Requester
1. **Create Procurement Plan** — Multi-step form:
   - Step 1: Header fields (Tracking No., Project, Manager, Dates, Funding, Donor)
   - Step 2: Add line items (table with inline editing or modal per item)
   - Step 3: Review totals (auto-calculated costs, currency summary)
   - Step 4: Submit selected items for approval (bulk or individual)
2. **My Procurement Plans** — List view with filters (status, date, project)
3. **Line Item Detail** — Full detail with status timeline, approval history, comments, attachments
4. **Edit Returned Items** — Pre-filtered view showing only "Returned for Correction" items with approver comments visible

#### Project/Department Manager (Approver)
1. **Approval Inbox** — Filtered queue of items "Submitted for Approval" assigned to this approver
   - Sortable by: date submitted, cost, project, location, urgency
   - Preview pane showing item details, cost breakdown, approval history
   - Actions: Approve / Return for Correction (with mandatory comment) / Cancel
   - **Bulk Approve** — Select multiple items, approve with single comment (policy must allow)
2. **Plan Overview** — Tree view: Header → Line Items with colour-coded status badges
   - Mixed state indicator: "10 ✅ / 2 🔄 / 1 📝 / 2 ❌"
3. **Approval History** — Full log of all decisions made

#### Supply Chain Officer
1. **Approved Items Queue** — Items in "Approved" status ready for PR
2. **Raise PR** — Select multiple approved items → Create PR with single PR Number
3. **PR Management** — List of PRs with linked items; update sourcing details
4. **Sourcing Tracker** — Kanban board: PR Raised → Sourcing → Ordered/Contracted → Delivery In Progress
5. **LTA Reference Lookup** — Quick search for LTA numbers

#### Stores/Inventory Officer
1. **Pending Deliveries** — Items in "Delivery In Progress" or "Ordered/Contracted"
2. **Record Delivery** — Form: select line item, enter quantity, date, notes, upload delivery note
3. **Stock/Asset Register** — Current inventory with search/filter
4. **Stock Availability Check** — Cross-reference against procurement line items flagged with stock available

#### Finance/Grants
1. **Read-Only Dashboard** — All plans, items, costs; no edit capability
2. **Budget vs Actuals** — Planned cost vs committed (PR raised) vs delivered
3. **Donor Report Generator** — Export filtered data by donor, project, FY, quarter
4. **Currency Conversion View** — Toggle between KES and EUR; configure exchange rates
5. **Compliance Alerts** — Budget threshold warnings (optional design hook)

#### System Admin
1. **User Management** — CRUD users, assign roles, project-scope roles
2. **Approval Rules Engine** — Visual rule builder (conditions: cost threshold, type, method, material group, location → approval steps)
3. **Lookup Management** — Manage locations, material groups, UoM, sourcing methods, funding sources
4. **Exchange Rate Management** — Add/edit rates by date
5. **Audit Log Viewer** — Searchable/filterable audit trail
6. **Import/Export Admin** — Template download, upload with validation preview

### E.2 Line Item Approval Inbox (Detail)

```
┌─────────────────────────────────────────────────────────────────┐
│ APPROVAL INBOX                          [Bulk Approve] [Filter] │
├─────┬───────────┬─────────────────────┬──────────┬──────┬──────┤
│ ☐   │ Ref       │ Description         │ Cost     │ CCY  │ Days │
├─────┼───────────┼─────────────────────┼──────────┼──────┼──────┤
│ ☐   │ PP0374-001│ Lead Consultant NBS │ 15,200   │ EUR  │ 2    │
│ ☐   │ PP0374-003│ Travel Kilifi-Kwale │ 85,000   │ KES  │ 5    │
│ ☐   │ PP0375-001│ Catering – Training │ 120,000  │ KES  │ 1    │
└─────┴───────────┴─────────────────────┴──────────┴──────┴──────┘
                            [Approve Selected] [Return Selected]
```

Clicking a row expands to show:
- Full item details (all planning fields)
- Cost breakdown (unit price × qty + warehousing + transport)
- Approval history (previous decisions if returned before)
- Comments thread
- Attachments
- Stock warning (if applicable)

### E.3 Validations & Inline Calculations (UI)

| Field | Validation / Calculation |
|-------|------------------------|
| Quantity | Required, > 0, numeric |
| Estimated Unit Price | Required, ≥ 0, numeric |
| Estimated Total Item/Service Cost | Auto = Quantity × Unit Price (read-only) |
| Estimated Warehousing Cost | ≥ 0, numeric, default 0 |
| Estimated Transport Cost | ≥ 0, numeric, default 0 |
| Estimated Total Cost | Auto = Item/Service Cost + Warehousing + Transport (read-only) |
| Month | Required, 1–12 dropdown |
| Quarter | Auto-derived from Month; editable only if consistent |
| UoM | Required, dropdown |
| Location | Required, dropdown |
| Material Group | Required, dropdown with group number |
| Return Comment | Mandatory when returning item |
| Cancel Reason | Mandatory when cancelling |
| Stock Acknowledgement | If stock available ≥ qty, must acknowledge before submit |

---

## F) Reporting & Dashboards

### F.1 Proposed Charts & Tables

| Report | Type | Description |
|--------|------|-------------|
| **Pipeline by Status** | Stacked bar chart | Line item count + value by status, filterable by project/location/FY |
| **Approval Ageing** | Histogram + table | Distribution of days items spend in Submitted/Returned states |
| **Overdue Deliveries** | Table with heatmap | Items past estimated delivery date, sorted by days overdue |
| **Planned vs Progress** | Waterfall chart | Planned → PR Raised → Ordered → Delivered (value cascade) |
| **Top 10 Cost Items** | Horizontal bar chart | Highest estimated_total_cost items |
| **Monthly Spend Trend** | Line chart (dual axis) | KES and EUR planned values by month |
| **Stock Avoided** | KPI card + table | Count and value of items fulfilled from stock |
| **Partial Approval Summary** | Table | Per plan: approved/returned/draft/submitted/cancelled counts |
| **Currency Roll-up** | Summary cards | Total Estimated in Euro; Total Estimated in KES (with conversion) |
| **Donor Report** | Exportable table | All fields + approval trail columns for GAC reporting |

### F.2 Query Logic (SQL-like Pseudocode)

#### Total Planned Cost by Currency with Conversion
```sql
-- Native totals
SELECT 
  currency_code,
  SUM(estimated_total_cost) AS total_native
FROM procurement_plan_line_items
WHERE deleted_at IS NULL
  AND fiscal_year = 'FY2025'
  AND status != 'Cancelled'
GROUP BY currency_code;

-- Converted to EUR
SELECT 
  SUM(CASE 
    WHEN li.currency_code = 'EUR' THEN li.estimated_total_cost
    ELSE li.estimated_total_cost * er.rate
  END) AS total_estimated_in_euro
FROM procurement_plan_line_items li
LEFT JOIN LATERAL (
  SELECT rate FROM exchange_rates 
  WHERE from_currency = 'KES' AND to_currency = 'EUR'
    AND effective_date <= CURRENT_DATE
  ORDER BY effective_date DESC LIMIT 1
) er ON li.currency_code = 'KES'
WHERE li.deleted_at IS NULL AND li.status != 'Cancelled';
```

#### Pipeline Count/Value by Status
```sql
SELECT 
  status,
  COUNT(*) AS item_count,
  SUM(CASE WHEN currency_code = 'KES' THEN estimated_total_cost ELSE 0 END) AS value_kes,
  SUM(CASE WHEN currency_code = 'EUR' THEN estimated_total_cost ELSE 0 END) AS value_eur
FROM procurement_plan_line_items
WHERE deleted_at IS NULL
  AND fiscal_year = :fy
  AND (:project_id IS NULL OR header_id IN (SELECT id FROM procurement_plan_headers WHERE project_id = :project_id))
GROUP BY status;
```

#### Approval Ageing
```sql
SELECT 
  li.id, li.line_item_ref, li.item_description, li.estimated_total_cost, li.currency_code,
  li.status,
  EXTRACT(DAY FROM NOW() - li.updated_at) AS days_in_current_status,
  u.full_name AS pending_approver
FROM procurement_plan_line_items li
JOIN procurement_plan_headers h ON li.header_id = h.id
JOIN users u ON h.department_manager_id = u.id
WHERE li.status IN ('Submitted for Approval', 'Returned for Correction')
  AND li.deleted_at IS NULL
ORDER BY days_in_current_status DESC;
```

#### Overdue Deliveries
```sql
SELECT 
  li.line_item_ref, li.item_description, li.estimated_delivery_date,
  (CURRENT_DATE - li.estimated_delivery_date) AS days_overdue,
  li.quantity, li.delivered_quantity,
  ROUND(li.delivered_quantity / li.quantity * 100, 1) AS delivery_pct,
  loc.location_name
FROM procurement_plan_line_items li
JOIN locations loc ON li.location_id = loc.id
WHERE li.estimated_delivery_date < CURRENT_DATE
  AND li.status NOT IN ('Delivered/Closed', 'Cancelled')
  AND li.deleted_at IS NULL
ORDER BY days_overdue DESC;
```

#### Plan-Level Partial Approval Summary
```sql
SELECT 
  h.tracking_no,
  COUNT(*) AS total_items,
  COUNT(*) FILTER (WHERE li.status = 'Approved') AS approved,
  COUNT(*) FILTER (WHERE li.status = 'Returned for Correction') AS returned,
  COUNT(*) FILTER (WHERE li.status = 'Draft') AS draft,
  COUNT(*) FILTER (WHERE li.status = 'Submitted for Approval') AS submitted,
  COUNT(*) FILTER (WHERE li.status = 'Cancelled') AS cancelled,
  COUNT(*) FILTER (WHERE li.status IN ('PR Raised','Sourcing','Ordered/Contracted','Delivery In Progress','Delivered/Closed')) AS in_procurement
FROM procurement_plan_headers h
JOIN procurement_plan_line_items li ON li.header_id = h.id
WHERE li.deleted_at IS NULL
GROUP BY h.id, h.tracking_no;
```

#### Stock-Avoided Procurement
```sql
SELECT 
  li.line_item_ref, li.item_description, li.quantity, li.quantity_available,
  li.estimated_total_cost, li.currency_code
FROM procurement_plan_line_items li
WHERE li.is_stock_on_hand_available = true
  AND li.quantity_available >= li.quantity
  AND li.deleted_at IS NULL;
```

---

## G) Implementation Plan

### G.1 Phased Build

#### Phase 1: MVP (8-10 weeks)
- Database schema creation with all core tables
- Authentication + RBAC (users, roles, permissions)
- CRUD: Procurement Plan Headers + Line Items
- Line item lifecycle (status transitions with validation)
- Single-step approval (Project Manager → Approve/Return)
- Basic dashboard (pipeline by status, totals in KES/EUR)
- CSV import/export (plans + line items)
- Audit log for all mutations

#### Phase 2: Enhanced (6-8 weeks)
- Multi-step configurable approval rules engine
- PR management (create, link to items, sourcing)
- Delivery tracking (partial deliveries)
- Stock/Asset module
- Exchange rate management + automatic conversion
- Advanced reporting (approval ageing, overdue, top items)
- File attachment uploads
- Comments on line items and PRs

#### Phase 3: Polish & Compliance (4-6 weeks)
- Approval delegation and escalation
- Bulk actions (bulk submit, bulk approve)
- Donor-ready export templates (including approval trail columns)
- Budget threshold warnings for Finance
- Email/in-app notifications
- Performance optimization (query tuning, indexes, caching)
- UAT and bug fixes

### G.2 Recommended Tech-Stack Options

#### Option A: Node.js + React (Recommended)
| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React 18 + TypeScript + Ant Design Pro | Rich data tables, form builder, charting; enterprise UI library |
| Backend | Node.js + Express + TypeScript | Fast development, strong typing, large ecosystem |
| ORM | Prisma | Type-safe DB access, migrations, generated client |
| Database | PostgreSQL 15+ | Generated columns, JSONB, partitioning, CTEs for reporting |
| Auth | JWT + bcrypt | Stateless auth tokens with refresh; role claims in token |
| File Storage | Local/S3 | Attachments stored server-side or in cloud bucket |
| Reporting | Chart.js / Recharts | Lightweight, customisable charts |
| Export | ExcelJS + csv-parser | Excel/CSV generation and parsing |
| Deployment | Docker + nginx | Containerised, portable |

#### Option B: Python + Django
| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React or Django Templates + HTMX | Faster with templates; React for richer experience |
| Backend | Django 5 + Django REST Framework | Batteries-included: ORM, admin, auth, permissions |
| Database | PostgreSQL 15+ | Same advantages as above |
| Auth | Django Auth + django-rest-framework-simplejwt | Built-in RBAC |
| Export | openpyxl + pandas | Powerful data manipulation |

#### Option C: C# + .NET + Blazor
| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | Blazor Server or WASM | Strongly typed full-stack C# |
| Backend | ASP.NET Core 8 Web API | Enterprise-grade, high performance |
| ORM | Entity Framework Core | Migrations, LINQ queries |
| Database | PostgreSQL or SQL Server | Either works well with EF Core |
| Auth | ASP.NET Identity + JWT | Mature RBAC with claims-based authorization |

**Recommendation: Option A (Node.js + React + PostgreSQL)** for this project because:
1. Fastest development velocity for a mid-size team
2. Prisma ORM provides excellent type safety and migration tooling
3. React + Ant Design Pro gives best enterprise table/form UX out of the box
4. PostgreSQL generated columns perfectly suit the calculated fields requirement
5. Excellent ecosystem for Excel/CSV import-export

---

## H) Risks & Mitigations

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|-----------|------------|
| 1 | **Data quality on import** — Users upload CSV files with missing required fields, invalid month/quarter, or duplicate tracking numbers | Medium | High | Row-level validation with clear error messages; preview mode before commit; downloadable error report; provide template with data validation dropdowns |
| 2 | **Currency conversion accuracy** — Exchange rates change frequently; incorrect rates lead to inaccurate donor reports | High | Medium | Date-effective exchange rate table; always store native currency + code; convert at query time using nearest rate; admin controls rate entry; flag if no rate exists for period |
| 3 | **Approval bottlenecks** — Single approver becomes a blocker, items stuck in "Submitted" state | High | High | Configurable delegation rules; escalation after N days; approval ageing dashboard with alerts; email/notification reminders; bulk approve for low-value items |
| 4 | **Audit compliance** — Audit trail gaps could jeopardise donor audits | High | Low | Append-only approval history; immutable audit_log table; no hard deletes (soft delete only); database triggers as safety net; regular audit log integrity checks |
| 5 | **Partial delivery tracking complexity** — Users confused by partial quantities or miss updating stock | Medium | Medium | Clear delivered vs remaining quantity display; auto-update delivered_quantity via trigger; prevent closing item until delivered_quantity >= planned quantity; allow manual close override with reason |
| 6 | **RBAC misconfiguration** — Wrong roles assigned, users edit fields they shouldn't | High | Medium | Field-level permission enforcement in backend (not just UI); comprehensive permission tests; admin audit of role assignments; principle of least privilege defaults |
| 7 | **Performance with large datasets** — Reporting queries slow down as data grows | Medium | Low (initially) | Proper indexing strategy from day 1; materialized views for dashboard queries; pagination everywhere; archival strategy for closed fiscal years |
| 8 | **Multi-step approval rule complexity** — Overlapping or conflicting rules cause unexpected routing | Medium | Medium | Rule priority system; admin UI shows rule evaluation preview; test mode to simulate which rules apply to a sample item; comprehensive rule validation on save |

---

*This design document is build-ready. The companion files in this repository contain the full database schema (SQL), backend application code, frontend application code, and seed data.*
