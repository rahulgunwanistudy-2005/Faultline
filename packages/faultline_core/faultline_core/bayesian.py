"""Explicit deterministic Bayesian inference over executable procedures.

Computes ``P(h | D) ∝ P(h) · Π_i P(D_i | h)`` in numerically stable log space
with log-sum-exp normalization. Every input is deterministic structured evidence
and a transparent configuration; **no model self-confidence is used as a
probability**.

Outputs the full posterior plus the diagnostics the rubric requires: top
hypothesis, top-two margin, posterior entropy, answer/step reproduction rates,
evidence count, prior mode/config, and explicit abstention reasons.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from math import exp, isinf, log, log2
from typing import Iterable, Mapping, Sequence

from .domain import Observation
from .hypothesis_set import NULL_HYPOTHESIS_ID, Candidate, build_candidate_set
from .likelihood import LikelihoodParams, answer_likelihood, step_likelihood
from .priors import build_prior


@dataclass(frozen=True)
class BayesianParams:
    prior_mode: str = "uniform"
    prior_weights: Mapping[str, float] | None = None
    likelihood: LikelihoodParams = field(default_factory=LikelihoodParams)
    # Abstention gates
    min_items: int = 5
    min_mean_support: float = 0.55
    min_reproduction: float = 0.70
    abstention_entropy_threshold: float = 1.20
    top_two_margin_threshold: float = 0.15


@dataclass(frozen=True)
class EvidenceRow:
    problem_id: str
    best_observed: str
    predicted: str
    matched: bool
    answer_likelihood: float
    step_likelihood: float


@dataclass(frozen=True)
class BayesianResult:
    posterior: dict[str, float]
    ranked: list[tuple[str, float]]
    top_hypothesis: str
    top_posterior: float
    top_two_margin: float
    entropy_bits: float
    answer_reproduction: dict[str, float]
    step_reproduction: dict[str, float]
    evidence: dict[str, tuple[EvidenceRow, ...]]
    evidence_count: int
    mean_support: float
    prior_mode: str
    prior: dict[str, float]
    abstained: bool
    state: str
    reasons: list[str]
    needed_evidence: list[str]

    def as_metadata(self) -> dict[str, object]:
        """Compact, JSON-safe technical snapshot for additive API fields."""
        return {
            "state": self.state,
            "top_hypothesis": self.top_hypothesis,
            "top_posterior": round(self.top_posterior, 6),
            "top_two_margin": round(self.top_two_margin, 6),
            "entropy_bits": round(self.entropy_bits, 6),
            "evidence_count": self.evidence_count,
            "mean_support": round(self.mean_support, 6),
            "prior_mode": self.prior_mode,
            "answer_reproduction": {k: round(v, 6) for k, v in self.answer_reproduction.items()},
            "posterior": [
                {"id": hid, "probability": round(prob, 6)} for hid, prob in self.ranked
            ],
            "abstained": self.abstained,
            "reasons": list(self.reasons),
            "needed_evidence": list(self.needed_evidence),
        }


def _best_reading(observation: Observation) -> tuple[Fraction, float]:
    best = max(observation.candidates, key=lambda candidate: candidate.confidence)
    return best.value, best.confidence


def _entropy_bits(probabilities: Iterable[float]) -> float:
    return -sum(p * log2(p) for p in probabilities if p > 0)


def infer_bayesian(
    observations: Sequence[Observation],
    candidates: Sequence[Candidate] | None = None,
    params: BayesianParams | None = None,
) -> BayesianResult:
    observations = tuple(observations)
    if not observations:
        raise ValueError("at least one observation is required")
    params = params or BayesianParams()
    likelihood_params = params.likelihood.validated()
    candidates = list(candidates) if candidates is not None else build_candidate_set()
    if not candidates:
        raise ValueError("at least one candidate hypothesis is required")

    hypothesis_ids = [candidate.id for candidate in candidates]
    prior = build_prior(params.prior_mode, hypothesis_ids, params.prior_weights)

    log_scores: dict[str, float] = {}
    evidence: dict[str, tuple[EvidenceRow, ...]] = {}
    answer_reproduction: dict[str, float] = {}
    step_reproduction: dict[str, float] = {}

    for candidate in candidates:
        log_score = log(prior[candidate.id])
        rows: list[EvidenceRow] = []
        answer_matches = 0
        step_matches = 0
        step_items = 0
        for observation in observations:
            predicted = candidate.predict(observation.problem)
            a_like = answer_likelihood(predicted, observation, likelihood_params)
            s_like = step_likelihood(
                observation.step_features, candidate.step_signature, likelihood_params
            )
            log_score += log(a_like) + log(s_like)
            best_value, _ = _best_reading(observation)
            matched = predicted is not None and best_value == predicted
            answer_matches += int(matched)
            if observation.step_features:
                step_items += 1
                if observation.step_features & candidate.step_signature:
                    step_matches += 1
            rows.append(
                EvidenceRow(
                    problem_id=observation.problem.id,
                    best_observed=str(best_value),
                    predicted="—" if predicted is None else str(predicted),
                    matched=matched,
                    answer_likelihood=a_like,
                    step_likelihood=s_like,
                )
            )
        log_scores[candidate.id] = log_score
        evidence[candidate.id] = tuple(rows)
        answer_reproduction[candidate.id] = answer_matches / len(observations)
        step_reproduction[candidate.id] = (step_matches / step_items) if step_items else 0.0

    posterior = _normalize_log_scores(log_scores)
    ranked = sorted(posterior.items(), key=lambda kv: (-kv[1], kv[0]))
    top_id, top_posterior = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else 0.0
    margin = top_posterior - second
    entropy = _entropy_bits(posterior.values())
    mean_support = _mean_support(observations)

    state, reasons, needed = _abstention(
        top_id=top_id,
        evidence_count=len(observations),
        entropy=entropy,
        margin=margin,
        mean_support=mean_support,
        top_reproduction=answer_reproduction.get(top_id, 0.0),
        params=params,
    )

    return BayesianResult(
        posterior=posterior,
        ranked=ranked,
        top_hypothesis=top_id,
        top_posterior=top_posterior,
        top_two_margin=margin,
        entropy_bits=entropy,
        answer_reproduction=answer_reproduction,
        step_reproduction=step_reproduction,
        evidence=evidence,
        evidence_count=len(observations),
        mean_support=mean_support,
        prior_mode=params.prior_mode,
        prior=prior,
        abstained=state != "named_diagnosis",
        state=state,
        reasons=reasons,
        needed_evidence=needed,
    )


def _normalize_log_scores(log_scores: Mapping[str, float]) -> dict[str, float]:
    maximum = max(log_scores.values())
    if isinf(maximum):
        raise ValueError("degenerate log scores")
    weights = {key: exp(value - maximum) for key, value in log_scores.items()}
    normalizer = sum(weights.values())
    return {key: value / normalizer for key, value in weights.items()}


def _mean_support(observations: Sequence[Observation]) -> float:
    supports = [max(c.confidence for c in obs.candidates) for obs in observations]
    return sum(supports) / len(supports)


def _abstention(
    *,
    top_id: str,
    evidence_count: int,
    entropy: float,
    margin: float,
    mean_support: float,
    top_reproduction: float,
    params: BayesianParams,
) -> tuple[str, list[str], list[str]]:
    reasons: list[str] = []
    needed: list[str] = []
    if evidence_count < params.min_items:
        reasons.append("too_few_items")
        needed.append("collect at least a few more visible items")
    if mean_support < params.min_mean_support:
        reasons.append("low_transcription_support")
        needed.append("re-scan or review low-confidence readings")
    if entropy > params.abstention_entropy_threshold:
        reasons.append("posterior_entropy_too_high")
        needed.append("ask a question that separates the leading procedures")
    if margin < params.top_two_margin_threshold:
        reasons.append("top_two_margin_too_small")
        needed.append("ask a question where the top two procedures disagree")
    if top_id != NULL_HYPOTHESIS_ID and top_reproduction < params.min_reproduction:
        reasons.append("insufficient_reproduction")
        needed.append("the leading procedure does not reproduce enough answers yet")
    state = "named_diagnosis" if not reasons else "more_evidence_needed"
    return state, reasons, needed


def expected_information_gain(
    problem,
    posterior: Mapping[str, float],
    candidates: Sequence[Candidate],
) -> float:
    """Exact expected reduction in posterior entropy from observing ``problem``.

    Hypotheses that predict the same answer form one outcome group; a problem
    where all live hypotheses agree yields ~0 gain.
    """
    predictor = {candidate.id: candidate for candidate in candidates}
    active = {
        hid: prob
        for hid, prob in posterior.items()
        if hid in predictor and prob > 0 and predictor[hid].predict(problem) is not None
    }
    total = sum(active.values())
    if total <= 0:
        return 0.0
    active = {hid: prob / total for hid, prob in active.items()}
    current = _entropy_bits(active.values())
    groups: dict[str, list[float]] = {}
    for hid, prob in active.items():
        answer = str(predictor[hid].predict(problem))
        groups.setdefault(answer, []).append(prob)
    expected = 0.0
    for masses in groups.values():
        mass = sum(masses)
        expected += mass * _entropy_bits(value / mass for value in masses)
    return current - expected
