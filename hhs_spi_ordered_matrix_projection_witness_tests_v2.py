"""Tests for O2 ordered-matrix projection witness v2."""
from __future__ import annotations

import json

from hhs_spi_ordered_matrix_projection_witness_v2 import (
    DERIVED_ALL_ONES_SURFACE,
    PASS129_XY_UNIT_CLAIM,
    ordered_matrix_projection_witness_v2,
    validation_report,
)


def test_validation_green():
    report = validation_report()
    assert report["ok"], report
    assert report["projection_relation"] == "a²=xy=1"
    assert report["canonical_admission_authority"] is False


def test_derived_surface_is_all_ones_and_symmetric():
    witness = ordered_matrix_projection_witness_v2()
    symmetric = witness["symmetric_unit_product_surface"]
    assert symmetric["derived_unit_surface"] == DERIVED_ALL_ONES_SURFACE
    receipt = symmetric["unit_layer_receipt"]
    assert receipt["symmetry_complete"] is True
    assert receipt["all_orbit_products_unit"] is True
    assert receipt["covered_component_count"] == 9
    assert receipt["symmetry_orbit_count"] == 6


def test_pass129_xy_unit_precedent_is_bound():
    witness = ordered_matrix_projection_witness_v2()
    precedent = witness["symmetric_unit_product_surface"]["pass129_xy_unit_precedent"]
    assert precedent["claim"] == PASS129_XY_UNIT_CLAIM
    assert precedent["xy_projection_unit"] == 1
    assert precedent["native_xy_yx_identity_claimed"] is False


def test_new_layer_is_a2_xy_unit_projection_only():
    witness = ordered_matrix_projection_witness_v2()
    exact_one = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
    assert witness["result"]["a²"] == exact_one
    assert witness["result"]["xy"] == exact_one
    assert witness["result"]["relation"] == "a²=xy=1"
    assert witness["result"]["relation_kind"] == "SCALAR_PROJECTION_LAYER_ONLY"
    assert witness["native_a2_xy_identity_authorized"] is False
    assert witness["xy_yx_commutation_authorized"] is False


def test_generic_matrix_tensor_scalarization_stays_fail_closed():
    witness = ordered_matrix_projection_witness_v2()
    assert witness["generic_matrix_tensor_scalarization_authorized"] is False
    assert witness["symmetry_plus_all_unit_products_required"] is True


def test_authority_boundary_unchanged():
    witness = ordered_matrix_projection_witness_v2()
    for key in (
        "canonical_admission_authority",
        "vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "canonical_persistence_authority",
        "floating_point_authority",
    ):
        assert witness[key] is False


def test_deterministic():
    assert ordered_matrix_projection_witness_v2() == ordered_matrix_projection_witness_v2()


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
        "schema": "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_TEST_REPORT_V2",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
