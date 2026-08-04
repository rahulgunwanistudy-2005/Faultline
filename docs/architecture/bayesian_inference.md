# Deterministic Bayesian inference

Implemented in `packages/faultline_core/faultline_core/` across `priors.py`,
`likelihood.py`, `hypothesis_set.py`, and `bayesian.py`. Pure Python, no web/model
dependencies, exact rational arithmetic for math, stable log-space for aggregation.

## The model

For a candidate set of executable hypotheses `H` and observed structured evidence
`D = {D_1 … D_n}`:

```
log P(h | D) = log P(h) + Σ_i log P(D_i | h) − log Z
```

`Z` is computed with log-sum-exp for numerical stability.

## Priors `P(h)` — `priors.py`

- `uniform` (default): equal mass over the candidate set.
- `configured`: explicit non-negative weights, normalized; unlisted ids receive
  the smallest listed weight (never zero) so nothing is eliminated.

Priors are never model-derived and always appear in evaluation metadata.

## Likelihood `P(D_i | h)` — `likelihood.py`

Two channels multiply:

1. **Final-answer**, marginalized over candidate readings:
   `P(D_i | h) = Σ_r P(r)·P(D_i | h, r)`, where readings `r` are weighted by
   consensus support with a residual "unreadable" mass at a neutral likelihood.
   A match uses `answer_match_probability` (0.90), a mismatch
   `answer_mismatch_probability` (0.08) — **never zero**, so one recognition error
   cannot destroy all evidence.
2. **Step features**: a per-feature Bernoulli factor —
   `step_match_probability` (0.80) when a feature is consistent with the
   hypothesis signature, `step_mismatch_probability` (0.30) when it contradicts.
   No observed features → neutral factor 1.0.

A hypothesis that predicts nothing (the explicit `no_consistent_procedure`
component) contributes a flat `null_item_probability` (0.25) per item.

## Candidate set — `hypothesis_set.py`

Always the full known library first, plus any verifier-accepted provisional
proposals, plus the null component. The neural model can add candidates (via
verified proposals) but can never remove a known hypothesis.

## Outputs — `bayesian.py::BayesianResult`

Full posterior, ranked list, top hypothesis, top-two margin, posterior entropy
(bits), answer/step reproduction rates, evidence count, mean support, prior mode
+ config, and the abstention decision (state + reasons + needed evidence).

## Abstention — `bayesian.py::_abstention`

Named diagnosis withheld if any of: `too_few_items`, `low_transcription_support`,
`posterior_entropy_too_high`, `top_two_margin_too_small`, `insufficient_reproduction`.

## Information gain — `bayesian.py::expected_information_gain`

`IG(item) = H(posterior) − E[H(posterior | response)]` over executable
predictions. Items where all live hypotheses predict the same answer yield ~0 gain.

## Determinism

Order-invariant and repeatable: identical inputs + configuration → identical
posteriors (`test_bayesian.py::test_order_invariance`, `test_deterministic_repeatability`).
No model self-confidence enters any term.
