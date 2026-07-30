from __future__ import annotations

from collections import defaultdict
from math import log2

from .domain import FractionProblem
from .malrules import HYPOTHESES, Hypothesis


def entropy(probabilities) -> float:
    return -sum(probability * log2(probability) for probability in probabilities if probability > 0)


def information_gain(
    problem: FractionProblem,
    posterior: dict[str, float],
    hypotheses: tuple[Hypothesis, ...] = HYPOTHESES,
) -> float:
    hypothesis_map = {hypothesis.id: hypothesis for hypothesis in hypotheses}
    active = {
        hypothesis_id: probability
        for hypothesis_id, probability in posterior.items()
        if hypothesis_id in hypothesis_map and probability > 0
    }
    total = sum(active.values())
    if total <= 0:
        return 0.0
    active = {key: value / total for key, value in active.items()}
    current_entropy = entropy(active.values())
    groups: dict[str, dict[str, float]] = defaultdict(dict)
    for hypothesis_id, probability in active.items():
        answer = str(hypothesis_map[hypothesis_id].predict(problem))
        groups[answer][hypothesis_id] = probability
    expected_entropy = 0.0
    for group in groups.values():
        mass = sum(group.values())
        conditioned = [probability / mass for probability in group.values()]
        expected_entropy += mass * entropy(conditioned)
    return current_entropy - expected_entropy


def rank_items(
    items: list[FractionProblem],
    posterior: dict[str, float],
    limit: int = 3,
) -> list[tuple[float, FractionProblem]]:
    ranked = sorted(
        ((information_gain(item, posterior), item) for item in items),
        key=lambda pair: (-pair[0], pair[1].id),
    )
    selected: list[tuple[float, FractionProblem]] = []
    used_pairs: set[tuple[int, int]] = set()
    for gain, item in ranked:
        pair = tuple(sorted((item.d1, item.d2)))
        if pair in used_pairs:
            continue
        selected.append((gain, item))
        used_pairs.add(pair)
        if len(selected) == limit:
            break
    return selected
