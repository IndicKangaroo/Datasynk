import os
import time


from watcher import IGNORE_PATHS
from discovery import is_lan
from storgae import upload_file, download_file, delete_file
from database import get_connection
from devices import get_devices
from transfer import send_file, SYNC_FOLDER
import requests

RELAY_URL = "https://your-app.onrender.com"
def sync_loop():
    while True:
        try:
            conn = get_connection()
            rows = conn.execute(
                "SELECT * FROM file_events WHERE synced = 0"
            ).fetchall()
            conn.close()

            devices = get_devices()

            for row in rows:
                event_type = row["event_type"]
                file_path = row["file_path"]

                if event_type in ("created", "modified"):
                    for device in devices:
                        if is_lan(device["ip_address"]):
                            try:
                                send_file(device["ip_address"], device["transfer_port"], file_path)
                            except Exception as e:
                                print(f"Failed to send to {device['ip_address']}: {e}")
                                continue
                        else:
                            key = upload_file(file_path)
                            filename = os.path.basename(file_path)
                            try:
                                requests.post(
                                    f"{RELAY_URL}/notify",
                                    params={
                                        "target_device": device["device_id"],
                                        "file_key": key,
                                        "filename": filename
                                    }
                                )
                                print(f"Notified relay: {filename} waiting for {device['device_name']}")
                            except Exception as e:
                                print(f"Failed to notify relay: {e}")
                elif event_type == "deleted":
                    pass  # V6

                # mark synced only after attempting all peers
                conn = get_connection()
                conn.execute(
                    "UPDATE file_events SET synced = 1 WHERE id = ?",
                    (row["id"],)
                )
                conn.commit()
                conn.close()

        except Exception as e:
            print(f"Sync loop error: {e}")

        time.sleep(5)


def poll_loop(device_id):
    ping_count = 0
    while True:
        try:
            if ping_count % 60 == 0:
                requests.get(f"{RELAY_URL}/status", timeout=5)
            ping_count += 1

            response = requests.get(f"{RELAY_URL}/poll/{device_id}", timeout=15)
            if response.status_code != 200 or not response.text.strip():
                time.sleep(10)
                continue
            pending = response.json()

        except Exception as e:
            print(f"Poll loop error: {e}")
        time.sleep(10)

