import netifaces

def get_default_gateway():
    gateways = netifaces.gateways()
    default = gateways.get('default', {})
    if netifaces.AF_INET not in default:
        return None, None
    gateway_ip, interface = default[netifaces.AF_INET]
    return gateway_ip, interface

def get_local_ip(interface):
    addrs = netifaces.ifaddresses(interface)
    inet = addrs.get(netifaces.AF_INET)
    if not inet:
        return None
    return inet[0]['addr']

def get_subnet(interface):
    addrs = netifaces.ifaddresses(interface)
    inet = addrs.get(netifaces.AF_INET)
    if not inet:
        return None
    return inet[0].get('netmask')

if __name__ == "__main__":
    gateway_ip, interface = get_default_gateway()
    if not gateway_ip:
        print("Could not detect a default gateway.")
    else:
        local_ip = get_local_ip(interface)
        subnet = get_subnet(interface)
        print(f"Interface: {interface}")
        print(f"Gateway IP: {gateway_ip}")
        print(f"Local IP: {local_ip}")
        print(f"Subnet mask: {subnet}")
