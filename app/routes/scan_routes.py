from fastapi import APIRouter, Query
from app.services.scan_service import start_scan

router = APIRouter()

@router.post("/api/scan")
def run_scan(target: str = Query(...)):
    return {"message": "Use the web form at /scan-ui for browser scans, or update this API route to pass a database session."}
