from __future__ import annotations

from typing import Any, Protocol


class RuleProposalAdapter(Protocol):
    async def propose(self, structured_examples: list[dict[str, Any]]) -> list[dict[str, Any]]: ...


class FeatherlessRuleProposalAdapter:
    """Proposal-only boundary for novel procedure candidates.

    Returned JSON expressions must pass the deterministic DSL verifier before they
    can appear as a provisional pattern. The model never writes or executes Python.
    """

    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key

    async def propose(self, structured_examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("FEATHERLESS_API_KEY is not configured")
        raise RuntimeError(
            "The optional live proposal adapter is disabled until a model contract is selected and tested"
        )
