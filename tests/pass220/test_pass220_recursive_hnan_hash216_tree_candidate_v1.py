from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import pytest
from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import TensorRef, SymbolicTensorError
from hhs_runtime.hhs_pass220_recursive_bigint_p_metadata_hydration_v1 import LOCAL_BASE
from hhs_runtime.hhs_pass220_recursive_hnan_hash216_tree_candidate_v1 import (
    verify_recursive_hnan_hash216_tree, verify_recursive_tree_manifest,
)

LINEAGE = "a"*72 + "b"*72 + "c"*72

def ref(p, ancestry=LINEAGE):
    return TensorRef(p,"BIGINT",ancestry,"global")

def inherited_gate(raw, *, candidate=None):
    return {
        "raw_roundtrip_exact":True,
        "hnan_gate_inherited":True,
        "three_binary_perspectives_retained":True,
        "raw5184_sha256":sha256(raw.encode("ascii")).hexdigest(),
        "i074_hash216":LINEAGE,
        "i074_candidate_root_sha256":"d"*64,
        "candidate_receipt_sha256":sha256(("HNAN:"+raw).encode("ascii")).hexdigest(),
    }

@pytest.mark.parametrize("p,expected",[
    (LOCAL_BASE-1,1),
    (LOCAL_BASE,2),
    (LOCAL_BASE**3+1,4),
])
def test_local_hnan_gate_for_every_recursive_segment_and_ordered_tree(p,expected):
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_hash216_tree_candidate_v1.execute_candidate",
               side_effect=inherited_gate) as native:
        result=verify_recursive_hnan_hash216_tree("ADD",ref(p),ref(0))
    assert native.call_count==expected
    assert result["segment_count"]==expected
    assert result["P"]==str(p)
    assert result["all_local_hnan_gates_executed"]
    assert verify_recursive_tree_manifest(result)
    assert not result["canonical_hash216_minted"]
    assert not result["global_composite_hnan_closure_proved"]
    assert not result["native_spatial_swap_ratio_proved"]

def test_inversion_of_ordered_segments_rejected():
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_hash216_tree_candidate_v1.execute_candidate",
               side_effect=inherited_gate):
        record=verify_recursive_hnan_hash216_tree("ADD",ref(LOCAL_BASE+7),ref(0))
    corrupted=deepcopy(record)
    corrupted["ordered_leaves"].reverse()
    assert not verify_recursive_tree_manifest(corrupted)

def test_changed_leaf_hash216_lineage_rejected():
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_hash216_tree_candidate_v1.execute_candidate",
               side_effect=inherited_gate):
        record=verify_recursive_hnan_hash216_tree("ADD",ref(LOCAL_BASE+7),ref(0))
    corrupted=deepcopy(record)
    corrupted["ordered_leaves"][1]["i074_hash216"]="z"*216
    assert not verify_recursive_tree_manifest(corrupted)

def test_mismatched_operand_ancestry_fails_closed():
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_hash216_tree_candidate_v1.execute_candidate",
               side_effect=inherited_gate):
        with pytest.raises(SymbolicTensorError,match="ANCESTRY_DISCONTINUITY"):
            verify_recursive_hnan_hash216_tree("ADD",ref(2,"x"*216),ref(3))

def test_inherited_gate_failure_fails_closed():
    def rejected(raw,*,candidate=None):
        result=inherited_gate(raw,candidate=candidate)
        result["three_binary_perspectives_retained"]=False
        return result
    with patch("hhs_runtime.hhs_pass220_recursive_hnan_hash216_tree_candidate_v1.execute_candidate",
               side_effect=rejected):
        with pytest.raises(SymbolicTensorError,match="SEGMENT_HNAN_GATE_REJECTED"):
            verify_recursive_hnan_hash216_tree("ADD",ref(2),ref(3))
