"""Pass 219 Lane 5 Genesis orientation/U9/Qe proof bridge.

Read-only proof composition over existing repository authority.

This module does not:
- scalarize the native x/y/z/w tensor;
- identify the native Eigenvector-0 tensor with the conventional Fourier k=0 vector;
- grant VM81/Hash72/Hash216 mutation authority;
- choose Qe when surrounding constraints leave more than one admissible exponent.

The repository-authoritative finite construction used here is:

    3*24 = 72 phase-cover positions
    72+9 = 81 with the retained nine-cell Genesis/Lo-Shu nucleus
    81*64 = 5184 = 72^2

The nine-position U9 operator is consumed only as an address-orbit permutation.
A complete nine-step orbit returns the full ordered tensor object.  One-step
Fourier eigenvector substitution is not inferred.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Iterable, Sequence

from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import (
    MACROCYCLE_ORDER,
    macrocycle_permutation,
    permutation_power,
)

SCHEMA = "HHS_PASS219_LANE5_GENESIS_ORIENTATION_U9_QE_BRIDGE_V1"
VERSION = "1.0.0-cycle3"

CENTERED_LO_SHU = (
    (-1, 4, -3),
    (-2, 0, 2),
    (3, -4, 1),
)

EIGENVECTOR0_TENSOR = (
    ("xy", "x+y", "yx"),
    ("xy-zw", "x+y-z-w+xy+yx-zw-wz", "wz-yx"),
    ("wz", "z+w", "zw"),
)

ORIENTATION_TABLE = (
    (-1, 1, -1),
    (-1, 0, 1),
    (1, -1, 1),
)

MAGNITUDE_TABLE = (
    (1, 4, 3),
    (2, 0, 2),
    (3, 4, 1),
)

PHASE_COVER_POSITIONS = 72
GENESIS_NUCLEUS_CELLS = 9
VM81_CELLS = 81
OPERATION64 = 64
VM5184 = 5184


class Lane5GenesisBridgeError(ValueError):
    pass


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    core = dict(payload)
    core["receipt_sha256"] = sha256(_stable(core).encode("utf-8")).hexdigest()
    return core


def _flatten(matrix: Sequence[Sequence[Any]]) -> tuple[Any, ...]:
    return tuple(value for row in matrix for value in row)


def _rotate180(matrix: Sequence[Sequence[Any]]) -> tuple[tuple[Any, ...], ...]:
    rows = tuple(tuple(row) for row in matrix)
    return tuple(tuple(reversed(row)) for row in reversed(rows))


def _sign(value: int) -> int:
    return -1 if value < 0 else (1 if value > 0 else 0)


def orientation_table() -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(_sign(value) for value in row) for row in CENTERED_LO_SHU)


def magnitude_table() -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(abs(value) for value in row) for row in CENTERED_LO_SHU)


def apply_permutation(
    values: Sequence[Any],
    permutation: Sequence[int],
) -> tuple[Any, ...]:
    """Apply the repository permutation convention to an ordered value tuple.

    The Pass 220 convention is: column j maps to row permutation[j].
    """
    source = tuple(values)
    perm = tuple(permutation)
    if len(source) != len(perm):
        raise Lane5GenesisBridgeError("value/permutation cardinality mismatch")
    expected = set(range(1, len(perm) + 1))
    if set(perm) != expected:
        raise Lane5GenesisBridgeError("invalid exact permutation")
    output: list[Any] = [None] * len(source)
    for column, row in enumerate(perm, start=1):
        output[row - 1] = source[column - 1]
    return tuple(output)


def u9_tensor_orbit() -> tuple[tuple[str, ...], ...]:
    tensor = _flatten(EIGENVECTOR0_TENSOR)
    permutation = macrocycle_permutation()
    states = [tensor]
    current = tensor
    for _ in range(MACROCYCLE_ORDER):
        current = apply_permutation(current, permutation)
        states.append(current)
    return tuple(states)


def qe_admissible_class(
    numerator: int,
    denominator: int,
    target_residue: int,
    candidate_exponents: Iterable[int],
) -> tuple[int, ...]:
    """Return Qe values admitted by the supplied modular projection constraint.

    Native slash is represented only at its already-declared residue surface:

        N/D := D mod N^Qe

    This helper does not decide the rest of the tensor normalization predicate.
    The caller supplies the candidate set already surviving surrounding
    tensor/path constraints.
    """
    if isinstance(numerator, bool) or not isinstance(numerator, int):
        raise Lane5GenesisBridgeError("numerator must be an exact integer")
    if isinstance(denominator, bool) or not isinstance(denominator, int):
        raise Lane5GenesisBridgeError("denominator must be an exact integer")
    if isinstance(target_residue, bool) or not isinstance(target_residue, int):
        raise Lane5GenesisBridgeError("target residue must be an exact integer")
    if numerator <= 0:
        raise Lane5GenesisBridgeError("positive numerator/modulus base required")

    candidates = tuple(candidate_exponents)
    if not candidates:
        raise Lane5GenesisBridgeError("candidate Qe set must be nonempty")
    if any(
        isinstance(q, bool) or not isinstance(q, int) or q < 1
        for q in candidates
    ):
        raise Lane5GenesisBridgeError(
            "candidate Qe values must be positive exact integers"
        )

    return tuple(
        q
        for q in candidates
        if denominator % (numerator**q) == target_residue
    )


def qe_constraint_receipt(
    numerator: int,
    denominator: int,
    target_residue: int,
    candidate_exponents: Iterable[int],
) -> dict[str, Any]:
    candidates = tuple(candidate_exponents)
    admitted = qe_admissible_class(
        numerator,
        denominator,
        target_residue,
        candidates,
    )
    unique = len(admitted) == 1
    return _receipt(
        {
            "schema": "HHS_PASS219_QE_CONSTRAINT_SELECTION_RECEIPT_V1",
            "native_slash_surface": "D mod N^Qe",
            "numerator": numerator,
            "denominator": denominator,
            "target_residue": target_residue,
            "candidate_exponents": list(candidates),
            "admissible_qe": list(admitted),
            "decision": "COMMIT" if unique else "UNRESOLVED",
            "selected_qe": admitted[0] if unique else None,
            "qe_is_free_parameter": False,
            "surrounding_tensor_constraints_required": True,
            "canonical_mutation_authority": False,
        }
    )


def genesis_projection_witness() -> dict[str, Any]:
    flat_loshu = _flatten(CENTERED_LO_SHU)
    flat_tensor = _flatten(EIGENVECTOR0_TENSOR)
    orbit = u9_tensor_orbit()
    permutation = macrocycle_permutation()

    reciprocal_pairs = (
        ((0, 0), (2, 2), "xy", "zw", -1, 1),
        ((0, 1), (2, 1), "x+y", "z+w", 4, -4),
        ((0, 2), (2, 0), "yx", "wz", -3, 3),
        ((1, 0), (1, 2), "xy-zw", "wz-yx", -2, 2),
    )

    checks = {
        "loshu_offset_alphabet_exact": tuple(sorted(flat_loshu))
        == tuple(range(-4, 5)),
        "loshu_zero_total": sum(flat_loshu) == 0,
        "loshu_rows_zero": all(sum(row) == 0 for row in CENTERED_LO_SHU),
        "loshu_columns_zero": all(
            sum(CENTERED_LO_SHU[row][column] for row in range(3)) == 0
            for column in range(3)
        ),
        "loshu_diagonals_zero": (
            sum(CENTERED_LO_SHU[i][i] for i in range(3)) == 0
            and sum(CENTERED_LO_SHU[i][2 - i] for i in range(3)) == 0
        ),
        "orientation_table_exact": orientation_table() == ORIENTATION_TABLE,
        "magnitude_table_exact": magnitude_table() == MAGNITUDE_TABLE,
        "scalar_180_reciprocity": _rotate180(CENTERED_LO_SHU)
        == tuple(tuple(-value for value in row) for row in CENTERED_LO_SHU),
        "center_is_lock_expression": EIGENVECTOR0_TENSOR[1][1]
        == "x+y-z-w+xy+yx-zw-wz",
        "reciprocal_position_pairs_exact": all(
            EIGENVECTOR0_TENSOR[a[0]][a[1]] == left
            and EIGENVECTOR0_TENSOR[b[0]][b[1]] == right
            and CENTERED_LO_SHU[a[0]][a[1]] == left_scalar
            and CENTERED_LO_SHU[b[0]][b[1]] == right_scalar
            and left_scalar == -right_scalar
            for a, b, left, right, left_scalar, right_scalar
            in reciprocal_pairs
        ),
        "vm81_72_plus_9": PHASE_COVER_POSITIONS + GENESIS_NUCLEUS_CELLS
        == VM81_CELLS,
        "vm5184_crosswalk": VM81_CELLS * OPERATION64
        == 72**2
        == VM5184,
        "u9_is_nine_cycle": permutation_power(
            permutation, MACROCYCLE_ORDER
        ) == tuple(range(1, MACROCYCLE_ORDER + 1)),
        "u9_full_orbit_returns_tensor": orbit[-1] == flat_tensor,
        "u9_visits_nine_distinct_address_states": len(set(orbit[:-1]))
        == MACROCYCLE_ORDER,
        "u9_one_step_not_identity_on_tensor_positions": orbit[1] != flat_tensor,
    }

    return _receipt(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
            "native_eigenvector0": [
                list(row) for row in EIGENVECTOR0_TENSOR
            ],
            "centered_loshu": [list(row) for row in CENTERED_LO_SHU],
            "orientation_table": [list(row) for row in ORIENTATION_TABLE],
            "magnitude_table": [list(row) for row in MAGNITUDE_TABLE],
            "vm81_construction": {
                "phase_cover_positions": PHASE_COVER_POSITIONS,
                "genesis_nucleus_cells": GENESIS_NUCLEUS_CELLS,
                "vm81_cells": VM81_CELLS,
                "rule": "72+9=81",
                "kronecker_scalar_construction_authority": False,
            },
            "u9": {
                "role": (
                    "address-orbit permutation over nine tensor positions"
                ),
                "permutation": list(permutation),
                "full_orbit_closes": orbit[-1] == flat_tensor,
                "one_step_scalar_eigenclaim": False,
                "conventional_fourier_mode_substitution_authorized": False,
            },
            "projection_policy": {
                "orientation_is_state_bearing": True,
                "flat_scalar_substitution_authorized": False,
                "scalar_projection_requires_admitted_pipeline": True,
            },
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
        }
    )


def self_test() -> dict[str, Any]:
    result = genesis_projection_witness()
    if result["status"] != "PASS":
        raise Lane5GenesisBridgeError("Genesis bridge self-test failed")

    qe_unique = qe_constraint_receipt(2, 2, 0, range(1, 9))
    if qe_unique["decision"] != "COMMIT" or qe_unique["selected_qe"] != 1:
        raise Lane5GenesisBridgeError("unique Qe selection self-test failed")

    qe_ambiguous = qe_constraint_receipt(2, 2, 2, range(1, 9))
    if qe_ambiguous["decision"] != "UNRESOLVED":
        raise Lane5GenesisBridgeError("ambiguous Qe must fail closed")

    return {
        "schema": "HHS_PASS219_LANE5_GENESIS_ORIENTATION_U9_QE_SELF_TEST_V1",
        "status": "PASS",
        "genesis_receipt_sha256": result["receipt_sha256"],
        "qe_unique_receipt_sha256": qe_unique["receipt_sha256"],
        "qe_ambiguous_receipt_sha256": qe_ambiguous["receipt_sha256"],
    }


if __name__ == "__main__":
    print(_stable(self_test()))
