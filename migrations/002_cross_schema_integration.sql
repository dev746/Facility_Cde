-- ============================================================================
-- FACILITY CDE v2 — Migration 002: Cross-Schema Integration Layer
-- Run after 001 (facility_cde_v2_postgres_schema.sql).
--
-- Important framing: all 9 schemas already live in ONE Postgres database.
-- CREATE SCHEMA in Postgres is a namespace inside a single DB, not a
-- separate database — so "integrate into one database" is structurally
-- already true. What was actually missing, and what this migration adds:
--   1. A generic edge table so any record in any schema can point at any
--      other record in any schema (core.cross_references)
--   2. A single fast read for "everything about asset X across every
--      medium" (core.asset_summary)
--   3. Fuzzy name matching so intent.py can resolve "hydraulic press" to
--      "Hydraulic Press #4" instead of requiring exact match
--   4. Full-text search across findings for keyword pre-filtering before
--      RAG/embeddings get involved
--   5. Migration bookkeeping so db_init() can apply this file exactly once
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE IF NOT EXISTS core.schema_migrations (
    version      TEXT PRIMARY KEY,
    applied_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- 1. CROSS-REFERENCES — the actual "cross-functional" layer.
-- Lets you say things like: "this scrap piece was cut from this BIM element",
-- "this CV detection is documented in this manual chunk", "this geometry
-- shape and this cv.track are the same physical object seen by two modules".
-- Deliberately medium-agnostic: source/target identify (schema, table, id)
-- rather than using typed FKs, since the whole point is that any two
-- schemas can reference each other without core.assets needing to model
-- every possible relationship type up front.
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS core.cross_references (
    ref_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_schema     TEXT NOT NULL,
    source_table      TEXT NOT NULL,
    source_id         TEXT NOT NULL,          -- store as text; casts cleanly from UUID or TEXT PKs
    target_schema     TEXT NOT NULL,
    target_table      TEXT NOT NULL,
    target_id         TEXT NOT NULL,
    relationship_type TEXT NOT NULL,           -- e.g. 'derived_from','same_physical_object',
                                                -- 'located_in','documents','superseded_by'
    confidence        NUMERIC(4,3),
    created_by        TEXT,                    -- 'llm_normaliser' | 'manual' | phone of the user
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_xref_source ON core.cross_references(source_schema, source_table, source_id);
CREATE INDEX IF NOT EXISTS idx_xref_target ON core.cross_references(target_schema, target_table, target_id);
CREATE INDEX IF NOT EXISTS idx_xref_type ON core.cross_references(relationship_type);

-- convenience view: both directions in one query, so callers don't need
-- to know whether the record they have was the source or the target
CREATE OR REPLACE VIEW core.cross_references_bidirectional AS
SELECT ref_id, source_schema, source_table, source_id,
       target_schema, target_table, target_id,
       relationship_type, confidence, created_at
FROM core.cross_references
UNION ALL
SELECT ref_id, target_schema, target_table, target_id,
       source_schema, source_table, source_id,
       relationship_type || '_inverse', confidence, created_at
FROM core.cross_references;

-- ----------------------------------------------------------------------------
-- 2. ASSET SUMMARY — one query, every medium's contribution to an asset.
-- This is what powers the `summary` WhatsApp command and is the clearest
-- payoff of the schema-per-medium design: instead of 6 separate queries
-- against 6 tables, commands.py makes one call.
--
-- Materialized (not a live view) because it aggregates across 7 tables
-- with subqueries — fine for on-demand refresh after ingestion, too slow
-- to recompute on every WhatsApp message.
-- ----------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS core.asset_summary AS
SELECT
    a.asset_id,
    a.name,
    a.type,
    a.location,
    (SELECT COUNT(*) FROM cv.detections d WHERE d.asset_id = a.asset_id)      AS cv_detection_count,
    (SELECT COUNT(*) FROM cv.tracks t WHERE t.asset_id = a.asset_id)          AS cv_track_count,
    (SELECT COUNT(*) FROM scrap.batches b WHERE b.asset_id = a.asset_id)      AS scrap_batch_count,
    (SELECT COUNT(*) FROM geometry.shapes g WHERE g.asset_id = a.asset_id)    AS geometry_shape_count,
    (SELECT COUNT(*) FROM bim.elements e WHERE e.asset_id = a.asset_id)       AS bim_element_count,
    (SELECT COUNT(*) FROM rag.documents r WHERE r.asset_id = a.asset_id)      AS rag_document_count,
    (SELECT COUNT(*) FROM core.expert_notes n WHERE n.asset_id = a.asset_id)  AS note_count,
    (SELECT COUNT(*) FROM core.cross_references x
       WHERE (x.source_schema, x.source_id) = ('core', a.asset_id)
          OR (x.target_schema, x.target_id) = ('core', a.asset_id))           AS cross_reference_count,
    (SELECT MAX(f.timestamp) FROM core.findings_unified f WHERE f.asset_id = a.asset_id) AS last_activity_at
FROM core.assets a;

-- required for REFRESH MATERIALIZED VIEW CONCURRENTLY
CREATE UNIQUE INDEX IF NOT EXISTS idx_asset_summary_pk ON core.asset_summary(asset_id);

-- ----------------------------------------------------------------------------
-- 3. FUZZY ASSET RESOLUTION — replaces exact-match find_asset_by_name()
-- "hydraulic press" -> "Hydraulic Press #4" via trigram similarity instead
-- of requiring the WhatsApp user to type the exact stored name.
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_core_assets_name_trgm ON core.assets USING GIN (name gin_trgm_ops);

CREATE OR REPLACE FUNCTION core.find_asset_by_name(search_term TEXT, match_limit INT DEFAULT 5)
RETURNS TABLE(asset_id TEXT, name TEXT, similarity REAL) AS $$
    SELECT asset_id, name, similarity(name, search_term) AS sim
    FROM core.assets
    WHERE name % search_term  -- pg_trgm's "reasonably similar" operator
    ORDER BY sim DESC
    LIMIT match_limit;
$$ LANGUAGE sql STABLE;

-- ----------------------------------------------------------------------------
-- 4. FULL-TEXT SEARCH across findings — keyword pre-filter for `ask` and
-- for intent resolution ("any pressure drop issues?" -> matches without
-- needing an embedding call). Materialized for index-ability; the live
-- `core.findings_unified` view remains the source of truth for
-- time-sensitive commands (`latest`, `critical`) since this view goes
-- stale between refreshes.
-- ----------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS core.findings_search AS
SELECT
    finding_id, asset_id, object, condition, confidence, source, timestamp, origin,
    to_tsvector('english', coalesce(object, '') || ' ' || coalesce(condition, '')) AS search_vector
FROM core.findings_unified;

CREATE UNIQUE INDEX IF NOT EXISTS idx_findings_search_pk ON core.findings_search(finding_id);
CREATE INDEX IF NOT EXISTS idx_findings_search_vector ON core.findings_search USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_findings_search_asset ON core.findings_search(asset_id);

-- ----------------------------------------------------------------------------
-- 5. updated_at trigger — the column existed in 001 but nothing set it
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION core.set_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_assets_updated_at ON core.assets;
CREATE TRIGGER trg_assets_updated_at
    BEFORE UPDATE ON core.assets
    FOR EACH ROW EXECUTE FUNCTION core.set_updated_at();

-- ----------------------------------------------------------------------------
-- 6. Ingestion audit needs a target table, not just a target schema
-- ----------------------------------------------------------------------------

ALTER TABLE ingest.files ADD COLUMN IF NOT EXISTS target_table TEXT;

-- ----------------------------------------------------------------------------
-- 7. VETTED FIX: bim.elements should not cascade-delete when core.assets
-- rows are removed. CV detections are cheap to regenerate; BIM data is
-- authored, expensive to reproduce, and often outlives whatever asset stub
-- row happens to reference it. Swap CASCADE for RESTRICT so deleting an
-- asset fails loudly instead of silently destroying BIM data.
-- ----------------------------------------------------------------------------

ALTER TABLE bim.elements DROP CONSTRAINT IF EXISTS bim_elements_asset_id_fkey;
ALTER TABLE bim.elements
    ADD CONSTRAINT bim_elements_asset_id_fkey
    FOREIGN KEY (asset_id) REFERENCES core.assets(asset_id) ON DELETE RESTRICT;

-- ----------------------------------------------------------------------------
-- Refresh helper — call after any ingestion batch completes
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION core.refresh_cross_functional_views() RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY core.asset_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY core.findings_search;
END;
$$ LANGUAGE plpgsql;

INSERT INTO core.schema_migrations(version) VALUES ('002_cross_schema_integration')
ON CONFLICT (version) DO NOTHING;
