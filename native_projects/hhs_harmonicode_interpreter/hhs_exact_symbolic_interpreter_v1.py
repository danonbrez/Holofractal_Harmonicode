"""Exact, bounded, receipt-producing interpreter for HHS_EXECUTABLE_IR_V1."""
from __future__ import annotations

import ast
from copy import deepcopy
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable

from .hhs_executable_ir_v1 import verify_executable_ir
from .hhs_pass076_contracts_v1 import (
    INTERPRETER_RUN_SCHEMA,
    INTERPRETER_STATE_SCHEMA,
    INTERPRETER_STEP_RECEIPT_SCHEMA,
    MAX_EXECUTION_STEPS,
    REQUIRED_INVARIANT_EXPECTATIONS,
    rooted,
    verify_rooted,
)

INTERPRETER_VERSION = "HHS_EXACT_SYMBOLIC_INTERPRETER_PASS_076_V1"


def rational(value: Fraction | int) -> Dict[str, Any]:
    item = value if isinstance(value, Fraction) else Fraction(value, 1)
    return {"type": "EXACT_RATIONAL", "numerator": item.numerator, "denominator": item.denominator}


def boolean(value: bool) -> Dict[str, Any]:
    return {"type": "BOOLEAN", "value": bool(value)}


def symbol(name: str) -> Dict[str, Any]:
    kind = "ORDERED_PRODUCT" if len(name) == 2 and name.isascii() and name.isalpha() else "SYMBOL"
    return {"type": kind, "name": name}


def expression(operator: str, operands: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return {"type": "SYMBOLIC_EXPRESSION", "operator": operator, "operands": [stable(x) for x in operands]}


def _fraction(value: Mapping[str, Any]) -> Fraction | None:
    if value.get("type") == "EXACT_RATIONAL":
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    return None


def _value_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return stable(left) == stable(right)


def _contains_symbol(value: Mapping[str, Any], name: str) -> bool:
    if value.get("type") in {"SYMBOL", "ORDERED_PRODUCT"}:
        return value.get("name") == name
    return any(_contains_symbol(x, name) for x in value.get("operands", []))


def _eval_node(node: ast.AST, bindings: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            return boolean(node.value)
        if isinstance(node.value, int) and not isinstance(node.value, bool):
            return rational(node.value)
        raise ContractError("REJECT_NON_EXACT_LITERAL")
    if isinstance(node, ast.Name):
        return deepcopy(bindings.get(node.id, symbol(node.id)))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _eval_node(node.operand, bindings)
        frac = _fraction(value)
        if frac is not None:
            return rational(frac if isinstance(node.op, ast.UAdd) else -frac)
        return expression("UNARY_PLUS" if isinstance(node.op, ast.UAdd) else "UNARY_MINUS", [value])
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left, bindings)
        right = _eval_node(node.right, bindings)
        lf, rf = _fraction(left), _fraction(right)
        if isinstance(node.op, ast.Add):
            return rational(lf + rf) if lf is not None and rf is not None else expression("ADD", [left, right])
        if isinstance(node.op, ast.Sub):
            return rational(lf - rf) if lf is not None and rf is not None else expression("SUBTRACT", [left, right])
        if isinstance(node.op, ast.Mult):
            return rational(lf * rf) if lf is not None and rf is not None else expression("MULTIPLY", [left, right])
        if isinstance(node.op, ast.Div):
            if rf is not None and rf == 0:
                raise ContractError("REJECT_DIVISION_BY_ZERO")
            return rational(lf / rf) if lf is not None and rf is not None else expression("DIVIDE", [left, right])
        if isinstance(node.op, ast.Pow):
            if rf is None or rf.denominator != 1:
                raise ContractError("REJECT_NONINTEGER_EXPONENT")
            exponent = int(rf)
            if lf is not None:
                if lf == 0 and exponent < 0:
                    raise ContractError("REJECT_DIVISION_BY_ZERO")
                return rational(lf ** exponent)
            return expression("POWER", [left, right])
    raise ContractError(f"REJECT_UNSUPPORTED_EXPRESSION_NODE:{type(node).__name__}")


def evaluate_term(text: str, bindings: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    value = text.strip()
    if value.lower() == "true":
        return boolean(True)
    if value.lower() == "false":
        return boolean(False)
    try:
        tree = ast.parse(value, mode="eval")
    except SyntaxError as exc:
        raise ContractError(f"REJECT_EXPRESSION_SYNTAX:{value}") from exc
    return stable(_eval_node(tree.body, bindings))


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


def _evaluate_equality(operands: Sequence[str], bindings: MutableMapping[str, Dict[str, Any]]) -> Dict[str, Any]:
    if len(operands) < 2:
        raise ContractError("REJECT_EQUALITY_REQUIRES_TWO_OPERANDS")
    observations: List[Dict[str, Any]] = []
    for left_text, right_text in zip(operands, operands[1:]):
        left_name = _bare_bindable_symbol(left_text, bindings)
        right_name = _bare_bindable_symbol(right_text, bindings)
        left = evaluate_term(left_text, bindings)
        right = evaluate_term(right_text, bindings)
        if left_name and not _contains_symbol(right, left_name):
            bindings[left_name] = stable(right)
            left = stable(right)
            action = "BOUND_LEFT_SYMBOL"
        elif right_name and not _contains_symbol(left, right_name):
            bindings[right_name] = stable(left)
            right = stable(left)
            action = "BOUND_RIGHT_SYMBOL"
        else:
            action = "COMPARED_EXISTING_VALUES"
        equal = _value_equal(left, right)
        observations.append({
            "left_text": left_text,
            "right_text": right_text,
            "left_value": left,
            "right_value": right,
            "action": action,
            "equal": equal,
        })
        if not equal:
            return {"satisfied": False, "observations": observations, "diagnostic": "EQUALITY_NOT_SATISFIED"}
    return {"satisfied": True, "observations": observations}


def _evaluate_distinctness(operands: Sequence[str], bindings: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    if len(operands) < 2:
        raise ContractError("REJECT_DISTINCTNESS_REQUIRES_TWO_OPERANDS")
    observations = []
    for left_text, right_text in zip(operands, operands[1:]):
        left, right = evaluate_term(left_text, bindings), evaluate_term(right_text, bindings)
        distinct = not _value_equal(left, right)
        observations.append({"left_text": left_text, "right_text": right_text, "left_value": left, "right_value": right, "distinct": distinct})
        if not distinct:
            return {"satisfied": False, "observations": observations, "diagnostic": "DISTINCTNESS_NOT_SATISFIED"}
    return {"satisfied": True, "observations": observations}


def _flatten_plan(executable_ir: Mapping[str, Any]) -> List[Dict[str, Any]]:
    gates = {str(x.get("name")): x for x in executable_ir.get("statements", []) if x.get("operation") == "DEFINE_GATE"}
    plan: List[Dict[str, Any]] = []

    def append_statement(statement: Mapping[str, Any], stack: Tuple[str, ...] = ()) -> None:
        operation = statement.get("operation")
        item = {k: deepcopy(v) for k, v in statement.items() if k != "children"}
        plan.append(stable(item))
        if operation == "INVOKE_GATE":
            name = str(statement.get("name") or "")
            if name not in gates:
                raise ContractError(f"REJECT_UNKNOWN_GATE_INVOCATION:{name}")
            if name in stack:
                raise ContractError(f"REJECT_RECURSIVE_GATE_CYCLE:{name}")
            for child in gates[name].get("children", []):
                append_statement(child, (*stack, name))

    for statement in executable_ir.get("statements", []):
        append_statement(statement)
    if len(plan) > MAX_EXECUTION_STEPS:
        raise ContractError("REJECT_EXECUTION_PLAN_EXCEEDS_BOUND")
    return plan


def _state_body(run_id: str, executable_ir: Mapping[str, Any], plan: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return {
        "schema": INTERPRETER_STATE_SCHEMA,
        "version": INTERPRETER_VERSION,
        "run_id": run_id,
        "executable_ir_ref": executable_ir.get("executable_ir_id"),
        "executable_ir_root_hash72": executable_ir.get("executable_ir_root_hash72"),
        "program_counter": 0,
        "step_count": 0,
        "plan_length": len(plan),
        "status": "READY",
        "bindings": {},
        "defined_gates": {},
        "invariant_status": {name: "UNRESOLVED" for name in REQUIRED_INVARIANT_EXPECTATIONS},
        "diagnostics": [],
        "previous_state_root_hash72": "GENESIS",
        "external_effects_executed": False,
        "foundation_mutated": False,
    }


def initialize_state(run_id: str, executable_ir: Mapping[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    if not verify_executable_ir(executable_ir):
        raise ContractError("REJECT_INVALID_EXECUTABLE_IR")
    if executable_ir.get("unsupported_effects"):
        raise ContractError("REJECT_PASS076_UNSUPPORTED_EFFECT")
    plan = _flatten_plan(executable_ir)
    state = rooted("pass076_interpreter_state", _state_body(run_id, executable_ir, plan), "state_root_hash72")
    return state, plan


def _update_invariants(state: MutableMapping[str, Any]) -> None:
    for name, expected in REQUIRED_INVARIANT_EXPECTATIONS.items():
        value = state["bindings"].get(name)
        state["invariant_status"][name] = "SATISFIED" if value is not None and _value_equal(value, expected) else "UNRESOLVED_OR_FAILED"


def execute_step(state: Mapping[str, Any], plan: Sequence[Mapping[str, Any]], *, previous_step_receipt_root_hash72: str = "GENESIS") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not verify_rooted("pass076_interpreter_state", state, "state_root_hash72"):
        raise ContractError("REJECT_INTERPRETER_STATE_ROOT_MISMATCH")
    current = deepcopy(dict(state))
    previous_root = str(current.pop("state_root_hash72"))
    pc = int(current["program_counter"])
    if current.get("status") in {"CLOSED", "FAILED", "BOUNDED_STOP"}:
        raise ContractError("REJECT_STEP_AFTER_TERMINAL_STATE")
    if pc >= len(plan):
        raise ContractError("REJECT_STEP_OUTSIDE_EXECUTION_PLAN")
    statement = deepcopy(dict(plan[pc]))
    operation = str(statement.get("operation"))
    outcome: Dict[str, Any]
    if operation == "DEFINE_GATE":
        name = str(statement.get("name") or "")
        if not name:
            raise ContractError("REJECT_GATE_WITHOUT_NAME")
        current["defined_gates"][name] = statement.get("statement_root_hash72")
        outcome = {"satisfied": True, "gate_defined": name}
    elif operation == "INVOKE_GATE":
        name = str(statement.get("name") or "")
        outcome = {"satisfied": name in current["defined_gates"], "gate_invoked": name}
        if not outcome["satisfied"]:
            outcome["diagnostic"] = "GATE_NOT_DEFINED"
    elif operation == "EVALUATE_EQUALITY":
        outcome = _evaluate_equality(statement.get("operands", []), current["bindings"])
    elif operation == "EVALUATE_DISTINCTNESS":
        outcome = _evaluate_distinctness(statement.get("operands", []), current["bindings"])
    else:
        values = [evaluate_term(x, current["bindings"]) for x in statement.get("operands", [])]
        outcome = {"satisfied": True, "values": values}
    current["program_counter"] = pc + 1
    current["step_count"] = int(current["step_count"]) + 1
    current["previous_state_root_hash72"] = previous_root
    if not outcome.get("satisfied", False):
        diagnostic = {"code": str(outcome.get("diagnostic") or "INTERPRETER_CONSTRAINT_FAILED"), "statement_id": statement.get("statement_id"), "severity": "ERROR"}
        current["diagnostics"].append(diagnostic)
        current["status"] = "FAILED"
    elif current["program_counter"] >= len(plan):
        _update_invariants(current)
        if all(value == "SATISFIED" for value in current["invariant_status"].values()):
            current["status"] = "CLOSED"
        else:
            current["status"] = "FAILED"
            current["diagnostics"].append({"code": "REQUIRED_INVARIANT_CLOSURE_FAILED", "severity": "ERROR", "invariant_status": stable(current["invariant_status"])})
    else:
        current["status"] = "RUNNING"
        _update_invariants(current)
    final = rooted("pass076_interpreter_state", current, "state_root_hash72")
    receipt_body = {
        "schema": INTERPRETER_STEP_RECEIPT_SCHEMA,
        "run_id": current["run_id"],
        "step_index": current["step_count"],
        "program_counter_before": pc,
        "program_counter_after": current["program_counter"],
        "statement_id": statement.get("statement_id"),
        "statement_root_hash72": statement.get("statement_root_hash72"),
        "operation": operation,
        "previous_step_receipt_root_hash72": previous_step_receipt_root_hash72,
        "previous_state_root_hash72": previous_root,
        "resulting_state_root_hash72": final["state_root_hash72"],
        "outcome": stable(outcome),
        "status_after": final["status"],
        "external_effects_executed": False,
        "foundation_mutated": False,
    }
    receipt = rooted("pass076_interpreter_step_receipt", receipt_body, "step_receipt_root_hash72")
    return final, receipt


def execute_program(*, run_id: str, executable_ir: Mapping[str, Any], max_steps: int = MAX_EXECUTION_STEPS) -> Dict[str, Any]:
    if max_steps <= 0 or max_steps > MAX_EXECUTION_STEPS:
        raise ContractError("REJECT_INVALID_EXECUTION_STEP_BOUND")
    state, plan = initialize_state(run_id, executable_ir)
    initial_root = state["state_root_hash72"]
    receipts: List[Dict[str, Any]] = []
    while state["status"] not in {"CLOSED", "FAILED"} and len(receipts) < max_steps:
        previous_receipt = receipts[-1]["step_receipt_root_hash72"] if receipts else "GENESIS"
        state, receipt = execute_step(state, plan, previous_step_receipt_root_hash72=previous_receipt)
        receipts.append(receipt)
    if state["status"] not in {"CLOSED", "FAILED"}:
        body = deepcopy(dict(state))
        body.pop("state_root_hash72", None)
        body["status"] = "BOUNDED_STOP"
        body["diagnostics"].append({"code": "EXECUTION_STEP_BOUND_REACHED", "severity": "ERROR"})
        state = rooted("pass076_interpreter_state", body, "state_root_hash72")
    run_body = {
        "schema": INTERPRETER_RUN_SCHEMA,
        "version": INTERPRETER_VERSION,
        "run_id": run_id,
        "executable_ir_ref": executable_ir.get("executable_ir_id"),
        "executable_ir_root_hash72": executable_ir.get("executable_ir_root_hash72"),
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
    return rooted("pass076_interpreter_run", run_body, "execution_run_root_hash72")


def replay_execution(run: Mapping[str, Any], executable_ir: Mapping[str, Any]) -> Dict[str, Any]:
    if not verify_rooted("pass076_interpreter_run", run, "execution_run_root_hash72"):
        raise ContractError("REJECT_EXECUTION_RUN_ROOT_MISMATCH")
    observed = execute_program(run_id=str(run.get("run_id")), executable_ir=executable_ir, max_steps=max(MAX_EXECUTION_STEPS, int(run.get("step_count", 0))))
    matches = observed.get("execution_run_root_hash72") == run.get("execution_run_root_hash72")
    body = {
        "schema": "HHS_INTERPRETER_REPLAY_VERIFICATION_V1",
        "run_id": run.get("run_id"),
        "expected_execution_root_hash72": run.get("execution_run_root_hash72"),
        "observed_execution_root_hash72": observed.get("execution_run_root_hash72"),
        "matches": matches,
        "thread_context_used": False,
        "host_path_used_as_identity": False,
    }
    return rooted("pass076_interpreter_replay", body, "replay_verification_root_hash72")
