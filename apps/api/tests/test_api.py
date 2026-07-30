from __future__ import annotations

import time
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from faultline_api.main import app

client = TestClient(app)


def image_bytes(width: int = 1200, height: int = 1600) -> bytes:
    image = Image.new("RGB", (width, height), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_health_and_security_headers() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert response.headers["x-request-id"]


def test_demo_class_has_actionable_lanes_and_no_held_out_leakage() -> None:
    response = client.get("/v1/demo/classes/period-3")
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["students"] == 12
    assert any(lane["id"] == "check_wording" and lane["count"] >= 1 for lane in payload["lanes"])
    assert any(lane["id"] == "more_evidence" and lane["count"] >= 1 for lane in payload["lanes"])
    serialized = response.text
    assert "actual_answer" not in serialized
    assert "predicted_answer" not in serialized


def test_bundled_demo_asset_has_no_held_out_answers() -> None:
    asset = Path(__file__).resolve().parents[2] / "web-static" / "assets" / "demo-class.js"
    source = asset.read_text(encoding="utf-8")
    assert "actual_answer" not in source
    assert "predicted_answer" not in source


def test_upload_rejects_unsupported_type() -> None:
    response = client.post(
        "/v1/analyses?template_id=fractions-v1",
        content=b"%PDF-1.7",
        headers={"Content-Type": "application/pdf", "X-Filename": "worksheet.pdf"},
    )
    assert response.status_code == 415


def test_upload_rejects_spoofed_image() -> None:
    response = client.post(
        "/v1/analyses?template_id=fractions-v1",
        content=b"not-an-image",
        headers={"Content-Type": "image/png", "X-Filename": "page.png"},
    )
    assert response.status_code == 422
    assert "safe, readable" in response.json()["detail"]


def test_upload_returns_disclosed_bounded_job() -> None:
    response = client.post(
        "/v1/analyses?template_id=fractions-v1",
        content=image_bytes(),
        headers={"Content-Type": "image/png", "X-Filename": "page.png"},
    )
    assert response.status_code == 202
    accepted = response.json()
    assert accepted["mode"] == "synthetic_demo_fixture"
    assert accepted["upload"]["regions"] == 8
    assert accepted["upload"]["stored"] is False
    analysis_id = accepted["analysis_id"]
    payload = None
    for _ in range(20):
        result = client.get(f"/v1/analyses/{analysis_id}")
        assert result.status_code == 200
        payload = result.json()
        if payload["status"] == "complete":
            break
        time.sleep(0.01)
    assert payload is not None and payload["status"] == "complete"
    assert payload["result"]["summary"]["students"] == 12
    assert payload["result"]["analysis_mode"] == "synthetic_demo_fixture"
    assert "Live handwriting recognition is not enabled" in payload["disclosure"]


def test_prediction_then_signed_reveal_has_no_initial_leakage() -> None:
    prediction = client.post("/v1/students/cleo/held-out-prediction")
    assert prediction.status_code == 200
    prediction_payload = prediction.json()
    assert "actual_answer" not in prediction_payload
    assert prediction_payload["predicted_answer"] == "3/10"
    assert prediction_payload["proof_token"]
    reveal = client.post(
        "/v1/students/cleo/held-out-reveal",
        json={"proof_token": prediction_payload["proof_token"]},
    )
    assert reveal.status_code == 200
    assert reveal.json()["actual_answer"] == "3/10"
    assert reveal.json()["matched"] is True


def test_tampered_or_cross_student_proof_is_rejected() -> None:
    prediction = client.post("/v1/students/bea/held-out-prediction").json()
    token = prediction["proof_token"]
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    assert client.post("/v1/students/bea/held-out-reveal", json={"proof_token": tampered}).status_code == 409
    assert client.post("/v1/students/cleo/held-out-reveal", json={"proof_token": token}).status_code == 409


def test_static_app_and_judge_mode_load() -> None:
    home = client.get("/")
    judge = client.get("/judge")
    assert home.status_code == 200
    assert "See the procedure behind the error" in home.text
    assert judge.status_code == 200
    assert "30-second Judge Mode" in judge.text


def test_correction_recomputes_result_and_validates_reading() -> None:
    accepted = client.post(
        "/v1/analyses?template_id=fractions-v1",
        content=image_bytes(),
        headers={"Content-Type": "image/png", "X-Filename": "page.png"},
    )
    analysis_id = accepted.json()["analysis_id"]
    invalid = client.patch(
        f"/v1/analyses/{analysis_id}/readings/jai-p1",
        json={"normalized_answer": "not a fraction", "step_features": []},
    )
    assert invalid.status_code == 422
    missing = client.patch(
        f"/v1/analyses/{analysis_id}/readings/unknown-reading",
        json={"normalized_answer": "1", "step_features": []},
    )
    assert missing.status_code == 404
    corrected = client.patch(
        f"/v1/analyses/{analysis_id}/readings/jai-p1",
        json={"normalized_answer": "1/1", "step_features": ["numerators_added", "first_denominator_kept"]},
    )
    assert corrected.status_code == 200
    reading = next(
        item
        for student in corrected.json()["result"]["students"]
        if student["student_id"] == "jai"
        for item in student["observations"]
        if item["problem_id"] == "p1"
    )
    assert reading["reviewed"] is True
    assert reading["ocr_confidence"] == 100


def test_api_responses_are_not_cacheable_and_extra_json_is_rejected() -> None:
    demo = client.get("/v1/demo/classes/period-3")
    assert demo.headers["cache-control"] == "no-store"
    prediction = client.post("/v1/students/bea/held-out-prediction").json()
    response = client.post(
        "/v1/students/bea/held-out-reveal",
        json={"proof_token": prediction["proof_token"], "unexpected": "field"},
    )
    assert response.status_code == 422


def test_upload_rejects_body_over_default_limit() -> None:
    response = client.post(
        "/v1/analyses?template_id=fractions-v1",
        content=b"x" * (8 * 1024 * 1024 + 1),
        headers={"Content-Type": "image/png", "X-Filename": "oversized.png"},
    )
    assert response.status_code == 413


def test_filename_is_reduced_to_a_safe_basename() -> None:
    accepted = client.post(
        "/v1/analyses?template_id=fractions-v1",
        content=image_bytes(),
        headers={"Content-Type": "image/png", "X-Filename": "../../private/worksheet.png"},
    )
    analysis_id = accepted.json()["analysis_id"]
    result = client.get(f"/v1/analyses/{analysis_id}")
    assert result.json()["filename"] == "worksheet.png"
