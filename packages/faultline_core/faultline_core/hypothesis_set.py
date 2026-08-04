"""The executable candidate set for Bayesian inference.

Unifies three kinds of hypothesis into one executable abstraction:

* **known** procedures from the reference library (``malrules.HYPOTHESES``);
* **provisional** model-proposed procedures that passed the deterministic
  verifier (restricted-DSL programs);
* the explicit **no_consistent_procedure** component, which predicts nothing.

A neural model can *nominate* known ids or *propose* new programs, but it can
never remove a known hypothesis from this set. The set is always built from the
full known library first.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable

from .domain import FractionProblem
from .dsl import evaluate
from .malrules import HYPOTHESES, Hypothesis

NULL_HYPOTHESIS_ID = "no_consistent_procedure"


@dataclass(frozen=True)
class Candidate:
    id: str
    label: str
    predict_fn: Callable[[FractionProblem], Fraction | None]
    step_signature: frozenset[str] = frozenset()
    source: str = "known"  # known | provisional | null
    expression: dict[str, Any] | None = None

    def predict(self, problem: FractionProblem) -> Fraction | None:
        return self.predict_fn(problem)

    @property
    def is_known(self) -> bool:
        return self.source == "known"

    @property
    def is_provisional(self) -> bool:
        return self.source == "provisional"


def _known_candidate(hypothesis: Hypothesis) -> Candidate:
    return Candidate(
        id=hypothesis.id,
        label=hypothesis.short_label,
        predict_fn=hypothesis.predict,
        step_signature=hypothesis.step_signature,
        source="known",
    )


def _dsl_predictor(expression: dict[str, Any]) -> Callable[[FractionProblem], Fraction | None]:
    def predict(problem: FractionProblem) -> Fraction | None:
        environment = {"n1": problem.n1, "d1": problem.d1, "n2": problem.n2, "d2": problem.d2}
        try:
            value = evaluate(expression, environment)
        except (ValueError, ZeroDivisionError):
            return None
        return value if isinstance(value, Fraction) else Fraction(value)

    return predict


@dataclass(frozen=True)
class ProvisionalCandidate:
    id: str
    label: str
    expression: dict[str, Any]
    step_signature: frozenset[str] = field(default_factory=frozenset)


def build_candidate_set(
    provisional: list[ProvisionalCandidate] | None = None,
    *,
    known: tuple[Hypothesis, ...] = HYPOTHESES,
    include_null: bool = True,
) -> list[Candidate]:
    """Assemble the executable candidate set (known library first, always)."""
    candidates: list[Candidate] = [_known_candidate(h) for h in known]
    for item in provisional or []:
        candidates.append(
            Candidate(
                id=item.id,
                label=item.label,
                predict_fn=_dsl_predictor(item.expression),
                step_signature=item.step_signature,
                source="provisional",
                expression=item.expression,
            )
        )
    if include_null:
        candidates.append(
            Candidate(
                id=NULL_HYPOTHESIS_ID,
                label="No consistent procedure",
                predict_fn=lambda _problem: None,
                source="null",
            )
        )
    return candidates
