from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from typing import Callable

from .domain import FractionProblem


def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b)


@dataclass(frozen=True)
class Hypothesis:
    id: str
    short_label: str
    description: str
    action: str
    action_label: str
    provenance: str
    predict_fn: Callable[[FractionProblem], Fraction]
    step_signature: frozenset[str] = frozenset()

    def predict(self, problem: FractionProblem) -> Fraction:
        return self.predict_fn(problem)


def correct(problem: FractionProblem) -> Fraction:
    return Fraction(problem.n1, problem.d1) + Fraction(problem.n2, problem.d2)


def add_across(problem: FractionProblem) -> Fraction:
    return Fraction(problem.n1 + problem.n2, problem.d1 + problem.d2)


def keep_first_denominator(problem: FractionProblem) -> Fraction:
    return Fraction(problem.n1 + problem.n2, problem.d1)


def denominator_only_common(problem: FractionProblem) -> Fraction:
    return Fraction(problem.n1 + problem.n2, lcm(problem.d1, problem.d2))


def multiply_all(problem: FractionProblem) -> Fraction:
    return Fraction(problem.n1 * problem.n2, problem.d1 * problem.d2)


def scale_first_only(problem: FractionProblem) -> Fraction:
    common = lcm(problem.d1, problem.d2)
    return Fraction(problem.n1 * (common // problem.d1) + problem.n2, common)


HYPOTHESES: tuple[Hypothesis, ...] = (
    Hypothesis(
        "correct_common_denominator",
        "Procedure is intact",
        "Uses a common denominator and scales both numerators.",
        "confirm_or_extend",
        "Confirm, then extend",
        "reference-correct",
        correct,
        frozenset({"common_denominator", "both_numerators_scaled"}),
    ),
    Hypothesis(
        "add_across",
        "Adds straight across",
        "Adds the top numbers and bottom numbers separately.",
        "re_explain",
        "Re-explain the idea",
        "literature-grounded",
        add_across,
        frozenset({"numerators_added", "denominators_added"}),
    ),
    Hypothesis(
        "keep_first_denominator",
        "Keeps the first bottom number",
        "Adds the numerators but keeps the first denominator.",
        "re_explain",
        "Re-explain the idea",
        "teacher-observed",
        keep_first_denominator,
        frozenset({"numerators_added", "first_denominator_kept"}),
    ),
    Hypothesis(
        "denominator_only_common",
        "Changes only the denominator",
        "Finds a common denominator but does not scale the numerators.",
        "re_explain",
        "Re-explain the idea",
        "teacher-observed",
        denominator_only_common,
        frozenset({"common_denominator", "numerators_unscaled"}),
    ),
    Hypothesis(
        "multiply_all",
        "Multiplies instead of adding",
        "Multiplies across even though the operation is addition.",
        "re_explain",
        "Re-anchor the operation",
        "literature-grounded",
        multiply_all,
        frozenset({"numerators_multiplied", "denominators_multiplied"}),
    ),
    Hypothesis(
        "scale_first_only",
        "Scales one fraction only",
        "Scales only the first fraction before adding.",
        "re_explain",
        "Re-explain equivalence",
        "pilot-generated",
        scale_first_only,
        frozenset({"common_denominator", "first_numerator_scaled_only"}),
    ),
)

HYPOTHESIS_MAP = {hypothesis.id: hypothesis for hypothesis in HYPOTHESES}
