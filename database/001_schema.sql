-- ============================================================================
-- COSME Procurement Tracking System — Database Schema
-- PostgreSQL 15+
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- LOOKUP / REFERENCE TABLES
-- ============================================================================

CREATE TABLE projects (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_name    VARCHAR(200) NOT NULL,
    project_code    VARCHAR(50) NOT NULL UNIQUE,
    description     TEXT,
    start_date      DATE,
    end_date        DATE,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE locations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_name   VARCHAR(200) NOT NULL UNIQUE,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE funding_sources (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_name     VARCHAR(200) NOT NULL,
    donor_name      VARCHAR(200),
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE material_groups (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_number    VARCHAR(50) NOT NULL UNIQUE,
    group_name      VARCHAR(200) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE units_of_measure (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    uom_code        VARCHAR(20) NOT NULL UNIQUE,
    uom_name        VARCHAR(100) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE sourcing_methods (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    method_name     VARCHAR(200) NOT NULL UNIQUE,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE fiscal_periods (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    month           INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    quarter         VARCHAR(5) NOT NULL CHECK (quarter IN ('Q1','Q2','Q3','Q4')),
    fiscal_year     VARCHAR(10) NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    UNIQUE (month, fiscal_year)
);

-- ============================================================================
-- USERS / RBAC
-- ============================================================================

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    full_name       VARCHAR(200) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    last_login      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE roles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name       VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_roles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id),
    role_id         UUID NOT NULL REFERENCES roles(id),
    project_id      UUID REFERENCES projects(id),  -- optional: project-scoped role
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, role_id, project_id)
);

CREATE TABLE permissions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id             UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    resource            VARCHAR(100) NOT NULL,   -- entity name e.g. 'line_item', 'pr'
    action              VARCHAR(50) NOT NULL,     -- 'create','read','update','delete','approve','submit'
    field_restrictions  JSONB DEFAULT '[]'::jsonb, -- array of fields editable, empty = all
    conditions          JSONB DEFAULT '{}'::jsonb, -- e.g. {"status": ["Draft","Returned for Correction"]}
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (role_id, resource, action)
);

-- ============================================================================
-- PROCUREMENT PLAN HEADERS
-- ============================================================================

CREATE TABLE procurement_plan_headers (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tracking_no                 VARCHAR(50) NOT NULL UNIQUE,
    project_id                  UUID NOT NULL REFERENCES projects(id),
    type_of_procurement_plan    VARCHAR(100) NOT NULL,
    department_manager_id       UUID NOT NULL REFERENCES users(id),
    fad_spad_number             VARCHAR(100),
    project_code_cost_centre    VARCHAR(100) NOT NULL,
    funding_source_id           UUID NOT NULL REFERENCES funding_sources(id),
    donor_name                  VARCHAR(200),
    start_date                  DATE NOT NULL,
    end_date                    DATE NOT NULL,
    header_status               VARCHAR(20) NOT NULL DEFAULT 'Draft'
                                CHECK (header_status IN ('Draft','Active','Closed')),
    created_by                  UUID REFERENCES users(id),
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at                  TIMESTAMPTZ
);

CREATE INDEX idx_pph_project ON procurement_plan_headers(project_id);
CREATE INDEX idx_pph_funding ON procurement_plan_headers(funding_source_id);
CREATE INDEX idx_pph_status ON procurement_plan_headers(header_status);
CREATE INDEX idx_pph_manager ON procurement_plan_headers(department_manager_id);
CREATE INDEX idx_pph_donor ON procurement_plan_headers(donor_name);
CREATE INDEX idx_pph_dates ON procurement_plan_headers(start_date, end_date);
CREATE INDEX idx_pph_deleted ON procurement_plan_headers(deleted_at) WHERE deleted_at IS NULL;

-- ============================================================================
-- PROCUREMENT PLAN LINE ITEMS
-- ============================================================================

CREATE TABLE procurement_plan_line_items (
    id                                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    header_id                           UUID NOT NULL REFERENCES procurement_plan_headers(id),
    line_item_ref                       VARCHAR(50) NOT NULL,
    location_id                         UUID NOT NULL REFERENCES locations(id),
    activity_number                     VARCHAR(100),
    material_group_id                   UUID NOT NULL REFERENCES material_groups(id),
    item_description                    TEXT NOT NULL,
    uom_id                              UUID NOT NULL REFERENCES units_of_measure(id),
    quantity                            DECIMAL(15,4) NOT NULL CHECK (quantity > 0),
    currency_code                       VARCHAR(3) NOT NULL DEFAULT 'KES'
                                        CHECK (currency_code IN ('KES','EUR')),
    estimated_unit_price                DECIMAL(18,4) NOT NULL CHECK (estimated_unit_price >= 0),
    estimated_total_item_service_cost   DECIMAL(18,4) GENERATED ALWAYS AS (quantity * estimated_unit_price) STORED,
    estimated_warehousing_cost          DECIMAL(18,4) NOT NULL DEFAULT 0 CHECK (estimated_warehousing_cost >= 0),
    estimated_transport_cost            DECIMAL(18,4) NOT NULL DEFAULT 0 CHECK (estimated_transport_cost >= 0),
    estimated_total_cost                DECIMAL(18,4) GENERATED ALWAYS AS (
                                            quantity * estimated_unit_price + estimated_warehousing_cost + estimated_transport_cost
                                        ) STORED,
    month                               INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    quarter                             VARCHAR(5) NOT NULL CHECK (quarter IN ('Q1','Q2','Q3','Q4')),
    fiscal_year                         VARCHAR(10) NOT NULL,

    -- Lifecycle status
    status                              VARCHAR(30) NOT NULL DEFAULT 'Draft'
                                        CHECK (status IN (
                                            'Draft',
                                            'Submitted for Approval',
                                            'Returned for Correction',
                                            'Approved',
                                            'PR Raised',
                                            'Sourcing',
                                            'Ordered/Contracted',
                                            'Delivery In Progress',
                                            'Delivered/Closed',
                                            'Cancelled'
                                        )),
    status_changed_at                   TIMESTAMPTZ DEFAULT NOW(),

    -- Supply Chain fields
    pr_number                           VARCHAR(50),
    pr_submitted_date                   DATE,
    estimated_delivery_date             DATE,
    is_stock_on_hand_available          BOOLEAN NOT NULL DEFAULT false,
    quantity_available                   DECIMAL(15,4) NOT NULL DEFAULT 0 CHECK (quantity_available >= 0),
    item_type                           VARCHAR(50) CHECK (item_type IN ('Stock','Asset','Service')),
    sourcing_location                   VARCHAR(200),
    sourcing_method_id                  UUID REFERENCES sourcing_methods(id),
    lta_reference_number                VARCHAR(100),
    estimated_delivery_needed           TEXT,
    actual_delivery_date                DATE,
    stock_on_hand_asset_post            TEXT,
    sourcing_plan                       TEXT,

    -- Delivery tracking (internal)
    delivered_quantity                   DECIMAL(15,4) NOT NULL DEFAULT 0 CHECK (delivered_quantity >= 0),

    -- Cancellation
    cancellation_reason                 TEXT,

    -- Metadata
    created_by                          UUID REFERENCES users(id),
    created_at                          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at                          TIMESTAMPTZ,

    UNIQUE (header_id, line_item_ref)
);

-- Performance indexes
CREATE INDEX idx_li_header ON procurement_plan_line_items(header_id);
CREATE INDEX idx_li_status ON procurement_plan_line_items(status);
CREATE INDEX idx_li_ref ON procurement_plan_line_items(line_item_ref);
CREATE INDEX idx_li_location ON procurement_plan_line_items(location_id);
CREATE INDEX idx_li_material ON procurement_plan_line_items(material_group_id);
CREATE INDEX idx_li_pr ON procurement_plan_line_items(pr_number);
CREATE INDEX idx_li_currency ON procurement_plan_line_items(currency_code);
CREATE INDEX idx_li_month_qtr_fy ON procurement_plan_line_items(month, quarter, fiscal_year);
CREATE INDEX idx_li_sourcing ON procurement_plan_line_items(sourcing_method_id);
CREATE INDEX idx_li_delivery_date ON procurement_plan_line_items(estimated_delivery_date);
CREATE INDEX idx_li_deleted ON procurement_plan_line_items(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_li_status_changed ON procurement_plan_line_items(status_changed_at);

-- ============================================================================
-- APPROVAL RULES + STEPS + DECISIONS
-- ============================================================================

CREATE TABLE line_item_approval_rules (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_name                   VARCHAR(200) NOT NULL,
    cost_threshold_min          DECIMAL(18,4),
    cost_threshold_max          DECIMAL(18,4),
    cost_threshold_currency     VARCHAR(3) CHECK (cost_threshold_currency IN ('KES','EUR')),
    item_type                   VARCHAR(50) CHECK (item_type IN ('Stock','Asset','Service')),
    sourcing_method_id          UUID REFERENCES sourcing_methods(id),
    material_group_id           UUID REFERENCES material_groups(id),
    location_id                 UUID REFERENCES locations(id),
    priority                    INTEGER NOT NULL DEFAULT 0,
    is_active                   BOOLEAN NOT NULL DEFAULT true,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ar_active ON line_item_approval_rules(is_active, priority DESC);

CREATE TABLE line_item_approval_steps (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id                 UUID NOT NULL REFERENCES line_item_approval_rules(id) ON DELETE CASCADE,
    step_order              INTEGER NOT NULL,
    approver_role_id        UUID REFERENCES roles(id),
    specific_approver_id    UUID REFERENCES users(id),
    is_parallel             BOOLEAN NOT NULL DEFAULT false,
    can_delegate            BOOLEAN NOT NULL DEFAULT true,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (rule_id, step_order)
);

CREATE TABLE line_item_approvals (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    line_item_id        UUID NOT NULL REFERENCES procurement_plan_line_items(id),
    step_id             UUID NOT NULL REFERENCES line_item_approval_steps(id),
    approver_id         UUID NOT NULL REFERENCES users(id),
    delegated_from_id   UUID REFERENCES users(id),
    decision            VARCHAR(20) NOT NULL
                        CHECK (decision IN ('Approved','Returned','Cancelled','Escalated')),
    comments            TEXT,
    decided_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Append-only: no UPDATE/DELETE triggers enforced at application level
CREATE INDEX idx_lia_line_item ON line_item_approvals(line_item_id);
CREATE INDEX idx_lia_approver ON line_item_approvals(approver_id);
CREATE INDEX idx_lia_decision ON line_item_approvals(decision);
CREATE INDEX idx_lia_decided ON line_item_approvals(decided_at);

-- ============================================================================
-- PURCHASE REQUISITIONS
-- ============================================================================

CREATE TABLE purchase_requisitions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pr_number       VARCHAR(50) NOT NULL UNIQUE,
    submitted_date  DATE NOT NULL,
    submitted_by    UUID NOT NULL REFERENCES users(id),
    status          VARCHAR(30) NOT NULL DEFAULT 'Open'
                    CHECK (status IN ('Open','Sourcing','Ordered','Closed','Cancelled')),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pr_number ON purchase_requisitions(pr_number);
CREATE INDEX idx_pr_status ON purchase_requisitions(status);
CREATE INDEX idx_pr_submitted_by ON purchase_requisitions(submitted_by);

CREATE TABLE pr_line_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pr_id           UUID NOT NULL REFERENCES purchase_requisitions(id) ON DELETE CASCADE,
    line_item_id    UUID NOT NULL REFERENCES procurement_plan_line_items(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (pr_id, line_item_id)
);

CREATE INDEX idx_prli_pr ON pr_line_items(pr_id);
CREATE INDEX idx_prli_li ON pr_line_items(line_item_id);

-- ============================================================================
-- DELIVERIES
-- ============================================================================

CREATE TABLE deliveries (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    line_item_id        UUID NOT NULL REFERENCES procurement_plan_line_items(id),
    pr_id               UUID REFERENCES purchase_requisitions(id),
    delivery_date       DATE NOT NULL,
    quantity_delivered   DECIMAL(15,4) NOT NULL CHECK (quantity_delivered > 0),
    received_by         UUID REFERENCES users(id),
    delivery_note_ref   VARCHAR(200),
    condition_notes     TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_del_line_item ON deliveries(line_item_id);
CREATE INDEX idx_del_pr ON deliveries(pr_id);
CREATE INDEX idx_del_date ON deliveries(delivery_date);

-- ============================================================================
-- STOCK / ASSETS
-- ============================================================================

CREATE TABLE stock_assets (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    line_item_id        UUID REFERENCES procurement_plan_line_items(id),
    item_description    TEXT NOT NULL,
    item_type           VARCHAR(50) NOT NULL CHECK (item_type IN ('Stock','Asset')),
    quantity_on_hand    DECIMAL(15,4) NOT NULL DEFAULT 0,
    location_id         UUID REFERENCES locations(id),
    last_checked_date   DATE,
    last_updated_by     UUID REFERENCES users(id),
    asset_tag           VARCHAR(100),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sa_location ON stock_assets(location_id);
CREATE INDEX idx_sa_type ON stock_assets(item_type);
CREATE INDEX idx_sa_line_item ON stock_assets(line_item_id);

-- ============================================================================
-- EXCHANGE RATES
-- ============================================================================

CREATE TABLE exchange_rates (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_currency   VARCHAR(3) NOT NULL CHECK (from_currency IN ('KES','EUR')),
    to_currency     VARCHAR(3) NOT NULL CHECK (to_currency IN ('KES','EUR')),
    rate            DECIMAL(18,6) NOT NULL CHECK (rate > 0),
    effective_date  DATE NOT NULL,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (from_currency, to_currency, effective_date),
    CHECK (from_currency != to_currency)
);

CREATE INDEX idx_er_lookup ON exchange_rates(from_currency, to_currency, effective_date DESC);

-- ============================================================================
-- ATTACHMENTS
-- ============================================================================

CREATE TABLE attachments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type     VARCHAR(50) NOT NULL CHECK (entity_type IN ('line_item','purchase_requisition','delivery')),
    entity_id       UUID NOT NULL,
    file_name       VARCHAR(500) NOT NULL,
    file_path       VARCHAR(1000) NOT NULL,
    file_size       BIGINT,
    mime_type       VARCHAR(100),
    uploaded_by     UUID NOT NULL REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_att_entity ON attachments(entity_type, entity_id);

-- ============================================================================
-- COMMENTS
-- ============================================================================

CREATE TABLE comments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type     VARCHAR(50) NOT NULL CHECK (entity_type IN ('line_item','purchase_requisition','approval')),
    entity_id       UUID NOT NULL,
    author_id       UUID NOT NULL REFERENCES users(id),
    comment_text    TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cmt_entity ON comments(entity_type, entity_id);
CREATE INDEX idx_cmt_author ON comments(author_id);

-- ============================================================================
-- AUDIT LOG
-- ============================================================================

CREATE TABLE audit_log (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type     VARCHAR(50) NOT NULL,
    entity_id       UUID NOT NULL,
    action          VARCHAR(20) NOT NULL CHECK (action IN ('CREATE','UPDATE','DELETE','STATUS_CHANGE','APPROVAL')),
    field_name      VARCHAR(100),
    old_value       TEXT,
    new_value       TEXT,
    performed_by    UUID NOT NULL REFERENCES users(id),
    performed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_address      VARCHAR(45),
    user_agent      TEXT
);

CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id, performed_at);
CREATE INDEX idx_audit_user ON audit_log(performed_by);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_time ON audit_log(performed_at);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function: Auto-update header_status based on line items
CREATE OR REPLACE FUNCTION fn_update_header_status()
RETURNS TRIGGER AS $$
DECLARE
    v_header_id UUID;
    v_all_draft BOOLEAN;
    v_all_closed BOOLEAN;
    v_new_status VARCHAR(20);
BEGIN
    v_header_id := COALESCE(NEW.header_id, OLD.header_id);

    SELECT
        BOOL_AND(status = 'Draft') AS all_draft,
        BOOL_AND(status IN ('Delivered/Closed', 'Cancelled')) AS all_closed
    INTO v_all_draft, v_all_closed
    FROM procurement_plan_line_items
    WHERE header_id = v_header_id AND deleted_at IS NULL;

    IF v_all_draft THEN
        v_new_status := 'Draft';
    ELSIF v_all_closed THEN
        v_new_status := 'Closed';
    ELSE
        v_new_status := 'Active';
    END IF;

    UPDATE procurement_plan_headers
    SET header_status = v_new_status, updated_at = NOW()
    WHERE id = v_header_id AND header_status != v_new_status;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_line_item_status_change
AFTER INSERT OR UPDATE OF status ON procurement_plan_line_items
FOR EACH ROW
EXECUTE FUNCTION fn_update_header_status();

-- Function: Auto-update delivered_quantity on delivery insert
CREATE OR REPLACE FUNCTION fn_update_delivered_quantity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE procurement_plan_line_items
    SET delivered_quantity = (
        SELECT COALESCE(SUM(quantity_delivered), 0)
        FROM deliveries
        WHERE line_item_id = NEW.line_item_id
    ),
    updated_at = NOW()
    WHERE id = NEW.line_item_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_delivery_quantity_update
AFTER INSERT ON deliveries
FOR EACH ROW
EXECUTE FUNCTION fn_update_delivered_quantity();

-- Function: Auto-set updated_at on any update
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pph_updated_at BEFORE UPDATE ON procurement_plan_headers
FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_li_updated_at BEFORE UPDATE ON procurement_plan_line_items
FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_pr_updated_at BEFORE UPDATE ON purchase_requisitions
FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_sa_updated_at BEFORE UPDATE ON stock_assets
FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

-- Function: Set status_changed_at when status changes
CREATE OR REPLACE FUNCTION fn_set_status_changed_at()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        NEW.status_changed_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_li_status_changed_at BEFORE UPDATE ON procurement_plan_line_items
FOR EACH ROW EXECUTE FUNCTION fn_set_status_changed_at();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Line items with computed days remaining
CREATE OR REPLACE VIEW v_line_items_extended AS
SELECT
    li.*,
    h.tracking_no,
    h.start_date AS plan_start_date,
    h.end_date AS plan_end_date,
    GREATEST(0, h.end_date - CURRENT_DATE) AS days_remaining_until_project_end_date,
    h.project_code_cost_centre,
    h.donor_name AS header_donor_name,
    h.header_status,
    p.project_name,
    p.project_code,
    loc.location_name,
    mg.group_number AS material_group_number,
    mg.group_name AS material_group_name,
    uom.uom_code,
    uom.uom_name,
    sm.method_name AS sourcing_method_name,
    fs.source_name AS funding_source_name,
    fs.donor_name AS funding_donor_name,
    mgr.full_name AS department_manager_name,
    CASE
        WHEN li.estimated_delivery_date IS NOT NULL
             AND li.estimated_delivery_date < CURRENT_DATE
             AND li.status NOT IN ('Delivered/Closed', 'Cancelled')
        THEN true
        ELSE false
    END AS is_overdue,
    CASE
        WHEN li.estimated_delivery_date IS NOT NULL
             AND li.estimated_delivery_date < CURRENT_DATE
             AND li.status NOT IN ('Delivered/Closed', 'Cancelled')
        THEN CURRENT_DATE - li.estimated_delivery_date
        ELSE 0
    END AS days_overdue,
    CASE
        WHEN li.quantity > 0 THEN ROUND((li.delivered_quantity / li.quantity) * 100, 1)
        ELSE 0
    END AS delivery_percentage
FROM procurement_plan_line_items li
JOIN procurement_plan_headers h ON li.header_id = h.id
JOIN projects p ON h.project_id = p.id
JOIN locations loc ON li.location_id = loc.id
JOIN material_groups mg ON li.material_group_id = mg.id
JOIN units_of_measure uom ON li.uom_id = uom.id
JOIN users mgr ON h.department_manager_id = mgr.id
LEFT JOIN sourcing_methods sm ON li.sourcing_method_id = sm.id
LEFT JOIN funding_sources fs ON h.funding_source_id = fs.id
WHERE li.deleted_at IS NULL;

-- View: Plan approval summary
CREATE OR REPLACE VIEW v_plan_approval_summary AS
SELECT
    h.id AS plan_id,
    h.tracking_no,
    p.project_name,
    COUNT(*) AS total_items,
    COUNT(*) FILTER (WHERE li.status = 'Draft') AS draft_count,
    COUNT(*) FILTER (WHERE li.status = 'Submitted for Approval') AS submitted_count,
    COUNT(*) FILTER (WHERE li.status = 'Returned for Correction') AS returned_count,
    COUNT(*) FILTER (WHERE li.status = 'Approved') AS approved_count,
    COUNT(*) FILTER (WHERE li.status = 'PR Raised') AS pr_raised_count,
    COUNT(*) FILTER (WHERE li.status = 'Sourcing') AS sourcing_count,
    COUNT(*) FILTER (WHERE li.status = 'Ordered/Contracted') AS ordered_count,
    COUNT(*) FILTER (WHERE li.status = 'Delivery In Progress') AS delivery_ip_count,
    COUNT(*) FILTER (WHERE li.status = 'Delivered/Closed') AS delivered_count,
    COUNT(*) FILTER (WHERE li.status = 'Cancelled') AS cancelled_count,
    SUM(CASE WHEN li.currency_code = 'KES' THEN li.estimated_total_cost ELSE 0 END) AS total_cost_kes,
    SUM(CASE WHEN li.currency_code = 'EUR' THEN li.estimated_total_cost ELSE 0 END) AS total_cost_eur,
    h.header_status
FROM procurement_plan_headers h
JOIN procurement_plan_line_items li ON li.header_id = h.id
JOIN projects p ON h.project_id = p.id
WHERE li.deleted_at IS NULL AND h.deleted_at IS NULL
GROUP BY h.id, h.tracking_no, p.project_name, h.header_status;

-- View: Approval ageing
CREATE OR REPLACE VIEW v_approval_ageing AS
SELECT
    li.id AS line_item_id,
    li.line_item_ref,
    li.item_description,
    li.estimated_total_cost,
    li.currency_code,
    li.status,
    li.status_changed_at,
    EXTRACT(DAY FROM NOW() - li.status_changed_at)::INTEGER AS days_in_current_status,
    h.tracking_no,
    mgr.full_name AS pending_approver,
    p.project_name,
    loc.location_name
FROM procurement_plan_line_items li
JOIN procurement_plan_headers h ON li.header_id = h.id
JOIN projects p ON h.project_id = p.id
JOIN users mgr ON h.department_manager_id = mgr.id
JOIN locations loc ON li.location_id = loc.id
WHERE li.status IN ('Submitted for Approval', 'Returned for Correction')
  AND li.deleted_at IS NULL
ORDER BY days_in_current_status DESC;

-- View: Overdue deliveries
CREATE OR REPLACE VIEW v_overdue_deliveries AS
SELECT
    li.id AS line_item_id,
    li.line_item_ref,
    li.item_description,
    li.estimated_delivery_date,
    (CURRENT_DATE - li.estimated_delivery_date) AS days_overdue,
    li.quantity,
    li.delivered_quantity,
    CASE WHEN li.quantity > 0 THEN ROUND((li.delivered_quantity / li.quantity) * 100, 1) ELSE 0 END AS delivery_pct,
    li.estimated_total_cost,
    li.currency_code,
    loc.location_name,
    h.tracking_no,
    p.project_name
FROM procurement_plan_line_items li
JOIN procurement_plan_headers h ON li.header_id = h.id
JOIN projects p ON h.project_id = p.id
JOIN locations loc ON li.location_id = loc.id
WHERE li.estimated_delivery_date < CURRENT_DATE
  AND li.status NOT IN ('Delivered/Closed', 'Cancelled')
  AND li.deleted_at IS NULL
ORDER BY days_overdue DESC;
