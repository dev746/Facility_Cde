import json
import pandas as pd
from pathlib import Path

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

EXCEL_SIGNATURES = {
    "assets":   ["asset_id", "name"],
    "findings": ["asset_id", "condition"],
    "batch":    ["batch_number", "piece_name"],
}


def detect_json_schema(data: dict) -> str:
    for name, check in SCHEMA_SIGNATURES.items():
        try:
            if check(data):
                return name
        except Exception:
            continue
    return "unknown"


def detect_excel_schema(df: pd.DataFrame) -> str:
    cols = [c.lower().strip() for c in df.columns]
    for name, required in EXCEL_SIGNATURES.items():
        if all(r in cols for r in required):
            return name
    return "unknown"


def load_file(filepath: str):
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
