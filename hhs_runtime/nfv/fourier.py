from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable

from .audio import ExactScalar, ONE, ZERO
from .core import NFVError


@dataclass(frozen=True)
class GaussianRational:
    real: ExactScalar
    imag: ExactScalar = ZERO

    @classmethod
    def from_real(cls, value: ExactScalar | int) -> "GaussianRational":
        return cls(value if isinstance(value, ExactScalar) else ExactScalar(value), ZERO)

    def add(self, other: "GaussianRational") -> "GaussianRational":
        return GaussianRational(self.real.add(other.real), self.imag.add(other.imag))

    def subtract(self, other: "GaussianRational") -> "GaussianRational":
        return GaussianRational(self.real.subtract(other.real), self.imag.subtract(other.imag))

    def multiply(self, other: "GaussianRational") -> "GaussianRational":
        real = self.real.multiply(other.real).subtract(self.imag.multiply(other.imag))
        imag = self.real.multiply(other.imag).add(self.imag.multiply(other.real))
        return GaussianRational(real, imag)

    def scale(self, scalar: ExactScalar) -> "GaussianRational":
        return GaussianRational(self.real.multiply(scalar), self.imag.multiply(scalar))

    def conjugate(self) -> "GaussianRational":
        return GaussianRational(self.real, self.imag.negate())

    def negate(self) -> "GaussianRational":
        return GaussianRational(self.real.negate(), self.imag.negate())

    def is_zero(self) -> bool:
        return self.real.numerator == 0 and self.imag.numerator == 0

    def to_dict(self) -> dict[str, Any]:
        return {"real": self.real.to_dict(), "imag": self.imag.to_dict()}


I = GaussianRational(ZERO, ONE)
NEG_I = GaussianRational(ZERO, ExactScalar(-1))


def _as_real_gaussian(values: Iterable[ExactScalar | int]) -> tuple[GaussianRational, ...]:
    result = tuple(GaussianRational.from_real(value) for value in values)
    if len(result) != 4:
        raise NFVError("NFV_FOURIER_LENGTH_UNSUPPORTED", "exact native Fourier core currently requires length four")
    return result


def dft4(values: Iterable[ExactScalar | int]) -> tuple[GaussianRational, ...]:
    a, b, c, d = _as_real_gaussian(values)
    x0 = a.add(b).add(c).add(d)
    x1 = a.add(b.multiply(NEG_I)).subtract(c).add(d.multiply(I))
    x2 = a.subtract(b).add(c).subtract(d)
    x3 = a.add(b.multiply(I)).subtract(c).add(d.multiply(NEG_I))
    return x0, x1, x2, x3


def inverse_dft4(values: Iterable[GaussianRational]) -> tuple[ExactScalar, ...]:
    coefficients = tuple(values)
    if len(coefficients) != 4:
        raise NFVError("NFV_FOURIER_LENGTH_UNSUPPORTED", "inverse exact Fourier core currently requires length four")
    x0, x1, x2, x3 = coefficients
    quarter = ExactScalar(1, 4)
    samples = (
        x0.add(x1).add(x2).add(x3).scale(quarter),
        x0.add(x1.multiply(I)).subtract(x2).add(x3.multiply(NEG_I)).scale(quarter),
        x0.subtract(x1).add(x2).subtract(x3).scale(quarter),
        x0.add(x1.multiply(NEG_I)).subtract(x2).add(x3.multiply(I)).scale(quarter),
    )
    if any(sample.imag.numerator != 0 for sample in samples):
        raise NFVError("NFV_FOURIER_RECONSTRUCTION_COMPLEX_RESIDUAL", "real source reconstruction produced an imaginary residual")
    return tuple(sample.real for sample in samples)


def classify_phase_interaction(a: GaussianRational, b: GaussianRational) -> str:
    if a.is_zero() and b.is_zero():
        return "ZERO_SUM_CROSSING"
    if a == b:
        return "CONSTRUCTIVE_RESONANCE"
    if a == b.negate():
        return "DESTRUCTIVE_CANCELLATION"
    product = a.multiply(b.conjugate())
    if product.real.numerator == 0 and product.imag.numerator != 0:
        return "ORTHOGONAL_PHASE_LOCK"
    return "PHASE_CONFLICT"


@dataclass(frozen=True)
class FrequencyRegister:
    octave_carry: int
    normalized_ratio: ExactScalar

    def __post_init__(self) -> None:
        value = self.normalized_ratio.fraction
        if not Fraction(1, 1) <= value < Fraction(2, 1):
            raise NFVError("NFV_INVALID_FREQUENCY_REGISTER", "normalized ratio must be in [1,2)")

    @property
    def reconstructed_ratio(self) -> ExactScalar:
        value = self.normalized_ratio.fraction
        if self.octave_carry >= 0:
            value *= 2 ** self.octave_carry
        else:
            value /= 2 ** (-self.octave_carry)
        return ExactScalar.from_fraction(value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "octave_carry": self.octave_carry,
            "normalized_ratio": self.normalized_ratio.to_dict(),
            "reconstructed_ratio": self.reconstructed_ratio.to_dict(),
        }


def decompose_frequency_register(ratio: ExactScalar) -> FrequencyRegister:
    value = ratio.fraction
    if value <= 0:
        raise NFVError("NFV_INVALID_RELATIVE_FREQUENCY", "frequency ratio must be positive")
    octave = 0
    while value >= 2:
        value /= 2
        octave += 1
    while value < 1:
        value *= 2
        octave -= 1
    return FrequencyRegister(octave, ExactScalar.from_fraction(value))
