"""Exact phase-root and qutrit operator witnesses for ERS V2 Lane 5.

All calculations are exact integer/cyclotomic witnesses. They are immutable
candidate evidence and never perform a VM81 transition or mint Hash72.
"""
from __future__ import annotations

from typing import Any

ROOT_COUNT = 72
POLARITY_SECTORS = 4
OMEGA_POWER = 24
X3 = ((0, 0, 1), (1, 0, 0), (0, 1, 0))


def _root_index(k: int) -> int:
    if isinstance(k, bool) or not isinstance(k, int) or not 0 <= k < ROOT_COUNT:
        raise ValueError("root address must be an exact integer in [0,71]")
    return k


def phase_root_witness(k: int) -> dict[str, Any]:
    """u_k=exp(2*pi*i*k/72); represent powers by residues, not floats.

    The primitive carrier u=u_1 satisfies u^36=-1. Other admitted
    root addresses can have u_k^36=+1 or -1; the branch is retained.
    """
    _root_index(k)
    u36_sign = 1 if k % 2 == 0 else -1
    return {
        "root_index": k,
        "root_count": ROOT_COUNT,
        "u72_exponent_mod72": (72 * k) % 72,
        "u36_sign": u36_sign,
        "u_minus180_exponent_mod72": (-180 * k) % 72,
        "u_minus180_sign": u36_sign,
        "u_minus180_equals_one": u36_sign == 1,
        "u36_equals_one": u36_sign == 1,
        "primitive_root": k == 1 or k in tuple(
            j for j in range(1, ROOT_COUNT) if _coprime(j, ROOT_COUNT)
        ),
        "vm81_admission": False,
    }


def _coprime(a: int, b: int) -> bool:
    while b:
        a, b = b, a % b
    return a == 1


def phase_address(k: int, sector: int) -> dict[str, int]:
    _root_index(k)
    if isinstance(sector, bool) or not isinstance(sector, int) or not 0 <= sector < POLARITY_SECTORS:
        raise ValueError("sector address must be exact integer in [0,3]")
    return {"root": k, "sector": sector, "linear_address": sector * ROOT_COUNT + k}


def _omega_power(exponent: int) -> tuple[int, int]:
    """Coefficient pair in exact Z[omega], omega^2=-1-omega."""
    return ((1, 0), (0, 1), (-1, -1))[exponent % 3]


def z3_operator() -> tuple[tuple[int | None, ...], ...]:
    """Diagonal phase exponents; None means exact matrix zero."""
    return ((0, None, None), (None, 1, None), (None, None, 2))


def exact_qutrit_projector() -> dict[str, Any]:
    """(I + Z3 + Z3²)/3, with omega³=1, 1+omega+omega²=0."""
    numerators = []
    diagonals = []
    for j in range(3):
        a = b = 0
        for power in range(3):
            da, db = _omega_power(j * power)
            a += da
            b += db
        numerators.append((a, b))
        if b or a % 3:
            raise AssertionError("projector not integral in Z[omega]")
        diagonals.append(a // 3)
    matrix = tuple(
        tuple(diagonals[i] if i == j else 0 for j in range(3))
        for i in range(3)
    )
    return {
        "X3": X3,
        "Z3_diagonal_root_exponents": (0, OMEGA_POWER, 2 * OMEGA_POWER),
        "Z3_projector_numerators": tuple(numerators),
        "Pi_collapse": matrix,
        "Pi_squared_equals_Pi": all(value in (0, 1) for value in diagonals),
        "projector_nonzero_norm_required": True,
        "vm81_admission": False,
    }
