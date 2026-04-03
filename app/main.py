from pathlib import Path
import csv
import io
import os
from sqlalchemy import text
from fastapi import FastAPI, Depends, Form, Request
from fastapi import HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from app.routes.scan_routes import router as scan_router
from app.routes.device_routes import router as device_router
import threading
from app.services.scan_service import start_scan, get_scan_progress, request_cancel
from database.db import Base, engine, get_db
from database.crud import list_devices, list_scans, clear_devices, clear_scans
from database import models

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
APP_USERNAME = os.getenv("APP_USERNAME", "admin")
APP_PASSWORD_HASH = os.getenv("APP_PASSWORD_HASH", "")
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "change-this-secret-key")

Base.metadata.create_all(bind=engine)

with engine.begin() as conn:
    device_columns = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(devices)").fetchall()}
    if "vendor" not in device_columns:
        conn.exec_driver_sql("ALTER TABLE devices ADD COLUMN vendor VARCHAR")
    if "os_name" not in device_columns:
        conn.exec_driver_sql("ALTER TABLE devices ADD COLUMN os_name VARCHAR")
    if "os_version" not in device_columns:
        conn.exec_driver_sql("ALTER TABLE devices ADD COLUMN os_version VARCHAR")

with engine.begin() as conn:
    tables = {
        row[0] for row in conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }

    if "vulnerabilities" not in tables:
        conn.exec_driver_sql("""
            CREATE TABLE vulnerabilities (
                id INTEGER PRIMARY KEY,
                device_id INTEGER,
                port_id INTEGER,
                cve_id VARCHAR,
                description VARCHAR
            )
        """)

app = FastAPI(title="Home Network Scanner", version="0.1.0")
app.add_middleware(
    SessionMiddleware,
    secret_key=APP_SECRET_KEY,
)
app.include_router(scan_router)
app.include_router(device_router)

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def is_authenticated(request: Request) -> bool:
    return bool(request.session.get("user"))


def require_auth(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    return None

# Login/logout routes
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == APP_USERNAME and APP_PASSWORD_HASH and pwd_context.verify(password, APP_PASSWORD_HASH):
        request.session["user"] = username
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid username or password"},
        status_code=401,
    )


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    auth_redirect = require_auth(request)
    if auth_redirect:
        return auth_redirect
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "scans": list_scans(db),
            "devices": list_devices(db),
        },
    )

@app.get("/devices/{device_id}", response_class=HTMLResponse)
def device_detail(device_id: int, request: Request, db: Session = Depends(get_db)):
    auth_redirect = require_auth(request)
    if auth_redirect:
        return auth_redirect

    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return templates.TemplateResponse(
        "device_detail.html",
        {
            "request": request,
            "device": device,
        },
    )

# CSV export route
@app.get("/export/csv")
def export_devices_csv(request: Request, db: Session = Depends(get_db)):
    auth_redirect = require_auth(request)
    if auth_redirect:
        return auth_redirect
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "IP",
        "MAC",
        "Hostname",
        "Vendor",
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
                    getattr(device, "vendor", ""),
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
                getattr(device, "vendor", ""),
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
def clear_devices_route(request: Request, db: Session = Depends(get_db)):
    auth_redirect = require_auth(request)
    if auth_redirect:
        return auth_redirect
    clear_devices(db)
    return RedirectResponse(url="/", status_code=303)


@app.post("/scans/clear")
def clear_scans_route(request: Request, db: Session = Depends(get_db)):
    auth_redirect = require_auth(request)
    if auth_redirect:
        return auth_redirect
    clear_scans(db)
    return RedirectResponse(url="/", status_code=303)


@app.get("/scan")
def scan_get_redirect(request: Request):
    auth_redirect = require_auth(request)
    if auth_redirect:
        return auth_redirect
    return RedirectResponse(url="/", status_code=303)


@app.post("/scan")
@app.post("/scan-ui")
def scan_from_form(
    request: Request,
    target: str = Form(...),
    scan_name: str = Form("Manual Scan"),
    db: Session = Depends(get_db),
):
    auth_redirect = require_auth(request)
    if auth_redirect:
        return auth_redirect
    worker = threading.Thread(target=start_scan, kwargs={"target": target}, daemon=True)
    worker.start()
    return RedirectResponse(url="/", status_code=303)


@app.get("/progress")
def progress_status(request: Request):
    auth_redirect = require_auth(request)
    if auth_redirect:
        return auth_redirect
    return JSONResponse(get_scan_progress())

@app.post("/scan/cancel")
def cancel_scan(request: Request):
    auth_redirect = require_auth(request)
    if auth_redirect:
        return auth_redirect
    request_cancel()
    return RedirectResponse(url="/", status_code=303)
