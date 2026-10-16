import pytest
from hhs_runtime.hhs_pass220_course_m2_consecutive_witness_v1 import execute_course_m2_consecutive_witness
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

@pytest.mark.parametrize("t,m,closed",[(0,0,True),(1,1,True),(2,3,True),(3,5,False),(-2,0,False),(2**1024+17,2**1024+18,False)])
def test_exact_modulus_witness_without_false_gate_closure(t,m,closed):
    result=execute_course_m2_consecutive_witness(t,m)
    assert result["cubic_mod6"]=="0"
    assert result["quadratic_mod2"]=="0"
    assert result["supplied_pair_equality_gate_closed"] is closed
    assert result["cubic_witness"]==str(t**3-t)
    assert result["quadratic_witness"]==str(m*m-m)
    assert not result["global_p_indexed_cascade_proved"]
    assert not result["complete_module_two_proved"]
    assert not result["hash72_minted"] and not result["hash216_minted"]
    assert result==execute_course_m2_consecutive_witness(t,m)

@pytest.mark.parametrize("t,m",[(1.0,1),(1,"1"),(True,0),(None,0)])
def test_untyped_witness_rejected(t,m):
    with pytest.raises(ProofCorpusError,match="EXACT_INTEGER_WITNESSES_REQUIRED"):
        execute_course_m2_consecutive_witness(t,m)
