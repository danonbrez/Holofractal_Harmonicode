from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i124_pass200c import (
    PASS200C_CENSUS_CLASSIFICATION,
    PASS200C_CLASSIFICATION,
    PASS200C_NUMBER,
    PASS200C_VARIANT,
    REQUIRED_OPERATIONS,
    pass200c_membrane_manifest,
    preflight_pass200c_membrane,
)


def main() -> None:
    manifest = pass200c_membrane_manifest()
    assert manifest["pass_number"] == PASS200C_NUMBER == 200
    assert manifest["pass_variant"] == PASS200C_VARIANT == "C"
    assert manifest["pass_id"] == "pass200c"
    assert manifest["classification"] == PASS200C_CLASSIFICATION == "WIRED"
    assert manifest["census_classification"] == PASS200C_CENSUS_CLASSIFICATION == "MISSING_MEMBRANE_EXPOSURE"
    assert manifest["primary_pull_request"] == 140
    assert manifest["historical_squash_identity_bound"] is True
    assert manifest["immutable_source_identity_bound"] is True
    assert manifest["canary_evidence_gate_bound"] is True
    assert manifest["approval_and_activation_bound"] is True
    assert manifest["continuous_exact_guard_bound"] is True
    assert manifest["rollback_reference_restoration_bound"] is True
    assert manifest["inherited_durable_state_read_only_bound"] is True
    assert manifest["pass201_successor_bound"] is True
    assert manifest["pass219_new_active_admission_authority"] is False
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["pass219_new_persistence_authority"] is False
    assert manifest["pass219_new_hash72_clock"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False

    preflight = preflight_pass200c_membrane()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(REQUIRED_OPERATIONS) == 7
    assert all(row["ok"] is True for row in preflight["operations"])


if __name__ == "__main__":
    main()
