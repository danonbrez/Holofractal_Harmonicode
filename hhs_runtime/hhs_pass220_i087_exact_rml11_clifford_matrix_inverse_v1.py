"""Pass220 I087: exact RML10/RML11 Clifford lift of the I086 nine-cell matrix.

Uses the *existing* Pass219 Cl_(0,8)->M16(R) primitive matrices as a
mathematically exact, but PROJECTION-SCOPED representation. The ordered
source denominator becomes 3x3 blocks of 16x16 integer matrices, hence
M48(Q). Construct and verify both sides of its rational inverse without
floating-point, symbolic simplification, reordering, or a substitute
HHS native VM81 matrix operator.

Invertibility in this inherited Clifford module is not automatically
invertibility in the native HHS tensor algebra, nor a Hash72 receipt.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_i086_ordered_3x3_vm5184_hash72_matrix_v1 import (
    MATRIX, SOURCE, SOURCE_MATRIX_CENTER, _parse_cell_expression,
    formalize_i086,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import (
    hash72 as inherited_i069_candidate_hash72,
)
from hhs_runtime.pass219.phase_clifford_intertwiner import (
    _channel_action_matrices, _matmul,
    _identity, _zero, _add, _scale,
    build_one_gyroscope_clifford_channel_actions,
)
from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import HNAN_CENTER_EXPRESSION

SCHEMA = "HHS_PASS220_I087_RML11_EXACT_MATRIX_QUOTIENT_INVERSE_V1"
BLOCK_ORDER = 16
TENSOR_DIM = 3
LIFT_ORDER = BLOCK_ORDER * TENSOR_DIM
EXPECTED_DETERMINANT = 10485760000
ORDERED_PRIMITIVES = ("x", "y", "z", "w")
DECLARED_PRODUCTS = ("xy", "yx", "zw", "wz")
EXTENDED_PRODUCT = "wx"


class I087ExactCliffordError(ValueError):
    pass


def _original_rml11_actions() -> dict[str, tuple[tuple[int, ...], ...]]:
    """Read the real original Pass219 RML11 channel operator matrices."""
    originals = _channel_action_matrices()
    if any(name not in originals for name in (*ORDERED_PRIMITIVES, *DECLARED_PRODUCTS)):
        raise I087ExactCliffordError("original RML11 phase channels missing")
    if any(len(originals[name]) != 16 or any(len(r) != 16 for r in originals[name])
           for name in (*ORDERED_PRIMITIVES, *DECLARED_PRODUCTS)):
        raise I087ExactCliffordError("original RML11 Cl(0,8) dimensions changed")

    actions = {name: originals[name] for name in
               (*ORDERED_PRIMITIVES, *DECLARED_PRODUCTS)}
    for product in DECLARED_PRODUCTS:
        if actions[product] != _matmul(actions[product[0]], actions[product[1]]):
            raise I087ExactCliffordError("original ordered phase projection changed")
    # wx is NOT part of the inherited eight-channel registry. It is an
    # exact ordered *composite* in the existing RML11 Clifford projection.
    actions[EXTENDED_PRODUCT] = _matmul(actions["w"], actions["x"])
    if actions["wx"] == _matmul(actions["w"], actions["z"]):
        raise I087ExactCliffordError("w*x was aliased to w*z")
    if actions["xy"] == actions["yx"] or actions["zw"] == actions["wz"]:
        raise I087ExactCliffordError("native ordered signs were collapsed")
    return actions


def _cell_block(
    expression: str,
    actions: Mapping[str, tuple[tuple[int, ...], ...]],
) -> tuple[tuple[int, ...], ...]:
    cell = _parse_cell_expression(expression)
    acc = _zero(BLOCK_ORDER)
    for term in cell["ordered_terms"]:
        op = term["operand"]
        if op["head"] == "HHS_ORDERED_PRODUCT":
            name = op["source_token"]
            left = op["left"]["symbol"]
            right = op["right"]["symbol"]
            product = _matmul(actions[left],actions[right])
            if product != actions[name]:
                raise I087ExactCliffordError("source order mismatch for product")
            next_matrix = product
        elif op["head"] == "NATIVE_PHASE_ADDRESS":
            next_matrix = actions[op["symbol"]]
        else:
            raise I087ExactCliffordError("unknown native tensor phase operation")
        acc = _add(acc, _scale(next_matrix,term["sign"]))
    return acc


def original_i086_rml11_block_matrix() -> tuple[tuple[int, ...], ...]:
    """Lift the unchanged nine HHS source expressions into original Cl matrices."""
    if SOURCE_MATRIX_CENTER != HNAN_CENTER_EXPRESSION:
        raise I087ExactCliffordError("source HNAN center diverged")
    actions = _original_rml11_actions()
    blocks = tuple(
        tuple(_cell_block(MATRIX[row][col], actions) for col in range(3))
        for row in range(3)
    )
    matrix = tuple(
        tuple(
            value
            for block_col in range(3)
            for value in blocks[block_row][block_col][inner_row]
        )
        for block_row in range(3) for inner_row in range(BLOCK_ORDER)
    )
    if len(matrix) != LIFT_ORDER or any(len(row) != LIFT_ORDER for row in matrix):
        raise I087ExactCliffordError("I086 matrix Cl(0,8) block dimensions wrong")
    if blocks[0][2] != actions["wx"]:
        raise I087ExactCliffordError("new wx source product not projected")
    return matrix


def _exact_inverse(
    matrix: tuple[tuple[int, ...], ...],
) -> tuple[tuple[tuple[Fraction, ...], ...] | None, Fraction, int]:
    """Pure exact Fraction Gauss-Jordan, no host floats or implicit cofactor order."""
    n = len(matrix)
    if n != LIFT_ORDER or any(len(row) != n for row in matrix):
        raise I087ExactCliffordError("typed 48x48 Clifford projection required")
    if any(isinstance(v, bool) or not isinstance(v, (int, Fraction))
           for row in matrix for v in row):
        raise I087ExactCliffordError("exact matrix input required; floats forbidden")
    a = [[Fraction(v) for v in row] for row in matrix]
    b = [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    determinant = Fraction(1)
    swaps = 0
    for col in range(n):
        pivot_row = next((i for i in range(col,n) if a[i][col] != 0),None)
        if pivot_row is None:
            return None, Fraction(0), swaps
        if pivot_row != col:
            a[col],a[pivot_row] = a[pivot_row],a[col]
            b[col],b[pivot_row] = b[pivot_row],b[col]
            determinant = -determinant
            swaps += 1
        pivot = a[col][col]
        determinant *= pivot
        a[col] = [v/pivot for v in a[col]]
        b[col] = [v/pivot for v in b[col]]
        for row in range(n):
            if row == col:
                continue
            factor = a[row][col]
            if factor:
                a[row] = [left-factor*right for left,right in zip(a[row],a[col])]
                b[row] = [left-factor*right for left,right in zip(b[row],b[col])]
    if a != [[Fraction(int(i==j)) for j in range(n)] for i in range(n)]:
        raise I087ExactCliffordError("exact row operation did not produce identity")
    return tuple(tuple(row) for row in b), determinant, swaps


def _exact_fraction_record(v: Fraction)->dict[str,int]:
    return {"numerator":v.numerator,"denominator":v.denominator}


def _fingerprint_inverse(inv: tuple[tuple[Fraction,...],...])->str:
    encoded=[
        [[v.numerator,v.denominator] for v in row] for row in inv
    ]
    return sha256(json.dumps(encoded,separators=(",",":"),allow_nan=False).encode()).hexdigest()


def verify_i087_exact_clifford_inverse(*, include_inverse:bool=False) ->dict[str,Any]:
    """Provide real mathematically verified two-sided inverse in Cl(0,8) projection."""
    parent = formalize_i086()
    if parent["source_equation"] != SOURCE or parent["canonical_hash72_equation_proven"] is not False:
        raise I087ExactCliffordError("I086 source and authority boundary mismatch")
    source_matrix = original_i086_rml11_block_matrix()
    inverse, determinant, pivot_swaps = _exact_inverse(source_matrix)
    if inverse is None or determinant != Fraction(EXPECTED_DETERMINANT):
        raise I087ExactCliffordError("I086 exact RML11 matrix lost expected inverse/determinant")
    identity = _identity(LIFT_ORDER)
    left = _matmul(source_matrix,inverse)
    right = _matmul(inverse,source_matrix)
    if left != identity or right != identity:
        raise I087ExactCliffordError("I087 exact Clifford left/right inverse failed")
    # Carry out the user's 5184 / M left/right quotient in the exact
    # Clifford *projection*. This is not original VM81 matrix division.
    projected_quotient = tuple(
        tuple(Fraction(5184)*coefficient for coefficient in row)
        for row in inverse
    )
    scaled_identity = _scale(identity, 5184)
    if (
        _matmul(source_matrix, projected_quotient) != scaled_identity
        or _matmul(projected_quotient, source_matrix) != scaled_identity
    ):
        raise I087ExactCliffordError("exact 5184/M projected quotient residual")
    # Only original RML11 projection; do not conflate generator ancestry
    # with the original VM81 temporal Hash216 state.
    inherited = build_one_gyroscope_clifford_channel_actions()
    if inherited.get("schema") != "HHS_PASS219_RML11_ONE_GYROSCOPE_CLIFFORD_CHANNEL_ACTIONS_V1":
        raise I087ExactCliffordError("original RML11 Clifford generator proof missing")
    source_matrix_hash = sha256(json.dumps(
        source_matrix,separators=(",",":"),allow_nan=False
    ).encode()).hexdigest()
    quotient_rationals = [
        [[v.numerator,v.denominator] for v in row] for row in projected_quotient
    ]
    quotient_sha = sha256(json.dumps(
        quotient_rationals,separators=(",",":"),allow_nan=False
    ).encode()).hexdigest()
    candidate_hash72 = inherited_i069_candidate_hash72({
        "schema":SCHEMA,
        "original_i086_source_sha256":parent["source_identity_sha256"],
        "original_rml11_witness_sha256":inherited["witness_sha256"],
        "exact_rational_clifford_quotient":quotient_rationals,
        "authority":"CANDIDATE_PROJECTION_ONLY",
    })
    if not isinstance(candidate_hash72,str) or len(candidate_hash72)!=72:
        raise I087ExactCliffordError("inherited I069 candidate hash72 malformed")
    witness: dict[str,Any] = {
        "schema":SCHEMA,
        "i086_source":SOURCE,
        "i086_source_sha256":parent["source_identity_sha256"],
        "original_rml11_channel_witness_sha256":inherited["witness_sha256"],
        "original_rml10_cl08_witness_sha256":inherited["rml10_cl08_witness_sha256"],
        "actual_rml11_generator_matrices_executed":True,
        "mathematically_exact_48x48_lift_executed":True,
        "matrix_order":LIFT_ORDER,
        "original_i086_nine_ordered_cells_executed_in_clifford_projection":True,
        "wx_constructed_as_ordered_w_times_x":True,
        "wx_not_promoted_to_original_registered_phase8":True,
        "original_hnan_center_preserved":True,
        "matrix_clifford_projection_sha256":source_matrix_hash,
        "inverse_clifford_projection_sha256":_fingerprint_inverse(inverse),
        "determinant":_exact_fraction_record(determinant),
        "determinant_nonzero":True,
        "exact_projected_5184_over_matrix_quotient_executed":True,
        "exact_projected_quotient_sha256":quotient_sha,
        "original_i069_candidate_hash72_of_computed_quotient":candidate_hash72,
        "candidate_hash72_of_quotient_is_not_canonical_ledger":True,
        "exact_projected_left_quotient_identity":True,
        "exact_projected_right_quotient_identity":True,
        "exact_pivot_row_swaps":pivot_swaps,
        "exact_two_sided_inverse_verified":True,
        "exact_left_product_identity":True,
        "exact_right_product_identity":True,
        "original_vm81_native_tensor_invertibility_proven":False,
        "native_5184_over_matrix_equals_canonical_hash72_proven":False,
        "native_matrix_inverse_operator_admitted":False,
        "canonical_hash72_minted":False,
        "canonical_hash216_transition_admitted":False,
        "signed_vm81_mutation":False,
        "projection_only":True,
        "candidate_only":True,
        "floating_point_authority":False,
    }
    if include_inverse:
        witness["exact_inverse_coefficients"] = [
            [_exact_fraction_record(v) for v in row] for row in inverse
        ]
        witness["exact_projected_quotient_coefficients"] = [
            [_exact_fraction_record(v) for v in row] for row in projected_quotient
        ]
    return witness
