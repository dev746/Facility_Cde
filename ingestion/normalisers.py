"""
One normaliser function per known schema type.
Every function returns (assets: list[dict], findings: list[dict]).
All dicts must be canonical — produced by make_asset() / make_finding().
"""
import json
from ingestion.canonical import make_asset, make_finding, find_column



# ══════════════════════════════════════════════════════════════
# JSON NORMALISERS
# ══════════════════════════════════════════════════════════════

def normalise_batch(data: dict) -> tuple:
    """
    Format 1 — Batch/scrap measurement output.
    Trigger: has 'batch_number' AND 'scraps'
    Asset:   BATCH{n}
    Finding: one per scrap, condition = area + side lengths + vertices
    """
    assets, findings = [], []
    batch_id = f"BATCH{data['batch_number']}"
    scale    = data.get("cm_per_pixel", 0)
    total    = data.get("total_scraps", 0)

    assets.append(make_asset(
        asset_id=batch_id,
        name=f"Batch {data['batch_number']}",
        type="scrap_batch",
        location=f"{total} scraps | scale {scale:.4f} cm/px",
    ))

    for scrap in data.get("scraps", []):
        sides     = scrap.get("side_lengths_cm", {})
        area      = scrap.get("area_cm2", 0)
        stype     = scrap.get("shape_type", "unknown")
        name      = scrap.get("piece_name", "unknown")
        verts     = scrap.get("vertex_labels", {})
        sides_str = ", ".join(f"{k}:{v}cm" for k, v in sides.items())
        # show first 4 vertices to keep condition readable
        verts_str = ", ".join(
            f"{k}:{v}" for k, v in list(verts.items())[:4]
        )

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
    """
    Format 2 — CV object tracking / annotation export.
    Trigger: top-level keys start with 'track_'
    Asset:   asset_id from data, or SESSION_001
    Finding: one per track_ key
    """
    assets, findings = [], []

    session_id = str(
        data.get("asset_id", data.get("session_id", "ANNOTATIONS"))
    ).upper()

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
    """
    Format 3 — Standard CV detections.
    Trigger: has 'asset_id' AND 'detections'
    Asset:   from asset_id field
    Finding: one per detection
    """
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
    """
    Format — explicit findings list.
    Trigger: has 'findings' AND 'asset_id'
    Handles varied field names: object/component/part, condition/status/description, etc.
    """
    assets, findings = [], []
    aid = data.get("asset_id", "UNKNOWN")
    assets.append(make_asset(asset_id=aid))

    for f in data.get("findings", []):
        findings.append(make_finding(
            asset_id=aid,
            object=f.get("object",
                   f.get("component",
                   f.get("part", "Unknown"))),
            condition=f.get("condition",
                      f.get("status",
                      f.get("description",
                      f.get("observation", "Unknown")))),
            confidence=f.get("confidence",
                        f.get("score",
                        f.get("severity_score", 0.5))),
            source=f.get("source", "json_import"),
            timestamp=f.get("timestamp", data.get("timestamp", "")),
            raw=json.dumps(f),
        ))

    return assets, findings


def normalise_asset_json(data: dict) -> tuple:
    """
    Format — asset metadata only.
    Trigger: has 'asset_id' AND 'name', no 'detections'
    Handles varied field names for type and location.
    """
    assets = [make_asset(
        asset_id=data.get("asset_id", data.get("id", "UNKNOWN")),
        name=data.get("name",
             data.get("machine_name",
             data.get("asset_name", None))),
        type=data.get("type",
             data.get("asset_type",
             data.get("machine_type",
             data.get("category", None)))),
        location=data.get("location",
                 data.get("zone",
                 data.get("area",
                 data.get("bay", None)))),
    )]
    return assets, []


def normalise_geometry(data: dict) -> tuple:
    """
    Format — geometry / spatial output.
    Trigger: has 'geometry' or 'shapes'
    Stores shape data as findings for queryability.
    """
    assets, findings = [], []
    aid = str(data.get("asset_id", data.get("session_id", "GEOMETRY"))).upper()

    assets.append(make_asset(
        asset_id=aid,
        name=data.get("name", f"Geometry Session {aid}"),
        type="geometry_analysis",
        location=data.get("location", "Unknown"),
    ))

    shapes = data.get("geometry", data.get("shapes", []))
    if isinstance(shapes, list):
        for shape in shapes:
            if not isinstance(shape, dict):
                continue
            stype  = shape.get("type", shape.get("shape_type", "unknown"))
            dims   = shape.get("dimensions", shape.get("measurements", {}))
            dim_str = " | ".join(f"{k}:{v}" for k, v in dims.items()) if dims else ""
            findings.append(make_finding(
                asset_id=aid,
                object=f"Shape: {stype}",
                condition=dim_str or json.dumps(shape)[:200],
                confidence=1.0,
                source=data.get("source", "geometry_module"),
                timestamp=data.get("timestamp", ""),
                raw=json.dumps(shape),
            ))
    elif isinstance(shapes, dict):
        for shape_id, shape in shapes.items():
            if not isinstance(shape, dict):
                continue
            findings.append(make_finding(
                asset_id=aid,
                object=f"Shape {shape_id}",
                condition=json.dumps(shape)[:300],
                confidence=1.0,
                source=data.get("source", "geometry_module"),
                raw=json.dumps(shape),
            ))

    return assets, findings


# ══════════════════════════════════════════════════════════════
# EXCEL / CSV NORMALISERS
# ══════════════════════════════════════════════════════════════

def normalise_assets_excel(df) -> tuple:
    """
    Excel — asset registry / machine list.
    Trigger: has asset_id + name columns (any capitalisation).
    Tolerates wide variety of column names.
    """
    assets = []

    id_col  = find_column(df, "asset_id", "id", "machine_id", "equipment_id", "asset id")
    nm_col  = find_column(df, "name", "machine_name", "asset_name", "equipment_name", "machine name")
    ty_col  = find_column(df, "type", "machine_type", "asset_type", "category", "equipment_type")
    lo_col  = find_column(df, "location", "zone", "area", "site", "bay", "plant_location")
    ln_col  = find_column(df, "line", "production_line", "line_no", "line_number")
    zn_col  = find_column(df, "zone", "bay", "section", "department")

    if not id_col:
        print("[normalise_assets_excel] no asset_id column found")
        return [], []

    for _, row in df.iterrows():
        val = str(row[id_col]).strip()
        if not val or val.lower() in ("nan", "none", ""):
            continue
        assets.append(make_asset(
            asset_id=val,
            name=str(row[nm_col]).strip() if nm_col else None,
            type=str(row[ty_col]).strip() if ty_col else None,
            location=str(row[lo_col]).strip() if lo_col else None,
            line=str(row[ln_col]).strip() if ln_col else None,
            zone=str(row[zn_col]).strip() if zn_col else None,
        ))

    return assets, []


def normalise_findings_excel(df) -> tuple:
    """
    Excel — inspection report / defect list.
    Trigger: has asset_id + condition columns.
    """
    findings = []

    id_col   = find_column(df, "asset_id", "machine_id", "id", "equipment_id", "asset id")
    obj_col  = find_column(df, "object", "component", "part", "item", "component_name")
    con_col  = find_column(df, "condition", "status", "description", "observation",
                    "defect", "finding", "issue")
    conf_col = find_column(df, "confidence", "score", "severity_score", "probability",
                    "confidence_score")
    src_col  = find_column(df, "source", "module", "inspector", "reported_by")
    ts_col   = find_column(df, "timestamp", "date", "inspection_date", "time", "recorded_at")

    if not id_col:
        print("[normalise_findings_excel] no asset_id column found")
        return [], []

    for _, row in df.iterrows():
        val = str(row[id_col]).strip()
        if not val or val.lower() in ("nan", "none", ""):
            continue

        try:
            conf = float(row[conf_col]) if conf_col else 0.5
            # if confidence looks like a percentage (>1), convert
            if conf > 1:
                conf = conf / 100.0
        except (ValueError, TypeError):
            conf = 0.5

        findings.append(make_finding(
            asset_id=val,
            object=str(row[obj_col]).strip() if obj_col else "Unknown",
            condition=str(row[con_col]).strip() if con_col else "Unknown",
            confidence=conf,
            source=str(row[src_col]).strip() if src_col else "excel_import",
            timestamp=str(row[ts_col]).strip() if ts_col else "",
        ))

    return [], findings


def normalise_batch_excel(df) -> tuple:
    """
    Excel — batch/scrap data in spreadsheet form.
    Trigger: has batch_number + piece_name columns.
    Groups rows by batch_number.
    """
    assets, findings = [], []

    bn_col   = find_column(df, "batch_number", "batch", "batch_id", "batch_no")
    name_col = find_column(df, "piece_name", "name", "piece", "scrap_name", "item_name")
    type_col = find_column(df, "shape_type", "shape", "type", "geometry_type")
    area_col = find_column(df, "area_cm2", "area", "area_cm", "surface_area")

    if not bn_col:
        print("[normalise_batch_excel] no batch_number column found")
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
            area  = row[area_col] if area_col else "?"
            stype = str(row[type_col]).strip() if type_col else "unknown"
            pname = str(row[name_col]).strip() if name_col else "Unknown"
            findings.append(make_finding(
                asset_id=aid,
                object=f"{pname} ({stype})",
                condition=f"Area:{area}cm²",
                confidence=1.0,
                source="excel_batch",
            ))

    return assets, findings
