import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_devices_table():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id      TEXT PRIMARY KEY,
            device_name    TEXT NOT NULL,
            ip_address     TEXT NOT NULL,
            port           INTEGER NOT NULL,
            transfer_port  INTEGER NOT NULL,
            last_seen      REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def init_db():
    init_devices_table()
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS file_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type  TEXT NOT NULL,      -- 'created', 'modified', 'deleted', 'moved'
            file_path   TEXT NOT NULL,      -- full path of the file
            detected_at REAL NOT NULL,       -- unix timestamp
            synced      INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

