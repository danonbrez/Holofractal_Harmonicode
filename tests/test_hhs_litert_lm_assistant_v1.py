from __future__ import annotations

import asyncio

from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    HHSAssistantService,
    LiteRTLMConfig,
    PROVIDER_ID,
)


class FakeTransport:
    async def list_models(self):
        return {"object": "list", "data": [{"id": "gemma4-12b"}]}

    async def chat_completion(self, **kwargs):
        messages = kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        return {
            "id": "chatcmpl-test",
            "model": "gemma4-12b",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "VM81 status is available through the HHS runtime API.",
                },
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 9,
                "total_tokens": 21,
            },
        }


def make_service(max_messages: int = 8) -> HHSAssistantService:
    config = LiteRTLMConfig(
        model_id="gemma4-12b",
        max_threads=4,
        max_messages_per_thread=max_messages,
    )
    return HHSAssistantService(config=config, transport=FakeTransport())


def test_litert_lm_turn_is_receipted_and_non_mutating():
    service = make_service()
    thread = service.create_thread(project_id="project:test")
    turn = asyncio.run(
        service.send_message(thread["thread_id"], content="Show runtime status.")
    )

    assert turn["assistant_message"]["content"].startswith("VM81 status")
    assert turn["proposal"]["selected_provider_id"] == PROVIDER_ID
    assert turn["provider_invocation_receipt"][
        "provider_invocation_receipt_hash72"
    ]
    assert turn["provider_result_ingress"]["provider_result_ingress_root_hash72"]
    assert turn["runtime_mutation_admitted"] is False
    assert turn["model_output_is_canonical_without_runtime_admission"] is False
    assert turn["thread"]["message_count"] == 2


def test_thread_history_is_bounded_but_sequence_is_monotonic():
    service = make_service(max_messages=4)
    thread = service.create_thread()
    for index in range(3):
        asyncio.run(
            service.send_message(
                thread["thread_id"],
                content=f"message {index}",
            )
        )

    stored = service.threads.get(thread["thread_id"])
    assert stored is not None
    assert len(stored["messages"]) == 4
    assert stored["message_count"] == 6
    assert stored["messages"][-1]["sequence"] == 6
    assert stored["message_tip_hash72"] == stored["messages"][-1]["message_root_hash72"]


def test_health_reports_litert_models():
    service = make_service()
    health = asyncio.run(service.health())
    assert health["online"] is True
    assert health["models"]["data"][0]["id"] == "gemma4-12b"


def test_assistant_routes_are_mounted_in_canonical_backend_router():
    from hhs_backend.api.pass152_elastic_closure_routes import router

    route_keys = {
        (
            getattr(route, "path", None),
            tuple(sorted(getattr(route, "methods", []) or [])),
        )
        for route in router.routes
    }
    assert ("/api/assistant/status", ("GET",)) in route_keys
    assert ("/api/assistant/threads", ("GET",)) in route_keys
    assert ("/api/assistant/threads", ("POST",)) in route_keys
    assert ("/api/assistant/chat", ("POST",)) in route_keys
    assert ("/api/assistant/ws/{thread_id}", ()) in route_keys
