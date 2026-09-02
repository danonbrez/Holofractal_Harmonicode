import pytest
from hhs_runtime.pass178.exact import ComplexExact, ExactRational
from hhs_runtime.pass178.quantum import QuantumState, cayley_step, norm2

def test_exact_cayley_preserves_norm_for_hermitian_system():
    s=QuantumState("q",(ComplexExact(ExactRational(1),ExactRational(0)),ComplexExact(ExactRational(0),ExactRational(0))))
    H=[[[0,0],[1,0]],[[1,0],[0,0]]]
    n=cayley_step(s,H,"1/4","1")
    assert n.step_index==1
    assert norm2(n.amplitudes)==ExactRational(1)

def test_nonhermitian_closed_system_rejected():
    s=QuantumState("q",(ComplexExact(ExactRational(1),ExactRational(0)),ComplexExact(ExactRational(0),ExactRational(0))))
    with pytest.raises(Exception,match="NON_HERMITIAN"):
        cayley_step(s,[[0,1],[0,0]],"1/4")
