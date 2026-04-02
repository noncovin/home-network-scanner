# Home Network Scanner

A modular, open-source home network scanner built with Python, FastAPI, SQLAlchemy, and SQLite.

## Features

- Discover hosts on a local subnet using multiple techniques:
  - ARP scan (Scapy)
  - Nmap ping scan
  - ARP table fallback
  - TCP probe for silent devices
- Run TCP port scans with service and version detection (Nmap)
- Perform best-effort OS detection and version fingerprinting
- Store scan history in SQLite
- View devices, ports, OS, and scan progress in a web UI
- Real-time scan progress bar with elapsed and estimated time
- Export discovered devices to CSV
- Clear discovered devices from the UI
- Expose a REST API for scans, devices, and progress

## Authorized Use

Use this project only on networks and systems you own or are explicitly authorized to assess.

## Architecture

The project is split into three layers:

- **Scanner core**: host discovery, port scanning, OS detection
- **Web layer**: FastAPI routes, HTML UI, progress polling
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

You must install the Nmap binary locally because `python-nmap` wraps the Nmap executable.

- macOS: `brew install nmap`
- Linux: `sudo apt install nmap`

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
- `GET /progress` - current scan progress
- `GET /export/csv` - download discovered devices as CSV

Example scan request:

```bash
curl -X POST http://127.0.0.1:8000/api/scans \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.0/24","scan_name":"Initial Scan"}'
```

## UI Features

- Start scans from the browser
- View discovered devices with:
  - IP address
  - Hostname
  - OS and OS version (best effort)
  - Open ports and services
- Real-time progress bar with:
  - Percent complete
  - Elapsed time
  - Estimated time remaining
  - Hosts scanned vs total
- Clear device list
- Export results to CSV

## Notes on OS Detection

- OS detection uses Nmap fingerprinting (`-O`)
- Results are best-effort and may be:
  - Accurate on active hosts
  - Partial or missing on filtered devices
- Running with elevated privileges improves accuracy:

```bash
sudo uvicorn app.main:app --reload
```

## Roadmap

### v0.1.0
- Subnet input
- Multi-method host discovery
- TCP port scanning
- SQLite persistence
- Web dashboard

### v0.2.0
- Service version detection (complete)
- CSV export (complete)
- OS fingerprinting (complete)
- Scheduled scans
- Scan history improvements

### v0.3.0
- Vulnerability enrichment (CVE/NVD)
- MAC vendor lookup
- Network graph visualization
- Authentication and user accounts

## Development

```bash
pytest
```

## Notes

- Some scans require elevated privileges depending on OS
- ARP discovery works only on local network segments
- TCP probing increases detection but adds scan time
- OS detection is not guaranteed for all devices

## License

See `LICENSE` file for details.
