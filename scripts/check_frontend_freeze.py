#!/usr/bin/env python3
"""Frontend freeze guard.

The competition frontend under ``apps/web-static/`` is considered frozen and
already approved. This script records a SHA-256 manifest of every frontend file
and verifies the working tree against it. The release must fail if any frontend
file changes unintentionally.

Usage::

    python scripts/check_frontend_freeze.py           # verify against manifest
    python scripts/check_frontend_freeze.py --write    # regenerate the manifest

The ``--write`` mode is intentionally manual: it exists so a deliberate,
reviewed frontend change can be re-baselined. Verification (the default) is what
the release gate runs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = ROOT / "apps" / "web-static"
MANIFEST = ROOT / "FRONTEND_MANIFEST.json"
SKIP_NAMES = {".DS_Store"}


def _frontend_files() -> list[Path]:
    return sorted(
        path
        for path in FRONTEND_ROOT.rglob("*")
        if path.is_file() and path.name not in SKIP_NAMES
    )


def compute() -> dict:
    files = []
    for path in _frontend_files():
        content = path.read_bytes()
        files.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return {
        "schema": 1,
        "note": "Frozen competition frontend. Verified byte-for-byte by scripts/check_frontend_freeze.py.",
        "root": FRONTEND_ROOT.relative_to(ROOT).as_posix(),
        "file_count": len(files),
        "files": files,
    }


def _rendered() -> str:
    return json.dumps(compute(), indent=2, ensure_ascii=False) + "\n"


def _load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def verify() -> int:
    if not MANIFEST.exists():
        print(
            "FRONTEND_MANIFEST.json is missing; run scripts/check_frontend_freeze.py --write",
            file=sys.stderr,
        )
        return 1
    expected = {entry["path"]: entry for entry in _load_manifest()["files"]}
    actual = {entry["path"]: entry for entry in compute()["files"]}

    problems: list[str] = []
    for path in sorted(set(expected) | set(actual)):
        if path not in actual:
            problems.append(f"missing frontend file: {path}")
        elif path not in expected:
            problems.append(f"unexpected new frontend file: {path}")
        elif expected[path]["sha256"] != actual[path]["sha256"]:
            problems.append(f"frontend file changed: {path}")

    if problems:
        print("Frontend freeze verification FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        print(
            "\nThe frontend is frozen. If this change is intentional and reviewed, "
            "re-baseline with: python scripts/check_frontend_freeze.py --write",
            file=sys.stderr,
        )
        return 1
    print(f"Frontend freeze verified: {len(actual)} files unchanged.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify or regenerate the frozen frontend manifest")
    parser.add_argument("--write", action="store_true", help="regenerate FRONTEND_MANIFEST.json")
    args = parser.parse_args()
    if args.write:
        MANIFEST.write_text(_rendered(), encoding="utf-8")
        print(f"Wrote {MANIFEST.relative_to(ROOT)} with {compute()['file_count']} frontend files.")
        return 0
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
