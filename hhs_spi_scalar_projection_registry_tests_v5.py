"""Focused tests for Pass 219 SPI Scalar Projection Registry v5."""
from __future__ import annotations

import json

from hhs_spi_scalar_projection_registry_v4 import build_registry_v4
from hhs_spi_scalar_projection_registry_v5 import (
    CUBIC_THREESET_PROOF_ID,
    EQUAL_SUM_PROOF_ID,
    FIBONACCI_SCALE_PROOF_ID,
    STACK_PROOF_ID,
    build_registry_v5,
    coverage_manifest_v5,
    validation_report,
)


def test_validation_green():
    report = validation_report()
    assert report["ok"], report
    assert report["tensor_pair_three_set"] == "t³=t+a²"
    assert report["changed_predecessor_proof_ids"] == []
    assert report["canonical_admission_authority"] is False


def test_predecessor_registry_is_frozen():
    base = build_registry_v4()
    current = build_registry_v5()
    for proof_id, proof in base.items():
        assert current[proof_id].to_dict() == proof.to_dict()


def test_equal_sum_proof_is_equation_translation_only():
    proof = build_registry_v5()[EQUAL_SUM_PROOF_ID]
    assert proof.proof_status == "CLOSED"
    assert proof.coverage_state == "PROVEN"
    assert proof.result["local_scale"] == "a²=1"
    assert proof.result["lo_shu_sum"] == 15
    assert proof.result["sudoku_sum"] == 45
    assert proof.result["sudoku_equation_count"] == 27
    assert proof.result["cellwise_tensor_identity_authorized"] is False
    assert proof.canonical_admission is False


def test_fibonacci_scaling_proof_keeps_phi_symbolic():
    proof = build_registry_v5()[FIBONACCI_SCALE_PROOF_ID]
    assert proof.result["pythagorean_seed"] == "a²+b²=c²"
    assert proof.result["base_square_states"] == [1, 2, 3, 5, 8]
    assert proof.result["finite_ratios_exact"] is True
    assert proof.result["golden_limit"] == "Phi²-Phi-1=0; positive root"
    assert proof.result["finite_ratio_replaced_by_phi"] is False


def test_cubic_three_set_does_not_solve_t():
    proof = build_registry_v5()[CUBIC_THREESET_PROOF_ID]
    assert proof.result["three_set"] == ["t³", "t", "a²"]
    assert proof.result["relation"] == "t³=t+a²"
    assert proof.result["residual_relation"] == "t³-t=a²=∆=1"
    assert proof.result["native_t_solved"] is False


def test_composite_stack_orders_all_three_layers():
    proof = build_registry_v5()[STACK_PROOF_ID]
    assert proof.result["ordered_layers"] == [
        "EQUAL_SUM_A2_NORMALIZATION",
        "FIBONACCI_PYTHAGOREAN_SCALE",
        "TENSOR_PAIR_CUBIC_THREE_SET",
    ]
    assert proof.result["local_scale"] == "a²=1"
    assert proof.result["universal_denominator"] == "∆=1"
    assert proof.result["cubic_three_set"] == "t³=t+a²"
    assert proof.result["pythagorean_scale_seed"] == "a²+b²=c²"
    assert proof.result["golden_limit_symbolic"] is True
    assert proof.canonical_admission is False


def test_manifest_authority_boundary():
    manifest = coverage_manifest_v5()
    boundary = manifest["authority_boundary"]
    assert boundary["projection_only"] is True
    assert boundary["native_tensor_identity"] is False
    assert boundary["native_t_solved"] is False
    assert boundary["finite_ratio_replaced_by_phi"] is False
    assert boundary["vm81_mutation"] is False
    assert boundary["canonical_hash72_hash216_minting"] is False
    assert boundary["canonical_persistence"] is False
    assert boundary["floating_point_authority"] is False


def test_deterministic_manifest():
    assert coverage_manifest_v5()["manifest_sha256"] == coverage_manifest_v5()["manifest_sha256"]


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
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_TEST_REPORT_V5",
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
