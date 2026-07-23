"""Deterministic HHS_EXECUTABLE_IR_V1 projection to HHS portable bytecode."""
from __future__ import annotations

import ast
import base64
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable
from native_projects.hhs_harmonicode_interpreter.hhs_exact_symbolic_interpreter_v1 import evaluate_term
from native_projects.hhs_harmonicode_interpreter.hhs_executable_ir_v1 import verify_executable_ir
from native_projects.hhs_harmonicode_interpreter.hhs_pass076_contracts_v1 import REQUIRED_INVARIANT_EXPECTATIONS

from .hhs_pass077_contracts_v1 import (
    BYTECODE_MAGIC,
    COMPILED_ARTIFACT_SCHEMA,
    COMPILED_EXECUTION_SCHEMA,
    COMPILATION_PLAN_SCHEMA,
    COMPILATION_REQUEST_SCHEMA,
    MAX_ARTIFACT_BYTES,
    MAX_BYTECODE_INSTRUCTIONS,
    OPTIMIZATION_PROOF_SCHEMA,
    SUPPORTED_TARGET_OPERATIONS,
    TARGET_ID,
    TARGET_IR_SCHEMA,
    artifact_transport_identity,
    rooted,
    validate_compilation_request_fields,
    validate_registered_target_contract,
    verify_rooted,
)

COMPILER_IDENTITY = "HHS_PASS_077_PORTABLE_BYTECODE_COMPILER"
COMPILER_VERSION = "0.1.0"
BYTECODE_VM_VERSION = "HHS_PORTABLE_BYTECODE_VM_PASS_077_V1"

OPCODE_MAP = {
    "DEFINE_GATE": "GATE_DECLARE",
    "INVOKE_GATE": "GATE_INVOKE",
    "EVALUATE_EQUALITY": "RELATION_EQUAL",
    "EVALUATE_DISTINCTNESS": "ORDERED_DISTINCT",
    "EVALUATE_EXPRESSION": "EXPRESSION_EVAL",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(stable(value), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _walk(items: Iterable[Mapping[str, Any]]) -> Iterable[Mapping[str, Any]]:
    for item in items:
        yield item
        yield from _walk(item.get("children", []))


def _flatten_executable(executable_ir: Mapping[str, Any]) -> List[Dict[str, Any]]:
    gates = {str(x.get("name") or ""): x for x in executable_ir.get("statements", []) if x.get("operation") == "DEFINE_GATE"}
    plan: List[Dict[str, Any]] = []

    def append(statement: Mapping[str, Any], stack: Tuple[str, ...] = ()) -> None:
        operation = str(statement.get("operation") or "")
        current = {k: deepcopy(v) for k, v in statement.items() if k != "children"}
        plan.append(stable(current))
        if operation == "INVOKE_GATE":
            name = str(statement.get("name") or "")
            if name not in gates:
                raise ContractError(f"REJECT_UNKNOWN_GATE_INVOCATION:{name}")
            if name in stack:
                raise ContractError(f"REJECT_RECURSIVE_GATE_CYCLE:{name}")
            for child in gates[name].get("children", []):
                append(child, (*stack, name))

    for statement in executable_ir.get("statements", []):
        append(statement)
    if len(plan) > MAX_BYTECODE_INSTRUCTIONS:
        raise ContractError("REJECT_TARGET_INSTRUCTION_BOUND_EXCEEDED")
    return plan


def build_compilation_plan(
    *, compilation_id: str, executable_ir: Mapping[str, Any], target_contract: Mapping[str, Any],
    requirement_root_hash72: str, source_artifact_root_hash72: str,
    typed_ir_root_hash72: str, test_receipt_root_hash72: str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not verify_executable_ir(executable_ir):
        raise ContractError("REJECT_COMPILATION_INVALID_EXECUTABLE_IR")
    registration = validate_registered_target_contract(target_contract)
    if executable_ir.get("source_artifact_root_hash72") != source_artifact_root_hash72:
        raise ContractError("REJECT_COMPILATION_SOURCE_LINEAGE_MISMATCH")
    if executable_ir.get("typed_ir_root_hash72") != typed_ir_root_hash72:
        raise ContractError("REJECT_COMPILATION_TYPED_IR_LINEAGE_MISMATCH")
    source_plan = _flatten_executable(executable_ir)
    unsupported = sorted({str(item.get("operation") or "") for item in source_plan if str(item.get("operation") or "") not in OPCODE_MAP})
    if unsupported:
        raise ContractError("REJECT_TARGET_INVOKES_UNSUPPORTED_OPERATION:" + ",".join(unsupported))
    plan_body = {
        "schema": COMPILATION_PLAN_SCHEMA,
        "compilation_id": compilation_id,
        "compiler_identity": COMPILER_IDENTITY,
        "compiler_version": COMPILER_VERSION,
        "target_id": TARGET_ID,
        "target_contract_root_hash72": registration["contract_root_hash72"],
        "requirement_root_hash72": requirement_root_hash72,
        "source_artifact_root_hash72": source_artifact_root_hash72,
        "typed_ir_root_hash72": typed_ir_root_hash72,
        "executable_ir_root_hash72": executable_ir.get("executable_ir_root_hash72"),
        "test_receipt_root_hash72": test_receipt_root_hash72,
        "lowering_steps": [
            {
                "sequence": index,
                "source_statement_root_hash72": item.get("statement_root_hash72"),
                "source_operation": item.get("operation"),
                "target_operation": OPCODE_MAP[str(item.get("operation"))],
            }
            for index, item in enumerate(source_plan, 1)
        ],
        "planned_optimizations": ["IDENTITY_CANONICALIZATION"],
        "equivalence_test_plan": {
            "comparison": "EXACT_CANONICAL_PROJECTION_ROOT_EQUALITY",
            "tolerance": "EXACT",
            "reference_interpreter_required": True,
            "compiled_target_execution_required": True,
        },
        "deterministic": True,
        "effects_executed_during_planning": False,
    }
    plan = rooted("pass077_compilation_plan", plan_body, "compilation_plan_root_hash72")
    request_body = {
        "schema": COMPILATION_REQUEST_SCHEMA,
        "compilation_id": compilation_id,
        "target_contract_root_hash72": registration["contract_root_hash72"],
        "requirement_root_hash72": requirement_root_hash72,
        "source_artifact_root_hash72": source_artifact_root_hash72,
        "typed_ir_root_hash72": typed_ir_root_hash72,
        "executable_ir_root_hash72": executable_ir.get("executable_ir_root_hash72"),
        "compilation_plan_root_hash72": plan["compilation_plan_root_hash72"],
        "test_receipt_root_hash72": test_receipt_root_hash72,
        "requested_status": "CANDIDATE",
    }
    validate_compilation_request_fields(request_body)
    request = rooted("pass077_compilation_request", request_body, "compilation_request_root_hash72")
    return request, plan


def lower_to_target_ir(*, target_ir_id: str, executable_ir: Mapping[str, Any], compilation_plan: Mapping[str, Any], target_contract: Mapping[str, Any]) -> Dict[str, Any]:
    if not verify_executable_ir(executable_ir):
        raise ContractError("REJECT_LOWER_INVALID_EXECUTABLE_IR")
    registration = validate_registered_target_contract(target_contract)
    if not verify_rooted("pass077_compilation_plan", compilation_plan, "compilation_plan_root_hash72"):
        raise ContractError("REJECT_COMPILATION_PLAN_ROOT_MISMATCH")
    if compilation_plan.get("target_contract_root_hash72") != registration.get("contract_root_hash72"):
        raise ContractError("REJECT_COMPILATION_PLAN_CONTRACT_ROOT_MISMATCH")
    if compilation_plan.get("executable_ir_root_hash72") != executable_ir.get("executable_ir_root_hash72"):
        raise ContractError("REJECT_COMPILATION_PLAN_EXECUTABLE_IR_MISMATCH")
    instructions = []
    for index, statement in enumerate(_flatten_executable(executable_ir), 1):
        source_operation = str(statement.get("operation") or "")
        opcode = OPCODE_MAP.get(source_operation)
        if opcode not in SUPPORTED_TARGET_OPERATIONS:
            raise ContractError(f"REJECT_TARGET_INVOKES_UNSUPPORTED_OPERATION:{source_operation}")
        instruction_body = {
            "schema": "HHS_TARGET_IR_INSTRUCTION_V1",
            "instruction_index": index,
            "opcode": opcode,
            "source_operation": source_operation,
            "source_statement_id": statement.get("statement_id"),
            "source_statement_root_hash72": statement.get("statement_root_hash72"),
            "name": statement.get("name"),
            "operands": stable(statement.get("operands", [])),
            "effect_declaration": statement.get("effect_declaration"),
            "authority_requirements": stable(statement.get("authority_requirements", [])),
            "invariant_bindings": stable(statement.get("invariant_bindings", [])),
            "source_span": stable(statement.get("source_span", {})),
        }
        instruction_body["instruction_root_hash72"] = product_root("pass077_target_instruction", instruction_body)
        instructions.append(stable(instruction_body))
    body = {
        "schema": TARGET_IR_SCHEMA,
        "target_ir_id": target_ir_id,
        "target_id": TARGET_ID,
        "target_contract_root_hash72": registration["contract_root_hash72"],
        "compilation_plan_root_hash72": compilation_plan["compilation_plan_root_hash72"],
        "executable_ir_root_hash72": executable_ir.get("executable_ir_root_hash72"),
        "source_identity": {
            "source_artifact_root_hash72": executable_ir.get("source_artifact_root_hash72"),
            "source_sha256": executable_ir.get("source_sha256"),
            "typed_ir_root_hash72": executable_ir.get("typed_ir_root_hash72"),
            "executable_ir_root_hash72": executable_ir.get("executable_ir_root_hash72"),
        },
        "instructions": instructions,
        "instruction_count": len(instructions),
        "exact_integer_model": True,
        "exact_rational_model": True,
        "float_operations_present": False,
        "effects_declared_only": True,
        "deterministic": True,
    }
    return rooted("pass077_target_ir", body, "target_ir_root_hash72")


def verify_target_ir(value: Mapping[str, Any]) -> bool:
    if value.get("schema") != TARGET_IR_SCHEMA or not verify_rooted("pass077_target_ir", value, "target_ir_root_hash72"):
        return False
    instructions = value.get("instructions", [])
    if value.get("instruction_count") != len(instructions) or len(instructions) > MAX_BYTECODE_INSTRUCTIONS:
        return False
    for item in instructions:
        body = deepcopy(dict(item)); supplied = body.pop("instruction_root_hash72", "")
        if supplied != product_root("pass077_target_instruction", body):
            return False
        if item.get("opcode") not in SUPPORTED_TARGET_OPERATIONS:
            return False
    return True


def optimize_target_ir(*, optimization_id: str, target_ir: Mapping[str, Any], optimization: str = "IDENTITY_CANONICALIZATION") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not verify_target_ir(target_ir):
        raise ContractError("REJECT_OPTIMIZATION_INVALID_TARGET_IR")
    if optimization != "IDENTITY_CANONICALIZATION":
        raise ContractError(f"REJECT_UNREGISTERED_OPTIMIZATION:{optimization}")
    optimized = stable(target_ir)
    proof_body = {
        "schema": OPTIMIZATION_PROOF_SCHEMA,
        "optimization_id": optimization_id,
        "optimization": optimization,
        "input_region": "WHOLE_TARGET_IR",
        "output_region": "WHOLE_TARGET_IR",
        "input_target_ir_root_hash72": target_ir.get("target_ir_root_hash72"),
        "output_target_ir_root_hash72": optimized.get("target_ir_root_hash72"),
        "preserved_semantics": True,
        "preserved_ordering": True,
        "preserved_effects": True,
        "preserved_invariants": True,
        "instruction_order_unchanged": True,
        "equivalence_obligation": "EXACT_TARGET_IR_ROOT_IDENTITY",
        "equivalence_test_passed": target_ir == optimized,
    }
    proof = rooted("pass077_optimization_proof", proof_body, "optimization_proof_root_hash72")
    return optimized, proof


def emit_candidate_artifact(*, artifact_id: str, target_ir: Mapping[str, Any], optimization_proof: Mapping[str, Any]) -> Dict[str, Any]:
    if not verify_target_ir(target_ir):
        raise ContractError("REJECT_EMIT_INVALID_TARGET_IR")
    if not verify_rooted("pass077_optimization_proof", optimization_proof, "optimization_proof_root_hash72"):
        raise ContractError("REJECT_OPTIMIZATION_PROOF_ROOT_MISMATCH")
    if optimization_proof.get("equivalence_test_passed") is not True:
        raise ContractError("REJECT_OPTIMIZATION_WITHOUT_EQUIVALENCE_WITNESS")
    bytecode_document = {
        "schema": "HHS_PORTABLE_BYTECODE_V1",
        "bytecode_version": "1",
        "target_id": TARGET_ID,
        "target_contract_root_hash72": target_ir.get("target_contract_root_hash72"),
        "target_ir_root_hash72": target_ir.get("target_ir_root_hash72"),
        "executable_ir_root_hash72": target_ir.get("executable_ir_root_hash72"),
        "source_identity": stable(target_ir.get("source_identity", {})),
        "instructions": stable(target_ir.get("instructions", [])),
        "instruction_count": target_ir.get("instruction_count"),
        "numeric_model": {"integer": "EXACT", "rational": "EXACT", "float": "FORBIDDEN"},
        "effect_model": "DECLARED_ONLY",
    }
    data = BYTECODE_MAGIC + canonical_json_bytes(bytecode_document)
    identity = artifact_transport_identity(data)
    payload_identity = {
        "artifact_format": TARGET_ID,
        "target_contract_root_hash72": target_ir.get("target_contract_root_hash72"),
        "target_ir_root_hash72": target_ir.get("target_ir_root_hash72"),
        "executable_ir_root_hash72": target_ir.get("executable_ir_root_hash72"),
        **identity,
    }
    body = {
        "schema": COMPILED_ARTIFACT_SCHEMA,
        "artifact_id": artifact_id,
        "artifact_format": TARGET_ID,
        "status": "CANDIDATE",
        "target_contract_root_hash72": target_ir.get("target_contract_root_hash72"),
        "target_ir_root_hash72": target_ir.get("target_ir_root_hash72"),
        "executable_ir_root_hash72": target_ir.get("executable_ir_root_hash72"),
        "optimization_proof_root_hash72": optimization_proof.get("optimization_proof_root_hash72"),
        "artifact_bytes_base64": base64.b64encode(data).decode("ascii"),
        **identity,
        "artifact_payload_root_hash72": product_root("pass077_compiled_artifact_payload", payload_identity),
        "artifact_exists_but_does_not_self_authorize": True,
        "deployment_authority_conferred": False,
        "foundation_mutated": False,
    }
    return rooted("pass077_compiled_artifact", body, "artifact_root_hash72")


def artifact_bytes(artifact: Mapping[str, Any]) -> bytes:
    if artifact.get("schema") != COMPILED_ARTIFACT_SCHEMA:
        raise ContractError("REJECT_COMPILED_ARTIFACT_SCHEMA")
    if not verify_rooted("pass077_compiled_artifact", artifact, "artifact_root_hash72"):
        raise ContractError("REJECT_COMPILED_ARTIFACT_ROOT_MISMATCH")
    try:
        data = base64.b64decode(str(artifact.get("artifact_bytes_base64") or ""), validate=True)
    except Exception as exc:
        raise ContractError("REJECT_ARTIFACT_BASE64") from exc
    if len(data) != int(artifact.get("artifact_size_bytes", -1)) or len(data) > MAX_ARTIFACT_BYTES:
        raise ContractError("REJECT_ARTIFACT_SIZE_MISMATCH")
    if hashlib.sha256(data).hexdigest() != artifact.get("artifact_content_sha256"):
        raise ContractError("REJECT_ARTIFACT_TAMPERED")
    return data


def decode_bytecode_artifact(artifact: Mapping[str, Any]) -> Dict[str, Any]:
    data = artifact_bytes(artifact)
    if not data.startswith(BYTECODE_MAGIC):
        raise ContractError("REJECT_PORTABLE_BYTECODE_MAGIC")
    try:
        document = json.loads(data[len(BYTECODE_MAGIC):].decode("utf-8"))
    except Exception as exc:
        raise ContractError("REJECT_PORTABLE_BYTECODE_DECODE") from exc
    if canonical_json_bytes(document) != data[len(BYTECODE_MAGIC):]:
        raise ContractError("REJECT_NONCANONICAL_PORTABLE_BYTECODE")
    if document.get("schema") != "HHS_PORTABLE_BYTECODE_V1" or document.get("target_id") != TARGET_ID:
        raise ContractError("REJECT_PORTABLE_BYTECODE_SCHEMA")
    if document.get("instruction_count") != len(document.get("instructions", [])):
        raise ContractError("REJECT_PORTABLE_BYTECODE_INSTRUCTION_COUNT")
    if any(item.get("opcode") not in SUPPORTED_TARGET_OPERATIONS for item in document.get("instructions", [])):
        raise ContractError("REJECT_TARGET_INVOKES_UNSUPPORTED_OPERATION")
    return stable(document)


def _value_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return stable(left) == stable(right)


def _contains_symbol(value: Mapping[str, Any], name: str) -> bool:
    if value.get("type") in {"SYMBOL", "ORDERED_PRODUCT"}:
        return value.get("name") == name
    return any(_contains_symbol(x, name) for x in value.get("operands", []))


def _bare_bindable_symbol(term: str, bindings: Mapping[str, Mapping[str, Any]]) -> str:
    try:
        tree = ast.parse(term.strip(), mode="eval")
    except SyntaxError:
        return ""
    if isinstance(tree.body, ast.Name) and tree.body.id not in bindings:
        name = tree.body.id
        if len(name) == 2 and name.isascii() and name.isalpha():
            return ""
        return name
    return ""


def _equality(operands: Sequence[str], bindings: MutableMapping[str, Dict[str, Any]]) -> Dict[str, Any]:
    if len(operands) < 2:
        raise ContractError("REJECT_EQUALITY_REQUIRES_TWO_OPERANDS")
    observations = []
    for left_text, right_text in zip(operands, operands[1:]):
        left_name, right_name = _bare_bindable_symbol(left_text, bindings), _bare_bindable_symbol(right_text, bindings)
        left, right = evaluate_term(left_text, bindings), evaluate_term(right_text, bindings)
        if left_name and not _contains_symbol(right, left_name):
            bindings[left_name] = stable(right); left = stable(right); action = "BOUND_LEFT_SYMBOL"
        elif right_name and not _contains_symbol(left, right_name):
            bindings[right_name] = stable(left); right = stable(left); action = "BOUND_RIGHT_SYMBOL"
        else:
            action = "COMPARED_EXISTING_VALUES"
        equal = _value_equal(left, right)
        observations.append(stable({"left_text": left_text, "right_text": right_text, "left_value": left, "right_value": right, "action": action, "equal": equal}))
        if not equal:
            return {"satisfied": False, "observations": observations, "diagnostic": "EQUALITY_NOT_SATISFIED"}
    return {"satisfied": True, "observations": observations}


def _distinct(operands: Sequence[str], bindings: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    if len(operands) < 2:
        raise ContractError("REJECT_DISTINCTNESS_REQUIRES_TWO_OPERANDS")
    observations = []
    for left_text, right_text in zip(operands, operands[1:]):
        left, right = evaluate_term(left_text, bindings), evaluate_term(right_text, bindings)
        distinct = not _value_equal(left, right)
        observations.append(stable({"left_text": left_text, "right_text": right_text, "left_value": left, "right_value": right, "distinct": distinct}))
        if not distinct:
            return {"satisfied": False, "observations": observations, "diagnostic": "DISTINCTNESS_NOT_SATISFIED"}
    return {"satisfied": True, "observations": observations}


def execute_bytecode(*, run_id: str, artifact: Mapping[str, Any]) -> Dict[str, Any]:
    document = decode_bytecode_artifact(artifact)
    instructions = document["instructions"]
    state = {
        "schema": "HHS_PORTABLE_BYTECODE_STATE_V1",
        "run_id": run_id,
        "artifact_ref": artifact.get("artifact_id"),
        "artifact_root_hash72": artifact.get("artifact_payload_root_hash72"),
        "program_counter": 0,
        "step_count": 0,
        "status": "READY",
        "bindings": {},
        "defined_gates": {},
        "invariant_status": {name: "UNRESOLVED" for name in REQUIRED_INVARIANT_EXPECTATIONS},
        "diagnostics": [],
        "external_effects_executed": False,
        "foundation_mutated": False,
    }
    state["state_root_hash72"] = product_root("pass077_portable_bytecode_state", state)
    initial_root = state["state_root_hash72"]
    receipts = []
    for instruction in instructions:
        before = state["state_root_hash72"]
        previous_receipt = receipts[-1]["step_receipt_root_hash72"] if receipts else "GENESIS"
        body = deepcopy(state); body.pop("state_root_hash72", None)
        opcode = str(instruction.get("opcode") or "")
        if opcode == "GATE_DECLARE":
            name = str(instruction.get("name") or "")
            body["defined_gates"][name] = instruction.get("source_statement_root_hash72")
            outcome = {"satisfied": bool(name), "gate_defined": name}
        elif opcode == "GATE_INVOKE":
            name = str(instruction.get("name") or "")
            outcome = {"satisfied": name in body["defined_gates"], "gate_invoked": name}
            if not outcome["satisfied"]: outcome["diagnostic"] = "GATE_NOT_DEFINED"
        elif opcode == "RELATION_EQUAL":
            outcome = _equality(instruction.get("operands", []), body["bindings"])
        elif opcode == "ORDERED_DISTINCT":
            outcome = _distinct(instruction.get("operands", []), body["bindings"])
        elif opcode == "EXPRESSION_EVAL":
            outcome = {"satisfied": True, "values": [evaluate_term(x, body["bindings"]) for x in instruction.get("operands", [])]}
        else:
            raise ContractError(f"REJECT_TARGET_INVOKES_UNSUPPORTED_OPERATION:{opcode}")
        body["program_counter"] += 1
        body["step_count"] += 1
        for name, expected in REQUIRED_INVARIANT_EXPECTATIONS.items():
            value = body["bindings"].get(name)
            body["invariant_status"][name] = "SATISFIED" if value is not None and stable(value) == stable(expected) else "UNRESOLVED_OR_FAILED"
        if not outcome.get("satisfied"):
            body["status"] = "FAILED"
            body["diagnostics"].append({"code": outcome.get("diagnostic", "BYTECODE_CONSTRAINT_FAILED"), "severity": "ERROR"})
        elif body["program_counter"] == len(instructions):
            body["status"] = "CLOSED" if all(v == "SATISFIED" for v in body["invariant_status"].values()) else "FAILED"
            if body["status"] == "FAILED": body["diagnostics"].append({"code": "REQUIRED_INVARIANT_CLOSURE_FAILED", "severity": "ERROR"})
        else:
            body["status"] = "RUNNING"
        state = stable(body)
        state["state_root_hash72"] = product_root("pass077_portable_bytecode_state", state)
        receipt_body = {
            "schema": "HHS_PORTABLE_BYTECODE_STEP_RECEIPT_V1",
            "run_id": run_id,
            "step_index": state["step_count"],
            "operation": opcode,
            "source_statement_root_hash72": instruction.get("source_statement_root_hash72"),
            "previous_step_receipt_root_hash72": previous_receipt,
            "previous_state_root_hash72": before,
            "resulting_state_root_hash72": state["state_root_hash72"],
            "outcome": stable(outcome),
            "status_after": state["status"],
        }
        receipt_body["step_receipt_root_hash72"] = product_root("pass077_bytecode_step_receipt", receipt_body)
        receipts.append(stable(receipt_body))
        if state["status"] == "FAILED":
            break
    run_body = {
        "schema": COMPILED_EXECUTION_SCHEMA,
        "version": BYTECODE_VM_VERSION,
        "run_id": run_id,
        "compiled_artifact_ref": artifact.get("artifact_id"),
        "compiled_artifact_root_hash72": artifact.get("artifact_payload_root_hash72"),
        "initial_state_root_hash72": initial_root,
        "final_state": state,
        "step_receipts": receipts,
        "step_count": len(receipts),
        "status": state["status"],
        "closed": state["status"] == "CLOSED",
        "deterministic": True,
        "exact_arithmetic_only": True,
        "external_effects_executed": False,
        "foundation_mutated": False,
    }
    return rooted("pass077_portable_bytecode_execution", run_body, "compiled_execution_root_hash72")


def replay_compiled_execution(*, execution: Mapping[str, Any], artifact: Mapping[str, Any]) -> Dict[str, Any]:
    if not verify_rooted("pass077_portable_bytecode_execution", execution, "compiled_execution_root_hash72"):
        raise ContractError("REJECT_COMPILED_EXECUTION_ROOT_MISMATCH")
    observed = execute_bytecode(run_id=str(execution.get("run_id")), artifact=artifact)
    body = {
        "schema": "HHS_COMPILED_EXECUTION_REPLAY_V1",
        "expected_compiled_execution_root_hash72": execution.get("compiled_execution_root_hash72"),
        "observed_compiled_execution_root_hash72": observed.get("compiled_execution_root_hash72"),
        "matches": observed.get("compiled_execution_root_hash72") == execution.get("compiled_execution_root_hash72"),
        "thread_context_used": False,
        "llm_context_window_used": False,
        "host_path_used_as_identity": False,
    }
    return rooted("pass077_compiled_execution_replay", body, "compiled_replay_root_hash72")
