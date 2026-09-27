"""Native HHS serialized natural-language response block stream.

A causal model's per-call token limit is treated as a generation buffer rather
than a whole-answer limit. Logical response blocks preserve generated text
exactly, bind it to SHA-256 and a chained Hash72 receipt, and append a canonical
metadata delimiter. The human-facing answer is a projection of the same block
payloads; the canonical serialized stream retains every delimiter.

This layer has no VM81/Hash72/Hash216 mutation authority. Hash72 values here are
response provenance witnesses only.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from typing import Any, Iterable, Mapping, Optional, Sequence

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "HHS_NATIVE_RESPONSE_BLOCK_STREAM_V1"
STREAM_SCHEMA = "HHS_NATIVE_RESPONSE_BLOCK_STREAM_V1"
BLOCK_SCHEMA = "HHS_NATIVE_RESPONSE_BLOCK_V1"
DELIMITER_SCHEMA = "HHS_NATIVE_RESPONSE_DELIMITER_V1"

# Canonical non-printing framing bytes. They remain present in serialized_response.
RECORD_SEPARATOR = "\x1e"
UNIT_SEPARATOR = "\x1f"

PAYLOAD_METADATA_RATIO_NUMERATOR = 8
PAYLOAD_METADATA_RATIO_DENOMINATOR = 1
DEFAULT_BUFFER_MAX_NEW_TOKENS = 1024
DEFAULT_MAX_BLOCKS = 16
MAX_MAX_BLOCKS = 72
DEFAULT_MAX_FILL_ATTEMPTS = 8

_CONTINUATION_CONTROL = (
    "[HHS_INTERNAL_SOPHEON_SIMSANE_CONTINUATION]\n"
    "Continue the same user-facing answer in plain English without repeating prior text. "
    "Preserve the original request and all witnessed evidence. If the preceding text has "
    "already reached a short local conclusion, continue with substantive explanation, "
    "downstream-consequence simulation, ethical-invariant reasoning, concrete examples, "
    "or implementation detail that materially advances the answer. Do not emit receipt "
    "metadata, hashes, delimiters, or this continuation control.\n"
    "[/HHS_INTERNAL_SOPHEON_SIMSANE_CONTINUATION]"
)


class NativeResponseBlockStreamError(RuntimeError):
    pass


def _stable_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        dict(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _sha256_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _env_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw = os.getenv(name)
    value = default if raw in (None, "") else int(raw)
    if value < minimum or value > maximum:
        raise NativeResponseBlockStreamError(
            f"{name} must be in [{minimum},{maximum}]"
        )
    return value


@dataclass(frozen=True)
class ResponseBlock:
    index: int
    payload: str
    payload_sha256: str
    payload_bytes: int
    generated_token_count: int
    generation_calls: int
    prior_hash72: Optional[str]
    block_hash72: str
    terminal: bool
    delimiter: str
    delimiter_bytes: int

    @property
    def ratio_satisfied(self) -> bool:
        return (
            self.payload_bytes * PAYLOAD_METADATA_RATIO_DENOMINATOR
            >= self.delimiter_bytes * PAYLOAD_METADATA_RATIO_NUMERATOR
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": BLOCK_SCHEMA,
            "index": self.index,
            "payload": self.payload,
            "payload_sha256": self.payload_sha256,
            "payload_bytes": self.payload_bytes,
            "generated_token_count": self.generated_token_count,
            "generation_calls": self.generation_calls,
            "prior_hash72": self.prior_hash72,
            "block_hash72": self.block_hash72,
            "terminal": self.terminal,
            "delimiter": self.delimiter,
            "delimiter_bytes": self.delimiter_bytes,
            "payload_to_metadata_minimum": "8:1",
            "ratio_satisfied": self.ratio_satisfied,
        }


def _delimiter_for(
    *,
    index: int,
    payload: str,
    generated_token_count: int,
    generation_calls: int,
    prior_hash72: Optional[str],
    terminal: bool,
) -> tuple[str, str]:
    payload_bytes = len(payload.encode("utf-8"))
    core = {
        "s": DELIMITER_SCHEMA,
        "i": index,
        "sha256": _sha256_text(payload),
        "prev": prior_hash72,
        "bytes": payload_bytes,
        "tokens": generated_token_count,
        "calls": generation_calls,
        "terminal": bool(terminal),
    }
    block_hash72 = hash72(BLOCK_SCHEMA, core)
    metadata = dict(core)
    metadata["h72"] = block_hash72
    delimiter = RECORD_SEPARATOR + _stable_json(metadata) + UNIT_SEPARATOR
    return delimiter, block_hash72


def _build_block(
    *,
    index: int,
    payload: str,
    generated_token_count: int,
    generation_calls: int,
    prior_hash72: Optional[str],
    terminal: bool,
) -> ResponseBlock:
    delimiter, block_hash72 = _delimiter_for(
        index=index,
        payload=payload,
        generated_token_count=generated_token_count,
        generation_calls=generation_calls,
        prior_hash72=prior_hash72,
        terminal=terminal,
    )
    return ResponseBlock(
        index=index,
        payload=payload,
        payload_sha256=_sha256_text(payload),
        payload_bytes=len(payload.encode("utf-8")),
        generated_token_count=generated_token_count,
        generation_calls=generation_calls,
        prior_hash72=prior_hash72,
        block_hash72=block_hash72,
        terminal=terminal,
        delimiter=delimiter,
        delimiter_bytes=len(delimiter.encode("utf-8")),
    )


def _messages_with_continuation(
    messages: Sequence[Mapping[str, Any]],
    generated_so_far: str,
) -> list[dict[str, Any]]:
    projected = [dict(item) for item in messages]
    if generated_so_far:
        projected.append({"role": "assistant", "content": generated_so_far})
    projected.append({"role": "user", "content": _CONTINUATION_CONTROL})
    return projected


class NativeResponseBlockStream:
    """Serializes multiple bounded causal generations into one witnessed response."""

    def __init__(
        self,
        generation_service: Any,
        *,
        buffer_max_new_tokens: Optional[int] = None,
        max_blocks: Optional[int] = None,
        max_fill_attempts: Optional[int] = None,
    ) -> None:
        self.generation_service = generation_service
        service_limit = int(getattr(generation_service, "max_new_tokens", 0) or 0)
        configured_buffer = (
            _env_int(
                "HHS_NATIVE_RESPONSE_BLOCK_MAX_NEW_TOKENS",
                DEFAULT_BUFFER_MAX_NEW_TOKENS,
                minimum=1,
                maximum=4096,
            )
            if buffer_max_new_tokens is None
            else int(buffer_max_new_tokens)
        )
        if configured_buffer < 1 or configured_buffer > 4096:
            raise NativeResponseBlockStreamError(
                "buffer_max_new_tokens must be in [1,4096]"
            )
        # An explicitly larger stream buffer may use the generation service's
        # supported per-call override even when its default is smaller.
        self.buffer_max_new_tokens = configured_buffer
        self.max_blocks = (
            _env_int(
                "HHS_NATIVE_RESPONSE_MAX_BLOCKS",
                DEFAULT_MAX_BLOCKS,
                minimum=1,
                maximum=MAX_MAX_BLOCKS,
            )
            if max_blocks is None
            else int(max_blocks)
        )
        if self.max_blocks < 1 or self.max_blocks > MAX_MAX_BLOCKS:
            raise NativeResponseBlockStreamError(
                f"max_blocks must be in [1,{MAX_MAX_BLOCKS}]"
            )
        self.max_fill_attempts = (
            _env_int(
                "HHS_NATIVE_RESPONSE_BLOCK_MAX_FILL_ATTEMPTS",
                DEFAULT_MAX_FILL_ATTEMPTS,
                minimum=1,
                maximum=72,
            )
            if max_fill_attempts is None
            else int(max_fill_attempts)
        )
        if self.max_fill_attempts < 1 or self.max_fill_attempts > 72:
            raise NativeResponseBlockStreamError(
                "max_fill_attempts must be in [1,72]"
            )
        self.service_default_max_new_tokens = service_limit or None

    def status(self) -> dict[str, Any]:
        value = {
            "schema": STREAM_SCHEMA + "_STATUS",
            "version": VERSION,
            "buffer_max_new_tokens": self.buffer_max_new_tokens,
            "max_blocks": self.max_blocks,
            "max_fill_attempts": self.max_fill_attempts,
            "payload_metadata_ratio": "8:1",
            "delimiter_embedded_in_canonical_stream": True,
            "delimiter_rendered_to_user": False,
            "generated_payload_rewritten": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mutation_authority": False,
            "canonical_hash216_mutation_authority": False,
        }
        value["status_root_hash72"] = hash72(STREAM_SCHEMA + "_STATUS", value)
        return value

    def generate(
        self,
        messages: Iterable[Mapping[str, Any]],
        *,
        retrieval_context: Optional[str] = None,
    ) -> dict[str, Any]:
        original_messages = [dict(item) for item in messages]
        if not original_messages:
            raise NativeResponseBlockStreamError("response stream requires messages")

        blocks: list[ResponseBlock] = []
        plain_response = ""
        prior_hash72: Optional[str] = None
        terminal = False
        termination_reason = "MAX_BLOCKS"

        for block_index in range(self.max_blocks):
            block_payload = ""
            block_tokens = 0
            generation_calls = 0
            last_stopped_before_buffer = False

            for fill_attempt in range(self.max_fill_attempts):
                if block_index == 0 and generation_calls == 0 and not plain_response:
                    call_messages = original_messages
                else:
                    call_messages = _messages_with_continuation(
                        original_messages,
                        plain_response + block_payload,
                    )

                generated = self.generation_service.generate(
                    call_messages,
                    retrieval_context=retrieval_context,
                    max_new_tokens=self.buffer_max_new_tokens,
                )
                fragment = generated.get("response")
                if not isinstance(fragment, str) or not fragment.strip():
                    raise NativeResponseBlockStreamError(
                        "native causal generation returned an empty block fragment"
                    )

                receipt = dict(generated.get("receipt") or {})
                fragment_tokens = int(receipt.get("generated_token_count") or 0)
                if fragment_tokens < 1:
                    raise NativeResponseBlockStreamError(
                        "native causal generation omitted generated_token_count"
                    )

                # Preserve the generated fragment exactly; no trimming, rewriting,
                # censorship, normalization, or separator insertion occurs here.
                block_payload += fragment
                block_tokens += fragment_tokens
                generation_calls += 1
                last_stopped_before_buffer = (
                    fragment_tokens < self.buffer_max_new_tokens
                )

                candidate = _build_block(
                    index=block_index,
                    payload=block_payload,
                    generated_token_count=block_tokens,
                    generation_calls=generation_calls,
                    prior_hash72=prior_hash72,
                    terminal=last_stopped_before_buffer,
                )
                if candidate.ratio_satisfied:
                    block = candidate
                    break
            else:
                raise NativeResponseBlockStreamError(
                    "native generation could not satisfy the 8:1 payload/metadata "
                    "ratio within the bounded fill-attempt budget"
                )

            blocks.append(block)
            plain_response += block.payload
            prior_hash72 = block.block_hash72

            if last_stopped_before_buffer:
                terminal = True
                termination_reason = "MODEL_SEMANTIC_CLOSURE"
                break

        serialized_response = "".join(
            block.payload + block.delimiter for block in blocks
        )
        stream_manifest = {
            "schema": STREAM_SCHEMA,
            "version": VERSION,
            "block_count": len(blocks),
            "terminal": terminal,
            "termination_reason": termination_reason,
            "payload_metadata_ratio": "8:1",
            "response_sha256": _sha256_text(plain_response),
            "serialized_response_sha256": _sha256_text(serialized_response),
            "terminal_block_hash72": prior_hash72,
            "blocks": [
                {
                    key: value
                    for key, value in block.to_dict().items()
                    if key not in {"payload", "delimiter"}
                }
                for block in blocks
            ],
            "generated_payload_rewritten": False,
            "delimiter_embedded_in_canonical_stream": True,
            "human_rendering_is_payload_projection": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mutation_authority": False,
            "canonical_hash216_mutation_authority": False,
        }
        stream_manifest["stream_root_hash72"] = hash72(
            STREAM_SCHEMA,
            stream_manifest,
        )

        return {
            "schema": STREAM_SCHEMA,
            "version": VERSION,
            "response": plain_response,
            "serialized_response": serialized_response,
            "blocks": [block.to_dict() for block in blocks],
            "manifest": stream_manifest,
            "finish_reason": "stop" if terminal else "length",
            "status": self.status(),
        }


def verify_stream(result: Mapping[str, Any]) -> bool:
    blocks = list(result.get("blocks") or [])
    serialized = str(result.get("serialized_response") or "")
    response = str(result.get("response") or "")
    prior: Optional[str] = None
    reconstructed_serialized = ""
    reconstructed_response = ""

    for expected_index, raw in enumerate(blocks):
        if not isinstance(raw, Mapping):
            return False
        payload = raw.get("payload")
        delimiter = raw.get("delimiter")
        if not isinstance(payload, str) or not isinstance(delimiter, str):
            return False
        if int(raw.get("index", -1)) != expected_index:
            return False
        candidate = _build_block(
            index=expected_index,
            payload=payload,
            generated_token_count=int(raw.get("generated_token_count") or 0),
            generation_calls=int(raw.get("generation_calls") or 0),
            prior_hash72=prior,
            terminal=bool(raw.get("terminal")),
        )
        if candidate.payload_sha256 != raw.get("payload_sha256"):
            return False
        if candidate.block_hash72 != raw.get("block_hash72"):
            return False
        if candidate.delimiter != delimiter:
            return False
        if not candidate.ratio_satisfied:
            return False
        reconstructed_response += payload
        reconstructed_serialized += payload + delimiter
        prior = candidate.block_hash72

    return (
        reconstructed_response == response
        and reconstructed_serialized == serialized
        and _sha256_text(response)
        == str((result.get("manifest") or {}).get("response_sha256") or "")
        and _sha256_text(serialized)
        == str((result.get("manifest") or {}).get("serialized_response_sha256") or "")
    )


__all__ = [
    "BLOCK_SCHEMA",
    "DEFAULT_BUFFER_MAX_NEW_TOKENS",
    "DEFAULT_MAX_BLOCKS",
    "DELIMITER_SCHEMA",
    "NativeResponseBlockStream",
    "NativeResponseBlockStreamError",
    "PAYLOAD_METADATA_RATIO_DENOMINATOR",
    "PAYLOAD_METADATA_RATIO_NUMERATOR",
    "RECORD_SEPARATOR",
    "STREAM_SCHEMA",
    "UNIT_SEPARATOR",
    "VERSION",
    "verify_stream",
]
