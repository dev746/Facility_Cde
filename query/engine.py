import re
import uuid
from core.db import query, execute


def get_asset(asset_id: str) -> dict | None:
    rows = query("SELECT * FROM core.assets WHERE asset_id = %s", (asset_id.upper(),))
    return rows[0] if rows else None


def get_findings(asset_id: str, limit: int = 20) -> list:
    return query(
        "SELECT * FROM core.findings_unified WHERE asset_id = %s ORDER BY timestamp DESC LIMIT %s",
        (asset_id.upper(), limit),
    )


def get_notes(asset_id: str) -> list:
    return query(
        "SELECT * FROM core.expert_notes WHERE asset_id = %s ORDER BY timestamp DESC",
        (asset_id.upper(),),
    )


def get_asset_summary(asset_id: str) -> dict | None:
    try:
        rows = query("SELECT * FROM core.asset_summary WHERE asset_id = %s", (asset_id.upper(),))
        return rows[0] if rows else None
    except Exception:
        return None


def get_summary(asset_id: str) -> dict | None:
    summary_row = get_asset_summary(asset_id)
    if summary_row:
        return summary_row

    asset = get_asset(asset_id)
    if not asset:
        return None

    findings = get_findings(asset_id)
    notes    = get_notes(asset_id)

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = f.get("severity", "low")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    top = max(findings, key=lambda f: f.get("confidence") or 0) if findings else None

    return {
        "asset":           asset,
        "finding_count":   len(findings),
        "note_count":      len(notes),
        "top_finding":     top,
        "severity_counts": severity_counts,
        "critical":        severity_counts["critical"] > 0,
        "latest_note":     notes[0] if notes else None,
    }


def list_assets() -> list:
    return query("SELECT * FROM core.assets ORDER BY asset_id")


def critical_assets() -> list:
    return query(
        "SELECT * FROM core.findings_unified WHERE confidence >= 0.85 ORDER BY timestamp DESC"
    )


def latest_inspections(limit: int = 5) -> list:
    return query(
        """SELECT f.*, a.name as asset_name
           FROM core.findings_unified f
           JOIN core.assets a ON a.asset_id = f.asset_id
           ORDER BY f.timestamp DESC LIMIT %s""",
        (limit,),
    )


def find_asset_by_name(name: str):
    try:
        return query("SELECT * FROM core.find_asset_by_name(%s)", (name,))
    except Exception:
        return []


def add_note(asset_id: str, comment: str, author: str) -> bool:
    if not get_asset(asset_id):
        return False
    execute(
        "INSERT INTO core.expert_notes (note_id, asset_id, comment, author) VALUES (%s, %s, %s, %s)",
        (str(uuid.uuid4()), asset_id.upper(), comment, author),
    )
    return True


def search_findings(keyword: str) -> list:
    """Search findings by keyword — covers object, condition, notes, and asset type."""
    kw = f"%{keyword}%"
    try:
        rows = query(
            """SELECT f.*, a.name as asset_name, a.type as asset_type
               FROM core.findings_search f
               JOIN core.assets a ON a.asset_id = f.asset_id
               WHERE f.search_vector @@ plainto_tsquery('english', %s)
                  OR f.object ILIKE %s OR f.condition ILIKE %s
                  OR a.name ILIKE %s OR a.type ILIKE %s
               ORDER BY f.confidence DESC LIMIT 20""",
            (keyword, kw, kw, kw, kw),
        )
        if rows:
            return rows
    except Exception:
        pass

    # Fallback: findings_unified + asset name/type + expert notes
    findings = query(
        """SELECT f.*, a.name as asset_name, a.type as asset_type
           FROM core.findings_unified f
           JOIN core.assets a ON a.asset_id = f.asset_id
           WHERE f.object ILIKE %s OR f.condition ILIKE %s
              OR a.name ILIKE %s OR a.type ILIKE %s
           ORDER BY f.confidence DESC LIMIT 20""",
        (kw, kw, kw, kw),
    )
    notes = query(
        """SELECT n.asset_id, n.comment as condition, n.author as object,
                  n.timestamp, a.name as asset_name, a.type as asset_type,
                  'note' as source, 1.0 as confidence
           FROM core.expert_notes n
           JOIN core.assets a ON a.asset_id = n.asset_id
           WHERE n.comment ILIKE %s OR a.name ILIKE %s OR a.type ILIKE %s
           ORDER BY n.timestamp DESC LIMIT 10""",
        (kw, kw, kw),
    )
    return findings + notes


def get_line_status(line: str) -> list:
    return query(
        """SELECT a.*,
                  COUNT(f.finding_id) as finding_count,
                  SUM(CASE WHEN f.confidence >= 0.85 THEN 1 ELSE 0 END) as critical_count
           FROM core.assets a
           LEFT JOIN core.findings_unified f ON f.asset_id = a.asset_id
           WHERE a.line = %s OR a.location ILIKE %s
           GROUP BY a.asset_id, a.name, a.type, a.location, a.line, a.zone, a.status, a.created_at, a.updated_at
           ORDER BY critical_count DESC, finding_count DESC""",
        (line, f"%{line}%"),
    )


def resolve_asset(raw_text: str) -> dict | None:
    """
    Robust, fast asset resolver:
    1. Direct exact asset_id check
    2. Regex code pattern (M14, BATCH1, LINE3)
    3. Single optimized query — fuzzy ILIKE across name/location/asset_id
    """
    if not raw_text or not raw_text.strip():
        return None

    text = raw_text.strip()

    # 1. Direct ID match
    asset = get_asset(text)
    if asset:
        return asset

    from query.intent import ASSET_PATTERN, extract_asset_name, FILLER_WORDS
    match = ASSET_PATTERN.search(text)
    if match:
        asset = get_asset(match.group(1).upper())
        if asset:
            return asset

    # Extract clean name phrase
    clean_name = extract_asset_name(text) or text

    # 2. Combined single query — search name, location, asset_id AND type
    try:
        rows = query(
            """SELECT * FROM core.assets
               WHERE (name ILIKE %s OR location ILIKE %s OR asset_id ILIKE %s OR type ILIKE %s)
               ORDER BY
                 CASE WHEN asset_id ILIKE %s THEN 1
                      WHEN name ILIKE %s THEN 2
                      WHEN type ILIKE %s THEN 3
                      ELSE 4 END
               LIMIT 1""",
            (f"%{clean_name}%", f"%{clean_name}%", f"%{clean_name}%", f"%{clean_name}%",
             clean_name, f"%{clean_name}%", f"%{clean_name}%"),
        )
        if rows:
            return rows[0]
    except Exception:
        pass

    # 3. Word-by-word fallback — try each significant word individually
    #    Handles "lathe machine" -> matches type "CNC Lathe"
    significant_words = [
        w for w in re.findall(r'\w+', text, re.UNICODE)
        if len(w) >= 3 and w.lower() not in FILLER_WORDS
    ]
    for word in significant_words:
        try:
            rows = query(
                """SELECT * FROM core.assets
                   WHERE (name ILIKE %s OR type ILIKE %s OR location ILIKE %s)
                   ORDER BY
                     CASE WHEN type ILIKE %s THEN 1
                          WHEN name ILIKE %s THEN 2
                          ELSE 3 END
                   LIMIT 1""",
                (f"%{word}%", f"%{word}%", f"%{word}%",
                 f"%{word}%", f"%{word}%"),
            )
            if rows:
                return rows[0]
        except Exception:
            pass

    return None


def get_cross_references(asset_id: str) -> list:
    """Pulls cross-functional references linked to this asset across schemas."""
    try:
        return query(
            "SELECT * FROM core.cross_references WHERE source_id = %s OR target_id = %s",
            (asset_id.upper(), asset_id.upper()),
        )
    except Exception:
        return []
