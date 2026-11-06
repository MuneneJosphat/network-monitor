import nmap
from datetime import datetime
from network_info import get_default_gateway, get_subnet

def get_network_range():
    gateway_ip, interface = get_default_gateway()
    if not gateway_ip:
        return None
    subnet = get_subnet(interface)
    if not subnet:
        return None
    # Build a simple CIDR assuming a /24 style home network
    # We refine this later once we're on the real LAN
    parts = gateway_ip.split(".")
    network_range = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    return network_range

def scan_network(network_range=None):
    if not network_range:
        network_range = get_network_range()
    if not network_range:
        print("Could not determine network range.")
        return []

    scanner = nmap.PortScanner()
    print(f"Scanning {network_range}, this may take a moment...")
    scanner.scan(hosts=network_range, arguments="-sn")  # -sn = ping scan, no port scan yet

    devices = []
    for host in scanner.all_hosts():
        if scanner[host].state() == "up":
            hostname = scanner[host].hostname() or "Unknown"
            devices.append({
                "ip": host,
                "hostname": hostname,
                "seen_at": datetime.utcnow()
            })
    return devices

if __name__ == "__main__":
    found = scan_network()
    print(f"\nFound {len(found)} device(s):")
    for d in found:
        print(f"  IP: {d['ip']:<15} Hostname: {d['hostname']}")
