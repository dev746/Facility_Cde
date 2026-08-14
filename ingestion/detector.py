import json
import pandas as pd
from pathlib import Path

# ── Standard JSON schema signatures ──────────────────────────
SCHEMA_SIGNATURES = {
    "batch":       lambda d: "batch_number" in d and "scraps" in d,
    "cv":          lambda d: "asset_id" in d and "detections" in d,
    "annotations": lambda d: isinstance(d, dict) and any(
                       k.startswith("track_") for k in d.keys()
                   ),
    "tracks":      lambda d: "tracks" in d,
    "geometry":    lambda d: "geometry" in d or "shapes" in d,
    "finding":     lambda d: "findings" in d and "asset_id" in d,
    "asset":       lambda d: "asset_id" in d and "name" in d and "detections" not in d,
}

# ── Excel / CSV schema signatures ────────────────────────────
EXCEL_SIGNATURES = {
    "assets":   ["asset_id", "name"],
    "findings": ["asset_id", "condition"],
    "batch":    ["batch_number", "piece_name"],
}


def detect_json_schema(data: dict) -> str:
    """Returns first matching standard schema name or 'unknown'."""
    for name, check in SCHEMA_SIGNATURES.items():
        try:
            if check(data):
                return name
        except Exception:
            continue
    return "unknown"


def detect_excel_schema(df: pd.DataFrame) -> str:
    """Returns schema name based on required columns present."""
    cols = [c.lower().strip() for c in df.columns]
    for name, required in EXCEL_SIGNATURES.items():
        if all(r in cols for r in required):
            return name
    return "unknown"


def load_file(filepath: str):
    """
    Load any supported file.
    Returns (ftype, data) where ftype is 'json' or 'excel'.
    For json: data is a dict or list.
    For excel/csv: data is a DataFrame with lowercased columns.
    """
    p = Path(filepath)

    if p.suffix == ".json":
        with open(p, encoding="utf-8") as f:
            return "json", json.load(f)

    if p.suffix in (".xlsx", ".xls"):
        df = pd.read_excel(p)
        df.columns = [c.strip().lower() for c in df.columns]
        return "excel", df

    if p.suffix == ".csv":
        df = pd.read_csv(p)
        df.columns = [c.strip().lower() for c in df.columns]
        return "excel", df

    raise ValueError(f"Unsupported file type: {p.suffix}")

# ── BIM-specific detection additions ──────────────────────────
BIM_SIGNATURES = {
    "bim_json": lambda d: "elements" in d and isinstance(d.get("elements"), list),
    "ifc_json": lambda d: isinstance(d, list) and len(d) > 0 and "GlobalId" in d[0],
    "ifc_json_wrapped": lambda d: "entities" in d and isinstance(d.get("entities"), list),
}


def detect_bim_schema(data) -> str:
    for name, check in BIM_SIGNATURES.items():
        try:
            if check(data):
                return name
        except Exception:
            continue
    return "unknown"


def is_cobie(filepath: str) -> bool:
    """Check if Excel/CSV file is a COBie sheet."""
    try:
        if filepath.endswith((".xlsx", ".xls")):
            xl = pd.ExcelFile(filepath)
            sheets = xl.sheet_names
            return any(s in sheets for s in ["Component", "Space", "System", "Floor", "Type"])
    except Exception:
        pass
    return False

