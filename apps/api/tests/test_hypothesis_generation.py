"""Neuro-symbolic hypothesis generation tests (Phase 4)."""
from __future__ import annotations

import asyncio

import pytest

from faultline_core import HYPOTHESIS_MAP, FractionProblem, Observation
from faultline_api.config import build_settings
from faultline_api.schemas.model_outputs import HypothesisProposalBatch
from faultline_api.services.hypothesis_generation import evaluate_batch, generate_hypotheses

ADD_ACROSS = {
    "op": "fraction",
    "args": [
        {"op": "add", "args": [{"var": "n1"}, {"var": "n2"}]},
        {"op": "add", "args": [{"var": "d1"}, {"var": "d2"}]},
    ],
}
NOVEL = {
    "op": "fraction",
    "args": [
        {"op": "add", "args": [{"var": "n1"}, {"var": "n2"}]},
        {"op": "mul", "args": [{"var": "d1"}, {"var": "d2"}]},
    ],
}


def _problems() -> list[FractionProblem]:
    return [
        FractionProblem("p1", 1, 2, 1, 3),
        FractionProblem("p2", 2, 3, 1, 4),
        FractionProblem("p3", 3, 5, 1, 2),
        FractionProblem("p4", 1, 4, 2, 3),
        FractionProblem("p5", 2, 5, 3, 7),
        FractionProblem("p6", 3, 8, 1, 6),
    ]


def _observations_for(expression) -> list[Observation]:
    from faultline_core import evaluate

    return [
        Observation.exact(
            p, evaluate(expression, {"n1": p.n1, "d1": p.d1, "n2": p.n2, "d2": p.d2}), 0.97
        )
        for p in _problems()
    ]


def _settings(monkeypatch, **env):
    monkeypatch.setenv("FAULTLINE_RUNTIME_MODE", "local_ai")
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return build_settings()


class FakeClient:
    def __init__(self, response):
        self._response = response

    async def generate_json(self, *, model, prompt, images=None, schema=None):
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


def test_known_nomination_kept_as_hint_only(monkeypatch) -> None:
    settings = _settings(monkeypatch)
    batch = HypothesisProposalBatch.model_validate(
        {"known_hypothesis_ids": ["add_across", "not_a_real_id"], "proposals": []}
    )
    result = evaluate_batch(batch, _observations_for(NOVEL), settings)
    assert result.known_nominations == ["add_across"]  # unknown id filtered out
    assert result.accepted == []


def test_valid_novel_proposal_admitted(monkeypatch) -> None:
    settings = _settings(monkeypatch)
    batch = HypothesisProposalBatch.model_validate(
        {"known_hypothesis_ids": [], "proposals": [{"description": "add tops mul bottoms", "expression": NOVEL}]}
    )
    result = evaluate_batch(batch, _observations_for(NOVEL), settings)
    assert len(result.accepted) == 1
    assert result.accepted[0].expression == NOVEL


def test_equivalent_known_rule_rejected_as_novel(monkeypatch) -> None:
    settings = _settings(monkeypatch)
    batch = HypothesisProposalBatch.model_validate(
        {"known_hypothesis_ids": [], "proposals": [{"description": "adds across", "expression": ADD_ACROSS}]}
    )
    result = evaluate_batch(batch, _observations_for(ADD_ACROSS), settings)
    assert result.accepted == []
    assert result.audit[0].reason.startswith("duplicate_of_known")


def test_invalid_dsl_rejected(monkeypatch) -> None:
    settings = _settings(monkeypatch)
    batch = HypothesisProposalBatch.model_validate(
        {"known_hypothesis_ids": [], "proposals": [{"description": "code", "expression": {"op": "exec", "args": [1, 2]}}]}
    )
    result = evaluate_batch(batch, _observations_for(NOVEL), settings)
    assert result.accepted == []
    assert result.audit[0].reason.startswith("invalid_dsl")


def test_duplicate_proposals_deduplicated(monkeypatch) -> None:
    settings = _settings(monkeypatch)
    batch = HypothesisProposalBatch.model_validate(
        {
            "known_hypothesis_ids": [],
            "proposals": [
                {"description": "one", "expression": NOVEL},
                {"description": "same behaviour", "expression": NOVEL},
            ],
        }
    )
    result = evaluate_batch(batch, _observations_for(NOVEL), settings)
    assert len(result.accepted) == 1
    assert any(item.reason == "duplicate_proposal" for item in result.audit)


def test_proposals_disabled_when_max_is_zero(monkeypatch) -> None:
    settings = _settings(monkeypatch, FAULTLINE_MAX_HYPOTHESIS_PROPOSALS="0")
    client = FakeClient({"known_hypothesis_ids": [], "proposals": []})
    result = asyncio.run(generate_hypotheses(_observations_for(NOVEL), settings, client))
    assert result.status == "no_proposals"


def test_model_unavailable_handled_cleanly(monkeypatch) -> None:
    from faultline_api.adapters.ollama_client import ModelUnavailableError

    settings = _settings(monkeypatch)
    client = FakeClient(ModelUnavailableError("down"))
    result = asyncio.run(generate_hypotheses(_observations_for(NOVEL), settings, client))
    assert result.status == "model_unavailable"
    assert result.accepted == []


def test_model_diagnosis_language_has_no_field(monkeypatch) -> None:
    settings = _settings(monkeypatch)
    client = FakeClient(
        {"known_hypothesis_ids": [], "proposals": [], "diagnosis": "adds across", "posterior": 0.9}
    )
    # extra keys are forbidden → the batch is malformed and ignored, never used as a result.
    result = asyncio.run(generate_hypotheses(_observations_for(NOVEL), settings, client))
    assert result.status == "model_malformed"


def test_model_score_never_becomes_posterior() -> None:
    # There is no field on HypothesisProposalBatch for a probability/score.
    assert "posterior" not in HypothesisProposalBatch.model_fields
    assert "confidence" not in HypothesisProposalBatch.model_fields
    assert "diagnosis" not in HypothesisProposalBatch.model_fields
