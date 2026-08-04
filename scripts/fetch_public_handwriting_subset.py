#!/usr/bin/env python3
"""Reproducibly fetch a small licensed handwritten-symbol subset for evaluation.

Source: **HASYv2** (Martin Thoma), 168k handwritten mathematical symbols,
published on Zenodo under the **ODC Open Database License v1.0 (ODbL)**.
DOI: 10.5281/zenodo.259444

This script downloads the single official archive, verifies its MD5, extracts a
small deterministic subset (25-30 images) of *fraction-relevant* symbol classes
(digits, ``+ - = /``), records provenance + checksums, and deletes the archive.
It is transcription-only ground truth: single symbols, not full worksheets.

Safety:
* only the allowlisted Zenodo host/URL is contacted (HTTPS);
* bounded download size + timeout;
* archive MD5 pinned and verified;
* tar extraction guards against path traversal and non-PNG members;
* no executables are written; the run is idempotent.

Usage::

    python scripts/fetch_public_handwriting_subset.py           # fetch subset
    python scripts/fetch_public_handwriting_subset.py --check    # verify checksums only
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import ssl
import sys
import tarfile
import tempfile
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "evaluation" / "public_handwriting_subset"
IMAGES = DEST / "images"

ALLOWED_URL = "https://zenodo.org/records/259444/files/HASYv2.tar.bz2?download=1"
ALLOWED_HOST = "zenodo.org"
EXPECTED_MD5 = "fddf23f36e24b5236f6b3a0880c778e3"
MAX_DOWNLOAD_BYTES = 80 * 1024 * 1024  # HASYv2 is ~34.6 MB; cap generously.
CONNECT_TIMEOUT = 30
SUBSET_SIZE = 28
PER_CLASS = 4
# Fraction-relevant symbol classes (LaTeX as labelled in HASYv2).
TARGET_LATEX = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "=", "/")

LICENSE_NAME = "ODC Open Database License v1.0 (ODbL)"
ATTRIBUTION = "HASYv2 dataset, Martin Thoma (2017), DOI:10.5281/zenodo.259444"


def _tls_context() -> ssl.SSLContext:
    """A verifying TLS context. Falls back to certifi's CA bundle when the system
    trust store is unavailable (e.g. a Python build without installed certs).
    Verification is never disabled."""
    context = ssl.create_default_context()
    if context.cert_store_stats().get("x509_ca", 0) == 0:
        try:
            import certifi

            context = ssl.create_default_context(cafile=certifi.where())
        except ImportError:  # pragma: no cover - certifi ships with httpx
            pass
    return context


def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _download() -> bytes:
    from urllib.parse import urlparse

    if urlparse(ALLOWED_URL).hostname != ALLOWED_HOST:
        raise SystemExit(f"refusing non-allowlisted host: {ALLOWED_URL}")
    print(f"Downloading HASYv2 archive from {ALLOWED_HOST} (~34.6 MB)…")
    request = urllib.request.Request(ALLOWED_URL, headers={"User-Agent": "faultline-eval-fetch"})
    context = _tls_context()  # always verifies; never disabled
    with urllib.request.urlopen(request, timeout=CONNECT_TIMEOUT, context=context) as response:  # noqa: S310 - allowlisted HTTPS
        buffer = io.BytesIO()
        while True:
            chunk = response.read(1024 * 256)
            if not chunk:
                break
            buffer.write(chunk)
            if buffer.tell() > MAX_DOWNLOAD_BYTES:
                raise SystemExit("archive exceeded the maximum allowed download size")
        data = buffer.getvalue()
    digest = _md5(data)
    if digest != EXPECTED_MD5:
        raise SystemExit(f"archive MD5 mismatch: expected {EXPECTED_MD5}, got {digest}")
    print(f"Archive verified (MD5 {digest}, {len(data) // (1024 * 1024)} MB).")
    return data


def _safe_members(tar: tarfile.TarFile):
    for member in tar.getmembers():
        name = member.name
        if member.isdir():
            continue
        if name.startswith("/") or ".." in Path(name).parts:
            continue  # path traversal guard
        if member.issym() or member.islnk():
            continue
        yield member


def _extract_subset(archive: bytes) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:bz2") as tar:
            members = {member.name: member for member in _safe_members(tar)}
            labels_name = next(
                (name for name in members if name.endswith("hasy-data-labels.csv")), None
            )
            if labels_name is None:
                raise SystemExit("could not find hasy-data-labels.csv in the archive")
            labels_text = tar.extractfile(members[labels_name]).read().decode("utf-8")
            rows = list(csv.DictReader(io.StringIO(labels_text)))

            selected = _select_rows(rows)
            IMAGES.mkdir(parents=True, exist_ok=True)
            records: list[dict] = []
            for index, row in enumerate(selected):
                member = _resolve_image_member(members, row["path"])
                if member is None:
                    continue
                image_bytes = tar.extractfile(member).read()
                if not image_bytes.startswith(b"\x89PNG"):
                    continue  # only real PNGs
                sample_id = f"hasy_{index:03d}"
                out_path = IMAGES / f"{sample_id}.png"
                out_path.write_bytes(image_bytes)
                records.append(
                    {
                        "sample_id": sample_id,
                        "source_sample_id": row["path"],
                        "image_path": str(out_path.relative_to(DEST)),
                        "expected_symbol": row["latex"],
                        "sha256": _sha256(image_bytes),
                        "source_user_id": row.get("user_id", ""),
                    }
                )
            return records


def _select_rows(rows: list[dict]) -> list[dict]:
    by_class: dict[str, list[dict]] = {latex: [] for latex in TARGET_LATEX}
    for row in rows:
        latex = row.get("latex", "")
        if latex in by_class and len(by_class[latex]) < PER_CLASS:
            by_class[latex].append(row)
    selected: list[dict] = []
    for latex in TARGET_LATEX:
        selected.extend(by_class[latex])
        if len(selected) >= SUBSET_SIZE:
            break
    return selected[:SUBSET_SIZE]


def _resolve_image_member(members: dict, rel_path: str):
    target = Path(rel_path).name
    for name, member in members.items():
        if Path(name).name == target:
            return member
    return None


def _write_metadata(records: list[dict]) -> None:
    with (DEST / "labels.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "sample_id",
                "source_sample_id",
                "image_path",
                "expected_visible_expression",
                "expected_final_answer",
                "expected_intermediate_lines",
                "expected_step_features",
                "expected_symbol",
                "usable_for_transcription",
                "usable_for_end_to_end_diagnosis",
                "license_reference",
                "sha256",
            ]
        )
        for record in records:
            writer.writerow(
                [
                    record["sample_id"],
                    record["source_sample_id"],
                    record["image_path"],
                    "",  # single symbols: no full expression
                    "",
                    "",
                    "",
                    record["expected_symbol"],
                    "true",
                    "false",
                    LICENSE_NAME,
                    record["sha256"],
                ]
            )
    provenance = {
        "dataset_name": "HASYv2",
        "version": "v2",
        "source_url": ALLOWED_URL,
        "doi": "10.5281/zenodo.259444",
        "license": LICENSE_NAME,
        "attribution": ATTRIBUTION,
        "attribution_required": True,
        "redistribution": "permitted with attribution + share-alike (ODbL); excluded from the public release ZIP to avoid mis-licensing",
        "retrieval_date": date.today().isoformat(),
        "archive_md5": EXPECTED_MD5,
        "selection_criteria": (
            f"first {PER_CLASS} instances of each fraction-relevant symbol class "
            f"{list(TARGET_LATEX)}, capped at {SUBSET_SIZE} images, deterministic order"
        ),
        "image_count": len(records),
        "contains_real_student_information": False,
        "pii_note": "Only a pseudonymous integer user_id is present; no names, faces, or school identifiers.",
        "usable_for_transcription": True,
        "usable_for_end_to_end_diagnosis": False,
        "images": [
            {"sample_id": r["sample_id"], "sha256": r["sha256"], "expected_symbol": r["expected_symbol"]}
            for r in records
        ],
    }
    (DEST / "provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def check() -> int:
    provenance_path = DEST / "provenance.json"
    if not provenance_path.exists():
        print("dataset not fetched yet; run without --check", file=sys.stderr)
        return 1
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    problems = []
    for entry in provenance["images"]:
        image_path = IMAGES / f"{entry['sample_id']}.png"
        if not image_path.exists():
            problems.append(f"missing image: {entry['sample_id']}")
            continue
        digest = _sha256(image_path.read_bytes())
        if digest != entry["sha256"]:
            problems.append(f"checksum mismatch: {entry['sample_id']}")
    if problems:
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print(f"Dataset OK: {len(provenance['images'])} images, checksums verified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch the licensed HASYv2 evaluation subset")
    parser.add_argument("--check", action="store_true", help="verify existing checksums only")
    args = parser.parse_args()
    if args.check:
        return check()

    print(f"License: {LICENSE_NAME}\nAttribution: {ATTRIBUTION}")
    archive = _download()
    records = _extract_subset(archive)
    if not (25 <= len(records) <= 30):
        raise SystemExit(f"expected 25-30 images, selected {len(records)}")
    _write_metadata(records)
    print(f"Wrote {len(records)} images + provenance to {DEST.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
