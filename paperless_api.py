"""Helper to fetch the next ASN from Paperless-ngx API."""

import os
import requests

PAPERLESS_URL = os.environ.get("PAPERLESS_URL", "https://paperless.contiva.cloud")
PAPERLESS_TOKEN = os.environ.get("PAPERLESS_TOKEN", "")


def get_next_asn():
    """Fetch the current max ASN from Paperless and return the next one."""
    if not PAPERLESS_TOKEN:
        print("Warning: PAPERLESS_TOKEN not set")
        return None

    headers = {"Authorization": f"Token {PAPERLESS_TOKEN}"}
    try:
        resp = requests.get(
            f"{PAPERLESS_URL}/api/documents/",
            headers=headers,
            params={
                "ordering": "-archive_serial_number",
                "page_size": 1,
                "archive_serial_number__isnull": 0,
            },
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if results and results[0].get("archive_serial_number"):
            return results[0]["archive_serial_number"] + 1
    except Exception as e:
        print(f"Warning: Could not fetch ASN from Paperless: {e}")
    return None
