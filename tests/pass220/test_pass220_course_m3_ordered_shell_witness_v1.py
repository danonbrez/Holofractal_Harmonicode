import pytest
from pathlib import Path
from hhs_runtime.hhs_pass220_course_m3_ordered_shell_witness_v1 import execute_course_m3_ordered_shell_witness
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

def test_exact_ordered_shell_source_receipt():
    result=execute_course_m3_ordered_shell_witness()
    assert result["module_index"]==3
    assert result["ordered_shell_exponents"]==[72,36,72]
    assert result["alternate_exponents"]==[108,72]
    assert result["formal_delta_exponent"]=="-180"
    assert result["reciprocal_phase_factors"]==[["q-p","p-q"],["p-q","q-p"]]
    assert result["exact_exponent_arithmetic_verified"]
    assert not result["full_phase_gate_proved"]
    assert not result["global_delta_denominator_proved"]
    assert not result["hash72_minted"] and not result["hash216_minted"]
    assert result==execute_course_m3_ordered_shell_witness()

def test_missing_source_rejected(tmp_path):
    with pytest.raises((ProofCorpusError,FileNotFoundError)):
        execute_course_m3_ordered_shell_witness(tmp_path)
