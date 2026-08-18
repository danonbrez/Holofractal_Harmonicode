from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import (
    BIND_SYMBOL,
    CLASSIFICATION,
    PASS217_BIND_SYMBOL,
    PASS217_CAPABILITIES,
    PASS217_CLASSIFICATION,
    PASS217_NUMBER,
    PASS218_CAPABILITIES,
    PASS_NUMBER,
    pass217_membrane_manifest,
    pass217_membrane_source_evidence,
    pass217_membrane_surface_declaration,
    pass218_membrane_manifest,
    pass218_membrane_surface_declaration,
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


if __name__ == "__main__":
    main()
