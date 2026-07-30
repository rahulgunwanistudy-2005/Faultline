from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ReadingCandidate:
    normalized_answer: str
    confidence: float
    step_features: tuple[str, ...] = ()


class VisionAdapter(Protocol):
    async def transcribe(self, image_bytes: bytes) -> list[ReadingCandidate]: ...


class FixtureVisionAdapter:
    """Reliable demo adapter. It never sends student work to an external service."""

    async def transcribe(self, image_bytes: bytes) -> list[ReadingCandidate]:
        if not image_bytes:
            raise ValueError("empty upload")
        return [ReadingCandidate("2/5", 0.96, ("numerators_added", "denominators_added"))]


class FeatherlessVisionAdapter:
    """Integration boundary for a transcription-only vision call.

    The model may propose readings, but it never names a diagnosis. The competition
    package leaves network invocation behind this adapter so the deterministic demo
    remains reliable without an API key.
    """

    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key

    async def transcribe(self, image_bytes: bytes) -> list[ReadingCandidate]:
        if not self.api_key:
            raise RuntimeError("FEATHERLESS_API_KEY is not configured")
        raise RuntimeError(
            "The optional live vision adapter is disabled until its structured-output contract is tested"
        )
