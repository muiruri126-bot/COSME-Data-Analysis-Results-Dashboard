-- ============================================================================
-- COSME Procurement Tracking System — Seed Data
-- ============================================================================

-- ============================================================================
-- ROLES
-- ============================================================================
INSERT INTO roles (id, role_name, description) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'Project/Department Requester', 'Creates and manages procurement plans and line items'),
    ('a0000000-0000-0000-0000-000000000002', 'Project/Department Manager', 'Approves/returns line items; oversees project procurement'),
    ('a0000000-0000-0000-0000-000000000003', 'Supply Chain Officer', 'Manages PRs, sourcing, and delivery tracking'),
    ('a0000000-0000-0000-0000-000000000004', 'Stores/Inventory Officer', 'Manages delivery receipts and stock/asset tracking'),
    ('a0000000-0000-0000-0000-000000000005', 'Finance/Grants', 'Read-only reporting and compliance checks'),
    ('a0000000-0000-0000-0000-000000000006', 'System Admin', 'Full system access and configuration');

-- ============================================================================
-- PERMISSIONS
-- ============================================================================

-- Project/Department Requester permissions
INSERT INTO permissions (role_id, resource, action, field_restrictions, conditions) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'procurement_plan_header', 'create', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000001', 'procurement_plan_header', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000001', 'procurement_plan_header', 'update', '[]', '{"header_status": ["Draft"]}'),
    ('a0000000-0000-0000-0000-000000000001', 'line_item', 'create', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000001', 'line_item', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000001', 'line_item', 'update', '["item_description","quantity","estimated_unit_price","estimated_warehousing_cost","estimated_transport_cost","location_id","activity_number","material_group_id","uom_id","month","quarter","fiscal_year","item_type","is_stock_on_hand_available","quantity_available"]', '{"status": ["Draft","Returned for Correction"]}'),
    ('a0000000-0000-0000-0000-000000000001', 'line_item', 'submit', '[]', '{"status": ["Draft","Returned for Correction"]}');

-- Project/Department Manager permissions
INSERT INTO permissions (role_id, resource, action, field_restrictions, conditions) VALUES
    ('a0000000-0000-0000-0000-000000000002', 'procurement_plan_header', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000002', 'line_item', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000002', 'line_item', 'approve', '[]', '{"status": ["Submitted for Approval"]}'),
    ('a0000000-0000-0000-0000-000000000002', 'line_item', 'return', '[]', '{"status": ["Submitted for Approval"]}'),
    ('a0000000-0000-0000-0000-000000000002', 'line_item', 'cancel', '[]', '{}');

-- Supply Chain Officer permissions
INSERT INTO permissions (role_id, resource, action, field_restrictions, conditions) VALUES
    ('a0000000-0000-0000-0000-000000000003', 'procurement_plan_header', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000003', 'line_item', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000003', 'line_item', 'update', '["pr_number","pr_submitted_date","estimated_delivery_date","sourcing_location","sourcing_method_id","lta_reference_number","estimated_delivery_needed","sourcing_plan","actual_delivery_date","stock_on_hand_asset_post"]', '{"status": ["Approved","PR Raised","Sourcing","Ordered/Contracted","Delivery In Progress"]}'),
    ('a0000000-0000-0000-0000-000000000003', 'purchase_requisition', 'create', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000003', 'purchase_requisition', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000003', 'purchase_requisition', 'update', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000003', 'delivery', 'create', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000003', 'delivery', 'read', '[]', '{}');

-- Stores/Inventory Officer permissions
INSERT INTO permissions (role_id, resource, action, field_restrictions, conditions) VALUES
    ('a0000000-0000-0000-0000-000000000004', 'line_item', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000004', 'delivery', 'create', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000004', 'delivery', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000004', 'stock_asset', 'create', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000004', 'stock_asset', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000004', 'stock_asset', 'update', '[]', '{}');

-- Finance/Grants permissions (read-only + reporting)
INSERT INTO permissions (role_id, resource, action, field_restrictions, conditions) VALUES
    ('a0000000-0000-0000-0000-000000000005', 'procurement_plan_header', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000005', 'line_item', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000005', 'purchase_requisition', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000005', 'delivery', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000005', 'stock_asset', 'read', '[]', '{}'),
    ('a0000000-0000-0000-0000-000000000005', 'report', 'read', '[]', '{}');

-- System Admin (all resources, all actions)
INSERT INTO permissions (role_id, resource, action, field_restrictions, conditions) VALUES
    ('a0000000-0000-0000-0000-000000000006', '*', '*', '[]', '{}');

-- ============================================================================
-- PROJECTS (COSME components)
-- ============================================================================
INSERT INTO projects (id, project_name, project_code, description, start_date, end_date) VALUES
    ('b0000000-0000-0000-0000-000000000001', 'COSME NBS', 'FECNO', 'COSME Nature-Based Solutions component', '2024-01-01', '2027-12-31'),
    ('b0000000-0000-0000-0000-000000000002', 'COSME Economic Empowerment', 'FECEE', 'COSME Economic Empowerment component', '2024-01-01', '2027-12-31'),
    ('b0000000-0000-0000-0000-000000000003', 'COSME GEI', 'FECGI', 'COSME Gender Equality and Inclusion component', '2024-01-01', '2027-12-31'),
    ('b0000000-0000-0000-0000-000000000004', 'COSME MERL', 'FECML', 'COSME Monitoring, Evaluation, Research and Learning', '2024-01-01', '2027-12-31');

-- ============================================================================
-- LOCATIONS
-- ============================================================================
INSERT INTO locations (id, location_name) VALUES
    ('c0000000-0000-0000-0000-000000000001', 'Kilifi Office'),
    ('c0000000-0000-0000-0000-000000000002', 'Kwale Office');

-- ============================================================================
-- FUNDING SOURCES
-- ============================================================================
INSERT INTO funding_sources (id, source_name, donor_name) VALUES
    ('d0000000-0000-0000-0000-000000000001', 'Grant', 'GAC');

-- ============================================================================
-- MATERIAL GROUPS
-- ============================================================================
INSERT INTO material_groups (id, group_number, group_name) VALUES
    ('e0000000-0000-0000-0000-000000000001', 'MG001', 'Consultancy/Professional Services'),
    ('e0000000-0000-0000-0000-000000000002', 'MG002', 'Travel'),
    ('e0000000-0000-0000-0000-000000000003', 'MG003', 'Accommodation'),
    ('e0000000-0000-0000-0000-000000000004', 'MG004', 'Vehicles'),
    ('e0000000-0000-0000-0000-000000000005', 'MG005', 'Events'),
    ('e0000000-0000-0000-0000-000000000006', 'MG006', 'Equipment'),
    ('e0000000-0000-0000-0000-000000000007', 'MG007', 'Seedlings'),
    ('e0000000-0000-0000-0000-000000000008', 'MG008', 'Printing'),
    ('e0000000-0000-0000-0000-000000000009', 'MG009', 'Catering'),
    ('e0000000-0000-0000-0000-000000000010', 'MG010', 'Office Supplies'),
    ('e0000000-0000-0000-0000-000000000011', 'MG011', 'IT Equipment'),
    ('e0000000-0000-0000-0000-000000000012', 'MG012', 'Construction/Rehabilitation');

-- ============================================================================
-- UNITS OF MEASURE
-- ============================================================================
INSERT INTO units_of_measure (id, uom_code, uom_name) VALUES
    ('f0000000-0000-0000-0000-000000000001', 'EA', 'Each'),
    ('f0000000-0000-0000-0000-000000000002', 'LOT', 'Lot'),
    ('f0000000-0000-0000-0000-000000000003', 'DAY', 'Day'),
    ('f0000000-0000-0000-0000-000000000004', 'TRIP', 'Trip'),
    ('f0000000-0000-0000-0000-000000000005', 'MTH', 'Month'),
    ('f0000000-0000-0000-0000-000000000006', 'KG', 'Kilogram'),
    ('f0000000-0000-0000-0000-000000000007', 'PAX', 'Per Person'),
    ('f0000000-0000-0000-0000-000000000008', 'SET', 'Set'),
    ('f0000000-0000-0000-0000-000000000009', 'HR', 'Hour'),
    ('f0000000-0000-0000-0000-000000000010', 'LS', 'Lump Sum');

-- ============================================================================
-- SOURCING METHODS
-- ============================================================================
INSERT INTO sourcing_methods (id, method_name) VALUES
    ('60000000-0000-0000-0000-000000000001', 'LTA (Long-Term Agreement)'),
    ('60000000-0000-0000-0000-000000000002', 'Competitive Quotation'),
    ('60000000-0000-0000-0000-000000000003', 'Direct Procurement'),
    ('60000000-0000-0000-0000-000000000004', 'Request for Proposal'),
    ('60000000-0000-0000-0000-000000000005', 'Micro-Purchase'),
    ('60000000-0000-0000-0000-000000000006', 'Framework Agreement');

-- ============================================================================
-- SAMPLE USERS (password: 'CosmeDemo2025!' - bcrypt hashed)
-- ============================================================================
-- Password for all users: CosmePass2025!
INSERT INTO users (id, email, full_name, password_hash) VALUES
    ('10000000-0000-0000-0000-000000000001', 'jane.mwangi@cosme.org', 'Jane Mwangi', '$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2'),
    ('10000000-0000-0000-0000-000000000002', 'dr.kamau@cosme.org', 'Dr. Kamau', '$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2'),
    ('10000000-0000-0000-0000-000000000003', 'peter.ochieng@cosme.org', 'Peter Ochieng', '$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2'),
    ('10000000-0000-0000-0000-000000000004', 'mary.wanjiku@cosme.org', 'Mary Wanjiku', '$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2'),
    ('10000000-0000-0000-0000-000000000005', 'aisha.hassan@cosme.org', 'Aisha Hassan', '$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2'),
    ('10000000-0000-0000-0000-000000000006', 'admin@cosme.org', 'System Administrator', '$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2');

-- Assign roles
INSERT INTO user_roles (user_id, role_id, project_id) VALUES
    ('10000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001'), -- Jane = Requester for COSME NBS
    ('10000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000001'), -- Dr. Kamau = Manager for COSME NBS
    ('10000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000003', NULL), -- Peter = Supply Chain (all projects)
    ('10000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000004', NULL), -- Mary = Stores (all projects)
    ('10000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000005', NULL), -- Aisha = Finance (all projects)
    ('10000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000006', NULL); -- Admin

-- ============================================================================
-- SAMPLE EXCHANGE RATES
-- ============================================================================
INSERT INTO exchange_rates (from_currency, to_currency, rate, effective_date, created_by) VALUES
    ('EUR', 'KES', 156.50, '2025-01-01', '10000000-0000-0000-0000-000000000006'),
    ('KES', 'EUR', 0.00639, '2025-01-01', '10000000-0000-0000-0000-000000000006'),
    ('EUR', 'KES', 158.25, '2025-04-01', '10000000-0000-0000-0000-000000000006'),
    ('KES', 'EUR', 0.00632, '2025-04-01', '10000000-0000-0000-0000-000000000006'),
    ('EUR', 'KES', 160.00, '2025-07-01', '10000000-0000-0000-0000-000000000006'),
    ('KES', 'EUR', 0.00625, '2025-07-01', '10000000-0000-0000-0000-000000000006');

-- ============================================================================
-- FISCAL PERIODS (FY2025)
-- ============================================================================
INSERT INTO fiscal_periods (month, quarter, fiscal_year, start_date, end_date) VALUES
    (1,  'Q1', 'FY2025', '2025-01-01', '2025-01-31'),
    (2,  'Q1', 'FY2025', '2025-02-01', '2025-02-28'),
    (3,  'Q1', 'FY2025', '2025-03-01', '2025-03-31'),
    (4,  'Q2', 'FY2025', '2025-04-01', '2025-04-30'),
    (5,  'Q2', 'FY2025', '2025-05-01', '2025-05-31'),
    (6,  'Q2', 'FY2025', '2025-06-01', '2025-06-30'),
    (7,  'Q3', 'FY2025', '2025-07-01', '2025-07-31'),
    (8,  'Q3', 'FY2025', '2025-08-01', '2025-08-31'),
    (9,  'Q3', 'FY2025', '2025-09-01', '2025-09-30'),
    (10, 'Q4', 'FY2025', '2025-10-01', '2025-10-31'),
    (11, 'Q4', 'FY2025', '2025-11-01', '2025-11-30'),
    (12, 'Q4', 'FY2025', '2025-12-01', '2025-12-31');

-- ============================================================================
-- DEFAULT APPROVAL RULES
-- ============================================================================

-- Rule 1: Default — Project Manager must approve all line items
INSERT INTO line_item_approval_rules (id, rule_name, priority, is_active) VALUES
    ('20000000-0000-0000-0000-000000000001', 'Default: Project Manager Approval', 0, true);

INSERT INTO line_item_approval_steps (id, rule_id, step_order, approver_role_id) VALUES
    ('30000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', 1, 'a0000000-0000-0000-0000-000000000002');

-- Rule 2: High-value items (KES > 1,000,000) require Project Manager + Finance review
INSERT INTO line_item_approval_rules (id, rule_name, cost_threshold_min, cost_threshold_currency, priority, is_active) VALUES
    ('20000000-0000-0000-0000-000000000002', 'High Value KES: Manager + Finance', 1000000, 'KES', 10, true);

INSERT INTO line_item_approval_steps (id, rule_id, step_order, approver_role_id) VALUES
    ('30000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000002', 1, 'a0000000-0000-0000-0000-000000000002'),
    ('30000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000002', 2, 'a0000000-0000-0000-0000-000000000005');

-- Rule 3: High-value items (EUR > 10,000) require Project Manager + Finance review
INSERT INTO line_item_approval_rules (id, rule_name, cost_threshold_min, cost_threshold_currency, priority, is_active) VALUES
    ('20000000-0000-0000-0000-000000000003', 'High Value EUR: Manager + Finance', 10000, 'EUR', 10, true);

INSERT INTO line_item_approval_steps (id, rule_id, step_order, approver_role_id) VALUES
    ('30000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000003', 1, 'a0000000-0000-0000-0000-000000000002'),
    ('30000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000003', 2, 'a0000000-0000-0000-0000-000000000005');

-- Rule 4: LTA sourcing — expedited (only Project Manager, no Finance)
INSERT INTO line_item_approval_rules (id, rule_name, sourcing_method_id, priority, is_active) VALUES
    ('20000000-0000-0000-0000-000000000004', 'LTA Sourcing: Project Manager Only', '60000000-0000-0000-0000-000000000001', 5, true);

INSERT INTO line_item_approval_steps (id, rule_id, step_order, approver_role_id) VALUES
    ('30000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000004', 1, 'a0000000-0000-0000-0000-000000000002');

-- ============================================================================
-- SAMPLE PROCUREMENT PLAN + LINE ITEMS
-- ============================================================================

INSERT INTO procurement_plan_headers (
    id, tracking_no, project_id, type_of_procurement_plan,
    department_manager_id, fad_spad_number, project_code_cost_centre,
    funding_source_id, donor_name, start_date, end_date,
    header_status, created_by
) VALUES (
    '40000000-0000-0000-0000-000000000001',
    'PP0374',
    'b0000000-0000-0000-0000-000000000001',
    'Annual Procurement Plan',
    '10000000-0000-0000-0000-000000000002',
    'FAD-2025-001',
    'FECNO',
    'd0000000-0000-0000-0000-000000000001',
    'GAC',
    '2025-01-01',
    '2027-12-31',
    'Active',
    '10000000-0000-0000-0000-000000000001'
);

-- Line Item 1: Consultancy - Approved
INSERT INTO procurement_plan_line_items (
    id, header_id, line_item_ref, location_id, activity_number,
    material_group_id, item_description, uom_id, quantity, currency_code,
    estimated_unit_price, estimated_warehousing_cost, estimated_transport_cost,
    month, quarter, fiscal_year, status, item_type, created_by
) VALUES (
    '11000000-0000-0000-0000-000000000001',
    '40000000-0000-0000-0000-000000000001',
    'PP0374-001',
    'c0000000-0000-0000-0000-000000000001',  -- Kilifi Office
    'ACT-1.1',
    'e0000000-0000-0000-0000-000000000001',  -- Consultancy/Professional Services
    'Lead Consultant – NBS Technical Assessment',
    'f0000000-0000-0000-0000-000000000003',  -- Day
    30,
    'EUR',
    500.0000,
    0.0000,
    200.0000,
    3, 'Q1', 'FY2025',
    'Approved',
    'Service',
    '10000000-0000-0000-0000-000000000001'
);

-- Line Item 2: Equipment - Returned for Correction
INSERT INTO procurement_plan_line_items (
    id, header_id, line_item_ref, location_id, activity_number,
    material_group_id, item_description, uom_id, quantity, currency_code,
    estimated_unit_price, estimated_warehousing_cost, estimated_transport_cost,
    month, quarter, fiscal_year, status, item_type,
    is_stock_on_hand_available, quantity_available, created_by
) VALUES (
    '11000000-0000-0000-0000-000000000002',
    '40000000-0000-0000-0000-000000000001',
    'PP0374-002',
    'c0000000-0000-0000-0000-000000000002',  -- Kwale Office
    'ACT-2.3',
    'e0000000-0000-0000-0000-000000000006',  -- Equipment
    'Solar-powered irrigation kits',
    'f0000000-0000-0000-0000-000000000001',  -- Each
    50,
    'KES',
    45000.0000,
    25000.0000,
    15000.0000,
    6, 'Q2', 'FY2025',
    'Returned for Correction',
    'Stock',
    true,
    10,
    '10000000-0000-0000-0000-000000000001'
);

-- Line Item 3: Travel - Draft
INSERT INTO procurement_plan_line_items (
    id, header_id, line_item_ref, location_id, activity_number,
    material_group_id, item_description, uom_id, quantity, currency_code,
    estimated_unit_price, estimated_warehousing_cost, estimated_transport_cost,
    month, quarter, fiscal_year, status, item_type, created_by
) VALUES (
    '11000000-0000-0000-0000-000000000003',
    '40000000-0000-0000-0000-000000000001',
    'PP0374-003',
    'c0000000-0000-0000-0000-000000000001',  -- Kilifi Office
    'ACT-3.1',
    'e0000000-0000-0000-0000-000000000002',  -- Travel
    'Travel Kilifi–Kwale for field monitoring',
    'f0000000-0000-0000-0000-000000000004',  -- Trip
    12,
    'KES',
    8500.0000,
    0.0000,
    0.0000,
    4, 'Q2', 'FY2025',
    'Draft',
    'Service',
    '10000000-0000-0000-0000-000000000001'
);

-- Line Item 4: Catering - Submitted for Approval
INSERT INTO procurement_plan_line_items (
    id, header_id, line_item_ref, location_id, activity_number,
    material_group_id, item_description, uom_id, quantity, currency_code,
    estimated_unit_price, estimated_warehousing_cost, estimated_transport_cost,
    month, quarter, fiscal_year, status, item_type, created_by
) VALUES (
    '11000000-0000-0000-0000-000000000004',
    '40000000-0000-0000-0000-000000000001',
    'PP0374-004',
    'c0000000-0000-0000-0000-000000000001',  -- Kilifi Office
    'ACT-1.5',
    'e0000000-0000-0000-0000-000000000009',  -- Catering
    'Catering for NBS Training Workshop (40 pax, 3 days)',
    'f0000000-0000-0000-0000-000000000007',  -- Per Person
    120,
    'KES',
    1500.0000,
    0.0000,
    5000.0000,
    5, 'Q2', 'FY2025',
    'Submitted for Approval',
    'Service',
    '10000000-0000-0000-0000-000000000001'
);

-- Line Item 5: Seedlings - Approved
INSERT INTO procurement_plan_line_items (
    id, header_id, line_item_ref, location_id, activity_number,
    material_group_id, item_description, uom_id, quantity, currency_code,
    estimated_unit_price, estimated_warehousing_cost, estimated_transport_cost,
    month, quarter, fiscal_year, status, item_type, created_by
) VALUES (
    '11000000-0000-0000-0000-000000000005',
    '40000000-0000-0000-0000-000000000001',
    'PP0374-005',
    'c0000000-0000-0000-0000-000000000002',  -- Kwale Office
    'ACT-4.2',
    'e0000000-0000-0000-0000-000000000007',  -- Seedlings
    'Mangrove seedlings for restoration',
    'f0000000-0000-0000-0000-000000000001',  -- Each
    5000,
    'KES',
    50.0000,
    10000.0000,
    20000.0000,
    7, 'Q3', 'FY2025',
    'Approved',
    'Stock',
    '10000000-0000-0000-0000-000000000001'
);

-- Line Item 6: Printing - Cancelled
INSERT INTO procurement_plan_line_items (
    id, header_id, line_item_ref, location_id, activity_number,
    material_group_id, item_description, uom_id, quantity, currency_code,
    estimated_unit_price, estimated_warehousing_cost, estimated_transport_cost,
    month, quarter, fiscal_year, status, item_type, cancellation_reason, created_by
) VALUES (
    '11000000-0000-0000-0000-000000000006',
    '40000000-0000-0000-0000-000000000001',
    'PP0374-006',
    'c0000000-0000-0000-0000-000000000001',  -- Kilifi Office
    'ACT-5.1',
    'e0000000-0000-0000-0000-000000000008',  -- Printing
    'Annual report printing (500 copies)',
    'f0000000-0000-0000-0000-000000000001',  -- Each
    500,
    'KES',
    250.0000,
    0.0000,
    3000.0000,
    9, 'Q3', 'FY2025',
    'Cancelled',
    'Service',
    'Replaced by digital report distribution as per donor guidance.',
    '10000000-0000-0000-0000-000000000001'
);

-- ============================================================================
-- SAMPLE APPROVAL HISTORY
-- ============================================================================

-- Approval for PP0374-001 (Approved)
INSERT INTO line_item_approvals (line_item_id, step_id, approver_id, decision, comments) VALUES
    ('11000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 'Approved', 'Approved. Proceed with sourcing.');

-- Return for PP0374-002 (Returned)
INSERT INTO line_item_approvals (line_item_id, step_id, approver_id, decision, comments) VALUES
    ('11000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 'Returned', 'Unit price appears high for irrigation kits. Please obtain updated quotation from supplier.');

-- Approval for PP0374-005 (Approved)
INSERT INTO line_item_approvals (line_item_id, step_id, approver_id, decision, comments) VALUES
    ('11000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 'Approved', 'Approved. Coordinate with Kwale nurseries for supply.');

-- Cancellation for PP0374-006
INSERT INTO line_item_approvals (line_item_id, step_id, approver_id, decision, comments) VALUES
    ('11000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 'Cancelled', 'Replaced by digital report distribution as per donor guidance.');
