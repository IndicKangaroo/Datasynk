from fastapi import FastAPI
import sqlite3
import time

app = FastAPI()

def get_connection():
    conn = sqlite3.connect("relay.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_transfers (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            target_device TEXT NOT NULL,
            file_key      TEXT NOT NULL,
            filename      TEXT NOT NULL,
            uploaded_at   REAL NOT NULL,
            downloaded    INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.post("/notify")
def notify(target_device: str, file_key: str, filename: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO pending_transfers (target_device, file_key, filename, uploaded_at) VALUES (?, ?, ?, ?)",
        (target_device, file_key, filename, time.time())
    )
    conn.commit()
    conn.close()
    return {"status": "queued"}

@app.get("/poll/{device_id}")
def poll(device_id: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM pending_transfers WHERE target_device = ? AND downloaded = 0",
        (device_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/confirm/{transfer_id}")
def confirm(transfer_id: int):
    conn = get_connection()
    conn.execute("UPDATE pending_transfers SET downloaded = 1 WHERE id = ?", (transfer_id,))
    conn.commit()
    conn.close()
    return {"status": "confirmed"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("relay_server:app", host="0.0.0.0", port=port)