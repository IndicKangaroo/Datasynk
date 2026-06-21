import socket
import time
from zeroconf import ServiceBrowser, ServiceInfo
from zeroconf.asyncio import AsyncZeroconf
from devices import upsert_device

SERVICE_TYPE = "_datasync._tcp.local."

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

async def announce_device(device_id, device_name, port):
    ip = get_local_ip()
    transfer_port = port + 1
    azc = AsyncZeroconf()
    info = ServiceInfo(
        type_=SERVICE_TYPE,
        name=f"{device_name}-{port}.{SERVICE_TYPE}",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={
            "device_id": device_id,
            "transfer_port": str(transfer_port)
        }
    )
    await azc.async_register_service(info)
    print(f"Announced: {device_name} at {ip}:{port} (transfer port: {transfer_port})")
    return azc, info

async def start_discovery(device_id):
    azc = AsyncZeroconf()

    class Handler:
        def add_service(self, zc, type_, name):
            print(f"SERVICE FOUND: {name}")
            info = zc.get_service_info(type_, name, timeout=3000)
            if info:
                print(f"PROPERTIES: {info.properties}")
                found_id = info.properties.get(b"device_id", b"").decode()
                transfer_port = int(info.properties.get(b"transfer_port", b"9000").decode())
                if found_id and found_id != device_id:
                    ip = socket.inet_ntoa(info.addresses[0])
                    upsert_device(found_id, name, ip, info.port, transfer_port)
                    print(f"Discovered: {name} at {ip}:{info.port} (transfer: {transfer_port})")
            else:
                print("INFO IS NONE after 3s timeout")

        def remove_service(self, zc, type_, name):
            print(f"Device left: {name}")

        def update_service(self, zc, type_, name):
            pass


    browser = ServiceBrowser(azc.zeroconf, SERVICE_TYPE, Handler())
    return azc, browser


def is_lan(ip):
    return (
        ip.startswith("10.") or
        ip.startswith("192.168.") or
        ip.startswith("172.")
    )
