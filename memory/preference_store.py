import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "aipros_logs.db"

def _init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT,
            usage_count INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()

def get_preference(key: str) -> str | None:
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT value FROM preferences WHERE key = ?",
        (key,)
    )
    row = cur.fetchone()
    conn.close()

    return row[0] if row else None

def set_preference(key: str, value: str):
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO preferences (key, value, usage_count)
        VALUES (?, ?, 1)
        ON CONFLICT(key)
        DO UPDATE SET
            value = excluded.value,
            usage_count = usage_count + 1
    """, (key, value))

    conn.commit()
    conn.close()