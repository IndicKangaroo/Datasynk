import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS file_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type  TEXT NOT NULL,      -- 'created', 'modified', 'deleted', 'moved'
            file_path   TEXT NOT NULL,      -- full path of the file
            detected_at REAL NOT NULL       -- unix timestamp
        )
    """)
    conn.commit()
    conn.close()