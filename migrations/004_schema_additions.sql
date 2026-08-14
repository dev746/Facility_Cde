-- Per-user conversational context
CREATE TABLE IF NOT EXISTS core.user_context (
    phone           TEXT PRIMARY KEY,
    context_json    JSONB NOT NULL DEFAULT '{}',
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_context_phone
    ON core.user_context(phone);

-- Data version history — one row per unique file ingestion
CREATE TABLE IF NOT EXISTS core.data_versions (
    version_id      TEXT PRIMARY KEY,
    source_key      TEXT NOT NULL,          -- filename
    data_hash       TEXT NOT NULL,          -- SHA-256[:16] of file content
    schema_type     TEXT,                   -- batch / cv / annotations / etc
    asset_ids       JSONB DEFAULT '[]',     -- which assets were affected
    changes         JSONB DEFAULT '{}',     -- field-level diff
    ingested_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_data_versions_source
    ON core.data_versions(source_key, ingested_at DESC);

CREATE INDEX IF NOT EXISTS idx_data_versions_time
    ON core.data_versions(ingested_at DESC);
