from __future__ import annotations

from dataclasses import dataclass
from math import exp, log
from typing import Iterable

from .domain import Observation
from .malrules import HYPOTHESES, Hypothesis


@dataclass(frozen=True)
class EvidenceRow:
    problem_id: str
    observed: str
    predicted: str
    matched: bool
    candidate_match_probability: float
    step_support: float


@dataclass(frozen=True)
class InferenceResult:
    posterior: dict[str, float]
    evidence: dict[str, tuple[EvidenceRow, ...]]
    scorable_items: int
    mean_ocr_confidence: float
    reproduction: dict[str, float]


def _candidate_likelihood(observation: Observation, hypothesis: Hypothesis) -> tuple[float, bool, str]:
    predicted = hypothesis.predict(observation.problem)
    total_confidence = sum(candidate.confidence for candidate in observation.candidates)
    if total_confidence <= 0:
        return 0.5, False, "unreadable"

    likelihood = 0.0
    matched = False
    observed = str(observation.candidates[0].value)
    for candidate in observation.candidates:
        weight = candidate.confidence / total_confidence
        same = candidate.value == predicted
        matched = matched or same
        base = 0.97 if same else 0.03
        adjusted = candidate.confidence * base + (1 - candidate.confidence) * 0.5
        likelihood += weight * adjusted
    return max(likelihood, 1e-12), matched, observed


def infer(
    observations: Iterable[Observation],
    hypotheses: tuple[Hypothesis, ...] = HYPOTHESES,
) -> InferenceResult:
    observations = tuple(observations)
    if not observations:
        raise ValueError("At least one observation is required")

    log_scores: dict[str, float] = {}
    evidence: dict[str, tuple[EvidenceRow, ...]] = {}
    reproduction: dict[str, float] = {}
    prior = log(1 / (len(hypotheses) + 1))

    for hypothesis in hypotheses:
        score = prior
        rows: list[EvidenceRow] = []
        matches = 0
        for observation in observations:
            likelihood, matched, observed = _candidate_likelihood(observation, hypothesis)
            step_support = 0.0
            if observation.step_features and hypothesis.step_signature:
                overlap = len(observation.step_features & hypothesis.step_signature)
                contradiction = len(observation.step_features - hypothesis.step_signature)
                step_support = 0.32 * overlap - 0.12 * contradiction
                likelihood *= exp(step_support)
            score += log(max(likelihood, 1e-12))
            matches += int(matched)
            rows.append(
                EvidenceRow(
                    problem_id=observation.problem.id,
                    observed=observed,
                    predicted=str(hypothesis.predict(observation.problem)),
                    matched=matched,
                    candidate_match_probability=likelihood,
                    step_support=step_support,
                )
            )
        log_scores[hypothesis.id] = score
        evidence[hypothesis.id] = tuple(rows)
        reproduction[hypothesis.id] = matches / len(observations)

    unknown_id = "no_consistent_procedure"
    log_scores[unknown_id] = prior + len(observations) * log(0.30)
    evidence[unknown_id] = tuple()
    reproduction[unknown_id] = 0.0

    maximum = max(log_scores.values())
    weights = {key: exp(value - maximum) for key, value in log_scores.items()}
    normalizer = sum(weights.values())
    posterior = {
        key: value / normalizer
        for key, value in sorted(weights.items(), key=lambda pair: pair[1], reverse=True)
    }
    confidences = [max(candidate.confidence for candidate in item.candidates) for item in observations]
    return InferenceResult(
        posterior=posterior,
        evidence=evidence,
        scorable_items=len(observations),
        mean_ocr_confidence=sum(confidences) / len(confidences),
        reproduction=reproduction,
    )


def confidence_gate(
    result: InferenceResult,
    min_items: int = 5,
    min_ocr: float = 0.85,
    min_top: float = 0.70,
    min_ratio: float = 3.0,
    min_reproduction: float = 0.70,
) -> dict[str, object]:
    ranked = list(result.posterior.items())
    top_id, top_probability = ranked[0]
    second_probability = ranked[1][1] if len(ranked) > 1 else 0.0
    ratio = float("inf") if second_probability == 0 else top_probability / second_probability
    reasons: list[str] = []
    if result.scorable_items < min_items:
        reasons.append("too_few_items")
    if result.mean_ocr_confidence < min_ocr:
        reasons.append("low_ocr_confidence")
    if top_probability < min_top:
        reasons.append("posterior_not_concentrated")
    if ratio < min_ratio:
        reasons.append("top_two_too_close")
    if top_id != "no_consistent_procedure" and result.reproduction.get(top_id, 0) < min_reproduction:
        reasons.append("insufficient_reproduction")
    return {
        "state": "named_diagnosis" if not reasons else "more_evidence_needed",
        "top_hypothesis": top_id,
        "top_posterior": top_probability,
        "top_to_second_ratio": ratio,
        "reasons": reasons,
    }
