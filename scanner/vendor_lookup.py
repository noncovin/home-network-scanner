

from pathlib import Path

OUI_DB = {}


def load_oui_db():
    global OUI_DB

    if OUI_DB:
        return OUI_DB

    oui_file = Path("data/oui.txt")

    if not oui_file.exists():
        return OUI_DB

    for line in oui_file.read_text(errors="ignore").splitlines():
        parts = line.split(",", 1)
        if len(parts) == 2:
            prefix = parts[0].strip().upper().replace("-", ":")
            vendor = parts[1].strip()
            OUI_DB[prefix] = vendor

    return OUI_DB


def lookup_vendor(mac: str | None):
    if not mac:
        return None

    mac = mac.upper().replace("-", ":")
    prefix = ":".join(mac.split(":")[:3])

    db = load_oui_db()
    return db.get(prefix)
