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
from hhs_backend.runtime.hhs_pass219_lane5_chat_generator_selection_v1 import (
    select_lane5_chat_generator,
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
    semantic = next(
        item for item in fabric["members"]
        if item["member_id"] == "native-semantic:hhs-native-language-v1"
    )
    assert semantic["callable_from_unified_chat"] is False
    assert semantic["semantic_fallback_is_text_generation"] is False
    assert "TEXT_GENERATION" not in semantic["capabilities"]
    assert fabric["vm81_admission_boundary_preserved"] is True
    assert fabric["lane5_is_pass219_composition_authority"] is True
    assert fabric["local_provider_order_is_composition_authority"] is False
    assert fabric["all_members_visible_to_lane5"] is True
    assert all(item["visible_to_lane5"] is True for item in fabric["members"])
    assert all(item["candidate_only"] is True for item in fabric["members"])
    assert all(
        item["provider_output_canonical_authority"] is False
        for item in fabric["members"]
    )


def test_production_chat_uses_lane5_consensus_on_one_witnessed_thread(monkeypatch):
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
    assert result["selected_model_id"] in registry
    assert (
        result["selected_lane5_member_id"]
        == f"litert:{result['selected_model_id']}"
    )
    assert result["effective_mode"] == "UNIFIED_LITERT_MODEL_FABRIC"
    assert (
        result["assistant_message"]["content"]
        == f"answer:{result['selected_model_id']}"
    )
    assert result["composition_authority"] == "PASS219_LANE5"
    assert result["local_provider_hierarchy_authority"] is False
    selection = result["lane5_selection"]
    assert selection["ok"] is True
    assert selection["selection_uses_pass124_parallel_consensus"] is True
    assert selection["probability_created_authority"] is False
    assert (
        selection["replay"]["replay_status"]
        == "PARALLEL_DETERMINISTIC_GENERALIZATION_REPLAY_VALIDATED"
    )
    stored = service.threads.get(thread["thread_id"])
    assert [item["role"] for item in stored["messages"]] == ["user", "assistant"]

    calls = {"model-small": small_transport.calls}
    calls.update({model_id: transport.calls for model_id, transport in transports.items()})
    assert sum(calls.values()) == 1
    assert calls[result["selected_model_id"]] == 1


def test_lane5_selection_excludes_failed_generator_and_replays_exactly():
    fabric = build_unified_language_model_fabric(
        configured_model_id="model-a",
        registered_model_ids=["model-a", "model-b"],
        native_installation={},
        native_health={"ok": False, "online": False},
        pass153_models=[],
        pass166_status={},
    )
    first = select_lane5_chat_generator(
        fabric=fabric,
        thread_id="thread:selection",
        content="Choose an available generator.",
    )
    assert first["ok"] is True
    assert first["selected_member_id"] in {"litert:model-a", "litert:model-b"}
    assert (
        first["replay"]["replay_status"]
        == "PARALLEL_DETERMINISTIC_GENERALIZATION_REPLAY_VALIDATED"
    )

    second = select_lane5_chat_generator(
        fabric=fabric,
        thread_id="thread:selection",
        content="Choose an available generator.",
        failed_member_ids=[first["selected_member_id"]],
    )
    assert second["ok"] is True
    assert second["selected_member_id"] != first["selected_member_id"]
    assert second["candidate_count"] == 1
    assert first["selected_member_id"] in second["failed_member_ids"]
    assert second["probability_created_authority"] is False
    assert second["canonical_vm81_mutation_authority"] is False


def test_production_health_reports_lane5_candidate_pool_not_provider_hierarchy(monkeypatch):
    monkeypatch.setenv("HHS_ASSISTANT_MODEL_PRIORITY", "model-large,model-small")
    registry = ("model-small", "model-large")
    config = LiteRTLMConfig(model_id="model-small")
    base = HHSAPIAssistantService(
        config=config,
        transport=MultiModelTransport("model-small", registry),
    )
    service = ProductionAssistantService(
        model_service=base,
        native_service=OfflineService(base.threads),
        pass153_service=OfflineService(base.threads),
    )

    health = asyncio.run(service.health())
    assert health["ok"] is True
    assert health["composition_authority"] == "PASS219_LANE5"
    assert health["local_provider_hierarchy_authority"] is False
    assert health["provider_hierarchy_is_composition_authority"] is False
    assert health["selected_provider_id"] is None
    assert health["selected_model_id"] is None
    assert health["selected_lane5_member_id"] is None
    assert health["lane5_candidate_count"] == 2
    assert set(health["lane5_candidate_member_ids"]) == {
        "litert:model-small",
        "litert:model-large",
    }
    assert health["effective_mode"] == "PASS219_LANE5_COMPOSED_CHAT_GENERATOR"


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
