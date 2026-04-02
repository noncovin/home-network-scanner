def guess_device_type(host_result: dict) -> str | None:
    """Very small placeholder for future device classification logic."""
    open_services = {p.get("service") for p in host_result.get("ports", [])}
    if "ipp" in open_services or "printer" in open_services:
        return "printer"
    if "ssh" in open_services and "http" in open_services:
        return "server"
    return None
