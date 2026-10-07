#!/usr/bin/env python3
"""Fail-closed production assistant backend closure verification.

This validation runs the real production assistant router and
ProductionAssistantService against the repository-native language transport.
It intentionally excludes optional provider fallback from the admitted path so
an exact-memory turn proves the native production route can complete without
external provider health or causal generation.
"""
from __future__ import annotations

import asyncio
import json
import os
from typing import Any

os.environ.setdefault("HHS_LITERT_LM_PROVIDER_MODE", "native")
os.environ.setdefault("HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC", "0")
os.environ.setdefault("HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS", "3")

import httpx
from fastapi import FastAPI

from hhs_backend.api import litert_lm_assistant_routes as assistant_routes
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import LiteRTLMConfig
from hhs_backend.runtime.hhs_litert_lm_hhs_api_assistant_v1 import HHSAPIAssistantService
from hhs_backend.runtime.hhs_native_litert_lm_provider_v1 import (
    HHSNativeLiteRTLMTransport,
    MODEL_ID as NATIVE_MODEL_ID,
)
from hhs_backend.runtime.hhs_production_assistant_v1 import ProductionAssistantService


TOKEN = "HHS-PRODUCTION-BACKEND-CLOSURE-7249"
TURN_TIMEOUT_SECONDS = 20.0


class ForbiddenFallback:
    """Optional provider sentinel: native-first closure must never touch it."""

    provider_id = "provider:hhs.production_closure.forbidden_fallback"

    def __init__(self) -> None:
        self.threads: Any = None
        self.health_calls = 0
        self.send_calls = 0
        self.config = LiteRTLMConfig(model_id="forbidden-fallback")

    async def health(self) -> dict[str, Any]:
        self.health_calls += 1
        raise AssertionError("optional fallback health was touched on native-first closure")

    async def send_message(self, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        self.send_calls += 1
        raise AssertionError("optional fallback handled a native-first closure turn")

    def status(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "model_id": self.config.model_id,
            "status": "FORBIDDEN_ON_NATIVE_FIRST_CLOSURE",
        }


async def _post(
    client: httpx.AsyncClient,
    payload: dict[str, Any],
) -> dict[str, Any]:
    response = await asyncio.wait_for(
        client.post("/api/assistant/chat", json=payload),
        timeout=TURN_TIMEOUT_SECONDS,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"assistant closure HTTP {response.status_code}: {response.text[:2000]}"
        )
    body = response.json()
    if body.get("ok") is not True:
        raise RuntimeError(f"assistant closure returned non-ok payload: {body}")
    return body


async def verify() -> dict[str, Any]:
    threads_config = LiteRTLMConfig(
        base_url="hhs-native://local/v1",
        model_id=NATIVE_MODEL_ID,
        timeout_seconds=TURN_TIMEOUT_SECONDS,
        temperature=0.0,
        top_p=1.0,
        top_k=1,
        reasoning_effort="bounded",
        system_instruction="HHS_ASSISTANT_MODE=BOTH.",
    )
    native = HHSAPIAssistantService(
        config=threads_config,
        transport=HHSNativeLiteRTLMTransport(require_word2vec=False),
    )
    forbidden = ForbiddenFallback()
    service = ProductionAssistantService(
        native_service=native,
        pass153_service=forbidden,
    )
    if not service.native_first:
        raise RuntimeError("production closure did not select native-first routing")

    assistant_routes._SERVICE = service
    app = FastAPI()
    app.include_router(assistant_routes.router)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://hhs-production-closure",
        timeout=TURN_TIMEOUT_SECONDS,
    ) as client:
        first = await _post(
            client,
            {
                "project_id": "project:production-backend-closure",
                "title": "Production Backend Closure",
                "content": (
                    f"Remember this exact token for my next message: {TOKEN}. "
                    "Reply briefly."
                ),
                "assistant_mode": "BOTH",
            },
        )
        thread_id = str(first.get("thread_id") or "")
        if not thread_id:
            raise RuntimeError(f"first assistant turn omitted thread_id: {first}")

        second = await _post(
            client,
            {
                "thread_id": thread_id,
                "project_id": "project:production-backend-closure",
                "title": "Production Backend Closure",
                "content": (
                    "What exact token did I ask you to remember in my previous "
                    "message? Reply with only the token."
                ),
                "assistant_mode": "BOTH",
            },
        )

    recalled = str((second.get("assistant_message") or {}).get("content") or "").strip()
    if recalled != TOKEN:
        raise RuntimeError(
            f"production backend exact-memory closure failed: expected={TOKEN!r} "
            f"actual={recalled!r}"
        )
    if second.get("thread_id") != thread_id:
        raise RuntimeError("production backend thread identity changed between turns")
    if forbidden.health_calls or forbidden.send_calls:
        raise RuntimeError(
            "optional fallback was touched during native-first closure: "
            f"health={forbidden.health_calls} send={forbidden.send_calls}"
        )

    stored = service.threads.get(thread_id) or {}
    if stored.get("message_count") != 4:
        raise RuntimeError(f"expected four persisted messages, got: {stored}")

    return {
        "schema": "HHS_PRODUCTION_BACKEND_CLOSURE_RECEIPT_V1",
        "ok": True,
        "native_first": True,
        "assistant_http_router_verified": True,
        "assistant_two_turn_exact_memory_verified": True,
        "thread_continuity_verified": True,
        "optional_fallback_untouched": True,
        "thread_id": thread_id,
        "message_count": stored.get("message_count"),
        "token": TOKEN,
    }


def main() -> None:
    receipt = asyncio.run(verify())
    print(json.dumps(receipt, sort_keys=True))
    print("HHS_PRODUCTION_BACKEND_CLOSURE_VERIFIED=1")


if __name__ == "__main__":
    main()
