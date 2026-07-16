import shutil
from pathlib import Path
from core.schema import db_init
from ingestion.universal import ingest_any

INBOX     = Path("data/inbox")
PROCESSED = Path("data/processed")
FAILED    = Path("data/failed")
DOC_EXTS  = {".pdf", ".txt"}
DATA_EXTS = {".json", ".xlsx", ".xls", ".csv"}


def scan_inbox() -> dict:
    db_init()
    results = {"processed": 0, "failed": 0}

    all_files = [f for f in INBOX.iterdir()
                 if f.is_file() and f.suffix in DATA_EXTS | DOC_EXTS
                 and not f.name.startswith(".")]

    for f in all_files:
        try:
            if f.suffix in DOC_EXTS:
                from rag.doc_ingest import ingest_document
                ingest_document(str(f))
            else:
                ingest_any(str(f))
            shutil.move(str(f), PROCESSED / f.name)
            results["processed"] += 1
        except Exception as e:
            print(f"[watcher] FAILED {f.name}: {e}")
            shutil.move(str(f), FAILED / f.name)
            results["failed"] += 1

    return results


if __name__ == "__main__":
    r = scan_inbox()
    print(f"[watcher] done — {r['processed']} processed, {r['failed']} failed")
