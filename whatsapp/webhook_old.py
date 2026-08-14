import os
from fastapi import APIRouter, Request, Response
from dotenv import load_dotenv
from auth.rbac import get_user, can_access, is_rate_limited
from query.intent import parse_intent
from whatsapp.commands import dispatch
from whatsapp.sender import send_reply

load_dotenv()
router = APIRouter()


def _reply(to: str, text: str):
    if not text or not text.strip():
        return
    try:
        send_reply(to, text)
    except Exception as e:
        print(f"[webhook] send failed to {to}: {e}")


@router.get("/webhook")
def verify(request: Request):
    """Meta webhook verification — not needed for Twilio but kept for future migration."""
    p = request.query_params
    if p.get("hub.verify_token") == os.getenv("VERIFY_TOKEN"):
        return Response(content=p.get("hub.challenge"), media_type="text/plain")
    return Response(status_code=403)


@router.post("/webhook")
async def receive(request: Request):
    """Receives Twilio WhatsApp messages as form data."""
    form  = await request.form()
    phone = form.get("From", "")
    text  = form.get("Body", "").strip()

    print(f"[webhook] {phone}: {text}")

    if not text:
        return {"status": "empty"}

    # rate limit
    if is_rate_limited(phone):
        _reply(phone, "⏱ Too many requests. Please wait a minute.")
        return {"status": "rate_limited"}

    # auth
    user = get_user(phone)
    if not user:
        _reply(phone, "❌ You are not registered. Contact your administrator.")
        return {"status": "unregistered"}

    # parse intent
    parsed   = parse_intent(text)
    intent   = parsed.get("intent", "unknown")
    asset_id = parsed.get("asset_id")

    print(f"[webhook] intent={intent} asset={asset_id} user={user['name']} role={user['role']}")

    # rbac
    if not can_access(user["role"], intent):
        _reply(phone, f"⛔ Your role (*{user['role']}*) cannot use '{intent}'.\nType *help* to see your commands.")
        return {"status": "forbidden"}

    # dispatch
    reply = dispatch(intent, asset_id, text, user)
    _reply(phone, reply)
    return {"status": "ok"}
