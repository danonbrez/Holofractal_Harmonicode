"""Pass 220 I028 rooted G^3/Ouroboros VM81 opcode registry.

This is an additive Pass-079-style binding surface for the interpreter opcodes
24..34.  It does not alter the historical Pass 079 direct-ABI registry count.
"""
from __future__ import annotations

from typing import Any

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    product_root,
    stable,
)

SCHEMA = "HHS_PASS_220_I028_G3_OPCODE_REGISTRY_V1"
BINDING_SCHEMA = "HHS_NATIVE_OPCODE_BINDING_V1"
RECEIPT_SCHEMA = "HHS_VM81_G3_OPCODE_RECEIPT_V1"
AUTHORITY_SCOPE = "LANE5_VM81_G3_OUROBOROS_BOUNDARY_ONLY"

_ROWS = (
    (
        "OP_G3_IEEE_INGRESS", 24, "vm81.g3.ieee_ingress",
        "W_G3_IEEE_INGRESS",
        ("IEEE_RAW_BITS_BOUNDARY",),
        ("G3_IEEE_BOUNDARY_ADMITTED",),
    ),
    (
        "OP_G3_PAL_FOLD", 25, "vm81.g3.pal_fold",
        "W_G3_PAL_FOLD",
        ("G3_IEEE_BOUNDARY_ADMITTED", "I015_PALINDROMIC_PHASE"),
        ("G3_PALINDROME_FORWARD_REVERSE_EQUAL",),
    ),
    (
        "OP_G3_RNA_TRANSCRIBE", 26, "vm81.g3.rna_transcribe",
        "W_G3_RNA_TRANSCRIBE",
        ("G3_PALINDROME_FORWARD_REVERSE_EQUAL", "I019_RNA_WINDOW_COMPATIBLE"),
        ("G3_RNA_BIGINT_TYPED_CARRIER",),
    ),
    (
        "OP_G3_BIND_P4_C4", 27, "vm81.g3.bind_p4_c4",
        "W_G3_BIND_P4_C4",
        ("G3_RNA_BIGINT_TYPED_CARRIER", "P4_C4_EXACT_CARRIER_EQUALITY"),
        ("G3_P4_C4_BOUND_NO_P2_BRANCH",),
    ),
    (
        "OP_G3_CONSTRAIN_C5", 28, "vm81.g3.constrain_c5",
        "W_G3_CONSTRAIN_C5",
        ("G3_P4_C4_BOUND_NO_P2_BRANCH", "LO_SHU_VALUE_5_PRESENT"),
        ("G3_C5_CONSTRAINT_BOUND",),
    ),
    (
        "OP_G3_CONSTRAIN_C7", 29, "vm81.g3.constrain_c7",
        "W_G3_CONSTRAIN_C7",
        ("G3_C5_CONSTRAINT_BOUND", "LO_SHU_VALUE_7_PRESENT"),
        ("G3_C7_CONSTRAINT_BOUND",),
    ),
    (
        "OP_G3_SERIALIZE_A2_C1", 30, "vm81.g3.serialize_a2_c1",
        "W_G3_SERIALIZE_A2_C1",
        ("G3_C7_CONSTRAINT_BOUND", "LO_SHU_VALUE_1_SEMANTIC_REGISTER"),
        ("G3_C1_BIGINT_SEMANTIC_REGISTER_BOUND",),
    ),
    (
        "OP_G3_ZERO_SUM_CLOSE", 31, "vm81.g3.zero_sum_close",
        "W_G3_ZERO_SUM_CLOSE",
        ("G3_C1_BIGINT_SEMANTIC_REGISTER_BOUND", "LO_SHU_ZERO_CENTERED_SUM"),
        ("G3_NUCLEUS_ZERO_SUM_CLOSED",),
    ),
    (
        "OP_G3_RNA_REVERSE", 32, "vm81.g3.rna_reverse",
        "W_G3_RNA_REVERSE",
        ("G3_NUCLEUS_ZERO_SUM_CLOSED",),
        ("G3_RNA_REVERSE_IDENTITY",),
    ),
    (
        "OP_G3_IEEE_EGRESS", 33, "vm81.g3.ieee_egress",
        "W_G3_IEEE_EGRESS",
        ("G3_RNA_REVERSE_IDENTITY",),
        ("IEEE_OUT_EQ_IEEE_IN_RAW_BITS",),
    ),
    (
        "OP_G3_OUROBOROS", 34, "vm81.g3.ouroboros",
        "W_G3_OUROBOROS",
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
        ("G3_OUROBOROS_ALL_CONSTITUENTS_CLOSED",),
    ),
)


def _binding(
    enum_symbol: str,
    opcode_value: int,
    semantic_operation_identity: str,
    witness_class: str,
    pre: tuple[str, ...],
    post: tuple[str, ...],
) -> dict[str, Any]:
    body = {
        "schema": BINDING_SCHEMA,
        "registry_schema": SCHEMA,
        "binding_kind": "VM81_INTERPRETER_OPCODE",
        "native_opcode": enum_symbol,
        "numeric_opcode": opcode_value,
        "semantic_operation_identity": semantic_operation_identity,
        "abi_symbol": f"HARMONICODE_VM_RUNTIME.c::{enum_symbol}",
        "abi_disposition": "INTERNAL_VM81_OPCODE_APPEND_ONLY",
        "input_schema": {
            "type": "exact_vm81_cell_carriers",
            "ieee_boundary_representation": "RAW_UINT64_BITS_ONLY",
            "floating_arithmetic_authority": False,
        },
        "output_schema": {
            "type": "exact_vm81_cell_carrier_and_witness",
            "receipt_schema": RECEIPT_SCHEMA,
        },
        "memory_ownership": "VM81_OWNS_INTERNAL_G3_STATE",
        "buffer_bounds": "VM81_81X64_FIXED_WIDTH",
        "mutation_class": "BOUNDED_G3_VM81_TRANSITION",
        "authority_scope": AUTHORITY_SCOPE,
        "lease_requirements": [
            "TASK_BOUND",
            "SOURCE_SCOPED",
            "OPERATION_SCOPED",
            "SEQUENCE_BOUNDED",
        ],
        "pre_state_witness_requirements": list(pre),
        "post_state_witness_requirements": list(post),
        "witness_class": witness_class,
        "failure_semantics": [
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
        "four_lane_hydration_relation": (
            "COORDINATED_TYPED_VIEW_NO_INDEPENDENT_CANONICAL_AUTHORITY"
        ),
        "multimodal_geometry_relation": (
            "PLATONIC_COLOR_WHEEL_SPRITE_PROJECTION_DOWNSTREAM_ONLY"
        ),
    }
    body["binding_root_hash72"] = product_root(
        "pass220_i028_g3_opcode_binding_v1",
        stable(body),
    )
    return stable(body)


def build_g3_opcode_registry() -> dict[str, Any]:
    entries = [_binding(*row) for row in _ROWS]
    result = {
        "schema": SCHEMA,
        "binding_schema": BINDING_SCHEMA,
        "parent_binding_style": "PASS_079_ROOTED_OPCODE_BINDING",
        "historical_pass079_registry_mutated": False,
        "opcode_range": [24, 34],
        "registered_opcodes": len(entries),
        "entries": entries,
        "policy": (
            "NO_NAME_SIGNATURE_OR_FUSED_SHORTCUT_AUTHORITY;"
            "EVERY_PRIMITIVE_HAS_DISTINCT_ROOT_AND_WITNESS"
        ),
        "lane5_bios_relation": "OUROBOROS_MANIFOLD_ALGORITHM",
        "four_lane_hydration_authority": False,
        "graphics_projection_authority": False,
    }
    result["registry_root_hash72"] = product_root(
        "pass220_i028_g3_opcode_registry_v1",
        stable(result),
    )
    return stable(result)


def resolve_g3_opcode(
    opcode: str,
    request: dict[str, Any],
) -> dict[str, Any]:
    registry = build_g3_opcode_registry()
    matches = [
        entry
        for entry in registry["entries"]
        if entry["native_opcode"] == opcode
    ]
    if len(matches) != 1:
        raise ValueError("REJECT_UNREGISTERED_G3_OPCODE")
    binding = matches[0]
    if request.get("binding_root_hash72") != binding["binding_root_hash72"]:
        raise ValueError("REJECT_G3_BINDING_ROOT_MISMATCH")
    if request.get("authority_scope") != binding["authority_scope"]:
        raise ValueError("REJECT_G3_AUTHORITY_SCOPE_MISMATCH")
    if request.get("lease_status") != "ACTIVE_VALIDATED":
        raise ValueError("REJECT_G3_LEASE_NOT_ACTIVE_VALIDATED")
    if request.get("vm81_lane_binding_status") != "BOUND_WITNESSED":
        raise ValueError("REJECT_G3_VM81_LANE_NOT_BOUND")
    return stable({
        "decision": "RESOLVED_FOR_BOUNDED_VM81_INTERPRETER_INVOCATION",
        "native_opcode": opcode,
        "numeric_opcode": binding["numeric_opcode"],
        "binding_root_hash72": binding["binding_root_hash72"],
        "witness_class": binding["witness_class"],
        "invocation_not_executed": True,
    })
