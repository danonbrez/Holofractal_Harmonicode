"""Exact rational Euclidean-mod arithmetic for the P/t/m generator.

This implements only the Euclidean floor-wrap arithmetic already documented
in the HARMONICODE course. It does not evaluate MatrixTimes, NcalcMatrixPower,
or the third argument (30) of the source NcalcEuclideanMod operation.
"""
from __future__ import annotations

from fractions import Fraction


def euclidean_mod_rational(value: Fraction | int, modulus: Fraction | int) -> Fraction:
    """Return value - modulus * floor(value / modulus), exact, 0 <= r < modulus."""
    value = Fraction(value)
    modulus = Fraction(modulus)
    if modulus <= 0:
        raise ValueError("EUCLIDEAN_MODULUS_MUST_BE_POSITIVE")
    quotient = value // modulus
    result = value - quotient * modulus
    assert Fraction(0) <= result < modulus
    return result


def map_exact_cells(matrix: tuple[tuple[Fraction | int, ...], ...],
                    modulus: Fraction | int) -> tuple[tuple[Fraction, ...], ...]:
    """Cellwise floor wrap on an existing exact payload; no MatrixTimes assumption."""
    return tuple(tuple(euclidean_mod_rational(cell, modulus) for cell in row)
                 for row in matrix)


def canonical_wrap_receipt() -> dict:
    samples = (
        (Fraction(1001, 1000), 1),
        (Fraction(-1, 1), 2),
        (Fraction(-1001, 1000), 1),
        (Fraction(3000003, 3125), 248),
    )
    results = tuple({
        "input": str(value),
        "modulus": str(modulus),
        "result": str(euclidean_mod_rational(value, modulus)),
    } for value, modulus in samples)
    return {
        "operation": "EXACT_RATIONAL_EUCLIDEAN_FLOOR_WRAP",
        "samples": results,
        "source_ncalc_third_argument_30": "PRESERVED_UNINTERPRETED",
        "matrix_times": "NOT_EVALUATED",
        "nested_matrix_powers": "NOT_EVALUATED",
        "full_ptm_generator": "NOT_EVALUATED",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(canonical_wrap_receipt(), sort_keys=True, indent=2))
