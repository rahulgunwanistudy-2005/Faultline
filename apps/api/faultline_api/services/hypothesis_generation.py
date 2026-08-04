"""Neuro-symbolic hypothesis generation (Phase 4).

The local model may nominate known hypothesis ids and propose up to N new
symbolic procedures in the restricted DSL. It has NO diagnostic authority:

* nominations are hints only — the Bayesian engine always evaluates the full
  known library regardless of what was nominated;
* every proposal must pass the deterministic verifier (fit, validation,
  counterexample, complexity, novelty) before it can enter the candidate set;
* the model never returns a probability that is treated as a posterior.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Sequence

from pydantic import ValidationError

from faultline_core import (
    HYPOTHESES,
    HYPOTHESIS_MAP,
    Hypothesis,
    Observation,
    ProposalVerification,
    ProvisionalCandidate,
    SynthesisExample,
    verify_symbolic_hypothesis,
)

from ..adapters.ollama_client import ModelError, OllamaClient
from ..config import Settings
from ..schemas.model_outputs import HypothesisProposalBatch

LOGGER = logging.getLogger("faultline.hypotheses")

HYPOTHESIS_PROMPT = """You propose candidate procedures that might explain a student's fraction work.

You are NOT the judge. A deterministic engine will execute and score every idea.

STRICT RULES:
- Do NOT state a diagnosis, a probability, or a confidence. There is no field for it.
- You may nominate known_hypothesis_ids from the provided list.
- You may propose up to {max_proposals} NEW procedures as restricted-DSL expressions.
- Allowed variables: n1, d1, n2, d2. Allowed operations: add, sub, mul, lcm, fraction.
- A DSL node is one of: an integer; {{"var": "n1"}}; or {{"op": "add", "args": [<node>, <node>]}}.
- No strings-as-logic, no item ids, no conditionals, no lookups, no code.
- Return ONLY a JSON object with EXACTLY these keys: known_hypothesis_ids, proposals.
- Each proposal is {{"description": "...", "expression": <dsl-node>}}.

INPUT:
{payload}
"""


@dataclass(frozen=True)
class HypothesisGenerationResult:
    known_nominations: list[str]
    accepted: list[ProvisionalCandidate]
    audit: list[ProposalVerification]
    status: str  # ok | model_unavailable | model_malformed | no_proposals
    detail: str = ""
    raw_known_ids: list[str] = field(default_factory=list)


def _best_value(observation: Observation):
    return max(observation.candidates, key=lambda candidate: candidate.confidence).value


def _normalized_payload(observations: Sequence[Observation], known: tuple[Hypothesis, ...]) -> str:
    return json.dumps(
        {
            "observations": [
                {
                    "problem": {
                        "n1": obs.problem.n1,
                        "d1": obs.problem.d1,
                        "n2": obs.problem.n2,
                        "d2": obs.problem.d2,
                    },
                    "observed_answer": str(_best_value(obs)),
                    "step_features": sorted(obs.step_features),
                }
                for obs in observations
            ],
            "known_hypotheses": [
                {"id": h.id, "description": h.description} for h in known
            ],
            "allowed_variables": ["n1", "d1", "n2", "d2"],
            "allowed_operations": ["add", "sub", "mul", "lcm", "fraction"],
        },
        separators=(",", ":"),
        sort_keys=True,
    )


def _examples(observations: Sequence[Observation]) -> tuple[list[SynthesisExample], list[SynthesisExample]]:
    examples = [SynthesisExample(obs.problem, _best_value(obs)) for obs in observations]
    if len(examples) >= 6:
        split = max(4, int(round(len(examples) * 0.7)))
        return examples[:split], examples[split:]
    return examples, []


async def generate_hypotheses(
    observations: Sequence[Observation],
    settings: Settings,
    client: OllamaClient,
    known: tuple[Hypothesis, ...] = HYPOTHESES,
) -> HypothesisGenerationResult:
    if settings.max_hypothesis_proposals == 0:
        return HypothesisGenerationResult([], [], [], "no_proposals", "proposals disabled")

    prompt = HYPOTHESIS_PROMPT.format(
        max_proposals=settings.max_hypothesis_proposals,
        payload=_normalized_payload(observations, known),
    )
    try:
        raw = await client.generate_json(model=settings.hypothesis_model, prompt=prompt)
    except ModelError as exc:
        return HypothesisGenerationResult([], [], [], "model_unavailable", exc.client_message)

    try:
        batch = HypothesisProposalBatch.model_validate(raw)
    except ValidationError:
        LOGGER.warning('{"event":"hypothesis_schema_rejected"}')
        return HypothesisGenerationResult([], [], [], "model_malformed", "schema rejected")

    return evaluate_batch(batch, observations, settings, known)


def evaluate_batch(
    batch: HypothesisProposalBatch,
    observations: Sequence[Observation],
    settings: Settings,
    known: tuple[Hypothesis, ...] = HYPOTHESES,
) -> HypothesisGenerationResult:
    """Validate + gate a proposal batch (pure; no network). Nominations are hints only."""
    known_map = {h.id: h for h in known}
    nominations = [hid for hid in batch.known_hypothesis_ids if hid in known_map]

    fit, validation = _examples(observations)
    audit: list[ProposalVerification] = []
    accepted: list[ProvisionalCandidate] = []
    seen_signatures: set[tuple[str, ...]] = set()

    for index, proposal in enumerate(batch.proposals[: settings.max_hypothesis_proposals]):
        verification = verify_symbolic_hypothesis(
            proposal.description,
            proposal.expression,
            fit,
            validation or None,
            known=known,
            min_reproduction=settings.novel_rule_min_reproduction,
            validation_reproduction=settings.novel_rule_validation_reproduction,
        )
        # De-duplicate accepted proposals against each other by behavioural signature.
        if verification.accepted and verification.novelty_signature in seen_signatures:
            verification = ProposalVerification(
                accepted=False,
                reason="duplicate_proposal",
                description=verification.description,
                expression=verification.expression,
                novelty_signature=verification.novelty_signature,
            )
        audit.append(verification)
        if verification.accepted and verification.novelty_signature is not None:
            seen_signatures.add(verification.novelty_signature)
            accepted.append(
                ProvisionalCandidate(
                    id=f"proposed_{index + 1}",
                    label=(verification.description or "Proposed procedure")[:60],
                    expression=verification.expression,
                )
            )

    status = "ok" if (accepted or nominations or batch.proposals) else "no_proposals"
    return HypothesisGenerationResult(
        known_nominations=nominations,
        accepted=accepted,
        audit=audit,
        status=status,
        detail=f"{len(accepted)} accepted of {len(batch.proposals)} proposals",
        raw_known_ids=list(batch.known_hypothesis_ids),
    )
