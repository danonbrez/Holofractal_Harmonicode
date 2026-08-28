from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i125_pass200b import (
    PASS200B_CENSUS_CLASSIFICATION,
    PASS200B_CLASSIFICATION,
    PASS200B_NUMBER,
    PASS200B_VARIANT,
    REQUIRED_OPERATIONS,
    pass200b_membrane_manifest,
    preflight_pass200b_membrane,
)


def main() -> None:
    manifest = pass200b_membrane_manifest()
    assert manifest["pass_number"] == PASS200B_NUMBER == 200
    assert manifest["pass_variant"] == PASS200B_VARIANT == "B"
    assert manifest["pass_id"] == "pass200b"
    assert manifest["classification"] == PASS200B_CLASSIFICATION == "WIRED"
    assert manifest["census_classification"] == PASS200B_CENSUS_CLASSIFICATION == "MISSING_MEMBRANE_EXPOSURE"
    assert manifest["primary_pull_request"] == 139
    assert manifest["historical_squash_identity_bound"] is True
    assert manifest["immutable_source_identity_bound"] is True
    assert manifest["pass200a_shadow_gate_bound"] is True
    assert manifest["dual_approval_and_activation_bound"] is True
    assert manifest["bounded_integer_selection_bound"] is True
    assert manifest["exact_comparison_bound"] is True
    assert manifest["rollback_and_exhaustion_bound"] is True
    assert manifest["inherited_durable_state_read_only_bound"] is True
    assert manifest["pass200c_successor_bound"] is True
    assert manifest["pass219_new_canary_admission_authority"] is False
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["pass219_new_persistence_authority"] is False
    assert manifest["pass219_new_hash72_clock"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False

    preflight = preflight_pass200b_membrane()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(REQUIRED_OPERATIONS) == 7
    assert all(row["ok"] is True for row in preflight["operations"])


if __name__ == "__main__":
    main()
