import time
from database import get_connection


def upsert_device(device_id, device_name, ip_address, port, transfer_port):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO devices (device_id, device_name, ip_address, port, transfer_port, last_seen) VALUES (?, ?, ?, ?, ?, ?)",
        (device_id, device_name, ip_address, port, transfer_port, time.time())
    )
    conn.commit()
    conn.close()

def get_devices():
    conn = get_connection()
    devices = conn.execute("SELECT device_id, device_name, ip_address, port, transfer_port FROM devices").fetchall()
    conn.close()
    return [dict(row) for row in devices]

