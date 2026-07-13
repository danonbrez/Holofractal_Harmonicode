from hhs_python.runtime.hhs_ctypes_bridge import HHSHash72RingBridge, HASH72_LEN


def test_hash72_u72_ring_initializes_at_zero_sum_closure():
    ring = HHSHash72RingBridge()
    state = ring.export()

    assert len(state["dna"]) == HASH72_LEN
    assert ring.validate()
    assert sum(state["positions"]) % 72 == 0


def test_hash72_u72_rotation_preserves_zero_sum_and_trace_profile():
    ring = HHSHash72RingBridge()
    before = ring.export()

    assert ring.rotate(5, 17)
    after = ring.export()

    assert after["dna"] != before["dna"]
    assert after["trace_count"] == 1
    assert after["last_index"] == 5
    assert after["last_delta"] == 17
    assert sum(after["positions"]) % 72 == 0
    assert after["rotation_profile"][5] == before["rotation_profile"][5] + 17
    assert after["rotation_profile"][6] == before["rotation_profile"][6] - 17


def test_hash72_u72_reverse_state_uses_rotation_profile_key_schedule():
    ring = HHSHash72RingBridge()
    before = ring.export()

    ring.rotate(0, 5)
    ring.rotate(71, -12)
    reversed_ring = ring.reverse_state()
    reversed_state = reversed_ring.export()

    assert reversed_ring.validate()
    assert reversed_state["positions"] == before["positions"]
    assert reversed_state["dna"] == before["dna"]


def test_hash72_u72_tensor_projection_has_81_cells_and_72_projected_positions():
    ring = HHSHash72RingBridge()
    projection = ring.tensor_project()

    assert len(projection) == 81
    assert sum(1 for cell in projection if cell != 255) == 72
