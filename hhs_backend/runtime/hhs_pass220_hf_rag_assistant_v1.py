"""Pass 220 I005: Hugging Face-compatible Hash216 RAG assistant bridge.

From the text-generation boundary this is an ordinary RAG assistant:

    prompt -> HHS retrieval -> bounded context -> tokenizer -> model.generate -> text

Hash216 identity remains owned by the HHS retrieval layer.  This adapter only
validates returned identities, assembles authorized natural-language context,
and invokes the ordinary Hugging Face tokenizer/model interface.  It has no
VM81, Hash72, or Hash216 mutation authority.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, MutableMapping, Sequence

from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import split_hash216

SCHEMA = "HHS_PASS_220_I005_HUGGING_FACE_RAG_ASSISTANT_V1"
RETRIEVAL_SCHEMA = "HHS_PASS_220_I005_AUTHORIZED_RAG_RETRIEVAL_V1"
DEFAULT_TOP_K = 8
DEFAULT_MAX_CONTEXT_CHARACTERS = 32768
DEFAULT_MAX_NEW_TOKENS = 256


class Pass220HFRAGError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _exact_positive_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise Pass220HFRAGError(f"{name} must be a positive exact integer")
    return value


def _exact_hash216(value: Any, *, name: str) -> str:
    if not isinstance(value, str):
        raise Pass220HFRAGError(f"{name} must be a Hash216 string")
    try:
        split_hash216(value)
    except Exception as exc:
        raise Pass220HFRAGError(f"{name} is not a canonical 216-symbol Hash216 value") from exc
    return value


def _sequence_as_list(value: Any, *, name: str) -> list[Any]:
    if hasattr(value, "tolist"):
        value = value.tolist()
    if not isinstance(value, (list, tuple)):
        raise Pass220HFRAGError(f"{name} must be a token sequence")
    return list(value)


def _first_token_sequence(value: Any, *, name: str) -> list[Any]:
    outer = _sequence_as_list(value, name=name)
    if not outer:
        raise Pass220HFRAGError(f"{name} cannot be empty")
    first = outer[0]
    if hasattr(first, "tolist"):
        first = first.tolist()
    if isinstance(first, (list, tuple)):
        return list(first)
    return outer


def _render_record(record: Mapping[str, Any]) -> str:
    source = record.get("source")
    source_line = f" source={source}" if isinstance(source, str) and source else ""
    return (
        f"[retrieved record_id={record['record_id']} hash216={record['hash216']}{source_line}]\n"
        f"{record['text']}\n"
        "[/retrieved]"
    )


def normalize_retrieval(
    payload: Mapping[str, Any],
    *,
    top_k: int,
    max_context_characters: int,
) -> dict[str, Any]:
    """Validate, deduplicate, and whole-record-bound one HHS retrieval result."""
    top_k_i = _exact_positive_int(top_k, name="top_k")
    budget = _exact_positive_int(max_context_characters, name="max_context_characters")
    if not isinstance(payload, Mapping):
        raise Pass220HFRAGError("retrieval result must be a mapping")

    query_hash216 = _exact_hash216(payload.get("query_hash216"), name="query_hash216")
    records = payload.get("records", ())
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes, bytearray)):
        raise Pass220HFRAGError("retrieval records must be a sequence")

    seen_ids: set[str] = set()
    seen_hashes: dict[str, str] = {}
    unique: list[dict[str, Any]] = []
    duplicate_reuse_count = 0

    for ordinal, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            raise Pass220HFRAGError(f"records[{ordinal}] must be a mapping")
        record_id = raw.get("record_id")
        if not isinstance(record_id, str) or not record_id:
            raise Pass220HFRAGError(f"records[{ordinal}].record_id must be nonempty")
        if record_id in seen_ids:
            raise Pass220HFRAGError("retrieval record IDs must be unique")
        seen_ids.add(record_id)

        record_hash216 = _exact_hash216(raw.get("hash216"), name=f"records[{ordinal}].hash216")
        text = raw.get("text")
        if not isinstance(text, str) or not text:
            raise Pass220HFRAGError(f"records[{ordinal}].text must be nonempty natural language")
        if raw.get("assistant_context_allowed") is not True:
            raise Pass220HFRAGError("retrieval returned a record not authorized for assistant context")

        text_sha256 = _sha256_text(text)
        prior_text_root = seen_hashes.get(record_hash216)
        if prior_text_root is not None:
            if prior_text_root != text_sha256:
                raise Pass220HFRAGError("duplicate Hash216 identity has conflicting natural-language payload")
            duplicate_reuse_count += 1
            continue
        seen_hashes[record_hash216] = text_sha256

        unique.append(
            {
                "record_id": record_id,
                "hash216": record_hash216,
                "text": text,
                "text_sha256": text_sha256,
                "source": raw.get("source") if isinstance(raw.get("source"), str) else None,
                "assistant_context_allowed": True,
                "source_ordinal": ordinal,
            }
        )
        if len(unique) >= top_k_i:
            break

    selected: list[dict[str, Any]] = []
    omitted: list[dict[str, Any]] = []
    rendered_parts: list[str] = []
    used = 0

    for record in unique:
        rendered = _render_record(record)
        separator = 2 if rendered_parts else 0
        cost = separator + len(rendered)
        if used + cost <= budget:
            rendered_parts.append(rendered)
            selected.append(record)
            used += cost
        else:
            omitted.append(
                {
                    "record_id": record["record_id"],
                    "hash216": record["hash216"],
                    "reason": "WHOLE_RECORD_CONTEXT_BUDGET",
                    "rendered_characters": len(rendered),
                }
            )

    context = "\n\n".join(rendered_parts)
    context_identity = {
        "query_hash216": query_hash216,
        "selected": tuple(
            (record["record_id"], record["hash216"], record["text_sha256"])
            for record in selected
        ),
        "max_context_characters": budget,
    }
    context_root = sha256(_stable_json(context_identity).encode("utf-8")).hexdigest()

    return {
        "schema": RETRIEVAL_SCHEMA,
        "query_hash216": query_hash216,
        "retriever_schema": payload.get("schema"),
        "selected_records": selected,
        "omitted_records": omitted,
        "duplicate_reuse_count": duplicate_reuse_count,
        "context": context,
        "context_characters": len(context),
        "max_context_characters": budget,
        "context_root_sha256": context_root,
        "whole_record_budgeting": True,
        "assistant_context_authorized": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }


class Pass220HuggingFaceRAGAssistant:
    """Ordinary Hugging Face generation over HHS-retrieved natural-language context."""

    def __init__(
        self,
        *,
        tokenizer: Any,
        model: Any,
        retriever: Any,
        top_k: int = DEFAULT_TOP_K,
        max_context_characters: int = DEFAULT_MAX_CONTEXT_CHARACTERS,
        context_cache: MutableMapping[str, str] | None = None,
    ) -> None:
        if not callable(tokenizer):
            raise Pass220HFRAGError("tokenizer must be callable")
        if not callable(getattr(tokenizer, "decode", None)):
            raise Pass220HFRAGError("tokenizer.decode must be callable")
        if not callable(getattr(model, "generate", None)):
            raise Pass220HFRAGError("model.generate must be callable")
        if not callable(getattr(retriever, "retrieve", None)):
            raise Pass220HFRAGError("retriever.retrieve must be callable")

        self.tokenizer = tokenizer
        self.model = model
        self.retriever = retriever
        self.top_k = _exact_positive_int(top_k, name="top_k")
        self.max_context_characters = _exact_positive_int(
            max_context_characters,
            name="max_context_characters",
        )
        self._context_cache: MutableMapping[str, str] = (
            context_cache if context_cache is not None else {}
        )

    @staticmethod
    def render_generation_prompt(user_prompt: str, context: str) -> str:
        if not isinstance(user_prompt, str) or not user_prompt.strip():
            raise Pass220HFRAGError("user prompt must be nonempty natural language")
        return (
            "Retrieved context:\n"
            f"{context if context else '(no retrieved context)'}\n\n"
            "User:\n"
            f"{user_prompt}\n\n"
            "Assistant:\n"
        )

    def generate(
        self,
        user_prompt: str,
        *,
        generation_kwargs: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not isinstance(user_prompt, str) or not user_prompt.strip():
            raise Pass220HFRAGError("user prompt must be nonempty natural language")

        raw_retrieval = self.retriever.retrieve(prompt=user_prompt, top_k=self.top_k)
        retrieval = normalize_retrieval(
            raw_retrieval,
            top_k=self.top_k,
            max_context_characters=self.max_context_characters,
        )

        context_root = retrieval["context_root_sha256"]
        cached = self._context_cache.get(context_root)
        context_reused = cached is not None
        if cached is None:
            self._context_cache[context_root] = retrieval["context"]
            context = retrieval["context"]
        else:
            if cached != retrieval["context"]:
                raise Pass220HFRAGError("context cache identity collision")
            context = cached

        rendered_prompt = self.render_generation_prompt(user_prompt, context)
        encoded = self.tokenizer(
            rendered_prompt,
            return_tensors="pt",
            truncation=False,
        )
        if not isinstance(encoded, Mapping) or "input_ids" not in encoded:
            raise Pass220HFRAGError("tokenizer must return a mapping containing input_ids")

        generation = dict(generation_kwargs or {})
        generation.setdefault("max_new_tokens", DEFAULT_MAX_NEW_TOKENS)
        generation.setdefault("do_sample", False)
        if isinstance(generation.get("max_new_tokens"), bool) or not isinstance(
            generation.get("max_new_tokens"), int
        ) or generation["max_new_tokens"] <= 0:
            raise Pass220HFRAGError("max_new_tokens must be a positive exact integer")

        generated = self.model.generate(**dict(encoded), **generation)
        input_ids = _first_token_sequence(encoded["input_ids"], name="input_ids")
        output_ids = _first_token_sequence(generated, name="generated token IDs")
        if len(output_ids) < len(input_ids):
            raise Pass220HFRAGError(
                "causal model.generate output must include the input prefix before new tokens"
            )
        if output_ids[: len(input_ids)] != input_ids:
            raise Pass220HFRAGError(
                "causal model.generate output does not preserve the input token prefix"
            )
        new_ids = output_ids[len(input_ids) :]
        response_text = self.tokenizer.decode(new_ids, skip_special_tokens=True)
        if not isinstance(response_text, str):
            raise Pass220HFRAGError("tokenizer.decode must return natural-language text")

        selected_hash216 = tuple(
            record["hash216"] for record in retrieval["selected_records"]
        )
        receipt = {
            "schema": SCHEMA,
            "user_prompt_sha256": _sha256_text(user_prompt),
            "query_hash216": retrieval["query_hash216"],
            "retrieved_hash216": selected_hash216,
            "retrieved_record_ids": tuple(
                record["record_id"] for record in retrieval["selected_records"]
            ),
            "context_root_sha256": context_root,
            "context_reused": context_reused,
            "context_characters": retrieval["context_characters"],
            "duplicate_reuse_count": retrieval["duplicate_reuse_count"],
            "omitted_record_count": len(retrieval["omitted_records"]),
            "rendered_prompt_sha256": _sha256_text(rendered_prompt),
            "input_token_count": len(input_ids),
            "generated_token_count": len(new_ids),
            "response_sha256": _sha256_text(response_text),
            "generation_kwargs": generation,
            "hf_call_shape": "tokenizer(...) -> model.generate(...) -> tokenizer.decode(...)",
            "rag_boundary": True,
            "natural_language_egress_only": True,
            "retrieval_authority": "HHS_HASH216",
            "generation_authority": "HUGGING_FACE_COMPATIBLE_CAUSAL_LM",
            "probability_may_select_natural_language_tokens_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
        }
        receipt["receipt_sha256"] = sha256(_stable_json(receipt).encode("utf-8")).hexdigest()

        return {
            "schema": SCHEMA,
            "response": response_text,
            "retrieval": retrieval,
            "receipt": receipt,
        }


__all__ = [
    "DEFAULT_MAX_CONTEXT_CHARACTERS",
    "DEFAULT_MAX_NEW_TOKENS",
    "DEFAULT_TOP_K",
    "Pass220HFRAGError",
    "Pass220HuggingFaceRAGAssistant",
    "RETRIEVAL_SCHEMA",
    "SCHEMA",
    "normalize_retrieval",
]
