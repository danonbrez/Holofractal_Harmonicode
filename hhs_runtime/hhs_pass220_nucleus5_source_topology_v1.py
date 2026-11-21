"""Exact position-5 source topology for inherited Pass159 / Pass168 lowering.

This is an immutable source-span / address witness. It does not evaluate
MatrixTimes, invent VM81 opcodes, or grant canonical mutation authority.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any

from hhs_runtime.hhs_pass220_nucleus5_matrixtimes_abp_source_v1 import (
    Nucleus5Source,
    VERBATIM_SOURCE,
)


class Nucleus5TopologyError(ValueError):
    pass


def _matching(source: str, index: int) -> int:
    pairs = {"(": ")", "{": "}"}
    if source[index] not in pairs:
        raise Nucleus5TopologyError("NOT_OPEN_DELIMITER")
    stack: list[str] = []
    for pos in range(index, len(source)):
        char = source[pos]
        if char in pairs:
            stack.append(pairs[char])
        elif char in ")}":
            if not stack or stack.pop() != char:
                raise Nucleus5TopologyError("UNBALANCED_DELIMITERS")
            if not stack:
                return pos + 1
    raise Nucleus5TopologyError("UNTERMINATED_DELIMITER")


def _split_cells(source: str, start: int, stop: int) -> tuple[tuple[int, int], ...]:
    pieces: list[tuple[int, int]] = []
    stack: list[str] = []
    begin = start
    match = {"(": ")", "{": "}"}
    for pos in range(start, stop):
        char = source[pos]
        if char in match:
            stack.append(match[char])
        elif char in ")}":
            if not stack or stack.pop() != char:
                raise Nucleus5TopologyError("CELL_NESTING_DRIFT")
        elif char == "," and not stack:
            if begin == pos:
                raise Nucleus5TopologyError("EMPTY_CELL")
            pieces.append((begin, pos))
            begin = pos + 1
    if stack or begin >= stop:
        raise Nucleus5TopologyError("CELL_UNTERMINATED")
    pieces.append((begin, stop))
    return tuple(pieces)


def matrix_occurrences(source: str = VERBATIM_SOURCE) -> tuple[dict[str, Any], ...]:
    """Keep each ordered 4x4 brace matrix and every exact cell byte span."""
    matrices: list[dict[str, Any]] = []
    position = 0
    while True:
        start = source.find("{{", position)
        if start < 0:
            break
        end = _matching(source, start)
        outer = _split_cells(source, start + 1, end - 1)
        if len(outer) != 4:
            raise Nucleus5TopologyError("MATRIX_ROW_COUNT")
        cells = []
        for row_index, (rstart, rend) in enumerate(outer):
            if source[rstart] != "{" or source[rend - 1] != "}":
                raise Nucleus5TopologyError("MATRIX_ROW_DELIMITER")
            row = _split_cells(source, rstart + 1, rend - 1)
            if len(row) != 4:
                raise Nucleus5TopologyError("MATRIX_COLUMN_COUNT")
            for col_index, (cstart, cend) in enumerate(row):
                cells.append({
                    "row": row_index, "column": col_index,
                    "start": cstart, "end": cend,
                    "source": source[cstart:cend],
                })
        matrices.append({
            "index": len(matrices),
            "start": start, "end": end,
            "source": source[start:end],
            "cells": cells,
        })
        position = end
    if len(matrices) != 3 or any(len(m["cells"]) != 16 for m in matrices):
        raise Nucleus5TopologyError("EXPECTED_THREE_ORDERED_4X4_MATRICES")
    return tuple(matrices)


def source_topology(configuration: str) -> dict[str, Any]:
    """Reversible source-coordinate witness, not a mathematical proof."""
    witness = Nucleus5Source()
    circuit = witness.native_compilation_source_bytes(configuration).decode("utf-8")
    if not circuit.startswith("List(" + VERBATIM_SOURCE + ","):
        raise Nucleus5TopologyError("EXACT_TENSOR_PREFIX_LOST")
    matrix_data = matrix_occurrences()
    edges: list[dict[str, Any]] = []
    cursor = 0
    while True:
        index = circuit.find("==", cursor)
        if index < 0:
            break
        edges.append({"index": len(edges), "start": index, "end": index + 2})
        cursor = index + 2
    expected = 3 + sum(edge.count("==") for edge in witness.parameter_edges(configuration))
    if len(edges) != expected:
        raise Nucleus5TopologyError("EQUALITY_OCCURRENCE_DRIFT")
    if any(circuit[edge["start"]:edge["end"]] != "==" for edge in edges):
        raise Nucleus5TopologyError("EQUALITY_SPAN_LOST")
    if any(
        VERBATIM_SOURCE[cell["start"]:cell["end"]] != cell["source"]
        for matrix in matrix_data for cell in matrix["cells"]
    ):
        raise Nucleus5TopologyError("CELL_SOURCE_ROUNDTRIP_LOST")
    return {
        "schema": "HHS_PASS220_NUCLEUS5_SOURCE_TOPOLOGY_V1",
        "configuration": configuration,
        "nucleus_cell": 5,
        "source_sha256": witness.exact_source_sha256,
        "circuit_sha256": sha256(circuit.encode("utf-8")).hexdigest(),
        "matrix_count": len(matrix_data),
        "matrices": matrix_data,
        "equality_count": len(edges),
        "equality_occurrences": edges,
        "candidate_only": True,
        "native_effectful_vmir_execution_verified": False,
        "canonical_vm81_admission": False,
        "hash216_persisted": False,
    }
