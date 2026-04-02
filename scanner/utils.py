def merge_host_data(discovered_host: dict, scanned_host: dict) -> dict:
    merged = {**scanned_host}
    merged["ip"] = scanned_host.get("ip") or discovered_host.get("ip")
    merged["mac"] = discovered_host.get("mac")
    return merged
