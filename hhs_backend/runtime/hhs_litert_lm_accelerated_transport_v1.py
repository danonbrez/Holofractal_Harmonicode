"""Explicit LiteRT-LM accelerator selection for the HHS AI thread.

LiteRT-LM's OpenAI-compatible server selects the execution backend from the
request model parameter using the current v0.14 form:

    <registry-model-id>[,<backend>[,<max-engine-tokens>]]

HHS keeps the registry model identity separate from that transport-level
backend selector so `/v1/models` verification and Hash72 receipts continue to
refer to the canonical imported model ID.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, Iterable, List, Mapping, Optional

from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    LiteRTLMConfig,
    LiteRTLMTransport,
)

VERSION = "HHS_LITERT_LM_ACCELERATED_TRANSPORT_V1"
BACKEND_ENV = "HHS_LITERT_LM_BACKEND"
DEFAULT_BACKEND = "gpu"
VALID_BACKENDS = frozenset({"auto", "cpu", "gpu", "npu"})


def normalize_backend(value: Optional[str]) -> str:
    backend = str(value or DEFAULT_BACKEND).strip().lower()
    if backend not in VALID_BACKENDS:
        raise ValueError(
            f"unsupported LiteRT-LM backend {backend!r}; "
            f"expected one of {sorted(VALID_BACKENDS)}"
        )
    return backend


def backend_from_env() -> str:
    return normalize_backend(os.getenv(BACKEND_ENV, DEFAULT_BACKEND))


def compose_request_model_id(model_id: str, backend: str) -> str:
    registry_id = str(model_id).strip()
    if not registry_id:
        raise ValueError("LiteRT-LM registry model ID must not be empty")
    normalized = normalize_backend(backend)
    return registry_id if normalized == "auto" else f"{registry_id},{normalized}"


class LiteRTLMAcceleratedTransport(LiteRTLMTransport):
    """OpenAI-compatible transport with an explicit execution backend."""

    def __init__(
        self,
        config: LiteRTLMConfig,
        *,
        backend: Optional[str] = None,
    ):
        super().__init__(config)
        self.backend = normalize_backend(backend or backend_from_env())
        self.request_model_id = compose_request_model_id(
            config.model_id,
            self.backend,
        )

    async def chat_completion(
        self,
        *,
        messages: Iterable[Mapping[str, Any]],
        tools: Optional[List[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.request_model_id,
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
            self._request_sync,
            "POST",
            "/chat/completions",
            payload,
        )
