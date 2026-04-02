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
            "scan_id": device.scan_id,
            "ip_address": device.ip_address,
            "mac_address": device.mac_address,
            "hostname": device.hostname,
            "status": device.status,
            "os_guess": device.os_guess,
            "ports": [
                {
                    "port": port.port_number,
                    "protocol": port.protocol,
                    "state": port.state,
                    "service": port.service,
                    "version": port.version,
                }
                for port in device.ports
            ],
        }
        for device in devices
    ]
