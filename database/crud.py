from sqlalchemy.orm import Session
from database import models


def create_scan(db: Session, scan_name: str, target: str) -> models.Scan:
    scan = models.Scan(scan_name=scan_name, target=target, status="running")
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def complete_scan(db: Session, scan: models.Scan) -> models.Scan:
    scan.status = "completed"
    db.commit()
    db.refresh(scan)
    return scan


def list_scans(db: Session):
    return db.query(models.Scan).order_by(models.Scan.created_at.desc()).all()


def list_devices(db: Session):
    return db.query(models.Device).order_by(models.Device.created_at.desc()).all()


def add_device_with_ports(db: Session, scan_id: int, host_result: dict) -> models.Device:
    device = models.Device(
        scan_id=scan_id,
        ip_address=host_result["ip"],
        mac_address=host_result.get("mac"),
        hostname=host_result.get("hostname"),
        status=host_result.get("status", "up"),
        os_guess=host_result.get("os_guess"),
    )
    db.add(device)
    db.flush()

    for port in host_result.get("ports", []):
        db.add(
            models.Port(
                device_id=device.id,
                port_number=port["port"],
                protocol=port.get("protocol", "tcp"),
                state=port.get("state", "open"),
                service=port.get("service"),
                version=port.get("version"),
            )
        )

    db.commit()
    db.refresh(device)
    return device
