"""Build a frontend-compatible analysis from real local-AI evidence (Phase 8).

An uploaded worksheet is one student's work. This module runs the deterministic
Bayesian engine over the model-derived observations and shapes the result into
the exact class/student payload the frozen frontend already consumes, with all
new technical detail added under optional nested keys (``analysis_meta``,
``diagnosis.bayesian``).
"""
from __future__ import annotations

from dataclasses import asdict
from fractions import Fraction
from typing import Any

from faultline_core import (
    AnswerCandidate,
    BayesianParams,
    HYPOTHESIS_MAP,
    LikelihoodParams,
    NULL_HYPOTHESIS_ID,
    Observation,
    ProvisionalCandidate,
    build_candidate_set,
    expected_information_gain,
    infer_bayesian,
    parse_problem,
    rank_items,
)

from ..config import Settings
from .demo import ACTION_LANES, _item_bank
from .hypothesis_generation import HypothesisGenerationResult
from .reading_consensus import ReadingConsensus
from .transcription import TranscriptionOutcome

LOCAL_METHOD_NOTE = (
    "Each candidate procedure is executed against this worksheet's transcribed work. "
    "The neural model only proposes evidence and hypotheses; the deterministic "
    "Bayesian engine decides what the evidence supports, and abstains when it does not."
)


def bayesian_params_from_settings(settings: Settings) -> BayesianParams:
    likelihood = LikelihoodParams(
        answer_match_probability=settings.bayesian_answer_match_probability,
        answer_mismatch_probability=settings.bayesian_answer_mismatch_probability,
        step_match_probability=settings.bayesian_step_match_probability,
        step_mismatch_probability=settings.bayesian_step_mismatch_probability,
    ).validated()
    return BayesianParams(
        prior_mode=settings.bayesian_prior_mode,
        likelihood=likelihood,
        abstention_entropy_threshold=settings.bayesian_abstention_entropy_threshold,
        top_two_margin_threshold=settings.bayesian_top_two_margin_threshold,
        min_reproduction=settings.novel_rule_min_reproduction,
    )


def _usable_regions(outcomes: list[TranscriptionOutcome]):
    """Yield (problem, observation, observed_str, consensus) for parseable regions."""
    usable = []
    for outcome in outcomes:
        consensus: ReadingConsensus = outcome.consensus
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
        observation = Observation(problem, candidates, consensus.step_features)
        usable.append((problem, observation, str(consensus.best_value), consensus))
    return usable


def build_single_student_analysis(
    outcomes: list[TranscriptionOutcome],
    hypotheses: HypothesisGenerationResult,
    settings: Settings,
    *,
    student_id: str,
    display_name: str = "Uploaded worksheet",
) -> dict[str, Any]:
    params = bayesian_params_from_settings(settings)
    provisional = [
        ProvisionalCandidate(id=candidate.id, label=candidate.label, expression=candidate.expression)
        for candidate in hypotheses.accepted
    ]
    candidates = build_candidate_set(provisional)
    label_map = {c.id: c.label for c in candidates}

    usable = _usable_regions(outcomes)
    meta = _analysis_meta(outcomes, hypotheses, settings)

    if not usable:
        return _empty_analysis(student_id, display_name, meta)

    observations = [obs for _p, obs, _a, _c in usable]

    # Leave-one-out held-out check when there is enough visible work.
    held_index: int | None = None
    if len(usable) >= 6:
        full = infer_bayesian(observations, candidates, params)
        gains = [
            (expected_information_gain(problem, full.posterior, candidates), index)
            for index, (problem, _o, _a, _c) in enumerate(usable)
        ]
        held_index = max(gains, key=lambda pair: (pair[0], -pair[1]))[1]

    inference_obs = [obs for i, obs in enumerate(observations) if i != held_index]
    result = infer_bayesian(inference_obs, candidates, params)

    top_id = result.top_hypothesis
    named = result.state == "named_diagnosis"
    lane, diagnosis_label, description, action = _lane_for(top_id, named, label_map)

    distribution = [
        {"id": hid, "label": label_map.get(hid, "No consistent procedure"), "probability": round(prob, 4)}
        for hid, prob in result.ranked[:4]
    ]
    top_predict = HYPOTHESIS_MAP[top_id].predict if top_id in HYPOTHESIS_MAP else None

    observation_rows = []
    for index, (problem, _obs, observed, consensus) in enumerate(usable):
        if index == held_index:
            continue
        predicted = str(top_predict(problem)) if top_predict else "—"
        observation_rows.append(
            {
                "reading_id": f"{student_id}-{problem.id}",
                "problem_id": problem.id,
                "expression": problem.expression,
                "form": problem.form,
                "observed": observed,
                "ocr_confidence": round(consensus.support * 100),
                "predicted": predicted,
                "matched": observed == predicted,
                "reviewed": False,
            }
        )

    held_out_public, held_out_private = _held_out(
        usable, held_index, top_id, named, student_id
    )

    student = {
        "student_id": student_id,
        "display_name": display_name,
        "lane": lane,
        "diagnosis": {
            "hypothesis_id": top_id,
            "label": diagnosis_label,
            "description": description,
            "action": action,
            "state": result.state,
            "posterior": round(result.top_posterior, 4),
            "posterior_percent": round(result.top_posterior * 100),
            "reproduction": round(result.answer_reproduction.get(top_id, 0.0) * 100),
            "mean_ocr_confidence": round(result.mean_support * 100),
            "reasons": result.reasons,
            "distribution": distribution,
            "bayesian": result.as_metadata(),
        },
        "observations": observation_rows,
        "diagnostic_items": _diagnostic_items(result.posterior),
        "held_out": held_out_public,
    }

    analysis = _class_wrapper([student], meta)
    analysis["_private"] = {student_id: held_out_private} if held_out_private else {}
    return analysis


def _held_out(usable, held_index, top_id, named, student_id):
    if held_index is None:
        # No held-out check performed: expose a withheld proof block.
        problem = usable[0][0]
        return (
            {"problem": {**asdict(problem), "expression": problem.expression}, "proof_available": False},
            None,
        )
    problem, _obs, actual, consensus = usable[held_index]
    proof_available = named and top_id in HYPOTHESIS_MAP
    public = {
        "problem": {**asdict(problem), "expression": problem.expression},
        "proof_available": proof_available,
    }
    private = None
    if proof_available:
        predicted = str(HYPOTHESIS_MAP[top_id].predict(problem))
        private = {
            "problem": {**asdict(problem), "expression": problem.expression},
            "hypothesis_id": top_id,
            "predicted_answer": predicted,
            "actual_answer": actual,
            "ocr_confidence": round(consensus.support * 100),
        }
    return public, private


def _diagnostic_items(posterior: dict[str, float]) -> list[dict[str, Any]]:
    top_ids = [key for key in posterior if key in HYPOTHESIS_MAP][:2]
    ranked = rank_items(list(_item_bank()), posterior, 3)
    output = []
    for gain, item in ranked:
        predictions = {hid: str(HYPOTHESIS_MAP[hid].predict(item)) for hid in top_ids}
        explanation = "Different surviving procedures produce different answers here."
        if len(set(predictions.values())) <= 1:
            explanation = "Useful as a confidence check after the separating questions."
        output.append(
            {
                "id": item.id,
                "expression": item.expression,
                "form": item.form,
                "information_gain": round(gain, 3),
                "separates": predictions,
                "explanation": explanation,
            }
        )
    return output


def _lane_for(top_id: str, named: bool, label_map: dict[str, str]):
    if not named:
        return (
            "more_evidence",
            "Evidence is not strong enough yet",
            "Faultline is withholding a diagnosis until the reading or pattern is clearer.",
            "Ask the separating questions",
        )
    if top_id == NULL_HYPOTHESIS_ID:
        return (
            "guided_practice",
            "No stable procedure is visible",
            "The answers do not reproduce one consistent executable rule.",
            "Use short guided practice",
        )
    if top_id in HYPOTHESIS_MAP:
        hypothesis = HYPOTHESIS_MAP[top_id]
        return hypothesis.action, hypothesis.short_label, hypothesis.description, hypothesis.action_label
    # A provisional (model-proposed, verifier-accepted) procedure leads.
    return (
        "re_explain",
        label_map.get(top_id, "Proposed procedure"),
        "A provisional, verifier-accepted procedure best reproduces this work.",
        "Re-explain the idea",
    )


def _analysis_meta(outcomes, hypotheses: HypothesisGenerationResult, settings: Settings) -> dict[str, Any]:
    return {
        "runtime_mode": settings.runtime_mode,
        "vision_model": settings.vision_model,
        "hypothesis_model": settings.hypothesis_model,
        "transcription": {
            "regions": len(outcomes),
            "resolved": sum(1 for o in outcomes if o.consensus.resolved),
            "passes_succeeded": sum(o.passes_succeeded for o in outcomes),
            "mean_support": round(
                sum(o.consensus.support for o in outcomes) / max(len(outcomes), 1), 4
            ),
        },
        "hypotheses": {
            "status": hypotheses.status,
            "known_nominations": hypotheses.known_nominations,
            "accepted_proposals": len(hypotheses.accepted),
            "rejected_proposals": sum(1 for item in hypotheses.audit if not item.accepted),
        },
    }


def _class_wrapper(students: list[dict[str, Any]], meta: dict[str, Any]) -> dict[str, Any]:
    lanes = []
    for lane_id, lane_meta in ACTION_LANES.items():
        members = [s for s in students if s["lane"] == lane_id]
        lanes.append({"id": lane_id, **lane_meta, "count": len(members), "students": members})
    named = sum(1 for s in students if s["diagnosis"]["state"] == "named_diagnosis")
    mean_ocr = round(
        sum(s["diagnosis"]["mean_ocr_confidence"] for s in students) / max(len(students), 1)
    )
    return {
        "class_id": "uploaded-worksheet",
        "title": "Uploaded worksheet · live local-AI diagnosis",
        "skill": "Adding fractions with unlike denominators",
        "dataset_type": "live_local_ai",
        "summary": {
            "students": len(students),
            "named_diagnoses": named,
            "withheld": len(students) - named,
            "mean_ocr_confidence": mean_ocr,
            "minutes_to_action": 2,
        },
        "lanes": lanes,
        "students": students,
        "method_note": LOCAL_METHOD_NOTE,
        "analysis_meta": meta,
    }


def _empty_analysis(student_id: str, display_name: str, meta: dict[str, Any]) -> dict[str, Any]:
    student = {
        "student_id": student_id,
        "display_name": display_name,
        "lane": "more_evidence",
        "diagnosis": {
            "hypothesis_id": NULL_HYPOTHESIS_ID,
            "label": "Not enough readable work",
            "description": "No worksheet region produced a confident, parseable reading.",
            "action": "Re-scan the worksheet",
            "state": "more_evidence_needed",
            "posterior": 0.0,
            "posterior_percent": 0,
            "reproduction": 0,
            "mean_ocr_confidence": 0,
            "reasons": ["no_usable_readings"],
            "distribution": [],
            "bayesian": {"state": "more_evidence_needed", "reasons": ["no_usable_readings"]},
        },
        "observations": [],
        "diagnostic_items": [],
        "held_out": {"problem": {"expression": "—"}, "proof_available": False},
    }
    analysis = _class_wrapper([student], meta)
    analysis["_private"] = {}
    return analysis
