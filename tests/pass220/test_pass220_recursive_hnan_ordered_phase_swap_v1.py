from unittest.mock import patch
import pytest
from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import TensorRef, SymbolicTensorError
from hhs_runtime.hhs_pass220_recursive_hnan_ordered_phase_swap_v1 import inspect_recursive_ordered_phase_swap

def ref(p):
    return TensorRef(p,"BIGINT","a"*216,"global")

def tree():
    return {
        "P":"72",
        "candidate_root_sha256":"e"*64,
        "inherited_i074_hash216":"a"*216,
        "ordered_leaves":[
            {"depth":0,"raw5184_sha256":"1"*64,"candidate_receipt_sha256":"2"*64,
             "hnan_gate_verified":True,"ordered_phase_witness_verified":True},
            {"depth":1,"raw5184_sha256":"3"*64,"candidate_receipt_sha256":"4"*64,
             "hnan_gate_verified":True,"ordered_phase_witness_verified":True},
        ],
    }

def test_phase_swap_preserves_order_and_does_not_scalarize():
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_ordered_phase_swap_v1.verify_recursive_hnan_hash216_tree",return_value=tree()), patch("hhs_runtime.hhs_pass220_recursive_hnan_ordered_phase_swap_v1.verify_recursive_tree_manifest",return_value=True):
        r=inspect_recursive_ordered_phase_swap("ADD",ref(70),ref(2))
    assert len(r["ordered_phase_leaves"])==2
    assert all(x["ordered_xy_ast"]!=x["ordered_yx_ast"] for x in r["ordered_phase_leaves"])
    assert all(x["u_minus_108_mod_72"]==36 for x in r["ordered_phase_leaves"])
    assert not r["typed_yx_over_xy_equals_u_minus_108_proved"]
    assert not r["canonical_vm81_admission"]

def test_tampered_manifest_fails_closed():
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_ordered_phase_swap_v1.verify_recursive_hnan_hash216_tree",return_value=tree()), patch("hhs_runtime.hhs_pass220_recursive_hnan_ordered_phase_swap_v1.verify_recursive_tree_manifest",return_value=False):
        with pytest.raises(SymbolicTensorError,match="MANIFEST_REJECTED"):
            inspect_recursive_ordered_phase_swap("ADD",ref(70),ref(2))

def test_missing_native_phase_witness_fails_closed():
    x=tree()
    x["ordered_leaves"][1]["ordered_phase_witness_verified"]=False
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_ordered_phase_swap_v1.verify_recursive_hnan_hash216_tree",return_value=x), patch("hhs_runtime.hhs_pass220_recursive_hnan_ordered_phase_swap_v1.verify_recursive_tree_manifest",return_value=True):
        with pytest.raises(SymbolicTensorError,match="PHASE_WITNESS_REQUIRED"):
            inspect_recursive_ordered_phase_swap("ADD",ref(70),ref(2))
