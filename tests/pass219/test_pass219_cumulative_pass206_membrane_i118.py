from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i118_pass206 import (
    COMPLETION_RECEIPT_SHA256,
    PASS206_BIND_SYMBOL,
    REQUIRED_OPERATIONS,
    pass206_membrane_manifest,
    pass206_membrane_source_evidence,
    pass206_surface_declaration,
    preflight_pass206_membrane,
    validate_pass206_core_freeze,
    validate_pass206_development_completion,
    validate_pass206_repair_lineage,
    validate_pass207_successor_binding,
)


def main() -> None:
    source = pass206_membrane_source_evidence()
    assert source["grounding_baseline"] == "918121aeb6d1c55aa8fbd5d60b15f03c4eb22423"
    assert source["development_completion_head"] == "16d17c1db690116fdc5f5b63ef7a097548685885"
    assert source["completion_receipt_sha256"] == COMPLETION_RECEIPT_SHA256
    assert source["freeze_manifest"]["entry_count"] == 10
    assert source["repair_lineage"]["approved_successor_count"] == 1
    assert source["validation_matrix"]["stage"] == "DEVELOPMENT_COMPLETE_CANONICAL_MAIN_VERIFICATION_PENDING"
    assert source["completion_receipt"]["canonical_main"]["verified"] is False
    assert source["live_enforcement"]["ok"] is True
    assert source["successor_pass207"]["contract"]["pass"] == 207

    declaration = pass206_surface_declaration()
    assert declaration["surface_id"] == "validator:pass219.inherited.pass206.cumulative-enforcement"
    assert declaration["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert declaration["persistence_policy"] == "INHERITED_EVIDENCE_IDENTITY_ONLY"
    assert tuple(declaration["declared_operations"]) == REQUIRED_OPERATIONS
    assert PASS206_BIND_SYMBOL in declaration["validators"]

    manifest = pass206_membrane_manifest()
    assert manifest["pass_number"] == 206
    assert manifest["classification"] == "WIRED"
    assert manifest["frozen_core_count"] == 10
    assert manifest["approved_successor_count"] == 1
    assert manifest["canonical_mutation_authority"] == "VM81_KERNEL"
    assert manifest["canonical_mutation_authority_count"] == 1
    assert manifest["canonical_hash72_commit_stream_count"] == 1
    assert manifest["enforcement_admitted"] is True
    assert manifest["development_implementation_complete"] is True
    assert manifest["development_final_replay_complete"] is True
    assert manifest["development_completion_receipt_emitted"] is True
    assert manifest["canonical_main_verified"] is False
    assert manifest["canonical_main_promotion_authorized"] is False
    assert manifest["canonical_completion_claimed"] is False
    assert manifest["pass207_successor_bound"] is True
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["pass219_new_persistence_authority"] is False
    assert manifest["pass219_new_hash72_clock"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False
    assert manifest["next_pass_to_census"] == 205

    assert validate_pass206_core_freeze() == {"ok": True, "frozen_core_count": 10}
    assert validate_pass206_repair_lineage() == {"ok": True, "approved_successor_count": 1}
    assert validate_pass206_development_completion() == {"ok": True, "canonical_main_verified": False}
    assert validate_pass207_successor_binding() == {"ok": True, "successor_pass": 207}

    preflight = preflight_pass206_membrane()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(REQUIRED_OPERATIONS)
    assert all(row.get("ok") is True for row in preflight["operations"])


if __name__ == "__main__":
    main()
