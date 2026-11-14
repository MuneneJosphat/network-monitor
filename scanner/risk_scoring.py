RISKY_PORTS = {
    21: "FTP (often unencrypted, outdated)",
    23: "Telnet (unencrypted remote access, high risk)",
    135: "Windows RPC (commonly targeted)",
    139: "NetBIOS (legacy, exploitable)",
    445: "SMB (common ransomware target if exposed)",
    3389: "RDP (remote desktop, high value target if exposed)",
    5900: "VNC (remote control, often poorly secured)",
}

def score_device(device_type, open_ports_str, vendor, hostname, ip, gateway_ip, mac_address):
    """
    Returns (risk_level, reasons) where risk_level is one of
    Low, Medium, High, Critical, and reasons is a list of short
    human readable explanations for why.
    """
    score = 0
    reasons = []

    open_ports = []
    if open_ports_str:
        try:
            open_ports = [int(p) for p in open_ports_str.split(",") if p.strip().isdigit()]
        except ValueError:
            open_ports = []

    # Risky ports open
    for port in open_ports:
        if port in RISKY_PORTS:
            score += 25
            reasons.append(f"Port {port} open ({RISKY_PORTS[port]})")

    # Completely unidentified device, no vendor, no hostname, no type
    if (not vendor or vendor == "Unknown") and (not hostname or hostname == "Unknown") and device_type == "Unknown":
        score += 15
        reasons.append("No identifying information found for this device")

    # Gateway IP mismatch, possible spoofing red flag
    if gateway_ip and ip == gateway_ip and device_type != "Router (Main Gateway)":
        score += 40
        reasons.append("This IP is your gateway but did not classify as the router, possible spoofing")

    # Many risky ports open at once is worse than just one
    risky_open_count = sum(1 for p in open_ports if p in RISKY_PORTS)
    if risky_open_count >= 3:
        score += 20
        reasons.append(f"{risky_open_count} risky ports open simultaneously")

    # Convert score to a risk level
    if score >= 70:
        risk_level = "Critical"
    elif score >= 40:
        risk_level = "High"
    elif score >= 15:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if not reasons:
        reasons.append("No risk indicators found")

    return risk_level, reasons

if __name__ == "__main__":
    # Quick manual test
    level, reasons = score_device(
        device_type="Unknown",
        open_ports_str="23,3389",
        vendor="Unknown",
        hostname="Unknown",
        ip="192.168.1.50",
        gateway_ip="192.168.1.1",
        mac_address="AA:BB:CC:DD:EE:FF"
    )
    print(f"Risk level: {level}")
    for r in reasons:
        print(f"  - {r}")