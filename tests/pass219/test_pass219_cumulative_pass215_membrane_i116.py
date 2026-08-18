from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass215 import (
    PASS215_BIND_SYMBOL,
    PASS215_CAPABILITIES,
    PASS215_CLASSIFICATION,
    PASS215_NUMBER,
    pass215_membrane_manifest,
    pass215_membrane_source_evidence,
    pass215_membrane_surface_declaration,
    preflight_pass215_membrane,
)


def main() -> None:
    evidence = pass215_membrane_source_evidence()
    contract = evidence["contract"]
    source = contract["source_execution"]
    completion = contract["pass_completion"]
    constraints = contract["constraints"]

    assert evidence["final_head"] == "b85ea7c340976a20a78f9c7d8d89a688a1b4f8fc"
    assert evidence["final_tree"] == "17127e80a3f4852aeaedd1b807971fb4b4fba229"
    assert evidence["main_merge"] == "cc7a0d67d7d9e4bd1e800f62d5ef577cb4ab1086"
    assert evidence["validation_run"] == 31325831364
    assert evidence["validation_job"] == 93275935886
    assert evidence["artifact_sha256"] == "9e71ff3f48cd4da24c34854f8eadfa57f26d7c6ef5bddd1026c89e2ace63bf55"
    assert source["cumulative_test_count"] == 240
    assert source["selected_token_ids"] == [450, 6575, 471, 528, 2827, 322, 278]
    assert source["termination_reason"] == "MAX_NEW_TOKENS"
    assert source["reused_unique_chunk_count"] == 36
    assert source["reused_compressed_blob_bytes"] == 28375966
    assert source["incremental_later_compressed_blob_bytes"] == 125510422
    assert source["shared_store_savings_bytes"] == 28375966
    assert source["cross_process_replay"] is True
    assert source["semantic_exactness"] is True
    assert completion["pass215_contracted_benchmark_implementation_complete"] is True
    assert completion["bounded_profile_only"] is True
    assert completion["broader_generation_authority_promoted"] is False
    assert constraints["output_projection_pruning_executed"] is False
    assert constraints["probabilistic_sampling_executed"] is False
    assert constraints["canonical_float_interpretation_performed"] is False
    assert constraints["transport_compression_promoted_to_numerical_authority"] is False
    assert constraints["runtime_mutation_authority_promoted"] is False
    assert constraints["canonical_mutation_authorized"] is False

    declaration = pass215_membrane_surface_declaration()
    manifest = pass215_membrane_manifest()
    assert PASS215_NUMBER == 215
    assert PASS215_CLASSIFICATION == "WIRED"
    assert declaration["symbol"] == PASS215_BIND_SYMBOL
    assert declaration["declared_operations"] == [PASS215_BIND_SYMBOL]
    assert declaration["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert declaration["persistence_policy"] == "INHERITED_TERMINAL_CLOSURE_IDENTITY_ONLY"
    assert manifest["classification"] == "WIRED"
    assert tuple(manifest["capabilities"]) == PASS215_CAPABILITIES
    assert manifest["bounded_profile_only"] is True
    assert manifest["broader_generation_authority_promoted"] is False
    assert manifest["output_projection_pruning_executed"] is False
    assert manifest["probabilistic_sampling_executed"] is False
    assert manifest["canonical_float_interpretation_performed"] is False
    assert manifest["transport_compression_numerical_authority"] is False
    assert manifest["runtime_mutation_authority_promoted"] is False
    assert manifest["canonical_mutation_authorized"] is False
    assert manifest["historical_pass216_status_in_pass215_record"] == "RESERVED_NUMBER_NO_PASS"
    assert manifest["later_pass216_alignment_authority_present"] is True
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["next_pass_to_census"] == 214

    cache = {}
    first = preflight_pass215_membrane(cache=cache)
    second = preflight_pass215_membrane(cache=cache)
    assert first["ok"] is True
    assert second["ok"] is True
    assert first["status"] == "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"
    assert first["surface_id"] == declaration["surface_id"]
    assert first["operation"] == PASS215_BIND_SYMBOL
    assert first["composition_plan"]["composition_allowed"] is True
    assert first["composition_plan"]["pipeline"]["execution_adapter"] == PASS215_BIND_SYMBOL
    assert first["composition_plan"]["pipeline"]["handwired"] is False
    assert first["composition_plan"]["pipeline"]["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert second["cache"]["cache_hit"] is True


if __name__ == "__main__":
    main()
