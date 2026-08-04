# Baseline record — Faultline v0.2.0

Recorded at the start of the neuro-symbolic Bayesian upgrade. This is the honest
runtime truth of the corrected v0.2.0 release **before** any AI/ML feature work.

## Environment

| Item | Value |
|---|---|
| Branch at session start | `build/faultline-v0.2.0` |
| Base commit (`git rev-parse HEAD`) | `defdbfdda1efa77cbfbb73e6672c96937ee48896` |
| System Python | 3.11.14 |
| Verified test/runtime venv | `.venv` (Python 3.13.1) with pinned deps installed |
| Platform | macOS (Darwin 25.3.0) |

> Note: `scripts/verify_submission.sh` invokes bare `python`. The system `python`
> (3.11.14) does **not** have `fastapi`/`Pillow` installed, so the gate must be run
> with the `.venv` activated (`source .venv/bin/activate`). This is an environment
> setup detail, not a repository defect.

## Baseline gate results (inside `.venv`)

`./scripts/verify_submission.sh`:

1. Python compile + surface audit — **pass** (44 source files swept)
2. JavaScript syntax (`node --check`) — **pass**
3. Generated demo-asset integrity — **pass** (no held-out answers)
4. Core + API tests — **33 passed**
5. Dependency-closure consistency — **pass**
6. Reproducible fixture evaluation — **pass**
7. Live HTTP + signed-proof smoke test — **pass**
8. Release manifest — **stale** (see below)

### The single non-green item

`MANIFEST.json` reports stale because the working tree started this session with
four documentation files deleted (unstaged):

- `AUDIT_RESULTS.txt`
- `BUILD_LOG.md`
- `PROJECT_QUALITY_AUDIT.md`
- `PROJECT_STATUS.md`

These are recreated in Phase 12 (documentation) and the manifest is rebuilt in
Phase 10/13 (release). Per the human-owned Git workflow, they are **not** restored
via `git restore`. The committed state at `HEAD` is manifest-consistent.

## Architecture truth (verified by reading runtime code, not planning docs)

- **FastAPI** service (`apps/api/faultline_api`) serving a zero-build static
  frontend (`apps/web-static`).
- **Deterministic core** (`packages/faultline_core`) with exact `Fraction`
  arithmetic, six executable fraction procedures + a `no_consistent_procedure`
  hypothesis, a posterior-style log-space scorer (`inference.infer`), a confidence
  gate (`inference.confidence_gate`), exact information gain (`information_gain`),
  and a restricted JSON DSL verifier (`dsl` + `synthesis.verify_candidate`).
- **Held-out proof**: HMAC-SHA256 signed, TTL-bounded, student- and problem-bound
  tokens (`services/held_out.py`). No answers in public payloads or bundled assets.
- **Uploads**: raw bounded PNG/JPEG body, real image verification, decompression
  bomb limits, fixed-template 8-region segmentation, bytes not stored
  (`services/segmentation.py`, `routes/api.py`).
- **Jobs**: process-local, TTL + count bounded, time-based progress simulation
  (`services/jobs.py`).
- **Adapters** `adapters/vision.py` and `adapters/text_model.py` are **disabled
  boundaries** — `FixtureVisionAdapter` returns a hard-coded reading; the
  `Featherless*` adapters raise "disabled until tested". **No live model call
  exists in the baseline.** The job pipeline does not actually invoke any adapter;
  `create_analysis` validates/segments the image and then serves the synthetic
  fixture with an explicit disclosure.

## Gaps this upgrade must close (honestly)

1. No real neural model runs on a real image (adapters are inert).
2. Inference likelihoods are heuristic constants inlined in `inference.py`, not a
   documented/tested Bayesian model with explicit priors, likelihoods, reading
   marginalization, entropy, and margin.
3. No explicit `local_ai` vs `fixture` runtime mode; the fixture is always served.
4. Model-proposed hypotheses (`synthesis.verify_candidate`) exist but are never
   fed by a model and never merged into the posterior candidate set.
5. No licensed handwriting benchmark, model card, or layered evaluation.

## Preserved invariants (must not regress)

- Frontend byte-for-byte frozen (`FRONTEND_MANIFEST.json`, `scripts/check_frontend_freeze.py`).
- Existing API field names/routes/status codes (see `apps/api/tests/test_api.py`).
- No held-out leakage; signed reveal; bounded uploads; security headers; no body logging.
