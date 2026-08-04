# Privacy and trust boundary

## Worksheet data

- Uploaded bytes and per-region crops live only in memory for the duration of a
  request/pipeline run; they are **never** persisted to disk or static dirs
  (`services/background_jobs.py` clears crops in a `finally`; `segmentation.py`
  returns bytes, stores nothing).
- Request bodies and worksheet contents are **never** logged
  (`middleware.py` logs metadata only; `ollama_client.py` never logs images,
  base64, answers, prompts, tokens, or full raw responses —
  `test_ollama_adapter.py::test_no_image_bytes_or_prompt_in_logs`).
- The licensed dataset `images/` are excluded from the release ZIP
  (`scripts/release.sh`).

## Model calls (runtime)

- Loopback-only endpoint; a public host is rejected in `config.py`.
- Tools/web disabled: the client only calls `/api/generate`, `/api/tags`,
  `/api/show`. No tool-use, no browsing.
- Structured output only; anything outside the strict schema is rejected.
- No secrets or environment variables are placed in prompts.
- Model errors are mapped to typed internal errors and returned to clients as
  generic, redacted messages (`ModelError.client_message`).

## Held-out proof

- Public payloads and bundled assets contain **no** held-out answers
  (`audit_surface.py`, `test_api.py`, `test_local_ai_jobs.py`).
- Reveal requires a signed, TTL-bounded, student- and problem-bound HMAC token
  (`held_out.py`). Tampered or cross-student tokens are rejected.

## What is never inferred

Disability, language proficiency, intelligence, identity, motivation, or intent.
The neural output schemas have no field for any of these, and the prompts
explicitly forbid inferring them.
