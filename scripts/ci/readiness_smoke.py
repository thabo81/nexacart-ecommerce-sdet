"""Readiness smoke check used by CI (TEST-001). Standard library only; prints no credentials.

Two modes against a running API process:

* ``--expect ready``: /health/live is 200 *and* /health/ready returns 200 {"status": "ready"},
  which the application only does after a real PostgreSQL round-trip succeeds.
* ``--expect not-ready``: /health/live is still 200 (process is up) but /health/ready returns
  503 with error code NOT_READY and ``Cache-Control: no-store``. Run it against an instance whose
  database is unreachable to prove readiness reflects database connectivity, not process start.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlsplit


def fetch(url: str, timeout: float) -> tuple[int, dict[str, str], Any]:
    """GET ``url`` (http/https only). Returns (status, lower-cased headers, parsed JSON or None)."""
    if urlsplit(url).scheme not in {"http", "https"}:
        raise ValueError("only http(s) URLs are allowed")
    request = urllib.request.Request(url, method="GET")  # noqa: S310 - scheme validated above
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            status, headers, raw = response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        status, headers, raw = error.code, error.headers, error.read()
    try:
        body: Any = json.loads(raw)
    except ValueError:
        body = None
    return status, {k.lower(): v for k, v in headers.items()}, body


def wait_for(url: str, wanted: int, deadline: float) -> tuple[int, dict[str, str], Any]:
    """Poll until ``url`` returns ``wanted`` or the deadline passes; returns the last response."""
    last: tuple[int, dict[str, str], Any] = (0, {}, None)
    while True:
        try:
            last = fetch(url, timeout=5)
            if last[0] == wanted:
                return last
        except OSError:
            last = (0, {}, None)  # connection refused while the server starts
        if time.monotonic() >= deadline:
            return last
        time.sleep(1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument("--base-url", required=True, help="API origin, e.g. http://127.0.0.1:8000")
    parser.add_argument("--expect", choices=["ready", "not-ready"], required=True)
    parser.add_argument("--timeout", type=float, default=60, help="seconds to wait for the process")
    args = parser.parse_args(argv)
    base = args.base_url.rstrip("/")
    deadline = time.monotonic() + args.timeout

    status, _, body = wait_for(f"{base}/health/live", 200, deadline)
    if status != 200 or body != {"status": "ok"}:
        print(f"FAIL liveness: expected 200 {{'status': 'ok'}}, got {status} {body!r}")
        return 1
    print("PASS liveness: process is up")

    if args.expect == "ready":
        status, _, body = wait_for(f"{base}/health/ready", 200, deadline)
        if status != 200 or body != {"status": "ready"}:
            print(f"FAIL readiness: expected 200 {{'status': 'ready'}}, got {status} {body!r}")
            return 1
        print("PASS readiness: 200 ready (database round-trip succeeded)")
        return 0

    status, headers, body = wait_for(f"{base}/health/ready", 503, deadline)
    code = body.get("error", {}).get("code") if isinstance(body, dict) else None
    if status != 503 or code != "NOT_READY":
        print(f"FAIL readiness: expected 503 NOT_READY, got {status} code={code!r}")
        return 1
    if headers.get("cache-control") != "no-store":
        found = headers.get("cache-control")
        print(f"FAIL readiness: expected Cache-Control: no-store, got {found!r}")
        return 1
    print("PASS readiness: 503 NOT_READY while liveness stays 200 (database unreachable)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
