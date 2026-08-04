"""Runtime-mode configuration and health-contract tests."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from faultline_api import config
from faultline_api.config import ConfigError, build_settings
from faultline_api.main import app

client = TestClient(app)


def test_default_mode_is_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FAULTLINE_RUNTIME_MODE", raising=False)
    settings = build_settings()
    assert settings.runtime_mode == "fixture"
    assert settings.is_local_ai is False


def test_local_ai_mode_selectable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAULTLINE_RUNTIME_MODE", "local_ai")
    settings = build_settings()
    assert settings.runtime_mode == "local_ai"
    assert settings.is_local_ai is True


def test_invalid_mode_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAULTLINE_RUNTIME_MODE", "cloud")
    with pytest.raises(ConfigError):
        build_settings()


def test_invalid_provider_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAULTLINE_MODEL_PROVIDER", "openai")
    with pytest.raises(ConfigError):
        build_settings()


def test_numeric_config_is_range_checked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAULTLINE_TRANSCRIPTION_PASSES", "99")
    with pytest.raises(ConfigError):
        build_settings()


def test_public_model_host_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAULTLINE_OLLAMA_BASE_URL", "http://8.8.8.8:11434")
    monkeypatch.delenv("FAULTLINE_ALLOW_PRIVATE_MODEL_HOSTS", raising=False)
    with pytest.raises(ConfigError):
        build_settings()


def test_loopback_model_host_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAULTLINE_OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    assert build_settings().ollama_base_url == "http://127.0.0.1:11434"


def test_private_host_requires_optin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAULTLINE_OLLAMA_BASE_URL", "http://192.168.1.50:11434")
    monkeypatch.delenv("FAULTLINE_ALLOW_PRIVATE_MODEL_HOSTS", raising=False)
    with pytest.raises(ConfigError):
        build_settings()
    monkeypatch.setenv("FAULTLINE_ALLOW_PRIVATE_MODEL_HOSTS", "1")
    assert "192.168.1.50" in build_settings().ollama_base_url


def test_runtime_endpoint_has_no_secrets() -> None:
    response = client.get("/v1/runtime")
    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime_mode"] in {"fixture", "local_ai"}
    assert payload["model_provider"] == "ollama"
    # redacted endpoint: scheme://host:port only, no path
    assert payload["model_endpoint"].count("/") == 2
    serialized = response.text.lower()
    assert "secret" not in serialized and "proof_secret" not in serialized


def test_models_health_in_fixture_mode_needs_no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    # Default (fixture) mode must not require a running Ollama server.
    config.get_settings.cache_clear()
    response = client.get("/v1/models/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "fixture_mode"
    assert payload["models"] == []
