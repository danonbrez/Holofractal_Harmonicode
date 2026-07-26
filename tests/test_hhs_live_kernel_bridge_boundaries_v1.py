from hhs_backend.runtime.live_kernel_event_bridge_v1 import (
    AUTHORITY,
    LiveKernelEventBridge,
    live_kernel_event_bridge_self_test,
)
from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_python.runtime.hhs_runtime_emulator import HHSCEmulator
from hhs_runtime.hhs_authority_gate_v1 import audit_runtime_authority
from hhs_runtime.hhs_service_registry_v1 import (
    HHSServiceRegistry,
    make_default_service_registry,
)


def _emulator_tick():
    emulator = HHSCEmulator()
    return emulator, emulator.tick({"source": "boundary_test"})


def _bridge_and_tick():
    emulator = HHSCEmulator()
    bridge = LiveKernelEventBridge(runtime_emulator=emulator)
    tick = bridge.tick_kernel({"source": "boundary_test"})
    return bridge, tick


def test_hhs_runtime_controller_construction_contract():
    controller = HHSRuntimeController()
    assert controller.runtime is not None


def test_hhs_empty_service_registry_construction_contract():
    controller = HHSRuntimeController()
    registry = HHSServiceRegistry(controller=controller)
    assert registry.controller is controller


def test_hhs_default_service_registry_construction_contract():
    controller = HHSRuntimeController()
    registry = make_default_service_registry(controller)
    assert registry.services()


def test_hhs_emulator_construction_contract():
    emulator = HHSCEmulator()
    assert emulator.controller is not None
    assert emulator.service_registry is not None


def test_hhs_emulator_native_abi_contract():
    emulator = HHSCEmulator()
    assert emulator.controller.runtime.validate_abi() is True


def test_hhs_emulator_initial_authority_contract():
    emulator = HHSCEmulator()
    state = emulator.controller.latest_runtime_state()
    audit = audit_runtime_authority(
        state,
        source="test_hhs_emulator_initial_authority_contract",
        require_receipt=False,
    ).to_dict()
    assert audit["delta_e"] == 0
    assert audit["psi"] == 0
    assert audit["theta15"] is True
    assert audit["algebraic_closure"] is True
    assert audit["ok"] is True


def test_hhs_emulator_boot_completes():
    emulator = HHSCEmulator()
    boot = emulator.boot()
    assert isinstance(boot, dict)


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
