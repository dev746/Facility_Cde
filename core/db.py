import os
import psycopg
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Wegro26@localhost:5432/FACILITY1.DB")

pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=10)

def get_connection():
    """Return a new database connection from the pool.
    This helper mirrors older code expectations and provides a
    convenient way for scripts to obtain a raw connection.
    """
    return pool.connection()
def query(sql: str, params: tuple = ()) -> list:
    sql = sql.replace("?", "%s")
    with pool.connection() as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]


def execute(sql: str, params: tuple = ()) -> None:
    sql = sql.replace("?", "%s")
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()


def executemany(sql: str, params_list: list) -> int:
    if not params_list:
        return 0
    sql = sql.replace("?", "%s")
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, params_list)
        conn.commit()
        return len(params_list)

