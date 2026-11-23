"""Pass 220 I086: non-authoritative HNAN perimeter topology witness.

This module studies the address projection only. It never advances VM81,
executes the center gate, mints Hash72 or persists Hash216.
"""
from __future__ import annotations

from hashlib import sha256
import json

from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    HNAN_LO_SHU_TENSOR, HNAN_NUMERATOR, XY, YX, ZW, WZ,
)

SCHEMA = "HHS_PASS220_I086_HNAN_PERIMETER_TOPOLOGY_V1"
ADDRESS_MATRIX = (
    ("000", "001", "010"),
    ("011", "HNAN", "100"),
    ("101", "110", "111"),
)
LO_SHU_MATRIX = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
PERIMETER = ("000", "001", "010", "100", "111", "110", "101", "011")


def perimeter_step(address: str) -> str:
    """Apply the illustrative oriented address permutation, never VM81."""
    if type(address) is not str or address not in PERIMETER:
        raise ValueError("address is not an admitted perimeter address")
    return PERIMETER[(PERIMETER.index(address) + 1) % len(PERIMETER)]


def perimeter_orbit(address: str, steps: int) -> tuple[str, ...]:
    if type(steps) is not int or steps < 0:
        raise ValueError("steps must be a nonnegative exact integer")
    if type(address) is not str or address not in PERIMETER:
        raise ValueError("address is not an admitted perimeter address")
    orbit = [address]
    for _ in range(steps):
        orbit.append(perimeter_step(orbit[-1]))
    return tuple(orbit)


def topology_receipt() -> dict:
    tensor = HNAN_LO_SHU_TENSOR
    flat = tuple(cell for row in ADDRESS_MATRIX for cell in row)
    edges = tuple((address, perimeter_step(address)) for address in PERIMETER)
    checks = {
        "addresses_unique": len(flat) == len(set(flat)) == 9,
        "center_address_unchanged": ADDRESS_MATRIX[1][1] == "HNAN",
        "center_uses_inherited_gate": tensor[1][1] == HNAN_NUMERATOR,
        "perimeter_exactly_outer_eight": set(PERIMETER) == set(flat) - {"HNAN"},
        "degree_two_unoriented": all(
            sum(a == v or b == v for a, b in edges) == 2 for v in PERIMETER
        ),
        "period_eight": all(
            perimeter_orbit(v, 8)[-1] == v and
            all(perimeter_orbit(v, n)[-1] != v for n in range(1, 8))
            for v in PERIMETER
        ),
        "loshu_rows": all(sum(row) == 15 for row in LO_SHU_MATRIX),
        "loshu_columns": all(sum(row[i] for row in LO_SHU_MATRIX) == 15 for i in range(3)),
        "loshu_diagonals": (
            sum(LO_SHU_MATRIX[i][i] for i in range(3)) == 15 and
            sum(LO_SHU_MATRIX[i][2-i] for i in range(3)) == 15
        ),
        "ordered_xy_yx_unchanged": tensor[0][0] == XY and tensor[0][2] == YX and XY != YX,
        "ordered_zw_wz_unchanged": tensor[2][2] == ZW and tensor[2][0] == WZ and ZW != WZ,
    }
    receipt = {
        "schema": SCHEMA,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "addresses": ADDRESS_MATRIX,
        "loshu": LO_SHU_MATRIX,
        "directed_edges": edges,
        "projection_period": 8,
        "phase_period_verified": False,
        "vm81_state_period_verified": False,
        "native_admission_verified": False,
        "canonical_vm81_mutation_authority": False,
        "hash72_mint_authority": False,
        "hash216_persistence_authority": False,
    }
    receipt["receipt_sha256"] = sha256(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return receipt
