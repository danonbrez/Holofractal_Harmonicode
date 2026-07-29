from __future__ import annotations

import asyncio
import os

from fastapi.testclient import TestClient

from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    ConversationThreadStore,
    LiteRTLMConfig,
)
from hhs_backend.runtime.hhs_production_assistant_v1 import (
    ProductionAssistantService,
)


CANNED_DEMO_RESPONSE = (
    "The request was received without runtime mutation. LiteRT-LM and the "
    "canonical HHS runtime must be attached before inference can execute."
)

HARMONICODE_SOURCE = """PHASE_GATE := {
  x==1/y;
  z==1/w;
  xy≠yx;
  Δe=0;
  Ψ=0;
  Θ15=true;
  Ω=true
}
PHASE_GATE
"""


class OfflineModelService:
    def __init__(self) -> None:
        self.config = LiteRTLMConfig(
            max_threads=8,
            max_messages_per_thread=16,
        )
        self.threads = ConversationThreadStore(self.config)

    def create_thread(self, **kwargs):
        return self.threads.create(**kwargs)

    def status(self):
        return {
            "schema": "TEST_OFFLINE_MODEL_STATUS_V1",
            "ok": True,
            "provider_id": "provider:test.offline",
            "model_id": "test-offline-model",
        }

    async def health(self):
        return {
            "ok": False,
            "online": False,
            "status": "TEST_MODEL_OFFLINE",
            "error": "intentional offline provider",
        }

    async def send_message(self, *args, **kwargs):
        raise AssertionError("offline model service must not be invoked")


def test_production_assistant_is_query_specific_and_never_uses_demo_template(monkeypatch):
    async def fake_tool(tool_name, arguments):
        response = {
            "status": "IMPLEMENTED_EXECUTION_VERIFIED",
            "classification": "HHS_PASS_152_UNIVERSAL_ELASTIC_CLOSURE_INVARIANT_VERIFIED",
            "tool_name": tool_name,
        }
        return {
            "schema": "HHS_ASSISTANT_API_TOOL_RECEIPT_V1",
            "ok": True,
            "status": "ADMIT_READ_ONLY_HHS_ASSISTANT_API_TOOL_RESULT",
            "tool_name": tool_name,
            "arguments": dict(arguments),
            "response": response,
            "runtime_mutation_admitted": False,
            "tool_receipt_root_hash72": f"receipt:{tool_name}",
        }

    import hhs_backend.runtime.hhs_production_assistant_v1 as production

    monkeypatch.setattr(production, "execute_hhs_assistant_api_tool", fake_tool)
    service = ProductionAssistantService(model_service=OfflineModelService())
    thread = service.create_thread(project_id="project:test:production")

    capabilities = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="What can the production assistant do?",
        )
    )
    pass_status = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="What is the current Pass 152 status?",
        )
    )

    first = capabilities["assistant_message"]["content"]
    second = pass_status["assistant_message"]["content"]
    assert first != second
    assert CANNED_DEMO_RESPONSE not in first
    assert CANNED_DEMO_RESPONSE not in second
    assert "hhs_pass152_status" in second
    assert pass_status["hhs_api_tool_call_count"] >= 1
    assert pass_status["runtime_mutation_admitted"] is False
    assert pass_status["turn_root_hash72"]


def test_production_assistant_health_remains_online_without_model():
    service = ProductionAssistantService(model_service=OfflineModelService())
    health = asyncio.run(service.health())
    assert health["online"] is True
    assert health["model_online"] is False
    assert health["effective_mode"] == "DETERMINISTIC_HHS_CAPABILITY_ASSISTANT"
    assert health["same_template_response_enabled"] is False


def test_public_product_routes_are_callable(monkeypatch):
    monkeypatch.setenv("HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS", "0.1")
    monkeypatch.setenv("HHS_LITERT_LM_BACKEND", "auto")

    from hhs_backend.heroku_server import app

    client = TestClient(app)

    health = client.get("/healthz")
    assert health.status_code == 200
    assert health.json()["assistant_online"] is True

    capabilities = client.get("/api/product/capabilities")
    assert capabilities.status_code == 200
    payload = capabilities.json()
    assert payload["production"] is True
    assert payload["demo_mode"] is False
    assert all(item["callable"] for item in payload["capabilities"])

    chat = client.post(
        "/api/assistant/chat",
        json={
            "project_id": "project:test:public",
            "title": "Production public test",
            "content": "What can the production assistant do?",
        },
    )
    assert chat.status_code == 200
    turn = chat.json()
    assert turn["assistant_message"]["content"]
    assert CANNED_DEMO_RESPONSE not in turn["assistant_message"]["content"]

    analysis = client.post(
        "/api/workspace/harmonicode/analyze",
        json={"source": HARMONICODE_SOURCE},
    )
    assert analysis.status_code == 200
    result = analysis.json()
    assert result["ok"] is True
    assert result["result"]["document"]["ast"]
    assert result["result"]["typed_ir"]["schema"] == "HHS_TYPED_IR_V1"
    assert result["program_effects_executed"] is False
    assert result["runtime_mutation_admitted"] is False


def test_public_html_contains_boot_watchdog_and_no_disappearing_overlay():
    from pathlib import Path

    source = Path("hhs_gui/index.html").read_text(encoding="utf-8")
    assert "frontend_boot_timeout" in source
    assert "dataset.hhsMounted" in source
    assert "setTimeout(() =>" in source
    assert "overlay.remove()" not in source
