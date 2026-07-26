from __future__ import annotations

from dataclasses import dataclass, asdict
from math import comb
import json
from typing import Any

from .parser import hash216, hash72

LO_SHU = (4, 9, 2, 3, 5, 7, 8, 1, 6)
CENTERLINE_LABELS = ("x+y", "zw", "x", "z", "yx", "wz", "y", "w", "xy", "b^2", "c^2")
EXTENDED_CENTERLINE_LABELS = CENTERLINE_LABELS + ("d^2", "e^2", "f^2", "g^2")
GEAR_WORDS = ("xy", "yx", "zw", "wz")
DENOMINATIONS = ("8", "5", "3", "2", "sqrt(2)", "t^3", "Phi", "t", "1")

SUDOKU_X = (
    (1, 2, 3, 4, 5, 6, 7, 8, 9),
    (4, 5, 6, 7, 8, 9, 1, 2, 3),
    (7, 8, 9, 1, 2, 3, 4, 5, 6),
    (9, 3, 5, 2, 4, 1, 8, 6, 7),
    (6, 1, 7, 5, 3, 8, 2, 9, 4),
    (8, 4, 2, 6, 9, 7, 5, 3, 1),
    (2, 9, 8, 3, 1, 4, 6, 7, 5),
    (3, 7, 1, 8, 6, 5, 9, 4, 2),
    (5, 6, 4, 9, 7, 2, 3, 1, 8),
)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


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


def fibonacci_square_value(index: int) -> int:
    if index < 0:
        raise ValueError("negative Fibonacci-square index")
    a2, b2 = 1, 2
    if index == 0:
        return a2
    for _ in range(1, index):
        a2, b2 = b2, a2 + b2
    return b2


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


def _squarefree(rad: int) -> tuple[int, int]:
    if rad < 0:
        raise ValueError("negative exact radical requires an explicit complex carrier")
    if rad == 0:
        return 0, 1
    coefficient = 1
    squarefree = rad
    factor = 2
    while factor * factor <= squarefree:
        square = factor * factor
        while squarefree % square == 0:
            squarefree //= square
            coefficient *= factor
        factor += 1
    return coefficient, squarefree


@dataclass(frozen=True)
class ExactRadical:
    source: str
    radicand: int
    coefficient: int
    squarefree_radicand: int
    normalized: str
    authoritative: bool = True


def construct_exact_radius(square_state: int) -> ExactRadical:
    if square_state < 0:
        raise ValueError("square state must be nonnegative")
    coefficient, squarefree = _squarefree(square_state)
    if square_state == 0:
        normalized = "0"
    elif squarefree == 1:
        normalized = str(coefficient)
    elif coefficient == 1:
        normalized = f"sqrt({squarefree})"
    else:
        normalized = f"{coefficient}*sqrt({squarefree})"
    return ExactRadical(
        source=f"sqrt({square_state})",
        radicand=square_state,
        coefficient=coefficient,
        squarefree_radicand=squarefree,
        normalized=normalized,
    )


@dataclass(frozen=True)
class PhasePivotState:
    pivot_symbol: str
    phase_index: int
    fold_index: int
    scalar_zero: str
    residue_zero: str
    closure_zero: str
    fold_zero: str
    scalar_one: str
    unit_one: str
    renewed_one: str
    phase_one: str
    ordered_cancellation_words: tuple[str, str]
    normalized_phase_class: str
    rotation_closed: bool


def construct_phase_nucleus(rotation: int = 72) -> PhasePivotState:
    fold_index, phase_index = phase_decompose(rotation, 72)
    return PhasePivotState(
        pivot_symbol=".",
        phase_index=phase_index,
        fold_index=fold_index,
        scalar_zero="0_scalar",
        residue_zero="0_residue",
        closure_zero="0_closure",
        fold_zero="0_fold",
        scalar_one="1_scalar",
        unit_one="1_unit",
        renewed_one="1_renewed",
        phase_one="1_phase",
        ordered_cancellation_words=("1-1", "-1+1"),
        normalized_phase_class="u",
        rotation_closed=phase_index == 0,
    )


@dataclass(frozen=True)
class FactorialRatio:
    n: int
    k: int
    numerator: int
    denominator: int
    canonical: str


def factorial_ratio(n: int, k: int) -> FactorialRatio:
    if n < 0 or k < 0 or k > n:
        raise ValueError("require 0 <= k <= n")
    value = comb(n, k)
    return FactorialRatio(n=n, k=k, numerator=value, denominator=1, canonical=f"{value}/1")


def construct_factorial_ratio_matrix(
    index: int,
    dimensions: tuple[int, int] = (3, 3),
    *,
    max_factorial_argument: int = 4096,
) -> tuple[tuple[FactorialRatio, ...], ...]:
    rows, columns = dimensions
    if index < 0:
        raise ValueError("index must be nonnegative")
    if rows <= 0 or columns <= 0 or rows > 9 or columns > 9:
        raise ValueError("matrix dimensions must be within 1..9")
    largest = index + (rows - 1) + (columns - 1)
    if largest > max_factorial_argument:
        raise ValueError("FACTORIAL_BOUNDED")
    return tuple(
        tuple(factorial_ratio(index + i + j, i + j) for j in range(columns))
        for i in range(rows)
    )


@dataclass(frozen=True)
class LoShuCell:
    row: int
    column: int
    value: int
    constructor: str


def construct_loshu() -> tuple[LoShuCell, ...]:
    witnesses = (
        "a^2+c^2", "a^2+c^2+d^2", "b^2",
        "c^2", "d^2", "b^2+d^2",
        "c^2+d^2", "a^2", "a^2+d^2",
    )
    values = (
        1 + 3, 1 + 3 + 5, 2,
        3, 5, 2 + 5,
        3 + 5, 1, 1 + 5,
    )
    return tuple(
        LoShuCell(index // 3, index % 3, values[index], witnesses[index])
        for index in range(9)
    )


def validate_loshu(cells: tuple[LoShuCell, ...]) -> bool:
    if len(cells) != 9:
        return False
    matrix = [[0] * 3 for _ in range(3)]
    for cell in cells:
        matrix[cell.row][cell.column] = cell.value
    lanes = (
        *matrix,
        *([matrix[r][c] for r in range(3)] for c in range(3)),
        [matrix[i][i] for i in range(3)],
        [matrix[i][2 - i] for i in range(3)],
    )
    return all(sum(lane) == 15 for lane in lanes)


def validate_sudoku_x(grid: tuple[tuple[int, ...], ...] = SUDOKU_X) -> bool:
    symbols = set(range(1, 10))
    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        return False
    if any(set(row) != symbols for row in grid):
        return False
    if any({grid[r][c] for r in range(9)} != symbols for c in range(9)):
        return False
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            if {grid[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)} != symbols:
                return False
    if {grid[i][i] for i in range(9)} != symbols:
        return False
    if {grid[i][8 - i] for i in range(9)} != symbols:
        return False
    return True


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
class VM81PhaseTensorState:
    vm81_address: int
    row: int
    column: int
    sudoku_symbol: int
    lo_shu_address: int
    denomination: str
    phase_index: int
    fold_index: int
    ordered_gear_word: str
    magnitude_state: int
    radical_state: str
    factorial_ratio_matrix_ref: str
    local_hamiltonian_ref: str
    state_hash72: str


def construct_vm81_phase_tensor(
    *,
    full_rotation: int,
    fibonacci_squares: tuple[int, ...],
    factorial_matrix: tuple[tuple[FactorialRatio, ...], ...],
) -> tuple[VM81PhaseTensorState, ...]:
    if not validate_sudoku_x():
        raise ArithmeticError("Sudoku denomination topology invalid")
    matrix_ref = hash72(_canonical_json([[cell.canonical for cell in row] for row in factorial_matrix]))
    states: list[VM81PhaseTensorState] = []
    for address in range(81):
        row, column = divmod(address, 9)
        symbol = SUDOKU_X[row][column]
        lo_shu_address = LO_SHU[symbol - 1]
        denomination = DENOMINATIONS[symbol - 1]
        fold_index, phase_index = phase_decompose(full_rotation + address, 72)
        gear_word = GEAR_WORDS[address % len(GEAR_WORDS)]
        magnitude = fibonacci_squares[(symbol - 1) % len(fibonacci_squares)]
        radical = construct_exact_radius(magnitude).normalized
        hamiltonian = f"H[{row},{column},{phase_index},{fold_index}]"
        payload = {
            "vm81_address": address,
            "row": row,
            "column": column,
            "symbol": symbol,
            "lo_shu_address": lo_shu_address,
            "denomination": denomination,
            "phase_index": phase_index,
            "fold_index": fold_index,
            "gear_word": gear_word,
            "magnitude": magnitude,
            "radical": radical,
            "factorial_ratio_matrix_ref": matrix_ref,
            "local_hamiltonian_ref": hamiltonian,
        }
        states.append(VM81PhaseTensorState(
            vm81_address=address,
            row=row,
            column=column,
            sudoku_symbol=symbol,
            lo_shu_address=lo_shu_address,
            denomination=denomination,
            phase_index=phase_index,
            fold_index=fold_index,
            ordered_gear_word=gear_word,
            magnitude_state=magnitude,
            radical_state=radical,
            factorial_ratio_matrix_ref=matrix_ref,
            local_hamiltonian_ref=hamiltonian,
            state_hash72=hash72(_canonical_json(payload)),
        ))
    return tuple(states)


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
    phase_nucleus: PhasePivotState
    fibonacci_squares: tuple[int, ...]
    radical_carriers: tuple[ExactRadical, ...]
    factorial_ratio_matrix: tuple[tuple[FactorialRatio, ...], ...]
    lo_shu_construction: tuple[LoShuCell, ...]
    vm81_phase_tensor: tuple[VM81PhaseTensorState, ...]
    hash72_lanes: tuple[str, str, str]
    hash216_commitment: str

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

    phase_nucleus = construct_phase_nucleus(full_rotation)
    fib_squares = tuple(fibonacci_square_value(index) for index in range(9))
    radicals = tuple(construct_exact_radius(value) for value in fib_squares)
    factorial_matrix = construct_factorial_ratio_matrix(8, (3, 3))
    loshu = construct_loshu()
    if not validate_loshu(loshu):
        raise ArithmeticError("Lo Shu constructor closure failed")
    vm81_phase_tensor = construct_vm81_phase_tensor(
        full_rotation=full_rotation,
        fibonacci_squares=fib_squares,
        factorial_matrix=factorial_matrix,
    )

    magnitude_payload = {
        "fibonacci_squares": fib_squares,
        "radicals": [asdict(value) for value in radicals],
        "plastic_relation": "t^3=t+1",
        "golden_relation": "Phi^2=Phi+1",
        "denominations": DENOMINATIONS,
        "factorial_ratio_matrix": [[cell.canonical for cell in row] for row in factorial_matrix],
        "lo_shu": [asdict(cell) for cell in loshu],
        "sudoku_symbols": [state.sudoku_symbol for state in vm81_phase_tensor],
    }
    phase_payload = {
        "phase_nucleus": asdict(phase_nucleus),
        "ordered_gear_words": GEAR_WORDS,
        "centerline": list(zip(CENTERLINE_LABELS, centerline)),
        "local_phase": asdict(local),
        "orthogonal_phase": [asdict(lane) for lane in orthogonal],
    }
    nesting_payload = {
        "vm81": [asdict(state) for state in vm81_phase_tensor],
        "inheritance_parent": "HHS-P156.1-LSHPVS",
        "reconstruction": "COMPLETE",
    }
    lanes = (
        hash72(_canonical_json(magnitude_payload)),
        hash72(_canonical_json(phase_payload)),
        hash72(_canonical_json(nesting_payload)),
    )
    commitment = "".join(lanes)
    if len(commitment) != 216:
        raise ArithmeticError("Hash216 lane concatenation failed")

    return ExactTensor(
        P2, P4, A, B, pq, Delta, xy, yx, triple, local,
        orthogonal, tuple(zip(CENTERLINE_LABELS, centerline)), tuple(cells), vm81,
        hash216(tensor_payload), hash216(vm_payload),
        phase_nucleus, fib_squares, radicals, factorial_matrix, loshu,
        vm81_phase_tensor, lanes, commitment,
    )
