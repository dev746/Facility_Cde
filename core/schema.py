import pathlib
try:
    from core.db import pool
except ModuleNotFoundError:
    from db import pool

MIGRATIONS_DIR = pathlib.Path(__file__).parent.parent / "migrations"


def db_init():
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

    print("[schema] DB migrations up to date!")

if __name__ == "__main__":
    db_init()