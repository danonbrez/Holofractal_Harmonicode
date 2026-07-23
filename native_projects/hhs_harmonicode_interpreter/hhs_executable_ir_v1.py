"""Deterministic lowering from committed HHS_TYPED_IR_V1 to HHS_EXECUTABLE_IR_V1."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, sha256, stable
from native_projects.hhs_harmonicode_language.hhs_harmonicode_parser_v1 import parse_source
from native_projects.hhs_harmonicode_language.hhs_typed_ir_v1 import validate_typed_ir

from .hhs_pass076_contracts_v1 import (
    EXECUTABLE_IR_SCHEMA,
    EXECUTABLE_STATEMENT_SCHEMA,
    rooted,
    verify_rooted,
)

LOWERING_VERSION = "HHS_EXECUTABLE_IR_LOWERING_PASS_076_V1"


def _verify_source_artifact(artifact: Mapping[str, Any]) -> None:
    if artifact.get("schema") != "HHS_COMMITTED_SOURCE_ARTIFACT_V1":
        raise ContractError("REJECT_EXECUTABLE_IR_SOURCE_ARTIFACT_SCHEMA")
    if not verify_rooted("pass074_source_artifact", artifact, "artifact_root_hash72"):
        raise ContractError("REJECT_EXECUTABLE_IR_SOURCE_ARTIFACT_ROOT")


def _verify_typed_ir_artifact(artifact: Mapping[str, Any]) -> None:
    if artifact.get("schema") != "HHS_TYPED_IR_ARTIFACT_V1":
        raise ContractError("REJECT_EXECUTABLE_IR_TYPED_ARTIFACT_SCHEMA")
    if not verify_rooted("pass075_typed_ir_artifact", artifact, "artifact_root_hash72"):
        raise ContractError("REJECT_EXECUTABLE_IR_TYPED_ARTIFACT_ROOT")


def _walk(nodes: Iterable[Mapping[str, Any]]) -> Iterable[Mapping[str, Any]]:
    for node in nodes:
        yield node
        yield from _walk(node.get("children", []))


def _statement(node: Mapping[str, Any], block: Mapping[str, Any], children: List[Dict[str, Any]]) -> Dict[str, Any]:
    kind = str(node.get("kind") or "")
    operation = {
        "GateDeclaration": "DEFINE_GATE",
        "GateInvocation": "INVOKE_GATE",
        "AssertEquality": "EVALUATE_EQUALITY",
        "ChainEquality": "EVALUATE_EQUALITY",
        "DistinctChain": "EVALUATE_DISTINCTNESS",
        "RawExpression": "EVALUATE_EXPRESSION",
    }.get(kind, "EVALUATE_EXPRESSION")
    body = {
        "schema": EXECUTABLE_STATEMENT_SCHEMA,
        "statement_id": f"statement:{node.get('node_id')}",
        "node_ref": node.get("node_id"),
        "block_ref": block.get("block_id"),
        "operation": operation,
        "node_kind": kind,
        "name": str(node.get("name") or ""),
        "operator": str(node.get("operator") or ""),
        "operands": [str(x) for x in node.get("terms", [])],
        "source_span": stable(node.get("source_span", {})),
        "effect_declaration": block.get("effect_declaration"),
        "authority_requirements": stable(block.get("authority_requirements", [])),
        "invariant_bindings": stable(block.get("invariant_bindings", [])),
        "children": children,
    }
    body["statement_root_hash72"] = product_root("pass076_executable_statement", body)
    return stable(body)


def _lower_node(node: Mapping[str, Any], block_by_node: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    ref = str(node.get("node_id") or "")
    block = block_by_node.get(ref)
    if not block:
        raise ContractError(f"REJECT_EXECUTABLE_IR_BLOCK_NOT_FOUND:{ref}")
    children = [_lower_node(child, block_by_node) for child in node.get("children", [])]
    return _statement(node, block, children)


def lower_committed_typed_ir(
    *, executable_ir_id: str, typed_ir_artifact: Mapping[str, Any],
    source_artifact: Mapping[str, Any], validation: Mapping[str, Any],
) -> Dict[str, Any]:
    _verify_source_artifact(source_artifact)
    _verify_typed_ir_artifact(typed_ir_artifact)
    typed_ir = deepcopy(typed_ir_artifact.get("content", {}))
    source = str(source_artifact.get("content") or "")
    if typed_ir_artifact.get("source_artifact_ref") != source_artifact.get("artifact_id"):
        raise ContractError("REJECT_EXECUTABLE_IR_SOURCE_LINEAGE_REF_MISMATCH")
    if typed_ir_artifact.get("source_artifact_root_hash72") != source_artifact.get("artifact_root_hash72"):
        raise ContractError("REJECT_EXECUTABLE_IR_SOURCE_LINEAGE_ROOT_MISMATCH")
    if typed_ir.get("source_sha256") != sha256(source):
        raise ContractError("REJECT_EXECUTABLE_IR_SOURCE_CONTENT_MISMATCH")
    if not validation.get("valid") or validation.get("ir_root_hash72") != typed_ir.get("ir_root_hash72"):
        raise ContractError("REJECT_EXECUTABLE_IR_WITHOUT_VALID_TYPED_IR")
    observed_validation = validate_typed_ir(typed_ir, source_text=source)
    if not observed_validation.get("valid"):
        raise ContractError("REJECT_EXECUTABLE_IR_REVALIDATION_FAILED")
    ast = parse_source(source)
    if ast.get("ast_root_hash72") != typed_ir.get("ast_root_hash72"):
        raise ContractError("REJECT_EXECUTABLE_IR_REPARSE_AST_MISMATCH")
    blocks = list(typed_ir.get("blocks", []))
    block_by_node = {str(block.get("node_ref") or ""): block for block in blocks}
    if len(block_by_node) != len(blocks):
        raise ContractError("REJECT_EXECUTABLE_IR_NONUNIQUE_NODE_BINDING")
    statements = [_lower_node(node, block_by_node) for node in ast.get("nodes", [])]
    all_statements: List[Mapping[str, Any]] = []
    def collect(items: Iterable[Mapping[str, Any]]) -> None:
        for item in items:
            all_statements.append(item)
            collect(item.get("children", []))
    collect(statements)
    unsupported = sorted({str(x.get("effect_declaration")) for x in all_statements if x.get("effect_declaration") != "PURE_SYMBOLIC"})
    gate_names = [str(x.get("name") or "") for x in statements if x.get("operation") == "DEFINE_GATE"]
    if len(gate_names) != len(set(gate_names)):
        raise ContractError("REJECT_EXECUTABLE_IR_DUPLICATE_GATE_NAME")
    body = {
        "schema": EXECUTABLE_IR_SCHEMA,
        "version": LOWERING_VERSION,
        "executable_ir_id": executable_ir_id,
        "typed_ir_artifact_ref": typed_ir_artifact.get("artifact_id"),
        "typed_ir_artifact_root_hash72": typed_ir_artifact.get("artifact_root_hash72"),
        "typed_ir_ref": typed_ir.get("ir_id"),
        "typed_ir_root_hash72": typed_ir.get("ir_root_hash72"),
        "source_artifact_ref": source_artifact.get("artifact_id"),
        "source_artifact_root_hash72": source_artifact.get("artifact_root_hash72"),
        "source_sha256": typed_ir.get("source_sha256"),
        "validation_ref": validation.get("validation_id"),
        "validation_root_hash72": validation.get("validation_root_hash72"),
        "statements": statements,
        "statement_count": len(all_statements),
        "gate_names": gate_names,
        "unsupported_effects": unsupported,
        "all_effects_pure_symbolic": not unsupported,
        "source_spans_preserved": True,
        "ordered_products_not_commuted": True,
        "typed_ir_revalidated_before_lowering": True,
        "lowering_executes_no_program_effects": True,
        "execution_requires_runtime_authority": True,
    }
    return rooted("pass076_executable_ir", body, "executable_ir_root_hash72")


def verify_executable_ir(value: Mapping[str, Any]) -> bool:
    if value.get("schema") != EXECUTABLE_IR_SCHEMA:
        return False
    if not verify_rooted("pass076_executable_ir", value, "executable_ir_root_hash72"):
        return False
    def valid_statement(item: Mapping[str, Any]) -> bool:
        if item.get("schema") != EXECUTABLE_STATEMENT_SCHEMA:
            return False
        if not verify_rooted("pass076_executable_statement", item, "statement_root_hash72"):
            return False
        return all(valid_statement(child) for child in item.get("children", []))
    return all(valid_statement(item) for item in value.get("statements", []))
