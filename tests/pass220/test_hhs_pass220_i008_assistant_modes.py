from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.api import litert_lm_assistant_routes as routes
from hhs_backend.runtime.hhs_assistant_api_tool_gateway_v1 import (
    DEFAULT_HHS_ASSISTANT_TOOLS,
)
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    ASSISTANT_MODE_AGENTIC_APPLICATION_DEVELOPMENT,
    ASSISTANT_MODE_BOTH,
    ASSISTANT_MODE_GENERAL_CHAT,
    HHSAssistantService,
    LiteRTLMConfig,
)
from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import (
    HHSAPIAssistantService,
)
from hhs_backend.runtime.hhs_native_litert_lm_provider_v1 import (
    HHSNativeLiteRTLMTransport,
)


class CaptureTransport:
    provider_id = "provider:hhs.litert_lm.gemma4"
    requested_operation = "litert_lm.chat_completion"
    backend = "cpu"
    request_model_id = "gemma4-12b,cpu,test"

    def __init__(self) -> None:
        self.calls = []

    async def list_models(self):
        return {"object": "list", "data": [{"id": "gemma4-12b"}]}

    async def chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "id": "chatcmpl-i008",
            "model": "gemma4-12b",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Conversational answer.",
                },
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6},
        }


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


def _api_service(transport: CaptureTransport) -> HHSAPIAssistantService:
    return HHSAPIAssistantService(
        config=LiteRTLMConfig(
            model_id="gemma4-12b",
            system_instruction="BASE HHS AUTHORITY",
        ),
        transport=transport,
    )


def test_general_chat_mode_disables_default_hhs_tools_and_marks_system_prompt():
    transport = CaptureTransport()
    service = _api_service(transport)
    thread = service.create_thread(project_id="project:i008-general")

    result = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="Tell me something interesting about language.",
            assistant_mode=ASSISTANT_MODE_GENERAL_CHAT,
        )
    )

    assert result["assistant_mode"] == ASSISTANT_MODE_GENERAL_CHAT
    assert result["hhs_api_tools_enabled"] is False
    assert result["hhs_api_tool_call_count"] == 0
    assert transport.calls[-1]["tools"] == []
    assert "HHS_ASSISTANT_MODE=GENERAL_CHAT" in transport.calls[-1]["messages"][0]["content"]


def test_agentic_application_development_mode_exposes_governed_tools():
    transport = CaptureTransport()
    service = _api_service(transport)
    thread = service.create_thread(project_id="project:i008-agentic")

    result = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="Inspect the runtime and help me implement the application.",
            assistant_mode=ASSISTANT_MODE_AGENTIC_APPLICATION_DEVELOPMENT,
        )
    )

    names = {
        tool["function"]["name"]
        for tool in transport.calls[-1]["tools"]
    }
    assert "hhs_repository_search" in names
    assert "hhs_runtime_state" in names
    assert result["assistant_mode"] == ASSISTANT_MODE_AGENTIC_APPLICATION_DEVELOPMENT
    assert result["hhs_api_tools_enabled"] is True
    assert "HHS_ASSISTANT_MODE=AGENTIC_APPLICATION_DEVELOPMENT" in transport.calls[-1]["messages"][0]["content"]


def test_both_mode_keeps_general_chat_instruction_and_tool_capability():
    transport = CaptureTransport()
    service = _api_service(transport)
    thread = service.create_thread(project_id="project:i008-both")

    result = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="Hello there.",
            assistant_mode=ASSISTANT_MODE_BOTH,
        )
    )

    assert result["assistant_mode"] == ASSISTANT_MODE_BOTH
    assert result["hhs_api_tools_enabled"] is True
    assert transport.calls[-1]["tools"]
    assert "HHS_ASSISTANT_MODE=BOTH" in transport.calls[-1]["messages"][0]["content"]
    assert "Do not force developer tooling into unrelated general conversation" in transport.calls[-1]["messages"][0]["content"]


def test_invalid_mode_fails_closed_before_provider_invocation():
    transport = CaptureTransport()
    service = _api_service(transport)
    thread = service.create_thread(project_id="project:i008-invalid")

    with pytest.raises(ValueError, match="assistant mode"):
        asyncio.run(
            service.send_message(
                thread["thread_id"],
                content="hello",
                assistant_mode="UNBOUNDED_AUTO_AGENT",
            )
        )
    assert transport.calls == []


def test_native_provider_does_not_force_repository_search_for_general_or_mixed_chat():
    native = HHSNativeLiteRTLMTransport(
        word2vec_service=FakeWord2Vec(),
        require_word2vec=False,
    )

    general = native._select_tool_calls(
        "Tell me about friendship.",
        DEFAULT_HHS_ASSISTANT_TOOLS,
        assistant_mode=ASSISTANT_MODE_GENERAL_CHAT,
    )
    mixed_general = native._select_tool_calls(
        "Tell me about friendship.",
        DEFAULT_HHS_ASSISTANT_TOOLS,
        assistant_mode=ASSISTANT_MODE_BOTH,
    )
    mixed_dev = native._select_tool_calls(
        "Inspect the repository and fix the build test.",
        DEFAULT_HHS_ASSISTANT_TOOLS,
        assistant_mode=ASSISTANT_MODE_BOTH,
    )

    assert general == []
    assert mixed_general == []
    assert any(
        call["function"]["name"] == "hhs_repository_search"
        for call in mixed_dev
    )


def test_native_general_chat_runs_prompt_response_without_agentic_tools():
    native = HHSNativeLiteRTLMTransport(
        word2vec_service=FakeWord2Vec(),
        require_word2vec=False,
    )
    response = asyncio.run(
        native.chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "HHS_ASSISTANT_MODE=GENERAL_CHAT.",
                },
                {"role": "user", "content": "Hello"},
            ],
            tools=[],
        )
    )
    choice = response["choices"][0]
    assert choice["finish_reason"] == "stop"
    assert choice["message"]["content"] == "Hello. What would you like to talk about?"
    assert response["hhs_native_trace"]["assistant_mode"] == ASSISTANT_MODE_GENERAL_CHAT
    assert response["hhs_native_trace"]["general_chat_prompt_response_cycle"] is True


def test_agentic_only_native_mode_redirects_unrelated_chat_without_tool_search():
    native = HHSNativeLiteRTLMTransport(
        word2vec_service=FakeWord2Vec(),
        require_word2vec=False,
    )
    response = asyncio.run(
        native.chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "HHS_ASSISTANT_MODE=AGENTIC_APPLICATION_DEVELOPMENT.",
                },
                {"role": "user", "content": "How was your day?"},
            ],
            tools=DEFAULT_HHS_ASSISTANT_TOOLS,
        )
    )
    choice = response["choices"][0]
    assert choice["finish_reason"] == "stop"
    assert "does not appear to be an application-development task" in choice["message"]["content"]


def test_rest_chat_route_accepts_all_three_modes_and_rejects_unknown_mode():
    transport = CaptureTransport()
    service = _api_service(transport)
    previous = routes._SERVICE
    routes._SERVICE = service
    try:
        app = FastAPI()
        app.include_router(routes.router)
        client = TestClient(app)

        for mode in (
            ASSISTANT_MODE_GENERAL_CHAT,
            ASSISTANT_MODE_AGENTIC_APPLICATION_DEVELOPMENT,
            ASSISTANT_MODE_BOTH,
        ):
            response = client.post(
                "/api/assistant/chat",
                json={
                    "project_id": f"project:i008-{mode.lower()}",
                    "title": "I008",
                    "content": "Hello",
                    "assistant_mode": mode,
                },
            )
            assert response.status_code == 200
            assert response.json()["assistant_mode"] == mode

        invalid = client.post(
            "/api/assistant/chat",
            json={
                "project_id": "project:i008-invalid",
                "title": "I008",
                "content": "Hello",
                "assistant_mode": "EVERYTHING_WITHOUT_GATES",
            },
        )
        assert invalid.status_code == 422
    finally:
        routes._SERVICE = previous
