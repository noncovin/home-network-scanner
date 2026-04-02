from pathlib import Path
from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.routes.scan_routes import router as scan_router
from app.routes.device_routes import router as device_router
from app.services.scan_service import run_scan
from database.db import Base, engine, get_db
from database.crud import list_devices, list_scans

Base.metadata.create_all(bind=engine)

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


@app.post("/scan")
def scan_from_form(
    target: str = Form(...),
    scan_name: str = Form("Manual Scan"),
    db: Session = Depends(get_db),
):
    run_scan(db, target=target, scan_name=scan_name)
    return RedirectResponse(url="/", status_code=303)
