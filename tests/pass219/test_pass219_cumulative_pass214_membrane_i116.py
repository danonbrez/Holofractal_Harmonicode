from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass214 import (
    EXACT_VM81_RUNTIME_GIT_BLOB,
    PASS214_BIND_SYMBOL,
    PASS214_CAPABILITIES,
    PASS214_CLASSIFICATION,
    PASS214_MAIN_CLOSURE_ARTIFACT_SHA256,
    PASS214_MAIN_CLOSURE_COMMIT,
    PASS214_MAIN_CLOSURE_RUN,
    PASS214_MAIN_CLOSURE_TREE,
    PASS214_NUMBER,
    PASS214_ROOTS,
    PASS214_SEMANTIC_REUSE_HEAD,
    PASS214_TERMINAL_RECEIPT_HASH72,
    pass214_membrane_manifest,
    pass214_membrane_source_evidence,
    pass214_membrane_surface_declaration,
    preflight_pass214_membrane,
)


def main() -> None:
    evidence = pass214_membrane_source_evidence()
    iteration8 = evidence["iteration8"]
    boundary = iteration8["benchmark_boundary"]
    semantic = evidence["semantic_reuse"]
    authority = semantic["authority"]

    assert PASS214_NUMBER == 214
    assert PASS214_CLASSIFICATION == "WIRED"
    assert evidence["main_closure_commit"] == PASS214_MAIN_CLOSURE_COMMIT
    assert evidence["main_closure_tree"] == PASS214_MAIN_CLOSURE_TREE
    assert evidence["main_closure_run"] == PASS214_MAIN_CLOSURE_RUN
    assert evidence["main_closure_artifact_sha256"] == PASS214_MAIN_CLOSURE_ARTIFACT_SHA256
    assert evidence["terminal_roots"] == PASS214_ROOTS
    assert evidence["terminal_receipt_hash72"] == PASS214_TERMINAL_RECEIPT_HASH72
    assert boundary["workload_families"] == 15
    assert boundary["workload_modes_per_family"] == 11
    assert boundary["mode_executions"] == 165
    assert boundary["mandatory_ablations"] == 26
    assert boundary["a0_a9_stages"] == 10
    assert boundary["pass197_address_comparisons"] == 1658880
    assert boundary["pass212_full_hydration_bits"] == 50388480
    assert boundary["pass212_full_state_recoveries"] == 3
    assert boundary["cross_process_replays"] == 15
    assert boundary["multimodal_ml_compound_exercised"] is True
    assert boundary["multimodal_ml_ablation_exercised"] is True
    assert boundary["negative_controls_fail_closed"] is True
    assert boundary["complete_cost_accounting"] is True

    assert evidence["semantic_reuse_head"] == PASS214_SEMANTIC_REUSE_HEAD
    assert authority["execution_authority_changed"] is False
    assert authority["automatic_semantic_promotion"] is False
    assert authority["pass213_governed_mutation_authority_preserved"] is True
    assert semantic["semantic_reconciliation"]["reusable_registry_entries"] == 306
    assert semantic["isolation_accounting"]["remaining_reusable_extraction_backlog"] == 1383
    assert semantic["first_reusable_module_promotion"]["canonical_mutation_authority"] == "NONE"
    assert evidence["exact_vm81_kernel_git_blob"] == EXACT_VM81_RUNTIME_GIT_BLOB

    declaration = pass214_membrane_surface_declaration()
    manifest = pass214_membrane_manifest()
    assert declaration["symbol"] == PASS214_BIND_SYMBOL
    assert declaration["declared_operations"] == [PASS214_BIND_SYMBOL]
    assert declaration["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert declaration["persistence_policy"] == "INHERITED_BENCHMARK_AND_REUSE_IDENTITY_ONLY"
    assert manifest["classification"] == "WIRED"
    assert tuple(manifest["capabilities"]) == PASS214_CAPABILITIES
    assert manifest["pass213_gates_preserved"] is True
    assert manifest["execution_authority_changed_by_semantic_reuse"] is False
    assert manifest["automatic_semantic_promotion"] is False
    assert manifest["runtime_mutation_authority_promoted"] is False
    assert manifest["canonical_mutation_authorized"] is False
    assert manifest["migration_active"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False
    assert manifest["next_pass_to_census"] == 213

    cache = {}
    first = preflight_pass214_membrane(cache=cache)
    second = preflight_pass214_membrane(cache=cache)
    assert first["ok"] is True
    assert second["ok"] is True
    assert first["status"] == "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"
    assert first["surface_id"] == declaration["surface_id"]
    assert first["operation"] == PASS214_BIND_SYMBOL
    assert first["composition_plan"]["composition_allowed"] is True
    assert first["composition_plan"]["pipeline"]["execution_adapter"] == PASS214_BIND_SYMBOL
    assert first["composition_plan"]["pipeline"]["handwired"] is False
    assert first["composition_plan"]["pipeline"]["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert second["cache"]["cache_hit"] is True


if __name__ == "__main__":
    main()
