# Build Log

## v0.1.0 — Initial vertical

- Implemented the deterministic fraction domain, procedure library, posterior, confidence gate, information gain, safe DSL, FastAPI demo, static teacher UI, Judge Mode, fixtures, and tests.

## v0.2.0 — Quality-audit correction

- Removed held-out actual and predicted answers from all public class payloads and bundled assets.
- Replaced the global prediction store with HMAC-signed, expiring, student-bound proof tokens.
- Changed reveal from an unauthenticated GET to a token-verified POST.
- Removed caller-supplied held-out problems; the server now uses the separately stored canonical problem.
- Removed the unused Next.js/React duplicate runtime and its vulnerable/unlocked dependency surface.
- Removed `python-multipart`; uploads now use a bounded raw PNG/JPEG stream.
- Added actual image validation, decompression-bomb protection, dimensions, filename normalization, and no-storage metadata.
- Removed unsupported PDF claims.
- Replaced polling-side state mutation with time-derived job status.
- Bounded and expired the in-memory job store.
- Added rate limiting, opt-in CORS, security headers, safe request IDs, and metadata-only structured logs.
- Added strict correction validation and rejection of unknown reading IDs.
- Fixed wording-signal recomputation after teacher corrections.
- Removed dead diagnostic-download buttons by implementing their downloads.
- Added generated-fixture drift checks and stronger smoke tests.
- Hardened Docker to run as a non-root user.
- Expanded the suite from 22 to 33 tests.
