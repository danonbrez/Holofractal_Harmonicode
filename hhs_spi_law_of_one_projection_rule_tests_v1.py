"""Focused tests for the HARMONICODE Law-of-1 projection invariant."""
from __future__ import annotations

import json

from hhs_spi_law_of_one_projection_rule_v1 import (
    CONDITIONAL_UNIT_BRIDGES,
    LAW_OF_ONE_MEMBERS,
    OPERATOR_SOURCE,
    PROFILE,
    SPILawOfOneError,
    global_law_of_one_manifest,
    member_witness,
    normalization_witness,
    projected_product_witness,
)

EXACT_ONE = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}


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


def test_layer_normalization_preserves_unit():
    witness = normalization_witness("∆", "RATIONAL", "HYDRATION")
    assert witness["source_scalar"] == EXACT_ONE
    assert witness["target_scalar"] == EXACT_ONE
    assert witness["unit_preserved"] is True
    assert witness["native_identity_across_layers"] is False


def test_finite_projected_product_is_unit_without_native_product_evaluation():
    witness = projected_product_witness(
        ("a²", "x⁴", "∆", "P²-pq", "c²-b²"),
        layer_id="TEST-LAYER",
    )
    assert witness["projected_product"] == EXACT_ONE
    assert witness["unit_product"] is True
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


def test_global_manifest_local_and_global_rules():
    manifest = global_law_of_one_manifest()
    assert manifest["member_count"] == 12
    assert manifest["projection_only"] is True
    assert manifest["native_member_collapse"] is False
    assert manifest["native_commutation_or_reassociation"] is False
    assert manifest["canonical_admission_authority"] is False
    assert all(edge["unit_preserved"] for edge in manifest["normalization_edges"])
    assert manifest["conditional_unit_bridges"][0]["native_source_expression"] == "xy"


def test_deterministic_receipts():
    assert member_witness("a²") == member_witness("a²")
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
