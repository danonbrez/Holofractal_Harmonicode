import pytest
from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import Node, BridgeSearchError
from hhs_runtime.hhs_pass220_executed_p_bridge_roundtrip_v1 import execute_p_bridge

def test_executed_reversible_cross_modal_p_path():
    nodes = (Node(12,"BIGINT"),Node(144,"BIGINT"),
             Node(144,"LO_SHU_SERIALIZED"),Node(145,"LO_SHU_SERIALIZED"))
    r=execute_p_bridge(nodes[0],nodes[-1],nodes)
    assert r["found"] and r["hops"] == 3
    assert r["edge_kinds"] == [
        "SQUARE","DECLARED_SAME_P_MODALITY_BRIDGE","SUCCESSOR"
    ]
    assert r["type_converter_executed"]
    assert r["exact_external_type_roundtrip_verified"]
    assert all(w["roundtrip_verified"] for w in r["projection_witnesses"])
    assert r["projection_witnesses"][1]["canonical_root_sha256"] == r["projection_witnesses"][2]["canonical_root_sha256"]
    assert not r["native_admission"] and not r["hash72_minted"]
    assert execute_p_bridge(nodes[0],nodes[-1],nodes) == r

def test_unknown_modality_must_have_real_codec():
    nodes=(Node(12,"TEXT"),Node(144,"TEXT"))
    with pytest.raises(BridgeSearchError, match="REGISTERED_EXECUTABLE_CODEC_REQUIRED"):
        execute_p_bridge(nodes[0],nodes[1],nodes)

def test_local_encoding_limit_requires_higher_nesting_not_truncation():
    nodes=(Node(9**81,"BIGINT"),)
    with pytest.raises(BridgeSearchError,match="HIGHER_DEPTH_CONSTRUCTOR_REQUIRED"):
        execute_p_bridge(nodes[0],nodes[0],nodes)

def test_bounded_missing_route_remains_candidate_only():
    nodes=(Node(12,"BIGINT"),Node(145,"LO_SHU_SERIALIZED"))
    r=execute_p_bridge(nodes[0],nodes[1],nodes,max_hops=1)
    assert not r["found"]
    assert not r["type_converter_executed"]
