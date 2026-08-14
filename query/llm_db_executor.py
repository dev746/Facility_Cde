"""
query/llm_db_executor.py
========================
LLM ↔ PostgreSQL Bridge.

Exposes the full database schema to an LLM and provides:
  - get_schema_for_llm()       → markdown schema dump ready for LLM system prompt
  - execute_readonly_query()   → safe SELECT-only query runner
  - nl_to_sql_and_execute()    → ask a plain-English question, get back rows + SQL
  - get_db_version()           → returns last build version and timestamp
"""

import json
import re
from core.db import query
from core.llm import chat_json, chat_natural


# ─── Schema description (kept in-code so LLM can read it from a function call) ─

SCHEMA_INFO = """\
# Facility CDE PostgreSQL Schema Reference
*(All tables are fully-qualified with schema prefix.)*

---
## Schema: core
| Table | Key columns |
|-------|-------------|
| core.assets | asset_id TEXT PK, name TEXT, type TEXT, location TEXT, status TEXT, line TEXT, zone TEXT, created_at, updated_at |
| core.expert_notes | note_id UUID PK, asset_id FK→core.assets, comment TEXT, author TEXT, timestamp |
| core.cross_references | ref_id UUID PK, source_schema, source_table, source_id, target_schema, target_table, target_id, relationship_type TEXT, confidence NUMERIC |
| core.schema_migrations | version TEXT PK, applied_at TIMESTAMPTZ  ← **DB build version & last updated timestamp** |
| core.findings_unified | VIEW: finding_id, asset_id, object, condition, confidence, source, timestamp, origin |
| core.asset_summary | MATVIEW: asset_id, name, type, location, cv_detection_count, scrap_batch_count, bim_element_count, note_count, last_activity_at |

---
## Schema: cv
| Table | Key columns |
|-------|-------------|
| cv.detections | detection_id UUID PK, asset_id FK, object TEXT, condition TEXT, confidence NUMERIC(4,3), source TEXT, timestamp, raw_json JSONB |
| cv.tracks | track_pk UUID PK, track_id INT, session_id TEXT, asset_id FK, label TEXT, category TEXT, class_name TEXT, frame_id INT, area NUMERIC, bbox JSONB, centroid JSONB, angle NUMERIC, saved_at |
| cv.sessions | session_id TEXT PK, asset_id FK, source TEXT |

---
## Schema: scrap
| Table | Key columns |
|-------|-------------|
| scrap.batches | batch_id TEXT PK, asset_id FK→core.assets, batch_number INT, cm_per_pixel NUMERIC, total_scraps INT, created_at |
| scrap.scraps | scrap_id UUID PK, batch_id FK→scrap.batches, piece_name TEXT, shape_type TEXT, verified_shape TEXT, vertices_count INT, area_cm2 NUMERIC |
| scrap.vertices | id SERIAL PK, scrap_id FK→scrap.scraps, label TEXT, x NUMERIC, y NUMERIC |
| scrap.side_lengths | id SERIAL PK, scrap_id FK→scrap.scraps, side_label TEXT, length_cm NUMERIC |

---
## Schema: auth
| Table | Key columns |
|-------|-------------|
| auth.users | phone TEXT PK, name TEXT, role TEXT CHECK (admin/expert/technician/viewer), is_active BOOL |
| auth.groups | group_id UUID PK, group_name TEXT, wa_group_id TEXT |
| auth.group_members | phone FK, group_id FK |

---
## Schema: bim
| Table | Key columns |
|-------|-------------|
| bim.projects | project_id UUID PK, name TEXT, ifc_schema_version TEXT |
| bim.elements | element_id UUID PK, asset_id FK, project_id FK, ifc_guid TEXT, ifc_type TEXT, name TEXT, properties JSONB |
| bim.spatial_structure | node_id UUID PK, project_id FK, parent_node_id FK, node_type TEXT (site/building/storey/space) |
| bim.relationships | id BIGSERIAL PK, project_id FK, source_element_id FK, target_element_id FK, relationship_type TEXT |

---
## Schema: ingest
| Table | Key columns |
|-------|-------------|
| ingest.files | file_id UUID PK, filename TEXT, detected_schema TEXT, status TEXT, ingested_at TIMESTAMPTZ |

---
## Key views
- **core.findings_unified** – union of cv.detections + cv.tracks + scrap.scraps + geometry.shapes + bim.elements. Use this to search across all data.
- **core.asset_summary** – pre-aggregated counts per asset. Fast for dashboard-style queries.
- **core.cross_references_bidirectional** – both directions of cross-schema links.

---
## DB build version
The `core.schema_migrations` table records every build run with `version` and `applied_at`.
The last row where version LIKE 'db_build_%' is the current build version and its last updated timestamp.
"""


def get_schema_for_llm() -> str:
    """Returns full schema documentation for inclusion in LLM system prompt."""
    return SCHEMA_INFO


def get_db_version() -> dict:
    """
    Returns the last DB build version and its applied_at timestamp.
    This is the 'last updated' record written at the end of build_correlated_database.py.
    """
    rows = query(
        """SELECT version, applied_at
           FROM core.schema_migrations
           WHERE version LIKE %s
           ORDER BY applied_at DESC
           LIMIT 1""",
        ("db_build_%",)
    )
    if rows:
        return {
            "version": rows[0]["version"],
            "last_updated_at": str(rows[0]["applied_at"]),
        }
    return {"version": "unknown", "last_updated_at": "unknown"}


def execute_readonly_query(sql: str, params: tuple = ()) -> list | str:
    """
    Executes a read-only SQL query on the live database.
    Only SELECT statements are allowed for safety.
    Returns a list of row dicts, or an error string.
    """
    cleaned = sql.strip().lower()
    # Strip leading comments
    cleaned = re.sub(r"^--.*\n?", "", cleaned, flags=re.MULTILINE).strip()
    if not cleaned.startswith("select"):
        return "Error: Only SELECT queries are permitted for LLM database access."
    try:
        return query(sql, params)
    except Exception as e:
        return f"Error executing query: {str(e)}"


_NL2SQL_SYSTEM = """\
You are an expert SQL generator for a PostgreSQL database called Facility CDE.

DATABASE SCHEMA:
""" + SCHEMA_INFO + """

Rules:
1. Generate only ONE valid PostgreSQL SELECT statement.
2. Always use fully-qualified table names (e.g. core.assets, cv.detections).
3. LIMIT results to 50 rows unless the user explicitly asks for more.
4. Return ONLY a JSON object: {"sql": "<your SELECT statement>", "explanation": "<one sentence>"}
5. Do NOT add markdown code fences or any text outside the JSON.
"""


def nl_to_sql_and_execute(question: str) -> dict:
    """
    Accepts a natural-language question and:
      1. Asks the LLM to generate a safe SELECT SQL query.
      2. Executes the query against the live PostgreSQL database.
      3. Returns both the generated SQL and the result rows.

    Returns:
      {
        "question": str,
        "sql": str,
        "explanation": str,
        "rows": list[dict] | str,
        "row_count": int,
        "db_version": dict,
      }
    """
    db_ver = get_db_version()

    try:
        raw = chat_json(
            system=_NL2SQL_SYSTEM,
            user=f"Question: {question}",
            max_tokens=400,
        )
        parsed = json.loads(raw)
        sql = parsed.get("sql", "").strip()
        explanation = parsed.get("explanation", "")
    except Exception as e:
        # Distinguish rate-limit / quota errors from real bugs
        err_str = str(e).lower()
        if "429" in err_str or "rate" in err_str or "quota" in err_str:
            llm_err = "llm_rate_limited"
        else:
            llm_err = f"LLM failed: {e}"
        return {
            "question": question,
            "sql": "",
            "explanation": "",
            "rows": [],
            "llm_error": llm_err,
            "row_count": 0,
            "db_version": db_ver,
        }

    rows = execute_readonly_query(sql)
    return {
        "question": question,
        "sql": sql,
        "explanation": explanation,
        "rows": rows if isinstance(rows, list) else [],
        "error": rows if isinstance(rows, str) else None,
        "row_count": len(rows) if isinstance(rows, list) else 0,
        "db_version": db_ver,
    }


def ask_db(question: str, language: str = "english") -> str:
    """
    Full pipeline: NL question → SQL → DB rows → NL answer.
    Suitable for direct use from WhatsApp or terminal chat.
    """
    result = nl_to_sql_and_execute(question)

    # LLM rate-limited — return friendly message with direct command hints
    if result.get("llm_error") == "llm_rate_limited":
        return (
            "⏳ *AI assistant is temporarily unavailable* (daily limit reached).\n\n"
            "You can still use direct commands:\n"
            "• *list* — all assets\n"
            "• *summary M14* — asset overview\n"
            "• *findings M14* — defects\n"
            "• *critical* — critical findings\n"
            "• *latest* — recent inspections\n"
            "• *help* — all commands"
        )

    if result.get("llm_error"):
        return f"❌ Could not query database: {result['llm_error']}"

    if not result["rows"]:
        return f"📭 No records found for: *{question}*"

    system = (
        "You are a helpful AI assistant for an industrial facility. "
        "Answer the user's question using ONLY the database rows provided. "
        "Be concise. Use WhatsApp formatting (*bold*, bullet points)."
    )
    context = {
        "question": question,
        "sql_used": result["sql"],
        "rows": result["rows"][:20],  # Cap context size
        "db_version": result["db_version"],
    }
    try:
        reply = chat_natural(
            system=system,
            user=f"User question: {question}",
            language=language,
            context_data=context,
            temperature=0.2,
            max_tokens=600,
        )
        return reply or f"Found {result['row_count']} records. SQL: {result['sql']}"
    except Exception:
        # LLM down for formatting too — return raw rows as plain text
        lines = [f"📊 *Results for:* {question}\n"]
        for r in result["rows"][:10]:
            lines.append("  • " + ", ".join(f"{k}: {v}" for k, v in r.items()))
        if result["row_count"] > 10:
            lines.append(f"_...{result['row_count'] - 10} more rows_")
        return "\n".join(lines)
