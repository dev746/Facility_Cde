import uuid
import json
from query import engine
from core.db import execute, query as db_query
from auth.rbac import PERMISSIONS, register_user, deregister_user, list_users
from core.llm import detect_language
from query.responder import generate_reply

try:
    from rag.retriever import rag_query
    RAG_ENABLED = True
except ImportError:
    RAG_ENABLED = False


def _pct(v) -> str:
    try:
        return f"{float(v)*100:.0f}%"
    except (TypeError, ValueError):
        return "N/A"


def _resolve(aid: str, full_text: str):
    if aid:
        a = engine.get_asset(aid)
        if a:
            return a
    return engine.resolve_asset(full_text)



# ── Formatters ────────────────────────────────────────────────

def fmt_asset(a: dict) -> str:
    lines = [f"🏭 *{a.get('asset_id', 'N/A')} — {a.get('name', 'N/A')}*"]
    if a.get("type"):
        lines.append(f"├ Type: {a['type']}")
    if a.get("location"):
        lines.append(f"├ Location: {a['location']}")
    if a.get("line"):
        lines.append(f"├ Line: {a['line']}")
    if a.get("zone"):
        lines.append(f"├ Zone: {a['zone']}")
    lines.append(f"└ Status: {a.get('status','active').capitalize()}")
    return "\n".join(lines)


def fmt_findings(rows: list, asset_name: str = "") -> str:
    if not rows:
        return f"✅ No findings recorded{' for ' + asset_name if asset_name else ''}."
    critical = [f for f in rows if f.get("severity") == "critical"]
    high     = [f for f in rows if f.get("severity") == "high"]
    other    = [f for f in rows if f.get("severity") not in ("critical","high")]
    lines    = [f"🔍 *{len(rows)} finding(s){' — ' + asset_name if asset_name else ''}*\n"]
    if critical:
        lines.append("🚨 *Critical:*")
        for f in critical[:3]:
            lines.append(f"  • {f['object']} — {f['condition']} ({_pct(f['confidence'])})")
    if high:
        lines.append("⚠️ *High:*")
        for f in high[:3]:
            lines.append(f"  • {f['object']} — {f['condition']} ({_pct(f['confidence'])})")
    if other and not critical and not high:
        lines.append("📋 *Observations:*")
        for f in other[:4]:
            lines.append(f"  • {f['object']} — {f['condition']}")
    rem = len(rows) - 6
    if rem > 0:
        lines.append(f"\n_...{rem} more._")
    return "\n".join(lines)


def fmt_notes(rows: list) -> str:
    if not rows:
        return "No expert notes recorded."
    lines = [f"📝 *{len(rows)} note(s)*"]
    for n in rows[:5]:
        lines.append(f"• [{n['author']}] {n['comment']}")
    return "\n".join(lines)


def fmt_summary(s: dict) -> str:
    # If s is a row from core.asset_summary view directly
    if "cv_detection_count" in s:
        cv_cnt    = s.get("cv_detection_count", 0)
        scrap_cnt = s.get("scrap_batch_count", 0)
        bim_cnt   = s.get("bim_element_count", 0)
        notes_cnt = s.get("note_count", 0)
        last_act  = s.get("last_activity_at") or "N/A"
        
        lines = [
            f"📊 *{s['asset_id']} — {s['name']}*",
            f"├ Type: {s.get('type', 'Unknown')}",
            f"├ Location: {s.get('location', 'Unknown')}",
            f"├ Cross-Functional Data:",
            f"│  • {cv_cnt} CV detection(s)",
            f"│  • {scrap_cnt} scrap batch(es)",
            f"│  • {bim_cnt} BIM element(s)",
            f"│  • {notes_cnt} expert note(s)",
            f"└ Last Activity: {last_act}",
        ]
        return "\n".join(lines)

    a  = s["asset"]
    tf = s.get("top_finding")
    ln = s.get("latest_note")
    sc = s.get("severity_counts", {})
    if s.get("critical"):
        status = "🚨 Critical — Immediate Attention Required"
    elif s.get("finding_count", 0) > 5:
        status = "⚠️ Attention Required"
    else:
        status = "✅ Operational"
    lines = [
        f"📊 *{a['asset_id']} — {a['name']}*",
        f"├ Type: {a['type']}",
        f"├ Location: {a['location']}",
        f"├ Findings: {s.get('finding_count', 0)} (🚨{sc.get('critical',0)} ⚠️{sc.get('high',0)} 📋{sc.get('medium',0)})",
        f"└ Notes: {s.get('note_count', 0)}",
        "",
    ]
    if tf:
        lines += [f"*Top Finding:*",
                  f"  {tf['object']} — {tf['condition']}",
                  f"  Confidence: {_pct(tf['confidence'])}", ""]
    if ln:
        lines += [f"*Latest Note:*", f"  [{ln['author']}] {ln['comment']}", ""]
    lines.append(f"*Status: {status}*")
    return "\n".join(lines)


def fmt_list(rows: list) -> str:
    if not rows:
        return "No assets in database."
    lines = [f"📋 *{len(rows)} asset(s)*"]
    for a in rows:
        lines.append(f"• {a['asset_id']} — {a['name']} @ {a['location']}")
    return "\n".join(lines)


def fmt_critical(rows: list) -> str:
    if not rows:
        return "✅ No critical findings across facility."
    by_asset = {}
    for r in rows:
        by_asset.setdefault(r["asset_id"], []).append(r)
    lines = [f"🚨 *{len(rows)} critical finding(s) across {len(by_asset)} asset(s)*\n"]
    for aid, findings in list(by_asset.items())[:5]:
        lines.append(f"*{aid} — {findings[0].get('name','?')}:*")
        for f in findings[:2]:
            lines.append(f"  • {f['object']}: {f['condition']} ({_pct(f['confidence'])})")
    if len(by_asset) > 5:
        lines.append(f"\n_...{len(by_asset)-5} more assets affected._")
    return "\n".join(lines)


def fmt_latest(rows: list) -> str:
    if not rows:
        return "No inspections recorded."
    lines = ["🕐 *Latest Inspections*"]
    for r in rows:
        ts = (r.get("timestamp") or r.get("created_at") or "")[:10]
        lines.append(f"• {r['asset_id']} | {r['object']} — {r['condition']} | {ts}")
    return "\n".join(lines)


def fmt_search(rows: list, keyword: str) -> str:
    if not rows:
        return f"No findings found for '{keyword}'."
    lines = [f"🔎 *{len(rows)} result(s) for '{keyword}'*"]
    for r in rows[:6]:
        lines.append(f"• {r['asset_id']} | {r['object']} — {r['condition']}")
    return "\n".join(lines)


def fmt_line_status(rows: list, line: str) -> str:
    if not rows:
        return f"No assets found for line '{line}'."
    lines = [f"🏭 *Line Status — {line}* ({len(rows)} assets)\n"]
    for a in rows:
        crit = a.get("critical_count", 0)
        tot  = a.get("finding_count", 0)
        icon = "🚨" if crit else ("⚠️" if tot > 3 else "✅")
        lines.append(f"{icon} {a['asset_id']} — {a['name']} | {tot} findings, {crit} critical")
    return "\n".join(lines)



def fmt_help(role: str) -> str:
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
        "telemetry":  "M14 temperature 67 degrees   — log sensor reading",
        "calculate":  "calculate M14 temperature     — analyse readings",
        "convert":    "convert 45 celsius fahrenheit — unit conversion",
        "bim":        "(removed — BIM data auto-ingested via file inbox)",

        "search":     "search [keyword]              — search findings",
        "linestatus": "linestatus [line]             — production line status",
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


# ── Dispatcher ────────────────────────────────────────────────

def dispatch(intent: str, asset_id, full_text: str, user: dict) -> str:
    aid   = (asset_id or "").upper().strip()
    words = full_text.strip().split()
    args  = words[1:] if len(words) > 1 else []
    lang  = detect_language(full_text)

    if intent == "machine":
        a = _resolve(aid, full_text)
        if not a:
            return _ask_db_fallback(full_text, lang)
        reply = generate_reply("machine", a, language=lang, query_text=full_text, user=user)
        return reply or fmt_asset(a)

    if intent == "findings":
        a = _resolve(aid, full_text)
        if not a:
            return _ask_db_fallback(full_text, lang)
        rows = engine.get_findings(a["asset_id"])
        reply = generate_reply("findings", {"asset": a, "findings": rows}, language=lang, query_text=full_text, user=user)
        return reply or fmt_findings(rows, a["name"])

    if intent == "notes":
        a = _resolve(aid, full_text)
        if not a:
            return _ask_db_fallback(full_text, lang)
        rows = engine.get_notes(a["asset_id"])
        reply = generate_reply("notes", {"asset": a, "notes": rows}, language=lang, query_text=full_text, user=user)
        return reply or fmt_notes(rows)

    if intent == "summary":
        a = _resolve(aid, full_text)
        if not a:
            return _ask_db_fallback(full_text, lang)
        s = engine.get_summary(a["asset_id"])
        if not s:
            return _ask_db_fallback(full_text, lang)
        reply = generate_reply("summary", s, language=lang, query_text=full_text, user=user)
        return reply or fmt_summary(s)

    if intent == "list":
        assets = engine.list_assets()
        # Attempt to generate a LLM-based reply; if it fails (e.g., rate limits), fall back to plain formatting.
        try:
            reply = generate_reply("list", assets, language=lang, query_text=full_text, user=user)
            if reply:
                return reply
        except Exception as e:
            # Optionally log the exception; for now we silently fallback.
            pass
        return fmt_list(assets)

    if intent == "critical":
        rows = engine.critical_assets()
        reply = generate_reply("critical", rows, language=lang, query_text=full_text, user=user)
        return reply or fmt_critical(rows)

    if intent == "latest":
        rows = engine.latest_inspections()
        reply = generate_reply("latest", rows, language=lang, query_text=full_text, user=user)
        return reply or fmt_latest(rows)

    if intent == "search":
        keyword = " ".join(args) if args else full_text
        rows = engine.search_findings(keyword)
        reply = generate_reply("search", {"keyword": keyword, "results": rows}, language=lang, query_text=full_text, user=user)
        return reply or fmt_search(rows, keyword)

    if intent == "linestatus":
        line = " ".join(args) if args else full_text.replace("linestatus","").strip()
        rows = engine.get_line_status(line)
        reply = generate_reply("linestatus", {"line": line, "assets": rows}, language=lang, query_text=full_text, user=user)
        return reply or fmt_line_status(rows, line)

    if intent == "ask":
        # Try RAG first, then fall through to direct DB NL query
        if RAG_ENABLED:
            try:
                rag_reply = rag_query(full_text, aid or None)
                if rag_reply and rag_reply.strip():
                    return rag_reply
            except Exception:
                pass
        # Direct DB query via LLM NL→SQL bridge
        try:
            from query.llm_db_executor import ask_db
            return ask_db(full_text, language=lang)
        except Exception as e:
            return f"⚠️ Database query failed: {e}\nTry: *list*, *summary [machine]*, or *search [keyword]*"

    if intent == "image":
        a = _resolve(aid, full_text)
        if not a:
            return f"Asset not found: '{full_text}'"
        rows = db_query(
            "SELECT file_path, label FROM scrap.batch_images WHERE asset_id = %s",
            (a["asset_id"],)
        )
        if not rows:
            return f"No image found for {a['asset_id']}."
        from whatsapp.media_sender import send_image_reply
        send_image_reply(user["phone"], rows[0]["file_path"],
                         caption=f"CV output — {a['asset_id']} | {rows[0]['label']}")
        return ""

    if intent == "telemetry":
        from tools.telemetry import handle_telemetry_message
        return handle_telemetry_message(full_text, user)

    if intent == "calculate":
        from tools.calculator import summarise_telemetry_for_asset
        if not aid:
            a = find_asset_by_name(full_text)
            if a:
                aid = a["asset_id"]
        if not aid:
            return "Which machine? Try: *calculate M14 temperature*"
        result = summarise_telemetry_for_asset(aid)
        return result.get("reply", "No telemetry data found.")

    if intent == "convert":
        from tools.calculator import convert_unit
        import re
        nums = re.findall(r"[-+]?\d*\.?\d+", full_text)
        if not nums:
            return "Usage: *convert 45 celsius fahrenheit*"
        value = float(nums[0])
        text_lower = full_text.lower()
        pairs = [
            ("celsius","fahrenheit"), ("fahrenheit","celsius"),
            ("bar","psi"),            ("psi","bar"),
            ("mm","cm"),              ("cm","mm"),
            ("cm","m"),               ("m","cm"),
        ]
        for frm, to in pairs:
            if frm in text_lower and to in text_lower:
                result = convert_unit(value, frm, to)
                return result.get("reply", result.get("error","Conversion failed."))
        return "Could not find units to convert.\nTry: *convert 45 celsius fahrenheit*"

    if intent == "addnote":
        a = _resolve(aid, full_text)
        if not a or len(args) < 2:
            return "Usage: addnote [id] [note text]"
        ok = engine.add_note(a["asset_id"], " ".join(args[1:]), user["name"])
        return f"✅ Note added to {a['asset_id']}." if ok else "Asset not found."

    if intent == "report":
        a = _resolve(aid, full_text)
        if not a or len(args) < 2:
            return "Usage: report [id] [description]"
        execute(
            """INSERT INTO cv.detections
               (detection_id, asset_id, object, condition, confidence, source)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (str(uuid.uuid4()), a["asset_id"], "Field report",
             " ".join(args[1:]), 0.5, "field_report"),
        )
        return f"✅ Report submitted for {a['asset_id']}."

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
        return fmt_help(user["role"])

    # Unknown intent — try the NL→SQL bridge before giving up
    return _ask_db_fallback(full_text, lang)


def _ask_db_fallback(full_text: str, lang: str) -> str:
    """Route open-ended questions (no asset match, unknown intent, etc.) through the LLM→DB bridge."""
    try:
        from query.llm_db_executor import ask_db
        return ask_db(full_text, language=lang)
    except Exception as e:
        return f"I didn't understand: '{full_text}'\nType *help* to see available commands."
