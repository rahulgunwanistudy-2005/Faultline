# Faultline Evaluation Card

> Layered, reproducible evaluation. Each layer is labelled SYNTHETIC, PUBLIC,
> or UNAVAILABLE. Synthetic regression metrics are **not** classroom,
> handwriting, or learning-impact results. Public transcription metrics do
> **not** prove end-to-end diagnosis accuracy.

- Base commit: `defdbfdda1efa77cbfbb73e6672c96937ee48896`
- Working-tree diff fingerprint: `a6d52232fd6e1fa7`
- Generated: 2026-07-31T10:54:20.488792+00:00

## Layer A — Local vision transcription (PUBLIC HASYv2, transcription only)

**UNAVAILABLE** — runtime is not local_ai; set FAULTLINE_RUNTIME_MODE=local_ai

## Layer B — Deterministic Bayesian engine (SYNTHETIC fixture)

- Students: 12
- Top-1 procedure accuracy: **100%**
- Top-2 coverage: **100%**
- Named-diagnosis coverage: 100% (0 withheld)
- Deterministic (identical inputs → identical posteriors): True
- Prior mode: `uniform`

## Layer C — End-to-end (image → procedure)

**UNAVAILABLE by design.** The public HASYv2 subset is single symbols with no
procedure-level ground truth, so no honest end-to-end accuracy can be reported.
End-to-end behaviour is exercised structurally by the local-AI job integration
tests (`apps/api/tests/test_local_ai_jobs.py`) with a mocked model.

## Layer D — Neuro-symbolic proposals (CONTROLLED battery)

- Cases: 5
- Valid-proposal rate: 60%
- Acceptance rate: 20%
- Unsafe rejections: 2; duplicate-known rejections: 1
- Effect of an accepted proposal: top hypothesis `denominator_only_common` → `proposed_1`.

## Reproduce

```bash
PYTHONPATH=packages/faultline_core:apps/api python scripts/generate_evaluation_report.py
```

