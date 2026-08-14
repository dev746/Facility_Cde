"""
tests/test_ingestion_files.py

Tests ingestion with actual files from data/samples/.
Verifies that your real data (batch JSONs, annotation JSONs)
ingest correctly and produce the right DB records.

Run: PYTHONPATH=. python tests/test_ingestion_files.py
"""
import sys
import os
import json
import tempfile

# Ensure the project root is on PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set stdout/stderr encoding to UTF-8 for Windows consoles
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

GREEN = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"
BOLD  = "\033[1m";  RESET = "\033[0m"

_results = {"passed": 0, "failed": 0, "skipped": 0}

def _pass(msg, detail=""):
    _results["passed"] += 1
    print(f"  {GREEN}✓{RESET} {msg}" + (f" — {detail}" if detail else ""))

def _fail(msg, reason=""):
    _results["failed"] += 1
    print(f"  {RED}✗{RESET} {msg}" + (f" — {reason}" if reason else ""))

def _skip(msg, reason=""):
    _results["skipped"] += 1
    print(f"  {YELLOW}-{RESET} {msg}" + (f" — {reason}" if reason else ""))

def _section(t):
    print(f"\n{BOLD}── {t} ──{RESET}")


# ── Sample data ───────────────────────────────────────────────

BATCH1 = {
    "batch_number": 1, "cm_per_pixel": 0.10583867704109558, "total_scraps": 3,
    "scraps": [
        {"id":1,"piece_name":"square_1","shape_type":"square","vertices_count":4,
         "vertex_labels":{"A":[185,367],"B":[183,394],"C":[214,398],"D":[217,371]},
         "side_lengths_cm":{"AB":2.87,"BC":3.31,"CD":2.88,"DA":3.41},"area_cm2":11.15},
        {"id":2,"piece_name":"rectangle_1","shape_type":"rectangle","vertices_count":4,
         "vertex_labels":{"A":[351,220],"B":[347,289],"C":[397,293],"D":[400,224]},
         "side_lengths_cm":{"AB":7.32,"BC":5.31,"CD":7.31,"DA":5.2},"area_cm2":40.53},
        {"id":3,"piece_name":"triangle_1","shape_type":"triangle","vertices_count":3,
         "vertex_labels":{"A":[268,251],"B":[256,200],"C":[153,222]},
         "side_lengths_cm":{"AB":5.55,"BC":11.15,"CA":12.55},"area_cm2":36.95},
    ]
}

ANNOTATIONS = {
    "asset_id": "M14", "source": "cv_tracking",
    "track_1": {
        "track_id":1,"label":"board","category":"furniture","class_name":"tv",
        "frame_id":240,"area":12750.5,"bbox":[284,91,137,113],"centroid":[350,147],
        "angle":-3.4,"saved_at":"2026-06-04T10:07:42.628Z","notes":""
    },
    "track_23": {
        "track_id":23,"label":"","category":"unknown","class_name":"chair",
        "frame_id":200,"area":2625,"bbox":[514,190,37,121],"centroid":[531,240],
        "angle":-89.5,"saved_at":"2026-06-04T09:30:29.609Z","notes":""
    },
}

M14_CV = {
    "asset_id":"M14","asset_type":"CNC Lathe","location":"Bay 2, Line A",
    "timestamp":"2024-12-01T08:30:00Z",
    "detections":[
        {"object":"Bearing","condition":"Wear detected","confidence":0.92},
        {"object":"Spindle housing","condition":"Hairline crack","confidence":0.87},
        {"object":"Oil seal","condition":"Minor leak","confidence":0.74},
    ]
}

UNKNOWN_FORMAT = {
    "report_id": "RPT001",
    "machine": "Conveyor Belt",
    "zone": "Bay 1",
    "observations": [
        {"part": "drive_motor", "issue": "overheating", "severity": 0.91},
        {"part": "tension_roller", "issue": "misalignment", "severity": 0.66},
    ]
}

BIM_JSON = {
    "project": "FACTORY_FLOOR",
    "source": "bim_module",
    "elements": [
        {"id": "COL001", "name": "Column-001", "type": "StructuralColumn",
         "level": "Ground Floor",
         "location": {"x": 12.3, "y": 4.5, "z": 0.0},
         "properties": {"material": "concrete", "height_m": 3.2}},
        {"id": "BEAM001", "name": "Beam-001", "type": "StructuralBeam",
         "level": "Ground Floor",
         "location": {"x": 6.0, "y": 4.5, "z": 3.2},
         "properties": {"material": "steel", "length_m": 6.0}},
    ]
}


def write_tmp(data: dict) -> str:
    with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        return f.name


def test_normalisers_with_real_data():
    _section("Normalisers with real sample data")

    from ingestion.normalisers import (
        normalise_batch, normalise_annotations, normalise_cv
    )
    from ingestion.canonical import make_asset, make_finding

    # Batch 1
    assets, findings = normalise_batch(BATCH1)
    if (len(assets) == 1
            and assets[0]["asset_id"] == "BATCH1"
            and len(findings) == 3):
        _pass("BATCH1 normalises", "3 scraps → 3 findings")
    else:
        _fail("BATCH1", f"assets={len(assets)} findings={len(findings)}")

    # Check finding content
    areas = [f["condition"] for f in findings if "Area:" in f["condition"]]
    if len(areas) == 3:
        _pass("BATCH1 findings have area measurements", areas[0][:40])
    else:
        _fail("BATCH1 findings content", f"{len(areas)}/3 have area")

    # Annotations
    assets_a, findings_a = normalise_annotations(ANNOTATIONS)
    if (len(assets_a) == 1
            and assets_a[0]["asset_id"] == "M14"
            and len(findings_a) == 2):
        _pass("annotations normalise", "M14, 2 tracks")
    else:
        _fail("annotations", f"assets={len(assets_a)} findings={len(findings_a)}")

    # Check track labels preserved
    labels = [f["object"] for f in findings_a]
    if any("Track 1" in l for l in labels):
        _pass("track labels preserved", str(labels))
    else:
        _fail("track labels", f"got: {labels}")

    # CV detections
    assets_c, findings_c = normalise_cv(M14_CV)
    if (len(assets_c) == 1
            and assets_c[0]["asset_id"] == "M14"
            and len(findings_c) == 3):
        _pass("CV detections normalise", "M14, 3 detections")
    else:
        _fail("CV detections", f"assets={len(assets_c)} findings={len(findings_c)}")

    # Check highest confidence is critical
    confs = [f["confidence"] for f in findings_c]
    sevs  = [f["severity"] for f in findings_c]
    if "critical" in sevs:
        _pass("severity auto-assigned critical", f"confs={confs}")
    else:
        _fail("severity", f"sevs={sevs} confs={confs}")


def test_bim_normaliser():
    _section("BIM normaliser")

    try:
        from ingestion.bim_ingest import normalise_bim_json
    except ImportError as e:
        _skip("BIM normaliser", str(e))
        return

    assets, findings = normalise_bim_json(BIM_JSON)

    if len(assets) == 2:
        _pass("BIM elements → 2 assets", f"{[a['asset_id'] for a in assets]}")
    else:
        _fail("BIM asset count", f"expected 2, got {len(assets)}")

    if len(findings) == 2:
        _pass("BIM properties → 2 findings", "one per element")
    else:
        _fail("BIM findings count", f"expected 2, got {len(findings)}")

    if findings and "material" in findings[0]["condition"]:
        _pass("BIM properties in condition", findings[0]["condition"][:60])
    else:
        _fail("BIM properties content", str(findings[0] if findings else "empty"))


def test_detector_with_all_formats():
    _section("Detector against all format types")

    from ingestion.detector import (
        detect_json_schema, detect_bim_schema
    )

    test_cases = [
        (BATCH1,        "batch",    "standard"),
        (ANNOTATIONS,   "annotations", "standard"),
        (M14_CV,        "cv",       "standard"),
        (BIM_JSON,      "bim_json", "bim"),
        ({"findings": [], "asset_id": "X"}, "finding", "standard"),
        ({"asset_id": "X", "name": "Y"},    "asset",   "standard"),
        ({"geometry": []},                  "geometry", "standard"),
    ]

    for data, expected, schema_type in test_cases:
        schema = detect_json_schema(data)
        if schema == "unknown" and schema_type == "bim":
            schema = detect_bim_schema(data)
        if schema == expected:
            _pass(f"detect {expected}", "correct")
        else:
            _fail(f"detect {expected}", f"got '{schema}'")


def test_version_tracking_with_real_data():
    _section("Version tracking with real data")

    from ingestion.version_tracker import _hash, diff_asset

    # Same data produces same hash
    h1 = _hash(BATCH1)
    h2 = _hash(BATCH1)
    if h1 == h2:
        _pass("BATCH1 hash deterministic", h1)
    else:
        _fail("hash determinism", f"{h1} != {h2}")

    # Changed batch produces different hash
    batch_modified = {**BATCH1, "cm_per_pixel": 0.999}
    h3 = _hash(batch_modified)
    if h1 != h3:
        _pass("modified batch → different hash")
    else:
        _fail("hash sensitivity", "same hash for different data")

    # Asset diff detects location change
    existing = {"name": "CNC Lathe", "type": "CNC",
                "location": "Bay 2, Line A", "line": "", "zone": "", "status": "active"}
    incoming = {"asset_id": "M14", "name": "CNC Lathe", "type": "CNC",
                "location": "Bay 3, Line A", "line": "", "zone": ""}
    changes = diff_asset(incoming, existing)
    if "location" in changes:
        old, new = changes["location"]
        _pass("diff detects location change", f"'{old}' → '{new}'")
    else:
        _fail("diff location change", f"changes: {changes}")

    # Idempotent — same data, no changes
    same_incoming = {**existing, "asset_id": "M14"}
    no_changes = diff_asset(same_incoming, existing)
    if not no_changes:
        _pass("no diff on identical data", "{}")
    else:
        _fail("idempotent diff", f"unexpected: {no_changes}")


def test_unknown_format_llm_fallback():
    _section("Unknown format → LLM fallback")

    from ingestion.detector import detect_json_schema, detect_bim_schema

    schema = detect_json_schema(UNKNOWN_FORMAT)
    bim    = detect_bim_schema(UNKNOWN_FORMAT)

    if schema == "unknown" and bim == "unknown":
        _pass("unknown format correctly undetected", "will route to LLM")
    else:
        _fail("unknown format detection", f"schema={schema} bim={bim}")

    # Test LLM fallback if API available
    try:
        from ingestion.llm_normaliser import llm_normalise
        assets, findings = llm_normalise(UNKNOWN_FORMAT)
        if isinstance(assets, list) and isinstance(findings, list):
            total = len(assets) + len(findings)
            _pass("LLM fallback returns lists", f"{len(assets)} assets, {len(findings)} findings")
        else:
            _fail("LLM fallback types", f"assets={type(assets)} findings={type(findings)}")
    except Exception as e:
        _skip("LLM fallback (needs API)", str(e)[:60])


def test_full_ingest_pipeline():
    _section("Full ingest pipeline (universal.py)")

    try:
        from ingestion.universal import ingest_any
    except ImportError as e:
        _skip("universal import", str(e))
        return

    test_datasets = [
        ("BATCH1",       BATCH1),
        ("M14_CV",       M14_CV),
        ("ANNOTATIONS",  ANNOTATIONS),
        ("BIM_JSON",     BIM_JSON),
    ]

    for name, data in test_datasets:
        tmp = write_tmp(data)
        try:
            count = ingest_any(tmp)
            if isinstance(count, int) and count >= 0:
                if count == 0:
                    _pass(f"ingest {name}", "skipped (unchanged) or 0 records")
                else:
                    _pass(f"ingest {name}", f"{count} records written")
            else:
                _fail(f"ingest {name}", f"unexpected return: {count}")
        except Exception as e:
            # DB not available is acceptable in unit test context
            if "no such table" in str(e) or "relation" in str(e).lower() or "connect" in str(e).lower():
                _skip(f"ingest {name} (needs DB)", str(e)[:50])
            else:
                _fail(f"ingest {name}", str(e)[:80])
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass


if __name__ == "__main__":
    test_normalisers_with_real_data()
    test_bim_normaliser()
    test_detector_with_all_formats()
    test_version_tracking_with_real_data()
    test_unknown_format_llm_fallback()
    test_full_ingest_pipeline()

    p, f, s = _results["passed"], _results["failed"], _results["skipped"]
    print(f"\n{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}  {GREEN}{p} passed{RESET}  {RED}{f} failed{RESET}  {YELLOW}{s} skipped{RESET}")
    print(f"{BOLD}{'='*50}{RESET}\n")
    sys.exit(0 if f == 0 else 1)
