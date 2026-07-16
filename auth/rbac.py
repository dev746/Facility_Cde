from time import time
from collections import defaultdict
from core.db import query, execute

PERMISSIONS: dict = {
    "admin":      ["machine", "findings", "notes", "summary", "list", "critical",
                   "latest", "ask", "image", "addnote", "report", "help",
                   "adduser", "removeuser", "listusers", "search", "linestatus"],
    "expert":     ["machine", "findings", "notes", "summary", "list", "critical",
                   "latest", "ask", "image", "addnote", "help", "search", "linestatus"],
    "technician": ["machine", "findings", "summary", "latest", "image",
                   "report", "ask", "help", "search"],
    "viewer":     ["summary", "list", "help", "linestatus"],
}

_rate_store: dict = defaultdict(list)
RATE_LIMIT  = 10
RATE_WINDOW = 60


def get_user(phone: str) -> dict | None:
    rows = query("SELECT * FROM users WHERE phone=? AND is_active=1", (phone,))
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


def register_user(phone: str, name: str, role: str, shift: str = "", line: str = "") -> str:
    if role not in PERMISSIONS:
        return f"❌ Invalid role. Choose: {', '.join(PERMISSIONS)}"
    try:
        execute(
            "INSERT INTO users (phone, name, role, shift, line) VALUES (?,?,?,?,?)",
            (phone, name, role, shift, line),
        )
        return f"✅ {name} ({phone}) registered as {role}."
    except Exception:
        return "❌ Phone already registered."


def deregister_user(phone: str) -> str:
    execute("UPDATE users SET is_active=0 WHERE phone=?", (phone,))
    return f"✅ {phone} deactivated."


def list_users() -> str:
    rows = query("SELECT phone, name, role, shift, line FROM users WHERE is_active=1 ORDER BY role")
    if not rows:
        return "No active users."
    lines = [f"👥 *{len(rows)} active user(s)*"]
    for r in rows:
        extra = f" | {r['shift']} shift" if r.get("shift") else ""
        extra += f" | {r['line']}" if r.get("line") else ""
        lines.append(f"• {r['name']} — {r['role']}{extra}")
    return "\n".join(lines)
