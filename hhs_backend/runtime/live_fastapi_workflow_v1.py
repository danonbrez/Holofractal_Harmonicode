"""
HHS Live FastAPI Workflow v1
============================

Pass 045 lifecycle controller for the authoritative FastAPI runtime.  It owns a
bounded background tick loop that emits real kernel output through the canonical
four websocket channels.  Node/Vite remains a GUI/proxy surface only.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

from hhs_backend.runtime.live_kernel_event_bridge_v1 import LiveKernelEventBridge
from hhs_python.runtime.hhs_runtime_emulator import HHSCEmulator

VERSION = "PASS_045_LIVE_FASTAPI_KERNEL_RUNTIME_V1"
WORKFLOW_SCHEMA = "HHS_LIVE_FASTAPI_WORKFLOW_V1"


@dataclass
class LiveFastAPIRuntimeWorkflow:
    runtime_emulator: HHSCEmulator
    runtime_graph: Optional[Any] = None
    interval_seconds: float = 1.0
    auto_start: bool = True
    _task: Optional[asyncio.Task] = None
    _running: bool = False
    _tick_count: int = 0
    _last_emission: Optional[Dict[str, Any]] = None
    _errors: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.bridge = LiveKernelEventBridge(self.runtime_emulator)

    async def start(self) -> Dict[str, Any]:
        if self._running:
            return self.status()
        self._running = True
        if self.auto_start:
            self._task = asyncio.create_task(self._run_loop())
        return self.status()

    async def stop(self) -> Dict[str, Any]:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        return self.status()

    async def _run_loop(self) -> None:
        while self._running:
            try:
                await self.tick_once({"source": "live_fastapi_workflow.background_loop"})
            except Exception as exc:  # pragma: no cover - retained for live server robustness
                self._errors.append(str(exc))
            await asyncio.sleep(max(self.interval_seconds, 0.05))

    async def tick_once(self, instruction: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        emission = await self.bridge.emit_tick_event(instruction=instruction)
        self._tick_count += 1
        self._last_emission = emission
        if self.runtime_graph is not None:
            try:
                packet = self.runtime_emulator.controller.export_multimodal_packet()
                self.runtime_graph.ingest_runtime_state(packet)
            except Exception as exc:
                self._errors.append(f"graph_ingest:{exc}")
        return emission

    def status(self) -> Dict[str, Any]:
        return {
            "schema": "HHS_LIVE_FASTAPI_WORKFLOW_STATUS_V1",
            "version": VERSION,
            "running": self._running,
            "background_task_active": self._task is not None and not self._task.done(),
            "tick_count": self._tick_count,
            "last_emission": self._last_emission,
            "errors": list(self._errors[-8:]),
            "bridge": self.bridge.status(),
            "channels": ["/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport"],
            "node_role": "GUI_PROXY_ONLY_NO_RUNTIME_EVENT_AUTHORITY",
        }


def live_fastapi_workflow_self_test() -> Dict[str, Any]:
    async def _run():
        workflow = LiveFastAPIRuntimeWorkflow(HHSCEmulator(), auto_start=False)
        await workflow.start()
        emission = await workflow.tick_once({"source": "self_test"})
        await workflow.stop()
        return {
            "schema": "HHS_LIVE_FASTAPI_WORKFLOW_SELF_TEST_V1",
            "version": VERSION,
            "ok": bool(emission.get("ok") and workflow.status().get("tick_count") == 1),
            "emission": emission,
            "status": workflow.status(),
        }
    return asyncio.run(_run())


if __name__ == "__main__":
    print(live_fastapi_workflow_self_test())
