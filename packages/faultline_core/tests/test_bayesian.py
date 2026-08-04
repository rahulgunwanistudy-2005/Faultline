from fractions import Fraction

import pytest

from faultline_core import (
    BayesianParams,
    FractionProblem,
    HYPOTHESIS_MAP,
    Observation,
    build_candidate_set,
    expected_information_gain,
    infer_bayesian,
)
from faultline_core.bayesian import _entropy_bits, _normalize_log_scores
from faultline_core.likelihood import LikelihoodParams


def _problems() -> list[FractionProblem]:
    return [
        FractionProblem("p1", 1, 2, 1, 3),
        FractionProblem("p2", 2, 3, 1, 4),
        FractionProblem("p3", 3, 5, 1, 2),
        FractionProblem("p4", 1, 4, 2, 3),
        FractionProblem("p5", 2, 5, 1, 3),
        FractionProblem("p6", 3, 8, 1, 6),
    ]


def _observations_for(rule_id: str, confidence: float = 0.97) -> list[Observation]:
    rule = HYPOTHESIS_MAP[rule_id]
    return [
        Observation.exact(p, rule.predict(p), confidence, rule.step_signature) for p in _problems()
    ]


def test_posterior_normalizes_to_one() -> None:
    result = infer_bayesian(_observations_for("add_across"))
    assert sum(result.posterior.values()) == pytest.approx(1.0)


def test_uniform_prior_recovers_generating_hypothesis() -> None:
    result = infer_bayesian(_observations_for("add_across"))
    assert result.top_hypothesis == "add_across"
    assert result.top_posterior > 0.9
    assert result.state == "named_diagnosis"


def test_multiplies_instead_of_adding_is_recovered() -> None:
    result = infer_bayesian(_observations_for("multiply_all"))
    assert result.top_hypothesis == "multiply_all"


def test_configured_prior_shifts_but_never_eliminates() -> None:
    obs = _observations_for("add_across")
    params = BayesianParams(
        prior_mode="configured",
        prior_weights={"correct_common_denominator": 100.0},
    )
    result = infer_bayesian(obs, params=params)
    # A strong wrong prior may be overcome by evidence, but every hypothesis keeps
    # non-zero mass — nothing is eliminated.
    assert all(prob > 0 for prob in result.posterior.values())
    assert "add_across" in result.posterior


def test_order_invariance() -> None:
    obs = _observations_for("keep_first_denominator")
    forward = infer_bayesian(obs)
    backward = infer_bayesian(list(reversed(obs)))
    for hid in forward.posterior:
        assert forward.posterior[hid] == pytest.approx(backward.posterior[hid])


def test_deterministic_repeatability() -> None:
    obs = _observations_for("add_across")
    a = infer_bayesian(obs).posterior
    b = infer_bayesian(obs).posterior
    assert a == b


def test_log_sum_exp_is_stable_with_many_items() -> None:
    rule = HYPOTHESIS_MAP["add_across"]
    problems = [FractionProblem(f"p{i}", 1, 2, 1, 3) for i in range(200)]
    obs = [Observation.exact(p, rule.predict(p), 0.97, rule.step_signature) for p in problems]
    result = infer_bayesian(obs)
    assert sum(result.posterior.values()) == pytest.approx(1.0)
    assert result.top_hypothesis == "add_across"


def test_entropy_and_margin() -> None:
    assert _entropy_bits([0.5, 0.5]) == pytest.approx(1.0)
    assert _entropy_bits([1.0]) == pytest.approx(0.0)
    result = infer_bayesian(_observations_for("add_across"))
    assert 0.0 <= result.entropy_bits
    assert result.top_two_margin == pytest.approx(
        result.ranked[0][1] - result.ranked[1][1]
    )


def test_abstains_on_too_few_items() -> None:
    obs = _observations_for("add_across")[:3]
    result = infer_bayesian(obs)
    assert result.state == "more_evidence_needed"
    assert "too_few_items" in result.reasons
    assert result.needed_evidence


def test_abstains_on_low_support() -> None:
    result = infer_bayesian(_observations_for("add_across", confidence=0.40))
    assert result.state == "more_evidence_needed"
    assert "low_transcription_support" in result.reasons


def test_null_hypothesis_wins_when_nothing_reproduces() -> None:
    # Random, mutually inconsistent answers should favour "no consistent procedure".
    problems = _problems()
    weird = [Fraction(7, 9), Fraction(1, 11), Fraction(5, 13), Fraction(3, 17), Fraction(9, 19), Fraction(2, 23)]
    obs = [Observation.exact(p, w, 0.9) for p, w in zip(problems, weird)]
    result = infer_bayesian(obs)
    assert result.top_hypothesis == "no_consistent_procedure"


def test_information_gain_zero_when_all_agree() -> None:
    candidates = build_candidate_set()
    posterior = {"add_across": 0.5, "multiply_all": 0.5}
    # On 2/2 + 2/2 both predict 4/4 == 1, so the item separates nothing.
    agree = FractionProblem("x", 2, 2, 2, 2)
    assert HYPOTHESIS_MAP["add_across"].predict(agree) == HYPOTHESIS_MAP["multiply_all"].predict(agree)
    gain = expected_information_gain(agree, posterior, candidates)
    assert gain == pytest.approx(0.0, abs=1e-9)


def test_information_gain_positive_when_split() -> None:
    candidates = build_candidate_set()
    posterior = {"add_across": 0.5, "keep_first_denominator": 0.5}
    split = FractionProblem("y", 1, 2, 1, 5)
    gain = expected_information_gain(split, posterior, candidates)
    assert gain > 0.0


def test_predictions_use_exact_rational_arithmetic() -> None:
    result = infer_bayesian(_observations_for("add_across"))
    row = result.evidence["add_across"][0]
    assert "/" in row.predicted  # exact Fraction rendering, not a float


def test_normalize_rejects_degenerate_scores() -> None:
    with pytest.raises(ValueError):
        _normalize_log_scores({"a": float("-inf"), "b": float("-inf")})
