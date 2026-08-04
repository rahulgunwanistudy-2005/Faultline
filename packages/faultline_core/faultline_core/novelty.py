"""Novelty and complexity analysis for model-proposed symbolic procedures.

A proposal is *novel* only if its executable behaviour differs from every known
procedure across a fixed probe bank. Because the restricted DSL has no strings,
item ids, conditionals, or lookups, a proposal cannot memorize a worksheet — its
"signature" is purely a function of ``(n1, d1, n2, d2)``.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any

from .domain import FractionProblem
from .dsl import evaluate
from .malrules import HYPOTHESES, Hypothesis

# Fixed, diverse probe bank. Deterministic so signatures are reproducible.
PROBE_BANK: tuple[FractionProblem, ...] = (
    FractionProblem("probe1", 1, 2, 1, 3),
    FractionProblem("probe2", 2, 3, 1, 4),
    FractionProblem("probe3", 3, 5, 1, 2),
    FractionProblem("probe4", 1, 4, 2, 3),
    FractionProblem("probe5", 2, 5, 3, 7),
    FractionProblem("probe6", 3, 8, 1, 6),
    FractionProblem("probe7", 4, 9, 2, 5),
    FractionProblem("probe8", 2, 11, 3, 8),
)


def _environment(problem: FractionProblem) -> dict[str, int]:
    return {"n1": problem.n1, "d1": problem.d1, "n2": problem.n2, "d2": problem.d2}


def complexity(node: Any, depth: int = 0) -> tuple[int, int]:
    """Return ``(operation_count, max_depth)`` for a DSL expression."""
    if isinstance(node, int):
        return 0, depth
    if isinstance(node, dict) and "var" in node:
        return 0, depth
    if not isinstance(node, dict) or "op" not in node:
        return 0, depth
    ops = 1
    max_depth = depth
    for argument in node.get("args", []):
        child_ops, child_depth = complexity(argument, depth + 1)
        ops += child_ops
        max_depth = max(max_depth, child_depth)
    return ops, max_depth


def output_signature(expression: dict[str, Any], probes: tuple[FractionProblem, ...] = PROBE_BANK) -> tuple[str, ...] | None:
    """Deterministic behavioural signature, or ``None`` if it does not execute cleanly."""
    values: list[str] = []
    for problem in probes:
        try:
            value = evaluate(expression, _environment(problem))
        except (ValueError, ZeroDivisionError):
            return None
        fraction = value if isinstance(value, Fraction) else Fraction(value)
        values.append(str(fraction))
    return tuple(values)


def known_signatures(
    known: tuple[Hypothesis, ...] = HYPOTHESES,
    probes: tuple[FractionProblem, ...] = PROBE_BANK,
) -> dict[str, tuple[str, ...]]:
    return {
        hypothesis.id: tuple(str(hypothesis.predict(problem)) for problem in probes)
        for hypothesis in known
    }


def matches_known(
    signature: tuple[str, ...],
    known: tuple[Hypothesis, ...] = HYPOTHESES,
    probes: tuple[FractionProblem, ...] = PROBE_BANK,
) -> str | None:
    """Return the id of a known hypothesis with the same signature, else ``None``."""
    for hid, known_signature in known_signatures(known, probes).items():
        if known_signature == signature:
            return hid
    return None
