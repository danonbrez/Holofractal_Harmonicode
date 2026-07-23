"""Runtime-enforced interpreter/compiler semantic equivalence gate."""
from __future__ import annotations

from typing import Any, Dict, Mapping, Tuple

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_harmonicode_interpreter.hhs_executable_ir_v1 import verify_executable_ir

from .hhs_canonical_semantic_projection_v1 import (
    canonical_semantic_projection,
    compare_semantic_projections,
)
from .hhs_portable_bytecode_v1 import artifact_bytes
from .hhs_pass077_contracts_v1 import (
    EQUIVALENCE_RECEIPT_SCHEMA,
    rooted,
    validate_registered_target_contract,
    verify_rooted,
)


def build_equivalence_receipt(
    *, receipt_id: str, target_contract: Mapping[str, Any], executable_ir: Mapping[str, Any],
    compiled_artifact: Mapping[str, Any], interpreter_execution: Mapping[str, Any],
    compiled_execution: Mapping[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    registration = validate_registered_target_contract(target_contract)
    if not verify_executable_ir(executable_ir):
        raise ContractError("REJECT_EQUIVALENCE_INVALID_EXECUTABLE_IR")
    if not verify_rooted("pass076_interpreter_run", interpreter_execution, "execution_run_root_hash72"):
        raise ContractError("REJECT_EQUIVALENCE_INVALID_INTERPRETER_EXECUTION")
    if not verify_rooted("pass077_portable_bytecode_execution", compiled_execution, "compiled_execution_root_hash72"):
        raise ContractError("REJECT_EQUIVALENCE_INVALID_COMPILED_EXECUTION")
    artifact_bytes(compiled_artifact)
    if compiled_artifact.get("target_contract_root_hash72") != registration.get("contract_root_hash72"):
        raise ContractError("REJECT_EQUIVALENCE_TARGET_CONTRACT_MISMATCH")
    if compiled_artifact.get("executable_ir_root_hash72") != executable_ir.get("executable_ir_root_hash72"):
        raise ContractError("REJECT_EQUIVALENCE_EXECUTABLE_IR_MISMATCH")
    interpreter_projection = canonical_semantic_projection(execution=interpreter_execution, executable_ir=executable_ir)
    compiled_projection = canonical_semantic_projection(execution=compiled_execution, executable_ir=executable_ir)
    comparisons = compare_semantic_projections(interpreter=interpreter_projection, compiled=compiled_projection)
    roots_match = interpreter_projection["semantic_projection_root_hash72"] == compiled_projection["semantic_projection_root_hash72"]
    all_fields_match = all(item["match"] for item in comparisons)
    verified = roots_match and all_fields_match
    mismatch_codes = [item["rejection_code"] for item in comparisons if not item["match"]]
    body = {
        "schema": EQUIVALENCE_RECEIPT_SCHEMA,
        "receipt_id": receipt_id,
        "target_contract_root_hash72": registration["contract_root_hash72"],
        "source_artifact_root_hash72": executable_ir.get("source_artifact_root_hash72"),
        "executable_ir_root_hash72": executable_ir.get("executable_ir_root_hash72"),
        "compiled_artifact_root_hash72": compiled_artifact.get("artifact_payload_root_hash72"),
        "interpreter_execution_root_hash72": interpreter_execution.get("execution_run_root_hash72"),
        "compiled_execution_root_hash72": compiled_execution.get("compiled_execution_root_hash72"),
        "interpreter_semantic_projection_root_hash72": interpreter_projection.get("semantic_projection_root_hash72"),
        "compiled_semantic_projection_root_hash72": compiled_projection.get("semantic_projection_root_hash72"),
        "field_comparisons": comparisons,
        "execution_roots_expected_to_match": False,
        "execution_roots_match": interpreter_execution.get("execution_run_root_hash72") == compiled_execution.get("compiled_execution_root_hash72"),
        "semantic_projection_roots_match": roots_match,
        "all_contract_fields_match": all_fields_match,
        "status": "SEMANTIC_IDENTITY_VERIFIED" if verified else "SEMANTIC_IDENTITY_REJECTED",
        "summary_rejection_code": None if verified else "REJECT_INTERPRETER_COMPILER_SEMANTIC_DIVERGENCE",
        "field_rejection_codes": mismatch_codes,
        "artifact_admission_permitted": verified,
        "canonical_continuation_permitted": verified,
        "fallback_used": False,
    }
    receipt = rooted("pass077_interpreter_compiler_equivalence_receipt", body, "receipt_root_hash72")
    return receipt, interpreter_projection, compiled_projection


def enforce_equivalence(receipt: Mapping[str, Any]) -> None:
    if not verify_rooted("pass077_interpreter_compiler_equivalence_receipt", receipt, "receipt_root_hash72"):
        raise ContractError("REJECT_EQUIVALENCE_RECEIPT_ROOT_MISMATCH")
    if receipt.get("status") != "SEMANTIC_IDENTITY_VERIFIED" or receipt.get("artifact_admission_permitted") is not True:
        raise ContractError("REJECT_INTERPRETER_COMPILER_SEMANTIC_DIVERGENCE")
