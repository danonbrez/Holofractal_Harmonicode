import subprocess
from pathlib import Path
import pytest
from hhs_runtime.hhs_pass220_course_m4_inherited_hnan_phase_binding_v1 import bind_course_m4_inherited_native_phase_gate
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

def test_absent_native_checker_rejected():
    with pytest.raises(ProofCorpusError,match="COURSE_M4_NATIVE_LIBRARY_REQUIRED"):
        bind_course_m4_inherited_native_phase_gate("/missing/native.so")

def test_real_inherited_native_hnan_module_four_binding(tmp_path):
    c=tmp_path/"runtime.o"
    cpp=tmp_path/"wall.o"
    h=tmp_path/"hash.o"
    library=tmp_path/"libhhs.so"
    subprocess.run(["cc","-std=c11","-O0","-fPIC","-Ihhs_runtime/include",
        "-c","hhs_runtime/c/hhs_runtime_exact_abi.c","-o",str(c)],check=True,timeout=180)
    subprocess.run(["c++","-std=c++17","-O0","-fPIC","-Ihhs_runtime/include",
        "-Inative_projects/hhs_pass188_bott_runtime/include",
        "-Inative_projects/hhs_pass189_hqlh_runtime/include","-c",
        "hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp","-o",str(cpp)],check=True,timeout=180)
    subprocess.run(["cc","-std=c11","-O0","-fPIC","-Ihhs_runtime/include",
        "-c","hhs_runtime/src/hhs_hash216.c","-o",str(h)],check=True,timeout=180)
    subprocess.run(["c++","-shared",str(c),str(cpp),str(h),
        "-o",str(library),"-lm","-lcrypto"],check=True,timeout=180)
    receipt=bind_course_m4_inherited_native_phase_gate(str(library))
    assert receipt["module_index"]==4
    assert receipt["native_phase_order_verified"]
    assert receipt["xy_yx_distinct"] and receipt["zw_wz_distinct"]
    assert len(receipt["candidate_receipt_sha256"])==64
    assert not receipt["new_native_gate_proof_required"]
    assert not receipt["complete_module_four_proved"]
    assert not receipt["course_passthrough_theorem_proved"]
    assert not receipt["canonical_admission"] and not receipt["hash216_minted"]
