# Model Card — Faultline local neural components

Faultline is a **neuro-symbolic** system. The neural model is load-bearing for
perception and hypothesis proposal, but it has **no diagnostic authority**. This
card describes the neural components; the decision logic is the deterministic
Bayesian engine documented in [bayesian_inference.md](../architecture/bayesian_inference.md).

## Models

| Role | Default model | Where it runs | Purpose |
|---|---|---|---|
| Vision | `qwen3-vl:4b` (configurable) | Local Ollama (loopback only) | Transcribe visible handwritten work into structured evidence |
| Hypothesis | `qwen3-vl:4b` (configurable) | Local Ollama (loopback only) | Nominate known hypothesis ids + propose ≤3 restricted-DSL programs |

No hosted API key is required or accepted for these roles. Model names are
configurable via `FAULTLINE_VISION_MODEL` / `FAULTLINE_HYPOTHESIS_MODEL`.

## Inputs

- Vision: the smallest sufficient crop of one answer region, across up to
  `FAULTLINE_TRANSCRIPTION_PASSES` deterministic preprocessing views. No page
  context, names, filenames, tokens, or environment data.
- Hypothesis: normalized structured observations only (`{n1,d1,n2,d2}`, observed
  answer string, approved step features) + the known-hypothesis list. No image
  bytes, ids, or PII.

## Outputs (strictly schema-validated, `extra="forbid"`)

- Vision → `TranscriptionEvidence`: `visible_expression, final_answer,
  intermediate_lines, step_features (approved vocab), legibility, uncertain_tokens`.
- Hypothesis → `HypothesisProposalBatch`: `known_hypothesis_ids`, `proposals`
  (`description` + restricted-DSL `expression`). **No** diagnosis, posterior, or score field exists.

## What the model must NOT do

Assign the final diagnosis; return the posterior; produce a mastery/trait/identity
score; select an intervention by authority; execute code; use tools or the web;
bypass the symbolic executor, Bayesian engine, or verifier; or provide a
self-confidence value treated as a calibrated probability.

## Determinism

Calls use `temperature=0` and a fixed `seed` where supported. The deterministic
reading-consensus and Bayesian layers do not depend on model self-confidence, so
the diagnosis is reproducible even though a neural model is in the loop.

## Evaluation

See [EVALUATION_CARD.md](EVALUATION_CARD.md). Transcription is evaluated on a
licensed public symbol subset (HASYv2, ODbL); the deterministic engine on the
labelled synthetic fixture; proposals on a controlled battery. End-to-end
image→procedure accuracy is not claimed on public data (no procedure labels exist).

## Known limitations

- No verified handwriting accuracy; small local VLMs vary by handwriting quality.
- The public symbol subset is 32×32 single symbols, not full worksheets.
- Not production-ready for identifiable student data.
- A perfect score / perfect recognition is never claimed.
