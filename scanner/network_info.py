import platform
import subprocess
import re

def _get_gateway_windows():
    result = subprocess.run(["route", "print", "-4"], capture_output=True, text=True)
    output = result.stdout
    match = re.search(r"0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)", output)
    if not match:
        return None, None
    return match.group(1), match.group(2)  # gateway_ip, local_ip

def _get_subnet_windows():
    result = subprocess.run(["ipconfig"], capture_output=True, text=True)
    output = result.stdout
    match = re.search(r"Subnet Mask[.\s]*:\s*(\d+\.\d+\.\d+\.\d+)", output)
    return match.group(1) if match else None

def _get_gateway_linux():
    import netifaces
    gateways = netifaces.gateways()
    default = gateways.get('default', {})
    if netifaces.AF_INET not in default:
        return None, None
    gateway_ip, interface = default[netifaces.AF_INET]
    addrs = netifaces.ifaddresses(interface)
    inet = addrs.get(netifaces.AF_INET)
    local_ip = inet[0]['addr'] if inet else None
    return gateway_ip, local_ip

def _get_subnet_linux():
    import netifaces
    gateways = netifaces.gateways()
    default = gateways.get('default', {})
    if netifaces.AF_INET not in default:
        return None
    _, interface = default[netifaces.AF_INET]
    addrs = netifaces.ifaddresses(interface)
    inet = addrs.get(netifaces.AF_INET)
    return inet[0].get('netmask') if inet else None

def get_default_gateway():
    if platform.system() == "Windows":
        return _get_gateway_windows()
    return _get_gateway_linux()

def get_subnet(interface=None):
    # interface argument kept for compatibility with old scanner.py calls, unused on Windows
    if platform.system() == "Windows":
        return _get_subnet_windows()
    return _get_subnet_linux()

if __name__ == "__main__":
    gateway_ip, local_ip = get_default_gateway()
    subnet = get_subnet()

    if not gateway_ip:
        print("Could not detect a default gateway.")
    else:
        print(f"Gateway IP: {gateway_ip}")
        print(f"Local IP: {local_ip}")
        print(f"Subnet mask: {subnet}")