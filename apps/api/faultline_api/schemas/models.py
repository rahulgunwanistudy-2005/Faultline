from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from faultline_core import parse_fraction

ALLOWED_STEP_FEATURES = {
    "common_denominator",
    "both_numerators_scaled",
    "numerators_added",
    "denominators_added",
    "first_denominator_kept",
    "numerators_unscaled",
    "numerators_multiplied",
    "denominators_multiplied",
    "first_numerator_scaled_only",
}


class ReadingCorrection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    normalized_answer: str = Field(min_length=1, max_length=64)
    step_features: list[str] = Field(default_factory=list, max_length=12)

    @field_validator("normalized_answer")
    @classmethod
    def validate_fraction(cls, value: str) -> str:
        try:
            parsed = parse_fraction(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError("normalized_answer must be an integer or fraction such as 2/5") from exc
        if abs(parsed.numerator) > 1_000_000 or parsed.denominator > 1_000_000:
            raise ValueError("normalized_answer is outside the supported range")
        return str(parsed)

    @field_validator("step_features")
    @classmethod
    def validate_features(cls, values: list[str]) -> list[str]:
        unknown = sorted(set(values) - ALLOWED_STEP_FEATURES)
        if unknown:
            raise ValueError(f"unsupported step feature: {unknown[0]}")
        return list(dict.fromkeys(values))


class ProofRevealPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proof_token: str = Field(min_length=40, max_length=4096)


TemplateId = Literal["fractions-v1"]
