from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from hhs_runtime.pass219_native_universal_constraint_v1 import (
    CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE,
)

FIBONACCI_SEED = (1, 2)
LO_SHU_CELL_COUNT = 9
OUTER_HYDRATION_MODULUS = 1_259_713
PASS192_MAX_DEPTH = 4096


def source_membrane_depth(source: str = CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE) -> int:
    pairs = {")": "(", "]": "[", "}": "{"}
    openers = set(pairs.values())
    stack: list[str] = []
    maximum = 0
    for char in source:
        if char in openers:
            stack.append(char)
            maximum = max(maximum, len(stack))
        elif char in pairs:
            if not stack or stack[-1] != pairs[char]:
                raise ValueError("unbalanced native UCE membrane syntax")
            stack.pop()
    if stack:
        raise ValueError("unbalanced native UCE membrane syntax")
    return maximum


def fibonacci_prefix(depth: int) -> tuple[int, ...]:
    if not isinstance(depth, int) or depth < 0 or depth > PASS192_MAX_DEPTH:
        raise ValueError("depth is outside the exact Pass 192 finite-prefix domain")
    values = [FIBONACCI_SEED[0], FIBONACCI_SEED[1]]
    while len(values) <= depth + 1:
        values.append(values[-1] + values[-2])
    return tuple(values[: depth + 2])


@dataclass(frozen=True)
class FibonacciCompressionWitness:
    depth: int
    f_depth: int
    f_next: int
    transition: Fraction
    cumulative_scale: Fraction
    membrane_modulus: int
    membrane_residue: int
    lo_shu_cell_count: int
    shared_schedule_count: int
    outer_modulus: int

    def valid(self) -> bool:
        return (
            self.depth >= 0
            and self.transition == Fraction(self.f_depth, self.f_next)
            and self.cumulative_scale == Fraction(1, self.f_depth)
            and self.membrane_modulus == self.depth + 1
            and self.membrane_residue == self.depth
            and self.depth % self.membrane_modulus == self.membrane_residue
            and self.lo_shu_cell_count == LO_SHU_CELL_COUNT
            and self.shared_schedule_count == 1
            and self.outer_modulus == OUTER_HYDRATION_MODULUS
        )


def build_witness(depth: int) -> FibonacciCompressionWitness:
    values = fibonacci_prefix(depth)
    transitions = [Fraction(values[index], values[index + 1]) for index in range(depth)]
    cumulative = Fraction(1, 1)
    for transition in transitions:
        cumulative *= transition
    expected_cumulative = Fraction(1, values[depth])
    if cumulative != expected_cumulative:
        raise AssertionError("Pass 192 telescoping invariant failed")
    witness = FibonacciCompressionWitness(
        depth=depth,
        f_depth=values[depth],
        f_next=values[depth + 1],
        transition=Fraction(values[depth], values[depth + 1]),
        cumulative_scale=expected_cumulative,
        membrane_modulus=depth + 1,
        membrane_residue=depth % (depth + 1),
        lo_shu_cell_count=LO_SHU_CELL_COUNT,
        shared_schedule_count=1,
        outer_modulus=OUTER_HYDRATION_MODULUS,
    )
    if not witness.valid():
        raise AssertionError("Pass 192 compression witness failed exact invariants")
    return witness


def expanded_cell_schedules(depth: int) -> tuple[tuple[int, ...], ...]:
    schedule = fibonacci_prefix(depth)
    return tuple(schedule for _ in range(LO_SHU_CELL_COUNT))


def reference_invariants() -> dict[str, bool]:
    depth = source_membrane_depth()
    witness = build_witness(depth)
    return {
        "source_depth": depth == 10,
        "terminal_pair": witness.f_depth == 144 and witness.f_next == 233,
        "transition": witness.transition == Fraction(144, 233),
        "cumulative": witness.cumulative_scale == Fraction(1, 144),
        "membrane": witness.membrane_modulus == 11 and witness.membrane_residue == 10,
        "dedup": len(expanded_cell_schedules(depth)) == 9 and witness.shared_schedule_count == 1,
        "outer_namespace": witness.outer_modulus == 1_259_713,
    }


__all__ = [
    "FIBONACCI_SEED",
    "LO_SHU_CELL_COUNT",
    "OUTER_HYDRATION_MODULUS",
    "FibonacciCompressionWitness",
    "source_membrane_depth",
    "fibonacci_prefix",
    "build_witness",
    "expanded_cell_schedules",
    "reference_invariants",
]
