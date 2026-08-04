"""Minimal, hardened local Ollama client built on the existing ``httpx`` pin.

Design constraints (see docs/AI_ML_UPGRADE_PLAN.md):

* local HTTP only — the base URL is host-restricted in ``config.py``;
* connect + total timeouts and a concurrency semaphore;
* non-streaming structured (JSON) output for short calls;
* deterministic ``temperature=0`` + ``seed`` where supported;
* bounded response size;
* exactly one retry, only for malformed structured output;
* never logs images, base64, answers, raw student work, tokens, or full raw
  model responses;
* every transport failure maps to a typed internal error.
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
from typing import Any

import httpx

from ..config import Settings

LOGGER = logging.getLogger("faultline.model")


class ModelError(RuntimeError):
    """Base class for all local-model failures. Safe, generic message for clients."""

    client_message = "The local model is unavailable. See the local-AI setup instructions."


class ModelUnavailableError(ModelError):
    client_message = "The local model server is not reachable. Is `ollama serve` running?"


class ModelTimeoutError(ModelError):
    client_message = "The local model timed out. Try a smaller image or a faster model."


class ModelNotFoundError(ModelError):
    client_message = "The configured local model is not installed. Run `ollama pull <model>`."


class ModelCapabilityError(ModelError):
    client_message = "The configured local model does not support image input."


class ModelResponseTooLargeError(ModelError):
    client_message = "The local model returned an oversized response and was rejected."


class ModelSchemaError(ModelError):
    client_message = "The local model returned malformed structured output."


class OllamaClient:
    """Async client for a locally hosted Ollama runtime.

    A custom ``httpx`` transport can be injected for tests so no real server is
    required.
    """

    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._settings = settings
        self._transport = transport
        self._timeout = httpx.Timeout(
            settings.model_timeout_seconds,
            connect=settings.model_connect_timeout_seconds,
        )
        self._semaphore = asyncio.Semaphore(settings.model_max_concurrency)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._settings.ollama_base_url,
            timeout=self._timeout,
            transport=self._transport,
        )

    async def list_models(self) -> list[dict[str, Any]]:
        try:
            async with self._client() as client:
                response = await client.get("/api/tags")
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            raise ModelUnavailableError(str(exc)) from exc
        except httpx.TimeoutException as exc:
            raise ModelTimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise ModelUnavailableError(str(exc)) from exc
        if response.status_code != 200:
            raise ModelUnavailableError(f"tags returned HTTP {response.status_code}")
        payload = self._safe_json(response.content)
        models = payload.get("models", [])
        return models if isinstance(models, list) else []

    async def show_model(self, model: str) -> dict[str, Any]:
        try:
            async with self._client() as client:
                response = await client.post("/api/show", json={"model": model})
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            raise ModelUnavailableError(str(exc)) from exc
        except httpx.TimeoutException as exc:
            raise ModelTimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise ModelUnavailableError(str(exc)) from exc
        if response.status_code == 404:
            raise ModelNotFoundError(model)
        if response.status_code != 200:
            raise ModelUnavailableError(f"show returned HTTP {response.status_code}")
        return self._safe_json(response.content)

    async def generate_json(
        self,
        *,
        model: str,
        prompt: str,
        images: list[bytes] | None = None,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call ``/api/generate`` non-streaming and return parsed JSON output.

        Retries exactly once if the model returns non-JSON / malformed output.
        """
        body: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": schema if schema is not None else "json",
            "keep_alive": self._settings.model_keep_alive,
            "options": {
                "temperature": 0,
                "seed": self._settings.model_seed,
            },
        }
        if images:
            body["images"] = [base64.b64encode(image).decode("ascii") for image in images]

        last_error: ModelSchemaError | None = None
        for attempt in range(2):
            raw = await self._post_generate(model, body)
            try:
                return self._extract_json(raw)
            except ModelSchemaError as exc:
                last_error = exc
                LOGGER.warning(
                    json.dumps(
                        {
                            "event": "model_malformed_output",
                            "model": model,
                            "attempt": attempt,
                        },
                        separators=(",", ":"),
                    )
                )
        assert last_error is not None
        raise last_error

    async def _post_generate(self, model: str, body: dict[str, Any]) -> str:
        async with self._semaphore:
            try:
                async with self._client() as client:
                    response = await client.post("/api/generate", json=body)
            except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
                raise ModelUnavailableError(str(exc)) from exc
            except httpx.TimeoutException as exc:
                raise ModelTimeoutError(str(exc)) from exc
            except httpx.HTTPError as exc:
                raise ModelUnavailableError(str(exc)) from exc
        if response.status_code == 404:
            raise ModelNotFoundError(model)
        if response.status_code != 200:
            raise ModelUnavailableError(f"generate returned HTTP {response.status_code}")
        content = response.content
        if len(content) > self._settings.max_model_response_bytes:
            raise ModelResponseTooLargeError(f"{len(content)} bytes")
        envelope = self._safe_json(content)
        message = envelope.get("response")
        if not isinstance(message, str):
            raise ModelSchemaError("generate envelope has no string 'response'")
        if len(message.encode("utf-8")) > self._settings.max_model_response_bytes:
            raise ModelResponseTooLargeError(f"{len(message)} chars")
        return message

    def _safe_json(self, content: bytes) -> dict[str, Any]:
        try:
            value = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ModelSchemaError("response was not valid JSON") from exc
        if not isinstance(value, dict):
            raise ModelSchemaError("response JSON was not an object")
        return value

    def _extract_json(self, message: str) -> dict[str, Any]:
        try:
            value = json.loads(message)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ModelSchemaError("model output was not valid JSON") from exc
        if not isinstance(value, dict):
            raise ModelSchemaError("model output JSON was not an object")
        return value


def has_vision_capability(show_payload: dict[str, Any]) -> bool:
    """Best-effort check that a model can accept images.

    Ollama's ``/api/show`` exposes a ``capabilities`` list on recent versions;
    older versions expose family metadata. We treat an explicit ``vision``
    capability as authoritative and fall back to family heuristics.
    """
    capabilities = show_payload.get("capabilities")
    if isinstance(capabilities, list):
        return any(str(item).lower() == "vision" for item in capabilities)
    details = show_payload.get("details", {})
    families = details.get("families") or []
    if isinstance(families, list):
        blob = " ".join(str(item).lower() for item in families)
        if any(tag in blob for tag in ("clip", "vision", "mllama", "qwen-vl", "vl")):
            return True
    return False
