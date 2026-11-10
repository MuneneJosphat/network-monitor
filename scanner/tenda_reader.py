import requests
import base64

def login_and_get_devices(router_ip, password):
    """
    Logs into a Tenda router using its web admin API and returns the
    list of currently connected devices (the 'Online Devices' list).
    Credentials are used only for this one request, never stored.
    """
    session = requests.Session()
    base_url = f"http://{router_ip}"

    # Step 1: log in. Tenda expects the password base64 encoded.
    encoded_password = base64.b64encode(password.encode()).decode()
    login_resp = session.post(
        f"{base_url}/login/Auth",
        data={"password": encoded_password},
        timeout=5
    )

    if login_resp.status_code not in (200, 302):
        return {"success": False, "error": f"Login failed with status {login_resp.status_code}"}

    # Step 2: fetch the online device list using the same logged-in session
    devices_resp = session.get(
        f"{base_url}/goform/getQos",
        params={"modules": "localhost,onlineList,blackList,macFilter"},
        timeout=5
    )

    if devices_resp.status_code != 200:
        return {"success": False, "error": f"Could not fetch device list, status {devices_resp.status_code}"}

    try:
        data = devices_resp.json()
    except ValueError:
        return {"success": False, "error": "Router returned something that wasn't valid JSON, login may have failed silently"}

    online_devices = data.get("onlineList", [])

    devices = []
    for d in online_devices:
        devices.append({
            "hostname": d.get("qosListHostname", "Unknown"),
            "remark": d.get("qosListRemark", ""),
        })

    return {"success": True, "devices": devices, "raw": data}

if __name__ == "__main__":
    router_ip = input("Router IP (e.g. 192.168.100.4): ").strip()
    password = input("Router admin password: ").strip()

    result = login_and_get_devices(router_ip, password)

    if not result["success"]:
        print(f"Error: {result['error']}")
    else:
        print(f"\nFound {len(result['devices'])} connected device(s):")
        for d in result["devices"]:
            print(f"  {d['hostname']}  {('- ' + d['remark']) if d['remark'] else ''}")