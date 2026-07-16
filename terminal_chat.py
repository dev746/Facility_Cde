"""
Local terminal chat — full pipeline test without WhatsApp or Twilio.
Run: PYTHONPATH=. python terminal_chat.py
"""
from core.schema import db_init
from ingestion.watcher import scan_inbox
from query.intent import parse_intent
from whatsapp.commands import dispatch

MOCK_USER = {"phone": "local", "name": "Local Dev", "role": "admin"}


def main():
    db_init()
    result = scan_inbox()
    if result["processed"]:
        print(f"[startup] loaded {result['processed']} files from inbox\n")

    print("🏭 Facility CDE v2 — Terminal Chat")
    print("Type any question. 'quit' to exit.\n")

    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break
        if not text:
            continue
        if text.lower() == "quit":
            break

        parsed   = parse_intent(text)
        intent   = parsed.get("intent", "unknown")
        asset_id = parsed.get("asset_id")
        filters  = parsed.get("filters", {})

        print(f"  [intent={intent} asset={asset_id} filters={filters}]")

        reply = dispatch(intent, asset_id, text, MOCK_USER)
        print(f"\nBot:\n{reply}\n")


if __name__ == "__main__":
    main()
