"""Deterministic reading-consensus layer.

Turns several raw ``TranscriptionEvidence`` readings (from multiple preprocessing
views / passes) into a single consensus with an **engineering** support score.
The model's own words are never trusted as a probability: support is derived
only from cross-view agreement, exact fraction parsing, legibility, and
uncertainty counts.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction

from faultline_core import parse_fraction

from ..schemas.model_outputs import TranscriptionEvidence

_LEGIBILITY_WEIGHT = {"clear": 1.0, "partial": 0.7, "unreadable": 0.3}


@dataclass(frozen=True)
class ReadingCandidate:
    value: Fraction
    weight: float


@dataclass(frozen=True)
class ReadingConsensus:
    problem_id: str
    candidates: tuple[ReadingCandidate, ...]
    step_features: frozenset[str]
    support: float
    legibility: str
    resolved: bool
    needs_review: bool
    visible_expression: str = ""
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def best_value(self) -> Fraction | None:
        if not self.candidates:
            return None
        return max(self.candidates, key=lambda candidate: candidate.weight).value


def _safe_fraction(text: str) -> Fraction | None:
    try:
        return parse_fraction(text)
    except (ValueError, ZeroDivisionError):
        return None


def build_consensus(
    problem_id: str,
    readings: list[TranscriptionEvidence],
    *,
    auto_accept_threshold: float = 0.80,
    review_threshold: float = 0.55,
) -> ReadingConsensus:
    notes: list[str] = []
    passes = len(readings)
    if passes == 0:
        return ReadingConsensus(
            problem_id, (), frozenset(), 0.0, "unreadable", False, True, "", ("no_readings",)
        )

    visible_expression = _majority_expression(readings)

    parsed: list[Fraction] = []
    for reading in readings:
        value = _safe_fraction(reading.final_answer)
        if value is not None:
            parsed.append(value)

    if not parsed:
        return ReadingConsensus(
            problem_id, (), frozenset(), 0.0, "unreadable", False, True,
            visible_expression, ("no_parseable_answer",),
        )

    counts = Counter(str(value) for value in parsed)
    top_answer, top_count = counts.most_common(1)[0]
    parse_ratio = len(parsed) / passes
    agreement_ratio = top_count / len(parsed)

    legibility_weight = sum(
        _LEGIBILITY_WEIGHT.get(reading.legibility, 0.5) for reading in readings
    ) / passes
    mean_uncertain = sum(len(reading.uncertain_tokens) for reading in readings) / passes
    uncertainty_penalty = min(0.3, 0.1 * mean_uncertain)

    support = max(0.0, parse_ratio * agreement_ratio * legibility_weight - uncertainty_penalty)

    # Competing readings become candidates with agreement-derived weights, scaled
    # by overall support so a split, low-legibility reading yields low confidence.
    candidates: list[ReadingCandidate] = []
    for answer, count in counts.most_common():
        value = _safe_fraction(answer)
        if value is None:
            continue
        weight = round((count / len(parsed)) * support, 6)
        candidates.append(ReadingCandidate(value, weight))

    step_features = _majority_step_features(readings)
    legibility = _dominant_legibility(readings)
    if agreement_ratio < 1.0:
        notes.append(f"reading_split:{dict(counts)}")
    if mean_uncertain > 0:
        notes.append(f"uncertain_tokens:{round(mean_uncertain, 2)}")

    resolved = True
    needs_review = support < auto_accept_threshold
    if support < review_threshold:
        notes.append("below_review_threshold")

    return ReadingConsensus(
        problem_id=problem_id,
        candidates=tuple(candidates),
        step_features=step_features,
        support=round(support, 6),
        legibility=legibility,
        resolved=resolved,
        needs_review=needs_review,
        visible_expression=visible_expression,
        notes=tuple(notes),
    )


def _majority_step_features(readings: list[TranscriptionEvidence]) -> frozenset[str]:
    threshold = len(readings) / 2
    counter: Counter[str] = Counter()
    for reading in readings:
        counter.update(set(reading.step_features))
    return frozenset(feature for feature, count in counter.items() if count > threshold)


def _dominant_legibility(readings: list[TranscriptionEvidence]) -> str:
    counter = Counter(reading.legibility for reading in readings)
    return counter.most_common(1)[0][0]


def _majority_expression(readings: list[TranscriptionEvidence]) -> str:
    counter = Counter(
        reading.visible_expression.strip()
        for reading in readings
        if reading.visible_expression.strip()
    )
    return counter.most_common(1)[0][0] if counter else ""
