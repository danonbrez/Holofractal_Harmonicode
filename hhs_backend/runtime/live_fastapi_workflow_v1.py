"""
HHS Live FastAPI Workflow v1
============================

Pass 045 lifecycle controller for the authoritative FastAPI runtime. It owns a
bounded background tick loop that emits real kernel output through the canonical
four websocket channels. Node/Vite remains a GUI/proxy surface only.

The live cognition coordinator is downstream of committed kernel execution. It
may index, replay, predict, and align goals, but it receives no VM81 mutation
authority.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

from hhs_backend.api.cognition_routes import register_cognition_routes
from hhs_backend.runtime.immutable_agent_index_hooks_v1 import install_agent_index_hooks
from hhs_backend.runtime.live_cognition_runtime_v1 import (
    HHSRuntimeCognitionCoordinator,
    live_cognition_runtime,
)
from hhs_backend.runtime.live_kernel_event_bridge_v1 import LiveKernelEventBridge
from hhs_python.runtime.hhs_runtime_emulator import HHSCEmulator

VERSION = "PASS_045_LIVE_FASTAPI_KERNEL_RUNTIME_V1"
WORKFLOW_SCHEMA = "HHS_LIVE_FASTAPI_WORKFLOW_V1"

register_cognition_routes()
install_agent_index_hooks(live_cognition_runtime)


@dataclass
class LiveFastAPIRuntimeWorkflow:
    runtime_emulator: HHSCEmulator
    runtime_graph: Optional[Any] = None
    cognition_runtime: Optional[Any] = None
    interval_seconds: float = 1.0
    auto_start: bool = True
    _task: Optional[asyncio.Task] = None
    _running: bool = False
    _tick_count: int = 0
    _last_emission: Optional[Dict[str, Any]] = None
    _last_cognition: Optional[Dict[str, Any]] = None
    _errors: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.bridge = LiveKernelEventBridge(self.runtime_emulator)
        if self.cognition_runtime is None:
            self.cognition_runtime = live_cognition_runtime
        if self.cognition_runtime is not None:
            install_agent_index_hooks(self.cognition_runtime)

    async def start(self) -> Dict[str, Any]:
        if self._running:
            return self.status()
        self._running = True
        try:
            if self.cognition_runtime is not None:
                await asyncio.to_thread(self.cognition_runtime.initialize)

            # Runtime authority is not ready merely because a task was scheduled.
            # Complete one real emulator tick, Hash72 receipt, runtime-state hash,
            # graph ingress, cognition pass, and four-channel propagation before
            # startup returns or health may classify the workflow as online.
            if self._tick_count == 0 or not self._last_emission:
                await self.tick_once({"source": "live_fastapi_workflow.startup"})

            if self.auto_start:
                self._task = asyncio.create_task(self._run_loop())
            return self.status()
        except Exception as exc:
            self._errors.append(f"startup:{exc}")
            self._errors = self._errors[-16:]
            self._running = False
            raise

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
            except Exception as exc:  # pragma: no cover
                self._errors.append(str(exc))
                self._errors = self._errors[-16:]
            await asyncio.sleep(max(self.interval_seconds, 0.05))

    async def tick_once(
        self,
        instruction: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        # Kernel execution, packet projection, and graph ingestion are genuine
        # synchronous workloads. Keep them off the FastAPI event loop so live
        # health, authority, UI, and websocket requests remain serviceable while
        # the next reusable continuation snapshot is computed.
        emission = await self.bridge.emit_tick_event(instruction=instruction)
        self._tick_count += 1

        packet = await asyncio.to_thread(
            self.runtime_emulator.controller.export_multimodal_packet,
        )
        if self.runtime_graph is not None:
            try:
                await asyncio.to_thread(self.runtime_graph.ingest_runtime_state, packet)
            except Exception as exc:
                self._errors.append(f"graph_ingest:{exc}")
                self._errors = self._errors[-16:]

        cognition = None
        if self.cognition_runtime is not None:
            try:
                cognition = await asyncio.to_thread(
                    self.cognition_runtime.process_packet,
                    packet,
                    emission=emission,
                )
            except Exception as exc:
                self._errors.append(f"cognition_tick:{exc}")
                self._errors = self._errors[-16:]

        record = dict(emission)
        record["cognition"] = cognition
        self._last_cognition = cognition
        self._last_emission = record
        return record

    def status(self) -> Dict[str, Any]:
        cognition_status = None
        if self.cognition_runtime is not None:
            try:
                cognition_status = self.cognition_runtime.status()
            except Exception as exc:  # pragma: no cover
                cognition_status = {"ok": False, "error": str(exc)}
        last_emission = dict(self._last_emission or {})
        receipt_ready = bool(
            last_emission.get("ok")
            and last_emission.get("receipt_hash72")
            and last_emission.get("runtime_state_hash72")
        )
        return {
            "schema": "HHS_LIVE_FASTAPI_WORKFLOW_STATUS_V1",
            "version": VERSION,
            "running": self._running,
            "authority_ready": bool(self._running and receipt_ready),
            "background_task_active": self._task is not None and not self._task.done(),
            "tick_count": self._tick_count,
            "last_emission": self._last_emission,
            "last_cognition": self._last_cognition,
            "receipt_ready": receipt_ready,
            "errors": list(self._errors[-8:]),
            "bridge": self.bridge.status(),
            "cognition": cognition_status,
            "channels": ["/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport"],
            "node_role": "GUI_PROXY_ONLY_NO_RUNTIME_EVENT_AUTHORITY",
            "event_loop_blocking_kernel_work": False,
        }


def live_fastapi_workflow_self_test() -> Dict[str, Any]:
    async def _run():
        workflow = LiveFastAPIRuntimeWorkflow(
            HHSCEmulator(),
            cognition_runtime=HHSRuntimeCognitionCoordinator(),
            auto_start=False,
        )
        await workflow.start()
        emission = dict(workflow.status().get("last_emission") or {})
        await workflow.stop()
        workflow_status = workflow.status()
        cognition_ok = bool(emission.get("cognition", {}).get("processed"))
        return {
            "schema": "HHS_LIVE_FASTAPI_WORKFLOW_SELF_TEST_V1",
            "version": VERSION,
            "ok": bool(
                emission.get("ok")
                and workflow_status.get("tick_count") == 1
                and workflow_status.get("receipt_ready")
            ),
            "cognition_ok": cognition_ok,
            "emission": emission,
            "status": workflow_status,
        }

    return asyncio.run(_run())


if __name__ == "__main__":
    print(live_fastapi_workflow_self_test())
