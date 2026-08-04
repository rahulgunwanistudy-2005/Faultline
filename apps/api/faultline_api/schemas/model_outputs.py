"""Strict schemas for local neural-model output.

Everything a local model returns is untrusted structured data. These schemas
reject unexpected fields (``extra="forbid"``) and diagnosis language: the models
have no field through which to name a diagnosis, a posterior, or a trait.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import ALLOWED_STEP_FEATURES

Legibility = Literal["clear", "partial", "unreadable"]


class TranscriptionEvidence(BaseModel):
    """Structured evidence a local vision model emits for ONE problem region.

    The model transcribes only visible mathematics. It never assigns a diagnosis
    and may only use the approved step-feature vocabulary.
    """

    model_config = ConfigDict(extra="forbid")

    problem_id: str = Field(min_length=1, max_length=16, pattern=r"^p\d{1,3}$")
    visible_expression: str = Field(default="", max_length=64)
    final_answer: str = Field(default="", max_length=32)
    intermediate_lines: list[str] = Field(default_factory=list, max_length=8)
    step_features: list[str] = Field(default_factory=list, max_length=12)
    legibility: Legibility = "partial"
    uncertain_tokens: list[str] = Field(default_factory=list, max_length=16)

    @field_validator("intermediate_lines", "uncertain_tokens")
    @classmethod
    def _bound_strings(cls, values: list[str]) -> list[str]:
        return [value[:32] for value in values][:16]

    @field_validator("step_features")
    @classmethod
    def _known_features(cls, values: list[str]) -> list[str]:
        unknown = sorted(set(values) - ALLOWED_STEP_FEATURES)
        if unknown:
            raise ValueError(f"unsupported step feature: {unknown[0]}")
        return list(dict.fromkeys(values))


class HypothesisProposal(BaseModel):
    """A single model-proposed symbolic procedure.

    ``expression`` is a restricted-DSL node (``faultline_core.dsl``). It is stored
    verbatim here and validated + executed downstream; a malformed or unsafe
    expression is rejected by the deterministic verifier, never by authority.
    """

    model_config = ConfigDict(extra="forbid")

    description: str = Field(default="", max_length=240)
    expression: dict[str, Any]

    @field_validator("description")
    @classmethod
    def _clean_description(cls, value: str) -> str:
        return value.strip()[:240]


class HypothesisProposalBatch(BaseModel):
    """A bounded batch of model output: known-ID nominations + novel proposals.

    There is deliberately no field for a diagnosis, a chosen hypothesis, or a
    probability. Nominations are hints; the Bayesian engine evaluates the full
    known library regardless.
    """

    model_config = ConfigDict(extra="forbid")

    known_hypothesis_ids: list[str] = Field(default_factory=list, max_length=12)
    proposals: list[HypothesisProposal] = Field(default_factory=list, max_length=10)

    @field_validator("known_hypothesis_ids")
    @classmethod
    def _dedupe_ids(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(value.strip()[:64] for value in values if value.strip()))
