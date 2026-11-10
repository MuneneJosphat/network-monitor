import nmap
import requests
import re
from datetime import datetime, timezone
from mac_vendor_lookup import MacLookup
from network_info import get_default_gateway, get_subnet

mac_lookup = MacLookup()

def get_network_range():
    gateway_ip, local_ip = get_default_gateway()
    if not gateway_ip:
        return None
    subnet = get_subnet()
    if not subnet:
        return None
    parts = gateway_ip.split(".")
    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"

def lookup_vendor(mac_address):
    try:
        return mac_lookup.lookup(mac_address)
    except Exception:
        return "Unknown"

def get_page_title(ip):
    """Grabs the <title> of a device's web login page, if it has one. Fast timeout since many devices won't respond."""
    for scheme in ["http", "https"]:
        try:
            resp = requests.get(f"{scheme}://{ip}", timeout=1.5, verify=False)
            match = re.search(r"<title>(.*?)</title>", resp.text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        except Exception:
            continue
    return None

def classify_device(ip, gateway_ip, vendor, open_ports, os_guess, hostname, page_title):
    vendor_lower = (vendor or "").lower()
    os_lower = (os_guess or "").lower()
    title_lower = (page_title or "").lower()

    # Strongest signal: this IP literally is the gateway
    if gateway_ip and ip == gateway_ip:
        return "Router (Main Gateway)"

    # Page title often reveals access points vs routers from the same brand
    if any(k in title_lower for k in ["access point", "extender", "repeater", "mesh"]):
        return "Wi-Fi Access Point / Extender"
    if any(k in title_lower for k in ["router", "gateway"]):
        return "Router or Network Device"

    # Network equipment vendor with a web login, but no clear title match
    if any(k in vendor_lower for k in ["huawei", "tenda", "tp-link", "netgear", "cisco", "mikrotik", "d-link"]):
        if page_title:
            return "Network Equipment (unconfirmed role)"

    # Phones: known mobile vendor, and no open ports is typical for a phone on wifi
    if any(k in vendor_lower for k in ["xiaomi", "samsung", "apple", "oneplus", "oppo", "vivo"]):
        if not open_ports:
            return "Phone"

    # Smart TV / streaming
    if any(k in vendor_lower for k in ["roku", "amazon", "sony", "lg electronics", "vizio"]):
        return "Smart TV or Streaming Device"
    if 8008 in open_ports or 8009 in open_ports:
        return "Smart TV or Streaming Device"

    # Computers: OS fingerprint or typical PC ports
    if "windows" in os_lower or "linux" in os_lower or "mac" in os_lower:
        return "Computer"
    if 445 in open_ports or 3389 in open_ports or 135 in open_ports:
        return "Computer"

    return "Unknown"

def discover_hosts(network_range):
    """Phase 1: fast ping scan, finds everyone reliably."""
    scanner = nmap.PortScanner()
    print(f"Phase 1: discovering devices on {network_range}...")
    scanner.scan(hosts=network_range, arguments="-sn")
    return [h for h in scanner.all_hosts() if scanner[h].state() == "up"]

def deep_scan_host(ip):
    """Phase 2: OS and port scan for a single device."""
    scanner = nmap.PortScanner()
    scanner.scan(hosts=ip, arguments="-O --top-ports 50 -T4")
    if ip not in scanner.all_hosts():
        return {}, "Unknown", None

    host_data = scanner[ip]
    open_ports = []
    if "tcp" in host_data:
        open_ports = [port for port, data in host_data["tcp"].items() if data["state"] == "open"]

    os_guess = "Unknown"
    if "osmatch" in host_data and host_data["osmatch"]:
        os_guess = host_data["osmatch"][0]["name"]

    mac_address = None
    if "mac" in host_data["addresses"]:
        mac_address = host_data["addresses"]["mac"]

    return open_ports, os_guess, mac_address

def scan_network(network_range=None):
    if not network_range:
        network_range = get_network_range()
    if not network_range:
        print("Could not determine network range.")
        return []

    gateway_ip, _ = get_default_gateway()
    hosts = discover_hosts(network_range)
    print(f"Found {len(hosts)} device(s) in phase 1. Running deep scan on each...")

    devices = []
    for i, ip in enumerate(hosts, start=1):
        print(f"  Deep scanning {ip} ({i}/{len(hosts)})...")
        open_ports, os_guess, mac_address = deep_scan_host(ip)

        vendor = lookup_vendor(mac_address) if mac_address else "Unknown"
        page_title = get_page_title(ip) if 80 in open_ports or 443 in open_ports else None
        device_type = classify_device(ip, gateway_ip, vendor, open_ports, os_guess, None, page_title)

        devices.append({
            "ip": ip,
            "hostname": "Unknown",
            "mac": mac_address or "Unavailable",
            "vendor": vendor,
            "open_ports": ",".join(str(p) for p in open_ports),
            "os_guess": os_guess,
            "device_type": device_type,
            "page_title": page_title,
            "seen_at": datetime.now(timezone.utc)
        })
    return devices

if __name__ == "__main__":
    found = scan_network()
    print(f"\nFound {len(found)} device(s):")
    for d in found:
        title_info = f" | Page: {d['page_title']}" if d['page_title'] else ""
        print(f"  IP: {d['ip']:<15} Type: {d['device_type']:<30} Vendor: {d['vendor']:<20} Ports: {d['open_ports'] or 'none'}{title_info}")