# System Architecture

## Winning architecture

```mermaid
flowchart LR
    U[Teacher / Judge] --> W[Next.js Web App]
    W -->|upload or demo fixture| API[FastAPI API]
    API --> JOB[Analysis Job Orchestrator]
    JOB --> SEG[Template Segmentation]
    SEG --> VISION[Featherless Vision Adapter]
    VISION --> REVIEW[Structured OCR Candidates]
    REVIEW --> CORE[Faultline Core]
    CORE --> RULES[Executable Malrule Library]
    CORE --> POST[Posterior + Confidence Gate]
    POST --> IG[Information Gain Item Selector]
    POST --> SYNTH{Known rule fits?}
    SYNTH -->|no| LLM[Featherless Rule Proposal]
    LLM --> DSL[Safe JSON DSL Verifier]
    DSL --> POST
    POST --> EXPLAIN[Plain-Language Explanation]
    IG --> RESULT[Class Map + Tomorrow Card]
    EXPLAIN --> RESULT
    RESULT --> W
    API --> DB[(Postgres / SQLite demo)]
    API --> OBJ[(Object Storage)]
```

## Architectural principles

1. **Deterministic core:** malrule execution, likelihood scoring, confidence gates, information gain, and verification do not depend on free-form LLM judgment.
2. **Provider adapters:** vision and proposal models sit behind interfaces so the demo can run from fixtures and the provider can be swapped.
3. **Demo reliability:** seeded demo data bypasses external calls while exercising the same result schema and UI components.
4. **Narrow worksheet template:** fixed crop coordinates are acceptable and preferable for a winning prototype; generalized page understanding is a roadmap item.
5. **Separable metrics:** each stage emits its own evaluation result.

## Deployment profiles

### Submission profile

- Next.js on Vercel.
- FastAPI on Railway, Render, Fly.io, or a comparable Python host.
- Postgres/Supabase for job metadata.
- S3-compatible object storage for temporary images.
- In-process async worker or a single background process.

### Production roadmap

- Dedicated queue (Redis/RQ, Celery, or cloud queue).
- Isolated worker for image processing.
- Encrypted object storage and institutional SSO.
- Template authoring and district-level retention controls.

Do not introduce queue infrastructure before the deterministic flow and video are stable.
