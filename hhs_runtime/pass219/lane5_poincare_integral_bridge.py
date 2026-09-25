"""Pass 219 Lane 5 T_BRIDGE-01A Poincare integral-invariant bridge.

Exact rational executable companion to the connected Wolfram proof.

State order:
    (q1, q2, p1, p2)

Canonical symplectic form:
    Omega = [[0, I], [-I, 0]]

For a separable Hamiltonian with symmetric inverse-mass matrix A and symmetric
potential Hessian B, the two exact subflows are represented by

    K_h = [[I, 0], [-h B, I]]
    D_h = [[I, h A], [0, I]]

The carried kick->drift map is Phi_h = D_h K_h.

This module checks exact rational matrix identities only.  It does not claim:
- exact Hamiltonian/energy conservation;
- T_BRIDGE-01B long-time energy-band/class stability;
- canonical VM81/Hash72/Hash216 mutation authority.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Iterable, Sequence

SCHEMA = "HHS_PASS219_T_BRIDGE_01A_POINCARE_INVARIANT_V1"
STATE_ORDER = ("q1", "q2", "p1", "p2")

Q = Fraction
Matrix = tuple[tuple[Fraction, ...], ...]


class PoincareBridgeError(ValueError):
    pass


def _q(value: int | Fraction, name: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise PoincareBridgeError(f"{name} must be an exact int/Fraction")
    return Fraction(value)


def _matrix(
    values: Sequence[Sequence[int | Fraction]],
    name: str,
) -> Matrix:
    rows = tuple(tuple(_q(v, name) for v in row) for row in values)
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        raise PoincareBridgeError(f"{name} must be a nonempty rectangular matrix")
    return rows


def _shape(m: Matrix) -> tuple[int, int]:
    return len(m), len(m[0])


def _identity(n: int) -> Matrix:
    return tuple(
        tuple(Fraction(int(i == j)) for j in range(n))
        for i in range(n)
    )


def _zero(rows: int, cols: int) -> Matrix:
    return tuple(tuple(Fraction(0) for _ in range(cols)) for _ in range(rows))


def _add(left: Matrix, right: Matrix) -> Matrix:
    if _shape(left) != _shape(right):
        raise PoincareBridgeError("matrix add shape mismatch")
    return tuple(
        tuple(a + b for a, b in zip(lrow, rrow))
        for lrow, rrow in zip(left, right)
    )


def _sub(left: Matrix, right: Matrix) -> Matrix:
    if _shape(left) != _shape(right):
        raise PoincareBridgeError("matrix subtract shape mismatch")
    return tuple(
        tuple(a - b for a, b in zip(lrow, rrow))
        for lrow, rrow in zip(left, right)
    )


def _scale(scalar: Fraction, m: Matrix) -> Matrix:
    return tuple(tuple(scalar * value for value in row) for row in m)


def _transpose(m: Matrix) -> Matrix:
    rows, cols = _shape(m)
    return tuple(tuple(m[i][j] for i in range(rows)) for j in range(cols))


def _mul(left: Matrix, right: Matrix) -> Matrix:
    lr, lc = _shape(left)
    rr, rc = _shape(right)
    if lc != rr:
        raise PoincareBridgeError("matrix multiply shape mismatch")
    return tuple(
        tuple(
            sum((left[i][k] * right[k][j] for k in range(lc)), Fraction(0))
            for j in range(rc)
        )
        for i in range(lr)
    )


def _block(
    a: Matrix,
    b: Matrix,
    c: Matrix,
    d: Matrix,
) -> Matrix:
    ar, ac = _shape(a)
    br, bc = _shape(b)
    cr, cc = _shape(c)
    dr, dc = _shape(d)
    if ar != br or cr != dr or ac != cc or bc != dc:
        raise PoincareBridgeError("invalid block matrix dimensions")
    top = tuple(a[i] + b[i] for i in range(ar))
    bottom = tuple(c[i] + d[i] for i in range(cr))
    return top + bottom


def _det(m: Matrix) -> Fraction:
    n, cols = _shape(m)
    if n != cols:
        raise PoincareBridgeError("determinant requires square matrix")
    a = [list(row) for row in m]
    sign = 1
    determinant = Fraction(1)
    for col in range(n):
        pivot = next((row for row in range(col, n) if a[row][col] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            sign *= -1
        pivot_value = a[col][col]
        determinant *= pivot_value
        for row in range(col + 1, n):
            if a[row][col] == 0:
                continue
            factor = a[row][col] / pivot_value
            for k in range(col, n):
                a[row][k] -= factor * a[col][k]
    return determinant * sign


def _is_symmetric(m: Matrix) -> bool:
    return m == _transpose(m)


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _fraction_data(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def _matrix_data(m: Matrix) -> list[list[list[int]]]:
    return [[_fraction_data(value) for value in row] for row in m]


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    encoded = _stable(payload).encode("utf-8")
    return {**payload, "receipt_sha256": sha256(encoded).hexdigest()}


def canonical_omega(dof: int = 2) -> Matrix:
    if isinstance(dof, bool) or not isinstance(dof, int) or dof <= 0:
        raise PoincareBridgeError("dof must be a positive exact integer")
    identity = _identity(dof)
    zero = _zero(dof, dof)
    return _block(zero, identity, _scale(Fraction(-1), identity), zero)


def _validate_symmetric_2x2(
    value: Sequence[Sequence[int | Fraction]],
    name: str,
) -> Matrix:
    m = _matrix(value, name)
    if _shape(m) != (2, 2):
        raise PoincareBridgeError(f"{name} must be exactly 2x2")
    if not _is_symmetric(m):
        raise PoincareBridgeError(f"{name} must be symmetric")
    return m


def kick_matrix(
    h: int | Fraction,
    hessian: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    step = _q(h, "h")
    b = _validate_symmetric_2x2(hessian, "hessian")
    identity = _identity(2)
    zero = _zero(2, 2)
    return _block(identity, zero, _scale(-step, b), identity)


def drift_matrix(
    h: int | Fraction,
    inverse_mass: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    step = _q(h, "h")
    a = _validate_symmetric_2x2(inverse_mass, "inverse_mass")
    identity = _identity(2)
    zero = _zero(2, 2)
    return _block(identity, _scale(step, a), zero, identity)


def carried_kick_drift(
    h: int | Fraction,
    inverse_mass: Sequence[Sequence[int | Fraction]],
    hessian: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    return _mul(
        drift_matrix(h, inverse_mass),
        kick_matrix(h, hessian),
    )


def reverse_drift_kick(
    h: int | Fraction,
    inverse_mass: Sequence[Sequence[int | Fraction]],
    hessian: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    return _mul(
        kick_matrix(h, hessian),
        drift_matrix(h, inverse_mass),
    )


def simultaneous_old_state_euler(
    h: int | Fraction,
    inverse_mass: Sequence[Sequence[int | Fraction]],
    hessian: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    step = _q(h, "h")
    a = _validate_symmetric_2x2(inverse_mass, "inverse_mass")
    b = _validate_symmetric_2x2(hessian, "hessian")
    identity = _identity(2)
    return _block(
        identity,
        _scale(step, a),
        _scale(-step, b),
        identity,
    )


def symplectic_defect(matrix: Matrix) -> Matrix:
    m = _matrix(matrix, "matrix")
    if _shape(m) != (4, 4):
        raise PoincareBridgeError("symplectic check requires 4x4 matrix")
    omega = canonical_omega(2)
    return _sub(_mul(_mul(_transpose(m), omega), m), omega)


def is_symplectic(matrix: Matrix) -> bool:
    return symplectic_defect(matrix) == _zero(4, 4)


def volume_only_witness() -> Matrix:
    # det=1 but pair scalings (q1,p1) and (q2,p2) do not individually pair to 1.
    return (
        (Fraction(2), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0), Fraction(1, 2)),
    )


def poincare_bridge_receipt(
    *,
    h: int | Fraction,
    inverse_mass: Sequence[Sequence[int | Fraction]],
    hessian: Sequence[Sequence[int | Fraction]],
) -> dict[str, Any]:
    step = _q(h, "h")
    a = _validate_symmetric_2x2(inverse_mass, "inverse_mass")
    b = _validate_symmetric_2x2(hessian, "hessian")

    kick = kick_matrix(step, b)
    drift = drift_matrix(step, a)
    carried = carried_kick_drift(step, a, b)
    reverse = reverse_drift_kick(step, a, b)
    explicit = simultaneous_old_state_euler(step, a, b)
    volume_only = volume_only_witness()

    checks = {
        "kick_symplectic": is_symplectic(kick),
        "drift_symplectic": is_symplectic(drift),
        "carried_symplectic": is_symplectic(carried),
        "reverse_sequential_symplectic": is_symplectic(reverse),
        "sequential_orders_distinct": carried != reverse,
        "carried_det_one": _det(carried) == 1,
        "reverse_det_one": _det(reverse) == 1,
        "explicit_not_symplectic": not is_symplectic(explicit),
        "volume_only_det_one": _det(volume_only) == 1,
        "volume_only_not_symplectic": not is_symplectic(volume_only),
    }

    return _receipt(
        {
            "schema": SCHEMA,
            "status": "PASS" if all(checks.values()) else "FAIL",
            "state_order": list(STATE_ORDER),
            "step": _fraction_data(step),
            "inverse_mass": _matrix_data(a),
            "hessian": _matrix_data(b),
            "omega": _matrix_data(canonical_omega(2)),
            "checks": checks,
            "carried_map": _matrix_data(carried),
            "reverse_sequential_map": _matrix_data(reverse),
            "simultaneous_old_state_map": _matrix_data(explicit),
            "poincare_integral_invariant": (
                "Phi^*(sum_i dq_i wedge dp_i)=sum_i dq_i wedge dp_i"
            ),
            "four_d_projection_reading": (
                "oriented A1+A2 invariant; individual Ai may exchange"
            ),
            "volume_only_is_insufficient": True,
            "both_sequential_orders_symplectic": True,
            "simultaneous_old_state_explicit_symplectic": False,
            "exact_energy_conservation_claimed": False,
            "t_bridge_01b_energy_band_class_stability": "OPEN",
            "canonical_runtime_mutation_authority": False,
        }
    )


def self_test() -> dict[str, Any]:
    result = poincare_bridge_receipt(
        h=Fraction(1, 4),
        inverse_mass=((1, 0), (0, 1)),
        hessian=((2, 1), (1, 3)),
    )
    if result["status"] != "PASS":
        raise PoincareBridgeError("Poincare bridge self-test failed")
    return {
        "schema": "HHS_PASS219_T_BRIDGE_01A_POINCARE_SELF_TEST_V1",
        "status": "PASS",
        "receipt_sha256": result["receipt_sha256"],
    }


if __name__ == "__main__":
    print(_stable(self_test()))
