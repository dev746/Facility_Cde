import os
import atexit
import psycopg
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

_pool: ConnectionPool | None = None


def _get_pool() -> ConnectionPool:
    """Return the connection pool, creating it on first call."""
    global _pool
    if _pool is None:
        url = DATABASE_URL
        if not url:
            raise RuntimeError(
                "DATABASE_URL environment variable is not set. "
                "Add it in your Render / Coolify environment settings."
            )
        _pool = ConnectionPool(url, min_size=1, max_size=10)
        atexit.register(_pool.close)  # clean shutdown — avoids PythonFinalizationError
    return _pool


# Keep `pool` as a module-level property for backwards-compat imports
class _PoolProxy:
    """Proxy so `from core.db import pool` still works."""
    def __getattr__(self, name):
        return getattr(_get_pool(), name)

    def connection(self):
        return _get_pool().connection()

    def close(self):
        if _pool:
            _pool.close()


pool = _PoolProxy()


def get_connection():
    """Return a new database connection from the pool."""
    return _get_pool().connection()


def query(sql: str, params: tuple = ()) -> list:
    sql = sql.replace("?", "%s")
    with _get_pool().connection() as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]


def execute(sql: str, params: tuple = ()) -> None:
    sql = sql.replace("?", "%s")
    with _get_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()


def executemany(sql: str, params_list: list) -> int:
    if not params_list:
        return 0
    sql = sql.replace("?", "%s")
    with _get_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, params_list)
        conn.commit()
        return len(params_list)
