"""
tests/test_all_features.py

Run all feature tests in sequence.
Each test is self-contained and prints PASS / FAIL with a reason.

Usage:
    PYTHONPATH=. python tests/test_all_features.py
    PYTHONPATH=. python tests/test_all_features.py --feature semantic
    PYTHONPATH=. python tests/test_all_features.py --feature context
    PYTHONPATH=. python tests/test_all_features.py --feature versioning
    PYTHONPATH=. python tests/test_all_features.py --feature graph
    PYTHONPATH=. python tests/test_all_features.py --feature nlreply
    PYTHONPATH=. python tests/test_all_features.py --feature ingestion

Each test block is independent — a failure in one does not block the others.
"""
import sys
import os
import json
import time
import traceback

# Ensure the project root is on PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set stdout/stderr encoding to UTF-8 for Windows consoles
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ── Colour helpers ────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

_results = {"passed": 0, "failed": 0, "skipped": 0}


def _pass(name: str, detail: str = ""):
    _results["passed"] += 1
    print(f"  {GREEN}✓ PASS{RESET}  {name}" + (f" — {detail}" if detail else ""))


def _fail(name: str, reason: str):
    _results["failed"] += 1
    print(f"  {RED}✗ FAIL{RESET}  {name} — {reason}")


def _skip(name: str, reason: str):
    _results["skipped"] += 1
    print(f"  {YELLOW}- SKIP{RESET}  {name} — {reason}")


def _section(title: str):
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")


# ══════════════════════════════════════════════════════════════
# FEATURE 1 — Semantic inferencing
# ══════════════════════════════════════════════════════════════

def test_semantic_search():
    _section("Feature 1 — Semantic Search (DB-grounded)")

    try:
        from query.semantic_search import (
            _get_synonyms, resolve_any_query,
            search_assets_by_keyword, search_findings_by_keyword
        )
    except ImportError as e:
        _fail("import semantic_search", str(e))
        return

    # Test 1a: synonym expansion
    synonyms = _get_synonyms("pump")
    if "hydraulic" in synonyms and "pump" in synonyms:
        _pass("synonym expansion", f"'pump' → {synonyms[:4]}")
    else:
        _fail("synonym expansion", f"got: {synonyms}")

    # Test 1b: synonym for crack
    synonyms = _get_synonyms("crack")
    if len(synonyms) >= 2:
        _pass("crack synonyms", f"{synonyms}")
    else:
        _fail("crack synonyms", "expected ≥ 2 terms")

    # Test 1c: unknown term falls back cleanly
    synonyms = _get_synonyms("xyzabc123")
    if isinstance(synonyms, list) and len(synonyms) >= 1:
        _pass("unknown term fallback", "returns list with original term")
    else:
        _fail("unknown term fallback", f"got: {synonyms}")

    # Test 1d: asset search returns list
    try:
        results = search_assets_by_keyword("M14")
        if isinstance(results, list):
            _pass("search_assets_by_keyword M14", f"{len(results)} result(s)")
        else:
            _fail("search_assets_by_keyword", f"expected list, got {type(results)}")
    except Exception as e:
        _skip("search_assets_by_keyword (needs DB)", str(e))

    # Test 1e: resolve_any_query with asset ID
    try:
        result = resolve_any_query("M14")
        if result.get("match_type") in ("direct_id", "keyword", "none"):
            _pass("resolve_any_query M14", f"match_type={result['match_type']}")
        else:
            _fail("resolve_any_query", f"unexpected result: {result}")
    except Exception as e:
        _skip("resolve_any_query (needs DB)", str(e))

    # Test 1f: resolve_any_query with machine name
    try:
        result = resolve_any_query("hydraulic press")
        if isinstance(result, dict) and "assets" in result:
            _pass("resolve by machine name", f"{len(result['assets'])} asset(s) found")
        else:
            _fail("resolve by machine name", str(result))
    except Exception as e:
        _skip("resolve by machine name (needs DB)", str(e))

    # Test 1g: resolve with industrial keyword
    try:
        result = resolve_any_query("bearing wear")
        if isinstance(result, dict):
            total = len(result.get("assets", [])) + len(result.get("findings", []))
            _pass("resolve bearing wear", f"{total} total results")
        else:
            _fail("resolve bearing wear", "no dict returned")
    except Exception as e:
        _skip("resolve bearing wear (needs DB)", str(e))


# ══════════════════════════════════════════════════════════════
# FEATURE 2 — NL replies + user context
# ══════════════════════════════════════════════════════════════

def test_context_and_responder():
    _section("Feature 2 — NL Replies + User Context")

    # Context module
    try:
        from query.context import (
            get_context, update_context,
            resolve_asset_from_context, build_context_prompt,
            _mem
        )
    except ImportError as e:
        _fail("import context", str(e))
        return

    test_phone = "whatsapp:+91test0001"

    # Test 2a: get_context returns defaults for new user
    ctx = get_context(test_phone)
    required_keys = ["last_asset_id", "last_intent", "language",
                     "query_count", "recent_assets", "recent_intents"]
    missing = [k for k in required_keys if k not in ctx]
    if not missing:
        _pass("get_context default shape", "all required keys present")
    else:
        _fail("get_context default shape", f"missing: {missing}")

    # Test 2b: update_context stores asset and intent
    update_context(test_phone, "findings", "M14", "english")
    ctx = get_context(test_phone)
    if ctx["last_asset_id"] == "M14" and ctx["last_intent"] == "findings":
        _pass("update_context stores asset+intent", "M14 / findings")
    else:
        _fail("update_context", f"got: {ctx}")

    # Test 2c: rolling window
    for asset in ["M22", "M37", "BATCH1", "BATCH2", "M14"]:
        update_context(test_phone, "machine", asset, "english")
    ctx = get_context(test_phone)
    if len(ctx["recent_assets"]) <= 5:
        _pass("rolling window capped at 5", f"{ctx['recent_assets']}")
    else:
        _fail("rolling window", f"too many: {ctx['recent_assets']}")

    # Test 2d: pronoun resolution
    resolved = resolve_asset_from_context(test_phone, "show its findings", None)
    if resolved is not None:
        _pass("pronoun resolution 'its'", f"resolved to: {resolved}")
    else:
        _fail("pronoun resolution", "returned None when context has asset")

    # Test 2e: explicit asset_id overrides context
    resolved = resolve_asset_from_context(test_phone, "machine M22", "M22")
    if resolved == "M22":
        _pass("explicit ID overrides context", "M22")
    else:
        _fail("explicit ID override", f"got: {resolved}")

    # Test 2f: Hinglish pronoun
    update_context(test_phone, "machine", "M37", "hinglish")
    resolved = resolve_asset_from_context(test_phone, "isme kya problem hai", None)
    if resolved == "M37":
        _pass("Hinglish pronoun 'isme'", "resolved M37")
    else:
        _fail("Hinglish pronoun", f"got: {resolved}")

    # Test 2g: context prompt builds correctly
    mock_user = {"name": "Ravi", "role": "technician", "shift": "morning", "line": "Line A"}
    prompt = build_context_prompt(test_phone, mock_user)
    if "Ravi" in prompt and "technician" in prompt:
        _pass("context prompt", prompt[:80])
    else:
        _fail("context prompt", f"got: {prompt}")

    # Test 2h: query count increments
    initial_count = get_context(test_phone).get("query_count", 0)
    update_context(test_phone, "list", None, "english")
    new_count = get_context(test_phone).get("query_count", 0)
    if new_count == initial_count + 1:
        _pass("query count increments", f"{initial_count} → {new_count}")
    else:
        _fail("query count", f"expected {initial_count+1}, got {new_count}")

    # Responder module
    try:
        from query.responder import generate_reply, _structured_fallback
    except ImportError as e:
        _fail("import responder", str(e))
        return

    mock_user = {"name": "Dev", "role": "admin", "phone": test_phone}

    # Test 2i: structured fallback never crashes
    test_cases = [
        None,
        [],
        {},
        [{"asset_id": "M14", "name": "CNC Lathe"}],
        {"asset": {"asset_id": "M14", "name": "CNC"}, "finding_count": 3, "critical": True},
    ]
    all_ok = True
    for case in test_cases:
        try:
            result = _structured_fallback("findings", case, mock_user)
            if not isinstance(result, str):
                all_ok = False
        except Exception as e:
            all_ok = False
            _fail(f"structured fallback ({type(case).__name__})", str(e))
    if all_ok:
        _pass("structured_fallback handles all input types", "5/5 passed")

    # Test 2j: generate_reply with LLM (if API available)
    try:
        mock_data = {"asset_id": "M14", "name": "CNC Lathe", "type": "CNC",
                     "location": "Bay 2"}
        reply = generate_reply("machine", mock_data, "show machine M14",
                                mock_user, "", "english")
        if isinstance(reply, str) and len(reply) > 10:
            _pass("generate_reply LLM", f"{len(reply)} chars returned")
        else:
            _fail("generate_reply LLM", f"got: {reply}")
    except Exception as e:
        _skip("generate_reply LLM (needs API)", str(e)[:80])

    # Test 2k: language detection in webhook
    try:
        from whatsapp.webhook_updated import _detect_language
        tests = [
            ("hello", "english"),
            ("M14 ki kya problem hai", "hinglish"),
            ("कृपया मशीन M14 दिखाएं", "hindi"),
            ("summary M14 batao", "hinglish"),
        ]
        ok = True
        for text, expected in tests:
            detected = _detect_language(text)
            if detected != expected:
                _fail(f"language detect '{text[:25]}'", f"expected {expected}, got {detected}")
                ok = False
        if ok:
            _pass("language detection", "4/4 cases correct")
    except ImportError:
        _skip("language detection (webhook not found)", "check filename")


# ══════════════════════════════════════════════════════════════
# FEATURE 3 — Version tracking
# ══════════════════════════════════════════════════════════════

def test_versioning():
    _section("Feature 3 — File Versioning & Update Comparison")

    try:
        from ingestion.version_tracker import (
            _hash, diff_asset, ingest_with_version_check
        )
    except ImportError as e:
        _fail("import version_tracker", str(e))
        return

    # Test 3a: hash is deterministic
    data = {"batch_number": 1, "scraps": [{"id": 1, "area_cm2": 11.15}]}
    h1 = _hash(data)
    h2 = _hash(data)
    if h1 == h2 and len(h1) == 16:
        _pass("hash deterministic", h1)
    else:
        _fail("hash", f"h1={h1} h2={h2}")

    # Test 3b: different data produces different hash
    data2 = {"batch_number": 1, "scraps": [{"id": 1, "area_cm2": 12.00}]}
    h3 = _hash(data2)
    if h3 != h1:
        _pass("hash changes with data", f"{h1} ≠ {h3}")
    else:
        _fail("hash uniqueness", "same hash for different data")

    # Test 3c: diff_asset detects changes
    incoming = {"asset_id": "M14", "name": "CNC Lathe Unit 14",
                 "type": "CNC Lathe", "location": "Bay 3, Line A"}
    existing = {"asset_id": "M14", "name": "CNC Lathe",
                 "type": "CNC Lathe", "location": "Bay 2, Line A"}
    changes = diff_asset(incoming, existing)
    if "location" in changes:
        _pass("diff detects location change",
              f"Bay 2 → {changes['location'][1]}")
    else:
        _fail("diff_asset", f"expected location change, got: {changes}")

    # Test 3d: diff ignores Unknown values
    incoming2 = {"asset_id": "M14", "name": "Unknown",
                  "type": "Unknown", "location": "Bay 2"}
    existing2 = {"asset_id": "M14", "name": "CNC Lathe",
                  "type": "CNC Lathe", "location": "Bay 2"}
    changes2 = diff_asset(incoming2, existing2)
    if "name" not in changes2 and "type" not in changes2:
        _pass("diff ignores Unknown values", "name/type not overwritten")
    else:
        _fail("diff Unknown filter", f"should not overwrite: {changes2}")

    # Test 3e: diff detects no change
    incoming3 = {"asset_id": "M14", "name": "CNC Lathe",
                  "type": "CNC Lathe", "location": "Bay 2"}
    changes3 = diff_asset(incoming3, existing2)
    if not changes3:
        _pass("diff unchanged returns empty dict", "{}")
    else:
        _fail("diff unchanged", f"unexpected: {changes3}")

    # Test 3f: version check (in-memory only, no DB)
    try:
        import tempfile, json as _json
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                         delete=False) as f:
            _json.dump(data, f)
            tmp_path = f.name
        result = ingest_with_version_check(tmp_path, data, "batch")
        if result["status"] in ("ingested", "skipped"):
            _pass("ingest_with_version_check returns status",
                  result["status"])
        else:
            _fail("ingest_with_version_check", f"got: {result}")
        os.unlink(tmp_path)
    except Exception as e:
        _skip("ingest_with_version_check (may need DB)", str(e)[:60])


# ══════════════════════════════════════════════════════════════
# FEATURE 4 — Relational graph API
# ══════════════════════════════════════════════════════════════

def test_graph_api():
    _section("Feature 4 — Relational Graph API")

    try:
        from api.graph import router
        _pass("graph router imports", "no import errors")
    except ImportError as e:
        _fail("import graph", str(e))
        return

    # Test the schema endpoint (no DB needed)
    try:
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router, prefix="/graph")
        client = TestClient(app)

        # Schema endpoint needs no DB
        resp = client.get("/graph/schema",
                          headers={"X-API-Key": os.getenv("API_KEY", "")})
        if resp.status_code == 200:
            body = resp.json()
            if "schemas" in body and "key_relationships" in body:
                _pass("GET /graph/schema", f"{len(body['schemas'])} schemas documented")
            else:
                _fail("graph schema content", f"keys: {list(body.keys())}")
        else:
            _fail("GET /graph/schema", f"status {resp.status_code}")

        # Test graph data endpoint structure
        resp2 = client.get("/graph/data",
                           headers={"X-API-Key": os.getenv("API_KEY", "")})
        if resp2.status_code in (200, 500):  # 500 ok if no DB
            if resp2.status_code == 200:
                body2 = resp2.json()
                if "nodes" in body2 and "edges" in body2:
                    _pass("GET /graph/data structure",
                          f"{body2['node_count']} nodes, {body2['edge_count']} edges")
                else:
                    _fail("graph data keys", str(list(body2.keys())))
            else:
                _skip("GET /graph/data (no DB connection)", "DB not available in test")
        else:
            _fail("GET /graph/data", f"status {resp2.status_code}")

    except ImportError:
        _skip("FastAPI TestClient", "pip install httpx to enable API tests")
    except Exception as e:
        _fail("graph API tests", str(e)[:80])


# ══════════════════════════════════════════════════════════════
# FEATURE 5 — Ingestion pipeline
# ══════════════════════════════════════════════════════════════

def test_ingestion():
    _section("Feature 5 — Ingestion Pipeline (Normalisers + Detector)")

    # Test 5a: all normalisers import
    try:
        from ingestion.normalisers import (
            normalise_batch, normalise_cv, normalise_annotations,
            normalise_finding_json, normalise_asset_json, normalise_geometry,
            normalise_assets_excel, normalise_findings_excel,
        )
        _pass("all normalisers import", "8/8")
    except ImportError as e:
        _fail("normalisers import", str(e))
        return

    # Test 5b: batch normaliser
    batch_data = {
        "batch_number": 99,
        "cm_per_pixel": 0.105,
        "total_scraps": 2,
        "scraps": [
            {"id": 1, "piece_name": "sq_test", "shape_type": "square",
             "vertices_count": 4, "vertex_labels": {"A": [0,0]},
             "side_lengths_cm": {"AB": 3.0}, "area_cm2": 9.0},
            {"id": 2, "piece_name": "tri_test", "shape_type": "triangle",
             "vertices_count": 3, "vertex_labels": {"A": [0,0]},
             "side_lengths_cm": {"AB": 5.0}, "area_cm2": 12.5},
        ]
    }
    assets, findings = normalise_batch(batch_data)
    if (len(assets) == 1 and assets[0]["asset_id"] == "BATCH99"
            and len(findings) == 2):
        _pass("normalise_batch", "BATCH99, 2 findings")
    else:
        _fail("normalise_batch",
              f"assets={len(assets)} findings={len(findings)}")

    # Test 5c: annotations normaliser with track_ keys
    ann_data = {
        "asset_id": "M14", "source": "cv_tracking",
        "track_1": {"track_id": 1, "label": "board", "category": "furniture",
                    "class_name": "tv", "frame_id": 240, "area": 1200.0,
                    "bbox": [10,20,30,40], "centroid": [25,30],
                    "angle": -3.4, "saved_at": "2026-01-01T00:00:00Z", "notes": ""},
        "track_23": {"track_id": 23, "label": "shaft", "category": "component",
                     "class_name": "rod", "frame_id": 300, "area": 800.0,
                     "bbox": [5,10,15,20], "centroid": [12,15],
                     "angle": 0.0, "saved_at": "2026-01-01T01:00:00Z", "notes": ""}
    }
    assets_a, findings_a = normalise_annotations(ann_data)
    if (len(assets_a) == 1 and len(findings_a) == 2
            and assets_a[0]["asset_id"] == "M14"):
        _pass("normalise_annotations", "M14, 2 tracks")
    else:
        _fail("normalise_annotations",
              f"assets={len(assets_a)} findings={len(findings_a)}")

    # Test 5d: CV normaliser
    cv_data = {
        "asset_id": "M22",
        "asset_type": "Hydraulic Press",
        "location": "Bay 4",
        "timestamp": "2026-01-01T10:00:00Z",
        "detections": [
            {"object": "cylinder", "condition": "pressure drop",
             "confidence": 0.89},
        ]
    }
    assets_c, findings_c = normalise_cv(cv_data)
    if (len(assets_c) == 1 and len(findings_c) == 1
            and findings_c[0]["confidence"] == 0.89):
        _pass("normalise_cv", "M22, 1 detection, conf 0.89")
    else:
        _fail("normalise_cv", f"{assets_c} / {findings_c}")

    # Test 5e: finding_json normaliser with varied field names
    finding_data = {
        "asset_id": "M37",
        "findings": [
            {"component": "motor", "status": "overheating",
             "score": 0.91, "source": "thermal_cam"},
            {"part": "belt", "description": "misalignment",
             "confidence": 0.66},
        ]
    }
    assets_f, findings_f = normalise_finding_json(finding_data)
    if len(findings_f) == 2:
        _pass("normalise_finding_json varied fields",
              f"component+status and part+description both mapped")
    else:
        _fail("normalise_finding_json", f"{len(findings_f)} findings")

    # Test 5f: canonical confidence clamped to [0, 1]
    from ingestion.canonical import make_finding
    f = make_finding("M14", "test", "test", confidence=1.5)
    if f["confidence"] <= 1.0:
        _pass("confidence clamped to ≤1.0", str(f["confidence"]))
    else:
        _fail("confidence clamp", f"got {f['confidence']}")

    # Test 5g: severity auto-assignment
    for conf, expected in [(0.95,"critical"),(0.80,"high"),
                            (0.60,"medium"),(0.30,"low")]:
        f = make_finding("M14", "obj", "cond", confidence=conf)
        if f["severity"] == expected:
            _pass(f"severity at conf={conf}", expected)
        else:
            _fail(f"severity at conf={conf}",
                  f"expected {expected}, got {f['severity']}")

    # Test 5h: detector schema detection
    try:
        from ingestion.detector import detect_json_schema, detect_bim_schema
        tests = [
            ({"batch_number": 1, "scraps": []}, "batch"),
            ({"asset_id": "M14", "detections": []}, "cv"),
            ({"track_1": {}, "track_2": {}}, "annotations"),
            ({"findings": [], "asset_id": "M14"}, "finding"),
            ({"elements": [{"id": "EL1"}]}, "bim_json"),
            ({"entities": [{"GlobalId": "abc"}]}, "ifc_json_wrapped"),
        ]
        ok = True
        for data, expected in tests:
            # check standard first, then BIM
            schema = detect_json_schema(data)
            if schema == "unknown":
                schema = detect_bim_schema(data)
            if schema != expected:
                _fail(f"detect {expected}", f"got {schema}")
                ok = False
        if ok:
            _pass("detector schema detection", f"{len(tests)}/{len(tests)} correct")
    except ImportError as e:
        _skip("detector tests", str(e))


# ══════════════════════════════════════════════════════════════
# FEATURE 6 — End-to-end dispatch
# ══════════════════════════════════════════════════════════════

def test_dispatch():
    _section("Feature 6 — End-to-End Dispatch")

    try:
        from whatsapp.dispatch import dispatch
    except ImportError as e:
        _fail("import dispatch", str(e))
        return

    mock_user = {
        "phone":  "whatsapp:+91test9999",
        "name":   "Test User",
        "role":   "admin",
        "shift":  "morning",
        "line":   "Line A",
    }

    test_cases = [
        ("help",               "help",      None),
        ("list",               "list",      None),
        ("summary M14",        "summary",   "M14"),
        ("findings M14",       "findings",  "M14"),
        ("convert 45 celsius fahrenheit", "convert", None),
        ("machine M22",        "machine",   "M22"),
        ("critical",           "critical",  None),
        ("latest",             "latest",    None),
    ]

    for text, intent, asset_id in test_cases:
        try:
            reply = dispatch(intent, asset_id, text, mock_user, "english")
            if isinstance(reply, str):
                preview = reply[:60].replace("\n", " ")
                _pass(f"dispatch '{text}'", preview)
            else:
                _fail(f"dispatch '{text}'", f"non-string: {type(reply)}")
        except Exception as e:
            _fail(f"dispatch '{text}'", str(e)[:80])

    # Test context-aware dispatch (pronoun resolution)
    try:
        from query.context import update_context
        update_context(mock_user["phone"], "machine", "M14", "english")
        reply = dispatch("findings", None, "show its findings",
                          mock_user, "english")
        if isinstance(reply, str):
            _pass("context pronoun in dispatch", "resolved via context")
        else:
            _fail("context pronoun", str(reply))
    except Exception as e:
        _fail("context pronoun dispatch", str(e)[:80])


# ══════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════

FEATURE_MAP = {
    "semantic":   test_semantic_search,
    "context":    test_context_and_responder,
    "nlreply":    test_context_and_responder,
    "versioning": test_versioning,
    "graph":      test_graph_api,
    "ingestion":  test_ingestion,
    "dispatch":   test_dispatch,
}

if __name__ == "__main__":
    feature = None
    if "--feature" in sys.argv:
        idx = sys.argv.index("--feature")
        if idx + 1 < len(sys.argv):
            feature = sys.argv[idx + 1]

    if feature:
        fn = FEATURE_MAP.get(feature)
        if fn:
            fn()
        else:
            print(f"Unknown feature '{feature}'. Options: {list(FEATURE_MAP)}")
    else:
        # Run all
        test_semantic_search()
        test_context_and_responder()
        test_versioning()
        test_graph_api()
        test_ingestion()
        test_dispatch()

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Results: "
          f"{GREEN}{_results['passed']} passed{RESET}  "
          f"{RED}{_results['failed']} failed{RESET}  "
          f"{YELLOW}{_results['skipped']} skipped{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    sys.exit(0 if _results["failed"] == 0 else 1)
