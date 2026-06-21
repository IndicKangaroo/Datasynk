from discovery import *
from database import get_connection
import time



def send_file(ip, transfer_port, file_path):
    filename = os.path.basename(file_path).encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, transfer_port))
    sock.sendall(len(filename).to_bytes(4, "big"))
    sock.sendall(filename)
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sock.sendall(chunk)
    sock.close()
    print(f"Sent: {os.path.basename(file_path)} to {ip}:{transfer_port}")

import threading
import os
from watcher import IGNORE_PATHS


SYNC_FOLDER = os.path.join(os.path.expanduser("~"), "Datasynk")

def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed early")
        data += chunk
    return data

def handle_connection(conn, addr):
    try:
        name_length = int.from_bytes(recv_exact(conn, 4), "big")
        filename = recv_exact(conn, name_length).decode()
        filename = os.path.basename(filename)
        save_path = os.path.join(SYNC_FOLDER, filename)
        IGNORE_PATHS.add(save_path)
        with open(save_path, "wb") as f:
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                f.write(chunk)
        print(f"Received: {filename} from {addr}")

        # mark as already synced so we don't re-send it
        db = get_connection()
        db.execute(
            "INSERT INTO file_events (event_type, file_path, detected_at, synced) VALUES (?, ?, ?, ?)",
            ("created", save_path, time.time(), 1)
        )
        db.commit()
        db.close()
    except Exception as e:
        print(f"Transfer error: {e}")
    finally:
        conn.close()

def start_receiver(transfer_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", transfer_port))
    server.listen()
    print(f"File receiver listening on port {transfer_port}")

    def accept_loop():
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_connection, args=(conn, addr))
            thread.daemon = True
            thread.start()

    thread = threading.Thread(target=accept_loop)
    thread.daemon = True
    thread.start()
