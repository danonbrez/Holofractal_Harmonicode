from __future__ import annotations

import asyncio

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


class EmptyRegistryTransport:
    provider_id = "provider:test.empty"
    requested_operation = "litert_lm.chat_completion"

    async def list_models(self):
        return {"object": "list", "data": []}

    async def chat_completion(self, **_kwargs):
        raise AssertionError("empty registry transport must not be invoked")


class SemanticFallbackTransport:
    provider_id = "provider:test.native-semantic"
    requested_operation = "litert_lm.chat_completion"

    def __init__(self, model_id: str = "native-semantic") -> None:
        self.model_id = model_id
        self.calls = 0

    async def list_models(self):
        return {"object": "list", "data": [{"id": self.model_id}]}

    async def chat_completion(self, **_kwargs):
        self.calls += 1
        return {
            "id": "chatcmpl-semantic-fallback",
            "model": self.model_id,
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": (
                        "I can continue this as a general natural-language conversation."
                    ),
                },
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": 2,
                "completion_tokens": 8,
                "total_tokens": 10,
            },
            "hhs_native_trace": {
                "generation_path": "EXACT_SEMANTIC_FALLBACK",
                "general_chat_prompt_response_cycle": True,
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
    semantic = next(
        item for item in fabric["members"]
        if item["member_id"] == "native-semantic:hhs-native-language-v1"
    )
    assert semantic["role"] == "EXACT_SEMANTIC_CONTEXT"
    assert semantic["callable_from_unified_chat"] is False
    assert semantic["terminal_generation_eligible"] is False
    assert "TEXT_GENERATION" not in semantic["capabilities"]
    assert "SEMANTIC_CONTEXT" in semantic["capabilities"]
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


def test_semantic_fallback_is_nonterminal_and_does_not_duplicate_thread(monkeypatch):
    monkeypatch.setenv("HHS_LITERT_LM_PROVIDER_MODE", "auto")
    base_config = LiteRTLMConfig(
        model_id="unregistered-external",
        system_instruction="BASE HHS AUTHORITY",
    )
    base = HHSAPIAssistantService(
        config=base_config,
        transport=EmptyRegistryTransport(),
    )
    native_transport = SemanticFallbackTransport()
    native = HHSAPIAssistantService(
        config=LiteRTLMConfig(
            model_id=native_transport.model_id,
            system_instruction="NATIVE HHS AUTHORITY",
        ),
        transport=native_transport,
        thread_store=base.threads,
    )
    final_transport = MultiModelTransport(
        "pass153-final",
        ("pass153-final",),
    )
    pass153 = HHSAPIAssistantService(
        config=LiteRTLMConfig(
            model_id="pass153-final",
            system_instruction="PASS153 HHS AUTHORITY",
        ),
        transport=final_transport,
        thread_store=base.threads,
    )
    service = ProductionAssistantService(
        model_service=base,
        native_service=native,
        pass153_service=pass153,
    )
    thread = service.create_thread(project_id="project:nonterminal-fallback")
    result = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="Give me a substantive answer.",
            assistant_mode=ASSISTANT_MODE_BOTH,
        )
    )

    assert result["ok"] is True
    assert result["selected_model_id"] == "pass153-final"
    assert result["assistant_message"]["content"] == "answer:pass153-final"
    assert native_transport.calls == 1
    assert final_transport.calls == 1
    failed = result["failed_provider_results"]
    assert len(failed) == 1
    assert failed[0]["provider_metadata"]["generation_path"] == "EXACT_SEMANTIC_FALLBACK"
    assert (
        ProductionAssistantService._completion_state(failed[0])
        == "NONTERMINAL_SEMANTIC_FALLBACK"
    )

    stored = service.threads.get(thread["thread_id"])
    assert [item["role"] for item in stored["messages"]] == ["user", "assistant"]
    assert stored["messages"][-1]["content"] == "answer:pass153-final"
    assert all(
        "general natural-language conversation" not in item["content"]
        for item in stored["messages"]
    )


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
