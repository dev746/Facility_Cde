import os
from core.db import get_connection, execute

TABLES = """
CREATE TABLE IF NOT EXISTS assets (
    asset_id   TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    type       TEXT,
    location   TEXT,
    line       TEXT,
    zone       TEXT,
    status     TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS findings (
    finding_id TEXT PRIMARY KEY,
    asset_id   TEXT NOT NULL REFERENCES assets(asset_id),
    object     TEXT,
    condition  TEXT,
    confidence REAL,
    source     TEXT DEFAULT 'ingest',
    severity   TEXT DEFAULT 'low',
    status     TEXT DEFAULT 'open',
    timestamp  TEXT,
    raw_json   TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS expert_notes (
    note_id    TEXT PRIMARY KEY,
    asset_id   TEXT NOT NULL REFERENCES assets(asset_id),
    comment    TEXT,
    author     TEXT,
    timestamp  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS insights (
    insight_id   TEXT PRIMARY KEY,
    asset_id     TEXT NOT NULL REFERENCES assets(asset_id),
    summary      TEXT,
    severity     TEXT,
    generated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS users (
    phone      TEXT PRIMARY KEY,
    name       TEXT,
    role       TEXT NOT NULL CHECK(role IN ('admin','expert','technician','viewer')),
    shift      TEXT,
    line       TEXT,
    is_active  INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS batch_images (
    id         TEXT PRIMARY KEY,
    asset_id   TEXT NOT NULL,
    file_path  TEXT NOT NULL,
    label      TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ingest_log (
    id               TEXT PRIMARY KEY,
    filename         TEXT,
    schema_type      TEXT,
    assets_written   INTEGER DEFAULT 0,
    findings_written INTEGER DEFAULT 0,
    status           TEXT,
    error            TEXT,
    duration_ms      INTEGER,
    created_at       TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS groups (
    group_id    TEXT PRIMARY KEY,
    group_name  TEXT,
    wa_group_id TEXT UNIQUE,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS group_members (
    phone    TEXT,
    group_id TEXT,
    PRIMARY KEY (phone, group_id)
);

CREATE INDEX IF NOT EXISTS idx_findings_asset          ON findings(asset_id);
CREATE INDEX IF NOT EXISTS idx_findings_confidence     ON findings(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_findings_timestamp      ON findings(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_findings_severity       ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_findings_status         ON findings(status);
CREATE INDEX IF NOT EXISTS idx_findings_source         ON findings(source);
CREATE INDEX IF NOT EXISTS idx_findings_asset_conf     ON findings(asset_id, confidence DESC);
CREATE INDEX IF NOT EXISTS idx_assets_type             ON assets(type);
CREATE INDEX IF NOT EXISTS idx_assets_line             ON assets(line);
CREATE INDEX IF NOT EXISTS idx_assets_zone             ON assets(zone);
CREATE INDEX IF NOT EXISTS idx_notes_asset             ON expert_notes(asset_id);
CREATE INDEX IF NOT EXISTS idx_ingest_log_status       ON ingest_log(status, created_at DESC);
"""


def db_init():
    with get_connection() as conn:
        conn.executescript(TABLES)
        conn.commit()

    admin = os.getenv("ADMIN_PHONE", "whatsapp:+910000000000")
    execute(
        "INSERT OR IGNORE INTO users (phone, name, role) VALUES (?,?,?)",
        (admin, "Admin", "admin"),
    )
    print(f"[schema] DB ready. Admin: {admin}")


if __name__ == "__main__":
    db_init()
