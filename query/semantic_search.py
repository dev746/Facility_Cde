"""
query/semantic_search.py — Relational DB-grounded semantic search.

The relational database is the single source of truth at runtime.
This module ensures any keyword a user types — no matter how it was
saved in the DB — resolves to actual records by:

  1. Exact match (asset_id, name)
  2. ILIKE / LIKE partial match on name, type, location, condition, object
  3. Full-text search across findings condition + object columns
  4. LLM-assisted synonym expansion: maps "pump" → queries for
     "hydraulic", "centrifugal", "coolant pump" etc from DB vocabulary
  5. Fallback: return closest matches by token overlap

The LLM never answers from memory — it only interprets and reformulates
queries, and the DB returns all actual data.
"""
import re
from typing import Optional
from core.db import query
from core.llm import chat_json
import json

# Common industrial synonyms for keyword expansion
SYNONYM_MAP = {
    "pump":       ["hydraulic", "coolant", "suction", "centrifugal", "pump"],
    "motor":      ["drive", "motor", "actuator", "servo"],
    "belt":       ["conveyor", "belt", "chain", "drive belt"],
    "press":      ["hydraulic press", "punch press", "stamping"],
    "lathe":      ["cnc", "lathe", "turning", "spindle"],
    "bearing":    ["bearing", "roller", "ball bearing", "bushing"],
    "seal":       ["seal", "gasket", "o-ring", "packing"],
    "crack":      ["crack", "fracture", "break", "fissure", "damage"],
    "leak":       ["leak", "seepage", "drip", "overflow"],
    "vibration":  ["vibration", "oscillation", "tremor", "shake"],
    "overheating":["overheat", "thermal", "heat", "temperature", "hot"],
    "wear":       ["wear", "erosion", "abrasion", "degradation"],
}


def _like_param(keyword: str) -> str:
    return f"%{keyword.strip()}%"


def _try_pg_then_sqlite(sql_pg: str, sql_sq: str, params: tuple) -> list:
    """Try PostgreSQL, fall back to SQLite."""
    try:
        return query(sql_pg, params)
    except Exception:
        return query(sql_sq, params)


def search_assets_by_keyword(keyword: str, limit: int = 10) -> list:
    """
    Search assets by any keyword against name, type, and location.
    Uses ILIKE (PostgreSQL) / LIKE (SQLite) for case-insensitive partial match.
    Also checks synonyms from SYNONYM_MAP.
    """
    keyword = keyword.strip()
    synonyms = _get_synonyms(keyword)

    results = {}

    for term in synonyms:
        like = _like_param(term)
        rows = _try_pg_then_sqlite(
            """SELECT asset_id, name, type, location, status
               FROM core.assets
               WHERE name ILIKE %s OR type ILIKE %s OR location ILIKE %s
               LIMIT %s""",
            """SELECT asset_id, name, type, location, status
               FROM assets
               WHERE name LIKE ? OR type LIKE ? OR location LIKE ?
               LIMIT ?""",
            (like, like, like, limit)
        )
        for r in rows:
            results[r["asset_id"]] = dict(r)

    return list(results.values())[:limit]


def search_findings_by_keyword(keyword: str, asset_id: str = None,
                                limit: int = 20) -> list:
    """
    Full-coverage findings search:
    - Exact and partial match on object and condition columns
    - Synonym expansion
    - Optional asset_id filter
    """
    keyword  = keyword.strip()
    synonyms = _get_synonyms(keyword)
    results  = {}

    for term in synonyms:
        like = _like_param(term)

        if asset_id:
            rows = _try_pg_then_sqlite(
                """SELECT f.*, a.name as asset_name
                   FROM core.findings_unified f
                   JOIN core.assets a ON a.asset_id = f.asset_id
                   WHERE f.asset_id = %s
                     AND (f.object ILIKE %s OR f.condition ILIKE %s)
                   ORDER BY f.confidence DESC LIMIT %s""",
                """SELECT f.*, a.name as asset_name
                   FROM findings f
                   JOIN assets a ON a.asset_id = f.asset_id
                   WHERE f.asset_id = ?
                     AND (f.object LIKE ? OR f.condition LIKE ?)
                   ORDER BY f.confidence DESC LIMIT ?""",
                (asset_id.upper(), like, like, limit)
            )
        else:
            rows = _try_pg_then_sqlite(
                """SELECT f.*, a.name as asset_name
                   FROM core.findings_unified f
                   JOIN core.assets a ON a.asset_id = f.asset_id
                   WHERE f.object ILIKE %s OR f.condition ILIKE %s
                   ORDER BY f.confidence DESC LIMIT %s""",
                """SELECT f.*, a.name as asset_name
                   FROM findings f
                   JOIN assets a ON a.asset_id = f.asset_id
                   WHERE f.object LIKE ? OR f.condition LIKE ?
                   ORDER BY f.confidence DESC LIMIT ?""",
                (like, like, limit)
            )

        for r in rows:
            fid = r.get("finding_id", r.get("id", ""))
            results[fid] = dict(r)

    return list(results.values())[:limit]


def resolve_any_query(text: str, limit: int = 10) -> dict:
    """
    Top-level resolver: given ANY text, returns the best-matching
    assets and findings from the DB.

    Priority order:
      1. Direct asset_id match (e.g. "M14")
      2. Asset name/type/location match
      3. Findings object/condition match
      4. LLM-expanded synonym search
      5. Token overlap fallback
    """
    text = text.strip()

    # 1. Direct asset_id check
    asset_pattern = re.compile(r'\b([A-Z]{1,3}\d{1,4})\b', re.IGNORECASE)
    match = asset_pattern.search(text)
    if match:
        aid = match.group(1).upper()
        direct = _try_pg_then_sqlite(
            "SELECT * FROM core.assets WHERE asset_id = %s",
            "SELECT * FROM assets WHERE asset_id = ?",
            (aid,)
        )
        if direct:
            return {
                "match_type": "direct_id",
                "assets": [dict(direct[0])],
                "findings": search_findings_by_keyword(text, asset_id=aid, limit=limit),
            }

    # 2. Keyword-based asset search
    assets = search_assets_by_keyword(text, limit=limit)

    # 3. Findings search
    findings = search_findings_by_keyword(text, limit=limit)

    # 4. If nothing found, use LLM to expand the query vocabulary
    if not assets and not findings:
        expanded = _llm_expand_keywords(text)
        for kw in expanded:
            assets   += search_assets_by_keyword(kw, limit=5)
            findings += search_findings_by_keyword(kw, limit=5)

    # Deduplicate
    seen_a, seen_f = set(), set()
    unique_assets   = []
    unique_findings = []
    for a in assets:
        if a["asset_id"] not in seen_a:
            seen_a.add(a["asset_id"])
            unique_assets.append(a)
    for f in findings:
        fid = f.get("finding_id", f.get("id", ""))
        if fid not in seen_f:
            seen_f.add(fid)
            unique_findings.append(f)

    match_type = "keyword" if (unique_assets or unique_findings) else "none"

    return {
        "match_type": match_type,
        "assets":     unique_assets[:limit],
        "findings":   unique_findings[:limit],
    }


def _get_synonyms(keyword: str) -> list:
    """Return keyword + any known synonyms."""
    keyword_lower = keyword.lower()
    synonyms      = [keyword]
    for key, terms in SYNONYM_MAP.items():
        if key in keyword_lower or any(t in keyword_lower for t in terms):
            synonyms.extend(terms)
    return list(dict.fromkeys(synonyms))  # deduplicate preserving order


def _llm_expand_keywords(text: str) -> list:
    """
    Ask the LLM to suggest alternative search terms for a query
    that returned no DB results. The LLM only suggests terms —
    the DB does the actual lookup.
    """
    system = """You are a keyword expander for an industrial facility database.
The user searched for something but no results were found.
Suggest 3-5 alternative search terms that might find relevant records.
These should be industrial/technical synonyms or related terms.
Reply ONLY with a JSON array of strings. Example: ["bearing","roller","bushing"]"""

    try:
        raw     = chat_json(system, f"No results for: '{text}'. Suggest alternatives.", max_tokens=80)
        raw     = raw.strip().lstrip("```json").rstrip("```").strip()
        terms   = json.loads(raw)
        return [t for t in terms if isinstance(t, str)][:5]
    except Exception:
        # Simple token fallback
        return [w for w in text.lower().split() if len(w) > 3]


def _try_pg_then_sqlite(sql_pg, sql_sq, params):
    try:
        return query(sql_pg, params)
    except Exception:
        return query(sql_sq, params)
