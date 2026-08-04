#!/usr/bin/env python3
"""Neuro-symbolic proposal evaluation (Phase 7, layer D).

A controlled battery of symbolic proposals is run through the deterministic
verifier to measure valid-proposal, acceptance, duplicate-rejection, and
unsafe-rejection rates, plus the effect of adding an accepted proposal to the
Bayesian candidate set. Deterministic and reproducible.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from faultline_core import (
    FractionProblem,
    HYPOTHESIS_MAP,
    Observation,
    ProvisionalCandidate,
    SynthesisExample,
    build_candidate_set,
    evaluate,
    infer_bayesian,
    verify_symbolic_hypothesis,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "data" / "evaluation" / "results"

ADD_ACROSS = {
    "op": "fraction",
    "args": [
        {"op": "add", "args": [{"var": "n1"}, {"var": "n2"}]},
        {"op": "add", "args": [{"var": "d1"}, {"var": "d2"}]},
    ],
}
NOVEL_ADD_MUL = {
    "op": "fraction",
    "args": [
        {"op": "add", "args": [{"var": "n1"}, {"var": "n2"}]},
        {"op": "mul", "args": [{"var": "d1"}, {"var": "d2"}]},
    ],
}
UNSAFE_CODE = {"op": "exec", "args": [1, 2]}
STRING_LOGIC = {"op": "add", "args": ["n1", "n2"]}


def _problems() -> list[FractionProblem]:
    return [
        FractionProblem("p1", 1, 2, 1, 3),
        FractionProblem("p2", 2, 3, 1, 4),
        FractionProblem("p3", 3, 5, 1, 2),
        FractionProblem("p4", 1, 4, 2, 3),
        FractionProblem("p5", 2, 5, 3, 7),
        FractionProblem("p6", 3, 8, 1, 6),
    ]


def _examples(expression) -> list[SynthesisExample]:
    return [
        SynthesisExample(p, evaluate(expression, {"n1": p.n1, "d1": p.d1, "n2": p.n2, "d2": p.d2}))
        for p in _problems()
    ]


def _base_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def evaluate_proposals() -> dict:
    # (label, expression, ground-truth examples, expected outcome)
    battery = [
        ("valid_novel", NOVEL_ADD_MUL, _examples(NOVEL_ADD_MUL), "accept"),
        ("duplicate_known", ADD_ACROSS, _examples(ADD_ACROSS), "reject_duplicate"),
        ("unsafe_code", UNSAFE_CODE, _examples(NOVEL_ADD_MUL), "reject_unsafe"),
        ("string_logic", STRING_LOGIC, _examples(NOVEL_ADD_MUL), "reject_unsafe"),
        ("poor_fit", NOVEL_ADD_MUL, _examples(ADD_ACROSS), "reject_fit"),
    ]
    outcomes = []
    accepted = valid = duplicate_rejected = unsafe_rejected = 0
    for label, expression, examples, expected in battery:
        result = verify_symbolic_hypothesis("proposal", expression, examples)
        is_valid = not (result.reason or "").startswith("invalid_dsl")
        valid += int(is_valid)
        accepted += int(result.accepted)
        if (result.reason or "").startswith("duplicate_of_known"):
            duplicate_rejected += 1
        if (result.reason or "").startswith("invalid_dsl"):
            unsafe_rejected += 1
        outcomes.append(
            {
                "case": label,
                "expected": expected,
                "accepted": result.accepted,
                "reason": result.reason,
                "reproduction": result.reproduction,
                "validation_reproduction": result.validation_reproduction,
            }
        )

    # Effect of adding an accepted proposal to the Bayesian candidate set:
    # a student whose work follows the novel rule should now be diagnosed.
    novel_observations = [
        Observation.exact(p, evaluate(NOVEL_ADD_MUL, {"n1": p.n1, "d1": p.d1, "n2": p.n2, "d2": p.d2}), 0.97)
        for p in _problems()
    ]
    without = infer_bayesian(novel_observations)
    provisional = [ProvisionalCandidate("proposed_1", "add tops, mul bottoms", NOVEL_ADD_MUL)]
    with_proposal = infer_bayesian(novel_observations, build_candidate_set(provisional))

    return {
        "layer": "D_neuro_symbolic_proposals",
        "data_label": "CONTROLLED symbolic battery (deterministic)",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_commit": _base_commit(),
        "cases": len(battery),
        "valid_proposal_rate": round(valid / len(battery), 4),
        "acceptance_rate": round(accepted / len(battery), 4),
        "duplicate_known_rejections": duplicate_rejected,
        "unsafe_rejections": unsafe_rejected,
        "outcomes": outcomes,
        "proposal_effect": {
            "top_without_proposal": without.top_hypothesis,
            "state_without_proposal": without.state,
            "top_with_proposal": with_proposal.top_hypothesis,
            "state_with_proposal": with_proposal.state,
            "note": "Adding the verifier-accepted novel rule lets the engine explain "
            "work that no known procedure reproduced.",
        },
        "reproduce": "PYTHONPATH=packages/faultline_core python scripts/evaluate_neuro_symbolic_proposals.py",
    }


def main() -> int:
    report = evaluate_proposals()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / "neuro_symbolic_proposals.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    effect = report["proposal_effect"]
    print(
        f"Proposals: valid {report['valid_proposal_rate']:.0%}, accept {report['acceptance_rate']:.0%}, "
        f"unsafe rejected {report['unsafe_rejections']}, duplicate rejected {report['duplicate_known_rejections']}"
    )
    print(
        f"Effect: without proposal top={effect['top_without_proposal']} "
        f"→ with proposal top={effect['top_with_proposal']}"
    )
    print(f"Wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
