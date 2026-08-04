"""Mocked-transport tests for the local Ollama client.

No running Ollama server is required: an injected ``httpx`` transport plays the
role of the local runtime.
"""
from __future__ import annotations

import asyncio
import json
import logging

import httpx
import pytest

from faultline_api.adapters.ollama_client import (
    ModelNotFoundError,
    ModelResponseTooLargeError,
    ModelSchemaError,
    ModelTimeoutError,
    ModelUnavailableError,
    OllamaClient,
    has_vision_capability,
)
from faultline_api.config import build_settings


def _settings(monkeypatch: pytest.MonkeyPatch, **env: str):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return build_settings()


def _mock_transport(handler) -> httpx.MockTransport:
    return httpx.MockTransport(handler)


def _generate_response(payload: dict) -> httpx.Response:
    return httpx.Response(200, json={"response": json.dumps(payload), "done": True})


def test_generate_json_parses_structured_output(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/generate"
        body = json.loads(request.content)
        assert body["stream"] is False
        assert body["options"]["temperature"] == 0
        assert body["options"]["seed"] == settings.model_seed
        return _generate_response({"problem_id": "p1", "final_answer": "2/5"})

    client = OllamaClient(settings, transport=_mock_transport(handler))
    result = asyncio.run(client.generate_json(model="m", prompt="x"))
    assert result == {"problem_id": "p1", "final_answer": "2/5"}


def test_generate_json_retries_once_on_malformed_then_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings(monkeypatch)
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json={"response": "not-json{", "done": True})

    client = OllamaClient(settings, transport=_mock_transport(handler))
    with pytest.raises(ModelSchemaError):
        asyncio.run(client.generate_json(model="m", prompt="x"))
    assert calls["n"] == 2  # exactly one retry


def test_generate_json_recovers_on_second_attempt(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings(monkeypatch)
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(200, json={"response": "garbage", "done": True})
        return _generate_response({"problem_id": "p2"})

    client = OllamaClient(settings, transport=_mock_transport(handler))
    result = asyncio.run(client.generate_json(model="m", prompt="x"))
    assert result["problem_id"] == "p2"
    assert calls["n"] == 2


def test_missing_model_maps_to_typed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": "model not found"})

    client = OllamaClient(settings, transport=_mock_transport(handler))
    with pytest.raises(ModelNotFoundError):
        asyncio.run(client.generate_json(model="absent", prompt="x"))


def test_unreachable_server_maps_to_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = OllamaClient(settings, transport=_mock_transport(handler))
    with pytest.raises(ModelUnavailableError):
        asyncio.run(client.generate_json(model="m", prompt="x"))


def test_timeout_maps_to_typed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    client = OllamaClient(settings, transport=_mock_transport(handler))
    with pytest.raises(ModelTimeoutError):
        asyncio.run(client.generate_json(model="m", prompt="x"))


def test_oversized_response_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings(monkeypatch, FAULTLINE_MAX_MODEL_RESPONSE_BYTES="2048")
    big = "x" * 5000

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": big, "done": True})

    client = OllamaClient(settings, transport=_mock_transport(handler))
    with pytest.raises(ModelResponseTooLargeError):
        asyncio.run(client.generate_json(model="m", prompt="x"))


def test_concurrency_is_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings(monkeypatch, FAULTLINE_MODEL_MAX_CONCURRENCY="2")
    state = {"current": 0, "peak": 0}

    class RecordingTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            state["current"] += 1
            state["peak"] = max(state["peak"], state["current"])
            await asyncio.sleep(0.02)
            state["current"] -= 1
            return _generate_response({"problem_id": "p1"})

    client = OllamaClient(settings, transport=RecordingTransport())

    async def run_many() -> None:
        await asyncio.gather(
            *[client.generate_json(model="m", prompt=str(i)) for i in range(8)]
        )

    asyncio.run(run_many())
    assert state["peak"] <= 2


def test_no_image_bytes_or_prompt_in_logs(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    settings = _settings(monkeypatch)
    secret_prompt = "SENSITIVE-STUDENT-WORK-1/2+1/3"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": "still-not-json", "done": True})

    client = OllamaClient(settings, transport=_mock_transport(handler))
    with caplog.at_level(logging.DEBUG, logger="faultline.model"):
        with pytest.raises(ModelSchemaError):
            asyncio.run(client.generate_json(model="m", prompt=secret_prompt, images=[b"IMAGEBYTES"]))
    blob = " ".join(record.getMessage() for record in caplog.records)
    assert secret_prompt not in blob
    assert "IMAGEBYTES" not in blob
    assert "still-not-json" not in blob


def test_vision_capability_detection() -> None:
    assert has_vision_capability({"capabilities": ["completion", "vision"]}) is True
    assert has_vision_capability({"capabilities": ["completion"]}) is False
    assert has_vision_capability({"details": {"families": ["qwen2vl", "clip"]}}) is True
    assert has_vision_capability({"details": {"families": ["llama"]}}) is False
