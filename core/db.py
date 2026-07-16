import sqlite3
import os
import threading
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "facility.db")
_local  = threading.local()


def get_connection() -> sqlite3.Connection:
    if not hasattr(_local, "conn") or _local.conn is None:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA mmap_size=268435456")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn
    return _local.conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def query(sql: str, params: tuple = ()) -> list:
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def execute(sql: str, params: tuple = ()) -> None:
    with get_db() as conn:
        conn.execute(sql, params)


def executemany(sql: str, params_list: list) -> int:
    with get_db() as conn:
        conn.executemany(sql, params_list)
        return len(params_list)
