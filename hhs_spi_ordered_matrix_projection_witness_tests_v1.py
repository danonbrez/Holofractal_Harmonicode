"""Focused tests for the Pass 219 SPI O2 ordered-matrix projection witness."""
from __future__ import annotations

import json

from hhs_spi_ordered_matrix_projection_witness_v1 import (
    A2_MATRIX_DEFINITION_EDGE,
    DENOMINATOR_SHA256,
    DENOMINATOR_SOURCE,
    NATIVE_CENTER_CLOSURE,
    O2_EQUALITY_SHA256,
    PROJECTION_SHA256,
    ordered_matrix_projection_witness,
    validation_report,
)


def test_validation_green():
    report = validation_report()
    assert report["ok"], report
    assert report["projection_basis"] == "REGISTERED_SCALAR_DEFINITION_EDGE"
    assert report["scalar_value_complete_for_o2_profile"] is True
    assert report["generic_ncalc_family_complete"] is False
    assert report["canonical_admission_authority"] is False


def test_exact_source_identities():
    witness = ordered_matrix_projection_witness()
    source = witness["source_identity"]
    assert source["denominator_sha256"] == DENOMINATOR_SHA256
    assert source["projection_sha256"] == PROJECTION_SHA256
    assert source["equality_sha256"] == O2_EQUALITY_SHA256
    assert source["a2_matrix_definition_edge"] == A2_MATRIX_DEFINITION_EDGE
    assert source["combined_denominator_occurrence_count"] == 2
    assert source["phase12_tensor_source_preserved"] is True
    assert source["native_center_closure_source_preserved"] is True


def test_harmonicode_defined_scalar_rule_projects_matrix_branch_to_a2_value():
    witness = ordered_matrix_projection_witness()
    defined = witness["defined_scalar_projection"]
    result = witness["result"]
    exact_one = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
    exact_zero = {"type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1}
    assert defined["scalar_symbol"] == "a²"
    assert defined["scalar_proof_id"] == "SPI-PROJ-0001"
    assert defined["definition_kind"] == "EXACT_SYMBOLIC_MATRIX_POWER"
    assert defined["result"] == exact_one
    assert defined["residual"] == exact_zero
    assert defined["matrix_or_tensor_host_evaluated"] is False
    assert defined["native_substitution_authorized"] is False
    assert result["matrix_branch_projection"] == exact_one
    assert result["a_squared_projection"] == exact_one
    assert result["projection_basis"] == "REGISTERED_SCALAR_DEFINITION_EDGE"


def test_ordered_topology_remains_native_evidence():
    topology = ordered_matrix_projection_witness()["ordered_matrix_topology"]
    assert topology["outer_cell_count"] == 8
    assert topology["outer_phase_alignment_exact"] is True
    assert topology["all_nine_topology_cells_witnessed"] is True
    assert [cell["ordered_role"] for cell in topology["outer_cells"]] == [
        "x", "w", "yx", "zw", "y", "z", "xy", "wz"
    ]
    assert [cell["difference_mod72"] for cell in topology["outer_cells"]] == [0] * 8
    assert topology["ordered_xy_yx_distinct"] is True
    assert topology["ordered_zw_wz_distinct"] is True


def test_center_uses_native_closure_not_ordinary_division():
    center = ordered_matrix_projection_witness()["ordered_matrix_topology"]["center"]
    assert center["native_closure"] == NATIVE_CENTER_CLOSURE
    assert center["ordinary_zero_division_executed"] is False
    assert center["center_scalarized_from_outer_phase_cancellation"] is False
    assert center["native_constraint_intersection_required"] is True


def test_matrix_power_stays_exact_symbolic_node():
    witness = ordered_matrix_projection_witness()
    fourth = witness["fourth_power"]
    assert fourth["ncalc_matrix_power_source_exponent"] == 4
    assert fourth["outer_b4_projection"] == {
        "type": "EXACT_RATIONAL", "numerator": 4, "denominator": 1
    }
    assert fourth["node_type"] == "EXACT_SYMBOLIC_MATRIX_POWER"
    assert fourth["ncalc_matrix_power_host_evaluated"] is False
    assert fourth["algebraic_matrix_power_replacement_authorized"] is False


def test_squared_radical_branch_is_independent_consistency_not_projection_source():
    witness = ordered_matrix_projection_witness()
    root = witness["root_witness"]
    assert root["profile"] == "SPI-SURD-SQUARED-Q-v1"
    assert root["required_for_matrix_to_scalar_projection"] is False
    assert root["a_squared_projection"] == {
        "type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1
    }
    assert root["residual"] == {
        "type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1
    }


def test_projection_does_not_promote_native_authority_or_generic_matrix_collapse():
    witness = ordered_matrix_projection_witness()
    assert witness["projection_only"] is True
    assert witness["canonical_admission_authority"] is False
    assert witness["vm81_mutation_authority"] is False
    assert witness["canonical_hash72_authority"] is False
    assert witness["canonical_hash216_authority"] is False
    assert witness["canonical_persistence_authority"] is False
    assert witness["floating_point_authority"] is False
    assert witness["ncalc_matrix_power_generic_family_complete"] is False
    assert witness["equality_chain"]["native_node_collapse_authorized"] is False
    assert witness["exact_inverse_or_lift"]["reverse_native_reconstruction_authorized"] is False


def test_witness_deterministic():
    a = ordered_matrix_projection_witness()
    b = ordered_matrix_projection_witness()
    assert a == b
    assert a["witness_sha256"] == b["witness_sha256"]


def test_frozen_denominator_source_retains_order():
    assert "(y*x)" in DENOMINATOR_SOURCE
    assert "(x*y)" in DENOMINATOR_SOURCE
    assert "(w*z)" in DENOMINATOR_SOURCE
    assert "(z*w)" in DENOMINATOR_SOURCE
    assert DENOMINATOR_SOURCE.index("(y*x)") < DENOMINATOR_SOURCE.index("(x*y)")


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
        "schema": "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_TEST_REPORT_V1",
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
