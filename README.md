markdown
# Network Monitor

A home network monitoring tool that discovers connected devices, identifies
what it can about each one (vendor, type, open ports, operating system
guess), and flags devices with a rule based risk score, with a clear
explanation for every flag it raises.

## Why this exists

Most home routers show almost nothing about what is actually on the
network. This tool scans the local network, builds a readable picture of
every device it finds, and explains any risk indicators in plain language,
rather than just showing a number with no context.

## Features

- Two phase network scanning: a fast discovery pass followed by a deeper
  scan (open ports, OS guess) on each device found
- MAC address and vendor lookup
- Device type classification (router, computer, smart TV, phone, etc.)
  based on vendor, open ports, OS fingerprint, and web login page titles
- mDNS based hostname discovery as a fallback when standard detection
  does not return a name
- Rule based risk scoring (Low, Medium, High, Critical) with a plain
  language explanation for every flag
- A live dashboard (auto refreshes every 10 seconds) showing all devices
  with editable nicknames
- Works on native Windows and on WSL2 (with reduced device visibility
  under WSL2, since its virtual network cannot see the host's real LAN)

## Setup

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\Activate.ps1` (Windows) or
   `source venv/bin/activate` (Linux/WSL)
4. Install dependencies: `pip install -r requirements.txt`
5. Install [Nmap](https://nmap.org/download.html) and, on Windows,
   [Npcap](https://npcap.com/#download) (select "WinPcap API-compatible
   mode" during install)
6. Initialize the database: `python scanner/models.py`

## Running it

Scanning requires elevated privileges (raw network access):

- **Windows**: run PowerShell as Administrator, then:

python scanner\save_devices.py

- **Start the API and dashboard**:

.\start.ps1

Then open `dashboard/index.html` in your browser.

## Architecture

scanner/ -> device discovery, classification, risk scoring, database models
api/ -> FastAPI backend serving device data as JSON
dashboard/ -> static HTML/JS dashboard, polls the API
data/ -> SQLite database (not tracked in git)


## Known limitations

**Phone scanning is not supported, and this is an OS restriction, not a
missed feature.** Since Android 10, apps have been blocked from reading
a device's ARP table, which is what makes MAC address, vendor, and OS
detection possible on a laptop. An unrooted phone can only see which IP
addresses respond to a ping, nothing more. This tool is built to run on
a laptop or desktop with a full network stack, not natively on a phone.
The dashboard itself can still be viewed from a phone's browser, as long
as the phone is on the same network as the machine running the scanner.

**Router login based device lists are brand specific and are not
included.** Pulling a "connected devices" list directly from a router's
admin page requires reverse engineering that specific router's login
flow and page structure, there is no universal standard for this across
brands (TR-064 exists but is used almost exclusively by Fritz!Box
routers). An early working example for Tenda routers was built and then
removed to keep the project's scope focused on scanning that works
regardless of router brand or ISP.

**Deep scanning takes longer than a basic scan.** OS detection and port
scanning are done per device after an initial fast discovery pass, so a
full scan of a network with several devices can take a minute or more.

**WSL2 cannot see your real home network.** WSL2 runs behind a NAT layer
with its own virtual network, so scanning from inside WSL will only find
WSL's virtual gateway, not real devices. Run the scanner on native
Windows (or native Linux) for real results.

## Possible future work

- DNS query logging to flag suspicious domains a device is contacting
- ARP based traffic inspection for deeper behavioral analysis
- A known/unknown device approval flow with persistent alerts
- Support for additional router brands' device list APIs

## Ethics and scope

This tool is built for use on networks you own or have explicit
permission to monitor.