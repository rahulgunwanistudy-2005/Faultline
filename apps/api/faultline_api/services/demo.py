from __future__ import annotations

import json
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from typing import Any

from faultline_core import (
    FractionProblem,
    HYPOTHESIS_MAP,
    Observation,
    confidence_gate,
    infer,
    parse_fraction,
    rank_items,
)

ROOT = Path(__file__).resolve().parents[4]
DATA_PATH = ROOT / "data" / "demo_class.json"
ITEM_BANK_PATH = ROOT / "data" / "item_bank.json"

ACTION_LANES = {
    "re_explain": {
        "label": "Re-explain before more practice",
        "kicker": "A stable wrong procedure is running",
        "description": "More repetition would make the wrong routine faster. Re-anchor the idea first.",
    },
    "guided_practice": {
        "label": "Use short guided practice",
        "kicker": "No stable wrong procedure is visible",
        "description": "There is no single habit to unlearn. Build a reliable procedure with short prompts.",
    },
    "check_wording": {
        "label": "Check wording or context",
        "kicker": "The math works in bare computation",
        "description": "The procedure looks intact. Written context may be blocking access to the problem.",
    },
    "confirm_or_extend": {
        "label": "Confirm, then extend",
        "kicker": "The procedure is intact",
        "description": "No repeated fault is visible in this set. Confirm once, then move forward.",
    },
    "more_evidence": {
        "label": "Collect more evidence first",
        "kicker": "Faultline will not guess",
        "description": "The reading or posterior is not strong enough for a named diagnosis.",
    },
}


@lru_cache(maxsize=1)
def _load() -> dict[str, Any]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _item_bank() -> tuple[FractionProblem, ...]:
    raw_items = json.loads(ITEM_BANK_PATH.read_text(encoding="utf-8"))
    return tuple(FractionProblem(**item) for item in raw_items)


def _problems(data: dict[str, Any]) -> dict[str, FractionProblem]:
    return {
        raw["id"]: FractionProblem(
            id=raw["id"],
            n1=raw["n1"],
            d1=raw["d1"],
            n2=raw["n2"],
            d2=raw["d2"],
            operation=raw.get("operation", "+"),
            form=raw.get("form", "bare"),
        )
        for raw in data["problems"]
    }


def _detect_wording_signal(visible: list[dict[str, Any]], problems: dict[str, FractionProblem]) -> bool:
    correct = HYPOTHESIS_MAP["correct_common_denominator"]
    bare: list[bool] = []
    word: list[bool] = []
    for item in visible:
        problem = problems[item["problem_id"]]
        matched = parse_fraction(item["answer"]) == correct.predict(problem)
        (word if problem.form == "word" else bare).append(matched)
    return len(bare) >= 3 and len(word) >= 2 and sum(bare) / len(bare) >= 0.8 and sum(word) == 0


def _diagnostic_items(posterior: dict[str, float]) -> list[dict[str, Any]]:
    top_ids = [key for key in posterior if key in HYPOTHESIS_MAP][:2]
    ranked = rank_items(list(_item_bank()), posterior, 3)
    output: list[dict[str, Any]] = []
    for gain, item in ranked:
        predictions = {
            hypothesis_id: str(HYPOTHESIS_MAP[hypothesis_id].predict(item))
            for hypothesis_id in top_ids
        }
        explanation = "Different surviving procedures produce different answers here."
        if len(set(predictions.values())) <= 1:
            explanation = "Useful as a confidence check after the separating questions."
        output.append(
            {
                "id": item.id,
                "expression": item.expression,
                "form": item.form,
                "information_gain": round(gain, 3),
                "separates": predictions,
                "explanation": explanation,
            }
        )
    return output


def _build_students(
    corrections: dict[str, dict[str, Any]],
    *,
    include_private: bool,
) -> list[dict[str, Any]]:
    data = _load()
    problems = _problems(data)
    students: list[dict[str, Any]] = []

    for raw_student in data["students"]:
        held_out = next(item for item in raw_student["observations"] if item.get("held_out"))
        visible = [dict(item) for item in raw_student["observations"] if not item.get("held_out")]
        for item in visible:
            correction = corrections.get(f"{raw_student['student_id']}-{item['problem_id']}")
            if correction:
                item["answer"] = correction["normalized_answer"]
                item["ocr_confidence"] = 1.0
                item["step_features"] = correction.get("step_features", [])
                item["reviewed"] = True
        observations = [
            Observation.exact(
                problem=problems[item["problem_id"]],
                value=parse_fraction(item["answer"]),
                confidence=item["ocr_confidence"],
                step_features=item.get("step_features", ()),
            )
            for item in visible
        ]
        result = infer(observations)
        gate = confidence_gate(result)
        top_id = str(gate["top_hypothesis"])
        wording_signal = _detect_wording_signal(visible, problems)

        if gate["state"] != "named_diagnosis":
            lane = "more_evidence"
            label = "Evidence is not strong enough yet"
            description = "Faultline is withholding a diagnosis until the reading or pattern is clearer."
            action = "Ask the three separating questions"
        elif wording_signal:
            lane = "check_wording"
            label = "Bare computation works; wording may be the barrier"
            description = "The same fraction operation is correct without written context and breaks inside word problems."
            action = "Check wording or context"
        elif top_id == "no_consistent_procedure":
            lane = "guided_practice"
            label = "No stable procedure is visible"
            description = "The answers do not reproduce one consistent executable rule."
            action = "Use short guided practice"
        else:
            hypothesis = HYPOTHESIS_MAP[top_id]
            lane = hypothesis.action
            label = hypothesis.short_label
            description = hypothesis.description
            action = hypothesis.action_label

        top_posterior = float(gate["top_posterior"])
        top_rows = result.evidence.get(top_id, tuple())
        held_out_problem = problems[held_out["problem_id"]]
        held_out_payload: dict[str, Any] = {
            "problem": {**asdict(held_out_problem), "expression": held_out_problem.expression},
            "proof_available": gate["state"] == "named_diagnosis" and top_id in HYPOTHESIS_MAP,
        }
        if include_private:
            held_out_payload.update(
                {
                    "actual_answer": held_out["answer"],
                    "ocr_confidence": round(held_out["ocr_confidence"] * 100),
                    "predicted_answer": str(HYPOTHESIS_MAP[top_id].predict(held_out_problem))
                    if top_id in HYPOTHESIS_MAP
                    else None,
                }
            )

        student = {
            "student_id": raw_student["student_id"],
            "display_name": raw_student["display_name"],
            "lane": lane,
            "diagnosis": {
                "hypothesis_id": top_id,
                "label": label,
                "description": description,
                "action": action,
                "state": gate["state"],
                "posterior": round(top_posterior, 4),
                "posterior_percent": round(top_posterior * 100),
                "reproduction": round(result.reproduction.get(top_id, 0) * 100),
                "mean_ocr_confidence": round(result.mean_ocr_confidence * 100),
                "reasons": gate["reasons"],
                "distribution": [
                    {
                        "id": key,
                        "label": HYPOTHESIS_MAP[key].short_label
                        if key in HYPOTHESIS_MAP
                        else "No consistent procedure",
                        "probability": round(value, 4),
                    }
                    for key, value in list(result.posterior.items())[:4]
                ],
            },
            "observations": [
                {
                    "reading_id": f"{raw_student['student_id']}-{item['problem_id']}",
                    "problem_id": item["problem_id"],
                    "expression": problems[item["problem_id"]].expression,
                    "form": problems[item["problem_id"]].form,
                    "observed": item["answer"],
                    "ocr_confidence": round(item["ocr_confidence"] * 100),
                    "predicted": next(
                        (row.predicted for row in top_rows if row.problem_id == item["problem_id"]),
                        "—",
                    ),
                    "matched": next(
                        (row.matched for row in top_rows if row.problem_id == item["problem_id"]),
                        False,
                    ),
                    "reviewed": bool(item.get("reviewed", False)),
                }
                for item in visible
            ],
            "diagnostic_items": _diagnostic_items(result.posterior),
            "held_out": held_out_payload,
        }
        students.append(student)
    return students


def build_class_analysis(
    corrections: dict[str, dict[str, Any]] | None = None,
    *,
    include_private: bool = False,
) -> dict[str, Any]:
    data = _load()
    students = _build_students(corrections or {}, include_private=include_private)
    lanes = []
    for lane_id, meta in ACTION_LANES.items():
        members = [student for student in students if student["lane"] == lane_id]
        lanes.append({"id": lane_id, **meta, "count": len(members), "students": members})

    average_ocr = round(
        sum(student["diagnosis"]["mean_ocr_confidence"] for student in students) / len(students)
    )
    named = sum(student["diagnosis"]["state"] == "named_diagnosis" for student in students)
    return {
        "class_id": "period-3",
        "title": "Period 3 · Fractions exit ticket",
        "skill": data["skill"],
        "dataset_type": data["dataset_type"],
        "summary": {
            "students": len(students),
            "named_diagnoses": named,
            "withheld": len(students) - named,
            "mean_ocr_confidence": average_ocr,
            "minutes_to_action": 2,
        },
        "lanes": lanes,
        "students": students,
        "method_note": (
            "Every named procedure is executed against each observed answer. "
            "Held-out answers are absent from this payload and require a signed reveal token."
        ),
    }


def get_student(student_id: str) -> dict[str, Any] | None:
    return next(
        (student for student in build_class_analysis()["students"] if student["student_id"] == student_id),
        None,
    )


def get_student_private(student_id: str) -> dict[str, Any] | None:
    return next(
        (
            student
            for student in build_class_analysis(include_private=True)["students"]
            if student["student_id"] == student_id
        ),
        None,
    )
