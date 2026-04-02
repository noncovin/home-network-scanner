import nmap
from nmap.nmap import PortScannerError


def _extract_os_info(host_data):
    os_name = None
    os_version = None

    os_matches = host_data.get("osmatch", []) if isinstance(host_data, dict) else []
    if os_matches:
        best_match = os_matches[0]
        os_classes = best_match.get("osclass", []) if isinstance(best_match, dict) else []

        if os_classes:
            best_class = os_classes[0]
            vendor = best_class.get("vendor")
            family = best_class.get("osfamily")
            osgen = best_class.get("osgen")

            name_parts = [part for part in [vendor, family] if part]
            if name_parts:
                os_name = " ".join(name_parts)
            else:
                os_name = best_match.get("name")

            os_version = osgen or best_match.get("name")
        else:
            os_name = best_match.get("name")
            os_version = best_match.get("name")

    return os_name, os_version


def run_nmap_scan(target_ip):
    nm = nmap.PortScanner()
    scan_data = {
        "ports": [],
        "os_name": None,
        "os_version": None,
    }

    try:
        nm.scan(hosts=target_ip, arguments="-sT -sV -O --osscan-guess -T4")
    except PortScannerError:
        try:
            nm.scan(hosts=target_ip, arguments="-sT -sV -T4")
        except PortScannerError:
            return scan_data

    results = []

    if target_ip in nm.all_hosts():
        host_data = nm[target_ip]
        os_name, os_version = _extract_os_info(host_data)
        scan_data["os_name"] = os_name
        scan_data["os_version"] = os_version

        for proto in host_data.all_protocols():
            ports = host_data[proto].keys()

            for port in ports:
                service = host_data[proto][port]

                results.append({
                    "port": port,
                    "protocol": proto,
                    "state": service.get("state"),
                    "service": service.get("name"),
                    "version": service.get("version"),
                })

    scan_data["ports"] = results
    return scan_data
