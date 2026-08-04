from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

import hhs_backend.runtime.hhs_kimi_k3_agentic_assistant_v1 as kimi_module
from hhs_backend.runtime.hhs_kimi_k3_agentic_assistant_v1 import (
    KimiConversationThreadStore,
    KimiK3AgenticAssistantService,
    KimiK3AssistantConfig,
)
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import LiteRTLMConfig
from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import (
    HHSAPIAssistantService,
)
from hhs_backend.runtime.hhs_pass210_native_agi_optimizer_v1 import (
    NativeAGIOptimizer,
)
from hhs_backend.runtime.hhs_pass210_production_assistant_v1 import (
    Pass210ProductionAssistantService,
)


class _KimiToolTransport:
    provider_id = "provider:hhs.moonshot.kimi_k3.agentic"
    requested_operation = "moonshot.kimi_k3.agentic_swarm_chat_completion"
    model_id = "kimi-k3"
    request_model_id = "kimi-k3"
    backend = "remote_api"

    def __init__(self) -> None:
        self.calls = 0
        self.messages: list[list[dict[str, Any]]] = []

    async def list_models(self) -> Dict[str, Any]:
        return {"object": "list", "data": [{"id": "kimi-k3"}]}

    async def chat_completion(self, **kwargs: Any) -> Dict[str, Any]:
        self.calls += 1
        self.messages.append([dict(item) for item in kwargs["messages"]])
        if self.calls == 1:
            return {
                "id": "chatcmpl-kimi-tools",
                "model": "kimi-k3",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "reasoning_content": "Inspect both independent runtime surfaces.",
                        "tool_calls": [
                            {
                                "id": "call-a",
                                "type": "function",
                                "function": {
                                    "name": "hhs_runtime_state",
                                    "arguments": "{}",
                                },
                            },
                            {
                                "id": "call-b",
                                "type": "function",
                                "function": {
                                    "name": "hhs_kernel_invariants",
                                    "arguments": "{}",
                                },
                            },
                        ],
                    },
                    "finish_reason": "tool_calls",
                }],
            }
        return {
            "id": "chatcmpl-kimi-final",
            "model": "kimi-k3",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Both governed HHS surfaces returned witnessed evidence.",
                    "reasoning_content": "The tool receipts are sufficient for the response.",
                },
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
        }


class _FailingKimiTransport(_KimiToolTransport):
    async def chat_completion(self, **_: Any) -> Dict[str, Any]:
        raise RuntimeError("simulated Kimi outage")


class _GemmaTransport:
    provider_id = "provider:hhs.litert_lm.gemma4"
    requested_operation = "litert_lm.chat_completion"
    model_id = "gemma-4-E2B-it"
    request_model_id = "gemma-4-E2B-it,cpu"
    backend = "cpu"

    async def list_models(self) -> Dict[str, Any]:
        return {"object": "list", "data": [{"id": "gemma-4-E2B-it"}]}

    async def chat_completion(self, **_: Any) -> Dict[str, Any]:
        return {
            "id": "chatcmpl-gemma-fallback",
            "model": "gemma-4-E2B-it",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Gemma 4 continued the witnessed user turn locally.",
                },
                "finish_reason": "stop",
            }],
        }


class _NativeOptimizerTransport:
    provider_id = "provider:hhs.local.text"
    model_id = "hhs-native-language-v1"

    def installation_status(self) -> Dict[str, Any]:
        return {"ready": True, "offline_ready": True}

    async def chat_completion(self, **_: Any) -> Dict[str, Any]:
        return {
            "id": "chatcmpl-native-optimizer",
            "model": self.model_id,
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Reuse the witnessed tool trace as a deterministic retrieval hint.",
                },
                "finish_reason": "stop",
            }],
        }


class _RecordingOptimizer:
    def __init__(self) -> None:
        self.turns: list[dict[str, Any]] = []

    def enqueue_turn(
        self,
        turn: Mapping[str, Any],
        *,
        selected_provider_id: Optional[str],
        effective_mode: str,
        fallback_used: bool,
    ) -> Dict[str, Any]:
        record = {
            "turn": dict(turn),
            "selected_provider_id": selected_provider_id,
            "effective_mode": effective_mode,
            "fallback_used": fallback_used,
        }
        self.turns.append(record)
        return {
            "ok": True,
            "observation_root_hash72": "o" * 72,
            "native_agi_is_user_facing_provider": False,
        }

    def status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "ready": True,
            "role": "BACKEND_LEARNING_AND_OPTIMIZATION_AGENT",
            "native_agi_is_user_facing_provider": False,
        }


async def _tool_receipt(name: str, arguments: Mapping[str, Any]) -> Dict[str, Any]:
    if name == "hhs_runtime_state":
        await asyncio.sleep(0.02)
    return {
        "schema": "HHS_ASSISTANT_API_TOOL_RECEIPT_V1",
        "ok": True,
        "tool_name": name,
        "arguments": dict(arguments),
        "response": {"witness": name},
        "runtime_mutation_admitted": False,
    }


def _kimi_config() -> KimiK3AssistantConfig:
    return KimiK3AssistantConfig(
        enabled=True,
        api_key="test-key",
        max_threads=8,
        max_messages_per_thread=64,
        max_tool_rounds=4,
        max_tool_calls_per_round=8,
        max_parallel_tools=2,
    )


def test_kimi_agentic_swarm_preserves_reasoning_and_deterministic_tool_order(monkeypatch) -> None:
    monkeypatch.setattr(kimi_module, "execute_hhs_assistant_api_tool", _tool_receipt)
    config = _kimi_config()
    inner = _KimiToolTransport()
    service = KimiK3AgenticAssistantService(config=config, transport=inner)
    thread = service.create_thread(project_id="project:pass210")
    result = asyncio.run(
        service.send_message(thread["thread_id"], content="Inspect runtime and invariants")
    )

    assert result["ok"] is True
    assert result["hhs_api_tool_call_count"] == 2
    assert [item["tool_call_id"] for item in result["hhs_api_tool_trace"]] == [
        "call-a",
        "call-b",
    ]
    assert result["reasoning_content_preserved"] is True
    stored = service.threads.get(thread["thread_id"])
    assert stored is not None
    roles = [message["role"] for message in stored["messages"]]
    assert roles == ["user", "assistant", "tool", "tool", "assistant"]
    assert stored["messages"][1]["reasoning_content"].startswith("Inspect both")
    assert stored["messages"][-1]["reasoning_content"].startswith("The tool receipts")
    assert inner.messages[1][-3]["reasoning_content"].startswith("Inspect both")
    assert [message["tool_call_id"] for message in inner.messages[1][-2:]] == [
        "call-a",
        "call-b",
    ]


def test_kimi_failure_continues_same_witnessed_turn_through_gemma() -> None:
    kimi_config = _kimi_config()
    shared = KimiConversationThreadStore(
        kimi_config,
        provider_id="provider:hhs.pass210.shared_thread",
    )
    primary = KimiK3AgenticAssistantService(
        config=kimi_config,
        transport=_FailingKimiTransport(),
        thread_store=shared,
    )
    fallback = HHSAPIAssistantService(
        config=LiteRTLMConfig(
            base_url="http://127.0.0.1:9379/v1",
            model_id="gemma-4-E2B-it",
            max_threads=8,
            max_messages_per_thread=64,
        ),
        transport=_GemmaTransport(),
        thread_store=shared,
    )
    optimizer = _RecordingOptimizer()
    service = Pass210ProductionAssistantService(
        primary_service=primary,
        fallback_service=fallback,
        optimizer=optimizer,
    )
    thread = service.create_thread(project_id="project:pass210-fallback")
    result = asyncio.run(
        service.send_message(thread["thread_id"], content="Continue safely")
    )

    assert result["ok"] is True
    assert result["effective_mode"] == "GEMMA4_LITERT_LM_FALLBACK"
    assert result["fallback_used"] is True
    assert result["selected_provider_id"] == fallback.provider_id
    assert result["native_agi_is_user_facing_provider"] is False
    assert result["native_agi_observation_root_hash72"] == "o" * 72
    assert len(optimizer.turns) == 1
    stored = service.threads.get(thread["thread_id"])
    assert stored is not None
    assert [message["role"] for message in stored["messages"]] == ["user", "assistant"]
    assert stored["messages"][0]["content"] == "Continue safely"


def test_native_agi_optimizer_persists_noncanonical_proposal(tmp_path: Path) -> None:
    optimizer = NativeAGIOptimizer(
        db_path=tmp_path / "optimizer.sqlite3",
        transport=_NativeOptimizerTransport(),
    )
    turn = {
        "ok": True,
        "status": "ADMIT_KIMI_K3_AGENTIC_ASSISTANT_TURN",
        "thread_id": "thread:test",
        "turn_root_hash72": "t" * 72,
        "user_message": {"content": "Inspect the runtime"},
        "assistant_message": {
            "content": "The runtime is ready.",
            "reasoning_content": "private provider reasoning",
        },
        "hhs_api_tool_trace": [{"tool_name": "hhs_runtime_state", "ok": True}],
        "runtime_mutation_admitted": False,
    }
    queued = optimizer.enqueue_turn(
        turn,
        selected_provider_id="provider:hhs.moonshot.kimi_k3.agentic",
        effective_mode="KIMI_K3_AGENTIC_SWARM_API",
        fallback_used=False,
    )
    batch = asyncio.run(optimizer.process_pending(limit=4))
    proposals = optimizer.proposals()
    observations = optimizer.observations()

    assert queued["ok"] is True
    assert batch["completed_count"] == 1
    assert len(proposals) == 1
    assert proposals[0]["canonical_authority"] is False
    assert proposals[0]["separate_admission_required"] is True
    assert proposals[0]["runtime_mutation_admitted"] is False
    assert observations[0]["assistant_reasoning_present"] is True
    assert observations[0]["assistant_reasoning_root_hash72"]
    assert "private provider reasoning" not in str(observations[0])


def test_status_declares_two_user_facing_providers_and_native_observer() -> None:
    kimi_config = _kimi_config()
    shared = KimiConversationThreadStore(kimi_config)
    primary = KimiK3AgenticAssistantService(
        config=kimi_config,
        transport=_KimiToolTransport(),
        thread_store=shared,
    )
    fallback = HHSAPIAssistantService(
        config=LiteRTLMConfig(model_id="gemma-4-E2B-it"),
        transport=_GemmaTransport(),
        thread_store=shared,
    )
    service = Pass210ProductionAssistantService(
        primary_service=primary,
        fallback_service=fallback,
        optimizer=_RecordingOptimizer(),
    )
    health = asyncio.run(service.health())

    assert health["ok"] is True
    assert health["effective_mode"] == "KIMI_K3_AGENTIC_SWARM_API"
    assert len(health["provider_hierarchy"]) == 2
    assert health["native_agi_is_user_facing_provider"] is False
    assert health["native_agi_is_backend_learning_agent"] is True
