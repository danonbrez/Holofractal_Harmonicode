"""Exact changed-line incremental tokenization for the Pass 165 token model.

This module is a repair-forward extension of the Pass 165 tokenizer contract.  It
preserves ``MultimodalTokenizer.tokenize`` semantics while adding a real source
version delta path for text modalities:

* the parent source and token stream are already authenticated/committed by the
  caller;
* exact common prefix/suffix *lines* are reused as observations;
* only changed child lines are lexically scanned;
* unchanged suffix observations are rebased by exact byte and line deltas;
* every child token identity is recomputed under the child source hash, because
  Pass 165 token identity intentionally binds provenance/source identity.

The incremental result can be independently compared with the original full
Pass 165 tokenizer through ``validate_incremental_equivalence``.  No floating
point state, probabilistic matching, fuzzy diff, or semantic approximation is
used.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any, Mapping, Sequence

from hhs_runtime.pass165.ingestion import (
    MAX_TOKENS,
    TEXT_MEDIA,
    TOKENIZER_VERSION,
    IngestionError,
    MultimodalTokenizer,
    SourceObject,
    Token,
    _root,
    canonical_bytes,
)

VERSION = "HHS_PASS_165_INCREMENTAL_TOKENIZER_1.0.0"
RESULT_SCHEMA = "HHS_PASS165_INCREMENTAL_TOKENIZATION_RESULT_V1"
EQUIVALENCE_SCHEMA = "HHS_PASS165_INCREMENTAL_TOKENIZATION_EQUIVALENCE_V1"


@dataclass(frozen=True)
class IncrementalTokenizationResult:
    schema: str
    version: str
    parent_source_hash: str
    child_source_hash: str
    parent_token_stream_root: str
    child_token_stream_root: str
    parent_changed_span: tuple[int, int]
    child_changed_span: tuple[int, int]
    parent_changed_line_range: tuple[int, int]
    child_changed_line_range: tuple[int, int]
    common_prefix_line_count: int
    common_suffix_line_count: int
    reused_parent_observation_count: int
    retokenized_child_token_count: int
    lexically_scanned_child_bytes: int
    child_total_bytes: int
    byte_shift_after_change: int
    line_shift_after_change: int
    tokens: tuple[Token, ...]
    witness_root_hash216: str

    def summary(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "version": self.version,
            "parent_source_hash": self.parent_source_hash,
            "child_source_hash": self.child_source_hash,
            "parent_token_stream_root": self.parent_token_stream_root,
            "child_token_stream_root": self.child_token_stream_root,
            "parent_changed_span": list(self.parent_changed_span),
            "child_changed_span": list(self.child_changed_span),
            "parent_changed_line_range": list(self.parent_changed_line_range),
            "child_changed_line_range": list(self.child_changed_line_range),
            "common_prefix_line_count": self.common_prefix_line_count,
            "common_suffix_line_count": self.common_suffix_line_count,
            "reused_parent_observation_count": self.reused_parent_observation_count,
            "retokenized_child_token_count": self.retokenized_child_token_count,
            "lexically_scanned_child_bytes": self.lexically_scanned_child_bytes,
            "child_total_bytes": self.child_total_bytes,
            "byte_shift_after_change": self.byte_shift_after_change,
            "line_shift_after_change": self.line_shift_after_change,
            "token_count": len(self.tokens),
            "witness_root_hash216": self.witness_root_hash216,
        }


def token_stream_root(tokens: Sequence[Token]) -> str:
    return _root(b"HHS-P165-TOKEN-STREAM-V1\0", [asdict(token) for token in tokens])


def _lines(raw: bytes) -> tuple[bytes, ...]:
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IngestionError("P165_INCREMENTAL_TEXT_UTF8_REQUIRED") from exc
    return tuple(raw.splitlines(keepends=True))


def derive_changed_line_spans(parent_bytes: bytes, child_bytes: bytes) -> dict[str, Any]:
    """Return the smallest whole-line changed region under exact byte equality."""

    parent = bytes(parent_bytes)
    child = bytes(child_bytes)
    if parent == child:
        raise IngestionError("P165_INCREMENTAL_NO_SOURCE_CHANGE")
    parent_lines = _lines(parent)
    child_lines = _lines(child)

    prefix = 0
    limit = min(len(parent_lines), len(child_lines))
    while prefix < limit and parent_lines[prefix] == child_lines[prefix]:
        prefix += 1

    suffix = 0
    parent_remaining = len(parent_lines) - prefix
    child_remaining = len(child_lines) - prefix
    suffix_limit = min(parent_remaining, child_remaining)
    while (
        suffix < suffix_limit
        and parent_lines[len(parent_lines) - 1 - suffix]
        == child_lines[len(child_lines) - 1 - suffix]
    ):
        suffix += 1

    parent_changed_line_end = len(parent_lines) - suffix
    child_changed_line_end = len(child_lines) - suffix
    parent_start = sum(len(line) for line in parent_lines[:prefix])
    child_start = sum(len(line) for line in child_lines[:prefix])
    parent_end = sum(len(line) for line in parent_lines[:parent_changed_line_end])
    child_end = sum(len(line) for line in child_lines[:child_changed_line_end])

    return {
        "schema": "HHS_PASS165_INCREMENTAL_CHANGED_LINE_SPANS_V1",
        "common_prefix_line_count": prefix,
        "common_suffix_line_count": suffix,
        "parent_changed_span": (parent_start, parent_end),
        "child_changed_span": (child_start, child_end),
        "parent_changed_line_range": (prefix, parent_changed_line_end),
        "child_changed_line_range": (prefix, child_changed_line_end),
        "parent_line_count": len(parent_lines),
        "child_line_count": len(child_lines),
        "byte_shift_after_change": child_end - parent_end,
        "line_shift_after_change": child_changed_line_end - parent_changed_line_end,
    }


def _line_index(token: Token) -> int:
    prefix = "line/"
    if not token.structural_path.startswith(prefix):
        raise IngestionError("P165_INCREMENTAL_PARENT_TOKEN_PATH_INVALID")
    try:
        value = int(token.structural_path[len(prefix) :])
    except ValueError as exc:
        raise IngestionError("P165_INCREMENTAL_PARENT_TOKEN_PATH_INVALID") from exc
    if value < 0:
        raise IngestionError("P165_INCREMENTAL_PARENT_TOKEN_PATH_INVALID")
    return value


def _token_from_observation(source: SourceObject, observation: Mapping[str, Any]) -> Token:
    obs = {
        "token_class": str(observation["token_class"]),
        "canonical_payload": str(observation["canonical_payload"]),
        "source_span": tuple(observation["source_span"]),
        "temporal_span": observation.get("temporal_span"),
        "spatial_span": observation.get("spatial_span"),
        "structural_path": str(observation["structural_path"]),
        "local_relations": tuple(observation.get("local_relations") or ()),
    }
    body = {
        "version": TOKENIZER_VERSION,
        "modality": source.detected_media_type,
        **obs,
        "provenance_root": source.source_hash,
    }
    return Token(
        token_id=_root(b"HHS-P165-TOKEN-V1\0", body),
        modality=source.detected_media_type,
        provenance_root=source.source_hash,
        **obs,
    )


def _rebind_parent_token(
    token: Token,
    child_source: SourceObject,
    *,
    byte_shift: int,
    line_shift: int,
) -> Token:
    line = _line_index(token)
    start, end = token.source_span
    shifted_start = start + byte_shift
    shifted_end = end + byte_shift
    if shifted_start < 0 or shifted_end < shifted_start:
        raise IngestionError("P165_INCREMENTAL_REBASED_SOURCE_SPAN_INVALID")
    return _token_from_observation(
        child_source,
        {
            "token_class": token.token_class,
            "canonical_payload": token.canonical_payload,
            "source_span": (shifted_start, shifted_end),
            "temporal_span": token.temporal_span,
            "spatial_span": token.spatial_span,
            "structural_path": f"line/{line + line_shift}",
            "local_relations": token.local_relations,
        },
    )


def incremental_tokenize(
    parent_source: SourceObject,
    parent_tokens: Sequence[Token],
    child_source: SourceObject,
    *,
    tokenizer: MultimodalTokenizer | None = None,
) -> IncrementalTokenizationResult:
    """Tokenize a changed text source by scanning only changed child lines."""

    if parent_source.detected_media_type not in TEXT_MEDIA:
        raise IngestionError("P165_INCREMENTAL_TEXT_MODALITY_REQUIRED")
    if child_source.detected_media_type not in TEXT_MEDIA:
        raise IngestionError("P165_INCREMENTAL_TEXT_MODALITY_REQUIRED")
    if parent_source.detected_media_type != child_source.detected_media_type:
        raise IngestionError("P165_INCREMENTAL_MODALITY_CHANGED")
    if parent_source.provenance != child_source.provenance:
        raise IngestionError("P165_INCREMENTAL_PROVENANCE_CHANGED")
    if parent_source.authorization_scope != child_source.authorization_scope:
        raise IngestionError("P165_INCREMENTAL_AUTHORIZATION_SCOPE_CHANGED")
    if sha256(parent_source.source_bytes).hexdigest() != parent_source.source_hash:
        raise IngestionError("P165_INCREMENTAL_PARENT_SOURCE_HASH_INVALID")
    if sha256(child_source.source_bytes).hexdigest() != child_source.source_hash:
        raise IngestionError("P165_INCREMENTAL_CHILD_SOURCE_HASH_INVALID")

    parent_tokens_tuple = tuple(parent_tokens)
    parent_root = token_stream_root(parent_tokens_tuple)
    spans = derive_changed_line_spans(parent_source.source_bytes, child_source.source_bytes)
    prefix_lines = int(spans["common_prefix_line_count"])
    suffix_lines = int(spans["common_suffix_line_count"])
    parent_line_count = int(spans["parent_line_count"])
    parent_suffix_start_line = parent_line_count - suffix_lines
    byte_shift = int(spans["byte_shift_after_change"])
    line_shift = int(spans["line_shift_after_change"])

    prefix_tokens: list[Token] = []
    suffix_tokens: list[Token] = []
    for token in parent_tokens_tuple:
        line = _line_index(token)
        if line < prefix_lines:
            prefix_tokens.append(
                _rebind_parent_token(token, child_source, byte_shift=0, line_shift=0)
            )
        elif line >= parent_suffix_start_line:
            suffix_tokens.append(
                _rebind_parent_token(
                    token,
                    child_source,
                    byte_shift=byte_shift,
                    line_shift=line_shift,
                )
            )

    child_start, child_end = tuple(spans["child_changed_span"])
    changed_bytes = child_source.source_bytes[child_start:child_end]
    changed_text = changed_bytes.decode("utf-8")
    engine = tokenizer or MultimodalTokenizer()
    observations = engine._text_observations(  # exact inherited lexical semantics
        changed_text, child_source.detected_media_type
    )
    changed_tokens: list[Token] = []
    for observation in observations:
        local_line = int(str(observation["structural_path"]).split("/", 1)[1])
        start, end = tuple(observation["source_span"])
        adjusted = dict(observation)
        adjusted["source_span"] = (start + child_start, end + child_start)
        adjusted["structural_path"] = f"line/{prefix_lines + local_line}"
        changed_tokens.append(_token_from_observation(child_source, adjusted))

    tokens = tuple(prefix_tokens + changed_tokens + suffix_tokens)
    if len(tokens) > MAX_TOKENS:
        raise IngestionError("P165_TOKEN_BOUND")
    for left, right in zip(tokens, tokens[1:]):
        if left.source_span[0] > right.source_span[0]:
            raise IngestionError("P165_INCREMENTAL_TOKEN_ORDER_INVALID")
    child_root = token_stream_root(tokens)
    witness_body = {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "parent_source_hash": parent_source.source_hash,
        "child_source_hash": child_source.source_hash,
        "parent_token_stream_root": parent_root,
        "child_token_stream_root": child_root,
        "parent_changed_span": list(spans["parent_changed_span"]),
        "child_changed_span": list(spans["child_changed_span"]),
        "parent_changed_line_range": list(spans["parent_changed_line_range"]),
        "child_changed_line_range": list(spans["child_changed_line_range"]),
        "common_prefix_line_count": prefix_lines,
        "common_suffix_line_count": suffix_lines,
        "reused_parent_observation_count": len(prefix_tokens) + len(suffix_tokens),
        "retokenized_child_token_count": len(changed_tokens),
        "lexically_scanned_child_bytes": len(changed_bytes),
        "child_total_bytes": len(child_source.source_bytes),
        "byte_shift_after_change": byte_shift,
        "line_shift_after_change": line_shift,
        "token_ids": [token.token_id for token in tokens],
    }
    witness_root = _root(
        b"HHS-P165-INCREMENTAL-TOKENIZATION-V1\0", witness_body
    )
    return IncrementalTokenizationResult(
        schema=RESULT_SCHEMA,
        version=VERSION,
        parent_source_hash=parent_source.source_hash,
        child_source_hash=child_source.source_hash,
        parent_token_stream_root=parent_root,
        child_token_stream_root=child_root,
        parent_changed_span=tuple(spans["parent_changed_span"]),
        child_changed_span=tuple(spans["child_changed_span"]),
        parent_changed_line_range=tuple(spans["parent_changed_line_range"]),
        child_changed_line_range=tuple(spans["child_changed_line_range"]),
        common_prefix_line_count=prefix_lines,
        common_suffix_line_count=suffix_lines,
        reused_parent_observation_count=len(prefix_tokens) + len(suffix_tokens),
        retokenized_child_token_count=len(changed_tokens),
        lexically_scanned_child_bytes=len(changed_bytes),
        child_total_bytes=len(child_source.source_bytes),
        byte_shift_after_change=byte_shift,
        line_shift_after_change=line_shift,
        tokens=tokens,
        witness_root_hash216=witness_root,
    )


def validate_incremental_equivalence(
    result: IncrementalTokenizationResult,
    child_source: SourceObject,
    *,
    tokenizer: MultimodalTokenizer | None = None,
) -> dict[str, Any]:
    """Compare an incremental result with the original full Pass 165 tokenizer."""

    engine = tokenizer or MultimodalTokenizer()
    full_tokens = engine.tokenize(child_source)
    full_root = token_stream_root(full_tokens)
    incremental_rows = [asdict(token) for token in result.tokens]
    full_rows = [asdict(token) for token in full_tokens]
    equal = incremental_rows == full_rows and result.child_token_stream_root == full_root
    body = {
        "schema": EQUIVALENCE_SCHEMA,
        "version": VERSION,
        "equal": equal,
        "child_source_hash": child_source.source_hash,
        "incremental_token_stream_root": result.child_token_stream_root,
        "full_token_stream_root": full_root,
        "incremental_token_count": len(result.tokens),
        "full_token_count": len(full_tokens),
        "token_rows_equal": incremental_rows == full_rows,
        "full_reference_tokenizer": "hhs_runtime.pass165.ingestion.MultimodalTokenizer.tokenize",
        "incremental_tokenizer": "hhs_runtime.pass165.incremental_tokenization.incremental_tokenize",
    }
    body["equivalence_root_hash216"] = _root(
        b"HHS-P165-INCREMENTAL-EQUIVALENCE-V1\0", body
    )
    if not equal:
        raise IngestionError("P165_INCREMENTAL_FULL_TOKENIZATION_MISMATCH")
    return body


__all__ = [
    "VERSION",
    "RESULT_SCHEMA",
    "EQUIVALENCE_SCHEMA",
    "IncrementalTokenizationResult",
    "token_stream_root",
    "derive_changed_line_spans",
    "incremental_tokenize",
    "validate_incremental_equivalence",
]
