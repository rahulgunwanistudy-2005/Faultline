import json
from pathlib import Path

from faultline_core import FractionProblem, HYPOTHESES

ROOT = Path(__file__).resolve().parents[3]


def test_reference_malrule_catalog_matches_executable_library() -> None:
    catalog = json.loads((ROOT / "data" / "malrules.json").read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in catalog}
    assert set(by_id) == {hypothesis.id for hypothesis in HYPOTHESES}
    for hypothesis in HYPOTHESES:
        row = by_id[hypothesis.id]
        assert row["label"] == hypothesis.short_label
        assert row["action"] == hypothesis.action_label
        assert row["provenance"] == hypothesis.provenance


def test_item_bank_is_unique_and_domain_valid() -> None:
    rows = json.loads((ROOT / "data" / "item_bank.json").read_text(encoding="utf-8"))
    assert rows
    assert len({row["id"] for row in rows}) == len(rows)
    problems = [FractionProblem(**row) for row in rows]
    assert any(problem.form == "word" for problem in problems)
    assert any(problem.form == "visual" for problem in problems)


def test_demo_fixture_has_one_held_out_item_per_student() -> None:
    fixture = json.loads((ROOT / "data" / "demo_class.json").read_text(encoding="utf-8"))
    hypothesis_ids = {hypothesis.id for hypothesis in HYPOTHESES}
    student_ids = [student["student_id"] for student in fixture["students"]]
    assert len(student_ids) == len(set(student_ids))
    for student in fixture["students"]:
        held_out = [item for item in student["observations"] if item.get("held_out")]
        visible = [item for item in student["observations"] if not item.get("held_out")]
        assert len(held_out) == 1
        assert len(visible) >= 5
        assert student["assigned_procedure"] in hypothesis_ids | {"no_consistent_procedure"}
