from pathlib import Path
import csv
import io
from sqlalchemy import text
from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.routes.scan_routes import router as scan_router
from app.routes.device_routes import router as device_router
import threading
from app.services.scan_service import start_scan, get_scan_progress
from database.db import Base, engine, get_db
from database.crud import list_devices, list_scans, clear_devices
from database import models

Base.metadata.create_all(bind=engine)

with engine.begin() as conn:
    device_columns = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(devices)").fetchall()}
    if "os_name" not in device_columns:
        conn.exec_driver_sql("ALTER TABLE devices ADD COLUMN os_name VARCHAR")
    if "os_version" not in device_columns:
        conn.exec_driver_sql("ALTER TABLE devices ADD COLUMN os_version VARCHAR")

app = FastAPI(title="Home Network Scanner", version="0.1.0")
app.include_router(scan_router)
app.include_router(device_router)

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "scans": list_scans(db),
            "devices": list_devices(db),
        },
    )


# CSV export route
@app.get("/export/csv")
def export_devices_csv(db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "IP",
        "MAC",
        "Hostname",
        "OS",
        "OS Version",
        "Port",
        "Protocol",
        "State",
        "Service",
        "Version",
    ])

    devices = db.query(models.Device).all()

    for device in devices:
        if getattr(device, "ports", None):
            for port in device.ports:
                writer.writerow([
                    getattr(device, "ip", ""),
                    getattr(device, "mac", ""),
                    getattr(device, "hostname", ""),
                    getattr(device, "os_name", ""),
                    getattr(device, "os_version", ""),
                    getattr(port, "port", ""),
                    getattr(port, "protocol", ""),
                    getattr(port, "state", ""),
                    getattr(port, "service", ""),
                    getattr(port, "version", ""),
                ])
        else:
            writer.writerow([
                getattr(device, "ip", ""),
                getattr(device, "mac", ""),
                getattr(device, "hostname", ""),
                getattr(device, "os_name", ""),
                getattr(device, "os_version", ""),
                "",
                "",
                "",
                "",
                "",
            ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=discovered_devices.csv"},
    )


# Clear devices route
@app.post("/devices/clear")
def clear_devices_route(db: Session = Depends(get_db)):
    clear_devices(db)
    return RedirectResponse(url="/", status_code=303)


@app.get("/scan")
def scan_get_redirect():
    return RedirectResponse(url="/", status_code=303)


@app.post("/scan")
@app.post("/scan-ui")
def scan_from_form(
    target: str = Form(...),
    scan_name: str = Form("Manual Scan"),
    db: Session = Depends(get_db),
):
    worker = threading.Thread(target=start_scan, kwargs={"target": target}, daemon=True)
    worker.start()
    return RedirectResponse(url="/", status_code=303)


@app.get("/progress")
def progress_status():
    return JSONResponse(get_scan_progress())
