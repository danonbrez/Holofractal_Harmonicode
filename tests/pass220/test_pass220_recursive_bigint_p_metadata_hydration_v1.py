import pytest
from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import TensorRef, SymbolicTensorError
from hhs_runtime.hhs_pass220_recursive_bigint_p_metadata_hydration_v1 import hydrate_recursive_p_metadata, LOCAL_BASE

def ref(p):
    return TensorRef(p,"BIGINT","a"*216,"global")

@pytest.mark.parametrize("p",[0,1,1728,LOCAL_BASE-1,LOCAL_BASE,LOCAL_BASE+7,LOCAL_BASE**3+LOCAL_BASE*19+11])
def test_recursive_crt_bigint_segments_roundtrip(p):
    r=hydrate_recursive_p_metadata("ADD",ref(p),ref(0))
    assert r["P"]==str(p)
    assert r["segment_count"]==max(1,len(r["ordered_segments_least_significant_first"]))
    assert all(s["crt_roundtrip_exact"] for s in r["ordered_segments_least_significant_first"])
    assert r["recursive_bigint_exact"]
    assert r["segments_are_metadata_addresses_not_canonical_states"]
    assert not r["canonical_vm81_admission"]
    assert not r["hnan_native_gate_executed"]
    assert r==hydrate_recursive_p_metadata("ADD",ref(p),ref(0))

def test_multilevel_depth_and_order():
    p=LOCAL_BASE**3+LOCAL_BASE*19+11
    r=hydrate_recursive_p_metadata("ADD",ref(p),ref(0))
    assert [s["local_P"] for s in r["ordered_segments_least_significant_first"]]==["11","19","0","1"]
    assert r["segment_count"]==4

def test_invalid_lane_fails_closed():
    with pytest.raises(SymbolicTensorError,match="SIX_LANE"):
        hydrate_recursive_p_metadata("ADD",ref(1),ref(1),lane_index=12)

def test_ordered_provenance_retained():
    a=hydrate_recursive_p_metadata("ORDERED_MUL",ref(2),ref(3))
    b=hydrate_recursive_p_metadata("ORDERED_MUL",ref(3),ref(2))
    assert a["P"]==b["P"]=="6"
    assert a["candidate_sha256"]!=b["candidate_sha256"]
