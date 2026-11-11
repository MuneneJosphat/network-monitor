import time
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange

def discover_mdns_names(timeout=8):
    zc = Zeroconf()
    found = {}
    service_types_seen = set()

    def on_service_type_found(zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            service_types_seen.add(name)

    def on_service_state_change(zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info and info.addresses:
                for addr_bytes in info.addresses:
                    ip = ".".join(str(b) for b in addr_bytes)
                    clean_name = name.split(".")[0]
                    found[ip] = clean_name

    # First, discover what service types actually exist on this network
    meta_browser = ServiceBrowser(zc, "_services._dns-sd._udp.local.", handlers=[on_service_type_found])
    time.sleep(3)

    # Then browse each one we found
    browsers = [
        ServiceBrowser(zc, service_type, handlers=[on_service_state_change])
        for service_type in service_types_seen
    ]

    time.sleep(timeout)
    zc.close()
    return found, service_types_seen

if __name__ == "__main__":
    print("Discovering mDNS service types on the network...")
    mdns_names, types_found = discover_mdns_names()

    print(f"\nService types seen on this network: {len(types_found)}")
    for t in types_found:
        print(f"  {t}")

    print(f"\nFound {len(mdns_names)} device(s) via mDNS:")
    for ip, name in mdns_names.items():
        print(f"  {ip:<15} {name}")