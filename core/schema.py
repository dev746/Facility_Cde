import pathlib
from core.db import pool

MIGRATIONS_DIR = pathlib.Path(__file__).parent.parent / "migrations"
SEED_FILE      = pathlib.Path(__file__).parent.parent / "facility_knowledge_correlation.sql"


def db_init():
    import os
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS core;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS core.schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """)
            conn.commit()

            cur.execute("SELECT version FROM core.schema_migrations")
            applied = {r[0] for r in cur.fetchall()}

            for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
                version = path.stem
                if version in applied:
                    continue
                print(f"[schema] Applying migration: {version}")
                sql = path.read_text(encoding="utf-8")
                cur.execute(sql)
                cur.execute("INSERT INTO core.schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING", (version,))
                conn.commit()

            # Auto-register ADMIN_PHONE from environment
            admin_phone = os.getenv("ADMIN_PHONE")
            if admin_phone:
                print(f"[schema] Auto-registering admin phone: {admin_phone}")
                cur.execute("""
                    INSERT INTO auth.users (phone, name, role, is_active)
                    VALUES (%s, 'System Admin', 'admin', true)
                    ON CONFLICT (phone) DO UPDATE SET is_active = true, role = 'admin'
                """, (admin_phone,))
                conn.commit()

    print("[schema] DB migrations up to date!")


def seed_knowledge_base():
    """
    Auto-seed the knowledge base on first deploy.

    Reads facility_knowledge_correlation.sql and executes it statement by
    statement with autocommit=True so that duplicate / already-exists errors
    are silently skipped. The function is a no-op if core.assets already has
    rows (idempotent — safe to call on every startup).
    """
    import psycopg
    from core.db import DATABASE_URL

    if not SEED_FILE.exists():
        print("[seed] facility_knowledge_correlation.sql not found — skipping.")
        return

    if not DATABASE_URL:
        print("[seed] DATABASE_URL not set — skipping seed.")
        return

    # ── Idempotency check ────────────────────────────────────────
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM core.assets")
                count = cur.fetchone()[0]
        if count > 0:
            print(f"[seed] DB already seeded ({count} assets) — skipping.")
            return
    except Exception as exc:
        print(f"[seed] Cannot check asset count: {exc} — skipping seed.")
        return

    # ── Load & execute ───────────────────────────────────────────
    print("[seed] Empty DB detected — loading facility_knowledge_correlation.sql …")
    sql_text = SEED_FILE.read_text(encoding="utf-8")

    # Split on ";\n" — safe for standard pg_dump output
    statements = [
        s.strip() for s in sql_text.split(";\n")
        if s.strip() and not s.strip().startswith("--")
    ]

    ok = skip = errors = 0
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            for stmt in statements:
                try:
                    cur.execute(stmt)
                    ok += 1
                except Exception as exc:
                    msg = str(exc).lower()
                    if any(kw in msg for kw in ("already exists", "duplicate", "unique")):
                        skip += 1          # expected on re-runs
                    else:
                        errors += 1
                        print(f"[seed] ⚠  {exc!r}")

    print(f"[seed] ✓ Done — {ok} statements OK · {skip} skipped · {errors} errors")


if __name__ == "__main__":
    db_init()
    seed_knowledge_base()