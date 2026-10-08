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
from pathlib import Path
import re
import time
import uuid
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_assistant_stage_timing_v1 import timed_stage
from hhs_backend.runtime.hhs_pass220_native_causal_lm_generation_v1 import (
    NativeCausalLMGenerationService,
    NativeCausalLMNotReady,
)
from hhs_backend.runtime.hhs_native_response_block_stream_v1 import (
    NativeResponseBlockStream,
    NativeResponseBlockStreamError,
)
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    ASSISTANT_MODE_AGENTIC_APPLICATION_DEVELOPMENT,
    ASSISTANT_MODE_BOTH,
    ASSISTANT_MODE_GENERAL_CHAT,
    DEFAULT_ASSISTANT_MODE,
    normalize_assistant_mode,
)

VERSION = "HHS_NATIVE_LITERT_COMPATIBLE_LANGUAGE_PROVIDER_V1"
PROVIDER_ID = "provider:hhs.local.text"
MODEL_ID = "hhs-native-language-v1"
REQUESTED_OPERATION = "hhs_native_litert.chat_completion"

_EXPRESSION_MARKERS = (
    "==", "≠", "Δ", "Ω", "Θ", "Ψ", "Φ", "Γ", "Λ", ":=", "u^72", "u⁷²",
)
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{1,63}")
_STRUCTURED_HISTORY_TOKEN_RE = re.compile(
    r"\b[A-Za-z0-9]+(?:[-_:./][A-Za-z0-9]+){2,}\b"
)


def _bounded_timeout_seconds(name: str, default: float) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return min(60.0, max(0.05, value))


def _previous_user_content(messages: Sequence[Mapping[str, Any]]) -> str:
    user_messages = [
        str(message.get("content") or "")
        for message in messages
        if str(message.get("role") or "") == "user"
    ]
    return user_messages[-2] if len(user_messages) >= 2 else ""


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


def _assistant_mode_from_messages(messages: Sequence[Mapping[str, Any]]) -> str:
    for message in messages:
        if str(message.get("role") or "") != "system":
            continue
        content = str(message.get("content") or "")
        match = re.search(
            r"HHS_ASSISTANT_MODE=(GENERAL_CHAT|AGENTIC_APPLICATION_DEVELOPMENT|BOTH)",
            content,
        )
        if match:
            return normalize_assistant_mode(match.group(1))
    return DEFAULT_ASSISTANT_MODE


def _looks_like_development_request(query: str) -> bool:
    text = query.casefold()
    tokens = set(re.findall(r"[a-z0-9+#._-]+", text))
    words = {
        "app", "application", "code", "coding", "implement", "implementation",
        "repository", "repo", "git", "branch", "commit", "build", "compile",
        "compiler", "test", "pytest", "ci", "workflow", "deploy", "deployment",
        "digitalocean", "runtime", "vm81", "hash72", "hash216", "api",
        "endpoint", "server", "frontend", "backend", "gui", "typescript",
        "javascript", "python", "c++", "c#", "java", "linux", "bug", "fix",
        "refactor", "workspace", "file", "source",
    }
    phrases = (
        "pull request",
        "application development",
        "software development",
        "write code",
        "create an app",
        "build an app",
        "deploy an app",
    )
    return bool(tokens & words) or any(phrase in text for phrase in phrases)


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
        generation_service: Any = None,
    ) -> None:
        self._word2vec_service = word2vec_service
        self._generation_service = generation_service
        self._response_stream_service: Any = None
        self._prototype_cycle: Any = None
        self._prototype_dataset: Optional[Dict[str, Any]] = None
        self._prototype_model_id: Optional[str] = None
        self.require_word2vec = (
            os.getenv("HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC", "1").lower()
            not in {"0", "false", "no", "off"}
            if require_word2vec is None
            else bool(require_word2vec)
        )
        self.generation_timeout_seconds = _bounded_timeout_seconds(
            "HHS_NATIVE_LANGUAGE_GENERATION_TIMEOUT_SECONDS",
            25.0,
        )
        self.fallback_timeout_seconds = _bounded_timeout_seconds(
            "HHS_NATIVE_LANGUAGE_FALLBACK_TIMEOUT_SECONDS",
            8.0,
        )

    def _word2vec(self) -> Any:
        if self._word2vec_service is None:
            from hhs_runtime.pass166.service import DEFAULT_WORD2VEC_SERVICE

            self._word2vec_service = DEFAULT_WORD2VEC_SERVICE
        return self._word2vec_service

    def _causal_generation(self) -> Any:
        if self._generation_service is None:
            self._generation_service = NativeCausalLMGenerationService()
        return self._generation_service

    def _response_stream(self) -> NativeResponseBlockStream:
        if self._response_stream_service is None:
            self._response_stream_service = NativeResponseBlockStream(
                self._causal_generation()
            )
        return self._response_stream_service

    def _prototype_context(self, query: str, *, top_k: int = 3) -> tuple[str, Dict[str, Any]]:
        service = self._word2vec()
        status = dict(service.status())
        active_model_id = str(status.get("active_model_id") or "")
        if not active_model_id:
            return "", {
                "available": False,
                "reason": "PASS166_MODEL_NOT_ACTIVE",
                "prototype_dataset_reused": False,
                "candidate_count": 0,
            }

        reused = (
            self._prototype_cycle is not None
            and self._prototype_dataset is not None
            and self._prototype_model_id == active_model_id
        )
        if not reused:
            from hhs_runtime.hhs_pass219_ethical_text_training_v1 import (
                EthicalTextTrainingCycle,
                load_prompt_response_jsonl,
            )

            repository_root = Path(__file__).resolve().parents[2]
            cycle = EthicalTextTrainingCycle.from_repository(
                repository_root,
                word2vec_service=service,
                model_id=active_model_id,
            )
            examples = load_prompt_response_jsonl(
                repository_root / "data/pass219/ethical_alignment_prompt_response_v1.jsonl"
            )
            dataset = cycle.compile_dataset(examples, require_word2vec=True)
            self._prototype_cycle = cycle
            self._prototype_dataset = dataset
            self._prototype_model_id = active_model_id

        assert self._prototype_cycle is not None
        assert self._prototype_dataset is not None
        selected = self._prototype_cycle.select_response_candidate(
            query,
            self._prototype_dataset,
            top_k=top_k,
        )
        records_by_id = {
            str(item.get("example_id") or ""): item
            for item in self._prototype_dataset.get("records", ())
        }

        context_blocks: List[str] = []
        candidate_metadata: List[Dict[str, Any]] = []
        for candidate in selected.get("results", ()):
            score = dict(candidate.get("score") or {})
            numerator = int(score.get("numerator") or 0)
            denominator = int(score.get("denominator") or 1)
            if numerator <= 0 or denominator <= 0:
                continue
            example_id = str(candidate.get("example_id") or "")
            source_record = records_by_id.get(example_id, {})
            prompt = str(source_record.get("prompt") or "")
            response = str(candidate.get("response") or "")
            if not prompt or not response:
                continue
            context_blocks.append(
                "[admitted prompt/response prototype]\n"
                f"Prompt: {prompt}\n"
                f"Response: {response}\n"
                "[/admitted prompt/response prototype]"
            )
            candidate_metadata.append({
                "example_id": example_id,
                "score": {"numerator": numerator, "denominator": denominator},
                "record_hash72": candidate.get("record_hash72"),
                "hash216_root": candidate.get("hash216_root"),
                "declared_invariants": list(candidate.get("declared_invariants") or []),
            })

        return "\n\n".join(context_blocks), {
            "available": True,
            "prototype_dataset_reused": reused,
            "active_word2vec_model_id": active_model_id,
            "dataset_hash72": self._prototype_dataset.get("dataset_hash72"),
            "dataset_final_hash216_root": self._prototype_dataset.get("final_hash216_root"),
            "candidate_set_hash72": selected.get("candidate_set_hash72"),
            "candidate_count": len(candidate_metadata),
            "candidates": candidate_metadata,
            "candidate_only": True,
            "truth_promotion": False,
            "vm81_commit_invoked": False,
        }

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

        # Word2Vec is optional in production. Do not import/instantiate the
        # Pass 166 service merely to prove readiness for turns that do not use
        # language-memory retrieval. Required or already-injected Word2Vec
        # services are still checked exactly as before.
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
                "status": "OPTIONAL_WORD2VEC_STATUS_DEFERRED",
                "deferred": True,
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
        try:
            causal_status = dict(self._causal_generation().status())
        except Exception as exc:
            causal_status = {
                "configured": False,
                "loaded": False,
                "ready": False,
                "load_error": f"{type(exc).__name__}: {exc}",
            }

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
            "causal_lm": causal_status,
            "causal_lm_generation_supported": True,
            "causal_lm_required_for_provider_readiness": False,
            "errors": {
                "semantic": semantic_error,
                "reasoner": reasoner_error,
                "word2vec": word2vec_error,
            },
            "general_chat_prompt_response_supported": True,
            "agentic_application_development_supported": True,
            "combined_mode_supported": True,
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
        status = self._require_ready()
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
        *,
        assistant_mode: str,
    ) -> List[Dict[str, Any]]:
        mode = normalize_assistant_mode(assistant_mode)
        text = query.casefold()
        unified_tool_request = bool(
            "lane5" in text
            or "lane 5" in text
            or any(
                phrase in text
                for phrase in (
                    "model fabric",
                    "language model fabric",
                    "language models",
                    "which model",
                    "active model",
                    "selected model",
                )
            )
        )
        if mode == ASSISTANT_MODE_GENERAL_CHAT:
            return []
        if (
            mode == ASSISTANT_MODE_BOTH
            and not _looks_like_development_request(query)
            and not unified_tool_request
        ):
            return []

        available = _available_tool_names(tools)
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
        if any(
            phrase in text
            for phrase in (
                "model fabric",
                "language model fabric",
                "language models",
                "which model",
                "active model",
                "selected model",
            )
        ):
            add("hhs_language_model_fabric")

        lane5_requested = "lane5" in text or "lane 5" in text
        if lane5_requested:
            add("hhs_lane5_capability_status")
            if any(
                token in text
                for token in (
                    "capability",
                    "capabilities",
                    "search",
                    "find",
                    "tool",
                    "operation",
                    "registry",
                    "repository",
                )
            ):
                add("hhs_lane5_capability_search", {"query": query, "limit": 8})
        if any(token in text for token in ("runtime state", "vm81 state", "kernel state")):
            add("hhs_runtime_state")
        if any(token in text for token in ("kernel invariant", "invariants", "conformance")):
            add("hhs_kernel_invariants")
            add("hhs_kernel_conformance_status")
        if "pass 152" in text or "pass152" in text or "elastic closure" in text:
            add("hhs_pass152_status")
            add("hhs_pass152_capabilities")

        if (
            not selections
            and mode == ASSISTANT_MODE_AGENTIC_APPLICATION_DEVELOPMENT
            and _looks_like_development_request(query)
            and not _looks_like_harmonicode_expression(query)
        ):
            add("hhs_repository_search", {"query": query, "limit": 5})
        elif (
            not selections
            and mode == ASSISTANT_MODE_BOTH
            and _looks_like_development_request(query)
            and not _looks_like_harmonicode_expression(query)
        ):
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
    def _tool_text_payloads(cls, value: Any, *, limit: int = 8) -> List[str]:
        preferred = {"content", "text", "answer", "message", "summary", "response", "result"}
        found: List[str] = []

        def visit(node: Any, key: Optional[str] = None) -> None:
            if len(found) >= limit:
                return
            if isinstance(node, str):
                if key in preferred and node.strip() and node not in found:
                    found.append(node)
                return
            if isinstance(node, Mapping):
                for child_key, child_value in node.items():
                    visit(child_value, str(child_key).casefold())
                    if len(found) >= limit:
                        return
            elif isinstance(node, list):
                for child in node:
                    visit(child, key)
                    if len(found) >= limit:
                        return

        visit(value)
        return found

    @staticmethod
    def _tool_evidence_context(
        receipts: Sequence[Mapping[str, Any]],
        *,
        max_characters: int = 65536,
    ) -> str:
        if not receipts:
            return ""
        header = (
            "[governed HHS tool evidence]\n"
            "Use the evidence below to answer the original user request in plain English. "
            "Do not replace the answer with receipt/status reporting. Preserve uncertainty "
            "and authority boundaries present in the evidence.\n"
        )
        parts: List[str] = [header]
        used = len(header)
        for index, receipt in enumerate(receipts):
            encoded = json.dumps(
                dict(receipt),
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
                default=str,
            )
            prefix = f"[tool-receipt-{index}]\n"
            suffix = f"\n[/tool-receipt-{index}]\n"
            remaining = max_characters - used - len(prefix) - len(suffix)
            if remaining <= 0:
                break
            if len(encoded) > remaining:
                encoded = encoded[:remaining]
            block = prefix + encoded + suffix
            parts.append(block)
            used += len(block)
            if used >= max_characters:
                break
        parts.append("[/governed HHS tool evidence]")
        return "".join(parts)

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
                textual_payloads = cls._tool_text_payloads(response)
                if textual_payloads:
                    sections.append(
                        f"{tool_name}:\n" + "\n\n".join(textual_payloads)
                    )
                    continue
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

    def _history_recall_answer(
        self,
        query: str,
        messages: Sequence[Mapping[str, Any]],
    ) -> Optional[str]:
        lowered = query.casefold()
        recall_requested = any(
            phrase in lowered
            for phrase in (
                "previous message",
                "last message",
                "earlier message",
                "asked you to remember",
                "did i ask",
                "what did i say",
                "what did i tell",
            )
        )
        if not recall_requested:
            return None

        previous = _previous_user_content(messages).strip()
        if not previous:
            return None

        if any(word in lowered for word in ("token", "code", "identifier", "marker")):
            candidates = _STRUCTURED_HISTORY_TOKEN_RE.findall(previous)
            if candidates:
                return candidates[-1]

        return f'Your previous message was: "{previous}"'

    def _emergency_conversation_answer(
        self,
        query: str,
        messages: Sequence[Mapping[str, Any]],
        *,
        assistant_mode: str,
    ) -> tuple[str, Dict[str, Any]]:
        mode = normalize_assistant_mode(assistant_mode)
        recalled = self._history_recall_answer(query, messages)
        lowered = query.strip().casefold()
        if recalled is not None:
            answer = recalled
            classification = "BOUNDED_HISTORY_RECALL"
        elif "remember" in lowered:
            answer = "I’ll keep that in this conversation for your next message."
            classification = "BOUNDED_CONVERSATION_ACK"
        elif re.fullmatch(r"(hi|hello|hey|good morning|good afternoon|good evening)[!. ]*", lowered):
            answer = "Hello. What would you like to talk about?"
            classification = "BOUNDED_GREETING"
        else:
            answer = (
                "I received your message. The native causal generator is temporarily slow, "
                "so I’m continuing through the bounded conversational fallback without "
                "claiming any runtime mutation."
            )
            classification = "BOUNDED_CONVERSATION_FALLBACK"

        trace = {
            "schema": "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
            "assistant_mode": mode,
            "generation_path": "BOUNDED_CONVERSATION_FALLBACK",
            "fallback_classification": classification,
            "history_recall": recalled is not None,
            "general_chat_prompt_response_cycle": mode in {
                ASSISTANT_MODE_GENERAL_CHAT,
                ASSISTANT_MODE_BOTH,
            },
            "runtime_mutation_admitted": False,
        }
        trace["trace_root_hash72"] = hash72(
            "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
            trace,
        )
        return answer, trace

    def _compose_answer(
        self,
        query: str,
        receipts: Sequence[Mapping[str, Any]],
        *,
        assistant_mode: str,
        messages: Sequence[Mapping[str, Any]] = (),
    ) -> tuple[str, Dict[str, Any]]:
        mode = normalize_assistant_mode(assistant_mode)
        recalled = self._history_recall_answer(query, messages)
        if recalled is not None:
            trace = {
                "schema": "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
                "semantic_analysis": {},
                "word2vec_context": {},
                "bounded_reasoning": {},
                "tool_receipt_count": len(receipts),
                "assistant_mode": mode,
                "history_recall": True,
                "generation_path": "EXACT_SEMANTIC_HISTORY_FALLBACK",
                "general_chat_prompt_response_cycle": mode in {
                    ASSISTANT_MODE_GENERAL_CHAT,
                    ASSISTANT_MODE_BOTH,
                },
                "runtime_mutation_admitted": False,
            }
            trace["trace_root_hash72"] = hash72(
                "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
                trace,
            )
            return recalled, trace

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
            if mode == ASSISTANT_MODE_AGENTIC_APPLICATION_DEVELOPMENT:
                answer = (
                    "This request does not appear to be an application-development task. "
                    "Agentic application development mode is limited to code, workspace, "
                    "runtime, testing, build, deployment, repository, and related engineering "
                    "work. Switch to General chat or Both for ordinary conversation."
                )
            else:
                stripped = query.strip()
                lowered = stripped.casefold()
                if re.fullmatch(r"(hi|hello|hey|good morning|good afternoon|good evening)[!. ]*", lowered):
                    answer = "Hello. What would you like to talk about?"
                elif any(phrase in lowered for phrase in ("thank you", "thanks", "appreciate it")):
                    answer = "You're welcome."
                elif any(phrase in lowered for phrase in ("who are you", "what are you")):
                    answer = (
                        "I'm the native HHS natural-language assistant. In this mode I can "
                        "hold ordinary prompt-response conversations, while governed HHS "
                        "development tools stay separate unless you select Both or Agentic "
                        "application development."
                    )
                else:
                    topic = str(word2vec.get("token") or "").strip()
                    neighbors = [
                        str(item.get("token"))
                        for item in word2vec.get("neighbors") or []
                        if isinstance(item, Mapping) and item.get("token")
                    ]
                    if topic and neighbors:
                        answer = (
                            f"You’re asking about {topic}. The active native language memory "
                            f"associates it with {', '.join(neighbors[:4])}. I can continue "
                            "the conversation from that context, explain the idea, compare "
                            "possibilities, or use retrieved evidence when you explicitly "
                            "ask for sourced information."
                        )
                    else:
                        answer = (
                            "I can continue this as a general natural-language conversation. "
                            "Tell me what you want to understand, create, compare, or reason "
                            "through, and I’ll respond directly without forcing a developer "
                            "workflow."
                        )

        if (
            word2vec.get("token")
            and (
                semantic
                or evidence_sections
                or mode == ASSISTANT_MODE_AGENTIC_APPLICATION_DEVELOPMENT
            )
        ):
            neighbor_names = [
                str(item.get("token"))
                for item in word2vec.get("neighbors") or []
                if isinstance(item, Mapping) and item.get("token")
            ]
            if neighbor_names:
                answer += (
                    f"\n\nLanguage-memory context for “{word2vec['token']}”: "
                    + ", ".join(neighbor_names)
                    + "."
                )

        trace = {
            "schema": "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
            "semantic_analysis": semantic,
            "word2vec_context": word2vec,
            "bounded_reasoning": reasoning,
            "tool_receipt_count": len(receipts),
            "assistant_mode": mode,
            "general_chat_prompt_response_cycle": mode in {
                ASSISTANT_MODE_GENERAL_CHAT,
                ASSISTANT_MODE_BOTH,
            },
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
        with timed_stage("native_transport.require_ready"):
            self._require_ready()
        with timed_stage("native_transport.project_messages"):
            message_list = [dict(message) for message in messages]
            mode = _assistant_mode_from_messages(message_list)
            query = _last_user_content(message_list).strip()
        if not query:
            raise ValueError("native HHS provider requires a user message")

        with timed_stage("native_transport.tool_message_projection"):
            tool_messages = _tool_messages_after_last_user(message_list)
        if not tool_messages:
            with timed_stage("native_transport.select_tool_calls"):
                tool_calls = self._select_tool_calls(
                    query,
                    tools,
                    assistant_mode=mode,
                )
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

        with timed_stage("native_transport.parse_tool_receipts"):
            receipts = self._parse_tool_receipts(tool_messages)

        with timed_stage("native_transport.history_recall"):
            history_recall = (
                self._history_recall_answer(query, message_list)
                if not receipts
                else None
            )
        if history_recall is not None:
            trace = {
                "schema": "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
                "assistant_mode": mode,
                "generation_path": "EXACT_THREAD_HISTORY_RECALL",
                "history_recall": True,
                "causal_generation_failure": None,
                "general_chat_prompt_response_cycle": mode in {
                    ASSISTANT_MODE_GENERAL_CHAT,
                    ASSISTANT_MODE_BOTH,
                },
                "runtime_mutation_admitted": False,
            }
            trace["trace_root_hash72"] = hash72(
                "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
                trace,
            )
            completion_tokens = _word_count(history_recall)
            return {
                "id": _completion_id(),
                "object": "chat.completion",
                "created": int(time.time()),
                "model": MODEL_ID,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": history_recall,
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

        memory_acknowledgement = (
            not receipts
            and mode in {ASSISTANT_MODE_GENERAL_CHAT, ASSISTANT_MODE_BOTH}
            and "remember" in query.casefold()
        )
        if memory_acknowledgement:
            structured = _STRUCTURED_HISTORY_TOKEN_RE.findall(query)
            remembered = structured[-1] if structured else ""
            answer = (
                f"I’ll keep {remembered} in this conversation for your next message."
                if remembered
                else "I’ll keep that in this conversation for your next message."
            )
            trace = {
                "schema": "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
                "assistant_mode": mode,
                "generation_path": "EXACT_THREAD_MEMORY_ACKNOWLEDGEMENT",
                "history_recall": False,
                "causal_generation_failure": None,
                "conversation_memory_acknowledged": True,
                "remembered_structured_token": remembered or None,
                "general_chat_prompt_response_cycle": True,
                "runtime_mutation_admitted": False,
            }
            trace["trace_root_hash72"] = hash72(
                "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
                trace,
            )
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

        ordinary_conversation = (
            mode in {ASSISTANT_MODE_GENERAL_CHAT, ASSISTANT_MODE_BOTH}
            and not receipts
            and (
                mode == ASSISTANT_MODE_GENERAL_CHAT
                or not _looks_like_development_request(query)
            )
        )
        causal_failure: Optional[str] = None
        should_generate = ordinary_conversation or bool(receipts)
        if should_generate:
            try:
                prototype_context = ""
                prototype_trace: Dict[str, Any] = {
                    "available": False,
                    "reason": "NOT_REQUESTED",
                    "candidate_count": 0,
                }
                if ordinary_conversation:
                    prototype_context, prototype_trace = await asyncio.wait_for(
                        asyncio.to_thread(self._prototype_context, query),
                        timeout=self.generation_timeout_seconds,
                    )

                tool_context = self._tool_evidence_context(receipts)
                retrieval_parts = [
                    part for part in (prototype_context, tool_context) if part
                ]
                retrieval_context = "\n\n".join(retrieval_parts)
                generated = await asyncio.wait_for(
                    asyncio.to_thread(
                        self._response_stream().generate,
                        message_list,
                        retrieval_context=retrieval_context or None,
                    ),
                    timeout=self.generation_timeout_seconds,
                )
                answer = str(generated["response"])
                stream_manifest = dict(generated.get("manifest") or {})
                trace = {
                    "schema": "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
                    "assistant_mode": mode,
                    "generation_path": "NATIVE_CAUSAL_LM_SERIALIZED_BLOCK_STREAM",
                    "general_chat_prompt_response_cycle": True,
                    "prototype_retrieval": prototype_trace,
                    "tool_receipt_count": len(receipts),
                    "tool_evidence_synthesized_into_plain_english": bool(receipts),
                    "response_stream_manifest": stream_manifest,
                    "serialized_response": str(
                        generated.get("serialized_response") or ""
                    ),
                    "response_block_count": int(stream_manifest.get("block_count") or 0),
                    "embedded_metadata_delimiters": True,
                    "human_rendering_is_payload_projection": True,
                    "generated_payload_rewritten": False,
                    "runtime_mutation_admitted": False,
                }
                trace["trace_root_hash72"] = hash72(
                    "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
                    trace,
                )
                completion_tokens = sum(
                    int((block or {}).get("generated_token_count") or 0)
                    for block in (generated.get("blocks") or [])
                )
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
                        "finish_reason": str(generated.get("finish_reason") or "stop"),
                    }],
                    "usage": {
                        "prompt_tokens": _word_count(query),
                        "completion_tokens": completion_tokens or _word_count(answer),
                        "total_tokens": _word_count(query)
                        + (completion_tokens or _word_count(answer)),
                    },
                    "hhs_native_trace": trace,
                }
            except (NativeCausalLMNotReady, NativeResponseBlockStreamError) as exc:
                causal_failure = f"{type(exc).__name__}: {exc}"
            except Exception as exc:
                causal_failure = f"{type(exc).__name__}: {exc}"

        try:
            answer, trace = await asyncio.wait_for(
                asyncio.to_thread(
                    self._compose_answer,
                    query,
                    receipts,
                    assistant_mode=mode,
                    messages=message_list,
                ),
                timeout=self.fallback_timeout_seconds,
            )
            trace["generation_path"] = str(
                trace.get("generation_path") or "EXACT_SEMANTIC_FALLBACK"
            )
        except Exception as exc:
            answer, trace = self._emergency_conversation_answer(
                query,
                message_list,
                assistant_mode=mode,
            )
            trace["semantic_fallback_failure"] = f"{type(exc).__name__}: {exc}"
        trace["causal_generation_failure"] = causal_failure
        trace["trace_root_hash72"] = hash72(
            "HHS_NATIVE_LANGUAGE_PROVIDER_TRACE_V1",
            {key: value for key, value in trace.items() if key != "trace_root_hash72"},
        )
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
