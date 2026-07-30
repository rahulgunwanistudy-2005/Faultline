from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from functools import lru_cache


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if value <= 0:
        raise RuntimeError(f"{name} must be positive")
    return value


def _origins() -> tuple[str, ...]:
    raw = os.getenv("FAULTLINE_CORS_ORIGINS", "")
    return tuple(origin.strip() for origin in raw.split(",") if origin.strip())


@dataclass(frozen=True)
class Settings:
    max_upload_bytes: int
    max_image_pixels: int
    proof_ttl_seconds: int
    proof_secret: bytes
    job_ttl_seconds: int
    max_jobs: int
    demo_stage_ms: int
    cors_origins: tuple[str, ...]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    configured_secret = os.getenv("FAULTLINE_PROOF_SECRET", "").encode("utf-8")
    # A random process-local secret is safe for the single-worker demo. Deployments
    # with multiple workers must set FAULTLINE_PROOF_SECRET so tokens survive routing.
    proof_secret = configured_secret or secrets.token_bytes(32)
    return Settings(
        max_upload_bytes=_positive_int("FAULTLINE_MAX_UPLOAD_BYTES", 8 * 1024 * 1024),
        max_image_pixels=_positive_int("FAULTLINE_MAX_IMAGE_PIXELS", 20_000_000),
        proof_ttl_seconds=_positive_int("FAULTLINE_PROOF_TTL_SECONDS", 600),
        proof_secret=proof_secret,
        job_ttl_seconds=_positive_int("FAULTLINE_JOB_TTL_SECONDS", 900),
        max_jobs=_positive_int("FAULTLINE_MAX_JOBS", 100),
        demo_stage_ms=_positive_int("FAULTLINE_DEMO_STAGE_MS", 260),
        cors_origins=_origins(),
    )
