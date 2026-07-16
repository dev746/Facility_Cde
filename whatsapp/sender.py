import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN"),
        )
    return _client


def send_reply(to: str, body: str) -> None:
    if not body or not body.strip():
        return
    # WhatsApp messages max 1600 chars — split if needed
    chunks = [body[i:i+1580] for i in range(0, len(body), 1580)]
    client = _get_client()
    for chunk in chunks:
        client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_FROM"),
            to=to,
            body=chunk,
        )
