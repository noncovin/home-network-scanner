import requests


def lookup_cves(service: str | None, version: str | None):
    if not service:
        return []

    query = f"{service} {version or ''}".strip()

    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params = {
        "keywordSearch": query,
        "resultsPerPage": 3,
    }

    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    results = []

    for item in data.get("vulnerabilities", []):
        cve = item.get("cve", {})
        cve_id = cve.get("id")

        descriptions = cve.get("descriptions", [])
        description = next(
            (d.get("value") for d in descriptions if d.get("lang") == "en"),
            "",
        )

        results.append({
            "cve_id": cve_id,
            "description": description[:200],
        })

    return results
