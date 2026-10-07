from __future__ import annotations

import asyncio

import pytest

from hhs_backend.runtime.hhs_assistant_api_tool_gateway_v1 import (
    DEFAULT_HHS_ASSISTANT_TOOLS,
    assistant_api_tool_registry,
)
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    ASSISTANT_MODE_BOTH,
    ConversationThreadStore,
    LiteRTLMConfig,
)
from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import (
    HHSAPIAssistantService,
)
from hhs_backend.runtime.hhs_native_litert_lm_provider_v1 import (
    HHSNativeLiteRTLMTransport,
)
from hhs_backend.runtime.hhs_pass153_assistant_transport_v1 import (
    Pass153AssistantTransport,
)
from hhs_backend.runtime.hhs_production_assistant_v1 import (
    ProductionAssistantService,
)
from hhs_backend.runtime.hhs_unified_language_model_fabric_v1 import (
    build_unified_language_model_fabric,
    ordered_litert_model_ids,
)


class FakeWord2Vec:
    def status(self):
        return {
            "offline_ready": True,
            "active_model_id": "fake-word2vec",
            "installed_models": 1,
        }

    def nearest(self, token, top_k=4):
        return {
            "model_id": "fake-word2vec",
            "approximate": False,
            "results": [
                {"token": f"{token}-context-{index}"}
                for index in range(top_k)
            ],
        }


class MultiModelTransport:
    provider_id = "provider:hhs.litert_lm.gemma4"
    requested_operation = "litert_lm.chat_completion"
    backend = "cpu"

    def __init__(self, model_id: str, registry: tuple[str, ...]) -> None:
        self.model_id = model_id
        self.request_model_id = f"{model_id},cpu,test"
        self.registry = registry
        self.calls = 0

    async def list_models(self):
        return {
            "object": "list",
            "data": [{"id": model_id} for model_id in self.registry],
        }

    async def chat_completion(self, **_kwargs):
        self.calls += 1
        content = f"answer:{self.model_id}"
        return {
            "id": f"chatcmpl-{self.model_id}",
            "model": self.model_id,
            "choices": [{
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": 2,
                "completion_tokens": 1,
                "total_tokens": 3,
            },
        }


class OfflineService:
    provider_id = "provider:test.offline"

    def __init__(self, threads):
        self.threads = threads
        self.config = LiteRTLMConfig(model_id="offline")

    def status(self):
        return {
            "provider_id": self.provider_id,
            "model_id": "offline",
        }

    async def health(self):
        return {
            "ok": False,
            "online": False,
            "provider_id": self.provider_id,
            "status": "OFFLINE",
        }


def test_declared_model_priority_orders_all_registered_litert_models(monkeypatch):
    monkeypatch.setenv(
        "HHS_ASSISTANT_MODEL_PRIORITY",
        "model-large,model-medium,model-small",
    )
    order = ordered_litert_model_ids(
        ["model-small", "model-large", "model-medium"],
        configured_model_id="model-small",
    )
    assert order == ["model-large", "model-medium", "model-small"]


def test_unified_fabric_includes_generators_fallbacks_and_memory(monkeypatch):
    monkeypatch.setenv("HHS_ASSISTANT_PRIMARY_MODEL", "model-large")
    fabric = build_unified_language_model_fabric(
        configured_model_id="model-small",
        registered_model_ids=["model-small", "model-large"],
        native_installation={
            "causal_lm": {
                "ready": True,
                "configured": True,
                "loaded": True,
                "model_id": "hydrated-native",
            }
        },
        native_health={"ok": True, "online": True},
        pass153_models=[{
            "model_id": "hhs-reference-open-model-v1",
            "backend": "reference-ngram",
            "source": "reference_model.json",
            "capabilities": ["text-generation"],
        }],
        pass166_status={
            "offline_ready": True,
            "active_model_id": "word2vec-active",
        },
    )
    assert fabric["unified_chat_surface"] is True
    assert fabric["primary_model_id"] == "model-large"
    assert fabric["litert_route_order"] == ["model-large", "model-small"]
    member_ids = {item["member_id"] for item in fabric["members"]}
    assert "native-causal:hydrated-native" in member_ids
    assert "pass153:hhs-reference-open-model-v1" in member_ids
    assert "pass166:word2vec-active" in member_ids
    assert fabric["vm81_admission_boundary_preserved"] is True


def test_production_chat_uses_declared_primary_registered_model_on_one_thread(monkeypatch):
    monkeypatch.setenv("HHS_ASSISTANT_MODEL_PRIORITY", "model-large,model-small")
    registry = ("model-small", "model-large")
    config = LiteRTLMConfig(
        model_id="model-small",
        system_instruction="BASE HHS AUTHORITY",
    )
    small_transport = MultiModelTransport("model-small", registry)
    base = HHSAPIAssistantService(config=config, transport=small_transport)
    offline_native = OfflineService(base.threads)
    offline_pass153 = OfflineService(base.threads)
    transports: dict[str, MultiModelTransport] = {}

    def factory(model_id, sibling_config, threads):
        transport = MultiModelTransport(model_id, registry)
        transports[model_id] = transport
        return HHSAPIAssistantService(
            config=sibling_config,
            transport=transport,
            thread_store=threads,
        )

    service = ProductionAssistantService(
        model_service=base,
        native_service=offline_native,
        pass153_service=offline_pass153,
        model_service_factory=factory,
    )
    thread = service.create_thread(project_id="project:unified-model-test")
    result = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="Explain the model fabric.",
            assistant_mode=ASSISTANT_MODE_BOTH,
        )
    )

    assert result["ok"] is True
    assert result["selected_model_id"] == "model-large"
    assert result["effective_mode"] == "UNIFIED_LITERT_MODEL_FABRIC"
    assert result["assistant_message"]["content"] == "answer:model-large"
    stored = service.threads.get(thread["thread_id"])
    assert [item["role"] for item in stored["messages"]] == ["user", "assistant"]
    assert transports["model-large"].calls == 1
    assert small_transport.calls == 0


def test_lane5_and_model_fabric_tools_are_in_one_governed_registry():
    registry = assistant_api_tool_registry()
    names = set(registry["tool_names"])
    assert {
        "hhs_language_model_fabric",
        "hhs_lane5_capability_status",
        "hhs_lane5_capability_search",
    }.issubset(names)
    assert registry["read_only"] is True
    assert registry["mutating_tool_execution_allowed"] is False


def test_native_both_mode_routes_lane5_queries_to_lane5_tools():
    native = HHSNativeLiteRTLMTransport(
        word2vec_service=FakeWord2Vec(),
        require_word2vec=False,
    )
    calls = native._select_tool_calls(
        "Search Lane 5 capabilities for the model registry.",
        DEFAULT_HHS_ASSISTANT_TOOLS,
        assistant_mode=ASSISTANT_MODE_BOTH,
    )
    names = {call["function"]["name"] for call in calls}
    assert "hhs_lane5_capability_status" in names
    assert "hhs_lane5_capability_search" in names


def test_pass153_transport_is_available_as_unified_chat_fallback():
    transport = Pass153AssistantTransport()
    models = asyncio.run(transport.list_models())
    assert models["data"]
    response = asyncio.run(
        transport.chat_completion(
            messages=[
                {"role": "system", "content": "Answer as an HHS assistant."},
                {"role": "user", "content": "hello"},
            ]
        )
    )
    assert response["choices"][0]["message"]["content"].strip()
    assert response["hhs_pass153"]["runtime_mutation_admitted"] is False


class CountingProvider:
    """A full-thread stub that tracks whether optional health is eagerly probed."""

    def __init__(self, *, ready: bool, reply: str) -> None:
        self.ready = ready
        self.reply = reply
        self.provider_id = "provider:hhs.native" if reply == "native" else "provider:hhs.pass153"
        self.config = LiteRTLMConfig(model_id="test-provider")
        self.threads = None
        self.health_calls = 0
        self.send_calls = 0

    def status(self):
        return {"provider_id": self.provider_id, "model_id": self.config.model_id}

    async def health(self):
        self.health_calls += 1
        return {"ok": self.ready, "online": self.ready, "provider_id": self.provider_id}

    async def send_message(self, thread_id, *, content, **_kwargs):
        self.send_calls += 1
        user = self.threads.append(thread_id, role="user", content=content)
        if not self.ready:
            return {
                "ok": False,
                "thread_id": thread_id,
                "user_message": user,
                "assistant_message": None,
            }
        answer = self.threads.append(thread_id, role="assistant", content=self.reply)
        return {
            "ok": True,
            "thread_id": thread_id,
            "user_message": user,
            "assistant_message": answer,
        }

    async def continue_message(self, thread_id, *, user_message, **_kwargs):
        self.send_calls += 1
        if not self.ready:
            return {
                "ok": False,
                "thread_id": thread_id,
                "user_message": user_message,
                "assistant_message": None,
            }
        answer = self.threads.append(thread_id, role="assistant", content=self.reply)
        return {
            "ok": True,
            "thread_id": thread_id,
            "user_message": user_message,
            "assistant_message": answer,
        }


def test_native_first_turn_does_not_probe_optional_pass153_health(monkeypatch):
    monkeypatch.setenv("HHS_LITERT_LM_PROVIDER_MODE", "native")
    native = CountingProvider(ready=True, reply="native")
    pass153 = CountingProvider(ready=True, reply="pass153")
    service = ProductionAssistantService(
        native_service=native,
        pass153_service=pass153,
    )
    assert service.native_first is True
    thread = service.create_thread(project_id="project:native-first-health")
    result = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="Remember this exact token for my next message: TEST-123-A.",
        )
    )
    assert result["ok"] is True
    assert result["assistant_message"]["content"] == "native"
    assert native.health_calls == 0
    assert native.send_calls == 1
    assert pass153.health_calls == 0
    assert pass153.send_calls == 0
    assert service.threads.get(thread["thread_id"])["message_count"] == 2


def test_native_first_fallback_probes_pass153_only_when_needed(monkeypatch):
    monkeypatch.setenv("HHS_LITERT_LM_PROVIDER_MODE", "native")
    native = CountingProvider(ready=False, reply="native")
    pass153 = CountingProvider(ready=True, reply="pass153")
    service = ProductionAssistantService(
        native_service=native,
        pass153_service=pass153,
    )
    thread = service.create_thread(project_id="project:native-fallback-health")
    result = asyncio.run(
        service.send_message(thread["thread_id"], content="Fallback probe")
    )
    assert result["ok"] is True
    assert result["assistant_message"]["content"] == "pass153"
    assert native.health_calls == 0
    assert native.send_calls == 1
    assert pass153.health_calls == 1
    assert pass153.send_calls == 1
    assert service.threads.get(thread["thread_id"])["message_count"] == 2


def test_native_startup_prewarm_executes_selected_health_before_chat(monkeypatch):
    monkeypatch.setenv("HHS_LITERT_LM_PROVIDER_MODE", "native")
    native = CountingProvider(ready=True, reply="native")
    pass153 = CountingProvider(ready=True, reply="pass153")
    service = ProductionAssistantService(
        native_service=native,
        pass153_service=pass153,
    )

    receipt = asyncio.run(service.prewarm_native_installation())

    assert receipt["schema"] == "HHS_PRODUCTION_ASSISTANT_PREWARM_V1"
    assert receipt["status"] == "NATIVE_INSTALLATION_PREWARM_READY"
    assert receipt["ready"] is True
    assert receipt["runtime_mutation_admitted"] is False
    assert receipt["prewarm_root_hash72"]
    assert native.health_calls == 1
    assert pass153.health_calls == 0

    thread = service.create_thread(project_id="project:native-prewarm")
    result = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="Remember this exact token for my next message: PREWARM-123-A.",
        )
    )
    assert result["ok"] is True
    assert native.health_calls == 1
    assert native.send_calls == 1
    assert pass153.health_calls == 0
    assert pass153.send_calls == 0


def test_native_startup_prewarm_fails_closed_when_native_health_is_not_ready(monkeypatch):
    monkeypatch.setenv("HHS_LITERT_LM_PROVIDER_MODE", "native")
    native = CountingProvider(ready=False, reply="native")
    pass153 = CountingProvider(ready=True, reply="pass153")
    service = ProductionAssistantService(
        native_service=native,
        pass153_service=pass153,
    )

    with pytest.raises(
        RuntimeError,
        match="HHS_PRODUCTION_NATIVE_ASSISTANT_PREWARM_FAILED",
    ):
        asyncio.run(service.prewarm_native_installation())

    assert native.health_calls == 1
    assert native.send_calls == 0
    assert pass153.health_calls == 0
    assert pass153.send_calls == 0
