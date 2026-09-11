"""Focused tests for Pass 219 SPI Scalar Projection Registry v7."""
from __future__ import annotations

import json

from hhs_spi_octonion_dimensional_lift_v1 import (
    A2_UNIT,
    ORDERED_RECIPROCAL_OPERAND,
    PHASE_OPPOSITE,
    SOURCE_BASE_PAIR_SYNTAX,
    SOURCE_RECIPROCAL_SYNTAX,
    SYMBOLIC_BASE_PAIR,
)
from hhs_spi_scalar_projection_registry_v6 import build_registry_v6
from hhs_spi_scalar_projection_registry_v7 import (
    DIMENSIONAL_LIFT_PROOF_ID,
    IMAGINARY_ROTATION_PROOF_ID,
    build_registry_v7,
    coverage_manifest_v7,
    validation_report,
)


def test_validation_green():
    report = validation_report()
    assert report["ok"], report
    assert report["changed_predecessor_proof_ids"] == []
    assert report["new_proof_ids"] == sorted(
        [DIMENSIONAL_LIFT_PROOF_ID, IMAGINARY_ROTATION_PROOF_ID]
    )
    assert report["explicit_relational_dimensions"] == 4
    assert report["higher_dimension_rule"] == "RECURSIVE_SAME_ALGEBRA_CLOSURE_REFERENCE"
    assert report["typed_imaginary_rotation_round_trip"] is True
    assert report["a2_unit_projection_compatible"] is True
    assert report["canonical_admission_authority"] is False


def test_v6_registry_is_frozen():
    base = build_registry_v6()
    current = build_registry_v7()
    for proof_id, proof in base.items():
        assert current[proof_id].to_dict() == proof.to_dict()


def test_dimensional_lift_proof_preserves_three_distinct_relations():
    proof = build_registry_v7()[DIMENSIONAL_LIFT_PROOF_ID]
    assert proof.proof_status == "CLOSED"
    assert proof.coverage_state == "PROVEN"
    assert proof.result["source_reciprocal_syntax"] == SOURCE_RECIPROCAL_SYNTAX
    assert proof.result["source_base_pair_syntax"] == SOURCE_BASE_PAIR_SYNTAX
    assert proof.result["phase_opposite"] == PHASE_OPPOSITE
    assert proof.result["ordered_reciprocal_operand"] == ORDERED_RECIPROCAL_OPERAND
    assert proof.result["symbolic_base_pair"] == SYMBOLIC_BASE_PAIR
    assert proof.result["phase_opposite"]["x"] == "z"
    assert proof.result["ordered_reciprocal_operand"]["x"] == "y"
    assert proof.result["symbolic_base_pair"]["x"] == "Ixy"
    assert proof.result["new_basis_elements_introduced"] is False
    assert proof.result["combinatorial_materialization_required"] is False
    assert proof.canonical_admission is False


def test_dimensional_lift_is_a2_projection_compatible_without_native_collapse():
    proof = build_registry_v7()[DIMENSIONAL_LIFT_PROOF_ID]
    assert proof.result["a2_projection"] == A2_UNIT
    assert proof.result["projection_equality_implies_native_identity"] is False
    assert proof.reverse_lift_status == "full"


def test_imaginary_rotation_roundtrip_is_lossless_only_as_typed_carrier():
    proof = build_registry_v7()[IMAGINARY_ROTATION_PROOF_ID]
    assert proof.result["typed_rotation_carrier_lossless"] is True
    assert proof.result["phase_coordinate_alone_claimed_lossless"] is False
    assert proof.result["exact_round_trip"] is True
    assert proof.result["ordered_native_identity_preserved"] is True
    assert proof.result["floating_point_authority"] is False
    assert proof.result["canonical_admission_authority"] is False
    assert proof.reverse_lift_status == "full"


def test_manifest_authority_boundary():
    boundary = coverage_manifest_v7()["authority_boundary"]
    assert boundary == {
        "projection_only": True,
        "candidate_only": True,
        "native_ordered_identity_preserved": True,
        "commutative_reorder_authority": False,
        "vm81_mutation": False,
        "canonical_hash72_hash216_minting": False,
        "canonical_persistence": False,
        "floating_point_authority": False,
    }


def test_manifest_is_deterministic():
    assert coverage_manifest_v7()["manifest_sha256"] == coverage_manifest_v7()["manifest_sha256"]


def main() -> None:
    tests = [value for key, value in sorted(globals().items()) if key.startswith("test_") and callable(value)]
    results = []
    for test in tests:
        try:
            test()
            results.append({"name": test.__name__, "passed": True})
        except Exception as exc:
            results.append({"name": test.__name__, "passed": False, "error": f"{type(exc).__name__}: {exc}"})
    report = {
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_TEST_REPORT_V7",
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
