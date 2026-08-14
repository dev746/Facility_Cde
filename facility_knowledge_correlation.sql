--
-- PostgreSQL database dump
--

\restrict lowMt82ormpYrHvh9geW3BXlDdIwPJtAcw65T5TeT1ECxQoerPkljneBa5NybXj

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY scrap.vertices DROP CONSTRAINT IF EXISTS vertices_scrap_id_fkey;
ALTER TABLE IF EXISTS ONLY scrap.side_lengths DROP CONSTRAINT IF EXISTS side_lengths_scrap_id_fkey;
ALTER TABLE IF EXISTS ONLY scrap.scraps DROP CONSTRAINT IF EXISTS scraps_batch_id_fkey;
ALTER TABLE IF EXISTS ONLY scrap.batches DROP CONSTRAINT IF EXISTS batches_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY scrap.batch_images DROP CONSTRAINT IF EXISTS batch_images_batch_id_fkey;
ALTER TABLE IF EXISTS ONLY rag.documents DROP CONSTRAINT IF EXISTS documents_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY rag.chunks DROP CONSTRAINT IF EXISTS chunks_doc_id_fkey;
ALTER TABLE IF EXISTS ONLY geometry.shapes DROP CONSTRAINT IF EXISTS shapes_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY geometry.semantic_tags DROP CONSTRAINT IF EXISTS semantic_tags_shape_id_fkey;
ALTER TABLE IF EXISTS ONLY geometry.elements DROP CONSTRAINT IF EXISTS elements_shape_id_fkey;
ALTER TABLE IF EXISTS ONLY cv.tracks DROP CONSTRAINT IF EXISTS tracks_session_id_fkey;
ALTER TABLE IF EXISTS ONLY cv.tracks DROP CONSTRAINT IF EXISTS tracks_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY cv.sessions DROP CONSTRAINT IF EXISTS sessions_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY cv.detections DROP CONSTRAINT IF EXISTS detections_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY core.insights DROP CONSTRAINT IF EXISTS insights_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY core.expert_notes DROP CONSTRAINT IF EXISTS expert_notes_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY comms.messages DROP CONSTRAINT IF EXISTS messages_phone_fkey;
ALTER TABLE IF EXISTS ONLY comms.messages DROP CONSTRAINT IF EXISTS messages_group_id_fkey;
ALTER TABLE IF EXISTS ONLY comms.messages DROP CONSTRAINT IF EXISTS messages_asset_id_ref_fkey;
ALTER TABLE IF EXISTS ONLY comms.media DROP CONSTRAINT IF EXISTS media_message_id_fkey;
ALTER TABLE IF EXISTS ONLY bim.spatial_structure DROP CONSTRAINT IF EXISTS spatial_structure_project_id_fkey;
ALTER TABLE IF EXISTS ONLY bim.spatial_structure DROP CONSTRAINT IF EXISTS spatial_structure_parent_node_id_fkey;
ALTER TABLE IF EXISTS ONLY bim.relationships DROP CONSTRAINT IF EXISTS relationships_target_element_id_fkey;
ALTER TABLE IF EXISTS ONLY bim.relationships DROP CONSTRAINT IF EXISTS relationships_source_element_id_fkey;
ALTER TABLE IF EXISTS ONLY bim.relationships DROP CONSTRAINT IF EXISTS relationships_project_id_fkey;
ALTER TABLE IF EXISTS ONLY bim.elements DROP CONSTRAINT IF EXISTS elements_spatial_node_id_fkey;
ALTER TABLE IF EXISTS ONLY bim.elements DROP CONSTRAINT IF EXISTS elements_project_id_fkey;
ALTER TABLE IF EXISTS ONLY bim.elements DROP CONSTRAINT IF EXISTS elements_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY bim.element_geometry DROP CONSTRAINT IF EXISTS element_geometry_element_id_fkey;
ALTER TABLE IF EXISTS ONLY bim.cobie_components DROP CONSTRAINT IF EXISTS cobie_components_element_id_fkey;
ALTER TABLE IF EXISTS ONLY bim.elements DROP CONSTRAINT IF EXISTS bim_elements_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.rate_limit_log DROP CONSTRAINT IF EXISTS rate_limit_log_phone_fkey;
ALTER TABLE IF EXISTS ONLY auth.group_members DROP CONSTRAINT IF EXISTS group_members_phone_fkey;
ALTER TABLE IF EXISTS ONLY auth.group_members DROP CONSTRAINT IF EXISTS group_members_group_id_fkey;
DROP TRIGGER IF EXISTS trg_assets_updated_at ON core.assets;
DROP INDEX IF EXISTS scrap.idx_scrap_vertices_scrap;
DROP INDEX IF EXISTS scrap.idx_scrap_sides_scrap;
DROP INDEX IF EXISTS scrap.idx_scrap_scraps_shape;
DROP INDEX IF EXISTS scrap.idx_scrap_scraps_batch;
DROP INDEX IF EXISTS rag.idx_rag_chunks_doc;
DROP INDEX IF EXISTS ingest.idx_ingest_files_status;
DROP INDEX IF EXISTS geometry.idx_geometry_shapes_raw;
DROP INDEX IF EXISTS geometry.idx_geometry_shapes_asset;
DROP INDEX IF EXISTS geometry.idx_geometry_semantic_shape;
DROP INDEX IF EXISTS cv.idx_cv_tracks_session;
DROP INDEX IF EXISTS cv.idx_cv_tracks_asset;
DROP INDEX IF EXISTS cv.idx_cv_detections_raw;
DROP INDEX IF EXISTS cv.idx_cv_detections_confidence;
DROP INDEX IF EXISTS cv.idx_cv_detections_asset;
DROP INDEX IF EXISTS core.idx_xref_type;
DROP INDEX IF EXISTS core.idx_xref_target;
DROP INDEX IF EXISTS core.idx_xref_source;
DROP INDEX IF EXISTS core.idx_findings_search_vector;
DROP INDEX IF EXISTS core.idx_findings_search_pk;
DROP INDEX IF EXISTS core.idx_findings_search_asset;
DROP INDEX IF EXISTS core.idx_core_notes_asset;
DROP INDEX IF EXISTS core.idx_core_insights_asset;
DROP INDEX IF EXISTS core.idx_core_assets_type;
DROP INDEX IF EXISTS core.idx_core_assets_status;
DROP INDEX IF EXISTS core.idx_core_assets_name_trgm;
DROP INDEX IF EXISTS core.idx_core_assets_external_refs;
DROP INDEX IF EXISTS core.idx_asset_summary_pk;
DROP INDEX IF EXISTS comms.idx_comms_messages_phone;
DROP INDEX IF EXISTS bim.idx_bim_structure_parent;
DROP INDEX IF EXISTS bim.idx_bim_rel_target;
DROP INDEX IF EXISTS bim.idx_bim_rel_source;
DROP INDEX IF EXISTS bim.idx_bim_elements_type;
DROP INDEX IF EXISTS bim.idx_bim_elements_properties;
DROP INDEX IF EXISTS bim.idx_bim_elements_project;
DROP INDEX IF EXISTS bim.idx_bim_cobie_element;
DROP INDEX IF EXISTS auth.idx_auth_rate_phone_time;
ALTER TABLE IF EXISTS ONLY scrap.vertices DROP CONSTRAINT IF EXISTS vertices_pkey;
ALTER TABLE IF EXISTS ONLY scrap.side_lengths DROP CONSTRAINT IF EXISTS side_lengths_pkey;
ALTER TABLE IF EXISTS ONLY scrap.scraps DROP CONSTRAINT IF EXISTS scraps_pkey;
ALTER TABLE IF EXISTS ONLY scrap.batches DROP CONSTRAINT IF EXISTS batches_pkey;
ALTER TABLE IF EXISTS ONLY scrap.batch_images DROP CONSTRAINT IF EXISTS batch_images_pkey;
ALTER TABLE IF EXISTS ONLY rag.documents DROP CONSTRAINT IF EXISTS documents_pkey;
ALTER TABLE IF EXISTS ONLY rag.chunks DROP CONSTRAINT IF EXISTS chunks_pkey;
ALTER TABLE IF EXISTS ONLY ingest.files DROP CONSTRAINT IF EXISTS files_pkey;
ALTER TABLE IF EXISTS ONLY geometry.shapes DROP CONSTRAINT IF EXISTS shapes_pkey;
ALTER TABLE IF EXISTS ONLY geometry.semantic_tags DROP CONSTRAINT IF EXISTS semantic_tags_pkey;
ALTER TABLE IF EXISTS ONLY geometry.elements DROP CONSTRAINT IF EXISTS elements_pkey;
ALTER TABLE IF EXISTS ONLY cv.tracks DROP CONSTRAINT IF EXISTS tracks_pkey;
ALTER TABLE IF EXISTS ONLY cv.sessions DROP CONSTRAINT IF EXISTS sessions_pkey;
ALTER TABLE IF EXISTS ONLY cv.detections DROP CONSTRAINT IF EXISTS detections_pkey;
ALTER TABLE IF EXISTS ONLY core.schema_migrations DROP CONSTRAINT IF EXISTS schema_migrations_pkey;
ALTER TABLE IF EXISTS ONLY core.insights DROP CONSTRAINT IF EXISTS insights_pkey;
ALTER TABLE IF EXISTS ONLY core.expert_notes DROP CONSTRAINT IF EXISTS expert_notes_pkey;
ALTER TABLE IF EXISTS ONLY core.cross_references DROP CONSTRAINT IF EXISTS cross_references_pkey;
ALTER TABLE IF EXISTS ONLY core.assets DROP CONSTRAINT IF EXISTS assets_pkey;
ALTER TABLE IF EXISTS ONLY comms.messages DROP CONSTRAINT IF EXISTS messages_pkey;
ALTER TABLE IF EXISTS ONLY comms.media DROP CONSTRAINT IF EXISTS media_pkey;
ALTER TABLE IF EXISTS ONLY bim.spatial_structure DROP CONSTRAINT IF EXISTS spatial_structure_pkey;
ALTER TABLE IF EXISTS ONLY bim.spatial_structure DROP CONSTRAINT IF EXISTS spatial_structure_ifc_guid_key;
ALTER TABLE IF EXISTS ONLY bim.relationships DROP CONSTRAINT IF EXISTS relationships_pkey;
ALTER TABLE IF EXISTS ONLY bim.projects DROP CONSTRAINT IF EXISTS projects_pkey;
ALTER TABLE IF EXISTS ONLY bim.elements DROP CONSTRAINT IF EXISTS elements_pkey;
ALTER TABLE IF EXISTS ONLY bim.elements DROP CONSTRAINT IF EXISTS elements_ifc_guid_key;
ALTER TABLE IF EXISTS ONLY bim.element_geometry DROP CONSTRAINT IF EXISTS element_geometry_pkey;
ALTER TABLE IF EXISTS ONLY bim.cobie_components DROP CONSTRAINT IF EXISTS cobie_components_pkey;
ALTER TABLE IF EXISTS ONLY auth.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY auth.rate_limit_log DROP CONSTRAINT IF EXISTS rate_limit_log_pkey;
ALTER TABLE IF EXISTS ONLY auth.groups DROP CONSTRAINT IF EXISTS groups_wa_group_id_key;
ALTER TABLE IF EXISTS ONLY auth.groups DROP CONSTRAINT IF EXISTS groups_pkey;
ALTER TABLE IF EXISTS ONLY auth.group_members DROP CONSTRAINT IF EXISTS group_members_pkey;
ALTER TABLE IF EXISTS scrap.vertices ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS scrap.side_lengths ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS geometry.semantic_tags ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS bim.relationships ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS auth.rate_limit_log ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS scrap.vertices_id_seq;
DROP TABLE IF EXISTS scrap.vertices;
DROP SEQUENCE IF EXISTS scrap.side_lengths_id_seq;
DROP TABLE IF EXISTS scrap.side_lengths;
DROP TABLE IF EXISTS scrap.batch_images;
DROP TABLE IF EXISTS rag.chunks;
DROP TABLE IF EXISTS ingest.files;
DROP SEQUENCE IF EXISTS geometry.semantic_tags_id_seq;
DROP TABLE IF EXISTS geometry.semantic_tags;
DROP TABLE IF EXISTS geometry.elements;
DROP TABLE IF EXISTS cv.sessions;
DROP TABLE IF EXISTS core.schema_migrations;
DROP TABLE IF EXISTS core.insights;
DROP MATERIALIZED VIEW IF EXISTS core.findings_search;
DROP VIEW IF EXISTS core.cross_references_bidirectional;
DROP MATERIALIZED VIEW IF EXISTS core.asset_summary;
DROP TABLE IF EXISTS rag.documents;
DROP VIEW IF EXISTS core.findings_unified;
DROP TABLE IF EXISTS scrap.scraps;
DROP TABLE IF EXISTS scrap.batches;
DROP TABLE IF EXISTS geometry.shapes;
DROP TABLE IF EXISTS cv.tracks;
DROP TABLE IF EXISTS cv.detections;
DROP TABLE IF EXISTS core.expert_notes;
DROP TABLE IF EXISTS core.cross_references;
DROP TABLE IF EXISTS core.assets;
DROP TABLE IF EXISTS comms.messages;
DROP TABLE IF EXISTS comms.media;
DROP TABLE IF EXISTS bim.spatial_structure;
DROP SEQUENCE IF EXISTS bim.relationships_id_seq;
DROP TABLE IF EXISTS bim.relationships;
DROP TABLE IF EXISTS bim.projects;
DROP TABLE IF EXISTS bim.elements;
DROP TABLE IF EXISTS bim.element_geometry;
DROP TABLE IF EXISTS bim.cobie_components;
DROP TABLE IF EXISTS auth.users;
DROP SEQUENCE IF EXISTS auth.rate_limit_log_id_seq;
DROP TABLE IF EXISTS auth.rate_limit_log;
DROP TABLE IF EXISTS auth.groups;
DROP TABLE IF EXISTS auth.group_members;
DROP FUNCTION IF EXISTS core.set_updated_at();
DROP FUNCTION IF EXISTS core.refresh_cross_functional_views();
DROP FUNCTION IF EXISTS core.find_asset_by_name(search_term text, match_limit integer);
DROP EXTENSION IF EXISTS pgcrypto;
DROP EXTENSION IF EXISTS pg_trgm;
DROP SCHEMA IF EXISTS scrap;
DROP SCHEMA IF EXISTS rag;
DROP SCHEMA IF EXISTS ingest;
DROP SCHEMA IF EXISTS geometry;
DROP SCHEMA IF EXISTS cv;
DROP SCHEMA IF EXISTS core;
DROP SCHEMA IF EXISTS comms;
DROP SCHEMA IF EXISTS bim;
DROP SCHEMA IF EXISTS auth;
--
-- Name: auth; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA auth;


ALTER SCHEMA auth OWNER TO postgres;

--
-- Name: bim; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA bim;


ALTER SCHEMA bim OWNER TO postgres;

--
-- Name: comms; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA comms;


ALTER SCHEMA comms OWNER TO postgres;

--
-- Name: core; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA core;


ALTER SCHEMA core OWNER TO postgres;

--
-- Name: cv; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA cv;


ALTER SCHEMA cv OWNER TO postgres;

--
-- Name: geometry; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA geometry;


ALTER SCHEMA geometry OWNER TO postgres;

--
-- Name: ingest; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA ingest;


ALTER SCHEMA ingest OWNER TO postgres;

--
-- Name: rag; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA rag;


ALTER SCHEMA rag OWNER TO postgres;

--
-- Name: scrap; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA scrap;


ALTER SCHEMA scrap OWNER TO postgres;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: find_asset_by_name(text, integer); Type: FUNCTION; Schema: core; Owner: postgres
--

CREATE FUNCTION core.find_asset_by_name(search_term text, match_limit integer DEFAULT 5) RETURNS TABLE(asset_id text, name text, similarity real)
    LANGUAGE sql STABLE
    AS $$
    SELECT asset_id, name, similarity(name, search_term) AS sim
    FROM core.assets
    WHERE name % search_term  -- pg_trgm's "reasonably similar" operator
    ORDER BY sim DESC
    LIMIT match_limit;
$$;


ALTER FUNCTION core.find_asset_by_name(search_term text, match_limit integer) OWNER TO postgres;

--
-- Name: refresh_cross_functional_views(); Type: FUNCTION; Schema: core; Owner: postgres
--

CREATE FUNCTION core.refresh_cross_functional_views() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY core.asset_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY core.findings_search;
END;
$$;


ALTER FUNCTION core.refresh_cross_functional_views() OWNER TO postgres;

--
-- Name: set_updated_at(); Type: FUNCTION; Schema: core; Owner: postgres
--

CREATE FUNCTION core.set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION core.set_updated_at() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: group_members; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.group_members (
    phone text NOT NULL,
    group_id uuid NOT NULL
);


ALTER TABLE auth.group_members OWNER TO postgres;

--
-- Name: groups; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.groups (
    group_id uuid DEFAULT gen_random_uuid() NOT NULL,
    group_name text,
    wa_group_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE auth.groups OWNER TO postgres;

--
-- Name: rate_limit_log; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.rate_limit_log (
    id bigint NOT NULL,
    phone text NOT NULL,
    requested_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE auth.rate_limit_log OWNER TO postgres;

--
-- Name: rate_limit_log_id_seq; Type: SEQUENCE; Schema: auth; Owner: postgres
--

CREATE SEQUENCE auth.rate_limit_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.rate_limit_log_id_seq OWNER TO postgres;

--
-- Name: rate_limit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: postgres
--

ALTER SEQUENCE auth.rate_limit_log_id_seq OWNED BY auth.rate_limit_log.id;


--
-- Name: users; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.users (
    phone text NOT NULL,
    name text,
    role text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT users_role_check CHECK ((role = ANY (ARRAY['admin'::text, 'expert'::text, 'technician'::text, 'viewer'::text])))
);


ALTER TABLE auth.users OWNER TO postgres;

--
-- Name: cobie_components; Type: TABLE; Schema: bim; Owner: postgres
--

CREATE TABLE bim.cobie_components (
    component_id uuid DEFAULT gen_random_uuid() NOT NULL,
    element_id uuid,
    component_name text,
    type_name text,
    space_name text,
    floor_name text,
    serial_number text,
    install_date date,
    warranty_expiry date,
    raw_row jsonb
);


ALTER TABLE bim.cobie_components OWNER TO postgres;

--
-- Name: element_geometry; Type: TABLE; Schema: bim; Owner: postgres
--

CREATE TABLE bim.element_geometry (
    element_id uuid NOT NULL,
    geometry_type text,
    coordinate_system text DEFAULT 'project_local'::text,
    geometry_data jsonb,
    bounding_box jsonb
);


ALTER TABLE bim.element_geometry OWNER TO postgres;

--
-- Name: elements; Type: TABLE; Schema: bim; Owner: postgres
--

CREATE TABLE bim.elements (
    element_id uuid DEFAULT gen_random_uuid() NOT NULL,
    asset_id text,
    project_id uuid NOT NULL,
    spatial_node_id uuid,
    ifc_guid text,
    ifc_type text,
    name text,
    properties jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE bim.elements OWNER TO postgres;

--
-- Name: projects; Type: TABLE; Schema: bim; Owner: postgres
--

CREATE TABLE bim.projects (
    project_id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    ifc_schema_version text,
    source_file text,
    imported_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE bim.projects OWNER TO postgres;

--
-- Name: relationships; Type: TABLE; Schema: bim; Owner: postgres
--

CREATE TABLE bim.relationships (
    id bigint NOT NULL,
    project_id uuid NOT NULL,
    source_element_id uuid NOT NULL,
    target_element_id uuid NOT NULL,
    relationship_type text
);


ALTER TABLE bim.relationships OWNER TO postgres;

--
-- Name: relationships_id_seq; Type: SEQUENCE; Schema: bim; Owner: postgres
--

CREATE SEQUENCE bim.relationships_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE bim.relationships_id_seq OWNER TO postgres;

--
-- Name: relationships_id_seq; Type: SEQUENCE OWNED BY; Schema: bim; Owner: postgres
--

ALTER SEQUENCE bim.relationships_id_seq OWNED BY bim.relationships.id;


--
-- Name: spatial_structure; Type: TABLE; Schema: bim; Owner: postgres
--

CREATE TABLE bim.spatial_structure (
    node_id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    parent_node_id uuid,
    node_type text,
    name text,
    ifc_guid text,
    CONSTRAINT spatial_structure_node_type_check CHECK ((node_type = ANY (ARRAY['site'::text, 'building'::text, 'storey'::text, 'space'::text])))
);


ALTER TABLE bim.spatial_structure OWNER TO postgres;

--
-- Name: media; Type: TABLE; Schema: comms; Owner: postgres
--

CREATE TABLE comms.media (
    media_id uuid DEFAULT gen_random_uuid() NOT NULL,
    message_id uuid NOT NULL,
    file_path text NOT NULL,
    media_type text
);


ALTER TABLE comms.media OWNER TO postgres;

--
-- Name: messages; Type: TABLE; Schema: comms; Owner: postgres
--

CREATE TABLE comms.messages (
    message_id uuid DEFAULT gen_random_uuid() NOT NULL,
    phone text NOT NULL,
    direction text,
    body text,
    parsed_intent text,
    asset_id_ref text,
    group_id uuid,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT messages_direction_check CHECK ((direction = ANY (ARRAY['inbound'::text, 'outbound'::text])))
);


ALTER TABLE comms.messages OWNER TO postgres;

--
-- Name: assets; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.assets (
    asset_id text NOT NULL,
    name text NOT NULL,
    type text,
    location text,
    external_refs jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    status text DEFAULT 'active'::text NOT NULL,
    line text DEFAULT ''::text NOT NULL,
    zone text DEFAULT ''::text NOT NULL
);


ALTER TABLE core.assets OWNER TO postgres;

--
-- Name: cross_references; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.cross_references (
    ref_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_schema text NOT NULL,
    source_table text NOT NULL,
    source_id text NOT NULL,
    target_schema text NOT NULL,
    target_table text NOT NULL,
    target_id text NOT NULL,
    relationship_type text NOT NULL,
    confidence numeric(4,3),
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE core.cross_references OWNER TO postgres;

--
-- Name: expert_notes; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.expert_notes (
    note_id uuid DEFAULT gen_random_uuid() NOT NULL,
    asset_id text NOT NULL,
    comment text NOT NULL,
    author text,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE core.expert_notes OWNER TO postgres;

--
-- Name: detections; Type: TABLE; Schema: cv; Owner: postgres
--

CREATE TABLE cv.detections (
    detection_id uuid DEFAULT gen_random_uuid() NOT NULL,
    asset_id text NOT NULL,
    object text,
    condition text,
    confidence numeric(4,3),
    source text DEFAULT 'cv_module'::text,
    "timestamp" timestamp with time zone,
    raw_json jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT detections_confidence_check CHECK (((confidence >= (0)::numeric) AND (confidence <= (1)::numeric)))
);


ALTER TABLE cv.detections OWNER TO postgres;

--
-- Name: tracks; Type: TABLE; Schema: cv; Owner: postgres
--

CREATE TABLE cv.tracks (
    track_pk uuid DEFAULT gen_random_uuid() NOT NULL,
    track_id integer,
    session_id text,
    asset_id text NOT NULL,
    label text,
    category text,
    class_name text,
    frame_id integer,
    area numeric,
    bbox jsonb,
    centroid jsonb,
    angle numeric,
    notes text,
    saved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cv.tracks OWNER TO postgres;

--
-- Name: shapes; Type: TABLE; Schema: geometry; Owner: postgres
--

CREATE TABLE geometry.shapes (
    shape_id uuid DEFAULT gen_random_uuid() NOT NULL,
    asset_id text NOT NULL,
    source text,
    shape_type text,
    raw_json jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE geometry.shapes OWNER TO postgres;

--
-- Name: batches; Type: TABLE; Schema: scrap; Owner: postgres
--

CREATE TABLE scrap.batches (
    batch_id text NOT NULL,
    asset_id text NOT NULL,
    batch_number integer,
    cm_per_pixel numeric,
    total_scraps integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE scrap.batches OWNER TO postgres;

--
-- Name: scraps; Type: TABLE; Schema: scrap; Owner: postgres
--

CREATE TABLE scrap.scraps (
    scrap_id uuid DEFAULT gen_random_uuid() NOT NULL,
    batch_id text NOT NULL,
    piece_name text,
    shape_type text,
    verified_shape text,
    vertices_count integer,
    area_cm2 numeric,
    raw_json jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE scrap.scraps OWNER TO postgres;

--
-- Name: findings_unified; Type: VIEW; Schema: core; Owner: postgres
--

CREATE VIEW core.findings_unified AS
 SELECT (detections.detection_id)::text AS finding_id,
    detections.asset_id,
    detections.object,
    detections.condition,
    detections.confidence,
    detections.source,
    detections."timestamp",
    'cv.detections'::text AS origin
   FROM cv.detections
UNION ALL
 SELECT (tracks.track_pk)::text AS finding_id,
    tracks.asset_id,
    tracks.label AS object,
    tracks.class_name AS condition,
    NULL::numeric AS confidence,
    'cv_tracking'::text AS source,
    tracks.saved_at AS "timestamp",
    'cv.tracks'::text AS origin
   FROM cv.tracks
UNION ALL
 SELECT (s.scrap_id)::text AS finding_id,
    b.asset_id,
    s.piece_name AS object,
    s.shape_type AS condition,
    NULL::numeric AS confidence,
    'scrap_batch'::text AS source,
    b.created_at AS "timestamp",
    'scrap.scraps'::text AS origin
   FROM (scrap.scraps s
     JOIN scrap.batches b ON ((b.batch_id = s.batch_id)))
UNION ALL
 SELECT (shapes.shape_id)::text AS finding_id,
    shapes.asset_id,
    shapes.shape_type AS object,
    NULL::text AS condition,
    NULL::numeric AS confidence,
    shapes.source,
    shapes.created_at AS "timestamp",
    'geometry.shapes'::text AS origin
   FROM geometry.shapes
UNION ALL
 SELECT (elements.element_id)::text AS finding_id,
    elements.asset_id,
    elements.ifc_type AS object,
    elements.name AS condition,
    NULL::numeric AS confidence,
    'bim'::text AS source,
    elements.created_at AS "timestamp",
    'bim.elements'::text AS origin
   FROM bim.elements
  WHERE (elements.asset_id IS NOT NULL);


ALTER VIEW core.findings_unified OWNER TO postgres;

--
-- Name: documents; Type: TABLE; Schema: rag; Owner: postgres
--

CREATE TABLE rag.documents (
    doc_id uuid DEFAULT gen_random_uuid() NOT NULL,
    title text,
    source_path text,
    doc_type text,
    asset_id text,
    ingested_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE rag.documents OWNER TO postgres;

--
-- Name: asset_summary; Type: MATERIALIZED VIEW; Schema: core; Owner: postgres
--

CREATE MATERIALIZED VIEW core.asset_summary AS
 SELECT asset_id,
    name,
    type,
    location,
    ( SELECT count(*) AS count
           FROM cv.detections d
          WHERE (d.asset_id = a.asset_id)) AS cv_detection_count,
    ( SELECT count(*) AS count
           FROM cv.tracks t
          WHERE (t.asset_id = a.asset_id)) AS cv_track_count,
    ( SELECT count(*) AS count
           FROM scrap.batches b
          WHERE (b.asset_id = a.asset_id)) AS scrap_batch_count,
    ( SELECT count(*) AS count
           FROM geometry.shapes g
          WHERE (g.asset_id = a.asset_id)) AS geometry_shape_count,
    ( SELECT count(*) AS count
           FROM bim.elements e
          WHERE (e.asset_id = a.asset_id)) AS bim_element_count,
    ( SELECT count(*) AS count
           FROM rag.documents r
          WHERE (r.asset_id = a.asset_id)) AS rag_document_count,
    ( SELECT count(*) AS count
           FROM core.expert_notes n
          WHERE (n.asset_id = a.asset_id)) AS note_count,
    ( SELECT count(*) AS count
           FROM core.cross_references x
          WHERE (((x.source_schema = 'core'::text) AND (x.source_id = a.asset_id)) OR ((x.target_schema = 'core'::text) AND (x.target_id = a.asset_id)))) AS cross_reference_count,
    ( SELECT max(f."timestamp") AS max
           FROM core.findings_unified f
          WHERE (f.asset_id = a.asset_id)) AS last_activity_at
   FROM core.assets a
  WITH NO DATA;


ALTER MATERIALIZED VIEW core.asset_summary OWNER TO postgres;

--
-- Name: cross_references_bidirectional; Type: VIEW; Schema: core; Owner: postgres
--

CREATE VIEW core.cross_references_bidirectional AS
 SELECT cross_references.ref_id,
    cross_references.source_schema,
    cross_references.source_table,
    cross_references.source_id,
    cross_references.target_schema,
    cross_references.target_table,
    cross_references.target_id,
    cross_references.relationship_type,
    cross_references.confidence,
    cross_references.created_at
   FROM core.cross_references
UNION ALL
 SELECT cross_references.ref_id,
    cross_references.target_schema AS source_schema,
    cross_references.target_table AS source_table,
    cross_references.target_id AS source_id,
    cross_references.source_schema AS target_schema,
    cross_references.source_table AS target_table,
    cross_references.source_id AS target_id,
    (cross_references.relationship_type || '_inverse'::text) AS relationship_type,
    cross_references.confidence,
    cross_references.created_at
   FROM core.cross_references;


ALTER VIEW core.cross_references_bidirectional OWNER TO postgres;

--
-- Name: findings_search; Type: MATERIALIZED VIEW; Schema: core; Owner: postgres
--

CREATE MATERIALIZED VIEW core.findings_search AS
 SELECT finding_id,
    asset_id,
    object,
    condition,
    confidence,
    source,
    "timestamp",
    origin,
    to_tsvector('english'::regconfig, ((COALESCE(object, ''::text) || ' '::text) || COALESCE(condition, ''::text))) AS search_vector
   FROM core.findings_unified
  WITH NO DATA;


ALTER MATERIALIZED VIEW core.findings_search OWNER TO postgres;

--
-- Name: insights; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.insights (
    insight_id uuid DEFAULT gen_random_uuid() NOT NULL,
    asset_id text NOT NULL,
    summary text,
    severity text,
    generated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT insights_severity_check CHECK ((severity = ANY (ARRAY['low'::text, 'medium'::text, 'high'::text, 'critical'::text])))
);


ALTER TABLE core.insights OWNER TO postgres;

--
-- Name: schema_migrations; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.schema_migrations (
    version text NOT NULL,
    applied_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE core.schema_migrations OWNER TO postgres;

--
-- Name: sessions; Type: TABLE; Schema: cv; Owner: postgres
--

CREATE TABLE cv.sessions (
    session_id text NOT NULL,
    asset_id text,
    source text DEFAULT 'cv_tracking'::text,
    started_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cv.sessions OWNER TO postgres;

--
-- Name: elements; Type: TABLE; Schema: geometry; Owner: postgres
--

CREATE TABLE geometry.elements (
    element_id uuid DEFAULT gen_random_uuid() NOT NULL,
    shape_id uuid NOT NULL,
    element_type text,
    coordinates jsonb
);


ALTER TABLE geometry.elements OWNER TO postgres;

--
-- Name: semantic_tags; Type: TABLE; Schema: geometry; Owner: postgres
--

CREATE TABLE geometry.semantic_tags (
    id bigint NOT NULL,
    shape_id uuid NOT NULL,
    predicate text,
    object_value text,
    confidence numeric(4,3),
    generated_by text DEFAULT 'owlrl'::text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE geometry.semantic_tags OWNER TO postgres;

--
-- Name: semantic_tags_id_seq; Type: SEQUENCE; Schema: geometry; Owner: postgres
--

CREATE SEQUENCE geometry.semantic_tags_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE geometry.semantic_tags_id_seq OWNER TO postgres;

--
-- Name: semantic_tags_id_seq; Type: SEQUENCE OWNED BY; Schema: geometry; Owner: postgres
--

ALTER SEQUENCE geometry.semantic_tags_id_seq OWNED BY geometry.semantic_tags.id;


--
-- Name: files; Type: TABLE; Schema: ingest; Owner: postgres
--

CREATE TABLE ingest.files (
    file_id uuid DEFAULT gen_random_uuid() NOT NULL,
    filename text NOT NULL,
    detected_schema text,
    target_schema text,
    status text DEFAULT 'pending'::text,
    error_log text,
    ingested_at timestamp with time zone DEFAULT now() NOT NULL,
    target_table text,
    CONSTRAINT files_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'processed'::text, 'failed'::text])))
);


ALTER TABLE ingest.files OWNER TO postgres;

--
-- Name: chunks; Type: TABLE; Schema: rag; Owner: postgres
--

CREATE TABLE rag.chunks (
    chunk_id uuid DEFAULT gen_random_uuid() NOT NULL,
    doc_id uuid NOT NULL,
    chunk_index integer,
    content text NOT NULL,
    embedding_ref text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE rag.chunks OWNER TO postgres;

--
-- Name: batch_images; Type: TABLE; Schema: scrap; Owner: postgres
--

CREATE TABLE scrap.batch_images (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    batch_id text NOT NULL,
    file_path text NOT NULL,
    label text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE scrap.batch_images OWNER TO postgres;

--
-- Name: side_lengths; Type: TABLE; Schema: scrap; Owner: postgres
--

CREATE TABLE scrap.side_lengths (
    id bigint NOT NULL,
    scrap_id uuid NOT NULL,
    side_label text,
    length_cm numeric
);


ALTER TABLE scrap.side_lengths OWNER TO postgres;

--
-- Name: side_lengths_id_seq; Type: SEQUENCE; Schema: scrap; Owner: postgres
--

CREATE SEQUENCE scrap.side_lengths_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE scrap.side_lengths_id_seq OWNER TO postgres;

--
-- Name: side_lengths_id_seq; Type: SEQUENCE OWNED BY; Schema: scrap; Owner: postgres
--

ALTER SEQUENCE scrap.side_lengths_id_seq OWNED BY scrap.side_lengths.id;


--
-- Name: vertices; Type: TABLE; Schema: scrap; Owner: postgres
--

CREATE TABLE scrap.vertices (
    id bigint NOT NULL,
    scrap_id uuid NOT NULL,
    label text,
    x numeric,
    y numeric
);


ALTER TABLE scrap.vertices OWNER TO postgres;

--
-- Name: vertices_id_seq; Type: SEQUENCE; Schema: scrap; Owner: postgres
--

CREATE SEQUENCE scrap.vertices_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE scrap.vertices_id_seq OWNER TO postgres;

--
-- Name: vertices_id_seq; Type: SEQUENCE OWNED BY; Schema: scrap; Owner: postgres
--

ALTER SEQUENCE scrap.vertices_id_seq OWNED BY scrap.vertices.id;


--
-- Name: rate_limit_log id; Type: DEFAULT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.rate_limit_log ALTER COLUMN id SET DEFAULT nextval('auth.rate_limit_log_id_seq'::regclass);


--
-- Name: relationships id; Type: DEFAULT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.relationships ALTER COLUMN id SET DEFAULT nextval('bim.relationships_id_seq'::regclass);


--
-- Name: semantic_tags id; Type: DEFAULT; Schema: geometry; Owner: postgres
--

ALTER TABLE ONLY geometry.semantic_tags ALTER COLUMN id SET DEFAULT nextval('geometry.semantic_tags_id_seq'::regclass);


--
-- Name: side_lengths id; Type: DEFAULT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.side_lengths ALTER COLUMN id SET DEFAULT nextval('scrap.side_lengths_id_seq'::regclass);


--
-- Name: vertices id; Type: DEFAULT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.vertices ALTER COLUMN id SET DEFAULT nextval('scrap.vertices_id_seq'::regclass);


--
-- Data for Name: group_members; Type: TABLE DATA; Schema: auth; Owner: postgres
--



--
-- Data for Name: groups; Type: TABLE DATA; Schema: auth; Owner: postgres
--



--
-- Data for Name: rate_limit_log; Type: TABLE DATA; Schema: auth; Owner: postgres
--



--
-- Data for Name: users; Type: TABLE DATA; Schema: auth; Owner: postgres
--

INSERT INTO auth.users (phone, name, role, is_active, created_at) VALUES ('+919876543210', 'Priya Sharma', 'expert', true, '2026-08-08 11:16:12.669222+05:30');
INSERT INTO auth.users (phone, name, role, is_active, created_at) VALUES ('+919876543211', 'Arjun Mehta', 'technician', true, '2026-08-08 11:16:12.669222+05:30');
INSERT INTO auth.users (phone, name, role, is_active, created_at) VALUES ('+919876543212', 'Ravi Kumar', 'technician', true, '2026-08-08 11:16:12.669222+05:30');
INSERT INTO auth.users (phone, name, role, is_active, created_at) VALUES ('+919876543213', 'System Admin', 'admin', true, '2026-08-08 11:16:12.669222+05:30');
INSERT INTO auth.users (phone, name, role, is_active, created_at) VALUES ('+919876543214', 'Quality Inspector', 'viewer', true, '2026-08-08 11:16:12.669222+05:30');


--
-- Data for Name: cobie_components; Type: TABLE DATA; Schema: bim; Owner: postgres
--



--
-- Data for Name: element_geometry; Type: TABLE DATA; Schema: bim; Owner: postgres
--



--
-- Data for Name: elements; Type: TABLE DATA; Schema: bim; Owner: postgres
--



--
-- Data for Name: projects; Type: TABLE DATA; Schema: bim; Owner: postgres
--



--
-- Data for Name: relationships; Type: TABLE DATA; Schema: bim; Owner: postgres
--



--
-- Data for Name: spatial_structure; Type: TABLE DATA; Schema: bim; Owner: postgres
--



--
-- Data for Name: media; Type: TABLE DATA; Schema: comms; Owner: postgres
--



--
-- Data for Name: messages; Type: TABLE DATA; Schema: comms; Owner: postgres
--



--
-- Data for Name: assets; Type: TABLE DATA; Schema: core; Owner: postgres
--

INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('SESSION_001', 'CV Tracking Session 001', 'cv_tracking', 'Bay 2, Line A', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.670844+05:30', 'active', 'Line A', 'Bay 2');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('SESSION_002', 'Scrap Session 002', 'scrap_measurement', 'Bay 4, Line B', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.670844+05:30', 'active', 'Line B', 'Bay 4');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('SESSION_003', 'Scrap Session 003', 'scrap_measurement', 'Bay 3, Line A', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.670844+05:30', 'active', 'Line A', 'Bay 3');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('SESSION_004', 'Scrap Session 004', 'scrap_measurement', 'Bay 3, Line B', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.670844+05:30', 'active', 'Line B', 'Bay 3');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('SESSION_005', 'Scrap Session 005', 'scrap_measurement', 'Bay 1, Line C', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.670844+05:30', 'active', 'Line C', 'Bay 1');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('BATCH1', 'Scrap Batch 1', 'scrap_batch', 'Bay 2, Line A', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.670844+05:30', 'active', 'Line A', 'Bay 2');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('BATCH2', 'Scrap Batch 2', 'scrap_batch', 'Bay 4, Line B', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.670844+05:30', 'active', 'Line B', 'Bay 4');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('BATCH3', 'Scrap Batch 3', 'scrap_batch', 'Bay 3, Line A', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.670844+05:30', 'active', 'Line A', 'Bay 3');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('BATCH4', 'Scrap Batch 4', 'scrap_batch', 'Bay 3, Line B', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.670844+05:30', 'active', 'Line B', 'Bay 3');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('BATCH5', 'Scrap Batch 5', 'scrap_batch', 'Bay 1, Line C', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.670844+05:30', 'active', 'Line C', 'Bay 1');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('M14', 'CNC Lathe #14', 'CNC Lathe', 'Bay 2, Line A', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.714233+05:30', 'active', 'Line A', 'Bay 2');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('M22', 'Hydraulic Press #22', 'Hydraulic Press', 'Bay 4, Line B', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.715484+05:30', 'active', 'Line B', 'Bay 4');
INSERT INTO core.assets (asset_id, name, type, location, external_refs, created_at, updated_at, status, line, zone) VALUES ('M37', 'Conveyor Belt #37', 'Conveyor Belt', 'Bay 1, Line C', '{}', '2026-08-08 11:16:12.670844+05:30', '2026-08-08 11:16:12.716147+05:30', 'active', 'Line C', 'Bay 1');


--
-- Data for Name: cross_references; Type: TABLE DATA; Schema: core; Owner: postgres
--

INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('93b2696d-2553-48c0-8091-49d4d4102914', 'core', 'assets', 'M14', 'scrap', 'batches', 'BATCH1', 'processed_scrap_batch', 0.950, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('5678505f-5d87-4075-b9f1-f94effff484b', 'core', 'assets', 'M14', 'cv', 'sessions', 'SESSION_001', 'monitored_by_cv_tracking', 1.000, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('6d6daec2-dd74-4107-a477-84fda34db360', 'core', 'assets', 'M22', 'scrap', 'batches', 'BATCH2', 'stamped_scrap_batch', 0.950, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('d53f9cea-5a0f-4227-bbb1-98f6cd0e9dad', 'core', 'assets', 'M37', 'scrap', 'batches', 'BATCH5', 'transported_scrap_batch', 0.900, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('37bbe131-8727-44a3-90c7-033a37927201', 'cv', 'detections', '80d6a70f-2f9b-490c-9571-92aaee40d47e', 'core', 'expert_notes', '79229f39-869c-47e8-9a17-c053286f9fdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('fe4ea1e6-458b-4ab2-9ff5-f0bad2448ba0', 'cv', 'detections', '80d6a70f-2f9b-490c-9571-92aaee40d47e', 'core', 'expert_notes', 'd523a683-6029-4e32-a028-40f8af5cdbdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('07405af7-9c71-4a32-97d5-170367c6ce41', 'cv', 'detections', '80d6a70f-2f9b-490c-9571-92aaee40d47e', 'core', 'expert_notes', '71b83420-448f-49e4-bf53-8432c466137a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('c7a174ac-3804-4a00-9226-2413a4207d10', 'cv', 'detections', '80d6a70f-2f9b-490c-9571-92aaee40d47e', 'core', 'expert_notes', '46ddf642-7ec6-47d8-ab6a-82576ceaf555', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('acf72753-074f-434a-be2e-22fe0865d0bc', 'cv', 'detections', '80d6a70f-2f9b-490c-9571-92aaee40d47e', 'core', 'expert_notes', 'b4a820e8-bf41-4efc-8414-2b9176603314', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('42058e5c-e2d3-4203-a9c1-13bf35916533', 'cv', 'detections', '80d6a70f-2f9b-490c-9571-92aaee40d47e', 'core', 'expert_notes', '6f8183ec-501d-4e24-8dc6-bfe54556b2c4', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('a06d19e6-fca7-4144-852a-4a7080254362', 'cv', 'detections', '891dcce2-44a0-4b64-b27d-e7629d678c2e', 'core', 'expert_notes', '79229f39-869c-47e8-9a17-c053286f9fdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('067e4029-fb02-4bf0-b77d-8749d3350791', 'cv', 'detections', '891dcce2-44a0-4b64-b27d-e7629d678c2e', 'core', 'expert_notes', 'd523a683-6029-4e32-a028-40f8af5cdbdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('b9040e35-3b63-4171-9059-5696609e8136', 'cv', 'detections', '891dcce2-44a0-4b64-b27d-e7629d678c2e', 'core', 'expert_notes', '71b83420-448f-49e4-bf53-8432c466137a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('e851cdf9-cc9a-44f4-95f5-104553b8a7b3', 'cv', 'detections', '891dcce2-44a0-4b64-b27d-e7629d678c2e', 'core', 'expert_notes', '46ddf642-7ec6-47d8-ab6a-82576ceaf555', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('5bb55ba4-b5f6-49c0-9263-5b6027035c58', 'cv', 'detections', '891dcce2-44a0-4b64-b27d-e7629d678c2e', 'core', 'expert_notes', 'b4a820e8-bf41-4efc-8414-2b9176603314', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('2c4d087b-c6af-437c-8502-7e1ad1993b9e', 'cv', 'detections', '891dcce2-44a0-4b64-b27d-e7629d678c2e', 'core', 'expert_notes', '6f8183ec-501d-4e24-8dc6-bfe54556b2c4', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('d9d1b094-acaa-421c-940b-87f2b9f48a09', 'cv', 'detections', 'd61e53b7-1c92-496e-a563-6825e2fee31f', 'core', 'expert_notes', 'e6719a6b-42c4-4348-a804-4160a84ebef6', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('a17d7c36-ca07-4be9-80ae-dd4eb9196e91', 'cv', 'detections', 'd61e53b7-1c92-496e-a563-6825e2fee31f', 'core', 'expert_notes', 'f24b4744-65d1-4d8a-a170-2082dc0ed711', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('4207d8f8-a80b-469a-88ea-8f5511b2a4f8', 'cv', 'detections', 'd61e53b7-1c92-496e-a563-6825e2fee31f', 'core', 'expert_notes', '9ddf3549-3821-4e52-bf11-248109c8deff', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('6baea0da-e2b5-44fd-9b2c-8734fc8cfa48', 'cv', 'detections', 'bfa581e7-e60a-40f0-bccb-46cae71dcf3c', 'core', 'expert_notes', '96304420-23d7-4385-bf42-4f5dd61ea7e9', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('8e534e34-e80c-44e4-9958-49261cf27093', 'cv', 'detections', 'bfa581e7-e60a-40f0-bccb-46cae71dcf3c', 'core', 'expert_notes', 'd1dee645-898b-4423-b3b0-9e4457988408', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('121a0c90-8a85-4bb0-8352-37f7d0d56db3', 'cv', 'detections', 'bfa581e7-e60a-40f0-bccb-46cae71dcf3c', 'core', 'expert_notes', '502a8136-6113-4ef7-a021-ac8eb8d40f2a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('c2d1f448-1841-4082-9d60-84c254eea8b1', 'cv', 'detections', 'd7598b87-8702-4738-ab4c-80117c581c62', 'core', 'expert_notes', '79229f39-869c-47e8-9a17-c053286f9fdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('98d90747-ec7e-4d15-bbe3-562b92e4b8fc', 'cv', 'detections', 'd7598b87-8702-4738-ab4c-80117c581c62', 'core', 'expert_notes', 'd523a683-6029-4e32-a028-40f8af5cdbdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('a86f4a8a-b745-41f8-ba0a-c5c09de670bd', 'cv', 'detections', 'd7598b87-8702-4738-ab4c-80117c581c62', 'core', 'expert_notes', '71b83420-448f-49e4-bf53-8432c466137a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('901e3534-54ce-4877-b275-68a732a4cec9', 'cv', 'detections', 'd7598b87-8702-4738-ab4c-80117c581c62', 'core', 'expert_notes', '46ddf642-7ec6-47d8-ab6a-82576ceaf555', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('2ca415d6-0665-469e-8545-fdb3eadfb2c2', 'cv', 'detections', 'd7598b87-8702-4738-ab4c-80117c581c62', 'core', 'expert_notes', 'b4a820e8-bf41-4efc-8414-2b9176603314', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('1362303c-c1ca-4de6-8582-822544ce994d', 'cv', 'detections', 'd7598b87-8702-4738-ab4c-80117c581c62', 'core', 'expert_notes', '6f8183ec-501d-4e24-8dc6-bfe54556b2c4', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('fd7c77c2-f356-45db-873b-493ac23fab65', 'cv', 'detections', '4282f4b1-276f-43ab-ab00-66761f6aa3c6', 'core', 'expert_notes', '79229f39-869c-47e8-9a17-c053286f9fdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('bc9075fa-2a9b-41fd-9760-a2e36bd047da', 'cv', 'detections', '4282f4b1-276f-43ab-ab00-66761f6aa3c6', 'core', 'expert_notes', 'd523a683-6029-4e32-a028-40f8af5cdbdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('46a54285-b4bd-4e44-8592-ccca2616e615', 'cv', 'detections', '4282f4b1-276f-43ab-ab00-66761f6aa3c6', 'core', 'expert_notes', '71b83420-448f-49e4-bf53-8432c466137a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('6a7cd360-3166-440f-b802-f9fa9cf3394b', 'cv', 'detections', '4282f4b1-276f-43ab-ab00-66761f6aa3c6', 'core', 'expert_notes', '46ddf642-7ec6-47d8-ab6a-82576ceaf555', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('416db051-c546-48b1-ab4d-dec562d4e6b8', 'cv', 'detections', '4282f4b1-276f-43ab-ab00-66761f6aa3c6', 'core', 'expert_notes', 'b4a820e8-bf41-4efc-8414-2b9176603314', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('6f0b9bbc-a867-472c-93f7-94bd85e36f72', 'cv', 'detections', '4282f4b1-276f-43ab-ab00-66761f6aa3c6', 'core', 'expert_notes', '6f8183ec-501d-4e24-8dc6-bfe54556b2c4', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('6625c14e-ad15-456b-aec9-2429480b7106', 'cv', 'detections', '4c8c68ad-070b-4964-acbb-40365d3df680', 'core', 'expert_notes', 'e6719a6b-42c4-4348-a804-4160a84ebef6', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('40ff186f-dc2c-40e0-b842-cd04429094b2', 'cv', 'detections', '4c8c68ad-070b-4964-acbb-40365d3df680', 'core', 'expert_notes', 'f24b4744-65d1-4d8a-a170-2082dc0ed711', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('63abd62c-23b7-44ee-ad67-6a8758cd8c6e', 'cv', 'detections', '4c8c68ad-070b-4964-acbb-40365d3df680', 'core', 'expert_notes', '9ddf3549-3821-4e52-bf11-248109c8deff', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('6916a458-995c-4221-a712-8a2881165d32', 'cv', 'detections', '5e5c60e6-29fb-4888-a61d-4c6f9574e017', 'core', 'expert_notes', '96304420-23d7-4385-bf42-4f5dd61ea7e9', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('b8eac023-97b9-4714-805a-de699a2e47e3', 'cv', 'detections', '5e5c60e6-29fb-4888-a61d-4c6f9574e017', 'core', 'expert_notes', 'd1dee645-898b-4423-b3b0-9e4457988408', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('51cf7f7c-1917-4dd2-973a-1c3235eb1311', 'cv', 'detections', '5e5c60e6-29fb-4888-a61d-4c6f9574e017', 'core', 'expert_notes', '502a8136-6113-4ef7-a021-ac8eb8d40f2a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('5e108860-5807-4857-9ac3-8633594e72e4', 'cv', 'detections', 'dc708e2a-06cb-4de8-b369-74271e1a7327', 'core', 'expert_notes', '79229f39-869c-47e8-9a17-c053286f9fdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('592bff08-1746-443f-b894-a17cbe8795e5', 'cv', 'detections', 'dc708e2a-06cb-4de8-b369-74271e1a7327', 'core', 'expert_notes', 'd523a683-6029-4e32-a028-40f8af5cdbdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('f05c7ffa-ee54-4f20-8852-be25b4f4271f', 'cv', 'detections', 'dc708e2a-06cb-4de8-b369-74271e1a7327', 'core', 'expert_notes', '71b83420-448f-49e4-bf53-8432c466137a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('346fb5a5-24e4-4ad2-ab32-0156f2f63bc7', 'cv', 'detections', 'dc708e2a-06cb-4de8-b369-74271e1a7327', 'core', 'expert_notes', '46ddf642-7ec6-47d8-ab6a-82576ceaf555', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('6eb1baec-84ee-46c9-bd73-0d4c4b0daf27', 'cv', 'detections', 'dc708e2a-06cb-4de8-b369-74271e1a7327', 'core', 'expert_notes', 'b4a820e8-bf41-4efc-8414-2b9176603314', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('5da321ce-3a70-4b2f-a9ee-5ce725256261', 'cv', 'detections', 'dc708e2a-06cb-4de8-b369-74271e1a7327', 'core', 'expert_notes', '6f8183ec-501d-4e24-8dc6-bfe54556b2c4', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('cccd0bd9-c2e7-4a9b-b67f-30a2f5f2ec3a', 'cv', 'detections', 'b5da41b7-af63-4092-9dd9-499939e22286', 'core', 'expert_notes', '79229f39-869c-47e8-9a17-c053286f9fdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('f0e5cdad-d9f2-49fe-aad4-748f987fb70f', 'cv', 'detections', 'b5da41b7-af63-4092-9dd9-499939e22286', 'core', 'expert_notes', 'd523a683-6029-4e32-a028-40f8af5cdbdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('6acc5f2d-e625-49eb-abc7-82a3d8a6baa3', 'cv', 'detections', 'b5da41b7-af63-4092-9dd9-499939e22286', 'core', 'expert_notes', '71b83420-448f-49e4-bf53-8432c466137a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('ce5c3bba-9421-4c4b-9556-d565397b2ca8', 'cv', 'detections', 'b5da41b7-af63-4092-9dd9-499939e22286', 'core', 'expert_notes', '46ddf642-7ec6-47d8-ab6a-82576ceaf555', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('45435cb2-29ac-489b-b070-d25e8c0ea1ba', 'cv', 'detections', 'b5da41b7-af63-4092-9dd9-499939e22286', 'core', 'expert_notes', 'b4a820e8-bf41-4efc-8414-2b9176603314', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('7153e214-a289-410a-be7d-387b14f745de', 'cv', 'detections', 'b5da41b7-af63-4092-9dd9-499939e22286', 'core', 'expert_notes', '6f8183ec-501d-4e24-8dc6-bfe54556b2c4', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('b8029488-ad06-4c15-9ebe-9e1e9bd670e9', 'cv', 'detections', 'f5785b28-ed0b-4d47-8299-15c82f06fe07', 'core', 'expert_notes', 'e6719a6b-42c4-4348-a804-4160a84ebef6', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('56ad45da-b852-4dc5-954d-e5bdb4b960a1', 'cv', 'detections', 'f5785b28-ed0b-4d47-8299-15c82f06fe07', 'core', 'expert_notes', 'f24b4744-65d1-4d8a-a170-2082dc0ed711', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('96f3f027-c4d3-4402-98cc-d3c67c60f58a', 'cv', 'detections', 'f5785b28-ed0b-4d47-8299-15c82f06fe07', 'core', 'expert_notes', '9ddf3549-3821-4e52-bf11-248109c8deff', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('7e31c049-a31f-4f2c-895f-1fe3adf03a65', 'cv', 'detections', '34d80367-24ab-43d2-894a-e8ab79e00c20', 'core', 'expert_notes', '96304420-23d7-4385-bf42-4f5dd61ea7e9', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('11e05662-b1d1-4a19-bd85-6e65b08675fb', 'cv', 'detections', '34d80367-24ab-43d2-894a-e8ab79e00c20', 'core', 'expert_notes', 'd1dee645-898b-4423-b3b0-9e4457988408', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('9f359b8b-90aa-46a2-b00f-aba930bd5f6f', 'cv', 'detections', '34d80367-24ab-43d2-894a-e8ab79e00c20', 'core', 'expert_notes', '502a8136-6113-4ef7-a021-ac8eb8d40f2a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('e8f0b990-7d3a-41e3-bc47-ff7e16e0dfa8', 'cv', 'detections', '6f7baeff-f0f1-40a0-b3d7-e88307420671', 'core', 'expert_notes', '79229f39-869c-47e8-9a17-c053286f9fdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('e3146fa7-8f06-4394-87af-6f99a09830ed', 'cv', 'detections', '6f7baeff-f0f1-40a0-b3d7-e88307420671', 'core', 'expert_notes', 'd523a683-6029-4e32-a028-40f8af5cdbdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('08383d33-49c3-4957-ac0a-7fa9bfea872d', 'cv', 'detections', '6f7baeff-f0f1-40a0-b3d7-e88307420671', 'core', 'expert_notes', '71b83420-448f-49e4-bf53-8432c466137a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('85ac9a70-0341-4f09-8837-fae693d43b26', 'cv', 'detections', '6f7baeff-f0f1-40a0-b3d7-e88307420671', 'core', 'expert_notes', '46ddf642-7ec6-47d8-ab6a-82576ceaf555', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('4117ab29-ee57-43a7-a275-b64a8fc9f253', 'cv', 'detections', '6f7baeff-f0f1-40a0-b3d7-e88307420671', 'core', 'expert_notes', 'b4a820e8-bf41-4efc-8414-2b9176603314', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('f7438cfa-c7d4-4948-ac80-15103baac227', 'cv', 'detections', '6f7baeff-f0f1-40a0-b3d7-e88307420671', 'core', 'expert_notes', '6f8183ec-501d-4e24-8dc6-bfe54556b2c4', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('befe0870-f2b5-46bf-bec8-c7e651796a39', 'cv', 'detections', 'af1ce777-c0f6-4a9b-b164-d3fe7a11ae73', 'core', 'expert_notes', '79229f39-869c-47e8-9a17-c053286f9fdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('fabda7ff-9335-47a1-b73a-9b12f54274b9', 'cv', 'detections', 'af1ce777-c0f6-4a9b-b164-d3fe7a11ae73', 'core', 'expert_notes', 'd523a683-6029-4e32-a028-40f8af5cdbdd', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('ad6ad0a3-083d-4be7-b3e5-d39b1edb4553', 'cv', 'detections', 'af1ce777-c0f6-4a9b-b164-d3fe7a11ae73', 'core', 'expert_notes', '71b83420-448f-49e4-bf53-8432c466137a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('1b6b2909-08ce-4a86-bc36-d82fd0ddc94d', 'cv', 'detections', 'af1ce777-c0f6-4a9b-b164-d3fe7a11ae73', 'core', 'expert_notes', '46ddf642-7ec6-47d8-ab6a-82576ceaf555', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('f03c18ae-d7cd-43d5-97b4-fc0d544b4cf7', 'cv', 'detections', 'af1ce777-c0f6-4a9b-b164-d3fe7a11ae73', 'core', 'expert_notes', 'b4a820e8-bf41-4efc-8414-2b9176603314', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('9e7c1f7b-c5c7-42b8-99f0-36503050aa06', 'cv', 'detections', 'af1ce777-c0f6-4a9b-b164-d3fe7a11ae73', 'core', 'expert_notes', '6f8183ec-501d-4e24-8dc6-bfe54556b2c4', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('342c31ff-30dd-4fb6-bd10-c89e6a1c17c5', 'cv', 'detections', 'c419ddaa-b691-40a2-afff-d3203b20ca5e', 'core', 'expert_notes', 'e6719a6b-42c4-4348-a804-4160a84ebef6', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('600295aa-8f43-4b6e-9680-706bd522853f', 'cv', 'detections', 'c419ddaa-b691-40a2-afff-d3203b20ca5e', 'core', 'expert_notes', 'f24b4744-65d1-4d8a-a170-2082dc0ed711', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('5fb3e148-960f-42ef-b708-0d49efbb1646', 'cv', 'detections', 'c419ddaa-b691-40a2-afff-d3203b20ca5e', 'core', 'expert_notes', '9ddf3549-3821-4e52-bf11-248109c8deff', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('b4911853-f1af-4a7a-9c7e-c6b808de291f', 'cv', 'detections', '298d542a-1919-4912-ae79-a339ff4ef4fc', 'core', 'expert_notes', '96304420-23d7-4385-bf42-4f5dd61ea7e9', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('f9f72389-9564-4c97-bacf-430a9b145e6e', 'cv', 'detections', '298d542a-1919-4912-ae79-a339ff4ef4fc', 'core', 'expert_notes', 'd1dee645-898b-4423-b3b0-9e4457988408', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');
INSERT INTO core.cross_references (ref_id, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type, confidence, created_by, created_at) VALUES ('3c25cf8a-2337-405a-ab0d-3c2f78ed4ea6', 'cv', 'detections', '298d542a-1919-4912-ae79-a339ff4ef4fc', 'core', 'expert_notes', '502a8136-6113-4ef7-a021-ac8eb8d40f2a', 'annotated_by_expert_note', 0.980, 'knowledge_correlator', '2026-08-08 11:16:12.716839+05:30');


--
-- Data for Name: expert_notes; Type: TABLE DATA; Schema: core; Owner: postgres
--

INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('79229f39-869c-47e8-9a17-c053286f9fdd', 'M14', 'Bearing replacement scheduled for next maintenance window.', 'Priya Sharma', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('d523a683-6029-4e32-a028-40f8af5cdbdd', 'M14', 'Crack on spindle housing flagged — monitor closely.', 'Arjun Mehta', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('e6719a6b-42c4-4348-a804-4160a84ebef6', 'M22', 'Hydraulic fluid topped up. Pressure drop persists — investigate cylinder seal.', 'Priya Sharma', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('96304420-23d7-4385-bf42-4f5dd61ea7e9', 'M37', 'Drive motor thermal trip recorded twice this week. Priority review.', 'Ravi Kumar', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('71b83420-448f-49e4-bf53-8432c466137a', 'M14', 'Bearing replacement scheduled for next maintenance window.', 'Priya Sharma', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('46ddf642-7ec6-47d8-ab6a-82576ceaf555', 'M14', 'Crack on spindle housing flagged — monitor closely.', 'Arjun Mehta', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('f24b4744-65d1-4d8a-a170-2082dc0ed711', 'M22', 'Hydraulic fluid topped up. Pressure drop persists — investigate cylinder seal.', 'Priya Sharma', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('d1dee645-898b-4423-b3b0-9e4457988408', 'M37', 'Drive motor thermal trip recorded twice this week. Priority review.', 'Ravi Kumar', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('b4a820e8-bf41-4efc-8414-2b9176603314', 'M14', 'Bearing replacement scheduled for next maintenance window.', '+919876543210', '2026-08-08 11:16:12.686151+05:30');
INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('6f8183ec-501d-4e24-8dc6-bfe54556b2c4', 'M14', 'Crack on spindle housing flagged — monitor closely.', '+919876543211', '2026-08-08 11:16:12.686151+05:30');
INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('9ddf3549-3821-4e52-bf11-248109c8deff', 'M22', 'Hydraulic fluid topped up. Pressure drop persists — investigate cylinder seal.', '+919876543210', '2026-08-08 11:16:12.686151+05:30');
INSERT INTO core.expert_notes (note_id, asset_id, comment, author, "timestamp") VALUES ('502a8136-6113-4ef7-a021-ac8eb8d40f2a', 'M37', 'Drive motor thermal trip recorded twice this week. Priority review.', '+919876543212', '2026-08-08 11:16:12.686151+05:30');


--
-- Data for Name: insights; Type: TABLE DATA; Schema: core; Owner: postgres
--



--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: core; Owner: postgres
--

INSERT INTO core.schema_migrations (version, applied_at) VALUES ('002_cross_schema_integration', '2026-08-08 11:16:12.645806+05:30');
INSERT INTO core.schema_migrations (version, applied_at) VALUES ('003_add_status_column', '2026-08-08 11:16:12.667633+05:30');
INSERT INTO core.schema_migrations (version, applied_at) VALUES ('db_build_v2_processed_sync', '2026-08-08 11:16:12.741838+05:30');


--
-- Data for Name: detections; Type: TABLE DATA; Schema: cv; Owner: postgres
--

INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('ab726757-c12d-4aaf-9c17-2e2f7142c6c0', 'M14', 'Track 1 — board', 'Category:furniture | Area:12750.5px² | Angle:-3.4° | Frame:240 | BBox:[284, 91, 137, 113] | Centroid:[350, 147]', 1.000, 'cv_tracking', '2026-06-04 15:37:42.628+05:30', '{"area": 12750.5, "bbox": [284, 91, 137, 113], "angle": -3.4, "label": "board", "notes": "", "category": "furniture", "centroid": [350, 147], "frame_id": 240, "saved_at": "2026-06-04T10:07:42.628Z", "track_id": 1, "class_name": "tv"}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('dee3a0f5-96fd-4de5-b93b-bcd4e80ceadc', 'M14', 'Track 23 — chair', 'Category:unknown | Area:2625px² | Angle:-89.5° | Frame:200 | BBox:[514, 190, 37, 121] | Centroid:[531, 240]', 1.000, 'cv_tracking', '2026-06-04 15:00:29.609+05:30', '{"area": 2625, "bbox": [514, 190, 37, 121], "angle": -89.5, "label": "", "notes": "", "category": "unknown", "centroid": [531, 240], "frame_id": 200, "saved_at": "2026-06-04T09:30:29.609Z", "track_id": 23, "class_name": "chair"}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('ac97eb93-7ae0-41a4-89fc-58fb303f3eda', 'BATCH1', 'square_1 (square)', 'Area:11.15cm² | Sides:AB:2.87cm, BC:3.31cm, CD:2.88cm, DA:3.41cm | Vertices:A:[185, 367], B:[183, 394], C:[214, 398], D:[217, 371]', 1.000, 'cv_batch', NULL, '{"id": 1, "area_cm2": 11.15, "piece_name": "square_1", "shape_type": "square", "vertex_labels": {"A": [185, 367], "B": [183, 394], "C": [214, 398], "D": [217, 371]}, "vertices_count": 4, "side_lengths_cm": {"AB": 2.87, "BC": 3.31, "CD": 2.88, "DA": 3.41}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('fb5e0e2d-5154-431a-9485-7dc4b470f4ad', 'BATCH1', 'rectangle_1 (rectangle)', 'Area:40.53cm² | Sides:AB:7.32cm, BC:5.31cm, CD:7.31cm, DA:5.2cm | Vertices:A:[351, 220], B:[347, 289], C:[397, 293], D:[400, 224]', 1.000, 'cv_batch', NULL, '{"id": 2, "area_cm2": 40.53, "piece_name": "rectangle_1", "shape_type": "rectangle", "vertex_labels": {"A": [351, 220], "B": [347, 289], "C": [397, 293], "D": [400, 224]}, "vertices_count": 4, "side_lengths_cm": {"AB": 7.32, "BC": 5.31, "CD": 7.31, "DA": 5.2}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('9cb5de83-89e6-4dc9-ac91-251cbcc40c9e', 'BATCH1', 'triangle_1 (triangle)', 'Area:36.95cm² | Sides:AB:5.55cm, BC:11.15cm, CA:12.55cm | Vertices:A:[268, 251], B:[256, 200], C:[153, 222]', 1.000, 'cv_batch', NULL, '{"id": 3, "area_cm2": 36.95, "piece_name": "triangle_1", "shape_type": "triangle", "vertex_labels": {"A": [268, 251], "B": [256, 200], "C": [153, 222]}, "vertices_count": 3, "side_lengths_cm": {"AB": 5.55, "BC": 11.15, "CA": 12.55}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('84279c09-3693-4d9b-a67d-29b61c9177d1', 'BATCH2', 'irregular_1 (irregular)', 'Area:25.18cm² | Sides:AB:1.7cm, BC:4.75cm, CD:5.62cm, DE:1.62cm, EF:7.59cm, FA:7.05cm | Vertices:A:[131, 335], B:[128, 351], C:[172, 363], D:[162, 416]', 1.000, 'cv_batch', NULL, '{"id": 1, "area_cm2": 25.18, "piece_name": "irregular_1", "shape_type": "irregular", "vertex_labels": {"A": [131, 335], "B": [128, 351], "C": [172, 363], "D": [162, 416], "E": [177, 420], "F": [197, 350]}, "vertices_count": 6, "side_lengths_cm": {"AB": 1.7, "BC": 4.75, "CD": 5.62, "DE": 1.62, "EF": 7.59, "FA": 7.05}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('5316ed2b-504a-41ff-8fd9-8c28ac4c8541', 'BATCH2', 'irregular_2 (irregular)', 'Area:33.7cm² | Sides:AB:2.54cm, BC:2.73cm, CD:3.02cm, DE:2.3cm, EF:2.58cm, FG:2.41cm, GH:2.0cm, HA:2.91cm | Vertices:A:[384, 322], B:[364, 336], C:[361, 362], D:[381, 383]', 1.000, 'cv_batch', NULL, '{"id": 2, "area_cm2": 33.7, "piece_name": "irregular_2", "shape_type": "irregular", "vertex_labels": {"A": [384, 322], "B": [364, 336], "C": [361, 362], "D": [381, 383], "E": [403, 384], "F": [421, 367], "G": [423, 344], "H": [411, 329]}, "vertices_count": 8, "side_lengths_cm": {"AB": 2.54, "BC": 2.73, "CD": 3.02, "DE": 2.3, "EF": 2.58, "FG": 2.41, "GH": 2.0, "HA": 2.91}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('31aa0b2e-c602-466a-babe-8b672b4093a7', 'BATCH2', 'circle_1 (circle)', 'Area:8.87cm² | Sides:AB:1.65cm, BC:0.84cm, CD:1.15cm, DE:1.7cm, EF:1.42cm, FG:2.41cm, GA:1.5cm | Vertices:A:[268, 300], B:[253, 305], C:[249, 312], D:[248, 323]', 1.000, 'cv_batch', NULL, '{"id": 3, "area_cm2": 8.87, "piece_name": "circle_1", "shape_type": "circle", "vertex_labels": {"A": [268, 300], "B": [253, 305], "C": [249, 312], "D": [248, 323], "E": [260, 334], "F": [273, 330], "G": [280, 308]}, "vertices_count": 7, "side_lengths_cm": {"AB": 1.65, "BC": 0.84, "CD": 1.15, "DE": 1.7, "EF": 1.42, "FG": 2.41, "GA": 1.5}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('8734e81e-39b6-4f94-ba8c-e4bb74f2c73d', 'BATCH2', 'irregular_3 (irregular)', 'Area:11.12cm² | Sides:AB:1.97cm, BC:0.63cm, CD:5.1cm, DE:3.25cm, EA:3.03cm | Vertices:A:[144, 220], B:[128, 230], C:[128, 236], D:[160, 273]', 1.000, 'cv_batch', NULL, '{"id": 4, "area_cm2": 11.12, "piece_name": "irregular_3", "shape_type": "irregular", "vertex_labels": {"A": [144, 220], "B": [128, 230], "C": [128, 236], "D": [160, 273], "E": [163, 242]}, "vertices_count": 5, "side_lengths_cm": {"AB": 1.97, "BC": 0.63, "CD": 5.1, "DE": 3.25, "EA": 3.03}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('68043665-9083-46c5-9e74-5b91c412ff12', 'BATCH2', 'irregular_4 (irregular)', 'Area:31.36cm² | Sides:AB:4.91cm, BC:6.46cm, CD:5.79cm, DE:3.31cm, EF:1.59cm, FA:2.43cm | Vertices:A:[311, 212], B:[301, 258], C:[362, 269], D:[370, 214]', 1.000, 'cv_batch', NULL, '{"id": 5, "area_cm2": 31.36, "piece_name": "irregular_4", "shape_type": "irregular", "vertex_labels": {"A": [311, 212], "B": [301, 258], "C": [362, 269], "D": [370, 214], "E": [342, 229], "F": [334, 216]}, "vertices_count": 6, "side_lengths_cm": {"AB": 4.91, "BC": 6.46, "CD": 5.79, "DE": 3.31, "EF": 1.59, "FA": 2.43}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('80d6a70f-2f9b-490c-9571-92aaee40d47e', 'M14', 'Bearing', 'Wear detected', 0.920, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Bearing", "condition": "Wear detected", "confidence": 0.92}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('891dcce2-44a0-4b64-b27d-e7629d678c2e', 'M14', 'Spindle housing', 'Hairline crack', 0.870, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Spindle housing", "condition": "Hairline crack", "confidence": 0.87}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('b31a38af-3272-4e1c-9b05-e3a1ebc0c1d5', 'M14', 'Oil seal', 'Minor leak', 0.740, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Oil seal", "condition": "Minor leak", "confidence": 0.74}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('d61e53b7-1c92-496e-a563-6825e2fee31f', 'M22', 'Hydraulic cylinder', 'Pressure drop', 0.890, 'cv_module', '2024-12-02 16:45:00+05:30', '{"object": "Hydraulic cylinder", "condition": "Pressure drop", "confidence": 0.89}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('cd999ebb-0717-46ca-a707-07e48c518f99', 'M22', 'Piston rod', 'Surface corrosion', 0.810, 'cv_module', '2024-12-02 16:45:00+05:30', '{"object": "Piston rod", "condition": "Surface corrosion", "confidence": 0.81}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('430aec5a-f5b7-4261-acb6-32f43fe619b5', 'M37', 'Belt tension roller', 'Misalignment', 0.660, 'cv_module', '2024-12-03 14:30:00+05:30', '{"object": "Belt tension roller", "condition": "Misalignment", "confidence": 0.66}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('bfa581e7-e60a-40f0-bccb-46cae71dcf3c', 'M37', 'Drive motor', 'Overheating', 0.910, 'cv_module', '2024-12-03 14:30:00+05:30', '{"object": "Drive motor", "condition": "Overheating", "confidence": 0.91}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('c4a72c92-38b6-4728-a0cb-d75cfc6b2490', 'M14', 'Track 1 — board', 'Category:furniture | Area:12750.5px² | Angle:-3.4° | Frame:240 | BBox:[284, 91, 137, 113] | Centroid:[350, 147]', 1.000, 'cv_tracking', '2026-06-04 15:37:42.628+05:30', '{"area": 12750.5, "bbox": [284, 91, 137, 113], "angle": -3.4, "label": "board", "notes": "", "category": "furniture", "centroid": [350, 147], "frame_id": 240, "saved_at": "2026-06-04T10:07:42.628Z", "track_id": 1, "class_name": "tv"}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('b888d2b6-8dc4-4ce3-878c-97a02cd4c713', 'M14', 'Track 23 — chair', 'Category:unknown | Area:2625px² | Angle:-89.5° | Frame:200 | BBox:[514, 190, 37, 121] | Centroid:[531, 240]', 1.000, 'cv_tracking', '2026-06-04 15:00:29.609+05:30', '{"area": 2625, "bbox": [514, 190, 37, 121], "angle": -89.5, "label": "", "notes": "", "category": "unknown", "centroid": [531, 240], "frame_id": 200, "saved_at": "2026-06-04T09:30:29.609Z", "track_id": 23, "class_name": "chair"}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('1b12c1f9-ad08-47ea-b00a-611f8f26171c', 'BATCH1', 'square_1 (square)', 'Area:11.15cm² | Sides:AB:2.87cm, BC:3.31cm, CD:2.88cm, DA:3.41cm | Vertices:A:[185, 367], B:[183, 394], C:[214, 398], D:[217, 371]', 1.000, 'cv_batch', NULL, '{"id": 1, "area_cm2": 11.15, "piece_name": "square_1", "shape_type": "square", "vertex_labels": {"A": [185, 367], "B": [183, 394], "C": [214, 398], "D": [217, 371]}, "vertices_count": 4, "side_lengths_cm": {"AB": 2.87, "BC": 3.31, "CD": 2.88, "DA": 3.41}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('f7c95587-98ec-4b21-bfe6-e910a1748858', 'BATCH1', 'rectangle_1 (rectangle)', 'Area:40.53cm² | Sides:AB:7.32cm, BC:5.31cm, CD:7.31cm, DA:5.2cm | Vertices:A:[351, 220], B:[347, 289], C:[397, 293], D:[400, 224]', 1.000, 'cv_batch', NULL, '{"id": 2, "area_cm2": 40.53, "piece_name": "rectangle_1", "shape_type": "rectangle", "vertex_labels": {"A": [351, 220], "B": [347, 289], "C": [397, 293], "D": [400, 224]}, "vertices_count": 4, "side_lengths_cm": {"AB": 7.32, "BC": 5.31, "CD": 7.31, "DA": 5.2}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('74762ae5-e09b-4450-9b0c-154935a3a3b9', 'BATCH1', 'triangle_1 (triangle)', 'Area:36.95cm² | Sides:AB:5.55cm, BC:11.15cm, CA:12.55cm | Vertices:A:[268, 251], B:[256, 200], C:[153, 222]', 1.000, 'cv_batch', NULL, '{"id": 3, "area_cm2": 36.95, "piece_name": "triangle_1", "shape_type": "triangle", "vertex_labels": {"A": [268, 251], "B": [256, 200], "C": [153, 222]}, "vertices_count": 3, "side_lengths_cm": {"AB": 5.55, "BC": 11.15, "CA": 12.55}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('65428251-a2a9-4975-8809-be96380eab0c', 'BATCH2', 'irregular_1 (irregular)', 'Area:25.18cm² | Sides:AB:1.7cm, BC:4.75cm, CD:5.62cm, DE:1.62cm, EF:7.59cm, FA:7.05cm | Vertices:A:[131, 335], B:[128, 351], C:[172, 363], D:[162, 416]', 1.000, 'cv_batch', NULL, '{"id": 1, "area_cm2": 25.18, "piece_name": "irregular_1", "shape_type": "irregular", "vertex_labels": {"A": [131, 335], "B": [128, 351], "C": [172, 363], "D": [162, 416], "E": [177, 420], "F": [197, 350]}, "vertices_count": 6, "side_lengths_cm": {"AB": 1.7, "BC": 4.75, "CD": 5.62, "DE": 1.62, "EF": 7.59, "FA": 7.05}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('4333065f-1225-4582-8aff-74c95864d673', 'BATCH2', 'irregular_2 (irregular)', 'Area:33.7cm² | Sides:AB:2.54cm, BC:2.73cm, CD:3.02cm, DE:2.3cm, EF:2.58cm, FG:2.41cm, GH:2.0cm, HA:2.91cm | Vertices:A:[384, 322], B:[364, 336], C:[361, 362], D:[381, 383]', 1.000, 'cv_batch', NULL, '{"id": 2, "area_cm2": 33.7, "piece_name": "irregular_2", "shape_type": "irregular", "vertex_labels": {"A": [384, 322], "B": [364, 336], "C": [361, 362], "D": [381, 383], "E": [403, 384], "F": [421, 367], "G": [423, 344], "H": [411, 329]}, "vertices_count": 8, "side_lengths_cm": {"AB": 2.54, "BC": 2.73, "CD": 3.02, "DE": 2.3, "EF": 2.58, "FG": 2.41, "GH": 2.0, "HA": 2.91}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('0905379a-b664-4aab-bc02-47c426aaf168', 'BATCH2', 'circle_1 (circle)', 'Area:8.87cm² | Sides:AB:1.65cm, BC:0.84cm, CD:1.15cm, DE:1.7cm, EF:1.42cm, FG:2.41cm, GA:1.5cm | Vertices:A:[268, 300], B:[253, 305], C:[249, 312], D:[248, 323]', 1.000, 'cv_batch', NULL, '{"id": 3, "area_cm2": 8.87, "piece_name": "circle_1", "shape_type": "circle", "vertex_labels": {"A": [268, 300], "B": [253, 305], "C": [249, 312], "D": [248, 323], "E": [260, 334], "F": [273, 330], "G": [280, 308]}, "vertices_count": 7, "side_lengths_cm": {"AB": 1.65, "BC": 0.84, "CD": 1.15, "DE": 1.7, "EF": 1.42, "FG": 2.41, "GA": 1.5}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('d7ca80eb-6843-4ce9-9ae5-a2bb009f414f', 'BATCH2', 'irregular_3 (irregular)', 'Area:11.12cm² | Sides:AB:1.97cm, BC:0.63cm, CD:5.1cm, DE:3.25cm, EA:3.03cm | Vertices:A:[144, 220], B:[128, 230], C:[128, 236], D:[160, 273]', 1.000, 'cv_batch', NULL, '{"id": 4, "area_cm2": 11.12, "piece_name": "irregular_3", "shape_type": "irregular", "vertex_labels": {"A": [144, 220], "B": [128, 230], "C": [128, 236], "D": [160, 273], "E": [163, 242]}, "vertices_count": 5, "side_lengths_cm": {"AB": 1.97, "BC": 0.63, "CD": 5.1, "DE": 3.25, "EA": 3.03}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('85d03c0d-7450-4dc0-8bb2-e5e963d0a6a5', 'BATCH2', 'irregular_4 (irregular)', 'Area:31.36cm² | Sides:AB:4.91cm, BC:6.46cm, CD:5.79cm, DE:3.31cm, EF:1.59cm, FA:2.43cm | Vertices:A:[311, 212], B:[301, 258], C:[362, 269], D:[370, 214]', 1.000, 'cv_batch', NULL, '{"id": 5, "area_cm2": 31.36, "piece_name": "irregular_4", "shape_type": "irregular", "vertex_labels": {"A": [311, 212], "B": [301, 258], "C": [362, 269], "D": [370, 214], "E": [342, 229], "F": [334, 216]}, "vertices_count": 6, "side_lengths_cm": {"AB": 4.91, "BC": 6.46, "CD": 5.79, "DE": 3.31, "EF": 1.59, "FA": 2.43}}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('d7598b87-8702-4738-ab4c-80117c581c62', 'M14', 'Bearing', 'Wear detected', 0.920, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Bearing", "condition": "Wear detected", "confidence": 0.92}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('4282f4b1-276f-43ab-ab00-66761f6aa3c6', 'M14', 'Spindle housing', 'Hairline crack', 0.870, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Spindle housing", "condition": "Hairline crack", "confidence": 0.87}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('5dfdfb29-e973-41b0-9550-02a1286ca270', 'M14', 'Oil seal', 'Minor leak', 0.740, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Oil seal", "condition": "Minor leak", "confidence": 0.74}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('4c8c68ad-070b-4964-acbb-40365d3df680', 'M22', 'Hydraulic cylinder', 'Pressure drop', 0.890, 'cv_module', '2024-12-02 16:45:00+05:30', '{"object": "Hydraulic cylinder", "condition": "Pressure drop", "confidence": 0.89}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('823f7ef5-2900-4609-9d2a-2874b0546b4a', 'M22', 'Piston rod', 'Surface corrosion', 0.810, 'cv_module', '2024-12-02 16:45:00+05:30', '{"object": "Piston rod", "condition": "Surface corrosion", "confidence": 0.81}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('53be0c9f-47e7-4891-806d-c177caaf30d8', 'M37', 'Belt tension roller', 'Misalignment', 0.660, 'cv_module', '2024-12-03 14:30:00+05:30', '{"object": "Belt tension roller", "condition": "Misalignment", "confidence": 0.66}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('5e5c60e6-29fb-4888-a61d-4c6f9574e017', 'M37', 'Drive motor', 'Overheating', 0.910, 'cv_module', '2024-12-03 14:30:00+05:30', '{"object": "Drive motor", "condition": "Overheating", "confidence": 0.91}', '2026-08-08 11:16:12.676374+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('dc708e2a-06cb-4de8-b369-74271e1a7327', 'M14', 'Bearing', 'Wear detected', 0.920, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Bearing", "condition": "Wear detected", "confidence": 0.92}', '2026-08-08 11:16:12.68695+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('b5da41b7-af63-4092-9dd9-499939e22286', 'M14', 'Spindle housing', 'Hairline crack', 0.870, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Spindle housing", "condition": "Hairline crack", "confidence": 0.87}', '2026-08-08 11:16:12.68695+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('64e74878-3357-4b45-bc83-f691fefd2880', 'M14', 'Oil seal', 'Minor leak', 0.740, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Oil seal", "condition": "Minor leak", "confidence": 0.74}', '2026-08-08 11:16:12.68695+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('f5785b28-ed0b-4d47-8299-15c82f06fe07', 'M22', 'Hydraulic cylinder', 'Pressure drop', 0.890, 'cv_module', '2024-12-02 16:45:00+05:30', '{"object": "Hydraulic cylinder", "condition": "Pressure drop", "confidence": 0.89}', '2026-08-08 11:16:12.68695+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('1c33ac63-7c37-4532-8a9a-c2f541ccec59', 'M22', 'Piston rod', 'Surface corrosion', 0.810, 'cv_module', '2024-12-02 16:45:00+05:30', '{"object": "Piston rod", "condition": "Surface corrosion", "confidence": 0.81}', '2026-08-08 11:16:12.68695+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('7283a994-fbd5-4d61-b37a-6e96655fbf93', 'M37', 'Belt tension roller', 'Misalignment', 0.660, 'cv_module', '2024-12-03 14:30:00+05:30', '{"object": "Belt tension roller", "condition": "Misalignment", "confidence": 0.66}', '2026-08-08 11:16:12.68695+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('34d80367-24ab-43d2-894a-e8ab79e00c20', 'M37', 'Drive motor', 'Overheating', 0.910, 'cv_module', '2024-12-03 14:30:00+05:30', '{"object": "Drive motor", "condition": "Overheating", "confidence": 0.91}', '2026-08-08 11:16:12.68695+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('6f7baeff-f0f1-40a0-b3d7-e88307420671', 'M14', 'Bearing', 'Wear detected', 0.920, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Bearing", "condition": "Wear detected", "confidence": 0.92}', '2026-08-08 11:16:12.714233+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('af1ce777-c0f6-4a9b-b164-d3fe7a11ae73', 'M14', 'Spindle housing', 'Hairline crack', 0.870, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Spindle housing", "condition": "Hairline crack", "confidence": 0.87}', '2026-08-08 11:16:12.714233+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('b4ad2fb4-4555-4674-a13e-7851a551ec27', 'M14', 'Oil seal', 'Minor leak', 0.740, 'cv_module', '2024-12-01 14:00:00+05:30', '{"object": "Oil seal", "condition": "Minor leak", "confidence": 0.74}', '2026-08-08 11:16:12.714233+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('c419ddaa-b691-40a2-afff-d3203b20ca5e', 'M22', 'Hydraulic cylinder', 'Pressure drop', 0.890, 'cv_module', '2024-12-02 16:45:00+05:30', '{"object": "Hydraulic cylinder", "condition": "Pressure drop", "confidence": 0.89}', '2026-08-08 11:16:12.715484+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('6749acc2-a6c3-4f69-9b60-0590ff5f6475', 'M22', 'Piston rod', 'Surface corrosion', 0.810, 'cv_module', '2024-12-02 16:45:00+05:30', '{"object": "Piston rod", "condition": "Surface corrosion", "confidence": 0.81}', '2026-08-08 11:16:12.715484+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('578a7986-3b69-4e2b-bb31-167151c62e94', 'M37', 'Belt tension roller', 'Misalignment', 0.660, 'cv_module', '2024-12-03 14:30:00+05:30', '{"object": "Belt tension roller", "condition": "Misalignment", "confidence": 0.66}', '2026-08-08 11:16:12.716147+05:30');
INSERT INTO cv.detections (detection_id, asset_id, object, condition, confidence, source, "timestamp", raw_json, created_at) VALUES ('298d542a-1919-4912-ae79-a339ff4ef4fc', 'M37', 'Drive motor', 'Overheating', 0.910, 'cv_module', '2024-12-03 14:30:00+05:30', '{"object": "Drive motor", "condition": "Overheating", "confidence": 0.91}', '2026-08-08 11:16:12.716147+05:30');


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: cv; Owner: postgres
--

INSERT INTO cv.sessions (session_id, asset_id, source, started_at, created_at) VALUES ('M14', 'M14', 'cv_tracking', NULL, '2026-08-08 11:16:12.688683+05:30');


--
-- Data for Name: tracks; Type: TABLE DATA; Schema: cv; Owner: postgres
--

INSERT INTO cv.tracks (track_pk, track_id, session_id, asset_id, label, category, class_name, frame_id, area, bbox, centroid, angle, notes, saved_at, created_at) VALUES ('f3f0d3c3-4648-4661-a44b-2f4a534ee796', 1, 'M14', 'M14', 'board', 'furniture', 'tv', 240, 12750.5, '[284, 91, 137, 113]', '[350, 147]', -3.4, '', '2026-06-04 15:37:42.628+05:30', '2026-08-08 11:16:12.688683+05:30');
INSERT INTO cv.tracks (track_pk, track_id, session_id, asset_id, label, category, class_name, frame_id, area, bbox, centroid, angle, notes, saved_at, created_at) VALUES ('2207d85c-8123-4ba4-931a-f919a38dbfed', 23, 'M14', 'M14', '', 'unknown', 'chair', 200, 2625, '[514, 190, 37, 121]', '[531, 240]', -89.5, '', '2026-06-04 15:00:29.609+05:30', '2026-08-08 11:16:12.688683+05:30');
INSERT INTO cv.tracks (track_pk, track_id, session_id, asset_id, label, category, class_name, frame_id, area, bbox, centroid, angle, notes, saved_at, created_at) VALUES ('23c92509-e766-4167-9f72-e57eb460351a', 1, 'M14', 'M14', 'board', 'furniture', 'tv', 240, 12750.5, '[284, 91, 137, 113]', '[350, 147]', -3.4, '', '2026-06-04 15:37:42.628+05:30', '2026-08-08 11:16:12.690678+05:30');
INSERT INTO cv.tracks (track_pk, track_id, session_id, asset_id, label, category, class_name, frame_id, area, bbox, centroid, angle, notes, saved_at, created_at) VALUES ('ccc33463-fbcf-45ed-a796-9e6b273b510e', 23, 'M14', 'M14', '', 'unknown', 'chair', 200, 2625, '[514, 190, 37, 121]', '[531, 240]', -89.5, '', '2026-06-04 15:00:29.609+05:30', '2026-08-08 11:16:12.690678+05:30');


--
-- Data for Name: elements; Type: TABLE DATA; Schema: geometry; Owner: postgres
--



--
-- Data for Name: semantic_tags; Type: TABLE DATA; Schema: geometry; Owner: postgres
--



--
-- Data for Name: shapes; Type: TABLE DATA; Schema: geometry; Owner: postgres
--



--
-- Data for Name: files; Type: TABLE DATA; Schema: ingest; Owner: postgres
--



--
-- Data for Name: chunks; Type: TABLE DATA; Schema: rag; Owner: postgres
--



--
-- Data for Name: documents; Type: TABLE DATA; Schema: rag; Owner: postgres
--



--
-- Data for Name: batch_images; Type: TABLE DATA; Schema: scrap; Owner: postgres
--



--
-- Data for Name: batches; Type: TABLE DATA; Schema: scrap; Owner: postgres
--

INSERT INTO scrap.batches (batch_id, asset_id, batch_number, cm_per_pixel, total_scraps, created_at) VALUES ('BATCH1', 'BATCH1', 1, 0.0903679068873131, 3, '2026-08-08 11:16:12.691858+05:30');
INSERT INTO scrap.batches (batch_id, asset_id, batch_number, cm_per_pixel, total_scraps, created_at) VALUES ('BATCH2', 'BATCH2', 2, 0.0824561403508772, 3, '2026-08-08 11:16:12.700138+05:30');
INSERT INTO scrap.batches (batch_id, asset_id, batch_number, cm_per_pixel, total_scraps, created_at) VALUES ('BATCH3', 'SESSION_003', 3, 0.0744532559897688, 3, '2026-08-08 11:16:12.707255+05:30');
INSERT INTO scrap.batches (batch_id, asset_id, batch_number, cm_per_pixel, total_scraps, created_at) VALUES ('BATCH4', 'SESSION_004', 4, 0.0849505496374105, 3, '2026-08-08 11:16:12.709289+05:30');
INSERT INTO scrap.batches (batch_id, asset_id, batch_number, cm_per_pixel, total_scraps, created_at) VALUES ('BATCH5', 'SESSION_005', 5, 0.0779445798997825, 3, '2026-08-08 11:16:12.711408+05:30');


--
-- Data for Name: scraps; Type: TABLE DATA; Schema: scrap; Owner: postgres
--

INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('d9e94ca8-2aca-4ccf-83ff-53dc9441b4b8', 'BATCH1', 'square_1', 'square', NULL, 4, 11.15, '{"id": 1, "area_cm2": 11.15, "piece_name": "square_1", "shape_type": "square", "vertex_labels": {"A": [185, 367], "B": [183, 394], "C": [214, 398], "D": [217, 371]}, "vertices_count": 4, "side_lengths_cm": {"AB": 2.87, "BC": 3.31, "CD": 2.88, "DA": 3.41}}', '2026-08-08 11:16:12.691858+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('683ade6d-56f6-44a1-b94e-dffd1f02ec98', 'BATCH1', 'rectangle_1', 'rectangle', NULL, 4, 40.53, '{"id": 2, "area_cm2": 40.53, "piece_name": "rectangle_1", "shape_type": "rectangle", "vertex_labels": {"A": [351, 220], "B": [347, 289], "C": [397, 293], "D": [400, 224]}, "vertices_count": 4, "side_lengths_cm": {"AB": 7.32, "BC": 5.31, "CD": 7.31, "DA": 5.2}}', '2026-08-08 11:16:12.691858+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('454aea8e-7334-4b3b-b272-fe3cf8b11054', 'BATCH1', 'triangle_1', 'triangle', NULL, 3, 36.95, '{"id": 3, "area_cm2": 36.95, "piece_name": "triangle_1", "shape_type": "triangle", "vertex_labels": {"A": [268, 251], "B": [256, 200], "C": [153, 222]}, "vertices_count": 3, "side_lengths_cm": {"AB": 5.55, "BC": 11.15, "CA": 12.55}}', '2026-08-08 11:16:12.691858+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('518c1936-cbc7-4ebf-b418-8af6910c3037', 'BATCH1', 'irregular_1', 'irregular', 'False', 14, 35.83, '{"id": 1, "area_cm2": 35.83, "centroid": {"x": 329, "y": 422}, "angles_deg": [156.8, 157.62, 153.29, 154.34, 144.52, 155.22, 153.43, 161.57, 145.3, 146.5, 158.2, 158.63, 156.37, 158.2], "fill_ratio": 0.79, "piece_name": "irregular_1", "shape_type": "irregular", "centroid_cm": {"x": 29.73, "y": 38.14}, "flag_reason": "irregular geometry inconsistent", "waste_ratio": 0.21, "bounding_box": {"width_cm": 6.33, "height_cm": 7.14}, "perimeter_cm": 22.48, "nearby_scraps": [{"piece": "rectangle_1", "distance_cm": 26.26, "relationship": "nearby"}, {"piece": "triangle_1", "distance_cm": 21.21, "relationship": "nearby"}], "vertex_labels": {"A": [305, 394], "B": [295, 404], "C": [290, 416], "D": [291, 430], "E": [303, 451], "F": [316, 457], "G": [341, 457], "H": [355, 450], "I": [365, 440], "J": [369, 418], "K": [363, 404], "L": [354, 395], "M": [338, 388], "N": [320, 388]}, "verified_shape": false, "vertices_count": 14, "regularity_score": 0.99, "shape_confidence": 0.99, "material_efficiency": "medium", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 1.28, "BC": 1.17, "CD": 1.27, "DE": 2.19, "EF": 1.29, "FG": 2.26, "GH": 1.41, "HI": 1.28, "IJ": 2.02, "JK": 1.38, "KL": 1.15, "LM": 1.58, "MN": 1.63, "NA": 1.46}}', '2026-08-08 11:16:12.696943+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('5bd199ee-7c3f-499e-8c30-e1a624f92fe0', 'BATCH1', 'rectangle_1', 'rectangle', 'False', 4, 95.13, '{"id": 2, "area_cm2": 95.13, "centroid": {"x": 154, "y": 190}, "angles_deg": [82.41, 98.39, 87.27, 91.94], "fill_ratio": 0.95, "piece_name": "rectangle_1", "shape_type": "rectangle", "centroid_cm": {"x": 13.92, "y": 17.17}, "flag_reason": "rectangle geometry inconsistent", "waste_ratio": 0.05, "bounding_box": {"width_cm": 6.98, "height_cm": 14.35}, "perimeter_cm": 41.79, "nearby_scraps": [{"piece": "irregular_1", "distance_cm": 26.26, "relationship": "nearby"}, {"piece": "triangle_1", "distance_cm": 18.34, "relationship": "nearby"}], "vertex_labels": {"A": [75, 154], "B": [84, 225], "C": [232, 228], "D": [230, 155]}, "verified_shape": false, "vertices_count": 4, "regularity_score": 0.7, "shape_confidence": 0.7, "material_efficiency": "high", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 6.47, "BC": 13.38, "CD": 6.6, "DA": 14.01}}', '2026-08-08 11:16:12.696943+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('f193290d-9dc6-47f9-94a2-2179e17e1976', 'BATCH1', 'triangle_1', 'triangle', 'True', 3, 66.27, '{"id": 3, "area_cm2": 66.27, "centroid": {"x": 357, "y": 189}, "angles_deg": [57.51, 94.21, 28.28], "fill_ratio": 0.53, "piece_name": "triangle_1", "shape_type": "triangle", "centroid_cm": {"x": 32.26, "y": 17.08}, "flag_reason": null, "waste_ratio": 0.47, "bounding_box": {"width_cm": 17.17, "height_cm": 7.23}, "perimeter_cm": 42.57, "nearby_scraps": [{"piece": "irregular_1", "distance_cm": 21.21, "relationship": "nearby"}, {"piece": "rectangle_1", "distance_cm": 18.34, "relationship": "nearby"}], "vertex_labels": {"A": [411, 124], "B": [322, 139], "C": [337, 299]}, "verified_shape": true, "vertices_count": 3, "regularity_score": 1.0, "shape_confidence": 1.0, "material_efficiency": "low", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 8.16, "BC": 14.52, "CA": 17.17}}', '2026-08-08 11:16:12.696943+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'BATCH2', 'irregular_1', 'irregular', NULL, 6, 25.18, '{"id": 1, "area_cm2": 25.18, "piece_name": "irregular_1", "shape_type": "irregular", "vertex_labels": {"A": [131, 335], "B": [128, 351], "C": [172, 363], "D": [162, 416], "E": [177, 420], "F": [197, 350]}, "vertices_count": 6, "side_lengths_cm": {"AB": 1.7, "BC": 4.75, "CD": 5.62, "DE": 1.62, "EF": 7.59, "FA": 7.05}}', '2026-08-08 11:16:12.700138+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('30888a53-8558-49ba-a185-e47f7579db53', 'BATCH2', 'irregular_2', 'irregular', NULL, 8, 33.7, '{"id": 2, "area_cm2": 33.7, "piece_name": "irregular_2", "shape_type": "irregular", "vertex_labels": {"A": [384, 322], "B": [364, 336], "C": [361, 362], "D": [381, 383], "E": [403, 384], "F": [421, 367], "G": [423, 344], "H": [411, 329]}, "vertices_count": 8, "side_lengths_cm": {"AB": 2.54, "BC": 2.73, "CD": 3.02, "DE": 2.3, "EF": 2.58, "FG": 2.41, "GH": 2.0, "HA": 2.91}}', '2026-08-08 11:16:12.700138+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('fb9edee9-e505-4696-8178-59b300b50081', 'BATCH2', 'circle_1', 'circle', NULL, 7, 8.87, '{"id": 3, "area_cm2": 8.87, "piece_name": "circle_1", "shape_type": "circle", "vertex_labels": {"A": [268, 300], "B": [253, 305], "C": [249, 312], "D": [248, 323], "E": [260, 334], "F": [273, 330], "G": [280, 308]}, "vertices_count": 7, "side_lengths_cm": {"AB": 1.65, "BC": 0.84, "CD": 1.15, "DE": 1.7, "EF": 1.42, "FG": 2.41, "GA": 1.5}}', '2026-08-08 11:16:12.700138+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('78c9d90b-9594-480d-91ff-efee6d6aec9f', 'BATCH2', 'irregular_3', 'irregular', NULL, 5, 11.12, '{"id": 4, "area_cm2": 11.12, "piece_name": "irregular_3", "shape_type": "irregular", "vertex_labels": {"A": [144, 220], "B": [128, 230], "C": [128, 236], "D": [160, 273], "E": [163, 242]}, "vertices_count": 5, "side_lengths_cm": {"AB": 1.97, "BC": 0.63, "CD": 5.1, "DE": 3.25, "EA": 3.03}}', '2026-08-08 11:16:12.700138+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('3664c010-d77e-444e-bc05-326c5590d6a2', 'BATCH2', 'irregular_4', 'irregular', NULL, 6, 31.36, '{"id": 5, "area_cm2": 31.36, "piece_name": "irregular_4", "shape_type": "irregular", "vertex_labels": {"A": [311, 212], "B": [301, 258], "C": [362, 269], "D": [370, 214], "E": [342, 229], "F": [334, 216]}, "vertices_count": 6, "side_lengths_cm": {"AB": 4.91, "BC": 6.46, "CD": 5.79, "DE": 3.31, "EF": 1.59, "FA": 2.43}}', '2026-08-08 11:16:12.700138+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('fc58d984-23d3-4288-bb95-97e369896ade', 'BATCH2', 'irregular_1', 'irregular', 'False', 6, 37.45, '{"id": 1, "area_cm2": 37.45, "centroid": {"x": 360, "y": 422}, "angles_deg": [84.09, 88.61, 47.73, 99.1, 142.13, 96.55], "fill_ratio": 0.76, "piece_name": "irregular_1", "shape_type": "irregular", "centroid_cm": {"x": 29.68, "y": 34.8}, "flag_reason": "irregular geometry inconsistent", "waste_ratio": 0.24, "bounding_box": {"width_cm": 7.66, "height_cm": 6.4}, "perimeter_cm": 27.89, "nearby_scraps": [{"piece": "l-shape_1", "distance_cm": 16.61, "relationship": "nearby"}, {"piece": "rectangle_1", "distance_cm": 23.45, "relationship": "nearby"}], "vertex_labels": {"A": [408, 394], "B": [318, 393], "C": [319, 469], "D": [349, 441], "E": [367, 455], "F": [401, 455]}, "verified_shape": false, "vertices_count": 6, "regularity_score": 0.87, "shape_confidence": 0.87, "material_efficiency": "medium", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 7.42, "BC": 6.27, "CD": 3.38, "DE": 1.88, "EF": 2.8, "FA": 5.06}}', '2026-08-08 11:16:12.705352+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('0fa54902-a0a8-4c59-b114-3d6ee076b05e', 'BATCH2', 'l-shape_1', 'l-shape', 'False', 6, 38.95, '{"id": 2, "area_cm2": 38.95, "centroid": {"x": 346, "y": 221}, "angles_deg": [85.91, 96.54, 91.66, 93.29, 92.43, 83.48], "fill_ratio": 0.46, "piece_name": "l-shape_1", "shape_type": "l-shape", "centroid_cm": {"x": 28.53, "y": 18.22}, "flag_reason": "l-shape geometry inconsistent", "waste_ratio": 0.54, "bounding_box": {"width_cm": 9.07, "height_cm": 9.32}, "perimeter_cm": 35.99, "nearby_scraps": [{"piece": "irregular_1", "distance_cm": 16.61, "relationship": "nearby"}, {"piece": "rectangle_1", "distance_cm": 16.71, "relationship": "nearby"}], "vertex_labels": {"A": [278, 186], "B": [280, 214], "C": [350, 217], "D": [349, 289], "E": [377, 291], "F": [389, 186]}, "verified_shape": false, "vertices_count": 6, "regularity_score": 0.67, "shape_confidence": 0.67, "material_efficiency": "low", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 2.31, "BC": 5.78, "CD": 5.94, "DE": 2.31, "EF": 8.71, "FA": 9.15}}', '2026-08-08 11:16:12.705352+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('94fc7f8a-5101-4ad4-b0d8-b13a2fe387fd', 'BATCH2', 'rectangle_1', 'rectangle', 'False', 4, 60.21, '{"id": 3, "area_cm2": 60.21, "centroid": {"x": 144, "y": 237}, "angles_deg": [82.88, 95.93, 88.13, 93.06], "fill_ratio": 0.93, "piece_name": "rectangle_1", "shape_type": "rectangle", "centroid_cm": {"x": 11.87, "y": 19.54}, "flag_reason": "rectangle geometry inconsistent", "waste_ratio": 0.07, "bounding_box": {"width_cm": 9.73, "height_cm": 6.68}, "perimeter_cm": 32.12, "nearby_scraps": [{"piece": "irregular_1", "distance_cm": 23.45, "relationship": "nearby"}, {"piece": "l-shape_1", "distance_cm": 16.71, "relationship": "nearby"}], "vertex_labels": {"A": [103, 180], "B": [110, 293], "C": [182, 296], "D": [183, 185]}, "verified_shape": false, "vertices_count": 4, "regularity_score": 0.79, "shape_confidence": 0.79, "material_efficiency": "high", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 9.34, "BC": 5.94, "CD": 9.15, "DA": 6.61}}', '2026-08-08 11:16:12.705352+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('5c4c2a34-e76d-4984-a6c5-c335d827ee74', 'BATCH3', 'polygon_1', 'polygon', 'False', 5, 22.48, '{"id": 1, "area_cm2": 22.48, "centroid": {"x": 369, "y": 434}, "angles_deg": [66.82, 122.34, 116.36, 137.79, 96.69], "fill_ratio": 0.66, "piece_name": "polygon_1", "shape_type": "polygon", "centroid_cm": {"x": 27.47, "y": 32.31}, "flag_reason": "polygon geometry inconsistent", "waste_ratio": 0.34, "bounding_box": {"width_cm": 6.93, "height_cm": 4.92}, "perimeter_cm": 20.55, "nearby_scraps": [{"piece": "zigzag_1", "distance_cm": 21.48, "relationship": "nearby"}, {"piece": "polygon_2", "distance_cm": 17.08, "relationship": "nearby"}], "vertex_labels": {"A": [412, 405], "B": [323, 414], "C": [320, 420], "D": [354, 465], "E": [391, 472]}, "verified_shape": false, "vertices_count": 5, "regularity_score": 0.97, "shape_confidence": 0.97, "material_efficiency": "medium", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 6.66, "BC": 0.5, "CD": 4.2, "DE": 2.8, "EA": 5.23}}', '2026-08-08 11:16:12.707255+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('9f80320d-fb7b-4e2a-8811-311752411bc6', 'BATCH3', 'zigzag_1', 'zigzag', 'False', 9, 31.57, '{"id": 2, "area_cm2": 31.57, "centroid": {"x": 163, "y": 232}, "angles_deg": [94.39, 87.85, 120.59, 151.54, 57.14, 158.2, 118.91, 62.64, 119.41], "fill_ratio": 0.42, "piece_name": "zigzag_1", "shape_type": "zigzag", "centroid_cm": {"x": 12.14, "y": 17.27}, "flag_reason": "zigzag geometry inconsistent", "waste_ratio": 0.58, "bounding_box": {"width_cm": 7.61, "height_cm": 9.87}, "perimeter_cm": 40.81, "nearby_scraps": [{"piece": "polygon_1", "distance_cm": 21.48, "relationship": "nearby"}, {"piece": "polygon_2", "distance_cm": 14.44, "relationship": "nearby"}], "vertex_labels": {"A": [148, 164], "B": [120, 294], "C": [137, 297], "D": [143, 290], "E": [160, 211], "F": [170, 221], "G": [200, 291], "H": [220, 293], "I": [170, 167]}, "verified_shape": false, "vertices_count": 9, "regularity_score": 0.07, "shape_confidence": 0.07, "material_efficiency": "low", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 9.9, "BC": 1.29, "CD": 0.69, "DE": 6.02, "EF": 1.05, "FG": 5.67, "GH": 1.5, "HI": 10.09, "IA": 1.65}}', '2026-08-08 11:16:12.707255+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('17f267e8-2dc6-4f35-86da-044a47365430', 'BATCH3', 'polygon_2', 'polygon', 'False', 6, 46.71, '{"id": 3, "area_cm2": 46.71, "centroid": {"x": 355, "y": 205}, "angles_deg": [122.91, 97.33, 130.72, 128.52, 105.52, 135.0], "fill_ratio": 0.81, "piece_name": "polygon_2", "shape_type": "polygon", "centroid_cm": {"x": 26.43, "y": 15.26}, "flag_reason": "polygon geometry inconsistent", "waste_ratio": 0.19, "bounding_box": {"width_cm": 5.68, "height_cm": 10.12}, "perimeter_cm": 28.84, "nearby_scraps": [{"piece": "polygon_1", "distance_cm": 17.08, "relationship": "nearby"}, {"piece": "zigzag_1", "distance_cm": 14.44, "relationship": "nearby"}], "vertex_labels": {"A": [383, 142], "B": [313, 157], "C": [320, 241], "D": [371, 278], "E": [389, 273], "F": [389, 148]}, "verified_shape": false, "vertices_count": 6, "regularity_score": 0.98, "shape_confidence": 0.98, "material_efficiency": "high", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 5.33, "BC": 6.28, "CD": 4.69, "DE": 1.39, "EF": 9.31, "FA": 0.63}}', '2026-08-08 11:16:12.707255+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('a2d0184a-ed31-4e05-b491-50b7411310a5', 'BATCH4', 'irregular_1', 'irregular', 'False', 6, 67.62, '{"id": 1, "area_cm2": 67.62, "centroid": {"x": 386, "y": 409}, "angles_deg": [90.72, 64.53, 100.89, 125.12, 92.25, 88.27], "fill_ratio": 0.63, "piece_name": "irregular_1", "shape_type": "irregular", "centroid_cm": {"x": 32.79, "y": 34.74}, "flag_reason": "irregular geometry inconsistent", "waste_ratio": 0.37, "bounding_box": {"width_cm": 10.96, "height_cm": 9.77}, "perimeter_cm": 38.84, "nearby_scraps": [{"piece": "frame_1", "distance_cm": 25.44, "relationship": "nearby"}, {"piece": "irregular_2", "distance_cm": 18.31, "relationship": "nearby"}], "vertex_labels": {"A": [321, 361], "B": [320, 407], "C": [340, 398], "D": [404, 489], "E": [426, 489], "F": [431, 362]}, "verified_shape": false, "vertices_count": 6, "regularity_score": 0.87, "shape_confidence": 0.87, "material_efficiency": "medium", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 3.91, "BC": 1.86, "CD": 9.45, "DE": 1.87, "EF": 10.8, "FA": 9.34}}', '2026-08-08 11:16:12.709289+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('65ebf55d-d713-4fda-af70-b5ca86821948', 'BATCH4', 'frame_1', 'frame', 'False', 4, 77.32, '{"id": 2, "area_cm2": 77.32, "centroid": {"x": 157, "y": 216}, "angles_deg": [90.27, 86.06, 98.02, 85.64], "fill_ratio": 0.92, "piece_name": "frame_1", "shape_type": "frame", "centroid_cm": {"x": 13.34, "y": 18.35}, "flag_reason": "frame geometry inconsistent", "waste_ratio": 0.08, "bounding_box": {"width_cm": 8.97, "height_cm": 9.39}, "perimeter_cm": 35.34, "nearby_scraps": [{"piece": "irregular_1", "distance_cm": 25.44, "relationship": "nearby"}, {"piece": "irregular_2", "distance_cm": 16.74, "relationship": "nearby"}], "vertex_labels": {"A": [202, 162], "B": [103, 168], "C": [116, 268], "D": [209, 269], "E": [126, 193], "F": [187, 191], "G": [193, 248], "H": [189, 252], "I": [130, 248]}, "verified_shape": false, "vertices_count": 4, "regularity_score": 0.87, "shape_confidence": 0.87, "material_efficiency": "high", "inner_side_lengths_cm": {"EF": 5.18, "FG": 4.87, "GH": 0.48, "HI": 5.02, "IE": 4.68}, "outer_side_lengths_cm": {"AB": 8.43, "BC": 8.57, "CD": 7.9, "DA": 9.11}}', '2026-08-08 11:16:12.709289+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('08d033b0-7eb2-470c-a227-f3f1cfae6761', 'BATCH4', 'irregular_2', 'irregular', 'False', 5, 42.98, '{"id": 3, "area_cm2": 42.98, "centroid": {"x": 353, "y": 196}, "angles_deg": [89.14, 132.8, 33.31, 122.33, 47.08], "fill_ratio": 0.43, "piece_name": "irregular_2", "shape_type": "irregular", "centroid_cm": {"x": 29.99, "y": 16.65}, "flag_reason": "irregular geometry inconsistent", "waste_ratio": 0.57, "bounding_box": {"width_cm": 9.19, "height_cm": 10.98}, "perimeter_cm": 36.63, "nearby_scraps": [{"piece": "irregular_1", "distance_cm": 18.31, "relationship": "nearby"}, {"piece": "frame_1", "distance_cm": 16.74, "relationship": "nearby"}], "vertex_labels": {"A": [347, 121], "B": [340, 125], "C": [308, 263], "D": [351, 222], "E": [411, 237]}, "verified_shape": false, "vertices_count": 5, "regularity_score": 0.78, "shape_confidence": 0.78, "material_efficiency": "low", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 0.68, "BC": 12.03, "CD": 5.05, "DE": 5.25, "EA": 11.25}}', '2026-08-08 11:16:12.709289+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('1bef46de-f2a5-4a93-be44-3cddc5d2adc3', 'BATCH5', 'irregular_1', 'irregular', 'False', 5, 24.76, '{"id": 1, "area_cm2": 24.76, "centroid": {"x": 366, "y": 403}, "angles_deg": [93.73, 145.16, 86.91, 61.37, 83.15], "fill_ratio": 0.62, "piece_name": "irregular_1", "shape_type": "irregular", "centroid_cm": {"x": 28.53, "y": 31.41}, "flag_reason": "irregular geometry inconsistent", "waste_ratio": 0.38, "bounding_box": {"width_cm": 4.27, "height_cm": 9.42}, "perimeter_cm": 25.4, "nearby_scraps": [{"piece": "zigzag_1", "distance_cm": 19.73, "relationship": "nearby"}, {"piece": "polygon_1", "distance_cm": 16.3, "relationship": "nearby"}], "vertex_labels": {"A": [348, 346], "B": [356, 390], "C": [335, 436], "D": [391, 458], "E": [376, 339]}, "verified_shape": false, "vertices_count": 5, "regularity_score": 0.85, "shape_confidence": 0.85, "material_efficiency": "medium", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 3.49, "BC": 3.94, "CD": 4.69, "DE": 9.35, "EA": 2.25}}', '2026-08-08 11:16:12.711408+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('52331be6-7787-4c5b-a305-d8ebc42db24f', 'BATCH5', 'zigzag_1', 'zigzag', 'False', 10, 48.01, '{"id": 2, "area_cm2": 48.01, "centroid": {"x": 190, "y": 221}, "angles_deg": [82.86, 138.44, 44.37, 93.62, 88.63, 43.66, 75.24, 146.07, 91.41, 87.05], "fill_ratio": 0.49, "piece_name": "zigzag_1", "shape_type": "zigzag", "centroid_cm": {"x": 14.81, "y": 17.23}, "flag_reason": "zigzag geometry inconsistent", "waste_ratio": 0.51, "bounding_box": {"width_cm": 9.2, "height_cm": 10.69}, "perimeter_cm": 52.72, "nearby_scraps": [{"piece": "irregular_1", "distance_cm": 19.73, "relationship": "nearby"}, {"piece": "polygon_1", "distance_cm": 14.5, "relationship": "nearby"}], "vertex_labels": {"A": [245, 162], "B": [221, 168], "C": [171, 241], "D": [158, 167], "E": [131, 170], "F": [149, 303], "G": [215, 212], "H": [224, 223], "I": [227, 255], "J": [256, 253]}, "verified_shape": false, "vertices_count": 10, "regularity_score": 0.11, "shape_confidence": 0.11, "material_efficiency": "low", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 1.93, "BC": 6.9, "CD": 5.86, "DE": 2.12, "EF": 10.46, "FG": 8.76, "GH": 1.11, "HI": 2.51, "IJ": 2.27, "JA": 7.14}}', '2026-08-08 11:16:12.711408+05:30');
INSERT INTO scrap.scraps (scrap_id, batch_id, piece_name, shape_type, verified_shape, vertices_count, area_cm2, raw_json, created_at) VALUES ('ebed037e-9bec-41aa-9d5b-8ef1ffeb7af0', 'BATCH5', 'polygon_1', 'polygon', 'False', 7, 17.88, '{"id": 3, "area_cm2": 17.88, "centroid": {"x": 374, "y": 194}, "angles_deg": [89.07, 149.4, 120.51, 132.74, 113.88, 146.04, 148.36], "fill_ratio": 0.83, "piece_name": "polygon_1", "shape_type": "polygon", "centroid_cm": {"x": 29.15, "y": 15.12}, "flag_reason": "polygon geometry inconsistent", "waste_ratio": 0.17, "bounding_box": {"width_cm": 6.16, "height_cm": 3.51}, "perimeter_cm": 17.28, "nearby_scraps": [{"piece": "irregular_1", "distance_cm": 16.3, "relationship": "nearby"}, {"piece": "zigzag_1", "distance_cm": 14.5, "relationship": "nearby"}], "vertex_labels": {"A": [394, 159], "B": [357, 161], "C": [351, 165], "D": [354, 219], "E": [377, 238], "F": [383, 235], "G": [396, 212]}, "verified_shape": false, "vertices_count": 7, "regularity_score": 0.98, "shape_confidence": 0.98, "material_efficiency": "high", "inner_side_lengths_cm": {}, "outer_side_lengths_cm": {"AB": 2.89, "BC": 0.56, "CD": 4.22, "DE": 2.33, "EF": 0.52, "FG": 2.06, "GA": 4.13}}', '2026-08-08 11:16:12.711408+05:30');


--
-- Data for Name: side_lengths; Type: TABLE DATA; Schema: scrap; Owner: postgres
--

INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (1, 'd9e94ca8-2aca-4ccf-83ff-53dc9441b4b8', 'AB', 2.87);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (2, 'd9e94ca8-2aca-4ccf-83ff-53dc9441b4b8', 'BC', 3.31);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (3, 'd9e94ca8-2aca-4ccf-83ff-53dc9441b4b8', 'CD', 2.88);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (4, 'd9e94ca8-2aca-4ccf-83ff-53dc9441b4b8', 'DA', 3.41);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (5, '683ade6d-56f6-44a1-b94e-dffd1f02ec98', 'AB', 7.32);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (6, '683ade6d-56f6-44a1-b94e-dffd1f02ec98', 'BC', 5.31);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (7, '683ade6d-56f6-44a1-b94e-dffd1f02ec98', 'CD', 7.31);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (8, '683ade6d-56f6-44a1-b94e-dffd1f02ec98', 'DA', 5.2);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (9, '454aea8e-7334-4b3b-b272-fe3cf8b11054', 'AB', 5.55);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (10, '454aea8e-7334-4b3b-b272-fe3cf8b11054', 'BC', 11.15);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (11, '454aea8e-7334-4b3b-b272-fe3cf8b11054', 'CA', 12.55);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (12, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'AB', 1.7);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (13, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'BC', 4.75);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (14, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'CD', 5.62);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (15, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'DE', 1.62);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (16, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'EF', 7.59);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (17, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'FA', 7.05);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (18, '30888a53-8558-49ba-a185-e47f7579db53', 'AB', 2.54);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (19, '30888a53-8558-49ba-a185-e47f7579db53', 'BC', 2.73);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (20, '30888a53-8558-49ba-a185-e47f7579db53', 'CD', 3.02);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (21, '30888a53-8558-49ba-a185-e47f7579db53', 'DE', 2.3);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (22, '30888a53-8558-49ba-a185-e47f7579db53', 'EF', 2.58);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (23, '30888a53-8558-49ba-a185-e47f7579db53', 'FG', 2.41);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (24, '30888a53-8558-49ba-a185-e47f7579db53', 'GH', 2);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (25, '30888a53-8558-49ba-a185-e47f7579db53', 'HA', 2.91);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (26, 'fb9edee9-e505-4696-8178-59b300b50081', 'AB', 1.65);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (27, 'fb9edee9-e505-4696-8178-59b300b50081', 'BC', 0.84);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (28, 'fb9edee9-e505-4696-8178-59b300b50081', 'CD', 1.15);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (29, 'fb9edee9-e505-4696-8178-59b300b50081', 'DE', 1.7);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (30, 'fb9edee9-e505-4696-8178-59b300b50081', 'EF', 1.42);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (31, 'fb9edee9-e505-4696-8178-59b300b50081', 'FG', 2.41);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (32, 'fb9edee9-e505-4696-8178-59b300b50081', 'GA', 1.5);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (33, '78c9d90b-9594-480d-91ff-efee6d6aec9f', 'AB', 1.97);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (34, '78c9d90b-9594-480d-91ff-efee6d6aec9f', 'BC', 0.63);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (35, '78c9d90b-9594-480d-91ff-efee6d6aec9f', 'CD', 5.1);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (36, '78c9d90b-9594-480d-91ff-efee6d6aec9f', 'DE', 3.25);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (37, '78c9d90b-9594-480d-91ff-efee6d6aec9f', 'EA', 3.03);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (38, '3664c010-d77e-444e-bc05-326c5590d6a2', 'AB', 4.91);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (39, '3664c010-d77e-444e-bc05-326c5590d6a2', 'BC', 6.46);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (40, '3664c010-d77e-444e-bc05-326c5590d6a2', 'CD', 5.79);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (41, '3664c010-d77e-444e-bc05-326c5590d6a2', 'DE', 3.31);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (42, '3664c010-d77e-444e-bc05-326c5590d6a2', 'EF', 1.59);
INSERT INTO scrap.side_lengths (id, scrap_id, side_label, length_cm) VALUES (43, '3664c010-d77e-444e-bc05-326c5590d6a2', 'FA', 2.43);


--
-- Data for Name: vertices; Type: TABLE DATA; Schema: scrap; Owner: postgres
--

INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (1, 'd9e94ca8-2aca-4ccf-83ff-53dc9441b4b8', 'A', 185, 367);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (2, 'd9e94ca8-2aca-4ccf-83ff-53dc9441b4b8', 'B', 183, 394);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (3, 'd9e94ca8-2aca-4ccf-83ff-53dc9441b4b8', 'C', 214, 398);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (4, 'd9e94ca8-2aca-4ccf-83ff-53dc9441b4b8', 'D', 217, 371);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (5, '683ade6d-56f6-44a1-b94e-dffd1f02ec98', 'A', 351, 220);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (6, '683ade6d-56f6-44a1-b94e-dffd1f02ec98', 'B', 347, 289);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (7, '683ade6d-56f6-44a1-b94e-dffd1f02ec98', 'C', 397, 293);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (8, '683ade6d-56f6-44a1-b94e-dffd1f02ec98', 'D', 400, 224);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (9, '454aea8e-7334-4b3b-b272-fe3cf8b11054', 'A', 268, 251);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (10, '454aea8e-7334-4b3b-b272-fe3cf8b11054', 'B', 256, 200);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (11, '454aea8e-7334-4b3b-b272-fe3cf8b11054', 'C', 153, 222);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (12, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'A', 305, 394);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (13, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'B', 295, 404);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (14, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'C', 290, 416);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (15, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'D', 291, 430);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (16, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'E', 303, 451);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (17, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'F', 316, 457);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (18, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'G', 341, 457);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (19, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'H', 355, 450);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (20, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'I', 365, 440);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (21, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'J', 369, 418);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (22, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'K', 363, 404);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (23, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'L', 354, 395);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (24, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'M', 338, 388);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (25, '518c1936-cbc7-4ebf-b418-8af6910c3037', 'N', 320, 388);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (26, '5bd199ee-7c3f-499e-8c30-e1a624f92fe0', 'A', 75, 154);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (27, '5bd199ee-7c3f-499e-8c30-e1a624f92fe0', 'B', 84, 225);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (28, '5bd199ee-7c3f-499e-8c30-e1a624f92fe0', 'C', 232, 228);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (29, '5bd199ee-7c3f-499e-8c30-e1a624f92fe0', 'D', 230, 155);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (30, 'f193290d-9dc6-47f9-94a2-2179e17e1976', 'A', 411, 124);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (31, 'f193290d-9dc6-47f9-94a2-2179e17e1976', 'B', 322, 139);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (32, 'f193290d-9dc6-47f9-94a2-2179e17e1976', 'C', 337, 299);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (33, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'A', 131, 335);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (34, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'B', 128, 351);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (35, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'C', 172, 363);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (36, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'D', 162, 416);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (37, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'E', 177, 420);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (38, '80945ecb-2ac9-44b9-a2e7-63308abaf86f', 'F', 197, 350);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (39, '30888a53-8558-49ba-a185-e47f7579db53', 'A', 384, 322);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (40, '30888a53-8558-49ba-a185-e47f7579db53', 'B', 364, 336);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (41, '30888a53-8558-49ba-a185-e47f7579db53', 'C', 361, 362);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (42, '30888a53-8558-49ba-a185-e47f7579db53', 'D', 381, 383);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (43, '30888a53-8558-49ba-a185-e47f7579db53', 'E', 403, 384);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (44, '30888a53-8558-49ba-a185-e47f7579db53', 'F', 421, 367);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (45, '30888a53-8558-49ba-a185-e47f7579db53', 'G', 423, 344);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (46, '30888a53-8558-49ba-a185-e47f7579db53', 'H', 411, 329);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (47, 'fb9edee9-e505-4696-8178-59b300b50081', 'A', 268, 300);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (48, 'fb9edee9-e505-4696-8178-59b300b50081', 'B', 253, 305);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (49, 'fb9edee9-e505-4696-8178-59b300b50081', 'C', 249, 312);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (50, 'fb9edee9-e505-4696-8178-59b300b50081', 'D', 248, 323);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (51, 'fb9edee9-e505-4696-8178-59b300b50081', 'E', 260, 334);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (52, 'fb9edee9-e505-4696-8178-59b300b50081', 'F', 273, 330);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (53, 'fb9edee9-e505-4696-8178-59b300b50081', 'G', 280, 308);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (54, '78c9d90b-9594-480d-91ff-efee6d6aec9f', 'A', 144, 220);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (55, '78c9d90b-9594-480d-91ff-efee6d6aec9f', 'B', 128, 230);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (56, '78c9d90b-9594-480d-91ff-efee6d6aec9f', 'C', 128, 236);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (57, '78c9d90b-9594-480d-91ff-efee6d6aec9f', 'D', 160, 273);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (58, '78c9d90b-9594-480d-91ff-efee6d6aec9f', 'E', 163, 242);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (59, '3664c010-d77e-444e-bc05-326c5590d6a2', 'A', 311, 212);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (60, '3664c010-d77e-444e-bc05-326c5590d6a2', 'B', 301, 258);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (61, '3664c010-d77e-444e-bc05-326c5590d6a2', 'C', 362, 269);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (62, '3664c010-d77e-444e-bc05-326c5590d6a2', 'D', 370, 214);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (63, '3664c010-d77e-444e-bc05-326c5590d6a2', 'E', 342, 229);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (64, '3664c010-d77e-444e-bc05-326c5590d6a2', 'F', 334, 216);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (65, 'fc58d984-23d3-4288-bb95-97e369896ade', 'A', 408, 394);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (66, 'fc58d984-23d3-4288-bb95-97e369896ade', 'B', 318, 393);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (67, 'fc58d984-23d3-4288-bb95-97e369896ade', 'C', 319, 469);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (68, 'fc58d984-23d3-4288-bb95-97e369896ade', 'D', 349, 441);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (69, 'fc58d984-23d3-4288-bb95-97e369896ade', 'E', 367, 455);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (70, 'fc58d984-23d3-4288-bb95-97e369896ade', 'F', 401, 455);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (71, '0fa54902-a0a8-4c59-b114-3d6ee076b05e', 'A', 278, 186);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (72, '0fa54902-a0a8-4c59-b114-3d6ee076b05e', 'B', 280, 214);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (73, '0fa54902-a0a8-4c59-b114-3d6ee076b05e', 'C', 350, 217);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (74, '0fa54902-a0a8-4c59-b114-3d6ee076b05e', 'D', 349, 289);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (75, '0fa54902-a0a8-4c59-b114-3d6ee076b05e', 'E', 377, 291);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (76, '0fa54902-a0a8-4c59-b114-3d6ee076b05e', 'F', 389, 186);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (77, '94fc7f8a-5101-4ad4-b0d8-b13a2fe387fd', 'A', 103, 180);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (78, '94fc7f8a-5101-4ad4-b0d8-b13a2fe387fd', 'B', 110, 293);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (79, '94fc7f8a-5101-4ad4-b0d8-b13a2fe387fd', 'C', 182, 296);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (80, '94fc7f8a-5101-4ad4-b0d8-b13a2fe387fd', 'D', 183, 185);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (81, '5c4c2a34-e76d-4984-a6c5-c335d827ee74', 'A', 412, 405);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (82, '5c4c2a34-e76d-4984-a6c5-c335d827ee74', 'B', 323, 414);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (83, '5c4c2a34-e76d-4984-a6c5-c335d827ee74', 'C', 320, 420);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (84, '5c4c2a34-e76d-4984-a6c5-c335d827ee74', 'D', 354, 465);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (85, '5c4c2a34-e76d-4984-a6c5-c335d827ee74', 'E', 391, 472);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (86, '9f80320d-fb7b-4e2a-8811-311752411bc6', 'A', 148, 164);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (87, '9f80320d-fb7b-4e2a-8811-311752411bc6', 'B', 120, 294);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (88, '9f80320d-fb7b-4e2a-8811-311752411bc6', 'C', 137, 297);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (89, '9f80320d-fb7b-4e2a-8811-311752411bc6', 'D', 143, 290);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (90, '9f80320d-fb7b-4e2a-8811-311752411bc6', 'E', 160, 211);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (91, '9f80320d-fb7b-4e2a-8811-311752411bc6', 'F', 170, 221);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (92, '9f80320d-fb7b-4e2a-8811-311752411bc6', 'G', 200, 291);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (93, '9f80320d-fb7b-4e2a-8811-311752411bc6', 'H', 220, 293);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (94, '9f80320d-fb7b-4e2a-8811-311752411bc6', 'I', 170, 167);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (95, '17f267e8-2dc6-4f35-86da-044a47365430', 'A', 383, 142);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (96, '17f267e8-2dc6-4f35-86da-044a47365430', 'B', 313, 157);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (97, '17f267e8-2dc6-4f35-86da-044a47365430', 'C', 320, 241);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (98, '17f267e8-2dc6-4f35-86da-044a47365430', 'D', 371, 278);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (99, '17f267e8-2dc6-4f35-86da-044a47365430', 'E', 389, 273);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (100, '17f267e8-2dc6-4f35-86da-044a47365430', 'F', 389, 148);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (101, 'a2d0184a-ed31-4e05-b491-50b7411310a5', 'A', 321, 361);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (102, 'a2d0184a-ed31-4e05-b491-50b7411310a5', 'B', 320, 407);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (103, 'a2d0184a-ed31-4e05-b491-50b7411310a5', 'C', 340, 398);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (104, 'a2d0184a-ed31-4e05-b491-50b7411310a5', 'D', 404, 489);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (105, 'a2d0184a-ed31-4e05-b491-50b7411310a5', 'E', 426, 489);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (106, 'a2d0184a-ed31-4e05-b491-50b7411310a5', 'F', 431, 362);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (107, '65ebf55d-d713-4fda-af70-b5ca86821948', 'A', 202, 162);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (108, '65ebf55d-d713-4fda-af70-b5ca86821948', 'B', 103, 168);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (109, '65ebf55d-d713-4fda-af70-b5ca86821948', 'C', 116, 268);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (110, '65ebf55d-d713-4fda-af70-b5ca86821948', 'D', 209, 269);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (111, '65ebf55d-d713-4fda-af70-b5ca86821948', 'E', 126, 193);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (112, '65ebf55d-d713-4fda-af70-b5ca86821948', 'F', 187, 191);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (113, '65ebf55d-d713-4fda-af70-b5ca86821948', 'G', 193, 248);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (114, '65ebf55d-d713-4fda-af70-b5ca86821948', 'H', 189, 252);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (115, '65ebf55d-d713-4fda-af70-b5ca86821948', 'I', 130, 248);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (116, '08d033b0-7eb2-470c-a227-f3f1cfae6761', 'A', 347, 121);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (117, '08d033b0-7eb2-470c-a227-f3f1cfae6761', 'B', 340, 125);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (118, '08d033b0-7eb2-470c-a227-f3f1cfae6761', 'C', 308, 263);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (119, '08d033b0-7eb2-470c-a227-f3f1cfae6761', 'D', 351, 222);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (120, '08d033b0-7eb2-470c-a227-f3f1cfae6761', 'E', 411, 237);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (121, '1bef46de-f2a5-4a93-be44-3cddc5d2adc3', 'A', 348, 346);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (122, '1bef46de-f2a5-4a93-be44-3cddc5d2adc3', 'B', 356, 390);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (123, '1bef46de-f2a5-4a93-be44-3cddc5d2adc3', 'C', 335, 436);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (124, '1bef46de-f2a5-4a93-be44-3cddc5d2adc3', 'D', 391, 458);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (125, '1bef46de-f2a5-4a93-be44-3cddc5d2adc3', 'E', 376, 339);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (126, '52331be6-7787-4c5b-a305-d8ebc42db24f', 'A', 245, 162);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (127, '52331be6-7787-4c5b-a305-d8ebc42db24f', 'B', 221, 168);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (128, '52331be6-7787-4c5b-a305-d8ebc42db24f', 'C', 171, 241);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (129, '52331be6-7787-4c5b-a305-d8ebc42db24f', 'D', 158, 167);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (130, '52331be6-7787-4c5b-a305-d8ebc42db24f', 'E', 131, 170);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (131, '52331be6-7787-4c5b-a305-d8ebc42db24f', 'F', 149, 303);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (132, '52331be6-7787-4c5b-a305-d8ebc42db24f', 'G', 215, 212);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (133, '52331be6-7787-4c5b-a305-d8ebc42db24f', 'H', 224, 223);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (134, '52331be6-7787-4c5b-a305-d8ebc42db24f', 'I', 227, 255);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (135, '52331be6-7787-4c5b-a305-d8ebc42db24f', 'J', 256, 253);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (136, 'ebed037e-9bec-41aa-9d5b-8ef1ffeb7af0', 'A', 394, 159);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (137, 'ebed037e-9bec-41aa-9d5b-8ef1ffeb7af0', 'B', 357, 161);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (138, 'ebed037e-9bec-41aa-9d5b-8ef1ffeb7af0', 'C', 351, 165);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (139, 'ebed037e-9bec-41aa-9d5b-8ef1ffeb7af0', 'D', 354, 219);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (140, 'ebed037e-9bec-41aa-9d5b-8ef1ffeb7af0', 'E', 377, 238);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (141, 'ebed037e-9bec-41aa-9d5b-8ef1ffeb7af0', 'F', 383, 235);
INSERT INTO scrap.vertices (id, scrap_id, label, x, y) VALUES (142, 'ebed037e-9bec-41aa-9d5b-8ef1ffeb7af0', 'G', 396, 212);


--
-- Name: rate_limit_log_id_seq; Type: SEQUENCE SET; Schema: auth; Owner: postgres
--

SELECT pg_catalog.setval('auth.rate_limit_log_id_seq', 1, false);


--
-- Name: relationships_id_seq; Type: SEQUENCE SET; Schema: bim; Owner: postgres
--

SELECT pg_catalog.setval('bim.relationships_id_seq', 1, false);


--
-- Name: semantic_tags_id_seq; Type: SEQUENCE SET; Schema: geometry; Owner: postgres
--

SELECT pg_catalog.setval('geometry.semantic_tags_id_seq', 1, false);


--
-- Name: side_lengths_id_seq; Type: SEQUENCE SET; Schema: scrap; Owner: postgres
--

SELECT pg_catalog.setval('scrap.side_lengths_id_seq', 43, true);


--
-- Name: vertices_id_seq; Type: SEQUENCE SET; Schema: scrap; Owner: postgres
--

SELECT pg_catalog.setval('scrap.vertices_id_seq', 142, true);


--
-- Name: group_members group_members_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.group_members
    ADD CONSTRAINT group_members_pkey PRIMARY KEY (phone, group_id);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (group_id);


--
-- Name: groups groups_wa_group_id_key; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.groups
    ADD CONSTRAINT groups_wa_group_id_key UNIQUE (wa_group_id);


--
-- Name: rate_limit_log rate_limit_log_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.rate_limit_log
    ADD CONSTRAINT rate_limit_log_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (phone);


--
-- Name: cobie_components cobie_components_pkey; Type: CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.cobie_components
    ADD CONSTRAINT cobie_components_pkey PRIMARY KEY (component_id);


--
-- Name: element_geometry element_geometry_pkey; Type: CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.element_geometry
    ADD CONSTRAINT element_geometry_pkey PRIMARY KEY (element_id);


--
-- Name: elements elements_ifc_guid_key; Type: CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.elements
    ADD CONSTRAINT elements_ifc_guid_key UNIQUE (ifc_guid);


--
-- Name: elements elements_pkey; Type: CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.elements
    ADD CONSTRAINT elements_pkey PRIMARY KEY (element_id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (project_id);


--
-- Name: relationships relationships_pkey; Type: CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.relationships
    ADD CONSTRAINT relationships_pkey PRIMARY KEY (id);


--
-- Name: spatial_structure spatial_structure_ifc_guid_key; Type: CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.spatial_structure
    ADD CONSTRAINT spatial_structure_ifc_guid_key UNIQUE (ifc_guid);


--
-- Name: spatial_structure spatial_structure_pkey; Type: CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.spatial_structure
    ADD CONSTRAINT spatial_structure_pkey PRIMARY KEY (node_id);


--
-- Name: media media_pkey; Type: CONSTRAINT; Schema: comms; Owner: postgres
--

ALTER TABLE ONLY comms.media
    ADD CONSTRAINT media_pkey PRIMARY KEY (media_id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: comms; Owner: postgres
--

ALTER TABLE ONLY comms.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (message_id);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (asset_id);


--
-- Name: cross_references cross_references_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.cross_references
    ADD CONSTRAINT cross_references_pkey PRIMARY KEY (ref_id);


--
-- Name: expert_notes expert_notes_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.expert_notes
    ADD CONSTRAINT expert_notes_pkey PRIMARY KEY (note_id);


--
-- Name: insights insights_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.insights
    ADD CONSTRAINT insights_pkey PRIMARY KEY (insight_id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: detections detections_pkey; Type: CONSTRAINT; Schema: cv; Owner: postgres
--

ALTER TABLE ONLY cv.detections
    ADD CONSTRAINT detections_pkey PRIMARY KEY (detection_id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: cv; Owner: postgres
--

ALTER TABLE ONLY cv.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (session_id);


--
-- Name: tracks tracks_pkey; Type: CONSTRAINT; Schema: cv; Owner: postgres
--

ALTER TABLE ONLY cv.tracks
    ADD CONSTRAINT tracks_pkey PRIMARY KEY (track_pk);


--
-- Name: elements elements_pkey; Type: CONSTRAINT; Schema: geometry; Owner: postgres
--

ALTER TABLE ONLY geometry.elements
    ADD CONSTRAINT elements_pkey PRIMARY KEY (element_id);


--
-- Name: semantic_tags semantic_tags_pkey; Type: CONSTRAINT; Schema: geometry; Owner: postgres
--

ALTER TABLE ONLY geometry.semantic_tags
    ADD CONSTRAINT semantic_tags_pkey PRIMARY KEY (id);


--
-- Name: shapes shapes_pkey; Type: CONSTRAINT; Schema: geometry; Owner: postgres
--

ALTER TABLE ONLY geometry.shapes
    ADD CONSTRAINT shapes_pkey PRIMARY KEY (shape_id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: ingest; Owner: postgres
--

ALTER TABLE ONLY ingest.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (file_id);


--
-- Name: chunks chunks_pkey; Type: CONSTRAINT; Schema: rag; Owner: postgres
--

ALTER TABLE ONLY rag.chunks
    ADD CONSTRAINT chunks_pkey PRIMARY KEY (chunk_id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: rag; Owner: postgres
--

ALTER TABLE ONLY rag.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (doc_id);


--
-- Name: batch_images batch_images_pkey; Type: CONSTRAINT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.batch_images
    ADD CONSTRAINT batch_images_pkey PRIMARY KEY (id);


--
-- Name: batches batches_pkey; Type: CONSTRAINT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.batches
    ADD CONSTRAINT batches_pkey PRIMARY KEY (batch_id);


--
-- Name: scraps scraps_pkey; Type: CONSTRAINT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.scraps
    ADD CONSTRAINT scraps_pkey PRIMARY KEY (scrap_id);


--
-- Name: side_lengths side_lengths_pkey; Type: CONSTRAINT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.side_lengths
    ADD CONSTRAINT side_lengths_pkey PRIMARY KEY (id);


--
-- Name: vertices vertices_pkey; Type: CONSTRAINT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.vertices
    ADD CONSTRAINT vertices_pkey PRIMARY KEY (id);


--
-- Name: idx_auth_rate_phone_time; Type: INDEX; Schema: auth; Owner: postgres
--

CREATE INDEX idx_auth_rate_phone_time ON auth.rate_limit_log USING btree (phone, requested_at);


--
-- Name: idx_bim_cobie_element; Type: INDEX; Schema: bim; Owner: postgres
--

CREATE INDEX idx_bim_cobie_element ON bim.cobie_components USING btree (element_id);


--
-- Name: idx_bim_elements_project; Type: INDEX; Schema: bim; Owner: postgres
--

CREATE INDEX idx_bim_elements_project ON bim.elements USING btree (project_id);


--
-- Name: idx_bim_elements_properties; Type: INDEX; Schema: bim; Owner: postgres
--

CREATE INDEX idx_bim_elements_properties ON bim.elements USING gin (properties);


--
-- Name: idx_bim_elements_type; Type: INDEX; Schema: bim; Owner: postgres
--

CREATE INDEX idx_bim_elements_type ON bim.elements USING btree (ifc_type);


--
-- Name: idx_bim_rel_source; Type: INDEX; Schema: bim; Owner: postgres
--

CREATE INDEX idx_bim_rel_source ON bim.relationships USING btree (source_element_id);


--
-- Name: idx_bim_rel_target; Type: INDEX; Schema: bim; Owner: postgres
--

CREATE INDEX idx_bim_rel_target ON bim.relationships USING btree (target_element_id);


--
-- Name: idx_bim_structure_parent; Type: INDEX; Schema: bim; Owner: postgres
--

CREATE INDEX idx_bim_structure_parent ON bim.spatial_structure USING btree (parent_node_id);


--
-- Name: idx_comms_messages_phone; Type: INDEX; Schema: comms; Owner: postgres
--

CREATE INDEX idx_comms_messages_phone ON comms.messages USING btree (phone, "timestamp");


--
-- Name: idx_asset_summary_pk; Type: INDEX; Schema: core; Owner: postgres
--

CREATE UNIQUE INDEX idx_asset_summary_pk ON core.asset_summary USING btree (asset_id);


--
-- Name: idx_core_assets_external_refs; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_core_assets_external_refs ON core.assets USING gin (external_refs);


--
-- Name: idx_core_assets_name_trgm; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_core_assets_name_trgm ON core.assets USING gin (name public.gin_trgm_ops);


--
-- Name: idx_core_assets_status; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_core_assets_status ON core.assets USING btree (status);


--
-- Name: idx_core_assets_type; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_core_assets_type ON core.assets USING btree (type);


--
-- Name: idx_core_insights_asset; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_core_insights_asset ON core.insights USING btree (asset_id);


--
-- Name: idx_core_notes_asset; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_core_notes_asset ON core.expert_notes USING btree (asset_id);


--
-- Name: idx_findings_search_asset; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_findings_search_asset ON core.findings_search USING btree (asset_id);


--
-- Name: idx_findings_search_pk; Type: INDEX; Schema: core; Owner: postgres
--

CREATE UNIQUE INDEX idx_findings_search_pk ON core.findings_search USING btree (finding_id);


--
-- Name: idx_findings_search_vector; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_findings_search_vector ON core.findings_search USING gin (search_vector);


--
-- Name: idx_xref_source; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_xref_source ON core.cross_references USING btree (source_schema, source_table, source_id);


--
-- Name: idx_xref_target; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_xref_target ON core.cross_references USING btree (target_schema, target_table, target_id);


--
-- Name: idx_xref_type; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_xref_type ON core.cross_references USING btree (relationship_type);


--
-- Name: idx_cv_detections_asset; Type: INDEX; Schema: cv; Owner: postgres
--

CREATE INDEX idx_cv_detections_asset ON cv.detections USING btree (asset_id);


--
-- Name: idx_cv_detections_confidence; Type: INDEX; Schema: cv; Owner: postgres
--

CREATE INDEX idx_cv_detections_confidence ON cv.detections USING btree (confidence);


--
-- Name: idx_cv_detections_raw; Type: INDEX; Schema: cv; Owner: postgres
--

CREATE INDEX idx_cv_detections_raw ON cv.detections USING gin (raw_json);


--
-- Name: idx_cv_tracks_asset; Type: INDEX; Schema: cv; Owner: postgres
--

CREATE INDEX idx_cv_tracks_asset ON cv.tracks USING btree (asset_id);


--
-- Name: idx_cv_tracks_session; Type: INDEX; Schema: cv; Owner: postgres
--

CREATE INDEX idx_cv_tracks_session ON cv.tracks USING btree (session_id);


--
-- Name: idx_geometry_semantic_shape; Type: INDEX; Schema: geometry; Owner: postgres
--

CREATE INDEX idx_geometry_semantic_shape ON geometry.semantic_tags USING btree (shape_id);


--
-- Name: idx_geometry_shapes_asset; Type: INDEX; Schema: geometry; Owner: postgres
--

CREATE INDEX idx_geometry_shapes_asset ON geometry.shapes USING btree (asset_id);


--
-- Name: idx_geometry_shapes_raw; Type: INDEX; Schema: geometry; Owner: postgres
--

CREATE INDEX idx_geometry_shapes_raw ON geometry.shapes USING gin (raw_json);


--
-- Name: idx_ingest_files_status; Type: INDEX; Schema: ingest; Owner: postgres
--

CREATE INDEX idx_ingest_files_status ON ingest.files USING btree (status);


--
-- Name: idx_rag_chunks_doc; Type: INDEX; Schema: rag; Owner: postgres
--

CREATE INDEX idx_rag_chunks_doc ON rag.chunks USING btree (doc_id);


--
-- Name: idx_scrap_scraps_batch; Type: INDEX; Schema: scrap; Owner: postgres
--

CREATE INDEX idx_scrap_scraps_batch ON scrap.scraps USING btree (batch_id);


--
-- Name: idx_scrap_scraps_shape; Type: INDEX; Schema: scrap; Owner: postgres
--

CREATE INDEX idx_scrap_scraps_shape ON scrap.scraps USING btree (shape_type);


--
-- Name: idx_scrap_sides_scrap; Type: INDEX; Schema: scrap; Owner: postgres
--

CREATE INDEX idx_scrap_sides_scrap ON scrap.side_lengths USING btree (scrap_id);


--
-- Name: idx_scrap_vertices_scrap; Type: INDEX; Schema: scrap; Owner: postgres
--

CREATE INDEX idx_scrap_vertices_scrap ON scrap.vertices USING btree (scrap_id);


--
-- Name: assets trg_assets_updated_at; Type: TRIGGER; Schema: core; Owner: postgres
--

CREATE TRIGGER trg_assets_updated_at BEFORE UPDATE ON core.assets FOR EACH ROW EXECUTE FUNCTION core.set_updated_at();


--
-- Name: group_members group_members_group_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.group_members
    ADD CONSTRAINT group_members_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth.groups(group_id) ON DELETE CASCADE;


--
-- Name: group_members group_members_phone_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.group_members
    ADD CONSTRAINT group_members_phone_fkey FOREIGN KEY (phone) REFERENCES auth.users(phone) ON DELETE CASCADE;


--
-- Name: rate_limit_log rate_limit_log_phone_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.rate_limit_log
    ADD CONSTRAINT rate_limit_log_phone_fkey FOREIGN KEY (phone) REFERENCES auth.users(phone) ON DELETE CASCADE;


--
-- Name: elements bim_elements_asset_id_fkey; Type: FK CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.elements
    ADD CONSTRAINT bim_elements_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES core.assets(asset_id) ON DELETE RESTRICT;


--
-- Name: cobie_components cobie_components_element_id_fkey; Type: FK CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.cobie_components
    ADD CONSTRAINT cobie_components_element_id_fkey FOREIGN KEY (element_id) REFERENCES bim.elements(element_id) ON DELETE CASCADE;


--
-- Name: element_geometry element_geometry_element_id_fkey; Type: FK CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.element_geometry
    ADD CONSTRAINT element_geometry_element_id_fkey FOREIGN KEY (element_id) REFERENCES bim.elements(element_id) ON DELETE CASCADE;


--
-- Name: elements elements_asset_id_fkey; Type: FK CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.elements
    ADD CONSTRAINT elements_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES core.assets(asset_id) ON DELETE SET NULL;


--
-- Name: elements elements_project_id_fkey; Type: FK CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.elements
    ADD CONSTRAINT elements_project_id_fkey FOREIGN KEY (project_id) REFERENCES bim.projects(project_id) ON DELETE CASCADE;


--
-- Name: elements elements_spatial_node_id_fkey; Type: FK CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.elements
    ADD CONSTRAINT elements_spatial_node_id_fkey FOREIGN KEY (spatial_node_id) REFERENCES bim.spatial_structure(node_id) ON DELETE SET NULL;


--
-- Name: relationships relationships_project_id_fkey; Type: FK CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.relationships
    ADD CONSTRAINT relationships_project_id_fkey FOREIGN KEY (project_id) REFERENCES bim.projects(project_id) ON DELETE CASCADE;


--
-- Name: relationships relationships_source_element_id_fkey; Type: FK CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.relationships
    ADD CONSTRAINT relationships_source_element_id_fkey FOREIGN KEY (source_element_id) REFERENCES bim.elements(element_id) ON DELETE CASCADE;


--
-- Name: relationships relationships_target_element_id_fkey; Type: FK CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.relationships
    ADD CONSTRAINT relationships_target_element_id_fkey FOREIGN KEY (target_element_id) REFERENCES bim.elements(element_id) ON DELETE CASCADE;


--
-- Name: spatial_structure spatial_structure_parent_node_id_fkey; Type: FK CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.spatial_structure
    ADD CONSTRAINT spatial_structure_parent_node_id_fkey FOREIGN KEY (parent_node_id) REFERENCES bim.spatial_structure(node_id) ON DELETE CASCADE;


--
-- Name: spatial_structure spatial_structure_project_id_fkey; Type: FK CONSTRAINT; Schema: bim; Owner: postgres
--

ALTER TABLE ONLY bim.spatial_structure
    ADD CONSTRAINT spatial_structure_project_id_fkey FOREIGN KEY (project_id) REFERENCES bim.projects(project_id) ON DELETE CASCADE;


--
-- Name: media media_message_id_fkey; Type: FK CONSTRAINT; Schema: comms; Owner: postgres
--

ALTER TABLE ONLY comms.media
    ADD CONSTRAINT media_message_id_fkey FOREIGN KEY (message_id) REFERENCES comms.messages(message_id) ON DELETE CASCADE;


--
-- Name: messages messages_asset_id_ref_fkey; Type: FK CONSTRAINT; Schema: comms; Owner: postgres
--

ALTER TABLE ONLY comms.messages
    ADD CONSTRAINT messages_asset_id_ref_fkey FOREIGN KEY (asset_id_ref) REFERENCES core.assets(asset_id) ON DELETE SET NULL;


--
-- Name: messages messages_group_id_fkey; Type: FK CONSTRAINT; Schema: comms; Owner: postgres
--

ALTER TABLE ONLY comms.messages
    ADD CONSTRAINT messages_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth.groups(group_id) ON DELETE SET NULL;


--
-- Name: messages messages_phone_fkey; Type: FK CONSTRAINT; Schema: comms; Owner: postgres
--

ALTER TABLE ONLY comms.messages
    ADD CONSTRAINT messages_phone_fkey FOREIGN KEY (phone) REFERENCES auth.users(phone) ON DELETE CASCADE;


--
-- Name: expert_notes expert_notes_asset_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.expert_notes
    ADD CONSTRAINT expert_notes_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES core.assets(asset_id) ON DELETE CASCADE;


--
-- Name: insights insights_asset_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.insights
    ADD CONSTRAINT insights_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES core.assets(asset_id) ON DELETE CASCADE;


--
-- Name: detections detections_asset_id_fkey; Type: FK CONSTRAINT; Schema: cv; Owner: postgres
--

ALTER TABLE ONLY cv.detections
    ADD CONSTRAINT detections_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES core.assets(asset_id) ON DELETE CASCADE;


--
-- Name: sessions sessions_asset_id_fkey; Type: FK CONSTRAINT; Schema: cv; Owner: postgres
--

ALTER TABLE ONLY cv.sessions
    ADD CONSTRAINT sessions_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES core.assets(asset_id) ON DELETE SET NULL;


--
-- Name: tracks tracks_asset_id_fkey; Type: FK CONSTRAINT; Schema: cv; Owner: postgres
--

ALTER TABLE ONLY cv.tracks
    ADD CONSTRAINT tracks_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES core.assets(asset_id) ON DELETE CASCADE;


--
-- Name: tracks tracks_session_id_fkey; Type: FK CONSTRAINT; Schema: cv; Owner: postgres
--

ALTER TABLE ONLY cv.tracks
    ADD CONSTRAINT tracks_session_id_fkey FOREIGN KEY (session_id) REFERENCES cv.sessions(session_id) ON DELETE CASCADE;


--
-- Name: elements elements_shape_id_fkey; Type: FK CONSTRAINT; Schema: geometry; Owner: postgres
--

ALTER TABLE ONLY geometry.elements
    ADD CONSTRAINT elements_shape_id_fkey FOREIGN KEY (shape_id) REFERENCES geometry.shapes(shape_id) ON DELETE CASCADE;


--
-- Name: semantic_tags semantic_tags_shape_id_fkey; Type: FK CONSTRAINT; Schema: geometry; Owner: postgres
--

ALTER TABLE ONLY geometry.semantic_tags
    ADD CONSTRAINT semantic_tags_shape_id_fkey FOREIGN KEY (shape_id) REFERENCES geometry.shapes(shape_id) ON DELETE CASCADE;


--
-- Name: shapes shapes_asset_id_fkey; Type: FK CONSTRAINT; Schema: geometry; Owner: postgres
--

ALTER TABLE ONLY geometry.shapes
    ADD CONSTRAINT shapes_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES core.assets(asset_id) ON DELETE CASCADE;


--
-- Name: chunks chunks_doc_id_fkey; Type: FK CONSTRAINT; Schema: rag; Owner: postgres
--

ALTER TABLE ONLY rag.chunks
    ADD CONSTRAINT chunks_doc_id_fkey FOREIGN KEY (doc_id) REFERENCES rag.documents(doc_id) ON DELETE CASCADE;


--
-- Name: documents documents_asset_id_fkey; Type: FK CONSTRAINT; Schema: rag; Owner: postgres
--

ALTER TABLE ONLY rag.documents
    ADD CONSTRAINT documents_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES core.assets(asset_id) ON DELETE SET NULL;


--
-- Name: batch_images batch_images_batch_id_fkey; Type: FK CONSTRAINT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.batch_images
    ADD CONSTRAINT batch_images_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES scrap.batches(batch_id) ON DELETE CASCADE;


--
-- Name: batches batches_asset_id_fkey; Type: FK CONSTRAINT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.batches
    ADD CONSTRAINT batches_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES core.assets(asset_id) ON DELETE CASCADE;


--
-- Name: scraps scraps_batch_id_fkey; Type: FK CONSTRAINT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.scraps
    ADD CONSTRAINT scraps_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES scrap.batches(batch_id) ON DELETE CASCADE;


--
-- Name: side_lengths side_lengths_scrap_id_fkey; Type: FK CONSTRAINT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.side_lengths
    ADD CONSTRAINT side_lengths_scrap_id_fkey FOREIGN KEY (scrap_id) REFERENCES scrap.scraps(scrap_id) ON DELETE CASCADE;


--
-- Name: vertices vertices_scrap_id_fkey; Type: FK CONSTRAINT; Schema: scrap; Owner: postgres
--

ALTER TABLE ONLY scrap.vertices
    ADD CONSTRAINT vertices_scrap_id_fkey FOREIGN KEY (scrap_id) REFERENCES scrap.scraps(scrap_id) ON DELETE CASCADE;


--
-- Name: asset_summary; Type: MATERIALIZED VIEW DATA; Schema: core; Owner: postgres
--

REFRESH MATERIALIZED VIEW core.asset_summary;


--
-- Name: findings_search; Type: MATERIALIZED VIEW DATA; Schema: core; Owner: postgres
--

REFRESH MATERIALIZED VIEW core.findings_search;


--
-- PostgreSQL database dump complete
--

\unrestrict lowMt82ormpYrHvh9geW3BXlDdIwPJtAcw65T5TeT1ECxQoerPkljneBa5NybXj

