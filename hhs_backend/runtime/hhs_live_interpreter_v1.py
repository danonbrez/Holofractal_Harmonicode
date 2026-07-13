"""HHS live interpreter surface for the Pass 049 Visual Runtime OS workspace."""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Mapping, Optional
import ast
import operator
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import VERSION, AUTHORITY, hash72

INTERPRETER_REQUEST_SCHEMA = "HHS_INTERPRETER_REQUEST_V1"
INTERPRETER_RESULT_SCHEMA = "HHS_INTERPRETER_RESULT_V1"

_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_ALLOWED_UNARY = {ast.UAdd: lambda x: x, ast.USub: lambda x: -x}


def _eval_fraction_node(node: ast.AST) -> Fraction:
    if isinstance(node, ast.Expression):
        return _eval_fraction_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return Fraction(node.value, 1)
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left = _eval_fraction_node(node.left)
        right = _eval_fraction_node(node.right)
        return _ALLOWED_BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_eval_fraction_node(node.operand))
    raise ValueError("REJECT_INTERPRETER_HOST_EVAL")


def build_interpreter_request(
    *,
    project_id: str,
    source_object_id: str,
    expression: str,
    input_state_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    request = {
        "schema": INTERPRETER_REQUEST_SCHEMA,
        "version": VERSION,
        "request_id": f"interpret:{uuid.uuid4().hex}",
        "project_id": project_id,
        "source_object_id": source_object_id,
        "expression_range": {"start": 0, "end": len(expression)},
        "expression_hash72": hash72("HHS_INTERPRETER_EXPRESSION_V1", expression),
        "input_state_ids": list(input_state_ids or []),
        "execution_mode": "AUTHORIZED_INTERPRET",
        "requested_outputs": ["VALUE", "STATE_TRANSITION", "WITNESS", "GRAPH_PROJECTION", "RECEIPT"],
        "requires_authority": True,
    }
    request["request_root_hash72"] = hash72(INTERPRETER_REQUEST_SCHEMA, request)
    return request


def interpret_expression(request: Mapping[str, Any], expression: str) -> Dict[str, Any]:
    reasons: List[str] = []
    if "__" in expression or "import" in expression or "eval" in expression or "open(" in expression:
        reasons.append("REJECT_INTERPRETER_HOST_EVAL")
    if any(ch.isalpha() for ch in expression.replace("Fraction", "")):
        # Pass 049 vertical slice only interprets exact integer/rational arithmetic.
        reasons.append("REJECT_UNDERIVED_PRIMITIVE")
    value: Optional[Fraction] = None
    if not reasons:
        try:
            value = _eval_fraction_node(ast.parse(expression, mode="eval"))
        except Exception:
            reasons.append("REJECT_INTERPRETER_HOST_EVAL")
    if reasons:
        rejection = {
            "schema": INTERPRETER_RESULT_SCHEMA,
            "version": VERSION,
            "ok": False,
            "status": "INTERPRETER_REJECTED",
            "request_id": request.get("request_id"),
            "reasons": sorted(dict.fromkeys(reasons)),
            "witnessed_rejection": True,
        }
        rejection["result_root_hash72"] = hash72("HHS_INTERPRETER_REJECTION_V1", rejection)
        return rejection
    assert value is not None
    exact = {"numerator": value.numerator, "denominator": value.denominator}
    transition = {
        "schema": "HHS_INTERPRETER_STATE_TRANSITION_V1",
        "pre_state_root_hash72": hash72("HHS_INTERPRETER_PRE_STATE_V1", request),
        "operation": "interpret.execute",
        "post_state_root_hash72": hash72("HHS_INTERPRETER_POST_STATE_V1", exact),
    }
    transition["transition_hash72"] = hash72("HHS_INTERPRETER_STATE_TRANSITION_V1", transition)
    receipt = {
        "schema": "HHS_INTERPRETER_RECEIPT_V1",
        "request_id": request.get("request_id"),
        "transition_hash72": transition["transition_hash72"],
        "authority": AUTHORITY,
    }
    receipt["receipt_hash72"] = hash72("HHS_INTERPRETER_RECEIPT_V1", receipt)
    result = {
        "schema": INTERPRETER_RESULT_SCHEMA,
        "version": VERSION,
        "ok": True,
        "status": "INTERPRETER_RESULT",
        "request_id": request.get("request_id"),
        "exact_symbolic_value": exact,
        "display_value": f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator),
        "floating_point_is_display_only": True,
        "transition_witness": transition,
        "graph_projection": {"node_type": "INTERPRETER_RESULT", "value_root_hash72": hash72("HHS_INTERPRETER_VALUE_V1", exact)},
        "execution_receipt": receipt,
    }
    result["result_root_hash72"] = hash72(INTERPRETER_RESULT_SCHEMA, result)
    return result


def live_interpreter_self_test() -> Dict[str, Any]:
    request = build_interpreter_request(project_id="project:pass049", source_object_id="object:expr", expression="1+2*3/4")
    result = interpret_expression(request, "1+2*3/4")
    rejected = interpret_expression(request, "__import__('os').system('echo unsafe')")
    return {
        "schema": "HHS_LIVE_INTERPRETER_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(result.get("ok") and not rejected.get("ok") and result.get("exact_symbolic_value", {}).get("numerator") == 5),
        "request": request,
        "result": result,
        "host_eval_rejection": rejected,
        "constraint": "NO_ARBITRARY_HOST_LANGUAGE_EVALUATION",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(live_interpreter_self_test(), indent=2, sort_keys=True, default=str))
