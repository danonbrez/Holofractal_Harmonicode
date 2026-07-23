from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from hhs_runtime.pass145.canonical import hash72
from hhs_runtime.pass145.errors import Pass145Error
from .registry import SEMANTIC_REGISTRY_VERSION


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    start: int
    end: int

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "text": self.text, "start": self.start, "end": self.end}


_COMMANDS = {
    "\\Delta": ("SYMBOL", "Δ"),
    "\\pi": ("SYMBOL", "π"),
    "\\infty": ("SYMBOL", "∞"),
    "\\varnothing": ("SYMBOL", "∅"),
    "\\neq": ("OP", "≠"),
    "\\cdot": ("OP", "·"),
    "\\times": ("OP", "*"),
    "\\sqrt": ("SQRT", "\\sqrt"),
    "\\frac": ("FRAC", "\\frac"),
    "\\left": ("SKIP", "\\left"),
    "\\right": ("SKIP", "\\right"),
}


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    while i < len(source):
        ch = source[i]
        if ch.isspace():
            i += 1
            continue
        if ch == "\\":
            j = i + 1
            while j < len(source) and source[j].isalpha():
                j += 1
            command = source[i:j]
            kind, text = _COMMANDS.get(command, ("UNKNOWN", command))
            if kind != "SKIP":
                tokens.append(Token(kind, text, i, j))
            i = j
            continue
        two = source[i:i+2]
        if two in {"==", "!=", "->", "=>"}:
            tokens.append(Token("OP", two, i, i+2)); i += 2; continue
        if ch in "=≠+-*/^·":
            tokens.append(Token("OP", ch, i, i+1)); i += 1; continue
        if ch in "({[":
            tokens.append(Token("OPEN", ch, i, i+1)); i += 1; continue
        if ch in ")}]":
            tokens.append(Token("CLOSE", ch, i, i+1)); i += 1; continue
        if ch in {",", ":", ";"}:
            tokens.append(Token("PUNCT", ch, i, i+1)); i += 1; continue
        if ch in {"⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"}:
            mapped = {"⁰":"0", "¹":"1", "²":"2", "³":"3", "⁴":"4", "⁵":"5", "⁶":"6", "⁷":"7", "⁸":"8", "⁹":"9"}[ch]
            tokens.append(Token("NUMBER", mapped, i, i+1)); i += 1; continue
        if ch.isdigit():
            j = i + 1
            while j < len(source) and source[j].isdigit():
                j += 1
            if j < len(source) and source[j] == ".":
                k = j + 1
                while k < len(source) and source[k].isdigit():
                    k += 1
                j = k
            tokens.append(Token("NUMBER", source[i:j], i, j)); i = j; continue
        if ch.isalpha() or ch in {"Δ", "π", "∞", "∅", "Ω", "Ψ", "Θ"}:
            # Single-symbol tokenization deliberately preserves AB vs BA order as
            # implicit composition rather than collapsing either into one name.
            tokens.append(Token("SYMBOL", ch, i, i+1)); i += 1; continue
        tokens.append(Token("UNKNOWN", ch, i, i+1)); i += 1
    tokens.append(Token("EOF", "", len(source), len(source)))
    return tokens


_OPERATOR_IDS = {
    "==": "HHS_GATE_EQ",
    "=": "HHS_DECLARATIVE_RELATION",
    "≠": "HHS_DISTINCT_FROM",
    "!=": "HHS_DISTINCT_FROM",
    "+": "HHS_PROJECTION_PLUS",
    "-": "HHS_RESIDUAL_MINUS",
    "*": "HHS_ORDERED_COMPOSITION",
    "·": "HHS_ORDERED_COMPOSITION",
    "/": "HHS_TYPED_FRACTION",
    "^": "HHS_PHASE_EXPONENT",
    "IMPLICIT": "HHS_ORDERED_COMPOSITION",
}

_PRECEDENCE = {
    "==": 10, "=": 10, "≠": 10, "!=": 10,
    "->": 15, "=>": 15,
    "+": 30, "-": 30,
    "*": 50, "·": 50, "/": 50, "IMPLICIT": 50,
    "^": 70,
}


class Parser:
    def __init__(self, source: str):
        self.source = source
        self.tokens = tokenize(source)
        self.pos = 0
        self.diagnostics: list[dict[str, Any]] = []

    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        value = self.current
        self.pos += 1
        return value

    def parse(self) -> dict[str, Any]:
        if self.current.kind == "EOF":
            node = self._node("EMPTY", 0, 0, value="")
        else:
            node = self.expression(0)
        trailing = []
        while self.current.kind != "EOF":
            trailing.append(self.advance().to_dict())
        if trailing:
            self.diagnostics.append({"code": "TRAILING_TOKENS", "tokens": trailing})
        payload = {
            "schema": "HHS_PASS148_ORDERED_AST_V1",
            "source_expression": self.source,
            "registry_version": SEMANTIC_REGISTRY_VERSION,
            "tokens": [t.to_dict() for t in self.tokens[:-1]],
            "root": node,
            "parse_diagnostics": self.diagnostics,
            "source_preserved": True,
        }
        payload["canonical_ast_hash"] = hash72("hhs_pass148_ordered_ast_v1", {"root": node, "registry_version": SEMANTIC_REGISTRY_VERSION})
        payload["source_hash72"] = hash72("hhs_pass148_expression_source_v1", self.source)
        return payload

    def expression(self, min_precedence: int) -> dict[str, Any]:
        left = self.prefix()
        while True:
            token = self.current
            implicit = self._begins_primary(token)
            if token.kind == "OP" and token.text in _PRECEDENCE:
                op = token.text
                precedence = _PRECEDENCE[op]
                if precedence < min_precedence:
                    break
                self.advance()
            elif implicit:
                op = "IMPLICIT"
                precedence = _PRECEDENCE[op]
                if precedence < min_precedence:
                    break
            else:
                break
            next_min = precedence if op == "^" else precedence + 1
            right = self.expression(next_min)
            left = self._node(
                "BINARY",
                left["span"][0], right["span"][1],
                operator_glyph=op,
                operator_id=_OPERATOR_IDS.get(op, "UNREGISTERED_OPERATOR"),
                left=left,
                right=right,
                ordered=True,
            )
        return left

    def prefix(self) -> dict[str, Any]:
        token = self.current
        if token.kind == "OP" and token.text in {"+", "-"}:
            self.advance()
            operand = self.expression(80)
            return self._node("UNARY", token.start, operand["span"][1], operator_glyph=token.text, operator_id="HHS_UNARY_" + ("POSITIVE" if token.text == "+" else "NEGATIVE"), operand=operand, ordered=True)
        if token.kind == "FRAC":
            start = self.advance().start
            numerator = self.required_group("fraction numerator")
            denominator = self.required_group("fraction denominator")
            return self._node("BINARY", start, denominator["span"][1], operator_glyph="\\frac", operator_id="HHS_TYPED_FRACTION", left=numerator, right=denominator, ordered=True)
        if token.kind == "SQRT":
            start = self.advance().start
            operand = self.required_group("root operand") if self.current.kind == "OPEN" else self.prefix()
            return self._node("UNARY", start, operand["span"][1], operator_glyph="\\sqrt", operator_id="HHS_SYMBOLIC_ROOT", operand=operand, ordered=True)
        if token.kind == "OPEN":
            return self.group()
        if token.kind in {"SYMBOL", "NUMBER"}:
            self.advance()
            return self._node(token.kind, token.start, token.end, value=token.text)
        if token.kind == "UNKNOWN":
            self.advance()
            self.diagnostics.append({"code": "UNKNOWN_TOKEN", "token": token.to_dict()})
            return self._node("UNKNOWN", token.start, token.end, value=token.text)
        if token.kind == "EOF":
            self.diagnostics.append({"code": "UNEXPECTED_END"})
            return self._node("MISSING", token.start, token.end, value="")
        self.advance()
        self.diagnostics.append({"code": "UNEXPECTED_TOKEN", "token": token.to_dict()})
        return self._node("UNKNOWN", token.start, token.end, value=token.text)

    def group(self) -> dict[str, Any]:
        opening = self.advance()
        matching = {"(": ")", "{": "}", "[": "]"}[opening.text]
        value = self.expression(0)
        if self.current.kind == "CLOSE" and self.current.text == matching:
            closing = self.advance()
            return self._node("GROUP", opening.start, closing.end, delimiter=opening.text + matching, value=value)
        self.diagnostics.append({"code": "UNCLOSED_GROUP", "opening": opening.to_dict(), "expected": matching})
        return self._node("GROUP", opening.start, value["span"][1], delimiter=opening.text + matching, value=value, closed=False)

    def required_group(self, role: str) -> dict[str, Any]:
        if self.current.kind != "OPEN":
            token = self.current
            self.diagnostics.append({"code": "MISSING_REQUIRED_GROUP", "role": role, "at": token.start})
            return self.prefix()
        return self.group()

    @staticmethod
    def _begins_primary(token: Token) -> bool:
        return token.kind in {"SYMBOL", "NUMBER", "OPEN", "FRAC", "SQRT"}

    def _node(self, kind: str, start: int, end: int, **fields: Any) -> dict[str, Any]:
        return {"kind": kind, "span": [start, end], "source_slice": self.source[start:end], **fields}


def parse_expression(source: str) -> dict[str, Any]:
    if not isinstance(source, str):
        raise Pass145Error("SEMANTIC_SOURCE_INVALID", "expression must be a string", "SEMANTIC_PARSE")
    return Parser(source).parse()


def ast_semantic_key(node: dict[str, Any]) -> Any:
    kind = node.get("kind")
    if kind in {"SYMBOL", "NUMBER", "UNKNOWN", "MISSING", "EMPTY"}:
        return [kind, node.get("value")]
    if kind == "GROUP":
        return [kind, node.get("delimiter"), ast_semantic_key(node["value"])]
    if kind == "UNARY":
        return [kind, node.get("operator_id"), node.get("operator_glyph"), ast_semantic_key(node["operand"])]
    if kind == "BINARY":
        return [kind, node.get("operator_id"), node.get("operator_glyph"), ast_semantic_key(node["left"]), ast_semantic_key(node["right"])]
    return [kind, {k: v for k, v in node.items() if k not in {"span", "source_slice"}}]


def render_ast(node: dict[str, Any]) -> str:
    kind = node.get("kind")
    if kind in {"SYMBOL", "NUMBER", "UNKNOWN", "MISSING", "EMPTY"}:
        return str(node.get("value", ""))
    if kind == "GROUP":
        delimit = node.get("delimiter", "()")
        return delimit[0] + render_ast(node["value"]) + delimit[-1]
    if kind == "UNARY":
        op = node.get("operator_glyph", "")
        if op == "\\sqrt":
            return "√(" + render_ast(node["operand"]) + ")"
        return op + render_ast(node["operand"])
    if kind == "BINARY":
        op = node.get("operator_glyph", "")
        if op == "\\frac":
            return "(" + render_ast(node["left"]) + ")/(" + render_ast(node["right"]) + ")"
        if op == "IMPLICIT":
            op = "·"
        return "(" + render_ast(node["left"]) + op + render_ast(node["right"]) + ")"
    return str(node)


def walk_ast(node: dict[str, Any]) -> Iterable[dict[str, Any]]:
    yield node
    if node.get("kind") == "GROUP":
        yield from walk_ast(node["value"])
    elif node.get("kind") == "UNARY":
        yield from walk_ast(node["operand"])
    elif node.get("kind") == "BINARY":
        yield from walk_ast(node["left"])
        yield from walk_ast(node["right"])
