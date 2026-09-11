"""Focused tests for the additive HARMONICODE nested-expression AST v2."""
from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from native_projects.hhs_harmonicode_language.hhs_harmonicode_parser_v1 import parse_source as parse_source_v1
from native_projects.hhs_harmonicode_language.hhs_harmonicode_nested_expression_ast_v2 import (
    PARSER_VERSION,
    find_enclosing_nodes,
    parse_source,
)

CANONICAL = REPO_ROOT / "HHS_PASS_169_CANONICAL_ALGEBRA_CORPUS.harmonicode"


def _canonical_source() -> str:
    return CANONICAL.read_text(encoding="utf-8")


def _nodes(ast, kind):
    return [node for node in ast["nested_expression_nodes"] if node["kind"] == kind]


def test_predecessor_identity_preserved():
    source = _canonical_source()
    predecessor = parse_source_v1(source)
    successor = parse_source(source)
    assert successor["predecessor_parser_version"] == predecessor["parser_version"]
    assert successor["predecessor_ast_root_hash72"] == predecessor["ast_root_hash72"]
    assert successor["source_sha256"] == predecessor["source_sha256"]
    assert successor["statement_nodes"] == predecessor["nodes"]


def test_power_chain_preserves_order_without_associativity():
    ast = parse_source("c^b^4")
    chains = _nodes(ast, "PowerChain")
    assert len(chains) == 1
    chain = chains[0]
    assert chain["source_text"] == "c^b^4"
    assert [item["source_text"] for item in chain["ordered_operands"]] == ["c", "b", "4"]
    assert chain["associativity"] == "UNRESOLVED_SOURCE_CHAIN"
    assert chain["algebraic_associativity_selected"] is False
    assert chain["scalar_value"] is None
    assert chain["canonical_admission"] is False


def test_parenthesized_power_is_not_rewritten_as_chain():
    chained = parse_source("c^b^4")
    parenthesized = parse_source("c^(b^4)")
    assert _nodes(chained, "PowerChain")
    assert not _nodes(parenthesized, "PowerChain")
    assert chained["ast_root_hash72"] != parenthesized["ast_root_hash72"]


def test_radical_exponent_surface_preserves_complete_source():
    source = "√(pq+u⁷²)^x²"
    ast = parse_source(source)
    radicals = _nodes(ast, "RadicalPowerSurface")
    assert len(radicals) == 1
    radical = radicals[0]
    assert radical["source_text"] == source
    assert [item["source_text"] for item in radical["ordered_operands"]] == ["(pq+u⁷²)", "x²"]
    assert radical["scalar_value"] is None
    superscripts = {node["source_text"] for node in _nodes(ast, "SuperscriptPower")}
    assert {"u⁷²", "x²"} <= superscripts


def test_canonical_source_exposes_both_repair_surfaces():
    source = _canonical_source()
    ast = parse_source(source)
    chain = [node for node in _nodes(ast, "PowerChain") if node["source_text"] == "c^b^4"]
    radical = [
        node
        for node in _nodes(ast, "RadicalPowerSurface")
        if node["source_text"] == "√(pq+u⁷²)^x²"
    ]
    assert len(chain) == 1
    assert len(radical) == 1


def test_partial_scanner_spans_bind_to_enclosing_nodes():
    source = _canonical_source()
    ast = parse_source(source)
    c_start = source.index("c^b")
    c_matches = find_enclosing_nodes(ast, c_start, c_start + len("c^b"), kinds=("PowerChain",))
    assert c_matches and c_matches[0]["source_text"] == "c^b^4"

    p_start = source.index("(pq+u⁷²)^x")
    p_matches = find_enclosing_nodes(
        ast,
        p_start,
        p_start + len("(pq+u⁷²)^x"),
        kinds=("RadicalPowerSurface",),
    )
    assert p_matches and p_matches[0]["source_text"] == "√(pq+u⁷²)^x²"


def test_successor_remains_nonexecuting_and_nonauthoritative():
    ast = parse_source(_canonical_source())
    assert ast["parser_executes_program_effects"] is False
    assert ast["canonical_admission_authority"] is False
    assert ast["ordered_products_not_commuted"] is True
    assert ast["capabilities"]["power_chain_associativity_selected"] is False
    assert ast["capabilities"]["general_nested_expression_ast_complete"] is False


def test_deterministic():
    source = _canonical_source()
    assert parse_source(source) == parse_source(source)


TESTS = [
    test_predecessor_identity_preserved,
    test_power_chain_preserves_order_without_associativity,
    test_parenthesized_power_is_not_rewritten_as_chain,
    test_radical_exponent_surface_preserves_complete_source,
    test_canonical_source_exposes_both_repair_surfaces,
    test_partial_scanner_spans_bind_to_enclosing_nodes,
    test_successor_remains_nonexecuting_and_nonauthoritative,
    test_deterministic,
]


def main() -> int:
    results = []
    for test in TESTS:
        try:
            test()
            results.append({"name": test.__name__, "passed": True})
        except Exception as exc:  # noqa: BLE001
            results.append({"name": test.__name__, "passed": False, "error": repr(exc)})
    report = {
        "suite": "HHS_HARMONICODE_NESTED_EXPRESSION_AST_V2_TESTS",
        "parser_version": PARSER_VERSION,
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
