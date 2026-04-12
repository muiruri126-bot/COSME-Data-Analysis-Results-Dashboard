# COSME DIP — Detailed Implementation Plan & Results Dashboard
## Full System Specification v1.0

---

# 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                             │
│  React 18 + TypeScript + TanStack Query + Zustand + Tailwind CSS    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌───────────┐  │
│  │ Auth/RBAC│ │Framework │ │  Tasks   │ │  Gantt  │ │Dashboards │  │
│  │  Module  │ │ Browser  │ │  CRUD    │ │  View   │ │& Reports  │  │
│  └──────────┘ └──────────┘ └──────────┘ └─────────┘ └───────────┘  │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ HTTPS / REST (JSON)
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       API GATEWAY / BACKEND                          │
│                                                                      │
│  Option A: Node 20 + NestJS + TypeORM + Bull (jobs) + Passport      │
│  Option B: Python 3.12 + Django 5 / FastAPI + SQLAlchemy + Celery   │
│                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Auth/JWT  │ │Framework │ │  Task    │ │  Report  │ │  Notif.  │  │
│  │MiddleWr  │ │  CRUD    │ │  Engine  │ │  Engine  │ │  Service │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────┬────────────────────────┬───────────────────┬──────────────┘
          │                        │                   │
          ▼                        ▼                   ▼
┌──────────────────┐  ┌────────────────────┐  ┌──────────────────┐
│  PostgreSQL 16   │  │  Redis (cache +    │  │  S3/MinIO (file  │
│  (primary DB)    │  │  job queue)        │  │  storage)        │
└──────────────────┘  └────────────────────┘  └──────────────────┘
```

### Hosting Options
| Option | Provider | Notes |
|--------|----------|-------|
| Cloud | AWS (ECS/Fargate + RDS + S3 + CloudFront) | Recommended for production |
| Cloud | Azure (App Service + Azure DB for PostgreSQL + Blob) | Alternative |
| Budget | Railway / Render + Supabase (managed PG) + Cloudflare R2 | Lowest cost |
| On-prem | Docker Compose on Ubuntu VPS (Hetzner/DigitalOcean) | Full control |

---

# 2. Recommended Tech Stack

## Option A: React + Node/NestJS + PostgreSQL
| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Shadcn/UI |
| State | Zustand (client), TanStack Query (server) |
| Gantt | **dhtmlxGantt** or **frappe-gantt** (open-source) |
| Charts | Recharts / Nivo |
| Backend | NestJS (Node 20), TypeORM, Passport (JWT + local), Bull (Redis queue) |
| Database | PostgreSQL 16 |
| File Storage | S3-compatible (MinIO for self-host) |
| Email | Nodemailer + SendGrid/SES |
| Cache/Queue | Redis 7 |

## Option B: React + Python (Django/FastAPI) + PostgreSQL
| Layer | Technology |
|-------|------------|
| Frontend | Same as Option A |
| Backend | Django 5 + Django REST Framework (or FastAPI + SQLAlchemy) |
| Task Queue | Celery + Redis |
| Auth | Django AllAuth + SimpleJWT |
| File Storage | django-storages → S3 |
| Email | Django email backend → SendGrid/SES |

---

# 3. Database Schema

## 3.1 Entity Relationship Diagram (ASCII)

```
users ──────┐
  │ (FK)    │
  ▼         │
roles ◄─── user_roles ──► permissions
                          
budget_holders ◄──────── users.budget_holder_id

intermediate_outcomes
    │ 1:N
    ▼
immediate_outcomes
    │ 1:N
    ▼
outputs
    │ 1:N
    ▼
activities
    │ 1:N                     ┌── attachments
    ▼                         │
tasks ──────────────────────►─┤── task_comments
    │                         │
    │                         └── task_revisions
    │
    ├── baselines / approvals
    │
    └── audit_logs (polymorphic)
```

## 3.2 Table Definitions

### `users`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen_random_uuid() |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | NOT NULL |
| phone | VARCHAR(20) | |
| is_active | BOOLEAN | DEFAULT true |
| budget_holder_id | UUID | FK → budget_holders(id), NULL |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | DEFAULT now() |

**Indexes:** `idx_users_email` UNIQUE on email; `idx_users_budget_holder` on budget_holder_id.

### `roles`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(50) | UNIQUE, NOT NULL — Admin, ME_Specialist, Budget_Holder, Implementer, Viewer |
| description | TEXT | |

### `permissions`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| resource | VARCHAR(50) | NOT NULL — e.g. 'task', 'activity', 'output', 'dashboard' |
| action | VARCHAR(20) | NOT NULL — create, read, update, delete, approve, export |

### `role_permissions`
| Column | Type | Constraints |
|--------|------|-------------|
| role_id | UUID | FK → roles(id), PK |
| permission_id | UUID | FK → permissions(id), PK |

### `user_roles`
| Column | Type | Constraints |
|--------|------|-------------|
| user_id | UUID | FK → users(id), PK |
| role_id | UUID | FK → roles(id), PK |

### `budget_holders`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(100) | UNIQUE, NOT NULL |
| created_at | TIMESTAMPTZ | DEFAULT now() |

Seed: Caro, Mwanzia, Jenard, Lilian, Benard, Agneta, Beryl

### `intermediate_outcomes`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| code | VARCHAR(10) | UNIQUE, NOT NULL — e.g. '1100' |
| description | TEXT | NOT NULL |
| sort_order | INT | NOT NULL |
| is_deleted | BOOLEAN | DEFAULT false |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### `immediate_outcomes`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| code | VARCHAR(10) | UNIQUE, NOT NULL — e.g. '1110' |
| description | TEXT | NOT NULL |
| intermediate_outcome_id | UUID | FK → intermediate_outcomes(id), NOT NULL |
| sort_order | INT | NOT NULL |
| is_deleted | BOOLEAN | DEFAULT false |
| created_at | TIMESTAMPTZ | DEFAULT now() |

**Index:** `idx_imm_out_parent` on intermediate_outcome_id.

### `outputs`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| code | VARCHAR(10) | UNIQUE, NOT NULL — e.g. '1111' |
| description | TEXT | NOT NULL |
| immediate_outcome_id | UUID | FK → immediate_outcomes(id), NOT NULL |
| sort_order | INT | NOT NULL |
| is_deleted | BOOLEAN | DEFAULT false |
| created_at | TIMESTAMPTZ | DEFAULT now() |

**Index:** `idx_outputs_parent` on immediate_outcome_id.

### `activities`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| code | VARCHAR(20) | UNIQUE, NOT NULL — e.g. '1111.1' |
| description | TEXT | NOT NULL |
| output_id | UUID | FK → outputs(id), NOT NULL |
| budget_holder_id | UUID | FK → budget_holders(id), NULL |
| status | VARCHAR(20) | DEFAULT 'Active' — Active, Completed, Suspended |
| sort_order | INT | NOT NULL |
| is_deleted | BOOLEAN | DEFAULT false |
| created_at | TIMESTAMPTZ | DEFAULT now() |

**Indexes:** `idx_activities_output` on output_id; `idx_activities_bh` on budget_holder_id.

### `tasks`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| activity_id | UUID | FK → activities(id), NOT NULL |
| name | VARCHAR(500) | NOT NULL |
| responsible_id | UUID | FK → users(id), NULL |
| plan_actual | VARCHAR(10) | NOT NULL, CHECK IN ('Planned','Actual') |
| start_date | DATE | NOT NULL |
| end_date | DATE | NOT NULL, CHECK (end_date >= start_date) |
| status | VARCHAR(20) | NOT NULL DEFAULT 'Pending', CHECK IN ('Pending','In progress','Complete','Delayed','Cancelled') |
| completion_evidence | TEXT | NULL — required when status = 'Complete' |
| baseline_id | UUID | FK → baselines(id), NULL |
| is_deleted | BOOLEAN | DEFAULT false |
| created_by | UUID | FK → users(id), NOT NULL |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | DEFAULT now() |

**Indexes:** `idx_tasks_activity` on activity_id; `idx_tasks_responsible` on responsible_id; `idx_tasks_status` on status; `idx_tasks_dates` on (start_date, end_date); `idx_tasks_plan_actual` on plan_actual.

**CHECK constraint:** `chk_complete_evidence` — When status = 'Complete', end_date must be set (enforced at app layer: evidence OR end_date required).

### `task_comments`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| task_id | UUID | FK → tasks(id), NOT NULL |
| parent_comment_id | UUID | FK → task_comments(id), NULL — for threading |
| author_id | UUID | FK → users(id), NOT NULL |
| body | TEXT | NOT NULL (rich text HTML) |
| mentions | UUID[] | Array of mentioned user IDs |
| is_deleted | BOOLEAN | DEFAULT false |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | DEFAULT now() |

**Index:** `idx_comments_task` on task_id.

### `attachments`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| task_id | UUID | FK → tasks(id), NOT NULL |
| file_name | VARCHAR(255) | NOT NULL |
| file_type | VARCHAR(10) | NOT NULL, CHECK IN ('pdf','jpg','png','xlsx','docx') |
| file_size_bytes | BIGINT | NOT NULL |
| storage_key | VARCHAR(500) | NOT NULL — S3 key |
| uploaded_by | UUID | FK → users(id), NOT NULL |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### `baselines`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| status | VARCHAR(20) | DEFAULT 'Draft', CHECK IN ('Draft','Submitted','Approved','Locked') |
| submitted_by | UUID | FK → users(id) |
| approved_by | UUID | FK → users(id) |
| submitted_at | TIMESTAMPTZ | |
| approved_at | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### `task_revisions`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| task_id | UUID | FK → tasks(id), NOT NULL |
| baseline_id | UUID | FK → baselines(id), NOT NULL |
| changed_by | UUID | FK → users(id), NOT NULL |
| field_name | VARCHAR(50) | NOT NULL |
| old_value | TEXT | |
| new_value | TEXT | |
| reason | TEXT | NOT NULL |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### `audit_logs`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users(id), NOT NULL |
| entity_type | VARCHAR(50) | NOT NULL — 'task', 'activity', 'output', etc. |
| entity_id | UUID | NOT NULL |
| action | VARCHAR(20) | NOT NULL — 'create', 'update', 'delete', 'approve' |
| changes | JSONB | — { field: { old, new } } |
| ip_address | INET | |
| created_at | TIMESTAMPTZ | DEFAULT now() |

**Indexes:** `idx_audit_entity` on (entity_type, entity_id); `idx_audit_user` on user_id; `idx_audit_created` on created_at.

### `notifications`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users(id), NOT NULL |
| type | VARCHAR(50) | NOT NULL — 'task_assigned', 'due_soon', 'overdue', 'status_change', 'mention' |
| title | VARCHAR(255) | NOT NULL |
| body | TEXT | |
| reference_type | VARCHAR(50) | |
| reference_id | UUID | |
| is_read | BOOLEAN | DEFAULT false |
| email_sent | BOOLEAN | DEFAULT false |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### `schedule_flags` (optional — for X marks from Gantt chart)
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| activity_id | UUID | FK → activities(id), NOT NULL |
| quarter | VARCHAR(5) | NOT NULL — 'Q1','Q2','Q3' or 'W1','W2','W3' |
| week | VARCHAR(10) | |
| is_planned | BOOLEAN | DEFAULT true |
| notes | TEXT | — e.g. 'refresher' |

---

# 4. API Design (REST)

Base URL: `/api/v1`

## 4.1 Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/login` | Login → returns JWT access + refresh tokens | Public |
| POST | `/auth/refresh` | Refresh access token | Refresh token |
| POST | `/auth/logout` | Invalidate refresh token | Bearer |
| GET | `/auth/me` | Get current user profile | Bearer |

### Example: POST `/auth/login`
```json
// Request
{ "email": "benard@cosme.org", "password": "••••" }

// Response 200
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "uuid",
    "full_name": "Benard",
    "roles": ["Budget_Holder"],
    "budget_holder": { "id": "uuid", "name": "Benard" }
  }
}
```

## 4.2 Framework (Results Hierarchy)
| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/intermediate-outcomes` | List all | All |
| GET | `/intermediate-outcomes/:id/immediate-outcomes` | Cascading filter | All |
| GET | `/immediate-outcomes/:id/outputs` | Cascading filter | All |
| GET | `/outputs/:id/activities` | Cascading filter | All |
| GET | `/activities/:id` | Activity detail | All |
| POST | `/intermediate-outcomes` | Create | Admin, ME |
| PUT | `/intermediate-outcomes/:id` | Update | Admin, ME |
| DELETE | `/intermediate-outcomes/:id` | Soft delete | Admin |

(Same CRUD pattern for immediate-outcomes, outputs, activities)

### Example: GET `/intermediate-outcomes/:id/immediate-outcomes`
```json
// Response 200
{
  "data": [
    {
      "id": "uuid",
      "code": "1110",
      "description": "Increased capacity of communities...",
      "intermediate_outcome_id": "uuid",
      "outputs_count": 3
    }
  ]
}
```

## 4.3 Tasks
| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/activities/:id/tasks` | List tasks for activity | All (filtered by role) |
| POST | `/activities/:id/tasks` | Create task | Admin, ME, BH (own), Implementer (assigned) |
| GET | `/tasks/:id` | Task detail + comments | All (filtered) |
| PUT | `/tasks/:id` | Update task | Admin, ME, BH (own), Implementer (assigned) |
| DELETE | `/tasks/:id` | Soft delete | Admin, ME |
| POST | `/tasks/bulk-assign` | Bulk assign responsible | Admin, ME, BH |
| POST | `/tasks/bulk-shift-dates` | Bulk shift dates | Admin, ME |
| POST | `/tasks/bulk-status` | Bulk status update | Admin, ME |
| GET | `/tasks/my-tasks` | Current user's tasks | Implementer |

### Example: POST `/activities/:id/tasks`
```json
// Request
{
  "name": "Conduct mangrove mapping in Kilifi Creek",
  "responsible_id": "uuid",
  "plan_actual": "Planned",
  "start_date": "2026-04-15",
  "end_date": "2026-05-15",
  "status": "Pending"
}

// Response 201
{
  "id": "uuid",
  "activity_id": "uuid",
  "name": "Conduct mangrove mapping in Kilifi Creek",
  "responsible": { "id": "uuid", "full_name": "Agneta" },
  "plan_actual": "Planned",
  "start_date": "15/04/2026",
  "end_date": "15/05/2026",
  "status": "Pending",
  "created_at": "2026-04-10T10:00:00+03:00"
}
```

## 4.4 Comments & Attachments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks/:id/comments` | List threaded comments |
| POST | `/tasks/:id/comments` | Add comment (supports @mentions) |
| PUT | `/comments/:id` | Edit own comment |
| DELETE | `/comments/:id` | Delete own comment |
| POST | `/tasks/:id/attachments` | Upload file (multipart/form-data) |
| GET | `/attachments/:id/download` | Download (signed URL) |
| DELETE | `/attachments/:id` | Delete attachment |

## 4.5 Gantt
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/gantt/by-activity/:id` | Tasks as Gantt data for one activity |
| GET | `/gantt/by-output/:id` | Roll-up by output |
| GET | `/gantt/by-immediate-outcome/:id` | Roll-up by immediate outcome |
| GET | `/gantt/by-intermediate-outcome/:id` | Roll-up by intermediate outcome |
| GET | `/gantt/by-budget-holder/:id` | All tasks under budget holder |
| GET | `/gantt/by-responsible/:id` | All tasks for person |
| GET | `/gantt/export` | Export Gantt to PDF/PNG |

Query params: `?status=In+progress&start=2026-01-01&end=2026-12-31&plan_actual=both&budget_holder_id=uuid`

### Gantt Response Shape
```json
{
  "bars": [
    {
      "id": "task-uuid",
      "label": "Conduct mangrove mapping...",
      "parent_code": "1111.1",
      "planned_start": "2026-04-15",
      "planned_end": "2026-05-15",
      "actual_start": "2026-04-18",
      "actual_end": null,
      "status": "In progress",
      "responsible": "Agneta",
      "variance_days": -3,
      "color": "#3B82F6"
    }
  ],
  "groups": [
    { "code": "1111.1", "label": "Map mangrove...", "level": "activity" },
    { "code": "1111", "label": "Biodiversity assessment...", "level": "output" }
  ]
}
```

## 4.6 Dashboards
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/executive` | KPIs, charts, summaries |
| GET | `/dashboard/budget-holder/:id` | BH-specific dashboard |
| GET | `/dashboard/my-tasks` | Implementer dashboard |
| GET | `/dashboard/export` | Export dashboard to PDF/Excel |

## 4.7 Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/activity-progress` | Activity progress report |
| GET | `/reports/output-completion` | Output completion report |
| GET | `/reports/variance` | Planned vs actual variance |
| GET | `/reports/workload` | Responsible person workload |
| GET | `/reports/dip-export?format=excel` | Full DIP export |
| GET | `/reports/dip-export?format=pdf` | Full DIP PDF |

## 4.8 Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | List users |
| POST | `/admin/users` | Create user |
| PUT | `/admin/users/:id` | Update user/roles |
| DELETE | `/admin/users/:id` | Deactivate user |
| GET | `/admin/roles` | List roles + permissions |
| PUT | `/admin/roles/:id/permissions` | Update role permissions |
| GET | `/admin/audit-logs` | Query audit logs |
| POST | `/admin/baselines` | Create baseline |
| PUT | `/admin/baselines/:id/approve` | Approve baseline |

## 4.9 Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications` | List current user's notifications |
| PUT | `/notifications/:id/read` | Mark as read |
| PUT | `/notifications/read-all` | Mark all as read |

---

# 5. UI Wireframes (Text Descriptions)

## 5.1 Login Page
```
┌────────────────────────────────────────────┐
│              COSME DIP Tracker             │
│                                            │
│     ┌────────────────────────────┐         │
│     │ Email                      │         │
│     └────────────────────────────┘         │
│     ┌────────────────────────────┐         │
│     │ Password           👁      │         │
│     └────────────────────────────┘         │
│                                            │
│     [        Sign In        ]              │
│                                            │
│     Forgot password?                       │
└────────────────────────────────────────────┘
```
- Form validation: email format, required fields
- CAPTCHA after 3 failed attempts
- Redirects to Implementation Plan on success

## 5.2 Implementation Plan — Cascading Selection
```
┌─────────────────────────────────────────────────────────────────┐
│ ☰ COSME DIP    Implementation Plan  Gantt  Dashboard  Reports  │
│                                              🔔(3)  👤 Benard ▾│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Budget Holder:  [ Benard              ▾ ]                     │
│                                                                 │
│  Intermediate Outcome:                                          │
│  [ 1100 Enhanced adoption of gender-responsive... ▾ ]          │
│                                                                 │
│  Immediate Outcome:                                             │
│  [ 1110 Increased capacity of communities...      ▾ ]          │
│                                                                 │
│  Output:                                                        │
│  [ 1111 Biodiversity assessment for mangrove...   ▾ ]          │
│                                                                 │
│  Activities under Output 1111:                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ▶ 1111.1 Map mangrove and other coastal forest...  (3) │  │
│  │ ▶ 1111.2 Conduct biodiversity assessment on...     (5) │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Click an activity to expand tasks ↓                            │
└─────────────────────────────────────────────────────────────────┘
```
Each dropdown filters the next. Activity cards show task count badge. Budget Holders see only their portfolio.

## 5.3 Activity Detail + Task Table Grid
```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back to Output 1111                                           │
│                                                                 │
│ Activity 1111.1                                                │
│ Map mangrove and other coastal forest ecosystems                │
│ Budget Holder: Benard    Status: Active                        │
│                                                                 │
│ ┌─ Tasks ──────────────────────────────────────────────────┐   │
│ │ [+ New Task]  [Bulk Actions ▾]  Filter: [All Status ▾]  │   │
│ │                                                          │   │
│ │ □ Task Name       Resp.   Type    Start     End      St. │   │
│ │ ─────────────────────────────────────────────────────────│   │
│ │ □ Map Kilifi Crk  Agneta  Planned 15/04/26  15/05/26 🔵 │   │
│ │ □ Map Lamu sites  Beryl   Planned 01/05/26  30/05/26 ⚪ │   │
│ │ □ Map Kilifi Crk  Agneta  Actual  18/04/26  —        🔵 │   │
│ │                                                          │   │
│ │ Showing 3 of 3 tasks                                     │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│ [View Gantt for this Activity]                                  │
└─────────────────────────────────────────────────────────────────┘
```
Status icons: ⚪ Pending, 🔵 In progress, 🟢 Complete, 🟠 Delayed, ⚫ Cancelled
Inline editing on double-click; row checkbox for bulk ops.

## 5.4 Add/Edit Task Modal
```
┌─────────────── Add New Task ──────────────────┐
│                                               │
│  Task Name *                                  │
│  ┌───────────────────────────────────────┐    │
│  │                                       │    │
│  └───────────────────────────────────────┘    │
│                                               │
│  Responsible *       Planned/Actual *         │
│  [ Select user  ▾ ] [ Planned       ▾ ]      │
│                                               │
│  Start Date *        End Date *               │
│  [ dd/mm/yyyy 📅 ]  [ dd/mm/yyyy 📅 ]       │
│                                               │
│  Status *                                     │
│  [ Pending           ▾ ]                      │
│                                               │
│  Comments                                     │
│  ┌───────────────────────────────────────┐    │
│  │ B I U  | 📎 Attach  | @mention       │    │
│  │                                       │    │
│  │                                       │    │
│  └───────────────────────────────────────┘    │
│                                               │
│  Attachments                                  │
│  [📎 Upload File] (PDF/JPG/PNG/XLSX/DOCX)   │
│                                               │
│  ┌──────┐  ┌────────────┐                     │
│  │Cancel│  │ Save Task  │                     │
│  └──────┘  └────────────┘                     │
└───────────────────────────────────────────────┘
```
- Validation: name required, end ≥ start, evidence-on-complete check
- Rich text editor for comments (TipTap or Quill)
- File drag & drop zone

## 5.5 Gantt Page
```
┌─────────────────────────────────────────────────────────────────┐
│ Gantt Chart                                    [Export PDF/PNG] │
│                                                                 │
│ View: [By Activity ▾]  BH: [All ▾]  Resp: [All ▾]            │
│ Status: [All ▾]  Date: [01/01/2026] → [31/12/2026]            │
│ [✓] Show Planned vs Actual overlay                             │
│                                                                 │
│ Timeline ──────── Apr 2026 ────────── May 2026 ──────────      │
│                                                                 │
│ 1111.1 Map mangrove...                                          │
│   ████████████████████  (Planned - blue)                        │
│   ░░░░░░░░░░░░░░░░░░░░░░░ (Actual - hatched, +3 days late)    │
│                                                                 │
│ 1111.2 Conduct bio...                                           │
│   ██████████████  (Planned - grey/pending)                      │
│                                                                 │
│ ─────────────────────────────────────────────────               │
│ Legend: ⬜Pending 🟦In progress 🟩Complete 🟧Delayed ⬛Cancel.  │
│ Variance: +N days late shown as red tag | -N days ahead green   │
└─────────────────────────────────────────────────────────────────┘
```

## 5.6 Dashboards Page

### Executive / M&E Dashboard
```
┌─────────────────────────────────────────────────────────────────┐
│ Dashboard          Filter: [All BH ▾] [Date Range]  [Export ▾] │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│ Total Tasks │ % Complete   │ On-Time Rate │ Avg Days Overdue   │
│    247      │    42%       │    78%       │     8.3            │
├─────────────┴──────────────┴──────────────┴────────────────────┤
│                                                                 │
│  ┌──── Tasks by Status ────┐  ┌──── Completion Trend ────────┐ │
│  │ 🟦 In progress  68     │  │ Line chart: weekly cumulative │ │
│  │ ⬜ Pending      45     │  │ planned vs actual complete    │ │
│  │ 🟩 Complete    104     │  │                               │ │
│  │ 🟧 Delayed      22     │  └───────────────────────────────┘ │
│  │ ⬛ Cancelled     8     │                                    │
│  └─────────────────────────┘                                    │
│                                                                 │
│  ┌──── Top 5 Delayed ─────┐  ┌──── Workload by Person ──────┐ │
│  │ 1. Activity 1122.4 +21d│  │ Bar chart: tasks per person   │ │
│  │ 2. Activity 1221.5 +14d│  │ stacked by status             │ │
│  │ ...                     │  └───────────────────────────────┘ │
│  └─────────────────────────┘                                    │
│                                                                 │
│  ┌──── Planned vs Actual Variance Summary ────────────────────┐ │
│  │ Scatter plot: each output as dot, x=planned days,          │ │
│  │ y=actual days, diagonal = on-time line                     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Budget Holder Dashboard
```
┌─────────────────────────────────────────────────────────────────┐
│ My Portfolio — Benard                               [Export ▾]  │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│ My Outputs  │ My Tasks     │ Due < 14 days│ Overdue            │
│    5        │    32        │    8         │    3               │
├─────────────┴──────────────┴──────────────┴────────────────────┤
│                                                                 │
│  ┌──── Activities Under My Portfolio ─────────────────────────┐ │
│  │ 1111.1 Map mangrove...      [3 tasks] [67% complete]      │ │
│  │ 1112.3 Develop content...   [5 tasks] [40% complete]      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──── Due Soon (14 days) ────┐ ┌──── Overdue ──────────────┐  │
│  │ Task list sorted by due    │ │ Task list sorted by days   │  │
│  │ date ascending             │ │ overdue descending         │  │
│  └────────────────────────────┘ └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementer Dashboard
```
┌─────────────────────────────────────────────────────────────────┐
│ My Tasks — Agneta                                               │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│ Assigned    │ In Progress  │ Completed    │ Overdue            │
│    12       │     4        │     6        │     2              │
├─────────────┴──────────────┴──────────────┴────────────────────┤
│                                                                 │
│  ┌──── Quick Update ──────────────────────────────────────────┐ │
│  │ Task: Map Kilifi Creek                                     │ │
│  │ Status: [In progress ▾]  End: [dd/mm/yyyy]                │ │
│  │ Comment: [_____________]  [💾 Save]                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Tab: [Due Soon] [Overdue] [Completed] [All]                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ □ Map Kilifi Creek    1111.1  Due: 15/05/26  🔵           │ │
│  │ □ Assess Lamu sites   1111.2  Due: 30/05/26  ⚪           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 5.7 Admin Settings + User Management
```
┌─────────────────────────────────────────────────────────────────┐
│ Admin Settings                                                  │
│                                                                 │
│ [Users] [Roles & Permissions] [Budget Holders] [Framework]      │
│ [Baselines] [Audit Log]                                         │
│                                                                 │
│ ── Users ───────────────────────────────────────────────────── │
│ [+ Add User]  Search: [____________]  Role: [All ▾]           │
│                                                                 │
│ Name          Email              Roles          BH      Active  │
│ ────────────────────────────────────────────────────────────── │
│ Benard M.     benard@cosme.org   Budget_Holder  Benard  ✓      │
│ Agneta W.     agneta@cosme.org   Implementer    —       ✓      │
│ Admin         admin@cosme.org    Admin          —       ✓      │
│                                                                 │
│ [Edit] [Deactivate]                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

# 6. Gantt Logic

## 6.1 Bar Computation
Each **task** with `start_date` and `end_date` produces one Gantt bar.
- **X position** = start_date mapped to timeline scale (days)
- **Width** = (end_date − start_date) in days + 1
- **Y position** = row index, grouped under parent activity
- **Color** = status-based:
  | Status | Color |
  |--------|-------|
  | Pending | `#9CA3AF` (grey) |
  | In progress | `#3B82F6` (blue) |
  | Complete | `#22C55E` (green) |
  | Delayed | `#F97316` (orange) |
  | Cancelled | `#4B5563` (dark grey) |

## 6.2 Planned vs Actual Overlay
For each activity, tasks are paired by `plan_actual` field:
1. Query all tasks for the activity.
2. Group by task semantic key (activity + task name pattern).
3. Render **Planned** bar (solid) above **Actual** bar (hatched/striped).
4. Calculate variance:
   - `variance_start = actual_start - planned_start` (days)
   - `variance_end = actual_end - planned_end` (days; null if in progress)
   - Positive = late, Negative = early
5. Display variance label on the Actual bar: e.g. "+3d late" or "−2d ahead"

## 6.3 Roll-Up Calculation
| Level | Start | End | Progress |
|-------|-------|-----|----------|
| **Activity** | MIN(task.start_date) for all tasks under activity | MAX(task.end_date) | % tasks Complete |
| **Output** | MIN(activity.rolled_start) for all activities under output | MAX(activity.rolled_end) | AVG(activity.progress) |
| **Immediate Outcome** | MIN(output.rolled_start) | MAX(output.rolled_end) | AVG(output.progress) |
| **Intermediate Outcome** | MIN(immediate.rolled_start) | MAX(immediate.rolled_end) | AVG(immediate.progress) |

Roll-up bars are rendered as **summary bars** (thicker, with progress indicator).

## 6.4 Export
- Server-side: Use Puppeteer (Node) or WeasyPrint (Python) to render the Gantt HTML → PDF/PNG.
- Client-side fallback: html2canvas → PNG download.

---

# 7. KPI Definitions & Formulas

| KPI | Formula | Dashboard |
|-----|---------|-----------|
| **% Tasks Complete** | `COUNT(tasks WHERE status='Complete') / COUNT(all tasks) × 100` | Executive |
| **On-Time Completion Rate** | `COUNT(tasks WHERE status='Complete' AND actual_end <= planned_end) / COUNT(complete tasks) × 100` | Executive |
| **Tasks by Status** | `GROUP BY status → COUNT` | Executive |
| **Avg Days Overdue** | `AVG(CURRENT_DATE - planned_end) WHERE status IN ('In progress','Delayed') AND planned_end < CURRENT_DATE` | Executive |
| **Delayed Task Ageing** | `CURRENT_DATE - planned_end` per task, bucketed: 1-7d, 8-14d, 15-30d, 30+d | Executive |
| **Variance (days)** | For paired planned/actual tasks: `actual_date - planned_date` | Gantt, Variance Report |
| **Workload Distribution** | `COUNT(tasks) GROUP BY responsible_id, status` | Executive |
| **Due Soon** | `COUNT(tasks WHERE end_date BETWEEN NOW() AND NOW()+14d AND status NOT IN ('Complete','Cancelled'))` | BH |
| **Overdue Count** | `COUNT(tasks WHERE end_date < NOW() AND status NOT IN ('Complete','Cancelled'))` | BH, Implementer |
| **Output Completion %** | `COUNT(complete tasks under output) / COUNT(all tasks under output) × 100` | Reports |
| **Activity Progress** | Same formula scoped to activity | Reports |

---

# 8. Permissions Matrix by Role

| Resource / Action | Admin | M&E Specialist | Budget Holder | Implementer | Viewer/Donor |
|-------------------|-------|----------------|---------------|-------------|--------------|
| **Intermediate Outcome** | | | | | |
| Create/Edit/Delete | ✅ | ✅ | ❌ | ❌ | ❌ |
| View | ✅ | ✅ | ✅ (own BH) | ✅ (assigned) | ✅ |
| **Immediate Outcome** | | | | | |
| Create/Edit/Delete | ✅ | ✅ | ❌ | ❌ | ❌ |
| View | ✅ | ✅ | ✅ (own BH) | ✅ (assigned) | ✅ |
| **Output** | | | | | |
| Create/Edit/Delete | ✅ | ✅ | ❌ | ❌ | ❌ |
| View | ✅ | ✅ | ✅ (own BH) | ✅ (assigned) | ✅ |
| **Activity** | | | | | |
| Create/Edit | ✅ | ✅ | ✅ (own BH) | ❌ | ❌ |
| Delete | ✅ | ✅ | ❌ | ❌ | ❌ |
| View | ✅ | ✅ | ✅ (own BH) | ✅ (assigned) | ✅ |
| **Task** | | | | | |
| Create | ✅ | ✅ | ✅ (own BH) | ✅ (under assigned activity) | ❌ |
| Edit | ✅ | ✅ | ✅ (own BH) | ✅ (own tasks) | ❌ |
| Delete | ✅ | ✅ | ❌ | ❌ | ❌ |
| Bulk Ops | ✅ | ✅ | ✅ (own BH) | ❌ | ❌ |
| View | ✅ | ✅ | ✅ (own BH) | ✅ (own tasks) | ✅ |
| **Comments** | | | | | |
| Create/Edit own | ✅ | ✅ | ✅ | ✅ | ❌ |
| Delete any | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Attachments** | | | | | |
| Upload | ✅ | ✅ | ✅ | ✅ | ❌ |
| Download | ✅ | ✅ | ✅ | ✅ | ✅ |
| Delete | ✅ | ✅ (own) | ✅ (own) | ✅ (own) | ❌ |
| **Dashboards** | | | | | |
| Executive | ✅ | ✅ | ❌ | ❌ | ✅ |
| Budget Holder | ✅ | ✅ | ✅ (own) | ❌ | ❌ |
| Implementer | ✅ | ✅ | ❌ | ✅ (own) | ❌ |
| **Reports / Export** | | | | | |
| All reports | ✅ | ✅ | ✅ (own BH scope) | ❌ | ✅ (read-only) |
| Export Excel/PDF | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Baseline / Approval** | | | | | |
| Create baseline | ✅ | ✅ | ❌ | ❌ | ❌ |
| Submit | ✅ | ✅ | ✅ (own BH) | ❌ | ❌ |
| Approve | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Audit Log** | | | | | |
| View | ✅ | ✅ | ❌ | ❌ | ❌ |
| **User Management** | | | | | |
| CRUD users/roles | ✅ | ❌ | ❌ | ❌ | ❌ |

---

# 9. Testing Plan

## 9.1 Unit Tests
| Module | Test Cases |
|--------|-----------|
| Auth | JWT generation/validation, password hashing, role extraction |
| Framework CRUD | Create/read/update/soft-delete for each entity, code uniqueness |
| Task validation | end ≥ start, status transitions, complete-requires-evidence |
| Gantt computation | Bar position, roll-up MIN/MAX, variance calculation |
| KPI formulas | Completion %, on-time rate, overdue counts with test datasets |
| RBAC middleware | Permit/deny per role matrix above |

**Coverage target:** ≥ 80% on business logic.

## 9.2 Integration Tests
| Scenario | Description |
|----------|-------------|
| Cascading selection | Select IntOutcome → verify correct ImmOutcomes returned → verify correct Outputs → Activities |
| Task lifecycle | Create Planned task → update to In progress → add Actual task → mark Complete with evidence |
| Bulk operations | Select 5 tasks → bulk shift dates +7 → verify all dates shifted |
| Gantt API | Create tasks → hit gantt endpoint → verify bar data matches |
| Auth flow | Login → access protected endpoint → refresh token → access again |
| File upload | Upload PDF → verify stored in S3 → download via signed URL |
| Notifications | Assign task → verify notification created for assignee |
| Audit trail | Update task status → verify audit_logs entry with old/new values |

## 9.3 UAT Scenarios
| # | Scenario | Persona | Steps |
|---|----------|---------|-------|
| 1 | Budget Holder views portfolio | Benard (BH) | Login → see BH dashboard → verify only own activities visible → navigate to activity → see tasks |
| 2 | Create and track task | Agneta (Impl.) | Login → navigate to assigned activity → create task → set dates → save → see in Gantt |
| 3 | Planned vs Actual tracking | M&E | Create Planned task → later create Actual task → open Gantt → toggle overlay → verify variance shown |
| 4 | Bulk date shift | M&E | Select multiple tasks → bulk shift +14 days → verify dates updated → check Gantt updated |
| 5 | Complete with evidence | Implementer | Update task to Complete without evidence → see validation error → attach PDF → mark Complete → success |
| 6 | Dashboard accuracy | Donor (Viewer) | Login → view Executive dashboard → verify KPI numbers match manual count from task list |
| 7 | Export DIP | M&E | Go to Reports → Export DIP Excel → open file → verify framework hierarchy + tasks present |
| 8 | Baseline approval | Admin | Create baseline → BH submits → Admin approves → verify tasks locked → attempt edit → see "revision required" |
| 9 | Threaded comments + @mention | Implementer | Open task → add comment @Benard → verify Benard sees notification |
| 10 | Overdue notification | System | Set task end_date to yesterday → run scheduled job → verify in-app + email notification sent |

---

# 10. Implementation Phases

## Phase 1: MVP (Weeks 1–6)
**Goal:** Core framework browsing, task CRUD, basic Gantt.

| Deliverable | Details |
|-------------|---------|
| Auth | Login/logout, JWT, basic RBAC (Admin + ME + BH + Implementer) |
| DB + Seed | Full schema, seed framework from docx (all 3 Intermediate Outcomes, 10 Immediate Outcomes, ~30 Outputs, ~100 Activities), seed Budget Holders |
| Framework browser | Cascading dropdowns: IntOutcome → ImmOutcome → Output → Activity |
| Task CRUD | Create/edit/delete tasks, all required fields, validation |
| Basic Gantt | By-activity Gantt view, colour by status, date range filter |
| Responsive layout | Mobile-first navigation, collapsible sidebar |

## Phase 2: V1 (Weeks 7–12)
**Goal:** Full dashboards, exports, notifications, Gantt enhancements.

| Deliverable | Details |
|-------------|---------|
| Planned vs Actual | Overlay toggle on Gantt, variance display |
| Roll-up Gantt | By Output, Immediate Outcome, Intermediate Outcome, BH, Responsible |
| Gantt export | PDF/PNG export |
| Dashboards | Executive, BH, Implementer dashboards with all KPIs |
| Reports | Activity progress, output completion, variance, workload reports |
| DIP Export | Excel (pivot-friendly) + PDF |
| Bulk operations | Bulk assign, shift dates, status update |
| Comments | Threaded comments, @mentions, rich text |
| Attachments | File upload/download with S3 |
| Notifications | In-app + email: assignment, due soon (14d), overdue, status change, mentions |

## Phase 3: V2 (Weeks 13–18)
**Goal:** Governance, advanced analytics, offline support.

| Deliverable | Details |
|-------------|---------|
| Baselines | Draft → Submitted → Approved → Locked workflow |
| Change control | Revision records for edits after baseline lock |
| Audit trail UI | Searchable audit log in admin panel |
| Dashboard enhancements | Trend charts, delayed ageing buckets, predictive completion |
| Scheduled emails | Weekly/monthly digest summaries via Celery/Bull cron |
| Offline support | Service worker + IndexedDB for task updates while offline, sync on reconnect |
| Advanced filters | Saved filter presets, shareable URLs |
| Accessibility | WCAG 2.1 AA audit, keyboard navigation, screen reader labels |

---

# 11. Seed Data — Results Framework

Below is the complete hierarchy extracted from the Gannt_Chart.docx file, to be seeded into the database on first deployment.

## Intermediate Outcome 1100
**1100** — Enhanced adoption of gender-responsive and socially inclusive nature-based solutions (NbS) for climate change adaptation with biodiversity and ecosystem integrity co-benefits

### Immediate Outcome 1110
**1110** — Increased capacity of communities, especially women, to undertake gender-responsive and equitable mangrove restoration and conservation with biodiversity co-benefits

| Output | Activities |
|--------|-----------|
| **1111** Biodiversity assessment for mangrove restoration conducted | 1111.1 Map mangrove and other coastal forest ecosystems (current and potential) |
| | 1111.2 Conduct biodiversity assessment on mangroves ecosystems in target communities |
| **1112** Members of mangrove groups trained and coached in mangrove restoration, conservation | 1112.1 Identify mangrove groups (current and potential) to be trained |
| | 1112.2 Conduct TNA and opportunities on mangrove restoration, conservation |
| | 1112.3 Develop/tailor content for training on mangrove restoration, conservation |
| | 1112.4 Provide ToT on mangrove restoration, conservation |
| | 1112.5 Train mangrove groups on restoration and conservation |
| | 1112.6 Provide follow-up and ongoing mentorship support |
| **1113** Mangrove groups equipped with restoration and conservation inputs | 1113.1 Support mangrove groups to become formally registered BMUs and CFAs |
| | 1113.2 Provide inputs for mangrove restoration and conservation to mangrove groups |

### Immediate Outcome 1120
**1120** — Increased capacity of women-led cooperatives to undertake regenerative and sustainable seaweed production, value addition and commercialization

| Output | Activities |
|--------|-----------|
| **1121** Gendered market and environmental assessment, and research into improved seaweed varietals conducted | 1121.1 Review cultural and environmental context for local seaweed cultivation |
| | 1121.2 Undertake research and development into climate-resilient seaweed varietals and biobank |
| | 1121.3 Undertake gendered local and export market analysis and value addition opportunities |
| | 1121.4 Develop and distribute one-year outlook tide table |
| **1122** Women-led seaweed groups trained in seaweed production, value addition and commercialization | 1122.1 Identify women-led seaweed groups |
| | 1122.2 Develop and adapt training materials on seaweed production, value addition and commercialization |
| | 1122.3 Conduct ToT on seaweed production, value addition and commercialization |
| | 1122.4 Conduct training for women-led groups on seaweed production, value addition and commercialization |
| | 1122.5 Provide follow-up and ongoing mentorship support |
| **1123** Women-led seaweed groups provided with inputs to sustain or improve seaweed production | 1123.1 Undertake needs assessment of equipment and supplies |
| | 1123.2 Provide inputs to women-led seaweed groups |
| | 1123.3 Develop nursery to support biobank and seaweed groups |
| | 1123.4 Develop sustainable mechanism for groups' access to biobank |
| **1124** High-capacity women-led seaweed groups supported through innovation pilots | 1124.1 Identify women-led seaweed groups with capacity to participate in innovation pilots |
| | 1124.2 Develop innovations for crop resilience, yield improvement, or value-addition |
| | 1124.3 Implement innovation pilots with selected women-led seaweed groups |
| | 1124.4 Document and disseminate lessons learned |

### Immediate Outcome 1130
**1130** — Increased capacity of communities, especially women, to undertake gender-responsive, locally-led forest management and conservation

| Output | Activities |
|--------|-----------|
| **1131** Targeted local communities trained in gender-responsive forest management and conservation | 1131.1 Lead sensitization sessions on gender-focused conservation |
| | 1131.2 Develop training content on sustainable forest regeneration, enrichment planting, wildfire management |
| | 1131.3 Conduct training sessions with forest conservation groups |
| **1132** Targeted local women's groups supported to promote and pilot NbS based on forestry | 1132.1 Facilitate gender-responsive actions on sustainable forest regeneration |
| | 1132.2 Promote local community members, especially women, in governance structures |
| | 1132.3 Increase community-led forest monitoring and patrols |

---

## Intermediate Outcome 1200
**1200** — Increased agency of women in their diversity to exercise their right to participate in gender-responsive, nature-based solutions with biodiversity co-benefits

### Immediate Outcome 1210
**1210** — Increased knowledge and skills of women on gender responsive NbS, economic rights, life skills, & GE&I

| Output | Activities |
|--------|-----------|
| **1211** Targeted women trained on gender responsive NbS, economic rights, life skills, & GE&I, including UPCW | 1211.1 Develop and adapt content for training on climate change, economic rights, life skills, & GE&I |
| | 1211.2 Provide ToT on climate change, economic rights, life skills, & GE&I |
| | 1211.3 Conduct trainings and provide coaching with women |
| | 1211.4 Facilitate peer to peer learning exchanges among targeted women |
| | 1211.5 Provide post-training support and follow-up, including referrals |

### Immediate Outcome 1220
**1220** — Increased access to resilience building assets and opportunities for women

| Output | Activities |
|--------|-----------|
| **1221** Women's savings groups established or strengthened | 1221.1 Map existing SGs and identify communities for new groups |
| | 1221.2 Review and adapt SG materials |
| | 1221.3 Provide supplies to new and existing SGs (box, passbook, stamps) |
| | 1221.4 Train community-based trainers (CBTs) as facilitators on SG methodologies |
| | 1221.5 Roll out SGs and deliver foundational training |
| | 1221.6 Provide regular monitoring and support to SGs |
| | 1221.7 Create linkages with financial institutions to offer credit facilities to women |
| **1222** Women-led demonstration plots on regenerative agriculture supported | 1222.1 Identify shared land for demonstration plots |
| | 1222.2 Develop and adapt training materials on regenerative agriculture |
| | 1222.3 Identify and train facilitators for the training |
| | 1222.4 Deliver training to targeted households on regenerative agriculture |
| | 1222.5 Provide rainwater harvesting and drip-irrigation solutions |
| | 1222.6 Provide input support (seeds, nature fertilizer, farm tools) |
| | 1222.7 Undertake post training assessment and follow-up coaching |
| | 1222.8 Hold awareness information dissemination sessions |
| **1223** Solar and improved technology solutions distributed to targeted women | 1223.1 Train partners/participants on solar panels, cook stoves operation |
| | 1223.2 Procure and distribute solar kits and solar panels |
| | 1223.3 Procure and distribute fuel efficient cooking supplies |

### Immediate Outcome 1230
**1230** — Increased capacity of community members and leaders, particularly men, to promote and support gender equality, women's rights and engagement in gender-responsive NbS

| Output | Activities |
|--------|-----------|
| **1231** SBCC strategy to promote gender responsive NbS, economic rights & GE&I, including UPCW | 1231.1 Conduct participatory design workshop to inform and design SBCC strategy |
| | 1231.2 Develop/adapt content for SBCC material |
| | 1231.3 Print material and produce media for SBCC strategy |
| | 1231.4 Implement SBCC strategy (launch, community fairs, murals, radio programs, banners) |
| **1232** Change Agents trained and supported to promote gender responsive NbS | 1232.1 Map and identify potential Change Agents |
| | 1232.2 Develop/contextualize training material for Change Agents |
| | 1232.3 Train Change Agents |
| | 1232.4 Support Change Agents to develop community sensitization action plans |
| | 1232.5 Provide Change Agents with technical follow-up and materials |
| | 1232.6 Organize regional experience-sharing and learning exchanges |
| | 1232.7 Organize inter-generational dialogues between YLOs and Change Agents |
| **1233** Men trained to promote and support gender responsive NbS, economic rights & GE&I | 1233.1 Engage and recruit training participants as Male Champions |
| | 1233.2 Develop and adapt content for training, including retention strategy |
| | 1233.3 Provide ToT on training content |
| | 1233.4 Conduct trainings and provide coaching |
| | 1233.5 Conduct post training coaching and mentoring sessions |
| **1234** Inclusive gender-transformative household action plans developed and implemented | 1234.1 Develop and adapt household action plan methodology and tools |
| | 1234.2 Provide ToT on household action plan methodology and tools |
| | 1234.3 Facilitate the development of household action plans with targeted families |
| | 1234.4 Monitor implementation of household action plans |
| | 1234.5 Facilitate reflection and sharing between targeted households and communities |

---

## Intermediate Outcome 1300
**1300** — Improved gender-responsive and child/youth-friendly governance for climate adaptation, resilience and biodiversity

### Immediate Outcome 1310
**1310** — Increased awareness and knowledge of primary school children, particularly girls, on climate change, NbS, and conservation

| Output | Activities |
|--------|-----------|
| **1311** 4K and Roots and Shoots clubs established and trained on climate change and conservation | 1311.1 Conduct project sensitization to MoE, TSC and schools (**Completed**) |
| | 1311.2 Map existing 4K and Roots and Shoots school clubs (**Completed**) |
| | 1311.3 Establish new 4K and Roots and Shoots clubs where not existing |
| | 1311.4 Revise and contextualize training program material and methodology |
| | 1311.5 Train facilitators on program methodology and CP |
| | 1311.6 Implement training program with groups |
| | 1311.7 Provide coaching, mentoring and supportive supervision |
| **1312** 4K and Roots and Shoots clubs supported to implement community based initiatives | 1312.1 Support the development of community based climate change initiatives |
| | 1312.2 Provide material support for implementation |
| | 1312.3 Facilitate learning and sharing exchanges |
| **1313** Innovative clean water solution established in targeted schools | 1313.1 Form and build capacity of school-based water management clubs |
| | 1313.2 Provide Solvatten kits in targeted schools |
| | 1313.3 Establish demonstration plots for drip-irrigation at target schools |
| | 1313.4 Provide rainwater harvesting and drip-irrigation solutions |

### Immediate Outcome 1320
**1320** — Strengthened gender responsive community governance structures to reduce risk and enhance preparedness to climate change

| Output | Activities |
|--------|-----------|
| **1321** Community-level gender responsive adaptation and preparedness plans developed and funded | 1321.1 Develop and adapt participatory risk assessment tools and methodology |
| | 1321.2 Train facilitators on participatory risk assessment |
| | 1321.3 Conduct participatory multi-hazard risk assessment |
| | 1321.4 Analyze and summarize findings from multi-hazard risk assessment |
| | 1321.5 Facilitate participatory planning with community stakeholders |
| | 1321.6 Provide material support for selected initiatives |
| | 1321.7 Provide ongoing supportive supervision |
| **1322** Communities linked with county level and national climate funds | 1322.1 Map existing national and county climate funding mechanisms |
| | 1322.2 Raise awareness to communities on funding mechanisms |
| | 1322.3 Support communities to access climate action funding |
| **1323** High-level event held to profile and promote gender responsive NbS | 1323.1 Document knowledge and prepare materials for sharing |
| | 1323.2 Hold high-level national learning and sharing event |

### Immediate Outcome 1330
**1330** — Increased ability of WRO and YLOs to undertake evidenced-based advocacy for gender responsive and inclusive climate adaptation and resilience

| Output | Activities |
|--------|-----------|
| **1331** Evidence on benefits generated through M&E systems and specialized research | 1331.1 Conduct Baseline, GBA+ and endline evaluation studies |
| | 1331.2 Conduct rapid biodiversity and gendered climate risk assessment |
| | 1331.3 Set up project Management Information System (MIS) |
| | 1331.4 Research business case for payment for ecosystem services |
| | 1331.5 Conduct specialized research on social, economic, climate and biodiversity benefits of NbS |
| **1332** Evidence disseminated to communities, governments, research institutions | 1332.1 Develop knowledge management and dissemination strategy |
| | 1332.2 Edit and print material as per audiences targeted |
| | 1332.3 Distribute material to targeted audiences |
| | 1332.4 Organize information sharing events |
| **1333** Members of WRO and YLOs trained on leadership, gender and climate change, and advocacy | 1333.1 Conduct mapping of WRO and YLOs |
| | 1333.2 Conduct capacity needs assessment of WROs and YLOs |
| | 1333.3 Develop training package for WROs and YLOs |
| | 1333.4 Deliver ToT on leadership, gender and climate change, and advocacy |
| | 1333.5 Train WRO and YLO members |
| | 1333.6 Organize information sharing events with WROs and YLOs |
| **1334** WRO and YLOs' evidenced-based advocacy plans supported | 1334.1 Support WROs and YLOs on the development of advocacy plans |
| | 1334.2 Provide inputs to WROs and YLOs for implementation |
| | 1334.3 Provide supportive supervision during implementation |

---

# 12. Non-Functional Requirements Summary

| Requirement | Implementation |
|-------------|---------------|
| **Responsive UI** | Tailwind CSS mobile-first breakpoints; collapsible sidebar; touch-friendly task grid |
| **Low bandwidth** | Lazy loading, code splitting (Vite), compressed API responses (gzip/brotli), pagination, React Query caching |
| **TLS** | HTTPS everywhere; HSTS header; free cert via Let's Encrypt or AWS ACM |
| **Password security** | bcrypt (cost 12) or argon2; minimum 8 chars; no plaintext storage |
| **Sessions/JWT** | Access token (15 min) + refresh token (7 days, rotated); HttpOnly secure cookies for refresh |
| **RBAC enforcement** | Middleware on every API route + conditional UI rendering; deny by default |
| **Data integrity** | FK constraints, CHECK constraints, unique indexes, soft delete (is_deleted flag) |
| **Backups** | Automated daily PG dump (pg_dump) → S3 with 30-day retention |
| **Error logging** | Structured JSON logs (Winston/Pino or Python logging), Sentry for error tracking |
| **Monitoring** | Health check endpoint `/health`; uptime monitoring (UptimeRobot); optional Prometheus + Grafana |
| **Accessibility** | Semantic HTML, ARIA labels, 4.5:1 contrast ratio, keyboard navigation, focus indicators |
| **Timezone** | All timestamps stored as UTC; displayed as `Africa/Nairobi` (UTC+3); date format `dd/mm/yyyy` |

---

# 13. Notification Rules

| Trigger | Recipients | Channel | Timing |
|---------|-----------|---------|--------|
| Task assigned | Assignee (responsible) | In-app + email | Immediate |
| Due in 14 days | Responsible + BH | In-app | Daily cron check |
| Due in 3 days | Responsible | In-app + email | Daily cron check |
| Overdue (1 day) | Responsible + BH | In-app + email | Daily cron check |
| Overdue (7+ days) | Responsible + BH + M&E | In-app + email | Weekly escalation |
| Status → Delayed | BH + M&E | In-app + email | Immediate |
| Status → Cancelled | BH + M&E | In-app + email | Immediate |
| Comment @mention | Mentioned user(s) | In-app + email | Immediate |
| Baseline submitted | Admin + M&E | In-app | Immediate |
| Baseline approved | BH (submitter) | In-app + email | Immediate |

---

**Selected Stack: Python 3.12 + Flask + PostgreSQL** (matching Vehicle Request Tracker on PythonAnywhere)

<function_calls>
<invoke name="manage_todo_list">
<parameter name="todoList">[{"id": 1, "status": "completed", "title": "Extract Gannt_Chart.docx data"}, {"id": 2, "status": "completed", "title": "Design full system specification"}, {"id": 3, "status": "completed", "title": "Write specification document"}]