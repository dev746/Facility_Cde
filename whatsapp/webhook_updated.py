"""
whatsapp/webhook_updated.py — Updated webhook with context and language injection.

Replace your existing whatsapp/webhook.py with this file (rename to webhook.py).

Changes from previous version:
  - Calls dispatch.dispatch() instead of commands.dispatch()
  - Passes detected language to dispatch
  - Updates user context after every message
  - Logs intent + asset_id to console for debugging
"""
import os
from fastapi import APIRouter, Request, Response
from dotenv import load_dotenv
from auth.rbac import get_user, can_access, is_rate_limited
from query.intent import parse_intent
from whatsapp.dispatch import dispatch
from whatsapp.sender import send_reply

load_dotenv()
router = APIRouter()


def _detect_language(text: str) -> str:
    """
    Fast local language detection before hitting the LLM.
    Checks for Devanagari script or common Hinglish markers.
    """
    # Devanagari Unicode block
    if any('\u0900' <= c <= '\u097F' for c in text):
        return "hindi"
    hinglish_markers = [
        "kya", "kahan", "kaun", "kitna", "batao", "dikha", "bata",
        "hai", "hain", "nahi", "kyun", "kaise", "ka", "ki", "ke",
        "isme", "uska", "wala", "abhi", "aur", "ya", "yeh", "woh",
    ]
    text_lower = text.lower()
    hits = sum(1 for m in hinglish_markers if f" {m} " in f" {text_lower} ")
    return "hinglish" if hits >= 1 else "english"


def _reply(to: str, text: str):
    if not text or not text.strip():
        return
    try:
        send_reply(to, text)
    except Exception as e:
        print(f"[webhook] send failed to {to}: {e}")


@router.get("/webhook")
def verify(request: Request):
    """Meta webhook verification — kept for future Meta Business API migration."""
    p = request.query_params
    if p.get("hub.verify_token") == os.getenv("VERIFY_TOKEN"):
        return Response(content=p.get("hub.challenge"), media_type="text/plain")
    return Response(status_code=403)


@router.post("/webhook")
async def receive(request: Request):
    """Receives Twilio WhatsApp messages (form data) or Meta (JSON)."""

    # Support both Twilio (form) and Meta (JSON) message formats
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        # Meta Business API format
        body = await request.json()
        try:
            msg   = body["entry"][0]["changes"][0]["value"]["messages"][0]
            phone = msg["from"]
            text  = msg.get("text", {}).get("body", "").strip()
        except (KeyError, IndexError):
            return {"status": "no_message"}
    else:
        # Twilio format
        form  = await request.form()
        phone = form.get("From", "")
        text  = form.get("Body", "").strip()

    print(f"[webhook] {phone}: {text}")

    if not text:
        return {"status": "empty"}

    # ── Rate limit ────────────────────────────────────────────
    if is_rate_limited(phone):
        _reply(phone, "⏱ Too many requests. Please wait a minute.")
        return {"status": "rate_limited"}

    # ── Auth ──────────────────────────────────────────────────
    user = get_user(phone)
    if not user:
        _reply(phone, "❌ You are not registered. Contact your administrator.")
        return {"status": "unregistered"}

    # ── Language detection ────────────────────────────────────
    language = _detect_language(text)

    # ── Intent parsing ────────────────────────────────────────
    parsed   = parse_intent(text)
    intent   = parsed.get("intent", "unknown")
    asset_id = parsed.get("asset_id")

    print(f"[webhook] intent={intent} asset={asset_id} "
          f"lang={language} user={user['name']} role={user['role']}")

    # ── RBAC ──────────────────────────────────────────────────
    if not can_access(user["role"], intent):
        _reply(
            phone,
            f"⛔ Your role (*{user['role']}*) cannot use '{intent}'.\n"
            "Type *help* to see your available commands."
        )
        return {"status": "forbidden"}

    # ── Dispatch ──────────────────────────────────────────────
    reply = dispatch(intent, asset_id, text, user, language=language)
    _reply(phone, reply)
    return {"status": "ok"}
