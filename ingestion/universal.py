"""
ingestion/universal_updated.py — Ingestion with version tracking.

Replace your existing ingestion/universal.py with this file.

Changes:
  - Wraps every ingest call with version_tracker.ingest_with_version_check()
  - Skips files whose content hash matches last ingestion (idempotent)
  - Uses upsert_asset_with_diff() for field-level change tracking
  - Logs version history to data_versions table
"""
import uuid
import time
from pathlib import Path

from ingestion.detector import (
    load_file, detect_json_schema,
    detect_excel_schema, detect_bim_schema, is_cobie
)
from ingestion.normalisers import (
    normalise_batch, normalise_cv, normalise_annotations,
    normalise_finding_json, normalise_asset_json, normalise_geometry,
    normalise_assets_excel, normalise_findings_excel, normalise_batch_excel,
)
from ingestion.bim_ingest import normalise_bim_json, normalise_ifc_json, normalise_cobie
from ingestion.llm_normaliser import llm_normalise
from ingestion.version_tracker import (
    ingest_with_version_check, record_version, upsert_asset_with_diff
)
from core.db import executemany, execute

JSON_HANDLERS = {
    "batch":            normalise_batch,
    "cv":               normalise_cv,
    "annotations":      normalise_annotations,
    "tracks":           normalise_annotations,
    "geometry":         normalise_geometry,
    "finding":          normalise_finding_json,
    "asset":            normalise_asset_json,
    "bim_json":         normalise_bim_json,
    "ifc_json":         normalise_ifc_json,
    "ifc_json_wrapped": normalise_ifc_json,
}

EXCEL_HANDLERS = {
    "assets":   normalise_assets_excel,
    "findings": normalise_findings_excel,
    "batch":    normalise_batch_excel,
}


def _write_batch(assets: list, findings: list) -> tuple:
    """
    Write assets using diff-aware upsert, findings in bulk.
    Returns (assets_written, findings_written).
    """
    na = 0
    for asset in assets:
        result = upsert_asset_with_diff(asset)
        if result["action"] in ("created", "updated"):
            na += 1

    nf = 0
    if findings:
        try:
            executemany(
                """INSERT INTO cv.detections
                   (detection_id, asset_id, object, condition, confidence,
                    source, timestamp, raw_json)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT DO NOTHING""",
                [(str(uuid.uuid4()), f["asset_id"], f["object"],
                  f["condition"], f["confidence"], f["source"],
                  f["timestamp"], f["raw_json"]) for f in findings]
            )
            nf = len(findings)
        except Exception as e:
            print(f"[universal] findings write failed: {e}")

    return na, nf


def _log_ingest(filename, schema_type, na, nf, status, error, duration_ms):
    try:
        execute(
            """INSERT INTO ingest.files
               (id,filename,schema_type,assets_written,findings_written,
                status,error,duration_ms)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (str(uuid.uuid4()), filename, schema_type,
             na, nf, status, error, duration_ms)
        )
    except Exception:
        try:
            execute(
                """INSERT INTO ingest_log
                   (id,filename,schema_type,assets_written,findings_written,
                    status,error,duration_ms)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (str(uuid.uuid4()), filename, schema_type,
                 na, nf, status, error, duration_ms)
            )
        except Exception:
            pass


def ingest_any(filepath: str) -> int:
    start    = time.time()
    filename = Path(filepath).name
    schema   = "unknown"

    try:
        ftype, data = load_file(filepath)

        if ftype == "json":
            # Version check — skip if identical to last ingestion
            version_result = ingest_with_version_check(filepath, data, schema)
            if version_result["status"] == "skipped":
                print(f"[universal] {filename} — skipped (unchanged since last ingestion)")
                duration = int((time.time() - start) * 1000)
                _log_ingest(filename, "skipped", 0, 0, "skipped",
                            "identical hash", duration)
                return 0

            # Detect schema and normalise
            bim_schema = detect_bim_schema(data)
            if bim_schema != "unknown":
                schema  = bim_schema
                handler = JSON_HANDLERS[schema]
            else:
                schema  = detect_json_schema(data)
                handler = JSON_HANDLERS.get(schema)

            if handler:
                assets, findings = handler(data)
            else:
                print(f"[universal] {filename} — unknown schema, LLM fallback")
                assets, findings = llm_normalise(data)
                schema = "llm_mapped"

        else:  # excel / csv
            # Version check for tabular data using raw dict
            version_result = ingest_with_version_check(
                filepath, data.to_dict(orient="records"), schema
            )
            if version_result["status"] == "skipped":
                print(f"[universal] {filename} — skipped (unchanged)")
                _log_ingest(filename, "skipped", 0, 0, "skipped",
                            "identical hash", int((time.time()-start)*1000))
                return 0

            if is_cobie(filepath):
                assets, findings = normalise_cobie(filepath)
                schema = "cobie"
            else:
                schema  = detect_excel_schema(data)
                handler = EXCEL_HANDLERS.get(schema)
                if handler:
                    assets, findings = handler(data)
                else:
                    print(f"[universal] {filename} — unknown Excel schema, LLM fallback")
                    assets, findings = llm_normalise(data.to_dict(orient="records"))
                    schema = "llm_mapped"

        na, nf   = _write_batch(assets, findings)
        duration = int((time.time() - start) * 1000)

        # Record version with asset IDs
        asset_ids = [a["asset_id"] for a in assets]
        record_version(filename, version_result.get("hash",""), schema, asset_ids, {})

        _log_ingest(filename, schema, na, nf, "success", None, duration)
        print(f"[universal] {filename} ({schema}) → "
              f"{na} assets, {nf} findings [{duration}ms]")
        return na + nf

    except Exception as e:
        duration = int((time.time() - start) * 1000)
        _log_ingest(filename, schema, 0, 0, "failed", str(e), duration)
        raise


def refresh_views() -> None:
    """Refresh database materialized views (best-effort)."""
    from core.db import execute
    try:
        execute("SELECT core.refresh_cross_functional_views()")
    except Exception:
        try:
            execute("REFRESH MATERIALIZED VIEW core.asset_summary")
            execute("REFRESH MATERIALIZED VIEW core.findings_search")
        except Exception as e:
            print(f"[universal] refresh_views failed: {e}")

