#!/usr/bin/env python3
"""Zero-dependency independent verifier for HHS Pass 077 artifact packages.

This verifier uses only Python's standard library and package-contained data.
It does not confer deployment authority and does not trust a stored status by
itself: it replays both the reference executable IR and portable bytecode,
projects their canonical semantics, and compares exact projection roots.
"""
from __future__ import annotations

import ast
import base64
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple
import zipfile

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()^=!?>"
BYTECODE_MAGIC = b"HHSBC1\n"
SEMANTIC_FIELDS = (
    "output_values", "symbolic_relations", "ordered_products", "reciprocal_bindings",
    "gate_results", "zero_sum_closure", "required_invariants", "declared_effects",
    "authority_scope", "source_identity",
)
EXPECTED_INVARIANTS = {
    "Δe": {"type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1},
    "Ψ": {"type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1},
    "Θ15": {"type": "BOOLEAN", "value": True},
    "Ω": {"type": "BOOLEAN", "value": True},
}

class VerificationError(RuntimeError):
    pass


def stable(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(stable(value), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def product_root(label: str, payload: Any) -> str:
    material = canonical_bytes({"label": label, "payload": stable(payload)})
    value = int.from_bytes(hashlib.sha256(material).digest(), "big")
    chars = []
    for _ in range(72):
        value, remainder = divmod(value, len(ALPHABET)); chars.append(ALPHABET[remainder])
    return "".join(reversed(chars))


def verify_rooted(label: str, value: Mapping[str, Any], root_field: str) -> bool:
    body = deepcopy(dict(value)); supplied = str(body.pop(root_field, ""))
    return bool(supplied) and supplied == product_root(label, body)


def rooted(label: str, value: Mapping[str, Any], root_field: str) -> Dict[str, Any]:
    body = stable(value); body[root_field] = product_root(label, body); return stable(body)


def load_package(path: str | Path) -> Dict[str, bytes]:
    p = Path(path)
    if p.is_dir():
        return {str(x.relative_to(p)).replace("\\", "/"): x.read_bytes() for x in sorted(p.rglob("*")) if x.is_file()}
    if p.is_file():
        with zipfile.ZipFile(p, "r") as archive:
            return {name: archive.read(name) for name in sorted(archive.namelist()) if not name.endswith("/")}
    raise VerificationError("PACKAGE_NOT_FOUND")


def jload(files: Mapping[str, bytes], name: str) -> Dict[str, Any]:
    if name not in files: raise VerificationError("MISSING_PACKAGE_FILE:" + name)
    try: return json.loads(files[name].decode("utf-8"))
    except Exception as exc: raise VerificationError("INVALID_JSON:" + name) from exc


def rational(value: Fraction | int) -> Dict[str, Any]:
    item = value if isinstance(value, Fraction) else Fraction(value, 1)
    return {"type": "EXACT_RATIONAL", "numerator": item.numerator, "denominator": item.denominator}


def boolean(value: bool) -> Dict[str, Any]: return {"type": "BOOLEAN", "value": bool(value)}

def symbol(name: str) -> Dict[str, Any]:
    return {"type": "ORDERED_PRODUCT" if len(name) == 2 and name.isascii() and name.isalpha() else "SYMBOL", "name": name}

def expression(operator: str, operands: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return {"type": "SYMBOLIC_EXPRESSION", "operator": operator, "operands": [stable(x) for x in operands]}

def fraction_of(value: Mapping[str, Any]):
    return Fraction(int(value["numerator"]), int(value["denominator"])) if value.get("type") == "EXACT_RATIONAL" else None

def contains_symbol(value: Mapping[str, Any], name: str) -> bool:
    if value.get("type") in {"SYMBOL", "ORDERED_PRODUCT"}: return value.get("name") == name
    return any(contains_symbol(x, name) for x in value.get("operands", []))


def eval_node(node: ast.AST, bindings: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool): return boolean(node.value)
        if isinstance(node.value, int) and not isinstance(node.value, bool): return rational(node.value)
        raise VerificationError("REJECT_NON_EXACT_LITERAL")
    if isinstance(node, ast.Name): return deepcopy(bindings.get(node.id, symbol(node.id)))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = eval_node(node.operand, bindings); frac = fraction_of(value)
        if frac is not None: return rational(frac if isinstance(node.op, ast.UAdd) else -frac)
        return expression("UNARY_PLUS" if isinstance(node.op, ast.UAdd) else "UNARY_MINUS", [value])
    if isinstance(node, ast.BinOp):
        left, right = eval_node(node.left, bindings), eval_node(node.right, bindings)
        lf, rf = fraction_of(left), fraction_of(right)
        if isinstance(node.op, ast.Add): return rational(lf + rf) if lf is not None and rf is not None else expression("ADD", [left, right])
        if isinstance(node.op, ast.Sub): return rational(lf - rf) if lf is not None and rf is not None else expression("SUBTRACT", [left, right])
        if isinstance(node.op, ast.Mult): return rational(lf * rf) if lf is not None and rf is not None else expression("MULTIPLY", [left, right])
        if isinstance(node.op, ast.Div):
            if rf is not None and rf == 0: raise VerificationError("REJECT_DIVISION_BY_ZERO")
            return rational(lf / rf) if lf is not None and rf is not None else expression("DIVIDE", [left, right])
        if isinstance(node.op, ast.Pow):
            if rf is None or rf.denominator != 1: raise VerificationError("REJECT_NONINTEGER_EXPONENT")
            exponent = int(rf)
            if lf is not None:
                if lf == 0 and exponent < 0: raise VerificationError("REJECT_DIVISION_BY_ZERO")
                return rational(lf ** exponent)
            return expression("POWER", [left, right])
    raise VerificationError("REJECT_UNSUPPORTED_EXPRESSION_NODE:" + type(node).__name__)


def evaluate_term(text: str, bindings: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    value = text.strip()
    if value.lower() == "true": return boolean(True)
    if value.lower() == "false": return boolean(False)
    try: tree = ast.parse(value, mode="eval")
    except SyntaxError as exc: raise VerificationError("REJECT_EXPRESSION_SYNTAX:" + value) from exc
    return stable(eval_node(tree.body, bindings))


def bare_bindable(term: str, bindings: Mapping[str, Mapping[str, Any]]) -> str:
    try: tree = ast.parse(term.strip(), mode="eval")
    except SyntaxError: return ""
    if isinstance(tree.body, ast.Name) and tree.body.id not in bindings:
        name = tree.body.id
        if len(name) == 2 and name.isascii() and name.isalpha(): return ""
        return name
    return ""


def equality(operands: Sequence[str], bindings: MutableMapping[str, Dict[str, Any]]) -> Dict[str, Any]:
    if len(operands) < 2: raise VerificationError("REJECT_EQUALITY_REQUIRES_TWO_OPERANDS")
    observations = []
    for lt, rt in zip(operands, operands[1:]):
        ln, rn = bare_bindable(lt, bindings), bare_bindable(rt, bindings)
        left, right = evaluate_term(lt, bindings), evaluate_term(rt, bindings)
        if ln and not contains_symbol(right, ln): bindings[ln] = stable(right); left = stable(right); action = "BOUND_LEFT_SYMBOL"
        elif rn and not contains_symbol(left, rn): bindings[rn] = stable(left); right = stable(left); action = "BOUND_RIGHT_SYMBOL"
        else: action = "COMPARED_EXISTING_VALUES"
        equal = stable(left) == stable(right)
        observations.append(stable({"left_text": lt, "right_text": rt, "left_value": left, "right_value": right, "action": action, "equal": equal}))
        if not equal: return {"satisfied": False, "observations": observations, "diagnostic": "EQUALITY_NOT_SATISFIED"}
    return {"satisfied": True, "observations": observations}


def distinctness(operands: Sequence[str], bindings: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    if len(operands) < 2: raise VerificationError("REJECT_DISTINCTNESS_REQUIRES_TWO_OPERANDS")
    observations = []
    for lt, rt in zip(operands, operands[1:]):
        left, right = evaluate_term(lt, bindings), evaluate_term(rt, bindings)
        distinct = stable(left) != stable(right)
        observations.append(stable({"left_text": lt, "right_text": rt, "left_value": left, "right_value": right, "distinct": distinct}))
        if not distinct: return {"satisfied": False, "observations": observations, "diagnostic": "DISTINCTNESS_NOT_SATISFIED"}
    return {"satisfied": True, "observations": observations}


def verify_executable_ir(value: Mapping[str, Any]) -> bool:
    if value.get("schema") != "HHS_EXECUTABLE_IR_V1" or not verify_rooted("pass076_executable_ir", value, "executable_ir_root_hash72"): return False
    def valid(item):
        return item.get("schema") == "HHS_EXECUTABLE_IR_STATEMENT_V1" and verify_rooted("pass076_executable_statement", item, "statement_root_hash72") and all(valid(x) for x in item.get("children", []))
    return all(valid(x) for x in value.get("statements", []))


def flatten_executable(executable_ir: Mapping[str, Any]) -> List[Dict[str, Any]]:
    gates = {str(x.get("name")): x for x in executable_ir.get("statements", []) if x.get("operation") == "DEFINE_GATE"}
    plan = []
    def append(statement, stack=()):
        operation = statement.get("operation"); plan.append(stable({k: deepcopy(v) for k, v in statement.items() if k != "children"}))
        if operation == "INVOKE_GATE":
            name = str(statement.get("name") or "")
            if name not in gates or name in stack: raise VerificationError("INVALID_GATE_PLAN")
            for child in gates[name].get("children", []): append(child, (*stack, name))
    for statement in executable_ir.get("statements", []): append(statement)
    return plan


def update_invariants(state: MutableMapping[str, Any]) -> None:
    for name, expected in EXPECTED_INVARIANTS.items():
        value = state["bindings"].get(name)
        state["invariant_status"][name] = "SATISFIED" if value is not None and stable(value) == stable(expected) else "UNRESOLVED_OR_FAILED"


def execute_reference(run_id: str, executable_ir: Mapping[str, Any]) -> Dict[str, Any]:
    if not verify_executable_ir(executable_ir): raise VerificationError("INVALID_EXECUTABLE_IR")
    plan = flatten_executable(executable_ir)
    state = {
        "schema": "HHS_HARMONICODE_INTERPRETER_STATE_V1", "version": "HHS_EXACT_SYMBOLIC_INTERPRETER_PASS_076_V1",
        "run_id": run_id, "executable_ir_ref": executable_ir.get("executable_ir_id"), "executable_ir_root_hash72": executable_ir.get("executable_ir_root_hash72"),
        "program_counter": 0, "step_count": 0, "plan_length": len(plan), "status": "READY", "bindings": {}, "defined_gates": {},
        "invariant_status": {name: "UNRESOLVED" for name in EXPECTED_INVARIANTS}, "diagnostics": [], "previous_state_root_hash72": "GENESIS",
        "external_effects_executed": False, "foundation_mutated": False,
    }
    state = rooted("pass076_interpreter_state", state, "state_root_hash72"); initial = state["state_root_hash72"]; receipts = []
    for statement in plan:
        body = deepcopy(state); previous = body.pop("state_root_hash72"); pc = body["program_counter"]
        operation = statement.get("operation")
        if operation == "DEFINE_GATE":
            name = str(statement.get("name") or ""); body["defined_gates"][name] = statement.get("statement_root_hash72"); outcome = {"satisfied": True, "gate_defined": name}
        elif operation == "INVOKE_GATE":
            name = str(statement.get("name") or ""); outcome = {"satisfied": name in body["defined_gates"], "gate_invoked": name}
            if not outcome["satisfied"]: outcome["diagnostic"] = "GATE_NOT_DEFINED"
        elif operation == "EVALUATE_EQUALITY": outcome = equality(statement.get("operands", []), body["bindings"])
        elif operation == "EVALUATE_DISTINCTNESS": outcome = distinctness(statement.get("operands", []), body["bindings"])
        else: outcome = {"satisfied": True, "values": [evaluate_term(x, body["bindings"]) for x in statement.get("operands", [])]}
        body["program_counter"] = pc + 1; body["step_count"] += 1; body["previous_state_root_hash72"] = previous
        if not outcome.get("satisfied"):
            body["diagnostics"].append({"code": outcome.get("diagnostic", "INTERPRETER_CONSTRAINT_FAILED"), "statement_id": statement.get("statement_id"), "severity": "ERROR"}); body["status"] = "FAILED"
        elif body["program_counter"] >= len(plan):
            update_invariants(body)
            body["status"] = "CLOSED" if all(v == "SATISFIED" for v in body["invariant_status"].values()) else "FAILED"
            if body["status"] == "FAILED": body["diagnostics"].append({"code": "REQUIRED_INVARIANT_CLOSURE_FAILED", "severity": "ERROR", "invariant_status": stable(body["invariant_status"])})
        else: body["status"] = "RUNNING"; update_invariants(body)
        state = rooted("pass076_interpreter_state", body, "state_root_hash72")
        rb = {"schema": "HHS_INTERPRETER_STEP_RECEIPT_V1", "run_id": run_id, "step_index": state["step_count"], "program_counter_before": pc, "program_counter_after": state["program_counter"],
              "statement_id": statement.get("statement_id"), "statement_root_hash72": statement.get("statement_root_hash72"), "operation": operation,
              "previous_step_receipt_root_hash72": receipts[-1]["step_receipt_root_hash72"] if receipts else "GENESIS", "previous_state_root_hash72": previous,
              "resulting_state_root_hash72": state["state_root_hash72"], "outcome": stable(outcome), "status_after": state["status"], "external_effects_executed": False, "foundation_mutated": False}
        receipts.append(rooted("pass076_interpreter_step_receipt", rb, "step_receipt_root_hash72"))
        if state["status"] == "FAILED": break
    run = {"schema": "HHS_INTERPRETER_EXECUTION_RUN_V1", "version": "HHS_EXACT_SYMBOLIC_INTERPRETER_PASS_076_V1", "run_id": run_id,
           "executable_ir_ref": executable_ir.get("executable_ir_id"), "executable_ir_root_hash72": executable_ir.get("executable_ir_root_hash72"), "initial_state_root_hash72": initial,
           "final_state": state, "step_receipts": receipts, "step_count": len(receipts), "status": state["status"], "closed": state["status"] == "CLOSED", "deterministic": True,
           "exact_arithmetic_only": True, "external_effects_executed": False, "foundation_mutated": False}
    return rooted("pass076_interpreter_run", run, "execution_run_root_hash72")


def decode_bytecode(data: bytes) -> Dict[str, Any]:
    if not data.startswith(BYTECODE_MAGIC): raise VerificationError("INVALID_BYTECODE_MAGIC")
    document = json.loads(data[len(BYTECODE_MAGIC):].decode("utf-8"))
    if canonical_bytes(document) != data[len(BYTECODE_MAGIC):]: raise VerificationError("NONCANONICAL_BYTECODE")
    return stable(document)


def execute_bytecode(run_id: str, artifact_id: str, artifact_root: str, data: bytes) -> Dict[str, Any]:
    document = decode_bytecode(data); instructions = document["instructions"]
    state = {"schema": "HHS_PORTABLE_BYTECODE_STATE_V1", "run_id": run_id, "artifact_ref": artifact_id, "artifact_root_hash72": artifact_root,
             "program_counter": 0, "step_count": 0, "status": "READY", "bindings": {}, "defined_gates": {},
             "invariant_status": {name: "UNRESOLVED" for name in EXPECTED_INVARIANTS}, "diagnostics": [], "external_effects_executed": False, "foundation_mutated": False}
    state["state_root_hash72"] = product_root("pass077_portable_bytecode_state", state); initial = state["state_root_hash72"]; receipts = []
    for instruction in instructions:
        before = state["state_root_hash72"]; body = deepcopy(state); body.pop("state_root_hash72", None); opcode = instruction.get("opcode")
        if opcode == "GATE_DECLARE":
            name = str(instruction.get("name") or ""); body["defined_gates"][name] = instruction.get("source_statement_root_hash72"); outcome = {"satisfied": bool(name), "gate_defined": name}
        elif opcode == "GATE_INVOKE":
            name = str(instruction.get("name") or ""); outcome = {"satisfied": name in body["defined_gates"], "gate_invoked": name}
            if not outcome["satisfied"]: outcome["diagnostic"] = "GATE_NOT_DEFINED"
        elif opcode == "RELATION_EQUAL": outcome = equality(instruction.get("operands", []), body["bindings"])
        elif opcode == "ORDERED_DISTINCT": outcome = distinctness(instruction.get("operands", []), body["bindings"])
        elif opcode == "EXPRESSION_EVAL": outcome = {"satisfied": True, "values": [evaluate_term(x, body["bindings"]) for x in instruction.get("operands", [])]}
        else: raise VerificationError("UNSUPPORTED_BYTECODE_OPCODE")
        body["program_counter"] += 1; body["step_count"] += 1; update_invariants(body)
        if not outcome.get("satisfied"): body["status"] = "FAILED"; body["diagnostics"].append({"code": outcome.get("diagnostic", "BYTECODE_CONSTRAINT_FAILED"), "severity": "ERROR"})
        elif body["program_counter"] == len(instructions):
            body["status"] = "CLOSED" if all(v == "SATISFIED" for v in body["invariant_status"].values()) else "FAILED"
            if body["status"] == "FAILED": body["diagnostics"].append({"code": "REQUIRED_INVARIANT_CLOSURE_FAILED", "severity": "ERROR"})
        else: body["status"] = "RUNNING"
        state = stable(body); state["state_root_hash72"] = product_root("pass077_portable_bytecode_state", state)
        rb = {"schema": "HHS_PORTABLE_BYTECODE_STEP_RECEIPT_V1", "run_id": run_id, "step_index": state["step_count"], "operation": opcode,
              "source_statement_root_hash72": instruction.get("source_statement_root_hash72"), "previous_step_receipt_root_hash72": receipts[-1]["step_receipt_root_hash72"] if receipts else "GENESIS",
              "previous_state_root_hash72": before, "resulting_state_root_hash72": state["state_root_hash72"], "outcome": stable(outcome), "status_after": state["status"]}
        receipts.append(rooted("pass077_bytecode_step_receipt", rb, "step_receipt_root_hash72"))
        if state["status"] == "FAILED": break
    run = {"schema": "HHS_PORTABLE_BYTECODE_EXECUTION_V1", "version": "HHS_PORTABLE_BYTECODE_VM_PASS_077_V1", "run_id": run_id,
           "compiled_artifact_ref": artifact_id, "compiled_artifact_root_hash72": artifact_root, "initial_state_root_hash72": initial, "final_state": state,
           "step_receipts": receipts, "step_count": len(receipts), "status": state["status"], "closed": state["status"] == "CLOSED", "deterministic": True,
           "exact_arithmetic_only": True, "external_effects_executed": False, "foundation_mutated": False}
    return rooted("pass077_portable_bytecode_execution", run, "compiled_execution_root_hash72")


def walk_statements(items: Iterable[Mapping[str, Any]]):
    for item in items: yield item; yield from walk_statements(item.get("children", []))

def sorted_unique(values):
    encoded = {json.dumps(stable(x), sort_keys=True, ensure_ascii=False, separators=(",", ":")): stable(x) for x in values}
    return [encoded[k] for k in sorted(encoded)]

def semantic_projection(execution: Mapping[str, Any], executable_ir: Mapping[str, Any]) -> Dict[str, Any]:
    state = execution["final_state"]; symbolic=[]; ordered=[]; reciprocal=[]; gates=[]
    for receipt in execution.get("step_receipts", []):
        op=receipt.get("operation"); outcome=receipt.get("outcome", {})
        if op in {"EVALUATE_EQUALITY", "RELATION_EQUAL"}:
            for obs in outcome.get("observations", []):
                rel=stable({"left_text":obs.get("left_text"),"right_text":obs.get("right_text"),"left_value":obs.get("left_value"),"right_value":obs.get("right_value"),"action":obs.get("action"),"equal":bool(obs.get("equal"))}); symbolic.append(rel)
                right=rel.get("right_value") or {}; operands=right.get("operands", []) if isinstance(right, dict) else []
                if right.get("type")=="SYMBOLIC_EXPRESSION" and right.get("operator")=="DIVIDE" and len(operands)==2 and operands[0]=={"type":"EXACT_RATIONAL","numerator":1,"denominator":1} and operands[1].get("type") in {"SYMBOL","ORDERED_PRODUCT"}:
                    reciprocal.append(stable({"bound_symbol":rel.get("left_text"),"reciprocal_of":operands[1].get("name"),"value":right}))
        elif op in {"EVALUATE_DISTINCTNESS", "ORDERED_DISTINCT"}:
            for obs in outcome.get("observations", []): ordered.append(stable({"left_text":obs.get("left_text"),"right_text":obs.get("right_text"),"left_value":obs.get("left_value"),"right_value":obs.get("right_value"),"distinct":bool(obs.get("distinct"))}))
        elif op in {"DEFINE_GATE","GATE_DECLARE"}: gates.append(stable({"operation":"DECLARE","gate":outcome.get("gate_defined"),"satisfied":bool(outcome.get("satisfied"))}))
        elif op in {"INVOKE_GATE","GATE_INVOKE"}: gates.append(stable({"operation":"INVOKE","gate":outcome.get("gate_invoked"),"satisfied":bool(outcome.get("satisfied"))}))
    statements=list(walk_statements(executable_ir.get("statements", [])))
    effects=sorted_unique(str(x.get("effect_declaration") or "") for x in statements)
    authority=sorted_unique(req for x in statements for req in x.get("authority_requirements", []))
    bindings=stable(state.get("bindings", {})); inv=stable(state.get("invariant_status", {}))
    body={"schema":"HHS_CANONICAL_PROGRAM_SEMANTIC_PROJECTION_V1","output_values":bindings,"symbolic_relations":sorted_unique(symbolic),"ordered_products":sorted_unique(ordered),
          "reciprocal_bindings":sorted_unique(reciprocal),"gate_results":gates,"zero_sum_closure":{"invariant":"Δe","status":inv.get("Δe"),"value":bindings.get("Δe"),"closed":inv.get("Δe")=="SATISFIED"},
          "required_invariants":{name:{"status":inv.get(name),"value":bindings.get(name)} for name in sorted(inv)},"declared_effects":effects,"authority_scope":authority,
          "source_identity":{"source_artifact_root_hash72":executable_ir.get("source_artifact_root_hash72"),"source_sha256":executable_ir.get("source_sha256"),"typed_ir_root_hash72":executable_ir.get("typed_ir_root_hash72"),"executable_ir_root_hash72":executable_ir.get("executable_ir_root_hash72")}}
    return rooted("pass077_canonical_program_semantic_projection", body, "semantic_projection_root_hash72")


def verify_package(path: str | Path) -> Dict[str, Any]:
    files=load_package(path)
    manifest=jload(files,"manifest/HHS_ARTIFACT_MANIFEST_V1.json")
    if not verify_rooted("pass077_artifact_manifest",manifest,"manifest_root_hash72"): raise VerificationError("MANIFEST_ROOT_MISMATCH")
    for item in manifest.get("files",[]):
        name=item["path"]
        if name not in files: raise VerificationError("MISSING_BOUND_FILE:"+name)
        if hashlib.sha256(files[name]).hexdigest()!=item["sha256"] or len(files[name])!=item["size_bytes"]: raise VerificationError("BOUND_FILE_DIGEST_MISMATCH:"+name)
    artifact=jload(files,"manifest/HHS_COMPILED_ARTIFACT_V1.json")
    if not verify_rooted("pass077_compiled_artifact",artifact,"artifact_root_hash72"): raise VerificationError("ARTIFACT_OBJECT_ROOT_MISMATCH")
    data=files["artifact/program.hhsbc"]
    if hashlib.sha256(data).hexdigest()!=artifact.get("artifact_content_sha256"): raise VerificationError("ARTIFACT_BYTE_DIGEST_MISMATCH")
    contract=jload(files,"manifest/HHS_TARGET_CONTRACT_V1.json")
    if product_root("pass077_compiler_target_contract",contract["contract"])!=contract.get("contract_root_hash72"): raise VerificationError("TARGET_CONTRACT_ROOT_MISMATCH")
    if contract["contract"].get("embedded_validator_self_authorizes") is not False: raise VerificationError("SELF_AUTHORIZATION_CLAIM")
    lineage=jload(files,"manifest/HHS_ARTIFACT_LINEAGE_CERTIFICATE_V1.json")
    if not verify_rooted("pass077_artifact_lineage_certificate",lineage,"lineage_root_hash72"): raise VerificationError("LINEAGE_ROOT_MISMATCH")
    if bool(lineage.get("genesis_source_root_hash72"))==bool(lineage.get("parent_artifact_root_hash72")): raise VerificationError("INVALID_GENESIS_PARENT_LINEAGE")
    if lineage.get("artifact_content_sha256")!=hashlib.sha256(data).hexdigest(): raise VerificationError("LINEAGE_ARTIFACT_DIGEST_MISMATCH")
    eq=jload(files,"receipts/equivalence_receipt.json")
    if not verify_rooted("pass077_interpreter_compiler_equivalence_receipt",eq,"receipt_root_hash72"): raise VerificationError("EQUIVALENCE_RECEIPT_ROOT_MISMATCH")
    if eq.get("status")!="SEMANTIC_IDENTITY_VERIFIED": raise VerificationError("RECORDED_EQUIVALENCE_NOT_VERIFIED")
    executable=jload(files,"reference/executable_ir.json")
    recorded_interpreter=jload(files,"reference/interpreter_execution.json")
    recorded_compiled=jload(files,"receipts/compiled_execution.json")
    reference=execute_reference(str(recorded_interpreter.get("run_id")),executable)
    compiled=execute_bytecode(str(recorded_compiled.get("run_id")),str(artifact.get("artifact_id")),artifact.get("artifact_payload_root_hash72"),data)
    reference_projection=semantic_projection(reference,executable); compiled_projection=semantic_projection(compiled,executable)
    semantic_match=reference_projection["semantic_projection_root_hash72"]==compiled_projection["semantic_projection_root_hash72"]
    recorded_reference_match=reference.get("execution_run_root_hash72")==recorded_interpreter.get("execution_run_root_hash72")
    # The packaged compiled execution preserves the original artifact object root.
    recorded_compiled_match=compiled.get("compiled_execution_root_hash72")==recorded_compiled.get("compiled_execution_root_hash72")
    expected=manifest.get("expected_semantic_projection_root_hash72")
    expected_match=reference_projection["semantic_projection_root_hash72"]==expected
    status="REEXECUTED_SEMANTIC_EQUIVALENCE" if semantic_match and recorded_reference_match and recorded_compiled_match and expected_match else "REJECTED"
    body={"schema":"HHS_INDEPENDENT_ARTIFACT_VERIFICATION_V1","status":status,"artifact_content_sha256":hashlib.sha256(data).hexdigest(),
          "target_contract_root_hash72":contract.get("contract_root_hash72"),"lineage_root_hash72":lineage.get("lineage_root_hash72"),
          "interpreter_execution_replayed":recorded_reference_match,"compiled_execution_replayed":recorded_compiled_match,
          "interpreter_semantic_projection_root_hash72":reference_projection["semantic_projection_root_hash72"],"compiled_semantic_projection_root_hash72":compiled_projection["semantic_projection_root_hash72"],
          "semantic_projection_roots_match":semantic_match,"expected_semantic_projection_matches":expected_match,"package_contents_only":True,"originating_repository_required":False,
          "originating_conversation_required":False,"development_agent_required":False,"self_authorization_accepted":False,"deployment_authority_conferred":False}
    return rooted("pass077_external_verification",body,"verification_root_hash72")


def main(argv: Sequence[str] | None = None) -> int:
    args=list(argv or sys.argv[1:])
    if len(args)!=1:
        print("usage: verify_artifact.py <extracted-package-directory-or-hhspkg>",file=sys.stderr); return 2
    try:
        result=verify_package(args[0]); print(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)); return 0 if result["status"]=="REEXECUTED_SEMANTIC_EQUIVALENCE" else 1
    except Exception as exc:
        print(json.dumps({"status":"REJECTED","error":str(exc)},indent=2,sort_keys=True),file=sys.stderr); return 1

if __name__=="__main__": raise SystemExit(main())
