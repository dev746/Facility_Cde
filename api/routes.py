"""
REST API for structured data access.

Endpoints:
  GET /api/asset/{asset_id}              → full asset record
  GET /api/assets                        → list assets (optional ?line=, ?type=)
  GET /api/findings/{asset_id}           → all findings for asset
  GET /api/notes/{asset_id}              → expert notes for asset
  GET /api/telemetry/{asset_id}          → latest telemetry readings
  POST /api/telemetry                    → ingest a telemetry reading programmatically
  GET /api/summary/{asset_id}            → full summary (asset + findings + notes)
  GET /api/ingest/log                    → recent ingestion log entries
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter()


def _check_api_key(x_api_key: str = Header(default="")):
    """Simple API key auth for programmatic access."""
    expected = os.getenv("API_KEY", "")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# ── Asset endpoints ───────────────────────────────────────────

@router.get("/asset/{asset_id}")
def get_asset(asset_id: str, _=Depends(_check_api_key)):
    from query.engine import get_asset as _get
    asset = _get(asset_id.upper())
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return {"status": "ok", "data": asset}


@router.get("/findings/{asset_id}")
def get_findings(asset_id: str, limit: int = 50,
                 severity: str = None, _=Depends(_check_api_key)):
    from query.engine import get_findings as _get_findings
    rows = _get_findings(asset_id, limit=limit)
    if severity:
        rows = [r for r in rows if r.get("severity") == severity]
    return {"status": "ok", "asset_id": asset_id.upper(),
            "count": len(rows), "data": rows}


@router.get("/notes/{asset_id}")
def get_notes(asset_id: str, _=Depends(_check_api_key)):
    from query.engine import get_notes as _get_notes
    rows = _get_notes(asset_id)
    return {"status": "ok", "asset_id": asset_id.upper(),
            "count": len(rows), "data": rows}


@router.get("/summary/{asset_id}")
def get_summary(asset_id: str, _=Depends(_check_api_key)):
    from query.engine import get_summary as _get
    summary = _get(asset_id.upper())
    if not summary:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return {"status": "ok", "data": summary}


@router.get("/assets")
def list_assets(line: str = None, type: str = None,
                _=Depends(_check_api_key)):
    from query.engine import list_assets as _list_assets
    rows = _list_assets()
    if line:
        line_lower = line.lower()
        rows = [r for r in rows if line_lower in (r.get("line") or "").lower()
                                or line_lower in (r.get("location") or "").lower()]
    if type:
        type_lower = type.lower()
        rows = [r for r in rows if type_lower in (r.get("type") or "").lower()]
    return {"status": "ok", "count": len(rows), "data": rows}


# ── Telemetry endpoints ───────────────────────────────────────

class TelemetryPayload(BaseModel):
    asset_id: str
    metric:   str
    value:    float
    unit:     Optional[str] = ""
    source:   Optional[str] = "api"


@router.post("/telemetry")
def ingest_telemetry(payload: TelemetryPayload, _=Depends(_check_api_key)):
    """Any module can POST structured telemetry directly."""
    from tools.telemetry import store_reading
    from tools.calculator import check_threshold
    from core.db import query

    store_reading(payload.asset_id, payload.metric,
                  payload.value, payload.unit, payload.source)

    rows       = query("SELECT type FROM core.assets WHERE asset_id = %s",
                       (payload.asset_id.upper(),))
    asset_type = rows[0]["type"] if rows else "default"
    check      = check_threshold(payload.value, payload.metric, asset_type)

    return {
        "status":    "ok",
        "stored":    True,
        "threshold": check,
    }


@router.get("/telemetry/{asset_id}")
def get_telemetry(asset_id: str, metric: str = None,
                  limit: int = 50, _=Depends(_check_api_key)):
    from core.db import query
    from tools.calculator import analyse_readings

    sql    = "SELECT * FROM scrap.batches WHERE asset_id = %s"
    params = [asset_id.upper()]
    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    rows = query(sql, tuple(params))

    by_metric: dict = {}
    for r in rows:
        by_metric.setdefault(r["metric"], []).append(r["value"])

    analysis = {}
    for m, vals in by_metric.items():
        res = analyse_readings(vals, m, asset_id)
        analysis[m] = {
            "mean":   res["mean"],
            "min":    res["min"],
            "max":    res["max"],
            "trend":  res["trend"],
            "status": res["status"],
        }

    return {
        "status":   "ok",
        "asset_id": asset_id.upper(),
        "readings": rows,
        "analysis": analysis,
    }


# ── Ingestion log ─────────────────────────────────────────────

@router.get("/ingest/log")
def ingest_log(limit: int = 20, _=Depends(_check_api_key)):
    from core.db import query
    rows = query(
        "SELECT * FROM ingest.files ORDER BY ingested_at DESC LIMIT %s", (limit,)
    )
    return {"status": "ok", "data": rows}


# ── LLM Database Access endpoints ─────────────────────────────

@router.get("/db/schema")
def db_schema(_=Depends(_check_api_key)):
    """Returns the full PostgreSQL schema reference document for LLM context injection."""
    from query.llm_db_executor import get_schema_for_llm
    return {"status": "ok", "schema": get_schema_for_llm()}


@router.get("/db/version")
def db_version(_=Depends(_check_api_key)):
    """Returns the last DB build version and its last_updated_at timestamp."""
    from query.llm_db_executor import get_db_version
    ver = get_db_version()
    return {"status": "ok", **ver}


class DbQueryPayload(BaseModel):
    question: Optional[str] = None   # Natural language question (LLM generates SQL)
    sql: Optional[str] = None         # Raw SELECT SQL (bypasses LLM SQL generation)
    language: Optional[str] = "english"


@router.post("/db/query")
def db_query(payload: DbQueryPayload, _=Depends(_check_api_key)):
    """
    LLM database query endpoint.

    Supply either:
      - `question` (str)  → LLM converts to SQL, executes, returns rows + NL answer
      - `sql` (str)       → Executes raw SELECT directly, returns rows (no LLM involved)

    Returns:
      {
        "status": "ok",
        "sql": str,          # The SQL that was executed
        "explanation": str,  # One-sentence explanation of what the SQL does
        "rows": [...],       # Result rows as list of dicts
        "row_count": int,
        "nl_answer": str,    # Natural-language summary (only when question is supplied)
        "db_version": {...}, # Build version + last_updated_at
      }
    """
    from query.llm_db_executor import (
        nl_to_sql_and_execute, execute_readonly_query, ask_db, get_db_version
    )

    if payload.sql:
        # Raw SQL path — LLM is not involved
        rows = execute_readonly_query(payload.sql)
        return {
            "status": "ok",
            "sql": payload.sql,
            "explanation": "Raw SQL query provided by caller.",
            "rows": rows if isinstance(rows, list) else [],
            "error": rows if isinstance(rows, str) else None,
            "row_count": len(rows) if isinstance(rows, list) else 0,
            "nl_answer": None,
            "db_version": get_db_version(),
        }

    if payload.question:
        # NL → SQL → rows → NL answer path
        result = nl_to_sql_and_execute(payload.question)
        nl_answer = ask_db(payload.question, language=payload.language or "english")
        return {
            "status": "ok",
            **result,
            "nl_answer": nl_answer,
        }

    raise HTTPException(
        status_code=422,
        detail="Provide either 'question' (natural language) or 'sql' (raw SELECT)."
    )
