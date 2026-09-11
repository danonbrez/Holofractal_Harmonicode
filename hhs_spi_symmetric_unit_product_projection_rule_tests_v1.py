"""Tests for the HARMONICODE symmetric unit-product projection rule."""
from __future__ import annotations

import json

from hhs_spi_symmetric_unit_product_projection_rule_v1 import (
    PROFILE,
    SPISymmetricUnitProductError,
    symmetric_unit_product_projection,
)


def _raises(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def _all_ones_3x3_receipt():
    # Standard transpose symmetry of the projected all-ones 3x3 magnitude layer.
    orbits = (
        {"orbit_id": "diag-00", "members": ("00",), "product": 1, "involution_closed": True},
        {"orbit_id": "diag-11", "members": ("11",), "product": 1, "involution_closed": True},
        {"orbit_id": "diag-22", "members": ("22",), "product": 1, "involution_closed": True},
        {"orbit_id": "transpose-01", "members": ("01", "10"), "product": 1, "involution_closed": True},
        {"orbit_id": "transpose-02", "members": ("02", "20"), "product": 1, "involution_closed": True},
        {"orbit_id": "transpose-12", "members": ("12", "21"), "product": 1, "involution_closed": True},
    )
    return symmetric_unit_product_projection(
        surface_id="TEST:ALL_ONES_3X3",
        surface_source="((1,1,1),(1,1,1),(1,1,1))",
        symmetry_orbits=orbits,
        total_component_count=9,
    )


def test_symmetric_all_ones_surface_projects_new_unit_layer():
    receipt = _all_ones_3x3_receipt()
    assert receipt["profile"] == PROFILE
    assert receipt["symmetry_complete"] is True
    assert receipt["all_orbit_products_unit"] is True
    assert receipt["covered_component_count"] == 9
    layer = receipt["projection_layer"]
    assert layer["relation"] == "a²=xy=1"
    assert layer["a²"] == {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
    assert layer["xy"] == {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
    assert layer["relation_kind"] == "SCALAR_PROJECTION_LAYER_ONLY"


def test_native_identity_and_xy_yx_commutation_remain_forbidden():
    receipt = _all_ones_3x3_receipt()
    assert receipt["native_a2_xy_identity_authorized"] is False
    assert receipt["xy_yx_commutation_authorized"] is False
    assert receipt["canonical_admission_authority"] is False
    assert receipt["vm81_mutation_authority"] is False


def test_nonunit_orbit_fails_closed():
    _raises(
        SPISymmetricUnitProductError,
        symmetric_unit_product_projection,
        surface_id="BAD",
        surface_source="((1,2),(2,1))",
        symmetry_orbits=(
            {"orbit_id": "diag", "members": ("00", "11"), "product": 1, "involution_closed": True},
            {"orbit_id": "off", "members": ("01", "10"), "product": 4, "involution_closed": True},
        ),
        total_component_count=4,
    )


def test_incomplete_surface_coverage_fails_closed():
    _raises(
        SPISymmetricUnitProductError,
        symmetric_unit_product_projection,
        surface_id="BAD-COVERAGE",
        surface_source="((1,1),(1,1))",
        symmetry_orbits=(
            {"orbit_id": "diag", "members": ("00", "11"), "product": 1, "involution_closed": True},
        ),
        total_component_count=4,
    )


def test_noninvolutive_symmetry_fails_closed():
    _raises(
        SPISymmetricUnitProductError,
        symmetric_unit_product_projection,
        surface_id="BAD-SYMMETRY",
        surface_source="tensor",
        symmetry_orbits=(
            {"orbit_id": "o", "members": ("a",), "product": 1, "involution_closed": False},
        ),
        total_component_count=1,
    )


def test_float_product_fails_closed():
    _raises(
        SPISymmetricUnitProductError,
        symmetric_unit_product_projection,
        surface_id="BAD-FLOAT",
        surface_source="tensor",
        symmetry_orbits=(
            {"orbit_id": "o", "members": ("a",), "product": 1.0, "involution_closed": True},
        ),
        total_component_count=1,
    )


def test_receipt_deterministic():
    assert _all_ones_3x3_receipt() == _all_ones_3x3_receipt()


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
        "schema": "HHS_SPI_SYMMETRIC_UNIT_PRODUCT_PROJECTION_TEST_REPORT_V1",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
