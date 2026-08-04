"""Novelty signature and complexity analysis (Phase 6)."""
from faultline_core import HYPOTHESIS_MAP, complexity, known_signatures, matches_known, output_signature
from faultline_core.novelty import PROBE_BANK

ADD_ACROSS = {
    "op": "fraction",
    "args": [
        {"op": "add", "args": [{"var": "n1"}, {"var": "n2"}]},
        {"op": "add", "args": [{"var": "d1"}, {"var": "d2"}]},
    ],
}
NOVEL = {
    "op": "fraction",
    "args": [
        {"op": "add", "args": [{"var": "n1"}, {"var": "n2"}]},
        {"op": "mul", "args": [{"var": "d1"}, {"var": "d2"}]},
    ],
}


def test_known_add_across_signature_matches_library() -> None:
    signature = output_signature(ADD_ACROSS, PROBE_BANK)
    assert matches_known(signature) == "add_across"


def test_novel_rule_matches_nothing_known() -> None:
    signature = output_signature(NOVEL, PROBE_BANK)
    assert matches_known(signature) is None


def test_signature_is_deterministic() -> None:
    assert output_signature(NOVEL) == output_signature(NOVEL)


def test_known_signatures_cover_every_hypothesis() -> None:
    signatures = known_signatures()
    assert set(signatures) == set(HYPOTHESIS_MAP)
    # Signatures are exact-fraction strings.
    assert all("/" in value or value.lstrip("-").isdigit() for row in signatures.values() for value in row)


def test_complexity_counts_operations_and_depth() -> None:
    ops, depth = complexity(ADD_ACROSS)
    assert ops == 3  # fraction + two adds
    assert depth >= 2


def test_nonexecutable_expression_signature_is_none() -> None:
    # Divide-by-zero style expression that fails on a probe returns no signature.
    zero_denominator = {"op": "fraction", "args": [{"var": "n1"}, {"op": "sub", "args": [{"var": "d1"}, {"var": "d1"}]}]}
    assert output_signature(zero_denominator) is None
