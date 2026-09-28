"""OpenAI-compatible transport over the governed Pass 153 model environment.

This adapter lets Pass 153 registered text-generation models participate in the
same HHS assistant thread, provider-receipt, result-ingress, and tool membrane
used by LiteRT-LM and the repository-native provider.  It does not grant model
output canonical authority.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Iterable, List, Mapping, Optional

from hhs_runtime.pass153.environment import AgentEnvironment, build_default_environment

VERSION = "HHS_PASS153_ASSISTANT_TRANSPORT_V1"
PROVIDER_ID = "provider:hhs.pass153.open_model"
REQUESTED_OPERATION = "pass153.chat_completion"


class Pass153AssistantTransport:
    provider_id = PROVIDER_ID
    requested_operation = REQUESTED_OPERATION
    backend = "pass153"

    def __init__(
        self,
        *,
        environment: Optional[AgentEnvironment] = None,
        model_id: Optional[str] = None,
    ) -> None:
        self.environment = environment or build_default_environment()
        registered = sorted(self.environment.models)
        if not registered:
            raise RuntimeError("Pass 153 has no registered text-generation model")
        self.model_id = str(model_id or registered[0])
        if self.model_id not in self.environment.models:
            raise RuntimeError(f"Pass 153 model is not registered: {self.model_id}")
        self.request_model_id = self.model_id

    async def list_models(self) -> Dict[str, Any]:
        return {
            "object": "list",
            "data": [
                {
                    "id": spec.model_id,
                    "object": "model",
                    "created": 0,
                    "owned_by": "hhs-pass153",
                    "backend": spec.backend,
                    "source": spec.source,
                    "capabilities": list(spec.capabilities),
                    "model_index": spec.model_index,
                }
                for spec, _backend in sorted(
                    self.environment.models.values(),
                    key=lambda pair: pair[0].model_id,
                )
            ],
        }

    @staticmethod
    def _render_messages(messages: Iterable[Mapping[str, Any]]) -> str:
        rendered: List[str] = []
        for message in messages:
            role = str(message.get("role") or "").strip().lower()
            if role not in {"system", "user", "assistant", "tool"}:
                continue
            content = str(message.get("content") or "").strip()
            if not content:
                continue
            rendered.append(f"{role.upper()}: {content}")
        rendered.append("ASSISTANT:")
        return "\n\n".join(rendered)

    async def chat_completion(
        self,
        *,
        messages: Iterable[Mapping[str, Any]],
        tools: Optional[List[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        del tools, response_format
        spec, backend = self.environment.models[self.model_id]
        prompt = self._render_messages(messages)
        response = backend.generate(prompt, max_tokens=128)
        if not isinstance(response, str) or not response.strip():
            raise RuntimeError("Pass 153 model returned empty assistant text")
        text = response.strip()
        return {
            "id": f"chatcmpl-pass153-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": spec.model_id,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(text.split()),
                "total_tokens": len(prompt.split()) + len(text.split()),
            },
            "hhs_pass153": {
                "version": VERSION,
                "backend": spec.backend,
                "model_index": spec.model_index,
                "model_output_authoritative": False,
                "runtime_mutation_admitted": False,
            },
        }


__all__ = [
    "PROVIDER_ID",
    "REQUESTED_OPERATION",
    "VERSION",
    "Pass153AssistantTransport",
]
