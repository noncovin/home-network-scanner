from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True)
    target = Column(String)
    status = Column(String)

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    ip = Column(String)
    mac = Column(String)
    hostname = Column(String)
    vendor = Column(String)
    os_name = Column(String)
    os_version = Column(String)
    ports = relationship("Port", backref="device", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", backref="device", cascade="all, delete-orphan")

class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    port = Column(Integer)
    protocol = Column(String)
    state = Column(String)
    service = Column(String)
    version = Column(String)
    vulnerabilities = relationship("Vulnerability", backref="port", cascade="all, delete-orphan")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    port_id = Column(Integer, ForeignKey("ports.id"), nullable=True)
    cve_id = Column(String)
    description = Column(String)
