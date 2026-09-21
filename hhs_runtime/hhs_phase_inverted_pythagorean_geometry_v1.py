"""Exact reference oracle for the Pass 219 phase-inverted Pythagorean theorem.

This module lowers additive witnesses from
`HHS_PHASE_INVERTED_PYTHAGOREAN_ENTANGLEMENT_THEOREM_V1.md` without widening
canonical VM81/Hash72/Hash216 authority.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from math import isqrt
from typing import Any, Dict, Mapping, Tuple

from hhs_spi_fibonacci_pythagorean_scaling_rule_v1 import square_state_sequence


FORMAT = "HHS_PHASE_INVERTED_PYTHAGOREAN_GEOMETRY_V1"
VERSION = "1.0.0"
PROFILE = "PASS219-PHASE-INVERTED-PYTHAGOREAN-v1"

A2 = 1
B2 = 2
C2 = A2 + B2
C4 = C2 * C2
P4_COLLAPSE = C4

LO_SHU: Tuple[Tuple[int, ...], ...] = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
FINITE_PHASE = {4: 0, 2: 18, 6: 36, 8: 54}
CONTINUATION = frozenset({9, 3, 5, 7, 1})

VM5184 = 72**2
MANIFOLD = 72**72
BIPARTITE_COORDINATES = 72 + 72
SCIENTIFIC_MATRIX_ROWS = 10
SCIENTIFIC_MATRIX_COLUMNS = 10
SCIENTIFIC_MATRIX_CELLS = SCIENTIFIC_MATRIX_ROWS * SCIENTIFIC_MATRIX_COLUMNS


class PhaseInvertedPythagoreanError(ValueError):
    pass


def _q(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise PhaseInvertedPythagoreanError("exact geometry forbids bool/float arithmetic")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise PhaseInvertedPythagoreanError(f"invalid exact scalar: {value!r}") from exc


def _exact_json(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {
            "type": "EXACT_RATIONAL",
            "numerator": value.numerator,
            "denominator": value.denominator,
        }
    if isinstance(value, tuple):
        return [_exact_json(item) for item in value]
    if isinstance(value, list):
        return [_exact_json(item) for item in value]
    if isinstance(value, frozenset):
        return [_exact_json(item) for item in sorted(value)]
    if isinstance(value, Mapping):
        return {str(key): _exact_json(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise PhaseInvertedPythagoreanError(f"unsupported receipt type: {type(value).__name__}")


def _stable_json(value: Any) -> str:
    return json.dumps(_exact_json(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _seal(receipt: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(receipt)
    payload["receipt_sha256"] = sha256(_stable_json(payload).encode("utf-8")).hexdigest()
    return _exact_json(payload)


def pythagorean_collapse_witness() -> Dict[str, Any]:
    triangle = (C2 - B2, C2 - A2, A2 + B2)
    expected = (A2, B2, C2)
    if C2 != 3 or C4 != 9 or triangle != expected:
        raise PhaseInvertedPythagoreanError("PYTHAGOREAN_SEED_MISMATCH")
    receipt: Dict[str, Any] = {
        "schema": "HHS_PHASE_INVERTED_PYTHAGOREAN_COLLAPSE_WITNESS_V1",
        "profile": PROFILE,
        "a²": A2,
        "b²": B2,
        "c²": C2,
        "c⁴": C4,
        "P⁴": P4_COLLAPSE,
        "V_Ω": P4_COLLAPSE,
        "triangle_reconstruction": triangle,
        "triangle_expected": expected,
        "p2_branch_selected": False,
        "projection_only": True,
        "canonical_admission_authority": False,
        "floating_point_authority": False,
    }
    return _seal(receipt)


def kappa(digit: int) -> int:
    if isinstance(digit, bool) or not isinstance(digit, int) or not 1 <= digit <= 9:
        raise PhaseInvertedPythagoreanError("Lo Shu digit must be an integer in 1..9")
    return 10 - digit


def lo_shu_phase_witness() -> Dict[str, Any]:
    flattened = tuple(cell for row in LO_SHU for cell in row)
    if set(flattened) != set(range(1, 10)):
        raise PhaseInvertedPythagoreanError("LO_SHU_PARTITION_MISMATCH")
    if set(FINITE_PHASE) | CONTINUATION != set(flattened):
        raise PhaseInvertedPythagoreanError("LO_SHU_PARTITION_MISMATCH")
    if set(FINITE_PHASE) & CONTINUATION:
        raise PhaseInvertedPythagoreanError("LO_SHU_PARTITION_MISMATCH")

    half_turn_checks = {}
    for digit, phase in FINITE_PHASE.items():
        opposite = kappa(digit)
        expected = (phase + 36) % 72
        actual = FINITE_PHASE.get(opposite)
        if actual != expected:
            raise PhaseInvertedPythagoreanError("LO_SHU_HALF_TURN_MISMATCH")
        if kappa(opposite) != digit:
            raise PhaseInvertedPythagoreanError("LO_SHU_HALF_TURN_MISMATCH")
        half_turn_checks[str(digit)] = {
            "opposite": opposite,
            "phase": phase,
            "opposite_phase": actual,
            "expected_opposite_phase": expected,
        }

    receipt: Dict[str, Any] = {
        "schema": "HHS_LO_SHU_PHASE_INVERSION_WITNESS_V1",
        "profile": PROFILE,
        "lo_shu": LO_SHU,
        "finite_phase": FINITE_PHASE,
        "continuation": CONTINUATION,
        "finite_count": len(FINITE_PHASE),
        "continuation_count": len(CONTINUATION),
        "delta_phase": 18,
        "half_turn": 36,
        "kappa_equation": "kappa(d)=10-d",
        "half_turn_checks": half_turn_checks,
        "projection_only": True,
        "canonical_admission_authority": False,
        "floating_point_authority": False,
    }
    return _seal(receipt)


def pq_orientation_witness(*, p: Any, q: Any, P: Any) -> Dict[str, Any]:
    p_q = _q(p)
    q_q = _q(q)
    P_q = _q(P)
    symmetric_sum = p_q + q_q
    symmetric_product = p_q * q_q
    if symmetric_sum != 2 * P_q or symmetric_product != P_q * P_q - 1:
        raise PhaseInvertedPythagoreanError("PQ_PROJECTION_PRECONDITION_FAILED")

    delta = q_q - p_q
    sigma = delta / 2
    if delta * delta != 4 or sigma * sigma != 1:
        raise PhaseInvertedPythagoreanError("PQ_ORIENTATION_MISMATCH")

    quotient = None
    quotient_closed = None
    if P_q != 0:
        quotient = (delta * P_q) / symmetric_sum
        quotient_closed = quotient == sigma
        if not quotient_closed:
            raise PhaseInvertedPythagoreanError("PQ_ORIENTATION_MISMATCH")

    receipt: Dict[str, Any] = {
        "schema": "HHS_PQ_PHASE_ORIENTATION_WITNESS_V1",
        "profile": PROFILE,
        "p": p_q,
        "q": q_q,
        "P": P_q,
        "p_plus_q": symmetric_sum,
        "pq": symmetric_product,
        "q_minus_p": delta,
        "sigma": sigma,
        "sigma_squared": sigma * sigma,
        "orientation_quotient": quotient,
        "orientation_quotient_closed": quotient_closed,
        "swap_flips_sigma": (-delta / 2) == -sigma,
        "projection_only": True,
        "canonical_admission_authority": False,
        "floating_point_authority": False,
    }
    return _seal(receipt)


def directional_projection_witness() -> Dict[str, Any]:
    receipt: Dict[str, Any] = {
        "schema": "HHS_DIRECTIONAL_PHASE_COLLAPSE_PROJECTION_V1",
        "profile": PROFILE,
        "ordered_source_symbols": ("xy", "yx", "zw", "wz"),
        "typed_projection": {"yx": "xy", "zw": "wz"},
        "global_commutativity_authorized": False,
        "normalized_matrix": (
            ("xy/4", "(x+y)/9", "xy/2"),
            ("(xy-wz)/3", "(2xy+x+y-z-w-2wz)/5", "(wz-xy)/7"),
            ("wz/8", "z+w", "wz/6"),
        ),
        "projection_only": True,
        "canonical_admission_authority": False,
        "floating_point_authority": False,
    }
    return _seal(receipt)


def positive_factor_pairs(target: int) -> Tuple[Tuple[int, int], ...]:
    if isinstance(target, bool) or not isinstance(target, int) or target <= 0:
        raise PhaseInvertedPythagoreanError("factor target must be a positive integer")
    pairs = []
    for left in range(1, isqrt(target) + 1):
        if target % left == 0:
            pairs.append((left, target // left))
    return tuple(pairs)


def factorization_closure_100_witness() -> Dict[str, Any]:
    pairs = positive_factor_pairs(SCIENTIFIC_MATRIX_CELLS)
    expected = ((1, 100), (2, 50), (4, 25), (5, 20), (10, 10))
    all_agree = pairs == expected and all(left * right == 100 for left, right in pairs)
    if not all_agree:
        raise PhaseInvertedPythagoreanError("FACTOR_100_CLOSURE_FAILED")
    receipt: Dict[str, Any] = {
        "schema": "HHS_FACTOR_100_CLOSURE_WITNESS_V1",
        "profile": PROFILE,
        "matrix_shape": (SCIENTIFIC_MATRIX_ROWS, SCIENTIFIC_MATRIX_COLUMNS),
        "matrix_cells": SCIENTIFIC_MATRIX_CELLS,
        "positive_factor_pairs": pairs,
        "prime_factorization": "2²*5²",
        "all_factorizations_agree": True,
        "projection_only": True,
        "canonical_admission_authority": False,
        "floating_point_authority": False,
    }
    return _seal(receipt)


def one_positional_anchor_witness() -> Dict[str, Any]:
    row_1based = column_1based = None
    for row_index, row in enumerate(LO_SHU, start=1):
        for column_index, value in enumerate(row, start=1):
            if value == 1:
                row_1based, column_1based = row_index, column_index
                break
    if (row_1based, column_1based) != (3, 2):
        raise PhaseInvertedPythagoreanError("LO_SHU_PARTITION_MISMATCH")
    receipt: Dict[str, Any] = {
        "schema": "HHS_ONE_POSITIONAL_ANCHOR_WITNESS_V1",
        "profile": PROFILE,
        "scalar_unit": A2,
        "lo_shu_value": 1,
        "lo_shu_position_1based": (3, 2),
        "lo_shu_position_0based": (2, 1),
        "scientific_matrix_shape": (10, 10),
        "scientific_matrix_cells": 100,
        "bigint_string_position": None,
        "bigint_string_position_resolved": False,
        "resolution_requirement": "canonical serialization source required",
        "projection_only": True,
        "canonical_admission_authority": False,
        "floating_point_authority": False,
    }
    return _seal(receipt)


def manifold_closure_witness() -> Dict[str, Any]:
    if VM5184 != 5184 or VM5184 != 81 * 64:
        raise PhaseInvertedPythagoreanError("MANIFOLD_EXPONENT_CLOSURE_FAILED")
    if MANIFOLD != VM5184**36:
        raise PhaseInvertedPythagoreanError("MANIFOLD_EXPONENT_CLOSURE_FAILED")
    ladder = square_state_sequence(9)
    if ladder != tuple(Fraction(value) for value in (1, 2, 3, 5, 8, 13, 21, 34, 55)):
        raise PhaseInvertedPythagoreanError("Fibonacci dependency mismatch")
    receipt: Dict[str, Any] = {
        "schema": "HHS_72_72_MANIFOLD_CLOSURE_WITNESS_V1",
        "profile": PROFILE,
        "72²": VM5184,
        "81*64": 81 * 64,
        "72^72": MANIFOLD,
        "5184^36": VM5184**36,
        "bipartite_coordinates": BIPARTITE_COORDINATES,
        "fibonacci_square_states": ladder,
        "finite_phi_substitution": False,
        "projection_only": True,
        "canonical_admission_authority": False,
        "floating_point_authority": False,
    }
    return _seal(receipt)


def full_geometry_witness() -> Dict[str, Any]:
    receipt: Dict[str, Any] = {
        "schema": "HHS_PHASE_INVERTED_PYTHAGOREAN_FULL_GEOMETRY_V1",
        "format": FORMAT,
        "version": VERSION,
        "profile": PROFILE,
        "pythagorean": pythagorean_collapse_witness(),
        "lo_shu": lo_shu_phase_witness(),
        "directional_projection": directional_projection_witness(),
        "one_anchor": one_positional_anchor_witness(),
        "factor_100": factorization_closure_100_witness(),
        "manifold": manifold_closure_witness(),
        "projection_only": True,
        "canonical_admission_authority": False,
        "floating_point_authority": False,
    }
    return _seal(receipt)
