from hhs_python.runtime.hhs_exact_ctypes_bridge import HHSExactRuntimeBridge

from hhs_runtime.harmonicode_lane5_t64_exhaustive_resolution_v1 import (
    phase_product_reference,
)


def test_native_phase_product_matches_t004_reference_for_all_64_pairs():
    bridge = HHSExactRuntimeBridge()
    assert bridge.validate() is True
    compared = 0
    for left in range(8):
        for right in range(8):
            native = bridge.phase_product(left, right)
            expected = phase_product_reference(left, right)
            assert native["left_basis"] == left
            assert native["right_basis"] == right
            assert native["raw_additive_phase"] == expected["raw_additive_phase"]
            assert native["phase"] == expected["phase"]
            assert native["closure"] == expected["native_closure_flag"]
            assert (
                native["phase"] + expected["reciprocal_phase"]
            ) % 72 == 0
            compared += 1
    assert compared == 64


def test_native_vm5184_addresses_cover_81_times_64_exactly():
    bridge = HHSExactRuntimeBridge()
    seen = set()
    for cell in range(81):
        for operation64 in range(64):
            left, right = divmod(operation64, 8)
            address = bridge.vm5184_address(cell, left, right)
            assert address == cell * 64 + operation64
            assert bridge.vm5184_decode(address) == (cell, left, right)
            seen.add(address)
    assert len(seen) == 5184
    assert seen == set(range(5184))
