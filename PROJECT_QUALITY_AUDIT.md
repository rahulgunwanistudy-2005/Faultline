# Faultline Project Quality Audit — Corrected v0.2.0

## Final verdict

**Submission-ready as a hardened synthetic competition prototype. Not production-ready for real student data and not yet a validated handwriting/classroom product.**

The uploaded project was audited against the supplied deterministic seven-phase quality-audit specification. Every actionable code defect found in the audited scope was corrected. Remaining gaps are explicit product/research boundaries rather than hidden or partially implemented claims.

## Audit scope

- Source files deep-read: **41**
- Source lines: **3,221**
- Languages: 34 Python, 3 JavaScript, 2 HTML, 1 CSS, 1 SQL planning schema
- Tags: frontend, backend, full-stack, AI-assisted, research/evaluation
- Runtime: FastAPI + zero-build browser interface + dependency-light Python core

## Tooling ground truth

| Tool/check | Result |
|---|---|
| Python compileall | Passed |
| pytest | **33 passed** |
| Node JavaScript syntax | Passed for `app.js` and `judge.js` |
| Generated fixture integrity | Passed; no public held-out actual/predicted fields |
| Custom categorical security sweep | Passed across 44 runtime/config files |
| Project dependency-closure check | Passed for all exact direct pins and transitive metadata constraints |
| Evaluation regeneration | Passed |
| Live HTTP smoke test | Passed |
| Release manifest | Deterministic SHA-256 manifest included |
| ruff / mypy / pyright / bandit / pip-audit / hadolint | Not installed in the audit sandbox |
| Docker build | Docker engine unavailable in the audit sandbox |
| Rendered browser automation | Browser sandbox blocked localhost/file navigation; manual visual gate remains |
| Fresh package download | Sandbox package mirror returned no distributions; exact installed versions were verified instead |

## Issue registry and fixes

| ID | Severity | Finding | Resolution |
|---|---:|---|---|
| Q-001 | **Critical** | Held-out actual and predicted answers were present in the initial API/browser fixture, invalidating the centerpiece prediction-before-reveal proof. | Removed both fields from all public payloads and generated assets; added leakage tests and asset-generation guard. |
| Q-002 | **Critical if activated** | An unused duplicate Next.js/React runtime had no lockfile and pinned versions later covered by a React Flight RCE advisory. | Removed the entire unverified duplicate runtime and its package surface; one tested frontend remains. |
| Q-003 | **Critical** | `python-multipart==0.0.22` was unnecessary and affected by later multipart-parser advisories. | Removed multipart parsing and the dependency; upload now accepts a bounded raw PNG/JPEG body. |
| Q-004 | **Major** | Held-out prediction accepted caller-controlled problem data, reveal used GET/global mutable state, and integrity was not student-bound. | Server now uses the canonical problem, returns an expiring HMAC token, and verifies signature, student, problem, and age on POST reveal. |
| Q-005 | **Major** | Upload trusted MIME, accepted unsupported PDF claims, read before robust validation, and did not clearly separate upload handling from fixture diagnosis. | Added streamed byte cap, early content-length rejection, Pillow byte verification, decompression limits, minimum dimensions, EXIF normalization, fixed-template crops, no persistence, and explicit synthetic-fixture disclosure. |
| Q-006 | **Major** | Polling GET requests mutated job progress and jobs accumulated without a bounded lifecycle. | Progress is time-derived; jobs now expire by TTL and the store has a hard maximum. |
| Q-007 | **Major** | Public write routes lacked rate limiting; CORS and security/observability boundaries were weak. | Added bounded sliding-window limits, normalized rate buckets, opt-in CORS, CSP/anti-framing/MIME/referrer/permissions headers, no-store API responses, safe request IDs, and metadata-only structured logs. |
| Q-008 | **Major** | Reading corrections allowed weak schemas, unknown IDs, mutable defaults, and did not consistently recompute the wording signal. | Added strict Pydantic models, exact fraction parsing/range checks, vocabulary validation/deduplication, unknown-ID rejection, and complete recomputation. |
| Q-009 | **Major** | Rate limits could be diluted with changing resource IDs and the key map could exceed its cap. | Keys are now per-client/per-operation, stale entries are pruned, and new keys are denied at the cap. |
| Q-010 | **Medium** | Docker ran as root and Compose allowed a writable filesystem. | Added an unprivileged runtime user, read-only Compose filesystem, tmpfs, and `no-new-privileges`; Compose now requires an explicit proof secret. |
| Q-011 | **Medium** | Static demo data could drift from the inference engine. | Added deterministic asset generation plus `--check`; release verification fails on drift. |
| Q-012 | **Medium** | Current docs claimed Next.js, PostgreSQL, live Featherless OCR, a controlled handwriting evaluation, and other unimplemented features. | Rewrote claims, architecture, deployment, API blueprint, ADRs, and Devpost copy to match v0.2.0 exactly. |
| Q-013 | **Medium** | Diagnostic-item download controls were nonfunctional. | Implemented question and tomorrow-plan downloads. |
| Q-014 | **Medium** | Public proof responses could be cached and JSON models accepted unexpected fields. | Added `Cache-Control: no-store` for `/v1/*` and `extra="forbid"` request schemas. |
| Q-015 | **Minor** | Optional provider classes looked like unfinished runtime stubs. | They now fail explicitly with bounded, truthful disabled-adapter errors; docs mark them non-runtime. |
| Q-016 | **Minor** | Reference malrule JSON, item bank, and fixture could drift silently. | Added catalog, domain, uniqueness, and one-held-out-item integrity tests. |
| Q-017 | **Minor** | Static dialogs lacked basic dialog semantics and download URL cleanup was fragile. | Added dialog roles/labels and safer temporary download handling. |
| Q-018 | **Minor** | Release contents had no reproducible integrity inventory. | Added a deterministic file-size/SHA-256 `MANIFEST.json` and verification command. |

## Cross-file architecture review

### Claim-to-code alignment

Current claims now match implementation. The project explicitly says that uploaded images are validated and segmented, while displayed diagnoses remain a synthetic fixture because live OCR is disabled.

### Data and privacy flow

Uploaded bytes are held only in request memory, decoded/cropped, and discarded. Logs contain method, route, status, duration, and request ID—not worksheet bytes, answers, names, tokens, or filenames. The demo uses pseudonyms.

### Held-out integrity

Public class payloads and browser assets include the problem but not the actual answer or precomputed prediction. Prediction and reveal are separate server calls with a signed token. The server-side source fixture necessarily contains demo ground truth, so this is a trustworthy UI/API separation—not secrecy from repository maintainers.

### Dependency architecture

The release has one frontend runtime and no npm dependency graph. Python runtime and test dependencies are exactly pinned. The custom dependency checker evaluates the installed dependency closure while ignoring unrelated packages in a shared host environment.

### Failure behavior

Invalid uploads, unsupported media, oversized bodies, invalid corrections, unknown records, rate limits, and proof-token failures return explicit 4xx responses. Unexpected server exceptions are logged with stack traces and return a generic 500 response with security headers.

### Scaling boundary

Jobs, limits, and signing configuration are suitable for a single-instance competition demo. Multi-instance production requires shared persistence/queues/limits, authentication, authorization, tenant isolation, encryption/retention policies, and governance for student data.

## Verification-loop result

### Cycle 1

Critical proof leakage, dependency vulnerabilities, upload weaknesses, state lifecycle, schema, docs, and deployment defects fixed.

### Cycle 2

Rate-limit bypass/key-cap issue, API caching, strict extra-field rejection, CORS upload-header bug, dependency-check portability, data drift, and accessibility details fixed.

### Cycle 3

Full compile, source sweeps, **33 tests**, JavaScript syntax, fixture integrity, dependency closure, evaluation, and live HTTP proof flow all passed. No additional actionable code defects were found.

## Remaining NEEDS_HUMAN / research gates

1. **Visual browser QA:** run Chrome and Safari at approximately 375 px and 1440 px; verify keyboard/focus behavior and console/network cleanliness.
2. **Docker execution:** build and run the image on a machine with Docker; the Dockerfile/Compose configuration was statically reviewed only.
3. **Automated CVE scanner:** run `pip-audit` or an equivalent scanner in a normal networked environment; it was unavailable here.
4. **Real OCR evaluation:** wire a privacy-reviewed provider and report transcription, engine-on-reviewed-transcription, and end-to-end metrics separately.
5. **Real data controls:** do not upload identifiable student work until authentication, authorization, consent, retention, encryption, and governance are implemented.

## Release recommendation

Use v0.2.0 for the hackathon demo and pitch **only with the synthetic-data badge and current disclosure text intact**. Do not claim real handwriting accuracy, classroom accuracy, or learning improvement.
