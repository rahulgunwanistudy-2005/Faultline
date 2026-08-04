"""Dataset provenance, licensing, PII, and checksum tests (Phase 2/9).

Skips cleanly with a clear reason when the subset has not been fetched.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "evaluation" / "public_handwriting_subset"
PROVENANCE = DEST / "provenance.json"

pytestmark = pytest.mark.skipif(
    not PROVENANCE.exists(),
    reason="handwriting subset not fetched; run scripts/fetch_public_handwriting_subset.py",
)


def _provenance() -> dict:
    return json.loads(PROVENANCE.read_text(encoding="utf-8"))


def test_image_count_between_25_and_30() -> None:
    provenance = _provenance()
    assert 25 <= provenance["image_count"] <= 30
    images = list((DEST / "images").glob("*.png"))
    assert 25 <= len(images) <= 30


def test_license_and_attribution_recorded() -> None:
    provenance = _provenance()
    assert "ODbL" in provenance["license"] or "ODC Open Database" in provenance["license"]
    assert provenance["attribution"]
    assert provenance["source_url"].startswith("https://zenodo.org/")


def test_no_pii_declared() -> None:
    provenance = _provenance()
    assert provenance["contains_real_student_information"] is False
    assert "pii_note" in provenance


def test_transcription_only_scope() -> None:
    provenance = _provenance()
    assert provenance["usable_for_transcription"] is True
    assert provenance["usable_for_end_to_end_diagnosis"] is False


def test_every_image_checksum_matches() -> None:
    provenance = _provenance()
    for entry in provenance["images"]:
        image = DEST / "images" / f"{entry['sample_id']}.png"
        assert image.exists(), entry["sample_id"]
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        assert digest == entry["sha256"], entry["sample_id"]


def test_labels_csv_has_required_columns() -> None:
    with (DEST / "labels.csv").open(encoding="utf-8") as handle:
        header = next(csv.reader(handle))
    required = {
        "sample_id",
        "source_sample_id",
        "image_path",
        "expected_symbol",
        "usable_for_transcription",
        "usable_for_end_to_end_diagnosis",
        "license_reference",
        "sha256",
    }
    assert required <= set(header)
