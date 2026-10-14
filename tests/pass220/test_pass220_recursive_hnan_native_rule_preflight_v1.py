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
