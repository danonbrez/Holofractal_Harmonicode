from hhs_runtime.hhs_pass220_course_hnan_browser_reference_witness_v1 import execute_browser_passthrough_reference

def test_inherited_browser_passthrough_is_source_bound_not_native_authority():
    result=execute_browser_passthrough_reference()
    witness=result["browser_reference_witness"]
    assert witness["bypass"]==13
    assert witness["ordinary"]==6
    assert witness["hnanFires"]==1
    assert witness["phase_unchanged"]
    assert result["native_hnan_gate_proof_inherited"]
    assert not result["course_passthrough_theorem_proved"]
    assert not result["native_theorem_admission"]
    assert not result["hash216_minted"]
