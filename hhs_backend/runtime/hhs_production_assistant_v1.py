"""Production HHS assistant provider hierarchy.

The public assistant first uses the configured LiteRT-LM/OpenAI-compatible
provider with the governed HHS tool loop. When that provider is unavailable,
it remains operational through a deterministic natural-language capability and
repository-retrieval assistant backed by read-only HHS API tool receipts. The
fallback does not impersonate a model and does not fabricate runtime mutation.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any, Dict, List, Mapping, Optional

from hhs_backend.runtime.hhs_assistant_api_tool_gateway_v1 import (
    assistant_api_tool_registry,
    execute_hhs_assistant_api_tool,
)
from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import (
    DEFAULT_HHS_API_ASSISTANT_SERVICE,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "HHS_PRODUCTION_ASSISTANT_V1"
STATUS_SCHEMA = "HHS_PRODUCTION_ASSISTANT_STATUS_V1"
TURN_SCHEMA = "HHS_PRODUCTION_ASSISTANT_TURN_V1"
PROVIDER_ID = "provider:hhs.production_assistant"
DETERMINISTIC_PROVIDER_ID = "provider:hhs.deterministic_capability_assistant"


class ProductionAssistantService:
    """Always-available assistant with an honest provider fallback boundary."""

    def __init__(self, model_service: Any = None):
        self.model_service = model_service or DEFAULT_HHS_API_ASSISTANT_SERVICE
        self.threads = self.model_service.threads
        self._health_cache: Optional[Dict[str, Any]] = None
        self._health_cache_at = 0.0
        self._health_ttl = max(
            1.0,
            float(os.getenv("HHS_ASSISTANT_HEALTH_CACHE_SECONDS", "15")),
        )
        self._health_timeout = max(
            0.5,
            float(os.getenv("HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS", "3")),
        )

    def create_thread(
        self,
        *,
        project_id: str = "project:default",
        title: str = "HHS Assistant",
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.model_service.create_thread(
            project_id=project_id,
            title=title,
            metadata=metadata,
        )

    def _base_status(self) -> Dict[str, Any]:
        model_status = self.model_service.status()
        status: Dict[str, Any] = {
            **model_status,
            "schema": STATUS_SCHEMA,
            "version": VERSION,
            "ok": True,
            "online": True,
            "provider_id": PROVIDER_ID,
            "model_provider_id": model_status.get("provider_id"),
            "deterministic_provider_id": DETERMINISTIC_PROVIDER_ID,
            "deterministic_fallback_enabled": True,
            "repository_retrieval_enabled": True,
            "same_template_response_enabled": False,
            "public_interface_mode": "PRODUCTION",
            "runtime_mutation_admitted": False,
        }
        status["status_root_hash72"] = hash72(
            STATUS_SCHEMA,
            {key: value for key, value in status.items() if key != "status_root_hash72"},
        )
        return status

    def status(self) -> Dict[str, Any]:
        status = self._base_status()
        cached = self._health_cache or {}
        status.update({
            "model_online": bool(cached.get("online")),
            "effective_mode": (
                "GOVERNED_MODEL_AND_HHS_TOOLS"
                if cached.get("online")
                else "DETERMINISTIC_HHS_CAPABILITY_ASSISTANT"
            ),
        })
        return status

    async def _model_health(self, *, force: bool = False) -> Dict[str, Any]:
        now = time.monotonic()
        if (
            not force
            and self._health_cache is not None
            and now - self._health_cache_at < self._health_ttl
        ):
            return dict(self._health_cache)
        try:
            health = await asyncio.wait_for(
                self.model_service.health(),
                timeout=self._health_timeout,
            )
        except Exception as exc:
            health = {
                "ok": False,
                "online": False,
                "status": "MODEL_PROVIDER_HEALTH_ERROR",
                "error": f"{type(exc).__name__}: {exc}",
            }
        self._health_cache = dict(health)
        self._health_cache_at = now
        return dict(health)

    async def health(self) -> Dict[str, Any]:
        model_health = await self._model_health(force=True)
        result = self._base_status()
        result.update({
            "online": True,
            "status": "HHS_PRODUCTION_ASSISTANT_ONLINE",
            "model_online": bool(model_health.get("online")),
            "model_health": model_health,
            "effective_mode": (
                "GOVERNED_MODEL_AND_HHS_TOOLS"
                if model_health.get("online")
                else "DETERMINISTIC_HHS_CAPABILITY_ASSISTANT"
            ),
            "supported_without_model": [
                "runtime state",
                "registered services",
                "service status",
                "kernel invariants",
                "kernel conformance",
                "Pass 152 status",
                "Pass 152 capabilities",
                "assistant tool registry",
                "bounded repository knowledge search",
            ],
        })
        result["status_root_hash72"] = hash72(
            STATUS_SCHEMA,
            {key: value for key, value in result.items() if key != "status_root_hash72"},
        )
        return result

    @staticmethod
    def _select_tools(content: str) -> List[str]:
        text = content.casefold()
        selected: List[str] = []

        def add(name: str) -> None:
            if name not in selected:
                selected.append(name)

        if any(token in text for token in ("runtime", "vm81", "state", "status")):
            add("hhs_runtime_state")
        if any(token in text for token in ("service", "registered", "surface")):
            add("hhs_runtime_services")
            add("hhs_runtime_service_status")
        if any(token in text for token in ("invariant", "constraint", "kernel", "conformance")):
            add("hhs_kernel_invariants")
            add("hhs_kernel_conformance_status")
        if "pass 152" in text or "pass152" in text or "elastic closure" in text:
            add("hhs_pass152_status")
            add("hhs_pass152_capabilities")
        if not selected and any(token in text for token in ("capability", "tool", "what can", "help")):
            return []
        if not selected:
            add("hhs_repository_search")
        return selected

    @staticmethod
    def _top_level_summary(value: Any, *, limit: int = 8) -> List[str]:
        if not isinstance(value, Mapping):
            return [str(value)]
        lines: List[str] = []
        preferred = (
            "status",
            "classification",
            "system",
            "runtime_id",
            "boot_id",
            "authority",
            "pass",
            "contract_id",
            "canonical_invariant",
            "available",
            "count",
        )
        for key in preferred:
            if key not in value:
                continue
            item = value[key]
            if isinstance(item, (str, int, float, bool)) or item is None:
                lines.append(f"{key}: {item}")
        if len(lines) < limit:
            for key, item in value.items():
                if any(line.startswith(f"{key}:") for line in lines):
                    continue
                if isinstance(item, list):
                    lines.append(f"{key}: {len(item)} item(s)")
                elif isinstance(item, Mapping):
                    lines.append(f"{key}: {len(item)} field(s)")
                elif isinstance(item, (str, int, float, bool)) or item is None:
                    lines.append(f"{key}: {item}")
                if len(lines) >= limit:
                    break
        return lines or ["No scalar projection was returned."]

    def _compose_answer(
        self,
        content: str,
        trace: List[Dict[str, Any]],
        model_error: Optional[str] = None,
    ) -> str:
        text = content.casefold()
        if any(token in text for token in ("what can", "capability", "tool", "help")):
            registry = assistant_api_tool_registry()
            names = registry.get("tool_names") or []
            return (
                "The production assistant is online. I can execute these governed "
                f"read-only HHS tools now: {', '.join(map(str, names))}. "
                "A configured model provider expands this to generative reasoning; "
                "repository retrieval remains available without it, and runtime "
                "mutation still requires separate admission."
            )

        sections: List[str] = []
        for item in trace:
            tool_name = str(item.get("tool_name") or "HHS tool")
            receipt = dict(item.get("receipt") or {})
            if not receipt.get("ok"):
                sections.append(
                    f"{tool_name} could not complete: {receipt.get('error') or receipt.get('reason') or receipt.get('status')}"
                )
                continue
            response = receipt.get("response")
            if tool_name == "hhs_repository_search" and isinstance(response, Mapping):
                results = response.get("results") or []
                if results:
                    evidence = []
                    for result in results:
                        if not isinstance(result, Mapping):
                            continue
                        evidence.append(
                            f"- {result.get('path')}: {result.get('snippet')}"
                        )
                    sections.append(
                        "Repository evidence\n" + "\n".join(evidence)
                    )
                else:
                    sections.append(
                        f"Repository search found no bounded source match for: {content}"
                    )
                continue
            summary = self._top_level_summary(response)
            sections.append(
                f"{tool_name}\n" + "\n".join(f"- {line}" for line in summary)
            )

        if not sections:
            sections.append(
                "No matching governed HHS read-only tool was required for this request."
            )
        provider_note = (
            f"\n\nThe configured model provider was unavailable ({model_error}); "
            "this answer was generated from governed HHS tool and repository evidence."
            if model_error
            else "\n\nThis answer was generated from governed HHS tool and repository evidence."
        )
        return "\n\n".join(sections) + provider_note

    async def _deterministic_turn(
        self,
        thread_id: str,
        *,
        content: str,
        existing_user_message: Optional[Mapping[str, Any]] = None,
        model_error: Optional[str] = None,
    ) -> Dict[str, Any]:
        thread = self.threads.get(thread_id)
        if not thread:
            raise KeyError(thread_id)
        user_message = (
            dict(existing_user_message)
            if existing_user_message
            else self.threads.append(thread_id, role="user", content=content)
        )
        trace: List[Dict[str, Any]] = []
        for tool_name in self._select_tools(content):
            arguments: Dict[str, Any] = (
                {"query": content, "limit": 5}
                if tool_name == "hhs_repository_search"
                else {}
            )
            receipt = await execute_hhs_assistant_api_tool(tool_name, arguments)
            trace.append({
                "tool_name": tool_name,
                "arguments": arguments,
                "receipt": receipt,
            })
        answer = self._compose_answer(content, trace, model_error=model_error)
        assistant_message = self.threads.append(
            thread_id,
            role="assistant",
            content=answer,
            admission={
                "provider_id": DETERMINISTIC_PROVIDER_ID,
                "runtime_mutation_admitted": False,
                "tool_receipts": [
                    item.get("receipt", {}).get("tool_receipt_root_hash72")
                    for item in trace
                ],
            },
        )
        tool_trace_root = hash72(
            "HHS_PRODUCTION_ASSISTANT_TOOL_TRACE_V1",
            {"thread_id": thread_id, "trace": trace},
        )
        result: Dict[str, Any] = {
            "schema": TURN_SCHEMA,
            "version": VERSION,
            "ok": True,
            "status": "ADMIT_DETERMINISTIC_HHS_ASSISTANT_TURN",
            "effective_mode": "DETERMINISTIC_HHS_CAPABILITY_ASSISTANT",
            "provider_id": DETERMINISTIC_PROVIDER_ID,
            "model_provider_attempted": bool(model_error),
            "model_provider_error": model_error,
            "thread_id": thread_id,
            "user_message": user_message,
            "assistant_message": assistant_message,
            "hhs_api_tools_enabled": True,
            "hhs_api_tool_call_count": len(trace),
            "hhs_api_tool_trace": trace,
            "hhs_api_tool_trace_root_hash72": tool_trace_root,
            "runtime_mutation_admitted": False,
            "model_output_is_canonical_without_runtime_admission": False,
            "thread": self.threads.get(thread_id),
        }
        result["turn_root_hash72"] = hash72(TURN_SCHEMA, result)
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
        model_health = await self._model_health()
        if model_health.get("online"):
            result = await self.model_service.send_message(
                thread_id,
                content=content,
                tools=tools,
                response_format=response_format,
            )
            if result.get("assistant_message", {}).get("content"):
                result["effective_mode"] = "GOVERNED_MODEL_AND_HHS_TOOLS"
                result["production_assistant_version"] = VERSION
                return result
            return await self._deterministic_turn(
                thread_id,
                content=content,
                existing_user_message=result.get("user_message"),
                model_error=str(result.get("error") or result.get("status")),
            )
        return await self._deterministic_turn(
            thread_id,
            content=content,
            model_error=str(model_health.get("error") or model_health.get("status")),
        )


DEFAULT_PRODUCTION_ASSISTANT_SERVICE = ProductionAssistantService()


if __name__ == "__main__":
    print(json.dumps(DEFAULT_PRODUCTION_ASSISTANT_SERVICE.status(), indent=2, default=str))
