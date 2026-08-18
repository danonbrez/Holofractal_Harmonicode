from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass213 import (
    PASS213_BIND_SYMBOL,
    PASS213_CAPABILITIES,
    PASS213_CLASSIFICATION,
    PASS213_EXECUTE_SYMBOL,
    PASS213_MAIN_ARTIFACT_SHA256,
    PASS213_MAIN_MERGE_HEAD,
    PASS213_MAIN_VALIDATION_JOB,
    PASS213_MAIN_VALIDATION_RUN,
    PASS213_NATIVE_DISPATCH_IDS,
    PASS213_NUMBER,
    PASS213_SEMANTIC_ROOT_HASH216,
    PASS213_TERMINAL_RECEIPT_HASH72,
    ROOT,
    pass213_execution_surface_declaration,
    pass213_membrane_manifest,
    pass213_membrane_source_evidence,
    pass213_validator_surface_declaration,
    preflight_pass213_membrane,
)


def main() -> None:
    evidence = pass213_membrane_source_evidence()
    contract = evidence["contract"]
    semantic = contract["terminal_semantic_evidence"]
    observation = contract["reference_performance_observation"]

    assert PASS213_NUMBER == 213
    assert PASS213_CLASSIFICATION == "WIRED"
    assert evidence["main_merge_head"] == PASS213_MAIN_MERGE_HEAD
    assert evidence["main_validation_run"] == PASS213_MAIN_VALIDATION_RUN
    assert evidence["main_validation_job"] == PASS213_MAIN_VALIDATION_JOB
    assert evidence["main_artifact_sha256"] == PASS213_MAIN_ARTIFACT_SHA256
    assert evidence["semantic_root_hash216"] == PASS213_SEMANTIC_ROOT_HASH216
    assert evidence["terminal_receipt_hash72"] == PASS213_TERMINAL_RECEIPT_HASH72
    assert contract["final_iteration"] == 11
    assert contract["closure"]["implementation_complete"] is True
    assert contract["closure"]["remaining_iterations"] == []
    assert tuple(contract["native_dispatch_ids"]) == PASS213_NATIVE_DISPATCH_IDS
    assert contract["required_invariants"]["no_float_canonical_authority"] is True
    assert contract["required_invariants"]["singleton_vm81_admission"] is True
    assert contract["required_invariants"]["native_dispatch_real_c_abi_required"] is True
    assert contract["required_invariants"]["native_dispatch_dynamic_allocation_forbidden"] is True
    assert contract["required_invariants"]["native_dispatch_ambient_state_forbidden"] is True
    assert semantic["dispatch_final_sequence"] == 32
    assert semantic["uninterrupted_and_resumed_receipts_equal"] is True
    assert semantic["ledger_chains_valid"] is True
    assert observation["hardware_specific"] is True
    assert observation["timings_canonical"] is False

    manifest = pass213_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert tuple(manifest["capabilities"]) == PASS213_CAPABILITIES
    assert manifest["inherited_governed_canonical_mutation_authority"] is True
    assert manifest["pass219_new_mutation_authority"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_direct_mutation_authority"] is False
    assert manifest["raw_native_dispatch_bypass_forbidden"] is True
    assert manifest["no_float_canonical_authority"] is True
    assert manifest["performance_timings_canonical"] is False
    assert manifest["next_pass_to_census"] == 212

    validator = pass213_validator_surface_declaration()
    execution = pass213_execution_surface_declaration()
    assert validator["symbol"] == PASS213_BIND_SYMBOL
    assert validator["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert execution["symbol"] == PASS213_EXECUTE_SYMBOL
    assert execution["mutation_policy"] == "CONTROLLED_RUNTIME_MUTATION"
    assert execution["persistence_policy"] == "CANONICAL_MUTATION_RECEIPT"
    assert execution["raw_native_c_symbol"] == "hhs_pass213_native_dispatch_execute"
    assert execution["raw_native_c_symbol_directly_reachable"] is False
    assert execution["inherited_authority"] is True
    assert execution["pass219_new_mutation_authority"] is False

    aggregate = (ROOT / "hhs_runtime/c/hhs_runtime_exact_abi.c").read_text("utf-8")
    assert "hhs_pass213_native_dispatch_execute" not in aggregate
    assert "hhs_pass219_inherited_pass213_1_16.inc" in aggregate

    cache = {}
    first = preflight_pass213_membrane(cache=cache)
    second = preflight_pass213_membrane(cache=cache)
    assert first["ok"] is True
    assert second["ok"] is True
    for record, expected_surface, expected_operation in (
        (first["validator"], validator["surface_id"], PASS213_BIND_SYMBOL),
        (first["execution"], execution["surface_id"], PASS213_EXECUTE_SYMBOL),
    ):
        assert record["ok"] is True
        assert record["status"] == "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"
        assert record["surface_id"] == expected_surface
        assert record["operation"] == expected_operation
        assert record["composition_plan"]["composition_allowed"] is True
        assert record["composition_plan"]["pipeline"]["handwired"] is False
    assert first["execution"]["composition_plan"]["pipeline"]["mutation_policy"] == "CONTROLLED_RUNTIME_MUTATION"
    assert first["execution"]["composition_plan"]["pipeline"]["persistence_policy"] == "CANONICAL_MUTATION_RECEIPT"
    assert second["validator"]["cache"]["cache_hit"] is True
    assert second["execution"]["cache"]["cache_hit"] is True


if __name__ == "__main__":
    main()
