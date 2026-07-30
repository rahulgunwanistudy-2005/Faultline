#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "faultline_core"))
sys.path.insert(0, str(ROOT / "apps" / "api"))

from faultline_api.services.demo import build_class_analysis  # noqa: E402

OUTPUT = ROOT / "apps" / "web-static" / "assets" / "demo-class.js"


def rendered_asset() -> str:
    payload = build_class_analysis()
    text = "window.__FAULTLINE_DEMO__ = " + json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False,
    ) + ";\n"
    if "actual_answer" in text or "predicted_answer" in text:
        raise RuntimeError("Public demo asset contains held-out answer material")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the sanitized static demo fixture")
    parser.add_argument("--check", action="store_true", help="fail if the committed asset is stale")
    args = parser.parse_args()
    expected = rendered_asset()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("Static demo asset is stale; run scripts/generate_demo_asset.py", file=sys.stderr)
            return 1
        print("Static demo asset is current and contains no held-out answers.")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
