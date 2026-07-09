import sqlite3
from pathlib import Path

DB_PATH = Path("data/db.sqlite")


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
        id TEXT PRIMARY KEY,
        status TEXT,
        input_path TEXT,
        cleaned_path TEXT,
        report_path TEXT,
        created_at TEXT,
        error_type TEXT,
        error_message TEXT
    )
    """)

    conn.commit()
    conn.close()