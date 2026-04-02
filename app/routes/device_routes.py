from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from database.crud import list_devices

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("")
def get_devices(db: Session = Depends(get_db)):
    devices = list_devices(db)
    return [
        {
            "id": device.id,
            "scan_id": getattr(device, "scan_id", None),
            "ip": getattr(device, "ip", None),
            "mac": getattr(device, "mac", None),
            "hostname": getattr(device, "hostname", None),
            "ports": [
                {
                    "port": getattr(port, "port", None),
                    "protocol": getattr(port, "protocol", None),
                    "state": getattr(port, "state", None),
                    "service": getattr(port, "service", None),
                    "version": getattr(port, "version", None),
                }
                for port in device.ports
            ],
        }
        for device in devices
    ]
