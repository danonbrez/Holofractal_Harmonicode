from hhs_runtime.hhs_expanded_state_decay_lifecycle_v1 import (
    expanded_state_decay_lifecycle_self_test,
    register_expanded_state,
    self_delete_expired_expanded_state,
    verify_no_expired_expanded_states,
)


def test_expanded_state_decay_self_test_passes():
    assert expanded_state_decay_lifecycle_self_test()["ok"] is True


def test_expired_unpropagated_state_self_deletes():
    handle = register_expanded_state("expanded:test", {"schema": "X"}, source_surface_id="s", created_at_tick=1, decay_window_ticks=2)
    deleted = self_delete_expired_expanded_state(handle, current_tick=3)
    assert deleted["ok"] is True
    assert deleted["expanded_payload"] is None
    assert deleted["decay_witness"]["expanded_payload_retained"] is False


def test_unexpired_stalled_state_is_reported():
    handle = register_expanded_state("expanded:test", {"schema": "X"}, source_surface_id="s", created_at_tick=1, decay_window_ticks=2)
    audit = verify_no_expired_expanded_states([handle], current_tick=3)
    assert audit["ok"] is False
