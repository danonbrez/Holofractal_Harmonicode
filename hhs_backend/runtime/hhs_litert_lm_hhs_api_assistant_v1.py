"""LiteRT-LM Gemma 4 assistant with a governed HHS API tool loop."""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Mapping, Optional

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_assistant_api_tool_gateway_v1 import (
    DEFAULT_HHS_ASSISTANT_TOOLS,
    execute_hhs_assistant_api_tool,
)
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    AUTHORITY,
    TURN_SCHEMA,
    HHSAssistantService,
    LiteRTLMConfig,
    LiteRTLMTransport,
)

VERSION = "HHS_LITERT_LM_GEMMA4_HHS_API_ASSISTANT_V1"
TOOL_LOOP_SCHEMA = "HHS_LITERT_LM_HHS_API_TOOL_LOOP_V1"
MAX_TOOL_ROUNDS = 4


def _merge_tools(
    default_tools: Iterable[Mapping[str, Any]],
    supplied_tools: Optional[List[Mapping[str, Any]]],
) -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for tool in [*default_tools, *(supplied_tools or [])]:
        item = dict(tool)
        function = dict(item.get("function") or {})
        name = str(function.get("name") or "")
        if name:
            merged[name] = item
    return [merged[name] for name in sorted(merged)]


def _parse_arguments(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, Mapping):
        return dict(raw)
    if raw is None or raw == "":
        return {}
    try:
        value = json.loads(str(raw))
    except json.JSONDecodeError:
        return {"_raw": str(raw)}
    return dict(value) if isinstance(value, Mapping) else {"value": value}


class GovernedHHSToolLoopTransport:
    """Wrap a LiteRT-LM transport and resolve allowlisted read-only HHS tools."""

    def __init__(self, inner: Any, max_tool_rounds: int = MAX_TOOL_ROUNDS):
        self.inner = inner
        self.max_tool_rounds = max(1, int(max_tool_rounds))
        self.last_tool_trace: List[Dict[str, Any]] = []

    async def list_models(self) -> Dict[str, Any]:
        return await self.inner.list_models()

    async def chat_completion(
        self,
        *,
        messages: Iterable[Mapping[str, Any]],
        tools: Optional[List[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        working_messages = [dict(message) for message in messages]
        available_tools = _merge_tools(DEFAULT_HHS_ASSISTANT_TOOLS, tools)
        trace: List[Dict[str, Any]] = []
        final_response: Dict[str, Any] = {}

        for round_index in range(self.max_tool_rounds + 1):
            final_response = await self.inner.chat_completion(
                messages=working_messages,
                tools=available_tools,
                response_format=response_format,
            )
            choices = list(final_response.get("choices") or [])
            message = dict((choices[0] or {}).get("message") or {}) if choices else {}
            tool_calls = list(message.get("tool_calls") or [])
            if not tool_calls:
                break
            if round_index >= self.max_tool_rounds:
                trace.append({
                    "schema": "HHS_LITERT_LM_TOOL_ROUND_LIMIT_V1",
                    "ok": False,
                    "status": "REJECT_ADDITIONAL_MODEL_TOOL_ROUND",
                    "round_index": round_index,
                    "max_tool_rounds": self.max_tool_rounds,
                    "runtime_mutation_admitted": False,
                })
                break

            working_messages.append({
                "role": "assistant",
                "content": message.get("content") or "",
                "tool_calls": tool_calls,
            })

            for call in tool_calls:
                call_record = dict(call or {})
                function = dict(call_record.get("function") or {})
                tool_name = str(function.get("name") or "")
                arguments = _parse_arguments(function.get("arguments"))
                receipt = await execute_hhs_assistant_api_tool(tool_name, arguments)
                trace.append({
                    "round_index": round_index,
                    "tool_call_id": call_record.get("id"),
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "receipt": receipt,
                })
                working_messages.append({
                    "role": "tool",
                    "tool_call_id": str(call_record.get("id") or f"tool-{round_index}"),
                    "name": tool_name,
                    "content": json.dumps(receipt, ensure_ascii=False, default=str),
                })

        self.last_tool_trace = trace
        final_response = dict(final_response)
        final_response["hhs_api_tool_trace"] = trace
        final_response["hhs_api_tool_round_count"] = len({
            item.get("round_index") for item in trace if "round_index" in item
        })
        return final_response

    def consume_tool_trace(self) -> List[Dict[str, Any]]:
        trace = self.last_tool_trace
        self.last_tool_trace = []
        return trace


class HHSAPIAssistantService(HHSAssistantService):
    """HHS assistant service with default read-only HHS API tool execution."""

    def __init__(
        self,
        config: Optional[LiteRTLMConfig] = None,
        transport: Optional[Any] = None,
        max_tool_rounds: int = MAX_TOOL_ROUNDS,
    ):
        resolved_config = config or LiteRTLMConfig.from_env()
        inner = transport or LiteRTLMTransport(resolved_config)
        governed = (
            inner
            if isinstance(inner, GovernedHHSToolLoopTransport)
            else GovernedHHSToolLoopTransport(inner, max_tool_rounds=max_tool_rounds)
        )
        super().__init__(config=resolved_config, transport=governed)

    async def send_message(
        self,
        thread_id: str,
        *,
        content: str,
        tools: Optional[List[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        result = await super().send_message(
            thread_id,
            content=content,
            tools=tools,
            response_format=response_format,
        )
        transport = self.transport
        trace = (
            transport.consume_tool_trace()
            if isinstance(transport, GovernedHHSToolLoopTransport)
            else []
        )
        result["hhs_api_tool_trace"] = trace
        result["hhs_api_tool_call_count"] = len(trace)
        result["hhs_api_tools_enabled"] = True
        result["mutating_model_tool_execution_allowed"] = False
        result["version"] = VERSION
        result["turn_root_hash72"] = hash72(
            TURN_SCHEMA,
            {key: value for key, value in result.items() if key != "turn_root_hash72"},
        )
        return result

    def status(self) -> Dict[str, Any]:
        status = super().status()
        status.update({
            "version": VERSION,
            "hhs_api_tools_enabled": True,
            "default_hhs_api_tool_count": len(DEFAULT_HHS_ASSISTANT_TOOLS),
            "mutating_model_tool_execution_allowed": False,
            "max_tool_rounds": getattr(self.transport, "max_tool_rounds", 0),
            "authority": AUTHORITY,
        })
        status["status_root_hash72"] = hash72(
            str(status.get("schema") or "HHS_LITERT_LM_ASSISTANT_STATUS_V1"),
            {key: value for key, value in status.items() if key != "status_root_hash72"},
        )
        return status


DEFAULT_HHS_API_ASSISTANT_SERVICE = HHSAPIAssistantService()
