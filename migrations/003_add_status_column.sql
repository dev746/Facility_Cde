-- ============================================================================
-- FACILITY CDE v2 — Migration 003: Fix missing columns
-- Adds: status column to core.assets (used by query/engine.py)
--       line and zone columns to core.assets (used by ingestion/normalisers.py)
-- ============================================================================

ALTER TABLE core.assets ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active';
ALTER TABLE core.assets ADD COLUMN IF NOT EXISTS line TEXT NOT NULL DEFAULT '';
ALTER TABLE core.assets ADD COLUMN IF NOT EXISTS zone TEXT NOT NULL DEFAULT '';

CREATE INDEX IF NOT EXISTS idx_core_assets_status ON core.assets(status);

INSERT INTO core.schema_migrations(version) VALUES ('003_add_status_column')
ON CONFLICT (version) DO NOTHING;
