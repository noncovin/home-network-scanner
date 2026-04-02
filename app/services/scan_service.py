from sqlalchemy.orm import Session
from database import crud
from scanner.discovery import discover_hosts
from scanner.nmap_wrapper import scan_host
from scanner.utils import merge_host_data


def run_scan(db: Session, target: str, scan_name: str):
    scan = crud.create_scan(db, scan_name=scan_name, target=target)

    discovered_hosts = discover_hosts(target)
    if not discovered_hosts:
        # Fallback: allow direct host/subnet testing without discovery results.
        discovered_hosts = [{"ip": target, "mac": None}] if "/" not in target else []

    for discovered_host in discovered_hosts:
        scanned_host = scan_host(discovered_host["ip"])
        merged = merge_host_data(discovered_host, scanned_host)
        crud.add_device_with_ports(db, scan.id, merged)

    return crud.complete_scan(db, scan)
