"""Pass 220 I088 — exact Cl(0,8) WORD-ALGEBRA inverse of I086.

Unlike the I087 M48(Q) matrix-inverse check, this proves BOTH SIDES
again by multiplying 256-basis Clifford words with the original
RML10 relations e_i**2=-1, e_i e_j=-e_j e_i (i!=j).
The result is a compact exact Cl(0,8) word inverse and the 5184/M
quotient. It is an original RML10 subalgebra theorem, NOT a proof
of full native VM81/HHS/Hash72 tensor division or canonical mint.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime import hhs_pass220_i087_exact_rml11_clifford_matrix_inverse_v1 as i087
from hhs_runtime import hhs_pass220_i086_ordered_3x3_vm5184_hash72_matrix_v1 as i086
from hhs_runtime.pass219.real_clifford_morita_witness import (
    build_cl08_word_matrices,
    build_cl08_isomorphism_witness,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import (
    hash72 as inherited_i069_candidate_hash72,
)

SCHEMA = "HHS_PASS220_I088_EXACT_ORIGINAL_RML10_CLIFFORD_WORD_INVERSE_V1"
SOURCE = i086.SOURCE
MATRIX = i086.MATRIX
N = 3
WORD_COUNT = 256
BASIS_GENERATORS = ("x","y","z","w")
WORD_DIM = 16
IDENTITY_MASK = 0
SCALAR_5184 = 81*64
EXPECTED_DET = 10485760000
EXPECTED_SPARSE_TERMS = 52


class I088WordInverseError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",",":"),
        allow_nan=False,
    ).encode("utf-8")


def _word_pair(left: int, right: int) -> tuple[int, int]:
    """Exact native Cl(0,8) word multiplication on ascending-mask words.

    For each generator e_j of the right operand, every e_i on its
    left with i>j crosses it, and an overlapping index contributes
    e_j**2=-1. This is *ordered* and handles wx separately from xw.
    """
    if any(isinstance(v,bool) or not isinstance(v,int) or not 0<=v<WORD_COUNT
           for v in (left,right)):
        raise I088WordInverseError("original Clifford 8-generator word masks required")
    swaps=sum((left >> (j+1)).bit_count()
              for j in range(8) if right & (1<<j))
    overlaps=(left & right).bit_count()
    return left^right, -1 if (swaps+overlaps)%2 else 1


def _add_term(acc: dict[int,Fraction], word: int, amount: Fraction) -> None:
    if amount==0:
        return
    total=acc.get(word,Fraction(0))+amount
    if total:
        acc[word]=total
    else:
        acc.pop(word,None)


def _source_block(expression: str)->dict[int,Fraction]:
    """Parse original I086 ordered signed source; projection only."""
    terms=i086._parse_cell_expression(expression)["ordered_terms"]
    out:dict[int,Fraction]={}
    for term in terms:
        op=term["operand"]
        if op["head"]=="NATIVE_PHASE_ADDRESS":
            label=op["symbol"]
            if label not in BASIS_GENERATORS:
                raise I088WordInverseError("unknown source primitive")
            index=BASIS_GENERATORS.index(label)
            mask,sgn=1<<index,1
        elif op["head"]=="HHS_ORDERED_PRODUCT":
            a=op["left"]["symbol"]
            b=op["right"]["symbol"]
            if a not in BASIS_GENERATORS or b not in BASIS_GENERATORS:
                raise I088WordInverseError("unregistered original word generator")
            mask,sgn=_word_pair(1<<BASIS_GENERATORS.index(a),
                                1<<BASIS_GENERATORS.index(b))
            if op["source_token"]!=a+b:
                raise I088WordInverseError("ordered product source token drift")
        else:
            raise I088WordInverseError("unsupported source cell operation")
        _add_term(out,mask,Fraction(term["sign"]*sgn))
    return out


def _source_word_matrix()->tuple[tuple[dict[int,Fraction],...],...]:
    if (
        MATRIX!=i087.MATRIX or MATRIX!=i086.MATRIX
        or SOURCE!=i087.SOURCE or SOURCE!=i086.SOURCE
        or MATRIX[1][1]!=i086.HNAN_CENTER_EXPRESSION
    ):
        raise I088WordInverseError("original I086/I087/HNAN source identity drift")
    return tuple(tuple(_source_block(MATRIX[r][c]) for c in range(N))
                 for r in range(N))


def _multiply_words(
    left: Mapping[int,Fraction],right: Mapping[int,Fraction],
)->dict[int,Fraction]:
    out:dict[int,Fraction]={}
    for a,ca in left.items():
        for b,cb in right.items():
            mask,sign=_word_pair(a,b)
            _add_term(out,mask,ca*cb*sign)
    return out


def _multiply_matrix_words(
    a: tuple[tuple[dict[int,Fraction],...],...],
    b: tuple[tuple[dict[int,Fraction],...],...],
)->tuple[tuple[dict[int,Fraction],...],...]:
    if len(a)!=N or len(b)!=N or any(len(row)!=N for row in (*a,*b)):
        raise I088WordInverseError("3x3 exact original Clifford word matrix required")
    return tuple(
        tuple(_sum_words(_multiply_words(a[i][k],b[k][j]) for k in range(N))
              for j in range(N))
        for i in range(N)
    )


def _sum_words(items: Any)->dict[int,Fraction]:
    out:dict[int,Fraction]={}
    for item in items:
        for mask,value in item.items():
            _add_term(out,mask,value)
    return out


def _scale_words(
    a: tuple[tuple[dict[int,Fraction],...],...], scalar: int,
)->tuple[tuple[dict[int,Fraction],...],...]:
    if isinstance(scalar,bool) or not isinstance(scalar,int):
        raise I088WordInverseError("exact integer numerator required")
    return tuple(tuple({mask:value*scalar for mask,value in block.items()}
                       for block in row) for row in a)


def _identity_words(scalar:int=1)->tuple[tuple[dict[int,Fraction],...],...]:
    return tuple(tuple({0:Fraction(scalar)} if r==c else {}
                       for c in range(N)) for r in range(N))


def _word_projection(
    words: tuple[tuple[dict[int,Fraction],...],...],
    word_matrices: tuple[tuple[tuple[int,...],...],...],
)->tuple[tuple[Fraction,...],...]:
    """Construct the exact 48x48 RML10 module from Clifford words."""
    def block_sum(b:Mapping[int,Fraction])->tuple[tuple[Fraction,...],...]:
        m=[[Fraction(0) for _ in range(WORD_DIM)] for _ in range(WORD_DIM)]
        for word,coef in b.items():
            base=word_matrices[word]
            for i in range(WORD_DIM):
                for j in range(WORD_DIM):
                    if base[i][j]:
                        m[i][j]+=coef*base[i][j]
        return tuple(tuple(row) for row in m)
    blocks=tuple(tuple(block_sum(words[r][c]) for c in range(N)) for r in range(N))
    return tuple(
        tuple(x for bc in range(N) for x in blocks[br][bc][ir])
        for br in range(N) for ir in range(WORD_DIM)
    )


def _decode_inverse_word_blocks(
    original_inverse:tuple[tuple[Fraction,...],...],
    basis:tuple[tuple[tuple[int,...],...],...],
)->tuple[tuple[dict[int,Fraction],...],...]:
    """Expand every rational 16x16 inverse block in original 256 RML10 words.

    RML10 Cl_(0,8) word matrices form an exact orthogonal basis
    of M16(R), each with squared Frobenius norm 16.
    """
    if len(basis)!=WORD_COUNT or len(original_inverse)!=48:
        raise I088WordInverseError("original RML10 full word basis required")
    blocks=[]
    for br in range(N):
        row=[]
        for bc in range(N):
            block=[r[bc*WORD_DIM:(bc+1)*WORD_DIM]
                   for r in original_inverse[br*WORD_DIM:(br+1)*WORD_DIM]]
            coeffs:dict[int,Fraction]={}
            for mask,wm in enumerate(basis):
                if len(wm)!=WORD_DIM:
                    raise I088WordInverseError("RML10 generator basis shape mismatch")
                dot=sum(Fraction(wm[i][j])*block[i][j]
                        for i in range(WORD_DIM) for j in range(WORD_DIM)
                        if wm[i][j])
                if dot:
                    _add_term(coeffs,mask,dot/Fraction(WORD_DIM))
            row.append(coeffs)
        blocks.append(tuple(row))
    return tuple(blocks)


def _sparse_record(blocks:tuple[tuple[dict[int,Fraction],...],...])->list[list[list[dict[str,int]]]]:
    return [
        [
            [
                {"word_mask":word,"numerator":v.numerator,"denominator":v.denominator}
                for word,v in sorted(block.items())
            ]
            for block in row
        ]
        for row in blocks
    ]


def prove_i088_word_inverse(*, include_coefficients:bool=False)->dict[str,Any]:
    """Independent exact Clifford-word two-sided inverse, source-bound and held."""
    inherited=i087.verify_i087_exact_clifford_inverse()
    if (
        inherited.get("determinant")!={"numerator":EXPECTED_DET,"denominator":1}
        or inherited.get("native_matrix_inverse_operator_admitted") is not False
    ):
        raise I088WordInverseError("I087 exact inverse source or authority drift")

    rml10=build_cl08_isomorphism_witness()
    if rml10.get("witness_sha256")!=inherited["original_rml10_cl08_witness_sha256"]:
        raise I088WordInverseError("original RML10 isomorphism witness drift")
    basis=build_cl08_word_matrices()
    source_words=_source_word_matrix()
    direct_source=_word_projection(source_words,basis)
    original_matrix=i087.original_i086_rml11_block_matrix()
    if direct_source!=original_matrix:
        raise I088WordInverseError("original I086 ordered source and Cl08 word projection mismatch")

    inverse_matrix,det,_=i087._exact_inverse(original_matrix)
    if inverse_matrix is None or det!=Fraction(EXPECTED_DET):
        raise I088WordInverseError("original exact inverse disappeared")
    inverse_words=_decode_inverse_word_blocks(inverse_matrix,basis)
    reconstructed=_word_projection(inverse_words,basis)
    if reconstructed!=inverse_matrix:
        raise I088WordInverseError("original RML10 256-word basis failed exact reconstruction")
    support=sum(len(block) for row in inverse_words for block in row)
    if support!=EXPECTED_SPARSE_TERMS:
        raise I088WordInverseError("I086 original sparse inverse word support drift")

    # Crucially, these products take place in the independently
    # encoded Cl(0,8) WORD ALGEBRA, not the 48x48 matrix algebra.
    identity=_identity_words()
    if (
        _multiply_matrix_words(source_words,inverse_words)!=identity
        or _multiply_matrix_words(inverse_words,source_words)!=identity
    ):
        raise I088WordInverseError("two-sided original Clifford WORD inverse failed")
    quotient=_scale_words(inverse_words,SCALAR_5184)
    target=_identity_words(SCALAR_5184)
    if (
        _multiply_matrix_words(source_words,quotient)!=target
        or _multiply_matrix_words(quotient,source_words)!=target
    ):
        raise I088WordInverseError("exact 5184/M Clifford WORD quotient failed")

    payload=_sparse_record(quotient)
    source_bound={
        "schema":SCHEMA,
        "original_i086_source":SOURCE,
        "original_i087_matrix_sha256":inherited["matrix_clifford_projection_sha256"],
        "original_rml10_word_basis_witness_sha256":rml10["witness_sha256"],
        "quotient_exact_word_coefficients":payload,
        "authority":"RML10_CLIFFORD_WORD_PROJECTION_CANDIDATE_ONLY",
    }
    fingerprint=sha256(_canonical(source_bound)).hexdigest()
    candidate=inherited_i069_candidate_hash72(source_bound)
    if not isinstance(candidate,str) or len(candidate)!=72:
        raise I088WordInverseError("inherited I069 quotient candidate hash malformed")

    result:dict[str,Any]={
        "schema":SCHEMA,
        "original_i086_source":SOURCE,
        "i086_source_sha256":inherited["i086_source_sha256"],
        "rml10_cl08_isomorphism_sha256":rml10["witness_sha256"],
        "i087_matrix_sha256":inherited["matrix_clifford_projection_sha256"],
        "exact_48x48_matrix_order":48,
        "exact_256_word_clifford_basis_order":WORD_COUNT,
        "all_nine_source_operators_preserved":True,
        "native_wx_composite_proven_in_original_rml10_subalgebra":True,
        "native_wx_promoted_to_vm81_phase8":False,
        "original_rml10_cl08_word_multiplication_executed":True,
        "original_clifford_source_word_reconstruction_exact":True,
        "original_clifford_inverse_word_reconstruction_exact":True,
        "exact_clifford_word_inverse_nonzero_blocks":sum(bool(block) for row in inverse_words for block in row),
        "exact_clifford_word_inverse_nonzero_terms":support,
        "exact_clifford_word_inverse_left":True,
        "exact_clifford_word_inverse_right":True,
        "exact_clifford_word_5184_quotient_left":True,
        "exact_clifford_word_5184_quotient_right":True,
        "exact_clifford_word_quotient_coefficient_sha256":fingerprint,
        "i069_72_character_candidate_hash72_from_actual_clifford_quotient":candidate,
        "canonical_hash72_from_clifford_candidate_admitted":False,
        "native_full_HHS_VM81_tensor_matrix_division_proven":False,
        "native_Lane5_signed_mutation_authority":False,
        "native_Hash216_previous_current_receipt_lineage_proven":False,
        "projection_scope":"ORIGINAL_RML10_CL08_SUBALGEBRA_ONLY",
        "candidate_only":True,
        "floating_point_authority":False,
    }
    if include_coefficients:
        result["source_word_blocks"]=_sparse_record(source_words)
        result["exact_inverse_word_blocks"]=_sparse_record(inverse_words)
        result["exact_quotient_word_blocks"]=payload
    return result
