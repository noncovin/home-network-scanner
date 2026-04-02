from typing import List, Optional
from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    target: str = Field(..., examples=["192.168.1.0/24"])
    scan_name: str = Field(default="Manual Scan")


class PortResult(BaseModel):
    port: int
    protocol: str = "tcp"
    state: str
    service: Optional[str] = None
    version: Optional[str] = None


class HostResult(BaseModel):
    ip: str
    mac: Optional[str] = None
    hostname: Optional[str] = None
    status: str = "up"
    os_guess: Optional[str] = None
    ports: List[PortResult] = []
