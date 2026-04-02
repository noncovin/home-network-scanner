from typing import Dict, List
import os

try:
    import nmap
except Exception:  # pragma: no cover
    nmap = None

DEFAULT_SCAN_ARGUMENTS = os.getenv("DEFAULT_SCAN_ARGUMENTS", "-T4 -F")


def scan_host(ip_address: str, arguments: str = DEFAULT_SCAN_ARGUMENTS) -> Dict:
    """Scan a single host with Nmap and return normalized data."""
    if nmap is None:
        return {
            "ip": ip_address,
            "status": "unknown",
            "ports": [],
        }

    scanner = nmap.PortScanner()
    scanner.scan(hosts=ip_address, arguments=arguments)

    if ip_address not in scanner.all_hosts():
        return {
            "ip": ip_address,
            "status": "down",
            "ports": [],
        }

    host_data = scanner[ip_address]
    ports: List[Dict] = []
    for proto in host_data.all_protocols():
        for port_number, details in host_data[proto].items():
            ports.append(
                {
                    "port": int(port_number),
                    "protocol": proto,
                    "state": details.get("state", "unknown"),
                    "service": details.get("name"),
                    "version": " ".join(
                        filter(
                            None,
                            [details.get("product"), details.get("version"), details.get("extrainfo")],
                        )
                    )
                    or None,
                }
            )

    return {
        "ip": ip_address,
        "hostname": host_data.hostname() if hasattr(host_data, "hostname") else None,
        "status": host_data.state() if hasattr(host_data, "state") else "up",
        "ports": sorted(ports, key=lambda p: (p["protocol"], p["port"])),
    }
