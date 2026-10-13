import pytest
from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import BridgeSearchError
from hhs_runtime.hhs_pass220_native_numpy_ieee_p_bridge_v1 import verify_ieee_p_bridge

@pytest.mark.parametrize("bits", [
    0x0000000000000000,
    0x8000000000000000,
    0x3ff0000000000000,
    0x0000000000000001,
    0x7fefffffffffffff,
])
def test_existing_numpy_ieee_ingress_to_lo_shu_is_exact(bits):
    receipt=verify_ieee_p_bridge(bits)
    assert receipt["P_decimal"] == str(bits)
    assert receipt["raw_ieee_binary64_hex"] == f"{bits:016x}"
    assert receipt["raw_bits_roundtrip_verified"]
    assert receipt["type_codec_executed"]
    assert receipt["edge_kinds"] == [
        "DECLARED_SAME_P_MODALITY_BRIDGE",
        "DECLARED_SAME_P_MODALITY_BRIDGE",
    ]
    assert receipt["float_numeric_value_is_bit_integer"] is False
    assert receipt["native_admission"] is False
    assert receipt["hash216_persisted"] is False
    assert verify_ieee_p_bridge(bits) == receipt

@pytest.mark.parametrize("bits", [True,-1,1<<64,1.5,"0x3ff0000000000000"])
def test_invalid_bit_ingress_fails_closed(bits):
    with pytest.raises(BridgeSearchError, match="IEEE_BINARY64_EXACT_BITS_REQUIRED"):
        verify_ieee_p_bridge(bits)

@pytest.mark.parametrize("bits", [0x7ff0000000000000,0x7ff8000000000001])
def test_nonfinite_bits_obey_inherited_numpy1_admission(bits):
    with pytest.raises(BridgeSearchError, match="IEEE_NUMPY1_BOUNDARY_NOT_ADMITTED"):
        verify_ieee_p_bridge(bits)
