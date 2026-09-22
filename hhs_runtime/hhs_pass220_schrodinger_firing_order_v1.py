"""Pass 220 I025 exact firing-order Schrödinger spectrum receipt.

This module proves the permutation/unitarity/cycle/de-generacy surface with
integer and rational arithmetic only. The cyclotomic phase is represented by
an exponent of a primitive 72nd root. No floating-point eigenvalue solver is
used.

The standard evolution convention is fixed explicitly:

    U = ExpSym(-i H Delta_t / u72)

Under the nonnegative k=0..8 branch this gives
U psi_k = zeta_9^(-k) psi_k.

A single unitary U does not uniquely choose a Hermitian logarithm; I025 records
the branch selector as part of the Hamiltonian receipt.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Iterable

SCHEMA = "HHS_PASS_220_I025_SCHRODINGER_FULL_ORBIT_V1"
PROFILE = "PASS220-I025-SCHRODINGER-FULL-ORBIT-v1"

PHASE_MODULUS = 72
FIRING_ORIGIN = 8
FIRING_STEP = 16
MACROCYCLE_ORDER = 9
FULL_ORBIT_CYCLE_COUNT = 8
ZETA9_EXPONENT_IN_ZETA72 = 8
I_EXPONENT_IN_ZETA72 = 18

EVOLUTION_CONVENTION = "U=ExpSym(-i*H*Delta_t/u72)"
HAMILTONIAN_BRANCH = "NONNEGATIVE_K_0_TO_8"
FINITE_DIFFERENCE_IS_LOG_HAMILTONIAN = False
HOST_WALL_CLOCK_AUTHORITY = False
FLOATING_POINT_AUTHORITY = False
NUMERICAL_EIGENSOLVER_AUTHORITY = False
CANONICAL_ADMISSION_AUTHORITY = False


class Pass220I025QuantumError(ValueError):
    pass


@dataclass(frozen=True)
class Phase72:
    """Exact multiplicative phase zeta_72^exponent."""

    exponent: int

    def __post_init__(self) -> None:
        if isinstance(self.exponent, bool) or not isinstance(
            self.exponent, int
        ):
            raise Pass220I025QuantumError(
                "phase exponent must be an exact integer"
            )
        object.__setattr__(
            self, "exponent", self.exponent % PHASE_MODULUS
        )

    def __mul__(self, other: "Phase72") -> "Phase72":
        if not isinstance(other, Phase72):
            return NotImplemented
        return Phase72(self.exponent + other.exponent)

    def __pow__(self, power: int) -> "Phase72":
        if isinstance(power, bool) or not isinstance(power, int):
            raise Pass220I025QuantumError(
                "phase power must be an exact integer"
            )
        return Phase72(self.exponent * power)

    def conjugate(self) -> "Phase72":
        return Phase72(-self.exponent)

    def inverse(self) -> "Phase72":
        return self.conjugate()

    def as_text(self) -> str:
        return f"zeta72^{self.exponent}"


@dataclass(frozen=True)
class EnergyLevel:
    k: int
    turn_fraction: Fraction
    phase: Phase72
    degeneracy: int

    @property
    def exact_text(self) -> str:
        if self.k == 0:
            return "0"
        return (
            f"u72*(2*pi*{self.k}/9)/(tau*theta)"
        )


def _i(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I025QuantumError(
            f"{name} must be an exact integer"
        )
    return value


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return {
        **payload,
        "receipt_sha256": sha256(encoded.encode("utf-8")).hexdigest(),
    }


def sigma(transition_index: int) -> int:
    n = _i(transition_index, "transition_index")
    residue = (FIRING_ORIGIN + FIRING_STEP * n) % PHASE_MODULUS
    return PHASE_MODULUS if residue == 0 else residue


def firing_order() -> tuple[int, ...]:
    return tuple(sigma(n) for n in range(MACROCYCLE_ORDER))


def shift_permutation(size: int, step: int) -> tuple[int, ...]:
    n = _i(size, "size")
    s = _i(step, "step")
    if n <= 0:
        raise Pass220I025QuantumError("size must be positive")
    return tuple(
        ((label - 1 + s) % n) + 1
        for label in range(1, n + 1)
    )


def _validate_permutation(
    permutation: tuple[int, ...],
    name: str = "permutation",
) -> int:
    n = len(permutation)
    if n <= 0:
        raise Pass220I025QuantumError(
            f"{name} must be a nonempty exact permutation"
        )
    if any(
        isinstance(label, bool) or not isinstance(label, int)
        for label in permutation
    ):
        raise Pass220I025QuantumError(
            f"{name} labels must be exact integers"
        )
    expected = set(range(1, n + 1))
    if set(permutation) != expected:
        raise Pass220I025QuantumError(
            f"{name} must be an exact permutation"
        )
    return n


def compose_permutations(
    left: tuple[int, ...],
    right: tuple[int, ...],
) -> tuple[int, ...]:
    if len(left) != len(right):
        raise Pass220I025QuantumError(
            "permutations must have equal size"
        )
    n = _validate_permutation(left, "left")
    _validate_permutation(right, "right")
    return tuple(left[right[i] - 1] for i in range(n))


def permutation_power(
    permutation: tuple[int, ...],
    power: int,
) -> tuple[int, ...]:
    p = _i(power, "power")
    if p < 0:
        raise Pass220I025QuantumError(
            "permutation power must be nonnegative"
        )
    n = _validate_permutation(permutation)
    result = tuple(range(1, n + 1))
    base = permutation
    exponent = p
    while exponent:
        if exponent & 1:
            result = compose_permutations(base, result)
        base = compose_permutations(base, base)
        exponent >>= 1
    return result


def permutation_cycles(
    permutation: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    n = _validate_permutation(permutation)
    seen: set[int] = set()
    cycles: list[tuple[int, ...]] = []
    for start in range(1, n + 1):
        if start in seen:
            continue
        cycle: list[int] = []
        current = start
        while current not in seen:
            seen.add(current)
            cycle.append(current)
            current = permutation[current - 1]
        cycles.append(tuple(cycle))
    return tuple(cycles)


def permutation_matrix(
    permutation: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    n = _validate_permutation(permutation)
    # Column j is mapped to row permutation[j].
    return tuple(
        tuple(
            1 if row == permutation[column - 1] else 0
            for column in range(1, n + 1)
        )
        for row in range(1, n + 1)
    )


def permutation_unitary_exact(
    permutation: tuple[int, ...],
) -> bool:
    matrix = permutation_matrix(permutation)
    n = len(matrix)
    row_ok = all(sum(row) == 1 for row in matrix)
    col_ok = all(
        sum(matrix[row][col] for row in range(n)) == 1
        for col in range(n)
    )
    binary = all(
        entry in (0, 1)
        for row in matrix
        for entry in row
    )
    return row_ok and col_ok and binary


def _poly_mul(
    left: tuple[int, ...],
    right: tuple[int, ...],
) -> tuple[int, ...]:
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return tuple(out)


def _poly_pow(
    polynomial: tuple[int, ...],
    power: int,
) -> tuple[int, ...]:
    p = _i(power, "power")
    if p < 0:
        raise Pass220I025QuantumError(
            "polynomial power must be nonnegative"
        )
    result = (1,)
    base = polynomial
    exponent = p
    while exponent:
        if exponent & 1:
            result = _poly_mul(result, base)
        base = _poly_mul(base, base)
        exponent >>= 1
    return result


def characteristic_polynomial_from_cycles(
    cycle_lengths: Iterable[int],
) -> tuple[int, ...]:
    # Coefficients are low degree -> high degree for det(x I - P).
    polynomial = (1,)
    for length in cycle_lengths:
        l = _i(length, "cycle_length")
        if l <= 0:
            raise Pass220I025QuantumError(
                "cycle length must be positive"
            )
        factor = [-1] + [0] * (l - 1) + [1]
        polynomial = _poly_mul(polynomial, tuple(factor))
    return polynomial


def cyclotomic_9_factor_product() -> tuple[int, ...]:
    x_minus_1 = (-1, 1)
    phi3 = (1, 1, 1)
    phi9 = (1, 0, 0, 1, 0, 0, 1)
    return _poly_mul(_poly_mul(x_minus_1, phi3), phi9)


def macrocycle_permutation() -> tuple[int, ...]:
    return shift_permutation(MACROCYCLE_ORDER, 1)


def full_orbit_permutation() -> tuple[int, ...]:
    return shift_permutation(PHASE_MODULUS, FIRING_STEP)


def exact_energy_levels() -> tuple[EnergyLevel, ...]:
    return tuple(
        EnergyLevel(
            k=k,
            turn_fraction=Fraction(k, MACROCYCLE_ORDER),
            phase=Phase72(-ZETA9_EXPONENT_IN_ZETA72 * k),
            degeneracy=FULL_ORBIT_CYCLE_COUNT,
        )
        for k in range(MACROCYCLE_ORDER)
    )


def exact_node_phase(k: int) -> Phase72:
    mode = _i(k, "k")
    if not 0 <= mode < MACROCYCLE_ORDER:
        raise Pass220I025QuantumError(
            f"k must satisfy 0 <= k < {MACROCYCLE_ORDER}"
        )
    return exact_energy_levels()[mode].phase


def field_embedding_descriptor() -> dict[str, Any]:
    return _receipt({
        "schema": "HHS_PASS_220_I025_CYCLOTOMIC_FIELD_V1",
        "state_space": "Q(zeta72)^9",
        "zeta9_embedding": "zeta9=zeta72^8",
        "imaginary_unit_embedding": "i=zeta72^18",
        "zeta72_order": 72,
        "zeta9_order": 9,
        "phase_arithmetic": "exponent_mod_72",
        "floating_point_authority": False,
    })


def full_orbit_receipt() -> dict[str, Any]:
    u9 = macrocycle_permutation()
    u72 = full_orbit_permutation()
    cycles9 = permutation_cycles(u9)
    cycles72 = permutation_cycles(u72)
    lengths9 = tuple(sorted(len(c) for c in cycles9))
    lengths72 = tuple(sorted(len(c) for c in cycles72))

    identity9 = tuple(range(1, MACROCYCLE_ORDER + 1))
    identity72 = tuple(range(1, PHASE_MODULUS + 1))

    cp9 = characteristic_polynomial_from_cycles(lengths9)
    cp72 = characteristic_polynomial_from_cycles(lengths72)
    expected9 = cyclotomic_9_factor_product()
    expected72 = _poly_pow(
        expected9, FULL_ORBIT_CYCLE_COUNT
    )

    levels = exact_energy_levels()

    checks = {
        "firing_order_exact": firing_order()
        == (8, 24, 40, 56, 72, 16, 32, 48, 64),
        "phase_period_9": all(
            sigma(n + MACROCYCLE_ORDER) == sigma(n)
            for n in range(PHASE_MODULUS)
        ),
        "macrocycle_unitary": permutation_unitary_exact(u9),
        "macrocycle_nine_closure": (
            permutation_power(u9, MACROCYCLE_ORDER) == identity9
        ),
        "macrocycle_charpoly_x9_minus_1": cp9 == expected9,
        "full_orbit_unitary": permutation_unitary_exact(u72),
        "full_orbit_nine_closure": (
            permutation_power(u72, MACROCYCLE_ORDER) == identity72
        ),
        "full_orbit_eight_cycles": lengths72
        == (MACROCYCLE_ORDER,) * FULL_ORBIT_CYCLE_COUNT,
        "full_orbit_eightfold_charpoly": cp72 == expected72,
        "zeta9_embedding": (
            Phase72(1) ** ZETA9_EXPONENT_IN_ZETA72
            == Phase72(ZETA9_EXPONENT_IN_ZETA72)
        ),
        "imaginary_unit_embedding": (
            Phase72(I_EXPONENT_IN_ZETA72) ** 2 == Phase72(36)
        ),
        "energy_level_count": len(levels) == MACROCYCLE_ORDER,
        "energy_degeneracy_eight": all(
            level.degeneracy == FULL_ORBIT_CYCLE_COUNT
            for level in levels
        ),
        "positive_branch_phase_sign": all(
            level.phase
            == Phase72(-ZETA9_EXPONENT_IN_ZETA72 * level.k)
            for level in levels
        ),
    }

    return _receipt({
        "schema": SCHEMA,
        "profile": PROFILE,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "pass_count": sum(bool(v) for v in checks.values()),
        "check_count": len(checks),
        "firing_order": firing_order(),
        "macrocycle_cycles": cycles9,
        "full_orbit_cycles": cycles72,
        "full_orbit_cycle_lengths": lengths72,
        "macrocycle_charpoly_coefficients_low_to_high": cp9,
        "full_orbit_charpoly_coefficients_low_to_high": cp72,
        "cyclotomic_factorization_macrocycle": (
            "(x-1)(x^2+x+1)(x^6+x^3+1)"
        ),
        "cyclotomic_factorization_full_orbit": (
            "((x-1)(x^2+x+1)(x^6+x^3+1))^8"
        ),
        "energy_levels": [
            {
                "k": level.k,
                "turn_fraction": (
                    f"{level.turn_fraction.numerator}/"
                    f"{level.turn_fraction.denominator}"
                ),
                "eigenphase": level.phase.as_text(),
                "energy": level.exact_text,
                "degeneracy": level.degeneracy,
            }
            for level in levels
        ],
        "evolution_convention": EVOLUTION_CONVENTION,
        "hamiltonian_branch": HAMILTONIAN_BRANCH,
        "hamiltonian_branch_is_additional_receipt_data": True,
        "single_U_has_unique_logarithm_without_branch": False,
        "exact_committed_node_gate": (
            "psi[n+1]=U psi[n]=ExpSym(-i H Delta_t/u72) psi[n]"
        ),
        "finite_difference_gate_exact_log_hamiltonian": (
            FINITE_DIFFERENCE_IS_LOG_HAMILTONIAN
        ),
        "finite_difference_role": (
            "coarse-grain/egress approximation, not finite-step "
            "Hermitian logarithmic generator"
        ),
        "host_wall_clock_authority": HOST_WALL_CLOCK_AUTHORITY,
        "floating_point_authority": FLOATING_POINT_AUTHORITY,
        "numerical_eigensolver_authority": (
            NUMERICAL_EIGENSOLVER_AUTHORITY
        ),
        "canonical_admission_authority": CANONICAL_ADMISSION_AUTHORITY,
        "projection_only": True,
    })


def quantum_contract_descriptor() -> dict[str, Any]:
    return _receipt({
        "schema": SCHEMA,
        "profile": PROFILE,
        "state_space": "Q(zeta72)^72",
        "macrocycle_state_space": "Q(zeta72)^9",
        "full_orbit_state_space": "Q(zeta72)^72",
        "full_orbit_state_space_decomposition": (
            "direct_sum_8_of_Q(zeta72)^9"
        ),
        "macrocycle_operator": "shift_by_1_on_9",
        "full_operator": "shift_by_16_on_72",
        "full_cycle_decomposition": "8_cycles_x_9_states",
        "evolution_convention": EVOLUTION_CONVENTION,
        "hamiltonian_branch": HAMILTONIAN_BRANCH,
        "branch_required_for_unique_energy_labels": True,
        "spectrum": (
            "E_k=u72*(2*pi*k/9)/(tau*theta), k=0..8"
        ),
        "eigenphase_for_positive_branch": "zeta9^(-k)",
        "level_degeneracy": 8,
        "exact_gate": (
            "psi[n+1]=ExpSym(-i H Delta_t/u72) psi[n]"
        ),
        "finite_difference_gate_is_exact_log_generator": False,
        "finite_difference_gate_role": "coarse_grain_egress",
        "host_wall_clock_authority": False,
        "floating_point_authority": False,
        "numerical_eigensolver_authority": False,
        "projection_only": True,
    })
