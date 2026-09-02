from hhs_runtime.pass178.exact import ExactRational, ComplexExact, AlgebraicRoot
from hhs_runtime.pass178.constraints import canonical_membrane, membrane_admitted

def test_exact_rational_decimal_and_complex_closure():
    assert ExactRational.coerce("0.125")==ExactRational(1,8)
    z=ComplexExact(ExactRational(1,2),ExactRational(1,3))
    assert (z*z.conjugate()).imag==ExactRational(0)

def test_membrane_positive_and_negative_cases():
    g=canonical_membrane({"P":"2","A":"4","B":"4","p":"1","q":"1"})
    assert membrane_admitted(g) is True
    bad=canonical_membrane({"P":"2","A":"4","B":"5","p":"1","q":"1"})
    assert membrane_admitted(bad) is False

def test_algebraic_root_keeps_branch_symbolic():
    r=AlgebraicRoot(ExactRational(2),2,"POSITIVE_REAL")
    assert r.payload()["radicand"]==[2,1]
