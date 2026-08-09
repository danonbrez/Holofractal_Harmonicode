"""Repository-native HHS language provider with a LiteRT-LM-compatible surface.

This provider is the operational fallback for the external/local Gemma provider.
It uses the existing HHS semantic membrane, bounded semantic reasoner, activated
Pass 166 Word2Vec language memory, and governed read-only HHS tools. It returns
OpenAI-compatible model and chat-completion envelopes so the existing assistant
thread, policy, receipt, and provider-result ingress paths remain unchanged.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
import uuid
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "HHS_NATIVE_LITERT_COMPATIBLE_LANGUAGE_PROVIDER_V1"
PROVIDER_ID = "provider:hhs.local.text"
MODEL_ID = "hhs-native-language-v1"
REQUESTED_OPERATION = "hhs_native_litert.chat_completion"

_EXPRESSION_MARKERS = (
    "==", "≠", "Δ", "Ω", "Θ", "Ψ", "Φ", "Γ", "Λ", ":=", "u^72", "u⁷²",
)
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{1,63}")


def _now_ms() -> int:
    return int(time.time() * 1000)


def _completion_id() -> str:
    return f"chatcmpl-hhs-native-{uuid.uuid4().hex}"


def _available_tool_names(tools: Optional[Sequence[Mapping[str, Any]]]) -> set[str]:
    names: set[str] = set()
    for tool in tools or []:
        function = dict(tool.get("function") or {})
        name = str(function.get("name") or "")
        if name:
            names.add(name)
    return names


def _last_user_content(messages: Sequence[Mapping[str, Any]]) -> str:
    for message in reversed(messages):
        if str(message.get("role") or "") == "user":
            return str(message.get("content") or "")
    return ""


def _tool_messages_after_last_user(messages: Sequence[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    last_user_index = -1
    for index, message in enumerate(messages):
        if str(message.get("role") or "") == "user":
            last_user_index = index
    return [
        message
        for message in messages[last_user_index + 1 :]
        if str(message.get("role") or "") == "tool"
    ]


def _looks_like_harmonicode_expression(text: str) -> bool:
    return any(marker in text for marker in _EXPRESSION_MARKERS) or bool(
        re.search(r"\b(?:AB|P\^?2|pq|xy|yx|zw|wz)\b", text)
    )


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


class HHSNativeLanguageProviderNotReady(RuntimeError):
    pass


class HHSNativeLiteRTLMTransport:
    """OpenAI-compatible transport backed by native HHS language capabilities."""

    provider_id = PROVIDER_ID
    requested_operation = REQUESTED_OPERATION
    model_id = MODEL_ID
    backend = "native"
    request_model_id = MODEL_ID

    def __init__(
        self,
        *,
        word2vec_service: Any = None,
        require_word2vec: Optional[bool] = None,
    ) -> None:
        self._word2vec_service = word2vec_service
        self.require_word2vec = (
            os.getenv("HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC", "1").lower()
            not in {"0", "false", "no", "off"}
            if require_word2vec is None
            else bool(require_word2vec)
        )

    def _word2vec(self) -> Any:
        if self._word2vec_service is None:
            from hhs_runtime.pass166.service import DEFAULT_WORD2VEC_SERVICE

            self._word2vec_service = DEFAULT_WORD2VEC_SERVICE
        return self._word2vec_service

    def installation_status(self) -> Dict[str, Any]:
        semantic_error = None
        reasoner_error = None
        word2vec_error = None
        semantic_ready = False
        reasoner_ready = False
        word2vec_status: Dict[str, Any] = {}

        try:
            from hhs_runtime.pass148.semantics import analyze_expression  # noqa: F401

            semantic_ready = True
        except Exception as exc:
            semantic_error = f"{type(exc).__name__}: {exc}"

        try:
            from hhs_runtime.pass151.semantic_reasoner import BoundedSemanticReasoner  # noqa: F401

            reasoner_ready = True
        except Exception as exc:
            reasoner_error = f"{type(exc).__name__}: {exc}"

        if self.require_word2vec or self._word2vec_service is not None:
            try:
                word2vec_status = dict(self._word2vec().status())
            except Exception as exc:
                word2vec_error = f"{type(exc).__name__}: {exc}"
                word2vec_status = {
                    "offline_ready": False,
                    "active_model_id": None,
                    "installed_models": 0,
                }
        else:
            word2vec_status = {
                "offline_ready": False,
                "active_model_id": None,
                "installed_models": 0,
                "probe_skipped": True,
                "classification": "HHS_PASS_166_WORD2VEC_OPTIONAL_UNPROBED",
            }

        word2vec_ready = bool(
            word2vec_status.get("offline_ready")
            and word2vec_status.get("active_model_id")
        )
        ready = bool(
            semantic_ready
            and reasoner_ready
            and (word2vec_ready or not self.require_word2vec)
        )
        status = {
            "schema": "HHS_NATIVE_LANGUAGE_PROVIDER_INSTALLATION_STATUS_V1",
            "version": VERSION,
            "provider_id": PROVIDER_ID,
            "model_id": MODEL_ID,
            "ready": ready,
            "semantic_membrane_ready": semantic_ready,
            "bounded_reasoner_ready": reasoner_ready,
            "word2vec_required": self.require_word2vec,
            "word2vec_ready": word2vec_ready,
            "word2vec": word2vec_status,
            "errors": {
                "semantic": semantic_error,
                "reasoner": reasoner_error,
                "word2vec": word2vec_error,
            },
            "runtime_mutation_admitted": False,
        }
        status["status_root_hash72"] = hash72(
            "HHS_NATIVE_LANGUAGE_PROVIDER_INSTALLATION_STATUS_V1",
            status,
        )
        return status

    def _require_ready(self) -> Dict[str, Any]:
        status = self.installation_status()
        if not status["ready"]:
            missing: List[str] = []
            if not status["semantic_membrane_ready"]:
                missing.append("Pass 148 semantic membrane")
            if not status["bounded_reasoner_ready"]:
                missing.append("Pass 151 bounded semantic reasoner")
            if status["word2vec_required"] and not status["word2vec_ready"]:
                missing.append("active offline-ready Pass 166 Word2Vec model")
            raise HHSNativeLanguageProviderNotReady(
                "native HHS language provider is not installation-closed: "
                + ", ".join(missing)
            )
        return status

    async def list_models(self) -> Dict[str, Any]:
        status = await asyncio.to_thread(self._require_ready)
        return {
            "object": "list",
            "data": [{
                "id": MODEL_ID,
                "object": "model",
                "created": 0,
                "owned_by": "hhs",
                "provider_id": PROVIDER_ID,
                "provider_kind": "HHS_NATIVE_LITERT_COMPATIBLE_PROVIDER",
                "word2vec_model_id": status["word2vec"].get("active_model_id"),
                "semantic_registry": "PASS148",
                "reasoner": "PASS151",
            }],
            "hhs_installation_status": status,
        }

    @staticmethod
    def _tool_call(name: str, arguments: Mapping[str, Any], index: int) -> Dict[str, Any]:
        return {
            "id": f"call-hhs-native-{index}-{uuid.uuid4().hex[:12]}",
            "type": "function",
            "function": {
                "name": name,
                "arguments": json.dumps(dict(arguments), ensure_ascii=False),
            },
        }

    def _select_tool_calls(
        self,
        query: str,
        tools: Optional[Sequence[Mapping[str, Any]]],
    ) -> List[Dict[str, Any]]:
        available = _available_tool_names(tools)
        text = query.casefold()
        selections: List[tuple[str, Dict[str, Any]]] = []

        def add(name: str, arguments: Optional[Mapping[str, Any]] = None) -> None:
            if name in available and name not in {item[0] for item in selections}:
                selections.append((name, dict(arguments or {})))

        explicit_runtime_service = any(
            phrase in text
            for phrase in (
                "runtime service", "registered service", "service registry",
                "services status", "service status",
            )
        )
        if explicit_runtime_service:
            add("hhs_runtime_services")
            add("hhs_runtime_service_status")
        if any(token in text for token in ("runtime state", "vm81 state", "kernel state")):
            add("hhs_runtime_state")
        if any(token in text for token in ("kernel invariant", "invariants", "conformance")):
            add("hhs_kernel_invariants")
            add("hhs_kernel_conformance_status")
        if "pass 152" in text or "pass152" in text or "elastic closure" in text:
            add("hhs_pass152_status")
            add("hhs_pass152_capabilities")

        if not selections and not _looks_like_harmonicode_expression(query):
            add("hhs_repository_search", {"query": query, "limit": 5})

        return [
            self._tool_call(name, arguments, index)
            for index, (name, arguments) in enumerate(selections)
        ]

    @staticmethod
    def _semantic_analysis(query: str) -> Optional[Dict[str, Any]]:
        if not _looks_like_harmonicode_expression(query):
            return None
        try:
            from hhs_runtime.pass148.semantics import analyze_expression

            return analyze_expression(
                query,
                source_type="model_output",
                source_reference="provider:hhs.local.text:user-query",
                profile_id="HHS_NATIVE_TYPED_V1",
            )
        except Exception as exc:
            return {
                "schema": "HHS_NATIVE_SEMANTIC_ANALYSIS_ERROR_V1",
                "error": f"{type(exc).__name__}: {exc}",
            }

    def _word2vec_context(self, query: str) -> Dict[str, Any]:
        service = self._word2vec()
        tokens = []
        for token in _WORD_RE.findall(query.casefold()):
            if token not in tokens:
                tokens.append(token)
        for token in tokens[:12]:
            try:
                nearest = service.nearest(token, top_k=4)
                return {
                    "token": token,
                    "model_id": nearest.get("model_id"),
                    "neighbors": nearest.get("results") or [],
                    "exact": not bool(nearest.get("approximate")),
                }
            except Exception:
                continue
        return {
            "token": None,
            "model_id": service.status().get("active_model_id"),
            "neighbors": [],
            "exact": True,
        }

    @staticmethod
    def _parse_tool_receipts(
        tool_messages: Sequence[Mapping[str, Any]],
    ) -> List[Dict[str, Any]]:
        receipts: List[Dict[str, Any]] = []
        for message in tool_messages:
            try:
                value = json.loads(str(message.get("content") or "{}"))
            except json.JSONDecodeError:
                value = {
                    "ok": False,
                    "error": "tool result was not valid JSON",
                    "raw": str(message.get("content") or "")[:1024],
                }
            receipts.append(value if isinstance(value, dict) else {"value": value})
        return receipts

    @staticmethod
    def _repository_evidence(response: Mapping[str, Any]) -> List[str]:
        lines: List[str] = []
        for result in (response.get("results") or [])[:5]:
            if not isinstance(result, Mapping):
                continue
            path = str(result.get("path") or "unknown source")
            snippet = str(result.get("snippet") or "").strip()
            lines.append(f"- {path}: {snippet}")
        return lines

    @classmethod
    def _tool_evidence_lines(cls, receipts: Sequence[Mapping[str, Any]]) -> List[str]:
        sections: List[str] = []
        for receipt in receipts:
            tool_name = str(receipt.get("tool_name") or "HHS tool")
            if not receipt.get("ok"):
                sections.append(
                    f"{tool_name} failed: {receipt.get('error') or receipt.get('reason') or receipt.get('status')}"
                )
                continue
            response = receipt.get("response")
            if tool_name == "hhs_repository_search" and isinstance(response, Mapping):
                evidence = cls._repository_evidence(response)
                sections.append(
                    "Repository evidence:\n" + (
                        "\n".join(evidence)
                        if evidence
                        else "- No bounded source match was found."
                    )
                )
                continue
            if isinstance(response, Mapping):
                scalar_lines: List[str] = []
                for key, value in response.items():
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        scalar_lines.append(f"- {key}: {value}")
                    elif isinstance(value, list):
                        scalar_lines.append(f"- {key}: {len(value)} item(s)")
                    elif isinstance(value, Mapping):
                        scalar_lines.append(f"- {key}: {len(value)} field(s)")
                    if len(scalar_lines) >= 10:
                        break
                sections.append(f"{tool_name}:\n" + "\n".join(scalar_lines))
            else:
                sections.append(f"{tool_name}: {response}")
        return sections

    def _compose_answer(
        self,
        query: str,
        receipts: Sequence[Mapping[str, Any]],
    ) -> tuple[str, Dict[str, Any]]:
        semantic = self._semantic_analysis(query)
        word2vec = self._word2vec_context(query)
        evidence_sections = self._tool_evidence_lines(receipts)
        facts: List[str] = []

        if semantic and semantic.get("proposition"):
            proposition = semantic["proposition"]
            facts.extend([
                f"semantic_class={proposition.get('primary_class')}",
                f"consequence_class={proposition.get('consequence_class')}",
                f"authority_level={proposition.get('authority_level')}",
                f"proposition_hash72={proposition.get('hash72_identity')}",
            ])
        facts.extend(evidence_sections)
        if word2vec.get("token"):
            neighbors = [
                str(item.get("token"))
                for item in word2vec.get("neighbors") or []
                if isinstance(item, Mapping) and item.get("token")
            ]
            facts.append(
                f"word2vec[{word2vec['token']}] nearest={neighbors} model={word2vec.get('model_id')}"
            )

        from hhs_runtime.pass151.semantic_reasoner import BoundedSemanticReasoner

        reasoner = BoundedSemanticReasoner()
        request = reasoner.request(
            "NATIVE_SEMANTIC_EXPLANATION_REQUIRED",
            obligation_ids=[],
            verbatim=[query],
            facts=facts,
            allowed=[
                "Answer from witnessed HHS tool evidence",
                "Preserve unresolved native semantics",
                "Report dependency or authority boundaries explicitly",
            ],
            prohibited=[
                "fabricate runtime mutation",
                "promote model output to canonical truth",
                "replace missing model assets with a mock response",
            ],
            budget=8,
        )
        reasoning = reasoner.reason(request)

        text = query.casefold()
        if any(token in text for token in ("what can", "capabilities", "help")):
            answer = (
                "The native HHS language provider is active through the LiteRT-compatible "
                "assistant pipeline. It can analyze HARMONICODE with the Pass 148 semantic "
                "membrane, use Pass 151 bounded reasoning, query the active Pass 166 "
                "Word2Vec memory, and call governed read-only HHS runtime and repository tools."
            )
        elif semantic and semantic.get("proposition"):
            proposition = semantic["proposition"]
            unresolved = semantic.get("unresolved_elements") or []
            contamination = semantic.get("contamination_findings") or []
            answer = (
                f"Native HHS semantic analysis classifies the expression as "
                f"{proposition.get('primary_class')} with consequence class "
                f"{proposition.get('consequence_class')} at authority "
                f"{proposition.get('authority_level')}. The source spelling and operand "
                f"order are preserved. Unresolved elements: {len(unresolved)}. "
                f"Contamination findings: {len(contamination)}. Proposition witness: "
                f"{proposition.get('hash72_identity')}."
            )
            if evidence_sections:
                answer += "\n\n" + "\n\n".join(evidence_sections)
        elif evidence_sections:
            answer = "\n\n".join(evidence_sections)
        else:
            answer = (
                "The native HHS provider completed bounded language analysis, but no "
                "governed evidence surface returned a direct factual result for this query. "
                "The request remains unresolved rather than receiving a fabricated answer."
            )

        if word2vec.get("token"):
            neighbor_names = [
                str(item.get("token"))
                for item in word2vec.get("neighbors") or []
                if isinstance(item, Mapping) and item.get("token")
            ]
            if neighbor_names:
                answer += (
                    f"\n\nActive Word2Vec context for “{word2vec['token']}”: "
                    + ", ".join(neighbor_names)
                    + "."
                )

        trace = {
            "schema": "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
            "semantic_analysis": semantic,
            "word2vec_context": word2vec,
            "bounded_reasoning": reasoning,
            "tool_receipt_count": len(receipts),
            "runtime_mutation_admitted": False,
        }
        trace["trace_root_hash72"] = hash72(
            "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
            trace,
        )
        return answer, trace

    async def chat_completion(
        self,
        *,
        messages: Iterable[Mapping[str, Any]],
        tools: Optional[List[Mapping[str, Any]]] = None,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        del response_format
        await asyncio.to_thread(self._require_ready)
        message_list = [dict(message) for message in messages]
        query = _last_user_content(message_list).strip()
        if not query:
            raise ValueError("native HHS provider requires a user message")

        tool_messages = _tool_messages_after_last_user(message_list)
        if not tool_messages:
            tool_calls = self._select_tool_calls(query, tools)
            if tool_calls:
                return {
                    "id": _completion_id(),
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": MODEL_ID,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": tool_calls,
                        },
                        "finish_reason": "tool_calls",
                    }],
                    "usage": {
                        "prompt_tokens": _word_count(query),
                        "completion_tokens": 0,
                        "total_tokens": _word_count(query),
                    },
                }

        receipts = self._parse_tool_receipts(tool_messages)
        answer, trace = self._compose_answer(query, receipts)
        completion_tokens = _word_count(answer)
        return {
            "id": _completion_id(),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": MODEL_ID,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": answer,
                },
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": _word_count(query),
                "completion_tokens": completion_tokens,
                "total_tokens": _word_count(query) + completion_tokens,
            },
            "hhs_native_trace": trace,
        }
