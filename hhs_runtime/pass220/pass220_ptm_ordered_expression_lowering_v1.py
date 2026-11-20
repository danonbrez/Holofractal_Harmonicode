"""Strict ordered expression lowering for the exact source-bound P/t/m generators.

Converts the original HARMONICODE source into immutable ordered operation
nodes.  It does not scalarize List, simplify comparisons, or evaluate Ncalc.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from hhs_runtime.pass220.pass220_ptm_exact_generator_witness_v1 import (
    GENERATOR_SOURCE, CONSTRAINED_SOURCE,
)


@dataclass(frozen=True)
class Node:
    op: str
    text: str = ""
    args: tuple["Node", ...] = ()


class SourceSyntaxError(ValueError):
    pass


def tokenize(source: str) -> tuple[str, ...]:
    if type(source) is not str or not source:
        raise SourceSyntaxError("PTM_SOURCE_EMPTY")
    out = []
    i = 0
    while i < len(source):
        c = source[i]
        if c.isspace():
            i += 1
            continue
        if c.isalpha() or c == "_":
            j = i + 1
            while j < len(source) and (source[j].isalnum() or source[j] == "_"):
                j += 1
            out.append(source[i:j])
        elif c.isdigit():
            j = i + 1
            while j < len(source) and source[j].isdigit():
                j += 1
            if j < len(source) and source[j] == ".":
                j += 1
                if j >= len(source) or not source[j].isdigit():
                    raise SourceSyntaxError("PTM_DECIMAL_TOKEN")
                while j < len(source) and source[j].isdigit():
                    j += 1
            out.append(source[i:j])
        elif source.startswith("==", i):
            j = i + 2
            out.append("==")
        elif c in "()+-*/^,":
            j = i + 1
            out.append(c)
        else:
            raise SourceSyntaxError("PTM_UNEXPECTED_CHARACTER")
        i = j
    return tuple(out)


_PRECEDENCE = {"==": 1, "+": 2, "-": 2, "*": 3, "/": 3, "^": 5}
_FUNCTIONS = {"NcalcMatrixPower", "NcalcEuclideanMod", "MatrixTimes", "List", "Sqrt"}


class _Parser:
    def __init__(self, tokens: tuple[str, ...]):
        self.tokens = tokens
        self.i = 0

    def peek(self) -> str | None:
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def take(self, token: str) -> bool:
        if self.peek() == token:
            self.i += 1
            return True
        return False

    def expect(self, token: str) -> None:
        if not self.take(token):
            raise SourceSyntaxError(f"PTM_EXPECTED:{token}")

    def expression(self, min_bp: int = 0) -> Node:
        tok = self.peek()
        if tok is None:
            raise SourceSyntaxError("PTM_UNEXPECTED_END")
        self.i += 1
        if tok == "(":
            lhs = self.expression()
            self.expect(")")
        elif tok in ("-", "+"):
            # Unary signs bind below exponentiation: -x^2 == -(x^2).
            lhs = Node("unary" + tok, args=(self.expression(4),))
        elif tok[0].isdigit():
            lhs = Node("literal", text=tok)
        elif tok[0].isalpha() or tok[0] == "_":
            if self.take("("):
                if tok not in _FUNCTIONS:
                    raise SourceSyntaxError(f"PTM_UNKNOWN_CALL:{tok}")
                args = []
                if not self.take(")"):
                    while True:
                        args.append(self.expression())
                        if self.take(")"):
                            break
                        self.expect(",")
                lhs = Node(tok, args=tuple(args))
            else:
                lhs = Node("symbol", text=tok)
        else:
            raise SourceSyntaxError(f"PTM_UNEXPECTED_TOKEN:{tok}")
        while True:
            op = self.peek()
            if op not in _PRECEDENCE:
                break
            bp = _PRECEDENCE[op]
            if bp < min_bp:
                break
            self.i += 1
            rhs = self.expression(bp if op == "^" else bp + 1)
            lhs = Node(op, args=(lhs, rhs))
        return lhs


def lower(source: str) -> Node:
    parser = _Parser(tokenize(source))
    result = parser.expression()
    if parser.peek() is not None:
        raise SourceSyntaxError("PTM_TRAILING_TOKEN")
    return result


def op_counts(root: Node) -> dict[str, int]:
    out: dict[str, int] = {}
    def walk(node: Node):
        out[node.op] = out.get(node.op, 0) + 1
        for child in node.args:
            walk(child)
    walk(root)
    return out


def postorder(root: Node) -> tuple[tuple[str, str, int], ...]:
    out = []
    def walk(node: Node):
        for child in node.args:
            walk(child)
        out.append((node.op, node.text, len(node.args)))
    walk(root)
    return tuple(out)


def receipt(source: str) -> dict:
    root = lower(source)
    ops = postorder(root)
    return {
        "source_sha256": sha256(source.encode("utf-8")).hexdigest(),
        "root_op": root.op,
        "node_count": len(ops),
        "operator_counts": op_counts(root),
        "ordered_postorder": ops,
        "native_value_execution": "NOT_EXECUTED",
        "matrix_power_value_derivation": False,
    }


def canonical_receipts() -> tuple[dict, dict]:
    return (receipt(GENERATOR_SOURCE), receipt(CONSTRAINED_SOURCE))


if __name__ == "__main__":
    import json
    for item in canonical_receipts():
        print(json.dumps(item, sort_keys=True))
