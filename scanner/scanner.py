import nmap
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
    # Build a simple CIDR assuming a /24 style home network
    parts = gateway_ip.split(".")
    network_range = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    return network_range

def lookup_vendor(mac_address):
    try:
        return mac_lookup.lookup(mac_address)
    except Exception:
        return "Unknown"

def scan_network(network_range=None):
    if not network_range:
        network_range = get_network_range()
    if not network_range:
        print("Could not determine network range.")
        return []

    scanner = nmap.PortScanner()
    print(f"Scanning {network_range}, this may take a moment...")
    scanner.scan(hosts=network_range, arguments="-sn")

    devices = []
    for host in scanner.all_hosts():
        if scanner[host].state() != "up":
            continue

        hostname = scanner[host].hostname() or "Unknown"
        mac_address = None
        vendor = "Unknown"

        if "mac" in scanner[host]["addresses"]:
            mac_address = scanner[host]["addresses"]["mac"]
            vendor = lookup_vendor(mac_address)

        devices.append({
            "ip": host,
            "hostname": hostname,
            "mac": mac_address or "Unavailable",
            "vendor": vendor,
            "seen_at": datetime.now(timezone.utc)
        })
    return devices

if __name__ == "__main__":
    found = scan_network()
    print(f"\nFound {len(found)} device(s):")
    for d in found:
        print(f"  IP: {d['ip']:<15} MAC: {d['mac']:<17} Vendor: {d['vendor']:<20} Hostname: {d['hostname']}")