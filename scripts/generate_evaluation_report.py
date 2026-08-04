#!/usr/bin/env python3
"""Aggregate the layered evaluation results into EVALUATION_CARD.md (Phase 7).

Runs the deterministic layers (Bayesian engine, neuro-symbolic proposals), reads
any local-AI transcription result already produced, and writes a reproducible
card that records base commit, working-tree fingerprint, timestamp, and clear
SYNTHETIC / PUBLIC / UNAVAILABLE labels per layer.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import evaluate_bayesian_engine
import evaluate_neuro_symbolic_proposals

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "data" / "evaluation" / "results"
CARD = ROOT / "docs" / "evaluation" / "EVALUATION_CARD.md"


def _base_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def _worktree_fingerprint() -> str:
    """Hash of `git diff` so the card records the exact working-tree state."""
    try:
        diff = subprocess.check_output(["git", "diff"], cwd=ROOT, text=True)
    except (subprocess.CalledProcessError, OSError):
        return "unknown"
    return hashlib.sha256(diff.encode("utf-8")).hexdigest()[:16]


def _load(name: str) -> dict | None:
    path = RESULTS_DIR / name
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    bayesian = evaluate_bayesian_engine.evaluate()
    (RESULTS_DIR / "bayesian_engine.json").write_text(
        json.dumps(bayesian, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    proposals = evaluate_neuro_symbolic_proposals.evaluate_proposals()
    (RESULTS_DIR / "neuro_symbolic_proposals.json").write_text(
        json.dumps(proposals, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    transcription = _load("local_ai_transcription.json")

    lines = [
        "# Faultline Evaluation Card",
        "",
        "> Layered, reproducible evaluation. Each layer is labelled SYNTHETIC, PUBLIC,",
        "> or UNAVAILABLE. Synthetic regression metrics are **not** classroom,",
        "> handwriting, or learning-impact results. Public transcription metrics do",
        "> **not** prove end-to-end diagnosis accuracy.",
        "",
        f"- Base commit: `{_base_commit()}`",
        f"- Working-tree diff fingerprint: `{_worktree_fingerprint()}`",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Layer A — Local vision transcription (PUBLIC HASYv2, transcription only)",
        "",
    ]
    if transcription is None:
        lines += [
            "_No result recorded._ Run with a local model:",
            "```bash",
            "FAULTLINE_RUNTIME_MODE=local_ai python scripts/evaluate_local_ai.py",
            "```",
        ]
    elif transcription.get("status") == "unavailable":
        lines += [f"**UNAVAILABLE** — {transcription['detail']}"]
    else:
        lines += [
            f"- Model: `{transcription['vision_model']}`",
            f"- Images: {transcription['samples']}",
            f"- Exact-symbol accuracy: **{transcription['exact_symbol_accuracy']:.0%}**",
            f"- Latency p50 / p95: {transcription['latency_ms_p50']} / {transcription['latency_ms_p95']} ms",
            "- Scope: single-symbol recognition, not end-to-end diagnosis.",
        ]

    lines += [
        "",
        "## Layer B — Deterministic Bayesian engine (SYNTHETIC fixture)",
        "",
        f"- Students: {bayesian['students']}",
        f"- Top-1 procedure accuracy: **{bayesian['top1_accuracy']:.0%}**",
        f"- Top-2 coverage: **{bayesian['top2_coverage']:.0%}**",
        f"- Named-diagnosis coverage: {bayesian['named_diagnosis_coverage']:.0%} "
        f"({bayesian['withheld']} withheld)",
        f"- Deterministic (identical inputs → identical posteriors): {bayesian['deterministic']}",
        f"- Prior mode: `{bayesian['prior_mode']}`",
        "",
        "## Layer C — End-to-end (image → procedure)",
        "",
        "**UNAVAILABLE by design.** The public HASYv2 subset is single symbols with no",
        "procedure-level ground truth, so no honest end-to-end accuracy can be reported.",
        "End-to-end behaviour is exercised structurally by the local-AI job integration",
        "tests (`apps/api/tests/test_local_ai_jobs.py`) with a mocked model.",
        "",
        "## Layer D — Neuro-symbolic proposals (CONTROLLED battery)",
        "",
        f"- Cases: {proposals['cases']}",
        f"- Valid-proposal rate: {proposals['valid_proposal_rate']:.0%}",
        f"- Acceptance rate: {proposals['acceptance_rate']:.0%}",
        f"- Unsafe rejections: {proposals['unsafe_rejections']}; "
        f"duplicate-known rejections: {proposals['duplicate_known_rejections']}",
        f"- Effect of an accepted proposal: top hypothesis "
        f"`{proposals['proposal_effect']['top_without_proposal']}` → "
        f"`{proposals['proposal_effect']['top_with_proposal']}`.",
        "",
        "## Reproduce",
        "",
        "```bash",
        "PYTHONPATH=packages/faultline_core:apps/api python scripts/generate_evaluation_report.py",
        "```",
        "",
    ]
    CARD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {CARD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
