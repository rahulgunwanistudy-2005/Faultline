from __future__ import annotations

import ipaddress
import os
import secrets
from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import urlparse


class ConfigError(RuntimeError):
    """Raised for an invalid or out-of-range configuration value."""


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer") from exc
    if value <= 0:
        raise ConfigError(f"{name} must be positive")
    return value


def _int_in_range(name: str, default: int, low: int, high: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer") from exc
    if not low <= value <= high:
        raise ConfigError(f"{name} must be between {low} and {high}")
    return value


def _float_in_range(name: str, default: float, low: float, high: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number") from exc
    if not low <= value <= high:
        raise ConfigError(f"{name} must be between {low} and {high}")
    return value


def _choice(name: str, default: str, allowed: frozenset[str]) -> str:
    value = os.getenv(name, default).strip().lower()
    if value not in allowed:
        raise ConfigError(f"{name} must be one of {sorted(allowed)}; got {value!r}")
    return value


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _origins() -> tuple[str, ...]:
    raw = os.getenv("FAULTLINE_CORS_ORIGINS", "")
    return tuple(origin.strip() for origin in raw.split(",") if origin.strip())


RUNTIME_MODES = frozenset({"local_ai", "fixture"})
MODEL_PROVIDERS = frozenset({"ollama"})
PRIOR_MODES = frozenset({"uniform", "configured"})


def _validated_model_base_url(name: str, default: str, allow_private: bool) -> str:
    """Return a model base URL restricted to loopback (or opted-in private) hosts.

    Runtime model calls must stay local. A public/global host is rejected outright;
    a private-range host is allowed only when FAULTLINE_ALLOW_PRIVATE_MODEL_HOSTS is set.
    """
    url = os.getenv(name, default).strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ConfigError(f"{name} must be an http(s) URL with a host")
    host = parsed.hostname
    if host in {"localhost", "localhost.localdomain"}:
        return url
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ConfigError(
            f"{name} host must be a loopback/private IP or localhost; got {host!r}"
        ) from exc
    if address.is_loopback:
        return url
    if address.is_private and allow_private:
        return url
    raise ConfigError(
        f"{name} host {host!r} is not permitted. Runtime model calls must be local; "
        "set FAULTLINE_ALLOW_PRIVATE_MODEL_HOSTS=1 to opt into a private-range host."
    )


@dataclass(frozen=True)
class Settings:
    # Existing v0.2.0 fields (unchanged meaning)
    max_upload_bytes: int
    max_image_pixels: int
    proof_ttl_seconds: int
    proof_secret: bytes
    job_ttl_seconds: int
    max_jobs: int
    demo_stage_ms: int
    cors_origins: tuple[str, ...]
    # Runtime mode + model provider
    runtime_mode: str
    model_provider: str
    ollama_base_url: str
    vision_model: str
    hypothesis_model: str
    allow_private_model_hosts: bool
    # Model client bounds
    model_timeout_seconds: float
    model_connect_timeout_seconds: float
    model_max_concurrency: int
    model_keep_alive: str
    model_seed: int
    transcription_passes: int
    max_model_response_bytes: int
    max_hypothesis_proposals: int
    # OCR / reading-consensus thresholds
    ocr_auto_accept_threshold: float
    ocr_review_threshold: float
    # Novel-rule verifier thresholds
    novel_rule_min_reproduction: float
    novel_rule_validation_reproduction: float
    # Bayesian inference configuration
    bayesian_prior_mode: str
    bayesian_answer_match_probability: float
    bayesian_answer_mismatch_probability: float
    bayesian_step_match_probability: float
    bayesian_step_mismatch_probability: float
    bayesian_abstention_entropy_threshold: float
    bayesian_top_two_margin_threshold: float

    @property
    def is_local_ai(self) -> bool:
        return self.runtime_mode == "local_ai"


def build_settings() -> Settings:
    configured_secret = os.getenv("FAULTLINE_PROOF_SECRET", "").encode("utf-8")
    # A random process-local secret is safe for the single-worker demo. Deployments
    # with multiple workers must set FAULTLINE_PROOF_SECRET so tokens survive routing.
    proof_secret = configured_secret or secrets.token_bytes(32)
    allow_private = _bool("FAULTLINE_ALLOW_PRIVATE_MODEL_HOSTS", False)
    return Settings(
        max_upload_bytes=_positive_int("FAULTLINE_MAX_UPLOAD_BYTES", 8 * 1024 * 1024),
        max_image_pixels=_positive_int("FAULTLINE_MAX_IMAGE_PIXELS", 20_000_000),
        proof_ttl_seconds=_positive_int("FAULTLINE_PROOF_TTL_SECONDS", 600),
        proof_secret=proof_secret,
        job_ttl_seconds=_positive_int("FAULTLINE_JOB_TTL_SECONDS", 900),
        max_jobs=_positive_int("FAULTLINE_MAX_JOBS", 100),
        demo_stage_ms=_positive_int("FAULTLINE_DEMO_STAGE_MS", 260),
        cors_origins=_origins(),
        # Default mode is the safe, deterministic fixture so a zero-config checkout,
        # the existing tests, and the public deployment keep working without a model.
        # The local-AI setup explicitly exports FAULTLINE_RUNTIME_MODE=local_ai.
        runtime_mode=_choice("FAULTLINE_RUNTIME_MODE", "fixture", RUNTIME_MODES),
        model_provider=_choice("FAULTLINE_MODEL_PROVIDER", "ollama", MODEL_PROVIDERS),
        ollama_base_url=_validated_model_base_url(
            "FAULTLINE_OLLAMA_BASE_URL", "http://127.0.0.1:11434", allow_private
        ),
        vision_model=os.getenv("FAULTLINE_VISION_MODEL", "qwen3-vl:4b").strip(),
        hypothesis_model=os.getenv("FAULTLINE_HYPOTHESIS_MODEL", "qwen3-vl:4b").strip(),
        allow_private_model_hosts=allow_private,
        model_timeout_seconds=_float_in_range("FAULTLINE_MODEL_TIMEOUT_SECONDS", 60.0, 1.0, 600.0),
        model_connect_timeout_seconds=_float_in_range(
            "FAULTLINE_MODEL_CONNECT_TIMEOUT_SECONDS", 5.0, 0.5, 60.0
        ),
        model_max_concurrency=_int_in_range("FAULTLINE_MODEL_MAX_CONCURRENCY", 2, 1, 32),
        model_keep_alive=os.getenv("FAULTLINE_MODEL_KEEP_ALIVE", "5m").strip(),
        model_seed=_int_in_range("FAULTLINE_MODEL_SEED", 7, 0, 2**31 - 1),
        transcription_passes=_int_in_range("FAULTLINE_TRANSCRIPTION_PASSES", 3, 1, 5),
        max_model_response_bytes=_int_in_range(
            "FAULTLINE_MAX_MODEL_RESPONSE_BYTES", 262_144, 1024, 8 * 1024 * 1024
        ),
        max_hypothesis_proposals=_int_in_range("FAULTLINE_MAX_HYPOTHESIS_PROPOSALS", 3, 0, 10),
        ocr_auto_accept_threshold=_float_in_range("FAULTLINE_OCR_AUTO_ACCEPT_THRESHOLD", 0.80, 0.0, 1.0),
        ocr_review_threshold=_float_in_range("FAULTLINE_OCR_REVIEW_THRESHOLD", 0.55, 0.0, 1.0),
        novel_rule_min_reproduction=_float_in_range(
            "FAULTLINE_NOVEL_RULE_MIN_REPRODUCTION", 0.70, 0.0, 1.0
        ),
        novel_rule_validation_reproduction=_float_in_range(
            "FAULTLINE_NOVEL_RULE_VALIDATION_REPRODUCTION", 0.80, 0.0, 1.0
        ),
        bayesian_prior_mode=_choice("FAULTLINE_BAYESIAN_PRIOR_MODE", "uniform", PRIOR_MODES),
        bayesian_answer_match_probability=_float_in_range(
            "FAULTLINE_BAYESIAN_ANSWER_MATCH_PROBABILITY", 0.90, 0.01, 0.999
        ),
        bayesian_answer_mismatch_probability=_float_in_range(
            "FAULTLINE_BAYESIAN_ANSWER_MISMATCH_PROBABILITY", 0.08, 0.001, 0.5
        ),
        bayesian_step_match_probability=_float_in_range(
            "FAULTLINE_BAYESIAN_STEP_MATCH_PROBABILITY", 0.80, 0.01, 0.999
        ),
        bayesian_step_mismatch_probability=_float_in_range(
            "FAULTLINE_BAYESIAN_STEP_MISMATCH_PROBABILITY", 0.30, 0.001, 0.999
        ),
        bayesian_abstention_entropy_threshold=_float_in_range(
            "FAULTLINE_BAYESIAN_ABSTENTION_ENTROPY_THRESHOLD", 1.20, 0.0, 10.0
        ),
        bayesian_top_two_margin_threshold=_float_in_range(
            "FAULTLINE_BAYESIAN_TOP_TWO_MARGIN_THRESHOLD", 0.15, 0.0, 1.0
        ),
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return build_settings()
