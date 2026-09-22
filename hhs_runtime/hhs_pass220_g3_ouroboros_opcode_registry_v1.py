"""Pass 220 I028 rooted G^3/Ouroboros VM81 opcode registry.

The G^3 family is append-only interpreter microcode.  It is not a parallel
execution service and it is not a fifth hydration lane.  Resolution is legal
only inside the inherited Lane 5 dataflow:

648-byte x86_64 carrier -> hydrated raw5184 -> palindromic x/y/z/w RNA ->
Holo4 four-lane candidate state -> mandatory validated constructor graph ->
G^3 candidate microcode -> Hash216 self-solving validation -> canonical
admission when requested -> inverse egress compilation.

The historical Pass 079 direct-ABI registry remains unchanged.
"""
from __future__ import annotations

from typing import Any

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    product_root,
    stable,
)

SCHEMA = "HHS_PASS_220_I028_G3_OPCODE_REGISTRY_V2"
BINDING_SCHEMA = "HHS_NATIVE_OPCODE_BINDING_V1"
RECEIPT_SCHEMA = "HHS_VM81_G3_OPCODE_RECEIPT_V1"
PIPELINE_SCHEMA = "HHS_PASS_220_I028_LANE5_G3_PIPELINE_V1"
AUTHORITY_SCOPE = "LANE5_VM81_G3_OUROBOROS_BOUNDARY_ONLY"

MANDATORY_LANE5_WITNESSES = (
    "I149_RAW648_VM5184_HYDRATED_INGRESS",
    "I015_PALINDROMIC_PHASE",
    "I019_EXACT_5184_CHARACTER_SERIALIZER_WITNESS",
    "LANE5_HOLO4_FOUR_LANE_PREPARED",
    "LANE5_GREEN_PR_CONSTRUCTOR_GRAPH_BOUND",
    "LANE5_CANONICAL_WHITEPAPER_PROOF_GRAPH_BOUND",
    "LANE5_SUCCESSFUL_BENCHMARK_GRAPH_BOUND",
    "LANE5_SERVICE_REGISTRY_GRAPH_BOUND",
    "LANE5_COMMIT_MERGE_LINEAGE_GRAPH_BOUND",
    "LANE5_NO_CANONICAL_MUTATION_AUTHORITY",
)

MANDATORY_CONSTRUCTOR_CLASSES = (
    "GREEN_MERGED_PR_IMPLEMENTATION",
    "GREEN_EXACT_HEAD_WORKFLOW",
    "CANONICAL_CONTRACT",
    "CANONICAL_WHITEPAPER_PROOF",
    "FORMAL_PROOF_RECEIPT",
    "SUCCESSFUL_BENCHMARK_RECEIPT",
    "RESTART_CHECKPOINT",
    "COMMIT_MERGE_LINEAGE",
    "REGISTERED_REPOSITORY_SERVICE",
    "HASH216_VALIDATED_COMPOSITION",
)

PIPELINE_STAGES = (
    "RAW648_X86_64_INGRESS",
    "I149_HYDRATED_RAW5184",
    "PALINDROMIC_IEEE_EXACT_DYADIC_FRAME",
    "ORDERED_XYZW_RNA_5184_TRANSCRIPTION",
    "HOLO4_FOUR_LANE_HYDRATION",
    "LANE5_MANDATORY_CONSTRUCTOR_COMPOSITION",
    "G3_OUROBOROS_VM81_CANDIDATE_MICROCODE",
    "HASH216_SELF_SOLVING_VALIDATION",
    "SIGNED_ENVIRONMENTAL_VM81_ADMISSION_IF_MUTATING",
    "HASH72_HASH216_SUCCESSOR_LINEAGE",
    "INVERSE_EGRESS_COMPILATION",
    "RAW648_X86_64_EGRESS",
)

_ROWS = (
    ("OP_G3_IEEE_INGRESS", 24, "vm81.g3.ieee_ingress", "W_G3_IEEE_INGRESS",
     ("IEEE_RAW_BITS_BOUNDARY",), ("G3_IEEE_BOUNDARY_ADMITTED",)),
    ("OP_G3_PAL_FOLD", 25, "vm81.g3.pal_fold", "W_G3_PAL_FOLD",
     ("G3_IEEE_BOUNDARY_ADMITTED", "I015_PALINDROMIC_PHASE"),
     ("G3_PALINDROME_FORWARD_REVERSE_EQUAL",)),
    ("OP_G3_RNA_TRANSCRIBE", 26, "vm81.g3.rna_transcribe", "W_G3_RNA_TRANSCRIBE",
     ("G3_PALINDROME_FORWARD_REVERSE_EQUAL", "I019_RNA_WINDOW_COMPATIBLE"),
     ("G3_RNA_BIGINT_TYPED_CARRIER",)),
    ("OP_G3_BIND_P4_C4", 27, "vm81.g3.bind_p4_c4", "W_G3_BIND_P4_C4",
     ("G3_RNA_BIGINT_TYPED_CARRIER", "P4_C4_EXACT_CARRIER_EQUALITY"),
     ("G3_P4_C4_BOUND_NO_P2_BRANCH",)),
    ("OP_G3_CONSTRAIN_C5", 28, "vm81.g3.constrain_c5", "W_G3_CONSTRAIN_C5",
     ("G3_P4_C4_BOUND_NO_P2_BRANCH", "LO_SHU_VALUE_5_PRESENT"),
     ("G3_C5_CONSTRAINT_BOUND",)),
    ("OP_G3_CONSTRAIN_C7", 29, "vm81.g3.constrain_c7", "W_G3_CONSTRAIN_C7",
     ("G3_C5_CONSTRAINT_BOUND", "LO_SHU_VALUE_7_PRESENT"),
     ("G3_C7_CONSTRAINT_BOUND",)),
    ("OP_G3_SERIALIZE_A2_C1", 30, "vm81.g3.serialize_a2_c1", "W_G3_SERIALIZE_A2_C1",
     ("G3_C7_CONSTRAINT_BOUND", "LO_SHU_VALUE_1_SEMANTIC_REGISTER"),
     ("G3_C1_BIGINT_SEMANTIC_REGISTER_BOUND",)),
    ("OP_G3_ZERO_SUM_CLOSE", 31, "vm81.g3.zero_sum_close", "W_G3_ZERO_SUM_CLOSE",
     ("G3_C1_BIGINT_SEMANTIC_REGISTER_BOUND", "LO_SHU_ZERO_CENTERED_SUM"),
     ("G3_NUCLEUS_ZERO_SUM_CLOSED",)),
    ("OP_G3_RNA_REVERSE", 32, "vm81.g3.rna_reverse", "W_G3_RNA_REVERSE",
     ("G3_NUCLEUS_ZERO_SUM_CLOSED",), ("G3_RNA_REVERSE_IDENTITY",)),
    ("OP_G3_IEEE_EGRESS", 33, "vm81.g3.ieee_egress", "W_G3_IEEE_EGRESS",
     ("G3_RNA_REVERSE_IDENTITY",), ("IEEE_OUT_EQ_IEEE_IN_RAW_BITS",)),
    ("OP_G3_OUROBOROS", 34, "vm81.g3.ouroboros", "W_G3_OUROBOROS",
     (
         "G3_IEEE_BOUNDARY_ADMITTED",
         "G3_PALINDROME_FORWARD_REVERSE_EQUAL",
         "G3_RNA_BIGINT_TYPED_CARRIER",
         "G3_P4_C4_BOUND_NO_P2_BRANCH",
         "G3_C5_CONSTRAINT_BOUND",
         "G3_C7_CONSTRAINT_BOUND",
         "G3_C1_BIGINT_SEMANTIC_REGISTER_BOUND",
         "I019_EXACT_5184_CHARACTER_SERIALIZER_WITNESS",
         "G3_NUCLEUS_ZERO_SUM_CLOSED",
         "G3_RNA_REVERSE_IDENTITY",
         "IEEE_OUT_EQ_IEEE_IN_RAW_BITS",
     ),
     ("G3_OUROBOROS_ALL_CONSTITUENTS_CLOSED",)),
)


def build_lane5_g3_pipeline_contract() -> dict[str, Any]:
    constructor_graph = {
        "schema": "HHS_PASS_220_I028_MANDATORY_CONSTRUCTOR_GRAPH_V1",
        "classes": list(MANDATORY_CONSTRUCTOR_CLASSES),
        "green_evidence_required": True,
        "dependency_frontier_reuse_required": True,
        "mergeable_branch_visibility": "CANDIDATE_KNOWLEDGE_ONLY",
        "unmerged_canonical_authority": False,
    }
    constructor_graph["constructor_graph_root_hash72"] = product_root(
        "pass220_i028_mandatory_constructor_graph_v1",
        stable(constructor_graph),
    )
    body = {
        "schema": PIPELINE_SCHEMA,
        "stages": list(PIPELINE_STAGES),
        "ingress_bytes": 648,
        "ingress_bits": 5184,
        "vm81_geometry": "81X64",
        "hash72_geometry": "72X72",
        "holo4_lane_count": 4,
        "g3_is_fifth_lane": False,
        "g3_is_parallel_service": False,
        "g3_role": "LANE5_CANDIDATE_MICROCODE_PROFILE",
        "mandatory_constructor_classes": list(MANDATORY_CONSTRUCTOR_CLASSES),
        "mandatory_constructor_graph": stable(constructor_graph),
        "mandatory_constructor_graph_root_hash72": (
            constructor_graph["constructor_graph_root_hash72"]
        ),
        "successful_pr_proof_benchmark_evidence_is_mandatory": True,
        "mergeable_branch_evidence_visibility": "LANE5_BIOS_CANDIDATE_KNOWLEDGE",
        "unmerged_evidence_canonical_authority": False,
        "lane5_canonical_vm81_mutation_authority": False,
        "lane5_hash72_mint_authority": False,
        "lane5_hash216_canonical_mint_authority": False,
        "external_egress_requires_hash216_self_solving_validation": True,
        "candidate_ieee_egress_is_external_emission": False,
    }
    body["pipeline_root_hash72"] = product_root(
        "pass220_i028_lane5_g3_pipeline_v1", stable(body)
    )
    return stable(body)


def _binding(
    enum_symbol: str,
    opcode_value: int,
    semantic_operation_identity: str,
    witness_class: str,
    pre: tuple[str, ...],
    post: tuple[str, ...],
) -> dict[str, Any]:
    required_pre = tuple(dict.fromkeys((*MANDATORY_LANE5_WITNESSES, *pre)))
    body = {
        "schema": BINDING_SCHEMA,
        "registry_schema": SCHEMA,
        "binding_kind": "LANE5_MEDIATED_VM81_INTERPRETER_MICROCODE",
        "native_opcode": enum_symbol,
        "numeric_opcode": opcode_value,
        "semantic_operation_identity": semantic_operation_identity,
        "abi_symbol": f"HARMONICODE_VM_RUNTIME.c::{enum_symbol}",
        "abi_disposition": "INTERNAL_VM81_OPCODE_APPEND_ONLY",
        "input_schema": {
            "type": "lane5_hydrated_exact_vm81_candidate",
            "raw_ingress_bytes": 648,
            "hydrated_width_bits": 5184,
            "ieee_boundary_representation": "RAW_UINT64_BITS_ONLY",
            "floating_arithmetic_authority": False,
        },
        "output_schema": {
            "type": "lane5_candidate_microcode_witness",
            "receipt_schema": RECEIPT_SCHEMA,
            "external_egress": False,
        },
        "memory_ownership": "VM81_OWNS_INTERNAL_G3_STATE",
        "buffer_bounds": "I149_RAW648_TO_VM81_81X64_FIXED_WIDTH",
        "mutation_class": "CANDIDATE_ONLY_G3_VM81_TRANSITION",
        "authority_scope": AUTHORITY_SCOPE,
        "lease_requirements": [
            "TASK_BOUND",
            "SOURCE_SCOPED",
            "OPERATION_SCOPED",
            "SEQUENCE_BOUNDED",
        ],
        "pre_state_witness_requirements": list(required_pre),
        "post_state_witness_requirements": list(post),
        "witness_class": witness_class,
        "failure_semantics": [
            "REJECT_IF_LANE5_NOT_MEDIATED",
            "REJECT_IF_HOLO4_NOT_PREPARED",
            "REJECT_IF_MANDATORY_CONSTRUCTOR_GRAPH_NOT_BOUND",
            "REJECT_NO_CANONICAL_SUCCESSOR",
            "REJECT_NO_AUTHORITATIVE_RECEIPT",
            "REJECT_NO_LOGICAL_TIME_ADVANCE",
            "REJECT_LEDGER_FROZEN",
        ],
        "receipt_schema": RECEIPT_SCHEMA,
        "compiler_may_synthesize": False,
        "ieee_is_boundary_only": True,
        "bigint_physical_5184_character_offset_resolved": False,
        "bigint_semantic_register": "LO_SHU_VALUE_1_A2",
        "bigint_native_cell_is_complete_serialized_object": False,
        "authoritative_bigint_exactness_requirement": (
            "I019_EXACT_5184_CHARACTER_SERIALIZER_WITNESS"
        ),
        "lane5_pipeline_required": True,
        "holo4_four_lane_hydration_required": True,
        "four_lane_hydration_relation": (
            "MANDATORY_COORDINATED_TYPED_VIEW_SINGLE_VM81_CANDIDATE"
        ),
        "multimodal_geometry_relation": (
            "LANE5_HASH216_KNOWLEDGE_GRAPH_HYDRATION_DIMENSION"
        ),
        "successful_history_relation": (
            "GREEN_PR_PROOF_BENCHMARKS_ARE_MANDATORY_CONSTRUCTORS"
        ),
        "candidate_ieee_egress_is_external_emission": False,
        "external_egress_requirement": (
            "HASH216_SELF_SOLVING_VALIDATION_THEN_INVERSE_EGRESS_COMPILATION"
        ),
    }
    body["binding_root_hash72"] = product_root(
        "pass220_i028_g3_opcode_binding_v2", stable(body)
    )
    return stable(body)


def build_g3_opcode_registry() -> dict[str, Any]:
    entries = [_binding(*row) for row in _ROWS]
    pipeline = build_lane5_g3_pipeline_contract()
    result = {
        "schema": SCHEMA,
        "binding_schema": BINDING_SCHEMA,
        "parent_binding_style": "PASS_079_ROOTED_OPCODE_BINDING",
        "historical_pass079_registry_mutated": False,
        "opcode_range": [24, 34],
        "registered_opcodes": len(entries),
        "entries": entries,
        "policy": (
            "NO_DIRECT_G3_EXECUTION_OUTSIDE_LANE5;"
            "NO_NAME_SIGNATURE_OR_FUSED_SHORTCUT_AUTHORITY;"
            "EVERY_PRIMITIVE_HAS_DISTINCT_ROOT_AND_WITNESS"
        ),
        "lane5_bios_relation": "MANDATORY_GLOBAL_5184_CONSTRUCTOR_GRAPH",
        "pipeline": pipeline,
        "four_lane_hydration_authority": False,
        "graphics_projection_authority": False,
    }
    result["registry_root_hash72"] = product_root(
        "pass220_i028_g3_opcode_registry_v2", stable(result)
    )
    return stable(result)


def resolve_g3_opcode(opcode: str, request: dict[str, Any]) -> dict[str, Any]:
    registry = build_g3_opcode_registry()
    matches = [entry for entry in registry["entries"] if entry["native_opcode"] == opcode]
    if len(matches) != 1:
        raise ValueError("REJECT_UNREGISTERED_G3_OPCODE")
    binding = matches[0]
    if request.get("binding_root_hash72") != binding["binding_root_hash72"]:
        raise ValueError("REJECT_G3_BINDING_ROOT_MISMATCH")
    if request.get("authority_scope") != binding["authority_scope"]:
        raise ValueError("REJECT_G3_AUTHORITY_SCOPE_MISMATCH")
    if request.get("lease_status") != "ACTIVE_VALIDATED":
        raise ValueError("REJECT_G3_LEASE_NOT_ACTIVE_VALIDATED")
    required_status = {
        "vm81_lane_binding_status": "BOUND_WITNESSED",
        "raw648_hydration_status": "I149_BOUND_WITNESSED",
        "holo4_status": "FOUR_LANES_PREPARED",
        "lane5_bios_status": "MEDIATED",
        "constructor_graph_status": "MANDATORY_GREEN_HISTORY_BOUND",
    }
    for key, expected in required_status.items():
        if request.get(key) != expected:
            raise ValueError(f"REJECT_G3_{key.upper()}")

    pipeline = registry["pipeline"]
    if request.get("lane5_pipeline_root_hash72") != pipeline["pipeline_root_hash72"]:
        raise ValueError("REJECT_G3_LANE5_PIPELINE_ROOT_MISMATCH")
    if (
        request.get("constructor_graph_root_hash72")
        != pipeline["mandatory_constructor_graph_root_hash72"]
    ):
        raise ValueError("REJECT_G3_CONSTRUCTOR_GRAPH_ROOT_MISMATCH")

    return stable({
        "decision": "RESOLVED_FOR_LANE5_MEDIATED_VM81_CANDIDATE_MICROCODE",
        "native_opcode": opcode,
        "numeric_opcode": binding["numeric_opcode"],
        "binding_root_hash72": binding["binding_root_hash72"],
        "witness_class": binding["witness_class"],
        "lane5_pipeline_root_hash72": pipeline["pipeline_root_hash72"],
        "constructor_graph_root_hash72": (
            pipeline["mandatory_constructor_graph_root_hash72"]
        ),
        "canonical_mutation_authority": False,
        "external_egress_authority": False,
        "invocation_not_executed": True,
    })
