"""
HARMONICODE Interpreter v1
==========================

Python-based scaffold for the HARMONICODE language.

Pipeline:
    source -> lexer -> parser -> AST -> constraint graph -> IR -> receipt

Scope v1:
- chain equality: A=B=C
- assertion equality: x==1/y
- inequality / distinct chain: x≠y≠xy≠yx
- gate declaration: NAME := { ... }
- gate invocation: NAME
- function/list expressions are preserved as expression text nodes for later deep parsing
- ordered product text is never commuted or simplified

This scaffold does not execute kernel mutation. It emits a deterministic IR receipt
and marks all state mutation as future AUDITED transition work.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json
import re

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_stress_test_v1 import stress_validate_interpreter_artifacts


class TokenKind(str, Enum):
    IDENT = "IDENT"
    NUMBER = "NUMBER"
    OP = "OP"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA = "COMMA"
    NEWLINE = "NEWLINE"
    TEXT = "TEXT"


class ASTKind(str, Enum):
    PROGRAM = "Program"
    CHAIN_EQ = "ChainEq"
    ASSERT_EQ = "AssertEq"
    DISTINCT_CHAIN = "DistinctChain"
    GATE_DECL = "GateDeclaration"
    GATE_INVOKE = "GateInvocation"
    RAW_EXPR = "RawExpression"


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: str
    position: int

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class ASTNode:
    kind: ASTKind
    value: str | None = None
    terms: List[str] | None = None
    children: List["ASTNode"] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind.value,
            "value": self.value,
            "terms": self.terms or [],
            "children": [c.to_dict() for c in self.children or []],
        }


@dataclass(frozen=True)
class ConstraintEdge:
    type: str
    source: str
    target: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConstraintGraph:
    nodes: List[str]
    edges: List[ConstraintEdge]
    graph_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {"nodes": self.nodes, "edges": [e.to_dict() for e in self.edges], "graph_hash72": self.graph_hash72}


@dataclass(frozen=True)
class IRBlock:
    kind: str
    effect: str
    payload: Dict[str, Any]
    block_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IRProgram:
    kind: str
    blocks: List[IRBlock]
    ir_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {"kind": self.kind, "blocks": [b.to_dict() for b in self.blocks], "ir_hash72": self.ir_hash72}


@dataclass(frozen=True)
class InterpreterReceipt:
    source_hash72: str
    ast_hash72: str
    graph_hash72: str
    ir_hash72: str
    stress_hash72: str
    status: str
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InterpreterResult:
    tokens: List[Token]
    ast: ASTNode
    graph: ConstraintGraph
    ir: IRProgram
    receipt: InterpreterReceipt

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tokens": [t.to_dict() for t in self.tokens],
            "ast": self.ast.to_dict(),
            "graph": self.graph.to_dict(),
            "ir": self.ir.to_dict(),
            "receipt": self.receipt.to_dict(),
        }


# ... (unchanged code omitted for brevity in patch) ...


def interpret(source: str) -> InterpreterResult:
    tokens = lex(source)
    ast = parse(source)
    graph = build_constraint_graph(ast)
    ir = lower_to_ir(ast, graph)

    source_hash = hash72_digest(("harmonicode_source_v1", normalize_source(source)), width=24)
    ast_hash = hash72_digest(("harmonicode_ast_v1", ast.to_dict()), width=24)

    # 🔷 Stress harness gate
    stress = stress_validate_interpreter_artifacts(
        source=source,
        source_hash72=source_hash,
        ast=ast.to_dict(),
        ast_hash72=ast_hash,
        graph=graph.to_dict(),
        ir=ir.to_dict(),
    )

    if stress.receipt.status.value != "PASSED":
        status = "QUARANTINED"
    else:
        status = "IR_EMITTED"

    receipt_hash = hash72_digest(
        (
            "harmonicode_interpreter_receipt_v1",
            source_hash,
            ast_hash,
            graph.graph_hash72,
            ir.ir_hash,
            stress.receipt.receipt_hash72,
            status,
        ),
        width=24,
    )

    receipt = InterpreterReceipt(
        source_hash,
        ast_hash,
        graph.graph_hash72,
        ir.ir_hash,
        stress.receipt.receipt_hash72,
        status,
        receipt_hash,
    )

    return InterpreterResult(tokens, ast, graph, ir, receipt)


# rest unchanged
