"""HHS compiler IR primitives for Pass 049."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from hhs_backend.runtime.runtime_workspace_object_v1 import VERSION, AUTHORITY, hash72

IR_SCHEMA = "HHS_COMPILER_IR_V1"
ARTIFACT_SCHEMA = "HHS_COMPILED_ARTIFACT_V1"

SUPPORTED_TARGETS = [
    "HHS_IR",
    "C_KERNEL_PLAN",
    "C_SOURCE",
    "PYTHON_ADAPTER",
    "JSON_EXECUTION_GRAPH",
    "DOT_GRAPH",
    "BYTECODE_OR_VM_PLAN",
    "RECEIPT_ONLY_PLAN",
]


def tokenize_hhs_source(source_text: str) -> List[str]:
    return [token for token in source_text.replace("\n", " ").split(" ") if token]


def build_hhs_ir(source_object_id: str, source_text: str) -> Dict[str, Any]:
    tokens = tokenize_hhs_source(source_text)
    ops = []
    for index, token in enumerate(tokens):
        ops.append({
            "op_index": index,
            "operation": "SYMBOLIC_TOKEN",
            "token_hash72": hash72("HHS_IR_SYMBOLIC_TOKEN_V1", token),
            "invariant_owners": ["HHS-I001", "HHS-I002", "HHS-I008", "HHS-I011"],
            "witness_required": True,
        })
    ir = {
        "schema": IR_SCHEMA,
        "version": VERSION,
        "source_object_id": source_object_id,
        "deterministic_ordering": True,
        "state_inputs": [],
        "state_outputs": [],
        "operations": ops,
        "explicit_authority_gates": ["zero_bypass_interposer", "kernel_conformance_surface_map"],
        "explicit_failure_paths": ["REJECT_INVARIANT_DERIVATION_FAILURE", "REJECT_COMPILER_EFFECT_MISMATCH"],
        "authority": AUTHORITY,
    }
    ir["ir_root_hash72"] = hash72(IR_SCHEMA, ir)
    return ir


def build_compiled_artifact(source_object_id: str, source_text: str, target: str = "HHS_IR") -> Dict[str, Any]:
    if target not in SUPPORTED_TARGETS:
        rejection = {
            "schema": "HHS_COMPILED_ARTIFACT_REJECTION_V1",
            "version": VERSION,
            "ok": False,
            "status": "REJECT_COMPILER_TARGET_UNAUTHORIZED",
            "target": target,
        }
        rejection["rejection_hash72"] = hash72("HHS_COMPILED_ARTIFACT_REJECTION_V1", rejection)
        return rejection
    ir = build_hhs_ir(source_object_id, source_text)
    artifact = {
        "schema": ARTIFACT_SCHEMA,
        "version": VERSION,
        "artifact_id": f"artifact:{ir['ir_root_hash72'][:16]}",
        "source_object_ids": [source_object_id],
        "target": target,
        "ir_root_hash72": ir["ir_root_hash72"],
        "target_root_hash72": hash72(f"HHS_COMPILED_ARTIFACT_TARGET_{target}_V1", ir),
        "compiler_pipeline_root_hash72": hash72("HHS_COMPILER_PIPELINE_V1", {"target": target, "ir": ir}),
        "conformance_status": "ADMIT_COMPILED_ARTIFACT",
        "execution_authorized": False,
        "ir": ir,
        "authority": AUTHORITY,
    }
    artifact["receipt_hash72"] = hash72(ARTIFACT_SCHEMA, artifact)
    artifact["ok"] = True
    return artifact


def compiler_ir_self_test() -> Dict[str, Any]:
    ir = build_hhs_ir("object:source", "a²=1 b²=2")
    artifact = build_compiled_artifact("object:source", "a²=1 b²=2", "HHS_IR")
    rejected = build_compiled_artifact("object:source", "a²=1", "UNDECLARED_HOST_BINARY")
    return {
        "schema": "HHS_COMPILER_IR_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(ir.get("ir_root_hash72") and artifact.get("ok") and not rejected.get("ok")),
        "ir": ir,
        "artifact": artifact,
        "target_rejection": rejected,
        "constraint": "COMPILATION_DOES_NOT_IMPLY_EXECUTION_AUTHORIZATION",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(compiler_ir_self_test(), indent=2, sort_keys=True, default=str))
