#!/usr/bin/env python3
"""Smoke-test every playground demo page offline (P3, IGNITE prep).

Starts router.py on a throwaway port, GETs every static page plus the API
endpoints, and fails if any returns non-200 or a crash body. Mirrors the SDK's
scripts/race_smoke.py philosophy: prove the booth demos render without a
live Foundry token.

Usage:
    python scripts/smoke_demos.py
Exit code 0 = all pages served 200; 1 = at least one failure.
"""
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PORT = int(os.environ.get("SMOKE_PORT", "9123"))
BASE = f"http://127.0.0.1:{PORT}"

PAGES = [
    "/", "/playground.html", "/diff.html", "/matrix.html", "/matrix_app.html",
    "/expo.html", "/trace-viz-demo.html", "/api-reference.html",
    "/auth-guide.html", "/faq.html", "/ignite.html", "/index.html",
]
APIS = ["/api/health", "/api/sdk-matrix"]


def _get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # pragma: no cover - network level
        return -1, str(e)


def main() -> int:
    env = dict(os.environ, PORT=str(PORT))
    proc = subprocess.Popen(
        [sys.executable, os.path.join(ROOT, "router.py")],
        cwd=ROOT, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    failures = 0
    try:
        # wait for the server to come up
        for _ in range(50):
            code, _ = _get("/api/health")
            if code == 200:
                break
            time.sleep(0.2)
        else:
            print("FAIL: router did not start")
            return 1

        for p in PAGES:
            code, body = _get(p)
            ok = code == 200 and "Traceback" not in body and "Traceback" not in body
            # crude crash detector for the static renderer / template errors
            status = "ok" if ok else "FAIL"
            if not ok:
                failures += 1
            print(f"  {status} {code}  {p}")
        for a in APIS:
            code, body = _get(a)
            ok = code == 200 and body.strip() != ""
            status = "ok" if ok else "FAIL"
            if not ok:
                failures += 1
            print(f"  {status} {code}  {a}  ({len(body)} bytes)")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    print(f"\nSMOKE: {'PASS' if failures == 0 else 'FAIL'} "
          f"({failures} failure(s))")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
