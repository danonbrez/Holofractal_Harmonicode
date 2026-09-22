from hhs_runtime.hhs_pass220_g3_ouroboros_opcode_registry_v1 import (
    AUTHORITY_SCOPE,
    MANDATORY_CONSTRUCTOR_CLASSES,
    MANDATORY_LANE5_WITNESSES,
    PIPELINE_STAGES,
    build_g3_opcode_registry,
    build_lane5_g3_pipeline_contract,
    resolve_g3_opcode,
)


def test_g3_registry_is_append_only_24_through_34():
    registry = build_g3_opcode_registry()
    entries = registry["entries"]
    assert registry["registered_opcodes"] == 11
    assert [entry["numeric_opcode"] for entry in entries] == list(range(24, 35))
    assert entries[0]["native_opcode"] == "OP_G3_IEEE_INGRESS"
    assert entries[-1]["native_opcode"] == "OP_G3_OUROBOROS"
    assert registry["historical_pass079_registry_mutated"] is False


def test_each_g3_opcode_has_distinct_root_and_witness():
    entries = build_g3_opcode_registry()["entries"]
    roots = [entry["binding_root_hash72"] for entry in entries]
    witnesses = [entry["witness_class"] for entry in entries]
    assert len(set(roots)) == 11
    assert len(set(witnesses)) == 11
    assert all(len(root) == 72 for root in roots)
    assert all(entry["compiler_may_synthesize"] is False for entry in entries)


def test_lane5_full_648_to_hash216_to_egress_pipeline_is_mandatory():
    pipeline = build_lane5_g3_pipeline_contract()
    assert pipeline["ingress_bytes"] == 648
    assert pipeline["ingress_bits"] == 5184
    assert pipeline["vm81_geometry"] == "81X64"
    assert pipeline["hash72_geometry"] == "72X72"
    assert pipeline["holo4_lane_count"] == 4
    assert pipeline["g3_is_fifth_lane"] is False
    assert pipeline["g3_is_parallel_service"] is False
    assert pipeline["g3_role"] == "LANE5_CANDIDATE_MICROCODE_PROFILE"
    assert pipeline["stages"] == list(PIPELINE_STAGES)
    assert pipeline["stages"][0] == "RAW648_X86_64_INGRESS"
    assert "HASH216_SELF_SOLVING_VALIDATION" in pipeline["stages"]
    assert pipeline["stages"][-1] == "RAW648_X86_64_EGRESS"
    assert pipeline["external_egress_requires_hash216_self_solving_validation"] is True
    assert pipeline["candidate_ieee_egress_is_external_emission"] is False


def test_successful_pr_benchmarks_and_proofs_are_mandatory_lane5_constructors():
    pipeline = build_lane5_g3_pipeline_contract()
    required = set(MANDATORY_CONSTRUCTOR_CLASSES)
    assert pipeline["successful_pr_proof_benchmark_evidence_is_mandatory"] is True
    assert set(pipeline["mandatory_constructor_classes"]) == required
    assert len(pipeline["pipeline_root_hash72"]) == 72
    assert len(pipeline["mandatory_constructor_graph_root_hash72"]) == 72
    assert (
        pipeline["mandatory_constructor_graph"]["constructor_graph_root_hash72"]
        == pipeline["mandatory_constructor_graph_root_hash72"]
    )
    assert {
        "GREEN_MERGED_PR_IMPLEMENTATION",
        "GREEN_EXACT_HEAD_WORKFLOW",
        "CANONICAL_CONTRACT",
        "CANONICAL_WHITEPAPER_PROOF",
        "FORMAL_PROOF_RECEIPT",
        "SUCCESSFUL_BENCHMARK_RECEIPT",
        "REGISTERED_REPOSITORY_SERVICE",
        "COMMIT_MERGE_LINEAGE",
        "HASH216_VALIDATED_COMPOSITION",
    } <= required
    assert pipeline["mergeable_branch_evidence_visibility"] == (
        "LANE5_BIOS_CANDIDATE_KNOWLEDGE"
    )
    assert pipeline["unmerged_evidence_canonical_authority"] is False


def test_ieee_bigint_and_authority_boundaries_are_explicit():
    entries = build_g3_opcode_registry()["entries"]
    assert all(entry["ieee_is_boundary_only"] is True for entry in entries)
    assert all(
        entry["input_schema"]["floating_arithmetic_authority"] is False
        for entry in entries
    )
    assert all(entry["input_schema"]["raw_ingress_bytes"] == 648 for entry in entries)
    assert all(entry["input_schema"]["hydrated_width_bits"] == 5184 for entry in entries)
    assert all(
        entry["bigint_physical_5184_character_offset_resolved"] is False
        for entry in entries
    )
    assert all(
        entry["bigint_semantic_register"] == "LO_SHU_VALUE_1_A2"
        for entry in entries
    )
    assert all(
        entry["authoritative_bigint_exactness_requirement"]
        == "I019_EXACT_5184_CHARACTER_SERIALIZER_WITNESS"
        for entry in entries
    )
    assert all(entry["mutation_class"] == "CANDIDATE_ONLY_G3_VM81_TRANSITION" for entry in entries)
    assert all(entry["candidate_ieee_egress_is_external_emission"] is False for entry in entries)


def test_every_opcode_requires_lane5_holo4_green_constructor_context():
    entries = build_g3_opcode_registry()["entries"]
    required = set(MANDATORY_LANE5_WITNESSES)
    for entry in entries:
        assert required <= set(entry["pre_state_witness_requirements"])
        assert entry["lane5_pipeline_required"] is True
        assert entry["holo4_four_lane_hydration_required"] is True
        assert entry["four_lane_hydration_relation"] == (
            "MANDATORY_COORDINATED_TYPED_VIEW_SINGLE_VM81_CANDIDATE"
        )
        assert entry["successful_history_relation"] == (
            "GREEN_PR_PROOF_BENCHMARKS_ARE_MANDATORY_CONSTRUCTORS"
        )
        assert entry["external_egress_requirement"] == (
            "HASH216_SELF_SOLVING_VALIDATION_THEN_INVERSE_EGRESS_COMPILATION"
        )


def test_fused_opcode_requires_all_constituent_witnesses():
    fused = build_g3_opcode_registry()["entries"][-1]
    required = fused["pre_state_witness_requirements"]
    assert "G3_P4_C4_BOUND_NO_P2_BRANCH" in required
    assert "G3_C5_CONSTRAINT_BOUND" in required
    assert "G3_C7_CONSTRAINT_BOUND" in required
    assert "G3_C1_BIGINT_SEMANTIC_REGISTER_BOUND" in required
    assert "I019_EXACT_5184_CHARACTER_SERIALIZER_WITNESS" in required
    assert "G3_NUCLEUS_ZERO_SUM_CLOSED" in required
    assert "IEEE_OUT_EQ_IEEE_IN_RAW_BITS" in required


def test_resolver_requires_root_authority_lease_and_complete_lane5_context():
    registry = build_g3_opcode_registry()
    binding = registry["entries"][0]
    pipeline = registry["pipeline"]
    good = {
        "binding_root_hash72": binding["binding_root_hash72"],
        "authority_scope": AUTHORITY_SCOPE,
        "lease_status": "ACTIVE_VALIDATED",
        "vm81_lane_binding_status": "BOUND_WITNESSED",
        "raw648_hydration_status": "I149_BOUND_WITNESSED",
        "holo4_status": "FOUR_LANES_PREPARED",
        "lane5_bios_status": "MEDIATED",
        "constructor_graph_status": "MANDATORY_GREEN_HISTORY_BOUND",
        "lane5_pipeline_root_hash72": pipeline["pipeline_root_hash72"],
        "constructor_graph_root_hash72": (
            pipeline["mandatory_constructor_graph_root_hash72"]
        ),
    }
    resolved = resolve_g3_opcode(binding["native_opcode"], good)
    assert resolved["numeric_opcode"] == 24
    assert resolved["witness_class"] == "W_G3_IEEE_INGRESS"
    assert resolved["canonical_mutation_authority"] is False
    assert resolved["external_egress_authority"] is False
    assert resolved["lane5_pipeline_root_hash72"] == pipeline["pipeline_root_hash72"]
    assert resolved["constructor_graph_root_hash72"] == (
        pipeline["mandatory_constructor_graph_root_hash72"]
    )
    assert resolved["decision"] == (
        "RESOLVED_FOR_LANE5_MEDIATED_VM81_CANDIDATE_MICROCODE"
    )

    for key in (
        "binding_root_hash72",
        "authority_scope",
        "lease_status",
        "vm81_lane_binding_status",
        "raw648_hydration_status",
        "holo4_status",
        "lane5_bios_status",
        "constructor_graph_status",
        "lane5_pipeline_root_hash72",
        "constructor_graph_root_hash72",
    ):
        request = dict(good)
        request[key] = "bad"
        try:
            resolve_g3_opcode(binding["native_opcode"], request)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{key} shortcut unexpectedly resolved")


def test_multimodal_and_four_lane_surfaces_are_lane5_dimensions_not_authorities():
    registry = build_g3_opcode_registry()
    assert registry["lane5_bios_relation"] == "MANDATORY_GLOBAL_5184_CONSTRUCTOR_GRAPH"
    assert registry["four_lane_hydration_authority"] is False
    assert registry["graphics_projection_authority"] is False
    for entry in registry["entries"]:
        assert entry["multimodal_geometry_relation"] == (
            "LANE5_HASH216_KNOWLEDGE_GRAPH_HYDRATION_DIMENSION"
        )


def test_runtime_os_surface_is_projection_and_lane5_membrane_is_non_bypassable():
    pipeline = build_lane5_g3_pipeline_contract()
    assert pipeline["runtime_os_surface_role"] == (
        "LINEAR_VALIDATION_CONSTRUCTION_PROJECTION"
    )
    assert pipeline["lane5_bios_system_role"] == (
        "GLOBAL_ORTHOGONAL_CONTROL_CONSTRAINT_MANIFOLD"
    )
    assert pipeline["linux_api_abi_ingress_requires_lane5_zero_bypass"] is True
    assert pipeline["cpp_rna_cell_wall_required_before_canonical_vm81"] is True
    assert (
        pipeline[
            "pqc_environmental_instruction_membrane_required_before_canonical_vm81"
        ]
        is True
    )
    assert pipeline["direct_linux_environmental_opcode_canonical_authority"] is False
    assert pipeline["direct_public_abi_vm81_commit_authority"] is False
    assert pipeline["legacy_low_level_vm81_public_dynamic_symbol_allowed"] is False
    assert pipeline["canonical_vm81_execution_requires_inherited_pass219_membrane"] is True
    assert "PASS219_CPP_RNA_CELL_WALL" in pipeline["stages"]
    assert "PASS219_PQC_ENVIRONMENTAL_INSTRUCTION_MEMBRANE" in pipeline["stages"]
    assert pipeline["canonical_handoff_requirements"] == [
        "PASS219_CPP_RNA_CELL_WALL_PATH_REQUIRED",
        "VALID_PARENT_HASH216_ARRAY_REQUIRED",
        "PASS219_PQC_PROVENANCE_REQUIRED",
        "SIGNED_ENVIRONMENTAL_VM81_ADMISSION_REQUIRED",
        "VALID_CHILD_HASH216_ARRAY_REQUIRED",
    ]
