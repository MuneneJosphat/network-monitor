import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scanner"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import SessionLocal, Device

app = FastAPI(title="Network Monitor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Network Monitor API is running"}

@app.get("/devices")
def get_devices():
    session = SessionLocal()
    devices = session.query(Device).all()
    result = []
    for d in devices:
        result.append({
            "id": d.id,
            "mac_address": d.mac_address,
            "ip_address": d.ip_address,
            "hostname": d.hostname,
            "vendor": d.vendor,
            "nickname": d.nickname,
            "device_type": d.device_type,
            "os_guess": d.os_guess,
            "first_seen": d.first_seen.isoformat() if d.first_seen else None,
            "last_seen": d.last_seen.isoformat() if d.last_seen else None,
            "is_known": d.is_known,
            "risk_level": d.risk_level,
        })
    session.close()
    return result
