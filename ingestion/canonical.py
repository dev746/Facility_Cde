def _safe_float(v, default: float = 0.5) -> float:
    try:
        return max(0.0, min(1.0, float(v)))
    except (TypeError, ValueError):
        return default


def find_column(df, *opts) -> str | None:
    """Find first matching column name in a DataFrame (case-agnostic helper)."""
    cols = {str(c).strip().lower(): c for c in df.columns}
    for o in opts:
        o_lower = o.strip().lower()
        if o_lower in cols:
            return cols[o_lower]
    return None



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
    from datetime import datetime, timezone
    ts = timestamp if timestamp else datetime.now(timezone.utc).isoformat()
    return {
        "asset_id":   str(asset_id).upper().strip(),
        "object":     str(object or "Unknown"),
        "condition":  str(condition or "Unknown"),
        "confidence": conf,
        "severity":   _severity(conf),
        "source":     str(source),
        "timestamp":  ts,
        "raw_json":   str(raw or ""),
    }


def _severity(confidence: float) -> str:
    if confidence >= 0.90: return "critical"
    if confidence >= 0.75: return "high"
    if confidence >= 0.50: return "medium"
    return "low"


def make_cv_detection(detection_id=None, asset_id=None, label=None, confidence=1.0, timestamp=None, raw=None) -> dict:
    return {
        "detection_id": detection_id,
        "asset_id": str(asset_id).upper().strip() if asset_id else "UNKNOWN",
        "label": str(label or "Unknown"),
        "confidence": _safe_float(confidence),
        "timestamp": timestamp,
        "raw_json": str(raw or ""),
    }


def make_cv_track(track_id=None, asset_id=None, label=None, category=None, bbox=None, centroid=None, area=None, angle=None, frame_id=None, timestamp=None, raw=None) -> dict:
    return {
        "track_id": track_id,
        "asset_id": str(asset_id).upper().strip() if asset_id else "UNKNOWN",
        "label": str(label or "Unknown"),
        "category": str(category or "Unknown"),
        "bbox": bbox,
        "centroid": centroid,
        "area": area,
        "angle": angle,
        "frame_id": frame_id,
        "timestamp": timestamp,
        "raw_json": str(raw or ""),
    }


def make_scrap_batch(batch_id=None, asset_id=None, weight_kg=None, scrap_count=None, scale_cm_per_px=None, timestamp=None, raw=None) -> dict:
    return {
        "batch_id": batch_id,
        "asset_id": str(asset_id).upper().strip() if asset_id else "UNKNOWN",
        "weight_kg": weight_kg,
        "scrap_count": scrap_count,
        "scale_cm_per_px": scale_cm_per_px,
        "timestamp": timestamp,
        "raw_json": str(raw or ""),
    }


def make_scrap(scrap_id=None, asset_id=None, shape_type=None, area_cm2=None, side_lengths=None, vertex_labels=None, raw=None) -> dict:
    return {
        "scrap_id": scrap_id,
        "asset_id": str(asset_id).upper().strip() if asset_id else "UNKNOWN",
        "shape_type": shape_type,
        "area_cm2": area_cm2,
        "side_lengths": side_lengths,
        "vertex_labels": vertex_labels,
        "raw_json": str(raw or ""),
    }


def make_geometry_shape(shape_id=None, asset_id=None, shape_type=None, area_cm2=None, side_lengths=None, vertex_labels=None, data=None) -> dict:
    return {
        "shape_id": shape_id,
        "asset_id": str(asset_id).upper().strip() if asset_id else "UNKNOWN",
        "shape_type": shape_type,
        "area_cm2": area_cm2,
        "side_lengths": side_lengths,
        "vertex_labels": vertex_labels,
        "data": data,
    }




