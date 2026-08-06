"""Exact integer geometry for Pass 213 Iteration 8 moving tensors."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import hmac
import math
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    FULL_HYDRATION_DOMAIN,
    G243_CONTROLS,
    HYDRATION_LANES,
    ORDERED_OPCODES,
    VM5184_G243_DOMAIN,
    canonical_bytes,
    hash216,
)

ITERATION = 8
LO_SHU_BASE = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
AXIS_MODULI = (9, 9, 4, 4, 4, 3, 3, 3, 3, 3, 40)
SUDOKU_SYMBOLS = frozenset(range(1, 10))


class Pass213TensorGeometryError(RuntimeError):
    pass


def seed_word(seed: bytes, label: str, index: int) -> int:
    encoded = label.encode("utf-8")
    payload = (
        b"HHS-P213-ITER8-SEED-WORD-V1\0"
        + len(encoded).to_bytes(2, "big")
        + encoded
        + int(index).to_bytes(8, "big")
    )
    return int.from_bytes(hmac.new(seed, payload, sha256).digest(), "big")


def permutation(size: int, seed: bytes, label: str) -> tuple[int, ...]:
    values = list(range(size))
    for position in range(size - 1, 0, -1):
        other = seed_word(seed, label, position) % (position + 1)
        values[position], values[other] = values[other], values[position]
    return tuple(values)


def inverse_permutation(values: Sequence[int]) -> tuple[int, ...]:
    result = [0] * len(values)
    for output, source in enumerate(values):
        result[int(source)] = output
    return tuple(result)


def require_permutation(values: Sequence[int], size: int, code: str) -> tuple[int, ...]:
    result = tuple(int(item) for item in values)
    if len(result) != size or set(result) != set(range(size)):
        raise Pass213TensorGeometryError(code)
    return result


def _rotate(grid: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    size = len(grid)
    return tuple(
        tuple(int(grid[size - 1 - column][row]) for column in range(size))
        for row in range(size)
    )


def _reflect(grid: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(reversed(tuple(int(item) for item in row))) for row in grid)


def lo_shu_grid(transform_index: int) -> tuple[tuple[int, ...], ...]:
    if not 0 <= int(transform_index) < 8:
        raise Pass213TensorGeometryError("PASS213_TENSOR_LO_SHU_TRANSFORM_INVALID")
    grid: tuple[tuple[int, ...], ...] = LO_SHU_BASE
    if transform_index >= 4:
        grid = _reflect(grid)
    for _ in range(transform_index % 4):
        grid = _rotate(grid)
    validate_lo_shu(grid)
    return grid


def validate_lo_shu(grid: Sequence[Sequence[int]]) -> None:
    rows = tuple(tuple(int(item) for item in row) for row in grid)
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise Pass213TensorGeometryError("PASS213_TENSOR_LO_SHU_SHAPE_INVALID")
    if set(item for row in rows for item in row) != set(range(1, 10)):
        raise Pass213TensorGeometryError("PASS213_TENSOR_LO_SHU_SYMBOLS_INVALID")
    lines = list(rows)
    lines.extend(tuple(rows[row][column] for row in range(3)) for column in range(3))
    lines.extend(
        (
            tuple(rows[index][index] for index in range(3)),
            tuple(rows[index][2 - index] for index in range(3)),
        )
    )
    if any(sum(line) != 15 for line in lines):
        raise Pass213TensorGeometryError("PASS213_TENSOR_LO_SHU_MAGIC_SUM_INVALID")


def fibonacci_phase(sequence: int) -> tuple[int, ...]:
    if int(sequence) < 1:
        raise Pass213TensorGeometryError("PASS213_TENSOR_SEQUENCE_INVALID")
    a, b = 0, 1
    values: list[int] = []
    for index in range(int(sequence) + len(AXIS_MODULI)):
        if index >= sequence:
            values.append(a % AXIS_MODULI[index - sequence])
        a, b = b, a + b
    return tuple(values)


def _group_order(seed: bytes, label: str) -> tuple[int, ...]:
    groups = permutation(3, seed, f"{label}/groups")
    result: list[int] = []
    for output_group, source_group in enumerate(groups):
        inner = permutation(3, seed, f"{label}/inner/{output_group}")
        result.extend(source_group * 3 + value for value in inner)
    return tuple(result)


def _base_sudoku(row: int, column: int) -> int:
    return ((row * 3 + row // 3 + column) % 9) + 1


@dataclass(frozen=True)
class SudokuTensor:
    row_order: tuple[int, ...]
    column_order: tuple[int, ...]
    digit_permutation: tuple[int, ...]
    transpose: bool
    grid: tuple[tuple[int, ...], ...]
    root_hash216: str

    @classmethod
    def derive(cls, seed: bytes) -> "SudokuTensor":
        rows = _group_order(seed, "sudoku/rows")
        columns = _group_order(seed, "sudoku/columns")
        digits = permutation(9, seed, "sudoku/digits")
        transpose = bool(seed_word(seed, "sudoku/transpose", 0) & 1)
        grid = cls._grid(rows, columns, digits, transpose)
        unsigned = {
            "row_order": rows,
            "column_order": columns,
            "digit_permutation": digits,
            "transpose": transpose,
            "grid": grid,
        }
        tensor = cls(rows, columns, digits, transpose, grid, hash216(
            "sudoku-tensor", canonical_bytes(unsigned)
        ))
        tensor.validate()
        return tensor

    @staticmethod
    def _grid(
        rows: Sequence[int],
        columns: Sequence[int],
        digits: Sequence[int],
        transpose: bool,
    ) -> tuple[tuple[int, ...], ...]:
        rows = require_permutation(rows, 9, "PASS213_TENSOR_SUDOKU_ROWS_INVALID")
        columns = require_permutation(columns, 9, "PASS213_TENSOR_SUDOKU_COLUMNS_INVALID")
        digits = require_permutation(digits, 9, "PASS213_TENSOR_SUDOKU_DIGITS_INVALID")
        output: list[tuple[int, ...]] = []
        for out_row in range(9):
            row: list[int] = []
            for out_column in range(9):
                source_row, source_column = rows[out_row], columns[out_column]
                if transpose:
                    source_row, source_column = source_column, source_row
                row.append(digits[_base_sudoku(source_row, source_column) - 1] + 1)
            output.append(tuple(row))
        return tuple(output)

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "row_order": self.row_order,
            "column_order": self.column_order,
            "digit_permutation": self.digit_permutation,
            "transpose": self.transpose,
            "grid": self.grid,
        }

    def to_mapping(self) -> dict[str, Any]:
        return {**self.unsigned_payload(), "root_hash216": self.root_hash216}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "SudokuTensor":
        tensor = cls(
            tuple(int(item) for item in value["row_order"]),
            tuple(int(item) for item in value["column_order"]),
            tuple(int(item) for item in value["digit_permutation"]),
            bool(value["transpose"]),
            tuple(tuple(int(item) for item in row) for row in value["grid"]),
            str(value["root_hash216"]),
        )
        tensor.validate()
        return tensor

    def validate(self) -> None:
        expected_grid = self._grid(
            self.row_order, self.column_order, self.digit_permutation, self.transpose
        )
        if expected_grid != self.grid:
            raise Pass213TensorGeometryError("PASS213_TENSOR_SUDOKU_DERIVATION_MISMATCH")
        for row in self.grid:
            if set(row) != SUDOKU_SYMBOLS:
                raise Pass213TensorGeometryError("PASS213_TENSOR_SUDOKU_ROW_INVALID")
        for column in range(9):
            if {self.grid[row][column] for row in range(9)} != SUDOKU_SYMBOLS:
                raise Pass213TensorGeometryError("PASS213_TENSOR_SUDOKU_COLUMN_INVALID")
        for band in range(3):
            for stack in range(3):
                region = {
                    self.grid[band * 3 + row][stack * 3 + column]
                    for row in range(3)
                    for column in range(3)
                }
                if region != SUDOKU_SYMBOLS:
                    raise Pass213TensorGeometryError("PASS213_TENSOR_SUDOKU_REGION_INVALID")
        expected = hash216("sudoku-tensor", canonical_bytes(self.unsigned_payload()))
        if not hmac.compare_digest(expected, self.root_hash216):
            raise Pass213TensorGeometryError("PASS213_TENSOR_SUDOKU_ROOT_MISMATCH")


def _coprime(seed: bytes, label: str, modulus: int) -> int:
    value = seed_word(seed, label, 0) % modulus or 1
    while math.gcd(value, modulus) != 1:
        value = (value + 1) % modulus or 1
    return value


@dataclass(frozen=True)
class TensorCoordinateMap:
    row_map: tuple[int, ...]
    column_map: tuple[int, ...]
    operation_axis_order: tuple[int, ...]
    operation_offsets: tuple[int, ...]
    control_axis_order: tuple[int, ...]
    control_offsets: tuple[int, ...]
    lane_multiplier: int
    lane_offset: int
    root_hash216: str

    @classmethod
    def derive(
        cls, seed: bytes, sudoku: SudokuTensor, phase: Sequence[int]
    ) -> "TensorCoordinateMap":
        operation_order = permutation(3, seed, "coordinate/operation-axis")
        control_order = permutation(5, seed, "coordinate/control-axis")
        operation_offsets = tuple(
            (seed_word(seed, "coordinate/operation-offset", index) + phase[2 + index]) % 4
            for index in range(3)
        )
        control_offsets = tuple(
            (seed_word(seed, "coordinate/control-offset", index) + phase[5 + index]) % 3
            for index in range(5)
        )
        unsigned = {
            "row_map": inverse_permutation(sudoku.row_order),
            "column_map": inverse_permutation(sudoku.column_order),
            "operation_axis_order": operation_order,
            "operation_offsets": operation_offsets,
            "control_axis_order": control_order,
            "control_offsets": control_offsets,
            "lane_multiplier": _coprime(seed, "coordinate/lane", HYDRATION_LANES),
            "lane_offset": (
                seed_word(seed, "coordinate/lane-offset", 0) + phase[10]
            ) % HYDRATION_LANES,
        }
        mapping = cls(**unsigned, root_hash216=hash216(
            "moving-tensor-coordinate-map", canonical_bytes(unsigned)
        ))
        mapping.validate()
        return mapping

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "row_map": self.row_map,
            "column_map": self.column_map,
            "operation_axis_order": self.operation_axis_order,
            "operation_offsets": self.operation_offsets,
            "control_axis_order": self.control_axis_order,
            "control_offsets": self.control_offsets,
            "lane_multiplier": self.lane_multiplier,
            "lane_offset": self.lane_offset,
        }

    def to_mapping(self) -> dict[str, Any]:
        return {**self.unsigned_payload(), "root_hash216": self.root_hash216}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "TensorCoordinateMap":
        mapping = cls(
            tuple(int(item) for item in value["row_map"]),
            tuple(int(item) for item in value["column_map"]),
            tuple(int(item) for item in value["operation_axis_order"]),
            tuple(int(item) for item in value["operation_offsets"]),
            tuple(int(item) for item in value["control_axis_order"]),
            tuple(int(item) for item in value["control_offsets"]),
            int(value["lane_multiplier"]),
            int(value["lane_offset"]),
            str(value["root_hash216"]),
        )
        mapping.validate()
        return mapping

    def validate(self) -> None:
        require_permutation(self.row_map, 9, "PASS213_TENSOR_ROW_MAP_INVALID")
        require_permutation(self.column_map, 9, "PASS213_TENSOR_COLUMN_MAP_INVALID")
        require_permutation(self.operation_axis_order, 3, "PASS213_TENSOR_OPERATION_AXIS_INVALID")
        require_permutation(self.control_axis_order, 5, "PASS213_TENSOR_CONTROL_AXIS_INVALID")
        if len(self.operation_offsets) != 3 or any(not 0 <= value < 4 for value in self.operation_offsets):
            raise Pass213TensorGeometryError("PASS213_TENSOR_OPERATION_OFFSET_INVALID")
        if len(self.control_offsets) != 5 or any(not 0 <= value < 3 for value in self.control_offsets):
            raise Pass213TensorGeometryError("PASS213_TENSOR_CONTROL_OFFSET_INVALID")
        if not 0 <= self.lane_offset < HYDRATION_LANES or math.gcd(self.lane_multiplier, HYDRATION_LANES) != 1:
            raise Pass213TensorGeometryError("PASS213_TENSOR_LANE_AFFINE_INVALID")
        expected = hash216("moving-tensor-coordinate-map", canonical_bytes(self.unsigned_payload()))
        if not hmac.compare_digest(expected, self.root_hash216):
            raise Pass213TensorGeometryError("PASS213_TENSOR_COORDINATE_ROOT_MISMATCH")

    @staticmethod
    def decode(index: int, domain_size: int) -> tuple[int, ...]:
        if domain_size not in {VM5184_G243_DOMAIN, FULL_HYDRATION_DOMAIN} or not 0 <= int(index) < domain_size:
            raise Pass213TensorGeometryError("PASS213_TENSOR_COORDINATE_OUT_OF_RANGE")
        lane, remaining = (0, int(index))
        if domain_size == FULL_HYDRATION_DOMAIN:
            lane, remaining = divmod(remaining, VM5184_G243_DOMAIN)
        state, g243 = divmod(remaining, G243_CONTROLS)
        cell, opcode = divmod(state, ORDERED_OPCODES)
        row, column = divmod(cell, 9)
        a, remainder = divmod(opcode, 16)
        b, d = divmod(remainder, 4)
        controls: list[int] = []
        for _ in range(5):
            controls.append(g243 % 3)
            g243 //= 3
        return (row, column, a, b, d, *controls, lane)

    @staticmethod
    def encode(coordinates: Sequence[int], domain_size: int) -> int:
        values = tuple(int(item) for item in coordinates)
        if len(values) != 11:
            raise Pass213TensorGeometryError("PASS213_TENSOR_COORDINATE_ARITY_INVALID")
        row, column, a, b, d, *tail = values
        controls, lane = tail[:5], tail[5]
        if not (0 <= row < 9 and 0 <= column < 9) or any(not 0 <= value < 4 for value in (a, b, d)) or any(not 0 <= value < 3 for value in controls):
            raise Pass213TensorGeometryError("PASS213_TENSOR_COORDINATE_COMPONENT_INVALID")
        if domain_size == VM5184_G243_DOMAIN and lane != 0:
            raise Pass213TensorGeometryError("PASS213_TENSOR_LANE_NOT_IN_DOMAIN")
        if domain_size == FULL_HYDRATION_DOMAIN and not 0 <= lane < HYDRATION_LANES:
            raise Pass213TensorGeometryError("PASS213_TENSOR_LANE_INVALID")
        if domain_size not in {VM5184_G243_DOMAIN, FULL_HYDRATION_DOMAIN}:
            raise Pass213TensorGeometryError("PASS213_TENSOR_DOMAIN_INVALID")
        state = ORDERED_OPCODES * (9 * row + column) + (16 * a + 4 * b + d)
        g243 = sum(value * (3 ** index) for index, value in enumerate(controls))
        base = G243_CONTROLS * state + g243
        return base if domain_size == VM5184_G243_DOMAIN else lane * VM5184_G243_DOMAIN + base

    def map_index(self, index: int, domain_size: int) -> int:
        source = self.decode(index, domain_size)
        operation, controls = source[2:5], source[5:10]
        mapped_operation = tuple(
            (operation[self.operation_axis_order[axis]] + self.operation_offsets[axis]) % 4
            for axis in range(3)
        )
        mapped_controls = tuple(
            (controls[self.control_axis_order[axis]] + self.control_offsets[axis]) % 3
            for axis in range(5)
        )
        lane = source[10]
        if domain_size == FULL_HYDRATION_DOMAIN:
            lane = (self.lane_multiplier * lane + self.lane_offset) % HYDRATION_LANES
        return self.encode((self.row_map[source[0]], self.column_map[source[1]], *mapped_operation, *mapped_controls, lane), domain_size)

    def unmap_index(self, index: int, domain_size: int) -> int:
        mapped = self.decode(index, domain_size)
        operation, controls = [0, 0, 0], [0, 0, 0, 0, 0]
        for output, source in enumerate(self.operation_axis_order):
            operation[source] = (mapped[2 + output] - self.operation_offsets[output]) % 4
        for output, source in enumerate(self.control_axis_order):
            controls[source] = (mapped[5 + output] - self.control_offsets[output]) % 3
        lane = mapped[10]
        if domain_size == FULL_HYDRATION_DOMAIN:
            lane = pow(self.lane_multiplier, -1, HYDRATION_LANES) * (lane - self.lane_offset) % HYDRATION_LANES
        return self.encode((inverse_permutation(self.row_map)[mapped[0]], inverse_permutation(self.column_map)[mapped[1]], *operation, *controls, lane), domain_size)
