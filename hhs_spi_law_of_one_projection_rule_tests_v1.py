"""Focused tests for the HARMONICODE Law-of-1 projection invariant."""
from __future__ import annotations

import json

from hhs_spi_law_of_one_projection_rule_v1 import (
    CONDITIONAL_UNIT_BRIDGES,
    LAW_OF_ONE_MEMBERS,
    LOCAL_GLOBAL_SCALE_BRIDGE,
    LOCAL_SCALE_SYMBOL,
    OPERATOR_SOURCE,
    PROFILE,
    SPILawOfOneError,
    UNIVERSAL_DENOMINATOR_SYMBOL,
    global_law_of_one_manifest,
    local_scale_witness,
    member_witness,
    normalization_witness,
    projected_product_witness,
    scale_bridge_witness,
    universal_denominator_witness,
)

EXACT_ONE = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
EXACT_FIVE = {"type": "EXACT_RATIONAL", "numerator": 5, "denominator": 1}
EXACT_ZERO = {"type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1}


def _raises(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def test_operator_source_preserved_verbatim():
    assert OPERATOR_SOURCE == "1=a²,x⁴,y⁴,z⁴,w⁴,∆,P²-pq,t³-t,m²-m,e^x²O,c²-b²,b²/2u⁷²"


def test_all_primary_members_project_to_exact_one():
    assert len(LAW_OF_ONE_MEMBERS) == 12
    for member in LAW_OF_ONE_MEMBERS:
        witness = member_witness(member)
        assert witness["profile"] == PROFILE
        assert witness["native_source_expression"] == member
        assert witness["projection_value"] == EXACT_ONE
        assert witness["projection_only"] is True
        assert witness["native_identity_with_other_members"] is False
        assert witness["canonical_admission_authority"] is False


def test_delta_is_universal_denominator_member():
    assert UNIVERSAL_DENOMINATOR_SYMBOL == "∆"
    delta = member_witness("∆")
    assert delta["universal_denominator_member"] is True
    assert delta["local_scale_member"] is False
    assert delta["projection_value"] == EXACT_ONE


def test_a2_is_local_scale_and_bridges_to_delta():
    assert LOCAL_SCALE_SYMBOL == "a²"
    assert LOCAL_GLOBAL_SCALE_BRIDGE == "a²=∆=1"
    a2 = member_witness("a²")
    assert a2["local_scale_member"] is True
    assert a2["universal_denominator_member"] is False
    bridge = scale_bridge_witness("LOCAL-TEST")
    assert bridge["relation"] == "a²=∆=1"
    assert bridge["local_scale"] == EXACT_ONE
    assert bridge["universal_denominator"] == EXACT_ONE
    assert bridge["residual"] == EXACT_ZERO
    assert bridge["projection_only"] is True
    assert bridge["native_a2_delta_identity_authorized"] is False


def test_universal_delta_denominator_is_value_preserving():
    witness = universal_denominator_witness(5, layer_id="RATIONAL")
    assert witness["denominator_symbol"] == "∆"
    assert witness["denominator_scalar"] == EXACT_ONE
    assert witness["input_scalar"] == EXACT_FIVE
    assert witness["normalized_scalar"] == EXACT_FIVE
    assert witness["residual"] == EXACT_ZERO
    assert witness["value_preserved"] is True
    assert witness["native_division_by_delta_executed"] is False


def test_local_a2_scale_is_value_preserving_and_bridged_to_delta():
    witness = local_scale_witness(5, layer_id="MATRIX-TENSOR")
    assert witness["local_scale_symbol"] == "a²"
    assert witness["local_scale_scalar"] == EXACT_ONE
    assert witness["normalized_scalar"] == EXACT_FIVE
    assert witness["bridge_relation"] == "a²=∆=1"
    assert witness["residual"] == EXACT_ZERO
    assert witness["value_preserved"] is True
    assert witness["native_division_by_a2_executed"] is False


def test_float_normalization_fails_closed():
    _raises(SPILawOfOneError, universal_denominator_witness, 1.0, layer_id="BAD")
    _raises(SPILawOfOneError, local_scale_witness, 1.0, layer_id="BAD")


def test_phase_quartic_members_are_projection_axioms_not_native_collapse():
    for member in ("x⁴", "y⁴", "z⁴", "w⁴"):
        witness = member_witness(member)
        assert witness["evidence_kind"] == "OPERATOR_SUPPLIED_PHASE_QUARTIC_PROJECTION_AXIOM"
        assert witness["native_identity_with_other_members"] is False
        assert witness["native_commutation_authorized"] is False


def test_euler_and_b2_over_2u72_sources_are_not_reparsed():
    euler = member_witness("e^x²O")
    boundary = member_witness("b²/2u⁷²")
    assert euler["native_source_expression"] == "e^x²O"
    assert boundary["native_source_expression"] == "b²/2u⁷²"
    assert euler["evidence_kind"] == "OPERATOR_SUPPLIED_SOURCE_BOUND_PROJECTION_AXIOM"
    assert boundary["evidence_kind"] == "OPERATOR_SUPPLIED_SOURCE_BOUND_PROJECTION_AXIOM"


def test_xy_is_conditional_bridge_not_primary_member():
    assert "xy" not in LAW_OF_ONE_MEMBERS
    assert CONDITIONAL_UNIT_BRIDGES == ("xy",)
    _raises(SPILawOfOneError, member_witness, "xy")
    witness = member_witness("xy", conditional_bridge=True)
    assert witness["projection_value"] == EXACT_ONE
    assert witness["conditional_bridge"] is True
    assert witness["native_identity_with_other_members"] is False


def test_layer_normalization_preserves_unit_and_scale_hierarchy():
    witness = normalization_witness("∆", "RATIONAL", "HYDRATION")
    assert witness["source_scalar"] == EXACT_ONE
    assert witness["target_scalar"] == EXACT_ONE
    assert witness["universal_denominator_symbol"] == "∆"
    assert witness["local_scale_symbol"] == "a²"
    assert witness["unit_preserved"] is True
    assert witness["native_identity_across_layers"] is False


def test_finite_projected_product_is_unit_without_native_product_evaluation():
    witness = projected_product_witness(
        ("a²", "x⁴", "∆", "P²-pq", "c²-b²"),
        layer_id="TEST-LAYER",
    )
    assert witness["projected_product"] == EXACT_ONE
    assert witness["unit_product"] is True
    assert witness["universal_denominator"] == EXACT_ONE
    assert witness["local_scale"] == EXACT_ONE
    assert witness["native_product_evaluated"] is False
    assert witness["native_reordering_authorized"] is False


def test_conditional_xy_product_requires_explicit_bridge_permission():
    _raises(
        SPILawOfOneError,
        projected_product_witness,
        ("a²", "xy"),
        layer_id="TEST-LAYER",
    )
    witness = projected_product_witness(
        ("a²", "xy"),
        layer_id="SYMMETRIC-UNIT-LAYER",
        allow_conditional_bridges=True,
    )
    assert witness["unit_product"] is True
    assert witness["projected_product"] == EXACT_ONE


def test_global_manifest_declares_delta_and_a2_hierarchy():
    manifest = global_law_of_one_manifest()
    assert manifest["member_count"] == 12
    assert manifest["universal_denominator"]["symbol"] == "∆"
    assert manifest["universal_denominator"]["scalar"] == EXACT_ONE
    assert manifest["universal_denominator"]["system_wide_for_scalar_normalization"] is True
    assert manifest["local_scale"]["symbol"] == "a²"
    assert manifest["local_scale"]["bridge"] == "a²=∆=1"
    assert manifest["local_scale"]["scalar"] == EXACT_ONE
    assert manifest["projection_only"] is True
    assert manifest["native_a2_delta_identity"] is False
    assert manifest["native_member_collapse"] is False
    assert manifest["native_commutation_or_reassociation"] is False
    assert manifest["canonical_admission_authority"] is False
    assert all(edge["unit_preserved"] for edge in manifest["normalization_edges"])
    assert all(bridge["relation"] == "a²=∆=1" for bridge in manifest["scale_bridges"])
    assert manifest["conditional_unit_bridges"][0]["native_source_expression"] == "xy"


def test_deterministic_receipts():
    assert member_witness("a²") == member_witness("a²")
    assert scale_bridge_witness("A") == scale_bridge_witness("A")
    assert universal_denominator_witness(5, layer_id="A") == universal_denominator_witness(5, layer_id="A")
    assert local_scale_witness(5, layer_id="A") == local_scale_witness(5, layer_id="A")
    assert normalization_witness("∆", "A", "B") == normalization_witness("∆", "A", "B")
    assert global_law_of_one_manifest() == global_law_of_one_manifest()


def main() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    results = []
    for test in tests:
        try:
            test()
            results.append({"name": test.__name__, "passed": True})
        except Exception as exc:
            results.append({"name": test.__name__, "passed": False, "error": f"{type(exc).__name__}: {exc}"})
    report = {
        "schema": "HHS_SPI_LAW_OF_ONE_PROJECTION_TEST_REPORT_V1",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
