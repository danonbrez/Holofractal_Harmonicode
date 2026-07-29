"""Production HHS assistant provider hierarchy.

Provider order:
1. configured Gemma model through LiteRT-LM, only when the configured alias is
   present in the provider model registry;
2. repository-native HHS local-text provider through the same LiteRT-compatible
   conversation, tool, policy, receipt, and result-ingress pipeline, only when
   Pass 148/151 and an active offline-ready Pass 166 Word2Vec model are ready;
3. a closed provider-unavailable turn. No canned or simulated assistant answer
   is generated when neither provider is installation-closed.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any, Dict, List, Mapping, Optional

from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import LiteRTLMConfig
from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import (
    DEFAULT_HHS_API_ASSISTANT_SERVICE,
    HHSAPIAssistantService,
)
from hhs_backend.runtime.hhs_native_litert_lm_provider_v1 import (
    HHSNativeLiteRTLMTransport,
    MODEL_ID as NATIVE_MODEL_ID,
    PROVIDER_ID as NATIVE_PROVIDER_ID,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "HHS_PRODUCTION_ASSISTANT_V2"
STATUS_SCHEMA = "HHS_PRODUCTION_ASSISTANT_STATUS_V2"
TURN_SCHEMA = "HHS_PRODUCTION_ASSISTANT_TURN_V2"
PROVIDER_ID = "provider:hhs.production_assistant"


class ProductionAssistantService:
    """Production provider hierarchy with installation-closed failover."""

    def __init__(
        self,
        model_service: Any = None,
        native_service: Any = None,
    ) -> None:
        self.model_service = model_service or DEFAULT_HHS_API_ASSISTANT_SERVICE
        self.threads = self.model_service.threads
        if native_service is None:
            native_transport = HHSNativeLiteRTLMTransport()
            native_config = LiteRTLMConfig(
                base_url="hhs-native://local/v1",
                model_id=NATIVE_MODEL_ID,
                timeout_seconds=30.0,
                max_threads=self.model_service.config.max_threads,
                max_messages_per_thread=self.model_service.config.max_messages_per_thread,
                max_output_tokens=self.model_service.config.max_output_tokens,
                temperature=0.0,
                top_p=1.0,
                top_k=1,
                seed=72,
                reasoning_effort="bounded",
                system_instruction=(
                    "Use native HHS semantics, bounded reasoning, active Word2Vec memory, "
                    "and governed read-only HHS tools. Preserve source identity and never "
                    "claim canonical mutation without admitted runtime evidence."
                ),
            )
            native_service = HHSAPIAssistantService(
                config=native_config,
                transport=native_transport,
                thread_store=self.threads,
            )
        else:
            native_service.threads = self.threads
        self.native_service = native_service
        self._health_cache: Dict[str, Dict[str, Any]] = {}
        self._health_cache_at: Dict[str, float] = {}
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

    async def _provider_health(
        self,
        name: str,
        service: Any,
        *,
        force: bool = False,
    ) -> Dict[str, Any]:
        now = time.monotonic()
        if (
            not force
            and name in self._health_cache
            and now - self._health_cache_at.get(name, 0.0) < self._health_ttl
        ):
            return dict(self._health_cache[name])
        try:
            health = await asyncio.wait_for(
                service.health(),
                timeout=self._health_timeout,
            )
        except Exception as exc:
            health = {
                "ok": False,
                "online": False,
                "status": "ASSISTANT_PROVIDER_HEALTH_ERROR",
                "provider_id": getattr(service, "provider_id", name),
                "error": f"{type(exc).__name__}: {exc}",
            }
        self._health_cache[name] = dict(health)
        self._health_cache_at[name] = now
        return dict(health)

    def _native_installation_status(self) -> Dict[str, Any]:
        transport = getattr(self.native_service, "transport", None)
        inner = getattr(transport, "inner", transport)
        installation_status = getattr(inner, "installation_status", None)
        if callable(installation_status):
            try:
                return dict(installation_status())
            except Exception as exc:
                return {
                    "ready": False,
                    "provider_id": NATIVE_PROVIDER_ID,
                    "model_id": NATIVE_MODEL_ID,
                    "error": f"{type(exc).__name__}: {exc}",
                }
        return {
            "ready": False,
            "provider_id": NATIVE_PROVIDER_ID,
            "model_id": NATIVE_MODEL_ID,
            "error": "native provider does not expose installation status",
        }

    def status(self) -> Dict[str, Any]:
        gemma_status = dict(self.model_service.status())
        native_status = dict(self.native_service.status())
        gemma_health = self._health_cache.get("gemma", {})
        native_health = self._health_cache.get("native", {})
        gemma_ready = bool(gemma_health.get("online") and gemma_health.get("ok"))
        native_ready = bool(native_health.get("online") and native_health.get("ok"))
        selected = (
            gemma_status.get("provider_id")
            if gemma_ready
            else native_status.get("provider_id")
            if native_ready
            else None
        )
        status: Dict[str, Any] = {
            "schema": STATUS_SCHEMA,
            "version": VERSION,
            "ok": bool(selected),
            "online": bool(selected),
            "status": (
                "HHS_PRODUCTION_ASSISTANT_READY"
                if selected
                else "HHS_PRODUCTION_ASSISTANT_PROVIDER_UNAVAILABLE"
            ),
            "provider_id": PROVIDER_ID,
            "selected_provider_id": selected,
            "effective_mode": (
                "GEMMA4_LITERT_LM"
                if selected == gemma_status.get("provider_id")
                else "HHS_NATIVE_LITERT_COMPATIBLE"
                if selected == native_status.get("provider_id")
                else "UNAVAILABLE"
            ),
            "provider_hierarchy": [
                gemma_status.get("provider_id"),
                native_status.get("provider_id"),
            ],
            "gemma": {
                "status": gemma_status,
                "health": gemma_health,
                "ready": gemma_ready,
            },
            "native_hhs": {
                "status": native_status,
                "health": native_health,
                "installation": self._native_installation_status(),
                "ready": native_ready,
            },
            "same_template_response_enabled": False,
            "repository_search_is_provider": False,
            "runtime_mutation_admitted": False,
            "public_interface_mode": "PRODUCTION",
        }
        status["status_root_hash72"] = hash72(
            STATUS_SCHEMA,
            {key: value for key, value in status.items() if key != "status_root_hash72"},
        )
        return status

    async def health(self) -> Dict[str, Any]:
        gemma_health, native_health = await asyncio.gather(
            self._provider_health("gemma", self.model_service, force=True),
            self._provider_health("native", self.native_service, force=True),
        )
        status = self.status()
        status["gemma"]["health"] = gemma_health
        status["gemma"]["ready"] = bool(
            gemma_health.get("ok") and gemma_health.get("online")
        )
        status["native_hhs"]["health"] = native_health
        status["native_hhs"]["ready"] = bool(
            native_health.get("ok") and native_health.get("online")
        )
        status["ok"] = bool(status["gemma"]["ready"] or status["native_hhs"]["ready"])
        status["online"] = status["ok"]
        if status["gemma"]["ready"]:
            status["selected_provider_id"] = self.model_service.provider_id
            status["effective_mode"] = "GEMMA4_LITERT_LM"
            status["status"] = "HHS_PRODUCTION_ASSISTANT_READY"
        elif status["native_hhs"]["ready"]:
            status["selected_provider_id"] = self.native_service.provider_id
            status["effective_mode"] = "HHS_NATIVE_LITERT_COMPATIBLE"
            status["status"] = "HHS_PRODUCTION_ASSISTANT_READY"
        else:
            status["selected_provider_id"] = None
            status["effective_mode"] = "UNAVAILABLE"
            status["status"] = "HHS_PRODUCTION_ASSISTANT_PROVIDER_UNAVAILABLE"
        status["status_root_hash72"] = hash72(
            STATUS_SCHEMA,
            {key: value for key, value in status.items() if key != "status_root_hash72"},
        )
        return status

    @staticmethod
    def _completed(result: Mapping[str, Any]) -> bool:
        return bool(
            result.get("ok")
            and str((result.get("assistant_message") or {}).get("content") or "").strip()
        )

    def _unavailable_turn(
        self,
        thread_id: str,
        *,
        user_message: Mapping[str, Any],
        gemma_health: Mapping[str, Any],
        native_health: Mapping[str, Any],
        gemma_result: Optional[Mapping[str, Any]] = None,
        native_result: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "schema": TURN_SCHEMA,
            "version": VERSION,
            "ok": False,
            "status": "REJECT_ASSISTANT_TURN_WITHOUT_READY_PROVIDER",
            "error": (
                "No production language provider is ready. The configured Gemma alias "
                "must be registered in LiteRT-LM, or the native HHS provider must have "
                "Pass 148/151 ready with an active offline-ready Pass 166 Word2Vec model."
            ),
            "thread_id": thread_id,
            "user_message": dict(user_message),
            "assistant_message": None,
            "provider_hierarchy": [
                getattr(self.model_service, "provider_id", None),
                getattr(self.native_service, "provider_id", None),
            ],
            "gemma_health": dict(gemma_health),
            "native_health": dict(native_health),
            "gemma_result": dict(gemma_result or {}),
            "native_result": dict(native_result or {}),
            "native_installation": self._native_installation_status(),
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

        gemma_health = await self._provider_health("gemma", self.model_service)
        native_health = await self._provider_health("native", self.native_service)
        gemma_ready = bool(gemma_health.get("ok") and gemma_health.get("online"))
        native_ready = bool(native_health.get("ok") and native_health.get("online"))

        if gemma_ready:
            gemma_result = await self.model_service.send_message(
                thread_id,
                content=content,
                tools=tools,
                response_format=response_format,
            )
            if self._completed(gemma_result):
                gemma_result["effective_mode"] = "GEMMA4_LITERT_LM"
                gemma_result["production_assistant_version"] = VERSION
                gemma_result["fallback_used"] = False
                return gemma_result

            user_message = gemma_result.get("user_message")
            if native_ready and isinstance(user_message, Mapping):
                native_result = await self.native_service.continue_message(
                    thread_id,
                    user_message=user_message,
                    tools=tools,
                    response_format=response_format,
                )
                if self._completed(native_result):
                    native_result["effective_mode"] = "HHS_NATIVE_LITERT_COMPATIBLE"
                    native_result["production_assistant_version"] = VERSION
                    native_result["fallback_used"] = True
                    native_result["failed_primary_result"] = gemma_result
                    return native_result
                return self._unavailable_turn(
                    thread_id,
                    user_message=user_message,
                    gemma_health=gemma_health,
                    native_health=native_health,
                    gemma_result=gemma_result,
                    native_result=native_result,
                )
            if isinstance(user_message, Mapping):
                return self._unavailable_turn(
                    thread_id,
                    user_message=user_message,
                    gemma_health=gemma_health,
                    native_health=native_health,
                    gemma_result=gemma_result,
                )

        if native_ready:
            native_result = await self.native_service.send_message(
                thread_id,
                content=content,
                tools=tools,
                response_format=response_format,
            )
            if self._completed(native_result):
                native_result["effective_mode"] = "HHS_NATIVE_LITERT_COMPATIBLE"
                native_result["production_assistant_version"] = VERSION
                native_result["fallback_used"] = True
                return native_result
            user_message = native_result.get("user_message")
            if isinstance(user_message, Mapping):
                return self._unavailable_turn(
                    thread_id,
                    user_message=user_message,
                    gemma_health=gemma_health,
                    native_health=native_health,
                    native_result=native_result,
                )

        user_message = self.threads.append(
            thread_id,
            role="user",
            content=content,
        )
        return self._unavailable_turn(
            thread_id,
            user_message=user_message,
            gemma_health=gemma_health,
            native_health=native_health,
        )


DEFAULT_PRODUCTION_ASSISTANT_SERVICE = ProductionAssistantService()


if __name__ == "__main__":
    print(json.dumps(DEFAULT_PRODUCTION_ASSISTANT_SERVICE.status(), indent=2, default=str))
