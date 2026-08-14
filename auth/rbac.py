from time import time
from collections import defaultdict
from core.db import query, execute

PERMISSIONS: dict = {
    "admin":      ["machine","findings","notes","summary","list","critical","latest",
                   "ask","image","telemetry","calculate","convert",
                   "addnote","report","search","linestatus","help",
                   "adduser","removeuser","listusers"],
    "expert":     ["machine","findings","notes","summary","list","critical","latest",
                   "ask","image","telemetry","calculate","convert",
                   "addnote","search","linestatus","help"],
    "technician": ["machine","findings","summary","latest","image",
                   "telemetry","calculate","convert","report","search","help"],
    "viewer":     ["summary","list","linestatus","help"],
}

_rate_store: dict = defaultdict(list)
RATE_LIMIT  = 10
RATE_WINDOW = 60


def get_user(phone: str) -> dict | None:
    rows = query("SELECT * FROM auth.users WHERE phone = %s AND is_active = true", (phone,))
    return rows[0] if rows else None


def can_access(role: str, intent: str) -> bool:
    return intent in PERMISSIONS.get(role, [])


def is_rate_limited(phone: str) -> bool:
    now = time()
    _rate_store[phone] = [t for t in _rate_store[phone] if now - t < RATE_WINDOW]
    if len(_rate_store[phone]) >= RATE_LIMIT:
        return True
    _rate_store[phone].append(now)
    return False


def register_user(phone: str, name: str, role: str,
                  shift: str = "", line: str = "") -> str:
    if role not in PERMISSIONS:
        return f"❌ Invalid role. Choose: {', '.join(PERMISSIONS)}"
    try:
        execute(
            """INSERT INTO auth.users (phone, name, role, is_active)
               VALUES (%s, %s, %s, true)
               ON CONFLICT (phone) DO UPDATE SET name=EXCLUDED.name, role=EXCLUDED.role, is_active=true""",
            (phone, name, role),
        )
        return f"✅ {name} ({phone}) registered as {role}."
    except Exception as e:
        return f"❌ Registration failed: {e}"


def deregister_user(phone: str) -> str:
    execute("UPDATE auth.users SET is_active = false WHERE phone = %s", (phone,))
    return f"✅ {phone} deactivated."


def list_users() -> str:
    rows = query(
        "SELECT phone, name, role FROM auth.users WHERE is_active = true ORDER BY role"
    )
    if not rows:
        return "No active users."
    lines = [f"👥 *{len(rows)} active user(s)*"]
    for r in rows:
        lines.append(f"• {r['name']} ({r['phone']}) — {r['role']}")
    return "\n".join(lines)
