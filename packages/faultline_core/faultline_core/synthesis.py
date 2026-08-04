from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Iterable

from .domain import FractionProblem
from .dsl import DSLValidationError, evaluate, validate
from .malrules import HYPOTHESES, Hypothesis
from .novelty import PROBE_BANK, complexity, matches_known, output_signature

# Complexity ceilings for a *novel* proposal. Tighter than the raw DSL limits so
# proposals stay interpretable procedures, not obfuscated curve-fits.
MAX_PROPOSAL_OPERATIONS = 12
MAX_PROPOSAL_DEPTH = 6
MAX_ABS_OUTPUT = 1_000_000


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


@dataclass(frozen=True)
class ProposalVerification:
    """Full audit record for a model-proposed symbolic hypothesis."""

    accepted: bool
    reason: str | None
    description: str
    expression: dict[str, Any]
    reproduction: float = 0.0
    validation_reproduction: float | None = None
    counterexamples_passed: int = 0
    operations: int = 0
    depth: int = 0
    novelty_signature: tuple[str, ...] | None = None
    label: str = "provisional_verified_symbolic_hypothesis"


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


_COUNTEREXAMPLE_BANK: tuple[FractionProblem, ...] = (
    FractionProblem("cx1", 1, 2, 1, 5),
    FractionProblem("cx2", 2, 3, 3, 7),
    FractionProblem("cx3", 3, 4, 1, 6),
    FractionProblem("cx4", 1, 8, 5, 12),
    FractionProblem("cx5", 4, 9, 2, 5),
    FractionProblem("cx6", 2, 11, 3, 8),
)


def _reproduction(expression: dict[str, Any], examples: tuple[SynthesisExample, ...]) -> float:
    matches = 0
    for example in examples:
        predicted = evaluate(expression, _environment(example.problem))
        matches += int(predicted == example.observed)
    return matches / len(examples)


def verify_symbolic_hypothesis(
    description: str,
    expression: dict[str, Any],
    fit_examples: Iterable[SynthesisExample],
    validation_examples: Iterable[SynthesisExample] | None = None,
    *,
    known: tuple[Hypothesis, ...] = HYPOTHESES,
    min_reproduction: float = 0.70,
    validation_reproduction: float = 0.80,
) -> ProposalVerification:
    """Deterministically adjudicate a model-proposed symbolic procedure.

    Runs every gate and returns a full audit record with the first failing
    reason (or ``accepted=True``). Never mutates the known-rule library; an
    accepted proposal is labelled a *provisional* verified symbolic hypothesis.
    """
    description = description.strip()[:240]
    fit = tuple(fit_examples)
    validation = tuple(validation_examples) if validation_examples is not None else None

    def reject(reason: str, **extra: Any) -> ProposalVerification:
        return ProposalVerification(
            accepted=False, reason=reason, description=description, expression=expression, **extra
        )

    # 1. Schema + DSL validity
    try:
        validate(expression)
    except DSLValidationError as exc:
        return reject(f"invalid_dsl:{exc}")

    if not fit:
        return reject("no_fit_examples")

    # 2. Complexity limits
    operations, depth = complexity(expression)
    if operations > MAX_PROPOSAL_OPERATIONS or depth > MAX_PROPOSAL_DEPTH:
        return reject("too_complex", operations=operations, depth=depth)

    # 3. Fit reproduction
    reproduction = _reproduction(expression, fit)
    if reproduction < min_reproduction:
        return reject("insufficient_fit", reproduction=reproduction, operations=operations, depth=depth)

    # 4. Validation reproduction (held-out), when enough samples exist
    validation_score: float | None = None
    if validation:
        validation_score = _reproduction(expression, validation)
        if validation_score < validation_reproduction:
            return reject(
                "insufficient_validation",
                reproduction=reproduction,
                validation_reproduction=validation_score,
                operations=operations,
                depth=depth,
            )

    # 5. Counterexample execution + output-range sanity
    passed = 0
    for problem in _COUNTEREXAMPLE_BANK:
        try:
            value = evaluate(expression, _environment(problem))
        except (DSLValidationError, ZeroDivisionError, ValueError):
            return reject("counterexample_failed", reproduction=reproduction, operations=operations, depth=depth)
        fraction = value if isinstance(value, Fraction) else Fraction(value)
        if fraction.denominator == 0 or abs(fraction.numerator) > MAX_ABS_OUTPUT or fraction.denominator > MAX_ABS_OUTPUT:
            return reject("output_out_of_range", reproduction=reproduction, operations=operations, depth=depth)
        passed += 1

    # 6. Novelty against the known library
    signature = output_signature(expression, PROBE_BANK)
    if signature is None:
        return reject("nonexecutable_signature", reproduction=reproduction, operations=operations, depth=depth)
    duplicate = matches_known(signature, known, PROBE_BANK)
    if duplicate is not None:
        return reject(
            f"duplicate_of_known:{duplicate}",
            reproduction=reproduction,
            operations=operations,
            depth=depth,
            novelty_signature=signature,
        )

    return ProposalVerification(
        accepted=True,
        reason=None,
        description=description,
        expression=expression,
        reproduction=reproduction,
        validation_reproduction=validation_score,
        counterexamples_passed=passed,
        operations=operations,
        depth=depth,
        novelty_signature=signature,
    )
