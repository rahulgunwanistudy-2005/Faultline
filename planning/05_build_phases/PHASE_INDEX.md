# Build Phases

Each phase is designed for one focused GPT-5.6 chat session. Attach `06_agent_prompts/MASTER_CONTEXT.md`, the phase prompt, and only the reference files named in that prompt.

| Phase | Deliverable | Hard gate |
|---:|---|---|
| 0 | Evidence lock, scope, repo and build log | No unsupported claim; domain frozen |
| 1 | Monorepo scaffold and CI | All apps boot; CI passes |
| 2 | Fraction domain and executable malrules | Exhaustive rule tests pass |
| 3 | Posterior, uncertainty and confidence gate | Controlled fixtures identify expected rule |
| 4 | Information-gain item selector | Ambiguous fixture receives separating items |
| 5 | Worksheet template and Featherless transcription | Structured crops + correction UI work |
| 6 | FastAPI job pipeline and persistence | Upload-to-result integration test passes |
| 7 | Class map and evidence drawer | Full seeded flow is beautiful and usable |
| 8 | Held-out prediction and reveal | Held-out answer cannot leak into inference |
| 9 | Safe novel-rule proposal | No arbitrary code; verifier tests pass |
| 10 | Evaluation lab and confusion matrix | Metrics are reproducible and labeled honestly |
| 11 | Judge Mode, deployment and observability | 30s tour and public app work in incognito |
| 12 | Pitch, Devpost, README and final red team | Video under 2:00; all links verified |
