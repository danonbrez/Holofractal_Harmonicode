from unittest.mock import patch
import pytest
from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import TensorRef,SymbolicTensorError
from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import native_recursive_hnan_preflight

def ref(p): return TensorRef(p,"BIGINT","a"*216,"root")

def test_missing_native_library_fails_closed():
    tree={"P":"2","candidate_sha256":"a"*64,"ordered_phase_leaves":[]}
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.inspect_recursive_ordered_phase_swap",return_value=tree):
        with pytest.raises(SymbolicTensorError,match="LIBRARY_REQUIRED"):
            native_recursive_hnan_preflight("ADD",ref(1),ref(1),native_library="/missing/hhs.so")

def test_native_global_rejection_fails_closed(tmp_path):
    path=tmp_path/"fake.so"
    path.write_bytes(b"not a valid shared library")
    tree={"P":"2","candidate_sha256":"a"*64,"ordered_phase_leaves":[]}
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.inspect_recursive_ordered_phase_swap",return_value=tree):
        with pytest.raises(OSError):
            native_recursive_hnan_preflight("ADD",ref(1),ref(1),native_library=str(path))


def test_real_compiled_native_global_rule_12(tmp_path):
    """Compile repository's C runtime and invoke genuine 1.63 rule authority."""
    import subprocess
    from pathlib import Path
    source=Path("hhs_runtime/c/hhs_runtime_exact_abi.c")
    assert source.is_file()
    library=tmp_path/"libhhs_native_hnan.so"
    c_object=tmp_path/"hhs_exact.o"
    cpp_object=tmp_path/"hhs_pqc.o"
    subprocess.run(["cc","-std=c11","-O0","-fPIC",
                    "-Ihhs_runtime/include","-c",str(source),"-o",str(c_object)],check=True,timeout=180)
    subprocess.run(["c++","-std=c++17","-O0","-fPIC",
                    "-Ihhs_runtime/include","-c",
                    "hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp",
                    "-o",str(cpp_object)],check=True,timeout=180)
    subprocess.run(["c++","-shared",str(c_object),str(cpp_object),"-o",str(library),"-lm"],check=True,timeout=180)
    tree={"P":"2","candidate_sha256":"a"*64,"ordered_phase_leaves":[{
        "depth":0,"inherited_hnan_receipt_sha256":"b"*64
    }]}
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.inspect_recursive_ordered_phase_swap",return_value=tree):
        result=native_recursive_hnan_preflight("ADD",ref(1),ref(1),native_library=str(library))
    assert result["native_global_rule_mask_verified"]
    assert len(result["native_ordered_rule_leaves"])==1
    assert result["native_ordered_rule_leaves"][0]["native_ordered_xy_yx_rule_verified"]
    assert not result["typed_yx_over_xy_equals_u_minus_108_proved"]
