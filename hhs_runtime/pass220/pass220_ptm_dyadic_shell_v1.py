"""Exact dyadic three-component shell witness for the P/t/m generator.

Preserves source structure: Delta=(2^n+(-2^0,+2^0,2^n))/
(2^m+(-2^0,+2^0,2^m)).
No tensor division semantics or Ncalc value semantics are asserted.
"""
from __future__ import annotations

from fractions import Fraction

DELTA_SOURCE = "∆=2^n+(-2⁰,+2⁰,2ⁿ)/2^m+(-2⁰,+2⁰,2^m)"
REFERENCE_M = 248
SWEEP_M = (247, 248, 249)


def shell(k: int) -> tuple[int, int, int]:
    if type(k) is not int or k < 0:
        raise ValueError("DELTA_EXPONENT_MUST_BE_NONNEGATIVE_INTEGER")
    power = 1 << k
    return (power - 1, power + 1, power << 1)


def exact_componentwise_probe(n: int, m: int) -> tuple[Fraction, Fraction, Fraction]:
    """One explicitly labeled coordinate projection, not the native tensor quotient."""
    a, b = shell(n), shell(m)
    return tuple(Fraction(a[i], b[i]) for i in range(3))


def witness(n: int = REFERENCE_M) -> dict:
    top = shell(n)
    rows = []
    for m in SWEEP_M:
        bottom = shell(m)
        rows.append({
            "n": n,
            "m": m,
            "numerator_components": top,
            "denominator_components": bottom,
            "coordinate_quotient_probe": tuple(str(v) for v in exact_componentwise_probe(n, m)),
            "native_tensor_quotient": "NOT_EVALUATED",
            "ncalc_matrix_output": "NOT_EVALUATED",
        })
    return {
        "source": DELTA_SOURCE,
        "reference_m": REFERENCE_M,
        "rows": rows,
        "status": "EXACT_DYADIC_COMPONENT_WITNESS_ONLY",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(witness(), indent=2, ensure_ascii=False))
