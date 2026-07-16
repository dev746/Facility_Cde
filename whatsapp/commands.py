import uuid
from query import engine
from query.engine import find_asset_by_name
from core.db import execute, query as db_query
from auth.rbac import PERMISSIONS, register_user, deregister_user, list_users

try:
    from rag.retriever import rag_query
    RAG_ENABLED = True
except ImportError:
    RAG_ENABLED = False


# ── Helpers ───────────────────────────────────────────────────

def _pct(v) -> str:
    try:
        return f"{float(v)*100:.0f}%"
    except (TypeError, ValueError):
        return "N/A"


def _resolve(aid: str, full_text: str) -> dict | None:
    if aid:
        a = engine.get_asset(aid)
        if a:
            return a
    return find_asset_by_name(full_text)


# ── Formatters ────────────────────────────────────────────────

def fmt_asset(a: dict) -> str:
    lines = [f"🏭 *{a['asset_id']} — {a['name']}*"]
    lines.append(f"├ Type: {a['type']}")
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
    other    = [f for f in rows if f.get("severity") not in ("critical", "high")]

    lines = [f"🔍 *{len(rows)} finding(s){' — ' + asset_name if asset_name else ''}*\n"]

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

    remaining = len(rows) - 6
    if remaining > 0:
        lines.append(f"\n_...{remaining} more. Ask for full report._")

    return "\n".join(lines)


def fmt_notes(rows: list) -> str:
    if not rows:
        return "No expert notes recorded."
    lines = [f"📝 *{len(rows)} note(s)*"]
    for n in rows[:5]:
        lines.append(f"• [{n['author']}] {n['comment']}")
    return "\n".join(lines)


def fmt_summary(s: dict) -> str:
    a   = s["asset"]
    tf  = s["top_finding"]
    ln  = s["latest_note"]
    sc  = s.get("severity_counts", {})

    if s["critical"]:
        status = "🚨 Critical — Immediate Attention Required"
    elif s["finding_count"] > 5:
        status = "⚠️ Attention Required"
    else:
        status = "✅ Operational"

    lines = [
        f"📊 *{a['asset_id']} — {a['name']}*",
        f"├ Type: {a['type']}",
        f"├ Location: {a['location']}",
        f"├ Findings: {s['finding_count']} "
        f"(🚨{sc.get('critical',0)} ⚠️{sc.get('high',0)} 📋{sc.get('medium',0)})",
        f"└ Notes: {s['note_count']}",
        "",
    ]
    if tf:
        lines += [
            f"*Top Finding:*",
            f"  {tf['object']} — {tf['condition']}",
            f"  Confidence: {_pct(tf['confidence'])}",
            "",
        ]
    if ln:
        lines += [
            f"*Latest Note:*",
            f"  [{ln['author']}] {ln['comment']}",
            "",
        ]
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
        "machine":    "machine [id or name]       — asset info + location",
        "findings":   "findings [id or name]      — defect list by severity",
        "notes":      "notes [id or name]         — expert notes",
        "summary":    "summary [id or name]       — full overview",
        "list":       "list                       — all assets",
        "critical":   "critical                   — critical findings",
        "latest":     "latest                     — recent inspections",
        "ask":        "ask [question]             — search documents (RAG)",
        "image":      "image [id]                 — CV output image",
        "search":     "search [keyword]           — search all findings",
        "linestatus": "linestatus [line name]     — production line overview",
        "addnote":    "addnote [id] [text]        — add expert note",
        "report":     "report [id] [description]  — field report",
        "adduser":    "adduser [phone] [name] [role] [shift] [line]",
        "removeuser": "removeuser [phone]",
        "listusers":  "listusers",
    }
    cmds  = PERMISSIONS.get(role, [])
    lines = [f"💬 *Commands available to {role}*\n"]
    for c in cmds:
        if c in descs:
            lines.append(f"• {descs[c]}")
    return "\n".join(lines)


# ── Dispatcher ────────────────────────────────────────────────

def dispatch(intent: str, asset_id, full_text: str, user: dict) -> str:
    aid   = (asset_id or "").upper().strip()
    words = full_text.strip().split()
    args  = words[1:] if len(words) > 1 else []

    if intent == "machine":
        a = _resolve(aid, full_text)
        return fmt_asset(a) if a else f"Asset not found for: '{full_text}'\nTry: *list*"

    if intent == "findings":
        a = _resolve(aid, full_text)
        if not a:
            return f"Asset not found for: '{full_text}'\nTry: *list*"
        return fmt_findings(engine.get_findings(a["asset_id"]), a["name"])

    if intent == "notes":
        a = _resolve(aid, full_text)
        if not a:
            return f"Asset not found: '{full_text}'"
        return fmt_notes(engine.get_notes(a["asset_id"]))

    if intent == "summary":
        a = _resolve(aid, full_text)
        if not a:
            return f"Asset not found: '{full_text}'"
        s = engine.get_summary(a["asset_id"])
        return fmt_summary(s) if s else "Could not generate summary."

    if intent == "list":
        return fmt_list(engine.list_assets())

    if intent == "critical":
        return fmt_critical(engine.critical_assets())

    if intent == "latest":
        return fmt_latest(engine.latest_inspections())

    if intent == "search":
        keyword = " ".join(args) if args else full_text
        return fmt_search(engine.search_findings(keyword), keyword)

    if intent == "linestatus":
        line = " ".join(args) if args else full_text.replace("linestatus", "").strip()
        return fmt_line_status(engine.get_line_status(line), line)

    if intent == "ask":
        if not RAG_ENABLED:
            return "RAG not available. Install chromadb + pypdf then restart."
        return rag_query(full_text, aid or None)

    if intent == "image":
        a = _resolve(aid, full_text)
        if not a:
            return f"Asset not found: '{full_text}'"
        rows = db_query(
            "SELECT file_path, label FROM batch_images WHERE asset_id=?",
            (a["asset_id"],)
        )
        if not rows:
            return f"No image found for {a['asset_id']}."
        from whatsapp.media_sender import send_image_reply
        send_image_reply(
            user["phone"],
            rows[0]["file_path"],
            caption=f"CV output — {a['asset_id']} | {rows[0]['label']}",
        )
        return ""

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
            """INSERT INTO findings
               (finding_id,asset_id,object,condition,confidence,source,severity)
               VALUES (?,?,?,?,?,?,?)""",
            (str(uuid.uuid4()), a["asset_id"], "Field report",
             " ".join(args[1:]), 0.5, "field_report", "medium"),
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

    return f"I didn't understand: '{full_text}'\nType *help* to see available commands."
