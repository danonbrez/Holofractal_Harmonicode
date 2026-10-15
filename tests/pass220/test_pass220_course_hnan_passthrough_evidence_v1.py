import pytest
from hhs_runtime.hhs_pass220_course_hnan_passthrough_evidence_v1 import (
    course_hnan_proof_obligations, require_course_passthrough_checker,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

def test_course_module_9_passthrough_is_separate_from_inherited_native_phase_gate():
    receipt=course_hnan_proof_obligations()
    assert receipt["course_module_index"]==9
    assert receipt["course_passthrough_obligations"]==[
        "divisor vanishes","gain exactly 1","no phase write"]
    assert receipt["native_gate_proof_status"]=="INHERITED_SEPARATE"
    assert not receipt["new_native_gate_proof_required"]
    assert not receipt["passthrough_implied_by_native_phase_gate"]
    assert not receipt["native_gate_implied_by_passthrough"]
    assert receipt["course_passthrough_executable_proof"]=="UNBOUND"
    assert not receipt["canonical_admission"]
    assert not receipt["hash216_minted"]

def test_untrusted_passthrough_proof_must_not_be_admitted():
    with pytest.raises(ProofCorpusError,match="EXECUTABLE_CHECKER_NOT_BOUND"):
        require_course_passthrough_checker({"verified":True,"gain":1,"phase_write":False})
