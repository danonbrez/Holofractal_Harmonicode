import pytest
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError
from hhs_runtime.hhs_pass220_executed_whitepaper_native_proof_binding_v1 import (
    HNAN_SOURCE, execute_hnan_whitepaper_proof,
)

def test_absent_native_library_rejected():
    with pytest.raises(ProofCorpusError,match="NATIVE_LIBRARY_REQUIRED"):
        execute_hnan_whitepaper_proof("/missing/native-hnan.so")

def test_compiled_inherited_hnan_executes_and_binds_to_source(tmp_path):
    import subprocess
    from pathlib import Path
    library=tmp_path/"libhhs.so"
    c_obj=tmp_path/"runtime.o"
    cpp_obj=tmp_path/"cellwall.o"
    hash_obj=tmp_path/"hash216.o"
    subprocess.run(["cc","-std=c11","-O0","-fPIC","-Ihhs_runtime/include","-c",
                    "hhs_runtime/c/hhs_runtime_exact_abi.c","-o",str(c_obj)],check=True,timeout=180)
    subprocess.run(["c++","-std=c++17","-O0","-fPIC",
                    "-Ihhs_runtime/include",
                    "-Inative_projects/hhs_pass188_bott_runtime/include",
                    "-Inative_projects/hhs_pass189_hqlh_runtime/include",
                    "-c","hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp",
                    "-o",str(cpp_obj)],check=True,timeout=180)
    subprocess.run(["cc","-std=c11","-O0","-fPIC","-Ihhs_runtime/include","-c",
                    "hhs_runtime/src/hhs_hash216.c","-o",str(hash_obj)],check=True,timeout=180)
    subprocess.run(["c++","-shared",str(c_obj),str(cpp_obj),str(hash_obj),
                    "-o",str(library),"-lm","-lcrypto"],check=True,timeout=180)
    receipt=execute_hnan_whitepaper_proof(str(library))
    assert receipt["source_path"]==HNAN_SOURCE
    assert receipt["native_check_executed"]
    assert receipt["native_global_constraint_verified"]
    assert receipt["corpus_file_count"]==69
    assert receipt["binding"]["checker"]=="NATIVE_HNAN_1_63"
    assert receipt["binding"]["candidate_binding_only"]
    assert not receipt["whole_corpus_proved"]
    assert not receipt["hash216_minted"]
    assert not receipt["canonical_vm81_admission"]
