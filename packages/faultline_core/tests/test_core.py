from fractions import Fraction

import pytest

from faultline_core import (
    AnswerCandidate,
    DSLValidationError,
    FractionProblem,
    HYPOTHESES,
    Observation,
    confidence_gate,
    evaluate,
    infer,
    information_gain,
    rank_items,
)


@pytest.fixture
def problems() -> list[FractionProblem]:
    return [
        FractionProblem("p1", 1, 2, 1, 3),
        FractionProblem("p2", 2, 3, 1, 4),
        FractionProblem("p3", 3, 5, 1, 2),
        FractionProblem("p4", 1, 4, 2, 3),
        FractionProblem("p5", 2, 5, 1, 3),
        FractionProblem("p6", 3, 8, 1, 6),
    ]


def test_every_rule_executes(problems: list[FractionProblem]) -> None:
    for hypothesis in HYPOTHESES:
        for problem in problems:
            assert isinstance(hypothesis.predict(problem), Fraction)


def test_posterior_selects_add_across(problems: list[FractionProblem]) -> None:
    rule = next(item for item in HYPOTHESES if item.id == "add_across")
    observations = [Observation.exact(p, rule.predict(p), 0.97, rule.step_signature) for p in problems]
    result = infer(observations)
    assert next(iter(result.posterior)) == "add_across"
    assert result.posterior["add_across"] > 0.95
    assert confidence_gate(result)["state"] == "named_diagnosis"


def test_low_ocr_confidence_blocks_label(problems: list[FractionProblem]) -> None:
    rule = next(item for item in HYPOTHESES if item.id == "add_across")
    observations = [Observation.exact(p, rule.predict(p), 0.55) for p in problems]
    gate = confidence_gate(infer(observations))
    assert gate["state"] == "more_evidence_needed"
    assert "low_ocr_confidence" in gate["reasons"]


def test_candidate_uncertainty_is_marginalized(problems: list[FractionProblem]) -> None:
    hypothesis_map = {item.id: item for item in HYPOTHESES}
    problem = problems[0]
    observations = [
        Observation(
            problem,
            (
                AnswerCandidate(hypothesis_map["add_across"].predict(problem), 0.55),
                AnswerCandidate(hypothesis_map["correct_common_denominator"].predict(problem), 0.45),
            ),
        )
    ] * 6
    result = infer(observations)
    assert next(iter(result.posterior)) in {"add_across", "correct_common_denominator"}
    assert result.posterior[next(iter(result.posterior))] < 0.95


def test_information_gain_is_nonnegative() -> None:
    posterior = {"add_across": 0.5, "keep_first_denominator": 0.5}
    assert information_gain(FractionProblem("x", 1, 2, 1, 3), posterior) >= 0


def test_rank_items_uses_diverse_denominators() -> None:
    posterior = {"add_across": 0.5, "keep_first_denominator": 0.5}
    items = [
        FractionProblem("a", 1, 2, 1, 3),
        FractionProblem("b", 2, 3, 1, 2),
        FractionProblem("c", 1, 4, 1, 5),
    ]
    ranked = rank_items(items, posterior, limit=2)
    pairs = [tuple(sorted((item.d1, item.d2))) for _, item in ranked]
    assert len(pairs) == len(set(pairs))


def test_dsl_evaluates_add_across() -> None:
    ast = {
        "op": "fraction",
        "args": [
            {"op": "add", "args": [{"var": "n1"}, {"var": "n2"}]},
            {"op": "add", "args": [{"var": "d1"}, {"var": "d2"}]},
        ],
    }
    assert evaluate(ast, {"n1": 1, "d1": 2, "n2": 1, "d2": 3}) == Fraction(2, 5)


def test_dsl_rejects_code_like_operator() -> None:
    with pytest.raises(DSLValidationError):
        evaluate({"op": "exec", "args": [1, 2]}, {})


def test_dsl_rejects_excessive_depth() -> None:
    node: object = 1
    for _ in range(10):
        node = {"op": "add", "args": [node, 1]}
    with pytest.raises(DSLValidationError):
        evaluate(node, {})


def test_verifier_accepts_reproducing_safe_candidate(problems: list[FractionProblem]) -> None:
    from faultline_core import SynthesisExample, verify_candidate

    ast = {
        "op": "fraction",
        "args": [
            {"op": "add", "args": [{"var": "n1"}, {"var": "n2"}]},
            {"op": "add", "args": [{"var": "d1"}, {"var": "d2"}]},
        ],
    }
    examples = [SynthesisExample(problem, Fraction(problem.n1 + problem.n2, problem.d1 + problem.d2)) for problem in problems]
    candidate = verify_candidate("Adds top and bottom separately", ast, examples)
    assert candidate is not None
    assert candidate.reproduction == 1.0
    assert candidate.provisional is True


def test_verifier_rejects_non_reproducing_candidate(problems: list[FractionProblem]) -> None:
    from faultline_core import SynthesisExample, verify_candidate

    ast = {"op": "fraction", "args": [{"var": "n1"}, {"var": "d1"}]}
    examples = [SynthesisExample(problem, Fraction(problem.n1 + problem.n2, problem.d1 + problem.d2)) for problem in problems]
    assert verify_candidate("Copies the first fraction", ast, examples) is None
