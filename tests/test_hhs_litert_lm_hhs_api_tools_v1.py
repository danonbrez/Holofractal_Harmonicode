from __future__ import annotations

import asyncio
import json

from hhs_backend.runtime.hhs_assistant_api_tool_gateway_v1 import (
    assistant_api_tool_registry,
    execute_hhs_assistant_api_tool,
)
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import LiteRTLMConfig
from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import (
    HHSAPIAssistantService,
)


class ToolCallingFakeTransport:
    def __init__(self):
        self.calls = 0
        self.tool_receipt = None

    async def list_models(self):
        return {"object": "list", "data": [{"id": "gemma4-12b"}]}

    async def chat_completion(self, **kwargs):
        self.calls += 1
        messages = list(kwargs["messages"])
        tools = list(kwargs.get("tools") or [])
        assert any(
            tool.get("function", {}).get("name") == "hhs_pass152_status"
            for tool in tools
        )

        if self.calls == 1:
            return {
                "id": "chatcmpl-tool-request",
                "model": "gemma4-12b",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [{
                            "id": "call-pass152-status",
                            "type": "function",
                            "function": {
                                "name": "hhs_pass152_status",
                                "arguments": "{}",
                            },
                        }],
                    },
                    "finish_reason": "tool_calls",
                }],
                "usage": {"prompt_tokens": 10, "completion_tokens": 4, "total_tokens": 14},
            }

        tool_messages = [message for message in messages if message.get("role") == "tool"]
        assert len(tool_messages) == 1
        self.tool_receipt = json.loads(tool_messages[0]["content"])
        assert self.tool_receipt["ok"] is True
        assert self.tool_receipt["tool_name"] == "hhs_pass152_status"
        assert self.tool_receipt["runtime_mutation_admitted"] is False
        assert self.tool_receipt["response"]["pass"] == 152

        return {
            "id": "chatcmpl-tool-final",
            "model": "gemma4-12b",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Pass 152 is implemented and execution-verified in the current HHS status projection.",
                },
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 42, "completion_tokens": 12, "total_tokens": 54},
        }


def test_default_hhs_api_tools_execute_inside_gemma4_turn():
    transport = ToolCallingFakeTransport()
    service = HHSAPIAssistantService(
        config=LiteRTLMConfig(model_id="gemma4-12b"),
        transport=transport,
    )
    thread = service.create_thread(project_id="project:api-tools")
    turn = asyncio.run(
        service.send_message(
            thread["thread_id"],
            content="What is the current Pass 152 status?",
        )
    )

    assert transport.calls == 2
    assert turn["ok"] is True
    assert turn["assistant_message"]["content"].startswith("Pass 152")
    assert turn["hhs_api_tools_enabled"] is True
    assert turn["hhs_api_tool_call_count"] == 1
    assert turn["hhs_api_tool_trace"][0]["receipt"]["ok"] is True
    assert turn["hhs_api_tool_trace"][0]["receipt"]["tool_receipt_root_hash72"]
    assert turn["mutating_model_tool_execution_allowed"] is False
    assert turn["runtime_mutation_admitted"] is False


def test_unregistered_mutating_tool_is_closed_rejection():
    rejected = asyncio.run(
        execute_hhs_assistant_api_tool("hhs_runtime_halt", {})
    )
    assert rejected["ok"] is False
    assert rejected["status"] == "REJECT_HHS_ASSISTANT_API_TOOL_CALL"
    assert rejected["runtime_mutation_admitted"] is False
    assert rejected["tool_receipt_root_hash72"]


def test_tool_registry_is_read_only_and_hash72_witnessed():
    registry = assistant_api_tool_registry()
    names = set(registry["tool_names"])
    assert "hhs_runtime_state" in names
    assert "hhs_pass152_status" in names
    assert "hhs_runtime_halt" not in names
    assert registry["read_only"] is True
    assert registry["mutating_tool_execution_allowed"] is False
    assert registry["tool_registry_root_hash72"]
