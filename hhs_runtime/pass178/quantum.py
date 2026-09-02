from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from .exact import (
    ComplexExact,
    ExactPhysicsError,
    ExactRational,
    I_C,
    ONE_C,
    ZERO_C,
)


def c(value: Any) -> ComplexExact:
    if isinstance(value, ComplexExact):
        return value
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return ComplexExact(ExactRational.coerce(value[0]), ExactRational.coerce(value[1]))
    return ComplexExact.coerce(value)


def matrix(values: Sequence[Sequence[Any]]) -> tuple[tuple[ComplexExact, ...], ...]:
    rows = tuple(tuple(c(v) for v in row) for row in values)
    if not rows or any(len(row) != len(rows) for row in rows):
        raise ExactPhysicsError("P178_QUANTUM_SQUARE_MATRIX_REQUIRED")
    if len(rows) > 81:
        raise ExactPhysicsError("P178_QUANTUM_MATRIX_DIMENSION")
    return rows


def is_hermitian(H: Sequence[Sequence[ComplexExact]]) -> bool:
    n = len(H)
    return all(H[i][j] == H[j][i].conjugate() for i in range(n) for j in range(n))


def norm2(amplitudes: Iterable[ComplexExact]) -> ExactRational:
    return sum((a.abs2() for a in amplitudes), ExactRational(0))


@dataclass(frozen=True)
class QuantumState:
    state_id: str
    amplitudes: tuple[ComplexExact, ...]
    step_index: int = 0

    def __post_init__(self) -> None:
        if not self.state_id:
            raise ExactPhysicsError("P178_QUANTUM_STATE_ID")
        if not self.amplitudes or len(self.amplitudes) > 81:
            raise ExactPhysicsError("P178_QUANTUM_STATE_DIMENSION")
        if self.step_index < 0:
            raise ExactPhysicsError("P178_QUANTUM_STEP_INDEX")
        if norm2(self.amplitudes) != ExactRational(1):
            raise ExactPhysicsError("P178_QUANTUM_NORMALIZATION_REQUIRED")

    def payload(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_178_QUANTUM_STATE_V1",
            "state_id": self.state_id,
            "step_index": self.step_index,
            "amplitudes": [a.as_pairs() for a in self.amplitudes],
            "norm2": norm2(self.amplitudes).as_pair(),
        }


def _mat_vec(
    A: Sequence[Sequence[ComplexExact]],
    v: Sequence[ComplexExact],
) -> list[ComplexExact]:
    return [
        sum((A[i][j] * v[j] for j in range(len(v))), ZERO_C)
        for i in range(len(A))
    ]


def _solve(
    A: Sequence[Sequence[ComplexExact]],
    b: Sequence[ComplexExact],
) -> tuple[ComplexExact, ...]:
    n = len(A)
    aug = [list(A[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = next((row for row in range(col, n) if aug[row][col] != ZERO_C), None)
        if pivot is None:
            raise ExactPhysicsError("P178_QUANTUM_SINGULAR_CAYLEY_MATRIX")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [x / scale for x in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            if factor == ZERO_C:
                continue
            aug[row] = [
                aug[row][j] - factor * aug[col][j]
                for j in range(n + 1)
            ]
    return tuple(aug[i][-1] for i in range(n))


def cayley_step(
    state: QuantumState,
    hamiltonian: Sequence[Sequence[Any]],
    dt: Any,
    hbar: Any = 1,
) -> QuantumState:
    H = matrix(hamiltonian)
    if len(H) != len(state.amplitudes):
        raise ExactPhysicsError("P178_QUANTUM_DIMENSION_MISMATCH")
    if not is_hermitian(H):
        raise ExactPhysicsError("P178_QUANTUM_NON_HERMITIAN_CLOSED_SYSTEM")
    dt_r = ExactRational.coerce(dt)
    hbar_r = ExactRational.coerce(hbar)
    if dt_r.num <= 0 or hbar_r.num <= 0:
        raise ExactPhysicsError("P178_QUANTUM_POSITIVE_DT_HBAR_REQUIRED")
    alpha = ComplexExact(ExactRational(0), dt_r / (ExactRational(2) * hbar_r))
    n = len(H)
    A: list[list[ComplexExact]] = []
    B: list[list[ComplexExact]] = []
    for i in range(n):
        ar: list[ComplexExact] = []
        br: list[ComplexExact] = []
        for j in range(n):
            ident = ONE_C if i == j else ZERO_C
            ar.append(ident + alpha * H[i][j])
            br.append(ident - alpha * H[i][j])
        A.append(ar)
        B.append(br)
    rhs = _mat_vec(B, state.amplitudes)
    next_amp = _solve(A, rhs)
    if norm2(next_amp) != norm2(state.amplitudes):
        raise ExactPhysicsError("P178_QUANTUM_NORM_DRIFT")
    return QuantumState(
        state_id=state.state_id,
        amplitudes=next_amp,
        step_index=state.step_index + 1,
    )


def double_slit_hamiltonian_nucleus() -> tuple[tuple[ComplexExact, ...], ...]:
    # Three-cell Hermitian lattice nucleus: left/slit/right with exact nearest-neighbor coupling.
    z = ZERO_C
    one = ComplexExact(ExactRational(1), ExactRational(0))
    minus = ComplexExact(ExactRational(-1), ExactRational(0))
    return (
        (one, minus, z),
        (minus, ComplexExact(ExactRational(2), ExactRational(0)), minus),
        (z, minus, one),
    )
