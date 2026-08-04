from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import time
from typing import Any
from uuid import uuid4

from dataclasses import dataclass

from faultline_core import HYPOTHESIS_MAP

from ..config import get_settings
from .demo import get_student_private
from .jobs import STORE


class ProofTokenError(ValueError):
    pass


@dataclass(frozen=True)
class HeldOutContext:
    """Normalized held-out prediction context, from the demo fixture or an upload job."""

    available: bool
    state: str
    problem: dict | None = None
    hypothesis_id: str | None = None
    predicted_answer: str | None = None
    actual_answer: str | None = None
    ocr_confidence: int | None = None


def _resolve_context(student_id: str) -> HeldOutContext | None:
    demo_student = get_student_private(student_id)
    if demo_student is not None:
        diagnosis = demo_student["diagnosis"]
        held_out = demo_student["held_out"]
        hypothesis_id = diagnosis["hypothesis_id"]
        available = diagnosis["state"] == "named_diagnosis" and hypothesis_id in HYPOTHESIS_MAP
        if not available:
            return HeldOutContext(False, diagnosis["state"])
        problem = held_out["problem"]
        predicted = str(HYPOTHESIS_MAP[hypothesis_id].predict(_problem_from_payload(problem)))
        return HeldOutContext(
            available=True,
            state=diagnosis["state"],
            problem=problem,
            hypothesis_id=hypothesis_id,
            predicted_answer=predicted,
            actual_answer=held_out["actual_answer"],
            ocr_confidence=held_out["ocr_confidence"],
        )

    job = STORE.get(student_id)
    if job is not None and job.kind == "local_ai":
        private = job.private_data.get(student_id)
        if private is None:
            return HeldOutContext(False, "withheld")
        return HeldOutContext(
            available=True,
            state="named_diagnosis",
            problem=private["problem"],
            hypothesis_id=private["hypothesis_id"],
            predicted_answer=private["predicted_answer"],
            actual_answer=private["actual_answer"],
            ocr_confidence=private["ocr_confidence"],
        )
    return None


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(value + padding)
    except (ValueError, binascii.Error) as exc:
        raise ProofTokenError("invalid proof token encoding") from exc


def _sign(payload: bytes) -> str:
    digest = hmac.new(get_settings().proof_secret, payload, hashlib.sha256).digest()
    return _encode(digest)


def create_prediction(student_id: str) -> dict[str, Any] | None:
    context = _resolve_context(student_id)
    if context is None:
        return None
    if not context.available:
        return {
            "student_id": student_id,
            "state": "withheld",
            "reason": "The evidence is not strong enough for a held-out prediction.",
        }

    problem = context.problem
    claims = {
        "student_id": student_id,
        "problem_id": problem["id"],
        "hypothesis_id": context.hypothesis_id,
        "predicted_answer": context.predicted_answer,
        "issued_at": int(time.time()),
        "nonce": str(uuid4()),
    }
    encoded_payload = _encode(json.dumps(claims, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    proof_token = f"{encoded_payload}.{_sign(encoded_payload.encode('ascii'))}"
    return {
        "student_id": student_id,
        "state": "locked",
        "problem_id": problem["id"],
        "expression": problem["expression"],
        "hypothesis_id": context.hypothesis_id,
        "predicted_answer": context.predicted_answer,
        "proof_token": proof_token,
        "expires_in_seconds": get_settings().proof_ttl_seconds,
    }


def reveal_prediction(student_id: str, proof_token: str) -> dict[str, Any] | None:
    context = _resolve_context(student_id)
    if context is None:
        return None
    claims = _verify_token(proof_token)
    if claims.get("student_id") != student_id:
        raise ProofTokenError("proof token does not belong to this student")
    if not context.available or context.problem is None:
        raise ProofTokenError("no held-out prediction is available for this student")
    if claims.get("problem_id") != context.problem["id"]:
        raise ProofTokenError("proof token is for a different problem")
    actual = context.actual_answer
    return {
        "student_id": student_id,
        "state": "revealed",
        "problem_id": claims["problem_id"],
        "hypothesis_id": claims["hypothesis_id"],
        "predicted_answer": claims["predicted_answer"],
        "actual_answer": actual,
        "matched": claims["predicted_answer"] == actual,
        "ocr_confidence": context.ocr_confidence,
    }


def _verify_token(token: str) -> dict[str, Any]:
    try:
        payload_segment, signature = token.split(".", 1)
    except ValueError as exc:
        raise ProofTokenError("malformed proof token") from exc
    expected = _sign(payload_segment.encode("ascii"))
    if not hmac.compare_digest(signature, expected):
        raise ProofTokenError("invalid proof token signature")
    try:
        claims = json.loads(_decode(payload_segment))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ProofTokenError("invalid proof token payload") from exc
    issued_at = claims.get("issued_at")
    if not isinstance(issued_at, int):
        raise ProofTokenError("proof token has no issue time")
    age = int(time.time()) - issued_at
    if age < -30 or age > get_settings().proof_ttl_seconds:
        raise ProofTokenError("proof token has expired")
    required = {"student_id", "problem_id", "hypothesis_id", "predicted_answer", "nonce"}
    if not required.issubset(claims):
        raise ProofTokenError("proof token is incomplete")
    return claims


def _problem_from_payload(payload: dict[str, Any]):
    from faultline_core import FractionProblem

    return FractionProblem(
        id=payload["id"],
        n1=payload["n1"],
        d1=payload["d1"],
        n2=payload["n2"],
        d2=payload["d2"],
        operation=payload.get("operation", "+"),
        form=payload.get("form", "bare"),
    )
