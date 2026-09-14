"""Focused tests for Pass 219 SPI Scalar Projection Registry v8."""
from __future__ import annotations

import json

from hhs_spi_computational_determinism_invariant_v1 import (
    DETERMINISM_INVARIANT_ID,
    HALT_REASONS,
    OUTCOMES,
)
from hhs_spi_computational_determinism_invariant_v2 import (
    SELECTION_RULE_V2,
    reference_determinism_witness,
)
from hhs_spi_scalar_projection_registry_v7 import build_registry_v7
from hhs_spi_scalar_projection_registry_v8 import (
    BOUNDED_EXECUTION_PROOF_ID,
    DETERMINISM_PROOF_ID,
    build_registry_v8,
    coverage_manifest_v8,
    validation_report,
)


def test_validation_green_and_v7_frozen():
    report = validation_report()
    assert report["ok"], report
    assert report["new_proof_ids"] == sorted(
        [BOUNDED_EXECUTION_PROOF_ID, DETERMINISM_PROOF_ID]
    )
    assert report["changed_predecessor_proof_ids"] == []
    assert report["determinism_invariant_id"] == DETERMINISM_INVARIANT_ID
    assert report["outcome_domain"] == list(OUTCOMES)
    assert report["halt_reason_classes"] == list(HALT_REASONS)
    assert report["selection_rule"] == list(SELECTION_RULE_V2)
    assert report["discretionary_refusal_state_exists"] is False
    assert report["canonical_admission_authority"] is False

    base = build_registry_v7()
    current = build_registry_v8()
    for proof_id, proof in base.items():
        assert current[proof_id].to_dict() == proof.to_dict()


def test_computational_determinism_is_registered_as_enforced_invariant():
    proof = build_registry_v8()[DETERMINISM_PROOF_ID]
    assert proof.proof_status == "CLOSED"
    assert proof.implementation_status == "IMPLEMENTED"
    assert proof.receipt_status == "VERIFIED"
    assert proof.coverage_state == "PROVEN"
    assert proof.result["determinism_invariant_id"] == DETERMINISM_INVARIANT_ID
    assert proof.result["outcomes"] == ["ADVANCE", "HALT"]
    assert proof.result["selection_rule"] == list(SELECTION_RULE_V2)
    assert proof.result["candidate_receipt_used_for_selection"] is False
    assert proof.result["semantic_label_used_for_selection"] is False
    assert proof.result["candidate_enumeration_order_has_no_authority"] is True
    assert proof.result["deterministic_replay_closes"] is True
    assert proof.result["duplicate_candidate_identity_halts"] is True
    assert proof.result["discretionary_refusal_state_exists"] is False
    assert proof.canonical_admission is False


def test_bounded_instruction_proof_requires_explicit_scope_and_closure():
    proof = build_registry_v8()[BOUNDED_EXECUTION_PROOF_ID]
    assert proof.result["explicit_instruction_required"] is True
    assert proof.result["authorized_scope_required"] is True
    assert proof.result["specific_closing_condition_required"] is True
    assert proof.result["finite_step_bound_required"] is True
    assert proof.result["outcome_domain"] == ["ADVANCE", "HALT"]
    assert proof.result["halt_reason_classes"] == list(HALT_REASONS)
    assert proof.result["closed_state_halts"] is True
    assert proof.result["empty_branch_halts"] is True
    assert proof.result["advance_reaches_closing_condition"] is True
    assert proof.result["discretionary_refusal_absent"] is True
    assert proof.result["semantic_override_authority"] is False
    assert proof.result["canonical_admission_authority"] is False


def test_reference_witness_closes_all_declared_invariants():
    witness = reference_determinism_witness()
    assert all(witness["invariants"].values()), witness["invariants"]
    assert witness["advance"]["outcome"] == "ADVANCE"
    assert witness["closed_halt"]["outcome"] == "HALT"
    assert witness["closed_halt"]["halt_reason"] == "CLOSED"
    assert witness["null_branch_halt"]["outcome"] == "HALT"
    assert witness["duplicate_identity_halt"]["outcome"] == "HALT"


def test_manifest_authority_boundary():
    manifest = coverage_manifest_v8()
    assert manifest["validation"]["ok"] is True
    assert manifest["authority_boundary"] == {
        "projection_only": True,
        "candidate_only": True,
        "computational_determinism_enforced": True,
        "outcomes_only_advance_or_halt": True,
        "discretionary_refusal_state": False,
        "semantic_selection_authority": False,
        "candidate_receipt_selection_authority": False,
        "vm81_mutation": False,
        "canonical_hash72_hash216_minting": False,
        "canonical_persistence": False,
        "floating_point_authority": False,
    }


def test_manifest_is_deterministic():
    assert coverage_manifest_v8()["manifest_sha256"] == coverage_manifest_v8()["manifest_sha256"]


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
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_TEST_REPORT_V8",
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
