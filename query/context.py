"""
query/context.py — Per-user conversational context and session awareness.

Stores recent query history, last-accessed asset, preferred language, and
role-specific context for each user. Used by commands.dispatch() to make
replies contextually aware — e.g. "show its notes" after "machine M14"
resolves M14 from context rather than failing.

Context is stored in the user_context table (SQLite/PostgreSQL).
In-memory fallback dict used if DB write fails.
"""
import json
import uuid
from datetime import datetime
from typing import Optional
from core.db import query, execute

# In-memory fallback for context during a session
_mem: dict = {}


def _now() -> str:
    return datetime.utcnow().isoformat()


# ── DB operations ─────────────────────────────────────────────

def get_context(phone: str) -> dict:
    """
    Load persisted context for a user.
    Returns a dict with:
      last_asset_id: str | None
      last_intent:   str | None
      language:      str
      query_count:   int
      recent_assets: list[str]   (last 5 queried asset IDs)
      recent_intents: list[str]  (last 5 intents)
      preferences:   dict        (user-set preferences)
    """
    # Memory-first for same-session speed
    if phone in _mem:
        return _mem[phone]

    try:
        rows = query(
            "SELECT context_json FROM core.user_context WHERE phone = %s",
            (phone,)
        )
        if rows and rows[0].get("context_json"):
            ctx = rows[0]["context_json"]
            if isinstance(ctx, str):
                ctx = json.loads(ctx)
            _mem[phone] = ctx
            return ctx
    except Exception:
        pass

    # Default context
    default = {
        "last_asset_id": None,
        "last_intent": None,
        "language": "english",
        "query_count": 0,
        "recent_assets": [],
        "recent_intents": [],
        "preferences": {},
        "updated_at": _now(),
    }
    _mem[phone] = default
    return default


def update_context(phone: str, intent: str, asset_id: Optional[str],
                   language: str = "english") -> None:
    """
    Update context after each successful query.
    Maintains rolling window of last 5 assets and intents.
    """
    ctx = get_context(phone)

    # Update fields
    if asset_id:
        ctx["last_asset_id"] = asset_id
        assets = ctx.get("recent_assets", [])
        if asset_id not in assets:
            assets = [asset_id] + assets
        ctx["recent_assets"] = assets[:5]

    ctx["last_intent"]    = intent
    ctx["language"]       = language
    ctx["query_count"]    = ctx.get("query_count", 0) + 1
    ctx["updated_at"]     = _now()

    intents = ctx.get("recent_intents", [])
    intents = [intent] + [i for i in intents if i != intent]
    ctx["recent_intents"] = intents[:5]

    _mem[phone] = ctx
    _persist(phone, ctx)


def resolve_asset_from_context(phone: str, text: str,
                                parsed_asset_id: Optional[str]) -> Optional[str]:
    """
    If parsed_asset_id is None, check context for last-used asset.
    Handles pronouns and references like 'it', 'this machine', 'same one'.
    """
    if parsed_asset_id:
        return parsed_asset_id

    reference_words = {
        "it", "this", "that", "same", "the machine", "the asset",
        "isme", "yahi", "wahi", "ispe", "uski"      # hinglish references
    }
    text_lower = text.lower()
    if any(w in text_lower for w in reference_words):
        ctx = get_context(phone)
        return ctx.get("last_asset_id")

    return None


def get_language_for_user(phone: str, detected_language: str) -> str:
    """
    Returns language to use. User's stored preference takes priority
    over freshly detected language unless they've switched languages.
    """
    ctx = get_context(phone)
    stored = ctx.get("language", "english")

    # If detected language differs from stored, update (user switched)
    if detected_language != "english" and detected_language != stored:
        ctx["language"] = detected_language
        _mem[phone] = ctx
        _persist(phone, ctx)
        return detected_language

    return stored if stored else detected_language


def set_preference(phone: str, key: str, value) -> None:
    """Store a user preference (e.g. preferred units, verbosity level)."""
    ctx = get_context(phone)
    ctx.setdefault("preferences", {})[key] = value
    _mem[phone] = ctx
    _persist(phone, ctx)


def build_context_prompt(phone: str, user: dict) -> str:
    """
    Builds a context string to inject into LLM system prompt,
    giving the model awareness of who the user is and what they've been doing.
    """
    ctx = get_context(phone)
    role  = user.get("role", "viewer")
    name  = user.get("name", "Worker")
    shift = user.get("shift", "")
    line  = user.get("line", "")

    parts = [f"User: {name} | Role: {role}"]
    if shift:
        parts.append(f"Shift: {shift}")
    if line:
        parts.append(f"Line: {line}")

    last = ctx.get("last_asset_id")
    if last:
        parts.append(f"Last queried asset: {last}")

    recent = ctx.get("recent_assets", [])
    if len(recent) > 1:
        parts.append(f"Recently viewed: {', '.join(recent[:3])}")

    queries = ctx.get("query_count", 0)
    parts.append(f"Session queries: {queries}")

    return " | ".join(parts)


def _persist(phone: str, ctx: dict) -> None:
    """Write context to DB. Silently fails — context is best-effort."""
    ctx_json = json.dumps(ctx, default=str)
    try:
        # Try PostgreSQL upsert with schema-qualified table
        execute(
            """INSERT INTO core.user_context (phone, context_json, updated_at)
               VALUES (%s, %s, NOW())
               ON CONFLICT (phone) DO UPDATE SET
               context_json = EXCLUDED.context_json,
               updated_at   = NOW()""",
            (phone, ctx_json)
        )
    except Exception as e:
        print(f"[context] persist failed for {phone}: {e}")

