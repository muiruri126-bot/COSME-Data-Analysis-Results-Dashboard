# COSME Procurement Tracking System

A comprehensive full-stack procurement lifecycle management system built for the COSME Project. Supports **line-item-level approvals**, dual currency (KES / EUR), role-based access control, audit trails, and donor-ready reporting.

---

## Architecture

| Layer      | Technology                                 |
|------------|-------------------------------------------|
| **Frontend** | React 18 + TypeScript + Ant Design + Recharts |
| **Backend**  | Node.js + Express + TypeScript + Prisma ORM   |
| **Database** | PostgreSQL 15+                              |
| **Auth**     | JWT + bcrypt with RBAC                      |

## Project Structure

```
Procurement/
├── SYSTEM_DESIGN.md          # Complete design document (Sections A-H)
├── README.md                 # This file
│
├── database/
│   ├── 001_schema.sql        # Full PostgreSQL DDL (24 tables, triggers, views)
│   └── 002_seed_data.sql     # COSME-specific seed data
│
├── backend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── .env.example
│   ├── prisma/
│   │   └── schema.prisma     # Prisma data model
│   └── src/
│       ├── server.ts          # Express app entry point
│       ├── lib/
│       │   ├── prisma.ts      # DB client singleton
│       │   ├── constants.ts   # Statuses, transitions, Zod schemas
│       │   └── audit.ts       # Audit log helpers
│       ├── middleware/
│       │   ├── auth.ts        # JWT + RBAC middleware
│       │   └── errorHandler.ts
│       └── routes/
│           ├── auth.ts
│           ├── procurementPlans.ts
│           ├── lineItems.ts
│           ├── approvals.ts
│           ├── purchaseRequisitions.ts
│           ├── deliveries.ts
│           ├── stockAssets.ts
│           ├── exchangeRates.ts
│           ├── reports.ts
│           ├── admin.ts
│           ├── attachments.ts
│           ├── comments.ts
│           └── importExport.ts
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api.ts             # Axios instance with JWT interceptor
        ├── store.ts           # Zustand auth store (persisted)
        ├── index.css
        ├── components/
        │   ├── AppLayout.tsx  # Sidebar navigation
        │   └── StatusTag.tsx  # Status badge + formatters
        └── pages/
            ├── LoginPage.tsx
            ├── DashboardPage.tsx
            ├── ProcurementPlansPage.tsx
            ├── PlanDetailPage.tsx
            ├── CreatePlanPage.tsx
            ├── ApprovalInboxPage.tsx
            ├── PurchaseRequisitionsPage.tsx
            ├── DeliveriesPage.tsx
            ├── StockAssetsPage.tsx
            ├── ExchangeRatesPage.tsx
            ├── ReportsPage.tsx
            ├── AdminUsersPage.tsx
            └── AuditLogPage.tsx
```

---

## System Modules

| # | Module | Description |
|---|--------|-------------|
| 1 | **Procurement Plan Header** | Create/view plans with tracking no, fiscal year, quarter, project, location, donor |
| 2 | **Line Items** | Full CRUD with auto-calculated costs, field-level RBAC, stock-on-hand warnings |
| 3 | **Approval Workflow** | Line-item-level multi-step approvals, bulk approve, delegate, return, cancel |
| 4 | **Purchase Requisitions** | Link approved items to PRs, update sourcing details |
| 5 | **Delivery & Receipt** | Partial delivery tracking with auto-status transitions |
| 6 | **Stock/Asset Register** | Track stock on hand and asset tags by location |
| 7 | **Exchange Rates** | KES/EUR rates with currency converter endpoint |
| 8 | **Reporting** | Dashboard KPIs, pipeline, approval ageing, overdue deliveries, stock avoidance |
| 9 | **Admin** | User/role management, approval rules, lookup tables, audit log viewer |
| 10 | **Import/Export** | CSV/XLSX import with row-level validation, Excel export with approval trail |

---

## Line Item Statuses (10)

```
Draft → Submitted for Approval → Approved → PR Raised → Ordered/Contracted
          ↕                                                    ↓
  Returned for Correction                          Delivery In Progress
                                                         ↓
                                                  Delivered/Closed

  Any (except Delivered/Closed) → Cancelled
  Any → On Hold → (previous status)
```

## Roles

| Role | Capabilities |
|------|-------------|
| **Requester** | Create plans + line items, submit for approval |
| **Supply Chain Officer** | Update sourcing fields, raise PRs, record deliveries |
| **Project/Department Manager** | Approve/return/cancel/delegate items |
| **Finance/Grants** | View-only, exchange rates, reports |
| **Stores/Inventory Officer** | Stock & asset management, receive deliveries |
| **System Admin** | Full access including user/role/rules management |

---

## Getting Started

### Prerequisites
- Node.js 18+
- PostgreSQL 15+
- npm or yarn

### 1. Database Setup

```bash
# Create database
psql -U postgres -c "CREATE DATABASE cosme_procurement;"

# Run schema
psql -U postgres -d cosme_procurement -f database/001_schema.sql

# Load seed data
psql -U postgres -d cosme_procurement -f database/002_seed_data.sql
```

### 2. Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env with your PostgreSQL connection string and JWT secret

npm install
npx prisma generate
npx prisma db pull   # (or use prisma migrate if preferred)
npm run dev
```

Backend runs on http://localhost:3001

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:3000 (proxies API to :3001)

### 4. Login

Use seed data credentials (default password for all: `CosmePass2025!`):

| Email | Role |
|-------|------|
| admin@cosme.org | System Admin |
| manager@cosme.org | Project/Department Manager |
| sc.officer@cosme.org | Supply Chain Officer |
| requester@cosme.org | Requester |
| finance@cosme.org | Finance/Grants |
| stores@cosme.org | Stores/Inventory Officer |

---

## API Reference

Base URL: `/api/v1`

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login with email/password |
| GET | `/auth/me` | Get current user |

### Procurement Plans
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/procurement-plans` | List plans (paginated, filterable) |
| GET | `/procurement-plans/:id` | Plan detail with line items |
| POST | `/procurement-plans` | Create plan with line items |
| PUT | `/procurement-plans/:id` | Update plan header |
| DELETE | `/procurement-plans/:id` | Soft delete |

### Line Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/line-items/plan/:planId` | Add line item to plan |
| GET | `/line-items/:id` | Get line item detail |
| PUT | `/line-items/:id` | Update (field-level RBAC) |
| POST | `/line-items/:id/submit` | Submit for approval |
| POST | `/line-items/bulk-submit` | Bulk submit |
| DELETE | `/line-items/:id` | Soft delete |

### Approvals
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/approvals/:id/approve` | Approve line item |
| POST | `/approvals/:id/return` | Return for correction |
| POST | `/approvals/:id/cancel` | Cancel line item |
| POST | `/approvals/:id/delegate` | Delegate to another approver |
| POST | `/approvals/bulk-approve` | Bulk approve |

### Purchase Requisitions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/purchase-requisitions` | List PRs |
| GET | `/purchase-requisitions/:id` | PR detail |
| POST | `/purchase-requisitions` | Create PR (links approved items) |
| PUT | `/purchase-requisitions/:id/sourcing` | Update sourcing details |

### Deliveries
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/deliveries/line-item/:id` | Record delivery |
| GET | `/deliveries/line-item/:id` | List deliveries for item |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/dashboard` | Full dashboard data |
| GET | `/reports/pipeline` | Pipeline by status |
| GET | `/reports/approval-ageing` | Ageing detail |
| GET | `/reports/overdue-deliveries` | Overdue items |
| GET | `/reports/stock-avoided` | Stock avoidance report |

### Import/Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/import-export/export/:planId` | Export plan as XLSX |
| POST | `/import-export/import/:planId` | Import CSV/XLSX line items |

---

## Design Document

See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for the complete 8-section design covering:
- **A**: Solution Overview
- **B**: Data Model (24 tables, full ERD)
- **C**: Workflow & Permissions
- **D**: API Design with request/response examples
- **E**: UI/UX Module Screens
- **F**: Reporting & Dashboards
- **G**: Implementation Plan (3 phases, 3 tech stacks)
- **H**: Risks & Mitigations
