from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database.db import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    scan_name = Column(String(255), nullable=False)
    target = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    devices = relationship("Device", back_populates="scan", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    ip_address = Column(String(64), nullable=False, index=True)
    mac_address = Column(String(64), nullable=True)
    hostname = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="up")
    os_guess = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    scan = relationship("Scan", back_populates="devices")
    ports = relationship("Port", back_populates="device", cascade="all, delete-orphan")


class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    port_number = Column(Integer, nullable=False)
    protocol = Column(String(16), nullable=False, default="tcp")
    state = Column(String(32), nullable=False)
    service = Column(String(128), nullable=True)
    version = Column(Text, nullable=True)

    device = relationship("Device", back_populates="ports")
