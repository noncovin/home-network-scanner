from scapy.all import ARP, Ether, srp
from scapy.error import Scapy_Exception
import nmap
import subprocess
import re

import ipaddress
import socket


IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
MAC_PATTERN = re.compile(r"\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b")
COMMON_TCP_PORTS = (80, 443, 22, 53, 445, 139, 62078, 8009, 8080, 8443)


def _normalize_hosts(hosts, target):
    merged = {}
    try:
        target_network = ipaddress.ip_network(target, strict=False)
    except ValueError:
        target_network = None

    for host in hosts:
        ip = host.get("ip")
        if not ip:
            continue

        if target_network is not None:
            try:
                if ipaddress.ip_address(ip) not in target_network:
                    continue
            except ValueError:
                continue

        if ip not in merged:
            merged[ip] = {"ip": ip, "mac": host.get("mac")}
        elif not merged[ip].get("mac") and host.get("mac"):
            merged[ip]["mac"] = host.get("mac")

    return list(merged.values())


def _scapy_arp_scan(target):
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target)
    result = srp(packet, timeout=2, verbose=0)[0]

    hosts = []
    for _, received in result:
        hosts.append({
            "ip": received.psrc,
            "mac": received.hwsrc,
        })

    return hosts


def _nmap_ping_scan(target):
    nm = nmap.PortScanner()
    nm.scan(hosts=target, arguments="-sn")

    hosts = []
    for host in nm.all_hosts():
        mac = None
        addresses = nm[host].get("addresses", {})
        if isinstance(addresses, dict):
            mac = addresses.get("mac")

        hosts.append({
            "ip": host,
            "mac": mac,
        })

    return hosts


def _arp_table_scan():
    hosts = []

    for command in (["arp", "-a"], ["ip", "neigh"]):
        try:
            output = subprocess.check_output(command, stderr=subprocess.DEVNULL, text=True)
        except Exception:
            continue

        for line in output.splitlines():
            ip_match = IP_PATTERN.search(line)
            if not ip_match:
                continue

            mac_match = MAC_PATTERN.search(line)
            hosts.append({
                "ip": ip_match.group(0),
                "mac": mac_match.group(0) if mac_match else None,
            })

        if hosts:
            break

    return hosts


def _tcp_probe_scan(target):
    hosts = []
    try:
        network = ipaddress.ip_network(target, strict=False)
    except ValueError:
        return hosts

    for ip in network.hosts():
        ip_str = str(ip)

        for port in COMMON_TCP_PORTS:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.2)
            try:
                result = sock.connect_ex((ip_str, port))
                if result == 0:
                    hosts.append({
                        "ip": ip_str,
                        "mac": None,
                    })
                    break
            except Exception:
                pass
            finally:
                sock.close()

    return hosts


def arp_scan(target):
    discovered_hosts = []

    try:
        discovered_hosts.extend(_scapy_arp_scan(target))
    except (PermissionError, Scapy_Exception):
        pass
    except Exception:
        pass

    try:
        discovered_hosts.extend(_nmap_ping_scan(target))
    except Exception:
        pass

    try:
        discovered_hosts.extend(_arp_table_scan())
    except Exception:
        pass

    try:
        discovered_hosts.extend(_tcp_probe_scan(target))
    except Exception:
        pass

    return _normalize_hosts(discovered_hosts, target)
