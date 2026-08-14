from fastapi import FastAPI
from core.schema import db_init
from ingestion.watcher import scan_inbox
from whatsapp.webhook import router as wa_router
from api.routes import router as api_router

app = FastAPI(title="Facility CDE — WhatsApp API v2")


@app.on_event("startup")
def startup():
    try:
        db_init()
    except Exception as exc:
        print(f"[startup] db init failed: {exc}")

    try:
        result = scan_inbox()
        print(f"[startup] inbox scan: {result}")
    except Exception as exc:
        print(f"[startup] inbox scan failed: {exc}")


app.include_router(wa_router, prefix="/webhook")
app.include_router(api_router, prefix="/api")


@app.get("/")
def health():
    return {"status": "ok", "service": "Facility CDE WhatsApp API", "version": "2.1"}


@app.get("/status")
def status():
    from core.db import query
    try:
        assets   = query("SELECT COUNT(*) as n FROM core.assets")[0]["n"]
        findings = query("SELECT COUNT(*) as n FROM core.findings_unified")[0]["n"]
        users    = query("SELECT COUNT(*) as n FROM auth.users WHERE is_active = true")[0]["n"]
        logs     = query("SELECT status, COUNT(*) as n FROM ingest.files GROUP BY status")
        return {
            "assets":     assets,
            "findings":   findings,
            "users":      users,
            "ingest_log": logs,
        }
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
