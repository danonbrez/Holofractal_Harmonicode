"""Pass 220 Lane 5: exact HNAN/Lo Shu phase-gradient witness.

Pure, read-only symbolic constraint verifier; never commits VM81/Hash72/Hash216.
Powers are formal ordered *scalar* u^(n/8) witnesses, not substitutions for
the native HNAN gate or NcalcMatrixPower inverse.
"""
from __future__ import annotations

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


# Each phase carrier is a formal ordered expression multiplied by S=sqrt(K).
# The first expression is (LoShuSymbol*S*carrier - 5). The second
# explicitly expanded expression retains the same S coefficient but has
# address-specific integral offsets. Preserve ordered carrier strings.
LO_SHU_ROWMAJOR = (4, 9, 2, 3, 5, 7, 8, 1, 6)
PHASE_CARRIERS = (
    ("x", "y"), ("y", "x"), ("z", "w"), ("w", "z"),
    ("x+y-z-w",), ("x*y", "z*w"), ("y^2", "w^2"),
    ("z^2", "x^2"), ("y^4", "w^4"),
)
EXPANDED_CONSTANTS = (
    (-4, -4), (-19, -19), (-2, -2), (-13, -13),
    (-10,), (-7, -7), (-8, -8), (-1, -1), (-6, -6),
)


def derive_gradient_offsets():
    """Compute F-G from both exact ordered coefficient arrays.

    Because every S*carrier coefficient agrees, the difference contains
    only exact integer constants; its partial x derivative is identically
    zero where S is differentiable. No float or symbolic evaluation.
    """
    if not (len(LO_SHU_ROWMAJOR) == len(PHASE_CARRIERS)
            == len(EXPANDED_CONSTANTS) == 9):
        raise HNANExactWitnessError("HNAN_NINE_CELL_WIDTH")
    result = []
    for symbol, carriers, constants in zip(
        LO_SHU_ROWMAJOR, PHASE_CARRIERS, EXPANDED_CONSTANTS, strict=True
    ):
        if not (len(carriers) == len(constants) in (1, 2)):
            raise HNANExactWitnessError("HNAN_PAIR_WIDTH")
        if type(symbol) is not int or any(type(v) is not int for v in constants):
            raise HNANExactWitnessError("HNAN_OFFSET_TYPE")
        # In F: symbol*S*carrier - 5, in G: symbol*S*carrier + constant.
        differences = tuple(-5 - constant for constant in constants)
        result.append(differences[0] if len(differences) == 1 else differences)
    return tuple(result)


def verify_gradient_offsets(*, offsets=OFFSETS):
    """Enforce exact F-G=D, implying D_x F == D_x G."""
    actual = derive_gradient_offsets()
    if actual != offsets or actual != OFFSETS:
        raise HNANExactWitnessError("HNAN_GRADIENT_OFFSET_DRIFT")
    return True


# Formal polynomial differentiation over ordered variable names; exact
# integer coefficients only. This checks the classical coordinate projection
# and must not reorder the native noncommutative HNAN phase operators.
VARIABLES = ("x", "y", "z", "w")


def _differentiate_monomials(poly, variable="x"):
    if variable not in VARIABLES:
        raise HNANExactWitnessError("HNAN_DERIVATIVE_AXIS")
    axis = VARIABLES.index(variable)
    result = {}
    for powers, coefficient in poly.items():
        if (not isinstance(powers, tuple) or len(powers) != 4
                or any(type(p) is not int or p < 0 for p in powers)
                or type(coefficient) is not int):
            raise HNANExactWitnessError("HNAN_DERIVATIVE_INEXACT")
        if powers[axis]:
            decreased = list(powers)
            decreased[axis] -= 1
            key = tuple(decreased)
            result[key] = result.get(key, 0) + coefficient * powers[axis]
    return {key: value for key, value in result.items() if value}


def verify_chiral_gradient_projection():
    """Exact coordinate identities underlying the native phase-duality model.

    These do not assert sign-definite feedback or norm preservation; those
    depend on native ordered HNAN transitions, not scalar calculus alone.
    """
    # K=w*x*y*z + x-y+w-z
    K = {(1, 1, 1, 1): 1, (1, 0, 0, 0): 1,
         (0, 1, 0, 0): -1, (0, 0, 1, 0): -1,
         (0, 0, 0, 1): 1}
    # chi=x-y+w-z; coordinate derivative is one.
    chi = {(1, 0, 0, 0): 1, (0, 1, 0, 0): -1,
           (0, 0, 1, 0): -1, (0, 0, 0, 1): 1}
    quartic = {(4, 0, 0, 0): 1}
    if _differentiate_monomials(K) != {
        (0, 1, 1, 1): 1, (0, 0, 0, 0): 1
    }:
        raise HNANExactWitnessError("HNAN_K_CHAIN_RULE_DRIFT")
    if _differentiate_monomials(chi) != {(0, 0, 0, 0): 1}:
        raise HNANExactWitnessError("HNAN_CHIRAL_SHEAR_DRIFT")
    if _differentiate_monomials(quartic) != {(3, 0, 0, 0): 4}:
        raise HNANExactWitnessError("HNAN_QUARTIC_GRADIENT_DRIFT")
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
    verify_chiral_gradient_projection()
    if len({serialization_address(l, b, s)
            for l in range(72) for b in range(8) for s in range(9)}) != 5184:
        raise HNANExactWitnessError("HNAN_5184_BIJECTION")
    for position in range(72):
        reciprocal_hash72(position)
    return {
        "schema": "HHS_PASS220_HNAN_LANE5_EXACT_WITNESS_V1",
        "matrix_factorization_exact": True,
        "gradient_offsets_constant": True,
        "chiral_coordinate_gradient_exact": True,
        "negative_feedback_certified": False,
        "phase_norm_preservation_certified": False,
        "hash72_reciprocal_exact": True,
        "bigint_5184_addresses_bijective": True,
        "candidate_only": True,
        "native_inverse_closure_certified": False,
        "genesis_equivalence_certified": False,
        "vm81_mutation_authority": False,
    }
