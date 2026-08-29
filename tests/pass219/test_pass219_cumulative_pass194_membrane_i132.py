from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i132_pass194 import (
    PASS194_CENSUS_CLASSIFICATION,
    REQUIRED_OPERATIONS,
    execute_pass194_membrane_preflight,
    invoke,
    pass194_membrane_manifest,
)


def main() -> None:
    manifest = pass194_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert PASS194_CENSUS_CLASSIFICATION == "MISSING_IMPLEMENTATION_AND_MEMBRANE_EXPOSURE"
    assert manifest["contract_authorization_commit"] == "714f3f3c5c77eab9714be421811ce4fd650a8e99"
    assert manifest["frozen_predecessor"] == "b8202201bc92470afdd15d701d16ea102aeb3aab"
    assert tuple(manifest["declared_operations"]) == REQUIRED_OPERATIONS

    preflight = execute_pass194_membrane_preflight()
    assert preflight["ok"] is True

    lineage = invoke("validate_pass194_contract_and_lineage")
    assert lineage["ok"] is True
    assert lineage["historical_contract_preserved"] is True

    storage = invoke("validate_pass194_content_and_sql_boundary")
    assert storage["content_addressed_blob_store"] is True
    assert storage["blob_identity_immutable"] is True
    assert storage["versioned_sql_context_graph"] is True
    assert storage["sqlite_wal"] is True
    assert storage["sqlite_synchronous_full"] is True
    assert storage["metadata_mutation_requires_inherited_vm81_receipt"] is True

    consent = invoke("validate_pass194_consent_dataset_boundary")
    assert consent["training_default_deny"] is True
    assert consent["sharing_default_deny"] is True
    assert consent["public_default_deny"] is True
    assert consent["training_requires_license"] is True
    assert consent["dataset_requires_snapshot_consent_closure"] is True

    vector = invoke("validate_pass194_vector_snapshot_boundary")
    assert vector["encrypted_hash216_vector_projection"] is True
    assert vector["vector_frame_uses_inherited_vmrc_snapshot_bytes"] is True
    assert vector["vector_store_is_source_authority"] is False
    assert vector["vector_store_is_consent_authority"] is False
    assert vector["vector_store_is_vm81_authority"] is False
    assert vector["snapshot_is_training_authorization"] is False

    training = invoke("validate_pass194_training_checkpoint_boundary")
    assert training["training_run_kinds_bounded"] is True
    assert training["dataset_lineage_bound"] is True
    assert training["checkpoint_artifact_sha256_bound"] is True
    assert training["training_provider_is_vm81_authority"] is False
    assert training["checkpoint_is_vm81_authority"] is False

    replay = invoke("validate_pass194_revocation_replay_boundary")
    assert replay["file_delete_tombstone"] is True
    assert replay["dataset_revocation_propagates"] is True
    assert replay["training_run_revocation_propagates"] is True
    assert replay["receipt_chain_replay"] is True

    successor = invoke("validate_pass194_successor_binding")
    assert successor["successor_pass"] == 195
    assert successor["successor_accepted_merge"] == "8bcc0921555ecface13113c8a2620415ddb3fdf1"
    assert successor["successor_preserved"] is True

    authority = invoke("validate_pass194_no_new_authority")
    assert authority["i132_new_candidate_authority"] is False
    assert authority["i132_new_canonical_mutation_authority"] is False
    assert authority["i132_new_persistence_authority"] is False
    assert authority["i132_new_hash72_clock"] is False
    assert authority["cxx_mutation_authority"] is False
    assert authority["vm81_mutation_authority"] is False
    assert authority["vector_store_is_source_authority"] is False
    assert authority["vector_store_is_consent_authority"] is False
    assert authority["browser_is_authority"] is False
    assert authority["training_provider_is_vm81_authority"] is False
    assert authority["singleton_vm81_authority_remains_inherited"] is True


if __name__ == "__main__":
    main()
