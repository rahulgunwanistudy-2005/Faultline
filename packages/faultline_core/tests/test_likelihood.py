from fractions import Fraction

import pytest

from faultline_core import (
    AnswerCandidate,
    FractionProblem,
    Observation,
    answer_likelihood,
    step_likelihood,
)
from faultline_core.likelihood import LikelihoodParams

PARAMS = LikelihoodParams().validated()


def _obs(value: Fraction, confidence: float = 0.99, steps=()) -> Observation:
    return Observation.exact(FractionProblem("p1", 1, 2, 1, 3), value, confidence, steps)


def test_answer_match_beats_mismatch() -> None:
    matched = answer_likelihood(Fraction(2, 5), _obs(Fraction(2, 5)), PARAMS)
    mismatched = answer_likelihood(Fraction(5, 6), _obs(Fraction(2, 5)), PARAMS)
    assert matched > mismatched
    assert matched > 0.8
    assert mismatched < 0.2


def test_mismatch_is_never_zero() -> None:
    # A single recognition error must not destroy all evidence.
    assert answer_likelihood(Fraction(5, 6), _obs(Fraction(2, 5)), PARAMS) > 0.0


def test_null_prediction_returns_flat_likelihood() -> None:
    assert answer_likelihood(None, _obs(Fraction(2, 5)), PARAMS) == PARAMS.null_item_probability


def test_marginalization_over_two_readings() -> None:
    problem = FractionProblem("p1", 1, 2, 1, 3)
    observation = Observation(
        problem,
        (AnswerCandidate(Fraction(2, 5), 0.5), AnswerCandidate(Fraction(5, 6), 0.4)),
    )
    like = answer_likelihood(Fraction(2, 5), observation, PARAMS)
    # Between full-match and full-mismatch because the reading is split.
    assert PARAMS.answer_mismatch_probability < like < PARAMS.answer_match_probability


def test_fully_unreadable_observation_is_neutral() -> None:
    problem = FractionProblem("p1", 1, 2, 1, 3)
    observation = Observation(problem, (AnswerCandidate(Fraction(2, 5), 0.0),))
    like = answer_likelihood(Fraction(2, 5), observation, PARAMS)
    assert like == pytest.approx(PARAMS.unreadable_neutral_probability)


def test_step_likelihood_match_and_contradiction() -> None:
    signature = frozenset({"numerators_added", "denominators_added"})
    consistent = step_likelihood(frozenset({"numerators_added"}), signature, PARAMS)
    contradicting = step_likelihood(frozenset({"common_denominator"}), signature, PARAMS)
    assert consistent > contradicting
    assert step_likelihood(frozenset(), signature, PARAMS) == 1.0


def test_params_reject_out_of_range() -> None:
    with pytest.raises(ValueError):
        LikelihoodParams(answer_match_probability=1.5).validated()
    with pytest.raises(ValueError):
        LikelihoodParams(step_mismatch_probability=0.0).validated()
