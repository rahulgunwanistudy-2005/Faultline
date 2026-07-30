#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = (ROOT / "apps", ROOT / "packages", ROOT / "scripts", ROOT / ".github")
TEXT_SUFFIXES = {".py", ".js", ".html", ".css", ".sh", ".yaml", ".yml", ".json", ".toml"}
SKIP_PARTS = {"__pycache__", ".pytest_cache", "node_modules", ".venv", "venv", "dist", "build"}

CHECKS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "hardcoded credential-like assignment",
        re.compile(
            r"(?i)(?:api[_-]?key|password|private[_-]?key)\s*[=:]\s*[\"'][^\"'\s]{12,}[\"']"
        ),
    ),
    ("debugger or breakpoint", re.compile(r"\bpdb\.set_trace\b|\bbreakpoint\(\)|\bdebugger;")),
    ("bare exception", re.compile(r"^\s*except\s*:\s*$", re.MULTILINE)),
    ("silent exception", re.compile(r"except\s+[^:\n]+:\s*pass\b")),
    ("personal absolute path", re.compile(r"/(?:Users|home)/[A-Za-z0-9_-]+/|[A-Z]:\\Users\\")),
    ("disabled TLS verification", re.compile(r"verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED|rejectUnauthorized\s*:\s*false")),
    ("dynamic Python execution", re.compile(r"\b(?:eval|exec)\s*\(")),
    ("unsafe subprocess shell", re.compile(r"subprocess\.[A-Za-z_]+\([^\n]*shell\s*=\s*True")),
    ("pickle load", re.compile(r"\bpickle\.loads?\s*\(")),
)


def source_files() -> list[Path]:
    output: list[Path] = []
    for base in SOURCE_ROOTS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if SKIP_PARTS.intersection(path.parts):
                continue
            output.append(path)
    return sorted(output)


def main() -> int:
    findings: list[str] = []
    for path in source_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in CHECKS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{path.relative_to(ROOT)}:{line}: {label}")

    public_asset = ROOT / "apps/web-static/assets/demo-class.js"
    if public_asset.exists():
        text = public_asset.read_text(encoding="utf-8")
        for forbidden in ("actual_answer", "predicted_answer"):
            if forbidden in text:
                findings.append(f"{public_asset.relative_to(ROOT)}: public held-out field: {forbidden}")

    if findings:
        print("Surface audit failed:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print(f"Surface audit passed across {len(source_files())} runtime/config source files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
