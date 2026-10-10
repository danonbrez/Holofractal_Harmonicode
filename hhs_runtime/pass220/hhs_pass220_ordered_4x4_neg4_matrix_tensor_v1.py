"""Pass 220: source-locked, non-evaluating ordered 4x4 -4 matrix-power HIR.

This retains HHS MatrixTimes, quotient, NcalcMatrixPower and equality as typed
source operations. No host MatrixPower, scalar substitution for s/v, VM81
mutation or Hash72/Hash216 minting occurs in this candidate-only module.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any

SCHEMA = "HHS_PASS220_ORDERED_4X4_NEG4_MATRIX_TENSOR_HIR_V1"
SOURCE_PATH = Path("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode")
SOURCE_BYTES = 366
SOURCE_SHA256 = "a3ba5ca5f31ee76261e5df75c7e9f43a78219d59df36a095a07c0acdf90dbd19"
PASS169_CANONICAL_TYPE = "ExactMatrixPower"
NODE_KIND = "EXACT_SYMBOLIC_MATRIX_POWER"
TOKEN_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|==|[0-9]+|[(),/\-]")


class MatrixTensorHIRReject(ValueError):
    """The caller/source does not meet the frozen HHS ordered HIR contract."""


@dataclass(frozen=True)
class Token:
    glyph: str
    start: int
    end: int


class OrderedSourceParser:
    """Non-evaluating structural parser. No symbolic scalar projections."""

    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        pos = 0
        while pos < len(source):
            match = TOKEN_PATTERN.match(source, pos)
            if match is None:
                raise MatrixTensorHIRReject(f"UNSUPPORTED_LEXICAL_GLYPH_AT:{pos}")
            self.tokens.append(Token(match.group(), pos, match.end()))
            pos = match.end()
        self.i = 0

    def peek(self) -> str | None:
        return self.tokens[self.i].glyph if self.i < len(self.tokens) else None

    def consume(self, expected: str | None = None) -> Token:
        if self.i >= len(self.tokens):
            raise MatrixTensorHIRReject("TRUNCATED_SOURCE")
        token = self.tokens[self.i]
        if expected is not None and token.glyph != expected:
            raise MatrixTensorHIRReject(f"UNEXPECTED_TOKEN:{token.glyph}:EXPECTED:{expected}")
        self.i += 1
        return token

    def node(self, kind: str, start: int, end: int, **kwargs: Any) -> dict[str, Any]:
        return {"kind": kind, "span": [start, end],
                "source": self.source[start:end], **kwargs}

    def primary(self) -> dict[str, Any]:
        token = self.consume()
        glyph = token.glyph
        if glyph == "-":
            child = self.primary()
            return self.node("ORDERED_NEGATE", token.start, child["span"][1], child=child)
        if glyph == "(":
            child = self.expression(0)
            close = self.consume(")")
            return self.node("GROUP", token.start, close.end, child=child)
        if glyph.isdecimal():
            return self.node("INTEGER_LITERAL", token.start, token.end, glyph=glyph)
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", glyph):
            if self.peek() != "(":
                return self.node("TYPED_SYMBOL", token.start, token.end, glyph=glyph)
            self.consume("(")
            args = []
            if self.peek() != ")":
                while True:
                    args.append(self.expression(0))
                    if self.peek() != ",":
                        break
                    self.consume(",")
            close = self.consume(")")
            if glyph not in {"List", "MatrixTimes", "NcalcMatrixPower"}:
                raise MatrixTensorHIRReject(f"UNREGISTERED_FUNCTION:{glyph}")
            return self.node("ORDERED_CALL", token.start, close.end,
                             operator=glyph, arguments=args)
        raise MatrixTensorHIRReject(f"INVALID_PRIMARY:{glyph}")

    def expression(self, minimum: int) -> dict[str, Any]:
        left = self.primary()
        while self.peek() in {"/", "=="}:
            operator = self.peek()
            precedence = 20 if operator == "/" else 10
            if precedence < minimum:
                break
            self.consume(operator)
            right = self.expression(precedence + 1)
            left = self.node(
                "ORDERED_DIVIDE" if operator == "/" else "ORDERED_EQUALITY_GATE",
                left["span"][0], right["span"][1],
                operator=operator, left=left, right=right)
        return left

    def parse(self) -> dict[str, Any]:
        result = self.expression(0)
        if self.i != len(self.tokens):
            raise MatrixTensorHIRReject("UNCONSUMED_SOURCE_TOKENS")
        return result


def _call(node: dict[str, Any], operator: str, arity: int) -> list[dict[str, Any]]:
    if node["kind"] != "ORDERED_CALL" or node["operator"] != operator or len(node["arguments"]) != arity:
        raise MatrixTensorHIRReject(f"EXPECTED_{operator}_ARITY_{arity}")
    return node["arguments"]


def _group(node: dict[str, Any]) -> dict[str, Any]:
    if node["kind"] != "GROUP":
        raise MatrixTensorHIRReject("EXPECTED_EXPLICIT_GROUP")
    return node["child"]


def _matrix(node: dict[str, Any]) -> dict[str, Any]:
    rows = _call(node, "List", 4)
    cells = []
    for row in rows:
        cell_row = []
        for cell in _call(row, "List", 4):
            if cell["kind"] == "INTEGER_LITERAL":
                cell_row.append(cell["source"])
            elif (cell["kind"] == "GROUP"
                  and cell["child"]["kind"] == "ORDERED_NEGATE"
                  and cell["child"]["child"]["kind"] == "INTEGER_LITERAL"):
                cell_row.append(cell["source"])
            else:
                raise MatrixTensorHIRReject("MATRIX_LITERAL_CELL_REQUIRED")
        cells.append(cell_row)
    return {"source": node["source"], "span": node["span"],
            "shape": [4, 4], "ordered_cells": cells,
            "cell_count": 16, "position_identity_preserved": True}


def _symbol(node: dict[str, Any], expected: str) -> None:
    if node["kind"] != "TYPED_SYMBOL" or node["glyph"] != expected:
        raise MatrixTensorHIRReject(f"TYPED_SYMBOL_{expected}_REQUIRED")


def _locked_tree(source: str) -> dict[str, Any]:
    ast = OrderedSourceParser(source).parse()
    if ast["kind"] != "ORDERED_EQUALITY_GATE":
        raise MatrixTensorHIRReject("OUTER_EQUALITY_GATE_REQUIRED")
    base, exponent_group = _call(ast["left"], "NcalcMatrixPower", 2)
    numerator_quotient = _group(base)
    if numerator_quotient["kind"] != "ORDERED_DIVIDE":
        raise MatrixTensorHIRReject("ORDERED_QUOTIENT_REQUIRED")
    first, second = _call(numerator_quotient["left"], "MatrixTimes", 2)
    denominator, symbol_s = _call(numerator_quotient["right"], "MatrixTimes", 2)
    symbol_v, closure = _call(ast["right"], "MatrixTimes", 2)
    if first["kind"] != "ORDERED_NEGATE" or second["kind"] != "ORDERED_NEGATE":
        raise MatrixTensorHIRReject("NEGATED_OPERAND_ORDER_REQUIRED")
    _symbol(symbol_s, "s")
    _symbol(symbol_v, "v")
    exponent = _group(exponent_group)
    if (exponent["kind"] != "ORDERED_NEGATE"
        or exponent["child"]["kind"] != "INTEGER_LITERAL"
        or exponent["child"]["glyph"] != "4"):
        raise MatrixTensorHIRReject("NEGATIVE_FOUR_EXPONENT_REQUIRED")
    matrices = [_matrix(first["child"]), _matrix(second["child"]),
                _matrix(denominator), _matrix(closure)]
    expected = [
        [["1","1","1","1"],["(-1)","1","1","1"],
         ["(-1)","(-1)","1","1"],["(-1)","(-1)","(-1)","1"]],
        [["(-1)","(-1)","(-1)","(-1)"],["1","(-1)","(-1)","(-1)"],
         ["1","1","(-1)","(-1)"],["1","1","1","(-1)"]],
        [["2","2","2","2"],["4","2","2","2"],
         ["4","4","2","2"],["4","4","4","2"]],
        [["0","0","0","0"],["1","0","0","0"],
         ["1","1","0","0"],["1","1","1","0"]],
    ]
    if [row["ordered_cells"] for row in matrices] != expected:
        raise MatrixTensorHIRReject("LITERAL_MATRIX_SOURCE_TOPOLOGY_DRIFT")
    return {"ordered_ast": ast, "matrix_occurrences": matrices,
            "exponent_token": exponent_group["source"],
            "typed_symbols": [symbol_s["source"], symbol_v["source"]],
            "ordered_matrix_operators": ["MatrixTimes"] * 3}


def stage_hir(root: str | Path | None = None) -> dict[str, Any]:
    repo = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[2]
    data = (repo / SOURCE_PATH).read_bytes()
    if len(data) != SOURCE_BYTES or sha256(data).hexdigest() != SOURCE_SHA256:
        raise MatrixTensorHIRReject("VERBATIM_SOURCE_IDENTITY_DRIFT")
    topology = _locked_tree(data.decode("utf-8", "strict"))
    diagnostic = sha256(
        b"HHS:READ_ONLY:MATRIX_HIR:V1\0"
        + json.dumps(topology, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema": SCHEMA, "source_path": str(SOURCE_PATH),
        "source_sha256": SOURCE_SHA256, "source_bytes": SOURCE_BYTES,
        "source_preserved_verbatim": True,
        "pass169_type": PASS169_CANONICAL_TYPE, "node_kind": NODE_KIND,
        "source_shape": [4, 4], **topology,
        "structural_sha256_non_authoritative": diagnostic,
        "matrix_power_value_derived": False,
        "matrix_division_evaluated": False,
        "typed_s_v_substituted": False,
        "host_matrixpower_used": False,
        "floating_point_authority": False,
        "vm81_execution_verified": False,
        "hash72_commit_authority": False,
        "hash216_commit_authority": False,
        "canonical_vm81_mutation_authority": False,
        "requires_registered_native_matrix_operators": True,
        "requires_existing_singleton_vm81_authority": True,
        "status": "EXACT_SOURCE_HIR_STAGED_NATIVE_4X4_EXECUTION_PENDING",
    }
