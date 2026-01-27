import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "aipros_logs.db"

def _init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_input TEXT,
            mode TEXT,
            tool TEXT,
            args TEXT,
            result TEXT
        )
    """)

    conn.commit()
    conn.close()

def log_event(
    user_input: str,
    mode: str,
    tool: str | None,
    args: dict | None,
    result: str
):
    _init_db()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO execution_logs
        (timestamp, user_input, mode, tool, args, result)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(timespec="seconds"),
            user_input,
            mode,
            tool,
            json.dumps(args) if args else None,
            result
        )
    )

    conn.commit()
    conn.close()