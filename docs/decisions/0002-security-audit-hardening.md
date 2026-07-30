# ADR 0002: Harden the public competition demo boundary

## Status

Accepted in v0.2.0.

## Context

The first release exposed held-out values in the browser fixture, accepted multipart uploads through an unnecessary dependency, and treated several in-memory demo controls as if they were production boundaries.

## Decision

- Remove held-out actual and predicted answers from public class payloads and generated browser assets.
- Use an expiring HMAC-signed token for prediction-then-reveal and reject tampered or cross-student tokens.
- Accept bounded raw PNG/JPEG bodies instead of multipart forms.
- Verify image bytes with Pillow, reject decompression bombs and undersized images, and never persist uploads.
- Bound in-memory job and rate-limit stores.
- Make CORS opt-in and add browser security headers, request IDs, metadata-only logs, and `Cache-Control: no-store` for API responses.
- Run the container as a non-root user.

## Limitations

This remains a public, unauthenticated, single-instance synthetic demo. Real student data requires authentication, authorization, tenant isolation, durable encrypted storage, retention controls, consent/governance, and a shared edge/Redis limiter.
