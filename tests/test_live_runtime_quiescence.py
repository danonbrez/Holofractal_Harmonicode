from __future__ import annotations

import asyncio

import hhs_backend.runtime.live_fastapi_workflow_v1 as workflow_module
from hhs_backend.runtime.live_fastapi_workflow_v1 import (
    LiveFastAPIRuntimeWorkflow,
    _env_enabled,
)


class _FakeController:
    def export_multimodal_packet(self):
        return {
            "runtime": {
                "state_hash72": "H" * 72,
                "step": 1,
                "receipt_hash72": "R" * 72,
            }
        }


class _FakeConfig:
    boot_id = "quiescence-test"


class _FakeEmulator:
    def __init__(self):
        self.controller = _FakeController()
        self.config = _FakeConfig()
        self.booted = True
        self.tick_history = []


class _FakeBridge:
    def __init__(self):
        self.calls = 0

    async def emit_tick_event(self, instruction=None):
        self.calls += 1
        return {
            "ok": True,
            "event_hash72": "E" * 72,
            "receipt_hash72": "R" * 72,
            "sequence_id": self.calls,
            "kernel_tick": self.calls,
            "runtime_state_hash72": "H" * 72,
        }

    def status(self):
        return {"calls": self.calls}


class _FakeCognition:
    def __init__(self):
        self.enabled = True
        self.calls = 0

    def initialize(self):
        return {"initialized": True, "enabled": self.enabled}

    def process_packet(self, packet, *, emission=None):
        self.calls += 1
        if not self.enabled:
            return {"processed": False, "status": "COGNITION_AUTO_TICK_DISABLED"}
        return {"processed": True}

    def status(self):
        return {"enabled": self.enabled, "calls": self.calls}


def _isolate_unrelated_agent_index_hooks(monkeypatch):
    monkeypatch.setattr(
        workflow_module,
        "install_agent_index_hooks",
        lambda _cognition: None,
    )


def test_auto_tick_flags_default_disabled(monkeypatch):
    monkeypatch.delenv("HHS_RUNTIME_AUTO_TICK", raising=False)
    monkeypatch.delenv("HHS_COGNITION_AUTO_TICK", raising=False)
    assert _env_enabled("HHS_RUNTIME_AUTO_TICK", default=False) is False
    assert _env_enabled("HHS_COGNITION_AUTO_TICK", default=False) is False


def test_explicit_auto_tick_opt_in(monkeypatch):
    monkeypatch.setenv("HHS_RUNTIME_AUTO_TICK", "1")
    monkeypatch.setenv("HHS_COGNITION_AUTO_TICK", "true")
    assert _env_enabled("HHS_RUNTIME_AUTO_TICK", default=False) is True
    assert _env_enabled("HHS_COGNITION_AUTO_TICK", default=False) is True


def test_server_style_auto_start_request_is_quiescent_without_env(monkeypatch):
    _isolate_unrelated_agent_index_hooks(monkeypatch)
    monkeypatch.delenv("HHS_RUNTIME_AUTO_TICK", raising=False)
    monkeypatch.delenv("HHS_COGNITION_AUTO_TICK", raising=False)
    cognition = _FakeCognition()
    workflow = LiveFastAPIRuntimeWorkflow(
        _FakeEmulator(),
        cognition_runtime=cognition,
        auto_start=True,
    )
    workflow.bridge = _FakeBridge()

    async def run():
        status = await workflow.start()
        await asyncio.sleep(0.02)
        stopped = await workflow.stop()
        return status, stopped

    status, stopped = asyncio.run(run())
    assert status["continuous_tick_requested"] is True
    assert status["continuous_tick_enabled"] is False
    assert status["background_task_active"] is False
    assert status["cognition_auto_tick_enabled"] is False
    assert status["tick_count"] == 1
    assert stopped["tick_count"] == 1
    assert workflow.bridge.calls == 1
    assert cognition.calls == 1


def test_continuous_tick_requires_explicit_env_opt_in(monkeypatch):
    _isolate_unrelated_agent_index_hooks(monkeypatch)
    monkeypatch.setenv("HHS_RUNTIME_AUTO_TICK", "1")
    monkeypatch.delenv("HHS_COGNITION_AUTO_TICK", raising=False)
    workflow = LiveFastAPIRuntimeWorkflow(
        _FakeEmulator(),
        cognition_runtime=_FakeCognition(),
        interval_seconds=0.005,
        auto_start=True,
    )
    workflow.bridge = _FakeBridge()

    async def run():
        await workflow.start()
        await asyncio.sleep(0.03)
        status = workflow.authority_status()
        await workflow.stop()
        return status

    status = asyncio.run(run())
    assert status["continuous_tick_enabled"] is True
    assert status["background_task_active"] is True
    assert status["tick_count"] > 1
