import pytest
from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import Node, BridgeSearchError
from hhs_runtime.hhs_pass220_reciprocal_modality_witness_binding_v1 import (
    bind_executed_reciprocal_candidate,
)

def test_exact_bidirectional_codec_witness():
    nodes=(Node(12,"BIGINT"),Node(144,"BIGINT"),
           Node(144,"LO_SHU_SERIALIZED"),Node(145,"LO_SHU_SERIALIZED"))
    r=bind_executed_reciprocal_candidate(nodes[0],nodes[-1],nodes)
    assert r["bidirectional_codec_roundtrip_verified"]
    assert r["conditional_path_theorem_available"]
    assert r["lean_theorem"]=="admitted_coverage_implies_bidirectional_paths"
    assert not r["universal_coverage_proved"]
    assert not r["ordered_reciprocal_closure_proved_for_route"]
    assert not r["canonical_vm81_admission"]
    assert not r["canonical_hash72_minted"]
    assert not r["canonical_hash216_persisted"]
    assert bind_executed_reciprocal_candidate(nodes[0],nodes[-1],nodes)==r

def test_unreachable_direction_rejected():
    nodes=(Node(12,"BIGINT"),Node(144,"BIGINT"),
           Node(144,"LO_SHU_SERIALIZED"),Node(145,"LO_SHU_SERIALIZED"))
    with pytest.raises(BridgeSearchError, match="BIDIRECTIONAL_EXECUTED_PATH_REQUIRED"):
        bind_executed_reciprocal_candidate(nodes[0],nodes[-1],nodes,max_hops=2)

def test_unknown_codec_rejected():
    nodes=(Node(4,"TEXT"),Node(4,"LO_SHU_SERIALIZED"))
    with pytest.raises(BridgeSearchError, match="REGISTERED_EXECUTABLE_CODEC_REQUIRED"):
        bind_executed_reciprocal_candidate(nodes[0],nodes[1],nodes)
