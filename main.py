from fastapi import FastAPI
from core.schema import db_init
from ingestion.watcher import scan_inbox
from whatsapp.webhook import router

app = FastAPI(title="Facility CDE — WhatsApp API v2")


@app.on_event("startup")
def startup():
    db_init()
    result = scan_inbox()
    print(f"[startup] inbox scan: {result}")


app.include_router(router, prefix="/webhook")


@app.get("/")
def health():
    return {"status": "ok", "service": "Facility CDE WhatsApp API", "version": "2.0"}


@app.get("/status")
def status():
    from core.db import query
    return {
        "assets":   query("SELECT COUNT(*) as n FROM assets")[0]["n"],
        "findings": query("SELECT COUNT(*) as n FROM findings")[0]["n"],
        "users":    query("SELECT COUNT(*) as n FROM users WHERE is_active=1")[0]["n"],
        "ingest_log": query(
            "SELECT status, COUNT(*) as n FROM ingest_log GROUP BY status"
        ),
    }
