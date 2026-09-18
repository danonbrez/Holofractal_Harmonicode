from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.api import litert_lm_assistant_routes as routes
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    MAX_CUSTOM_SYSTEM_INSTRUCTION_CHARS,
    LiteRTLMConfig,
)
from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import (
    HHSAPIAssistantService,
)


class CaptureTransport:
    provider_id = "provider:test.capture"
    requested_operation = "litert_lm.chat_completion"

    def __init__(self) -> None:
        self.messages = []

    async def list_models(self):
        return {"object": "list", "data": [{"id": "gemma4-12b"}]}

    async def chat_completion(self, **kwargs):
        self.messages = [dict(item) for item in kwargs["messages"]]
        return {
            "id": "chatcmpl-i007",
            "model": "gemma4-12b",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "I can explain that conversationally without exposing raw JSON.",
                },
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 12, "completion_tokens": 9, "total_tokens": 21},
        }


def _service(transport: CaptureTransport) -> HHSAPIAssistantService:
    return HHSAPIAssistantService(
        config=LiteRTLMConfig(
            model_id="gemma4-12b",
            system_instruction="BASE GOVERNED HHS SYSTEM INSTRUCTION",
        ),
        transport=transport,
    )


def test_custom_system_instruction_is_additive_and_receipted_by_hash_only():
    transport = CaptureTransport()
    service = _service(transport)
    thread = service.create_thread(project_id="project:i007")

    turn = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="Explain the vector state.",
            custom_system_instruction=(
                "Use plain English, short paragraphs, and never show raw JSON unless I ask."
            ),
        )
    )

    assert transport.messages[0]["role"] == "system"
    system = transport.messages[0]["content"]
    assert system.startswith("BASE GOVERNED HHS SYSTEM INSTRUCTION")
    assert "User-configured system instructions follow" in system
    assert "Use plain English, short paragraphs" in system
    assert system.index("BASE GOVERNED HHS SYSTEM INSTRUCTION") < system.index(
        "Use plain English"
    )

    assert turn["custom_system_instruction_applied"] is True
    assert turn["custom_system_instruction_root_hash72"]
    assert turn["runtime_mutation_admitted"] is False

    serialized = json.dumps(turn, sort_keys=True)
    assert "Use plain English, short paragraphs" not in serialized


def test_empty_custom_instruction_is_not_applied():
    transport = CaptureTransport()
    service = _service(transport)
    thread = service.create_thread(project_id="project:i007-empty")

    turn = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="Hello",
            custom_system_instruction="   ",
        )
    )

    assert turn["custom_system_instruction_applied"] is False
    assert turn["custom_system_instruction_root_hash72"] is None
    assert transport.messages[0]["content"] == "BASE GOVERNED HHS SYSTEM INSTRUCTION"


def test_custom_system_instruction_limit_is_fail_closed():
    transport = CaptureTransport()
    service = _service(transport)
    thread = service.create_thread(project_id="project:i007-limit")

    with pytest.raises(ValueError, match="exceeds"):
        asyncio.run(
            service.send_message(
                thread["thread_id"],
                content="Hello",
                custom_system_instruction="x" * (MAX_CUSTOM_SYSTEM_INSTRUCTION_CHARS + 1),
            )
        )


def test_assistant_chat_route_accepts_custom_system_instruction_and_rejects_oversize():
    transport = CaptureTransport()
    service = _service(transport)
    previous = routes._SERVICE
    routes._SERVICE = service
    try:
        app = FastAPI()
        app.include_router(routes.router)
        client = TestClient(app)

        response = client.post(
            "/api/assistant/chat",
            json={
                "project_id": "project:i007-route",
                "title": "I007",
                "content": "Answer naturally.",
                "custom_system_instruction": "Use conversational prose and concise paragraphs.",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["custom_system_instruction_applied"] is True
        assert body["custom_system_instruction_root_hash72"]
        assert "Use conversational prose" in transport.messages[0]["content"]

        oversized = client.post(
            "/api/assistant/chat",
            json={
                "project_id": "project:i007-route",
                "title": "I007",
                "content": "Answer naturally.",
                "custom_system_instruction": "x" * (MAX_CUSTOM_SYSTEM_INSTRUCTION_CHARS + 1),
            },
        )
        assert oversized.status_code == 422
    finally:
        routes._SERVICE = previous
