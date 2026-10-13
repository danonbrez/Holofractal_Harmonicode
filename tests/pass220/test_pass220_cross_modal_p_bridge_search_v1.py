import pytest
from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import (
    Node, BridgeSearchError, find_bridge, relations,
)

def test_arithmetic_recognizes_exact_edges():
    assert "SUCCESSOR" in relations(144,145)
    assert "SQUARE" in relations(12,144)
    assert "FACTOR_TO_MULTIPLE" in relations(12,144)
    assert "ROOT_SQUARE" in relations(144,12)
    assert relations(12,145) == ()

def test_multimodal_bridge_via_different_p_and_shared_modality():
    nodes = (Node(12,"TEXT"), Node(144,"TEXT"),
             Node(144,"ARRAY"), Node(145,"ARRAY"))
    r = find_bridge(nodes[0],nodes[-1],nodes,
                    declared_same_p_bridges=(("TEXT","ARRAY"),))
    assert r["found"]
    assert r["hops"] == 3
    assert r["edge_kinds"] == [
        "SQUARE","DECLARED_SAME_P_MODALITY_BRIDGE","SUCCESSOR"
    ]
    assert r["path"][2] == {"P":"144","modality":"ARRAY"}
    assert not r["native_admission"]
    assert not r["type_converter_executed"]
    assert not r["hash72_minted"]

def test_no_unregistered_modality_conversion():
    nodes=(Node(12,"TEXT"),Node(144,"TEXT"),Node(144,"ARRAY"))
    r=find_bridge(nodes[0],nodes[-1],nodes)
    assert not r["found"]
    assert not r["exhaustive"]

def test_hop_limit_and_determinism():
    nodes=(Node(12,"TEXT"),Node(144,"TEXT"),Node(144,"ARRAY"),Node(145,"ARRAY"))
    args=dict(declared_same_p_bridges=(("TEXT","ARRAY"),))
    assert find_bridge(nodes[0],nodes[-1],nodes,max_hops=2,**args)["found"] is False
    assert find_bridge(nodes[0],nodes[-1],nodes,**args)==find_bridge(nodes[0],nodes[-1],nodes,**args)

@pytest.mark.parametrize("bad",[True,-1,1.5])
def test_exact_p_only(bad):
    with pytest.raises(BridgeSearchError):
        Node(bad,"TEXT")
