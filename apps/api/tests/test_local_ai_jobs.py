"""End-to-end local-AI lifecycle via the HTTP API (Phase 8).

Uses an injected fake model client, so no running Ollama is required. Verifies
there is no silent fixture fallback and that the signed held-out proof works on
a real uploaded worksheet.
"""
from __future__ import annotations

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from faultline_api import config
from faultline_api.main import app
from faultline_api.services.background_jobs import reset_client_factory, set_client_factory


def _png(width: int = 1200, height: int = 1600) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (width, height), "white").save(buffer, format="PNG")
    return buffer.getvalue()


ADD_ACROSS_READING = {
    "problem_id": "p1",
    "visible_expression": "1/2 + 1/3",
    "final_answer": "2/5",
    "intermediate_lines": ["1 + 1 = 2", "2 + 3 = 5"],
    "step_features": ["numerators_added", "denominators_added"],
    "legibility": "clear",
    "uncertain_tokens": [],
}


class SmartFake:
    """Returns a transcription for vision prompts and a proposal batch otherwise."""

    async def generate_json(self, *, model, prompt, images=None, schema=None):
        if "propose candidate procedures" in prompt:
            return {"known_hypothesis_ids": ["add_across"], "proposals": []}
        return dict(ADD_ACROSS_READING)


class FailingFake:
    async def generate_json(self, *, model, prompt, images=None, schema=None):
        from faultline_api.adapters.ollama_client import ModelUnavailableError

        raise ModelUnavailableError("server down")


@pytest.fixture
def local_ai_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FAULTLINE_RUNTIME_MODE", "local_ai")
    monkeypatch.setenv("FAULTLINE_PROOF_SECRET", "test-secret-that-is-long-enough-for-hmac")
    config.get_settings.cache_clear()
    client = TestClient(app)
    try:
        yield client
    finally:
        reset_client_factory()
        config.get_settings.cache_clear()


def test_local_ai_upload_produces_real_diagnosis(local_ai_client: TestClient) -> None:
    set_client_factory(lambda settings: SmartFake())
    accepted = local_ai_client.post(
        "/v1/analyses?template_id=fractions-v1",
        content=_png(),
        headers={"Content-Type": "image/png", "X-Filename": "worksheet.png"},
    )
    assert accepted.status_code == 202
    body = accepted.json()
    assert body["mode"] == "local_ai"
    assert body["status"] == "complete"  # synchronous single-worker pipeline

    result = local_ai_client.get(f"/v1/analyses/{body['analysis_id']}")
    payload = result.json()
    assert payload["status"] == "complete"
    assert payload["mode"] == "local_ai"
    assert payload["result"]["analysis_mode"] == "local_ai"
    assert payload["result"]["summary"]["students"] == 1
    assert payload["result"]["dataset_type"] == "live_local_ai"
    student = payload["result"]["students"][0]
    assert student["diagnosis"]["hypothesis_id"] == "add_across"
    assert student["diagnosis"]["state"] == "named_diagnosis"
    assert "bayesian" in student["diagnosis"]  # additive technical field
    assert payload["result"]["analysis_meta"]["runtime_mode"] == "local_ai"
    assert "stages" in payload
    assert payload["stages"][-1] == "complete"


def test_local_ai_no_held_out_leakage(local_ai_client: TestClient) -> None:
    set_client_factory(lambda settings: SmartFake())
    accepted = local_ai_client.post(
        "/v1/analyses?template_id=fractions-v1",
        content=_png(),
        headers={"Content-Type": "image/png"},
    ).json()
    result = local_ai_client.get(f"/v1/analyses/{accepted['analysis_id']}")
    assert "actual_answer" not in result.text


def test_local_ai_held_out_proof_flow(local_ai_client: TestClient) -> None:
    set_client_factory(lambda settings: SmartFake())
    accepted = local_ai_client.post(
        "/v1/analyses?template_id=fractions-v1",
        content=_png(),
        headers={"Content-Type": "image/png"},
    ).json()
    student_id = accepted["analysis_id"]

    prediction = local_ai_client.post(f"/v1/students/{student_id}/held-out-prediction")
    assert prediction.status_code == 200
    locked = prediction.json()
    assert locked["state"] == "locked"
    assert "actual_answer" not in locked
    token = locked["proof_token"]

    reveal = local_ai_client.post(
        f"/v1/students/{student_id}/held-out-reveal", json={"proof_token": token}
    )
    assert reveal.status_code == 200
    revealed = reveal.json()
    assert revealed["state"] == "revealed"
    assert revealed["matched"] is True
    assert revealed["actual_answer"] == revealed["predicted_answer"]


def test_local_ai_failure_has_no_fixture_fallback(local_ai_client: TestClient) -> None:
    set_client_factory(lambda settings: FailingFake())
    accepted = local_ai_client.post(
        "/v1/analyses?template_id=fractions-v1",
        content=_png(),
        headers={"Content-Type": "image/png"},
    ).json()
    result = local_ai_client.get(f"/v1/analyses/{accepted['analysis_id']}")
    payload = result.json()
    assert payload["status"] == "failed"
    assert payload["result"] is None  # never the synthetic 12-student fixture
    assert "error" in payload
    # The synthetic fixture must not leak into a local-AI failure.
    assert "Period 3" not in result.text


def test_runtime_endpoint_reports_local_ai(local_ai_client: TestClient) -> None:
    runtime = local_ai_client.get("/v1/runtime").json()
    assert runtime["runtime_mode"] == "local_ai"
    assert runtime["local_ai"] is True
