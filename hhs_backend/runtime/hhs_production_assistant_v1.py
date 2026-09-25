"""Production HHS unified chatbot provider fabric.

Provider order:
1. all registered LiteRT-LM text models, ordered by the declared primary/priority
   configuration while sharing one witnessed conversation thread;
2. the repository-native HHS text provider, including its causal model when
   loaded and its exact semantic/Pass 166 memory path as fallback;
3. registered Pass 153 open-model generation through the same assistant receipt
   and result-ingress pipeline;
4. a closed provider-unavailable turn when no callable member is ready.

The routing layer does not widen VM81, Hash72, Hash216, or Lane 5 authority.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import replace
from typing import Any, Dict, List, Mapping, Optional

from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    ASSISTANT_MODES,
    DEFAULT_ASSISTANT_MODE,
    LiteRTLMConfig,
)
from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import (
    DEFAULT_HHS_API_ASSISTANT_SERVICE,
    HHSAPIAssistantService,
)
from hhs_backend.runtime.hhs_native_litert_lm_provider_v1 import (
    HHSNativeLiteRTLMTransport,
    MODEL_ID as NATIVE_MODEL_ID,
    PROVIDER_ID as NATIVE_PROVIDER_ID,
)
from hhs_backend.runtime.hhs_pass153_assistant_transport_v1 import (
    Pass153AssistantTransport,
)
from hhs_backend.runtime.hhs_unified_language_model_fabric_v1 import (
    build_unified_language_model_fabric,
    ordered_litert_model_ids,
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
        pass153_service: Any = None,
        model_service_factory: Any = None,
    ) -> None:
        self.model_service = model_service or DEFAULT_HHS_API_ASSISTANT_SERVICE
        self.threads = self.model_service.threads
        self._model_service_factory = model_service_factory
        self._litert_services: Dict[str, Any] = {
            str(self.model_service.config.model_id): self.model_service,
        }

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
                    "You are the native HHS natural-language assistant. Support ordinary "
                    "conversational prompt-response generation as well as governed application "
                    "development according to the selected assistant mode. Use bounded reasoning "
                    "and active Word2Vec memory. Use governed HHS tools only when the selected "
                    "mode permits them. Preserve source identity and never claim canonical "
                    "mutation without admitted runtime evidence."
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

        if pass153_service is None:
            try:
                pass153_transport = Pass153AssistantTransport()
                pass153_config = replace(
                    self.model_service.config,
                    base_url="hhs-pass153://local/v1",
                    model_id=pass153_transport.model_id,
                    temperature=0.0,
                    top_p=1.0,
                    top_k=1,
                    reasoning_effort="bounded",
                )
                pass153_service = HHSAPIAssistantService(
                    config=pass153_config,
                    transport=pass153_transport,
                    thread_store=self.threads,
                )
            except Exception:
                pass153_service = None
        elif pass153_service is not None:
            pass153_service.threads = self.threads
        self.pass153_service = pass153_service

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

    @staticmethod
    def _registered_litert_model_ids(health: Mapping[str, Any]) -> List[str]:
        direct = [
            str(value)
            for value in (health.get("registered_model_ids") or [])
            if str(value or "").strip()
        ]
        if direct:
            return sorted(dict.fromkeys(direct))
        models = dict(health.get("models") or {})
        return sorted({
            str(item.get("id"))
            for item in (models.get("data") or [])
            if isinstance(item, Mapping) and item.get("id")
        })

    def _litert_service(self, model_id: str) -> Any:
        model_id = str(model_id)
        existing = self._litert_services.get(model_id)
        if existing is not None:
            return existing
        config = replace(self.model_service.config, model_id=model_id)
        if self._model_service_factory is not None:
            service = self._model_service_factory(model_id, config, self.threads)
        else:
            service = HHSAPIAssistantService(
                config=config,
                thread_store=self.threads,
            )
        service.threads = self.threads
        self._litert_services[model_id] = service
        return service

    def _ordered_litert_services(
        self,
        health: Mapping[str, Any],
    ) -> List[tuple[str, Any]]:
        registered = self._registered_litert_model_ids(health)
        order = ordered_litert_model_ids(
            registered,
            configured_model_id=str(self.model_service.config.model_id),
        )
        return [(model_id, self._litert_service(model_id)) for model_id in order]

    def _pass153_models(self) -> List[Dict[str, Any]]:
        service = self.pass153_service
        if service is None:
            return []
        transport = getattr(service, "transport", None)
        inner = getattr(transport, "inner", transport)
        environment = getattr(inner, "environment", None)
        if environment is None:
            return []
        try:
            return [dict(item) for item in environment.status().get("models") or []]
        except Exception:
            return []

    @staticmethod
    def _pass166_status() -> Dict[str, Any]:
        try:
            from hhs_runtime.pass166.service import DEFAULT_WORD2VEC_SERVICE
            return dict(DEFAULT_WORD2VEC_SERVICE.status())
        except Exception as exc:
            return {
                "offline_ready": False,
                "active_model_id": None,
                "error": f"{type(exc).__name__}: {exc}",
            }

    def unified_model_fabric(self) -> Dict[str, Any]:
        litert_health = self._health_cache.get("gemma", {})
        registered = self._registered_litert_model_ids(litert_health)
        return build_unified_language_model_fabric(
            configured_model_id=str(self.model_service.config.model_id),
            registered_model_ids=registered,
            native_installation=self._native_installation_status(),
            native_health=self._health_cache.get("native", {}),
            pass153_models=self._pass153_models(),
            pass166_status=self._pass166_status(),
        )

    def status(self) -> Dict[str, Any]:
        litert_status = dict(self.model_service.status())
        native_status = dict(self.native_service.status())
        pass153_status = (
            dict(self.pass153_service.status())
            if self.pass153_service is not None
            else {}
        )
        litert_health = self._health_cache.get("gemma", {})
        native_health = self._health_cache.get("native", {})
        pass153_health = self._health_cache.get("pass153", {})
        registered = self._registered_litert_model_ids(litert_health)
        litert_ready = bool(registered)
        native_ready = bool(native_health.get("online") and native_health.get("ok"))
        pass153_ready = bool(
            self.pass153_service is not None
            and pass153_health.get("online")
            and pass153_health.get("ok")
        )
        fabric = self.unified_model_fabric()
        selected = (
            litert_status.get("provider_id")
            if litert_ready
            else native_status.get("provider_id")
            if native_ready
            else pass153_status.get("provider_id")
            if pass153_ready
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
            "selected_model_id": fabric.get("primary_model_id"),
            "effective_mode": (
                "UNIFIED_LITERT_MODEL_FABRIC"
                if litert_ready
                else "HHS_NATIVE_LITERT_COMPATIBLE"
                if native_ready
                else "HHS_PASS153_OPEN_MODEL"
                if pass153_ready
                else "UNAVAILABLE"
            ),
            "provider_hierarchy": [
                litert_status.get("provider_id"),
                native_status.get("provider_id"),
                pass153_status.get("provider_id") if pass153_status else None,
            ],
            "gemma": {
                "status": litert_status,
                "health": litert_health,
                "ready": litert_ready,
                "registered_model_ids": registered,
            },
            "native_hhs": {
                "status": native_status,
                "health": native_health,
                "installation": self._native_installation_status(),
                "ready": native_ready,
            },
            "pass153": {
                "status": pass153_status,
                "health": pass153_health,
                "ready": pass153_ready,
                "models": self._pass153_models(),
            },
            "unified_model_fabric": fabric,
            "same_template_response_enabled": False,
            "repository_search_is_provider": False,
            "assistant_modes": list(ASSISTANT_MODES),
            "default_assistant_mode": DEFAULT_ASSISTANT_MODE,
            "general_chat_prompt_response_supported": True,
            "agentic_application_development_supported": True,
            "lane5_tooling_enabled": True,
            "runtime_mutation_admitted": False,
            "public_interface_mode": "PRODUCTION",
        }
        status["status_root_hash72"] = hash72(
            STATUS_SCHEMA,
            {key: value for key, value in status.items() if key != "status_root_hash72"},
        )
        return status

    async def health(self) -> Dict[str, Any]:
        tasks = [
            self._provider_health("gemma", self.model_service, force=True),
            self._provider_health("native", self.native_service, force=True),
        ]
        if self.pass153_service is not None:
            tasks.append(
                self._provider_health("pass153", self.pass153_service, force=True)
            )
        results = await asyncio.gather(*tasks)
        gemma_health = results[0]
        native_health = results[1]
        pass153_health = results[2] if len(results) > 2 else {
            "ok": False,
            "online": False,
            "status": "PASS153_PROVIDER_UNAVAILABLE",
        }
        self._health_cache["gemma"] = dict(gemma_health)
        self._health_cache["native"] = dict(native_health)
        self._health_cache["pass153"] = dict(pass153_health)
        self._health_cache_at["gemma"] = time.monotonic()
        self._health_cache_at["native"] = time.monotonic()
        self._health_cache_at["pass153"] = time.monotonic()
        return self.status()

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
                "No unified chatbot language member is ready. At least one registered "
                "LiteRT-LM model, the native HHS language provider, or a registered "
                "Pass 153 open model must be callable."
            ),
            "thread_id": thread_id,
            "user_message": dict(user_message),
            "assistant_message": None,
            "provider_hierarchy": [
                getattr(self.model_service, "provider_id", None),
                getattr(self.native_service, "provider_id", None),
                (
                    getattr(self.pass153_service, "provider_id", None)
                    if self.pass153_service is not None
                    else None
                ),
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
        custom_system_instruction: Optional[str] = None,
        assistant_mode: Optional[str] = None,
        user_context: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.threads.get(thread_id):
            raise KeyError(thread_id)

        litert_health = await self._provider_health("gemma", self.model_service)
        native_health = await self._provider_health("native", self.native_service)
        pass153_health = (
            await self._provider_health("pass153", self.pass153_service)
            if self.pass153_service is not None
            else {"ok": False, "online": False}
        )
        native_ready = bool(native_health.get("ok") and native_health.get("online"))
        pass153_ready = bool(
            self.pass153_service is not None
            and pass153_health.get("ok")
            and pass153_health.get("online")
        )

        user_message: Optional[Mapping[str, Any]] = None
        failed_litert_results: List[Dict[str, Any]] = []

        for model_id, service in self._ordered_litert_services(litert_health):
            if user_message is None:
                result = await service.send_message(
                    thread_id,
                    content=content,
                    tools=tools,
                    response_format=response_format,
                    custom_system_instruction=custom_system_instruction,
                    assistant_mode=assistant_mode,
                    user_context=user_context,
                )
            else:
                result = await service.continue_message(
                    thread_id,
                    user_message=user_message,
                    tools=tools,
                    response_format=response_format,
                    custom_system_instruction=custom_system_instruction,
                    assistant_mode=assistant_mode,
                    user_context=user_context,
                )
            if self._completed(result):
                result["effective_mode"] = "UNIFIED_LITERT_MODEL_FABRIC"
                result["selected_model_id"] = model_id
                result["production_assistant_version"] = VERSION
                result["fallback_used"] = bool(failed_litert_results)
                result["failed_provider_results"] = failed_litert_results
                result["unified_model_fabric"] = self.unified_model_fabric()
                return result
            failed_litert_results.append(dict(result))
            candidate_user = result.get("user_message")
            if isinstance(candidate_user, Mapping):
                user_message = candidate_user

        native_result: Optional[Mapping[str, Any]] = None
        if native_ready:
            if user_message is None:
                native_result = await self.native_service.send_message(
                    thread_id,
                    content=content,
                    tools=tools,
                    response_format=response_format,
                    custom_system_instruction=custom_system_instruction,
                    assistant_mode=assistant_mode,
                    user_context=user_context,
                )
            else:
                native_result = await self.native_service.continue_message(
                    thread_id,
                    user_message=user_message,
                    tools=tools,
                    response_format=response_format,
                    custom_system_instruction=custom_system_instruction,
                    assistant_mode=assistant_mode,
                    user_context=user_context,
                )
            if self._completed(native_result):
                native_result["effective_mode"] = "HHS_NATIVE_LITERT_COMPATIBLE"
                native_result["selected_model_id"] = NATIVE_MODEL_ID
                native_result["production_assistant_version"] = VERSION
                native_result["fallback_used"] = True
                native_result["failed_provider_results"] = failed_litert_results
                native_result["unified_model_fabric"] = self.unified_model_fabric()
                return native_result
            candidate_user = native_result.get("user_message")
            if isinstance(candidate_user, Mapping):
                user_message = candidate_user

        pass153_result: Optional[Mapping[str, Any]] = None
        if pass153_ready and self.pass153_service is not None:
            if user_message is None:
                pass153_result = await self.pass153_service.send_message(
                    thread_id,
                    content=content,
                    tools=tools,
                    response_format=response_format,
                    custom_system_instruction=custom_system_instruction,
                    assistant_mode=assistant_mode,
                    user_context=user_context,
                )
            else:
                pass153_result = await self.pass153_service.continue_message(
                    thread_id,
                    user_message=user_message,
                    tools=tools,
                    response_format=response_format,
                    custom_system_instruction=custom_system_instruction,
                    assistant_mode=assistant_mode,
                    user_context=user_context,
                )
            if self._completed(pass153_result):
                pass153_result["effective_mode"] = "HHS_PASS153_OPEN_MODEL"
                pass153_result["selected_model_id"] = self.pass153_service.config.model_id
                pass153_result["production_assistant_version"] = VERSION
                pass153_result["fallback_used"] = True
                pass153_result["failed_provider_results"] = [
                    *failed_litert_results,
                    *([dict(native_result)] if isinstance(native_result, Mapping) else []),
                ]
                pass153_result["unified_model_fabric"] = self.unified_model_fabric()
                return pass153_result
            candidate_user = pass153_result.get("user_message")
            if isinstance(candidate_user, Mapping):
                user_message = candidate_user

        if user_message is None:
            user_message = self.threads.append(
                thread_id,
                role="user",
                content=content,
            )
        return self._unavailable_turn(
            thread_id,
            user_message=user_message,
            gemma_health=litert_health,
            native_health=native_health,
            gemma_result=failed_litert_results[-1] if failed_litert_results else None,
            native_result=(
                native_result
                if isinstance(native_result, Mapping)
                else pass153_result
                if isinstance(pass153_result, Mapping)
                else None
            ),
        )


DEFAULT_PRODUCTION_ASSISTANT_SERVICE = ProductionAssistantService()


if __name__ == "__main__":
    print(json.dumps(DEFAULT_PRODUCTION_ASSISTANT_SERVICE.status(), indent=2, default=str))
