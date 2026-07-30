from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable

from .domain import FractionProblem
from .dsl import DSLValidationError, evaluate, validate


@dataclass(frozen=True)
class SynthesisExample:
    problem: FractionProblem
    observed: Fraction


@dataclass(frozen=True)
class VerifiedCandidate:
    description: str
    expression: dict[str, Any]
    reproduction: float
    counterexamples_passed: int
    provisional: bool = True


def _environment(problem: FractionProblem) -> dict[str, int]:
    return {"n1": problem.n1, "d1": problem.d1, "n2": problem.n2, "d2": problem.d2}


def verify_candidate(
    description: str,
    expression: dict[str, Any],
    examples: Iterable[SynthesisExample],
    minimum_reproduction: float = 0.70,
) -> VerifiedCandidate | None:
    """Validate and execute a model-proposed rule without evaluating Python code.

    The restricted DSL has no conditionals, item identifiers, strings, imports, or I/O,
    so a candidate cannot memorize a worksheet by problem ID.
    """
    validate(expression)
    examples = tuple(examples)
    if not examples:
        raise ValueError("At least one example is required")
    matches = 0
    for example in examples:
        predicted = evaluate(expression, _environment(example.problem))
        matches += int(predicted == example.observed)
    reproduction = matches / len(examples)
    if reproduction < minimum_reproduction:
        return None

    counterexample_bank = (
        FractionProblem("cx1", 1, 2, 1, 5),
        FractionProblem("cx2", 2, 3, 3, 7),
        FractionProblem("cx3", 3, 4, 1, 6),
        FractionProblem("cx4", 1, 8, 5, 12),
        FractionProblem("cx5", 4, 9, 2, 5),
        FractionProblem("cx6", 2, 11, 3, 8),
    )
    passed = 0
    for problem in counterexample_bank:
        try:
            value = evaluate(expression, _environment(problem))
            if isinstance(value, Fraction) and value.denominator != 0:
                passed += 1
        except (DSLValidationError, ZeroDivisionError, ValueError):
            continue
    if passed != len(counterexample_bank):
        return None
    return VerifiedCandidate(
        description=description.strip()[:180],
        expression=expression,
        reproduction=reproduction,
        counterexamples_passed=passed,
    )
