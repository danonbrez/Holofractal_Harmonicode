"""Focused tests for Pass 219 SPI Scalar Projection Registry v6."""
from __future__ import annotations

import json

from hhs_spi_constraint_evolution_optimizer_v1 import LIFECYCLE
from hhs_spi_scalar_projection_registry_v5 import build_registry_v5
from hhs_spi_scalar_projection_registry_v6 import (
    OPTIMIZER_PROOF_ID,
    build_registry_v6,
    coverage_manifest_v6,
    validation_report,
)


def test_validation_green():
    report = validation_report()
    assert report["ok"], report
    assert report["changed_predecessor_proof_ids"] == []
    assert report["new_proof_ids"] == [OPTIMIZER_PROOF_ID]
    assert report["lifecycle"] == list(LIFECYCLE)
    assert report["vm5184_address_count"] == 5184
    assert report["canonical_admission_authority"] is False


def test_v5_registry_is_frozen():
    base = build_registry_v5()
    current = build_registry_v6()
    for proof_id, proof in base.items():
        assert current[proof_id].to_dict() == proof.to_dict()


def test_optimizer_proof_closes_full_lifecycle_without_authority_expansion():
    proof = build_registry_v6()[OPTIMIZER_PROOF_ID]
    assert proof.proof_status == "CLOSED"
    assert proof.implementation_status == "IMPLEMENTED"
    assert proof.receipt_status == "VERIFIED"
    assert proof.coverage_state == "PROVEN"
    assert proof.result["lifecycle"] == list(LIFECYCLE)
    assert proof.result["vm5184_address_count"] == 5184
    assert proof.result["four_lane_hydration"] is True
    assert proof.result["semantic_label_used_for_selection"] is False
    assert proof.result["empirical_speedup_claimed"] is False
    assert proof.result["canonical_hash216_minted"] is False
    assert proof.canonical_admission is False


def test_optimizer_reference_selection_is_exact_and_deterministic():
    proof = build_registry_v6()[OPTIMIZER_PROOF_ID]
    assert proof.result["selection_rule"] == [
        "MIN_UNRESOLVED_BRANCH_COUNT",
        "MAX_REUSABLE_BRANCH_COUNT",
        "STABLE_CANDIDATE_ID",
    ]
    assert proof.result["selected_reference_candidate"] == "SUDOKU-S4-REUSE"
    assert proof.result["selected_reference_score"] == {
        "unresolved_branch_count": 9,
        "reusable_branch_count": 72,
    }
    assert proof.result["next_cycle"] == "FORMALIZE"


def test_manifest_authority_boundary():
    manifest = coverage_manifest_v6()
    boundary = manifest["authority_boundary"]
    assert boundary == {
        "projection_only": True,
        "candidate_only": True,
        "semantic_selection_authority": False,
        "vm81_mutation": False,
        "canonical_hash72_hash216_minting": False,
        "canonical_persistence": False,
        "floating_point_authority": False,
        "unmeasured_speedup_claim": False,
    }


def test_manifest_is_deterministic():
    assert coverage_manifest_v6()["manifest_sha256"] == coverage_manifest_v6()["manifest_sha256"]


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
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_TEST_REPORT_V6",
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
