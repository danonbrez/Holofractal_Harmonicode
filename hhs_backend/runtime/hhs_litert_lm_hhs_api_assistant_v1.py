"""LiteRT-compatible assistant with a governed HHS API tool loop."""
from __future__ import annotations

import asyncio
import json
import os
import threading
from contextvars import ContextVar
from dataclasses import replace
from typing import Any, Dict, Iterable, List, Mapping, Optional

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_assistant_api_tool_gateway_v1 import (
    DEFAULT_HHS_ASSISTANT_TOOLS,
    execute_hhs_assistant_api_tool,
)
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    AUTHORITY,
    TURN_SCHEMA,
    ConversationThreadStore,
    HHSAssistantService,
    LiteRTLMConfig,
)
from hhs_backend.runtime.hhs_litert_lm_accelerated_transport_v1 import (
    LiteRTLMAcceleratedTransport,
    backend_from_env,
    compose_request_model_id,
)

VERSION = "HHS_LITERT_LM_GEMMA4_HHS_API_ASSISTANT_V1"
TOOL_LOOP_SCHEMA = "HHS_LITERT_LM_HHS_API_TOOL_LOOP_V1"
MAX_TOOL_ROUNDS = 4
DEFAULT_GEMMA4_MODEL_ALIAS = "gemma4-12b"
HHS_API_SYSTEM_INSTRUCTION = """You are the natural-language AI thread
interface to the Holofractal Harmonicode System (HHS). Preserve explicit user
propositions and HARMONICODE source notation. Use the supplied read-only HHS
API tools whenever current runtime state, services, invariants, conformance,
repository evidence, or Pass status is required. Read-only tool results are
governed HHS evidence. Never claim that a VM81 mutation, repository change,
receipt commit, or canonical state transition occurred unless a separate HHS
API result explicitly contains admitted evidence. Model-generated mutating
operations are proposals only and cannot self-authorize."""


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
    """Wrap a LiteRT-compatible transport and resolve allowlisted HHS tools."""

    def __init__(self, inner: Any, max_tool_rounds: int = MAX_TOOL_ROUNDS):
        self.inner = inner
        self.max_tool_rounds = max(1, int(max_tool_rounds))
        self.provider_id = str(
            getattr(inner, "provider_id", "provider:hhs.litert_lm.gemma4")
        )
        self.requested_operation = str(
            getattr(inner, "requested_operation", "litert_lm.chat_completion")
        )
        self.model_id = str(
            getattr(inner, "model_id", getattr(getattr(inner, "config", None), "model_id", ""))
        )
        self.backend = str(getattr(inner, "backend", "auto"))
        self.request_model_id = str(
            getattr(inner, "request_model_id", self.model_id)
        )
        self._tool_trace: ContextVar[tuple[Dict[str, Any], ...]] = ContextVar(
            "hhs_litert_lm_tool_trace",
            default=(),
        )

    async def list_models(self) -> Dict[str, Any]:
        return await self.inner.list_models()

    async def chat_completion(
        self,
        *,
        messages: Iterable[Mapping[str, Any]],
        tools: Optional[List[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._tool_trace.set(())
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

        self._tool_trace.set(tuple(trace))
        final_response = dict(final_response)
        final_response["hhs_api_tool_trace"] = trace
        final_response["hhs_api_tool_round_count"] = len({
            item.get("round_index") for item in trace if "round_index" in item
        })
        return final_response

    def consume_tool_trace(self) -> List[Dict[str, Any]]:
        trace = [dict(item) for item in self._tool_trace.get()]
        self._tool_trace.set(())
        return trace


class HHSAPIAssistantService(HHSAssistantService):
    """Assistant service with default governed read-only HHS API tools."""

    def __init__(
        self,
        config: Optional[LiteRTLMConfig] = None,
        transport: Optional[Any] = None,
        max_tool_rounds: int = MAX_TOOL_ROUNDS,
        *,
        thread_store: Optional[ConversationThreadStore] = None,
    ):
        resolved_config = config or LiteRTLMConfig.from_env()
        if config is None and transport is None:
            replacements: Dict[str, Any] = {}
            if "HHS_LITERT_LM_MODEL" not in os.environ:
                replacements["model_id"] = DEFAULT_GEMMA4_MODEL_ALIAS
            if "HHS_LITERT_LM_SYSTEM_INSTRUCTION" not in os.environ:
                replacements["system_instruction"] = HHS_API_SYSTEM_INSTRUCTION
            if replacements:
                resolved_config = replace(resolved_config, **replacements)

        requested_backend = str(
            getattr(transport, "backend", None) or backend_from_env()
        )
        inner = transport or LiteRTLMAcceleratedTransport(
            resolved_config,
            backend=requested_backend,
        )
        self.execution_backend = requested_backend
        self.request_model_id = str(
            getattr(
                inner,
                "request_model_id",
                compose_request_model_id(resolved_config.model_id, requested_backend),
            )
        )
        governed = (
            inner
            if isinstance(inner, GovernedHHSToolLoopTransport)
            else GovernedHHSToolLoopTransport(inner, max_tool_rounds=max_tool_rounds)
        )
        super().__init__(
            config=resolved_config,
            transport=governed,
            provider_id=governed.provider_id,
            requested_operation=governed.requested_operation,
            thread_store=thread_store,
        )
        self._thread_locks: Dict[str, asyncio.Lock] = {}
        self._thread_locks_guard = threading.RLock()

    def _thread_lock(self, thread_id: str) -> asyncio.Lock:
        with self._thread_locks_guard:
            lock = self._thread_locks.get(thread_id)
            if lock is None:
                lock = asyncio.Lock()
                self._thread_locks[thread_id] = lock
            return lock

    def _decorate_result(self, thread_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        transport = self.transport
        trace = (
            transport.consume_tool_trace()
            if isinstance(transport, GovernedHHSToolLoopTransport)
            else []
        )
        trace_root = hash72(
            TOOL_LOOP_SCHEMA,
            {
                "thread_id": thread_id,
                "provider_id": self.provider_id,
                "tool_trace": trace,
                "execution_backend": self.execution_backend,
                "request_model_id": self.request_model_id,
                "runtime_mutation_admitted": False,
            },
        )
        result["hhs_api_tool_trace"] = trace
        result["hhs_api_tool_trace_root_hash72"] = trace_root
        result["hhs_api_tool_call_count"] = len(trace)
        result["hhs_api_tools_enabled"] = True
        result["mutating_model_tool_execution_allowed"] = False
        result["per_thread_request_serialization"] = True
        result["execution_backend"] = self.execution_backend
        result["request_model_id"] = self.request_model_id
        result["provider_id"] = self.provider_id
        result["version"] = VERSION
        result["turn_root_hash72"] = hash72(
            TURN_SCHEMA,
            {key: value for key, value in result.items() if key != "turn_root_hash72"},
        )
        return result

    async def send_message(
        self,
        thread_id: str,
        *,
        content: str,
        tools: Optional[List[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.threads.get(thread_id):
            raise KeyError(thread_id)
        async with self._thread_lock(thread_id):
            result = await super().send_message(
                thread_id,
                content=content,
                tools=tools,
                response_format=response_format,
            )
            return self._decorate_result(thread_id, result)

    async def continue_message(
        self,
        thread_id: str,
        *,
        user_message: Mapping[str, Any],
        tools: Optional[List[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.threads.get(thread_id):
            raise KeyError(thread_id)
        async with self._thread_lock(thread_id):
            result = await super().continue_message(
                thread_id,
                user_message=user_message,
                tools=tools,
                response_format=response_format,
            )
            return self._decorate_result(thread_id, result)

    def status(self) -> Dict[str, Any]:
        status = super().status()
        status.update({
            "version": VERSION,
            "hhs_api_tools_enabled": True,
            "default_hhs_api_tool_count": len(DEFAULT_HHS_ASSISTANT_TOOLS),
            "mutating_model_tool_execution_allowed": False,
            "per_thread_request_serialization": True,
            "task_local_tool_traces": True,
            "max_tool_rounds": getattr(self.transport, "max_tool_rounds", 0),
            "execution_backend": self.execution_backend,
            "request_model_id": self.request_model_id,
            "gpu_accelerator_required": self.execution_backend == "gpu",
            "local_gpu_preflight_required": self.execution_backend == "gpu",
            "provider_ready_at_startup": os.getenv(
                "HHS_LITERT_LM_PROVIDER_READY", "0"
            ) == "1",
            "authority": AUTHORITY,
        })
        status["status_root_hash72"] = hash72(
            str(status.get("schema") or "HHS_LITERT_LM_ASSISTANT_STATUS_V1"),
            {key: value for key, value in status.items() if key != "status_root_hash72"},
        )
        return status


DEFAULT_HHS_API_ASSISTANT_SERVICE = HHSAPIAssistantService()
