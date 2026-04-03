from scanner.discovery import arp_scan
from scanner.nmap_wrapper import run_nmap_scan
from scanner.vendor_lookup import lookup_vendor
from scanner.vulns import lookup_cves
from database.db import SessionLocal
from database import models
import socket
import time
from copy import deepcopy

def resolve_hostname(ip: str):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return None


SCAN_PROGRESS = {
    "current": {
        "is_running": False,
        "target": None,
        "status": "idle",
        "message": "No scan running",
        "percent": 0,
        "elapsed_seconds": 0,
        "estimated_total_seconds": 0,
        "remaining_seconds": 0,
        "hosts_total": 0,
        "hosts_completed": 0,
    }
}

SCAN_CANCEL = {"cancel": False}


def _set_progress(**updates):
    current = SCAN_PROGRESS["current"]
    current.update(updates)

    elapsed = max(0, int(current.get("elapsed_seconds", 0)))
    estimated_total = max(0, int(current.get("estimated_total_seconds", 0)))

    if current.get("is_running"):
        if estimated_total > 0:
            current["remaining_seconds"] = max(0, estimated_total - elapsed)
        else:
            current["remaining_seconds"] = 0
    else:
        current["remaining_seconds"] = 0


def get_scan_progress():
    return deepcopy(SCAN_PROGRESS["current"])


def request_cancel():
    SCAN_CANCEL["cancel"] = True


def reset_cancel():
    SCAN_CANCEL["cancel"] = False


def start_scan(target: str):
    db = SessionLocal()
    start_time = time.time()
    reset_cancel()
    final_status = "running"

    _set_progress(
        is_running=True,
        target=target,
        status="running",
        message="Starting scan...",
        percent=2,
        elapsed_seconds=0,
        estimated_total_seconds=20,
        remaining_seconds=20,
        hosts_total=0,
        hosts_completed=0,
    )

    # Create scan record
    scan = models.Scan(target=target, status="running")
    db.add(scan)
    db.commit()
    db.refresh(scan)

    try:
        _set_progress(
            message="Discovering hosts...",
            percent=10,
            elapsed_seconds=int(time.time() - start_time),
            estimated_total_seconds=20,
        )

        # 1. Discover hosts
        hosts = arp_scan(target)
        hosts_total = len(hosts)

        estimated_total_seconds = max(10, int(time.time() - start_time) + max(6, hosts_total * 4))
        _set_progress(
            message=f"Discovered {hosts_total} host(s). Scanning ports...",
            percent=20,
            elapsed_seconds=int(time.time() - start_time),
            estimated_total_seconds=estimated_total_seconds,
            hosts_total=hosts_total,
            hosts_completed=0,
        )

        if hosts_total == 0:
            scan.status = "completed"
            db.commit()
            final_status = scan.status
            _set_progress(
                is_running=False,
                status="completed",
                message="Scan completed. No hosts found.",
                percent=100,
                elapsed_seconds=int(time.time() - start_time),
                estimated_total_seconds=int(time.time() - start_time),
                hosts_total=0,
                hosts_completed=0,
            )
            return {"status": final_status}

        for index, host in enumerate(hosts, start=1):
            if SCAN_CANCEL.get("cancel"):
                scan.status = "cancelled"
                db.commit()
                final_status = scan.status
                _set_progress(
                    is_running=False,
                    status="cancelled",
                    message="Scan cancelled by user",
                    percent=100,
                    elapsed_seconds=int(time.time() - start_time),
                    estimated_total_seconds=int(time.time() - start_time),
                    hosts_total=hosts_total,
                    hosts_completed=index - 1,
                )
                return {"status": final_status}
            device = models.Device(
                ip=host["ip"],
                mac=host.get("mac"),
                hostname=resolve_hostname(host["ip"]),
                vendor=lookup_vendor(host.get("mac")),
            )
            db.add(device)
            db.commit()
            db.refresh(device)

            # 2. Run Nmap scan
            scan_result = run_nmap_scan(host["ip"])
            ports = scan_result.get("ports", []) if isinstance(scan_result, dict) else scan_result
            device.os_name = scan_result.get("os_name") if isinstance(scan_result, dict) else None
            device.os_version = scan_result.get("os_version") if isinstance(scan_result, dict) else None

            # 3. Save ports
            for p in ports:
                port = models.Port(
                    device_id=device.id,
                    port=p["port"],
                    protocol=p["protocol"],
                    state=p["state"],
                    service=p.get("service"),
                    version=p.get("version")
                )
                db.add(port)
                db.flush()

                cves = lookup_cves(p.get("service"), p.get("version"))
                for cve in cves:
                    vuln = models.Vulnerability(
                        device_id=device.id,
                        port_id=port.id,
                        cve_id=cve.get("cve_id"),
                        description=cve.get("description"),
                    )
                    db.add(vuln)

            db.commit()

            percent = 20 + int((index / hosts_total) * 75)
            elapsed_seconds = int(time.time() - start_time)
            _set_progress(
                message=f"Scanned {index} of {hosts_total} host(s)...",
                percent=min(percent, 95),
                elapsed_seconds=elapsed_seconds,
                estimated_total_seconds=max(estimated_total_seconds, elapsed_seconds),
                hosts_total=hosts_total,
                hosts_completed=index,
            )

        scan.status = "completed"
        db.commit()
        final_status = scan.status

        total_elapsed = int(time.time() - start_time)
        _set_progress(
            is_running=False,
            status="completed",
            message="Scan completed.",
            percent=100,
            elapsed_seconds=total_elapsed,
            estimated_total_seconds=total_elapsed,
            hosts_total=hosts_total,
            hosts_completed=hosts_total,
        )

    except Exception as e:
        scan.status = "failed"
        db.commit()
        final_status = scan.status
        total_elapsed = int(time.time() - start_time)
        _set_progress(
            is_running=False,
            status="failed",
            message=f"Scan failed: {str(e)}",
            percent=100,
            elapsed_seconds=total_elapsed,
            estimated_total_seconds=total_elapsed,
        )
        raise e

    finally:
        db.close()

    return {"status": final_status}
