"""Exact read-only Lane 5 dyadic virtual-register candidates.

No VM81 admission, Hash72 mint, Hash216 persistence or canonical mutation.
Exact Fraction identities are projections, never OP_11 constitutive receipts.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt

RADIX = 72
WIDTH = 72
VM5184 = 5184

def _integer(value: int, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} requires an exact integer")
    return value

def dyadic(exponent: int) -> Fraction:
    n = _integer(exponent, "exponent")
    return Fraction(1 << n, 1) if n >= 0 else Fraction(1, 1 << -n)

def shell(depth: int) -> tuple[tuple[int, Fraction], ...]:
    n = _integer(depth, "depth")
    if n < 0:
        raise ValueError("negative shell depth")
    return tuple((k, dyadic(k)) for k in range(-n, n + 1))

def reciprocal_witness(exponent: int) -> bool:
    return dyadic(exponent) * dyadic(-exponent) == Fraction(1)

def encode_address(digits: tuple[int, ...]) -> int:
    if not isinstance(digits, tuple) or len(digits) != WIDTH:
        raise ValueError("expected 72 ordered radix-72 digits")
    result = 0
    for digit in reversed(digits):
        v = _integer(digit, "address digit")
        if not 0 <= v < RADIX:
            raise ValueError("radix-72 digit outside 0..71")
        result = result * RADIX + v
    return result

def decode_address(index: int) -> tuple[int, ...]:
    value = _integer(index, "address")
    if not 0 <= value < RADIX ** WIDTH:
        raise ValueError("address outside 72**72")
    result = []
    for _ in range(WIDTH):
        value, digit = divmod(value, RADIX)
        result.append(digit)
    return tuple(result)

def hydration_address(row: int, column: int) -> int:
    i = _integer(row, "row")
    j = _integer(column, "column")
    if not 0 <= i < RADIX or not 0 <= j < RADIX:
        raise ValueError("hydration coordinate outside 72x72")
    return RADIX * i + j

@dataclass(frozen=True)
class VirtualRegister:
    address: tuple[int, ...]
    exponent: int
    phase: str
    cell_type: str
    constructor: str
    provenance: str

    def __post_init__(self) -> None:
        encode_address(self.address)
        _integer(self.exponent, "exponent")
        for key in ("phase", "cell_type", "constructor", "provenance"):
            if not isinstance(getattr(self, key), str) or not getattr(self, key):
                raise ValueError(f"{key} must be a nonempty provenance-bearing string")

    @property
    def index(self) -> int:
        return encode_address(self.address)

    @property
    def quantization(self) -> Fraction:
        return dyadic(self.exponent)

def symmetric_witness(center: Fraction, exponent: int) -> dict[str, object]:
    """Rational projection where sqrt(2**n) is rational, else symbolic."""
    if type(center) is not Fraction:
        raise TypeError("center must be an exact Fraction")
    n = _integer(exponent, "exponent")
    delta = dyadic(n)
    if n % 2:
        return {"center": center, "delta": delta,
                "displacement": ("sqrt", delta),
                "p": None, "q": None,
                "pq": center * center - delta,
                "sum": 2 * center, "status": "SYMBOLIC_UNADMITTED"}
    d = dyadic(n // 2)
    p, q = center - d, center + d
    assert p + q == 2 * center and center * center - p * q == delta
    return {"center": center, "delta": delta, "displacement": d,
            "p": p, "q": q, "pq": p * q,
            "sum": p + q, "status": "EXACT_PROJECTION_UNADMITTED"}

def prime_center_witness(prime: int) -> dict[str, int]:
    """Candidate unit-defect witness with exact primality guard."""
    p = _integer(prime, "prime")
    if p < 3 or p % 2 == 0:
        raise ValueError("odd prime center required")
    for d in range(3, isqrt(p) + 1, 2):
        if p % d == 0:
            raise ValueError("center is composite")
    left, right = p - 1, p + 1
    assert p * p - left * right == 1
    return {"P": p, "p": left, "q": right, "modulus": left * right,
            "square": p * p, "defect": 1}
