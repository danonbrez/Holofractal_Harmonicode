"""Additive nested-expression AST membrane for HARMONICODE.

This module is a syntax-preserving successor to the frozen Pass 075 statement
parser. It does not replace or mutate that parser. It adds deterministic,
source-spanned nodes for power surfaces, chained powers, Unicode superscript
powers, and Unicode radical-exponent surfaces.

No algebra is simplified, no power-chain associativity is chosen, no scalar
value is inferred, and no VM81/Hash72/Hash216 admission authority is created.
"""
from __future__ import annotations

from hashlib import sha256 as _sha256
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root, stable
from native_projects.hhs_harmonicode_language.hhs_harmonicode_parser_v1 import (
    PARSER_VERSION as PASS075_PARSER_VERSION,
    normalize_source,
    parse_source as parse_source_v1,
    source_span,
)

PARSER_VERSION = "HHS_HARMONICODE_NESTED_EXPRESSION_AST_PASS_219_V2"
SCHEMA = "HHS_HARMONICODE_NESTED_EXPRESSION_AST_V2"
NODE_SCHEMA = "HHS_HARMONICODE_NESTED_EXPRESSION_NODE_V2"

_SUPERSCRIPT_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_SUPERSCRIPT_TO_ASCII = str.maketrans(_SUPERSCRIPT_DIGITS, "0123456789")
_IDENTIFIER_EXTRA = "_ΔΠπρφψχδτΘΩ"
_OPEN_TO_CLOSE = {"(": ")", "[": "]", "{": "}"}
_CLOSE_TO_OPEN = {value: key for key, value in _OPEN_TO_CLOSE.items()}


def _is_identifier_start(char: str) -> bool:
    return bool(char) and (char.isalpha() or char in _IDENTIFIER_EXTRA)


def _is_identifier_char(char: str) -> bool:
    return (
        bool(char)
        and char not in _SUPERSCRIPT_DIGITS
        and (char.isalnum() or char in _IDENTIFIER_EXTRA or char in "₀₁₂₃₄₅₆₇₈₉")
    )


def _quoted_offsets(source: str) -> set[int]:
    quoted: set[int] = set()
    quote = ""
    escaped = False
    for index, char in enumerate(source):
        if quote:
            quoted.add(index)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
            quoted.add(index)
    return quoted


def _match_left(source: str, closing_index: int) -> int | None:
    closing = source[closing_index]
    opening = _CLOSE_TO_OPEN.get(closing)
    if not opening:
        return None
    stack = [closing]
    quote = ""
    escaped = False
    index = closing_index - 1
    while index >= 0:
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            index -= 1
            continue
        if char in {"'", '"'}:
            quote = char
            index -= 1
            continue
        if char == closing:
            stack.append(char)
        elif char == opening:
            stack.pop()
            if not stack:
                return index
        index -= 1
    return None


def _match_right(source: str, opening_index: int) -> int | None:
    opening = source[opening_index]
    closing = _OPEN_TO_CLOSE.get(opening)
    if not closing:
        return None
    stack = [opening]
    quote = ""
    escaped = False
    for index in range(opening_index + 1, len(source)):
        char = source[index]
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
            continue
        if char == opening:
            stack.append(char)
        elif char == closing:
            stack.pop()
            if not stack:
                return index
    return None


def _left_atom(source: str, caret: int) -> Tuple[int, int] | None:
    index = caret - 1
    while index >= 0 and source[index].isspace():
        index -= 1
    if index < 0:
        return None
    if source[index] in _CLOSE_TO_OPEN:
        start = _match_left(source, index)
        if start is None:
            return None
        return start, index + 1

    end = index + 1
    while index >= 0 and source[index] in _SUPERSCRIPT_DIGITS:
        index -= 1
    while index >= 0 and _is_identifier_char(source[index]):
        index -= 1
    start = index + 1
    if start == end:
        return None
    return start, end


def _right_atom(source: str, caret: int) -> Tuple[int, int] | None:
    index = caret + 1
    while index < len(source) and source[index].isspace():
        index += 1
    if index >= len(source):
        return None
    if source[index] in _OPEN_TO_CLOSE:
        end_index = _match_right(source, index)
        if end_index is None:
            return None
        return index, end_index + 1

    start = index
    if source[index] in "+-" and index + 1 < len(source) and source[index + 1].isdigit():
        index += 1
    if index < len(source) and source[index].isdigit():
        while index < len(source) and source[index].isdigit():
            index += 1
        return start, index

    if not _is_identifier_start(source[index]):
        return None
    index += 1
    while index < len(source) and _is_identifier_char(source[index]):
        index += 1
    while index < len(source) and source[index] in _SUPERSCRIPT_DIGITS:
        index += 1
    return start, index


def _operand(source: str, start: int, end: int, index: int) -> Dict[str, Any]:
    return {
        "index": index,
        "source_text": source[start:end],
        "source_span": source_span(source, start, end),
    }


def _node_identity(kind: str, source: str, start: int, end: int) -> str:
    payload = f"{kind}|{start}|{end}|{source[start:end]}".encode("utf-8")
    return f"exprv2:{_sha256(payload).hexdigest()[:32]}"


def _build_node(
    source: str,
    *,
    kind: str,
    start: int,
    end: int,
    operator: str,
    operand_spans: Sequence[Tuple[int, int]],
    associativity: str,
    syntax_role: str,
    metadata: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "schema": NODE_SCHEMA,
        "node_id": _node_identity(kind, source, start, end),
        "kind": kind,
        "operator": operator,
        "syntax_role": syntax_role,
        "source_text": source[start:end],
        "source_span": source_span(source, start, end),
        "ordered_operands": [
            _operand(source, operand_start, operand_end, index)
            for index, (operand_start, operand_end) in enumerate(operand_spans)
        ],
        "associativity": associativity,
        "scalar_value": None,
        "syntax_only": True,
        "canonical_admission": False,
        "ordered_operand_identity_preserved": True,
        "children": [],
    }
    if metadata:
        body.update(dict(metadata))
    return body


def _superscript_nodes(source: str, quoted: set[int]) -> List[Dict[str, Any]]:
    nodes: List[Dict[str, Any]] = []
    index = 0
    while index < len(source):
        if index in quoted or not _is_identifier_start(source[index]):
            index += 1
            continue
        base_start = index
        index += 1
        while index < len(source) and _is_identifier_char(source[index]):
            index += 1
        exponent_start = index
        while index < len(source) and source[index] in _SUPERSCRIPT_DIGITS:
            index += 1
        if exponent_start == index:
            continue
        exponent_ascii = source[exponent_start:index].translate(_SUPERSCRIPT_TO_ASCII)
        nodes.append(
            _build_node(
                source,
                kind="SuperscriptPower",
                start=base_start,
                end=index,
                operator="SUPERSCRIPT",
                operand_spans=((base_start, exponent_start), (exponent_start, index)),
                associativity="EXPLICIT_SUPERSCRIPT_BINDING",
                syntax_role="POWER_SURFACE",
                metadata={"exponent_digits_ascii": exponent_ascii},
            )
        )
    return nodes


def _caret_power_nodes(source: str, quoted: set[int]) -> List[Dict[str, Any]]:
    surfaces: List[Dict[str, Any]] = []
    records: List[Dict[str, Any]] = []
    for caret, char in enumerate(source):
        if char != "^" or caret in quoted:
            continue
        left = _left_atom(source, caret)
        right = _right_atom(source, caret)
        if left is None or right is None:
            continue
        left_start, left_end = left
        right_start, right_end = right
        node = _build_node(
            source,
            kind="PowerSurface",
            start=left_start,
            end=right_end,
            operator="^",
            operand_spans=(left, right),
            associativity="SINGLE_CARET_SURFACE",
            syntax_role="POWER_SURFACE",
            metadata={"caret_offset": caret},
        )
        surfaces.append(node)
        records.append({"caret": caret, "left": left, "right": right, "node": node})

    nodes = list(surfaces)
    by_caret = {record["caret"]: record for record in records}
    chain_keys: set[Tuple[int, int]] = set()
    for record in records:
        operands = [record["left"], record["right"]]
        current = record
        while True:
            next_record = by_caret.get(current["right"][1])
            if next_record is None or next_record["left"] != current["right"]:
                break
            operands.append(next_record["right"])
            current = next_record
        if len(operands) < 3:
            continue
        start = operands[0][0]
        end = operands[-1][1]
        key = (start, end)
        if key in chain_keys:
            continue
        chain_keys.add(key)
        nodes.append(
            _build_node(
                source,
                kind="PowerChain",
                start=start,
                end=end,
                operator="^",
                operand_spans=tuple(operands),
                associativity="UNRESOLVED_SOURCE_CHAIN",
                syntax_role="CHAINED_POWER_SURFACE",
                metadata={
                    "caret_count": len(operands) - 1,
                    "algebraic_associativity_selected": False,
                },
            )
        )

    for record in records:
        left_start, left_end = record["left"]
        if left_start <= 0 or source[left_start - 1] != "√":
            continue
        right_start, right_end = record["right"]
        nodes.append(
            _build_node(
                source,
                kind="RadicalPowerSurface",
                start=left_start - 1,
                end=right_end,
                operator="√…^…",
                operand_spans=((left_start, left_end), (right_start, right_end)),
                associativity="EXPLICIT_RADICAL_THEN_EXPONENT_SURFACE",
                syntax_role="RADICAL_EXPONENT_SURFACE",
                metadata={
                    "radical_glyph": "√",
                    "radical_source_span": source_span(source, left_start - 1, left_end),
                },
            )
        )
    return nodes


def _attach_children(source: str, nodes: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ordered = [dict(node) for node in nodes]
    spans = {
        node["node_id"]: (int(node["source_span"]["start"]), int(node["source_span"]["end"]))
        for node in ordered
    }
    for parent in ordered:
        p_start, p_end = spans[parent["node_id"]]
        contained = [
            child
            for child in ordered
            if child["node_id"] != parent["node_id"]
            and p_start <= spans[child["node_id"]][0]
            and spans[child["node_id"]][1] <= p_end
            and (p_start, p_end) != spans[child["node_id"]]
        ]
        direct: List[Dict[str, Any]] = []
        for child in contained:
            c_start, c_end = spans[child["node_id"]]
            has_intermediate = False
            for middle in contained:
                if middle["node_id"] == child["node_id"]:
                    continue
                m_start, m_end = spans[middle["node_id"]]
                if (
                    p_start <= m_start <= c_start
                    and c_end <= m_end <= p_end
                    and (m_start, m_end) != (c_start, c_end)
                    and (m_start, m_end) != (p_start, p_end)
                ):
                    has_intermediate = True
                    break
            if not has_intermediate:
                direct.append(child)
        parent["children"] = [
            child["node_id"]
            for child in sorted(
                direct,
                key=lambda item: (
                    int(item["source_span"]["start"]),
                    int(item["source_span"]["end"]),
                    item["kind"],
                ),
            )
        ]

    finalized: List[Dict[str, Any]] = []
    for node in ordered:
        material = dict(node)
        material["node_root_hash72"] = product_root(
            "pass219_harmonicode_nested_expression_node_v2", material
        )
        finalized.append(stable(material))
    return sorted(
        finalized,
        key=lambda item: (
            int(item["source_span"]["start"]),
            int(item["source_span"]["end"]),
            item["kind"],
            item["node_id"],
        ),
    )


def nested_expression_nodes(source: str) -> List[Dict[str, Any]]:
    normalized = normalize_source(source)
    quoted = _quoted_offsets(normalized)
    nodes = _superscript_nodes(normalized, quoted) + _caret_power_nodes(normalized, quoted)
    deduped: Dict[Tuple[str, int, int], Dict[str, Any]] = {}
    for node in nodes:
        key = (node["kind"], int(node["source_span"]["start"]), int(node["source_span"]["end"]))
        deduped[key] = node
    return _attach_children(normalized, list(deduped.values()))


def parse_source(source: str) -> Dict[str, Any]:
    normalized = normalize_source(source)
    predecessor = parse_source_v1(normalized)
    nested = nested_expression_nodes(normalized)
    ast: Dict[str, Any] = {
        "schema": SCHEMA,
        "parser_version": PARSER_VERSION,
        "predecessor_parser_version": PASS075_PARSER_VERSION,
        "predecessor_ast_root_hash72": predecessor["ast_root_hash72"],
        "source_sha256": predecessor["source_sha256"],
        "source_length": predecessor["source_length"],
        "statement_nodes": predecessor["nodes"],
        "nested_expression_nodes": nested,
        "diagnostics": predecessor["diagnostics"],
        "source_spans_preserved": True,
        "ordered_products_not_commuted": True,
        "parser_executes_program_effects": False,
        "canonical_admission_authority": False,
        "capabilities": {
            "pass075_statement_ast_preserved": True,
            "superscript_power_surface": True,
            "ascii_caret_power_surface": True,
            "chained_power_surface": True,
            "unicode_radical_exponent_surface": True,
            "power_chain_associativity_selected": False,
            "general_nested_expression_ast_complete": False,
        },
    }
    ast["ast_root_hash72"] = product_root("pass219_harmonicode_nested_expression_ast_v2", ast)
    return stable(ast)


def find_enclosing_nodes(
    ast: Mapping[str, Any],
    start: int,
    end: int,
    *,
    kinds: Iterable[str] | None = None,
) -> List[Dict[str, Any]]:
    kind_set = set(kinds or ())
    matches = []
    for node in ast.get("nested_expression_nodes", []):
        if kind_set and node.get("kind") not in kind_set:
            continue
        span = node.get("source_span", {})
        n_start = int(span.get("start", -1))
        n_end = int(span.get("end", -1))
        if n_start <= start and end <= n_end:
            matches.append(dict(node))
    return sorted(
        matches,
        key=lambda node: (
            int(node["source_span"]["end"]) - int(node["source_span"]["start"]),
            int(node["source_span"]["start"]),
            node["kind"],
        ),
    )
