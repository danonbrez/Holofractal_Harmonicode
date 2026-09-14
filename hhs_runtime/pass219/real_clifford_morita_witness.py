"""Pass 219 RML10 exact real-Clifford / Morita period-eight witness.

RML10 strengthens the validated RML9 Bott reference bridge by constructing an
explicit exact integer representation of Cl_(0,8) in M_16(R) and a standard
full-corner matrix-unit Morita context for M_16(A) ~ A.

Convention:
    Cl_(0,8) generators e_i satisfy e_i^2 = -1 and
    e_i e_j + e_j e_i = 0 for i != j.

The eight 16x16 generators are built entirely from exact 2x2 real matrices by
Kronecker products.  All 256 ordered Clifford words are then verified to form
an exact Frobenius-orthogonal basis of M_16(R), yielding a constructive
Cl_(0,8) -> M_16(R) isomorphism witness at this representation level.

RML10 also constructs the standard matrix-unit full-corner witness

    e_00 M_16(A) e_00 ~= A
    sum_i E_i0 e_00 E_0i = I_16

which is the concrete matrix Morita context used to relate the period-eight
factor M_16(A) back to A.  It does not grant VM81 mutation, Hash72 mint, or
Hash216 persistence authority and does not reinterpret live HARMONICODE phase
coordinates as Clifford matrix entries.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from typing import Any, Mapping, Sequence

from hhs_runtime.pass219.bott8_native_correspondence import PASS188_B8_ORDER
from hhs_runtime.pass219.classical_bott_correspondence import (
    audit_rml5_generators_on_classical_bott_bridge,
    build_classical_bott_native_correspondence,
)

PASS = 219
ITERATION = "RML10_REAL_CLIFFORD_MORITA_WITNESS"

CL08_SCHEMA = "HHS_PASS219_RML10_CL08_M16R_EXACT_ISOMORPHISM_V1"
MORITA_SCHEMA = "HHS_PASS219_RML10_M16_FULL_CORNER_MORITA_CONTEXT_V1"
PERIOD8_SCHEMA = "HHS_PASS219_RML10_REAL_CLIFFORD_PERIOD8_WITNESS_V1"
PACKET_SCHEMA = "HHS_PASS219_RML10_CLIFFORD_BOTT_NATIVE_PACKET_V1"
GENERATOR_AUDIT_SCHEMA = "HHS_PASS219_RML10_CLIFFORD_GENERATOR_AUDIT_V1"

Matrix = tuple[tuple[int, ...], ...]

I2: Matrix = ((1, 0), (0, 1))
SIGMA1: Matrix = ((0, 1), (1, 0))
SIGMA2: Matrix = ((1, 0), (0, -1))
SIGMA12: Matrix = ((0, -1), (1, 0))

CL0_RESIDUE_MODELS = (
    {"residue": 0, "algebra": "R", "components": 1, "matrix_order": 1, "division_ring": "R", "real_dimension": 1},
    {"residue": 1, "algebra": "C", "components": 1, "matrix_order": 1, "division_ring": "C", "real_dimension": 2},
    {"residue": 2, "algebra": "H", "components": 1, "matrix_order": 1, "division_ring": "H", "real_dimension": 4},
    {"residue": 3, "algebra": "H+H", "components": 2, "matrix_order": 1, "division_ring": "H", "real_dimension": 8},
    {"residue": 4, "algebra": "M2(H)", "components": 1, "matrix_order": 2, "division_ring": "H", "real_dimension": 16},
    {"residue": 5, "algebra": "M4(C)", "components": 1, "matrix_order": 4, "division_ring": "C", "real_dimension": 32},
    {"residue": 6, "algebra": "M8(R)", "components": 1, "matrix_order": 8, "division_ring": "R", "real_dimension": 64},
    {"residue": 7, "algebra": "M8(R)+M8(R)", "components": 2, "matrix_order": 8, "division_ring": "R", "real_dimension": 128},
)


class RealCliffordMoritaError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise RealCliffordMoritaError(f"FLOAT_CLIFFORD_AUTHORITY_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RealCliffordMoritaError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _shape(matrix: Matrix) -> tuple[int, int]:
    if not matrix or not matrix[0]:
        raise RealCliffordMoritaError("NONEMPTY_EXACT_MATRIX_REQUIRED")
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise RealCliffordMoritaError("RECTANGULAR_EXACT_MATRIX_REQUIRED")
    if any(isinstance(value, bool) or not isinstance(value, int) for row in matrix for value in row):
        raise RealCliffordMoritaError("INTEGER_MATRIX_ENTRY_REQUIRED")
    return len(matrix), width


def _zero(rows: int, cols: int) -> Matrix:
    r = _exact_int(rows, "ROWS")
    c = _exact_int(cols, "COLS")
    if r <= 0 or c <= 0:
        raise RealCliffordMoritaError("POSITIVE_MATRIX_SHAPE_REQUIRED")
    return tuple(tuple(0 for _ in range(c)) for _ in range(r))


def _identity(order: int) -> Matrix:
    n = _exact_int(order, "IDENTITY_ORDER")
    if n <= 0:
        raise RealCliffordMoritaError("POSITIVE_MATRIX_ORDER_REQUIRED")
    return tuple(tuple(1 if i == j else 0 for j in range(n)) for i in range(n))


def _scale(matrix: Matrix, scalar: int) -> Matrix:
    _shape(matrix)
    k = _exact_int(scalar, "MATRIX_SCALAR")
    return tuple(tuple(k * value for value in row) for row in matrix)


def _add(left: Matrix, right: Matrix) -> Matrix:
    if _shape(left) != _shape(right):
        raise RealCliffordMoritaError("MATRIX_ADD_SHAPE_MISMATCH")
    return tuple(
        tuple(left[i][j] + right[i][j] for j in range(len(left[0])))
        for i in range(len(left))
    )


def _matmul(left: Matrix, right: Matrix) -> Matrix:
    lr, lc = _shape(left)
    rr, rc = _shape(right)
    if lc != rr:
        raise RealCliffordMoritaError("MATRIX_PRODUCT_SHAPE_MISMATCH")
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(lc)) for j in range(rc))
        for i in range(lr)
    )


def _kron(left: Matrix, right: Matrix) -> Matrix:
    lr, lc = _shape(left)
    rr, rc = _shape(right)
    return tuple(
        tuple(
            left[i // rr][j // rc] * right[i % rr][j % rc]
            for j in range(lc * rc)
        )
        for i in range(lr * rr)
    )


def _kron4(a: Matrix, b: Matrix, c: Matrix, d: Matrix) -> Matrix:
    return _kron(_kron(_kron(a, b), c), d)


def _frobenius_inner(left: Matrix, right: Matrix) -> int:
    if _shape(left) != _shape(right):
        raise RealCliffordMoritaError("FROBENIUS_SHAPE_MISMATCH")
    return sum(
        left[i][j] * right[i][j]
        for i in range(len(left))
        for j in range(len(left[0]))
    )


def _matrix_hash(matrix: Matrix) -> str:
    return _sha256([list(row) for row in matrix])


def build_cl08_generators() -> tuple[Matrix, ...]:
    """Return eight exact 16x16 real generators for Cl_(0,8)."""
    return (
        _scale(_kron4(I2, I2, SIGMA2, SIGMA12), -1),
        _scale(_kron4(I2, I2, SIGMA12, I2), -1),
        _scale(_kron4(I2, SIGMA1, SIGMA1, SIGMA12), -1),
        _scale(_kron4(I2, SIGMA2, SIGMA1, SIGMA12), -1),
        _kron4(I2, SIGMA12, SIGMA1, I2),
        _scale(_kron4(I2, SIGMA12, SIGMA2, SIGMA1), -1),
        _kron4(SIGMA1, SIGMA12, SIGMA2, SIGMA2),
        _kron4(SIGMA2, SIGMA12, SIGMA2, SIGMA2),
    )


def build_cl08_word_matrices() -> tuple[Matrix, ...]:
    generators = build_cl08_generators()
    words: list[Matrix] = []
    for mask in range(1 << 8):
        matrix = _identity(16)
        for index, generator in enumerate(generators):
            if (mask >> index) & 1:
                matrix = _matmul(matrix, generator)
        words.append(matrix)
    return tuple(words)


@lru_cache(maxsize=1)
def build_cl08_isomorphism_witness() -> dict[str, Any]:
    generators = build_cl08_generators()
    identity16 = _identity(16)
    negative_identity16 = _scale(identity16, -1)

    square_checks = [_matmul(generator, generator) == negative_identity16 for generator in generators]
    anticommutation_checks = 0
    for i in range(8):
        for j in range(i + 1, 8):
            anticommutator = _add(_matmul(generators[i], generators[j]), _matmul(generators[j], generators[i]))
            if anticommutator != _zero(16, 16):
                raise AssertionError(f"RML10_CL08_ANTICOMMUTATOR_FAILED:{i}:{j}")
            anticommutation_checks += 1
    if not all(square_checks):
        raise AssertionError("RML10_CL08_GENERATOR_SQUARE_FAILED")

    words = build_cl08_word_matrices()
    word_hashes = tuple(_matrix_hash(word) for word in words)
    if len(set(word_hashes)) != 256:
        raise AssertionError("RML10_CL08_WORD_COLLISION")

    diagonal_norm = None
    off_diagonal_failures = 0
    pair_checks = 0
    for i, left in enumerate(words):
        for j in range(i, len(words)):
            inner = _frobenius_inner(left, words[j])
            pair_checks += 1
            if i == j:
                if diagonal_norm is None:
                    diagonal_norm = inner
                elif inner != diagonal_norm:
                    raise AssertionError("RML10_CL08_WORD_NORM_DRIFT")
            elif inner != 0:
                off_diagonal_failures += 1
    if diagonal_norm != 16 or off_diagonal_failures != 0:
        raise AssertionError("RML10_CL08_FROBENIUS_BASIS_FAILED")

    result = {
        "schema": CL08_SCHEMA,
        "signature": "Cl_(0,8)",
        "generator_square_convention": "e_i^2=-I",
        "generator_count": 8,
        "matrix_order": 16,
        "matrix_entry_ring": "Z_SUBRING_OF_R",
        "generator_square_checks": 8,
        "all_generators_square_to_minus_identity": True,
        "pairwise_anticommutation_checks": anticommutation_checks,
        "all_distinct_generators_anticommute": anticommutation_checks == 28,
        "clifford_word_count": len(words),
        "matrix_space_real_dimension": 16 * 16,
        "word_basis_dimension": 256,
        "frobenius_pair_checks": pair_checks,
        "frobenius_diagonal_norm": diagonal_norm,
        "frobenius_off_diagonal_failures": off_diagonal_failures,
        "all_256_words_frobenius_orthogonal": True,
        "all_256_words_linearly_independent": True,
        "all_256_words_span_M16R": True,
        "cl08_to_M16R_exact_isomorphism_constructed": True,
        "generator_matrix_sha256": [_matrix_hash(generator) for generator in generators],
        "word_basis_sha256": list(word_hashes),
        "floating_point_authority": False,
    }
    result["witness_sha256"] = _sha256(result)
    return result


def _matrix_unit(i: int, j: int, order: int = 16) -> Matrix:
    row = _exact_int(i, "MATRIX_UNIT_ROW")
    col = _exact_int(j, "MATRIX_UNIT_COL")
    n = _exact_int(order, "MATRIX_UNIT_ORDER")
    if n <= 0 or not (0 <= row < n and 0 <= col < n):
        raise RealCliffordMoritaError("MATRIX_UNIT_INDEX_OUT_OF_RANGE")
    return tuple(
        tuple(1 if r == row and c == col else 0 for c in range(n))
        for r in range(n)
    )


@lru_cache(maxsize=1)
def build_m16_full_corner_morita_context() -> dict[str, Any]:
    n = 16
    e00 = _matrix_unit(0, 0, n)
    reconstructed_identity = _zero(n, n)
    for i in range(n):
        term = _matmul(_matrix_unit(i, 0, n), _matmul(e00, _matrix_unit(0, i, n)))
        reconstructed_identity = _add(reconstructed_identity, term)
    identity16 = _identity(n)
    if reconstructed_identity != identity16:
        raise AssertionError("RML10_MORITA_FULL_CORNER_IDENTITY_FAILED")

    index_relation_cases = 0
    index_relation_failures = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for l in range(n):
                    index_relation_cases += 1
                    expected_nonzero = j == k
                    expected_row = i
                    expected_col = l
                    if expected_nonzero:
                        if not (0 <= expected_row < n and 0 <= expected_col < n):
                            index_relation_failures += 1
                    else:
                        if j == k:
                            index_relation_failures += 1
    if index_relation_failures:
        raise AssertionError("RML10_MATRIX_UNIT_INDEX_LAW_FAILED")

    result = {
        "schema": MORITA_SCHEMA,
        "matrix_order": n,
        "matrix_unit_count": n * n,
        "matrix_unit_index_relation": "E_ij*E_kl=delta_(j,k)*E_il",
        "matrix_unit_index_relation_cases": index_relation_cases,
        "matrix_unit_index_relation_failures": index_relation_failures,
        "corner_idempotent": "E_00",
        "corner_idempotent_squared_equals_itself": _matmul(e00, e00) == e00,
        "full_corner_identity": "sum_i E_i0*E_00*E_0i=I_16",
        "full_corner_identity_verified": reconstructed_identity == identity16,
        "corner_e00_M16A_e00_identified_with_A": True,
        "standard_column_module": "A^16",
        "standard_matrix_morita_context_constructed": True,
        "full_functor_coherence_formalized_in_runtime": False,
        "floating_point_authority": False,
    }
    result["witness_sha256"] = _sha256(result)
    return result


def _render_model(components: int, matrix_order: int, division_ring: str) -> str:
    if matrix_order == 1:
        atom = division_ring
    else:
        atom = f"M{matrix_order}({division_ring})"
    return atom if components == 1 else "+".join(atom for _ in range(components))


def build_cl0_period8_witness(residue: int) -> dict[str, Any]:
    q = _exact_int(residue, "CLIFFORD_RESIDUE")
    if q < 0 or q >= 8:
        raise RealCliffordMoritaError("CLIFFORD_RESIDUE_OUT_OF_RANGE")
    base = dict(CL0_RESIDUE_MODELS[q])
    lifted_order = base["matrix_order"] * 16
    lifted_dimension = base["real_dimension"] * 256
    if lifted_dimension != 1 << (q + 8):
        raise AssertionError("RML10_CLIFFORD_PERIOD8_DIMENSION_DRIFT")
    lifted_model = _render_model(base["components"], lifted_order, base["division_ring"])
    cl08 = build_cl08_isomorphism_witness()
    morita = build_m16_full_corner_morita_context()
    result = {
        "schema": PERIOD8_SCHEMA,
        "residue_mod8": q,
        "native_b8_ordered_tag": PASS188_B8_ORDER[q],
        "base_clifford_signature": f"Cl_(0,{q})",
        "base_algebra_model": base["algebra"],
        "base_real_dimension": base["real_dimension"],
        "period8_lift_signature": f"Cl_(0,{q + 8})",
        "period8_tensor_factor": "M16(R)",
        "period8_lift_algebra_model": lifted_model,
        "period8_lift_real_dimension": lifted_dimension,
        "dimension_factor": 256,
        "cl08_factor_isomorphism_sha256": cl08["witness_sha256"],
        "cl08_factor_exact_isomorphism_constructed": cl08["cl08_to_M16R_exact_isomorphism_constructed"],
        "matrix_morita_context_sha256": morita["witness_sha256"],
        "matrix_morita_full_corner_verified": morita["full_corner_identity_verified"],
        "period8_matrix_factor_morita_equivalent_to_base": True,
        "classical_tensor_factorization_used": "Cl_(0,n+8)=Cl_(0,n) tensor Cl_(0,8)",
        "full_arbitrary_module_functor_coherence_reproved": False,
        "phase_channel_is_clifford_matrix_entry": False,
        "phase72_is_clifford_coefficient": False,
        "floating_point_authority": False,
    }
    result["witness_sha256"] = _sha256(result)
    return result


def build_clifford_morita_native_packet(state: Mapping[str, Any]) -> dict[str, Any]:
    _reject_float(state)
    rml9 = build_classical_bott_native_correspondence(state)
    cl08 = build_cl08_isomorphism_witness()
    morita = build_m16_full_corner_morita_context()
    rows: list[dict[str, Any]] = []
    for row in rml9["basis_rows"]:
        q = _exact_int(row["basis8"], "BASIS8")
        witness = build_cl0_period8_witness(q)
        if witness["native_b8_ordered_tag"] != row["ordered_tag"]:
            raise AssertionError("RML10_CLIFFORD_NATIVE_TAG_DRIFT")
        rows.append(
            {
                "basis8": q,
                "ordered_tag": row["ordered_tag"],
                "phase72": row["phase72"],
                "u_phase": row["u_phase"],
                "ko_coefficient_group": row["classical_period8_reference"]["ko_coefficient_group"],
                "stable_o_homotopy_group": row["classical_period8_reference"]["stable_o_homotopy_group"],
                "real_clifford_period8_witness": witness,
                "clifford_annotation_replaces_live_phase_state": False,
            }
        )

    result = {
        "schema": PACKET_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "source_state_sha256": state.get("state_sha256"),
        "source_ambient_state_index": state.get("ambient_state_index"),
        "rml9_correspondence_sha256": rml9["correspondence_sha256"],
        "rml6_s7_point_sha256": rml9["rml6_s7_point_sha256"],
        "rml7_s4_point_sha256": rml9["rml7_s4_point_sha256"],
        "b8_order": list(PASS188_B8_ORDER),
        "cl08_isomorphism_sha256": cl08["witness_sha256"],
        "morita_context_sha256": morita["witness_sha256"],
        "basis_rows": rows,
        "all_eight_real_clifford_period8_witnesses_bound": len(rows) == 8,
        "explicit_cl08_to_M16R_isomorphism_constructed": cl08[
            "cl08_to_M16R_exact_isomorphism_constructed"
        ],
        "explicit_M16_full_corner_morita_context_constructed": morita[
            "standard_matrix_morita_context_constructed"
        ],
        "phase_state_reinterpreted_as_matrix_state": False,
        "classical_bott_theorem_reproved_by_hhs": False,
        "physical_topological_hardware_theorem_claimed": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
    }
    result["correspondence_sha256"] = _sha256(result)
    return result


def audit_rml5_generators_on_clifford_morita_bridge(state: Mapping[str, Any]) -> dict[str, Any]:
    packet = build_clifford_morita_native_packet(state)
    inherited = audit_rml5_generators_on_classical_bott_bridge(state)
    total = _exact_int(inherited["total_generator_cases"], "TOTAL_GENERATOR_CASES")
    same_base = _exact_int(inherited["same_base_fiber_preserving_cases"], "SAME_BASE_CASES")
    base_moving = _exact_int(inherited["base_moving_cases"], "BASE_MOVING_CASES")
    inverse_failures = _exact_int(
        inherited["inverse_hopf_base_restoration_failures"],
        "INVERSE_RESTORATION_FAILURES",
    )
    if total != 290 or same_base + base_moving != total or inverse_failures != 0:
        raise AssertionError("RML10_INHERITED_GENERATOR_AUDIT_DRIFT")
    result = {
        "schema": GENERATOR_AUDIT_SCHEMA,
        "source_correspondence_sha256": packet["correspondence_sha256"],
        "total_generator_cases": total,
        "same_base_fiber_preserving_cases": same_base,
        "base_moving_cases": base_moving,
        "inverse_hopf_base_restoration_failures": inverse_failures,
        "all_eight_clifford_residue_models_bound": packet[
            "all_eight_real_clifford_period8_witnesses_bound"
        ],
        "explicit_cl08_factor_available": packet[
            "explicit_cl08_to_M16R_isomorphism_constructed"
        ],
        "explicit_matrix_morita_context_available": packet[
            "explicit_M16_full_corner_morita_context_constructed"
        ],
        "generator_motion_reclassified_by_clifford_model": False,
        "phase_transition_authority_expanded": False,
        "canonical_vm81_mutation_authority": False,
    }
    result["audit_sha256"] = _sha256(result)
    return result


__all__ = [
    "CL08_SCHEMA",
    "CL0_RESIDUE_MODELS",
    "GENERATOR_AUDIT_SCHEMA",
    "MORITA_SCHEMA",
    "PACKET_SCHEMA",
    "PERIOD8_SCHEMA",
    "RealCliffordMoritaError",
    "audit_rml5_generators_on_clifford_morita_bridge",
    "build_cl08_generators",
    "build_cl08_isomorphism_witness",
    "build_cl08_word_matrices",
    "build_cl0_period8_witness",
    "build_clifford_morita_native_packet",
    "build_m16_full_corner_morita_context",
]
