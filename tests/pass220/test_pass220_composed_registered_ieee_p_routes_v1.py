import pytest
from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import BridgeSearchError
from hhs_runtime.hhs_pass220_composed_registered_ieee_p_routes_v1 import compose_ieee_p_route

def test_composed_exact_arithmetic_route():
    r=compose_ieee_p_route((2,4,5,25))
    assert r["edge_count"]==3
    assert r["link_semantics"] == "INHERITED_BIGINT_GEOMETRY_METADATA_RELATIONS"
    assert r["new_canonical_state_minted_per_link"] is False
    assert r["independent_vm81_state_transition_claimed"] is False
    assert r["edge_kinds"]==["SQUARE","SUCCESSOR","SQUARE"]
    assert r["inverse_edge_kinds"]==["ROOT_SQUARE","PREDECESSOR","ROOT_SQUARE"]
    assert r["exact_edgewise_bidirectional_codec_roundtrip"]
    assert r["composed_route_candidate_verified"]
    assert len(r["edge_candidate_roots"])==3
    assert not r["native_lean_runtime_proof_attached"]
    assert not r["ordered_reciprocal_tensor_closure_proved"]
    assert not r["canonical_vm81_admission"]
    assert not r["hash216_persisted"]
    assert r==compose_ieee_p_route((2,4,5,25))

def test_endpoint_and_one_edge():
    r=compose_ieee_p_route((0,1))
    assert r["edge_count"]==1

@pytest.mark.parametrize("indices",[(),(1,),(2,7),(1,True),(1,-1),tuple(range(66))])
def test_invalid_or_unproven_edge_fails_closed(indices):
    with pytest.raises(BridgeSearchError):
        compose_ieee_p_route(indices)
