# AI/ML Proof — how Faultline actually uses AI

This document answers, with pointers to runtime code and tests, exactly what the
AI does and does not do. It is engineering truth. Nothing here claims a perfect
score, perfect recognition, or classroom impact.

## 1. What local neural model runs?

A local vision-language model, default `qwen3-vl:4b` (configurable via
`FAULTLINE_VISION_MODEL` / `FAULTLINE_HYPOTHESIS_MODEL`). It plays two roles:
perception (transcription) and bounded hypothesis proposal.

## 2. Where does it run?

Entirely locally, through an [Ollama](https://ollama.com) runtime reached over a
**loopback-only** HTTP endpoint (`apps/api/faultline_api/adapters/ollama_client.py`).
The base URL is host-restricted in `config.py::_validated_model_base_url` — a
public host is rejected; a private-range host requires an explicit opt-in.

## 3. Why is no API key needed?

The provider is a local runtime, not a hosted service. There is no code path that
reads or requires an OpenAI/Anthropic/Google/Featherless key. `config.py` only
recognizes `FAULTLINE_MODEL_PROVIDER=ollama`.

## 4. What image evidence does it receive?

The smallest sufficient crop of one answer region, across up to
`FAULTLINE_TRANSCRIPTION_PASSES` deterministic in-memory preprocessing views
(`services/transcription.py::preprocess_views`). No page context, names,
filenames, tokens, or environment data. Crops are never persisted or logged.

## 5. What structured transcription does it return?

A strictly schema-validated `TranscriptionEvidence`
(`schemas/model_outputs.py`, `extra="forbid"`): `visible_expression`,
`final_answer`, `intermediate_lines`, `step_features` (approved vocabulary only),
`legibility`, `uncertain_tokens`. Multiple views are combined by the deterministic
reading-consensus layer (`services/reading_consensus.py`), which derives an
**engineering** support score from cross-view agreement and exact fraction
parsing — never from the model's self-reported confidence.

## 6. What symbolic hypotheses may it propose?

Zero or more known-hypothesis id nominations plus up to
`FAULTLINE_MAX_HYPOTHESIS_PROPOSALS` (default 3) new procedures expressed as
restricted-DSL programs (`schemas/model_outputs.py::HypothesisProposalBatch`,
`services/hypothesis_generation.py`).

## 7. What operations are permitted in the DSL?

Variables `n1, d1, n2, d2` and operations `add, sub, mul, lcm, fraction`
(`packages/faultline_core/faultline_core/dsl.py`). No strings-as-logic, item ids,
conditionals, lookups, imports, I/O, or code. Depth and node counts are bounded.

## 8. How does the deterministic Bayesian engine compute the posterior?

`P(h | D) ∝ P(h) · Π_i P(D_i | h)`, in numerically stable log space with
log-sum-exp normalization (`packages/faultline_core/faultline_core/bayesian.py`).
See [bayesian_inference.md](architecture/bayesian_inference.md).

## 9. Why is the model not the diagnostic authority?

There is no field on any model-output schema for a diagnosis, a chosen
hypothesis, or a probability. Nominations are hints; the engine always evaluates
the **full known library** regardless (`hypothesis_set.build_candidate_set`). A
proposal enters the candidate set only after the deterministic verifier accepts
it. Tests: `test_hypothesis_generation.py::test_model_score_never_becomes_posterior`,
`test_known_nomination_kept_as_hint_only`.

## 10. How are priors and likelihoods defined?

Priors: transparent `uniform` (default) or validated `configured`
(`priors.py`) — never model-derived. Likelihoods: a final-answer term marginalized
over reading candidates and a per-feature step term, with conservative,
configurable, non-zero probabilities (`likelihood.py`). Every value appears in
evaluation metadata (`BayesianResult.as_metadata`).

## 11. How is transcription uncertainty marginalized?

`P(D_i | h) = Σ_r P(r) · P(D_i | h, r)` over candidate readings, including a
residual "unreadable" mass with a neutral likelihood
(`likelihood.py::answer_likelihood`, `_reading_masses`). Tests:
`test_uncertainty.py`.

## 12. How does the system abstain?

`bayesian.py::_abstention` withholds a named diagnosis when any gate fails: too
few items, low mean transcription support, high posterior entropy, small top-two
margin, or insufficient reproduction. It returns explicit reasons **and** what
additional evidence is needed. In `local_ai` mode, an unavailable model / timeout
/ malformed output yields a clear error or abstention — never a fixture fallback
(`services/background_jobs.py`, `test_local_ai_jobs.py::test_local_ai_failure_has_no_fixture_fallback`).

## 13. How is a novel symbolic hypothesis verified?

`synthesis.py::verify_symbolic_hypothesis` runs schema/DSL validity, complexity
limits, fit reproduction, held-out validation reproduction, counterexample-bank
execution, output-range sanity, and novelty against known behavioural signatures
(`novelty.py`). Accepted candidates are labelled
`provisional_verified_symbolic_hypothesis` and never added to the permanent
library. Tests: `test_synthesis_validation.py`, `test_novelty.py`.

## 14. What dataset was used and under what license?

HASYv2 (Martin Thoma), 28-image subset, **ODC Open Database License v1.0**,
DOI 10.5281/zenodo.259444. Provenance, per-image SHA-256, and PII review are
recorded in `data/evaluation/public_handwriting_subset/`. No PII is retained.

## 15. Which evaluation layers are real, synthetic, or unavailable?

- Layer A (local transcription): **PUBLIC** HASYv2, transcription only — runs
  only with a local model, otherwise reports UNAVAILABLE honestly.
- Layer B (Bayesian engine): **SYNTHETIC** fixture — real, reproducible,
  deterministic (top-1 100% on the synthetic set).
- Layer C (end-to-end image→procedure): **UNAVAILABLE by design** (no public
  procedure labels); exercised structurally by mocked-model integration tests.
- Layer D (neuro-symbolic proposals): **CONTROLLED** deterministic battery.

See [evaluation/EVALUATION_CARD.md](evaluation/EVALUATION_CARD.md).

## 16. What remains unproven?

Handwriting recognition accuracy in the field; end-to-end image→procedure
accuracy on real worksheets (no labelled public set exists); any classroom or
learning-impact effect; calibration at scale. These are explicitly **not** claimed.
