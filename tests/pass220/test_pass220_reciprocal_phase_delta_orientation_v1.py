from fractions import Fraction
import pytest

from hhs_runtime.hhs_pass220_reciprocal_phase_delta_orientation_v1 import (
    scalar_shadow, reciprocal_phase_witness, ReciprocalPhaseBoundaryError,
    EXPRESSION, TERMINAL,
)

@pytest.mark.parametrize("p,q", [
    (Fraction(0),Fraction(2)), (Fraction(2,3),Fraction(8,3)),
    (Fraction(-7,2),Fraction(9,4)), (Fraction(13),Fraction(-9))
])
def test_scalar_shadow_exact_negative_one(p,q):
    assert scalar_shadow(p,q) == -1

def test_ordered_witness_retains_sign_obligation():
    r=reciprocal_phase_witness(Fraction(0),Fraction(2))
    assert r["source_expression"] == EXPRESSION
    assert r["terminal_ordered_source"] == TERMINAL
    assert r["ordered_channel_pairs"] == (("q-p","p-q"),("AB","BA"),("yx","xy"))
    assert r["scalar_shadow"] == [-1,1]
    assert r["scalar_shadow_equals_delta_one"] is False
    assert r["typed_delta_target"] == "Delta=1"
    assert r["native_hnan_orientation_closure_proven"] is False
    assert r["phase36_antipodal"] and r["phase72_identity"]
    assert r["candidate_only"] is True
    assert r["canonical_vm81_mutation_authority"] is False
    assert r["canonical_hash72_mint_authority"] is False
    assert r["canonical_hash216_persistence_authority"] is False

def test_boundary_and_float_rejected():
    with pytest.raises(ReciprocalPhaseBoundaryError,match="P_EQ_Q"):
        scalar_shadow(Fraction(1),Fraction(1))
    with pytest.raises(ReciprocalPhaseBoundaryError,match="EXACT_RATIONAL"):
        scalar_shadow(.5,Fraction(2))
