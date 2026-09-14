"""Focused tests for reciprocal/base-pair octonion dimensional lift v1."""
from __future__ import annotations

import copy
import json

from hhs_spi_octonion_dimensional_lift_v1 import (
    A2_UNIT,
    ORDERED_RECIPROCAL_OPERAND,
    PHASE_OPPOSITE,
    SOURCE_BASE_PAIR_SYNTAX,
    SOURCE_RECIPROCAL_SYNTAX,
    SYMBOLIC_BASE_PAIR,
    SPIOctonionDimensionalLiftError,
    a2_projection_compatibility,
    collapse_to_imaginary_rotation,
    dimensional_lift,
    dimensional_lift_witness,
    four_coordinate_closure,
    ordered_reciprocal_operand,
    phase_opposite,
    restore_from_imaginary_rotation,
    symbolic_base_pair,
)


def test_exact_source_syntax_is_preserved_verbatim():
    witness = dimensional_lift_witness("x", phase72=18, dimension=8)
    assert witness["source_reciprocal_syntax"] == "x=1/y y=-x"
    assert witness["source_base_pair_syntax"] == "(x,y,z,w)²==(Ixy, I-yx, Izw, I-wz)²"
    assert SOURCE_RECIPROCAL_SYNTAX == "x=1/y y=-x"
    assert SOURCE_BASE_PAIR_SYNTAX == "(x,y,z,w)²==(Ixy, I-yx, Izw, I-wz)²"


def test_rml2_geometric_phase_opposites_are_involutive():
    assert PHASE_OPPOSITE == {"x": "z", "z": "x", "w": "y", "y": "w"}
    for state in ("x", "y", "z", "w"):
        assert phase_opposite(phase_opposite(state)) == state


def test_rml4_ordered_reciprocal_operands_are_separate_involution():
    assert ORDERED_RECIPROCAL_OPERAND == {"x": "y", "y": "x", "z": "w", "w": "z"}
    for state in ("x", "y", "z", "w"):
        assert ordered_reciprocal_operand(ordered_reciprocal_operand(state)) == state
        assert phase_opposite(state) != ordered_reciprocal_operand(state)


def test_symbolic_base_pair_mapping_matches_constructor_coordinatewise():
    assert SYMBOLIC_BASE_PAIR == {
        "x": "Ixy",
        "y": "I-yx",
        "z": "Izw",
        "w": "I-wz",
    }
    assert [symbolic_base_pair(v) for v in ("x", "y", "z", "w")] == [
        "Ixy",
        "I-yx",
        "Izw",
        "I-wz",
    ]


def test_first_four_dimensions_are_materialized_from_same_algebra():
    closure = four_coordinate_closure("x")
    assert [row["dimension"] for row in closure] == [1, 2, 3, 4]
    assert [row["value"] for row in closure] == ["x", "z", "Ixy", "Izw"]
    lift = dimensional_lift("x", 4)
    assert lift["explicit_relational_dimensions"] == 4
    assert lift["recursive_reference_dimensions"] == 0
    assert lift["same_octonion_algebra_all_dimensions"] is True
    assert lift["new_basis_elements_introduced"] is False


def test_higher_dimensions_use_recursive_closure_references_not_new_basis():
    lift = dimensional_lift("y", 9)
    assert lift["requested_dimension"] == 9
    assert lift["explicit_relational_dimensions"] == 4
    assert lift["recursive_reference_dimensions"] == 5
    recursive = lift["coordinates"][4:]
    assert [item["dimension"] for item in recursive] == [5, 6, 7, 8, 9]
    assert all(item["role"] == "RECURSIVE_SAME_ALGEBRA_CLOSURE_REFERENCE" for item in recursive)
    assert all(item["materializes_new_octonion_basis"] is False for item in recursive)
    assert len({item["closure_root_sha256"] for item in recursive}) == 1
    assert lift["combinatorial_materialization_required"] is False


def test_typed_imaginary_rotation_carrier_round_trips_without_loss():
    for state, phase in (("x", 0), ("y", 18), ("z", 36), ("w", 71)):
        carrier = collapse_to_imaginary_rotation(state, phase)
        restored = restore_from_imaginary_rotation(carrier)
        assert restored["source_channel"] == state
        assert restored["phase72"] == phase
        assert restored["exact_round_trip"] is True
        assert carrier["phase_coordinate_alone_claimed_lossless"] is False
        assert carrier["typed_rotation_carrier_lossless"] is True
        assert carrier["ordered_native_identity_preserved"] is True


def test_typed_rotation_carrier_tampering_fails_closed():
    carrier = collapse_to_imaginary_rotation("x", 18)
    tampered = copy.deepcopy(carrier)
    tampered["symbolic_base_pair"] = "I-yx"
    try:
        restore_from_imaginary_rotation(tampered)
    except SPIOctonionDimensionalLiftError as exc:
        assert "RECEIPT_MISMATCH" in str(exc)
    else:
        raise AssertionError("tampered carrier unexpectedly restored")


def test_a2_unit_projection_is_compatible_without_native_identity_collapse():
    for state in ("x", "y", "z", "w"):
        witness = a2_projection_compatibility(state)
        assert witness["a2_projection"] == A2_UNIT
        assert witness["projection_premise_id"] == "SPI-LAW1-A2-LOCAL-SCALE"
        assert witness["projection_equality_implies_native_identity"] is False
        assert witness["commutative_reorder_authorized"] is False
        assert witness["a2_projection_contradiction"] is False


def test_full_witness_preserves_authority_boundary():
    witness = dimensional_lift_witness("x", phase72=18, dimension=12)
    assert all(witness["invariants"].values())
    assert witness["authority"] == {
        "projection_only": True,
        "candidate_only": True,
        "vm81_mutation": False,
        "canonical_hash72_minting": False,
        "canonical_hash216_minting": False,
        "canonical_persistence": False,
        "floating_point_authority": False,
    }


def test_invalid_dimension_and_float_phase_fail_closed():
    try:
        dimensional_lift("x", 0)
    except SPIOctonionDimensionalLiftError as exc:
        assert "DIMENSION_MUST_BE_POSITIVE" in str(exc)
    else:
        raise AssertionError("dimension zero unexpectedly accepted")

    try:
        collapse_to_imaginary_rotation("x", 18.0)
    except SPIOctonionDimensionalLiftError as exc:
        assert "EXACT_INTEGER_REQUIRED" in str(exc)
    else:
        raise AssertionError("float phase unexpectedly accepted")


def test_witness_is_deterministic():
    assert dimensional_lift_witness("w", phase72=54, dimension=10) == dimensional_lift_witness(
        "w", phase72=54, dimension=10
    )


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
        "schema": "HHS_SPI_OCTONION_DIMENSIONAL_LIFT_TEST_REPORT_V1",
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
