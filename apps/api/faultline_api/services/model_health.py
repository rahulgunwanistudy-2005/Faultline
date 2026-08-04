"""Runtime + local-model health reporting.

Exposes non-secret runtime configuration and, in ``local_ai`` mode, probes the
local Ollama server for the configured models and their image capability. Never
returns secrets or full local filesystem paths.
"""
from __future__ import annotations

from urllib.parse import urlparse

from ..adapters.ollama_client import (
    ModelError,
    OllamaClient,
    has_vision_capability,
)
from ..config import Settings, get_settings


def _redacted_base_url(url: str) -> str:
    """Return scheme://host:port only (no path, query, or credentials)."""
    parsed = urlparse(url)
    host = parsed.hostname or "unknown"
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://{host}{port}"


def runtime_summary(settings: Settings | None = None) -> dict[str, object]:
    settings = settings or get_settings()
    return {
        "runtime_mode": settings.runtime_mode,
        "model_provider": settings.model_provider,
        "local_ai": settings.is_local_ai,
        "vision_model": settings.vision_model,
        "hypothesis_model": settings.hypothesis_model,
        "model_endpoint": _redacted_base_url(settings.ollama_base_url),
        "transcription_passes": settings.transcription_passes,
        "max_hypothesis_proposals": settings.max_hypothesis_proposals,
        "bayesian": {
            "prior_mode": settings.bayesian_prior_mode,
            "abstention_entropy_threshold": settings.bayesian_abstention_entropy_threshold,
            "top_two_margin_threshold": settings.bayesian_top_two_margin_threshold,
        },
    }


async def model_health(
    settings: Settings | None = None,
    client: OllamaClient | None = None,
) -> dict[str, object]:
    settings = settings or get_settings()
    base = runtime_summary(settings)

    if not settings.is_local_ai:
        return {
            **base,
            "status": "fixture_mode",
            "detail": "Fixture mode is deterministic and requires no local model.",
            "models": [],
        }

    client = client or OllamaClient(settings)
    try:
        installed = await client.list_models()
    except ModelError as exc:
        return {
            **base,
            "status": "unavailable",
            "detail": exc.client_message,
            "models": [],
        }

    installed_names = {str(entry.get("name", "")) for entry in installed}
    wanted = _wanted_models(settings)
    models: list[dict[str, object]] = []
    overall_ok = True
    for role, model_name in wanted:
        present = model_name in installed_names or _name_without_tag(model_name, installed_names)
        vision_ok: bool | None = None
        detail = "installed" if present else "not installed — run `ollama pull`"
        if present and role == "vision":
            try:
                show = await client.show_model(model_name)
                vision_ok = has_vision_capability(show)
                if not vision_ok:
                    detail = "installed but no image capability detected"
            except ModelError as exc:
                detail = exc.client_message
                present = False
        ok = present and (vision_ok is not False)
        overall_ok = overall_ok and ok
        models.append(
            {
                "role": role,
                "model": model_name,
                "installed": present,
                "vision_capable": vision_ok,
                "ok": ok,
                "detail": detail,
            }
        )

    return {
        **base,
        "status": "ready" if overall_ok else "degraded",
        "detail": "All configured local models are ready."
        if overall_ok
        else "One or more configured local models are missing or incapable.",
        "models": models,
    }


def _wanted_models(settings: Settings) -> list[tuple[str, str]]:
    wanted = [("vision", settings.vision_model)]
    if settings.hypothesis_model != settings.vision_model:
        wanted.append(("hypothesis", settings.hypothesis_model))
    else:
        wanted.append(("hypothesis", settings.hypothesis_model))
    return wanted


def _name_without_tag(model_name: str, installed_names: set[str]) -> bool:
    """Match ``qwen3-vl:4b`` against installed ``qwen3-vl:4b`` or bare name variants."""
    base = model_name.split(":", 1)[0]
    return any(name.split(":", 1)[0] == base for name in installed_names)
