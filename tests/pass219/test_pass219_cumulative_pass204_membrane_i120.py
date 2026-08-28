from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i120_pass204 import (
    PASS204_BIND_SYMBOL,
    PASS204_CENSUS_CLASSIFICATION,
    pass204_membrane_manifest,
    pass204_membrane_source_evidence,
    preflight_pass204_membrane,
    validate_pass203_inherited_replay,
    validate_pass204_declaration_closure,
    validate_pass204_fixed_sandbox_policy,
    validate_pass204_immutable_history_boundary,
    validate_pass204_native_execution_boundary,
    validate_pass204_persistence_and_recall,
    validate_pass204_production_identity,
    validate_pass205_successor_binding,
)


def main() -> None:
    source = pass204_membrane_source_evidence()
    assert source["validated_head"] == "6b26fbf6f4b767d4eb5f2a790c552b03fd39d352"
    assert source["merge_commit"] == "deb34287ee155d9538005bbbfd6519794d999ac9"
    assert source["validation_receipt_blob"] == "2b2a3baa87ea41577b4b4397da03b1b790c5cfae"

    production = validate_pass204_production_identity()
    assert production["ok"] is True
    assert production["classification"] == "HHS_PASS_204_UNIVERSAL_EXECUTABLE_DECLARATIONS_OPEN_CLOUD_VERIFIED"

    closure = validate_pass204_declaration_closure()
    assert closure["catalog_count"] == 2939
    assert closure["catalog_count"] == closure["hydrated_count"] == closure["callable_count"]
    assert closure["binding_gap_count"] == 0
    assert closure["all_declarations_executable"] is True

    sandbox = validate_pass204_fixed_sandbox_policy()
    assert sandbox["remote_users_automatically_sandboxed"] is True
    assert sandbox["persistent_capabilities"] is False
    assert sandbox["direct_host_kernel_access"] is False
    assert sandbox["caller_adjustable_internal_policy"] is False

    history = validate_pass204_immutable_history_boundary()
    assert history["admitted_history_mutable"] is False
    assert history["constraint_authority_mutable"] is False
    assert history["host_fault_can_rewrite_admitted_hash_history"] is False
    assert history["host_fault_can_mutate_constraint_contract"] is False

    persistence = validate_pass204_persistence_and_recall()
    assert persistence["inherited_durable_outputs"] == ["artifacts", "jobs", "receipts", "layered_snapshots"]
    assert persistence["recall_verified"] is True
    assert persistence["capabilities_restored_on_recall"] is False
    assert persistence["i120_new_persistence_authority"] is False

    native = validate_pass204_native_execution_boundary()
    assert native["core_native_execution_status"] == "COMPLETED"
    assert native["project_native_execution_status"] == "ACCEPTED"
    assert native["raw_pointer_exposed"] is False
    assert native["direct_host_kernel_access"] is False

    inherited = validate_pass203_inherited_replay()
    assert inherited["inherited_pass"] == 203
    assert inherited["standalone_replay"] is True

    successor = validate_pass205_successor_binding()
    assert successor["successor_pass"] == 205
    assert successor["successor_classification"] == "HHS_PASS_205_DETERMINISTIC_MULTIMODAL_CONTINUATION_RUNTIME_VERIFIED"

    manifest = pass204_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert manifest["census_classification"] == PASS204_CENSUS_CLASSIFICATION == "MISSING_MEMBRANE_EXPOSURE"
    assert manifest["pass219_c_abi_surface"] == PASS204_BIND_SYMBOL
    assert manifest["inherited_pass204_persistence_bound"] is True
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["pass219_new_persistence_authority"] is False
    assert manifest["pass219_new_hash72_clock"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False

    preflight = preflight_pass204_membrane()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == 8
    assert all(row["ok"] is True for row in preflight["operations"])


if __name__ == "__main__":
    main()
