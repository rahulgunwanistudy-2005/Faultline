"""Local-AI analysis pipeline that drives a job's real state machine (Phase 8).

Stages (``transcribing`` → ``generating_hypotheses`` → ``bayesian_inference`` →
``complete``/``failed``) reflect actual pipeline progress, not elapsed time. The
image crops live only for the duration of the run and are never persisted or
logged.

A client factory hook makes the pipeline testable without a running Ollama.
"""
from __future__ import annotations

import logging
from typing import Callable, Protocol

from ..config import Settings, get_settings
from ..adapters.ollama_client import ModelError, OllamaClient
from .hypothesis_generation import generate_hypotheses
from .jobs import AnalysisJob
from .local_analysis import build_single_student_analysis
from .transcription import AllRegionsFailed, TranscriptionOutcome, transcribe_regions

LOGGER = logging.getLogger("faultline.pipeline")


class _ClientLike(Protocol):
    async def generate_json(self, *, model, prompt, images=None, schema=None): ...


_client_factory: Callable[[Settings], _ClientLike] = lambda settings: OllamaClient(settings)


def set_client_factory(factory: Callable[[Settings], _ClientLike]) -> None:
    """Override the model-client factory (used by tests to inject a fake client)."""
    global _client_factory
    _client_factory = factory


def reset_client_factory() -> None:
    global _client_factory
    _client_factory = lambda settings: OllamaClient(settings)


async def run_local_ai_pipeline(
    job: AnalysisJob,
    crops: list[tuple[str, bytes]],
    settings: Settings | None = None,
    client: _ClientLike | None = None,
) -> None:
    """Execute transcription → hypotheses → Bayesian inference, updating job state.

    Never raises: every failure is recorded on the job as a ``failed`` state with
    a redacted message. In local-AI mode there is no fixture fallback.
    """
    settings = settings or get_settings()
    client = client or _client_factory(settings)
    try:
        job.advance("transcribing")
        outcomes: list[TranscriptionOutcome] = await transcribe_regions(crops, settings, client)

        observations = _observations_for_hypotheses(outcomes)
        job.advance("generating_hypotheses")
        if observations:
            hypotheses = await generate_hypotheses(observations, settings, client)
        else:
            from .hypothesis_generation import HypothesisGenerationResult

            hypotheses = HypothesisGenerationResult([], [], [], "no_proposals", "no usable readings")

        job.advance("bayesian_inference")
        analysis = build_single_student_analysis(
            outcomes, hypotheses, settings, student_id=job.id
        )
        job.private_data = analysis.pop("_private", {})
        job.result = analysis
        job.advance("complete")
    except AllRegionsFailed:
        job.fail("No worksheet region could be transcribed. Try a clearer scan.")
    except ModelError as exc:
        job.fail(exc.client_message)
    except Exception:  # defensive: never leak internals, never fall back to fixture
        LOGGER.exception('{"event":"pipeline_unexpected_failure","job":"%s"}', job.id)
        job.fail("The local-AI pipeline encountered an unexpected error.")
    finally:
        crops.clear()  # drop image bytes from memory


def _observations_for_hypotheses(outcomes: list[TranscriptionOutcome]):
    from faultline_core import AnswerCandidate, Observation, parse_problem

    observations = []
    for outcome in outcomes:
        consensus = outcome.consensus
        if not consensus.resolved or consensus.best_value is None:
            continue
        problem = parse_problem(consensus.visible_expression, consensus.problem_id)
        if problem is None:
            continue
        candidates = tuple(
            AnswerCandidate(candidate.value, min(1.0, max(0.0, candidate.weight)))
            for candidate in consensus.candidates
        )
        if not candidates:
            continue
        observations.append(Observation(problem, candidates, consensus.step_features))
    return observations
