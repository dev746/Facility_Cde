import uuid
from core.db import query, execute


def get_asset(asset_id: str) -> dict | None:
    rows = query("SELECT * FROM assets WHERE asset_id=?", (asset_id.upper(),))
    return rows[0] if rows else None


def get_findings(asset_id: str, limit: int = 20) -> list:
    return query(
        """SELECT * FROM findings WHERE asset_id=?
           ORDER BY confidence DESC, timestamp DESC LIMIT ?""",
        (asset_id.upper(), limit),
    )


def get_notes(asset_id: str) -> list:
    return query(
        "SELECT * FROM expert_notes WHERE asset_id=? ORDER BY timestamp DESC",
        (asset_id.upper(),),
    )


def get_summary(asset_id: str) -> dict | None:
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
    return query("SELECT * FROM assets WHERE status='active' ORDER BY asset_id")


def critical_assets() -> list:
    return query(
        """SELECT f.*, a.name, a.location, a.type, a.line
           FROM findings f
           JOIN assets a ON a.asset_id = f.asset_id
           WHERE f.severity IN ('critical','high') OR f.confidence >= 0.85
           ORDER BY f.confidence DESC, f.created_at DESC
           LIMIT 50"""
    )


def latest_inspections(limit: int = 5) -> list:
    return query(
        """SELECT f.*, a.name as asset_name
           FROM findings f
           JOIN assets a ON a.asset_id = f.asset_id
           ORDER BY f.timestamp DESC, f.created_at DESC LIMIT ?""",
        (limit,),
    )


def find_asset_by_name(text: str) -> dict | None:
    all_assets = list_assets()
    text_lower = text.lower()
    for a in all_assets:
        name_lower = a["name"].lower()
        type_lower = (a["type"] or "").lower()
        id_lower   = a["asset_id"].lower()
        if (
            id_lower in text_lower
            or any(w in text_lower for w in type_lower.split() if len(w) > 3)
            or any(w in text_lower for w in name_lower.split() if len(w) > 3)
        ):
            return a
    return None


def add_note(asset_id: str, comment: str, author: str) -> bool:
    if not get_asset(asset_id):
        return False
    execute(
        "INSERT INTO expert_notes (note_id,asset_id,comment,author) VALUES (?,?,?,?)",
        (str(uuid.uuid4()), asset_id.upper(), comment, author),
    )
    return True


def search_findings(keyword: str) -> list:
    like = f"%{keyword}%"
    return query(
        """SELECT f.*, a.name as asset_name
           FROM findings f JOIN assets a ON a.asset_id = f.asset_id
           WHERE f.object LIKE ? OR f.condition LIKE ?
           ORDER BY f.confidence DESC LIMIT 20""",
        (like, like),
    )


def get_line_status(line: str) -> list:
    return query(
        """SELECT a.*,
                  COUNT(f.finding_id) as finding_count,
                  SUM(CASE WHEN f.severity='critical' THEN 1 ELSE 0 END) as critical_count
           FROM assets a
           LEFT JOIN findings f ON f.asset_id = a.asset_id
           WHERE a.line=? OR a.location LIKE ?
           GROUP BY a.asset_id
           ORDER BY critical_count DESC, finding_count DESC""",
        (line, f"%{line}%"),
    )
