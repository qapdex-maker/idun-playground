#!/usr/bin/env python3
"""Start the Idun playground router with credentials loaded from
~/.idun/config.toml (no shell env inheritance needed for background launch).

Reads idun_base / idun_project / idun_agent (and FOUNDRY_TOKEN from
~/foundry_token.txt) and exports them into os.environ BEFORE importing
router.py, so the SDK resolves them correctly.
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.expanduser("~/.idun/config.toml")
TOKEN_FILE = os.path.expanduser("~/foundry_token.txt")


def _read_toml(path):
    # Minimal TOML reader for the few keys we need (avoids extra deps).
    data = {}
    section = None
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("[") and line.endswith("]"):
                    section = line[1:-1].strip()
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if section:
                        k = f"{section}.{k}"
                    data[k] = v
    except FileNotFoundError:
        pass
    return data


def main():
    # Tenant-agnostic: read Foundry coordinates from ~/.idun/config.toml
    # ([defaults] idun_base / idun_project / idun_agent) or the environment.
    # NO tenant-specific values are hardcoded here — end users supply their own
    # Foundry resource. If unset, the router serves recorded demo traces.
    try:
        from idun import config as _cfg

        cfg = _cfg.load_config().get("defaults", {}) or {}
    except Exception:
        cfg = {}
    COORDS = {
        "IDUN_BASE": cfg.get("idun_base"),
        "IDUN_PROJECT": cfg.get("idun_project"),
        "IDUN_AGENT": cfg.get("idun_agent"),
    }
    for k, v in COORDS.items():
        if v:
            os.environ.setdefault(k, str(v).strip())

    # Token from ~/foundry_token.txt if not already in env.
    if not os.environ.get("FOUNDRY_TOKEN") and os.path.exists(TOKEN_FILE):
        try:
            m = json.load(open(TOKEN_FILE))
            if m.get("access_token"):
                os.environ["FOUNDRY_TOKEN"] = m["access_token"]
        except Exception:
            pass

    # PORT is read by router.py at import time, so set it before importing.
    if os.environ.get("PORT"):
        os.environ["PORT"] = os.environ["PORT"]

    print(f"[run_router] IDUN_BASE={os.environ.get('IDUN_BASE')}")
    print(f"[run_router] IDUN_PROJECT={os.environ.get('IDUN_PROJECT')}")
    print(f"[run_router] token present={bool(os.environ.get('FOUNDRY_TOKEN'))}")

    # Import after env is set so router.py / idun.client see it.
    sys.path.insert(0, HERE)
    import router  # noqa: F401

    # router.py defines `main()`? Fall back to running its module __main__.
    if hasattr(router, "main"):
        router.main()
    else:
        # re-exec router as __main__ is not exposed; call its server directly
        router.run() if hasattr(router, "run") else None


if __name__ == "__main__":
    main()
