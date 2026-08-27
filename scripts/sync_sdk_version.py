#!/usr/bin/env python3
"""Keep the playground's advertised SDK version in sync with the installed
idun-sdk (P4, IGNITE prep).

Reads idun.__version__ from the active environment and rewrites the version
string in:
  - index.html       (idun-sdk vX.Y.Z)
  - ignite.html      (idun-sdk (vX.Y.Z)  +  SDK vX.Y.Z)
  - setup.py         (idun-sdk>=X.Y.Z)
  - requirements.txt (idun-sdk>=X.Y.Z)

This prevents the drift that left the playground pinned at >=0.1.21 while the
site advertised v1.0.32 against an actually-released v1.0.34.

Usage:
    python scripts/sync_sdk_version.py          # rewrite to installed idun
    python scripts/sync_sdk_version.py 1.0.34    # force a specific version
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _target_version() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    import idun
    return idun.__version__


def _rewrite(path: str, patterns):
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        print(f"  skip (missing): {path}")
        return
    with open(p, encoding="utf-8") as fh:
        s = fh.read()
    orig = s
    for rx, repl in patterns:
        s = re.sub(rx, repl, s)
    if s != orig:
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(s)
        print(f"  updated: {path}")
    else:
        print(f"  unchanged: {path}")


def main() -> int:
    ver = _target_version()
    print(f"Syncing playground to idun-sdk {ver}")
    _rewrite("index.html", [(r"idun-sdk v\d+\.\d+\.\d+", f"idun-sdk v{ver}")])
    _rewrite("ignite.html", [
        (r"idun-sdk</strong> \(v\d+\.\d+\.\d+\)", f"idun-sdk</strong> (v{ver})"),
        (r"SDK v\d+\.\d+\.\d+", f"SDK v{ver}"),
    ])
    _rewrite("setup.py", [(r"idun-sdk>=\d+\.\d+\.\d+", f"idun-sdk>={ver}")])
    _rewrite("requirements.txt", [(r"idun-sdk>=\d+\.\d+\.\d+", f"idun-sdk>={ver}")])
    print("Done. Review the diff and commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
