"""Focused tests for Pass 219 SPI Scalar Projection Registry v3."""
from __future__ import annotations

import json
from fractions import Fraction

from hhs_spi_law_of_one_projection_rule_v1 import LAW_OF_ONE_MEMBERS, OPERATOR_SOURCE
from hhs_spi_scalar_projection_registry_v2 import build_registry_v2
from hhs_spi_scalar_projection_registry_v3 import (
    GLOBAL_PROOF_ID,
    LAW_MEMBER_PROOF_IDS,
    XY_BRIDGE_PROOF_ID,
    build_registry_v3,
    coverage_manifest_v3,
    validation_report,
)


def test_validation_green():
    report = validation_report()
    assert report["ok"], report
    assert report["law_of_one_member_count"] == 12
    assert report["law_of_one_operator_source"] == OPERATOR_SOURCE
    assert report["xy_conditional_bridge"] is True
    assert report["changed_predecessor_proof_ids"] == []
    assert report["canonical_admission_authority"] is False


def test_predecessor_registry_is_frozen():
    base = build_registry_v2()
    current = build_registry_v3()
    assert set(base).issubset(current)
    for proof_id, proof in base.items():
        assert current[proof_id].to_dict() == proof.to_dict()


def test_all_primary_law_members_are_closed_unit_proofs():
    registry = build_registry_v3()
    assert tuple(LAW_MEMBER_PROOF_IDS) == LAW_OF_ONE_MEMBERS
    for member, proof_id in LAW_MEMBER_PROOF_IDS.items():
        proof = registry[proof_id]
        assert proof.proof_status == "CLOSED"
        assert proof.coverage_state == "PROVEN"
        assert proof.implementation_status == "IMPLEMENTED"
        assert proof.receipt_status == "VERIFIED"
        assert proof.result["projection"] == f"pi({member})"
        assert proof.result["value"] == Fraction(1)
        assert proof.canonical_admission is False
        assert proof.reverse_lift_status == "none"


def test_phase_quartics_are_explicit_projection_axioms():
    registry = build_registry_v3()
    for member in ("x⁴", "y⁴", "z⁴", "w⁴"):
        proof = registry[LAW_MEMBER_PROOF_IDS[member]]
        assert proof.result["evidence_kind"] == "OPERATOR_SUPPLIED_PHASE_QUARTIC_PROJECTION_AXIOM"
        assert any("without native phase collapse" in step for step in proof.derivation)


def test_source_bound_ambiguous_surfaces_are_not_reparsed():
    registry = build_registry_v3()
    exp_proof = registry[LAW_MEMBER_PROOF_IDS["e^x²O"]]
    b_proof = registry[LAW_MEMBER_PROOF_IDS["b²/2u⁷²"]]
    assert exp_proof.source_expression == "e^x²O"
    assert b_proof.source_expression == "b²/2u⁷²"
    assert any("without conventional reparsing" in step for step in exp_proof.derivation)
    assert any("without inserting precedence" in step for step in b_proof.derivation)


def test_xy_bridge_is_conditional_projection_only():
    registry = build_registry_v3()
    proof = registry[XY_BRIDGE_PROOF_ID]
    assert proof.result["value"] == Fraction(1)
    assert proof.result["conditional"] is True
    assert proof.authority == "PROJECTION_ONLY"
    assert proof.canonical_admission is False
    assert any("xy/yx" in item for item in proof.lost_information)


def test_global_law_is_local_and_cross_layer_unit_preserving():
    registry = build_registry_v3()
    proof = registry[GLOBAL_PROOF_ID]
    assert proof.result["unit"] == Fraction(1)
    assert proof.result["local_rule"] == "pi_L(E)=1_L"
    assert proof.result["global_rule"] == "N[L_i->L_j](1_Li)=1_Lj"
    assert proof.result["finite_projected_product"] == 1
    assert proof.canonical_admission is False


def test_manifest_authority_boundary():
    manifest = coverage_manifest_v3()
    boundary = manifest["authority_boundary"]
    assert boundary["projection_only"] is True
    assert boundary["native_member_identity_collapse"] is False
    assert boundary["xy_yx_commutation"] is False
    assert boundary["normalization_preserves_unit"] is True
    assert boundary["vm81_mutation"] is False
    assert boundary["canonical_hash72_hash216_minting"] is False
    assert boundary["canonical_persistence"] is False
    assert boundary["floating_point_authority"] is False


def test_deterministic_manifest():
    assert coverage_manifest_v3()["manifest_sha256"] == coverage_manifest_v3()["manifest_sha256"]


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
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_TEST_REPORT_V3",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
