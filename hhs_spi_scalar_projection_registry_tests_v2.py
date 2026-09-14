"""Focused tests for Pass 219 SPI Scalar Projection Registry v2."""
from __future__ import annotations

import json

from hhs_spi_scalar_projection_registry_v1 import MISSING_PROJECTION, OPEN, SYMBOLIC
from hhs_spi_scalar_projection_registry_v2 import (
    O2_PROFILE,
    build_registry_v2,
    coverage_manifest_v2,
    validation_report,
)


def test_validation_green():
    report = validation_report()
    assert report["ok"], report
    assert report["changed_proof_ids"] == ["SPI-O2-MATRIX"]
    assert report["o2_profile"] == O2_PROFILE
    assert report["o2_relation"] == "a²=xy=1"
    assert report["generic_matrix_tensor_scalarization_authorized"] is False
    assert report["canonical_admission_authority"] is False


def test_o2_closed_as_projection_layer():
    registry = build_registry_v2()
    o2 = registry["SPI-O2-MATRIX"]
    exact_one = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
    assert o2.profile == O2_PROFILE
    assert o2.proof_status == "CLOSED"
    assert o2.coverage_state == "PROVEN"
    assert o2.implementation_status == "IMPLEMENTED"
    assert o2.receipt_status == "VERIFIED"
    assert o2.result["a²"] == exact_one
    assert o2.result["xy"] == exact_one
    assert o2.result["relation"] == "a²=xy=1"
    assert o2.result["relation_kind"] == "SCALAR_PROJECTION_LAYER_ONLY"
    assert o2.canonical_admission is False


def test_o3_and_t3c_stay_open():
    registry = build_registry_v2()
    o3 = registry["SPI-O3-PROVENANCE"]
    t3c = registry["SPI-T3C"]
    assert o3.proof_status == OPEN
    assert o3.coverage_state == MISSING_PROJECTION
    assert t3c.proof_status == OPEN
    assert t3c.coverage_state == SYMBOLIC


def test_rules_do_not_authorize_native_identity_or_generic_scalarization():
    manifest = coverage_manifest_v2()
    boundary = manifest["authority_boundary"]
    assert boundary["projection_only"] is True
    assert boundary["native_a2_xy_identity"] is False
    assert boundary["xy_yx_commutation"] is False
    assert boundary["generic_matrix_tensor_scalarization"] is False
    assert boundary["vm81_mutation"] is False
    assert boundary["canonical_hash72_hash216_minting"] is False
    assert boundary["canonical_persistence"] is False
    assert boundary["floating_point_authority"] is False


def test_manifest_has_both_projection_rules():
    manifest = coverage_manifest_v2()
    assert manifest["projection_rules"] == [
        "MATRIX_TENSOR_DEFINED_SCALAR_PROJECTION-v1",
        "SYMMETRIC-UNIT-PRODUCT-LAYER-v1",
    ]


def test_receipts_deterministic():
    a = build_registry_v2()["SPI-O2-MATRIX"].receipt_sha256()
    b = build_registry_v2()["SPI-O2-MATRIX"].receipt_sha256()
    assert a == b
    assert coverage_manifest_v2()["manifest_sha256"] == coverage_manifest_v2()["manifest_sha256"]


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
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_TEST_REPORT_V2",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
