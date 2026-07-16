import os
import httpx
from dotenv import load_dotenv

load_dotenv()


def send_image_reply(to: str, image_path: str, caption: str = "") -> None:
    """Upload image to Meta then send via WhatsApp. Only works with Meta API, not Twilio sandbox."""
    token    = os.getenv("WA_TOKEN", "")
    phone_id = os.getenv("WA_PHONE_ID", "")

    if not token or not phone_id:
        # Twilio sandbox fallback: send caption only
        from whatsapp.sender import send_reply
        send_reply(to, f"📸 {caption}\n(Image sending requires Meta Business API)")
        return

    to = to.replace("whatsapp:", "")

    with open(image_path, "rb") as f:
        up = httpx.post(
            f"https://graph.facebook.com/v19.0/{phone_id}/media",
            headers={"Authorization": f"Bearer {token}"},
            data={"messaging_product": "whatsapp"},
            files={"file": (os.path.basename(image_path), f, "image/png")},
            timeout=30,
        )
    media_id = up.json()["id"]

    httpx.post(
        f"https://graph.facebook.com/v19.0/{phone_id}/messages",
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {"id": media_id, "caption": caption},
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
