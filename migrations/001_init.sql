-- ============================================================================
-- FACILITY CDE v2 — PostgreSQL Schema
-- Design: one Postgres SCHEMA (namespace) per input medium, not just tables.
-- Rationale: each medium (CV, scrap/batch, geometry, BIM, RAG docs, comms)
-- has its own shape, its own growth rate, and its own owning teammate/module.
-- Namespacing lets each grow independently (own migrations, own indexes,
-- own RBAC via GRANT) while `core` ties everything together through
-- asset_id and a unified findings view for the WhatsApp query layer.
--
-- Schemas:
--   core     -> assets, insights, unified findings view (query-layer facing)
--   auth     -> users, roles, groups, rate limiting
--   cv       -> object detections + object tracking (Formats 2 & 3)
--   scrap    -> batch/scrap measurement pipeline (Format 1)
--   geometry -> generic geometry/shape output (Format 4) + semantic layer
--   bim      -> IFC / COBie / BIM JSON (native BIM, not the CV geometry)
--   rag      -> documents, chunks, embeddings (pgvector-ready)
--   comms    -> WhatsApp messages/media (source of truth for chat layer)
--   ingest   -> file-level audit trail for the ingestion pipeline
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- gen_random_uuid()
-- CREATE EXTENSION IF NOT EXISTS vector;  -- uncomment if pgvector is installed;
                                            -- otherwise keep embeddings in ChromaDB
                                            -- and use rag.chunks only for text + metadata.

CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS cv;
CREATE SCHEMA IF NOT EXISTS scrap;
CREATE SCHEMA IF NOT EXISTS geometry;
CREATE SCHEMA IF NOT EXISTS bim;
CREATE SCHEMA IF NOT EXISTS rag;
CREATE SCHEMA IF NOT EXISTS comms;
CREATE SCHEMA IF NOT EXISTS ingest;

-- ============================================================================
-- CORE — the only cross-medium namespace. Every other schema's asset_id
-- references core.assets. This is what makes "AMA about the facility" work
-- across mediums without collapsing their differences into one wide table.
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.assets (
    asset_id     TEXT PRIMARY KEY,          -- e.g. M14, BATCH1, SESSION_001, BIM-ELEM-8831
    name         TEXT NOT NULL,
    type         TEXT,                      -- CNC Lathe, scrap_batch, cv_tracking, ifc_element...
    location     TEXT,
    external_refs JSONB DEFAULT '{}'::jsonb,-- e.g. {"ifc_guid": "...", "bim_space": "..."}
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_core_assets_type ON core.assets(type);
CREATE INDEX IF NOT EXISTS idx_core_assets_external_refs ON core.assets USING GIN (external_refs);

CREATE TABLE IF NOT EXISTS core.insights (
    insight_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id      TEXT NOT NULL REFERENCES core.assets(asset_id) ON DELETE CASCADE,
    summary       TEXT,
    severity      TEXT CHECK (severity IN ('low','medium','high','critical')),
    generated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_core_insights_asset ON core.insights(asset_id);

-- expert notes are cross-medium annotations, kept in core since they aren't
-- tied to any one ingestion pipeline
CREATE TABLE IF NOT EXISTS core.expert_notes (
    note_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id    TEXT NOT NULL REFERENCES core.assets(asset_id) ON DELETE CASCADE,
    comment     TEXT NOT NULL,
    author      TEXT,                       -- FK to auth.users(phone), soft-linked
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_core_notes_asset ON core.expert_notes(asset_id);

-- ============================================================================
-- AUTH — users, roles, groups, rate limiting
-- ============================================================================

CREATE TABLE IF NOT EXISTS auth.users (
    phone       TEXT PRIMARY KEY,           -- whatsapp:+91XXXXXXXXXX or +91XXXXXXXXXX
    name        TEXT,
    role        TEXT NOT NULL CHECK (role IN ('admin','expert','technician','viewer')),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS auth.rate_limit_log (
    id          BIGSERIAL PRIMARY KEY,
    phone       TEXT NOT NULL REFERENCES auth.users(phone) ON DELETE CASCADE,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_auth_rate_phone_time ON auth.rate_limit_log(phone, requested_at);

CREATE TABLE IF NOT EXISTS auth.groups (
    group_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_name   TEXT,
    wa_group_id  TEXT UNIQUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS auth.group_members (
    phone     TEXT REFERENCES auth.users(phone) ON DELETE CASCADE,
    group_id  UUID REFERENCES auth.groups(group_id) ON DELETE CASCADE,
    PRIMARY KEY (phone, group_id)
);

-- ============================================================================
-- CV — object detections (Format 3) + object tracking / annotations (Format 2)
-- Split into two tables because they come from different CV submodules
-- with different fields, even though both live under "cv".
-- ============================================================================

CREATE TABLE IF NOT EXISTS cv.detections (
    detection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id     TEXT NOT NULL REFERENCES core.assets(asset_id) ON DELETE CASCADE,
    object       TEXT,                      -- e.g. "Hydraulic cylinder"
    condition    TEXT,                      -- e.g. "Pressure drop"
    confidence   NUMERIC(4,3) CHECK (confidence BETWEEN 0 AND 1),
    source       TEXT DEFAULT 'cv_module',
    timestamp    TIMESTAMPTZ,
    raw_json     JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_cv_detections_asset ON cv.detections(asset_id);
CREATE INDEX IF NOT EXISTS idx_cv_detections_confidence ON cv.detections(confidence);
CREATE INDEX IF NOT EXISTS idx_cv_detections_raw ON cv.detections USING GIN (raw_json);

CREATE TABLE IF NOT EXISTS cv.sessions (
    session_id   TEXT PRIMARY KEY,          -- groups track_N entries from one export
    asset_id     TEXT REFERENCES core.assets(asset_id) ON DELETE SET NULL,
    source       TEXT DEFAULT 'cv_tracking',
    started_at   TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cv.tracks (
    track_pk     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    track_id     INTEGER,                   -- original track_N index, not globally unique
    session_id   TEXT REFERENCES cv.sessions(session_id) ON DELETE CASCADE,
    asset_id     TEXT NOT NULL REFERENCES core.assets(asset_id) ON DELETE CASCADE,
    label        TEXT,
    category     TEXT,
    class_name   TEXT,
    frame_id     INTEGER,
    area         NUMERIC,
    bbox         JSONB,                     -- [x,y,w,h]
    centroid     JSONB,                     -- [x,y]
    angle        NUMERIC,
    notes        TEXT,
    saved_at     TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_cv_tracks_asset ON cv.tracks(asset_id);
CREATE INDEX IF NOT EXISTS idx_cv_tracks_session ON cv.tracks(session_id);

-- ============================================================================
-- SCRAP — batch/scrap measurement pipeline (Format 1)
-- Normalized out of the flat scraps[] array into batches -> scraps ->
-- vertices/side_lengths, since these are the fields most likely to be
-- queried individually (e.g. "average area of squares in batch 3").
-- ============================================================================

CREATE TABLE IF NOT EXISTS scrap.batches (
    batch_id       TEXT PRIMARY KEY,        -- e.g. BATCH1
    asset_id       TEXT NOT NULL REFERENCES core.assets(asset_id) ON DELETE CASCADE,
    batch_number   INTEGER,
    cm_per_pixel   NUMERIC,
    total_scraps   INTEGER,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS scrap.scraps (
    scrap_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id         TEXT NOT NULL REFERENCES scrap.batches(batch_id) ON DELETE CASCADE,
    piece_name       TEXT,
    shape_type       TEXT,                  -- as labeled by CV module
    verified_shape   TEXT,                  -- semantic-check result, may differ from shape_type
    vertices_count   INTEGER,
    area_cm2         NUMERIC,
    raw_json         JSONB,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_scrap_scraps_batch ON scrap.scraps(batch_id);
CREATE INDEX IF NOT EXISTS idx_scrap_scraps_shape ON scrap.scraps(shape_type);

CREATE TABLE IF NOT EXISTS scrap.vertices (
    id          BIGSERIAL PRIMARY KEY,
    scrap_id    UUID NOT NULL REFERENCES scrap.scraps(scrap_id) ON DELETE CASCADE,
    label       TEXT,                       -- "A", "B", "C"...
    x           NUMERIC,
    y           NUMERIC
);
CREATE INDEX IF NOT EXISTS idx_scrap_vertices_scrap ON scrap.vertices(scrap_id);

CREATE TABLE IF NOT EXISTS scrap.side_lengths (
    id          BIGSERIAL PRIMARY KEY,
    scrap_id    UUID NOT NULL REFERENCES scrap.scraps(scrap_id) ON DELETE CASCADE,
    side_label  TEXT,                       -- "AB", "BC"...
    length_cm   NUMERIC
);
CREATE INDEX IF NOT EXISTS idx_scrap_sides_scrap ON scrap.side_lengths(scrap_id);

CREATE TABLE IF NOT EXISTS scrap.batch_images (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id    TEXT NOT NULL REFERENCES scrap.batches(batch_id) ON DELETE CASCADE,
    file_path   TEXT NOT NULL,
    label       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- GEOMETRY — generic CV-side geometry/shape output (Format 4, still open),
-- plus the semantic verification layer (RDF/OWL groundwork) mentioned in
-- the project's own learnings: flags where a labeled shape doesn't match
-- its measured geometry.
-- ============================================================================

CREATE TABLE IF NOT EXISTS geometry.shapes (
    shape_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id     TEXT NOT NULL REFERENCES core.assets(asset_id) ON DELETE CASCADE,
    source       TEXT,                      -- e.g. "geometry_analysis"
    shape_type   TEXT,
    raw_json     JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_geometry_shapes_asset ON geometry.shapes(asset_id);
CREATE INDEX IF NOT EXISTS idx_geometry_shapes_raw ON geometry.shapes USING GIN (raw_json);

CREATE TABLE IF NOT EXISTS geometry.elements (
    element_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shape_id     UUID NOT NULL REFERENCES geometry.shapes(shape_id) ON DELETE CASCADE,
    element_type TEXT,                      -- point/edge/face/mesh
    coordinates  JSONB
);

CREATE TABLE IF NOT EXISTS geometry.semantic_tags (
    id             BIGSERIAL PRIMARY KEY,
    shape_id       UUID NOT NULL REFERENCES geometry.shapes(shape_id) ON DELETE CASCADE,
    predicate      TEXT,                    -- e.g. "isSquare", "isAdjacentTo" (OWL/RDF-style)
    object_value   TEXT,
    confidence     NUMERIC(4,3),
    generated_by   TEXT DEFAULT 'owlrl',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_geometry_semantic_shape ON geometry.semantic_tags(shape_id);

-- ============================================================================
-- BIM — native BIM data: IFC elements, COBie components, spatial hierarchy.
-- Kept fully separate from `geometry` because BIM geometry is authored
-- (design-intent, GUID-stable) rather than measured/detected, and carries
-- its own containment hierarchy (site -> building -> storey -> space -> element).
-- ============================================================================

CREATE TABLE IF NOT EXISTS bim.projects (
    project_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name         TEXT NOT NULL,
    ifc_schema_version TEXT,                -- e.g. IFC4
    source_file  TEXT,
    imported_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bim.spatial_structure (
    node_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id   UUID NOT NULL REFERENCES bim.projects(project_id) ON DELETE CASCADE,
    parent_node_id UUID REFERENCES bim.spatial_structure(node_id) ON DELETE CASCADE,
    node_type    TEXT CHECK (node_type IN ('site','building','storey','space')),
    name         TEXT,
    ifc_guid     TEXT UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_bim_structure_parent ON bim.spatial_structure(parent_node_id);

CREATE TABLE IF NOT EXISTS bim.elements (
    element_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id       TEXT REFERENCES core.assets(asset_id) ON DELETE SET NULL,
    project_id     UUID NOT NULL REFERENCES bim.projects(project_id) ON DELETE CASCADE,
    spatial_node_id UUID REFERENCES bim.spatial_structure(node_id) ON DELETE SET NULL,
    ifc_guid       TEXT UNIQUE,
    ifc_type       TEXT,                    -- IfcWall, IfcPump, IfcDuctSegment...
    name           TEXT,
    properties     JSONB DEFAULT '{}'::jsonb, -- IFC property sets (Pset_*)
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_bim_elements_project ON bim.elements(project_id);
CREATE INDEX IF NOT EXISTS idx_bim_elements_type ON bim.elements(ifc_type);
CREATE INDEX IF NOT EXISTS idx_bim_elements_properties ON bim.elements USING GIN (properties);

-- native geometry representation; kept JSONB until normalise_geometry() is
-- finalized, so ingestion doesn't block on a fixed geometry schema
CREATE TABLE IF NOT EXISTS bim.element_geometry (
    element_id     UUID PRIMARY KEY REFERENCES bim.elements(element_id) ON DELETE CASCADE,
    geometry_type  TEXT,                    -- brep/extrusion/mesh
    coordinate_system TEXT DEFAULT 'project_local',
    geometry_data  JSONB,                   -- raw IFC geometry pending normaliser
    bounding_box   JSONB                    -- [minx,miny,minz,maxx,maxy,maxz]
);

-- COBie is a specific export format layered on top of IFC elements
CREATE TABLE IF NOT EXISTS bim.cobie_components (
    component_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    element_id     UUID REFERENCES bim.elements(element_id) ON DELETE CASCADE,
    component_name TEXT,
    type_name      TEXT,
    space_name     TEXT,
    floor_name     TEXT,
    serial_number  TEXT,
    install_date   DATE,
    warranty_expiry DATE,
    raw_row        JSONB                    -- original COBie Excel row, unparsed columns preserved
);
CREATE INDEX IF NOT EXISTS idx_bim_cobie_element ON bim.cobie_components(element_id);

CREATE TABLE IF NOT EXISTS bim.relationships (
    id             BIGSERIAL PRIMARY KEY,
    project_id     UUID NOT NULL REFERENCES bim.projects(project_id) ON DELETE CASCADE,
    source_element_id UUID NOT NULL REFERENCES bim.elements(element_id) ON DELETE CASCADE,
    target_element_id UUID NOT NULL REFERENCES bim.elements(element_id) ON DELETE CASCADE,
    relationship_type TEXT                  -- e.g. IfcRelConnectsElements, IfcRelAggregates
);
CREATE INDEX IF NOT EXISTS idx_bim_rel_source ON bim.relationships(source_element_id);
CREATE INDEX IF NOT EXISTS idx_bim_rel_target ON bim.relationships(target_element_id);

-- ============================================================================
-- RAG — documents ingested for `ask` (PDF/TXT/manuals). Vectors can live
-- here via pgvector, or this table can hold text+metadata only while
-- ChromaDB continues to hold embeddings (embedding_ref points to the
-- Chroma record id in that case).
-- ============================================================================

CREATE TABLE IF NOT EXISTS rag.documents (
    doc_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title        TEXT,
    source_path  TEXT,
    doc_type     TEXT,                      -- pdf/txt/excel
    asset_id     TEXT REFERENCES core.assets(asset_id) ON DELETE SET NULL,
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rag.chunks (
    chunk_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id       UUID NOT NULL REFERENCES rag.documents(doc_id) ON DELETE CASCADE,
    chunk_index  INTEGER,
    content      TEXT NOT NULL,
    embedding_ref TEXT,                     -- ChromaDB record id, if vectors stay external
    -- embedding  VECTOR(768),              -- uncomment if pgvector extension is enabled
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_doc ON rag.chunks(doc_id);

-- ============================================================================
-- COMMS — WhatsApp message log. Kept separate from `auth` because message
-- volume/retention policy differs from user/session data.
-- ============================================================================

CREATE TABLE IF NOT EXISTS comms.messages (
    message_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone         TEXT NOT NULL REFERENCES auth.users(phone) ON DELETE CASCADE,
    direction     TEXT CHECK (direction IN ('inbound','outbound')),
    body          TEXT,
    parsed_intent TEXT,
    asset_id_ref  TEXT REFERENCES core.assets(asset_id) ON DELETE SET NULL,
    group_id      UUID REFERENCES auth.groups(group_id) ON DELETE SET NULL,
    timestamp     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_comms_messages_phone ON comms.messages(phone, timestamp);

CREATE TABLE IF NOT EXISTS comms.media (
    media_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id    UUID NOT NULL REFERENCES comms.messages(message_id) ON DELETE CASCADE,
    file_path     TEXT NOT NULL,
    media_type    TEXT
);

-- ============================================================================
-- INGEST — audit trail for the file-based pipeline (inbox -> processed/failed)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ingest.files (
    file_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename        TEXT NOT NULL,
    detected_schema TEXT,                   -- batch/cv/annotations/tracks/geometry/bim/finding/asset/unknown
    target_schema   TEXT,                   -- which pg schema it was routed to
    status          TEXT CHECK (status IN ('pending','processed','failed')) DEFAULT 'pending',
    error_log       TEXT,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ingest_files_status ON ingest.files(status);

-- ============================================================================
-- CORE.FINDINGS_UNIFIED — the query-layer view. This is what query/engine.py
-- should hit for get_findings()/critical()/latest(), so WhatsApp commands
-- don't need to know which schema an asset's data actually lives in.
-- ============================================================================

CREATE OR REPLACE VIEW core.findings_unified AS
SELECT detection_id::text AS finding_id, asset_id, object, condition, confidence,
       source, timestamp, 'cv.detections' AS origin
FROM cv.detections
UNION ALL
SELECT track_pk::text, asset_id, label AS object, class_name AS condition, NULL::numeric,
       'cv_tracking', saved_at, 'cv.tracks'
FROM cv.tracks
UNION ALL
SELECT s.scrap_id::text, b.asset_id, s.piece_name AS object, s.shape_type AS condition,
       NULL::numeric, 'scrap_batch', b.created_at, 'scrap.scraps'
FROM scrap.scraps s JOIN scrap.batches b ON b.batch_id = s.batch_id
UNION ALL
SELECT shape_id::text, asset_id, shape_type AS object, NULL, NULL::numeric,
       source, created_at, 'geometry.shapes'
FROM geometry.shapes
UNION ALL
SELECT element_id::text, asset_id, ifc_type AS object, name AS condition, NULL::numeric,
       'bim', created_at, 'bim.elements'
FROM bim.elements
WHERE asset_id IS NOT NULL;

-- Note: views can't be indexed directly. If findings_unified needs speed at
-- scale, convert it to a MATERIALIZED VIEW and REFRESH on ingest instead.
