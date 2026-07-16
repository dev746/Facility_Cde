def _safe_float(v, default: float = 0.5) -> float:
    try:
        return max(0.0, min(1.0, float(v)))
    except (TypeError, ValueError):
        return default


def make_asset(asset_id, name=None, type=None, location=None,
               line=None, zone=None, meta=None) -> dict:
    aid = str(asset_id).upper().strip().replace(" ", "_")
    return {
        "asset_id": aid,
        "name":     name or aid,
        "type":     type or "Unknown",
        "location": location or "Unknown",
        "line":     line or "",
        "zone":     zone or "",
    }


def make_finding(asset_id, object=None, condition=None, confidence=1.0,
                 source="ingest", timestamp=None, raw=None) -> dict:
    conf = _safe_float(confidence)
    return {
        "asset_id":   str(asset_id).upper().strip(),
        "object":     str(object or "Unknown"),
        "condition":  str(condition or "Unknown"),
        "confidence": conf,
        "severity":   _severity(conf),
        "source":     str(source),
        "timestamp":  str(timestamp or ""),
        "raw_json":   str(raw or ""),
    }


def _severity(confidence: float) -> str:
    if confidence >= 0.90: return "critical"
    if confidence >= 0.75: return "high"
    if confidence >= 0.50: return "medium"
    return "low"
