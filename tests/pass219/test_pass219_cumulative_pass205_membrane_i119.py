from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i119_pass205 import (
    COMPLETION_RECEIPT_BLOB,
    PASS205_BIND_SYMBOL,
    PASS205_CENSUS_CLASSIFICATION,
    REQUIRED_OPERATIONS,
    pass205_membrane_manifest,
    pass205_membrane_source_evidence,
    pass205_surface_declaration,
    preflight_pass205_membrane,
    validate_pass205_accelerator_boundary,
    validate_pass205_geometry,
    validate_pass205_hash72_lineage,
    validate_pass205_production_identity,
    validate_pass205_vm81_authority,
    validate_pass206_successor_binding,
)


def main() -> None:
    source = pass205_membrane_source_evidence()
    assert source["grounding_baseline"] == "918121aeb6d1c55aa8fbd5d60b15f03c4eb22423"
    assert source["implementation_merge"] == "7be753b36d5b4c7a370b6435ddb027b6b05965d8"
    assert source["closure_merge"] == "c717ab9e0437e1f407bbd3b22ed1fdd14bcd29b6"
    assert source["completion_evidence_merge"] == "8e6cded890b86e36a2acd2162acf91d1cb4331ac"
    assert source["completion_receipt_blob"] == COMPLETION_RECEIPT_BLOB
    assert len(source["terminal_receipt_hash72"]) == 72
    assert source["native_freeze_entry"]["semantic_category"] == "SINGLETON_VM81_CONTINUATION_IMPLEMENTATION"
    assert source["bridge_freeze_entry"]["semantic_category"] == "PYTHON_NATIVE_AUTHORITY_BRIDGE"
    assert "singleton_vm81_admission" in source["bridge_freeze_entry"]["receipt_replay_obligations"]
    assert source["pass206_successor"]["contract"]["pass"] == 206

    declaration = pass205_surface_declaration()
    assert declaration["surface_id"] == "validator:pass219.inherited.pass205.deterministic-continuation"
    assert declaration["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert declaration["persistence_policy"] == "INHERITED_EVIDENCE_IDENTITY_ONLY"
    assert tuple(declaration["declared_operations"]) == REQUIRED_OPERATIONS
    assert PASS205_BIND_SYMBOL in declaration["validators"]

    manifest = pass205_membrane_manifest()
    assert manifest["pass_number"] == 205
    assert manifest["classification"] == "WIRED"
    assert manifest["census_classification"] == PASS205_CENSUS_CLASSIFICATION == "MISSING_MEMBRANE_EXPOSURE"
    assert manifest["canonical_mutation_authority"] == "VM81_KERNEL"
    assert manifest["canonical_mutation_authority_count"] == 1
    assert manifest["canonical_hash72_commit_stream_count"] == 1
    assert manifest["vm5184_state_bits"] == 5184
    assert manifest["g243_control_count"] == 243
    assert manifest["q_address_count"] == 1259712
    assert manifest["projection_channel_count"] == 32
    assert manifest["q_bijection_bound"] is True
    assert manifest["exact_sparse_full_equivalence_bound"] is True
    assert manifest["exact_retrieval_rerank_bound"] is True
    assert manifest["accelerator_candidate_only"] is True
    assert manifest["accelerator_may_commit_hash72"] is False
    assert manifest["physical_gpu_execution_claimed"] is False
    assert manifest["pass206_successor_bound"] is True
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["pass219_new_persistence_authority"] is False
    assert manifest["pass219_new_hash72_clock"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False
    assert manifest["next_pass_to_census"] == 204

    assert validate_pass205_production_identity()["ok"] is True
    authority = validate_pass205_vm81_authority()
    assert authority["ok"] is True
    assert authority["canonical_mutation_authority"] == "VM81_KERNEL"
    assert authority["canonical_mutation_authority_count"] == 1
    lineage = validate_pass205_hash72_lineage()
    assert lineage["ok"] is True
    assert lineage["canonical_hash72_commit_stream_count"] == 1
    assert lineage["hash216_mutation_authority"] is False
    geometry = validate_pass205_geometry()
    assert geometry == {
        "ok": True,
        "cell_count": 81,
        "state_bits": 5184,
        "control_count": 243,
        "q_address_count": 1259712,
        "projection_channel_count": 32,
    }
    accelerator = validate_pass205_accelerator_boundary()
    assert accelerator["ok"] is True
    assert accelerator["accelerator_candidate_only"] is True
    assert accelerator["accelerator_may_commit_hash72"] is False
    assert accelerator["physical_gpu_execution_claimed"] is False
    assert validate_pass206_successor_binding() == {
        "ok": True,
        "successor_pass": 206,
        "successor_preserves_single_vm81_authority": True,
    }

    preflight = preflight_pass205_membrane()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(REQUIRED_OPERATIONS)
    assert all(row.get("ok") is True for row in preflight["operations"])


if __name__ == "__main__":
    main()
