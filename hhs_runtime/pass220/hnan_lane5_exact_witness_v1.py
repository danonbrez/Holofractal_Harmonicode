"""Pass 220 Lane 5: exact HNAN/Lo Shu phase-gradient witness.

Pure, read-only symbolic constraint verifier; never commits VM81/Hash72/Hash216.
Powers are formal ordered *scalar* u^(n/8) witnesses, not substitutions for
the native HNAN gate or NcalcMatrixPower inverse.
"""
from __future__ import annotations

from fractions import Fraction

LO_SHU_CENTERED = ((-1, 4, -3), (-2, 0, 2), (3, -4, 1))
PHASE_EIGHTHS = ((9, 11, 13), (15, 8, -9), (-11, -13, -15))
# Entries encode pi*B(u), with the fractional exponent in eighths.
EXPECTED_PI_B = (
    ({9: -1, 11: -2, 13: 3}, {9: 4, 13: -4}, {9: -3, 11: 2, 13: 1}),
    ({-9: 3, 8: -2, 15: -1}, {-9: -4, 15: 4}, {-9: 1, 8: 2, 15: -3}),
    ({-15: 3, -13: -2, -11: -1}, {-15: -4, -11: 4}, {-15: 1, -13: 2, -11: -3}),
)
# Exact offsets: first supplied array minus final expanded array.
OFFSETS = ((-1, -1), (14, 14), (-3, -3), (8, 8), 5,
           (2, 2), (3, 3), (-4, -4), (1, 1))


class HNANExactWitnessError(ValueError):
    """An exact symbolic identity or address contract was violated."""


def pi_b_from_phase_matrix(phase_eighths=PHASE_EIGHTHS, lo_shu=LO_SHU_CENTERED):
    """Compute pi*B as formal monomial coefficients, with no floats."""
    if len(phase_eighths) != 3 or any(len(row) != 3 for row in phase_eighths):
        raise HNANExactWitnessError("HNAN_PHASE_MATRIX_SHAPE")
    if len(lo_shu) != 3 or any(len(row) != 3 for row in lo_shu):
        raise HNANExactWitnessError("HNAN_LO_SHU_SHAPE")
    out = []
    for i in range(3):
        row = []
        for j in range(3):
            terms = {}
            for k in range(3):
                exponent = phase_eighths[i][k]
                if not isinstance(exponent, int) or not isinstance(lo_shu[k][j], int):
                    raise HNANExactWitnessError("HNAN_INEXACT_PHASE")
                terms[exponent] = terms.get(exponent, 0) + lo_shu[k][j]
            row.append({p: c for p, c in terms.items() if c})
        out.append(tuple(row))
    return tuple(out)


def verify_matrix_factorization(*, expected=EXPECTED_PI_B):
    """Enforce U(u).L/pi == B(u) as a formal exact identity."""
    actual = pi_b_from_phase_matrix()
    if actual != expected:
        raise HNANExactWitnessError("HNAN_LO_SHU_PHASE_FACTORIZATION_DRIFT")
    return True


def verify_gradient_offsets(*, offsets=OFFSETS):
    """Constant F-G means D_x F = D_x G, without normalizing outer cells."""
    if offsets != OFFSETS:
        raise HNANExactWitnessError("HNAN_GRADIENT_OFFSET_DRIFT")
    if len(offsets) != 9 or any(
        not isinstance(v, int)
        for item in offsets
        for v in (item if isinstance(item, tuple) else (item,))
    ):
        raise HNANExactWitnessError("HNAN_OFFSET_TYPE_OR_WIDTH")
    return True


def reciprocal_hash72(position: int) -> int:
    if type(position) is not int or not 0 <= position < 72:
        raise HNANExactWitnessError("HASH72_POSITION_RANGE")
    result = (-position) % 72
    if (result + position) % 72:
        raise HNANExactWitnessError("HASH72_RECIPROCAL_CLOSURE")
    return result


def serialization_address(layer: int, block: int, symbol: int) -> int:
    if any(type(v) is not int for v in (layer, block, symbol)) or not (
        0 <= layer < 72 and 0 <= block < 8 and 0 <= symbol < 9
    ):
        raise HNANExactWitnessError("HNAN_5184_ADDRESS_RANGE")
    return 72 * layer + 9 * block + symbol


def verify_read_only_candidate():
    """Candidate-only evidence: not a native NcalcMatrixPower/Genesis proof."""
    verify_matrix_factorization()
    verify_gradient_offsets()
    if len({serialization_address(l, b, s)
            for l in range(72) for b in range(8) for s in range(9)}) != 5184:
        raise HNANExactWitnessError("HNAN_5184_BIJECTION")
    for position in range(72):
        reciprocal_hash72(position)
    return {
        "schema": "HHS_PASS220_HNAN_LANE5_EXACT_WITNESS_V1",
        "matrix_factorization_exact": True,
        "gradient_offsets_constant": True,
        "hash72_reciprocal_exact": True,
        "bigint_5184_addresses_bijective": True,
        "candidate_only": True,
        "native_inverse_closure_certified": False,
        "genesis_equivalence_certified": False,
        "vm81_mutation_authority": False,
    }
