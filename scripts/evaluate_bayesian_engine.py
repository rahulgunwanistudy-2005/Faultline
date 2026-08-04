#!/usr/bin/env python3
"""Deterministic Bayesian engine evaluation (Phase 7, layer B).

Runs the explicit Bayesian engine over the **synthetic** 12-student fixture using
exact structured evidence and reports top-1 / top-2 procedure accuracy, a
confusion matrix, named-diagnosis coverage, abstention reasons, and determinism.

These are labelled SYNTHETIC regression metrics — not classroom, handwriting, or
learning-impact results.
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from faultline_core import (
    BayesianParams,
    FractionProblem,
    Observation,
    infer_bayesian,
    parse_fraction,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data" / "demo_class.json"
RESULTS_DIR = ROOT / "data" / "evaluation" / "results"


def _problems(data: dict) -> dict[str, FractionProblem]:
    return {
        raw["id"]: FractionProblem(
            id=raw["id"], n1=raw["n1"], d1=raw["d1"], n2=raw["n2"], d2=raw["d2"],
            operation=raw.get("operation", "+"), form=raw.get("form", "bare"),
        )
        for raw in data["problems"]
    }


def _observations(student: dict, problems: dict[str, FractionProblem]) -> list[Observation]:
    observations = []
    for item in student["observations"]:
        if item.get("held_out"):
            continue
        observations.append(
            Observation.exact(
                problems[item["problem_id"]],
                parse_fraction(item["answer"]),
                item["ocr_confidence"],
                item.get("step_features", ()),
            )
        )
    return observations


def _base_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def evaluate() -> dict:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    problems = _problems(data)
    params = BayesianParams()

    top1 = top2 = named = 0
    confusion: dict[str, Counter] = defaultdict(Counter)
    reason_counts: Counter = Counter()
    per_student = []

    for student in data["students"]:
        observations = _observations(student, problems)
        result = infer_bayesian(observations, params=params)
        assigned = student["assigned_procedure"]
        top_ids = [hid for hid, _ in result.ranked[:2]]
        is_top1 = result.top_hypothesis == assigned
        is_top2 = assigned in top_ids
        top1 += int(is_top1)
        top2 += int(is_top2)
        named += int(result.state == "named_diagnosis")
        confusion[assigned][result.top_hypothesis] += 1
        for reason in result.reasons:
            reason_counts[reason] += 1
        per_student.append(
            {
                "student_id": student["student_id"],
                "assigned": assigned,
                "top_hypothesis": result.top_hypothesis,
                "top_posterior": round(result.top_posterior, 4),
                "state": result.state,
                "entropy_bits": round(result.entropy_bits, 4),
                "top_two_margin": round(result.top_two_margin, 4),
                "reasons": result.reasons,
            }
        )

    total = len(data["students"])
    # Determinism check: re-run and compare posteriors.
    deterministic = all(
        infer_bayesian(_observations(s, problems), params=params).posterior
        == infer_bayesian(_observations(s, problems), params=params).posterior
        for s in data["students"]
    )

    return {
        "layer": "B_deterministic_bayesian_engine",
        "data_label": "SYNTHETIC regression fixture (data/demo_class.json)",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_commit": _base_commit(),
        "prior_mode": params.prior_mode,
        "config": {
            "answer_match_probability": params.likelihood.answer_match_probability,
            "answer_mismatch_probability": params.likelihood.answer_mismatch_probability,
            "abstention_entropy_threshold": params.abstention_entropy_threshold,
            "top_two_margin_threshold": params.top_two_margin_threshold,
        },
        "students": total,
        "top1_accuracy": round(top1 / total, 4),
        "top2_coverage": round(top2 / total, 4),
        "named_diagnosis_coverage": round(named / total, 4),
        "withheld": total - named,
        "abstention_reasons": dict(reason_counts),
        "confusion_matrix": {k: dict(v) for k, v in confusion.items()},
        "deterministic": deterministic,
        "per_student": per_student,
        "reproduce": "PYTHONPATH=packages/faultline_core python scripts/evaluate_bayesian_engine.py",
    }


def main() -> int:
    report = evaluate()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / "bayesian_engine.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"Bayesian engine (SYNTHETIC): top-1 {report['top1_accuracy']:.0%}, "
        f"top-2 {report['top2_coverage']:.0%}, named {report['named_diagnosis_coverage']:.0%}, "
        f"deterministic={report['deterministic']}"
    )
    print(f"Wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
