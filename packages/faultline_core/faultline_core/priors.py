"""Transparent deterministic priors for Bayesian hypothesis inference.

Priors are never taken from a model. Two modes are supported:

* ``uniform`` — equal mass across the candidate set (the production default);
* ``configured`` — explicit, validated, documented weights.

Both return a normalized distribution over the exact set of hypothesis ids.
"""
from __future__ import annotations

from typing import Iterable, Mapping

PRIOR_MODES = ("uniform", "configured")


class PriorError(ValueError):
    pass


def uniform_prior(hypothesis_ids: Iterable[str]) -> dict[str, float]:
    ids = list(dict.fromkeys(hypothesis_ids))
    if not ids:
        raise PriorError("at least one hypothesis is required for a prior")
    mass = 1.0 / len(ids)
    return {hid: mass for hid in ids}


def configured_prior(
    hypothesis_ids: Iterable[str],
    weights: Mapping[str, float],
) -> dict[str, float]:
    """Normalize explicit non-negative weights over the candidate ids.

    Unlisted ids receive the smallest listed weight (never zero), so a configured
    prior can never silently eliminate a hypothesis from consideration.
    """
    ids = list(dict.fromkeys(hypothesis_ids))
    if not ids:
        raise PriorError("at least one hypothesis is required for a prior")
    for key, value in weights.items():
        if value < 0:
            raise PriorError(f"prior weight for {key!r} must be non-negative")
    positive = [value for value in weights.values() if value > 0]
    floor = min(positive) if positive else 1.0
    raw = {hid: float(weights.get(hid, floor)) for hid in ids}
    total = sum(raw.values())
    if total <= 0:
        raise PriorError("configured prior weights sum to zero")
    return {hid: value / total for hid, value in raw.items()}


def build_prior(
    mode: str,
    hypothesis_ids: Iterable[str],
    weights: Mapping[str, float] | None = None,
) -> dict[str, float]:
    if mode == "uniform":
        return uniform_prior(hypothesis_ids)
    if mode == "configured":
        if not weights:
            raise PriorError("configured prior mode requires weights")
        return configured_prior(hypothesis_ids, weights)
    raise PriorError(f"unknown prior mode: {mode!r}")
