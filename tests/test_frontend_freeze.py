"""Frontend freeze regression test.

The competition frontend under ``apps/web-static/`` is frozen. These tests fail
if any frontend file changes, is added, or is removed relative to the recorded
``FRONTEND_MANIFEST.json``. They also assert that the public static assets never
contain held-out answers.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_frontend_freeze as freeze  # noqa: E402


def _manifest() -> dict:
    path = ROOT / "FRONTEND_MANIFEST.json"
    assert path.exists(), "FRONTEND_MANIFEST.json is missing"
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_lists_every_frontend_file() -> None:
    recorded = {entry["path"] for entry in _manifest()["files"]}
    on_disk = {
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "apps" / "web-static").rglob("*")
        if p.is_file() and p.name not in freeze.SKIP_NAMES
    }
    assert recorded == on_disk, f"manifest/disk mismatch: {recorded ^ on_disk}"


def test_every_frontend_hash_matches() -> None:
    for entry in _manifest()["files"]:
        content = (ROOT / entry["path"]).read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        assert digest == entry["sha256"], f"frontend file changed: {entry['path']}"


def test_freeze_checker_passes() -> None:
    assert freeze.verify() == 0


@pytest.mark.parametrize("forbidden", ["actual_answer", "predicted_answer"])
def test_bundled_demo_data_asset_has_no_held_out_answers(forbidden: str) -> None:
    """The bundled fallback *data* asset must never embed held-out answers.

    ``app.js`` legitimately references these field names because it reads them
    from the authenticated reveal response, so only the pre-baked data asset is
    checked here (mirroring scripts/audit_surface.py).
    """
    asset = ROOT / "apps" / "web-static" / "assets" / "demo-class.js"
    text = asset.read_text(encoding="utf-8")
    assert forbidden not in text, f"{asset} leaks {forbidden}"
