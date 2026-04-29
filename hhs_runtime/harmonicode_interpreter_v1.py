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
from typing import Any, Dict, List
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


def normalize_source(source: str) -> str:
    return "\n".join(line.rstrip() for line in source.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n"))


def lex(source: str) -> List[Token]:
    tokens: List[Token] = []
    pattern = re.compile(r"(:=|==|!=|≠|[{}()\[\],=]|[A-Za-z_ΔΨΘΩ][A-Za-z0-9_ΔΨΘΩ₀-₉^]*|\d+(?:/\d+)?|\S)")
    for match in pattern.finditer(source):
        value = match.group(0)
        pos = match.start()
        if value == "{":
            kind = TokenKind.LBRACE
        elif value == "}":
            kind = TokenKind.RBRACE
        elif value == "(":
            kind = TokenKind.LPAREN
        elif value == ")":
            kind = TokenKind.RPAREN
        elif value == "[":
            kind = TokenKind.LBRACKET
        elif value == "]":
            kind = TokenKind.RBRACKET
        elif value == ",":
            kind = TokenKind.COMMA
        elif re.fullmatch(r"\d+(?:/\d+)?", value):
            kind = TokenKind.NUMBER
        elif re.fullmatch(r"[A-Za-z_ΔΨΘΩ][A-Za-z0-9_ΔΨΘΩ₀-₉^]*", value):
            kind = TokenKind.IDENT
        elif value in {":=", "==", "!=", "≠", "="}:
            kind = TokenKind.OP
        else:
            kind = TokenKind.TEXT
        tokens.append(Token(kind, value, pos))
    return tokens


def _split_top_level(source: str) -> List[str]:
    normalized = normalize_source(source)
    parts: List[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(normalized):
        if ch in "{([":
            depth += 1
        elif ch in "})]":
            depth = max(0, depth - 1)
        elif ch in {"\n", ";"} and depth == 0:
            segment = normalized[start:i].strip()
            if segment:
                parts.append(segment)
            start = i + 1
    tail = normalized[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def _terms(expr: str, sep: str) -> List[str]:
    return [p.strip() for p in expr.split(sep) if p.strip()]


def _parse_statement(stmt: str) -> ASTNode:
    gate = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*\{(.*)\}$", stmt, flags=re.DOTALL)
    if gate:
        name = gate.group(1)
        body = gate.group(2).strip()
        children = [_parse_statement(part) for part in _split_top_level(body)] if body else []
        return ASTNode(ASTKind.GATE_DECL, value=name, children=children)
    if "≠" in stmt:
        return ASTNode(ASTKind.DISTINCT_CHAIN, terms=_terms(stmt, "≠"))
    if "==" in stmt:
        return ASTNode(ASTKind.ASSERT_EQ, terms=_terms(stmt, "=="))
    if "=" in stmt and ":=" not in stmt:
        return ASTNode(ASTKind.CHAIN_EQ, terms=_terms(stmt, "="))
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", stmt):
        return ASTNode(ASTKind.GATE_INVOKE, value=stmt)
    return ASTNode(ASTKind.RAW_EXPR, value=stmt)


def parse(source: str) -> ASTNode:
    children = [_parse_statement(stmt) for stmt in _split_top_level(source)]
    return ASTNode(ASTKind.PROGRAM, children=children)


def _walk(node: ASTNode) -> List[ASTNode]:
    out = [node]
    for child in node.children or []:
        out.extend(_walk(child))
    return out


def build_constraint_graph(ast: ASTNode) -> ConstraintGraph:
    nodes = set()
    edges: List[ConstraintEdge] = []
    for node in _walk(ast):
        if node.terms:
            for term in node.terms:
                nodes.add(term)
            if node.kind in {ASTKind.CHAIN_EQ, ASTKind.ASSERT_EQ}:
                for a, b in zip(node.terms, node.terms[1:]):
                    edges.append(ConstraintEdge("EQUALS_ORDERED", a, b))
            elif node.kind == ASTKind.DISTINCT_CHAIN:
                for a, b in zip(node.terms, node.terms[1:]):
                    edges.append(ConstraintEdge("DISTINCT_ORDERED", a, b))
        if node.value:
            nodes.add(node.value)
    ordered_nodes = sorted(nodes)
    graph_hash = hash72_digest(("harmonicode_constraint_graph_v1", ordered_nodes, [e.to_dict() for e in edges]), width=24)
    return ConstraintGraph(ordered_nodes, edges, graph_hash)


def lower_to_ir(ast: ASTNode, graph: ConstraintGraph) -> IRProgram:
    blocks: List[IRBlock] = []
    for index, node in enumerate(_walk(ast)):
        if node.kind == ASTKind.PROGRAM:
            continue
        payload = {"index": index, "node": node.to_dict(), "graph_hash72": graph.graph_hash72}
        effect = "AUDIT_ONLY_NO_MUTATION"
        block_hash = hash72_digest(("harmonicode_ir_block_v1", node.kind.value, effect, payload), width=24)
        blocks.append(IRBlock(node.kind.value, effect, payload, block_hash))
    ir_hash = hash72_digest(("harmonicode_ir_program_v1", [b.to_dict() for b in blocks]), width=24)
    return IRProgram("HARMONICODE_IR_V1", blocks, ir_hash)


def interpret(source: str) -> InterpreterResult:
    tokens = lex(source)
    ast = parse(source)
    graph = build_constraint_graph(ast)
    ir = lower_to_ir(ast, graph)

    source_hash = hash72_digest(("harmonicode_source_v1", normalize_source(source)), width=24)
    ast_hash = hash72_digest(("harmonicode_ast_v1", ast.to_dict()), width=24)

    stress = stress_validate_interpreter_artifacts(
        source=source,
        source_hash72=source_hash,
        ast=ast.to_dict(),
        ast_hash72=ast_hash,
        graph=graph.to_dict(),
        ir=ir.to_dict(),
    )

    status = "IR_EMITTED" if stress.receipt.status.value == "PASSED" else "QUARANTINED"

    receipt_hash = hash72_digest(
        (
            "harmonicode_interpreter_receipt_v1",
            source_hash,
            ast_hash,
            graph.graph_hash72,
            ir.ir_hash72,
            stress.receipt.receipt_hash72,
            status,
        ),
        width=24,
    )

    receipt = InterpreterReceipt(
        source_hash,
        ast_hash,
        graph.graph_hash72,
        ir.ir_hash72,
        stress.receipt.receipt_hash72,
        status,
        receipt_hash,
    )

    return InterpreterResult(tokens, ast, graph, ir, receipt)


def main() -> None:
    sample = "x==1/y\nxy≠yx\nGATE := { a=b=c; z≠w }\nGATE"
    print(json.dumps(interpret(sample).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
