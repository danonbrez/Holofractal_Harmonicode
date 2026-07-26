from hhs_backend.runtime.live_kernel_event_bridge_v1 import (
    AUTHORITY,
    LiveKernelEventBridge,
    live_kernel_event_bridge_self_test,
)
from hhs_python.runtime.hhs_runtime_emulator import HHSCEmulator


def _emulator_tick():
    emulator = HHSCEmulator()
    return emulator, emulator.tick({"source": "boundary_test"})


def _bridge_and_tick():
    emulator = HHSCEmulator()
    bridge = LiveKernelEventBridge(runtime_emulator=emulator)
    tick = bridge.tick_kernel({"source": "boundary_test"})
    return bridge, tick


def test_hhs_emulator_boot_contract():
    emulator = HHSCEmulator()
    boot = emulator.boot()
    assert boot["booted"] is True
    assert boot["authority_audit"]["ok"] is True


def test_hhs_emulator_authorized_tick_completes():
    emulator, result = _emulator_tick()
    assert emulator.booted is True
    assert isinstance(result, dict)


def test_hhs_emulator_tick_runtime_projection():
    _, result = _emulator_tick()
    assert result["runtime"]["state_hash72"]


def test_hhs_emulator_tick_receipt_projection():
    _, result = _emulator_tick()
    assert result["receipt"]["receipt_hash72"]


def test_hhs_emulator_tick_authority_projection():
    _, result = _emulator_tick()
    assert result["authority_audit"]["ok"] is True


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
