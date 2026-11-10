import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import subprocess
import re
import platform

def _run_netsh():
    result = subprocess.run(
        ["netsh", "wlan", "show", "interfaces"],
        capture_output=True
    )
    for encoding in ["utf-8", "cp850", "cp437", "utf-16"]:
        try:
            return result.stdout.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return result.stdout.decode("utf-8", errors="replace")

def _fix_mojibake(text):
    """Repairs text that was UTF-8 but got decoded as cp1252/latin-1 somewhere upstream."""
    try:
        return text.encode("cp1252").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text

def get_connected_ssid():
    details = get_wifi_details()
    return details.get("ssid")

def get_wifi_details():
    if platform.system() != "Windows":
        return {}
    try:
        output = _run_netsh()

        def extract(label):
            match = re.search(rf"^\s*{label}\s*:\s*(.+)$", output, re.MULTILINE)
            return match.group(1).strip() if match else None

        ssid = extract("SSID")
        if ssid:
            ssid = _fix_mojibake(ssid)

        return {
            "ssid": ssid,
            "signal": extract("Signal"),
            "radio_type": extract("Radio type"),
            "channel": extract("Channel"),
        }
    except Exception:
        return {}

if __name__ == "__main__":
    details = get_wifi_details()
    if not details or not details.get("ssid"):
        print("Could not detect wifi network. Are you connected via wifi (not ethernet)?")
    else:
        print(f"Connected to: {details['ssid']}")
        print(f"Signal: {details.get('signal', 'Unknown')}")
        print(f"Radio type: {details.get('radio_type', 'Unknown')}")
        print(f"Channel: {details.get('channel', 'Unknown')}")