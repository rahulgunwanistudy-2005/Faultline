# Project Status — Faultline v0.3.0 (neuro-symbolic Bayesian)

Honest snapshot of what is implemented and verified. No claim of a perfect score,
perfect recognition, or classroom impact.

## Test + gate status

- **146 automated tests pass** (54 core, 81 API, 11 top-level).
- `./scripts/verify_submission.sh` gates all pass in the `.venv` (Python 3.13):
  compile/audit, JS syntax, frontend freeze, generated-asset integrity, tests,
  dependency consistency, fixture + Bayesian + neuro-symbolic evaluation, dataset
  checksums, live smoke test, and release manifest.
- Frontend under `apps/web-static/` is **byte-for-byte frozen**
  (`FRONTEND_MANIFEST.json`, `scripts/check_frontend_freeze.py`).

## Implemented in this upgrade

| Area | Status |
|---|---|
| Explicit runtime modes (`fixture` default, `local_ai` opt-in) | Done — no silent fallback |
| Validated model config (range-checked) + host allowlist | Done |
| Local Ollama client (bounded, typed errors, loopback-only) | Done |
| Runtime + model-health endpoints (`/v1/runtime`, `/v1/models/health`) | Done |
| Local vision transcription + preprocessing views | Done |
| Deterministic reading-consensus (engineering support, not model confidence) | Done |
| Neuro-symbolic hypothesis proposal (bounded, gated) | Done |
| Deterministic Bayesian engine (priors/likelihood/marginalization/abstention) | Done |
| Verifier-gated novel hypotheses (fit/validation/novelty/complexity) | Done |
| Local-AI job pipeline with real state machine + single-student analysis | Done |
| Signed held-out proof on real uploads (leave-one-out) | Done |
| Licensed public handwriting subset (HASYv2, ODbL, 28 images, no PII) | Done |
| Layered evaluation (Bayesian / proposals real; transcription + E2E honest) | Done |
| Setup + release automation (`setup_local_ai.sh`, `release.sh`, `check_local_model.py`) | Done |

## Preserved from v0.2.0 (not regressed)

Signed/expiring/student-bound held-out proof; bounded raw-body uploads; image
verification + decompression-bomb limits; process-local bounded jobs + rate
limits; security headers; metadata-only logging; strict correction schemas;
same-origin default; exact dependency pins.

## Known limitations / blocked items

- No verified handwriting accuracy; small local VLMs vary with handwriting.
- End-to-end image→procedure accuracy is not measured on public data (no labelled
  public set exists); it is exercised structurally with a mocked model.
- The local-AI pipeline runs synchronously within the request in this
  single-worker demo (real stages, not time-based simulation); a scaled
  deployment would use a task queue.
- Not production-ready for identifiable student data.

## Git

All work is left **unstaged** for manual review. No commits, branches, tags, or
history changes were made by the assistant. Per the human-owned Git constraint,
the assistant stayed on the checked-out branch and did **not** create the
`feature/neuro-symbolic-bayesian-ai` branch the original prompt suggested.
