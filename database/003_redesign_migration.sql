-- ============================================================================
-- COSME Procurement — Redesign Migration (Template FY26)
-- ============================================================================

-- Add new columns to procurement_plan_headers
ALTER TABLE procurement_plan_headers
  ADD COLUMN IF NOT EXISTS global_regional_hub VARCHAR(200),
  ADD COLUMN IF NOT EXISTS country_office VARCHAR(200),
  ADD COLUMN IF NOT EXISTS financial_year VARCHAR(10),
  ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'KES';

-- Create issue_logs table
CREATE TABLE IF NOT EXISTS issue_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  header_id UUID NOT NULL REFERENCES procurement_plan_headers(id),
  line_item_ref VARCHAR(50),
  issue_description TEXT NOT NULL,
  raised_by UUID NOT NULL REFERENCES users(id),
  raised_date DATE NOT NULL DEFAULT CURRENT_DATE,
  priority VARCHAR(20) DEFAULT 'Medium',
  status VARCHAR(30) DEFAULT 'Open',
  assigned_to UUID REFERENCES users(id),
  resolution TEXT,
  resolved_date DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_issue_header ON issue_logs(header_id);
CREATE INDEX IF NOT EXISTS idx_issue_status ON issue_logs(status);
