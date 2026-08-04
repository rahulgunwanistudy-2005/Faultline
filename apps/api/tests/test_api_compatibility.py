"""API compatibility snapshot for the frozen frontend contract.

The frontend under apps/web-static/ is byte-for-byte frozen. These tests pin the
shape it consumes so backend changes stay additive: required keys must remain,
and held-out answers must never appear in public payloads.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from faultline_api.main import app

client = TestClient(app)

REQUIRED_SUMMARY_KEYS = {"students", "named_diagnoses", "withheld", "mean_ocr_confidence"}
REQUIRED_LANE_KEYS = {"id", "kicker", "label", "description", "count", "students"}
REQUIRED_STUDENT_KEYS = {
    "student_id",
    "display_name",
    "lane",
    "diagnosis",
    "observations",
    "diagnostic_items",
    "held_out",
}
REQUIRED_DIAGNOSIS_KEYS = {
    "hypothesis_id",
    "label",
    "description",
    "action",
    "state",
    "posterior",
    "posterior_percent",
    "reproduction",
    "mean_ocr_confidence",
    "reasons",
    "distribution",
}
REQUIRED_OBSERVATION_KEYS = {
    "reading_id",
    "problem_id",
    "expression",
    "form",
    "observed",
    "ocr_confidence",
    "predicted",
    "matched",
    "reviewed",
}


def test_demo_class_shape_is_stable() -> None:
    payload = client.get("/v1/demo/classes/period-3").json()
    assert REQUIRED_SUMMARY_KEYS <= set(payload["summary"])
    assert payload["lanes"] and all(REQUIRED_LANE_KEYS <= set(lane) for lane in payload["lanes"])
    for student in payload["students"]:
        assert REQUIRED_STUDENT_KEYS <= set(student)
        assert REQUIRED_DIAGNOSIS_KEYS <= set(student["diagnosis"])
        for observation in student["observations"]:
            assert REQUIRED_OBSERVATION_KEYS <= set(observation)
        assert "problem" in student["held_out"]
        assert "proof_available" in student["held_out"]


def test_diagnostic_items_shape_is_stable() -> None:
    student = client.get("/v1/demo/classes/period-3").json()["students"][0]
    for item in student["diagnostic_items"]:
        assert {"id", "expression", "form", "information_gain", "separates", "explanation"} <= set(item)


def test_public_payload_has_no_held_out_answers() -> None:
    text = client.get("/v1/demo/classes/period-3").text
    assert "actual_answer" not in text
    assert "predicted_answer" not in text


def test_health_contract_unchanged() -> None:
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["service"] == "faultline-api"
