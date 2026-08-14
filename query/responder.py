"""
query/responder.py — Natural language response generator.

Takes structured DB results and generates a conversational,
role-aware, language-aware WhatsApp reply using Nemotron.

The LLM's job here is ONLY formatting and language — it never
invents data. All facts come from the DB result passed in.

User context is injected into every system prompt so replies
are aware of:
  - Who the user is (name, role, shift, line)
  - What they last queried
  - How many queries they've made this session
  - Their preferred language
"""
from core.llm import chat


SYSTEM_BASE = """You are a concise industrial facility assistant replying over WhatsApp.
You format DB query results into a clear, natural reply.

Rules:
- Never invent data — use ONLY what is in the provided result
- Keep replies under 300 words
- Use WhatsApp formatting: *bold* for labels, bullet points with •
- If data shows a critical issue, lead with 🚨
- If data is normal, use ✅
- Match the user's language (Hindi/Hinglish if they wrote in it)
- Address the user by name when greeting or giving important alerts
- Be direct — no filler phrases like "Great question!" or "Certainly!"
"""


def generate_reply(
    intent: str,
    db_result,
    query_text: str,
    user: dict,
    context_prompt: str = "",
    language: str = "english",
) -> str:
    """
    Main entry point. Takes DB result (any structure) and returns
    a WhatsApp-ready natural language string.

    Args:
        intent:         parsed intent string
        db_result:      raw result from engine / semantic_search
        query_text:     original user message
        user:           user dict from DB (name, role, shift, line)
        context_prompt: pre-built context string from context.py
        language:       detected/stored language
    """
    import json as _json

    name = user.get("name", "there")
    role = user.get("role", "viewer")

    system = SYSTEM_BASE
    if context_prompt:
        system += f"\n\nUser context: {context_prompt}"

    if language in ("hindi", "hinglish"):
        system += "\n\nReply in Hinglish — mix Hindi and English naturally as WhatsApp workers do."

    # Serialise result for the LLM
    if db_result is None:
        result_str = "No data found."
    elif isinstance(db_result, dict):
        result_str = _json.dumps(db_result, default=str, indent=2)
    elif isinstance(db_result, list):
        result_str = _json.dumps(db_result[:15], default=str, indent=2)
    else:
        result_str = str(db_result)

    user_prompt = (
        f"User ({name}, {role}) asked: \"{query_text}\"\n\n"
        f"Intent detected: {intent}\n\n"
        f"Database result:\n{result_str}\n\n"
        f"Write a clear WhatsApp reply based only on the above data."
    )

    try:
        return chat(system, user_prompt, temperature=0.15, max_tokens=400)
    except Exception as e:
        print(f"[responder] LLM failed: {e}, using structured fallback")
        return _structured_fallback(intent, db_result, user)


def generate_alert(asset_id: str, metric: str, value: float,
                   threshold: str, user: dict) -> str:
    """Generate a concise threshold breach alert message."""
    system = (
        "You write short industrial safety alerts for WhatsApp. "
        "One sentence max. Include asset ID, metric, value, and urgency."
    )
    prompt = (
        f"Asset {asset_id}: {metric} reading of {value} has breached {threshold}. "
        f"Alert {user.get('name','worker')} ({user.get('role','technician')})."
    )
    try:
        return chat(system, prompt, temperature=0.1, max_tokens=80)
    except Exception:
        return f"🚨 *Alert — {asset_id}*: {metric} = {value} has exceeded {threshold}."


def generate_summary_narrative(summary: dict, user: dict,
                                language: str = "english") -> str:
    """
    Generates a paragraph-style narrative summary for an asset,
    suitable for an expert or admin who wants full context.
    """
    import json as _json

    system = SYSTEM_BASE
    if language in ("hindi", "hinglish"):
        system += "\n\nReply in Hinglish."
    system += (
        "\n\nFor summary requests, write 2-3 sentences of narrative "
        "describing the asset's current state, top issues, and recommended action. "
        "Then list key numbers. Never pad — be direct."
    )

    prompt = (
        f"{user.get('name','Engineer')} ({user.get('role','expert')}) wants a summary.\n\n"
        f"Data:\n{_json.dumps(summary, default=str, indent=2)}"
    )

    try:
        return chat(system, prompt, temperature=0.2, max_tokens=350)
    except Exception:
        return _structured_fallback("summary", summary, user)


def _structured_fallback(intent: str, result, user: dict) -> str:
    """
    Non-LLM fallback formatter when Nemotron API is unavailable.
    Returns a simple structured string from the raw DB result.
    """
    if result is None:
        return "No data found for your query."

    if isinstance(result, dict):
        if "asset" in result:  # summary shape
            a = result["asset"]
            return (
                f"📊 *{a.get('asset_id','?')} — {a.get('name','?')}*\n"
                f"Findings: {result.get('finding_count',0)}\n"
                f"Critical: {'Yes' if result.get('critical') else 'No'}"
            )
        lines = [f"• {k}: {v}" for k, v in list(result.items())[:8]]
        return "\n".join(lines)

    if isinstance(result, list):
        if not result:
            return "No records found."
        lines = []
        for item in result[:5]:
            if isinstance(item, dict):
                key = item.get("asset_id") or item.get("name") or str(list(item.values())[0])
                lines.append(f"• {key}")
        return "\n".join(lines) if lines else "No records found."

    return str(result)
