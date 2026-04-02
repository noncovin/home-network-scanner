from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from database.crud import list_scans
from scanner.schemas import ScanRequest
from app.services.scan_service import run_scan

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.get("")
def get_scans(db: Session = Depends(get_db)):
    scans = list_scans(db)
    return [
        {
            "id": scan.id,
            "scan_name": scan.scan_name,
            "target": scan.target,
            "status": scan.status,
            "created_at": scan.created_at.isoformat(),
        }
        for scan in scans
    ]


@router.post("")
def create_scan(payload: ScanRequest, db: Session = Depends(get_db)):
    scan = run_scan(db, target=payload.target, scan_name=payload.scan_name)
    return {
        "id": scan.id,
        "scan_name": scan.scan_name,
        "target": scan.target,
        "status": scan.status,
        "created_at": scan.created_at.isoformat(),
    }
