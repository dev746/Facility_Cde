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


SYSTEM_BASE = """You are a highly articulate, professional, and context-aware industrial facility assistant communicating over WhatsApp.
Your task is to present raw database query results in a clear, well-structured, and helpful conversational manner.

Rules for response composition:
1. Grounding: Never invent facts. Rely ONLY on the provided database results. If no data exists or a value is missing, state it clearly.
2. Structure:
   - Start with a concise, direct summary of the information requested.
   - Use structured bullet points (•) for presenting lists, metrics, or detailed findings.
   - End with a brief, actionable recommendation or status update if appropriate.
3. Tone and Style:
   - Address the user by name when introducing information or alerts (e.g., "Hello Ravi," or "Hi Priya,").
   - Use WhatsApp formatting: *bold* for keys/labels, and standard emoji indicator highlights (🚨 for critical issues/errors, ⚠️ for warnings, ✅ for normal/operational statuses).
   - Do not use robotic placeholder phrases, generic transitions, or unnecessary fluff. Be direct, articulate, and clear.
4. Word Limit: Keep the reply under 300 words.
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

    lang_directives = {
        "english": "Respond in clear, professional, and grammatically correct English.",
        "hindi": "Respond in polite, formal Hindi using the Devanagari script. Ensure technical terms from the database (like asset IDs, metrics, or severity labels) are retained in English/Latin characters or translated naturally.",
        "kannada": "Respond in polite, grammatically correct Kannada script. Retain technical names (e.g., M14, CNC Lathe, Spindle) in their standard form.",
        "hinglish": "Respond in natural, conversational Hinglish (Hindi words written in Roman script mixed naturally with English technical terms, e.g., 'M14 ka state baseline levels par normal hai. Spindle wear abhi monitor kiya ja raha hai.'). Avoid robotic phrasing."
    }
    directive = lang_directives.get(language.lower(), lang_directives["english"])
    system += f"\n\nLANGUAGE & STYLE INSTRUCTION: {directive}"

    # Serialise result for the LLM
    if db_result is None:
        result_str = "No data found."
    elif isinstance(db_result, dict):
        result_str = _json.dumps(db_result, default=str, indent=2)
    elif isinstance(db_result, list):
        result_str = _json.dumps(db_result[:15], default=str, indent=2)
    else:
        result_str = str(db_result)

    if intent == "greeting":
        user_prompt = (
            f"User ({name}, {role}) casually addressed the system: \"{query_text}\"\n\n"
            f"Please generate a highly articulate, warm welcome and activation message.\n"
            f"Guidelines:\n"
            f"1. Acknowledge and greet the user by name ({name}) and mention their registered role ({role}) to confirm system activation.\n"
            f"2. Context Analysis: Casually refer to their past actions found in their context (e.g., if they have a 'Last queried asset' or any 'Session queries'). Mention these details naturally (e.g., 'Welcome back! I see you last checked asset M14.' or 'You've run 3 queries this shift. How can I help you next?').\n"
            f"3. Commands suggestions: Recommend 2-3 specific WhatsApp commands appropriate for their role ({role}) (e.g., technicians can check 'findings' or log 'telemetry', admins can 'list' or register workers, viewers can view a 'summary' or 'list'). Keep it structured and action-oriented."
        )
    else:
        user_prompt = (
            f"User ({name}, {role}) asked: \"{query_text}\"\n\n"
            f"Intent detected: {intent}\n\n"
            f"Database result:\n{result_str}\n\n"
            f"Write a clear WhatsApp reply based only on the above data."
        )

    try:
        return chat(system, user_prompt, temperature=0.15, max_tokens=400)
    except Exception as e:
        err = str(e).lower()
        if "429" not in err and "rate" not in err and "quota" not in err:
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
    
    lang_directives = {
        "english": "Respond in clear, professional, and grammatically correct English.",
        "hindi": "Respond in polite, formal Hindi using the Devanagari script. Ensure technical terms from the database are retained in English/Latin characters or translated naturally.",
        "kannada": "Respond in polite, grammatically correct Kannada script. Retain technical names in their standard form.",
        "hinglish": "Respond in natural, conversational Hinglish (Hindi words written in Roman script mixed naturally with English technical terms). Avoid robotic phrasing."
    }
    directive = lang_directives.get(language.lower(), lang_directives["english"])
    system += f"\n\nLANGUAGE & STYLE INSTRUCTION: {directive}"

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
    if intent == "greeting":
        name = user.get("name", "there")
        role = user.get("role", "viewer")
        return (
            f"👋 Hello {name}!\n"
            f"Your role *{role}* is successfully activated in the Facility CDE.\n"
            f"Type *help* to see available commands."
        )

    if result is None:
        return "No data found for your query."

    if isinstance(result, dict):
        # Shape 1: flat row from core.asset_summary materialized view
        if "cv_detection_count" in result:
            cv  = result.get("cv_detection_count", 0)
            sc  = result.get("scrap_batch_count", 0)
            bim = result.get("bim_element_count", 0)
            nt  = result.get("note_count", 0)
            la  = str(result.get("last_activity_at") or "N/A")[:10]
            return (
                f"📊 *{result.get('asset_id','?')} — {result.get('name','?')}*\n"
                f"├ Type: {result.get('type','Unknown')}\n"
                f"├ Location: {result.get('location','Unknown')}\n"
                f"├ CV Detections: {cv}\n"
                f"├ Scrap Batches: {sc}\n"
                f"├ BIM Elements: {bim}\n"
                f"├ Expert Notes: {nt}\n"
                f"└ Last Activity: {la}"
            )
        # Shape 2: computed summary {"asset": {...}, "finding_count": N, ...}
        if "asset" in result:
            a  = result["asset"]
            fc = result.get("finding_count", 0)
            nc = result.get("note_count", 0)
            sc = result.get("severity_counts", {})
            tf = result.get("top_finding")
            status = "🚨 Critical" if result.get("critical") else ("⚠️ Attention" if fc > 5 else "✅ OK")
            lines = [
                f"📊 *{a.get('asset_id','?')} — {a.get('name','?')}*",
                f"├ Type: {a.get('type','?')}",
                f"├ Location: {a.get('location','?')}",
                f"├ Findings: {fc} (🚨{sc.get('critical',0)} ⚠️{sc.get('high',0)})",
                f"├ Notes: {nc}",
                f"└ Status: {status}",
            ]
            if tf:
                lines.append(f"\n*Top Finding:* {tf.get('object','')} — {tf.get('condition','')}")
            return "\n".join(lines)
        # Shape 3: generic dict — just dump key-values
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
