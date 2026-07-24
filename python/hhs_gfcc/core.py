from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, getcontext
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
import json
import struct

CONTRACT_ID = "HHS-P152-GFCC"
PASS_NUMBER = "152"
IMPLEMENTATION_VERSION = "HHS_GFCC_P152_V1"
INTERPRETATION_VERSION = 1
HASH72_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"
PROJECTION_ALPHABET = HASH72_ALPHABET
HASH72_POSITIONS = 72
HASH216_POSITIONS = 216
_MASK64 = (1 << 64) - 1
_HASH72_STEP = 0x9E3779B97F4A7C15
_HASH216_STEP = 0x517CC1B727220A95
_FOLD_SEED = 0x179971179971

if len(HASH72_ALPHABET) != HASH72_POSITIONS:
    raise RuntimeError("canonical Hash72 alphabet must contain exactly 72 symbols")


def dataclass_is_instance(value: Any) -> bool:
    return hasattr(value, "__dataclass_fields__") and not isinstance(value, type)


def stable(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    if dataclass_is_instance(value):
        value = asdict(value)
    return json.loads(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        )
    )


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        stable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def digest256(value: Any) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def _mix64(value: int) -> int:
    value &= _MASK64
    value ^= value >> 33
    value = (value * 0xFF51AFD7ED558CCD) & _MASK64
    value ^= value >> 33
    value = (value * 0xC4CEB9FE1A85EC53) & _MASK64
    value ^= value >> 33
    return value & _MASK64


def _fold_bytes(data: bytes) -> int:
    state = _FOLD_SEED
    for index, byte in enumerate(data):
        state ^= int(byte) << ((index % 8) * 8)
        state = _mix64((state + index + 1) & _MASK64)
    return state


def _hash_from_seed(seed: int, positions: int, step: int) -> str:
    state = seed & _MASK64
    symbols: list[str] = []
    for index in range(positions):
        state = _mix64((state + ((step * (index + 1)) & _MASK64)) & _MASK64)
        symbols.append(HASH72_ALPHABET[state % HASH72_POSITIONS])
    return "".join(symbols)


def inherited_hash72(data: bytes | bytearray | memoryview | str) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    return _hash_from_seed(_fold_bytes(raw), HASH72_POSITIONS, _HASH72_STEP)


def inherited_hash216(data: bytes | bytearray | memoryview | str) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    return _hash_from_seed(_fold_bytes(raw), HASH216_POSITIONS, _HASH216_STEP)


def _authority_hash72(authority_root: str) -> str:
    if len(authority_root) == HASH72_POSITIONS and all(
        symbol in HASH72_ALPHABET for symbol in authority_root
    ):
        return authority_root
    return inherited_hash72(authority_root.encode("utf-8"))


def _u32(value: int) -> bytes:
    if not 0 <= value <= 0xFFFFFFFF:
        raise ValueError("u32 out of range")
    return int(value).to_bytes(4, "big", signed=False)


def _i64(value: int) -> bytes:
    if not -(1 << 63) <= value < (1 << 63):
        raise ValueError("i64 out of range")
    return int(value).to_bytes(8, "big", signed=True)


@dataclass(frozen=True)
class ExactRational:
    numerator: int
    denominator: int = 1

    def __post_init__(self) -> None:
        if self.denominator == 0:
            raise ValueError("HHS_GFCC_EXACTNESS_VIOLATION:zero denominator")
        reduced = Fraction(self.numerator, self.denominator)
        object.__setattr__(self, "numerator", reduced.numerator)
        object.__setattr__(self, "denominator", reduced.denominator)

    def __add__(self, other: "ExactRational") -> "ExactRational":
        result = Fraction(self.numerator, self.denominator) + Fraction(
            other.numerator, other.denominator
        )
        return ExactRational(result.numerator, result.denominator)

    def __sub__(self, other: "ExactRational") -> "ExactRational":
        result = Fraction(self.numerator, self.denominator) - Fraction(
            other.numerator, other.denominator
        )
        return ExactRational(result.numerator, result.denominator)

    def __mul__(self, other: "ExactRational") -> "ExactRational":
        result = Fraction(self.numerator, self.denominator) * Fraction(
            other.numerator, other.denominator
        )
        return ExactRational(result.numerator, result.denominator)

    def __truediv__(self, other: "ExactRational") -> "ExactRational":
        if other.numerator == 0:
            raise ValueError("HHS_GFCC_EXACTNESS_VIOLATION:division by zero")
        result = Fraction(self.numerator, self.denominator) / Fraction(
            other.numerator, other.denominator
        )
        return ExactRational(result.numerator, result.denominator)

    def to_dict(self) -> dict[str, int]:
        return {"numerator": self.numerator, "denominator": self.denominator}

    @property
    def is_integer(self) -> bool:
        return self.denominator == 1

    @property
    def integer(self) -> int:
        if not self.is_integer:
            raise ValueError("not an integer")
        return self.numerator


@dataclass(frozen=True)
class SymbolState:
    symbol_id: str
    display: str
    type: str
    exact: ExactRational
    dependency_ids: tuple[str, ...]


@dataclass(frozen=True)
class DependencyNode:
    node_id: str
    operation: str
    inputs: tuple[str, ...]
    expected: ExactRational
    shell: str | None = None


@dataclass(frozen=True)
class Delta369:
    ring_modulus: int
    zero_indexed_partition: tuple[tuple[int, int, int], ...]
    one_indexed_partition: tuple[tuple[int, int, int], ...]
    active_indexing: str
    matrix_shape: tuple[int, int]
    decimal_projection: str
    geometry_coordinates: tuple[str, str, str, str]
    golden_correspondence: str
    phase_structure: str


@dataclass(frozen=True)
class CollisionObject:
    object_id: str
    x_q16: int
    y_q16: int
    half_width_q16: int
    half_height_q16: int
    scale: ExactRational
    phase: int
    vm81_cell: int
    hash72: str
    hash216: str


class GFCCError(ValueError):
    def __init__(
        self,
        code: str,
        component: str,
        operation: str,
        message: str,
        details: Mapping[str, Any] | None = None,
        *,
        authority_level: str = "A3",
    ) -> None:
        super().__init__(f"{code}:{component}:{operation}:{message}")
        self.code = code
        self.component = component
        self.operation = operation
        self.message = message
        self.details = stable(details or {})
        self.authority_level = authority_level

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "authority_level": self.authority_level,
            "component": self.component,
            "operation": self.operation,
            "message": self.message,
            "details": self.details,
        }


def canonical_spec(fibonacci_stage: int = 8) -> dict[str, Any]:
    return stable(
        {
            "contract_id": CONTRACT_ID,
            "pass_number": PASS_NUMBER,
            "schema_version": 1,
            "interpretation_version": INTERPRETATION_VERSION,
            "symbols": {
                "a2": {"display": "a^2", "type": "exact_integer", "value": 1},
                "b2": {"display": "b^2", "type": "exact_integer", "value": 2},
                "c2": {"display": "c^2", "type": "exact_integer", "value": 3},
                "d2": {"display": "d^2", "type": "exact_integer", "value": 5},
                "e2": {"display": "e^2", "type": "exact_integer", "value": 8},
            },
            "dependencies": [
                {
                    "node_id": "c2",
                    "operation": "add",
                    "inputs": ["b2", "a2"],
                    "expected": 3,
                },
                {
                    "node_id": "d2",
                    "operation": "add",
                    "inputs": ["c2", "b2"],
                    "expected": 5,
                },
                {
                    "node_id": "e2",
                    "operation": "add",
                    "inputs": ["d2", "c2"],
                    "expected": 8,
                    "shell": "numerator",
                },
                {
                    "node_id": "c2_minus_a2",
                    "operation": "sub",
                    "inputs": ["c2", "a2"],
                    "expected": 2,
                    "shell": "denominator",
                },
                {
                    "node_id": "b4",
                    "operation": "sum",
                    "inputs": ["a2", "a2", "c2_minus_a2"],
                    "expected": 4,
                    "shell": "denominator",
                },
                {
                    "node_id": "outer_quotient",
                    "operation": "div",
                    "inputs": ["e2", "b4"],
                    "expected": 2,
                },
                {
                    "node_id": "terminal_residual",
                    "operation": "sub",
                    "inputs": ["outer_quotient", "b2"],
                    "expected": 0,
                },
            ],
            "shells": {
                "numerator": {
                    "root": "e2",
                    "must_close_before": "outer_quotient",
                },
                "denominator": {
                    "root": "b4",
                    "must_close_before": "outer_quotient",
                },
            },
            "fibonacci_stage": fibonacci_stage,
            "golden_limit": {
                "symbol": "PHI",
                "polynomial": [1, -1, -1],
                "root": "positive",
            },
            "inverse_diagonal_scale": {
                "symbol": "ETA",
                "polynomial": [2, 0, -1],
                "root": "positive",
            },
            "delta369": {
                "active_indexing": "zero_indexed",
                "zero_indexed_partition": [[0, 3, 6], [1, 4, 7], [2, 5, 8]],
                "one_indexed_partition": [[3, 6, 9], [1, 4, 7], [2, 5, 8]],
            },
            "nonary_qudit": {
                "shape": [3, 3],
                "lo_shu_traversal_zero_indexed": [3, 8, 1, 2, 4, 6, 7, 0, 5],
                "lo_shu_traversal_one_indexed": [4, 9, 2, 3, 5, 7, 8, 1, 6],
            },
            "projection_policy": {
                "hash72": "INHERITED-HHS-HASH72-V1",
                "hash216": "INHERITED-HHS-HASH216-V1",
                "decimal": "EXTERNAL_DISPLAY_ONLY",
            },
            "shader_target": "GLSL_450",
            "numeric_authority": "EXACT_INTEGER_RATIONAL_SYMBOLIC_IRRATIONAL",
        }
    )


def validate_spec(spec: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "contract_id",
        "pass_number",
        "symbols",
        "dependencies",
        "shells",
        "delta369",
        "nonary_qudit",
    }
    missing = sorted(required - set(spec))
    if missing:
        raise GFCCError(
            "HHS_GFCC_INVALID_SPEC",
            "schema",
            "validate_spec",
            "missing required fields",
            {"missing": missing},
        )
    if spec["contract_id"] != CONTRACT_ID or str(spec["pass_number"]) != PASS_NUMBER:
        raise GFCCError(
            "HHS_GFCC_INVALID_SPEC",
            "schema",
            "validate_spec",
            "contract identity mismatch",
        )
    values = {
        name: int(item["value"]) for name, item in spec["symbols"].items()
    }
    canonical_values = {"a2": 1, "b2": 2, "c2": 3, "d2": 5, "e2": 8}
    if values != canonical_values:
        raise GFCCError(
            "HHS_GFCC_INVALID_SYMBOL",
            "symbols",
            "validate_spec",
            "canonical square-state values altered",
            values,
        )
    if spec.get("numeric_authority") != "EXACT_INTEGER_RATIONAL_SYMBOLIC_IRRATIONAL":
        raise GFCCError(
            "HHS_GFCC_FLOAT_AUTHORITY_VIOLATION",
            "exact",
            "validate_spec",
            "canonical numeric authority changed",
        )
    zero_partition = spec["delta369"]["zero_indexed_partition"]
    one_partition = spec["delta369"]["one_indexed_partition"]
    if zero_partition != [[0, 3, 6], [1, 4, 7], [2, 5, 8]]:
        raise GFCCError(
            "HHS_GFCC_DELTA_COLLAPSE",
            "delta369",
            "validate_spec",
            "zero-indexed phase partition altered",
        )
    if one_partition != [[3, 6, 9], [1, 4, 7], [2, 5, 8]]:
        raise GFCCError(
            "HHS_GFCC_NONARY_INDEX_ERROR",
            "delta369",
            "validate_spec",
            "one-indexed phase partition altered",
        )
    traversal = spec["nonary_qudit"]["lo_shu_traversal_zero_indexed"]
    if traversal != [3, 8, 1, 2, 4, 6, 7, 0, 5] or set(traversal) != set(range(9)):
        raise GFCCError(
            "HHS_GFCC_NONARY_INDEX_ERROR",
            "nonary",
            "validate_spec",
            "Lo Shu traversal altered or non-bijective",
        )
    return {
        "valid": True,
        "source_digest": digest256(spec),
        "source_hash72": inherited_hash72(canonical_bytes(spec)),
        "classification": "IMPLEMENTED_AND_EXECUTION_VERIFIED",
    }


def _apply(operation: str, values: Sequence[ExactRational]) -> ExactRational:
    if operation in {"add", "sum"}:
        result = ExactRational(0)
        for value in values:
            result = result + value
        return result
    if operation == "sub" and len(values) == 2:
        return values[0] - values[1]
    if operation == "div" and len(values) == 2:
        return values[0] / values[1]
    raise GFCCError(
        "HHS_GFCC_INVALID_DEPENDENCY",
        "dependencies",
        "evaluate",
        "unsupported operation",
        {"operation": operation},
    )


def build_dependency_graph(spec: Mapping[str, Any]) -> dict[str, Any]:
    validate_spec(spec)
    nodes = [
        DependencyNode(
            node_id=str(item["node_id"]),
            operation=str(item["operation"]),
            inputs=tuple(str(value) for value in item["inputs"]),
            expected=ExactRational(int(item["expected"])),
            shell=item.get("shell"),
        )
        for item in spec["dependencies"]
    ]
    identities = [node.node_id for node in nodes]
    if len(identities) != len(set(identities)):
        raise GFCCError(
            "HHS_GFCC_INVALID_DEPENDENCY",
            "dependencies",
            "build",
            "duplicate node identity",
        )
    graph = {
        "nodes": [asdict(node) for node in nodes],
        "evaluation_order": identities,
        "shells": spec["shells"],
        "source_digest": digest256(spec),
    }
    graph["graph_digest"] = digest256(graph["nodes"])
    graph["graph_hash72"] = inherited_hash72(canonical_bytes(graph["nodes"]))
    return stable(graph)


def evaluate_dependency_graph(
    spec: Mapping[str, Any], graph: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    graph = graph or build_dependency_graph(spec)
    values: dict[str, ExactRational] = {
        name: ExactRational(int(item["value"]))
        for name, item in spec["symbols"].items()
    }
    ancestry: dict[str, list[str]] = {name: [] for name in values}
    closed_shells: set[str] = set()
    trace: list[dict[str, Any]] = []
    pending = [dict(node) for node in graph["nodes"]]
    while pending:
        progress = False
        for node in list(pending):
            if not all(input_id in values for input_id in node["inputs"]):
                continue
            if node["node_id"] == "outer_quotient" and not {
                "numerator",
                "denominator",
            } <= closed_shells:
                raise GFCCError(
                    "HHS_GFCC_PROJECTION_BEFORE_CLOSURE",
                    "dependencies",
                    "evaluate",
                    "outer projection attempted before shell closure",
                )
            result = _apply(
                node["operation"], [values[input_id] for input_id in node["inputs"]]
            )
            expected = ExactRational(
                int(node["expected"]["numerator"]),
                int(node["expected"]["denominator"]),
            )
            if result != expected:
                raise GFCCError(
                    "HHS_GFCC_INVALID_DEPENDENCY",
                    "dependencies",
                    "evaluate",
                    "dependency value mismatch",
                    {
                        "node": node["node_id"],
                        "observed": result.to_dict(),
                        "expected": expected.to_dict(),
                    },
                )
            values[node["node_id"]] = result
            ancestry[node["node_id"]] = list(node["inputs"])
            if node.get("shell"):
                shell_root = spec["shells"][node["shell"]]["root"]
                if node["node_id"] == shell_root:
                    closed_shells.add(node["shell"])
            trace.append(
                {
                    "node": node["node_id"],
                    "operation": node["operation"],
                    "inputs": node["inputs"],
                    "result": result.to_dict(),
                    "closed_shells": sorted(closed_shells),
                }
            )
            pending.remove(node)
            progress = True
        if not progress:
            raise GFCCError(
                "HHS_GFCC_DEPENDENCY_CYCLE",
                "dependencies",
                "evaluate",
                "unresolvable dependency cycle",
                {"pending": [node["node_id"] for node in pending]},
            )
    if closed_shells != {"numerator", "denominator"}:
        raise GFCCError(
            "HHS_GFCC_SHELL_UNRESOLVED",
            "dependencies",
            "evaluate",
            "required shell did not close",
            {"closed": sorted(closed_shells)},
        )
    if values["terminal_residual"] != ExactRational(0):
        raise GFCCError(
            "HHS_GFCC_EXACTNESS_VIOLATION",
            "dependencies",
            "evaluate",
            "terminal residual is nonzero",
        )
    result = {
        "values": {key: value.to_dict() for key, value in values.items()},
        "ancestry": ancestry,
        "closed_shells": sorted(closed_shells),
        "trace": trace,
        "terminal_residual": values["terminal_residual"].to_dict(),
    }
    result["closure_digest"] = digest256(trace)
    result["closure_hash72"] = inherited_hash72(canonical_bytes(trace))
    return stable(result)


def fibonacci_ratio(stage: int) -> ExactRational:
    if stage < 2 or stage > 92:
        raise GFCCError(
            "HHS_GFCC_RESOURCE_BOUNDED",
            "exact",
            "fibonacci_ratio",
            "stage outside supported exact int64 range",
            {"stage": stage},
        )
    a, b = 1, 1
    for _ in range(2, stage + 1):
        a, b = b, a + b
    return ExactRational(b, a)


def build_delta369(spec: Mapping[str, Any]) -> dict[str, Any]:
    validate_spec(spec)
    raw = spec["delta369"]
    delta = Delta369(
        ring_modulus=9,
        zero_indexed_partition=tuple(
            tuple(int(value) for value in lane)
            for lane in raw["zero_indexed_partition"]
        ),
        one_indexed_partition=tuple(
            tuple(int(value) for value in lane)
            for lane in raw["one_indexed_partition"]
        ),
        active_indexing=str(raw["active_indexing"]),
        matrix_shape=(3, 3),
        decimal_projection="EXTERNAL_DECIMAL_GLYPH_PROJECTION",
        geometry_coordinates=("x", "y", "phase", "scale_depth"),
        golden_correspondence="EXACT_STAGE_RATIO_PLUS_SYMBOLIC_PHI_LIMIT",
        phase_structure="ORDERED_THREE_LANE_PARTITION",
    )
    flattened = {
        value for lane in delta.zero_indexed_partition for value in lane
    }
    if delta.ring_modulus == 1 or flattened != set(range(9)):
        raise GFCCError(
            "HHS_GFCC_DELTA_COLLAPSE",
            "delta369",
            "build",
            "delta collapsed or lost residue identity",
        )
    body = asdict(delta)
    body["coordinate_dimensions"] = len(delta.geometry_coordinates)
    body["delta_digest"] = digest256(body)
    body["delta_hash72"] = inherited_hash72(canonical_bytes(body))
    return stable(body)


def build_qudit9(delta: Mapping[str, Any]) -> dict[str, Any]:
    traversal = [3, 8, 1, 2, 4, 6, 7, 0, 5]
    cells = []
    for index in range(9):
        row, column = divmod(index, 3)
        classes = ["row", "column"]
        if row == column or row + column == 2:
            classes.append("diagonal")
        else:
            classes.append("off_diagonal")
        cells.append(
            {
                "cell_index": index,
                "symbol": f"q{index}",
                "value": index,
                "phase": index % 3,
                "orientation": (row * 3 + column) % 4,
                "scale_depth": 0,
                "dependency_reference": "delta369",
                "constraint_class": classes,
                "coordinates": {
                    "x": column,
                    "y": row,
                    "phase": index % 3,
                    "scale_depth": 0,
                },
            }
        )
    result = {
        "shape": [3, 3],
        "cells": cells,
        "rows": [[3 * row + column for column in range(3)] for row in range(3)],
        "columns": [[3 * row + column for row in range(3)] for column in range(3)],
        "diagonals": [[0, 4, 8], [2, 4, 6]],
        "traversal_zero_indexed": traversal,
        "traversal_one_indexed": [value + 1 for value in traversal],
        "delta_digest": delta["delta_digest"],
    }
    result["qudit_digest"] = digest256(cells)
    result["qudit_hash72"] = inherited_hash72(canonical_bytes(cells))
    return stable(result)


def vm81_index(row: int, column: int) -> int:
    if not 0 <= row < 9 or not 0 <= column < 9:
        raise GFCCError(
            "HHS_GFCC_VM81_MAP_ERROR",
            "vm81",
            "index",
            "row or column outside Z9",
            {"row": row, "column": column},
        )
    return 9 * row + column


def vm81_inverse(index: int) -> tuple[int, int]:
    if not 0 <= index < 81:
        raise GFCCError(
            "HHS_GFCC_VM81_MAP_ERROR",
            "vm81",
            "inverse",
            "index outside 0..80",
            {"index": index},
        )
    return divmod(index, 9)


def _serialize_vm81_cells(cells: Sequence[Mapping[str, Any]]) -> bytes:
    buffer = bytearray()
    for cell in cells:
        buffer.extend(_u32(int(cell["cell_index"])))
        buffer.extend(
            bytes(
                [
                    int(cell["row"]),
                    int(cell["column"]),
                    int(cell["nonary_residue"]),
                    int(cell["phase_lane"]),
                ]
            )
        )
        buffer.extend(_u32(int(cell["scale_depth"])))
        buffer.extend(_i64(int(cell["exact_state"]["numerator"])))
        buffer.extend(_i64(int(cell["exact_state"]["denominator"])))
    return bytes(buffer)


def build_vm81(
    qudit: Mapping[str, Any],
    delta: Mapping[str, Any],
    stage_ratio: ExactRational,
) -> dict[str, Any]:
    cells = []
    for row in range(9):
        for column in range(9):
            index = vm81_index(row, column)
            if vm81_inverse(index) != (row, column):
                raise GFCCError(
                    "HHS_GFCC_VM81_MAP_ERROR",
                    "vm81",
                    "construct",
                    "forward/inverse mismatch",
                )
            residue = (row + column) % 9
            cells.append(
                {
                    "cell_index": index,
                    "row": row,
                    "column": column,
                    "nonary_residue": residue,
                    "phase_lane": residue % 3,
                    "scale_depth": row,
                    "parent_cell": 0xFFFFFFFF
                    if row == 0
                    else vm81_index(row - 1, column),
                    "child_mask": 0 if row == 8 else 1 << (column % 9),
                    "symbol": f"q{residue}",
                    "exact_state": stage_ratio.to_dict(),
                    "dependency": "golden_stage_ratio",
                    "constraints": ["nonary", "phase", "scale", "ancestry"],
                    "hash72_projection": None,
                    "hash216_index": None,
                }
            )
    serialized = _serialize_vm81_cells(cells)
    result = {
        "cell_count": 81,
        "mapping": "i=9r+c",
        "inverse_mapping": "(r,c)=divmod(i,9)",
        "cells": cells,
        "qudit_digest": qudit["qudit_digest"],
        "delta_digest": delta["delta_digest"],
        "stage_ratio": stage_ratio.to_dict(),
        "canonical_serialization_size": len(serialized),
        "canonical_serialization_sha256": sha256(serialized).hexdigest(),
        "state_hash72": inherited_hash72(serialized),
        "state_hash216": inherited_hash216(serialized),
    }
    result["vm81_digest"] = digest256(cells)
    return stable(result)


def _parameter_serialization(
    stage_ratio: ExactRational, delta: Mapping[str, Any]
) -> bytes:
    values = [1, 2, 3, 5, 8, 8, 4, 0, stage_ratio.numerator, stage_ratio.denominator]
    buffer = bytearray()
    buffer.extend(_u32(1))
    buffer.extend(_u32(INTERPRETATION_VERSION))
    for value in values:
        buffer.extend(_i64(value))
    for lane in delta["zero_indexed_partition"]:
        buffer.extend(bytes(int(value) for value in lane))
    if len(buffer) != 97:
        raise GFCCError(
            "HHS_GFCC_INTERNAL_ERROR",
            "parameters",
            "serialize",
            "canonical parameter serialization size mismatch",
            {"observed": len(buffer), "expected": 97},
            authority_level="A1",
        )
    return bytes(buffer)


def parameter_identity(
    stage_ratio: ExactRational, delta: Mapping[str, Any]
) -> dict[str, Any]:
    serialized = _parameter_serialization(stage_ratio, delta)
    return {
        "canonical_serialization_size": len(serialized),
        "canonical_serialization_sha256": sha256(serialized).hexdigest(),
        "source_hash72": inherited_hash72(serialized),
        "parameter_hash216": inherited_hash216(serialized),
    }


def project_hash72(
    vm81: Mapping[str, Any],
    shell: Mapping[str, Any],
    authority_root: str,
) -> dict[str, Any]:
    authority_hash72 = _authority_hash72(authority_root)
    serialized = bytearray()
    serialized.extend(authority_hash72.encode("ascii"))
    serialized.extend(str(vm81["state_hash72"]).encode("ascii"))
    serialized.extend(str(vm81["state_hash216"]).encode("ascii"))
    serialized.extend(_i64(int(vm81["stage_ratio"]["numerator"])))
    serialized.extend(_i64(int(vm81["stage_ratio"]["denominator"])))
    serialized.extend(_i64(int(shell["terminal_residual"]["numerator"])))
    if len(serialized) != 384:
        raise GFCCError(
            "HHS_GFCC_HASH72_ERROR",
            "hash72",
            "serialize",
            "canonical projection payload size mismatch",
            {"observed": len(serialized), "expected": 384},
            authority_level="A1",
        )
    payload = {
        "contract_id": CONTRACT_ID,
        "authority_root_input": authority_root,
        "authority_root_hash72": authority_hash72,
        "vm81_state_hash72": vm81["state_hash72"],
        "vm81_state_hash216": vm81["state_hash216"],
        "vm81_digest": vm81["vm81_digest"],
        "cell_count": vm81["cell_count"],
        "stage_ratio": vm81["stage_ratio"],
        "shell_ancestry": shell["ancestry"],
        "terminal_residual": shell["terminal_residual"],
        "projection_mode": "INHERITED_HHS_HASH72_GFCC_V1",
        "canonical_serialization_size": len(serialized),
        "canonical_serialization_sha256": sha256(serialized).hexdigest(),
    }
    return stable(
        {
            "positions": HASH72_POSITIONS,
            "value": inherited_hash72(serialized),
            "payload": payload,
            "projection_digest": digest256(payload),
        }
    )


def index_hash216(
    vm81: Mapping[str, Any],
    hash72: Mapping[str, Any],
    delta: Mapping[str, Any],
    stage_ratio: ExactRational,
    authority_root: str,
) -> dict[str, Any]:
    authority_hash72 = _authority_hash72(authority_root)
    identity = parameter_identity(stage_ratio, delta)
    serialized = bytearray()
    serialized.extend(authority_hash72.encode("ascii"))
    serialized.extend(str(hash72["value"]).encode("ascii"))
    serialized.extend(str(vm81["state_hash216"]).encode("ascii"))
    serialized.extend(identity["parameter_hash216"].encode("ascii"))
    if len(serialized) != 576:
        raise GFCCError(
            "HHS_GFCC_HASH216_ERROR",
            "hash216",
            "serialize",
            "canonical index payload size mismatch",
            {"observed": len(serialized), "expected": 576},
            authority_level="A1",
        )
    payload = {
        "contract_id": CONTRACT_ID,
        "authority_root_input": authority_root,
        "authority_root_hash72": authority_hash72,
        "vm81_digest": vm81["vm81_digest"],
        "vm81_state_hash216": vm81["state_hash216"],
        "hash72": hash72["value"],
        "delta_digest": delta["delta_digest"],
        "stage_ratio": stage_ratio.to_dict(),
        "parameter_hash216": identity["parameter_hash216"],
        "mapping_version": 1,
        "canonical_serialization_size": len(serialized),
        "canonical_serialization_sha256": sha256(serialized).hexdigest(),
    }
    return stable(
        {
            "positions": HASH216_POSITIONS,
            "value": inherited_hash216(serialized),
            "payload": payload,
            "index_digest": digest256(payload),
        }
    )


def _float_projection(value: Decimal) -> dict[str, Any]:
    as_float = float(value)
    return {
        "decimal": format(value, ".17g"),
        "float32_bits": struct.pack(">f", as_float).hex(),
        "rounding": "IEEE754_ROUND_TO_NEAREST_TIES_TO_EVEN",
    }


def shader_projection(stage_ratio: ExactRational) -> dict[str, Any]:
    getcontext().prec = 80
    phi = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)
    eta = Decimal(2).sqrt() / Decimal(2)
    ratio = Decimal(stage_ratio.numerator) / Decimal(stage_ratio.denominator)
    return stable(
        {
            "phi": {
                "exact_source": "Root_+(x^2-x-1)",
                **_float_projection(phi),
            },
            "inverse_sqrt2": {
                "exact_source": "positive eta satisfying 2*eta^2=1",
                **_float_projection(eta),
            },
            "stage_ratio": {
                "exact_source": stage_ratio.to_dict(),
                **_float_projection(ratio),
            },
            "target": "GLSL_450",
            "canonical_authority": False,
        }
    )


def generate_shader_source(stage_ratio: ExactRational) -> str:
    projection = shader_projection(stage_ratio)
    return "\n".join(
        [
            "#version 450",
            "// Generated by HHS-P152-GFCC; projected rendering only; no canonical authority.",
            f"// phi exact source: {projection['phi']['exact_source']}",
            f"// eta exact source: {projection['inverse_sqrt2']['exact_source']}",
            f"// stage ratio exact source: {stage_ratio.numerator}/{stage_ratio.denominator}",
            "layout(location = 0) out vec4 outColor;",
            f"const float HHS_GFCC_PHI = {projection['phi']['decimal']};",
            f"const float HHS_GFCC_ETA = {projection['inverse_sqrt2']['decimal']};",
            f"const float HHS_GFCC_STAGE_RATIO = {projection['stage_ratio']['decimal']};",
            "void main() {",
            "  vec2 p = gl_FragCoord.xy * HHS_GFCC_ETA;",
            "  float phase = fract((p.x + p.y) / 9.0);",
            "  float shell = fract(length(p) / max(HHS_GFCC_STAGE_RATIO, 0.0001));",
            "  outColor = vec4(phase, shell, fract(phase * HHS_GFCC_PHI), 1.0);",
            "}",
            "",
        ]
    )


def _valid_collision_identity(value: CollisionObject) -> bool:
    return (
        0 <= value.phase < 72
        and 0 <= value.vm81_cell < 81
        and value.scale.denominator > 0
        and value.half_width_q16 >= 0
        and value.half_height_q16 >= 0
        and len(value.hash72) == 72
        and len(value.hash216) == 216
        and all(symbol in HASH72_ALPHABET for symbol in value.hash72 + value.hash216)
    )


def build_collision_constraint(
    a: CollisionObject, b: CollisionObject
) -> dict[str, Any]:
    if not _valid_collision_identity(a) or not _valid_collision_identity(b):
        raise GFCCError(
            "HHS_GFCC_COLLISION_CONSTRAINT_ERROR",
            "collision",
            "build",
            "invalid canonical collision identity",
            authority_level="A1",
        )
    dx = b.x_q16 - a.x_q16
    dy = b.y_q16 - a.y_q16
    overlap_x = a.half_width_q16 + b.half_width_q16 - abs(dx)
    overlap_y = a.half_height_q16 + b.half_height_q16 - abs(dy)
    collision = overlap_x > 0 and overlap_y > 0
    phase_admissible = (a.phase - b.phase) % 3 == 0
    scale_admissible = a.scale == b.scale
    if not collision:
        outcome = "NO_COLLISION"
    elif not phase_admissible:
        outcome = "PHASE_CONFLICT"
    elif not scale_admissible:
        outcome = "SCALE_CONFLICT"
    else:
        outcome = "CONTACT_CONSTRAINED"
    correction = {"x_q16": 0, "y_q16": 0}
    if collision and outcome == "CONTACT_CONSTRAINED":
        if overlap_x <= overlap_y:
            correction["x_q16"] = overlap_x if dx >= 0 else -overlap_x
        else:
            correction["y_q16"] = overlap_y if dy >= 0 else -overlap_y
    result = {
        "object_a": a.object_id,
        "object_b": b.object_id,
        "outcome": outcome,
        "signed_separation": {
            "x_q16": abs(dx) - a.half_width_q16 - b.half_width_q16,
            "y_q16": abs(dy) - a.half_height_q16 - b.half_height_q16,
        },
        "penetration": {
            "x_q16": max(0, overlap_x),
            "y_q16": max(0, overlap_y),
        },
        "correction": correction,
        "phase_admissible": phase_admissible,
        "scale_admissible": scale_admissible,
        "vm81_continuity": True,
        "hash72_inputs": [a.hash72, b.hash72],
        "hash216_inputs": [a.hash216, b.hash216],
    }
    result["constraint_hash72"] = inherited_hash72(canonical_bytes(result))
    return stable(result)


def enforce_collision(
    a: CollisionObject,
    b: CollisionObject,
    constraint: Mapping[str, Any],
) -> dict[str, Any]:
    if constraint["outcome"] == "NO_COLLISION":
        return stable(
            {
                "outcome": "NO_COLLISION",
                "object_b": asdict(b),
                "invariants_preserved": True,
            }
        )
    if constraint["outcome"] != "CONTACT_CONSTRAINED":
        return stable(
            {
                "outcome": constraint["outcome"],
                "object_b": asdict(b),
                "invariants_preserved": True,
            }
        )
    correction = constraint["correction"]
    updated = CollisionObject(
        object_id=b.object_id,
        x_q16=b.x_q16 + int(correction["x_q16"]),
        y_q16=b.y_q16 + int(correction["y_q16"]),
        half_width_q16=b.half_width_q16,
        half_height_q16=b.half_height_q16,
        scale=b.scale,
        phase=b.phase,
        vm81_cell=b.vm81_cell,
        hash72=b.hash72,
        hash216=b.hash216,
    )
    preserved = (
        updated.scale == b.scale
        and updated.phase == b.phase
        and updated.vm81_cell == b.vm81_cell
        and updated.hash72 == b.hash72
        and updated.hash216 == b.hash216
    )
    if not preserved:
        raise GFCCError(
            "HHS_GFCC_COLLISION_INVARIANT_ERROR",
            "collision",
            "enforce",
            "protected identity changed",
            authority_level="A1",
        )
    result = {
        "outcome": "CORRECTION_APPLIED",
        "object_b": asdict(updated),
        "correction": correction,
        "invariants_preserved": True,
    }
    result["enforcement_hash72"] = inherited_hash72(canonical_bytes(result))
    return stable(result)


def make_receipt(
    operation_id: str,
    sequence: int,
    predecessor: str,
    inputs: Any,
    outputs: Any,
    classification: str = "IMPLEMENTED_AND_EXECUTION_VERIFIED",
) -> dict[str, Any]:
    body = {
        "contract_id": CONTRACT_ID,
        "pass_number": PASS_NUMBER,
        "operation_id": operation_id,
        "deterministic_sequence": sequence,
        "authority_level": "A1",
        "input_digest": digest256(inputs),
        "output_digest": digest256(outputs),
        "predecessor_receipt_digest": predecessor,
        "result_classification": classification,
        "error_classification": None,
        "implementation_version": IMPLEMENTATION_VERSION,
        "interpretation_version": INTERPRETATION_VERSION,
        "build_identity": None,
        "replay_identity": None,
    }
    body["hash72_witness"] = inherited_hash72(canonical_bytes(body))
    body["receipt_digest"] = digest256(body)
    return stable(body)


def run_representative_workload(
    authority_root: str = "HHS_PASS_152_AUTHORITY_ROOT",
) -> dict[str, Any]:
    spec = canonical_spec()
    validation = validate_spec(spec)
    graph = build_dependency_graph(spec)
    shell = evaluate_dependency_graph(spec, graph)
    ratio = fibonacci_ratio(int(spec["fibonacci_stage"]))
    delta = build_delta369(spec)
    qudit = build_qudit9(delta)
    vm81 = build_vm81(qudit, delta, ratio)
    parameters = parameter_identity(ratio, delta)
    hash72 = project_hash72(vm81, shell, authority_root)
    hash216 = index_hash216(vm81, hash72, delta, ratio, authority_root)
    shader = {
        "source": generate_shader_source(ratio),
        "projection": shader_projection(ratio),
    }
    a = CollisionObject(
        "A",
        0,
        0,
        65536,
        65536,
        ratio,
        6,
        40,
        hash72["value"],
        hash216["value"],
    )
    b = CollisionObject(
        "B",
        98304,
        0,
        65536,
        65536,
        ratio,
        9,
        41,
        hash72["value"],
        hash216["value"],
    )
    collision = build_collision_constraint(a, b)
    enforcement = enforce_collision(a, b, collision)
    operations = [
        ("GFCC_SOURCE_SPEC", spec, validation),
        ("GFCC_DEPENDENCY_GRAPH", spec, graph),
        ("GFCC_SHELL_CLOSURE", graph, shell),
        ("GFCC_DELTA369", spec["delta369"], delta),
        ("GFCC_NONARY_QUDIT", delta, qudit),
        ("GFCC_VM81_CONSTRUCTION", qudit, vm81),
        ("GFCC_HASH72_PROJECTION", vm81, hash72),
        ("GFCC_HASH216_INDEX", hash72, hash216),
        ("GFCC_SHADER_CODEGEN", ratio.to_dict(), shader),
        ("GFCC_COLLISION_CONSTRUCTION", [asdict(a), asdict(b)], collision),
        ("GFCC_COLLISION_ENFORCEMENT", collision, enforcement),
    ]
    receipts: list[dict[str, Any]] = []
    predecessor = "0" * 64
    for sequence, (operation, inputs, outputs) in enumerate(operations, start=1):
        receipt = make_receipt(operation, sequence, predecessor, inputs, outputs)
        receipts.append(receipt)
        predecessor = receipt["receipt_digest"]
    canonical_result = stable(
        {
            "spec": spec,
            "graph": graph,
            "shell": shell,
            "stage_ratio": ratio.to_dict(),
            "parameter_identity": parameters,
            "delta369": delta,
            "qudit9": qudit,
            "vm81": vm81,
            "hash72": hash72,
            "hash216": hash216,
            "shader": shader,
            "collision": collision,
            "enforcement": enforcement,
            "receipts": receipts,
            "authority_root": authority_root,
            "authority_root_hash72": _authority_hash72(authority_root),
        }
    )
    return stable(
        {
            **canonical_result,
            "canonical_result_digest": digest256(canonical_result),
            "canonical_result_hash72": inherited_hash72(
                canonical_bytes(canonical_result)
            ),
        }
    )


def replay_workload(original: Mapping[str, Any]) -> dict[str, Any]:
    replayed = run_representative_workload(str(original["authority_root"]))
    match = (
        replayed["canonical_result_digest"]
        == original["canonical_result_digest"]
        and replayed["canonical_result_hash72"]
        == original["canonical_result_hash72"]
    )
    return stable(
        {
            "match": match,
            "expected_digest": original["canonical_result_digest"],
            "observed_digest": replayed["canonical_result_digest"],
            "expected_hash72": original["canonical_result_hash72"],
            "observed_hash72": replayed["canonical_result_hash72"],
            "classification": "IMPLEMENTED_AND_EXECUTION_VERIFIED"
            if match
            else "REPLAY_MISMATCH",
        }
    )


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(stable(value), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, values: Iterable[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(
                stable(value),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            + "\n"
            for value in values
        ),
        encoding="utf-8",
    )
