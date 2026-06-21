import socket
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db, get_connection
from watcher import start_watcher
from devices import get_devices
import uuid
from discovery import announce_device, start_discovery
import threading
from sync_manager import sync_loop, poll_loop
from transfer import start_receiver

DEVICE_ID = str(uuid.uuid4())
DEVICE_NAME = socket.gethostname()
import sys
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

observer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global observer
    init_db()
    observer = start_watcher()
    start_receiver(PORT+1)
    sync_thread = threading.Thread(target=sync_loop)
    poll_thread = threading.Thread(target=poll_loop, args=(DEVICE_ID,))
    poll_thread.daemon = True
    poll_thread.start()
    sync_thread.daemon = True
    sync_thread.start()
    zc, info = await announce_device(DEVICE_ID, DEVICE_NAME, PORT)
    zc_browser, browser = await start_discovery(DEVICE_ID)
    print("DataSync backend started.")
    yield
    observer.stop()
    observer.join()
    await zc.async_unregister_service(info)
    await zc.async_close()
    await zc_browser.async_close()
    print("DataSync backend stopped.")

app = FastAPI(lifespan=lifespan)

@app.get("/status")
def get_status():
    return {"status": "ok"}

@app.get("/events")
def get_events():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM file_events ORDER BY detected_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/devices")
def list_devices():
    return get_devices()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False)