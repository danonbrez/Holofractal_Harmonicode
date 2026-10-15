import subprocess
from pathlib import Path
import pytest
from hhs_runtime.hhs_pass220_course_hnan_passthrough_graph_binding_v1 import (
    bind_executed_course_passthrough,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

@pytest.fixture(scope="module")
def library(tmp_path_factory):
    path=tmp_path_factory.mktemp("native")/"libcourse_passthrough.so"
    subprocess.run(["cc","-std=c11","-O2","-fPIC","-shared",
                    "-Ihhs_runtime/include",
                    "hhs_runtime/c/hhs_pass220_course_passthrough_witness.c",
                    "-o",str(path)],check=True,timeout=60)
    return str(path)

def test_executed_native_passthrough_bound_to_module_nine_graph(library):
    result=bind_executed_course_passthrough(
        library,bytes([0,255,9,72])*18,bytes([1,3,5,0])*18)
    assert result["module"]==9
    assert result["native_execution_witness_verified"]
    assert len(result["graph_sha256"])==64
    assert len(result["candidate_receipt_sha256"])==64
    assert result["witness_scope"]=="ZERO_DIVISOR_BYTE_IDENTICAL_CARRIER_AND_PHASE_GAIN_ONE"
    assert result["native_phase_gate_proof"]=="INHERITED_DISTINCT"
    assert result["proof_obligation"]!=result["native_phase_gate"]
    assert not result["complete_course_theorem_proved"]
    assert not result["canonical_vm81_admission"]
    assert not result["hash216_minted"]
    assert result==bind_executed_course_passthrough(
        library,bytes([0,255,9,72])*18,bytes([1,3,5,0])*18)

def test_missing_native_evidence_fails_closed():
    with pytest.raises(ProofCorpusError,match="INPUT_REQUIRED"):
        bind_executed_course_passthrough("/nonexistent.so",b"a",b"b")
