# Implemented Architecture

Faultline v0.2.0 uses a dependency-light inference package, a FastAPI orchestration layer, and a zero-build HTML/CSS/JavaScript interface served from the same process.

## Runtime components

1. **Static interface** — class map, evidence drawer, exports, and deterministic 30-second Judge Mode.
2. **Image boundary** — accepts a raw PNG/JPEG body, enforces an 8 MB default limit, verifies actual image bytes, constrains decompression, normalizes orientation/size, and crops eight fixed-template regions.
3. **Synthetic demo job** — clearly discloses that live handwriting transcription is disabled and returns a deterministic fixture after the upload boundary is demonstrated.
4. **Inference core** — executes six fraction procedures, scores their fit, incorporates step evidence and reading confidence, computes a posterior, and applies explicit confidence gates.
5. **Information-gain selector** — forward-simulates active hypotheses to rank the next questions.
6. **Held-out proof service** — creates an expiring HMAC-signed prediction token and requires that token for a separate POST reveal.
7. **Restricted synthesis verifier** — validates and interprets a small JSON expression language; it never evaluates Python or model-supplied code.

## Trust boundaries

- A future vision provider may return candidate readings and confidence only; it cannot name a diagnosis.
- A future text provider may propose restricted JSON expressions only; the verifier may reject every proposal.
- Action copy is reviewed static metadata, not generated advice.
- Public class payloads and browser assets omit both held-out actual answers and held-out predictions.
- The server-side fixture still contains the held-out ground truth required for the reveal; therefore this is a demo integrity boundary, not a claim of cryptographic secrecy from repository maintainers.

## State and scaling limits

Jobs and rate limits are bounded and stored in process memory. This is appropriate for a single-instance competition demo. A multi-instance product would require shared job persistence, shared rate limiting, authentication, tenant isolation, audit logs, and a student-data governance review.

## Demo reliability

The core class map and Judge Mode require no external API key or network call. If the proof API is unavailable, Judge Mode displays an error and does not fabricate an answer.
