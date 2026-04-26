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
    replacements = {
        "²": "^2",
        "³": "^3",
        "⁴": "^4",
        "⁶": "^6",
        "⁷": "^7",
        "⁸": "^8",
        "⁹": "^9",
        "⁰": "^0",
        "⁻": "^-",
        "√": "Sqrt",
    }
    out = source.replace("\r\n", "\n").replace("\r", "\n")
    for k, v in replacements.items():
        out = out.replace(k, v)
    return out


def lex(source: str) -> List[Token]:
    src = normalize_source(source)
    tokens: List[Token] = []
    token_re = re.compile(r"(:=|==|!=|≠|[{}()\[\],]|\n|[A-Za-z_ΠρφψχδτΩΘΔ][A-Za-z0-9_ΠρφψχδτΩΘΔ]*|\d+(?:\.\d+)?|\S)")
    for match in token_re.finditer(src):
        value = match.group(0)
        pos = match.start()
        if value == "\n":
            tokens.append(Token(TokenKind.NEWLINE, value, pos))
        elif value == "{":
            tokens.append(Token(TokenKind.LBRACE, value, pos))
        elif value == "}":
            tokens.append(Token(TokenKind.RBRACE, value, pos))
        elif value == "(":
            tokens.append(Token(TokenKind.LPAREN, value, pos))
        elif value == ")":
            tokens.append(Token(TokenKind.RPAREN, value, pos))
        elif value == "[":
            tokens.append(Token(TokenKind.LBRACKET, value, pos))
        elif value == "]":
            tokens.append(Token(TokenKind.RBRACKET, value, pos))
        elif value == ",":
            tokens.append(Token(TokenKind.COMMA, value, pos))
        elif re.fullmatch(r"[A-Za-z_ΠρφψχδτΩΘΔ][A-Za-z0-9_ΠρφψχδτΩΘΔ]*", value):
            tokens.append(Token(TokenKind.IDENT, value, pos))
        elif re.fullmatch(r"\d+(?:\.\d+)?", value):
            tokens.append(Token(TokenKind.NUMBER, value, pos))
        elif value in {":=", "==", "!=", "≠", "=", ":", "+", "-", "*", "/", "^"}:
            tokens.append(Token(TokenKind.OP, value, pos))
        else:
            tokens.append(Token(TokenKind.TEXT, value, pos))
    return tokens


def _split_top_level(source: str) -> List[str]:
    src = normalize_source(source)
    parts: List[str] = []
    buf: List[str] = []
    depth = 0
    for ch in src:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        if (ch == "\n" or ch == ",") and depth == 0:
            text = "".join(buf).strip()
            if text:
                parts.append(text)
            buf = []
        else:
            buf.append(ch)
    text = "".join(buf).strip()
    if text:
        parts.append(text)
    return parts


def _split_chain(text: str, op: str) -> List[str]:
    return [p.strip() for p in text.split(op) if p.strip()]


def parse(source: str) -> ASTNode:
    parts = _split_top_level(source)
    children: List[ASTNode] = []
    i = 0
    while i < len(parts):
        line = parts[i].strip()
        if not line:
            i += 1
            continue
        if ":=" in line:
            name, rhs = line.split(":=", 1)
            name = name.strip()
            rhs = rhs.strip()
            gate_children: List[ASTNode] = []
            if rhs.startswith("{") and rhs.endswith("}"):
                inner = rhs[1:-1]
                gate_children = parse(inner).children or []
            else:
                gate_children = [parse(rhs)]
            children.append(ASTNode(ASTKind.GATE_DECL, value=name, children=gate_children))
        elif "≠" in line or "!=" in line:
            op = "≠" if "≠" in line else "!="
            children.append(ASTNode(ASTKind.DISTINCT_CHAIN, terms=_split_chain(line, op)))
        elif "==" in line:
            children.append(ASTNode(ASTKind.ASSERT_EQ, terms=_split_chain(line, "==")))
        elif "=" in line:
            children.append(ASTNode(ASTKind.CHAIN_EQ, terms=_split_chain(line, "=")))
        elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", line):
            children.append(ASTNode(ASTKind.GATE_INVOKE, value=line))
        else:
            children.append(ASTNode(ASTKind.RAW_EXPR, value=line))
        i += 1
    return ASTNode(ASTKind.PROGRAM, children=children)


def build_constraint_graph(ast: ASTNode) -> ConstraintGraph:
    nodes: set[str] = set()
    edges: List[ConstraintEdge] = []

    def visit(node: ASTNode) -> None:
        if node.kind in {ASTKind.CHAIN_EQ, ASTKind.ASSERT_EQ}:
            terms = node.terms or []
            nodes.update(terms)
            edge_type = "assert_eq" if node.kind == ASTKind.ASSERT_EQ else "chain_eq"
            for a, b in zip(terms, terms[1:]):
                edges.append(ConstraintEdge(edge_type, a, b))
        elif node.kind == ASTKind.DISTINCT_CHAIN:
            terms = node.terms or []
            nodes.update(terms)
            for idx, a in enumerate(terms):
                for b in terms[idx + 1:]:
                    edges.append(ConstraintEdge("neq", a, b))
        elif node.kind == ASTKind.GATE_DECL:
            nodes.add(f"gate:{node.value}")
            for child in node.children or []:
                visit(child)
        elif node.kind == ASTKind.GATE_INVOKE:
            nodes.add(f"gate_invocation:{node.value}")
        elif node.kind == ASTKind.RAW_EXPR and node.value:
            nodes.add(node.value)
        for child in node.children or []:
            if node.kind != ASTKind.GATE_DECL:
                visit(child)

    visit(ast)
    node_list = sorted(nodes)
    edge_list = edges
    graph_hash = hash72_digest(("constraint_graph_v1", node_list, [e.to_dict() for e in edge_list]), width=24)
    return ConstraintGraph(node_list, edge_list, graph_hash)


def lower_to_ir(ast: ASTNode, graph: ConstraintGraph) -> IRProgram:
    blocks: List[IRBlock] = []

    def add_block(kind: str, effect: str, payload: Dict[str, Any]) -> None:
        h = hash72_digest(("harmonicode_ir_block_v1", kind, effect, payload), width=24)
        blocks.append(IRBlock(kind, effect, payload, h))

    add_block("ConstraintGraph", "PURE", graph.to_dict())
    for child in ast.children or []:
        if child.kind == ASTKind.GATE_DECL:
            add_block("GateDeclaration", "PURE", child.to_dict())
        elif child.kind == ASTKind.GATE_INVOKE:
            add_block("GateInvocation", "AUDITED", child.to_dict())
        elif child.kind in {ASTKind.CHAIN_EQ, ASTKind.ASSERT_EQ, ASTKind.DISTINCT_CHAIN, ASTKind.RAW_EXPR}:
            add_block("Constraint", "PURE", child.to_dict())
    ir_hash = hash72_digest(("harmonicode_ir_program_v1", [b.to_dict() for b in blocks]), width=24)
    return IRProgram("IRProgram", blocks, ir_hash)


def interpret(source: str) -> InterpreterResult:
    tokens = lex(source)
    ast = parse(source)
    graph = build_constraint_graph(ast)
    ir = lower_to_ir(ast, graph)
    source_hash = hash72_digest(("harmonicode_source_v1", normalize_source(source)), width=24)
    ast_hash = hash72_digest(("harmonicode_ast_v1", ast.to_dict()), width=24)
    status = "IR_EMITTED"
    receipt_hash = hash72_digest(("harmonicode_interpreter_receipt_v1", source_hash, ast_hash, graph.graph_hash72, ir.ir_hash, status), width=24)
    receipt = InterpreterReceipt(source_hash, ast_hash, graph.graph_hash72, ir.ir_hash, status, receipt_hash)
    return InterpreterResult(tokens, ast, graph, ir, receipt)


def main() -> None:
    sample = """
xy=-1/yx
yx=-xy
xy≠yx
PLASTIC_EIGENSTATE_CLOSURE_GATE := { ρ^3 = ρ + 1, b = ρ^2, b^2 = ρ^4 }
PLASTIC_EIGENSTATE_CLOSURE_GATE
"""
    print(json.dumps(interpret(sample).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
