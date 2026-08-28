from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i127_pass199 import (
    PASS199_CENSUS_CLASSIFICATION,
    REQUIRED_OPERATIONS,
    execute_pass199_membrane_preflight,
    invoke,
    pass199_membrane_manifest,
)


def main() -> None:
    manifest = pass199_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert PASS199_CENSUS_CLASSIFICATION == "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
    assert manifest["accepted_merge"] == "426fe7786abff2e1e4688222a600f5ab39d14a5a"
    assert manifest["frozen_predecessor"] == "fca09c16d2e9008de5cd9a09347e14de695e4ef3"
    assert manifest["validated_repair_head"] == "c2626fd4886b9e98e511c739b806dfc46863878d"
    assert manifest["review_finding_ids"] == [
        3700543546, 3700543548, 3700543550,
        3700543555, 3700543559, 3700543562,
    ]
    assert tuple(manifest["declared_operations"]) == REQUIRED_OPERATIONS

    preflight = execute_pass199_membrane_preflight()
    assert preflight["ok"] is True

    identity = invoke("validate_pass199_squash_identity")
    assert identity["ok"] is True
    assert identity["pull_request"] == 137
    assert identity["squash_aware"] is True
    assert identity["accepted_v1_v2_provenance_preserved"] is True

    repair = invoke("validate_pass199_review_repair")
    assert repair["ok"] is True
    assert repair["finding_count"] == 6
    assert repair["production_version"] == "HHS_PASS_199_DISTRIBUTED_CALIBRATION_FABRIC_V3"

    replay = invoke("validate_pass199_full_replay_closure")
    assert replay["full_replay_required"] is True
    assert replay["full_replay_executed"] is True
    assert replay["replayed_branch_jobs"] == 810
    assert replay["closure_without_replay_allowed"] is False

    binding = invoke("validate_pass199_receipt_and_verification_binding")
    assert binding["singleton_commit_count"] == 1
    assert binding["pass198_verification_count"] == 1
    assert binding["pass198_attachment_excluded_from_report_hash72_identity"] is True
    assert binding["conflicting_new_receipt_rejected"] is True

    restart = invoke("validate_pass199_worker_restartability")
    assert restart["stale_claim_recovery_before_slot_validation"] is True
    assert restart["durable_completion_total_reconciled"] is True
    assert restart["completed_before_restart_included"] is True
    assert restart["maximum_claim_batch_size"] == 64

    diversity = invoke("validate_pass199_gate_diversity")
    assert diversity["identity_basis"] == "CANONICAL_GATE_PAYLOAD_JSON"
    assert diversity["position_bound_hashes_counted_as_distinct"] is False
    assert diversity["pass197_exact_payload_identity_crosscheck"] is True

    acceptance = invoke("validate_pass199_production_acceptance")
    assert acceptance["parameter_states"] == 405
    assert acceptance["durable_branch_jobs"] == 810
    assert acceptance["admitted_states"] == 320
    assert acceptance["domain_rejections"] == 85
    assert acceptance["vm5184_address_comparisons"] == 1_658_880
    assert acceptance["replayed_branch_jobs"] == 810
    assert acceptance["singleton_commit_count"] == 1
    assert acceptance["pass198_verification_count"] == 1

    successor = invoke("validate_pass200a_successor_binding")
    assert successor["successor_variant"] == "A"
    assert successor["successor_preserved"] is True

    authority = invoke("validate_pass199_no_new_authority")
    assert authority["candidate_worker_is_authority"] is False
    assert authority["candidate_may_commit"] is False
    assert authority["pass198_mutation_authority"] is False
    assert authority["api_mutation_authority"] is False
    assert authority["i127_new_candidate_authority"] is False
    assert authority["i127_new_canonical_mutation_authority"] is False
    assert authority["i127_new_persistence_authority"] is False
    assert authority["i127_new_hash72_clock"] is False
    assert authority["cxx_mutation_authority"] is False
    assert authority["vm81_mutation_authority"] is False


if __name__ == "__main__":
    main()
