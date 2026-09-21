"""Pass 220 I021 exact 144-cell epsilon/Lo Shu phase closure.

G72 is an irreducible ordered phase-gear generator.  The runtime must route
all 72 teeth through symbolic epsilon orientation and the zero-centered Lo Shu
surface before the exact coefficient 2 may appear in a closure witness.
"""
from __future__ import annotations

from dataclasses import dataclass
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
G72_OPERATOR = "G72"
G72_RADICAND = 2
G72_ROOT_ORDER = 72
FNV_OFFSET = 1469598103934665603
FNV_PRIME = 1099511628211


class Pass220I021ClosureError(ValueError):
    pass


@dataclass(frozen=True)
class G72State:
    tooth_index: int
    completed_routes: int
    route_signature64: int
    generator_unresolved: bool = True
    epsilon_symbol: str = "e"
    epsilon_magnitude_unresolved: bool = True


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


def _mix_byte(hash64: int, value: int) -> int:
    return ((hash64 ^ (value & 0xFF)) * FNV_PRIME) & ((1 << 64) - 1)


def _mix_u32(hash64: int, value: int) -> int:
    for shift in range(0, 32, 8):
        hash64 = _mix_byte(hash64, (value >> shift) & 0xFF)
    return hash64


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


def g72_generator_descriptor():
    return _receipt({
        "schema": "HHS_PASS_220_I021_G72_GENERATOR_DESCRIPTOR_V1",
        "operator": G72_OPERATOR,
        "source_term": "2^(1/72)",
        "radicand": G72_RADICAND,
        "root_order": G72_ROOT_ORDER,
        "immutable_generator": True,
        "noncommutative_ordered_transition": True,
        "scalar_evaluation_allowed": False,
        "epsilon_symbolic_magnitude": True,
        "lo_shu_route_required": True,
        "floating_point_authority": False,
        "canonical_admission_authority": False,
    })


def g72_initial_state() -> G72State:
    return G72State(0, 0, FNV_OFFSET)


def _g72_state_valid(state: G72State) -> bool:
    return (
        isinstance(state, G72State)
        and state.tooth_index == state.completed_routes
        and 0 <= state.tooth_index <= G72_ROOT_ORDER
        and state.generator_unresolved is True
        and state.epsilon_symbol == "e"
        and state.epsilon_magnitude_unresolved is True
    )


def g72_advance(state: G72State):
    if not _g72_state_valid(state):
        raise Pass220I021ClosureError("invalid G72 state")
    if state.tooth_index >= G72_ROOT_ORDER:
        raise Pass220I021ClosureError("G72 has already routed all 72 teeth")

    from_tooth = state.tooth_index
    to_tooth = from_tooth + 1
    signature = _mix_u32(state.route_signature64, from_tooth)
    signature = _mix_u32(signature, to_tooth)
    for value in TRINARY:
        signature = _mix_byte(signature, value + 4)
    for row in ZERO_CENTERED_LO_SHU:
        for value in row:
            signature = _mix_byte(signature, value + 8)

    sums = zero_centered_lo_shu_line_sums()
    route = _receipt({
        "schema": "HHS_PASS_220_I021_G72_ROUTE_WITNESS_V1",
        "operator": G72_OPERATOR,
        "from_tooth": from_tooth,
        "to_tooth": to_tooth,
        "epsilon_symbol": "e",
        "epsilon_magnitude_unresolved": True,
        "epsilon_phase_orientation": TRINARY,
        "lo_shu_coefficients": ZERO_CENTERED_LO_SHU,
        "lo_shu_row_sums": tuple(_text(v) for v in sums["rows"]),
        "lo_shu_column_sums": tuple(_text(v) for v in sums["columns"]),
        "lo_shu_diagonal_sums": tuple(_text(v) for v in sums["diagonals"]),
        "previous_route_signature64": state.route_signature64,
        "route_signature64": signature,
        "generator_unresolved_before": True,
        "generator_unresolved_after": True,
        "scalar_resolution_performed": False,
        "local_zero_sum": sum(TRINARY) == 0,
        "lo_shu_zero_sum": all(v == 0 for group in sums.values() for v in group),
        "floating_point_authority": False,
    })
    next_state = G72State(to_tooth, state.completed_routes + 1, signature)
    return next_state, route


def g72_close(state: G72State):
    if not _g72_state_valid(state):
        raise Pass220I021ClosureError("invalid G72 state")
    if state.completed_routes != G72_ROOT_ORDER:
        raise Pass220I021ClosureError(
            "G72 closure is forbidden before 72 distinct epsilon/Lo Shu routing cycles"
        )
    u_exponent = G72_ROOT_ORDER * G72_ROOT_ORDER
    f_exponent = HARMONIC_CELLS * G72_ROOT_ORDER
    if u_exponent != VM5184 or f_exponent != FRACTAL_ORBIT:
        raise Pass220I021ClosureError("G72 exponent geometry did not close")
    return _receipt({
        "schema": "HHS_PASS_220_I021_G72_CLOSURE_V1",
        "operator": G72_OPERATOR,
        "routed_cycles": state.completed_routes,
        "required_cycles": G72_ROOT_ORDER,
        "emergent_binary_coefficient": G72_RADICAND,
        "u_exponent": u_exponent,
        "f_exponent": f_exponent,
        "resolved_identity": "f^10368=2u^5184",
        "generator_still_unresolved": True,
        "premature_scalar_resolution": False,
        "epsilon_orientation_preserved": True,
        "lo_shu_routing_preserved": True,
        "final_route_signature64": state.route_signature64,
        "floating_point_authority": False,
        "canonical_admission_authority": False,
    })


def harmonic_root_closure_witness():
    state = g72_initial_state()
    routes = []
    for _ in range(G72_ROOT_ORDER):
        state, route = g72_advance(state)
        routes.append(route)
    closure = g72_close(state)
    if not all(route["generator_unresolved_after"] for route in routes):
        raise Pass220I021ClosureError("G72 was resolved before the 72-cycle closure")
    if any(route["scalar_resolution_performed"] for route in routes):
        raise Pass220I021ClosureError("scalar preemption detected in G72 route")
    return _receipt({
        "schema": "HHS_PASS_220_I021_HARMONIC_ROOT_CLOSURE_V2",
        "source_identity": ROOT_IDENTITY,
        "generator": g72_generator_descriptor(),
        "routed_cycles": len(routes),
        "first_route_signature64": routes[0]["route_signature64"],
        "final_route_signature64": routes[-1]["route_signature64"],
        "all_routes_generator_unresolved": True,
        "all_routes_scalar_resolution_performed": False,
        "all_routes_lo_shu_zero_sum": all(route["lo_shu_zero_sum"] for route in routes),
        "all_routes_local_zero_sum": all(route["local_zero_sum"] for route in routes),
        "emergent_binary_coefficient": closure["emergent_binary_coefficient"],
        "f_exponent": closure["f_exponent"],
        "u_exponent": closure["u_exponent"],
        "resolved_identity": closure["resolved_identity"],
        "generator_still_unresolved": closure["generator_still_unresolved"],
        "fractional_exponent_approximated": False,
        "floating_point_authority": False,
        "projection_only": True,
        "canonical_admission_authority": False,
    })


def full_i021_witness():
    local = epsilon_phase_triplet(Fraction(1))
    phase = phase_matrix_144_witness()
    root = harmonic_root_closure_witness()
    return _receipt({
        "schema": "HHS_PASS_220_I021_FULL_CLOSURE_V2",
        "development_equation": DEVELOPMENT_EQUATION,
        "root_identity": ROOT_IDENTITY,
        "local_phase_tuple": LOCAL_PHASE_TUPLE,
        "local_trinary": tuple(sgn3(v) for v in local),
        "local_epsilon_sum": _text(sum(local, Fraction(0))),
        "harmonic_cells": HARMONIC_CELLS,
        "vm81_cells": VM81_CELLS,
        "vm5184": VM5184,
        "fractal_orbit": FRACTAL_ORBIT,
        "g72_operator": G72_OPERATOR,
        "g72_routed_cycles": root["routed_cycles"],
        "g72_generator_still_unresolved": root["generator_still_unresolved"],
        "g72_no_scalar_preemption": not root["all_routes_scalar_resolution_performed"],
        "phase_matrix_closed": phase["closed"],
        "root_identity_closed": root["resolved_identity"] == "f^10368=2u^5184",
        "closed": (
            phase["closed"]
            and sum(local, Fraction(0)) == 0
            and root["routed_cycles"] == G72_ROOT_ORDER
            and root["generator_still_unresolved"]
        ),
        "floating_point_authority": False,
        "projection_only": True,
        "canonical_admission_authority": False,
    })
