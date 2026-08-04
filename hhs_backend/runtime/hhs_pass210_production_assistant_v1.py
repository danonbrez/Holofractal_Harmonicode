"""Pass 210 production assistant provider hierarchy.

Provider order:
1. Kimi K3 remote API as the primary governed agentic-swarm assistant;
2. local LiteRT-LM Gemma 4 as the installation-closed fallback;
3. repository-native HHS AGI as a durable backend observer and optimization
   proposal producer, never as a synthetic user-facing fallback.
"""
from __future__ import annotations

import asyncio
import os
import time
from dataclasses import replace
from typing import Any, Dict, List, Mapping, Optional, Sequence

from hhs_backend.runtime.hhs_kimi_k3_agentic_assistant_v1 import (
    DEFAULT_KIMI_K3_AGENTIC_ASSISTANT,
    KimiConversationThreadStore,
    KimiK3AgenticAssistantService,
    KimiK3AssistantConfig,
)
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import LiteRTLMConfig
from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import (
    HHSAPIAssistantService,
    HHS_API_SYSTEM_INSTRUCTION,
)
from hhs_backend.runtime.hhs_pass210_native_agi_optimizer_v1 import (
    DEFAULT_PASS210_NATIVE_AGI_OPTIMIZER,
    NativeAGIOptimizer,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "HHS_PASS_210_PRODUCTION_ASSISTANT_V1"
STATUS_SCHEMA = "HHS_PASS_210_PRODUCTION_ASSISTANT_STATUS_V1"
TURN_SCHEMA = "HHS_PASS_210_PRODUCTION_ASSISTANT_TURN_V1"
PROVIDER_ID = "provider:hhs.pass210.production_assistant"


class Pass210ProductionAssistantService:
    """Kimi-first, Gemma-fallback hierarchy with native AGI observation."""

    def __init__(
        self,
        primary_service: Optional[Any] = None,
        fallback_service: Optional[Any] = None,
        optimizer: Optional[Any] = None,
    ) -> None:
        if primary_service is None:
            kimi_config = KimiK3AssistantConfig.from_env()
            shared_store = KimiConversationThreadStore(
                kimi_config,
                provider_id="provider:hhs.pass210.shared_thread",
            )
            primary_service = KimiK3AgenticAssistantService(
                config=kimi_config,
                thread_store=shared_store,
            )
        else:
            shared_store = primary_service.threads

        if fallback_service is None:
            gemma_config = LiteRTLMConfig.from_env()
            replacements: Dict[str, Any] = {}
            if "HHS_LITERT_LM_BASE_URL" not in os.environ:
                replacements["base_url"] = "http://127.0.0.1:9379/v1"
            if "HHS_LITERT_LM_MODEL" not in os.environ:
                replacements["model_id"] = "gemma-4-E2B-it"
            if "HHS_LITERT_LM_SYSTEM_INSTRUCTION" not in os.environ:
                replacements["system_instruction"] = HHS_API_SYSTEM_INSTRUCTION
            if replacements:
                gemma_config = replace(gemma_config, **replacements)
            fallback_service = HHSAPIAssistantService(
                config=gemma_config,
                thread_store=shared_store,
            )
        else:
            fallback_service.threads = shared_store

        self.primary_service = primary_service
        self.fallback_service = fallback_service
        self.optimizer = optimizer or DEFAULT_PASS210_NATIVE_AGI_OPTIMIZER
        self.threads = shared_store
        self._health_cache: Dict[str, Dict[str, Any]] = {}
        self._health_cache_at: Dict[str, float] = {}
        self._health_ttl = max(
            1.0,
            float(os.getenv("HHS_ASSISTANT_HEALTH_CACHE_SECONDS", "15")),
        )
        self._health_timeout = max(
            0.5,
            float(os.getenv("HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS", "5")),
        )

    def create_thread(
        self,
        *,
        project_id: str = "project:default",
        title: str = "HHS Assistant",
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.primary_service.create_thread(
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

    @staticmethod
    def _ready(health: Mapping[str, Any]) -> bool:
        return bool(health.get("ok") and health.get("online"))

    @staticmethod
    def _completed(result: Mapping[str, Any]) -> bool:
        return bool(
            result.get("ok")
            and str((result.get("assistant_message") or {}).get("content") or "").strip()
        )

    def _observe(
        self,
        turn: Dict[str, Any],
        *,
        selected_provider_id: Optional[str],
        effective_mode: str,
        fallback_used: bool,
    ) -> Dict[str, Any]:
        try:
            observation = self.optimizer.enqueue_turn(
                turn,
                selected_provider_id=selected_provider_id,
                effective_mode=effective_mode,
                fallback_used=fallback_used,
            )
        except Exception as exc:
            observation = {
                "schema": "HHS_PASS_210_NATIVE_AGI_OBSERVATION_ENQUEUE_ERROR_V1",
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
                "native_agi_is_user_facing_provider": False,
                "runtime_mutation_admitted": False,
            }
        turn["native_agi_observation"] = observation
        turn["native_agi_observation_root_hash72"] = observation.get(
            "observation_root_hash72"
        )
        turn["native_agi_is_user_facing_provider"] = False
        turn["native_agi_optimization_is_asynchronous"] = True
        turn["optimization_proposal_requires_separate_admission"] = True
        turn["production_assistant_version"] = VERSION
        turn["effective_mode"] = effective_mode
        turn["fallback_used"] = bool(fallback_used)
        turn["selected_provider_id"] = selected_provider_id
        turn["turn_root_hash72"] = hash72(
            TURN_SCHEMA,
            {key: value for key, value in turn.items() if key != "turn_root_hash72"},
        )
        return turn

    def status(self) -> Dict[str, Any]:
        primary_status = dict(self.primary_service.status())
        fallback_status = dict(self.fallback_service.status())
        primary_health = self._health_cache.get("kimi", {})
        fallback_health = self._health_cache.get("gemma", {})
        primary_ready = self._ready(primary_health)
        fallback_ready = self._ready(fallback_health)
        selected = (
            primary_status.get("provider_id")
            if primary_ready
            else fallback_status.get("provider_id")
            if fallback_ready
            else None
        )
        effective_mode = (
            "KIMI_K3_AGENTIC_SWARM_API"
            if selected == primary_status.get("provider_id")
            else "GEMMA4_LITERT_LM_FALLBACK"
            if selected == fallback_status.get("provider_id")
            else "UNAVAILABLE"
        )
        status: Dict[str, Any] = {
            "schema": STATUS_SCHEMA,
            "version": VERSION,
            "ok": bool(selected),
            "online": bool(selected),
            "status": (
                "HHS_PASS_210_PRODUCTION_ASSISTANT_READY"
                if selected
                else "HHS_PASS_210_PRODUCTION_ASSISTANT_PROVIDER_UNAVAILABLE"
            ),
            "provider_id": PROVIDER_ID,
            "selected_provider_id": selected,
            "effective_mode": effective_mode,
            "provider_hierarchy": [
                primary_status.get("provider_id"),
                fallback_status.get("provider_id"),
            ],
            "primary_kimi_k3": {
                "status": primary_status,
                "health": primary_health,
                "ready": primary_ready,
            },
            "fallback_gemma4": {
                "status": fallback_status,
                "health": fallback_health,
                "ready": fallback_ready,
            },
            "native_hhs_optimizer": self.optimizer.status(),
            "native_agi_is_user_facing_provider": False,
            "native_agi_is_backend_learning_agent": True,
            "same_template_response_enabled": False,
            "runtime_mutation_admitted": False,
            "public_interface_mode": "PRODUCTION",
        }
        status["status_root_hash72"] = hash72(STATUS_SCHEMA, status)
        return status

    async def health(self) -> Dict[str, Any]:
        primary_health, fallback_health = await asyncio.gather(
            self._provider_health("kimi", self.primary_service, force=True),
            self._provider_health("gemma", self.fallback_service, force=True),
        )
        status = self.status()
        status["primary_kimi_k3"]["health"] = primary_health
        status["primary_kimi_k3"]["ready"] = self._ready(primary_health)
        status["fallback_gemma4"]["health"] = fallback_health
        status["fallback_gemma4"]["ready"] = self._ready(fallback_health)
        if status["primary_kimi_k3"]["ready"]:
            status["ok"] = True
            status["online"] = True
            status["selected_provider_id"] = self.primary_service.provider_id
            status["effective_mode"] = "KIMI_K3_AGENTIC_SWARM_API"
            status["status"] = "HHS_PASS_210_PRODUCTION_ASSISTANT_READY"
        elif status["fallback_gemma4"]["ready"]:
            status["ok"] = True
            status["online"] = True
            status["selected_provider_id"] = self.fallback_service.provider_id
            status["effective_mode"] = "GEMMA4_LITERT_LM_FALLBACK"
            status["status"] = "HHS_PASS_210_PRODUCTION_ASSISTANT_READY"
        else:
            status["ok"] = False
            status["online"] = False
            status["selected_provider_id"] = None
            status["effective_mode"] = "UNAVAILABLE"
            status["status"] = "HHS_PASS_210_PRODUCTION_ASSISTANT_PROVIDER_UNAVAILABLE"
        status["status_root_hash72"] = hash72(
            STATUS_SCHEMA,
            {key: value for key, value in status.items() if key != "status_root_hash72"},
        )
        return status

    def _unavailable_turn(
        self,
        thread_id: str,
        *,
        user_message: Mapping[str, Any],
        primary_health: Mapping[str, Any],
        fallback_health: Mapping[str, Any],
        primary_result: Optional[Mapping[str, Any]] = None,
        fallback_result: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "schema": TURN_SCHEMA,
            "version": VERSION,
            "ok": False,
            "status": "REJECT_ASSISTANT_TURN_WITHOUT_READY_PROVIDER",
            "error": (
                "No user-facing language provider is ready. Configure Kimi K3 with "
                "MOONSHOT_API_KEY or restore the local LiteRT-LM Gemma 4 service. "
                "The repository-native AGI is an optimization observer and does not "
                "fabricate a substitute conversational response."
            ),
            "thread_id": thread_id,
            "user_message": dict(user_message),
            "assistant_message": None,
            "provider_hierarchy": [
                getattr(self.primary_service, "provider_id", None),
                getattr(self.fallback_service, "provider_id", None),
            ],
            "primary_health": dict(primary_health),
            "fallback_health": dict(fallback_health),
            "primary_result": dict(primary_result or {}),
            "fallback_result": dict(fallback_result or {}),
            "runtime_mutation_admitted": False,
            "model_output_is_canonical_without_runtime_admission": False,
            "thread": self.threads.get(thread_id),
        }
        return self._observe(
            result,
            selected_provider_id=None,
            effective_mode="UNAVAILABLE",
            fallback_used=bool(primary_result),
        )

    async def send_message(
        self,
        thread_id: str,
        *,
        content: str,
        tools: Optional[Sequence[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.threads.get(thread_id):
            raise KeyError(thread_id)

        primary_health, fallback_health = await asyncio.gather(
            self._provider_health("kimi", self.primary_service),
            self._provider_health("gemma", self.fallback_service),
        )
        primary_ready = self._ready(primary_health)
        fallback_ready = self._ready(fallback_health)

        if primary_ready:
            primary_result = await self.primary_service.send_message(
                thread_id,
                content=content,
                tools=list(tools or []) or None,
                response_format=response_format,
            )
            if self._completed(primary_result):
                return self._observe(
                    dict(primary_result),
                    selected_provider_id=self.primary_service.provider_id,
                    effective_mode="KIMI_K3_AGENTIC_SWARM_API",
                    fallback_used=False,
                )
            user_message = primary_result.get("user_message")
            if fallback_ready and isinstance(user_message, Mapping):
                fallback_result = await self.fallback_service.continue_message(
                    thread_id,
                    user_message=user_message,
                    tools=list(tools or []) or None,
                    response_format=response_format,
                )
                if self._completed(fallback_result):
                    result = dict(fallback_result)
                    result["failed_primary_result"] = dict(primary_result)
                    return self._observe(
                        result,
                        selected_provider_id=self.fallback_service.provider_id,
                        effective_mode="GEMMA4_LITERT_LM_FALLBACK",
                        fallback_used=True,
                    )
                return self._unavailable_turn(
                    thread_id,
                    user_message=user_message,
                    primary_health=primary_health,
                    fallback_health=fallback_health,
                    primary_result=primary_result,
                    fallback_result=fallback_result,
                )
            if isinstance(user_message, Mapping):
                return self._unavailable_turn(
                    thread_id,
                    user_message=user_message,
                    primary_health=primary_health,
                    fallback_health=fallback_health,
                    primary_result=primary_result,
                )

        if fallback_ready:
            fallback_result = await self.fallback_service.send_message(
                thread_id,
                content=content,
                tools=list(tools or []) or None,
                response_format=response_format,
            )
            if self._completed(fallback_result):
                return self._observe(
                    dict(fallback_result),
                    selected_provider_id=self.fallback_service.provider_id,
                    effective_mode="GEMMA4_LITERT_LM_FALLBACK",
                    fallback_used=True,
                )
            user_message = fallback_result.get("user_message")
            if isinstance(user_message, Mapping):
                return self._unavailable_turn(
                    thread_id,
                    user_message=user_message,
                    primary_health=primary_health,
                    fallback_health=fallback_health,
                    fallback_result=fallback_result,
                )

        user_message = self.threads.append(
            thread_id,
            role="user",
            content=content,
        )
        return self._unavailable_turn(
            thread_id,
            user_message=user_message,
            primary_health=primary_health,
            fallback_health=fallback_health,
        )


DEFAULT_PASS210_PRODUCTION_ASSISTANT = Pass210ProductionAssistantService(
    primary_service=DEFAULT_KIMI_K3_AGENTIC_ASSISTANT,
    optimizer=DEFAULT_PASS210_NATIVE_AGI_OPTIMIZER,
)
