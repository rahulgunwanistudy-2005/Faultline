# Technical QA

## Fresh-machine test

- Clone repository.
- Copy `.env.example`.
- Start fixture mode with documented commands.
- Run all tests.
- Open Judge Mode.
- Run a live upload if credentials are available.

## Failure injection

- Invalid image type.
- Corrupt PDF.
- Rotated page.
- One unreadable answer.
- Model timeout.
- Malformed model JSON.
- Database unavailable.
- Duplicate submission/correction.
- Held-out reveal requested before prediction.
- Unsupported worksheet template.

## Security

- Fuzz the DSL parser.
- Reject unknown operators and variables.
- Reject excessive AST depth and node count.
- Confirm no `eval`, `exec`, shell or dynamic import.
- Confirm path traversal cannot access arbitrary files.
- Confirm object-storage keys are generated server-side.
- Confirm logs redact page text and API keys.

## UI interaction audit

Use Playwright to click every visible button and link in the seeded flow. Fail the test for console errors, 404s, unhandled promise rejections, or controls with no action.
