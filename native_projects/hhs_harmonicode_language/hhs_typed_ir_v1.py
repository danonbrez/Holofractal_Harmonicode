"""HHS_TYPED_IR_V1 construction and validation for Pass 075."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root, sha256, stable

from .hhs_pass075_contracts_v1 import (
    EFFECTS,
    LANGUAGE_VALIDATION_SCHEMA,
    REQUIRED_INVARIANT_BINDINGS,
    TYPE_IDS,
    TYPED_IR_SCHEMA,
)
from .hhs_harmonicode_parser_v1 import infer_type

IR_VERSION = "HHS_TYPED_IR_PASS_075_V1"


def _walk(nodes: Iterable[Mapping[str, Any]]) -> Iterable[Mapping[str, Any]]:
    for node in nodes:
        yield node
        yield from _walk(node.get("children", []))


def _symbol_table(ast: Mapping[str, Any]) -> List[Dict[str, Any]]:
    first_spans: Dict[str, Mapping[str, Any]] = {}
    counts: Dict[str, int] = {}
    for node in _walk(ast.get("nodes", [])):
        span = node.get("source_span", {})
        for symbol in node.get("symbols", []):
            counts[symbol] = counts.get(symbol, 0) + 1
            first_spans.setdefault(symbol, span)
    table = []
    for symbol in sorted(counts):
        item = {
            "schema": "HHS_TYPED_SYMBOL_V1",
            "symbol_id": f"symbol:{product_root('pass075_symbol_identity', {'symbol': symbol})[-20:]}",
            "spelling": symbol,
            "type_id": infer_type(symbol),
            "occurrence_count": counts[symbol],
            "first_source_span": stable(first_spans[symbol]),
            "symbol_identity_is_spelling_and_scope_bound_not_position_only": True,
        }
        item["symbol_root_hash72"] = product_root("pass075_typed_symbol", item)
        table.append(stable(item))
    return table


def _block_effect(node: Mapping[str, Any]) -> str:
    text = str(node.get("source_text") or "")
    lowered = text.lower()
    if "external(" in lowered or "@external" in lowered:
        return "EXTERNAL_DECLARED"
    if "set(" in lowered or "mutate(" in lowered or "@audited" in lowered:
        return "AUDIT_REQUIRED"
    return "PURE_SYMBOLIC"


def _authority_requirements(effect: str) -> List[str]:
    if effect == "PURE_SYMBOLIC":
        return []
    if effect == "AUDIT_REQUIRED":
        return ["ROLE_CONTRACT", "TASK_ASSIGNMENT", "CAPABILITY_LEASE", "KERNEL_AUDIT"]
    return ["ROLE_CONTRACT", "TASK_ASSIGNMENT", "CAPABILITY_LEASE", "EXTERNAL_PROVIDER_CONTRACT", "KERNEL_AUDIT"]


def _block(node: Mapping[str, Any], index: int, source_lineage: Mapping[str, Any]) -> Dict[str, Any]:
    effect = _block_effect(node)
    result_type = "GATE" if node.get("kind") == "GateDeclaration" else "CONSTRAINT"
    body = {
        "schema": "HHS_TYPED_IR_BLOCK_V1",
        "block_id": f"ir-block:{index}:{str(node.get('node_id', '')).split(':')[-1]}",
        "index": index,
        "node_ref": node.get("node_id"),
        "node_kind": node.get("kind"),
        "operator": node.get("operator"),
        "source_span": stable(node.get("source_span", {})),
        "source_text_sha256": sha256(str(node.get("source_text") or "")),
        "operand_types": [
            {"term": term, "type_id": type_id}
            for term, type_id in zip(node.get("terms", []), node.get("term_types", []))
        ],
        "result_type_id": result_type,
        "effect_declaration": effect,
        "authority_requirements": _authority_requirements(effect),
        "invariant_bindings": [
            {"invariant": invariant, "status": "REQUIRED_NOT_ASSUMED_SATISFIED"}
            for invariant in REQUIRED_INVARIANT_BINDINGS
        ],
        "artifact_lineage": stable(source_lineage),
        "reconstruction_recipe": {
            "parser_version": "HHS_HARMONICODE_PARSER_PASS_075_V1",
            "ir_version": IR_VERSION,
            "source_span": stable(node.get("source_span", {})),
            "node_root_hash72": node.get("node_root_hash72"),
            "deterministic_reparse_required": True,
        },
        "execution_permitted": False,
        "typed_ir_is_not_execution_receipt": True,
    }
    body["block_root_hash72"] = product_root("pass075_typed_ir_block", body)
    return stable(body)


def build_typed_ir(
    ast: Mapping[str, Any], *, ir_id: str, source_ref: str, source_kind: str,
    source_root_hash72: str, source_sha256: str, parent_ir_ref: str = "",
) -> Dict[str, Any]:
    lineage = {
        "source_ref": source_ref,
        "source_kind": source_kind,
        "source_root_hash72": source_root_hash72,
        "source_sha256": source_sha256,
        "parent_ir_ref": parent_ir_ref or "GENESIS",
    }
    nodes = list(_walk(ast.get("nodes", [])))
    blocks = [_block(node, index, lineage) for index, node in enumerate(nodes)]
    ir = {
        "schema": TYPED_IR_SCHEMA,
        "version": IR_VERSION,
        "ir_id": ir_id,
        "source_ref": source_ref,
        "source_kind": source_kind,
        "source_root_hash72": source_root_hash72,
        "source_sha256": source_sha256,
        "ast_root_hash72": ast.get("ast_root_hash72"),
        "blocks": blocks,
        "symbol_table": _symbol_table(ast),
        "diagnostics": stable(ast.get("diagnostics", [])),
        "required_invariants": list(REQUIRED_INVARIANT_BINDINGS),
        "source_spans_preserved": True,
        "symbol_identity_preserved": True,
        "type_information_preserved": True,
        "authority_requirements_preserved": True,
        "effect_declarations_preserved": True,
        "invariant_bindings_preserved": True,
        "artifact_lineage_preserved": True,
        "reconstruction_recipe_preserved": True,
        "ordered_products_not_commuted": True,
        "execution_permitted": False,
        "interpreter_execution_deferred_to_pass076": True,
    }
    ir["ir_root_hash72"] = product_root("pass075_hhs_typed_ir_v1", ir)
    return stable(ir)


def _reversed_ordered_pair(left: str, right: str) -> bool:
    return len(left) == len(right) == 2 and left == right[::-1] and left != right and left.isalpha() and right.isalpha()


def validate_typed_ir(ir: Mapping[str, Any], *, source_text: str = "") -> Dict[str, Any]:
    diagnostics: List[Dict[str, Any]] = [stable(x) for x in ir.get("diagnostics", []) if x.get("severity") == "ERROR"]
    if ir.get("schema") != TYPED_IR_SCHEMA:
        diagnostics.append({"code": "IR_SCHEMA_MISMATCH", "severity": "ERROR"})
    body = deepcopy(dict(ir))
    supplied_root = str(body.pop("ir_root_hash72", ""))
    observed_root = product_root("pass075_hhs_typed_ir_v1", body)
    if supplied_root != observed_root:
        diagnostics.append({"code": "IR_ROOT_MISMATCH", "severity": "ERROR"})
    block_ids = set()
    for block in ir.get("blocks", []):
        block_body = deepcopy(dict(block))
        supplied = str(block_body.pop("block_root_hash72", ""))
        if supplied != product_root("pass075_typed_ir_block", block_body):
            diagnostics.append({"code": "IR_BLOCK_ROOT_MISMATCH", "severity": "ERROR", "block_id": block.get("block_id")})
        block_id = str(block.get("block_id") or "")
        if not block_id or block_id in block_ids:
            diagnostics.append({"code": "IR_BLOCK_ID_NOT_UNIQUE", "severity": "ERROR", "block_id": block_id})
        block_ids.add(block_id)
        if block.get("effect_declaration") not in EFFECTS:
            diagnostics.append({"code": "IR_EFFECT_UNKNOWN", "severity": "ERROR", "block_id": block_id})
        if block.get("result_type_id") not in TYPE_IDS:
            diagnostics.append({"code": "IR_RESULT_TYPE_UNKNOWN", "severity": "ERROR", "block_id": block_id})
        observed_bindings = [x.get("invariant") for x in block.get("invariant_bindings", [])]
        if observed_bindings != list(REQUIRED_INVARIANT_BINDINGS):
            diagnostics.append({"code": "IR_INVARIANT_BINDINGS_INCOMPLETE", "severity": "ERROR", "block_id": block_id})
        span = block.get("source_span", {})
        start, end = int(span.get("start", -1)), int(span.get("end", -1))
        if source_text:
            if not (0 <= start <= end <= len(source_text)):
                diagnostics.append({"code": "IR_SOURCE_SPAN_OUT_OF_RANGE", "severity": "ERROR", "block_id": block_id})
            elif sha256(source_text[start:end]) != block.get("source_text_sha256"):
                diagnostics.append({"code": "IR_SOURCE_SPAN_CONTENT_MISMATCH", "severity": "ERROR", "block_id": block_id})
        terms = [str(x.get("term") or "") for x in block.get("operand_types", [])]
        if block.get("node_kind") in {"ChainEquality", "AssertEquality"}:
            for left, right in zip(terms, terms[1:]):
                if _reversed_ordered_pair(left, right):
                    diagnostics.append({
                        "code": "UNAUTHORIZED_ORDERED_PRODUCT_COMMUTATION",
                        "severity": "ERROR",
                        "block_id": block_id,
                        "left": left,
                        "right": right,
                    })
    symbols = ir.get("symbol_table", [])
    symbol_ids = [x.get("symbol_id") for x in symbols]
    if len(symbol_ids) != len(set(symbol_ids)):
        diagnostics.append({"code": "IR_SYMBOL_ID_NOT_UNIQUE", "severity": "ERROR"})
    status = "VALID" if not any(x.get("severity") == "ERROR" for x in diagnostics) else "QUARANTINED"
    result = {
        "schema": LANGUAGE_VALIDATION_SCHEMA,
        "ir_id": ir.get("ir_id"),
        "ir_root_hash72": supplied_root,
        "observed_ir_root_hash72": observed_root,
        "status": status,
        "valid": status == "VALID",
        "diagnostics": diagnostics,
        "execution_attempted": False,
        "invariant_success_not_inferred_from_binding": True,
        "validation_is_not_execution_receipt": True,
    }
    result["validation_root_hash72"] = product_root("pass075_typed_ir_validation", result)
    return stable(result)
