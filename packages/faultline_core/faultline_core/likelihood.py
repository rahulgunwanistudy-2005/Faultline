"""Deterministic likelihood terms for Bayesian hypothesis inference.

Every term here is a plain probability computed from observed structured
evidence and a hypothesis's executable prediction. No model self-confidence
enters these functions.

Two evidence channels:

* **final-answer agreement**, marginalized over candidate readings
  ``P(D_i | h) = Σ_r P(r) · P(D_i | h, r)``;
* **intermediate step-feature agreement**, a per-feature Bernoulli factor.

Missing evidence contributes a neutral factor rather than a zero, so a single
recognition error cannot numerically destroy all evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .domain import Observation


@dataclass(frozen=True)
class LikelihoodParams:
    answer_match_probability: float = 0.90
    answer_mismatch_probability: float = 0.08
    unreadable_neutral_probability: float = 0.5
    # Flat per-item likelihood for a hypothesis that predicts nothing (the
    # explicit "no consistent procedure" component).
    null_item_probability: float = 0.25
    step_match_probability: float = 0.80
    step_mismatch_probability: float = 0.30

    def validated(self) -> "LikelihoodParams":
        for name, value in (
            ("answer_match_probability", self.answer_match_probability),
            ("answer_mismatch_probability", self.answer_mismatch_probability),
            ("unreadable_neutral_probability", self.unreadable_neutral_probability),
            ("null_item_probability", self.null_item_probability),
            ("step_match_probability", self.step_match_probability),
            ("step_mismatch_probability", self.step_mismatch_probability),
        ):
            if not 0.0 < value < 1.0:
                raise ValueError(f"{name} must be strictly within (0, 1); got {value}")
        return self


def _reading_masses(observation: Observation) -> list[tuple[Fraction | None, float]]:
    """Return (reading value, probability weight) including a residual unreadable mass."""
    total_conf = sum(candidate.confidence for candidate in observation.candidates)
    masses: list[tuple[Fraction | None, float]] = [
        (candidate.value, candidate.confidence) for candidate in observation.candidates
    ]
    residual = max(0.0, 1.0 - total_conf)
    masses.append((None, residual))
    normalizer = sum(weight for _, weight in masses)
    if normalizer <= 0:
        # Fully unreadable observation: a single neutral reading.
        return [(None, 1.0)]
    return [(value, weight / normalizer) for value, weight in masses]


def answer_likelihood(
    predicted: Fraction | None,
    observation: Observation,
    params: LikelihoodParams,
) -> float:
    """Marginalized probability of the observed answer under a hypothesis.

    ``predicted is None`` denotes a hypothesis that predicts no specific answer
    (the "no consistent procedure" component): it contributes a flat likelihood.
    """
    if predicted is None:
        return params.null_item_probability
    likelihood = 0.0
    for value, weight in _reading_masses(observation):
        if value is None:
            conditional = params.unreadable_neutral_probability
        elif value == predicted:
            conditional = params.answer_match_probability
        else:
            conditional = params.answer_mismatch_probability
        likelihood += weight * conditional
    return max(likelihood, 1e-12)


def step_likelihood(
    observed_features: frozenset[str],
    hypothesis_signature: frozenset[str],
    params: LikelihoodParams,
) -> float:
    """Per-feature Bernoulli factor over observed intermediate step features.

    Each observed feature is evidence: consistent with the hypothesis's signature
    (``step_match_probability``) or contradicting it (``step_mismatch_probability``).
    No observed features → neutral factor of 1.0 (missing evidence).
    """
    if not observed_features:
        return 1.0
    factor = 1.0
    for feature in observed_features:
        if feature in hypothesis_signature:
            factor *= params.step_match_probability
        else:
            factor *= params.step_mismatch_probability
    return max(factor, 1e-12)
