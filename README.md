# Network Monitor

A home network monitoring tool that discovers connected devices,
profiles them (hostname, vendor, open ports, OS guess), and flags
suspicious behavior using rule based scoring and anomaly detection.

## Why

Most home routers show almost nothing about what is actually
happening on the network. This project aims to give a clear,
readable view of every device on a home network, and raise an
alert when something looks risky.

## Status

Early development. Not production ready.

## Ethics and scope

This tool is built for use on networks you own or have explicit
permission to monitor. It includes an ARP spoofing module for
traffic visibility, which should never be run on a network without
the owner's consent. Misusing this tool on networks you do not
control may be illegal in your jurisdiction.

## Stack

- Python (Scapy, FastAPI, SQLAlchemy)
- SQLite
- Web dashboard (PWA)
