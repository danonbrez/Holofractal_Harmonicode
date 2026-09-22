"""Pass 220 I026 exact quantum measurement projector algebra.

T_QM-03A closes the exact projector/weight layer over Q(zeta_72)^9.

It deliberately does NOT grant canonical VM81/Lo-Shu admission authority and
does NOT implement random sampling. Collapse candidates are receipt-bound
projected states plus an exact symbolic normalization carrier.

The cyclotomic field uses:

    Phi_72(x) = x^24 - x^12 + 1

with exact Fraction coefficients in the basis 1,z,...,z^23.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
import re
from typing import Any, Iterable, Sequence

from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import (
    MACROCYCLE_ORDER,
    exact_node_phase,
)

SCHEMA = "HHS_PASS_220_I026_QUANTUM_MEASUREMENT_PROJECTORS_V1"
PROFILE = "PASS220-I026-QUANTUM-MEASUREMENT-PROJECTORS-v1"

CYCLOTOMIC_ORDER = 72
CYCLOTOMIC_DEGREE = 24
ZETA9_EXPONENT = 8
PROJECTOR_DIMENSION = 9

HOST_WALL_CLOCK_AUTHORITY = False
FLOATING_POINT_AUTHORITY = False
RANDOM_SAMPLING_AUTHORITY = False
CANONICAL_ADMISSION_AUTHORITY = False
LO_SHU_ADMISSION_BINDING_CLOSED = False
BORN_WEIGHT_ALGEBRA_CLOSED = True
STOCHASTIC_BORN_FREQUENCY_LAW_CLOSED = False

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class Pass220I026MeasurementError(ValueError):
    pass


def _q(value: Any, name: str = "value") -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise Pass220I026MeasurementError(
            f"{name} must be an exact int or Fraction"
        )
    return Fraction(value)


def _reduce_poly(values: Sequence[int | Fraction]) -> tuple[Fraction, ...]:
    coeffs = [Fraction(v) for v in values]
    if len(coeffs) < CYCLOTOMIC_DEGREE:
        coeffs.extend(
            [Fraction(0)] * (CYCLOTOMIC_DEGREE - len(coeffs))
        )

    # Phi_72(z)=z^24-z^12+1=0 -> z^24=z^12-1.
    for degree in range(len(coeffs) - 1, CYCLOTOMIC_DEGREE - 1, -1):
        coefficient = coeffs[degree]
        if coefficient == 0:
            continue
        coeffs[degree] = Fraction(0)
        coeffs[degree - 12] += coefficient
        coeffs[degree - 24] -= coefficient

    return tuple(coeffs[:CYCLOTOMIC_DEGREE])


@dataclass(frozen=True)
class Cyclotomic72:
    coefficients: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        if len(self.coefficients) != CYCLOTOMIC_DEGREE:
            raise Pass220I026MeasurementError(
                "Cyclotomic72 requires exactly 24 reduced coefficients"
            )
        normalized = tuple(
            _q(value, "coefficient") for value in self.coefficients
        )
        object.__setattr__(self, "coefficients", normalized)

    @classmethod
    def zero(cls) -> "Cyclotomic72":
        return cls((Fraction(0),) * CYCLOTOMIC_DEGREE)

    @classmethod
    def one(cls) -> "Cyclotomic72":
        return cls.rational(1)

    @classmethod
    def rational(
        cls, value: int | Fraction
    ) -> "Cyclotomic72":
        q = _q(value)
        coeffs = [Fraction(0)] * CYCLOTOMIC_DEGREE
        coeffs[0] = q
        return cls(tuple(coeffs))

    @classmethod
    def polynomial(
        cls, values: Sequence[int | Fraction]
    ) -> "Cyclotomic72":
        return cls(_reduce_poly(values))

    def is_zero(self) -> bool:
        return all(value == 0 for value in self.coefficients)

    def scale(self, scalar: int | Fraction) -> "Cyclotomic72":
        q = _q(scalar, "scalar")
        return Cyclotomic72(
            tuple(q * value for value in self.coefficients)
        )

    def __add__(self, other: "Cyclotomic72") -> "Cyclotomic72":
        if not isinstance(other, Cyclotomic72):
            return NotImplemented
        return Cyclotomic72(
            tuple(
                left + right
                for left, right in zip(
                    self.coefficients, other.coefficients
                )
            )
        )

    def __sub__(self, other: "Cyclotomic72") -> "Cyclotomic72":
        if not isinstance(other, Cyclotomic72):
            return NotImplemented
        return Cyclotomic72(
            tuple(
                left - right
                for left, right in zip(
                    self.coefficients, other.coefficients
                )
            )
        )

    def __neg__(self) -> "Cyclotomic72":
        return Cyclotomic72(
            tuple(-value for value in self.coefficients)
        )

    def __mul__(self, other: "Cyclotomic72") -> "Cyclotomic72":
        if not isinstance(other, Cyclotomic72):
            return NotImplemented
        product = [Fraction(0)] * (
            2 * CYCLOTOMIC_DEGREE - 1
        )
        for left_degree, left in enumerate(self.coefficients):
            if left == 0:
                continue
            for right_degree, right in enumerate(
                other.coefficients
            ):
                if right == 0:
                    continue
                product[left_degree + right_degree] += left * right
        return Cyclotomic72.polynomial(product)

    def __pow__(self, power: int) -> "Cyclotomic72":
        if isinstance(power, bool) or not isinstance(power, int):
            raise Pass220I026MeasurementError(
                "cyclotomic power must be an exact integer"
            )
        if power < 0:
            raise Pass220I026MeasurementError(
                "negative generic cyclotomic powers are not admitted"
            )
        result = Cyclotomic72.one()
        base = self
        exponent = power
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def conjugate(self) -> "Cyclotomic72":
        result = Cyclotomic72.zero()
        for degree, coefficient in enumerate(self.coefficients):
            if coefficient == 0:
                continue
            result = result + phase72(-degree).scale(coefficient)
        return result

    def is_self_conjugate(self) -> bool:
        return self.conjugate() == self

    def as_data(self) -> dict[str, Any]:
        terms = []
        for degree, coefficient in enumerate(self.coefficients):
            if coefficient == 0:
                continue
            terms.append(
                [
                    degree,
                    coefficient.numerator,
                    coefficient.denominator,
                ]
            )
        return {
            "field": "Q(zeta72)",
            "basis_degree": CYCLOTOMIC_DEGREE,
            "terms": terms,
        }

    def as_text(self) -> str:
        terms = []
        for degree, coefficient in enumerate(self.coefficients):
            if coefficient == 0:
                continue
            q = (
                f"{coefficient.numerator}/{coefficient.denominator}"
            )
            terms.append(f"({q})*zeta72^{degree}")
        return "0" if not terms else " + ".join(terms)


_GENERATOR = Cyclotomic72.polynomial((0, 1))
_PHASE_CACHE: tuple[Cyclotomic72, ...]


def _build_phase_cache() -> tuple[Cyclotomic72, ...]:
    phases = [Cyclotomic72.one()]
    current = Cyclotomic72.one()
    for _ in range(1, CYCLOTOMIC_ORDER):
        current = current * _GENERATOR
        phases.append(current)
    if current * _GENERATOR != Cyclotomic72.one():
        raise RuntimeError("zeta72 phase cache failed order-72 closure")
    return tuple(phases)


_PHASE_CACHE = _build_phase_cache()


def phase72(exponent: int) -> Cyclotomic72:
    if isinstance(exponent, bool) or not isinstance(exponent, int):
        raise Pass220I026MeasurementError(
            "phase exponent must be an exact integer"
        )
    return _PHASE_CACHE[exponent % CYCLOTOMIC_ORDER]


ExactState = tuple[Cyclotomic72, ...]


def _state(
    amplitudes: Iterable[Cyclotomic72],
) -> ExactState:
    values = tuple(amplitudes)
    if len(values) != PROJECTOR_DIMENSION:
        raise Pass220I026MeasurementError(
            "measurement state must contain exactly 9 amplitudes"
        )
    if any(not isinstance(value, Cyclotomic72) for value in values):
        raise Pass220I026MeasurementError(
            "all amplitudes must be Cyclotomic72 values"
        )
    return values


def zero_state() -> ExactState:
    return _state(
        Cyclotomic72.zero() for _ in range(PROJECTOR_DIMENSION)
    )


def basis_state(index: int) -> ExactState:
    if (
        isinstance(index, bool)
        or not isinstance(index, int)
        or not 0 <= index < PROJECTOR_DIMENSION
    ):
        raise Pass220I026MeasurementError(
            "basis index must satisfy 0 <= index < 9"
        )
    return _state(
        Cyclotomic72.one()
        if position == index
        else Cyclotomic72.zero()
        for position in range(PROJECTOR_DIMENSION)
    )


def fourier_mode(k: int) -> ExactState:
    if (
        isinstance(k, bool)
        or not isinstance(k, int)
        or not 0 <= k < PROJECTOR_DIMENSION
    ):
        raise Pass220I026MeasurementError(
            "mode index must satisfy 0 <= k < 9"
        )
    return _state(
        phase72(ZETA9_EXPONENT * k * position)
        for position in range(PROJECTOR_DIMENSION)
    )


def state_add(left: ExactState, right: ExactState) -> ExactState:
    a = _state(left)
    b = _state(right)
    return _state(x + y for x, y in zip(a, b))


def state_scale(
    scalar: Cyclotomic72,
    state: ExactState,
) -> ExactState:
    if not isinstance(scalar, Cyclotomic72):
        raise Pass220I026MeasurementError(
            "state scalar must be Cyclotomic72"
        )
    values = _state(state)
    return _state(scalar * value for value in values)


def inner_product(
    left: ExactState,
    right: ExactState,
) -> Cyclotomic72:
    a = _state(left)
    b = _state(right)
    total = Cyclotomic72.zero()
    for x, y in zip(a, b):
        total = total + x.conjugate() * y
    return total


def state_norm2(state: ExactState) -> Cyclotomic72:
    return inner_product(state, state)


def projector_overlap(
    state: ExactState,
    outcome: int,
) -> Cyclotomic72:
    values = _state(state)
    mode = fourier_mode(outcome)
    return inner_product(mode, values)


def project_state(
    state: ExactState,
    outcome: int,
) -> ExactState:
    overlap = projector_overlap(state, outcome)
    coefficient = overlap.scale(Fraction(1, PROJECTOR_DIMENSION))
    return state_scale(coefficient, fourier_mode(outcome))


def projector_weight_numerator(
    state: ExactState,
    outcome: int,
) -> Cyclotomic72:
    projected = project_state(state, outcome)
    return state_norm2(projected)


def _sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise Pass220I026MeasurementError(
            f"{name} must be lowercase sha256 hex"
        )
    return value


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return {
        **payload,
        "receipt_sha256": sha256(
            encoded.encode("utf-8")
        ).hexdigest(),
    }


def _state_data(state: ExactState) -> list[dict[str, Any]]:
    return [value.as_data() for value in _state(state)]


def measurement_weights(
    state: ExactState,
    *,
    source_state_receipt_sha256: str,
) -> dict[str, Any]:
    values = _state(state)
    source_sha = _sha(
        source_state_receipt_sha256,
        "source_state_receipt_sha256",
    )
    norm = state_norm2(values)
    if norm.is_zero():
        raise Pass220I026MeasurementError(
            "zero state has no normalized measurement weights"
        )
    if not norm.is_self_conjugate():
        raise Pass220I026MeasurementError(
            "state norm must be self-conjugate"
        )

    numerators = tuple(
        projector_weight_numerator(values, outcome)
        for outcome in range(PROJECTOR_DIMENSION)
    )
    if any(not value.is_self_conjugate() for value in numerators):
        raise Pass220I026MeasurementError(
            "projector weight numerator lost real-subfield closure"
        )

    numerator_sum = Cyclotomic72.zero()
    for value in numerators:
        numerator_sum = numerator_sum + value

    if numerator_sum != norm:
        raise Pass220I026MeasurementError(
            "projector completeness failed exact weight normalization"
        )

    outcomes = []
    for outcome, numerator in enumerate(numerators):
        phase = exact_node_phase(outcome)
        outcomes.append({
            "outcome": outcome,
            "firing_eigenphase": f"zeta72^{phase.exponent}",
            "weight_numerator": numerator.as_data(),
            "weight_denominator": norm.as_data(),
            "weight_carrier": "numerator/total_norm",
            "zero_weight": numerator.is_zero(),
        })

    return _receipt({
        "schema": (
            "HHS_PASS_220_I026_EXACT_MEASUREMENT_WEIGHTS_V1"
        ),
        "profile": PROFILE,
        "source_state_receipt_sha256": source_sha,
        "state_space": "Q(zeta72)^9",
        "state": _state_data(values),
        "total_norm": norm.as_data(),
        "outcomes": outcomes,
        "outcome_count": PROJECTOR_DIMENSION,
        "weights_complete_exactly": numerator_sum == norm,
        "born_weight_algebra_closed": BORN_WEIGHT_ALGEBRA_CLOSED,
        "stochastic_born_frequency_law_closed": (
            STOCHASTIC_BORN_FREQUENCY_LAW_CLOSED
        ),
        "random_sampling_authority": RANDOM_SAMPLING_AUTHORITY,
        "floating_point_authority": FLOATING_POINT_AUTHORITY,
        "projection_only": True,
    })


def collapse_candidate(
    state: ExactState,
    outcome: int,
    *,
    source_state_receipt_sha256: str,
    admission_witness_sha256: str,
) -> dict[str, Any]:
    if (
        isinstance(outcome, bool)
        or not isinstance(outcome, int)
        or not 0 <= outcome < PROJECTOR_DIMENSION
    ):
        raise Pass220I026MeasurementError(
            "outcome must satisfy 0 <= outcome < 9"
        )

    source_sha = _sha(
        source_state_receipt_sha256,
        "source_state_receipt_sha256",
    )
    admission_sha = _sha(
        admission_witness_sha256,
        "admission_witness_sha256",
    )
    values = _state(state)
    weights = measurement_weights(
        values,
        source_state_receipt_sha256=source_sha,
    )
    numerator = projector_weight_numerator(values, outcome)
    if numerator.is_zero():
        raise Pass220I026MeasurementError(
            "zero-weight outcome cannot form a collapse candidate"
        )

    projected = project_state(values, outcome)
    repeated = project_state(projected, outcome)
    if repeated != projected:
        raise Pass220I026MeasurementError(
            "projector repeatability failed"
        )

    excluded = []
    for other in range(PROJECTOR_DIMENSION):
        if other == outcome:
            continue
        orthogonal = project_state(projected, other)
        if orthogonal != zero_state():
            raise Pass220I026MeasurementError(
                "projector orthogonality failed"
            )
        excluded.append(other)

    return _receipt({
        "schema": (
            "HHS_PASS_220_I026_COLLAPSE_CANDIDATE_V1"
        ),
        "profile": PROFILE,
        "source_state_receipt_sha256": source_sha,
        "measurement_receipt_sha256": weights["receipt_sha256"],
        "admission_witness_sha256": admission_sha,
        "outcome": outcome,
        "firing_eigenphase": (
            f"zeta72^{exact_node_phase(outcome).exponent}"
        ),
        "projected_state": _state_data(projected),
        "normalization_carrier": {
            "operation": "divide_by_symbolic_sqrt",
            "norm2": numerator.as_data(),
        },
        "projector_repeatable": True,
        "orthogonal_outcomes_excluded": excluded,
        "canonical_state_mutated": False,
        "canonical_admission_authority": (
            CANONICAL_ADMISSION_AUTHORITY
        ),
        "lo_shu_admission_binding_closed": (
            LO_SHU_ADMISSION_BINDING_CLOSED
        ),
        "admission_witness_semantics_verified": False,
        "random_sampling_authority": RANDOM_SAMPLING_AUTHORITY,
        "floating_point_authority": FLOATING_POINT_AUTHORITY,
        "projection_only": True,
    })


def measurement_contract_descriptor() -> dict[str, Any]:
    return _receipt({
        "schema": SCHEMA,
        "profile": PROFILE,
        "state_space": "Q(zeta72)^9",
        "cyclotomic_polynomial": "x^24-x^12+1",
        "projector_rule": (
            "P_k=|v_k><v_k|/9, "
            "v_k[j]=zeta72^(8*k*j)"
        ),
        "weight_rule": (
            "w_k=<psi|P_k|psi>/<psi|psi>; stored as exact "
            "numerator/total_norm carrier"
        ),
        "completeness_rule": "sum_k P_k=I",
        "orthogonality_rule": "P_k P_r=delta_kr P_k",
        "collapse_candidate_rule": (
            "candidate_k=P_k psi with symbolic sqrt(norm2) "
            "normalization carrier"
        ),
        "born_weight_algebra_closed": True,
        "stochastic_born_frequency_law_closed": False,
        "lo_shu_admission_binding_closed": False,
        "canonical_admission_authority": False,
        "random_sampling_authority": False,
        "host_wall_clock_authority": False,
        "floating_point_authority": False,
        "projection_only": True,
    })
