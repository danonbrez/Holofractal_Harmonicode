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
    hash_object=tmp_path/"hhs_hash216.o"
    subprocess.run(["cc","-std=c11","-O0","-fPIC",
                    "-Ihhs_runtime/include","-c",str(source),"-o",str(c_object)],check=True,timeout=180)
    subprocess.run(["c++","-std=c++17","-O0","-fPIC",
                    "-Ihhs_runtime/include","-Inative_projects/hhs_pass188_bott_runtime/include",
                    "-Inative_projects/hhs_pass189_hqlh_runtime/include","-c",
                    "hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp",
                    "-o",str(cpp_object)],check=True,timeout=180)
    subprocess.run(["cc","-std=c11","-O0","-fPIC",
                    "-Ihhs_runtime/include","-c","hhs_runtime/src/hhs_hash216.c",
                    "-o",str(hash_object)],check=True,timeout=180)
    subprocess.run(["c++","-shared",str(c_object),str(cpp_object),str(hash_object),
                    "-o",str(library),"-lm","-lcrypto"],check=True,timeout=180)
    tree={"P":"2","candidate_sha256":"a"*64,"ordered_phase_leaves":[{
        "depth":0,"inherited_hnan_receipt_sha256":"b"*64
    }]}
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.inspect_recursive_ordered_phase_swap",return_value=tree):
        result=native_recursive_hnan_preflight("ADD",ref(1),ref(1),native_library=str(library))
    assert result["native_global_rule_mask_verified"]
    assert len(result["native_ordered_rule_leaves"])==1
    assert result["native_ordered_rule_leaves"][0]["native_ordered_xy_yx_rule_verified"]
    assert not result["typed_yx_over_xy_equals_u_minus_108_proved"]
    # Genuine C/C++ ABI proof gate, not a mocked shared library: carry one
    # source-bound exact Lean instance through the existing native preflight.
    theorem = {
        "theorem": "value_left_distrib",
        "carrier": "ExactRatValue",
        "relation": "Eq",
        "operator": "ExactRatValue.mul/ExactRatValue.add",
    }
    operands = [
        {"numerator": 17, "denominator": 19},
        {"numerator": -3, "denominator": 7},
        {"numerator": 11, "denominator": 13},
    ]
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.inspect_recursive_ordered_phase_swap", return_value=tree):
        instance_result = native_recursive_hnan_preflight(
            "ADD", ref(1), ref(1), native_library=str(library),
            lean_normalization=theorem, lean_normalization_operands=operands,
        )
    instance = instance_result["existing_lean_normalization_instance"]
    assert instance["operands"] == operands
    assert instance["lhs_exact"] == instance["rhs_exact"]
    assert instance["theorem"]["declaration"] == "value_left_distrib"
    assert instance["theorem"]["application_declaration"] == "value_left_distrib_application"
    assert instance_result["native_global_rule_mask_verified"]
    assert len(instance_result["native_ordered_rule_leaves"]) == 1
    assert not instance_result["canonical_vm81_admission"]
    assert not instance_result["canonical_hash216_minted"]
    assert not instance_result["global_composite_hnan_closure_proved"]

def test_native_exact_phase_witness_rejection_before_loading_library(tmp_path):
    """The existing native preflight must fail closed on exact-phase drift."""
    from hhs_runtime.pass220.hnan_lane5_exact_witness_v1 import HNANExactWitnessError
    from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import (
        native_recursive_hnan_preflight,
    )
    candidate = tmp_path / "native.so"
    candidate.write_bytes(b"placeholder")
    tree = {"P": "2", "candidate_sha256": "a" * 64, "ordered_phase_leaves": []}
    # Existing contract evaluates native rule first. Stub native verification
    # only in this rejection-path test; no acceptance is asserted.
    import ctypes
    class DummyFunc:
        def __init__(self, result=0):
            self.result = result
        def __call__(self, ptr):
            from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import (
                GlobalReceipt, VERSION, MASK,
            )
            receipt = ctypes.cast(ptr, ctypes.POINTER(GlobalReceipt)).contents
            receipt.version = VERSION
            receipt.decision = 1
            receipt.required_rule_mask = MASK
            receipt.verified_rule_mask = MASK
            for key in ("jordan_depth2_verified", "minimal_polynomial_degree4_verified",
                        "degree4_recurrence_verified", "hnan_channel_order_preserved",
                        "global_delta_denominator_preserved", "xy_yx_distinct", "zw_wz_distinct"):
                setattr(receipt, key, 1)
            return self.result
    class DummyLib:
        hhs_exact_pass219_hnan_global_system_verify = DummyFunc()
        hhs_exact_pass219_hnan_resolve = DummyFunc()
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.inspect_recursive_ordered_phase_swap", return_value=tree), \
         patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.C.CDLL", return_value=DummyLib()), \
         patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.verify_read_only_candidate", side_effect=HNANExactWitnessError("drift")):
        with pytest.raises(SymbolicTensorError, match="EXACT_PHASE_WITNESS_REJECTED"):
            native_recursive_hnan_preflight("ADD", ref(1), ref(1), native_library=str(candidate))

def test_native_token_identity_incomplete_handoff_rejected(tmp_path):
    """Optional token handoff must not accept an unpaired identity specification."""
    import ctypes
    from hhs_runtime.hhs_loshu_phase_embedding_v1 import embed_token
    from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import (
        native_recursive_hnan_preflight, GlobalReceipt, VERSION, MASK,
    )
    library_path = tmp_path / "native.so"
    library_path.write_bytes(b"placeholder")
    class Verify:
        def __call__(self, pointer):
            receipt = ctypes.cast(pointer, ctypes.POINTER(GlobalReceipt)).contents
            receipt.version = VERSION
            receipt.decision = 1
            receipt.required_rule_mask = MASK
            receipt.verified_rule_mask = MASK
            for key in ("jordan_depth2_verified", "minimal_polynomial_degree4_verified",
                        "degree4_recurrence_verified", "hnan_channel_order_preserved",
                        "global_delta_denominator_preserved", "xy_yx_distinct", "zw_wz_distinct"):
                setattr(receipt, key, 1)
            return 0
    class Library:
        hhs_exact_pass219_hnan_global_system_verify = Verify()
        hhs_exact_pass219_hnan_resolve = Verify()
    candidate_tree = {"P": "2", "candidate_sha256": "a" * 64, "ordered_phase_leaves": []}
    state = embed_token("AB", 0, 0, 72)
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.inspect_recursive_ordered_phase_swap", return_value=candidate_tree), \
         patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.C.CDLL", return_value=Library()):
        with pytest.raises(SymbolicTensorError, match="TOKEN_IDENTITY_SHAPE"):
            native_recursive_hnan_preflight("ADD", ref(1), ref(1), native_library=str(library_path),
                token_state=state, token_identity={"ordered_operator": "AB"})
        with pytest.raises(SymbolicTensorError, match="TOKEN_IDENTITY_REQUIRED"):
            native_recursive_hnan_preflight("ADD", ref(1), ref(1), native_library=str(library_path),
                token_state=state)

def test_native_lean_normalization_invalid_shape_rejected(tmp_path):
    import ctypes
    from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import (
        native_recursive_hnan_preflight, GlobalReceipt, VERSION, MASK,
    )
    library_path = tmp_path / "native.so"
    library_path.write_bytes(b"placeholder")
    class Verify:
        def __call__(self, pointer):
            receipt = ctypes.cast(pointer, ctypes.POINTER(GlobalReceipt)).contents
            receipt.version = VERSION
            receipt.decision = 1
            receipt.required_rule_mask = MASK
            receipt.verified_rule_mask = MASK
            for key in ("jordan_depth2_verified", "minimal_polynomial_degree4_verified",
                        "degree4_recurrence_verified", "hnan_channel_order_preserved",
                        "global_delta_denominator_preserved", "xy_yx_distinct", "zw_wz_distinct"):
                setattr(receipt, key, 1)
            return 0
    class Library:
        hhs_exact_pass219_hnan_global_system_verify = Verify()
        hhs_exact_pass219_hnan_resolve = Verify()
    tree = {"P": "2", "candidate_sha256": "a" * 64, "ordered_phase_leaves": []}
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.inspect_recursive_ordered_phase_swap", return_value=tree), \
         patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.C.CDLL", return_value=Library()):
        with pytest.raises(SymbolicTensorError, match="LEAN_NORMALIZATION_SHAPE"):
            native_recursive_hnan_preflight("ADD", ref(1), ref(1), native_library=str(library_path),
                lean_normalization={"theorem": "value_add_assoc"})
        with pytest.raises(SymbolicTensorError, match="LEAN_NORMALIZATION_REJECTED"):
            native_recursive_hnan_preflight("ADD", ref(1), ref(1), native_library=str(library_path),
                lean_normalization={"theorem": "value_add_assoc", "carrier": "HNAN",
                    "relation": "Eq", "operator": "AB"})

def test_native_lean_instance_requires_theorem(tmp_path):
    from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import native_recursive_hnan_preflight
    library_path = tmp_path / "native.so"
    library_path.write_bytes(b"placeholder")
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.inspect_recursive_ordered_phase_swap",
               return_value={"P":"2","candidate_sha256":"a"*64,"ordered_phase_leaves":[]}), \
         patch("hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1.C.CDLL") as loader:
        from hhs_runtime.hhs_pass220_recursive_hnan_native_rule_preflight_v1 import (
            GlobalReceipt, VERSION, MASK,
        )
        import ctypes
        def verify(pointer):
            receipt=ctypes.cast(pointer,ctypes.POINTER(GlobalReceipt)).contents
            receipt.version=VERSION
            receipt.decision=1
            receipt.required_rule_mask=MASK
            receipt.verified_rule_mask=MASK
            for key in ("jordan_depth2_verified","minimal_polynomial_degree4_verified",
                        "degree4_recurrence_verified","hnan_channel_order_preserved",
                        "global_delta_denominator_preserved","xy_yx_distinct","zw_wz_distinct"):
                setattr(receipt,key,1)
            return 0
        loader.return_value.hhs_exact_pass219_hnan_global_system_verify.side_effect=verify
        with pytest.raises(SymbolicTensorError, match="LEAN_INSTANCE_THEOREM_REQUIRED"):
            native_recursive_hnan_preflight("ADD",ref(1),ref(1),native_library=str(library_path),
                lean_normalization_operands=[
                    {"numerator":1,"denominator":2},
                    {"numerator":2,"denominator":3},
                    {"numerator":3,"denominator":4},
                ])
