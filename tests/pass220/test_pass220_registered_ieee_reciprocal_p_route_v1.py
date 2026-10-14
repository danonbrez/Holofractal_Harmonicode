import pytest

from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import BridgeSearchError
from hhs_runtime.hhs_pass220_registered_ieee_reciprocal_p_route_v1 import (
    verify_registered_ieee_p_route,
)

@pytest.mark.parametrize("P1,P2,relation",[
    (0,1,"SUCCESSOR"),
    (2,4,"SQUARE"),
    (3,6,"FACTOR_TO_MULTIPLE"),
])
def test_registered_ieee_endpoints_have_exact_reciprocal_p_routes(P1,P2,relation):
    receipt=verify_registered_ieee_p_route(P1,P2)
    assert receipt["forward_relation"] == relation
    assert receipt["exact_bidirectional_typed_roundtrip"]
    assert receipt["source"]["P"] == str(P1)
    assert receipt["target"]["P"] == str(P2)
    assert receipt["registered_surfaces"]
    assert not receipt["ordered_reciprocal_tensor_closure_proved"]
    assert not receipt["universal_modality_coverage_proved"]
    assert not receipt["canonical_vm81_admission"]
    assert not receipt["hash216_persisted"]
    assert verify_registered_ieee_p_route(P1,P2) == receipt

def test_reverse_p_relation_is_exact_and_reconstructed():
    r=verify_registered_ieee_p_route(4,2)
    assert r["forward_relation"] in {"ROOT_SQUARE","MULTIPLE_TO_FACTOR"}
    assert r["reverse_relation"] in {"SQUARE","FACTOR_TO_MULTIPLE"}

def test_missing_exact_relation_fails_closed():
    with pytest.raises(BridgeSearchError,match="EXACT_REVERSIBLE_P_ARITHMETIC_EDGE_REQUIRED"):
        verify_registered_ieee_p_route(12,19)

@pytest.mark.parametrize("bad",[-1,True,1<<64,0x7ff0000000000000])
def test_invalid_ieee_boundary_fails_closed(bad):
    with pytest.raises(BridgeSearchError):
        verify_registered_ieee_p_route(bad,1)
