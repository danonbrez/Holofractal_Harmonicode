"""Pass 220 I017: exact multidimensional constraint-manifold enforcement.

This module composes the already-verified I014/I015 Lo Shu/G41/ordered-phase
surfaces with the compatible dimensional, Hash72-facing algebraic projection,
decimal-cell, 3^4=81 geometry, and ordered curvature constraints supplied in
the Pass 220 formalization.

Important authority boundary:
- HASH72 below is an algebraic/curvature projection symbol and witness value;
  this module does not mint or replace the canonical 72-character Hash72
  digest/ledger authority.
- Trigonometric/spherical/toroidal coordinates are preserved symbolically.
  Canonical arithmetic remains exact integer/rational phase-index arithmetic.
- The verbatim compound equality is retained as a typed constructor/admission
  surface; it is not flattened into ordinary scalar equality.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_g41_sudoku_fingerprint_algebra_v1 import (
    derived_cell_values,
    g41_surface_reachability_witness,
    ordered_zero_cell_witness,
    symbol_radix,
)
from hhs_runtime.hhs_pass220_palindromic_ordered_phase_v1 import (
    palindromic_ordered_phase_witness,
)

SCHEMA = "HHS_PASS_220_MULTIDIMENSIONAL_CONSTRAINT_MANIFOLD_V1"
VERSION = "1.0.0-checkpoint.17"
PROFILE = "PASS220-I017-MULTIDIMENSIONAL-CONSTRAINT-MANIFOLD-v1"
WITNESS_SCHEMA = "HHS_PASS_220_MULTIDIMENSIONAL_CONSTRAINT_WITNESS_V1"

PHASE_CELLS = 72
NUCLEUS_CELLS = 9
VM81_CELLS = 81
TERNARY_AXIS = 3
LOCAL_MAGNITUDE_DOF = 9
CLOSURE_STATE_COUNT = 1
DECIMAL_SYMBOL_COUNT = 10

VERBATIM_CONSTRAINT_EQUATIONS: Tuple[str, ...] = (
    "(u^72)^2=HASH72",
    "HASH72=Q(P^4)^2-((P^4/(P^2-pq))=L^2)",
    "9=(HASH72=Q(P^4)^2-((P^4/(P^2-pq))=L^2))/b^4=P^4",
    "b^2/a^4",
    (
        "(((x*y)*(a^2+b^2==c^2))+(((z*w)*((-a^2)-b^2))==c^2))/"
        "((z*w)+(x*y))==c^2+(z*w)-(x*y)-"
        "{{x*y,y+x,x*y},{-w*z+x*y,(-2)*w*z-z+2*x*y+y+x-w,"
        "w*z-x*y},{w*z,z+w,w*z}}+3==0"
    ),
)


class Pass220MultidimensionalConstraintError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(
        _stable_json(record).encode("utf-8")
    ).hexdigest()
    return record


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220MultidimensionalConstraintError(
            f"{name} must be an exact integer"
        )
    return value


def _exact_div(numerator: int, denominator: int, *, name: str) -> int:
    n = _exact_int(numerator, name=f"{name}.numerator")
    d = _exact_int(denominator, name=f"{name}.denominator")
    if d == 0 or n % d:
        raise Pass220MultidimensionalConstraintError(
            f"{name} must be an exact integer quotient"
        )
    return n // d


def phase_index(index: int) -> int:
    """Return the exact 72-cell periodic phase address."""
    return _exact_int(index, name="phase index") % PHASE_CELLS


def phase_turn(index: int) -> Tuple[int, int]:
    """Fixed-denominator exact angular phase: residue/72 turns."""
    return phase_index(index), PHASE_CELLS


def ternary_address_to_board(
    a: int,
    b: int,
    c: int,
    d: int,
) -> Tuple[int, int]:
    """Project one Z3^4 address into the visible 9x9 chart."""
    coordinates = tuple(
        _exact_int(value, name=name)
        for name, value in zip(("a", "b", "c", "d"), (a, b, c, d))
    )
    if any(not 0 <= value < TERNARY_AXIS for value in coordinates):
        raise Pass220MultidimensionalConstraintError(
            "ternary coordinates must be in 0..2"
        )
    aa, bb, cc, dd = coordinates
    return TERNARY_AXIS * aa + bb, TERNARY_AXIS * cc + dd


def wrap_board_step(
    row: int,
    column: int,
    delta_row: int,
    delta_column: int,
) -> Tuple[int, int]:
    """Pacman/toroidal wrap on the visible 9x9 chart."""
    r = _exact_int(row, name="row")
    c = _exact_int(column, name="column")
    dr = _exact_int(delta_row, name="delta_row")
    dc = _exact_int(delta_column, name="delta_column")
    if not 0 <= r < 9 or not 0 <= c < 9:
        raise Pass220MultidimensionalConstraintError(
            "board address must be in 0..8"
        )
    return (r + dr) % 9, (c + dc) % 9


def _all_ternary_addresses() -> Tuple[Tuple[int, int, int, int], ...]:
    return tuple(
        (a, b, c, d)
        for a in range(3)
        for b in range(3)
        for c in range(3)
        for d in range(3)
    )


def invariant_nucleus_addresses() -> Tuple[Tuple[int, int, int, int], ...]:
    """The central 3x3 nucleus: a=c=1, with b,d spanning Z3."""
    return tuple(
        (1, b, 1, d)
        for b in range(3)
        for d in range(3)
    )


def transport_addresses() -> Tuple[Tuple[int, int, int, int], ...]:
    nucleus = set(invariant_nucleus_addresses())
    return tuple(
        address
        for address in _all_ternary_addresses()
        if address not in nucleus
    )


def transport_loop_address(index: int) -> Tuple[int, int, int, int]:
    """Cyclic address on the exact 72-position transport complement."""
    return transport_addresses()[phase_index(index)]


def dimensional_phase_ladder_witness() -> Dict[str, Any]:
    addresses = _all_ternary_addresses()
    nucleus = invariant_nucleus_addresses()
    transport = transport_addresses()
    board_addresses = tuple(
        ternary_address_to_board(*address)
        for address in addresses
    )
    periodic = all(
        phase_turn(index + PHASE_CELLS) == phase_turn(index)
        for index in range(PHASE_CELLS)
    )
    transport_periodic = all(
        transport_loop_address(index + PHASE_CELLS)
        == transport_loop_address(index)
        for index in range(PHASE_CELLS)
    )
    return {
        "one_dimensional_phase": {
            "carrier": "u^n",
            "quantization": "theta_n=2O*n/72",
            "exact_turn_denominator": 72,
            "ordered_direction_preserved": True,
        },
        "two_dimensional_circular_projection": (
            "cos(theta_n)",
            "sin(theta_n)",
        ),
        "three_dimensional_spherical_projection": (
            "r*sin(phi)*cos(theta_n)",
            "r*sin(phi)*sin(theta_n)",
            "r*cos(phi)",
        ),
        "four_dimensional_toroidal_projection": (
            "Rxy*cos(theta_n)",
            "Rxy*sin(theta_n)",
            "Rzw*cos(phi_n)",
            "Rzw*sin(phi_n)",
        ),
        "four_dimensional_phase_pairs": (("x", "y"), ("z", "w")),
        "scalar_semantics": (
            "4D curvature projection; scalar is not the primitive ordered state"
        ),
        "local_fiber": {
            "magnitude_dof": LOCAL_MAGNITUDE_DOF,
            "closure_states": CLOSURE_STATE_COUNT,
            "notation": "9D+0",
            "decimal_symbols": DECIMAL_SYMBOL_COUNT,
        },
        "ternary_geometry": {
            "3_power_4": TERNARY_AXIS**4,
            "vm81_cells": VM81_CELLS,
            "nucleus_3_power_2": TERNARY_AXIS**2,
            "nucleus_cells": len(nucleus),
            "transport_cells": len(transport),
            "decomposition": (len(transport), len(nucleus)),
            "address_symmetry_cardinality_81_power_4": VM81_CELLS**4,
            "visible_board_unique_addresses": len(set(board_addresses)),
        },
        "phase_periodicity_all_72": periodic,
        "transport_loop_periodicity_all_72": transport_periodic,
        "toroidal_wrap_examples": {
            "row_forward": wrap_board_step(8, 4, 1, 0),
            "row_reverse": wrap_board_step(0, 4, -1, 0),
            "column_forward": wrap_board_step(4, 8, 0, 1),
            "column_reverse": wrap_board_step(4, 0, 0, -1),
        },
    }


def hash72_algebraic_projection_witness(
    *,
    a2: int = 1,
    b2: int = 2,
    c2: int = 3,
    p2_minus_pq: int = 1,
) -> Dict[str, Any]:
    """Exact scalar-facing projection of the typed HASH72/Q/P/L constraints.

    This is not the cryptographic/ledger Hash72 digest. It is the exact
    algebraic projection of the HASH72 symbol on the current Genesis branch.
    """
    a = _exact_int(a2, name="a2")
    b = _exact_int(b2, name="b2")
    c = _exact_int(c2, name="c2")
    delta = _exact_int(p2_minus_pq, name="p2_minus_pq")
    if a <= 0 or b <= 0 or c <= 0:
        raise Pass220MultidimensionalConstraintError(
            "Genesis squared magnitudes must be positive"
        )
    if a + b != c:
        raise Pass220MultidimensionalConstraintError(
            "Pythagorean squared-magnitude closure failed"
        )
    if delta != a:
        raise Pass220MultidimensionalConstraintError(
            "P^2-pq must equal the Genesis a^2 closure unit"
        )

    a4 = a * a
    b4 = b * b
    p4 = c * c
    dyadic_exponent = _exact_div(b, a4, name="b2/a4")
    l2 = _exact_div(p4, delta, name="P4/(P2-pq)")
    hash72_projection = b4 * p4
    q_p4_squared = hash72_projection + l2
    q_ratio = _exact_div(q_p4_squared, p4, name="Q(P4)^2/P4")
    cells = derived_cell_values(a2=a, b2=b, c2=c)

    return {
        "authority_scope": (
            "ALGEBRAIC_PROJECTION_ONLY_NO_HASH72_DIGEST_MINT_AUTHORITY"
        ),
        "a2": a,
        "a4": a4,
        "b2": b,
        "b4": b4,
        "c2": c,
        "P4": p4,
        "P2_minus_pq": delta,
        "b2_over_a4": dyadic_exponent,
        "u72_pair_exponent": dyadic_exponent,
        "u_cycle_exponent": PHASE_CELLS * dyadic_exponent,
        "L2": l2,
        "HASH72_projection": hash72_projection,
        "Q_P4_squared": q_p4_squared,
        "Q_P4_squared_over_P4": q_ratio,
        "hash72_equals_q_square_minus_l2": (
            hash72_projection == q_p4_squared - l2
        ),
        "hash72_over_b4_equals_P4": (
            _exact_div(
                hash72_projection,
                b4,
                name="HASH72/b4",
            )
            == p4
        ),
        "L2_equals_P4": l2 == p4,
        "C4_equals_b4": cells[4] == b4,
        "C5_equals_Q_ratio": cells[5] == q_ratio,
        "C9_equals_P4": cells[9] == p4,
        "projected_equation_values": {
            "C4": cells[4],
            "C5": cells[5],
            "C9": cells[9],
            "HASH72": hash72_projection,
            "Q_P4_squared": q_p4_squared,
        },
    }


def _det3(matrix: Sequence[Sequence[int]]) -> int:
    rows = tuple(tuple(row) for row in matrix)
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise Pass220MultidimensionalConstraintError(
            "determinant requires a 3x3 matrix"
        )
    a, b, c = rows[0]
    d, e, f = rows[1]
    g, h, i = rows[2]
    values = (a, b, c, d, e, f, g, h, i)
    if any(isinstance(v, bool) or not isinstance(v, int) for v in values):
        raise Pass220MultidimensionalConstraintError(
            "matrix must contain exact integers"
        )
    return (
        a * (e * i - f * h)
        - b * (d * i - f * g)
        + c * (d * h - e * g)
    )


def ordered_curvature_tensor_witness(
    *,
    a2: int = 1,
    b2: int = 2,
    c2: int = 3,
    sx: int = 0,
    sz: int = 0,
    xy: int = 1,
    yx: int = -1,
    zw: int = 1,
    wz: int = -1,
) -> Dict[str, Any]:
    """Enforce the ordered xy/yx/zw/wz projection without commuting it."""
    values = {
        "a2": a2,
        "b2": b2,
        "c2": c2,
        "sx": sx,
        "sz": sz,
        "xy": xy,
        "yx": yx,
        "zw": zw,
        "wz": wz,
    }
    checked = {
        name: _exact_int(value, name=name)
        for name, value in values.items()
    }
    a = checked["a2"]
    b = checked["b2"]
    c = checked["c2"]
    if a + b != c:
        raise Pass220MultidimensionalConstraintError(
            "a^2+b^2==c^2 admission failed"
        )
    expected_phase = {
        "sx": 0,
        "sz": 0,
        "xy": a,
        "yx": -a,
        "zw": a,
        "wz": -a,
    }
    actual_phase = {
        key: checked[key]
        for key in ("sx", "sz", "xy", "yx", "zw", "wz")
    }
    if actual_phase != expected_phase:
        raise Pass220MultidimensionalConstraintError(
            "ordered q=-1 phase projection mismatch"
        )

    # Preserve the exact order from the user's 3x3 tensor.  The center term
    # -2*wz-z+2*xy+y+x-w is regrouped only as
    # -2*wz+2*xy+(x+y)-(z+w), preserving ordered products.
    matrix = (
        (checked["xy"], checked["sx"], checked["xy"]),
        (
            -checked["wz"] + checked["xy"],
            -2 * checked["wz"]
            + 2 * checked["xy"]
            + checked["sx"]
            - checked["sz"],
            checked["wz"] - checked["xy"],
        ),
        (checked["wz"], checked["sz"], checked["wz"]),
    )
    row_sums = tuple(sum(row) for row in matrix)
    column_sums = tuple(
        sum(matrix[row][column] for row in range(3))
        for column in range(3)
    )
    trace = sum(matrix[index][index] for index in range(3))
    determinant = _det3(matrix)
    b4 = b * b
    outer_scalar_projection = c + checked["zw"] - checked["xy"] + c

    return {
        "verbatim_constraint": VERBATIM_CONSTRAINT_EQUATIONS[-1],
        "constructor_admission_surface": True,
        "ordinary_scalar_flattening_performed": False,
        "ordered_products_commuted": False,
        "ordered_phase": actual_phase,
        "directional_curvature_xy_minus_wz": (
            checked["xy"] - checked["wz"]
        ),
        "forward_circumference_zw_plus_xy": (
            checked["zw"] + checked["xy"]
        ),
        "matrix": matrix,
        "row_sums": row_sums,
        "column_sums": column_sums,
        "trace": trace,
        "determinant": determinant,
        "rank_projection": 2,
        "nonzero_scalar_curvature": b4,
        "outer_scalar_projection_C6": outer_scalar_projection,
        "expected_matrix": (
            (a, 0, a),
            (b, b4, -b),
            (-a, 0, -a),
        ),
        "matrix_matches_genesis_curvature_ladder": matrix
        == (
            (a, 0, a),
            (b, b4, -b),
            (-a, 0, -a),
        ),
        "directional_curvature_equals_b2": (
            checked["xy"] - checked["wz"] == b
        ),
        "forward_circumference_equals_b2": (
            checked["zw"] + checked["xy"] == b
        ),
        "trace_equals_b4": trace == b4,
        "outer_projection_equals_C6": (
            outer_scalar_projection == b * c
        ),
    }


def decimal_nested_layer_witness() -> Dict[str, Any]:
    cells = derived_cell_values()
    zero = ordered_zero_cell_witness()
    radix = symbol_radix()
    carry = {
        "input": (9, 1),
        "local_closed_digit": 0,
        "parent_increment": 1,
        "scalar_projection": 10,
    }
    return {
        "cell_values": cells,
        "symbols": tuple(range(10)),
        "nine_plus_zero": (
            tuple(cells[index] for index in range(10))
            == tuple(range(10))
        ),
        "C0_ordered_identity_preserved": zero["identity_preserved"],
        "radix": radix,
        "C9_plus_C1_equals_radix": cells[9] + cells[1] == radix,
        "carry_9_plus_1": carry,
        "russian_doll_layer_semantics": (
            "digit selects recursively nested modular shell; carry closes "
            "C9 to C0 and increments the enclosing shell"
        ),
    }


def admit_multidimensional_constraint_state(
    *,
    a2: int = 1,
    b2: int = 2,
    c2: int = 3,
    p2_minus_pq: int = 1,
    sx: int = 0,
    sz: int = 0,
    xy: int = 1,
    yx: int = -1,
    zw: int = 1,
    wz: int = -1,
) -> Dict[str, Any]:
    """Fail-closed admission through every compatible I017 constraint."""
    ladder = dimensional_phase_ladder_witness()
    hash72 = hash72_algebraic_projection_witness(
        a2=a2,
        b2=b2,
        c2=c2,
        p2_minus_pq=p2_minus_pq,
    )
    curvature = ordered_curvature_tensor_witness(
        a2=a2,
        b2=b2,
        c2=c2,
        sx=sx,
        sz=sz,
        xy=xy,
        yx=yx,
        zw=zw,
        wz=wz,
    )
    decimal = decimal_nested_layer_witness()
    g41 = g41_surface_reachability_witness()
    phase = palindromic_ordered_phase_witness()

    checks = {
        "phase_periodicity_72": ladder["phase_periodicity_all_72"],
        "transport_periodicity_72": (
            ladder["transport_loop_periodicity_all_72"]
        ),
        "3_power_4_is_81": (
            ladder["ternary_geometry"]["3_power_4"] == 81
        ),
        "81_decomposes_72_plus_9": (
            ladder["ternary_geometry"]["decomposition"] == (72, 9)
        ),
        "visible_3x3x3x3_projection_is_bijective": (
            ladder["ternary_geometry"]["visible_board_unique_addresses"]
            == 81
        ),
        "hash72_q_l_relation": (
            hash72["hash72_equals_q_square_minus_l2"]
        ),
        "hash72_normalizes_to_P4": (
            hash72["hash72_over_b4_equals_P4"]
        ),
        "L2_locks_P4": hash72["L2_equals_P4"],
        "C9_locks_P4": hash72["C9_equals_P4"],
        "Q_ratio_locks_C5": hash72["C5_equals_Q_ratio"],
        "ordered_curvature_matrix": (
            curvature["matrix_matches_genesis_curvature_ladder"]
        ),
        "directional_curvature_b2": (
            curvature["directional_curvature_equals_b2"]
        ),
        "forward_circumference_b2": (
            curvature["forward_circumference_equals_b2"]
        ),
        "curvature_trace_b4": curvature["trace_equals_b4"],
        "curvature_determinant_zero": curvature["determinant"] == 0,
        "outer_projection_C6": (
            curvature["outer_projection_equals_C6"]
        ),
        "decimal_9_plus_0": decimal["nine_plus_zero"],
        "decimal_radix_10": decimal["radix"] == 10,
        "decimal_carry_closure": (
            decimal["C9_plus_C1_equals_radix"]
        ),
        "g41_41_classes": (
            g41["entangled_fingerprint_class_count"] == 41
        ),
        "g41_single_fixed_center": (
            g41["fixed_class_count"] == 1
            and g41["single_fixed_class_position"] == 41
        ),
        "joint_phase_g41_preserves_41": (
            phase["combined_g41"]["combined_fingerprint_class_count"]
            == 41
        ),
        "palindromic_phase": phase["phase_path_palindrome"],
        "mirror_projected_views_equal": phase["projected_views_equal"],
    }
    if not all(checks.values()):
        failed = tuple(
            name for name, passed in checks.items() if not passed
        )
        raise Pass220MultidimensionalConstraintError(
            "constraint admission failed: " + ",".join(failed)
        )

    return _receipt(
        {
            "schema": WITNESS_SCHEMA,
            "version": VERSION,
            "profile": PROFILE,
            "ok": True,
            "verbatim_constraint_equations": VERBATIM_CONSTRAINT_EQUATIONS,
            "checks": checks,
            "dimensional_phase_ladder": ladder,
            "hash72_algebraic_projection": hash72,
            "ordered_curvature_tensor": curvature,
            "decimal_nested_layers": decimal,
            "g41_summary": {
                "oriented": g41["unique_oriented_fingerprint_count"],
                "classes": g41["entangled_fingerprint_class_count"],
                "fixed_positions": g41["fixed_class_positions"],
            },
            "palindromic_phase_summary": {
                "path": phase["phase_path"],
                "forward_projection": (
                    phase["forward_q_minus_one_projection"]
                ),
                "mirror_projection": (
                    phase["mirror_q_minus_one_projection"]
                ),
                "combined_classes": (
                    phase["combined_g41"][
                        "combined_fingerprint_class_count"
                    ]
                ),
            },
            "floating_point_authority": False,
            "ordinary_scalar_flattening_authority": False,
            "canonical_hash72_mint_authority": False,
            "canonical_hash216_authority": False,
            "canonical_vm81_mutation_authority": False,
            "mutation_performed": False,
        }
    )


def validate_multidimensional_constraint_manifold() -> Dict[str, Any]:
    witness = admit_multidimensional_constraint_state()
    return _receipt(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "profile": PROFILE,
            "ok": witness["ok"],
            "witness": witness,
            "invariant_ids": (
                "HHS-I008",
                "HHS-I010",
                "HHS-I011",
                "HHS-I012",
                "HHS-I014",
                "HHS-I015",
            ),
            "mutation_policy": (
                "READ_ONLY_EXACT_CONSTRAINT_ADMISSION_NO_VM81_MUTATION"
            ),
            "persistence_policy": "NO_CANONICAL_PERSISTENCE",
            "floating_point_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_vm81_mutation_authority": False,
        }
    )


def multidimensional_constraint_manifold_self_test() -> Dict[str, Any]:
    return validate_multidimensional_constraint_manifold()
