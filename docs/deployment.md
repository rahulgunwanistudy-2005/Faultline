# Deployment

Faultline v0.2.0 is a single FastAPI service that serves both the API and the zero-build static interface.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
./start.sh
```

Open:

- app: `http://127.0.0.1:8000/`
- Judge Mode: `http://127.0.0.1:8000/judge`
- health: `http://127.0.0.1:8000/health`
- OpenAPI document: `http://127.0.0.1:8000/openapi.json`

Interactive Swagger/ReDoc pages are intentionally disabled so the production content-security policy does not depend on external CDN assets.

## Required production secret

Set a stable, high-entropy value before using more than one worker or instance:

```bash
FAULTLINE_PROOF_SECRET='replace-with-at-least-32-random-bytes'
```

Without it, a random process-local signing key is generated at startup. That is safe for a single-process local demo, but proof tokens will not survive routing to another process or a restart.

## Optional configuration

See `.env.example` for upload limits, proof TTL, job retention, animation timing, and an explicit CORS allowlist. CORS is disabled unless `FAULTLINE_CORS_ORIGINS` is set.

## Docker

```bash
docker build -t faultline:0.2.0 .
docker run --rm \
  -p 8000:8000 \
  -e FAULTLINE_PROOF_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')" \
  faultline:0.2.0
```

The image runs as an unprivileged user. `docker-compose.yml` additionally enables a read-only filesystem and `no-new-privileges`.

## Render

The repository includes `render.yaml`. Add `FAULTLINE_PROOF_SECRET` as a secret environment variable. Do not add `FEATHERLESS_API_KEY` until a live adapter contract, privacy review, and end-to-end evaluation are complete.

## Verification

```bash
./scripts/verify_submission.sh
./scripts/smoke_test.sh
```

Before submission, also perform a human Chrome/Safari pass at desktop and mobile widths. Browser automation was unavailable in the audit sandbox, so rendered visual behavior is a documented manual gate.
