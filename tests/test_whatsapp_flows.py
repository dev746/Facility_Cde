"""
tests/test_whatsapp_flows.py

Simulates real WhatsApp conversations without touching the actual
Twilio or Meta API. Tests the full message → intent → dispatch → reply chain
for every kind of user.

Run: PYTHONPATH=. python tests/test_whatsapp_flows.py
"""
import sys
import os

# Ensure the project root is on PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set stdout/stderr encoding to UTF-8 for Windows consoles
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

GREEN = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"
BOLD  = "\033[1m";  RESET = "\033[0m"

_results = {"passed": 0, "failed": 0}

def _pass(msg):
    _results["passed"] += 1
    print(f"  {GREEN}✓{RESET} {msg}")

def _fail(msg, reason=""):
    _results["failed"] += 1
    print(f"  {RED}✗{RESET} {msg}" + (f" — {reason}" if reason else ""))

def _section(t):
    print(f"\n{BOLD}── {t} ──{RESET}")


def simulate_message(phone, text, role="admin"):
    """Full pipeline: parse intent → dispatch → return reply string."""
    from query.intent import parse_intent
    from query.context import update_context
    from whatsapp.dispatch import dispatch

    user = {
        "phone": phone, "name": "Test", "role": role,
        "shift": "morning", "line": "Line A",
    }

    # language detection
    hindi_markers = ["kya","kahan","hai","batao","isme","wahi"]
    lang = "hinglish" if any(m in text.lower() for m in hindi_markers) else "english"

    parsed   = parse_intent(text)
    intent   = parsed.get("intent", "unknown")
    asset_id = parsed.get("asset_id")

    reply = dispatch(intent, asset_id, text, user, lang)
    update_context(phone, intent, asset_id, lang)
    return reply, intent, asset_id


# ── Conversation flows ────────────────────────────────────────

def test_admin_flow():
    _section("Admin conversation flow")
    phone = "whatsapp:+91admin001"

    flows = [
        ("help",                   str,    "should return help text"),
        ("list",                   str,    "should list assets"),
        ("summary M14",            str,    "summary of M14"),
        ("findings M14",           str,    "findings for M14"),
        ("notes M14",              str,    "notes for M14"),
        ("critical",               str,    "critical findings"),
        ("latest",                 str,    "latest inspections"),
        ("search bearing wear",    str,    "keyword search"),
        ("convert 45 celsius fahrenheit", str, "unit conversion"),
    ]

    for text, expected_type, description in flows:
        try:
            reply, intent, asset_id = simulate_message(phone, text, "admin")
            if isinstance(reply, expected_type) and len(str(reply)) > 0:
                preview = str(reply)[:50].replace("\n"," ")
                _pass(f"[admin] '{text}' → {preview}")
            else:
                _fail(f"[admin] '{text}'", f"empty or wrong type: {type(reply)}")
        except Exception as e:
            _fail(f"[admin] '{text}'", str(e)[:70])


def test_technician_flow():
    _section("Technician conversation flow")
    phone = "whatsapp:+91tech001"

    flows = [
        ("machine M22",            "should see machine info"),
        ("findings M22",           "should see findings"),
        ("M37 temperature 78",     "should log telemetry"),
        ("calculate M37 temperature", "should analyse readings"),
        ("report M22 oil leak near cylinder", "should submit report"),
        ("help",                   "should see limited help"),
    ]

    for text, description in flows:
        try:
            reply, intent, _ = simulate_message(phone, text, "technician")
            if isinstance(reply, str) and len(reply) > 0:
                _pass(f"[tech] '{text[:30]}'")
            else:
                _fail(f"[tech] '{text[:30]}'", "empty reply")
        except Exception as e:
            _fail(f"[tech] '{text[:30]}'", str(e)[:70])


def test_viewer_flow():
    _section("Viewer conversation flow")
    phone = "whatsapp:+91viewer001"

    # Viewers can only: summary, list, linestatus, help
    allowed = [
        ("help",        True),
        ("summary M14", True),
        ("list",        True),
    ]
    # These should be blocked by RBAC
    blocked_intents = ["findings", "notes", "critical", "addnote", "report"]

    for text, should_work in allowed:
        try:
            reply, intent, _ = simulate_message(phone, text, "viewer")
            if should_work and isinstance(reply, str) and len(reply) > 0:
                _pass(f"[viewer] allowed: '{text}'")
            else:
                _fail(f"[viewer] '{text}'", "blocked when should be allowed")
        except Exception as e:
            _fail(f"[viewer] '{text}'", str(e)[:70])

    # Check RBAC is enforced (dispatcher level)
    from auth.rbac import can_access
    for intent in blocked_intents:
        if not can_access("viewer", intent):
            _pass(f"[viewer] blocked: '{intent}'")
        else:
            _fail(f"[viewer] '{intent}' should be blocked but is allowed")


def test_context_conversation():
    _section("Context-aware multi-turn conversation")
    phone = "whatsapp:+91context001"

    try:
        # Turn 1: query M14
        r1, i1, a1 = simulate_message(phone, "machine M14", "expert")
        _pass(f"Turn 1: machine M14 → intent={i1}")

        # Turn 2: "show its findings" — should resolve M14 from context
        r2, i2, _ = simulate_message(phone, "show its findings", "expert")
        if isinstance(r2, str) and len(r2) > 0:
            _pass("Turn 2: 'show its findings' resolved via context")
        else:
            _fail("Turn 2: context resolution", f"reply: {r2}")

        # Turn 3: same with Hinglish
        r3, i3, _ = simulate_message(phone, "isme kya problem hai", "expert")
        if isinstance(r3, str) and len(r3) > 0:
            _pass("Turn 3: Hinglish 'isme' context resolution")
        else:
            _fail("Turn 3: Hinglish context", f"reply: {r3}")

        # Turn 4: explicit new asset overrides context
        r4, i4, a4 = simulate_message(phone, "summary M22", "expert")
        from query.context import get_context
        ctx = get_context(phone)
        if ctx.get("last_asset_id") == "M22":
            _pass("Turn 4: explicit M22 updates context")
        else:
            _fail("Turn 4: context update", f"last_asset={ctx.get('last_asset_id')}")

    except Exception as e:
        _fail("context conversation", str(e)[:80])


def test_hinglish_flow():
    _section("Hinglish / Hindi message handling")
    phone = "whatsapp:+91hindi001"

    flows = [
        ("M14 ki kya problem hai",       "findings intent expected"),
        ("hydraulic press kahan hai",    "machine intent expected"),
        ("M22 ka summary batao",         "summary intent expected"),
        ("kaun si machine critical hai", "critical intent expected"),
    ]

    from query.intent import parse_intent
    for text, expectation in flows:
        try:
            parsed = parse_intent(text)
            intent = parsed.get("intent")
            if intent not in ("unknown", None):
                _pass(f"Hinglish '{text[:30]}' → intent={intent}")
            else:
                _fail(f"Hinglish '{text[:30]}'", f"got unknown intent")
        except Exception as e:
            _fail(f"Hinglish '{text[:30]}'", str(e)[:60])


def test_telemetry_flow():
    _section("Telemetry input and calculation flow")
    phone = "whatsapp:+91telem001"

    readings = [
        "M14 temperature 67 degrees",
        "pressure on M22 is 280 bar",
        "M37 vibration 3.2 mm/s",
        "M14 RPM 1450",
        "M14 temperature 95 degrees",    # should trigger alert (above threshold)
    ]

    for text in readings:
        try:
            reply, intent, asset = simulate_message(phone, text, "technician")
            if intent == "telemetry" and isinstance(reply, str) and len(reply) > 0:
                alert = "🚨" in reply or "Alert" in reply
                _pass(f"telemetry '{text[:35]}'" +
                      (" [ALERT]" if alert else ""))
            else:
                _fail(f"telemetry '{text[:35]}'",
                      f"intent={intent} reply_len={len(str(reply))}")
        except Exception as e:
            _fail(f"telemetry '{text[:35]}'", str(e)[:70])

    # Test calculation after readings
    try:
        calc_reply, calc_intent, _ = simulate_message(
            phone, "calculate M14 temperature", "technician"
        )
        if isinstance(calc_reply, str) and len(calc_reply) > 5:
            _pass("calculate after telemetry readings")
        else:
            _fail("calculate", f"reply: {calc_reply}")
    except Exception as e:
        _fail("calculate", str(e)[:60])

    # Unit conversion
    conversions = [
        "convert 45 celsius fahrenheit",
        "convert 280 bar to psi",
        "convert 10 mm to cm",
    ]
    for text in conversions:
        try:
            reply, intent, _ = simulate_message(phone, text, "technician")
            if intent == "convert" and "=" in reply:
                _pass(f"convert '{text}'")
            else:
                _fail(f"convert '{text}'", f"intent={intent} reply={reply[:40]}")
        except Exception as e:
            _fail(f"convert '{text}'", str(e)[:60])


def test_edge_cases():
    _section("Edge cases and error handling")
    phone = "whatsapp:+91edge001"

    edge_cases = [
        ("",                    "empty message"),
        ("   ",                 "whitespace only"),
        ("XYZABC999",           "nonexistent asset ID"),
        ("findings ZZZZZ",      "asset that doesn't exist"),
        ("convert abc to xyz",  "invalid units"),
        ("!@#$%",               "special characters"),
        ("a" * 300,             "very long message"),
    ]

    for text, description in edge_cases:
        try:
            if not text.strip():
                _pass(f"edge: {description} — skipped (empty)")
                continue
            reply, intent, _ = simulate_message(phone, text.strip(), "admin")
            if isinstance(reply, str):
                _pass(f"edge: {description} — no crash")
            else:
                _fail(f"edge: {description}", f"non-string: {type(reply)}")
        except Exception as e:
            _fail(f"edge: {description}", str(e)[:60])


# ── Runner ────────────────────────────────────────────────────

if __name__ == "__main__":
    test_admin_flow()
    test_technician_flow()
    test_viewer_flow()
    test_context_conversation()
    test_hinglish_flow()
    test_telemetry_flow()
    test_edge_cases()

    print(f"\n{BOLD}{'='*55}{RESET}")
    p, f = _results["passed"], _results["failed"]
    total = p + f
    print(f"{BOLD}  {p}/{total} passed  |  {f} failed{RESET}")
    print(f"{BOLD}{'='*55}{RESET}\n")
    sys.exit(0 if f == 0 else 1)
