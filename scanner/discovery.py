from typing import List, Dict

try:
    from scapy.all import ARP, Ether, srp
except Exception:  # pragma: no cover
    ARP = Ether = srp = None


def discover_hosts(subnet: str, timeout: int = 2) -> List[Dict[str, str]]:
    """Discover hosts on a local subnet using ARP.

    Falls back to an empty result if Scapy is unavailable at runtime.
    """
    if ARP is None or Ether is None or srp is None:
        return []

    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet)
    answered, _ = srp(packet, timeout=timeout, verbose=False)

    hosts = []
    for _, response in answered:
        hosts.append({"ip": response.psrc, "mac": response.hwsrc})
    return hosts
