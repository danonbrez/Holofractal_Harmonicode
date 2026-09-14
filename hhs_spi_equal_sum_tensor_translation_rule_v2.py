"""Pass 219 SPI — equal-sum tensor translation normalization rule v2.

Additive successor to v1.  v2 retains the generic same-shape/equal-sum rule and
adds full 9x9 Sudoku tensor witnesses: all 9 rows, 9 columns, and 9 3x3 banks
must close to the same exact sum 45 before translation at the a²=1 layer.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, Sequence, Tuple

from hhs_spi_equal_sum_tensor_translation_rule_v1 import (
    PROFILE as V1_PROFILE,
    SPIEqualSumTensorTranslationError,
    equal_sum_translation_witness,
    lo_shu_translation_witness,
)

FORMAT = "HHS_SPI_EQUAL_SUM_TENSOR_TRANSLATION_RULE_V2"
VERSION = "2.0.0"
PROFILE = "EQUAL-SUM-SAME-SHAPE-TENSOR-A2-NORMALIZATION-v2"
SUDOKU_GROUP_SUM = 45

SUDOKU_GRID_A = (
    (1, 2, 3, 4, 5, 6, 7, 8, 9),
    (4, 5, 6, 7, 8, 9, 1, 2, 3),
    (7, 8, 9, 1, 2, 3, 4, 5, 6),
    (2, 3, 4, 5, 6, 7, 8, 9, 1),
    (5, 6, 7, 8, 9, 1, 2, 3, 4),
    (8, 9, 1, 2, 3, 4, 5, 6, 7),
    (3, 4, 5, 6, 7, 8, 9, 1, 2),
    (6, 7, 8, 9, 1, 2, 3, 4, 5),
    (9, 1, 2, 3, 4, 5, 6, 7, 8),
)

SUDOKU_GRID_B = (
    (9, 8, 7, 6, 5, 4, 3, 2, 1),
    (6, 5, 4, 3, 2, 1, 9, 8, 7),
    (3, 2, 1, 9, 8, 7, 6, 5, 4),
    (8, 7, 6, 5, 4, 3, 2, 1, 9),
    (5, 4, 3, 2, 1, 9, 8, 7, 6),
    (2, 1, 9, 8, 7, 6, 5, 4, 3),
    (7, 6, 5, 4, 3, 2, 1, 9, 8),
    (4, 3, 2, 1, 9, 8, 7, 6, 5),
    (1, 9, 8, 7, 6, 5, 4, 3, 2),
)


def _q(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise SPIEqualSumTensorTranslationError("exact Sudoku normalization forbids bool/float arithmetic")
    return Fraction(value)


def _sum_exact(values: Sequence[Any]) -> Fraction:
    total = Fraction(0)
    for value in values:
        total += _q(value)
    return total


def sudoku_equation_sums(grid: Sequence[Sequence[Any]]) -> Tuple[Fraction, ...]:
    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        raise SPIEqualSumTensorTranslationError("Sudoku tensor must be exactly 9x9")
    rows = tuple(_sum_exact(row) for row in grid)
    columns = tuple(_sum_exact(tuple(grid[r][c] for r in range(9))) for c in range(9))
    banks = []
    for br in range(3):
        for bc in range(3):
            values = []
            for r in range(br * 3, br * 3 + 3):
                for c in range(bc * 3, bc * 3 + 3):
                    values.append(grid[r][c])
            banks.append(_sum_exact(tuple(values)))
    return rows + columns + tuple(banks)


def full_sudoku_translation_witness() -> Dict[str, Any]:
    source_sums = sudoku_equation_sums(SUDOKU_GRID_A)
    target_sums = sudoku_equation_sums(SUDOKU_GRID_B)
    witness = equal_sum_translation_witness(
        source_id="SUDOKU_GRID_A",
        target_id="SUDOKU_GRID_B",
        source_tensor=SUDOKU_GRID_A,
        target_tensor=SUDOKU_GRID_B,
        invariant_sum=SUDOKU_GROUP_SUM,
        source_sum_equations=source_sums,
        target_sum_equations=target_sums,
        symmetry_family="SUDOKU_9X9_ROWS_COLUMNS_BANKS",
        layer_id="A2_SUDOKU_9X9_NORMALIZATION",
    )
    witness["successor_profile"] = PROFILE
    witness["predecessor_profile"] = V1_PROFILE
    witness["row_equation_count"] = 9
    witness["column_equation_count"] = 9
    witness["bank_equation_count"] = 9
    witness["complete_sudoku_equation_count"] = 27
    return witness
