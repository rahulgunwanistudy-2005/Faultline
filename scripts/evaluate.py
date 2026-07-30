#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "faultline_core"))
sys.path.insert(0, str(ROOT / "apps" / "api"))

from faultline_api.services.demo import build_class_analysis  # noqa: E402


def main() -> None:
    analysis = build_class_analysis()
    students = analysis["students"]
    fixture = json.loads((ROOT / "data" / "demo_class.json").read_text())
    assigned = {student["student_id"]: student["assigned_procedure"] for student in fixture["students"]}
    rows = []
    correct_top = 0
    named = 0
    for student in students:
        predicted = student["diagnosis"]["hypothesis_id"]
        expected = assigned[student["student_id"]]
        top_match = predicted == expected
        correct_top += int(top_match)
        named += int(student["diagnosis"]["state"] == "named_diagnosis")
        rows.append(
            {
                "student_id": student["student_id"],
                "assigned_procedure": expected,
                "top_hypothesis": predicted,
                "top_match": top_match,
                "gate_state": student["diagnosis"]["state"],
                "posterior": student["diagnosis"]["posterior"],
                "ocr_confidence_percent": student["diagnosis"]["mean_ocr_confidence"],
            }
        )

    output = ROOT / "data" / "evaluation" / "fixture_results.csv"
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    report = f"""# Faultline Evaluation Snapshot

> **Dataset:** synthetic deterministic fixture. These results are regression evidence, not a classroom accuracy or learning-impact claim.

- Assigned-procedure top-rank identification: **{correct_top}/{len(students)}**
- Named-diagnosis coverage after confidence gating: **{named}/{len(students)}**
- Deliberate refusals: **{len(students) - named}**
- Held-out leakage: enforced by API test; prediction payload excludes actual answer
- Core and API tests: run `./scripts/verify_submission.sh`

## Metric separation

1. **Engine-on-exact-fixture:** the executable procedure receiving the highest posterior.
2. **Confidence coverage:** how often Faultline allows a named diagnosis.
3. **End-to-end handwriting accuracy:** not claimed yet; use the controlled-pilot protocol before reporting it.
4. **Learning impact:** not claimed; would require a real intervention study.
"""
    (ROOT / "docs" / "evaluation" / "evaluation_report.md").write_text(report)
    print(report)
    print(f"Wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
