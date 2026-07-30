from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import time
from typing import Any
from uuid import uuid4

from faultline_core import HYPOTHESIS_MAP

from ..config import get_settings
from .demo import get_student_private


class ProofTokenError(ValueError):
    pass


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
    student = get_student_private(student_id)
    if student is None:
        return None
    hypothesis_id = student["diagnosis"]["hypothesis_id"]
    if student["diagnosis"]["state"] != "named_diagnosis" or hypothesis_id not in HYPOTHESIS_MAP:
        return {
            "student_id": student_id,
            "state": "withheld",
            "reason": "The evidence is not strong enough for a held-out prediction.",
        }

    problem = student["held_out"]["problem"]
    predicted_answer = str(HYPOTHESIS_MAP[hypothesis_id].predict(_problem_from_payload(problem)))
    claims = {
        "student_id": student_id,
        "problem_id": problem["id"],
        "hypothesis_id": hypothesis_id,
        "predicted_answer": predicted_answer,
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
        "hypothesis_id": hypothesis_id,
        "predicted_answer": predicted_answer,
        "proof_token": proof_token,
        "expires_in_seconds": get_settings().proof_ttl_seconds,
    }


def reveal_prediction(student_id: str, proof_token: str) -> dict[str, Any] | None:
    student = get_student_private(student_id)
    if student is None:
        return None
    claims = _verify_token(proof_token)
    if claims.get("student_id") != student_id:
        raise ProofTokenError("proof token does not belong to this student")
    if claims.get("problem_id") != student["held_out"]["problem"]["id"]:
        raise ProofTokenError("proof token is for a different problem")
    actual = student["held_out"]["actual_answer"]
    return {
        "student_id": student_id,
        "state": "revealed",
        "problem_id": claims["problem_id"],
        "hypothesis_id": claims["hypothesis_id"],
        "predicted_answer": claims["predicted_answer"],
        "actual_answer": actual,
        "matched": claims["predicted_answer"] == actual,
        "ocr_confidence": student["held_out"]["ocr_confidence"],
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
