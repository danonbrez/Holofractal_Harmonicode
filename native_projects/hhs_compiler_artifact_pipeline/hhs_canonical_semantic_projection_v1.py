"""Canonical semantic projection shared by interpreter and compiled paths."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable

from .hhs_pass077_contracts_v1 import SEMANTIC_FIELDS, SEMANTIC_PROJECTION_SCHEMA, rooted, verify_rooted


def _walk_statements(items: Iterable[Mapping[str, Any]]) -> Iterable[Mapping[str, Any]]:
    for item in items:
        yield item
        yield from _walk_statements(item.get("children", []))


def _sorted_unique(values: Iterable[Any]) -> List[Any]:
    encoded: Dict[str, Any] = {}
    import json
    for value in values:
        current = stable(value)
        encoded[json.dumps(current, sort_keys=True, ensure_ascii=False, separators=(",", ":"))] = current
    return [encoded[key] for key in sorted(encoded)]


def _relations(step_receipts: Iterable[Mapping[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    symbolic: List[Dict[str, Any]] = []
    ordered: List[Dict[str, Any]] = []
    reciprocal: List[Dict[str, Any]] = []
    gates: List[Dict[str, Any]] = []
    for receipt in step_receipts:
        operation = str(receipt.get("operation") or "")
        outcome = receipt.get("outcome", {})
        if operation in {"EVALUATE_EQUALITY", "RELATION_EQUAL"}:
            for observation in outcome.get("observations", []):
                relation = stable({
                    "left_text": observation.get("left_text"),
                    "right_text": observation.get("right_text"),
                    "left_value": observation.get("left_value"),
                    "right_value": observation.get("right_value"),
                    "action": observation.get("action"),
                    "equal": bool(observation.get("equal")),
                })
                symbolic.append(relation)
                right = relation.get("right_value") or {}
                operands = right.get("operands", []) if isinstance(right, dict) else []
                if (
                    right.get("type") == "SYMBOLIC_EXPRESSION"
                    and right.get("operator") == "DIVIDE"
                    and len(operands) == 2
                    and operands[0] == {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
                    and operands[1].get("type") in {"SYMBOL", "ORDERED_PRODUCT"}
                ):
                    reciprocal.append(stable({
                        "bound_symbol": relation.get("left_text"),
                        "reciprocal_of": operands[1].get("name"),
                        "value": right,
                    }))
        elif operation in {"EVALUATE_DISTINCTNESS", "ORDERED_DISTINCT"}:
            for observation in outcome.get("observations", []):
                ordered.append(stable({
                    "left_text": observation.get("left_text"),
                    "right_text": observation.get("right_text"),
                    "left_value": observation.get("left_value"),
                    "right_value": observation.get("right_value"),
                    "distinct": bool(observation.get("distinct")),
                }))
        elif operation in {"DEFINE_GATE", "GATE_DECLARE"}:
            gates.append(stable({"operation": "DECLARE", "gate": outcome.get("gate_defined"), "satisfied": bool(outcome.get("satisfied"))}))
        elif operation in {"INVOKE_GATE", "GATE_INVOKE"}:
            gates.append(stable({"operation": "INVOKE", "gate": outcome.get("gate_invoked"), "satisfied": bool(outcome.get("satisfied"))}))
    return {
        "symbolic_relations": _sorted_unique(symbolic),
        "ordered_products": _sorted_unique(ordered),
        "reciprocal_bindings": _sorted_unique(reciprocal),
        "gate_results": gates,
    }


def canonical_semantic_projection(*, execution: Mapping[str, Any], executable_ir: Mapping[str, Any]) -> Dict[str, Any]:
    state = deepcopy(dict(execution.get("final_state", {})))
    if not state:
        raise ContractError("REJECT_SEMANTIC_PROJECTION_WITHOUT_FINAL_STATE")
    relation_fields = _relations(execution.get("step_receipts", []))
    statements = list(_walk_statements(executable_ir.get("statements", [])))
    declared_effects = _sorted_unique(str(item.get("effect_declaration") or "") for item in statements)
    authority_scope = _sorted_unique(
        requirement
        for item in statements
        for requirement in item.get("authority_requirements", [])
    )
    bindings = stable(state.get("bindings", {}))
    invariant_status = stable(state.get("invariant_status", {}))
    required_invariants = {
        name: {"status": invariant_status.get(name), "value": bindings.get(name)}
        for name in sorted(invariant_status)
    }
    body = {
        "schema": SEMANTIC_PROJECTION_SCHEMA,
        "output_values": bindings,
        **relation_fields,
        "zero_sum_closure": {
            "invariant": "Δe",
            "status": invariant_status.get("Δe"),
            "value": bindings.get("Δe"),
            "closed": invariant_status.get("Δe") == "SATISFIED",
        },
        "required_invariants": required_invariants,
        "declared_effects": declared_effects,
        "authority_scope": authority_scope,
        "source_identity": {
            "source_artifact_root_hash72": executable_ir.get("source_artifact_root_hash72"),
            "source_sha256": executable_ir.get("source_sha256"),
            "typed_ir_root_hash72": executable_ir.get("typed_ir_root_hash72"),
            "executable_ir_root_hash72": executable_ir.get("executable_ir_root_hash72"),
        },
    }
    if tuple(sorted(k for k in body if k != "schema")) != tuple(sorted(SEMANTIC_FIELDS)):
        raise ContractError("REJECT_SEMANTIC_PROJECTION_FIELD_SET")
    return rooted("pass077_canonical_program_semantic_projection", body, "semantic_projection_root_hash72")


def verify_semantic_projection(value: Mapping[str, Any]) -> bool:
    return (
        value.get("schema") == SEMANTIC_PROJECTION_SCHEMA
        and all(field in value for field in SEMANTIC_FIELDS)
        and verify_rooted("pass077_canonical_program_semantic_projection", value, "semantic_projection_root_hash72")
    )


def compare_semantic_projections(*, interpreter: Mapping[str, Any], compiled: Mapping[str, Any]) -> List[Dict[str, Any]]:
    if not verify_semantic_projection(interpreter) or not verify_semantic_projection(compiled):
        raise ContractError("REJECT_INVALID_SEMANTIC_PROJECTION")
    comparisons = []
    codes = {
        "ordered_products": "REJECT_OPTIMIZATION_ORDERED_PRODUCT_CHANGE",
        "reciprocal_bindings": "REJECT_OPTIMIZATION_RECIPROCAL_DROP",
        "output_values": "REJECT_OPTIMIZATION_RATIONAL_MISMATCH",
        "authority_scope": "REJECT_AUTHORITY_SCOPE_MUTATION",
        "source_identity": "REJECT_SOURCE_IDENTITY_SUBSTITUTION",
    }
    for field in SEMANTIC_FIELDS:
        left, right = stable(interpreter.get(field)), stable(compiled.get(field))
        match = left == right
        item = {
            "field": field,
            "interpreter_value_root_hash72": product_root("pass077_semantic_field", {"field": field, "value": left}),
            "compiled_value_root_hash72": product_root("pass077_semantic_field", {"field": field, "value": right}),
            "match": match,
        }
        if not match:
            item["rejection_code"] = codes.get(field, "REJECT_INTERPRETER_COMPILER_SEMANTIC_DIVERGENCE")
        comparisons.append(stable(item))
    return comparisons
