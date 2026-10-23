"""I088: independent 256-word Cl(0,8) proof of I086 quotient."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction

import pytest

from hhs_runtime import hhs_pass220_i088_exact_clifford_word_inverse_v1 as mod
from hhs_runtime.pass219.real_clifford_morita_witness import build_cl08_word_matrices
from hhs_runtime.pass219.phase_clifford_intertwiner import _matmul, _identity


def test_original_cl08_word_product_respects_negative_generator_squares():
    for g in range(8):
        mask, sign = mod._word_pair(1<<g,1<<g)
        assert (mask,sign) == (0,-1)
    for g in range(8):
        for h in range(g+1,8):
            first=mod._word_pair(1<<g,1<<h)
            opposite=mod._word_pair(1<<h,1<<g)
            assert first == (opposite[0],-opposite[1])
    assert mod._word_pair(1<<3,1<<0) == (9,-1)
    assert mod._word_pair(1<<0,1<<3) == (9,1)


def test_word_products_agree_with_original_rml10_generator_module():
    basis=build_cl08_word_matrices()
    assert len(basis)==256
    for left in (0,1,2,3,4,7,15,31,63,95,127,255):
        for right in (0,1,2,3,4,7,15,31,63,95,127,255):
            mask,sign=mod._word_pair(left,right)
            assert _matmul(basis[left],basis[right]) == tuple(
                tuple(sign*v for v in row) for row in basis[mask]
            )


def test_i086_lexemes_preserved_independently_of_matrix_arithmetic():
    source=mod._source_word_matrix()
    assert len(source)==3 and all(len(row)==3 for row in source)
    assert source[0][0] == {3:Fraction(-1)}  # yx = -xy in Cl08 ONLY
    assert source[0][2] == {9:Fraction(-1)}  # wx = -xw in Cl08 ONLY
    assert source[2][0] == {3:Fraction(1)}
    assert source[2][2] == {12:Fraction(1)}
    assert source[1][1] == {
        1:Fraction(1),2:Fraction(1),4:Fraction(-1),8:Fraction(-1)
    }
    assert mod.MATRIX[1][1]=="x+y-z-w+xy+yx-zw-wz"


def test_exact_cl08_inverse_and_quotient_multiply_in_word_algebra():
    r=mod.prove_i088_word_inverse(include_coefficients=True)
    assert r["original_clifford_inverse_word_reconstruction_exact"] is True
    assert r["exact_clifford_word_inverse_nonzero_terms"] == 52
    assert r["exact_clifford_word_inverse_nonzero_blocks"] == 8
    assert r["exact_clifford_word_inverse_left"] is True
    assert r["exact_clifford_word_inverse_right"] is True
    assert r["exact_clifford_word_5184_quotient_left"] is True
    assert r["exact_clifford_word_5184_quotient_right"] is True
    assert r["original_rml10_cl08_word_multiplication_executed"] is True
    assert r["native_wx_composite_proven_in_original_rml10_subalgebra"] is True
    assert r["native_wx_promoted_to_vm81_phase8"] is False
    assert len(r["exact_clifford_word_quotient_coefficient_sha256"])==64
    assert len(r["i069_72_character_candidate_hash72_from_actual_clifford_quotient"])==72
    assert len(r["original_rml10_word_basis_witness_sha256"]) == 64 if (
        "original_rml10_word_basis_witness_sha256" in r
    ) else len(r["rml10_cl08_isomorphism_sha256"])==64

    def decode(records):
        return tuple(
            tuple({
                value["word_mask"]:Fraction(value["numerator"],value["denominator"])
                for value in block
            } for block in row) for row in records
        )

    source=decode(r["source_word_blocks"])
    inverse=decode(r["exact_inverse_word_blocks"])
    quotient=decode(r["exact_quotient_word_blocks"])
    assert source==mod._source_word_matrix()
    assert mod._multiply_matrix_words(source,inverse)==mod._identity_words()
    assert mod._multiply_matrix_words(inverse,source)==mod._identity_words()
    assert mod._multiply_matrix_words(source,quotient)==mod._identity_words(5184)
    assert mod._multiply_matrix_words(quotient,source)==mod._identity_words(5184)


def test_zero_host_scalarization_and_canonical_authority():
    r=mod.prove_i088_word_inverse()
    assert "exact_inverse_word_blocks" not in r
    assert "exact_quotient_word_blocks" not in r
    assert r["projection_scope"]=="ORIGINAL_RML10_CL08_SUBALGEBRA_ONLY"
    assert r["canonical_hash72_from_clifford_candidate_admitted"] is False
    assert r["native_full_HHS_VM81_tensor_matrix_division_proven"] is False
    assert r["native_Lane5_signed_mutation_authority"] is False
    assert r["native_Hash216_previous_current_receipt_lineage_proven"] is False
    assert r["candidate_only"] is True
    assert r["floating_point_authority"] is False


def test_unknown_word_or_host_float_rejected():
    for a,b in ((-1,0),(256,0),(0,256),(True,0),(0,1.0)):
        with pytest.raises(mod.I088WordInverseError):
            mod._word_pair(a,b)


def test_corrupt_original_i086_operator_order_fails_closed(monkeypatch):
    change=list(map(list,mod.MATRIX))
    change[0][2]="wz"
    monkeypatch.setattr(mod,"MATRIX",tuple(tuple(row) for row in change))
    with pytest.raises(mod.I088WordInverseError,match="source identity drift"):
        mod._source_word_matrix()


def test_repeatability_of_sparse_exact_cl08_witness():
    r1=mod.prove_i088_word_inverse()
    r2=mod.prove_i088_word_inverse()
    assert r1==r2


def test_missing_original_rml10_word_basis_rejected(monkeypatch):
    monkeypatch.setattr(mod,"build_cl08_word_matrices",lambda:())
    with pytest.raises(mod.I088WordInverseError,match="full word basis required"):
        mod.prove_i088_word_inverse()
