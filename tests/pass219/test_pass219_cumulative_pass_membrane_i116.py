from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import (
    BIND_SYMBOL,
    CLASSIFICATION,
    PASS216_BIND_SYMBOL,
    PASS216_CAPABILITIES,
    PASS216_CLASSIFICATION,
    PASS216_NUMBER,
    PASS217_BIND_SYMBOL,
    PASS217_CAPABILITIES,
    PASS217_CLASSIFICATION,
    PASS217_NUMBER,
    PASS218_CAPABILITIES,
    PASS_NUMBER,
    pass216_membrane_manifest,
    pass216_membrane_source_evidence,
    pass216_membrane_surface_declaration,
    pass217_membrane_manifest,
    pass217_membrane_source_evidence,
    pass217_membrane_surface_declaration,
    pass218_membrane_manifest,
    pass218_membrane_surface_declaration,
    preflight_pass216_membrane,
    preflight_pass217_membrane,
    preflight_pass218_membrane,
)


def _assert_preflight(declaration, operation, preflight) -> None:
    cache = {}
    first = preflight(cache=cache)
    second = preflight(cache=cache)
    assert first["ok"] is True
    assert second["ok"] is True
    assert first["status"] == "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"
    assert first["surface_id"] == declaration["surface_id"]
    assert first["operation"] == operation
    assert first["composition_plan"]["composition_allowed"] is True
    assert first["composition_plan"]["pipeline"]["execution_adapter"] == operation
    assert first["composition_plan"]["pipeline"]["handwired"] is False
    assert first["composition_plan"]["pipeline"]["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert second["cache"]["cache_hit"] is True


def main() -> None:
    declaration218 = pass218_membrane_surface_declaration()
    manifest218 = pass218_membrane_manifest()
    assert PASS_NUMBER == 218
    assert CLASSIFICATION == "WIRED"
    assert declaration218["symbol"] == BIND_SYMBOL
    assert declaration218["declared_operations"] == [BIND_SYMBOL]
    assert declaration218["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert declaration218["persistence_policy"] == "INHERITED_COMPLETION_IDENTITY_ONLY"
    assert manifest218["classification"] == "WIRED"
    assert manifest218["pass_number"] == 218
    assert tuple(manifest218["capabilities"]) == PASS218_CAPABILITIES
    assert manifest218["receipt_semantics_preserved"] is True
    assert manifest218["pass219_handoff_authority_minted"] is False
    assert manifest218["cxx_mutation_authority"] is False
    assert manifest218["canonical_pass218_i48_present_on_active_branch"] is True
    assert manifest218["required_repair"] is None
    assert manifest218["next_pass_to_census"] == 217
    assert manifest218["frozen_pass219_i116_checkpoint"] == "c34956f2982020d7b16513e31cae3f40d91e9326"
    assert manifest218["reconciliation_merge_commit"] == "b65cb3748abfb2558ef6f481dfede7c1da799344"
    _assert_preflight(declaration218, BIND_SYMBOL, preflight_pass218_membrane)

    evidence217 = pass217_membrane_source_evidence()
    closure = evidence217["closure"]
    i4 = evidence217["iteration4"]
    assert closure["status"] == "ADMIT_PASS217_CUMULATIVE_UTILIZATION_REACHABILITY_CLOSURE"
    assert closure["closure_ready"] is True
    assert closure["blockers"] == []
    assert closure["required_authority_count"] == 25
    assert closure["required_authority_bypass_negative_matrix"][
        "all_applicable_required_authority_omissions_blocked"
    ] is True
    assert closure["required_authority_profile_coverage"][
        "incremental_tokenization_applicable_active_path_proven"
    ] is True
    assert i4["claim_boundary"]["hash72_manifold_validated"] is True
    assert i4["claim_boundary"]["immutable_nucleus_validated"] is True
    assert i4["claim_boundary"]["canonical_authority_promoted"] is False
    assert i4["claim_boundary"]["runtime_mutation_performed"] is False

    declaration217 = pass217_membrane_surface_declaration()
    manifest217 = pass217_membrane_manifest()
    assert PASS217_NUMBER == 217
    assert PASS217_CLASSIFICATION == "WIRED"
    assert declaration217["symbol"] == PASS217_BIND_SYMBOL
    assert declaration217["declared_operations"] == [PASS217_BIND_SYMBOL]
    assert declaration217["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert declaration217["persistence_policy"] == "INHERITED_CLOSURE_IDENTITY_ONLY"
    assert manifest217["classification"] == "WIRED"
    assert manifest217["pass_number"] == 217
    assert tuple(manifest217["capabilities"]) == PASS217_CAPABILITIES
    assert manifest217["required_authority_count"] == 25
    assert manifest217["closure_blockers"] == []
    assert manifest217["global_surface_publication_complete"] is True
    assert manifest217["all_required_authority_omissions_blocked"] is True
    assert manifest217["incremental_tokenization_active_path_proven"] is True
    assert manifest217["i4_hash72_manifold_root_sha256"] == "c757bae150d9ab94485c680ec3143e715b674d35f445a72c6fb4ea2def6f7884"
    assert manifest217["i4_nucleus_identity_root_sha256"] == "da7b33fa1a419e00ce81eeeeb5f1c435acd6ae7b95d355e3a1749a6a238e3164"
    assert manifest217["i4_canonical_authority_promoted"] is False
    assert manifest217["checkpoint15_git_sha"] == "be71da59c9b8b7c7e055c03da703ca301849cfff"
    assert manifest217["integration_git_sha"] == "b0656a92ab29507f81eae760e070f74e49db83f4"
    assert manifest217["cxx_mutation_authority"] is False
    assert manifest217["genesis_rom_promotion_claimed_by_membrane"] is False
    assert manifest217["next_pass_to_census"] == 216
    _assert_preflight(declaration217, PASS217_BIND_SYMBOL, preflight_pass217_membrane)

    evidence216 = pass216_membrane_source_evidence()
    contract = evidence216["contract"]
    addendum = evidence216["addendum"]
    assert contract["status"] == "CONTRACT_COMPLETE_PARENT_TERMINAL_ALIGNED"
    assert contract["completion_boundary"]["contract_layer_complete"] is True
    assert contract["completion_boundary"]["parent_alignment_complete"] is True
    assert contract["completion_boundary"]["runtime_optimization_implementation_claimed"] is False
    assert addendum["sha256_deterministic_truth_gate"]["default_state"] == "CLOSED"
    assert addendum["sha256_deterministic_truth_gate"]["full_system_reproof_required_by_default"] is False
    assert addendum["pass216_operating_rule"]["global_strict_mode_default"] is False
    assert addendum["pass216_operating_rule"]["unchanged_authenticated_identity_requires_reexecution"] is False
    assert addendum["pass216_operating_rule"]["changed_transition_requires_dependency_scoped_exact_validation"] is True
    assert addendum["successor_inheritance"]["pass219_must_inherit_unchanged_pass215_pass216_and_pass217_authority"] is True

    declaration216 = pass216_membrane_surface_declaration()
    manifest216 = pass216_membrane_manifest()
    assert PASS216_NUMBER == 216
    assert PASS216_CLASSIFICATION == "WIRED"
    assert declaration216["symbol"] == PASS216_BIND_SYMBOL
    assert declaration216["declared_operations"] == [PASS216_BIND_SYMBOL]
    assert declaration216["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert declaration216["persistence_policy"] == "INHERITED_CONTRACT_ALIGNMENT_IDENTITY_ONLY"
    assert manifest216["classification"] == "WIRED"
    assert manifest216["pass_number"] == 216
    assert tuple(manifest216["capabilities"]) == PASS216_CAPABILITIES
    assert manifest216["contract_alignment_complete"] is True
    assert manifest216["parent_alignment_complete"] is True
    assert manifest216["pass215_final_head"] == "b85ea7c340976a20a78f9c7d8d89a688a1b4f8fc"
    assert manifest216["pass215_artifact_sha256"] == "9e71ff3f48cd4da24c34854f8eadfa57f26d7c6ef5bddd1026c89e2ace63bf55"
    assert manifest216["pass216_published_head"] == "0ad2759a4379376244589aa3ee241e51d779df26"
    assert manifest216["pass216_published_tree"] == "b9ff48b17f1e3c8272cd8c5c7b4381df69d4c7e9"
    assert manifest216["pass216_merge_commit"] == "f10e453c5d7c7467cf5e57f6452958491fe763ad"
    assert manifest216["contract_git_blob"] == "9e04e4aca8b127e009c0343ceb5e78092de40c43"
    assert manifest216["addendum_git_blob"] == "3e4121afe2f5750283f5ef350c0afa416eb2addd"
    assert manifest216["truth_gate_default_state"] == "CLOSED"
    assert manifest216["global_strict_mode_default"] is False
    assert manifest216["dependency_scoped_exact_validation"] is True
    assert manifest216["unchanged_identity_requires_reexecution"] is False
    assert manifest216["runtime_optimization_implementation_claimed"] is False
    assert manifest216["runtime_optimization_roadmap_complete"] is False
    assert manifest216["cxx_mutation_authority"] is False
    assert manifest216["next_pass_to_census"] == 215
    _assert_preflight(declaration216, PASS216_BIND_SYMBOL, preflight_pass216_membrane)


if __name__ == "__main__":
    main()
