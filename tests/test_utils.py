from scanner.utils import merge_host_data


def test_merge_host_data():
    discovered = {"ip": "192.168.1.10", "mac": "aa:bb:cc:dd:ee:ff"}
    scanned = {"ip": "192.168.1.10", "status": "up", "ports": []}
    merged = merge_host_data(discovered, scanned)
    assert merged["ip"] == "192.168.1.10"
    assert merged["mac"] == "aa:bb:cc:dd:ee:ff"
