"""Reading-uncertainty marginalization behaviour in the Bayesian engine."""
from fractions import Fraction

from faultline_core import (
    AnswerCandidate,
    FractionProblem,
    HYPOTHESIS_MAP,
    Observation,
    infer_bayesian,
)


def _problems() -> list[FractionProblem]:
    return [
        FractionProblem("p1", 1, 2, 1, 3),
        FractionProblem("p2", 2, 3, 1, 4),
        FractionProblem("p3", 3, 5, 1, 2),
        FractionProblem("p4", 1, 4, 2, 3),
        FractionProblem("p5", 2, 5, 1, 3),
        FractionProblem("p6", 3, 8, 1, 6),
    ]


def test_split_readings_reduce_concentration() -> None:
    add = HYPOTHESIS_MAP["add_across"]
    correct = HYPOTHESIS_MAP["correct_common_denominator"]

    confident = infer_bayesian(
        [Observation.exact(p, add.predict(p), 0.97, add.step_signature) for p in _problems()]
    )
    split = infer_bayesian(
        [
            Observation(
                p,
                (
                    AnswerCandidate(add.predict(p), 0.55),
                    AnswerCandidate(correct.predict(p), 0.45),
                ),
            )
            for p in _problems()
        ]
    )
    assert confident.top_posterior > split.top_posterior
    assert split.top_hypothesis in {"add_across", "correct_common_denominator"}


def test_unreadable_observation_does_not_crash() -> None:
    problems = _problems()
    add = HYPOTHESIS_MAP["add_across"]
    obs = [Observation.exact(p, add.predict(p), 0.9, add.step_signature) for p in problems[:-1]]
    obs.append(Observation(problems[-1], (AnswerCandidate(Fraction(2, 5), 0.0),)))
    result = infer_bayesian(obs)
    assert sum(result.posterior.values()) > 0.99


def test_missing_step_features_are_neutral() -> None:
    add = HYPOTHESIS_MAP["add_across"]
    with_steps = infer_bayesian(
        [Observation.exact(p, add.predict(p), 0.97, add.step_signature) for p in _problems()]
    )
    without_steps = infer_bayesian(
        [Observation.exact(p, add.predict(p), 0.97) for p in _problems()]
    )
    # Both still identify add_across; step features only sharpen it.
    assert with_steps.top_hypothesis == without_steps.top_hypothesis == "add_across"
    assert with_steps.top_posterior >= without_steps.top_posterior
