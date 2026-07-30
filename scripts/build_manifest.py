#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "MANIFEST.json"
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules", "dist", "build", ".next"}
SKIP_NAMES = {"MANIFEST.json", ".DS_Store"}


def payload() -> dict:
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or SKIP_PARTS.intersection(path.parts) or path.name in SKIP_NAMES:
            continue
        relative = path.relative_to(ROOT).as_posix()
        content = path.read_bytes()
        files.append(
            {
                "path": relative,
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return {"schema": 1, "release": "0.2.0", "file_count": len(files), "files": files}


def rendered() -> str:
    return json.dumps(payload(), indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify the deterministic release manifest")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = rendered()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("Release manifest is stale; run scripts/build_manifest.py", file=sys.stderr)
            return 1
        print(f"Release manifest is current ({payload()['file_count']} files).")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {payload()['file_count']} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
