# Faultline

> **A teacher sees the procedure behind a student’s fraction error—not merely a score and never an unsupported improvement claim.**

Faultline is a narrow, competition-oriented prototype for diagnosing repeated procedures in **adding fractions with unlike denominators**. It executes candidate procedures against visible student work, reports the full posterior, refuses to name a diagnosis when evidence is weak, and selects follow-up questions by exact expected information gain.

Faultline is **neuro-symbolic**: a local vision-language model transcribes handwriting into structured evidence and may propose symbolic procedure hypotheses, but a deterministic symbolic executor and an explicit Bayesian engine — never the model — decide the diagnosis. See [docs/AI_ML_PROOF.md](docs/AI_ML_PROOF.md) and [docs/architecture/neuro_symbolic_bayesian_architecture.md](docs/architecture/neuro_symbolic_bayesian_architecture.md).

## Runtime modes

- `FAULTLINE_RUNTIME_MODE=fixture` (default) — deterministic, clearly-synthetic fixture; no model required. This is what the public deployment runs.
- `FAULTLINE_RUNTIME_MODE=local_ai` — a real local vision model (via [Ollama](https://ollama.com), default `qwen3-vl:4b`) transcribes the uploaded worksheet and the deterministic Bayesian engine diagnoses it. No hosted API key is used or accepted. There is **no silent fixture fallback**: a missing model or timeout returns a clear error or abstention.

## What the verified build does

- Serves a zero-build HTML/CSS/JavaScript teacher interface from FastAPI.
- Shows a clearly labeled 12-student synthetic regression fixture.
- Executes six deterministic fraction procedures with exact rational arithmetic.
- Separates classes into teacher-action lanes.
- Shows item-by-item observed-versus-predicted evidence.
- Withholds low-confidence diagnoses.
- Ranks next questions by exact information gain.
- Locks a held-out prediction, returns a signed proof token, and reveals the separately stored answer only when that valid token is submitted.
- Validates and segments a PNG/JPEG known-template upload without retaining the image.
- Clearly discloses that live handwriting recognition is not enabled and that upload results use the synthetic fixture.
- Includes a deterministic 30-second Judge Mode.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt
./start.sh
```

Open:

- App: `http://localhost:8000`
- Judge Mode: `http://localhost:8000/judge`
- Health: `http://localhost:8000/health`
- OpenAPI schema: `http://localhost:8000/openapi.json`

Interactive Swagger/ReDoc pages are disabled in the hardened demo runtime. The OpenAPI JSON remains available.

## Run with a local model (optional)

```bash
# Terminal 1
ollama serve
# Terminal 2
ollama pull qwen3-vl:4b
export FAULTLINE_RUNTIME_MODE=local_ai
export FAULTLINE_PROOF_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
./scripts/setup_local_ai.sh    # verifies server, model, and structured output
./start.sh
```

Model health is reported at `GET /v1/models/health`; the active mode at `GET /v1/runtime`. Fixture mode remains available at any time with `FAULTLINE_RUNTIME_MODE=fixture ./start.sh`.

The public/fixture deployment does **not** perform live OCR; only `local_ai` mode invokes a model.

## Verify the release

```bash
./scripts/verify_submission.sh
```

The verification command checks:

1. Python compilation and categorical source sweeps
2. JavaScript syntax
3. Sanitized generated-fixture integrity
4. Core and API tests
5. Project dependency-closure consistency
6. Reproducible fixture evaluation
7. A live HTTP and signed-proof smoke test
8. Deterministic release-manifest integrity

Current corrected result: **33 tests passing**.

## The held-out proof is now genuinely server-gated

The public class endpoint and the bundled fallback asset contain:

- the held-out problem;
- whether proof is available;
- **no actual answer**;
- **no predicted answer**.

The proof flow is:

1. `POST /v1/students/{id}/held-out-prediction`
2. Server derives the prediction from visible work and returns a signed, expiring proof token.
3. `POST /v1/students/{id}/held-out-reveal` with that token.
4. Server verifies the signature, student, problem, and age before returning the separately stored answer.

Tampered tokens and cross-student token reuse are rejected by integration tests.

## Upload behavior and disclosure

The upload endpoint accepts one raw PNG or JPEG body:

```bash
curl -X POST \
  'http://localhost:8000/v1/analyses?template_id=fractions-v1' \
  -H 'Content-Type: image/png' \
  -H 'X-Filename: worksheet.png' \
  --data-binary '@worksheet.png'
```

The server:

- streams and enforces an 8 MB limit;
- validates actual image bytes rather than trusting the MIME header;
- rejects decompression bombs and unsafe/undersized images;
- normalizes orientation and dimensions;
- segments eight fixed-template regions;
- does not store the uploaded bytes;
- returns a clear disclosure that diagnoses come from the synthetic fixture because live OCR is not enabled.

PDF is deliberately not accepted because this build does not contain a verified PDF rasterization path.

## Architecture

```text
Teacher / Judge
      │
      ▼
Static web UI served by FastAPI
      │
      ├── raw bounded PNG/JPEG upload
      ├── fixed-template validation + segmentation
      ├── disclosed synthetic fixture path
      └── reading corrections
      ▼
Faultline Core
      ├── executable fraction procedures
      ├── posterior + confidence gate
      ├── exact information gain
      └── restricted JSON DSL verifier
      │
      ├── class map + evidence
      ├── next diagnostic questions
      └── signed prediction/reveal proof
```

The core package imports no web framework, model SDK, or database client.

## API surface

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | Health and runtime mode |
| GET | `/v1/demo/classes/period-3` | Sanitized synthetic class analysis |
| POST | `/v1/analyses?template_id=fractions-v1` | Validate and segment a raw PNG/JPEG body |
| GET | `/v1/analyses/{id}` | Read time-based demo job status |
| PATCH | `/v1/analyses/{id}/readings/{reading_id}` | Validate a reviewed answer and recompute |
| GET | `/v1/students/{id}/diagnostic-items` | Return highest-information questions |
| POST | `/v1/students/{id}/held-out-prediction` | Lock a prediction and issue a signed token |
| POST | `/v1/students/{id}/held-out-reveal` | Verify token and reveal separately stored work |

## Security controls in this corrected release

- No initial or bundled held-out-answer leakage
- Signed, expiring, student-bound proof tokens
- Raw-body uploads; no multipart parser dependency
- Streaming upload-size enforcement
- Real image verification and decompression-bomb limits
- Filename normalization; uploaded bytes are not stored
- Bounded and expiring in-memory job store
- Process-local sliding-window rate limits on write endpoints
- Strict correction schemas and allowed step-feature vocabulary
- Same-origin default; CORS is opt-in by environment variable
- CSP, anti-framing, MIME-sniffing, referrer, permissions, and request-ID headers
- Metadata-only request logging; request bodies are not logged
- Non-root Docker runtime with a read-only Compose filesystem
- Exact runtime dependency pins

See `SECURITY.md` and `PROJECT_QUALITY_AUDIT.md`.

## Honest evaluation

The included fixture reports:

- **12/12** assigned procedures rank first on exact fixture transcriptions;
- **11/12** receive a named diagnosis after confidence gating;
- **1/12** is deliberately withheld;
- held-out answer leakage, token tampering, and cross-student token reuse are blocked by tests.

These are regression results—not classroom accuracy, handwriting accuracy, or learning impact.

## Repository map

```text
apps/api/              FastAPI service and tests
apps/web-static/       verified competition interface
packages/faultline_core/ deterministic inference engine
data/                   fixture, item bank, rules, evaluation outputs
docs/                   architecture, claims, evaluation, pitch, security decisions
planning/               original winning blueprint; some files describe future-state ideas
scripts/                generation, evaluation, smoke, and release verification
```

## Local neural provider

In `local_ai` mode the transcription and hypothesis-proposal roles are served by a local Ollama model (default `qwen3-vl:4b`, configurable). The model transcribes visible work into strictly schema-validated evidence and may propose symbolic DSL hypotheses; it never names a diagnosis, returns a posterior, or runs code. Every proposal is adjudicated by the deterministic verifier before it can influence inference. See [docs/architecture/privacy_boundary.md](docs/architecture/privacy_boundary.md) and [docs/evaluation/MODEL_CARD.md](docs/evaluation/MODEL_CARD.md).

## Evaluation

Layered and reproducible — see [docs/evaluation/EVALUATION_CARD.md](docs/evaluation/EVALUATION_CARD.md). Deterministic Bayesian metrics use the labelled **synthetic** fixture; transcription is evaluated on a licensed public symbol subset (HASYv2, ODbL); end-to-end image→procedure accuracy is **not** claimed (no public procedure labels exist).

## Deliberate non-claims

- no arbitrary worksheet-layout recognition;
- no verified handwriting accuracy;
- no PDF ingestion;
- no causal learning-improvement percentage;
- no mastery forecast;
- no diagnosis of language proficiency, disability, or identity;
- no longitudinal learner model;
- no autonomous LLM diagnosis.

## Deployment

Set `FAULTLINE_PROOF_SECRET` to a stable high-entropy value before deploying or using multiple workers:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Then use the included `Dockerfile`, `docker-compose.yml`, or `render.yaml`.

## License

MIT
