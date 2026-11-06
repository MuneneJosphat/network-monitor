from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    mac_address = Column(String, unique=True, nullable=False)
    ip_address = Column(String)
    hostname = Column(String)
    vendor = Column(String)
    nickname = Column(String)
    device_type = Column(String)
    os_guess = Column(String)
    first_seen = Column(DateTime, default=utcnow)
    last_seen = Column(DateTime, default=utcnow)
    is_known = Column(Integer, default=0)  # 0 = unknown, 1 = approved
    risk_level = Column(String, default="Low")  # Low, Medium, High, Critical

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    device_mac = Column(String, nullable=False)
    message = Column(String)
    severity = Column(String)  # Low, Medium, High, Critical
    created_at = Column(DateTime, default=utcnow)
    resolved = Column(Integer, default=0)  # 0 = open, 1 = resolved

class DNSQuery(Base):
    __tablename__ = "dns_queries"

    id = Column(Integer, primary_key=True)
    device_mac = Column(String, nullable=False)
    domain = Column(String)
    queried_at = Column(DateTime, default=utcnow)
    flagged = Column(Integer, default=0)  # 0 = normal, 1 = flagged as risky

engine = create_engine("sqlite:///data/network_monitor.db")
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized at data/network_monitor.db")
