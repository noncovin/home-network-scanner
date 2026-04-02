from sqlalchemy import Column, Integer, String, ForeignKey
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
    os_name = Column(String)
    os_version = Column(String)

class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    port = Column(Integer)
    protocol = Column(String)
    state = Column(String)
    service = Column(String)
    version = Column(String)
