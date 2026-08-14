"""
ingestion/version_tracker.py — Data versioning and update comparison layer.

Every time a file is ingested, this module:
1. Computes a content hash of the incoming data
2. Compares against the last known hash for that source/asset
3. If unchanged → skip (idempotent re-ingestion)
4. If changed → upsert only the changed fields + log what changed
5. Records a version history entry

This makes the ingestion pipeline safe to re-run and enables
"what changed since last batch?" queries.
"""
import hashlib
import json
import uuid
from datetime import datetime
from typing import Optional
from core.db import query, execute


def _hash(data: dict | list | str) -> str:
    """Deterministic SHA-256 hash of any JSON-serialisable data."""
    raw = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ── Version check ─────────────────────────────────────────────

def is_unchanged(source_key: str, data_hash: str) -> bool:
    """
    Returns True if this exact data has been ingested before.
    source_key = e.g. 'batch_1_database.json' or 'M14_cv_output.json'
    """
    try:
        rows = query(
            "SELECT data_hash FROM core.data_versions WHERE source_key = %s ORDER BY ingested_at DESC LIMIT 1",
            (source_key,)
        )
    except Exception:
        return False
    return bool(rows) and rows[0]["data_hash"] == data_hash


def record_version(source_key: str, data_hash: str, schema_type: str,
                   asset_ids: list, changes: dict) -> None:
    """Log a new version entry for this source file."""
    _execute_compat(
        """INSERT INTO core.data_versions
           (version_id, source_key, data_hash, schema_type, asset_ids, changes, ingested_at)
           VALUES ({p}, {p}, {p}, {p}, {p}::jsonb, {p}::jsonb, {now})""",
        (str(uuid.uuid4()), source_key, data_hash, schema_type,
         json.dumps(asset_ids), json.dumps(changes))
    )


def get_version_history(source_key: str, limit: int = 10) -> list:
    """Return version history for a given source file."""
    try:
        return query(
            "SELECT * FROM core.data_versions WHERE source_key = %s ORDER BY ingested_at DESC LIMIT %s",
            (source_key, limit)
        )
    except Exception:
        return []


# ── Asset-level comparison ─────────────────────────────────────

def diff_asset(incoming: dict, existing: dict) -> dict:
    """
    Compare incoming asset dict against existing DB record.
    Returns dict of changed fields: {field: (old_value, new_value)}
    """
    tracked = ["name", "type", "location", "line", "zone", "status"]
    changes = {}
    for field in tracked:
        inc_val = incoming.get(field)
        ext_val = existing.get(field)
        if inc_val and inc_val != ext_val and inc_val.lower() not in ("unknown", "nan", "none"):
            changes[field] = (ext_val, inc_val)
    return changes


def upsert_asset_with_diff(asset: dict) -> dict:
    """
    Upsert an asset, only updating fields that have changed.
    Returns {"action": "created"|"updated"|"unchanged", "changes": dict}
    """
    asset_id = asset.get("asset_id", "").upper()
    if not asset_id:
        return {"action": "skipped", "changes": {}}

    try:
        existing = query("SELECT * FROM core.assets WHERE asset_id = %s", (asset_id,))
        param_style = "%s"
    except Exception:
        existing = query("SELECT * FROM assets WHERE asset_id = ?", (asset_id,))
        param_style = "?"

    if not existing:
        # New asset — insert
        _insert_asset(asset, param_style)
        return {"action": "created", "changes": {}}

    changes = diff_asset(asset, dict(existing[0]))
    if not changes:
        return {"action": "unchanged", "changes": {}}

    # Build partial update only for changed fields
    set_clauses = []
    values = []
    for field, (_, new_val) in changes.items():
        set_clauses.append(f"{field} = {param_style}")
        values.append(new_val)
    values.append(asset_id)

    set_sql = ", ".join(set_clauses)
    try:
        execute(
            f"UPDATE core.assets SET {set_sql}, updated_at = NOW() WHERE asset_id = {param_style}",
            tuple(values)
        )
    except Exception:
        execute(
            f"UPDATE assets SET {set_sql}, updated_at = datetime('now') WHERE asset_id = {param_style}",
            tuple(values)
        )

    return {"action": "updated", "changes": changes}


def _insert_asset(asset: dict, param_style: str = "%s") -> None:
    """Insert new asset record."""
    p = param_style
    try:
        execute(
            f"""INSERT INTO core.assets (asset_id, name, type, location, line, zone)
                VALUES ({p},{p},{p},{p},{p},{p})
                ON CONFLICT (asset_id) DO NOTHING""",
            (asset["asset_id"], asset.get("name", asset["asset_id"]),
             asset.get("type", "Unknown"), asset.get("location", "Unknown"),
             asset.get("line", ""), asset.get("zone", ""))
        )
    except Exception:
        execute(
            f"""INSERT INTO assets (asset_id, name, type, location, line, zone)
                VALUES ({p},{p},{p},{p},{p},{p})
                ON CONFLICT(asset_id) DO NOTHING""",
            (asset["asset_id"], asset.get("name", asset["asset_id"]),
             asset.get("type", "Unknown"), asset.get("location", "Unknown"),
             asset.get("line", ""), asset.get("zone", ""))
        )


# ── Full file ingestion with versioning ───────────────────────

def ingest_with_version_check(filepath: str, data: dict,
                               schema_type: str) -> dict:
    """
    Wraps the ingestion pipeline with version checking.
    Returns {"status": "skipped"|"ingested", "changes": dict, "hash": str}
    """
    from pathlib import Path
    source_key = Path(filepath).name
    data_hash  = _hash(data)

    if is_unchanged(source_key, data_hash):
        return {
            "status": "skipped",
            "reason": "identical to last ingestion",
            "hash": data_hash,
            "changes": {}
        }

    # Track asset-level changes
    asset_changes = {}
    asset_ids     = []

    if "scraps" in data:  # batch format
        asset_id = f"BATCH{data.get('batch_number', '?')}"
        asset_ids.append(asset_id)
    elif "asset_id" in data:
        asset_ids.append(data["asset_id"].upper())
    elif isinstance(data, dict):
        for key in data:
            if key.startswith("track_"):
                asset_id = data.get("asset_id", "ANNOTATIONS")
                asset_ids.append(asset_id.upper())
                break

    record_version(source_key, data_hash, schema_type, asset_ids, asset_changes)

    return {
        "status": "ingested",
        "hash": data_hash,
        "asset_ids": asset_ids,
        "changes": asset_changes
    }


def get_change_summary(since_hours: int = 24) -> list:
    """
    Returns all version changes in the last N hours.
    Used for 'what changed?' queries from WhatsApp or admin dashboard.
    """
    try:
        return query(
            """SELECT source_key, schema_type, asset_ids, changes, ingested_at
               FROM core.data_versions
               WHERE ingested_at >= NOW() - INTERVAL '%s hours'
               ORDER BY ingested_at DESC""",
            (since_hours,)
        )
    except Exception:
        return []


# ── Utility ───────────────────────────────────────────────────

def _execute_compat(sql_template: str, params: tuple) -> None:
    """Try PostgreSQL %s params, fall back to SQLite ? params."""
    sql_pg = sql_template.replace("{p}", "%s").replace("{now}", "NOW()")
    try:
        execute(sql_pg, params)
    except Exception as e:
        print(f"[version_tracker] persist failed: {e}")

