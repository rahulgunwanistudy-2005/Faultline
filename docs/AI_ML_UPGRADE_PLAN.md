# Faultline AI/ML Upgrade Plan (v0.2.0 → v0.3.0 neuro-symbolic Bayesian)

This plan turns the honest synthetic prototype into a genuinely AI-powered,
locally runnable, neuro-symbolic and evidence-backed release. It is engineering
truth, not marketing. Every claim here is backed by code and tests, or is
labelled as a target/limitation.

## 1. Current runtime truth

See [`docs/evaluation/baseline_v0.2.0.md`](evaluation/baseline_v0.2.0.md). In one
sentence: the deterministic fraction core, information gain, signed proof, bounded
uploads, and frozen frontend are real and tested; the neural adapters are inert
stubs and every displayed diagnosis comes from a disclosed synthetic fixture.

## 2. Target neuro-symbolic architecture

```
image → validate → segment → LOCAL NEURAL VISION MODEL (transcribe to structured evidence)
      → deterministic reading-consensus (multi-view, schema/parse validity, uncertainty)
      → LOCAL NEURAL HYPOTHESIS MODEL (nominate known IDs + propose ≤3 DSL programs)
      → symbolic execution of ALL known + all valid proposed procedures
      → DETERMINISTIC BAYESIAN INFERENCE (priors × likelihood, reading marginalization)
      → sufficient? named posterior : abstain + request evidence
      → information-gain next question → signed prediction/reveal → teacher contract
```

The architectural sentence that must stay true: **the neural model proposes
structured evidence and symbolic hypotheses; the deterministic engine executes
them and uses Bayesian inference to decide what the evidence supports.**

## 3. Deterministic Bayesian responsibilities

The `faultline_core` engine — never the model — computes:

- transparent priors `P(h)` (`priors.py`: `uniform` | `configured`);
- per-observation likelihood `P(D_i | h)` from final-answer agreement, step-feature
  agreement, and reading uncertainty (`likelihood.py`);
- reading-uncertainty marginalization `P(D_i|h) = Σ_r P(D_i|h,r)P(r)`;
- log-space posterior with log-sum-exp normalization (`bayesian.py`);
- posterior entropy, top-two margin, answer/step reproduction rate;
- abstention decisions and reasons;
- exact expected information gain over executable predictions.

Model self-confidence is **never** used as a probability. It is not an input to
priors or likelihoods.

## 4. Neural-model responsibilities (and hard limits)

May: transcribe visible work, extract intermediate lines + approved step features,
return alternative readings, nominate known hypothesis IDs, propose ≤3 new DSL
programs with short descriptions.

May **not**: assign the diagnosis, return the posterior, produce a mastery/trait
score, select an intervention by authority, execute code, use tools/web, or bypass
the symbolic executor / Bayesian engine / verifier. Strict Pydantic schemas with
`extra="forbid"` reject diagnosis language and stray fields.

## 5. API compatibility strategy

The frozen frontend (`apps/web-static/`) is byte-for-byte immutable. All new
information is **additive and optional**: new nested objects (e.g.
`diagnosis.bayesian`, `analysis_meta`) and new endpoints (`/v1/runtime`,
`/v1/models/health`). Existing field names, routes, status codes, and payload
meanings are preserved. Where the frozen UI cannot show a human-review step, low
transcription support **abstains** rather than guessing. A compatibility snapshot
test pins the shape the frontend consumes.

## 6. Runtime modes

`FAULTLINE_RUNTIME_MODE=fixture` (default-safe, deterministic, clearly synthetic) and
`FAULTLINE_RUNTIME_MODE=local_ai` (real local model via Ollama). In `local_ai`, any
model failure returns a clear recoverable error or abstention — **never** a silent
fixture substitution.

## 7. Dataset strategy

Acquire a small (25–30 image) legally-usable public handwriting subset for
transcription evaluation only, with recorded provenance/license/checksums and no
PII. If no clearly-licensed source is available, mark the dataset gate blocked,
keep the allowlisted fetch script + metadata, and skip dataset tests with a clear
reason. Synthetic fixtures remain the labelled regression set for the deterministic
engine. Public transcription data never stands in for classroom or end-to-end
diagnosis accuracy.

## 8. Privacy boundary

Worksheet bytes and crops stay in memory; never logged, never written to static
dirs, never in the release ZIP. Runtime model calls go only to a loopback (or
explicitly opted-in private) host, with tools/web disabled, structured output only,
and no secrets/paths in prompts. Model errors are redacted before reaching clients.

## 9. Test strategy

Layered and mocked-transport (no running Ollama required for CI):
neural-adapter, reading-consensus, hypothesis-generation, Bayesian math,
novelty/verifier, runtime-mode, API-compatibility, dataset-provenance, frontend-freeze,
release. Existing 33 tests must keep passing.

## 10. Rollback strategy

`local_ai` is opt-in; unset/`fixture` restores exact v0.2.0 behavior. The neural
layers are isolated modules; disabling them (mode switch) leaves the deterministic
core, proof flow, and frontend untouched. No known-hypothesis is ever removed from
the candidate set, so a bad model run degrades to the deterministic baseline, never
below it.

## 11. Explicit non-claims

No perfect handwriting recognition; no classroom/learning-impact accuracy; no
causal improvement; no disability/language/identity inference; no production
readiness for identifiable student data; model nominations are **not** the Bayesian
conclusion; synthetic metrics are not public-dataset metrics; public transcription
metrics do not prove end-to-end diagnosis; a perfect rubric score is never guaranteed.

## 12. Phase map

P0 baseline+freeze · P1 runtime/health · P2 dataset · P3 vision transcription ·
P4 hypothesis generation · P5 Bayesian engine · P6 verifier-gated novelty ·
P7 evaluation · P8 API integration · P9 security · P10 build/release · P11 tests ·
P12 docs · P13 red-team+release.

## 13. Git / commit ownership

Claude Code makes **no** commits, branches, tags, or history changes. All work is
left unstaged for Rahul to review and commit manually. (The prompt's suggestion to
create `feature/neuro-symbolic-bayesian-ai` is superseded by the explicit
human-owned Git constraint: work stays on the checked-out branch.)
