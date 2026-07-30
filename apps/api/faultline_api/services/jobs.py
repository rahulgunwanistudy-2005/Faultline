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


@dataclass
class AnalysisJob:
    id: str
    filename: str
    template_id: str
    upload_metadata: dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_monotonic: float = field(default_factory=monotonic)
    result: dict[str, Any] = field(default_factory=build_class_analysis)
    corrections: dict[str, dict[str, Any]] = field(default_factory=dict)
    force_complete: bool = False

    def snapshot(self) -> dict[str, Any]:
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
