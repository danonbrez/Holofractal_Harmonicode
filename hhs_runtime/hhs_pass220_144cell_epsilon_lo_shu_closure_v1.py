"""Pass 220 I021 exact 144-cell epsilon/Lo Shu phase closure."""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Sequence

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    HASH72_BASE,
    SCALAR_RADIX,
    VM81_CELLS,
)

SCHEMA = "HHS_PASS_220_I021_144CELL_EPSILON_LO_SHU_CLOSURE_V1"
PROFILE = "PASS220-I021-144CELL-EPSILON-LO-SHU-CLOSURE-v1"
ZERO_CENTERED_LO_SHU = ((-1, 4, -3), (-2, 0, 2), (3, -4, 1))
TRINARY = (-1, 0, 1)
HARMONIC_SIDE = 12
LOCAL_SIDE = 3
BLOCKS_PER_AXIS = 4
HARMONIC_BLOCKS = 16
HARMONIC_CELLS = 144
HARMONIC_ORBIT = HASH72_BASE
VM5184 = SCALAR_RADIX
FRACTAL_ORBIT = HARMONIC_CELLS * HARMONIC_ORBIT
DEVELOPMENT_EQUATION = "2m²/m(2*f^P(MOD144))-Factorial(f)+e==(t³-t)-(m²-m)-mM"
ROOT_IDENTITY = "f¹⁴⁴=(2^(1/72))u⁷²"
LOCAL_PHASE_TUPLE = "(-e,-e+e,+e)=(-e,0,+e)"


class Pass220I021ClosureError(ValueError):
    pass


def _q(value: Any, name: str = "value") -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise Pass220I021ClosureError(f"{name} must be int or Fraction")
    return Fraction(value)


def _i(value: Any, name: str = "value") -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I021ClosureError(f"{name} must be an exact integer")
    return value


def _text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {**payload, "receipt_sha256": sha256(encoded.encode("utf-8")).hexdigest()}


def sgn3(value: int | Fraction) -> int:
    q = _q(value)
    return -1 if q < 0 else (1 if q > 0 else 0)


def epsilon_phase_triplet(epsilon: int | Fraction) -> tuple[Fraction, Fraction, Fraction]:
    e = _q(epsilon, "epsilon")
    return (-e, -e + e, e)


def zero_centered_lo_shu_line_sums(matrix=ZERO_CENTERED_LO_SHU):
    rows = tuple(tuple(_q(v, "matrix cell") for v in row) for row in matrix)
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise Pass220I021ClosureError("matrix must be 3x3")
    return {
        "rows": tuple(sum(row, Fraction(0)) for row in rows),
        "columns": tuple(sum((rows[r][c] for r in range(3)), Fraction(0)) for c in range(3)),
        "diagonals": (
            sum((rows[i][i] for i in range(3)), Fraction(0)),
            sum((rows[i][2 - i] for i in range(3)), Fraction(0)),
        ),
    }


def lo_shu_phase_block(epsilon: int | Fraction):
    e = _q(epsilon, "epsilon")
    return tuple(tuple(e * coefficient for coefficient in row) for row in ZERO_CENTERED_LO_SHU)


def tessellate_144_phase_matrix(block_epsilons: Sequence[int | Fraction]):
    values = tuple(block_epsilons)
    if len(values) != HARMONIC_BLOCKS:
        raise Pass220I021ClosureError("exactly sixteen block epsilons are required")
    matrix = [[Fraction(0) for _ in range(HARMONIC_SIDE)] for _ in range(HARMONIC_SIDE)]
    for br in range(BLOCKS_PER_AXIS):
        for bc in range(BLOCKS_PER_AXIS):
            block = lo_shu_phase_block(values[br * BLOCKS_PER_AXIS + bc])
            for r in range(LOCAL_SIDE):
                for c in range(LOCAL_SIDE):
                    matrix[br * LOCAL_SIDE + r][bc * LOCAL_SIDE + c] = block[r][c]
    return tuple(tuple(row) for row in matrix)


def phase_matrix_144_witness(block_epsilons: Sequence[int | Fraction] | None = None):
    eps = tuple(range(1, 17)) if block_epsilons is None else tuple(block_epsilons)
    matrix = tessellate_144_phase_matrix(eps)
    rows = tuple(sum(row, Fraction(0)) for row in matrix)
    cols = tuple(sum((matrix[r][c] for r in range(12)), Fraction(0)) for c in range(12))
    diags = (
        sum((matrix[i][i] for i in range(12)), Fraction(0)),
        sum((matrix[i][11 - i] for i in range(12)), Fraction(0)),
    )
    total = sum(rows, Fraction(0))
    local = []
    for br in range(4):
        for bc in range(4):
            block = tuple(
                tuple(matrix[br * 3 + r][bc * 3 + c] for c in range(3))
                for r in range(3)
            )
            sums = zero_centered_lo_shu_line_sums(block)
            local.append(all(v == 0 for group in sums.values() for v in group))
    closed = all(local) and all(v == 0 for v in rows + cols + diags) and total == 0
    return _receipt({
        "schema": SCHEMA,
        "profile": PROFILE,
        "harmonic_cells": HARMONIC_CELLS,
        "harmonic_blocks": HARMONIC_BLOCKS,
        "row_sums": tuple(_text(v) for v in rows),
        "column_sums": tuple(_text(v) for v in cols),
        "diagonal_sums": tuple(_text(v) for v in diags),
        "total_epsilon": _text(total),
        "all_local_blocks_closed": all(local),
        "closed": closed,
        "projection_only": True,
        "canonical_admission_authority": False,
    })


def p_mod_144(p: int) -> int:
    return _i(p, "P") % HARMONIC_CELLS


def harmonic_root_closure_witness():
    f_exponent = 144 * 72
    u_exponent = 72 * 72
    assert f_exponent == 10368 == 2 * VM5184
    assert u_exponent == VM5184 == 5184
    return _receipt({
        "schema": "HHS_PASS_220_I021_HARMONIC_ROOT_CLOSURE_V1",
        "source_identity": ROOT_IDENTITY,
        "f_exponent": f_exponent,
        "binary_coefficient": 2,
        "u_exponent": u_exponent,
        "resolved_identity": "f^10368=2u^5184",
        "fractional_exponent_approximated": False,
        "projection_only": True,
        "canonical_admission_authority": False,
    })


def full_i021_witness():
    local = epsilon_phase_triplet(Fraction(1))
    phase = phase_matrix_144_witness()
    root = harmonic_root_closure_witness()
    return _receipt({
        "schema": "HHS_PASS_220_I021_FULL_CLOSURE_V1",
        "development_equation": DEVELOPMENT_EQUATION,
        "root_identity": ROOT_IDENTITY,
        "local_phase_tuple": LOCAL_PHASE_TUPLE,
        "local_trinary": tuple(sgn3(v) for v in local),
        "local_epsilon_sum": _text(sum(local, Fraction(0))),
        "harmonic_cells": HARMONIC_CELLS,
        "vm81_cells": VM81_CELLS,
        "vm5184": VM5184,
        "fractal_orbit": FRACTAL_ORBIT,
        "phase_matrix_closed": phase["closed"],
        "root_identity_closed": root["resolved_identity"] == "f^10368=2u^5184",
        "closed": phase["closed"] and sum(local, Fraction(0)) == 0,
        "floating_point_authority": False,
        "projection_only": True,
        "canonical_admission_authority": False,
    })
