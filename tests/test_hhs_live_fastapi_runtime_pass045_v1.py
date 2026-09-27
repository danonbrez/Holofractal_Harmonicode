import asyncio
import json

from hhs_backend.runtime.live_kernel_event_bridge_v1 import (
    LiveKernelEventBridge,
    live_kernel_event_bridge_self_test,
)
from hhs_backend.runtime.live_fastapi_workflow_v1 import live_fastapi_workflow_self_test
from hhs_backend.runtime.runtime_ws import RuntimeWSManager
from hhs_python.runtime.hhs_runtime_emulator import HHSCEmulator


def test_live_kernel_event_bridge_emits_real_kernel_state():
    result = live_kernel_event_bridge_self_test()
    assert result["ok"] is True
    assert result["authority"] == "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1"
    assert result["receipt_hash72"]
    assert result["runtime_state_hash72"]


def test_live_fastapi_workflow_startup_prime_without_background_tick():
    result = live_fastapi_workflow_self_test()
    assert result["ok"] is True
    assert result["startup_status"]["authority_ready"] is True
    assert result["startup_status"]["startup_prime_complete"] is True
    assert result["startup_status"]["background_task_active"] is False
    assert result["startup_status"]["tick_count"] == 1
    assert result["emission"]["receipt_hash72"]
    assert result["emission"]["runtime_state_hash72"]
    assert result["emission"]["channels"] == ["/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport"]


class _ProjectionSocket:
    def __init__(self):
        self.accepted = False
        self.messages = []

    async def accept(self):
        self.accepted = True

    async def send_text(self, payload):
        self.messages.append(json.loads(payload))


def test_late_websocket_clients_receive_latest_committed_kernel_projection():
    async def run():
        manager = RuntimeWSManager()
        bridge = LiveKernelEventBridge(HHSCEmulator())
        tick = bridge.tick_kernel({"source": "late-client-test"})
        event = bridge.build_event(tick)
        await manager.broadcast_runtime_event(event)

        channels = [
            (manager.connect_runtime, "/ws/runtime"),
            (manager.connect_replay, "/ws/replay"),
            (manager.connect_graph, "/ws/graph"),
            (manager.connect_transport, "/ws/transport"),
        ]
        projections = {}
        for connect, channel in channels:
            socket = _ProjectionSocket()
            await connect(socket)
            assert socket.accepted is True
            assert len(socket.messages) == 1
            projections[channel] = socket.messages[0]

        return manager.metrics(), projections

    metrics, projections = asyncio.run(run())
    assert metrics["current_projection_available"] is True
    for channel, projection in projections.items():
        assert projection["channel"] == channel
        assert projection["authority"] == "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1"
        assert projection["receipt_hash72"]
        assert projection["runtime_state_hash72"]
        assert projection["gui_projection_valid"] is True
