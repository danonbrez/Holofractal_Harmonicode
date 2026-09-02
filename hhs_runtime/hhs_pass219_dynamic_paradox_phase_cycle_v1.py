"""Pass 219 I147 bounded self-reference / phase-cycle closure.

The object-level fixed-point problem and the meta-level statement that the
object-level valid set is empty are deliberately separate types. The module
never promotes meta-level zero back into object-level option correctness.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence

SCHEMA = "HHS_PASS219_DYNAMIC_PARADOX_PHASE_CYCLE_V1"
VERSION = "1.0.0"
MAX_OPTIONS = 16
H36 = 36
MANIFOLD_BASE = 5184
MANIFOLD_POWER = 4
MANIFOLD_CARDINALITY = 722_204_136_308_736


@dataclass(frozen=True)
class ParadoxWitness:
    option_values: tuple[Fraction, ...]
    seed_index: int
    object_valid_option_indices: tuple[int, ...]
    trajectory: tuple[Fraction, ...]
    preperiod: int
    period: int
    meta_empty_valid_set: bool
    meta_probability: Fraction
    seed_candidate_trinary: int
    cycle_motion_trinary: int
    meta_closure_trinary: int
    typed_level_separation_preserved: bool = True
    bounded_closure: bool = True
    ordered_trajectory_preserved: bool = True
    canonical_mutation_authority: bool = False
    canonical_hash72_authority: bool = False
    canonical_persistence_authority: bool = False
    floating_point_authority: bool = False

    @property
    def object_has_fixed_point(self) -> bool:
        return bool(self.object_valid_option_indices)

    @property
    def seed_option_object_correct(self) -> bool:
        return self.seed_index in self.object_valid_option_indices


def _normalize_probability(value: Fraction | int) -> Fraction:
    out = value if isinstance(value, Fraction) else Fraction(value, 1)
    if out < 0 or out > 1:
        raise ValueError("probability must be in [0,1]")
    return out


def probability_map(
    option_values: Sequence[Fraction | int],
    value: Fraction | int,
) -> Fraction:
    options = tuple(_normalize_probability(v) for v in option_values)
    if not (2 <= len(options) <= MAX_OPTIONS):
        raise ValueError("option count out of range")
    current = _normalize_probability(value)
    return Fraction(sum(1 for item in options if item == current), len(options))


def fixed_point_valid_option_indices(
    option_values: Sequence[Fraction | int],
) -> tuple[int, ...]:
    options = tuple(_normalize_probability(v) for v in option_values)
    return tuple(
        i for i, value in enumerate(options)
        if probability_map(options, value) == value
    )


def analyze_paradox(
    option_values: Sequence[Fraction | int],
    *,
    seed_index: int,
    permit_meta_closure: bool = True,
    promote_meta_zero_to_object_correct: bool = False,
) -> ParadoxWitness:
    options = tuple(_normalize_probability(v) for v in option_values)
    if not (2 <= len(options) <= MAX_OPTIONS):
        raise ValueError("option count out of range")
    if not 0 <= seed_index < len(options):
        raise ValueError("seed index out of range")
    if promote_meta_zero_to_object_correct:
        raise ValueError("TYPE_LEVEL_CONFLATION")

    valid = fixed_point_valid_option_indices(options)
    visit_bound = len(options) + 2
    trajectory = [options[seed_index]]
    repeat_index: int | None = None

    while len(trajectory) < visit_bound:
        nxt = probability_map(options, trajectory[-1])
        try:
            repeat_index = trajectory.index(nxt)
        except ValueError:
            trajectory.append(nxt)
            continue
        trajectory.append(nxt)
        break

    if repeat_index is None:
        raise RuntimeError("NO_FINITE_CLOSURE")

    period = len(trajectory) - 1 - repeat_index
    meta_empty = permit_meta_closure and not valid
    return ParadoxWitness(
        option_values=options,
        seed_index=seed_index,
        object_valid_option_indices=valid,
        trajectory=tuple(trajectory),
        preperiod=repeat_index,
        period=period,
        meta_empty_valid_set=meta_empty,
        meta_probability=Fraction(0, 1) if meta_empty else Fraction(len(valid), len(options)),
        seed_candidate_trinary=1 if seed_index in valid else -1,
        cycle_motion_trinary=1 if period > 1 else 0,
        meta_closure_trinary=0 if meta_empty else (1 if valid else -1),
    )


def canonical_random_guess_paradox() -> ParadoxWitness:
    return analyze_paradox(
        (Fraction(1, 4), Fraction(0, 1), Fraction(1, 2), Fraction(1, 4)),
        seed_index=1,
        permit_meta_closure=True,
    )


def boolean_negation_cycle(seed: int) -> tuple[int, int, int]:
    if seed not in (0, 1):
        raise ValueError("Boolean seed must be 0 or 1")
    return (seed, 1 - seed, seed)


def h36_identity_witness() -> dict[str, int | bool]:
    a2, b2, c2 = 1, 2, 3
    b4 = b2 * b2
    b6 = b4 * b2
    c4 = c2 * c2
    denominator = c2 - a2
    if denominator == 0:
        raise ZeroDivisionError("H36 denominator is zero")
    lhs_numerator = b6 * c4
    if lhs_numerator % denominator:
        raise ArithmeticError("H36 left side is not integral")
    lhs = lhs_numerator // denominator
    rhs = (a2 + b2) ** 2 * b4
    cardinality = MANIFOLD_BASE ** MANIFOLD_POWER
    return {
        "schema": "HHS_PASS219_H36_CLOSURE_IDENTITY_V1",
        "a2": a2,
        "b2": b2,
        "c2": c2,
        "b4": b4,
        "b6": b6,
        "c4": c4,
        "denominator": denominator,
        "lhs_numerator": lhs_numerator,
        "lhs_denominator": denominator,
        "lhs_value": lhs,
        "rhs_value": rhs,
        "h36_value": H36,
        "identity_equal": lhs == rhs == H36,
        "manifold_base": MANIFOLD_BASE,
        "manifold_power": MANIFOLD_POWER,
        "manifold_cardinality": cardinality,
        "manifold_cardinality_equal": cardinality == MANIFOLD_CARDINALITY,
        "canonical_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }


def exact_work_model(
    *,
    evaluation_count: int = 1,
) -> dict[str, int | bool | str]:
    if evaluation_count <= 0:
        raise ValueError("evaluation_count must be positive")
    witness = canonical_random_guess_paradox()
    n = len(witness.option_values)
    bound = n + 2
    transitions = len(witness.trajectory) - 1

    # Baseline: each recursive layer recomputes all n candidate fixed-point
    # checks (n*n comparisons) and the current probability map (n more).
    baseline_per_evaluation = bound * (n * n + n)

    # Optimized: fixed-point census once, map only until first repeated state,
    # plus ordered visited-state comparisons for exact cycle detection.
    cycle_comparisons = 0
    prior: list[Fraction] = [witness.trajectory[0]]
    for nxt in witness.trajectory[1:]:
        for existing in prior:
            cycle_comparisons += 1
            if existing == nxt:
                break
        prior.append(nxt)
    optimized_per_evaluation = n * n + transitions * n + cycle_comparisons

    baseline = baseline_per_evaluation * evaluation_count
    optimized = optimized_per_evaluation * evaluation_count
    saved = baseline - optimized
    return {
        "schema": "HHS_PASS219_DYNAMIC_PARADOX_EXACT_WORK_MODEL_V1",
        "evaluation_count": evaluation_count,
        "option_count": n,
        "finite_visit_bound": bound,
        "actual_transitions": transitions,
        "baseline_per_evaluation": baseline_per_evaluation,
        "optimized_per_evaluation": optimized_per_evaluation,
        "baseline_total_work": baseline,
        "optimized_total_work": optimized,
        "exact_work_saved": saved,
        "reduction_permille_floor": (saved * 1000) // baseline,
        "timing_is_canonical": False,
        "canonical_authority_changed": False,
    }


__all__ = [
    "SCHEMA",
    "VERSION",
    "H36",
    "MANIFOLD_BASE",
    "MANIFOLD_POWER",
    "MANIFOLD_CARDINALITY",
    "ParadoxWitness",
    "probability_map",
    "fixed_point_valid_option_indices",
    "analyze_paradox",
    "canonical_random_guess_paradox",
    "boolean_negation_cycle",
    "h36_identity_witness",
    "exact_work_model",
]
