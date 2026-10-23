"""Pass220 I086: source-faithful nine-cell ordered VM5184/Hash72 matrix.

The new supplied expression has one 3x3 tensor matrix DENOMINATOR,
not an ordinary commutative scalar denominator. Never compute a
matrix determinant/inverse and use it as the native ordered quotient.
The inherited Hash72 word is a typed cryptographic witness, not the
5184-address/72x72 geometry or an evaluated fraction.

Source: (81*64)/((yx,y+w,wx),(-xy-wz,
 x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_i085_x_over_u_rational_vm81_hash72_crosswalk_v1 import (
    encode_address, formalize_i085,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import (
    hash72 as original_i069_hash72_candidate,
)
from hhs_runtime.hhs_pass220_i071_shared_root_phase_gear_loop_closure_v1 import (
    PHASE_BASIS, build_nucleus_qudit_surface, encode_phase_slot,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import LO_SHU
from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import HNAN_CENTER_EXPRESSION

SCHEMA = "HHS_PASS220_I086_ORDERED_3X3_VM5184_HASH72_MATRIX_QUOTIENT_V1"
SOURCE = "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72"
SOURCE_NUMERATOR = "81*64"
SOURCE_DENOMINATOR = "((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))"
SOURCE_RESULT = "hash72"
MATRIX = (
    ("yx", "y+w", "wx"),
    ("-xy-wz", "x+y-z-w+xy+yx-zw-wz", "-zw-yx"),
    ("xy", "x-z", "zw"),
)
SOURCE_MATRIX_CENTER = MATRIX[1][1]
PRIMITIVES = frozenset(("x", "y", "z", "w"))
ORIGINAL_ORDERED_PRODUCTS = frozenset(("xy", "yx", "zw", "wz"))
EXPLICIT_EXTENDED_PRODUCT = "wx"
TOKENS = ("xy", "yx", "zw", "wz", "wx", "x", "y", "z", "w")
LEXER = re.compile(r"[+-]?(?:xy|yx|zw|wz|wx|x|y|z|w)")
NATIVE_OBLIGATIONS = (
    "original-Matrix-Denominator:directed-native-quotient-semantics",
    "ordered-wx:distinct-w*x-channel-not-in-inherited-eight-basis",
    "matrix-native-inverse:left-right-and-nonzero-inversion-witness",
    "matrix-center:original-HNAN-ordered-constraint-source-and-phase-history",
    "numerator-5184:VM81-81x64-position-count-not-scalar-tensor-amplitude",
    "Hash72-result:canonical-72-character-ledger-admission-not-72x72-index-grid",
    "nine-matrix-polynomials:exact-Lo-Shu-address-provenance",
    "u72-and-x-over-u:phase-root-branch-consistency-from-I085",
    "Hash216:previous-current-receipt-lineage-and-typed-RNA-binding",
    "signed-VM81:original-singleton-environmental-mutation-gate",
)


class I086OrderedMatrixError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _scalar_exact_index(value: Any, name: str, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < maximum:
        raise I086OrderedMatrixError(f"{name} requires bounded exact integer")
    return value


def _parse_cell_expression(text: str) -> dict[str, Any]:
    """Parse only source's ordered ±primitive and ±two-letter products.

    Preserve original order and sign at each addend. Any unseen variable,
    magnitude or operator is not silently admitted.
    """
    if not isinstance(text, str) or not text:
        raise I086OrderedMatrixError("source matrix expression required")
    pos = 0
    ordered_terms = []
    for match in LEXER.finditer(text):
        if match.start() != pos:
            raise I086OrderedMatrixError("malformed/unregistered native operator")
        raw = match.group()
        sign = -1 if raw.startswith("-") else 1
        token = raw[1:] if raw.startswith(("-", "+")) else raw
        if len(token) == 2:
            if token not in ORIGINAL_ORDERED_PRODUCTS and token != EXPLICIT_EXTENDED_PRODUCT:
                raise I086OrderedMatrixError("unknown ordered phase product")
            operand = {
                "head": "HHS_ORDERED_PRODUCT",
                "left": {"head": "NATIVE_PHASE_ADDRESS", "symbol": token[0]},
                "right": {"head": "NATIVE_PHASE_ADDRESS", "symbol": token[1]},
                "source_token": token,
                "registered_original_phase8": token in ORIGINAL_ORDERED_PRODUCTS,
                "extended_wx_requires_native_basis_admission": token == EXPLICIT_EXTENDED_PRODUCT,
            }
        elif token in PRIMITIVES:
            operand = {"head": "NATIVE_PHASE_ADDRESS", "symbol": token}
        else:
            raise I086OrderedMatrixError("unregistered primitive phase channel")
        ordered_terms.append({
            "sign": sign,
            "original_lexeme": raw,
            "operand": operand,
        })
        pos = match.end()
    if pos != len(text) or not ordered_terms:
        raise I086OrderedMatrixError("incomplete source cell expression")
    if "".join(t["original_lexeme"] for t in ordered_terms) != text:
        raise I086OrderedMatrixError("ordered source reconstruction mismatch")
    return {
        "head": "HHS_SOURCE_ORDERED_SIGNED_SUM",
        "source": text,
        "ordered_terms": ordered_terms,
        "commute_terms_without_original_proof": False,
        "evaluate_native_products_as_host_scalar": False,
    }


def matrix_cell(row: int, column: int) -> dict[str, Any]:
    r = _scalar_exact_index(row, "matrix row", 3)
    c = _scalar_exact_index(column, "matrix column", 3)
    if SOURCE_MATRIX_CENTER != HNAN_CENTER_EXPRESSION:
        raise I086OrderedMatrixError("original inherited HNAN center changed")
    value = LO_SHU[r][c]
    source = MATRIX[r][c]
    return {
        "row": r, "column": c,
        "lo_shu_local_address": 3*r+c,
        "lo_shu_value": value,
        "native_matrix_expression": source,
        "native_ordered_ast": _parse_cell_expression(source),
        "native_tensor_value_executed": False,
        "matrix_cell_scalarized": False,
        "original_hnan_center_unchanged": (r,c) != (1,1) or source == HNAN_CENTER_EXPRESSION,
    }


def matrix_quotient_ast() -> dict[str, Any]:
    cells = [[matrix_cell(r,c) for c in range(3)] for r in range(3)]
    return {
        "head": "HHS_ORDERED_EQUATION",
        "source": SOURCE,
        "left": {
            "head": "HHS_ORDERED_MATRIX_QUOTIENT",
            "numerator": {
                "head": "ORIGINAL_VM81_64_BIT_COORDINATE_CARDINALITY",
                "source": SOURCE_NUMERATOR,
                "vm81_cells": 81,
                "x86_64_word_bits": 64,
                "exact_integer_cardinality": 5184,
                "represents_arbitrary_tensor_payload_values": False,
            },
            "denominator": {
                "head": "HHS_POSITIONED_3X3_ORDERED_PHASE_MATRIX",
                "source": SOURCE_DENOMINATOR,
                "row_order": ["r0", "r1", "r2"],
                "cells": cells,
                "native_inverse_computed": False,
                "native_matrix_noncommutative_division_proven": False,
            },
            "division_side_and_native_inverse_proven": False,
        },
        "right": {
            "head": "HHS_TYPED_HASH72_RESULT_OBLIGATION",
            "source": SOURCE_RESULT,
            "canonical_72_glyph_ledger_equality_proven": False,
            "hash216_transition_witness_proven": False,
        },
        "source_ordered_equality_not_symmetric_scalar_rewrite": True,
    }


def _root_from_source() -> str:
    return sha256(SOURCE.encode("utf-8")).hexdigest()


def lift_vm5184_matrix_position(s5184: int) -> dict[str, Any]:
    """Bound I086 matrix address to actual earlier I085/Pass186 map."""
    pos = _scalar_exact_index(s5184,"VM5184 position",5184)
    inherited = encode_address(pos)
    vm = inherited["vm81"]
    nucleus, local_cell = divmod(vm["cell"], 9)
    row,col = divmod(local_cell,3)
    basis = vm["operation64"]%8
    class8 = vm["operation64"]//8
    matrix = matrix_cell(row,col)
    if not (0<=nucleus<9 and 0<=basis<8 and 0<=class8<8):
        raise I086OrderedMatrixError("native VM81 address not admitted")
    return {
        "schema": f"{SCHEMA}_POSITION_LIFT",
        "s5184": pos,
        "vm81_nucleus": nucleus,
        "vm81_cell": vm["cell"],
        "vm81_operation64": vm["operation64"],
        "operation_class8": class8,
        "operation_basis8": basis,
        "ordered_operation_symbol": PHASE_BASIS[basis],
        "i071_phase_slot": encode_phase_slot(basis,local_cell),
        "matrix_cell": matrix,
        "inherited_i085_hash72_geometry": inherited["hash72_address_geometry"],
        "inherited_i085_rational_exponent": inherited["typed_constructor"]["exponent"],
        "original_vm81_tensor_payload_evaluated": False,
        "candidate_only": True,
    }


def enumerate_all_vm5184_matrix_positions() -> dict[str, Any]:
    """Fully exercise inherited 81*64 positions and 9x9x8x8 membership."""
    seen: set[tuple[int,int,int,int]] = set()
    seen_lo_shu: set[tuple[int,int]] = set()
    for s in range(5184):
        carrier=lift_vm5184_matrix_position(s)
        matrix=carrier["matrix_cell"]
        tuple4=(carrier["vm81_nucleus"],
                matrix["lo_shu_local_address"],
                carrier["operation_class8"],carrier["operation_basis8"])
        if tuple4 in seen:
            raise I086OrderedMatrixError("native nine-matrix tensor location aliased")
        seen.add(tuple4)
        seen_lo_shu.add((matrix["row"],matrix["column"]))
        if matrix["native_matrix_expression"] != MATRIX[matrix["row"]][matrix["column"]]:
            raise I086OrderedMatrixError("matrix source text drift")
    if len(seen)!=5184 or len(seen_lo_shu)!=9:
        raise I086OrderedMatrixError("native 5184/Lo-Shu geometry incomplete")
    return {
        "all_5184_position_lifts_executed":True,
        "original_matrix_cells":len(seen_lo_shu),
        "distinct_nucleus_cell_class_basis_positions":len(seen),
        "matrix_phase_slots_per_nucleus":72,
        "vm81_nuclei":9,
        "vm81_classes_per_phase":8,
        "9_times_72_times_8_equals_5184":9*72*8==5184,
        "matrix_operators_executed":False,
        "canonical_Hash72_witness_minted":False,
        "canonical_VM81_mutated":False,
    }


def verify_original_i071_matrix_phase_surface(*, nucleus_index:int=0)->dict[str,Any]:
    """Call original I070/I071 phase runtime; do not forge geometry receipts."""
    nucleus=_scalar_exact_index(nucleus_index,"VM81 nucleus",9)
    surface=build_nucleus_qudit_surface(
        shared_root_sha256=_root_from_source(),nucleus_index=nucleus
    )
    if len(surface)!=72:
        raise I086OrderedMatrixError("original I071 72 slots missing")
    for slot,item in enumerate(surface):
        basis,local_cell=divmod(slot,9)
        r,c=divmod(local_cell,3)
        if (
            item.phase_slot!=slot or item.phase_channel!=basis
            or item.phase_symbol!=PHASE_BASIS[basis]
            or item.vm81_cell_id!=nucleus*9+local_cell
            or item.lo_shu_value!=LO_SHU[r][c]
        ):
            raise I086OrderedMatrixError("original I071 phase/matrix source mismatch")
    return {
        "original_i070_i071_real_native_candidate_invoked":True,
        "nucleus":nucleus,
        "phase_slots":len(surface),
        "i071_root_source_sha256":_root_from_source(),
        "matrix_cell_values_matched_original_lo_shu":True,
        "i070_binding_hash72_candidate":surface[0].i070_binding_hash72,
        "candidate_only":True,
        "canonical_hash72_admitted":False,
    }


def formalize_i086(*,enumerate_positions:bool=False,
                   verify_phase_nucleus:int|None=None)->dict[str,Any]:
    inherited=formalize_i085()
    if (
        inherited.get("vm81_bit_positions")!=5184
        or inherited.get("hash72_geometry_positions")!=5184
        or inherited.get("native_universal_tensor_value_encoding_proven") is not False
    ):
        raise I086OrderedMatrixError("inherited 5184 crosswalk changed")
    if MATRIX[1][1]!=HNAN_CENTER_EXPRESSION:
        raise I086OrderedMatrixError("inherited original HNAN center changed")
    ast=matrix_quotient_ast()
    source_sha=_root_from_source()
    candidate=original_i069_hash72_candidate({
        "I086_source_sha256":source_sha,
        "matrix_ordered_sources":MATRIX,
        "original_i085_source_sha256":inherited["source_identity_sha256"],
        "hash_type":"SOURCE_BOUND_CANDIDATE_ONLY",
    })
    if not isinstance(candidate,str) or len(candidate)!=72:
        raise I086OrderedMatrixError("inherited I069 candidate digest shape failed")
    coverage=enumerate_all_vm5184_matrix_positions() if enumerate_positions else {
        "all_5184_position_lifts_executed":False
    }
    phase=verify_original_i071_matrix_phase_surface(
        nucleus_index=verify_phase_nucleus
    ) if verify_phase_nucleus is not None else {
        "original_i070_i071_real_native_candidate_invoked":False
    }
    return {
        "schema":SCHEMA,
        "source_equation":SOURCE,
        "source_identity_sha256":source_sha,
        "matrix_denominator_exact_source":SOURCE_DENOMINATOR,
        "matrix":ast["left"]["denominator"]["cells"],
        "ordered_equation_ast":ast,
        "numerator_exact_coordinate_count":5184,
        "matrix_center_original_HNAN_exact_match":True,
        "wx_extended_native_phase_basis_needs_admission":True,
        "inherited_i085_source_sha256":inherited["source_identity_sha256"],
        "i085_rational_address_lift":"(x/u)^(s5184/72) symbolic only",
        "candidate_hash72_word_from_original_I069_hash_function":candidate,
        "candidate_hash72_is_not_canonical_hash72_ledger":True,
        "position_coverage":coverage,
        "original_i070_i071_phase_binding":phase,
        "native_operator_obligations":list(NATIVE_OBLIGATIONS),
        "full_native_3x3_denominator_inverse_proven":False,
        "native_5184_divided_by_matrix_evaluated":False,
        "canonical_hash72_equation_proven":False,
        "canonical_hash216_receipt_proven":False,
        "universal_tensor_value_encoding_proven":False,
        "candidate_only":True,
        "floating_point_authority":False,
        "canonical_vm81_mutation_authority":False,
        "canonical_hash72_mint_authority":False,
        "canonical_hash216_mint_authority":False,
    }
