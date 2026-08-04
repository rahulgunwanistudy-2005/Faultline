"""Model-health service tests (mocked transport, no real Ollama)."""
from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from faultline_api.adapters.ollama_client import OllamaClient
from faultline_api.config import build_settings
from faultline_api.services.model_health import model_health, runtime_summary


def _local_ai_settings(monkeypatch: pytest.MonkeyPatch, **env: str):
    monkeypatch.setenv("FAULTLINE_RUNTIME_MODE", "local_ai")
    monkeypatch.setenv("FAULTLINE_VISION_MODEL", "qwen3-vl:4b")
    monkeypatch.setenv("FAULTLINE_HYPOTHESIS_MODEL", "qwen3-vl:4b")
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return build_settings()


def _client(settings, handler) -> OllamaClient:
    return OllamaClient(settings, transport=httpx.MockTransport(handler))


def test_runtime_summary_redacts_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _local_ai_settings(monkeypatch)
    summary = runtime_summary(settings)
    assert summary["runtime_mode"] == "local_ai"
    assert summary["model_endpoint"] == "http://127.0.0.1:11434"
    assert "proof" not in json.dumps(summary).lower()


def test_health_ready_when_vision_model_present(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _local_ai_settings(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "qwen3-vl:4b"}]})
        if request.url.path == "/api/show":
            return httpx.Response(200, json={"capabilities": ["completion", "vision"]})
        return httpx.Response(404)

    result = asyncio.run(model_health(settings, _client(settings, handler)))
    assert result["status"] == "ready"
    assert all(model["ok"] for model in result["models"])


def test_health_unavailable_when_server_down(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _local_ai_settings(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    result = asyncio.run(model_health(settings, _client(settings, handler)))
    assert result["status"] == "unavailable"
    assert "ollama serve" in result["detail"].lower()


def test_health_degraded_when_model_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _local_ai_settings(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "llama3:8b"}]})
        return httpx.Response(404)

    result = asyncio.run(model_health(settings, _client(settings, handler)))
    assert result["status"] == "degraded"
    assert any(model["installed"] is False for model in result["models"])


def test_health_degraded_when_model_not_vision(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _local_ai_settings(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "qwen3-vl:4b"}]})
        if request.url.path == "/api/show":
            return httpx.Response(200, json={"capabilities": ["completion"]})
        return httpx.Response(404)

    result = asyncio.run(model_health(settings, _client(settings, handler)))
    assert result["status"] == "degraded"
    vision = next(model for model in result["models"] if model["role"] == "vision")
    assert vision["vision_capable"] is False


def test_fixture_mode_health_skips_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAULTLINE_RUNTIME_MODE", "fixture")
    settings = build_settings()

    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover - must not run
        raise AssertionError("network must not be touched in fixture mode")

    result = asyncio.run(model_health(settings, _client(settings, handler)))
    assert result["status"] == "fixture_mode"
