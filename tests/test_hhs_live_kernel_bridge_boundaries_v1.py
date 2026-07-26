from hhs_backend.runtime.live_kernel_event_bridge_v1 import (
    AUTHORITY,
    LiveKernelEventBridge,
    live_kernel_event_bridge_self_test,
)
from hhs_python.runtime.hhs_runtime_emulator import HHSCEmulator


def _bridge_and_tick():
    bridge = LiveKernelEventBridge(runtime_emulator=HHSCEmulator())
    tick = bridge.tick_kernel({"source": "boundary_test"})
    return bridge, tick


def test_live_kernel_bridge_emulator_tick_contract():
    _, tick = _bridge_and_tick()
    assert tick["runtime"]["state_hash72"]
    assert tick["receipt"]["receipt_hash72"]
    assert tick["authority_audit"]["ok"] is True


def test_live_kernel_bridge_event_hash_contract():
    bridge, tick = _bridge_and_tick()
    event = bridge.build_event(tick)
    assert event.event_hash72
    assert event.verify_event_hash72() is True


def test_live_kernel_bridge_websocket_projection_contract():
    bridge, tick = _bridge_and_tick()
    payload = bridge.build_event(tick).to_websocket_payload()
    assert payload["runtime_state_hash72"]
    assert payload["receipt_hash72"]
    assert payload["authority"] == AUTHORITY
    assert payload["sequence_id"] == 1


def test_live_kernel_bridge_inherited_self_test_contract():
    result = live_kernel_event_bridge_self_test()
    assert result["ok"] is True
    assert result["authority"] == AUTHORITY
    assert result["receipt_hash72"]
    assert result["runtime_state_hash72"]
