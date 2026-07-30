# Security Policy

## Supported surface

This repository is a synthetic hackathon demo. It does not provide accounts, authentication, real student storage, or a production database. Do not upload real student work to a public deployment.

## Data handling

- Uploads are limited to PNG/JPEG images and eight megabytes.
- Image bytes are validated, segmented in memory, and discarded.
- Request bodies and image bytes are not written to application logs.
- Display names in the fixture are pseudonyms.
- Public class payloads and bundled JavaScript contain no held-out answers.

## Proof tokens

Held-out reveals require an HMAC-signed token bound to the student and problem. Tokens expire after ten minutes by default. Set `FAULTLINE_PROOF_SECRET` in every deployment. A random process-local secret is generated only for the single-worker local demo.

## Deployment limits

The rate limiter and job store are process-local. A multi-instance production service would need a shared edge/Redis limiter and persistent queue. Authentication and authorization are required before processing real educational records.

## Reporting

Do not include student information or secrets in a report. Provide the affected route or file, a minimal reproduction, expected impact, and mitigation suggestion.
