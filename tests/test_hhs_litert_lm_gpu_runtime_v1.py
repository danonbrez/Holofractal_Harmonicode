from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

from hhs_backend.runtime.hhs_litert_lm_accelerated_transport_v1 import (
    LiteRTLMAcceleratedTransport,
    compose_request_model_id,
    normalize_backend,
)
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import LiteRTLMConfig
from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import (
    HHSAPIAssistantService,
)

ROOT = Path(__file__).resolve().parents[1]


class CaptureTransport(LiteRTLMAcceleratedTransport):
    def __init__(self, config: LiteRTLMConfig, *, backend: str):
        super().__init__(config, backend=backend)
        self.last_payload = None

    def _request_sync(self, method, path, payload=None):
        self.last_payload = dict(payload or {})
        return {
            "id": "chatcmpl-gpu-test",
            "model": self.config.model_id,
            "choices": [{
                "message": {"role": "assistant", "content": "ok"},
                "finish_reason": "stop",
            }],
        }


class FakeTransport:
    async def list_models(self):
        return {"object": "list", "data": [{"id": "gemma4-12b"}]}

    async def chat_completion(self, **_):
        return {
            "id": "chatcmpl-fake",
            "model": "gemma4-12b",
            "choices": [{
                "message": {"role": "assistant", "content": "ok"},
                "finish_reason": "stop",
            }],
        }


def test_gpu_backend_is_encoded_separately_from_registry_identity() -> None:
    assert compose_request_model_id("gemma4-12b", "gpu") == "gemma4-12b,gpu"
    assert compose_request_model_id("gemma4-12b", "cpu") == "gemma4-12b,cpu"
    assert compose_request_model_id("gemma4-12b", "auto") == "gemma4-12b"
    assert normalize_backend("GPU") == "gpu"


def test_accelerated_transport_sends_gpu_model_parameter() -> None:
    config = LiteRTLMConfig(model_id="gemma4-12b")
    transport = CaptureTransport(config, backend="gpu")
    asyncio.run(
        transport.chat_completion(
            messages=[{"role": "user", "content": "hello"}],
        )
    )

    assert transport.last_payload is not None
    assert transport.last_payload["model"] == "gemma4-12b,gpu"
    assert config.model_id == "gemma4-12b"


def test_assistant_status_exposes_accelerator_boundary(monkeypatch) -> None:
    monkeypatch.setenv("HHS_LITERT_LM_BACKEND", "gpu")
    service = HHSAPIAssistantService(
        config=LiteRTLMConfig(model_id="gemma4-12b"),
        transport=FakeTransport(),
    )
    status = service.status()

    assert status["model_id"] == "gemma4-12b"
    assert status["request_model_id"] == "gemma4-12b,gpu"
    assert status["execution_backend"] == "gpu"
    assert status["gpu_accelerator_required"] is True
    assert status["status_root_hash72"]


def test_cpu_accelerator_probe_is_executable_without_gpu() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "probe_litert_lm_accelerator.py"),
            "--backend",
            "cpu",
            "--require",
        ],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    payload = json.loads(completed.stdout)
    assert payload["ready"] is True
    assert payload["backend"] == "cpu"
    assert payload["accelerator_required"] is False


def test_gpu_deployment_contract_covers_remote_provider_topology() -> None:
    deployment = (ROOT / "docs" / "HHS_LITERT_LM_GPU_DEPLOYMENT.md").read_text(
        encoding="utf-8"
    )
    assert "Vulkan" in deployment
    assert "gemma4-12b,gpu" in deployment
    assert "HHS_LITERT_LM_PROVIDER_MODE=external" in deployment
    assert "HHS_LITERT_LM_STRICT_STARTUP=1" in deployment
