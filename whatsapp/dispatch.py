"""
whatsapp/dispatch.py — Updated central dispatcher.

Replaces the intent→query→format pipeline with:
  intent → semantic_search (DB-grounded) → responder (NL generation)

Every query goes through the relational DB. The LLM only:
  1. Parses intent
  2. Reformats/narrates the DB result for WhatsApp

User context is loaded before every dispatch and updated after.
"""
import uuid
from query import engine
from query.semantic_search import resolve_any_query, search_findings_by_keyword
from query.context import (
    get_context, update_context,
    resolve_asset_from_context, build_context_prompt,
)
from query.responder import generate_reply, generate_summary_narrative
from core.db import execute, query as db_query
from auth.rbac import PERMISSIONS, register_user, deregister_user, list_users

try:
    from rag.retriever import rag_query
    RAG_ENABLED = True
except ImportError:
    RAG_ENABLED = False


def dispatch(intent: str, asset_id, full_text: str,
             user: dict, language: str = "english") -> str:
    """
    Main dispatch function.
    Returns a WhatsApp-ready string reply.
    """
    phone = user.get("phone", "")

    # ── Context setup ─────────────────────────────────────────
    context_prompt = build_context_prompt(phone, user)
    resolved_aid   = resolve_asset_from_context(phone, full_text, asset_id)
    aid            = (resolved_aid or "").upper().strip()
    words          = full_text.strip().split()
    args           = words[1:] if len(words) > 1 else []

    # ── Route by intent ───────────────────────────────────────

    if intent == "machine":
        if aid:
            result = engine.get_asset(aid)
        else:
            # DB-grounded semantic search — keyword can be anything
            search = resolve_any_query(full_text)
            result = search["assets"][0] if search["assets"] else None
        if not result:
            return _no_match(full_text, "asset")
        update_context(phone, intent, result.get("asset_id"), language)
        return generate_reply(intent, result, full_text, user, context_prompt, language)

    if intent == "findings":
        if aid:
            result = engine.get_findings(aid)
            asset  = engine.get_asset(aid)
        else:
            search = resolve_any_query(full_text)
            if search["assets"]:
                aid    = search["assets"][0]["asset_id"]
                result = engine.get_findings(aid)
                asset  = search["assets"][0]
            else:
                # Search findings directly by keyword
                result = search_findings_by_keyword(full_text, limit=10)
                asset  = None
        if not result:
            return _no_match(full_text, "findings")
        update_context(phone, intent, aid or None, language)
        db_result = {"asset": asset, "findings": result} if asset else result
        return generate_reply(intent, db_result, full_text, user, context_prompt, language)

    if intent == "notes":
        if not aid:
            search = resolve_any_query(full_text)
            aid    = search["assets"][0]["asset_id"] if search["assets"] else None
        if not aid:
            return _no_match(full_text, "notes")
        result = engine.get_notes(aid)
        update_context(phone, intent, aid, language)
        return generate_reply(intent, result, full_text, user, context_prompt, language)

    if intent == "summary":
        if not aid:
            search = resolve_any_query(full_text)
            aid    = search["assets"][0]["asset_id"] if search["assets"] else None
        if not aid:
            return _no_match(full_text, "summary")
        result = engine.get_summary(aid)
        if not result:
            return _no_match(full_text, "summary")
        update_context(phone, intent, aid, language)
        # Expert/admin get narrative; technician/viewer get structured
        if user.get("role") in ("expert", "admin"):
            return generate_summary_narrative(result, user, language)
        return generate_reply(intent, result, full_text, user, context_prompt, language)

    if intent == "list":
        result = engine.list_assets()
        update_context(phone, intent, None, language)
        return generate_reply(intent, result, full_text, user, context_prompt, language)

    if intent == "critical":
        result = engine.critical_assets()
        update_context(phone, intent, None, language)
        return generate_reply(intent, result, full_text, user, context_prompt, language)

    if intent == "latest":
        result = engine.latest_inspections()
        update_context(phone, intent, None, language)
        return generate_reply(intent, result, full_text, user, context_prompt, language)

    if intent == "search":
        keyword = " ".join(args) if args else full_text
        result  = resolve_any_query(keyword, limit=10)
        update_context(phone, intent, None, language)
        if not result["assets"] and not result["findings"]:
            return _no_match(keyword, "search")
        return generate_reply(intent, result, full_text, user, context_prompt, language)

    if intent == "linestatus":
        line   = " ".join(args) if args else full_text.replace("linestatus", "").strip()
        result = engine.get_line_status(line)
        update_context(phone, intent, None, language)
        return generate_reply(intent, result, full_text, user, context_prompt, language)

    if intent == "ask":
        if not RAG_ENABLED:
            return "RAG pipeline not available. Install chromadb and pypdf, then restart."
        result = rag_query(full_text, aid or None)
        update_context(phone, intent, aid or None, language)
        return result  # rag_query already returns formatted string

    if intent == "image":
        a = _resolve_asset(aid, full_text)
        if not a:
            return _no_match(full_text, "image")
        rows = db_query(
            "SELECT file_path, label FROM batch_images WHERE asset_id = %s",
            (a["asset_id"],)
        )
        if not rows:
            try:
                rows = db_query(
                    "SELECT file_path, label FROM batch_images WHERE asset_id = ?",
                    (a["asset_id"],)
                )
            except Exception:
                rows = []
        if not rows:
            return f"No image found for {a['asset_id']}."
        from whatsapp.media_sender import send_image_reply
        send_image_reply(
            user["phone"],
            rows[0]["file_path"],
            caption=f"CV output — {a['asset_id']} | {rows[0]['label']}",
        )
        update_context(phone, intent, a["asset_id"], language)
        return ""

    if intent == "telemetry":
        from tools.telemetry import handle_telemetry_message
        reply = handle_telemetry_message(full_text, user)
        update_context(phone, intent, aid or None, language)
        return reply

    if intent == "calculate":
        if not aid:
            search = resolve_any_query(full_text)
            aid    = search["assets"][0]["asset_id"] if search["assets"] else None
        if not aid:
            return "Which machine? Try: *calculate M14 temperature*"
        from tools.calculator import summarise_telemetry_for_asset
        result = summarise_telemetry_for_asset(aid)
        update_context(phone, intent, aid, language)
        return result.get("reply", "No telemetry data found.")

    if intent == "convert":
        from tools.calculator import convert_unit
        import re as _re
        nums = _re.findall(r"[-+]?\d*\.?\d+", full_text)
        if not nums:
            return "Usage: *convert 45 celsius fahrenheit*"
        value      = float(nums[0])
        text_lower = full_text.lower()
        pairs      = [
            ("celsius","fahrenheit"), ("fahrenheit","celsius"),
            ("bar","psi"), ("psi","bar"),
            ("mm","cm"), ("cm","mm"),
        ]
        for frm, to in pairs:
            if frm in text_lower and to in text_lower:
                result = convert_unit(value, frm, to)
                return result.get("reply", result.get("error", "Conversion failed."))
        return "Could not find units.\nTry: *convert 45 celsius fahrenheit*"

    if intent == "bim":
        from ingestion.bim_ingest import list_bim_elements, get_bim_element
        if aid:
            el = get_bim_element(aid)
            if el:
                result = el
                update_context(phone, intent, aid, language)
                return generate_reply(intent, result, full_text, user,
                                      context_prompt, language)
        keyword = full_text.lower().replace("bim", "").strip()
        rows    = list_bim_elements()
        if keyword:
            rows = [r for r in rows if
                    keyword in str(r.get("name","")).lower() or
                    keyword in str(r.get("type","")).lower() or
                    keyword in str(r.get("level","")).lower()]
        update_context(phone, intent, None, language)
        return generate_reply(intent, rows[:8], full_text, user,
                               context_prompt, language)

    if intent == "addnote":
        a = _resolve_asset(aid, full_text)
        if not a or len(args) < 2:
            return "Usage: addnote [id] [note text]"
        ok = engine.add_note(a["asset_id"], " ".join(args[1:]), user["name"])
        update_context(phone, intent, a["asset_id"], language)
        return f"✅ Note added to *{a['asset_id']}*." if ok else "Asset not found."

    if intent == "report":
        a = _resolve_asset(aid, full_text)
        if not a or len(args) < 2:
            return "Usage: report [id] [description]"
        execute(
            """INSERT INTO cv.detections
               (detection_id, asset_id, object, condition, confidence, source)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (str(uuid.uuid4()), a["asset_id"], "Field report",
             " ".join(args[1:]), 0.5, "field_report")
        )
        update_context(phone, intent, a["asset_id"], language)
        return f"✅ Report submitted for *{a['asset_id']}*."

    if intent == "adduser":
        if len(args) < 3:
            return "Usage: adduser [phone] [name] [role] [shift?] [line?]"
        shift = args[3] if len(args) > 3 else ""
        line  = args[4] if len(args) > 4 else ""
        return register_user(args[0], args[1], args[2], shift, line)

    if intent == "removeuser":
        if not args:
            return "Usage: removeuser [phone]"
        return deregister_user(args[0])

    if intent == "listusers":
        return list_users()

    if intent == "help":
        return _help_text(user.get("role", "viewer"))

    return (
        f"I didn't understand: *'{full_text}'*\n"
        "Type *help* to see available commands."
    )


# ── Helpers ───────────────────────────────────────────────────

def _resolve_asset(aid: str, full_text: str):
    if aid:
        a = engine.get_asset(aid)
        if a:
            return a
    from query.engine import find_asset_by_name
    return find_asset_by_name(full_text)


def _no_match(query_text: str, entity: str) -> str:
    return (
        f"No {entity} found matching *'{query_text}'*.\n"
        f"Try: *list* to see all assets, or use the machine ID directly."
    )


def _execute_compat(sql_pg, sql_sq, params):
    try:
        execute(sql_pg, params)
    except Exception:
        execute(sql_sq, params)


def _help_text(role: str) -> str:
    descs = {
        "machine":    "machine [id or name]          — asset info",
        "findings":   "findings [id or name]         — defects by severity",
        "notes":      "notes [id or name]            — expert notes",
        "summary":    "summary [id or name]          — full overview",
        "list":       "list                          — all assets",
        "critical":   "critical                      — critical findings",
        "latest":     "latest                        — recent inspections",
        "ask":        "ask [question]                — search documents",
        "image":      "image [id]                   — CV output image",
        "search":     "search [keyword]              — search all findings",
        "telemetry":  "M14 temperature 67 degrees   — log sensor reading",
        "calculate":  "calculate M14 temperature     — analyse readings",
        "convert":    "convert 45 celsius fahrenheit — unit conversion",
        "bim":        "bim [element or space]        — BIM element info",
        "linestatus": "linestatus [line]             — line overview",
        "addnote":    "addnote [id] [text]           — add expert note",
        "report":     "report [id] [description]     — field report",
        "adduser":    "adduser [phone] [name] [role] [shift] [line]",
        "removeuser": "removeuser [phone]",
        "listusers":  "listusers",
    }
    cmds  = PERMISSIONS.get(role, [])
    lines = [f"💬 *Commands for {role}*\n"]
    for c in cmds:
        if c in descs:
            lines.append(f"• {descs[c]}")
    return "\n".join(lines)
