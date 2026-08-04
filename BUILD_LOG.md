# Build Log — v0.2.0 → v0.3.0 neuro-symbolic Bayesian upgrade

Phases executed in-session. All work left unstaged for manual commit.

| Phase | Work | Verification |
|---|---|---|
| 0 | Baseline audit; frontend freeze (`check_frontend_freeze.py`, `FRONTEND_MANIFEST.json`); upgrade plan + target-architecture docs | 38 tests; freeze verified |
| 1 | Runtime modes + range-checked config; Ollama client; model-health service; `/v1/runtime`, `/v1/models/health` | +26 tests (mocked transport) |
| 5 | Deterministic Bayesian engine (`priors.py`, `likelihood.py`, `hypothesis_set.py`, `bayesian.py`) | +25 core tests |
| 6 | Verifier-gated novelty (`novelty.py`, `verify_symbolic_hypothesis`) | +15 core tests |
| 3 | Local vision transcription + preprocessing views; reading consensus | +14 tests |
| 4 | Neuro-symbolic hypothesis generation (bounded, gated) | +9 tests |
| 8 | Local-AI job pipeline + state machine; single-student analysis; upload-backed signed proof; API compatibility snapshot | +15 tests |
| 2 | HASYv2 subset fetch (ODbL, 28 images, MD5-verified, no PII) + provenance | +6 tests |
| 7 | Layered evaluation scripts + EVALUATION_CARD + MODEL_CARD | Bayesian top-1 100% (synthetic), deterministic |
| 9 | Model-boundary security tests (injection, logging, host lock) | +7 tests |
| 10 | `setup_local_ai.sh`, `check_local_model.py`, `release.sh`; improved `start.sh` | scripts executable |
| 11 | Expanded read-only verify gate to 12 checks incl. freeze + dataset + eval | verify green (pre-manifest) |
| 12 | AI_ML_PROOF, architecture + privacy docs, README, status/quality/build/test records | — |
| 13 | Red-team sweep, manifest rebuild, final report | see PROJECT_QUALITY_AUDIT.md |

## Environment note

`scripts/verify_submission.sh` runs bare `python`. The verified runtime/test venv
is `.venv` (Python 3.13) with the pinned dependencies. Activate it before running
gates: `source .venv/bin/activate`.

## Test growth

v0.2.0 baseline: 33 tests → v0.3.0: **146 tests**.
