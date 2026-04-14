-- ============================================================================
-- COSME Procurement — Full Reseed for Template FY26
-- Run AFTER 003_redesign_migration.sql
-- ============================================================================

-- Clear existing data in correct dependency order
DELETE FROM issue_logs;
DELETE FROM audit_log;
DELETE FROM comments;
DELETE FROM attachments;
DELETE FROM pr_line_items;
DELETE FROM deliveries;
DELETE FROM line_item_approvals;
DELETE FROM line_item_approval_steps;
DELETE FROM line_item_approval_rules;
DELETE FROM procurement_plan_line_items;
DELETE FROM procurement_plan_headers;
DELETE FROM purchase_requisitions;
DELETE FROM stock_assets;
DELETE FROM exchange_rates;
DELETE FROM fiscal_periods;
DELETE FROM user_roles;
DELETE FROM permissions;
DELETE FROM users;
DELETE FROM roles;
DELETE FROM projects;
DELETE FROM locations;
DELETE FROM funding_sources;
DELETE FROM material_groups;
DELETE FROM units_of_measure;
DELETE FROM sourcing_methods;

-- ============================================================================
-- ROLES
-- ============================================================================
INSERT INTO roles (id, role_name, description) VALUES
  ('a0000000-0000-0000-0000-000000000001','Project/Department Requester','Creates and manages procurement plans and line items'),
  ('a0000000-0000-0000-0000-000000000002','Project/Department Manager','Approves/returns line items; oversees project procurement'),
  ('a0000000-0000-0000-0000-000000000003','Supply Chain Officer','Manages PRs, sourcing, and delivery tracking'),
  ('a0000000-0000-0000-0000-000000000004','Stores/Inventory Officer','Manages delivery receipts and stock/asset tracking'),
  ('a0000000-0000-0000-0000-000000000005','Finance/Grants','Read-only reporting and compliance checks'),
  ('a0000000-0000-0000-0000-000000000006','System Admin','Full system access and configuration');

-- ============================================================================
-- PERMISSIONS (same as before)
-- ============================================================================
INSERT INTO permissions (role_id,resource,action,field_restrictions,conditions) VALUES
  ('a0000000-0000-0000-0000-000000000001','procurement_plan_header','create','[]','{}'),
  ('a0000000-0000-0000-0000-000000000001','procurement_plan_header','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000001','procurement_plan_header','update','[]','{"header_status":["Draft"]}'),
  ('a0000000-0000-0000-0000-000000000001','line_item','create','[]','{}'),
  ('a0000000-0000-0000-0000-000000000001','line_item','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000001','line_item','update','["item_description","quantity","estimated_unit_price","estimated_warehousing_cost","estimated_transport_cost","location_id","activity_number","material_group_id","uom_id","month","quarter","fiscal_year","item_type","is_stock_on_hand_available","quantity_available"]','{"status":["Draft","Returned for Correction"]}'),
  ('a0000000-0000-0000-0000-000000000001','line_item','submit','[]','{"status":["Draft","Returned for Correction"]}'),
  ('a0000000-0000-0000-0000-000000000002','procurement_plan_header','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000002','line_item','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000002','line_item','approve','[]','{"status":["Submitted for Approval"]}'),
  ('a0000000-0000-0000-0000-000000000002','line_item','return','[]','{"status":["Submitted for Approval"]}'),
  ('a0000000-0000-0000-0000-000000000002','line_item','cancel','[]','{}'),
  ('a0000000-0000-0000-0000-000000000003','procurement_plan_header','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000003','line_item','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000003','line_item','update','["pr_number","pr_submitted_date","estimated_delivery_date","sourcing_location","sourcing_method_id","lta_reference_number","estimated_delivery_needed","sourcing_plan","actual_delivery_date","stock_on_hand_asset_post"]','{"status":["Approved","PR Raised","Sourcing","Ordered/Contracted","Delivery In Progress"]}'),
  ('a0000000-0000-0000-0000-000000000003','purchase_requisition','create','[]','{}'),
  ('a0000000-0000-0000-0000-000000000003','purchase_requisition','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000003','purchase_requisition','update','[]','{}'),
  ('a0000000-0000-0000-0000-000000000003','delivery','create','[]','{}'),
  ('a0000000-0000-0000-0000-000000000003','delivery','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000004','line_item','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000004','delivery','create','[]','{}'),
  ('a0000000-0000-0000-0000-000000000004','delivery','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000004','stock_asset','create','[]','{}'),
  ('a0000000-0000-0000-0000-000000000004','stock_asset','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000004','stock_asset','update','[]','{}'),
  ('a0000000-0000-0000-0000-000000000005','procurement_plan_header','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000005','line_item','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000005','purchase_requisition','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000005','delivery','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000005','stock_asset','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000005','report','read','[]','{}'),
  ('a0000000-0000-0000-0000-000000000006','*','*','[]','{}');

-- ============================================================================
-- PROJECTS (from template) — includes PII Office Data enrichment fields
-- ============================================================================
INSERT INTO projects (id,project_name,project_code,description,start_date,end_date,global_regional_hub,country_office,fad_spad_number,funding_source_id,donor_name) VALUES
  ('b0000000-0000-0000-0000-000000000001','COSME NBS','FECNO','COSME Nature-Based Solutions','2024-01-01','2027-12-31','MEESA Regional Hub','Kenya','100374','d0000000-0000-0000-0000-000000000001','GAC'),
  ('b0000000-0000-0000-0000-000000000002','COSME Economic Empowerment','FECEE','COSME Economic Empowerment','2024-01-01','2027-12-31','MEESA Regional Hub','Kenya','100375','d0000000-0000-0000-0000-000000000001','GAC'),
  ('b0000000-0000-0000-0000-000000000003','COSME GEI','FECGI','COSME Gender Equality and Inclusion','2024-01-01','2027-12-31','MEESA Regional Hub','Kenya','100376','d0000000-0000-0000-0000-000000000001','GAC'),
  ('b0000000-0000-0000-0000-000000000004','COSME MERL','FECML','COSME Monitoring, Evaluation, Research and Learning','2024-01-01','2027-12-31','MEESA Regional Hub','Kenya','100377','d0000000-0000-0000-0000-000000000001','GAC');

-- ============================================================================
-- LOCATIONS (from template)
-- ============================================================================
INSERT INTO locations (id,location_name) VALUES
  ('c0000000-0000-0000-0000-000000000001','Kilifi Office'),
  ('c0000000-0000-0000-0000-000000000002','Kwale Office');

-- ============================================================================
-- FUNDING SOURCES
-- ============================================================================
INSERT INTO funding_sources (id,source_name,donor_name) VALUES
  ('d0000000-0000-0000-0000-000000000001','Grant','GAC'),
  ('d0000000-0000-0000-0000-000000000002','Sponsorship',NULL);

-- ============================================================================
-- UNITS OF MEASURE
-- ============================================================================
INSERT INTO units_of_measure (id,uom_code,uom_name) VALUES
  ('f0000000-0000-0000-0000-000000000001','EA','Each'),
  ('f0000000-0000-0000-0000-000000000002','LOT','Lot'),
  ('f0000000-0000-0000-0000-000000000003','DAY','Day'),
  ('f0000000-0000-0000-0000-000000000004','TRIP','Trip'),
  ('f0000000-0000-0000-0000-000000000005','MTH','Month'),
  ('f0000000-0000-0000-0000-000000000006','KG','Kilogram'),
  ('f0000000-0000-0000-0000-000000000007','PAX','Per Person'),
  ('f0000000-0000-0000-0000-000000000008','SET','Set'),
  ('f0000000-0000-0000-0000-000000000009','HR','Hour'),
  ('f0000000-0000-0000-0000-000000000010','LS','Lump Sum');

-- ============================================================================
-- SOURCING METHODS (from template instructions)
-- ============================================================================
INSERT INTO sourcing_methods (id,method_name) VALUES
  ('60000000-0000-0000-0000-000000000001','N/A'),
  ('60000000-0000-0000-0000-000000000002','Purchase Order'),
  ('60000000-0000-0000-0000-000000000003','LTA'),
  ('60000000-0000-0000-0000-000000000004','Competitive Quotations'),
  ('60000000-0000-0000-0000-000000000005','RFQ'),
  ('60000000-0000-0000-0000-000000000006','ITB'),
  ('60000000-0000-0000-0000-000000000007','RFP');

-- ============================================================================
-- MATERIAL GROUPS (all 130 from template "Procurement Category SC" sheet)
-- ============================================================================

-- FA — Fixed Assets (01xxx)
INSERT INTO material_groups (id,group_number,group_name) VALUES
  ('e0010000-0000-0000-0000-000000000001','01001','FA - Computer Hardware (Capital)'),
  ('e0010000-0000-0000-0000-000000000002','01002','FA - Equipment Cost (Capital)'),
  ('e0010000-0000-0000-0000-000000000003','01003','FA - Freehold Buildings'),
  ('e0010000-0000-0000-0000-000000000004','01004','FA - Freehold Land'),
  ('e0010000-0000-0000-0000-000000000005','01005','FA - Furniture and Fittings (Capital)'),
  ('e0010000-0000-0000-0000-000000000006','01006','FA - Intangible Asset Under Construction'),
  ('e0010000-0000-0000-0000-000000000007','01007','FA - Internally Generated Software (Capital)'),
  ('e0010000-0000-0000-0000-000000000008','01008','FA - Investment in Subsidiaries'),
  ('e0010000-0000-0000-0000-000000000009','01009','FA - Leasehold Building Improvements'),
  ('e0010000-0000-0000-0000-000000000010','01010','FA - Motor Vehicles (Capital)'),
  ('e0010000-0000-0000-0000-000000000011','01011','FA - Purchased Software & Licences (Capital)'),
  ('e0010000-0000-0000-0000-000000000012','01012','FA - Tangible Asset Under Construction (Capital)');

-- AE — Assets & Equipment (02xxx)
INSERT INTO material_groups (id,group_number,group_name) VALUES
  ('e0020000-0000-0000-0000-000000000001','02001','AE - Agricultural Machinery and Equipment'),
  ('e0020000-0000-0000-0000-000000000002','02002','AE - Appliances'),
  ('e0020000-0000-0000-0000-000000000003','02003','AE - Audio Equipment'),
  ('e0020000-0000-0000-0000-000000000004','02004','AE - Batteries'),
  ('e0020000-0000-0000-0000-000000000005','02005','AE - Building and Construction Machinery and Equipment'),
  ('e0020000-0000-0000-0000-000000000006','02006','AE - Communication Devices'),
  ('e0020000-0000-0000-0000-000000000007','02007','AE - Computer Accessories'),
  ('e0020000-0000-0000-0000-000000000008','02008','AE - Computers'),
  ('e0020000-0000-0000-0000-000000000009','02009','AE - Conferencing Equipment'),
  ('e0020000-0000-0000-0000-000000000010','02010','AE - Energy Machinery and Equipment'),
  ('e0020000-0000-0000-0000-000000000011','02011','AE - Fixtures and Fittings'),
  ('e0020000-0000-0000-0000-000000000012','02012','AE - Generators'),
  ('e0020000-0000-0000-0000-000000000013','02013','AE - Home Furniture'),
  ('e0020000-0000-0000-0000-000000000014','02014','AE - Medical Equipment'),
  ('e0020000-0000-0000-0000-000000000015','02015','AE - Motorbikes'),
  ('e0020000-0000-0000-0000-000000000016','02016','AE - Networks and Telecommunications Equipment'),
  ('e0020000-0000-0000-0000-000000000017','02017','AE - Office Furniture'),
  ('e0020000-0000-0000-0000-000000000018','02018','AE - Photography, Filming and Video Equipment'),
  ('e0020000-0000-0000-0000-000000000019','02019','AE - Printers, Scanners and Copiers'),
  ('e0020000-0000-0000-0000-000000000020','02020','AE - Printing and Publishing Equipment'),
  ('e0020000-0000-0000-0000-000000000021','02021','AE - Radio Equipment'),
  ('e0020000-0000-0000-0000-000000000022','02022','AE - Safety and Security Equipment'),
  ('e0020000-0000-0000-0000-000000000023','02023','AE - Satellite Equipment (Fixed and Mobile)'),
  ('e0020000-0000-0000-0000-000000000024','02024','AE - Servers'),
  ('e0020000-0000-0000-0000-000000000025','02025','AE - Sport Equipment'),
  ('e0020000-0000-0000-0000-000000000026','02026','AE - Vehicles'),
  ('e0020000-0000-0000-0000-000000000027','02027','AE - Vehicle/Motorbike Tracking Device'),
  ('e0020000-0000-0000-0000-000000000028','02028','AE - Veterinary Medical Equipment'),
  ('e0020000-0000-0000-0000-000000000029','02029','AE - Visual Equipment'),
  ('e0020000-0000-0000-0000-000000000030','02030','AE - Warehousing Handling and Distribution Equipment');

-- SR — Services (03xxx)
INSERT INTO material_groups (id,group_number,group_name) VALUES
  ('e0030000-0000-0000-0000-000000000001','03001','SR - Accountancy Services'),
  ('e0030000-0000-0000-0000-000000000002','03002','SR - Administrative Services'),
  ('e0030000-0000-0000-0000-000000000003','03003','SR - Advertising Services'),
  ('e0030000-0000-0000-0000-000000000004','03004','SR - Agriculture Services'),
  ('e0030000-0000-0000-0000-000000000005','03005','SR - Air Travel'),
  ('e0030000-0000-0000-0000-000000000006','03006','SR - Audit Services'),
  ('e0030000-0000-0000-0000-000000000007','03007','SR - Banking Services'),
  ('e0030000-0000-0000-0000-000000000008','03008','SR - Cleaning Service'),
  ('e0030000-0000-0000-0000-000000000009','03009','SR - Construction Machinery Repair and Maintenance'),
  ('e0030000-0000-0000-0000-000000000010','03010','SR - Construction Service'),
  ('e0030000-0000-0000-0000-000000000011','03011','SR - Construction Workers'),
  ('e0030000-0000-0000-0000-000000000012','03012','SR - Consultancy/Professional Services'),
  ('e0030000-0000-0000-0000-000000000013','03013','SR - Cooking or Catering Service'),
  ('e0030000-0000-0000-0000-000000000014','03014','SR - Courier'),
  ('e0030000-0000-0000-0000-000000000015','03015','SR - CVA Services'),
  ('e0030000-0000-0000-0000-000000000016','03016','SR - Equipment Rental/Lease'),
  ('e0030000-0000-0000-0000-000000000017','03017','SR - Equipment Repair and Maintenance'),
  ('e0030000-0000-0000-0000-000000000018','03018','SR - Events, Conferences and Meetings'),
  ('e0030000-0000-0000-0000-000000000019','03019','SR - Facilities Repair and Maintenance'),
  ('e0030000-0000-0000-0000-000000000020','03020','SR - Freight'),
  ('e0030000-0000-0000-0000-000000000021','03021','SR - Generator Repair and Maintenance'),
  ('e0030000-0000-0000-0000-000000000022','03022','SR - Ground Transportation'),
  ('e0030000-0000-0000-0000-000000000023','03023','SR - HR Services'),
  ('e0030000-0000-0000-0000-000000000024','03024','SR - Insurance'),
  ('e0030000-0000-0000-0000-000000000025','03025','SR - IT Equipment Rental/Lease'),
  ('e0030000-0000-0000-0000-000000000026','03026','SR - IT Equipment Repair and Maintenance'),
  ('e0030000-0000-0000-0000-000000000027','03027','SR - IT Support Services'),
  ('e0030000-0000-0000-0000-000000000028','03028','SR - Legal Services'),
  ('e0030000-0000-0000-0000-000000000029','03029','SR - Logistics Services'),
  ('e0030000-0000-0000-0000-000000000030','03030','SR - Media and Marketing Services'),
  ('e0030000-0000-0000-0000-000000000031','03031','SR - Medical Services'),
  ('e0030000-0000-0000-0000-000000000032','03032','SR - Membership and Subscriptions'),
  ('e0030000-0000-0000-0000-000000000033','03033','SR - Motorbike Repair and Maintenance'),
  ('e0030000-0000-0000-0000-000000000034','03034','SR - Networks and Telecommunications'),
  ('e0030000-0000-0000-0000-000000000035','03035','SR - Office Equipment and Furniture Repair and Maintenance'),
  ('e0030000-0000-0000-0000-000000000036','03036','SR - Photography, Filming and Videography Services'),
  ('e0030000-0000-0000-0000-000000000037','03037','SR - Printing and Publishing Services'),
  ('e0030000-0000-0000-0000-000000000038','03038','SR - Property Rental/Lease'),
  ('e0030000-0000-0000-0000-000000000039','03039','SR - Safety and Security Services'),
  ('e0030000-0000-0000-0000-000000000040','03040','SR - Software or Application Development Service'),
  ('e0030000-0000-0000-0000-000000000041','03041','SR - Software or Application Licenses'),
  ('e0030000-0000-0000-0000-000000000042','03042','SR - Tax and Advisory Services'),
  ('e0030000-0000-0000-0000-000000000043','03043','SR - Training Services'),
  ('e0030000-0000-0000-0000-000000000044','03044','SR - Translation Services'),
  ('e0030000-0000-0000-0000-000000000045','03045','SR - Travel Management Services'),
  ('e0030000-0000-0000-0000-000000000046','03046','SR - Utilities'),
  ('e0030000-0000-0000-0000-000000000047','03047','SR - Vehicle Rental/Lease'),
  ('e0030000-0000-0000-0000-000000000048','03048','SR - Vehicle Repair and Maintenance'),
  ('e0030000-0000-0000-0000-000000000049','03049','SR - Vehicle Tracking Services'),
  ('e0030000-0000-0000-0000-000000000050','03050','SR - Veterinary Services'),
  ('e0030000-0000-0000-0000-000000000051','03051','SR - Virtual Conferencing/Telepresence'),
  ('e0030000-0000-0000-0000-000000000052','03052','SR - Warehouse Rental/Lease'),
  ('e0030000-0000-0000-0000-000000000053','03053','SR - Warehouse Repair and Maintenance'),
  ('e0030000-0000-0000-0000-000000000054','03054','SR - Accommodation');

-- BM — Biological Materials (04xxx)
INSERT INTO material_groups (id,group_number,group_name) VALUES
  ('e0040000-0000-0000-0000-000000000001','04001','BM - Fuels, Lubricant and Fluids'),
  ('e0040000-0000-0000-0000-000000000002','04002','BM - Medical Consumables'),
  ('e0040000-0000-0000-0000-000000000003','04003','BM - Water, Hygiene and Sanitation Materials'),
  ('e0040000-0000-0000-0000-000000000004','04004','BM - Food and Beverages'),
  ('e0040000-0000-0000-0000-000000000005','04005','BM - Agricultural Pesticides, Herbicides and Fertilisers'),
  ('e0040000-0000-0000-0000-000000000006','04006','BM - Seeds, Cuttings and Seedlings'),
  ('e0040000-0000-0000-0000-000000000007','04007','BM - Specialised Nutrition Food'),
  ('e0040000-0000-0000-0000-000000000008','04008','BM - Pharmaceutical'),
  ('e0040000-0000-0000-0000-000000000009','04009','BM - Hygiene and Cleaning Supplies'),
  ('e0040000-0000-0000-0000-000000000010','04010','BM - Veterinary Medical Supplies');

-- NM — Non-Material (05xxx)
INSERT INTO material_groups (id,group_number,group_name) VALUES
  ('e0050000-0000-0000-0000-000000000001','05001','NM - Education and Child Protection Materials'),
  ('e0050000-0000-0000-0000-000000000002','05002','NM - Animal Feed'),
  ('e0050000-0000-0000-0000-000000000003','05003','NM - Animal shelters, Containment and Habitats'),
  ('e0050000-0000-0000-0000-000000000004','05004','NM - Clothing, Footwear, Luggage and Bags'),
  ('e0050000-0000-0000-0000-000000000005','05005','NM - Construction Materials'),
  ('e0050000-0000-0000-0000-000000000006','05006','NM - CVA Materials'),
  ('e0050000-0000-0000-0000-000000000007','05007','NM - Household Supplies and Accessories'),
  ('e0050000-0000-0000-0000-000000000008','05008','NM - Livestock, Poultry and Fisheries (Live Animals)'),
  ('e0050000-0000-0000-0000-000000000009','05009','NM - Media and Marketing Materials'),
  ('e0050000-0000-0000-0000-000000000010','05010','NM - Medical Devices'),
  ('e0050000-0000-0000-0000-000000000011','05011','NM - Medical Laboratory and Diagnostics Materials'),
  ('e0050000-0000-0000-0000-000000000012','05012','NM - Network Accessories'),
  ('e0050000-0000-0000-0000-000000000013','05013','NM - Office Supplies'),
  ('e0050000-0000-0000-0000-000000000014','05014','NM - Published Materials'),
  ('e0050000-0000-0000-0000-000000000015','05015','NM - Shelter'),
  ('e0050000-0000-0000-0000-000000000016','05016','NM - Spare Parts and Accessories'),
  ('e0050000-0000-0000-0000-000000000017','05017','NM - Sport Accessories'),
  ('e0050000-0000-0000-0000-000000000018','05018','NM - Tools, Hardware and Fixings');

-- ============================================================================
-- USERS — from template (password: CosmePass2025!)
-- ============================================================================
INSERT INTO users (id,email,full_name,password_hash) VALUES
  ('10000000-0000-0000-0000-000000000001','caroline.kurgat@cosme.org','Caroline Kurgat','$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2'),
  ('10000000-0000-0000-0000-000000000002','benard.muiruri@cosme.org','Benard Muiruri','$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2'),
  ('10000000-0000-0000-0000-000000000003','dennis.mwanzia@cosme.org','Dennis Mwanzia','$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2'),
  ('10000000-0000-0000-0000-000000000004','jenard.mwangangi@cosme.org','Jenard Mwangangi','$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2'),
  ('10000000-0000-0000-0000-000000000005','peter.ochieng@cosme.org','Peter Ochieng','$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2'),
  ('10000000-0000-0000-0000-000000000006','admin@cosme.org','System Administrator','$2a$10$PaqHFyPh872Heb8pr1vITOyi92TIW8m/GhhpsBCJeqz5YJSDLIpo2');

-- Assign roles
INSERT INTO user_roles (user_id,role_id,project_id) VALUES
  ('10000000-0000-0000-0000-000000000001','a0000000-0000-0000-0000-000000000002','b0000000-0000-0000-0000-000000000001'), -- Caroline = Manager for COSME NBS
  ('10000000-0000-0000-0000-000000000002','a0000000-0000-0000-0000-000000000001','b0000000-0000-0000-0000-000000000001'), -- Benard = Requester for COSME NBS
  ('10000000-0000-0000-0000-000000000003','a0000000-0000-0000-0000-000000000001','b0000000-0000-0000-0000-000000000003'), -- Dennis = Requester for COSME GEI
  ('10000000-0000-0000-0000-000000000004','a0000000-0000-0000-0000-000000000002','b0000000-0000-0000-0000-000000000004'), -- Jenard = Manager for COSME MERL
  ('10000000-0000-0000-0000-000000000005','a0000000-0000-0000-0000-000000000003',NULL),  -- Lilian = Supply Chain (all projects)
  ('10000000-0000-0000-0000-000000000006','a0000000-0000-0000-0000-000000000006',NULL);  -- Admin

-- ============================================================================
-- EXCHANGE RATES
-- ============================================================================
INSERT INTO exchange_rates (from_currency,to_currency,rate,effective_date,created_by) VALUES
  ('EUR','KES',156.50,'2025-01-01','10000000-0000-0000-0000-000000000006'),
  ('KES','EUR',0.00639,'2025-01-01','10000000-0000-0000-0000-000000000006'),
  ('EUR','KES',158.25,'2025-04-01','10000000-0000-0000-0000-000000000006'),
  ('KES','EUR',0.00632,'2025-04-01','10000000-0000-0000-0000-000000000006'),
  ('EUR','KES',160.00,'2025-07-01','10000000-0000-0000-0000-000000000006'),
  ('KES','EUR',0.00625,'2025-07-01','10000000-0000-0000-0000-000000000006');

-- ============================================================================
-- FISCAL PERIODS
-- ============================================================================
INSERT INTO fiscal_periods (month,quarter,fiscal_year,start_date,end_date) VALUES
  (1, 'Q1','FY26','2025-07-01','2025-07-31'),
  (2, 'Q1','FY26','2025-08-01','2025-08-31'),
  (3, 'Q1','FY26','2025-09-01','2025-09-30'),
  (4, 'Q2','FY26','2025-10-01','2025-10-31'),
  (5, 'Q2','FY26','2025-11-01','2025-11-30'),
  (6, 'Q2','FY26','2025-12-01','2025-12-31'),
  (7, 'Q3','FY26','2026-01-01','2026-01-31'),
  (8, 'Q3','FY26','2026-02-01','2026-02-28'),
  (9, 'Q3','FY26','2026-03-01','2026-03-31'),
  (10,'Q4','FY26','2026-04-01','2026-04-30'),
  (11,'Q4','FY26','2026-05-01','2026-05-31'),
  (12,'Q4','FY26','2026-06-01','2026-06-30');

-- ============================================================================
-- APPROVAL RULES
-- ============================================================================
INSERT INTO line_item_approval_rules (id,rule_name,priority,is_active) VALUES
  ('20000000-0000-0000-0000-000000000001','Default: Project Manager Approval',0,true);
INSERT INTO line_item_approval_steps (id,rule_id,step_order,approver_role_id) VALUES
  ('30000000-0000-0000-0000-000000000001','20000000-0000-0000-0000-000000000001',1,'a0000000-0000-0000-0000-000000000002');

INSERT INTO line_item_approval_rules (id,rule_name,cost_threshold_min,cost_threshold_currency,priority,is_active) VALUES
  ('20000000-0000-0000-0000-000000000002','High Value KES: Manager + Finance',1000000,'KES',10,true);
INSERT INTO line_item_approval_steps (id,rule_id,step_order,approver_role_id) VALUES
  ('30000000-0000-0000-0000-000000000002','20000000-0000-0000-0000-000000000002',1,'a0000000-0000-0000-0000-000000000002'),
  ('30000000-0000-0000-0000-000000000003','20000000-0000-0000-0000-000000000002',2,'a0000000-0000-0000-0000-000000000005');

-- ============================================================================
-- SAMPLE PROCUREMENT PLAN (COSME NBS FY26) — mirrors template data
-- ============================================================================
INSERT INTO procurement_plan_headers (
  id,tracking_no,global_regional_hub,country_office,project_id,
  type_of_procurement_plan,department_manager_id,fad_spad_number,
  project_code_cost_centre,funding_source_id,donor_name,
  financial_year,currency,start_date,end_date,header_status,created_by
) VALUES (
  '40000000-0000-0000-0000-000000000001','PP0374',
  'MEESA Regional Hub','Kenya',
  'b0000000-0000-0000-0000-000000000001',
  'Project','10000000-0000-0000-0000-000000000001','100374',
  'FECNO','d0000000-0000-0000-0000-000000000001','GAC',
  'FY26','KES','2025-07-01','2027-12-31','Active',
  '10000000-0000-0000-0000-000000000002'
);

-- Sample line items from the template
INSERT INTO procurement_plan_line_items (
  id,header_id,line_item_ref,location_id,activity_number,
  material_group_id,item_description,uom_id,quantity,currency_code,
  estimated_unit_price,estimated_warehousing_cost,estimated_transport_cost,
  month,quarter,fiscal_year,status,item_type,created_by
) VALUES
  ('50000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000001',
   'PP0374-001','c0000000-0000-0000-0000-000000000001','1.1.1.3',
   'e0030000-0000-0000-0000-000000000012','Consultancy services for market analysis for 3 main value chains','f0000000-0000-0000-0000-000000000001',
   1,'KES',1500000,0,0,8,'Q3','FY26','Draft','Service','10000000-0000-0000-0000-000000000002'),

  ('50000000-0000-0000-0000-000000000002','40000000-0000-0000-0000-000000000001',
   'PP0374-002','c0000000-0000-0000-0000-000000000001','1.1.1.3',
   'e0030000-0000-0000-0000-000000000054','Accommodation for consultant market analysis','f0000000-0000-0000-0000-000000000001',
   5,'KES',8000,0,0,8,'Q3','FY26','Draft','Service','10000000-0000-0000-0000-000000000002'),

  ('50000000-0000-0000-0000-000000000003','40000000-0000-0000-0000-000000000001',
   'PP0374-003','c0000000-0000-0000-0000-000000000001','1.1.1.3',
   'e0030000-0000-0000-0000-000000000022','Vehicle hire for market analysis transport','f0000000-0000-0000-0000-000000000001',
   5,'KES',15000,0,0,8,'Q3','FY26','Draft','Service','10000000-0000-0000-0000-000000000002'),

  ('50000000-0000-0000-0000-000000000004','40000000-0000-0000-0000-000000000001',
   'PP0374-004','c0000000-0000-0000-0000-000000000001','1.1.2.1',
   'e0030000-0000-0000-0000-000000000018','Conference for 200 CBT for 2 days - NBS awareness','f0000000-0000-0000-0000-000000000001',
   1,'KES',800000,0,0,8,'Q3','FY26','Draft','Service','10000000-0000-0000-0000-000000000002'),

  ('50000000-0000-0000-0000-000000000005','40000000-0000-0000-0000-000000000001',
   'PP0374-005','c0000000-0000-0000-0000-000000000001','1.1.2.1',
   'e0030000-0000-0000-0000-000000000022','Vehicle hire for staff transportation to CBT sessions','f0000000-0000-0000-0000-000000000001',
   4,'KES',15000,0,0,8,'Q3','FY26','Draft','Service','10000000-0000-0000-0000-000000000002'),

  ('50000000-0000-0000-0000-000000000006','40000000-0000-0000-0000-000000000001',
   'PP0374-006','c0000000-0000-0000-0000-000000000001','1.1.2.1',
   'e0030000-0000-0000-0000-000000000054','Accommodation for 3 staff for 2 days','f0000000-0000-0000-0000-000000000001',
   6,'KES',8000,0,0,8,'Q3','FY26','Draft','Service','10000000-0000-0000-0000-000000000002'),

  ('50000000-0000-0000-0000-000000000007','40000000-0000-0000-0000-000000000001',
   'PP0374-007','c0000000-0000-0000-0000-000000000001','1.2.1.1',
   'e0040000-0000-0000-0000-000000000006','Procurement of Seeds for crop production','f0000000-0000-0000-0000-000000000001',
   363,'KES',5000,0,0,9,'Q3','FY26','Draft','Stock','10000000-0000-0000-0000-000000000002'),

  ('50000000-0000-0000-0000-000000000008','40000000-0000-0000-0000-000000000001',
   'PP0374-008','c0000000-0000-0000-0000-000000000001','2.1.1.1',
   'e0020000-0000-0000-0000-000000000010','Purchase of solar lighting kits - 363 households','f0000000-0000-0000-0000-000000000001',
   363,'KES',8500,0,20000,10,'Q4','FY26','Draft','Asset','10000000-0000-0000-0000-000000000002'),

  ('50000000-0000-0000-0000-000000000009','40000000-0000-0000-0000-000000000001',
   'PP0374-009','c0000000-0000-0000-0000-000000000002','3.1.1.1',
   'e0030000-0000-0000-0000-000000000037','Design and printing of Certificates','f0000000-0000-0000-0000-000000000001',
   500,'KES',200,0,0,7,'Q3','FY26','Draft','Service','10000000-0000-0000-0000-000000000002'),

  ('50000000-0000-0000-0000-000000000010','40000000-0000-0000-0000-000000000001',
   'PP0374-010','c0000000-0000-0000-0000-000000000001','3.2.1.1',
   'e0020000-0000-0000-0000-000000000001','Purchase of water tanks','f0000000-0000-0000-0000-000000000001',
   10,'KES',25000,0,15000,11,'Q4','FY26','Draft','Asset','10000000-0000-0000-0000-000000000002');

-- ============================================================================
-- AUTO-POPULATE: Material Group → Default Sourcing Method mappings
-- (Mirrors Excel "Procurement Category SC" VLOOKUP column 2)
-- ============================================================================
UPDATE material_groups SET default_sourcing_method_id = '60000000-0000-0000-0000-000000000006' WHERE group_number LIKE '01%';  -- FA → ITB
UPDATE material_groups SET default_sourcing_method_id = '60000000-0000-0000-0000-000000000004' WHERE group_number LIKE '02%';  -- AE → Competitive Quotations
UPDATE material_groups SET default_sourcing_method_id = '60000000-0000-0000-0000-000000000002' WHERE group_number LIKE '03%';  -- CP → Purchase Order
UPDATE material_groups SET default_sourcing_method_id = '60000000-0000-0000-0000-000000000003' WHERE group_number LIKE '04%';  -- BM → LTA
UPDATE material_groups SET default_sourcing_method_id = '60000000-0000-0000-0000-000000000005' WHERE group_number LIKE '05%';  -- NM → RFQ
