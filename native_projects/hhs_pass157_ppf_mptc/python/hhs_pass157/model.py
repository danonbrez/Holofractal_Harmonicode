from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .parser import hash216

LO_SHU = (4, 9, 2, 3, 5, 7, 8, 1, 6)
CENTERLINE_LABELS = ("x+y", "zw", "x", "z", "yx", "wz", "y", "w", "xy", "b^2", "c^2")


def phase_decompose(n: int, modulus: int) -> tuple[int, int]:
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    q, r = divmod(n, modulus)
    assert n == q * modulus + r and 0 <= r < modulus
    return q, r


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("negative Fibonacci index")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def plastic_mul(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    k = [0] * 5
    for i, left in enumerate(a):
        for j, right in enumerate(b):
            k[i + j] += left * right
    return k[0] + k[3], k[1] + k[3] + k[4], k[2] + k[4]


def plastic_power(exponent: int) -> tuple[int, int, int]:
    if exponent < 0:
        raise ValueError("negative plastic exponent requires explicit inverse domain")
    acc = (1, 0, 0)
    factor = (0, 1, 0)
    while exponent:
        if exponent & 1:
            acc = plastic_mul(acc, factor)
        exponent >>= 1
        if exponent:
            factor = plastic_mul(factor, factor)
    return acc


def pythagorean(m: int, n: int) -> tuple[int, int, int]:
    if not (m > n > 0):
        raise ValueError("require m > n > 0")
    a, b, c = m * m - n * n, 2 * m * n, m * m + n * n
    if a * a + b * b != c * c:
        raise ArithmeticError("Pythagorean closure failed")
    return a, b, c


def polynomial_component(digit: int, a: int, b: int, c: int) -> int:
    a2, b2, c2 = a * a, b * b, c * c
    mapping = {
        1: a2,
        2: b2,
        3: c2,
        4: b2 * b2,
        5: b2 + c2,
        6: b2 * c2,
        7: c2 + b2 * b2,
        8: (b2 * b2) ** 2,
        9: c2 * c2,
    }
    return mapping[digit]


@dataclass(frozen=True)
class PhaseLane:
    modulus: int
    quotient: int
    residue: int


@dataclass(frozen=True)
class TensorCell:
    lo_shu_digit: int
    phase_lane: int
    polynomial_component: int
    fibonacci_component: int
    plastic_component: tuple[int, int, int]
    phase_residue: int
    combined_scalar: int


@dataclass(frozen=True)
class ExactTensor:
    P2: int
    P4: int
    A: int
    B: int
    pq: int
    Delta: int
    xy: int
    yx: int
    pythagorean: tuple[int, int, int]
    local_phase: PhaseLane
    orthogonal_phase: tuple[PhaseLane, PhaseLane, PhaseLane]
    centerline: tuple[tuple[str, int], ...]
    tensor: tuple[TensorCell, ...]
    vm81_cells: tuple[int, ...]
    tensor_hash216: str
    vm81_hash216: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def construct_exact(
    *, P: int, p: int, q: int, euclid_m: int, euclid_n: int,
    full_rotation: int, local_modulus: int, centerline: tuple[int, ...],
) -> ExactTensor:
    if P == 0:
        raise ValueError("P must be nonzero")
    if len(centerline) != len(CENTERLINE_LABELS):
        raise ValueError("centerline requires eleven values")
    if any(left >= right for left, right in zip(centerline, centerline[1:])):
        raise ValueError("centerline ordering mismatch")
    P2 = P * P
    P4 = P2 * P2
    A = B = xy = yx = P2
    pq = p * q
    Delta = P2 - pq
    if A * B != P4:
        raise ArithmeticError("AB=P^4 mismatch")
    triple = pythagorean(euclid_m, euclid_n)
    local_q, local_r = phase_decompose(full_rotation, local_modulus)
    local = PhaseLane(local_modulus, local_q, local_r)
    H = abs(P2)
    orthogonal = tuple(
        PhaseLane(modulus, *phase_decompose(full_rotation, modulus))
        for modulus in (4 * H, 7 * H, 11 * H)
    )
    cells: list[TensorCell] = []
    for digit in LO_SHU:
        lane_index = (digit - 1) % 3
        polynomial = polynomial_component(digit, *triple)
        fib = fibonacci(digit)
        plastic = plastic_power(digit)
        residue = orthogonal[lane_index].residue
        cells.append(TensorCell(digit, lane_index, polynomial, fib, plastic, residue, polynomial + fib + residue))
    vm81 = tuple((cells[index % 9].combined_scalar + index // 9 + local.residue) % 72 for index in range(81))
    tensor_payload = ("".join(
        f"{cell.lo_shu_digit}:{cell.polynomial_component}:{cell.fibonacci_component}:({cell.plastic_component[0]},{cell.plastic_component[1]},{cell.plastic_component[2]}):{cell.phase_residue}|"
        for cell in cells
    )).encode()
    vm_payload = (",".join(map(str, vm81)) + ",").encode()
    return ExactTensor(
        P2, P4, A, B, pq, Delta, xy, yx, triple, local,
        orthogonal, tuple(zip(CENTERLINE_LABELS, centerline)), tuple(cells), vm81,
        hash216(tensor_payload), hash216(vm_payload),
    )
