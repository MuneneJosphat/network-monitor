from scanner import scan_network
from models import SessionLocal, Device, init_db
from datetime import datetime, timezone

def save_devices(devices):
    init_db()
    session = SessionLocal()

    new_count = 0
    updated_count = 0

    for d in devices:
        mac = d.get("mac")
        if not mac or mac == "Unavailable":
            continue

        existing = session.query(Device).filter_by(mac_address=mac).first()

        if existing:
            existing.ip_address = d["ip"]
            existing.hostname = d["hostname"]
            existing.vendor = d["vendor"]
            existing.device_type = d.get("device_type", existing.device_type)
            existing.os_guess = d.get("os_guess", existing.os_guess)
            existing.open_ports = d.get("open_ports", existing.open_ports)
            existing.last_seen = datetime.now(timezone.utc)
            updated_count += 1
        else:
            new_device = Device(
                mac_address=mac,
                ip_address=d["ip"],
                hostname=d["hostname"],
                vendor=d["vendor"],
                device_type=d.get("device_type"),
                os_guess=d.get("os_guess"),
                open_ports=d.get("open_ports"),
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
            )
            session.add(new_device)
            new_count += 1

    session.commit()
    session.close()
    return new_count, updated_count

if __name__ == "__main__":
    found = scan_network()
    new_count, updated_count = save_devices(found)
    print(f"Saved {new_count} new device(s), updated {updated_count} existing device(s).")