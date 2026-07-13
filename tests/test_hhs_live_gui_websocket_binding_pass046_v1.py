from pathlib import Path

from hhs_backend.runtime.gui_projection_contract_v1 import (
    CHANNEL_BINDINGS,
    live_gui_projection_contract_self_test,
    validate_gui_projection_payload,
)
from hhs_backend.runtime.live_kernel_event_bridge_v1 import LiveKernelEventBridge
from hhs_backend.runtime.runtime_ws import runtime_ws_manager
from hhs_python.runtime.hhs_runtime_emulator import HHSCEmulator


def test_gui_projection_contract_accepts_all_four_kernel_channels():
    result = live_gui_projection_contract_self_test()
    assert result["ok"] is True
    assert result["status"]["channel_count"] == 4
    assert result["status"]["rejected_count"] == 0


def test_runtime_ws_manager_builds_channel_specific_kernel_payloads():
    bridge = LiveKernelEventBridge(HHSCEmulator())
    tick = bridge.tick_kernel({"source": "pass046.test"})
    event = bridge.build_event(tick)

    for channel, binding in CHANNEL_BINDINGS.items():
        payload = runtime_ws_manager.build_channel_projection_payload(event, channel)
        decision = validate_gui_projection_payload(payload)
        assert decision["ok"] is True
        assert payload["channel"] == channel
        assert payload["event_type"] == binding["event_type"]
        assert payload["authority"] == "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1"
        assert payload["receipt_hash72"]
        assert payload["runtime_state_hash72"]
        assert payload["gui_projection_valid"] is True


def test_synthetic_gui_runtime_packet_is_rejected():
    decision = validate_gui_projection_payload({
        "event_type": "runtime",
        "channel": "/ws/runtime",
        "authority": "NODE_DEMO_STUB",
        "payload": {"fake": True},
        "node_generated_runtime_event": True,
    })
    assert decision["ok"] is False
    assert decision["rejection_code"] == "REJECT_NODE_GENERATED_RUNTIME_EVENT"


def test_gui_socket_manager_declares_live_kernel_fields_and_no_demo_authority():
    source = Path("hhs_gui/runtime_os/core/RuntimeSocketManager.ts").read_text()
    assert "runtime_state_hash72" in source
    assert "kernel_tick" in source
    assert "getChannelHealth" in source
    assert "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1" in source
    assert "LIVE_KERNEL_CONNECTED" in source
    assert "NODE_DEMO_STUB" not in source


def test_live_projection_panel_renders_four_kernel_channels():
    source = Path("hhs_gui/runtime_os/core/LiveRuntimeProjectionPanel.tsx").read_text()
    for channel in ("runtime", "replay", "graph", "transport"):
        assert f"live-channel-${{health.channel}}" in source
        assert channel in source
    assert "GUI projection only" in source
    assert "no live kernel packet" in source


def test_vite_proxy_keeps_node_as_gui_proxy_only():
    source = Path("hhs_gui/vite.config.ts").read_text()
    assert '"/api"' in source
    assert '"/ws"' in source
    assert "ws: true" in source
    assert "127.0.0.1:8000" in source


def test_server_exposes_gui_projection_status_route():
    source = Path("hhs_backend/server.py").read_text()
    assert "/api/runtime/gui/projection/status" in source
    assert "live_gui_projection_contract_self_test" in source
    assert "list_gui_channel_bindings" in source


def test_browser_e2e_source_verifier_is_present():
    verifier = Path("hhs_gui/scripts/live-gui-e2e-source-verify.mjs")
    assert verifier.exists()
    verifier_source = verifier.read_text()
    assert "live-gui-e2e-source-verify: PASS" in verifier_source
    assert "live-channel-runtime" in verifier_source
    assert "live-channel-replay" in verifier_source
    assert "live-channel-graph" in verifier_source
    assert "live-channel-transport" in verifier_source
