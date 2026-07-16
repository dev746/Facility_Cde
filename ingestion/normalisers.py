import json
from ingestion.canonical import make_asset, make_finding


# ── JSON normalisers ──────────────────────────────────────────

def normalise_batch(data: dict) -> tuple:
    assets, findings = [], []
    batch_id = f"BATCH{data['batch_number']}"
    scale    = data.get("cm_per_pixel", 0)
    total    = data.get("total_scraps", 0)

    assets.append(make_asset(
        asset_id=batch_id,
        name=f"Batch {data['batch_number']}",
        type="scrap_batch",
        location=f"{total} scraps | {scale:.4f} cm/px",
    ))

    for scrap in data.get("scraps", []):
        sides     = scrap.get("side_lengths_cm", {})
        area      = scrap.get("area_cm2", 0)
        stype     = scrap.get("shape_type", "unknown")
        name      = scrap.get("piece_name", "unknown")
        verts     = scrap.get("vertex_labels", {})
        sides_str = ", ".join(f"{k}:{v}cm" for k, v in sides.items())
        verts_str = ", ".join(f"{k}:{v}" for k, v in list(verts.items())[:4])

        findings.append(make_finding(
            asset_id=batch_id,
            object=f"{name} ({stype})",
            condition=f"Area:{area}cm² | Sides:{sides_str} | Vertices:{verts_str}",
            confidence=1.0,
            source="cv_batch",
            raw=json.dumps(scrap),
        ))

    return assets, findings


def normalise_annotations(data: dict) -> tuple:
    assets, findings = [], []
    session_id = (
        str(data.get("asset_id", data.get("session_id", "ANNOTATIONS"))).upper()
    )

    assets.append(make_asset(
        asset_id=session_id,
        name=f"Tracking Session {session_id}",
        type="cv_tracking",
        location=data.get("location", "Unknown"),
    ))

    for key, track in data.items():
        if not (isinstance(track, dict) and key.startswith("track_")):
            continue
        track_id = track.get("track_id", key)
        label    = track.get("label") or track.get("class_name", "Unknown")
        category = track.get("category", "Unknown")
        area     = track.get("area", 0)
        bbox     = track.get("bbox", [])
        centroid = track.get("centroid", [])
        angle    = track.get("angle", 0)
        frame_id = track.get("frame_id", "")
        saved_at = track.get("saved_at", "")
        notes    = track.get("notes", "")

        condition = (
            f"Category:{category} | Area:{area}px² | "
            f"Angle:{angle}° | Frame:{frame_id} | "
            f"BBox:{bbox} | Centroid:{centroid}"
        )
        if notes:
            condition += f" | Notes:{notes}"

        findings.append(make_finding(
            asset_id=session_id,
            object=f"Track {track_id} — {label}",
            condition=condition,
            confidence=1.0,
            source=data.get("source", "cv_tracking"),
            timestamp=saved_at,
            raw=json.dumps(track),
        ))

    return assets, findings


def normalise_cv(data: dict) -> tuple:
    assets, findings = [], []
    aid = data.get("asset_id", "UNKNOWN")

    assets.append(make_asset(
        asset_id=aid,
        type=data.get("asset_type", "Unknown"),
        location=data.get("location", "Unknown"),
    ))

    for det in data.get("detections", []):
        findings.append(make_finding(
            asset_id=aid,
            object=det.get("object", det.get("type", "Unknown")),
            condition=det.get("condition", det.get("label", "Unknown")),
            confidence=det.get("confidence", det.get("score", 0.5)),
            source="cv_module",
            timestamp=data.get("timestamp", ""),
            raw=json.dumps(det),
        ))

    return assets, findings


def normalise_finding_json(data: dict) -> tuple:
    assets, findings = [], []
    aid = data.get("asset_id", "UNKNOWN")
    assets.append(make_asset(asset_id=aid))

    for f in data.get("findings", []):
        findings.append(make_finding(
            asset_id=aid,
            object=f.get("object", f.get("component", f.get("part", "Unknown"))),
            condition=f.get("condition", f.get("status", f.get("description", "Unknown"))),
            confidence=f.get("confidence", f.get("score", 0.5)),
            source=f.get("source", "json_import"),
            timestamp=f.get("timestamp", data.get("timestamp", "")),
            raw=json.dumps(f),
        ))

    return assets, findings


def normalise_asset_json(data: dict) -> tuple:
    return [make_asset(
        asset_id=data.get("asset_id", data.get("id", "UNKNOWN")),
        name=data.get("name", data.get("machine_name")),
        type=data.get("type", data.get("asset_type")),
        location=data.get("location", data.get("zone")),
    )], []


# ── Excel / CSV normalisers ───────────────────────────────────

def _col(df, *opts):
    cols = list(df.columns)
    for o in opts:
        if o in cols:
            return o
    return None


def normalise_assets_excel(df) -> tuple:
    assets = []
    id_col = _col(df, "asset_id", "id", "machine_id", "equipment_id")
    nm_col = _col(df, "name", "machine_name", "asset_name", "equipment_name")
    ty_col = _col(df, "type", "machine_type", "asset_type", "category")
    lo_col = _col(df, "location", "zone", "area", "site", "bay")
    ln_col = _col(df, "line", "production_line", "line_no")
    zn_col = _col(df, "zone", "bay", "section")

    if not id_col:
        return [], []

    for _, row in df.iterrows():
        assets.append(make_asset(
            asset_id=str(row[id_col]),
            name=str(row[nm_col]) if nm_col else None,
            type=str(row[ty_col]) if ty_col else None,
            location=str(row[lo_col]) if lo_col else None,
            line=str(row[ln_col]) if ln_col else None,
            zone=str(row[zn_col]) if zn_col else None,
        ))

    return assets, []


def normalise_findings_excel(df) -> tuple:
    findings = []
    id_col   = _col(df, "asset_id", "machine_id", "id", "equipment_id")
    obj_col  = _col(df, "object", "component", "part", "item")
    con_col  = _col(df, "condition", "status", "description", "observation", "defect")
    conf_col = _col(df, "confidence", "score", "severity_score", "probability")
    src_col  = _col(df, "source", "module", "inspector")
    ts_col   = _col(df, "timestamp", "date", "inspection_date", "time")

    if not id_col:
        return [], []

    for _, row in df.iterrows():
        findings.append(make_finding(
            asset_id=str(row[id_col]),
            object=str(row[obj_col]) if obj_col else "Unknown",
            condition=str(row[con_col]) if con_col else "Unknown",
            confidence=row[conf_col] if conf_col else 0.5,
            source=str(row[src_col]) if src_col else "excel_import",
            timestamp=str(row[ts_col]) if ts_col else "",
        ))

    return [], findings


def normalise_batch_excel(df) -> tuple:
    assets, findings = [], []
    bn_col   = _col(df, "batch_number", "batch", "batch_id")
    name_col = _col(df, "piece_name", "name", "piece", "scrap_name")
    type_col = _col(df, "shape_type", "shape", "type")
    area_col = _col(df, "area_cm2", "area", "area_cm")

    if not bn_col:
        return [], []

    for batch_id, group in df.groupby(df[bn_col]):
        aid = f"BATCH{batch_id}"
        assets.append(make_asset(
            asset_id=aid,
            name=f"Batch {batch_id}",
            type="scrap_batch",
            location=f"{len(group)} scraps",
        ))
        for _, row in group.iterrows():
            area = row[area_col] if area_col else "?"
            findings.append(make_finding(
                asset_id=aid,
                object=str(row[name_col]) if name_col else "Unknown",
                condition=f"Area:{area}cm²",
                source="excel_batch",
            ))

    return assets, findings
