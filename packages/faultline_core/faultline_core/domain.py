from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Iterable
import re


@dataclass(frozen=True)
class FractionProblem:
    id: str
    n1: int
    d1: int
    n2: int
    d2: int
    operation: str = "+"
    form: str = "bare"

    def __post_init__(self) -> None:
        if self.d1 <= 0 or self.d2 <= 0:
            raise ValueError("Denominators must be positive")
        if self.operation != "+":
            raise ValueError("Faultline's competition build supports addition only")
        if self.form not in {"bare", "word", "visual"}:
            raise ValueError("form must be bare, word, or visual")

    @property
    def expression(self) -> str:
        return f"{self.n1}/{self.d1} + {self.n2}/{self.d2}"


@dataclass(frozen=True)
class AnswerCandidate:
    value: Fraction
    confidence: float

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be in [0, 1]")


@dataclass(frozen=True)
class Observation:
    problem: FractionProblem
    candidates: tuple[AnswerCandidate, ...]
    step_features: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.candidates:
            raise ValueError("At least one answer candidate is required")

    @classmethod
    def exact(
        cls,
        problem: FractionProblem,
        value: Fraction,
        confidence: float = 0.99,
        step_features: Iterable[str] = (),
    ) -> "Observation":
        return cls(problem, (AnswerCandidate(value, confidence),), frozenset(step_features))


PROBLEM_PATTERN = re.compile(
    r"^\s*(\d{1,4})\s*/\s*(\d{1,4})\s*\+\s*(\d{1,4})\s*/\s*(\d{1,4})\s*$"
)


def parse_problem(expression: str, problem_id: str = "p1") -> FractionProblem | None:
    """Parse a printed ``a/b + c/d`` expression into a problem, as written.

    Numerators/denominators are kept unreduced because the diagnosed procedures
    depend on the literal digits (e.g. ``add_across`` uses ``d1 + d2``). Returns
    ``None`` when the text is not a well-formed unlike/like-denominator sum.
    """
    match = PROBLEM_PATTERN.fullmatch(expression or "")
    if not match:
        return None
    n1, d1, n2, d2 = (int(group) for group in match.groups())
    if d1 <= 0 or d2 <= 0:
        return None
    try:
        return FractionProblem(problem_id, n1, d1, n2, d2)
    except ValueError:
        return None


FRACTION_PATTERN = re.compile(r"^[+-]?\d+(?:/[+-]?\d+)?$")


def parse_fraction(value: str) -> Fraction:
    cleaned = value.strip().replace(" ", "")
    if not FRACTION_PATTERN.fullmatch(cleaned):
        raise ValueError("Expected an integer or fraction such as 2/5")
    if "/" not in cleaned:
        return Fraction(int(cleaned), 1)
    numerator, denominator = cleaned.split("/", 1)
    if int(denominator) == 0:
        raise ValueError("Denominator cannot be zero")
    return Fraction(int(numerator), int(denominator))
