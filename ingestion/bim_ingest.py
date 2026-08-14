"""
BIM file ingestion.

Supported input formats:
  1. BIM JSON export  — elements array with properties dict
  2. IFC JSON export  — GlobalId, Name, type, IfcProperties
  3. COBie Excel/CSV  — Component, Space, System sheets

BIM is the only module with two-way comms:
  - Inbound:  BIM sends files → stored as assets + findings
  - Outbound: BIM polls GET /api/asset/{id} and GET /api/findings/{id}

For geometry/spatial data that has no finding equivalent,
we store it in the bim_elements table and surface it via the API.
"""
import json
import uuid
import pandas as pd
from pathlib import Path
from ingestion.canonical import make_asset, make_finding
from core.db import execute, executemany, query as db_query


# ── BIM JSON normaliser ───────────────────────────────────────

def normalise_bim_json(data: dict) -> tuple:
    """
    Handles generic BIM JSON export.
    Expected shape:
    {
      "project": "...",
      "source": "bim_module",
      "elements": [
        {
          "id": "EL001",
          "name": "Column-001",
          "type": "StructuralColumn",
          "level": "Ground Floor",
          "location": {"x": 12.3, "y": 4.5, "z": 0.0},
          "properties": {"material": "concrete", "height_m": 3.2, ...}
        }
      ]
    }
    """
    assets, findings = [], []
    project = data.get("project", "BIM_PROJECT").upper().replace(" ", "_")

    for el in data.get("elements", []):
        el_id    = str(el.get("id", el.get("GlobalId", uuid.uuid4()))).upper()
        name     = el.get("name", el.get("Name", el_id))
        etype    = el.get("type", el.get("ifcType", "BIM_Element"))
        level    = el.get("level", el.get("floor", "Unknown"))
        loc      = el.get("location", {})
        loc_str  = (f"x:{loc.get('x',0):.2f} y:{loc.get('y',0):.2f} z:{loc.get('z',0):.2f}"
                    if isinstance(loc, dict) else str(loc))
        props    = el.get("properties", el.get("IfcProperties", {}))
        raw      = json.dumps(el)

        assets.append(make_asset(
            asset_id=el_id,
            name=name,
            type=etype,
            location=f"{level} | {loc_str}",
            zone=level,
        ))

        # store geometry/properties as a finding so it's queryable
        if props:
            props_str = " | ".join(f"{k}:{v}" for k, v in list(props.items())[:8])
            findings.append(make_finding(
                asset_id=el_id,
                object="BIM Properties",
                condition=props_str,
                confidence=1.0,
                source=data.get("source", "bim_module"),
                raw=raw,
            ))

        # also store in bim.elements for structured BIM API access (best-effort)
        try:
            _store_bim_element(el_id, project, name, etype, level, loc_str, props, raw)
        except Exception:
            pass  # DB write is optional; normaliser returns assets/findings regardless

    return assets, findings


# ── IFC JSON normaliser ───────────────────────────────────────

def normalise_ifc_json(data: dict) -> tuple:
    """
    Handles IFC exports converted to JSON (e.g. via IfcOpenShell or xBIM).
    Expected shape: list of IFC entities or dict with 'entities' key.
    """
    entities = data if isinstance(data, list) else data.get("entities", [])
    assets, findings = [], []

    for entity in entities:
        gid   = str(entity.get("GlobalId", uuid.uuid4())).upper()
        name  = entity.get("Name", entity.get("LongName", gid))
        etype = entity.get("type", entity.get("ifcType", "IfcElement"))
        desc  = entity.get("Description", "")
        props = entity.get("HasProperties", entity.get("properties", {}))
        raw   = json.dumps(entity)

        # only ingest spatial and physical elements, skip pure geometry
        skip_types = {"IfcRelAssociates", "IfcRelDefines",
                      "IfcGeometricRepresentationContext"}
        if etype in skip_types:
            continue

        assets.append(make_asset(
            asset_id=gid,
            name=name,
            type=etype,
            location=desc or "IFC Import",
        ))

        if props:
            if isinstance(props, dict):
                props_str = " | ".join(f"{k}:{v}" for k, v in list(props.items())[:8])
            else:
                props_str = str(props)[:300]

            findings.append(make_finding(
                asset_id=gid,
                object="IFC Properties",
                condition=props_str,
                confidence=1.0,
                source="ifc_import",
                raw=raw,
            ))

    return assets, findings


# ── COBie Excel normaliser ────────────────────────────────────

def normalise_cobie(filepath: str) -> tuple:
    """
    COBie is a spreadsheet standard for facility management.
    Key sheets: Component, Space, System, Type, Floor.
    We read whichever sheets exist.
    """
    assets, findings = [], []
    xl = pd.ExcelFile(filepath)

    # Component sheet → assets
    if "Component" in xl.sheet_names:
        df = xl.parse("Component")
        df.columns = [c.strip().lower() for c in df.columns]
        id_col   = _cobie_col(df, "name", "extidentifier", "id")
        type_col = _cobie_col(df, "typename", "type", "category")
        sp_col   = _cobie_col(df, "space", "floor", "zone")

        if id_col:
            for _, row in df.iterrows():
                aid = str(row[id_col]).upper().strip()
                assets.append(make_asset(
                    asset_id=aid,
                    name=str(row[id_col]),
                    type=str(row[type_col]) if type_col else "COBie Component",
                    location=str(row[sp_col]) if sp_col else "Unknown",
                ))

    # System sheet → findings (system associations)
    if "System" in xl.sheet_names:
        df = xl.parse("System")
        df.columns = [c.strip().lower() for c in df.columns]
        nm_col  = _cobie_col(df, "name", "systemname")
        cat_col = _cobie_col(df, "category", "type")
        comp_col = _cobie_col(df, "componentnames", "components")

        if nm_col and comp_col:
            for _, row in df.iterrows():
                components = str(row[comp_col]).split(",")
                for comp in components:
                    comp = comp.strip().upper()
                    if not comp:
                        continue
                    findings.append(make_finding(
                        asset_id=comp,
                        object="System Association",
                        condition=(
                            f"Part of system: {row[nm_col]} "
                            f"({row[cat_col] if cat_col else ''})"
                        ),
                        confidence=1.0,
                        source="cobie_import",
                    ))

    return assets, findings


def _cobie_col(df, *opts) -> str | None:
    for o in opts:
        if o in df.columns:
            return o
    return None


# ── BIM elements table ────────────────────────────────────────

def _store_bim_element(element_id, project, name, etype,
                        level, location, properties, raw_json):
    """Store full BIM element data for structured API access (best-effort)."""
    import json as _json
    try:
        execute(
            """INSERT INTO bim.elements
               (ifc_guid, ifc_type, name, properties)
               VALUES (%s,%s,%s,%s::jsonb)
               ON CONFLICT (ifc_guid) DO UPDATE SET
               ifc_type=excluded.ifc_type, name=excluded.name,
               properties=excluded.properties""",
            (element_id, etype, name, _json.dumps(properties)),
        )
    except Exception:
        pass


def get_bim_element(element_id: str) -> dict | None:
    from core.db import query
    try:
        rows = query(
            "SELECT * FROM bim.elements WHERE ifc_guid = %s",
            (element_id.upper(),),
        )
    except Exception:
        return None
    if not rows:
        return None
    row = dict(rows[0])
    if isinstance(row.get("properties"), str):
        try:
            row["properties"] = json.loads(row["properties"])
        except Exception:
            pass
    return row


def list_bim_elements(project: str = None) -> list:
    from core.db import query
    try:
        return query("SELECT * FROM bim.elements ORDER BY ifc_type, name")
    except Exception:
        return []
