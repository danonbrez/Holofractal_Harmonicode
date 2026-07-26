"""Governed LiteRT-LM / Gemma 4 conversational thread interface for HHS.

The model is a local capability provider. It never owns canonical HHS state and
cannot mutate VM81 directly. Every completed model turn is wrapped in an HHS
provider invocation receipt and re-enters the universal provider-result ingress.
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
from typing import Any, Dict, Iterable, List, Mapping, Optional

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import (
    build_provider_execution_proposal,
    validate_provider_execution_proposal,
)
from hhs_backend.runtime.hhs_capability_policy_gate_v1 import (
    evaluate_capability_policy_gate,
)
from hhs_backend.runtime.hhs_provider_invocation_receipt_v1 import (
    invoke_provider_with_receipt,
)
from hhs_backend.runtime.hhs_provider_result_ingress_v1 import (
    ingress_provider_result,
)

VERSION = "HHS_LITERT_LM_GEMMA4_ASSISTANT_V1"
AUTHORITY = "HHS_AI_THREAD_INTERFACE_AUTHORITY_V1"
THREAD_SCHEMA = "HHS_AI_CONVERSATION_THREAD_V1"
MESSAGE_SCHEMA = "HHS_AI_CONVERSATION_MESSAGE_V1"
TURN_SCHEMA = "HHS_LITERT_LM_ASSISTANT_TURN_V1"
STATUS_SCHEMA = "HHS_LITERT_LM_ASSISTANT_STATUS_V1"
PROVIDER_ID = "provider:hhs.litert_lm.gemma4"

DEFAULT_SYSTEM_INSTRUCTION = """You are the natural-language conversational
interface to the Holofractal Harmonicode System (HHS). Preserve explicit user
propositions and HARMONICODE source notation. Treat tool use and runtime
operations as proposals only. Never claim that a VM81 mutation, repository
change, receipt, or canonical state transition occurred unless the HHS API
returns an admitted receipt for that operation. Return concise natural-language
responses and structured tool-call arguments when tools are supplied."""


def _now_ms() -> int:
    return int(time.time() * 1000)


def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"


@dataclass(frozen=True)
class LiteRTLMConfig:
    base_url: str = "http://127.0.0.1:9379/v1"
    model_id: str = "gemma-4-E2B-it"
    timeout_seconds: float = 120.0
    max_threads: int = 128
    max_messages_per_thread: int = 64
    max_output_tokens: int = 2048
    temperature: float = 0.2
    top_p: float = 0.95
    top_k: int = 40
    seed: int = 72
    reasoning_effort: str = "medium"
    system_instruction: str = DEFAULT_SYSTEM_INSTRUCTION

    @classmethod
    def from_env(cls) -> "LiteRTLMConfig":
        return cls(
            base_url=os.getenv("HHS_LITERT_LM_BASE_URL", cls.base_url).rstrip("/"),
            model_id=os.getenv("HHS_LITERT_LM_MODEL", cls.model_id),
            timeout_seconds=float(os.getenv("HHS_LITERT_LM_TIMEOUT_SECONDS", "120")),
            max_threads=int(os.getenv("HHS_LITERT_LM_MAX_THREADS", "128")),
            max_messages_per_thread=int(
                os.getenv("HHS_LITERT_LM_MAX_MESSAGES_PER_THREAD", "64")
            ),
            max_output_tokens=int(os.getenv("HHS_LITERT_LM_MAX_OUTPUT_TOKENS", "2048")),
            temperature=float(os.getenv("HHS_LITERT_LM_TEMPERATURE", "0.2")),
            top_p=float(os.getenv("HHS_LITERT_LM_TOP_P", "0.95")),
            top_k=int(os.getenv("HHS_LITERT_LM_TOP_K", "40")),
            seed=int(os.getenv("HHS_LITERT_LM_SEED", "72")),
            reasoning_effort=os.getenv("HHS_LITERT_LM_REASONING_EFFORT", "medium"),
            system_instruction=os.getenv(
                "HHS_LITERT_LM_SYSTEM_INSTRUCTION", DEFAULT_SYSTEM_INSTRUCTION
            ),
        )


class LiteRTLMTransport:
    """Minimal stdlib client for `litert-lm serve` OpenAI-compatible endpoints."""

    def __init__(self, config: LiteRTLMConfig):
        self.config = config

    def _request_sync(
        self,
        method: str,
        path: str,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(dict(payload), ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.config.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.config.timeout_seconds
            ) as response:
                decoded = response.read().decode("utf-8")
                return json.loads(decoded) if decoded else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"LiteRT-LM HTTP {exc.code} for {path}: {detail[:1024]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"LiteRT-LM unavailable at {self.config.base_url}: {exc.reason}"
            ) from exc

    async def list_models(self) -> Dict[str, Any]:
        return await asyncio.to_thread(self._request_sync, "GET", "/models")

    async def chat_completion(
        self,
        *,
        messages: Iterable[Mapping[str, Any]],
        tools: Optional[List[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.config.model_id,
            "messages": [dict(message) for message in messages],
            "stream": False,
            "max_tokens": self.config.max_output_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "top_k": self.config.top_k,
            "seed": self.config.seed,
            "reasoning_effort": self.config.reasoning_effort,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        if response_format:
            payload["response_format"] = dict(response_format)
        return await asyncio.to_thread(
            self._request_sync, "POST", "/chat/completions", payload
        )


class ConversationThreadStore:
    """Bounded in-memory projection store with a Hash72-linked message chain."""

    def __init__(self, config: LiteRTLMConfig):
        self.config = config
        self._threads: Dict[str, Dict[str, Any]] = {}
        self._order: List[str] = []
        self._lock = threading.RLock()

    def _thread_projection(self, thread: Mapping[str, Any]) -> Dict[str, Any]:
        return json.loads(json.dumps(dict(thread), ensure_ascii=False, default=str))

    def create(
        self,
        *,
        project_id: str = "project:default",
        title: str = "HHS Assistant",
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        with self._lock:
            while len(self._order) >= self.config.max_threads:
                evicted = self._order.pop(0)
                self._threads.pop(evicted, None)
            thread_id = _unique("ai-thread")
            thread: Dict[str, Any] = {
                "schema": THREAD_SCHEMA,
                "version": VERSION,
                "thread_id": thread_id,
                "project_id": project_id,
                "title": title,
                "model_id": self.config.model_id,
                "provider_id": PROVIDER_ID,
                "messages": [],
                "message_count": 0,
                "created_at_unix_ms": _now_ms(),
                "updated_at_unix_ms": _now_ms(),
                "bounded_history": True,
                "max_messages": self.config.max_messages_per_thread,
                "transcript_is_canonical_runtime_state": False,
                "model_has_direct_mutation_authority": False,
                "metadata": dict(metadata or {}),
                "authority": AUTHORITY,
            }
            thread["thread_root_hash72"] = hash72(THREAD_SCHEMA, thread)
            self._threads[thread_id] = thread
            self._order.append(thread_id)
            return self._thread_projection(thread)

    def get(self, thread_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            thread = self._threads.get(thread_id)
            return self._thread_projection(thread) if thread else None

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                self._thread_projection(self._threads[thread_id])
                for thread_id in reversed(self._order)
                if thread_id in self._threads
            ]

    def append(
        self,
        thread_id: str,
        *,
        role: str,
        content: str,
        tool_calls: Optional[List[Mapping[str, Any]]] = None,
        admission: Optional[Mapping[str, Any]] = None,
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
                "tool_calls": [dict(item) for item in (tool_calls or [])],
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
                {
                    key: value
                    for key, value in thread.items()
                    if key != "thread_root_hash72"
                },
            )
            return self._thread_projection(message)


class HHSAssistantService:
    def __init__(
        self,
        config: Optional[LiteRTLMConfig] = None,
        transport: Optional[Any] = None,
    ):
        self.config = config or LiteRTLMConfig.from_env()
        self.transport = transport or LiteRTLMTransport(self.config)
        self.threads = ConversationThreadStore(self.config)

    def create_thread(
        self,
        *,
        project_id: str = "project:default",
        title: str = "HHS Assistant",
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.threads.create(
            project_id=project_id, title=title, metadata=metadata
        )

    def status(self) -> Dict[str, Any]:
        status = {
            "schema": STATUS_SCHEMA,
            "version": VERSION,
            "ok": True,
            "provider_id": PROVIDER_ID,
            "model_id": self.config.model_id,
            "base_url": self.config.base_url,
            "thread_count": len(self.threads.list()),
            "openai_compatible_endpoints": ["/v1/models", "/v1/chat/completions"],
            "direct_vm81_mutation_allowed": False,
            "provider_result_ingress_required": True,
            "authority": AUTHORITY,
        }
        status["status_root_hash72"] = hash72(STATUS_SCHEMA, status)
        return status

    async def health(self) -> Dict[str, Any]:
        try:
            models = await self.transport.list_models()
            return {
                **self.status(),
                "online": True,
                "models": models,
                "status": "LITERT_LM_ONLINE",
            }
        except Exception as exc:
            return {
                **self.status(),
                "ok": False,
                "online": False,
                "status": "LITERT_LM_OFFLINE",
                "error": str(exc),
            }

    def _model_messages(self, thread: Mapping[str, Any]) -> List[Dict[str, Any]]:
        projected = [{
            "role": "system",
            "content": self.config.system_instruction,
        }]
        for message in thread.get("messages") or []:
            role = str(message.get("role") or "")
            if role not in {"user", "assistant", "tool"}:
                continue
            entry: Dict[str, Any] = {
                "role": role,
                "content": str(message.get("content") or ""),
            }
            if message.get("tool_calls"):
                entry["tool_calls"] = list(message["tool_calls"])
            projected.append(entry)
        return projected

    @staticmethod
    def _extract_completion(raw: Mapping[str, Any]) -> Dict[str, Any]:
        choices = list(raw.get("choices") or [])
        if not choices:
            raise RuntimeError("LiteRT-LM response contained no choices")
        message = dict((choices[0] or {}).get("message") or {})
        content = message.get("content")
        if content is None:
            content = ""
        return {
            "content": str(content),
            "tool_calls": list(message.get("tool_calls") or []),
            "finish_reason": (choices[0] or {}).get("finish_reason"),
            "usage": dict(raw.get("usage") or {}),
            "model": raw.get("model"),
            "response_id": raw.get("id"),
        }

    async def send_message(
        self,
        thread_id: str,
        *,
        content: str,
        tools: Optional[List[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not str(content).strip():
            raise ValueError("message content must not be empty")
        thread = self.threads.get(thread_id)
        if not thread:
            raise KeyError(thread_id)

        user_message = self.threads.append(
            thread_id, role="user", content=str(content)
        )
        thread = self.threads.get(thread_id)
        assert thread is not None

        proposal = build_provider_execution_proposal(
            capability_class="TEXT_GENERATION",
            project_id=str(thread.get("project_id") or "project:default"),
            input_payload={
                "thread_id": thread_id,
                "message_root_hash72": user_message["message_root_hash72"],
            },
            requested_operation="litert_lm.chat_completion",
            constraints={
                "provider_id": PROVIDER_ID,
                "model_id": self.config.model_id,
                "direct_mutation_allowed": False,
            },
        )
        proposal_validation = validate_provider_execution_proposal(proposal)
        policy = evaluate_capability_policy_gate(proposal)
        if not proposal_validation.get("ok") or not policy.get("ok"):
            result = {
                "schema": TURN_SCHEMA,
                "version": VERSION,
                "ok": False,
                "status": "REJECT_LITERT_LM_PROVIDER_INVOCATION",
                "thread_id": thread_id,
                "user_message": user_message,
                "proposal": proposal,
                "proposal_validation": proposal_validation,
                "policy_gate_decision": policy,
                "runtime_mutation_admitted": False,
                "authority": AUTHORITY,
            }
            result["turn_root_hash72"] = hash72(TURN_SCHEMA, result)
            return result

        try:
            raw_response = await self.transport.chat_completion(
                messages=self._model_messages(thread),
                tools=[dict(tool) for tool in (tools or [])] or None,
                response_format=response_format,
            )
            completion = self._extract_completion(raw_response)
        except Exception as exc:
            result = {
                "schema": TURN_SCHEMA,
                "version": VERSION,
                "ok": False,
                "status": "LITERT_LM_TRANSPORT_ERROR",
                "thread_id": thread_id,
                "user_message": user_message,
                "proposal": proposal,
                "proposal_validation": proposal_validation,
                "policy_gate_decision": policy,
                "error": str(exc),
                "runtime_mutation_admitted": False,
                "authority": AUTHORITY,
            }
            result["turn_root_hash72"] = hash72(TURN_SCHEMA, result)
            return result

        receipt = invoke_provider_with_receipt(
            proposal,
            simulated_raw_result={
                "schema": "HHS_LITERT_LM_RAW_COMPLETION_V1",
                "provider_id": PROVIDER_ID,
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
            tool_calls=completion["tool_calls"],
            admission={
                "provider_invocation_receipt_hash72":
                    receipt.get("provider_invocation_receipt_hash72"),
                "provider_result_ingress_root_hash72":
                    ingress.get("provider_result_ingress_root_hash72"),
                "provider_result_ingress_ok": bool(ingress.get("ok")),
                "runtime_mutation_admitted": False,
            },
        )
        result = {
            "schema": TURN_SCHEMA,
            "version": VERSION,
            "ok": bool(ingress.get("ok")),
            "status": (
                "ADMIT_LITERT_LM_ASSISTANT_TURN"
                if ingress.get("ok")
                else "PROJECT_LITERT_LM_TURN_WITH_INGRESS_REJECTION"
            ),
            "thread_id": thread_id,
            "user_message": user_message,
            "assistant_message": assistant_message,
            "proposal": proposal,
            "proposal_validation": proposal_validation,
            "policy_gate_decision": policy,
            "provider_invocation_receipt": receipt,
            "provider_result_ingress": ingress,
            "runtime_mutation_admitted": False,
            "model_output_is_canonical_without_runtime_admission": False,
            "thread": self.threads.get(thread_id),
            "authority": AUTHORITY,
        }
        result["turn_root_hash72"] = hash72(TURN_SCHEMA, result)
        return result


class _SelfTestTransport:
    async def list_models(self) -> Dict[str, Any]:
        return {"object": "list", "data": [{"id": "gemma-4-E2B-it"}]}

    async def chat_completion(self, **_: Any) -> Dict[str, Any]:
        return {
            "id": "chatcmpl-self-test",
            "model": "gemma-4-E2B-it",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "HHS assistant self-test response",
                },
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 8, "completion_tokens": 5, "total_tokens": 13},
        }


def litert_lm_assistant_self_test() -> Dict[str, Any]:
    config = LiteRTLMConfig(max_messages_per_thread=8, max_threads=4)
    service = HHSAssistantService(config=config, transport=_SelfTestTransport())
    thread = service.create_thread(project_id="project:self-test")
    turn = asyncio.run(
        service.send_message(thread["thread_id"], content="status")
    )
    health = asyncio.run(service.health())
    ok = bool(
        turn.get("assistant_message", {}).get("message_root_hash72")
        and turn.get("provider_invocation_receipt", {}).get(
            "provider_invocation_receipt_hash72"
        )
        and turn.get("provider_result_ingress", {}).get(
            "provider_result_ingress_root_hash72"
        )
        and not turn.get("runtime_mutation_admitted")
        and health.get("online")
    )
    return {
        "schema": "HHS_LITERT_LM_ASSISTANT_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "turn": turn,
        "health": health,
        "invariant": "MODEL_OUTPUT_REQUIRES_HHS_INGRESS_AND_NEVER_DIRECTLY_MUTATES_VM81",
    }


DEFAULT_ASSISTANT_SERVICE = HHSAssistantService()


if __name__ == "__main__":
    print(json.dumps(
        litert_lm_assistant_self_test(),
        indent=2,
        sort_keys=True,
        default=str,
    ))
