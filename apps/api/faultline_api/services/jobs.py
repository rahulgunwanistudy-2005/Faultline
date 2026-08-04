from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from time import monotonic
from typing import Any
from uuid import uuid4

from ..config import get_settings
from .demo import build_class_analysis

DEMO_DISCLOSURE = (
    "The upload was validated and segmented using the known template. Live handwriting "
    "recognition is not enabled in this build, so the displayed diagnoses come from the "
    "clearly labeled synthetic regression fixture."
)

LOCAL_AI_DISCLOSURE = (
    "This worksheet was transcribed by a local vision model and diagnosed by the "
    "deterministic Bayesian engine. No hosted API was used and no image bytes were stored."
)

# Real pipeline stages, in order. Progress is derived from the stage reached,
# never from elapsed time.
LOCAL_AI_STAGES = (
    "validating",
    "segmenting",
    "transcribing",
    "generating_hypotheses",
    "bayesian_inference",
    "complete",
)
_STAGE_PROGRESS = {
    "validating": 8,
    "segmenting": 20,
    "transcribing": 55,
    "generating_hypotheses": 78,
    "bayesian_inference": 92,
    "complete": 100,
    "failed": 100,
}


@dataclass
class AnalysisJob:
    id: str
    filename: str
    template_id: str
    upload_metadata: dict[str, Any]
    kind: str = "fixture"  # fixture | local_ai
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_monotonic: float = field(default_factory=monotonic)
    result: dict[str, Any] | None = None
    corrections: dict[str, dict[str, Any]] = field(default_factory=dict)
    force_complete: bool = False
    # local_ai only
    state: str = "validating"
    state_history: list[str] = field(default_factory=list)
    error: str | None = None
    private_data: dict[str, Any] = field(default_factory=dict)

    def advance(self, state: str) -> None:
        self.state = state
        self.state_history.append(state)

    def fail(self, message: str) -> None:
        self.state = "failed"
        self.state_history.append("failed")
        self.error = message

    def snapshot(self) -> dict[str, Any]:
        if self.kind == "local_ai":
            return self._local_ai_snapshot()
        return self._fixture_snapshot()

    def _fixture_snapshot(self) -> dict[str, Any]:
        elapsed_ms = (monotonic() - self.created_monotonic) * 1000
        stage_ms = get_settings().demo_stage_ms
        if self.force_complete or elapsed_ms >= stage_ms * 3:
            status, progress = "complete", 100
        elif elapsed_ms >= stage_ms * 2:
            status, progress = "inferring", 79
        elif elapsed_ms >= stage_ms:
            status, progress = "reading", 52
        else:
            status, progress = "segmenting", 24
        payload: dict[str, Any] = {
            "id": self.id,
            "filename": self.filename,
            "template_id": self.template_id,
            "status": status,
            "progress": progress,
            "created_at": self.created_at,
            "mode": "synthetic_demo_fixture",
            "disclosure": DEMO_DISCLOSURE,
            "upload": deepcopy(self.upload_metadata),
            "result": None,
        }
        if status == "complete":
            payload["result"] = deepcopy(self.result)
            payload["result"]["analysis_mode"] = "synthetic_demo_fixture"
            payload["result"]["disclosure"] = DEMO_DISCLOSURE
            payload["result"]["upload"] = deepcopy(self.upload_metadata)
        return payload

    def _local_ai_snapshot(self) -> dict[str, Any]:
        status = self.state
        payload: dict[str, Any] = {
            "id": self.id,
            "filename": self.filename,
            "template_id": self.template_id,
            "status": status,
            "progress": _STAGE_PROGRESS.get(status, 0),
            "created_at": self.created_at,
            "mode": "local_ai",
            "disclosure": LOCAL_AI_DISCLOSURE,
            "upload": deepcopy(self.upload_metadata),
            "stages": list(self.state_history),
            "result": None,
        }
        if status == "failed":
            payload["error"] = self.error or "The local-AI pipeline failed."
        if status == "complete" and self.result is not None:
            result = deepcopy(self.result)
            result.pop("_private", None)  # never expose held-out answers
            result["analysis_mode"] = "local_ai"
            result["disclosure"] = LOCAL_AI_DISCLOSURE
            result["upload"] = deepcopy(self.upload_metadata)
            payload["result"] = result
        return payload


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, AnalysisJob] = {}
        self._lock = Lock()

    def _cleanup(self) -> None:
        now = monotonic()
        ttl = get_settings().job_ttl_seconds
        expired = [job_id for job_id, job in self._jobs.items() if now - job.created_monotonic > ttl]
        for job_id in expired:
            self._jobs.pop(job_id, None)
        if len(self._jobs) > get_settings().max_jobs:
            oldest = sorted(self._jobs.values(), key=lambda item: item.created_monotonic)
            for job in oldest[: len(self._jobs) - get_settings().max_jobs]:
                self._jobs.pop(job.id, None)

    def create(
        self,
        filename: str,
        template_id: str,
        upload_metadata: dict[str, Any],
    ) -> AnalysisJob:
        job = AnalysisJob(
            id=str(uuid4()),
            filename=filename,
            template_id=template_id,
            upload_metadata=upload_metadata,
            kind="fixture",
            result=build_class_analysis(),
        )
        with self._lock:
            self._cleanup()
            self._jobs[job.id] = job
        return job

    def create_local_ai(
        self,
        filename: str,
        template_id: str,
        upload_metadata: dict[str, Any],
    ) -> AnalysisJob:
        job = AnalysisJob(
            id=str(uuid4()),
            filename=filename,
            template_id=template_id,
            upload_metadata=upload_metadata,
            kind="local_ai",
            state="validating",
            state_history=["validating", "segmenting"],
        )
        with self._lock:
            self._cleanup()
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> AnalysisJob | None:
        with self._lock:
            self._cleanup()
            return self._jobs.get(job_id)

    def correct(self, job_id: str, reading_id: str, correction: dict[str, Any]) -> AnalysisJob | None:
        with self._lock:
            self._cleanup()
            job = self._jobs.get(job_id)
            if job is None:
                return None
            if job.kind != "fixture" or job.result is None:
                raise KeyError(reading_id)
            valid_readings = {
                observation["reading_id"]
                for student in job.result["students"]
                for observation in student["observations"]
            }
            if reading_id not in valid_readings:
                raise KeyError(reading_id)
            job.corrections[reading_id] = correction
            job.result = build_class_analysis(job.corrections)
            job.force_complete = True
            return job


STORE = JobStore()
