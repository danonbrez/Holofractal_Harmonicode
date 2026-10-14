import pytest

from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import BridgeSearchError
from hhs_runtime.hhs_pass220_registry_aware_p_modality_bridge_v1 import (
    inspect_numpy_ieee_bridge,
    require_registered_native_modality,
)

@pytest.mark.parametrize("bits", [
    0x0000000000000000,
    0x8000000000000000,
    0x3ff0000000000000,
    0x0000000000000001,
])
def test_numpy_registered_codec_reconstructs_exact_ieee_bits(bits):
    receipt = inspect_numpy_ieee_bridge(bits)
    assert receipt["capability_id"] == "numpy"
    assert receipt["P_decimal"] == str(bits)
    assert receipt["exact_registered_codec_roundtrip"]
    assert receipt["registered_native_surfaces"]
    assert not receipt["external_fallback_used"]
    assert not receipt["canonical_vm81_admission"]
    assert not receipt["canonical_hash72_mint"]
    assert not receipt["canonical_hash216_persistence"]
    assert inspect_numpy_ieee_bridge(bits) == receipt

def test_existing_native_numpy_registry_surface():
    paths = require_registered_native_modality("numpy")
    assert "hhs_runtime/hhs_pass220_numpy_harmonicode_array_v1.py" in paths

@pytest.mark.parametrize("name", ["matplotlib", "nonexistent_modality", ""])
def test_unregistered_native_codec_fails_closed(name):
    with pytest.raises(BridgeSearchError):
        require_registered_native_modality(name)

@pytest.mark.parametrize("bits", [-1, 1 << 64, True, "3ff0000000000000"])
def test_bad_ieee_bits_fail_closed(bits):
    with pytest.raises(BridgeSearchError):
        inspect_numpy_ieee_bridge(bits)
