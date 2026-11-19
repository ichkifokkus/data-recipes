"""Check every credential a scheduled job depends on BEFORE doing any work.

One cheap, read-only request per dependency. Never prints secrets: tokens are read
from the environment (or injected by a proxy) and only the HTTP status is reported.

    python preflight.py && python your_daily_job.py
"""
import os
import sys

import requests

def _hdr(name: str, env: str, prefix: str = "") -> dict:
    token = os.environ.get(env)
    return {name: prefix + token} if token else {}  # unset -> no header (e.g. a proxy injects it)


CHECKS = {
    # name: (url, headers) - pick an endpoint that needs auth but costs nothing
    "apify": ("https://api.apify.com/v2/users/me", _hdr("Authorization", "APIFY_TOKEN", "Bearer ")),
    "devto": ("https://dev.to/api/articles/me?per_page=1", _hdr("api-key", "DEVTO_API_KEY")),
}


def preflight() -> dict:
    status = {}
    for name, (url, headers) in CHECKS.items():
        try:
            status[name] = requests.get(url, headers=headers, timeout=15).status_code
        except requests.RequestException as e:
            status[name] = f"network error: {type(e).__name__}"
    return status


if __name__ == "__main__":
    result = preflight()
    for name, code in result.items():
        print(f"{name:8} {code}")
    bad = [n for n, c in result.items() if c != 200]
    if bad:
        print("FAILED:", ", ".join(bad), "- fix credentials before the job runs", file=sys.stderr)
        sys.exit(1)
