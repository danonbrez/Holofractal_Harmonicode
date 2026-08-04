"""Governed Kimi K3 agentic-swarm assistant for the HHS production interface.

Kimi K3 is the primary language and tool-planning provider. It may propose and
parallelize governed HHS API tool calls, but it never owns VM81 mutation,
Hash72/Hash216 commit, repository mutation, or canonical runtime state.

Kimi K3 requires the complete assistant message, including ``reasoning_content``
and ``tool_calls``, to be preserved across multi-turn and multi-tool execution.
This module therefore supplies a Hash72-linked conversation store that retains
the complete provider message envelope without exposing the API key.
"""
from __future__ import annotations

import asyncio
import json
import os
import threading
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from hhs_backend.runtime.hhs_assistant_api_tool_gateway_v1 import (
    DEFAULT_HHS_ASSISTANT_TOOLS,
    execute_hhs_assistant_api_tool,
)
from hhs_backend.runtime.hhs_capability_policy_gate_v1 import (
    evaluate_capability_policy_gate,
)
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    AUTHORITY,
    ConversationThreadStore,
)
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import (
    build_provider_execution_proposal,
    validate_provider_execution_proposal,
)
from hhs_backend.runtime.hhs_provider_invocation_receipt_v1 import (
    invoke_provider_with_receipt,
)
from hhs_backend.runtime.hhs_provider_result_ingress_v1 import (
    ingress_provider_result,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "HHS_PASS_210_KIMI_K3_AGENTIC_SWARM_ASSISTANT_V1"
STATUS_SCHEMA = "HHS_KIMI_K3_AGENTIC_ASSISTANT_STATUS_V1"
TURN_SCHEMA = "HHS_KIMI_K3_AGENTIC_ASSISTANT_TURN_V1"
TOOL_TRACE_SCHEMA = "HHS_KIMI_K3_AGENTIC_SWARM_TOOL_TRACE_V1"
THREAD_SCHEMA = "HHS_AI_CONVERSATION_THREAD_V1"
MESSAGE_SCHEMA = "HHS_AI_CONVERSATION_MESSAGE_V1"
PROVIDER_ID = "provider:hhs.moonshot.kimi_k3.agentic"
REQUESTED_OPERATION = "moonshot.kimi_k3.agentic_swarm_chat_completion"

KIMI_SYSTEM_INSTRUCTION = """You are the primary agentic assistant for the
Holofractal Harmonicode System (HHS). Preserve every explicit user proposition
and exact HARMONICODE notation. Use the supplied governed HHS API tools whenever
current repository, runtime, service, invariant, conformance, pass, or workspace
evidence is required. Independent tool calls may be issued together for bounded
parallel execution. Tool output and model output are proposals and evidence
projections only. Never claim VM81 mutation, Hash72 or Hash216 commit,
repository mutation, deployment completion, or canonical state transition
unless the returned HHS receipt explicitly proves admission. The repository
native AGI observes completed turns as a separate backend learning and
optimization agent; it does not replace your user-facing response."""


def _now_ms() -> int:
    return int(time.time() * 1000)


def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off", "disabled"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _parse_arguments(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, Mapping):
        return dict(raw)
    if raw in (None, ""):
        return {}
    try:
        value = json.loads(str(raw))
    except json.JSONDecodeError:
        return {"_raw": str(raw)}
    return dict(value) if isinstance(value, Mapping) else {"value": value}


def _merge_tools(
    default_tools: Iterable[Mapping[str, Any]],
    supplied_tools: Optional[Sequence[Mapping[str, Any]]],
) -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for tool in [*default_tools, *(supplied_tools or [])]:
        item = dict(tool)
        function = dict(item.get("function") or {})
        name = str(function.get("name") or "")
        if name:
            merged[name] = item
    return [merged[name] for name in sorted(merged)]


@dataclass(frozen=True)
class KimiK3AssistantConfig:
    enabled: bool = True
    base_url: str = "https://api.moonshot.ai/v1"
    model_id: str = "kimi-k3"
    api_key: str = ""
    timeout_seconds: float = 7200.0
    max_threads: int = 128
    max_messages_per_thread: int = 256
    max_completion_tokens: int = 32768
    temperature: float = 1.0
    top_p: float = 1.0
    reasoning_effort: str = "max"
    max_tool_rounds: int = 8
    max_tool_calls_per_round: int = 32
    max_parallel_tools: int = 8
    system_instruction: str = KIMI_SYSTEM_INSTRUCTION

    @classmethod
    def from_env(cls) -> "KimiK3AssistantConfig":
        effort = os.getenv("HHS_KIMI_K3_REASONING_EFFORT", cls.reasoning_effort).strip().lower()
        if effort not in {"low", "high", "max"}:
            effort = cls.reasoning_effort
        return cls(
            enabled=_env_bool("HHS_KIMI_K3_ENABLED", True),
            base_url=os.getenv("HHS_KIMI_K3_BASE_URL", cls.base_url).rstrip("/"),
            model_id=os.getenv("HHS_KIMI_K3_MODEL", cls.model_id).strip() or cls.model_id,
            api_key=(os.getenv("HHS_KIMI_K3_API_KEY") or os.getenv("MOONSHOT_API_KEY") or "").strip(),
            timeout_seconds=float(os.getenv("HHS_KIMI_K3_TIMEOUT_SECONDS", str(cls.timeout_seconds))),
            max_threads=int(os.getenv("HHS_KIMI_K3_MAX_THREADS", str(cls.max_threads))),
            max_messages_per_thread=int(
                os.getenv("HHS_KIMI_K3_MAX_MESSAGES_PER_THREAD", str(cls.max_messages_per_thread))
            ),
            max_completion_tokens=int(
                os.getenv("HHS_KIMI_K3_MAX_COMPLETION_TOKENS", str(cls.max_completion_tokens))
            ),
            temperature=float(os.getenv("HHS_KIMI_K3_TEMPERATURE", str(cls.temperature))),
            top_p=float(os.getenv("HHS_KIMI_K3_TOP_P", str(cls.top_p))),
            reasoning_effort=effort,
            max_tool_rounds=int(os.getenv("HHS_KIMI_K3_MAX_TOOL_ROUNDS", str(cls.max_tool_rounds))),
            max_tool_calls_per_round=int(
                os.getenv("HHS_KIMI_K3_MAX_TOOL_CALLS_PER_ROUND", str(cls.max_tool_calls_per_round))
            ),
            max_parallel_tools=int(
                os.getenv("HHS_KIMI_K3_MAX_PARALLEL_TOOLS", str(cls.max_parallel_tools))
            ),
            system_instruction=os.getenv(
                "HHS_KIMI_K3_SYSTEM_INSTRUCTION", cls.system_instruction
            ),
        )


class KimiConversationThreadStore(ConversationThreadStore):
    """Conversation store preserving Kimi reasoning and tool protocol fields."""

    def append(
        self,
        thread_id: str,
        *,
        role: str,
        content: str,
        tool_calls: Optional[List[Mapping[str, Any]]] = None,
        admission: Optional[Mapping[str, Any]] = None,
        reasoning_content: str = "",
        tool_call_id: Optional[str] = None,
        name: Optional[str] = None,
        provider_message: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized_role = str(role).lower()
        if normalized_role not in {"system", "user", "assistant", "tool"}:
            raise ValueError(f"unsupported conversation role: {role}")
        with self._lock:
            thread = self._threads.get(thread_id)
            if not thread:
                raise KeyError(thread_id)
            messages = thread["messages"]
            previous_root = (
                messages[-1]["message_root_hash72"]
                if messages
                else thread["thread_root_hash72"]
            )
            message: Dict[str, Any] = {
                "schema": MESSAGE_SCHEMA,
                "version": VERSION,
                "message_id": _unique("ai-message"),
                "thread_id": thread_id,
                "sequence": int(thread.get("message_count", 0)) + 1,
                "role": normalized_role,
                "content": str(content),
                "reasoning_content": str(reasoning_content or ""),
                "tool_calls": [dict(item) for item in (tool_calls or [])],
                "tool_call_id": str(tool_call_id or ""),
                "name": str(name or ""),
                "provider_message": dict(provider_message or {}),
                "previous_message_root_hash72": previous_root,
                "provider_output_is_canonical_without_runtime_admission": False,
                "admission": dict(admission or {}),
                "created_at_unix_ms": _now_ms(),
                "authority": AUTHORITY,
            }
            message["message_root_hash72"] = hash72(MESSAGE_SCHEMA, message)
            messages.append(message)
            if len(messages) > self.config.max_messages_per_thread:
                del messages[: len(messages) - self.config.max_messages_per_thread]
            thread["message_count"] = int(thread.get("message_count", 0)) + 1
            thread["updated_at_unix_ms"] = _now_ms()
            thread["message_tip_hash72"] = message["message_root_hash72"]
            thread["thread_root_hash72"] = hash72(
                THREAD_SCHEMA,
                {key: value for key, value in thread.items() if key != "thread_root_hash72"},
            )
            return self._thread_projection(message)


class KimiK3APITransport:
    provider_id = PROVIDER_ID
    requested_operation = REQUESTED_OPERATION
    backend = "remote_api"

    def __init__(self, config: KimiK3AssistantConfig):
        self.config = config
        self.model_id = config.model_id
        self.request_model_id = config.model_id

    def _request_sync(
        self,
        method: str,
        path: str,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.config.enabled:
            raise RuntimeError("Kimi K3 assistant is disabled")
        if not self.config.api_key:
            raise RuntimeError(
                "Kimi K3 API key is not configured; set MOONSHOT_API_KEY or HHS_KIMI_K3_API_KEY"
            )
        body = None
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": "HHS-Pass210-KimiK3-Agentic/1.0",
        }
        if payload is not None:
            body = _canonical_json(dict(payload)).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.config.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                decoded = response.read().decode("utf-8")
                return json.loads(decoded) if decoded else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Kimi K3 HTTP {exc.code} for {path}: {detail[:4096]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Kimi K3 unavailable at {self.config.base_url}: {exc.reason}") from exc

    async def list_models(self) -> Dict[str, Any]:
        return await asyncio.to_thread(self._request_sync, "GET", "/models")

    async def chat_completion(
        self,
        *,
        messages: Sequence[Mapping[str, Any]],
        tools: Optional[Sequence[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
        prompt_cache_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.config.model_id,
            "messages": [dict(message) for message in messages],
            "stream": False,
            "max_completion_tokens": self.config.max_completion_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "reasoning_effort": self.config.reasoning_effort,
            "parallel_tool_calls": True,
        }
        if prompt_cache_key:
            payload["prompt_cache_key"] = str(prompt_cache_key)
        if tools:
            payload["tools"] = [dict(tool) for tool in tools]
            payload["tool_choice"] = "auto"
        if response_format:
            payload["response_format"] = dict(response_format)
        return await asyncio.to_thread(
            self._request_sync,
            "POST",
            "/chat/completions",
            payload,
        )


class KimiK3AgenticSwarmTransport:
    """Bounded parallel HHS tool loop preserving complete Kimi messages."""

    def __init__(self, inner: Any, config: KimiK3AssistantConfig):
        self.inner = inner
        self.config = config
        self.provider_id = str(getattr(inner, "provider_id", PROVIDER_ID))
        self.requested_operation = str(getattr(inner, "requested_operation", REQUESTED_OPERATION))
        self.model_id = str(getattr(inner, "model_id", config.model_id))
        self.request_model_id = str(getattr(inner, "request_model_id", self.model_id))
        self.backend = str(getattr(inner, "backend", "remote_api"))

    async def list_models(self) -> Dict[str, Any]:
        return await self.inner.list_models()

    async def _execute_one(
        self,
        semaphore: asyncio.Semaphore,
        round_index: int,
        call_index: int,
        call: Mapping[str, Any],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        call_record = dict(call or {})
        function = dict(call_record.get("function") or {})
        tool_name = str(function.get("name") or "")
        arguments = _parse_arguments(function.get("arguments"))
        async with semaphore:
            receipt = await execute_hhs_assistant_api_tool(tool_name, arguments)
        tool_message = {
            "role": "tool",
            "tool_call_id": str(call_record.get("id") or f"kimi-tool-{round_index}-{call_index}"),
            "name": tool_name,
            "content": json.dumps(receipt, ensure_ascii=False, sort_keys=True, default=str),
        }
        trace = {
            "round_index": round_index,
            "call_index": call_index,
            "tool_call_id": tool_message["tool_call_id"],
            "tool_name": tool_name,
            "arguments": arguments,
            "receipt": receipt,
            "parallel_execution_bounded": True,
            "runtime_mutation_admitted": False,
        }
        return tool_message, trace

    async def chat_completion(
        self,
        *,
        messages: Sequence[Mapping[str, Any]],
        tools: Optional[Sequence[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
        prompt_cache_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        working_messages = [dict(message) for message in messages]
        available_tools = _merge_tools(DEFAULT_HHS_ASSISTANT_TOOLS, tools)
        transcript: List[Dict[str, Any]] = []
        trace: List[Dict[str, Any]] = []
        final_response: Dict[str, Any] = {}
        round_limit_reached = False

        for round_index in range(max(1, self.config.max_tool_rounds) + 1):
            final_response = await self.inner.chat_completion(
                messages=working_messages,
                tools=available_tools,
                response_format=response_format,
                prompt_cache_key=prompt_cache_key,
            )
            choices = list(final_response.get("choices") or [])
            message = dict((choices[0] or {}).get("message") or {}) if choices else {}
            tool_calls = [dict(item) for item in (message.get("tool_calls") or [])]
            if not tool_calls:
                break
            if round_index >= self.config.max_tool_rounds:
                round_limit_reached = True
                trace.append({
                    "schema": "HHS_KIMI_K3_TOOL_ROUND_LIMIT_V1",
                    "ok": False,
                    "round_index": round_index,
                    "max_tool_rounds": self.config.max_tool_rounds,
                    "status": "REJECT_ADDITIONAL_KIMI_TOOL_ROUND",
                    "runtime_mutation_admitted": False,
                })
                break

            preserved_assistant = dict(message)
            preserved_assistant.setdefault("role", "assistant")
            preserved_assistant.setdefault("content", "")
            working_messages.append(preserved_assistant)
            transcript.append(preserved_assistant)

            allowed = tool_calls[: max(1, self.config.max_tool_calls_per_round)]
            rejected = tool_calls[len(allowed) :]
            semaphore = asyncio.Semaphore(max(1, self.config.max_parallel_tools))
            executed = await asyncio.gather(*[
                self._execute_one(semaphore, round_index, index, call)
                for index, call in enumerate(allowed)
            ])
            for tool_message, item_trace in executed:
                working_messages.append(tool_message)
                transcript.append(tool_message)
                trace.append(item_trace)

            for offset, call in enumerate(rejected, start=len(allowed)):
                call_record = dict(call or {})
                function = dict(call_record.get("function") or {})
                tool_name = str(function.get("name") or "")
                receipt = {
                    "schema": "HHS_KIMI_K3_TOOL_CALL_LIMIT_REJECTION_V1",
                    "ok": False,
                    "status": "REJECT_TOOL_CALL_OVER_PER_ROUND_LIMIT",
                    "tool_name": tool_name,
                    "max_tool_calls_per_round": self.config.max_tool_calls_per_round,
                    "runtime_mutation_admitted": False,
                }
                tool_message = {
                    "role": "tool",
                    "tool_call_id": str(call_record.get("id") or f"kimi-tool-{round_index}-{offset}"),
                    "name": tool_name,
                    "content": json.dumps(receipt, ensure_ascii=False, sort_keys=True),
                }
                working_messages.append(tool_message)
                transcript.append(tool_message)
                trace.append({
                    "round_index": round_index,
                    "call_index": offset,
                    "tool_call_id": tool_message["tool_call_id"],
                    "tool_name": tool_name,
                    "arguments": _parse_arguments(function.get("arguments")),
                    "receipt": receipt,
                    "parallel_execution_bounded": True,
                    "runtime_mutation_admitted": False,
                })

        result = dict(final_response)
        result["hhs_agent_transcript"] = transcript
        result["hhs_api_tool_trace"] = trace
        result["hhs_api_tool_call_count"] = len([
            item for item in trace if item.get("tool_call_id")
        ])
        result["hhs_api_tool_round_count"] = len({
            int(item["round_index"])
            for item in trace
            if isinstance(item.get("round_index"), int) and item.get("tool_call_id")
        })
        result["hhs_swarm_round_limit_reached"] = round_limit_reached
        result["hhs_parallel_tool_limit"] = self.config.max_parallel_tools
        result["hhs_tool_call_limit_per_round"] = self.config.max_tool_calls_per_round
        return result


class KimiK3AgenticAssistantService:
    """Provider-governed Kimi K3 assistant with witnessed swarm transcripts."""

    def __init__(
        self,
        config: Optional[KimiK3AssistantConfig] = None,
        transport: Optional[Any] = None,
        *,
        thread_store: Optional[KimiConversationThreadStore] = None,
    ) -> None:
        self.config = config or KimiK3AssistantConfig.from_env()
        inner = transport or KimiK3APITransport(self.config)
        self.transport = (
            inner
            if isinstance(inner, KimiK3AgenticSwarmTransport)
            else KimiK3AgenticSwarmTransport(inner, self.config)
        )
        self.provider_id = str(getattr(self.transport, "provider_id", PROVIDER_ID))
        self.requested_operation = str(
            getattr(self.transport, "requested_operation", REQUESTED_OPERATION)
        )
        self.threads = thread_store or KimiConversationThreadStore(
            self.config,
            provider_id=self.provider_id,
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

    def create_thread(
        self,
        *,
        project_id: str = "project:default",
        title: str = "HHS Assistant",
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.threads.create(
            project_id=project_id,
            title=title,
            metadata=metadata,
        )

    def status(self) -> Dict[str, Any]:
        status: Dict[str, Any] = {
            "schema": STATUS_SCHEMA,
            "version": VERSION,
            "ok": bool(self.config.enabled),
            "online": False,
            "status": (
                "KIMI_K3_READY_FOR_PROVIDER_PROBE"
                if self.config.enabled and self.config.api_key
                else "KIMI_K3_CONFIGURATION_REQUIRED"
                if self.config.enabled
                else "KIMI_K3_DISABLED"
            ),
            "provider_id": self.provider_id,
            "model_id": self.config.model_id,
            "base_url": self.config.base_url,
            "configured": bool(self.config.api_key),
            "api_key_exposed": False,
            "reasoning_effort": self.config.reasoning_effort,
            "reasoning_content_history_preserved": True,
            "tool_call_history_preserved": True,
            "parallel_tool_calls": True,
            "max_tool_rounds": self.config.max_tool_rounds,
            "max_tool_calls_per_round": self.config.max_tool_calls_per_round,
            "max_parallel_tools": self.config.max_parallel_tools,
            "prompt_cache_key_bound_to_thread": True,
            "thread_count": len(self.threads.list()),
            "direct_vm81_mutation_allowed": False,
            "provider_result_ingress_required": True,
            "authority": AUTHORITY,
        }
        status["status_root_hash72"] = hash72(STATUS_SCHEMA, status)
        return status

    async def health(self) -> Dict[str, Any]:
        base = self.status()
        if not self.config.enabled or not self.config.api_key:
            return {
                **base,
                "ok": False,
                "online": False,
                "configured_model_registered": False,
                "error": "Kimi K3 is disabled" if not self.config.enabled else "API key is not configured",
            }
        try:
            models = await self.transport.list_models()
            model_ids = {
                str(item.get("id"))
                for item in (models.get("data") or [])
                if isinstance(item, Mapping) and item.get("id")
            }
            ready = self.config.model_id in model_ids
            return {
                **base,
                "ok": ready,
                "online": True,
                "configured_model_registered": ready,
                "registered_model_ids": sorted(model_ids),
                "status": "KIMI_K3_MODEL_READY" if ready else "KIMI_K3_MODEL_NOT_REGISTERED",
                "error": None if ready else "configured model is not listed by the provider",
            }
        except Exception as exc:
            return {
                **base,
                "ok": False,
                "online": False,
                "configured_model_registered": False,
                "status": "KIMI_K3_PROVIDER_OFFLINE",
                "error": f"{type(exc).__name__}: {exc}",
            }

    def _model_messages(self, thread: Mapping[str, Any]) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = [{
            "role": "system",
            "content": self.config.system_instruction,
        }]
        for message in thread.get("messages") or []:
            role = str(message.get("role") or "")
            if role not in {"user", "assistant", "tool"}:
                continue
            projected: Dict[str, Any] = {
                "role": role,
                "content": str(message.get("content") or ""),
            }
            if role == "assistant":
                if message.get("reasoning_content"):
                    projected["reasoning_content"] = str(message["reasoning_content"])
                if message.get("tool_calls"):
                    projected["tool_calls"] = [dict(item) for item in message["tool_calls"]]
                provider_message = dict(message.get("provider_message") or {})
                for key, value in provider_message.items():
                    if key not in {"role", "content", "reasoning_content", "tool_calls"}:
                        projected[key] = value
            if role == "tool":
                projected["tool_call_id"] = str(message.get("tool_call_id") or "")
                if message.get("name"):
                    projected["name"] = str(message["name"])
            messages.append(projected)
        return messages

    @staticmethod
    def _extract_completion(raw: Mapping[str, Any]) -> Dict[str, Any]:
        choices = list(raw.get("choices") or [])
        if not choices:
            raise RuntimeError("Kimi K3 response contained no choices")
        message = dict((choices[0] or {}).get("message") or {})
        return {
            "content": str(message.get("content") or ""),
            "reasoning_content": str(message.get("reasoning_content") or ""),
            "tool_calls": [dict(item) for item in (message.get("tool_calls") or [])],
            "provider_message": message,
            "finish_reason": (choices[0] or {}).get("finish_reason"),
            "usage": dict(raw.get("usage") or {}),
            "model": raw.get("model"),
            "response_id": raw.get("id"),
            "tool_trace": [dict(item) for item in (raw.get("hhs_api_tool_trace") or [])],
            "agent_transcript": [dict(item) for item in (raw.get("hhs_agent_transcript") or [])],
            "swarm_round_limit_reached": bool(raw.get("hhs_swarm_round_limit_reached")),
        }

    def _append_transcript(self, thread_id: str, transcript: Sequence[Mapping[str, Any]]) -> None:
        for item in transcript:
            message = dict(item)
            role = str(message.get("role") or "")
            if role == "assistant":
                self.threads.append(
                    thread_id,
                    role="assistant",
                    content=str(message.get("content") or ""),
                    reasoning_content=str(message.get("reasoning_content") or ""),
                    tool_calls=[dict(call) for call in (message.get("tool_calls") or [])],
                    provider_message=message,
                    admission={
                        "intermediate_agentic_message": True,
                        "runtime_mutation_admitted": False,
                    },
                )
            elif role == "tool":
                self.threads.append(
                    thread_id,
                    role="tool",
                    content=str(message.get("content") or ""),
                    tool_call_id=str(message.get("tool_call_id") or ""),
                    name=str(message.get("name") or ""),
                    provider_message=message,
                    admission={
                        "governed_hhs_tool_receipt": True,
                        "runtime_mutation_admitted": False,
                    },
                )

    async def _execute_turn(
        self,
        thread_id: str,
        *,
        user_message: Mapping[str, Any],
        tools: Optional[Sequence[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        thread = self.threads.get(thread_id)
        if not thread:
            raise KeyError(thread_id)
        proposal = build_provider_execution_proposal(
            capability_class="TEXT_GENERATION",
            project_id=str(thread.get("project_id") or "project:default"),
            input_payload={
                "thread_id": thread_id,
                "message_root_hash72": user_message["message_root_hash72"],
                "prompt_cache_key": thread_id,
            },
            requested_operation=self.requested_operation,
            constraints={
                "provider_id": self.provider_id,
                "model_id": self.config.model_id,
                "direct_mutation_allowed": False,
                "parallel_tool_execution_bounded": True,
            },
        )
        proposal_validation = validate_provider_execution_proposal(proposal)
        policy = evaluate_capability_policy_gate(proposal)
        if not proposal_validation.get("ok") or not policy.get("ok"):
            result: Dict[str, Any] = {
                "schema": TURN_SCHEMA,
                "version": VERSION,
                "ok": False,
                "status": "REJECT_KIMI_K3_PROVIDER_INVOCATION",
                "thread_id": thread_id,
                "user_message": dict(user_message),
                "proposal": proposal,
                "proposal_validation": proposal_validation,
                "policy_gate_decision": policy,
                "runtime_mutation_admitted": False,
                "authority": AUTHORITY,
            }
            result["turn_root_hash72"] = hash72(TURN_SCHEMA, result)
            return result

        try:
            raw = await self.transport.chat_completion(
                messages=self._model_messages(thread),
                tools=tools,
                response_format=response_format,
                prompt_cache_key=thread_id,
            )
            completion = self._extract_completion(raw)
        except Exception as exc:
            result = {
                "schema": TURN_SCHEMA,
                "version": VERSION,
                "ok": False,
                "status": "KIMI_K3_TRANSPORT_ERROR",
                "thread_id": thread_id,
                "user_message": dict(user_message),
                "proposal": proposal,
                "proposal_validation": proposal_validation,
                "policy_gate_decision": policy,
                "error": f"{type(exc).__name__}: {exc}",
                "runtime_mutation_admitted": False,
                "authority": AUTHORITY,
            }
            result["turn_root_hash72"] = hash72(TURN_SCHEMA, result)
            return result

        self._append_transcript(thread_id, completion["agent_transcript"])
        receipt = invoke_provider_with_receipt(
            proposal,
            simulated_raw_result={
                "schema": "HHS_KIMI_K3_RAW_COMPLETION_V1",
                "provider_id": self.provider_id,
                "model_id": completion.get("model") or self.config.model_id,
                **completion,
            },
        )
        ingress = ingress_provider_result(
            receipt,
            project_id=str(thread.get("project_id") or "project:default"),
            output_modality="TEXT",
            target_artifact_type="AI_THREAD_ASSISTANT_TURN",
        )
        assistant_message = self.threads.append(
            thread_id,
            role="assistant",
            content=completion["content"],
            reasoning_content=completion["reasoning_content"],
            tool_calls=completion["tool_calls"],
            provider_message=completion["provider_message"],
            admission={
                "provider_id": self.provider_id,
                "provider_invocation_receipt_hash72": receipt.get(
                    "provider_invocation_receipt_hash72"
                ),
                "provider_result_ingress_root_hash72": ingress.get(
                    "provider_result_ingress_root_hash72"
                ),
                "provider_result_ingress_ok": bool(ingress.get("ok")),
                "runtime_mutation_admitted": False,
            },
        )
        completed = bool(
            ingress.get("ok")
            and completion["content"].strip()
            and not completion["swarm_round_limit_reached"]
        )
        result = {
            "schema": TURN_SCHEMA,
            "version": VERSION,
            "ok": completed,
            "status": (
                "ADMIT_KIMI_K3_AGENTIC_ASSISTANT_TURN"
                if completed
                else "KIMI_K3_AGENTIC_TURN_INCOMPLETE"
            ),
            "thread_id": thread_id,
            "user_message": dict(user_message),
            "assistant_message": assistant_message,
            "proposal": proposal,
            "proposal_validation": proposal_validation,
            "policy_gate_decision": policy,
            "provider_invocation_receipt": receipt,
            "provider_result_ingress": ingress,
            "hhs_api_tool_trace": completion["tool_trace"],
            "hhs_api_tool_call_count": len(completion["tool_trace"]),
            "hhs_swarm_round_limit_reached": completion["swarm_round_limit_reached"],
            "reasoning_content_preserved": bool(completion["reasoning_content"]),
            "reasoning_content_exposed_in_status": False,
            "runtime_mutation_admitted": False,
            "model_output_is_canonical_without_runtime_admission": False,
            "thread": self.threads.get(thread_id),
            "authority": AUTHORITY,
        }
        result["tool_trace_root_hash72"] = hash72(
            TOOL_TRACE_SCHEMA,
            {
                "thread_id": thread_id,
                "provider_id": self.provider_id,
                "trace": completion["tool_trace"],
                "runtime_mutation_admitted": False,
            },
        )
        result["turn_root_hash72"] = hash72(TURN_SCHEMA, result)
        return result

    async def send_message(
        self,
        thread_id: str,
        *,
        content: str,
        tools: Optional[Sequence[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not str(content).strip():
            raise ValueError("message content must not be empty")
        if not self.threads.get(thread_id):
            raise KeyError(thread_id)
        async with self._thread_lock(thread_id):
            user_message = self.threads.append(
                thread_id,
                role="user",
                content=str(content),
            )
            return await self._execute_turn(
                thread_id,
                user_message=user_message,
                tools=tools,
                response_format=response_format,
            )

    async def continue_message(
        self,
        thread_id: str,
        *,
        user_message: Mapping[str, Any],
        tools: Optional[Sequence[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.threads.get(thread_id):
            raise KeyError(thread_id)
        if (
            user_message.get("thread_id") != thread_id
            or user_message.get("role") != "user"
            or not user_message.get("message_root_hash72")
        ):
            raise ValueError("existing user message is not a witnessed message for this thread")
        async with self._thread_lock(thread_id):
            return await self._execute_turn(
                thread_id,
                user_message=user_message,
                tools=tools,
                response_format=response_format,
            )


DEFAULT_KIMI_K3_AGENTIC_ASSISTANT = KimiK3AgenticAssistantService()
