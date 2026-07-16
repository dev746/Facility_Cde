import uuid
import time
from pathlib import Path
from ingestion.detector import load_file, detect_json_schema, detect_excel_schema
from ingestion.normalisers import (
    normalise_batch, normalise_cv, normalise_annotations,
    normalise_finding_json, normalise_asset_json,
    normalise_assets_excel, normalise_findings_excel, normalise_batch_excel,
)
from ingestion.llm_normaliser import llm_normalise
from core.db import executemany, execute

JSON_HANDLERS = {
    "batch":       normalise_batch,
    "cv":          normalise_cv,
    "annotations": normalise_annotations,
    "tracks":      normalise_annotations,
    "finding":     normalise_finding_json,
    "asset":       normalise_asset_json,
}

EXCEL_HANDLERS = {
    "assets":   normalise_assets_excel,
    "findings": normalise_findings_excel,
    "batch":    normalise_batch_excel,
}


def _write_batch(assets: list, findings: list) -> tuple:
    if assets:
        executemany(
            """INSERT INTO assets (asset_id, name, type, location, line, zone)
               VALUES (?,?,?,?,?,?)
               ON CONFLICT(asset_id) DO UPDATE SET
               name=COALESCE(excluded.name,name),
               type=COALESCE(excluded.type,type),
               location=COALESCE(excluded.location,location),
               updated_at=datetime('now')""",
            [(a["asset_id"], a["name"], a["type"], a["location"],
              a.get("line",""), a.get("zone","")) for a in assets],
        )
    if findings:
        executemany(
            """INSERT INTO findings
               (finding_id,asset_id,object,condition,confidence,
                source,severity,timestamp,raw_json)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            [(str(uuid.uuid4()), f["asset_id"], f["object"], f["condition"],
              f["confidence"], f["source"], f.get("severity","low"),
              f["timestamp"], f["raw_json"]) for f in findings],
        )
    return len(assets), len(findings)


def _log(filename, schema_type, na, nf, status, error, duration_ms):
    execute(
        """INSERT INTO ingest_log
           (id,filename,schema_type,assets_written,findings_written,
            status,error,duration_ms)
           VALUES (?,?,?,?,?,?,?,?)""",
        (str(uuid.uuid4()), filename, schema_type, na, nf, status, error, duration_ms),
    )


def ingest_any(filepath: str) -> int:
    start    = time.time()
    filename = Path(filepath).name
    schema   = "unknown"

    try:
        ftype, data = load_file(filepath)

        if ftype == "json":
            schema  = detect_json_schema(data)
            handler = JSON_HANDLERS.get(schema)
            if not handler:
                print(f"[universal] {filename} — unknown schema, LLM fallback")
                assets, findings = llm_normalise(data)
                schema = "llm_mapped"
            else:
                assets, findings = handler(data)
        else:
            schema  = detect_excel_schema(data)
            handler = EXCEL_HANDLERS.get(schema)
            if not handler:
                print(f"[universal] {filename} — unknown Excel schema, LLM fallback")
                assets, findings = llm_normalise(data.to_dict(orient="records"))
                schema = "llm_mapped"
            else:
                assets, findings = handler(data)

        na, nf   = _write_batch(assets, findings)
        duration = int((time.time() - start) * 1000)
        _log(filename, schema, na, nf, "success", None, duration)
        print(f"[universal] {filename} ({schema}) → {na} assets, {nf} findings in {duration}ms")
        return na + nf

    except Exception as e:
        duration = int((time.time() - start) * 1000)
        _log(filename, schema, 0, 0, "failed", str(e), duration)
        raise
