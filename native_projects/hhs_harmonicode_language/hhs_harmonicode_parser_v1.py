"""Deterministic, non-executing Harmonicode parser for Pass 075.

The parser preserves source spans and ordered symbolic identity. It does not
simplify algebra, commute products, execute gates, or claim invariant success.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence, Tuple
import re

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root, sha256, stable

PARSER_VERSION = "HHS_HARMONICODE_PARSER_PASS_075_V1"
IDENTIFIER_PATTERN = re.compile(r"[A-Za-z_ΔΨΘΩπρφψχδτ][A-Za-z0-9_ΔΨΘΩπρφψχδτ₀-₉]*")
INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")
RATIONAL_PATTERN = re.compile(r"^[+-]?\d+/\d+$")
BOOLEAN_PATTERN = re.compile(r"^(true|false)$", re.IGNORECASE)
BARE_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_ΔΨΘΩπρφψχδτ][A-Za-z0-9_ΔΨΘΩπρφψχδτ₀-₉]*$")


@dataclass(frozen=True)
class Segment:
    text: str
    start: int
    end: int


def normalize_source(source: str) -> str:
    return source.replace("\r\n", "\n").replace("\r", "\n")


def _position(source: str, offset: int) -> Tuple[int, int]:
    line = source.count("\n", 0, offset) + 1
    previous = source.rfind("\n", 0, offset)
    column = offset + 1 if previous < 0 else offset - previous
    return line, column


def source_span(source: str, start: int, end: int) -> Dict[str, Any]:
    line_start, column_start = _position(source, start)
    line_end, column_end = _position(source, end)
    text = source[start:end]
    return {
        "start": start,
        "end": end,
        "line_start": line_start,
        "column_start": column_start,
        "line_end": line_end,
        "column_end": column_end,
        "text_sha256": sha256(text),
    }


def split_top_level(source: str, separators: Iterable[str] = ("\n", ";")) -> List[Segment]:
    normalized = normalize_source(source)
    sep = set(separators)
    segments: List[Segment] = []
    stack: List[str] = []
    pairs = {"}": "{", ")": "(", "]": "["}
    quote = ""
    escaped = False
    start = 0
    for index, char in enumerate(normalized):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
        elif char in "{([":
            stack.append(char)
        elif char in "})]":
            if stack and stack[-1] == pairs[char]:
                stack.pop()
        elif char in sep and not stack:
            raw = normalized[start:index]
            left = len(raw) - len(raw.lstrip())
            right = len(raw.rstrip())
            if right > left:
                segments.append(Segment(raw[left:right], start + left, start + right))
            start = index + 1
    raw = normalized[start:]
    left = len(raw) - len(raw.lstrip())
    right = len(raw.rstrip())
    if right > left:
        segments.append(Segment(raw[left:right], start + left, start + right))
    return segments


def split_operator(text: str, operator: str) -> List[str]:
    parts: List[str] = []
    stack: List[str] = []
    pairs = {"}": "{", ")": "(", "]": "["}
    quote = ""
    escaped = False
    start = 0
    index = 0
    while index < len(text):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            index += 1
            continue
        if char in "{([":
            stack.append(char)
            index += 1
            continue
        if char in "})]":
            if stack and stack[-1] == pairs[char]:
                stack.pop()
            index += 1
            continue
        if not stack and text.startswith(operator, index):
            value = text[start:index].strip()
            if value:
                parts.append(value)
            start = index + len(operator)
            index = start
            continue
        index += 1
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def delimiter_diagnostics(source: str) -> List[Dict[str, Any]]:
    stack: List[Tuple[str, int]] = []
    pairs = {"}": "{", ")": "(", "]": "["}
    diagnostics: List[Dict[str, Any]] = []
    quote = ""
    escaped = False
    for index, char in enumerate(source):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
        elif char in "{([":
            stack.append((char, index))
        elif char in "})]":
            if not stack or stack[-1][0] != pairs[char]:
                diagnostics.append({"code": "UNMATCHED_CLOSING_DELIMITER", "offset": index, "token": char, "severity": "ERROR"})
            else:
                stack.pop()
    for token, offset in stack:
        diagnostics.append({"code": "UNCLOSED_DELIMITER", "offset": offset, "token": token, "severity": "ERROR"})
    if quote:
        diagnostics.append({"code": "UNCLOSED_STRING", "offset": len(source), "token": quote, "severity": "ERROR"})
    return diagnostics


def infer_type(expression: str) -> str:
    value = expression.strip()
    if INTEGER_PATTERN.fullmatch(value):
        return "EXACT_INTEGER"
    if RATIONAL_PATTERN.fullmatch(value):
        return "EXACT_RATIONAL"
    if BOOLEAN_PATTERN.fullmatch(value):
        return "BOOLEAN"
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1]
        return "MATRIX" if any(x.strip().startswith("[") for x in split_operator(inner, ",")) else "LIST"
    if re.match(r"^[A-Za-z_ΔΨΘΩπρφψχδτ][A-Za-z0-9_ΔΨΘΩπρφψχδτ₀-₉]*\s*\(", value):
        return "FUNCTION_CALL"
    if BARE_IDENTIFIER_PATTERN.fullmatch(value):
        return "ORDERED_PRODUCT" if len(value) == 2 and value.isascii() and value.isalpha() else "SYMBOL"
    return "SYMBOLIC_EXPRESSION"


def extract_symbols(expression: str) -> List[str]:
    reserved = {"true", "false", "List", "Sqrt", "Mod", "Sum"}
    return [value for value in IDENTIFIER_PATTERN.findall(expression) if value not in reserved]


def _classify(segment: Segment, source: str, index: int) -> Dict[str, Any]:
    text = segment.text
    kind = "RawExpression"
    operator = ""
    terms: List[str] = []
    name = ""
    children: List[Dict[str, Any]] = []
    gate = re.match(r"^([A-Za-z_ΔΨΘΩπρφψχδτ][A-Za-z0-9_ΔΨΘΩπρφψχδτ₀-₉]*)\s*:=\s*\{(.*)\}$", text, re.DOTALL)
    if gate:
        kind = "GateDeclaration"
        operator = ":="
        name = gate.group(1)
        body_start_local = text.find("{") + 1
        body_end_local = text.rfind("}")
        body = text[body_start_local:body_end_local]
        for child_index, child in enumerate(split_top_level(body, separators=("\n", ";", ","))):
            absolute = Segment(child.text, segment.start + body_start_local + child.start, segment.start + body_start_local + child.end)
            children.append(_classify(absolute, source, child_index))
    elif "≠" in text:
        kind, operator, terms = "DistinctChain", "≠", split_operator(text, "≠")
    elif "!=" in text:
        kind, operator, terms = "DistinctChain", "!=", split_operator(text, "!=")
    elif "==" in text:
        kind, operator, terms = "AssertEquality", "==", split_operator(text, "==")
    elif "=" in text and ":=" not in text:
        kind, operator, terms = "ChainEquality", "=", split_operator(text, "=")
    elif BARE_IDENTIFIER_PATTERN.fullmatch(text):
        kind, name = "GateInvocation", text
    else:
        terms = [text]

    symbols = sorted(set(extract_symbols(text)))
    body = {
        "schema": "HHS_HARMONICODE_AST_NODE_V1",
        "node_id": f"node:{index}:{product_root('pass075_node_identity', {'text': text, 'start': segment.start})[-16:]}",
        "kind": kind,
        "operator": operator,
        "name": name,
        "terms": terms,
        "term_types": [infer_type(term) for term in terms],
        "symbols": symbols,
        "source_span": source_span(source, segment.start, segment.end),
        "source_text": text,
        "children": children,
        "ordered_symbol_identity_preserved": True,
    }
    body["node_root_hash72"] = product_root("pass075_harmonicode_ast_node", body)
    return stable(body)


def parse_source(source: str) -> Dict[str, Any]:
    normalized = normalize_source(source)
    diagnostics = delimiter_diagnostics(normalized)
    nodes = [_classify(segment, normalized, index) for index, segment in enumerate(split_top_level(normalized))]
    if not normalized.strip():
        diagnostics.append({"code": "EMPTY_SOURCE", "severity": "ERROR", "offset": 0})
    if not nodes and normalized.strip():
        diagnostics.append({"code": "NO_PARSEABLE_STATEMENTS", "severity": "ERROR", "offset": 0})
    ast = {
        "schema": "HHS_HARMONICODE_AST_V1",
        "parser_version": PARSER_VERSION,
        "source_sha256": sha256(normalized),
        "source_length": len(normalized),
        "nodes": nodes,
        "diagnostics": diagnostics,
        "source_spans_preserved": True,
        "ordered_products_not_commuted": True,
        "parser_executes_program_effects": False,
    }
    ast["ast_root_hash72"] = product_root("pass075_harmonicode_ast", ast)
    return stable(ast)
