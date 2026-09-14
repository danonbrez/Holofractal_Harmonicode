"""Focused tests for Pass 219 SPI Scalar Projection Registry v4."""
from __future__ import annotations

import json
from fractions import Fraction

from hhs_spi_scalar_projection_registry_v3 import build_registry_v3
from hhs_spi_scalar_projection_registry_v4 import (
    A2_LOCAL_SCALE_PROOF_ID,
    DELTA_DENOMINATOR_PROOF_ID,
    HIERARCHY_PROOF_ID,
    build_registry_v4,
    coverage_manifest_v4,
    validation_report,
)


def test_validation_green():
    report = validation_report()
    assert report["ok"], report
    assert report["universal_denominator"] == "∆=1"
    assert report["local_scale_bridge"] == "a²=∆=1"
    assert report["changed_predecessor_proof_ids"] == []
    assert report["canonical_admission_authority"] is False


def test_predecessor_v3_is_frozen():
    base = build_registry_v3()
    current = build_registry_v4()
    assert set(base).issubset(current)
    for proof_id, proof in base.items():
        assert current[proof_id].to_dict() == proof.to_dict()


def test_delta_is_system_wide_denominator_unit():
    proof = build_registry_v4()[DELTA_DENOMINATOR_PROOF_ID]
    assert proof.proof_status == "CLOSED"
    assert proof.coverage_state == "PROVEN"
    assert proof.result["symbol"] == "∆"
    assert proof.result["projection"] == Fraction(1)
    assert proof.result["role"] == "SYSTEM_WIDE_UNIVERSAL_DENOMINATOR_UNIT"
    assert proof.result["value_preserving"] is True
    assert proof.canonical_admission is False


def test_a2_is_local_scale_bridged_to_delta():
    proof = build_registry_v4()[A2_LOCAL_SCALE_PROOF_ID]
    assert proof.proof_status == "CLOSED"
    assert proof.result["local_scale_symbol"] == "a²"
    assert proof.result["local_scale"] == Fraction(1)
    assert proof.result["universal_denominator_symbol"] == "∆"
    assert proof.result["universal_denominator"] == Fraction(1)
    assert proof.result["bridge"] == "a²=∆=1"
    assert proof.result["native_a2_delta_identity_authorized"] is False
    assert proof.canonical_admission is False


def test_unit_hierarchy_composes_local_and_global_normalization():
    proof = build_registry_v4()[HIERARCHY_PROOF_ID]
    assert proof.result["universal_denominator"] == {"symbol": "∆", "value": Fraction(1)}
    assert proof.result["local_scale"] == {"symbol": "a²", "value": Fraction(1)}
    assert proof.result["bridge"] == "a²=∆=1"
    assert "without scalar drift" in proof.result["composition_rule"]
    assert proof.canonical_admission is False


def test_manifest_preserves_native_boundaries():
    manifest = coverage_manifest_v4()
    hierarchy = manifest["normalization_hierarchy"]
    assert hierarchy["universal_denominator"] == "∆=1"
    assert hierarchy["local_scale_bridge"] == "a²=∆=1"
    assert hierarchy["native_a2_delta_identity"] is False
    boundary = manifest["authority_boundary"]
    assert boundary["projection_only"] is True
    assert boundary["native_a2_delta_identity"] is False
    assert boundary["native_member_identity_collapse"] is False
    assert boundary["native_division_rewrite"] is False
    assert boundary["xy_yx_commutation"] is False
    assert boundary["normalization_preserves_unit"] is True
    assert boundary["vm81_mutation"] is False
    assert boundary["canonical_hash72_hash216_minting"] is False
    assert boundary["canonical_persistence"] is False
    assert boundary["floating_point_authority"] is False


def test_deterministic_manifest():
    assert coverage_manifest_v4()["manifest_sha256"] == coverage_manifest_v4()["manifest_sha256"]


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
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_TEST_REPORT_V4",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
