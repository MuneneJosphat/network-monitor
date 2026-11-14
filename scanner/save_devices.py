from scanner import scan_network
from models import SessionLocal, Device, init_db
from risk_scoring import score_device
from network_info import get_default_gateway
from datetime import datetime, timezone

def save_devices(devices):
    init_db()
    session = SessionLocal()

    gateway_ip, _ = get_default_gateway()

    new_count = 0
    updated_count = 0

    for d in devices:
        mac = d.get("mac")
        if not mac or mac == "Unavailable":
            continue

        risk_level, reasons = score_device(
            device_type=d.get("device_type"),
            open_ports_str=d.get("open_ports"),
            vendor=d.get("vendor"),
            hostname=d.get("hostname"),
            ip=d.get("ip"),
            gateway_ip=gateway_ip,
            mac_address=mac
        )

        existing = session.query(Device).filter_by(mac_address=mac).first()

        if existing:
            existing.ip_address = d["ip"]
            existing.hostname = d["hostname"]
            existing.vendor = d["vendor"]
            existing.device_type = d.get("device_type", existing.device_type)
            existing.os_guess = d.get("os_guess", existing.os_guess)
            existing.open_ports = d.get("open_ports", existing.open_ports)
            existing.risk_level = risk_level
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
                risk_level=risk_level,
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
            )
            session.add(new_device)
            new_count += 1

        if reasons and reasons[0] != "No risk indicators found":
            print(f"  {d['ip']:<15} Risk: {risk_level:<10} Reasons: {'; '.join(reasons)}")

    session.commit()
    session.close()
    return new_count, updated_count

if __name__ == "__main__":
    found = scan_network()
    new_count, updated_count = save_devices(found)
    print(f"\nSaved {new_count} new device(s), updated {updated_count} existing device(s).")