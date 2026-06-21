import time
import os
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from database import get_connection

SYNC_FOLDER = os.path.join(os.path.expanduser("~"), "Datasynk")

IGNORE_PATHS = set()

def log_event(event_type, file_path):
    if file_path in IGNORE_PATHS:
        IGNORE_PATHS.discard(file_path)
        return
    conn = get_connection()
    conn.execute(
        "INSERT INTO file_events (event_type, file_path, detected_at, synced) VALUES (?, ?, ?, ?)",
        (event_type, file_path, time.time(), 0)
    )
    conn.commit()
    conn.close()

class SyncHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            log_event("created", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            log_event("modified", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"DELETE DETECTED: {event.src_path}")
            log_event("deleted", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            log_event("moved", event.src_path)

def start_watcher():
    os.makedirs(SYNC_FOLDER, exist_ok=True)
    print(f"Watching folder: {SYNC_FOLDER}")  # add this
    observer = PollingObserver()
    observer.schedule(SyncHandler(), SYNC_FOLDER, recursive=True)
    observer.start()
    return observer