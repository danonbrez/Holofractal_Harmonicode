import pytest
from hhs_runtime.hhs_pass220_course_m1_exact_p_gate_binding_v1 import execute_course_m1_exact_p_closure
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

@pytest.mark.parametrize("P",[2,3,5,17,72,10**90+37,2**4096+123])
def test_exact_p_indexed_gate_and_source_receipt(P):
    result=execute_course_m1_exact_p_closure(P)
    assert result["P"]==str(P)
    assert result["p"]==str(P-1) and result["q"]==str(P+1)
    assert result["delta"]=="1"
    assert result["cleared_gate_lhs"]==result["cleared_gate_rhs"]==str(2*P)
    assert result["exact_integer_gate_verified"]
    assert len(result["module_sha256"])==64
    assert len(result["dependency_graph_sha256"])==64
    assert len(result["candidate_receipt_sha256"])==64
    assert not result["cubic_witness_proved"]
    assert not result["entire_module_one_proved"]
    assert not result["canonical_vm81_admission"]
    assert not result["hash72_minted"] and not result["hash216_minted"]
    assert result==execute_course_m1_exact_p_closure(P)

@pytest.mark.parametrize("value",[0,1,-9,True,3.0,"3",None])
def test_invalid_or_noncanonical_p_rejected(value):
    with pytest.raises(ProofCorpusError,match="BIGINT_P_REQUIRED"):
        execute_course_m1_exact_p_closure(value)
