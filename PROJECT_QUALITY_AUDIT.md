# Project Quality Audit + Red-Team — Faultline v0.3.0

Each red-team question is answered against runtime code and a test. "No" means the
attack is blocked.

## Red-team results

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Can the frontend access held-out answers before reveal? | No | `audit_surface.py`, `test_api.py`, `test_api_compatibility.py::test_public_payload_has_no_held_out_answers` |
| 2 | Can a caller select the held-out problem? | No | Held-out is server-chosen (fixture) / leave-one-out (upload); not caller-supplied |
| 3 | Can proof tokens be modified, replayed, or reused for another student? | No | HMAC + TTL + student/problem binding; `test_api.py::test_tampered_or_cross_student_proof_is_rejected` |
| 4 | Can worksheet text override the model prompt? | No | Prompts declare image text untrusted; injected answers only ever parse as a fraction — `test_model_security.py::test_injection_text_in_transcription_cannot_become_a_hypothesis` |
| 5 | Can malformed neural output reach the symbolic/Bayesian core? | No | Strict Pydantic (`extra="forbid"`) + DSL verifier; `test_model_security.py::test_malformed_expression_cannot_reach_bayesian_core` |
| 6 | Can model confidence become the posterior? | No | No probability field exists on model schemas; `test_hypothesis_generation.py::test_model_score_never_becomes_posterior` |
| 7 | Can the model directly assign a diagnosis? | No | No diagnosis field; nominations are hints only |
| 8 | Can a known hypothesis be excluded because the model failed to nominate it? | No | `build_candidate_set` always includes the full known library first |
| 9 | Can a proposal execute code, use item ids, or memorize answers? | No | DSL has no strings/ids/conditionals/code; `test_synthesis_validation.py` |
| 10 | Can an equivalent known rule be misrepresented as novel? | No | Behavioural-signature novelty check; `test_synthesis_validation.py::test_duplicate_of_known_rule_rejected` |
| 11 | Can local-AI mode silently use fixtures? | No | Pipeline fails or abstains; `test_local_ai_jobs.py::test_local_ai_failure_has_no_fixture_fallback` |
| 12 | Can uploaded work enter logs, static assets, or the release ZIP? | No | In-memory crops cleared in `finally`; metadata-only logs; release excludes images |
| 13 | Can the dataset contain untracked licensing or PII? | No | Provenance records ODbL + no-PII; `test_dataset_provenance.py` |
| 14 | Can dataset downloads traverse paths or place executables? | No | tar path-traversal guard + PNG-magic check; allowlisted host + MD5 |
| 15 | Can one client exhaust model slots or job capacity? | Bounded | Concurrency semaphore + bounded job store + rate limits |
| 16 | Can Bayesian results vary between identical runs? | No | Order-invariant, deterministic; `test_bayesian.py` |
| 17 | Can priors/thresholds change without appearing in metadata? | No | `BayesianResult.as_metadata` records prior mode + config; eval card records config |
| 18 | Did any frontend file change? | No | `git diff -- apps/web-static` empty; freeze verified |

## Quality gates

- 146 tests pass; `verify_submission.sh` (12 gates) green in `.venv`.
- Surface audit: no `eval`/`exec`, bare/silent except, personal paths, disabled TLS,
  pickle, or shell-injection patterns across 71+ source files.
- TLS verification is never disabled (dataset fetch uses a verifying context with
  certifi fallback).
- Exact dependency pins unchanged; only `httpx` (already pinned) used for the model client.

## Residual risks (documented, not hidden)

- Local VLM transcription accuracy is unverified in the field.
- Synchronous local-AI pipeline in this single-worker demo (real stages).
- No production readiness for identifiable student data.
