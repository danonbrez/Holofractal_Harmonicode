import ctypes
import subprocess
from pathlib import Path
import pytest
from hhs_runtime.hhs_pass220_course_passthrough_native_witness_binding_v1 import (
    execute_course_passthrough_native_witness,Witness,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

def test_compiled_course_passthrough_native_witness(tmp_path):
    library=tmp_path/"libcourse_passthrough.so"
    subprocess.run(["cc","-std=c11","-O2","-fPIC","-shared",
                    "-Ihhs_runtime/include",
                    "hhs_runtime/c/hhs_pass220_course_passthrough_witness.c",
                    "-o",str(library)],check=True,timeout=60)
    carrier=bytes([0,255,17,72,1,0,99,3])*9
    phase=bytes([19,32,11,0,240,255])*12
    result=execute_course_passthrough_native_witness(str(library),carrier,phase)
    assert result["independent_passthrough_native_witness_executed"]
    assert result["gain_exact"]=="1/1"
    assert result["phase_writes"]==0
    assert result["carrier_preserved"] and result["phase_preserved"]
    assert not result["complete_course_theorem_proved"]
    assert not result["canonical_vm81_admission"] and not result["hash216_minted"]
    assert result["native_hnan_gate_inherited_unchanged"]
    with pytest.raises(ProofCorpusError,match="INPUT_REQUIRED"):
        execute_course_passthrough_native_witness(str(library),b"",phase)
    lib=ctypes.CDLL(str(library))
    fn=lib.hhs220_course_passthrough_execute
    fn.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,
                 ctypes.c_uint32,ctypes.c_void_p,ctypes.c_void_p,ctypes.POINTER(Witness)]
    fn.restype=ctypes.c_int
    ca=ctypes.create_string_buffer(carrier,len(carrier))
    pa=ctypes.create_string_buffer(phase,len(phase))
    co=ctypes.create_string_buffer(len(carrier))
    po=ctypes.create_string_buffer(len(phase))
    w=Witness()
    assert fn(ca,len(carrier),pa,len(phase),0,co,po,ctypes.byref(w))==0
    assert w.decision==0
