# Home Network Scanner

A modular, open-source home network scanner built with Python, FastAPI, SQLAlchemy, and SQLite.

## Features

- Discover hosts on a local subnet
- Run TCP port scans with Nmap
- Store scan history in SQLite
- View devices and scan results in a simple web UI
- Expose a small API for triggering scans and viewing results
- Designed to be extended with service detection, vulnerability lookups, and change tracking

## Authorized Use

Use this project only on networks and systems you own or are explicitly authorized to assess.

## Architecture

The project is split into three layers:

- **Scanner core**: host discovery and port scanning
- **Web layer**: FastAPI routes and HTML pages
- **Data layer**: SQLAlchemy models backed by SQLite

## Project Layout

```text
home-network-scanner/
├── app/
├── scanner/
├── database/
├── tests/
├── scripts/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── pyproject.toml
└── docker-compose.yml
```

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Install Nmap

You need the Nmap binary installed locally because `python-nmap` wraps the Nmap executable.

### 3. Run the app

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## API Endpoints

- `GET /health` - health check
- `POST /api/scans` - create a new scan
- `GET /api/scans` - list scans
- `GET /api/devices` - list discovered devices

Example scan request:

```bash
curl -X POST http://127.0.0.1:8000/api/scans \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.0/24","scan_name":"Initial Scan"}'
```

## Roadmap

### v0.1.0
- Subnet input
- ARP-based discovery
- Common TCP port scan
- SQLite persistence
- Simple dashboard

### v0.2.0
- Service version detection
- Historical change tracking
- JSON and CSV exports
- Scheduled scans

### v0.3.0
- Vulnerability enrichment
- Device fingerprinting
- Network graph view
- Authentication

## Development

```bash
pytest
```

## Notes

- Some scans may require elevated privileges depending on the host OS and scan type.
- ARP discovery is intended for local network segments.
- Vulnerability enrichment is scaffolded but not fully implemented in this starter release.
