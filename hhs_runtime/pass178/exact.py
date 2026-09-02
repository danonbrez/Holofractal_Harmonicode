from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from typing import Any, Iterable, Mapping


class ExactPhysicsError(ValueError):
    pass


def reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ExactPhysicsError(f"P178_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            reject_float(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            reject_float(item, f"{path}[{index}]")


@dataclass(frozen=True, order=True)
class ExactRational:
    num: int
    den: int = 1

    def __post_init__(self) -> None:
        if isinstance(self.num, bool) or isinstance(self.den, bool):
            raise ExactPhysicsError("P178_BOOLEAN_NOT_NUMERIC")
        if not isinstance(self.num, int) or not isinstance(self.den, int):
            raise ExactPhysicsError("P178_INTEGER_NUMERATOR_DENOMINATOR_REQUIRED")
        if self.den == 0:
            raise ExactPhysicsError("P178_ZERO_DENOMINATOR")
        n, d = self.num, self.den
        if d < 0:
            n, d = -n, -d
        g = gcd(abs(n), d)
        object.__setattr__(self, "num", n // g)
        object.__setattr__(self, "den", d // g)

    @classmethod
    def coerce(cls, value: Any) -> "ExactRational":
        if isinstance(value, cls):
            return value
        if isinstance(value, bool):
            raise ExactPhysicsError("P178_BOOLEAN_NOT_NUMERIC")
        if isinstance(value, int):
            return cls(value, 1)
        if isinstance(value, (list, tuple)):
            if len(value) != 2:
                raise ExactPhysicsError("P178_EXACT_RATIONAL_PAIR_ARITY")
            num, den = value
            if isinstance(num, bool) or isinstance(den, bool) or not isinstance(num, int) or not isinstance(den, int):
                raise ExactPhysicsError("P178_EXACT_RATIONAL_PAIR_INTEGER_REQUIRED")
            return cls(num, den)
        if isinstance(value, str):
            raw = value.strip()
            if "/" in raw:
                n, d = raw.split("/", 1)
                return cls(int(n), int(d))
            if "." in raw:
                sign = -1 if raw.startswith("-") else 1
                body = raw[1:] if raw[:1] in "+-" else raw
                whole, frac = body.split(".", 1)
                if not whole:
                    whole = "0"
                return cls(sign * int(whole + frac), 10 ** len(frac))
            return cls(int(raw), 1)
        if isinstance(value, Fraction):
            return cls(value.numerator, value.denominator)
        if isinstance(value, float):
            raise ExactPhysicsError("P178_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN")
        raise ExactPhysicsError(f"P178_EXACT_RATIONAL_UNSUPPORTED:{type(value).__name__}")

    def __add__(self, other: Any) -> "ExactRational":
        o = self.coerce(other)
        return ExactRational(self.num * o.den + o.num * self.den, self.den * o.den)

    def __sub__(self, other: Any) -> "ExactRational":
        o = self.coerce(other)
        return ExactRational(self.num * o.den - o.num * self.den, self.den * o.den)

    def __mul__(self, other: Any) -> "ExactRational":
        o = self.coerce(other)
        return ExactRational(self.num * o.num, self.den * o.den)

    def __truediv__(self, other: Any) -> "ExactRational":
        o = self.coerce(other)
        if o.num == 0:
            raise ExactPhysicsError("P178_DIVIDE_BY_ZERO")
        return ExactRational(self.num * o.den, self.den * o.num)

    def __neg__(self) -> "ExactRational":
        return ExactRational(-self.num, self.den)

    def __pow__(self, exponent: int) -> "ExactRational":
        if not isinstance(exponent, int) or isinstance(exponent, bool):
            raise ExactPhysicsError("P178_INTEGER_EXPONENT_REQUIRED")
        if exponent < 0:
            if self.num == 0:
                raise ExactPhysicsError("P178_ZERO_NEGATIVE_POWER")
            return ExactRational(self.den, self.num) ** (-exponent)
        return ExactRational(self.num ** exponent, self.den ** exponent)

    def abs(self) -> "ExactRational":
        return ExactRational(abs(self.num), self.den)

    def is_zero(self) -> bool:
        return self.num == 0

    def as_pair(self) -> list[int]:
        return [self.num, self.den]


@dataclass(frozen=True)
class ComplexExact:
    real: ExactRational
    imag: ExactRational

    @classmethod
    def coerce(cls, value: Any) -> "ComplexExact":
        if isinstance(value, cls):
            return value
        return cls(ExactRational.coerce(value), ExactRational(0))

    def __add__(self, other: Any) -> "ComplexExact":
        o = self.coerce(other)
        return ComplexExact(self.real + o.real, self.imag + o.imag)

    def __sub__(self, other: Any) -> "ComplexExact":
        o = self.coerce(other)
        return ComplexExact(self.real - o.real, self.imag - o.imag)

    def __mul__(self, other: Any) -> "ComplexExact":
        o = self.coerce(other)
        return ComplexExact(
            self.real * o.real - self.imag * o.imag,
            self.real * o.imag + self.imag * o.real,
        )

    def __truediv__(self, other: Any) -> "ComplexExact":
        o = self.coerce(other)
        denom = o.real * o.real + o.imag * o.imag
        if denom.is_zero():
            raise ExactPhysicsError("P178_COMPLEX_DIVIDE_BY_ZERO")
        return ComplexExact(
            (self.real * o.real + self.imag * o.imag) / denom,
            (self.imag * o.real - self.real * o.imag) / denom,
        )

    def conjugate(self) -> "ComplexExact":
        return ComplexExact(self.real, -self.imag)

    def abs2(self) -> ExactRational:
        return self.real * self.real + self.imag * self.imag

    def as_pairs(self) -> list[list[int]]:
        return [self.real.as_pair(), self.imag.as_pair()]


ZERO_C = ComplexExact(ExactRational(0), ExactRational(0))
ONE_C = ComplexExact(ExactRational(1), ExactRational(0))
I_C = ComplexExact(ExactRational(0), ExactRational(1))


@dataclass(frozen=True)
class AlgebraicRoot:
    radicand: ExactRational
    degree: int
    branch: str

    def __post_init__(self) -> None:
        if self.degree < 2:
            raise ExactPhysicsError("P178_ALGEBRAIC_ROOT_DEGREE")
        if self.branch not in {"NONNEGATIVE_REAL", "POSITIVE_REAL", "SYMBOLIC_COMPLEX"}:
            raise ExactPhysicsError("P178_ALGEBRAIC_ROOT_BRANCH")
        if self.branch in {"NONNEGATIVE_REAL", "POSITIVE_REAL"} and self.radicand.num < 0:
            raise ExactPhysicsError("P178_REAL_ROOT_NEGATIVE_RADICAND")

    def payload(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_178_ALGEBRAIC_ROOT_V1",
            "radicand": self.radicand.as_pair(),
            "degree": self.degree,
            "branch": self.branch,
        }


def rational_vector(values: Iterable[Any]) -> tuple[ExactRational, ...]:
    return tuple(ExactRational.coerce(v) for v in values)
