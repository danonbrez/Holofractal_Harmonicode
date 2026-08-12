"""Pass 217 Checkpoint 7 content-addressed reuse and incremental tokenization.

Checkpoint 7 connects two Pass 214/215 REQUIRED classes:

* ``content_addressed_source_reuse`` -> Pass 165
  ``MultimodalLearningService.ingest_source`` on an already committed identity;
* ``incremental_tokenization`` -> the Pass 165 repair extension
  ``hhs_runtime.pass165.incremental_tokenization.incremental_tokenize``.

The incremental path is exact and text-domain bounded.  It requires an already
committed parent source/token stream, derives the smallest whole-line changed
region, reuses unchanged parent observations, lexically scans only changed child
lines, rebases shifted suffix observations, recomputes child token identities
under the child source hash, and proves equality against the original full Pass
165 tokenizer.  Stale parents, malformed spans, modality/scope changes, partial
context, or equality failure all fail closed.

No source is newly committed by this preflight bridge.
"""
from __future__ import annotations

import base64
import binascii
from hashlib import sha256
from typing import Any, Dict, Iterable, List, Mapping, Optional

from hhs_runtime.hhs_cumulative_execution_authority_v1 import (
    ACTIVE_IN_PATH,
    EXPLICITLY_SUPERSEDED,
    NOT_APPLICABLE,
    build_authority_reachability,
)
from hhs_runtime.hhs_pass217_checkpoint6_retrieval_reuse_v1 import (
    CHECKPOINT6_REQUIRED_AUTHORITIES,
    build_checkpoint6_inherited_authority_reachability,
)


VERSION = "PASS_217_CUMULATIVE_EXECUTION_COMPOSER_CHECKPOINT_7_V2"
CONTENT_SOURCE_REQUEST_SCHEMA = "HHS_PASS217_CONTENT_ADDRESSED_SOURCE_REUSE_REQUEST_V1"
INCREMENTAL_TOKENIZATION_REQUEST_SCHEMA = "HHS_PASS217_INCREMENTAL_TOKENIZATION_REQUEST_V1"
CHECKPOINT7_AUTHORITIES = (
    "content_addressed_source_reuse",
    "incremental_tokenization",
)
CHECKPOINT7_REQUIRED_AUTHORITIES = CHECKPOINT6_REQUIRED_AUTHORITIES + CHECKPOINT7_AUTHORITIES

INCREMENTAL_TOKENIZATION_MARKERS = frozenset(
    {
        "incremental_tokenization",
        "parent_source_hash",
        "parent_token_stream_root",
        "source_version_parent",
        "changed_regions",
        "changed_source_spans",
        "token_delta",
    }
)

CHECKPOINT7_AUTHORITY_MAP: Dict[str, Dict[str, Any]] = {
    "content_addressed_source_reuse": {
        "origin_pass": 165,
        "module": "hhs_runtime.pass165.ingestion",
        "symbol": "MultimodalLearningService.ingest_source",
        "callable_role": "content-addressed committed-source lookup and reuse receipt",
        "mutation_permitted_in_preflight": False,
        "reuse_branch_required": True,
    },
    "incremental_tokenization": {
        "origin_pass": 165,
        "repair_extension_pass": 217,
        "module": "hhs_runtime.pass165.incremental_tokenization",
        "symbol": "incremental_tokenize",
        "reference_module": "hhs_runtime.pass165.ingestion",
        "reference_symbol": "MultimodalTokenizer.tokenize",
        "callable_role": (
            "exact changed-line source tokenization with unchanged observation reuse, "
            "suffix span/path rebasing, and child-source token identity recomputation"
        ),
        "incremental_delta_callable_proven": True,
        "full_source_equivalence_validator": (
            "hhs_runtime.pass165.incremental_tokenization.validate_incremental_equivalence"
        ),
        "changed_region_granularity": "WHOLE_UTF8_TEXT_LINES",
        "text_modalities_only": True,
        "parent_committed_receipt_required": True,
        "parent_token_stream_root_required": True,
        "declared_changed_spans_must_equal_derived_spans": True,
        "mutation_permitted_in_preflight": False,
        "floating_point_authority": False,
    },
}


def _walk_mappings(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk_mappings(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _walk_mappings(child)


def _unique_mappings(values: Iterable[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    seen: set[int] = set()
    output: List[Mapping[str, Any]] = []
    for value in values:
        marker = id(value)
        if marker in seen:
            continue
        seen.add(marker)
        output.append(value)
    return output


def _content_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    body = dict(payload or {})
    found: List[Mapping[str, Any]] = []
    for mapping in _walk_mappings(body):
        named = mapping.get("content_addressed_source_reuse")
        if isinstance(named, Mapping):
            found.append(named)
        if mapping.get("schema") == CONTENT_SOURCE_REQUEST_SCHEMA:
            found.append(mapping)
    return _unique_mappings(found)


def _incremental_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    body = dict(payload or {})
    found: List[Mapping[str, Any]] = []
    for mapping in _walk_mappings(body):
        named = mapping.get("incremental_tokenization")
        if isinstance(named, Mapping):
            found.append(named)
        if mapping.get("schema") == INCREMENTAL_TOKENIZATION_REQUEST_SCHEMA:
            found.append(mapping)
    return _unique_mappings(found)


def _incremental_markers(payload: Optional[Mapping[str, Any]]) -> tuple[str, ...]:
    found: set[str] = set()
    for mapping in _walk_mappings(dict(payload or {})):
        for key in mapping:
            text = str(key)
            if text in INCREMENTAL_TOKENIZATION_MARKERS:
                found.add(text)
    return tuple(sorted(found))


def content_reuse_context_facts(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    candidates = _content_candidates(payload)
    exact = [row for row in candidates if row.get("schema") == CONTENT_SOURCE_REQUEST_SCHEMA]
    incremental_candidates = _incremental_candidates(payload)
    incremental_exact = [
        row
        for row in incremental_candidates
        if row.get("schema") == INCREMENTAL_TOKENIZATION_REQUEST_SCHEMA
    ]
    markers = _incremental_markers(payload)
    return {
        "schema": "HHS_PASS217_CONTENT_REUSE_APPLICABILITY_FACTS_V2",
        "content_source_domain_present": bool(candidates),
        "candidate_bundle_count": len(candidates),
        "exact_request_schema_count": len(exact),
        "candidate_bundle_unique": len(candidates) == 1,
        "exact_request_unique": len(candidates) == 1 and len(exact) == 1,
        "incremental_tokenization_domain_present": bool(markers),
        "incremental_tokenization_markers": list(markers),
        "incremental_candidate_bundle_count": len(incremental_candidates),
        "incremental_exact_request_schema_count": len(incremental_exact),
        "incremental_exact_request_unique": (
            len(incremental_candidates) == 1 and len(incremental_exact) == 1
        ),
        "incremental_delta_callable_proven": True,
        "request_schema": CONTENT_SOURCE_REQUEST_SCHEMA,
        "incremental_request_schema": INCREMENTAL_TOKENIZATION_REQUEST_SCHEMA,
    }


def _decode_source_bytes(request: Mapping[str, Any]) -> bytes:
    has_text = "source_text" in request
    has_b64 = "source_bytes_b64" in request
    if has_text == has_b64:
        raise ValueError("REJECT_PASS165_SOURCE_ENCODING_AMBIGUOUS_OR_MISSING")
    if has_text:
        text = request.get("source_text")
        if not isinstance(text, str) or not text:
            raise ValueError("REJECT_PASS165_SOURCE_TEXT_INVALID")
        return text.encode("utf-8")
    encoded = request.get("source_bytes_b64")
    if not isinstance(encoded, str) or not encoded:
        raise ValueError("REJECT_PASS165_SOURCE_BASE64_INVALID")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("REJECT_PASS165_SOURCE_BASE64_INVALID") from exc
    if not raw:
        raise ValueError("REJECT_PASS165_SOURCE_BYTES_EMPTY")
    return raw


def _decode_version_bytes(request: Mapping[str, Any], prefix: str) -> bytes:
    text_key = f"{prefix}_source_text"
    b64_key = f"{prefix}_source_bytes_b64"
    has_text = text_key in request
    has_b64 = b64_key in request
    if has_text == has_b64:
        raise ValueError(f"REJECT_INCREMENTAL_{prefix.upper()}_SOURCE_ENCODING_AMBIGUOUS_OR_MISSING")
    if has_text:
        text = request.get(text_key)
        if not isinstance(text, str) or not text:
            raise ValueError(f"REJECT_INCREMENTAL_{prefix.upper()}_SOURCE_TEXT_INVALID")
        return text.encode("utf-8")
    encoded = request.get(b64_key)
    if not isinstance(encoded, str) or not encoded:
        raise ValueError(f"REJECT_INCREMENTAL_{prefix.upper()}_SOURCE_BASE64_INVALID")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"REJECT_INCREMENTAL_{prefix.upper()}_SOURCE_BASE64_INVALID") from exc
    if not raw:
        raise ValueError(f"REJECT_INCREMENTAL_{prefix.upper()}_SOURCE_BYTES_EMPTY")
    return raw


def _active_failure(authority_id: str, reason: str, facts: Mapping[str, Any]) -> Dict[str, Any]:
    info = CHECKPOINT7_AUTHORITY_MAP[authority_id]
    return {
        "observed": False,
        "path": ["kernel_runtime_autocomposer", authority_id],
        "traversal_witness": {
            "schema": "HHS_PASS217_CHECKPOINT7_TRAVERSAL_FAILURE_V2",
            "status": "REJECT_CHECKPOINT7_INHERITED_TRAVERSAL",
            "authority_id": authority_id,
            "reason": str(reason),
            "authority_map": dict(info),
            "applicability_facts": dict(facts),
        },
        "witness_root": "",
    }


def _load_source_reuse_service(source_reuse_service: Any = None) -> Any:
    if source_reuse_service is not None:
        return source_reuse_service
    from hhs_runtime.pass165.ingestion import DEFAULT_MULTIMODAL_LEARNING_SERVICE

    return DEFAULT_MULTIMODAL_LEARNING_SERVICE


def observe_content_addressed_source_reuse(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    source_reuse_service: Any = None,
) -> Dict[str, Any]:
    """Traverse Pass 165's existing-source reuse branch without new mutation."""

    applicability = dict(facts or content_reuse_context_facts(payload))
    candidates = _content_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "content_addressed_source_reuse",
            "REJECT_PASS165_CONTENT_REUSE_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != CONTENT_SOURCE_REQUEST_SCHEMA:
        return _active_failure(
            "content_addressed_source_reuse",
            "REJECT_PASS165_CONTENT_REUSE_REQUEST_SCHEMA",
            applicability,
        )

    try:
        raw = _decode_source_bytes(request)
        provenance = request.get("provenance")
        authorization_scope = request.get("authorization_scope")
        declared_media_type = request.get("declared_media_type")
        if not isinstance(provenance, str) or not provenance:
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_PROVENANCE_MISSING")
        if not isinstance(authorization_scope, str) or not authorization_scope:
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_AUTHORIZATION_MISSING")
        if declared_media_type is not None and not isinstance(declared_media_type, str):
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_MEDIA_TYPE_INVALID")

        expected_source_hash = sha256(raw).hexdigest()
        declared_hash = request.get("expected_source_hash")
        if declared_hash is not None and declared_hash != expected_source_hash:
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_EXPECTED_HASH_MISMATCH")

        service = _load_source_reuse_service(source_reuse_service)
        source = service.capture_source(
            raw,
            declared_media_type=declared_media_type,
            provenance=provenance,
            authorization_scope=authorization_scope,
        )
        if source.source_hash != expected_source_hash:
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_SOURCE_HASH_MISMATCH")
        if source.provenance != provenance or source.authorization_scope != authorization_scope:
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_SCOPE_OR_PROVENANCE_MISMATCH")
        normalized_declared = declared_media_type.upper() if declared_media_type else None
        if source.declared_media_type != normalized_declared:
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_DECLARED_MEDIA_MISMATCH")

        try:
            prior_receipt = service.get_ingestion_receipt(source.source_hash)
        except Exception as exc:
            if getattr(exc, "classification", None) == "P165_RECEIPT_NOT_FOUND":
                observed = dict(applicability)
                observed.update(
                    {
                        "source_hash": source.source_hash,
                        "committed_source_receipt_present": False,
                        "content_addressed_reuse_candidate_present": False,
                    }
                )
                return {
                    "mechanically_proven": True,
                    "predicate": "committed_source_receipt_present == false",
                    "observed_facts": observed,
                    "reason": (
                        "exact Pass 165 source hash has no committed ingestion receipt; "
                        "there is no content-addressed source reuse candidate"
                    ),
                }
            raise

        before = service.status()
        output = service.ingest_source(
            raw,
            declared_media_type=declared_media_type,
            provenance=provenance,
            authorization_scope=authorization_scope,
        )
        after = service.status()
        receipt = output.get("receipt")
        if not isinstance(receipt, Mapping):
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_RECEIPT_MISSING")
        if receipt.get("reused") is not True:
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_BRANCH_NOT_TAKEN")
        if receipt.get("classification") != "P165_CONTENT_ADDRESSED_SOURCE_REUSED":
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_CLASSIFICATION")
        receipt_root = str(receipt.get("receipt_hash72") or "").strip()
        if not receipt_root:
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_RECEIPT_ROOT_MISSING")
        if receipt_root != prior_receipt.get("receipt_hash72"):
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_RECEIPT_IDENTITY_CHANGED")
        source_summary = output.get("source")
        if not isinstance(source_summary, Mapping):
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_SOURCE_SUMMARY_MISSING")
        if source_summary.get("source_hash") != expected_source_hash:
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_OUTPUT_HASH_MISMATCH")

        before_vm81 = dict(before.get("vm81") or {})
        after_vm81 = dict(after.get("vm81") or {})
        if before.get("ingestion_epoch") != after.get("ingestion_epoch"):
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_MUTATED_INGESTION_EPOCH")
        if before_vm81.get("state_hash72") != after_vm81.get("state_hash72"):
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_MUTATED_VM81_STATE")
        if before.get("sources") != after.get("sources"):
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_MUTATED_SOURCE_COUNT")
        if before.get("weights") != after.get("weights"):
            raise ValueError("REJECT_PASS165_CONTENT_REUSE_MUTATED_WEIGHT_COUNT")

        info = CHECKPOINT7_AUTHORITY_MAP["content_addressed_source_reuse"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "content_addressed_source_reuse",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_CONTENT_ADDRESSED_SOURCE_REUSE_TRAVERSAL_V1",
                "status": "ADMIT_CONTENT_ADDRESSED_SOURCE_REUSE_TRAVERSAL",
                "repository_native_callable": dict(info),
                "source_hash": expected_source_hash,
                "source_id": source_summary.get("source_id"),
                "detected_media_type": source_summary.get("detected_media_type"),
                "byte_length": source_summary.get("byte_length"),
                "receipt_hash72": receipt_root,
                "content_addressed_source_reused": True,
                "token_count": output.get("token_count"),
                "chunk_count": output.get("chunk_count"),
                "projection_hash72": output.get("projection_hash72"),
                "preflight_mutation_performed": False,
                "ingestion_epoch_unchanged": True,
                "vm81_state_unchanged": True,
                "applicability_facts": applicability,
            },
            "witness_root": receipt_root,
        }
    except Exception as exc:
        return _active_failure(
            "content_addressed_source_reuse",
            f"REJECT_PASS165_CONTENT_REUSE_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def observe_incremental_tokenization(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    source_reuse_service: Any = None,
) -> Dict[str, Any]:
    """Traverse exact Pass 165 changed-line incremental tokenization."""

    applicability = dict(facts or content_reuse_context_facts(payload))
    candidates = _incremental_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "incremental_tokenization",
            "REJECT_INCREMENTAL_TOKENIZATION_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != INCREMENTAL_TOKENIZATION_REQUEST_SCHEMA:
        return _active_failure(
            "incremental_tokenization",
            "REJECT_INCREMENTAL_TOKENIZATION_REQUEST_SCHEMA",
            applicability,
        )

    try:
        from hhs_runtime.pass165.incremental_tokenization import (
            incremental_tokenize,
            validate_incremental_equivalence,
        )

        parent_bytes = _decode_version_bytes(request, "parent")
        child_bytes = _decode_version_bytes(request, "child")
        parent_hash = sha256(parent_bytes).hexdigest()
        child_hash = sha256(child_bytes).hexdigest()
        if request.get("parent_source_hash") != parent_hash:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_PARENT_SOURCE_HASH_MISMATCH")
        expected_child_hash = request.get("expected_child_source_hash")
        if expected_child_hash is not None and expected_child_hash != child_hash:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_CHILD_SOURCE_HASH_MISMATCH")
        parent_token_root = request.get("parent_token_stream_root")
        if not isinstance(parent_token_root, str) or len(parent_token_root) != 64:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_PARENT_TOKEN_ROOT_REQUIRED")
        declared_spans = request.get("changed_source_spans")
        if not isinstance(declared_spans, Mapping):
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_CHANGED_SPANS_REQUIRED")
        if set(declared_spans) != {"parent", "child"}:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_CHANGED_SPANS_SCHEMA")
        for name in ("parent", "child"):
            span = declared_spans.get(name)
            if (
                not isinstance(span, (list, tuple))
                or len(span) != 2
                or any(not isinstance(value, int) or isinstance(value, bool) for value in span)
                or span[0] < 0
                or span[1] < span[0]
            ):
                raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_CHANGED_SPAN_INVALID")

        provenance = request.get("provenance")
        authorization_scope = request.get("authorization_scope")
        declared_media_type = request.get("declared_media_type")
        if not isinstance(provenance, str) or not provenance:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_PROVENANCE_MISSING")
        if not isinstance(authorization_scope, str) or not authorization_scope:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_AUTHORIZATION_MISSING")
        if declared_media_type is not None and not isinstance(declared_media_type, str):
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_MEDIA_TYPE_INVALID")

        service = _load_source_reuse_service(source_reuse_service)
        before = service.status()
        receipt = service.get_ingestion_receipt(parent_hash)
        if receipt.get("token_root") != parent_token_root:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_PARENT_RECEIPT_TOKEN_ROOT_MISMATCH")
        parent_result = service.analyze(
            parent_bytes,
            declared_media_type=declared_media_type,
            provenance=provenance,
            authorization_scope=authorization_scope,
        )
        if parent_result.source.source_hash != parent_hash:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_PARENT_RESULT_HASH_MISMATCH")
        if parent_result.token_stream_root != parent_token_root:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_STALE_PARENT_TOKEN_ROOT")
        child_source = service.capture_source(
            child_bytes,
            declared_media_type=declared_media_type,
            provenance=provenance,
            authorization_scope=authorization_scope,
        )
        if child_source.source_hash != child_hash:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_CHILD_CAPTURE_HASH_MISMATCH")
        result = incremental_tokenize(
            parent_result.source,
            parent_result.tokens,
            child_source,
        )
        if list(result.parent_changed_span) != list(declared_spans["parent"]):
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_PARENT_CHANGED_SPAN_MISMATCH")
        if list(result.child_changed_span) != list(declared_spans["child"]):
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_CHILD_CHANGED_SPAN_MISMATCH")
        expected_child_root = request.get("expected_child_token_stream_root")
        if expected_child_root is not None and expected_child_root != result.child_token_stream_root:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_CHILD_TOKEN_ROOT_MISMATCH")
        equivalence = validate_incremental_equivalence(result, child_source)
        if equivalence.get("equal") is not True:
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_FULL_REFERENCE_MISMATCH")
        after = service.status()
        if before.get("ingestion_epoch") != after.get("ingestion_epoch"):
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_MUTATED_INGESTION_EPOCH")
        if before.get("sources") != after.get("sources"):
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_MUTATED_SOURCE_COUNT")
        if before.get("weights") != after.get("weights"):
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_MUTATED_WEIGHT_COUNT")
        if (before.get("vm81") or {}).get("state_hash72") != (after.get("vm81") or {}).get("state_hash72"):
            raise ValueError("REJECT_INCREMENTAL_TOKENIZATION_MUTATED_VM81_STATE")

        info = CHECKPOINT7_AUTHORITY_MAP["incremental_tokenization"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "incremental_tokenization",
                f"{info['module']}.{info['symbol']}",
                info["full_source_equivalence_validator"],
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_INCREMENTAL_TOKENIZATION_TRAVERSAL_V1",
                "status": "ADMIT_INCREMENTAL_TOKENIZATION_TRAVERSAL",
                "repository_native_callable": dict(info),
                "parent_source_hash": parent_hash,
                "child_source_hash": child_hash,
                "parent_receipt_hash72": receipt.get("receipt_hash72"),
                "parent_token_stream_root": parent_token_root,
                "child_token_stream_root": result.child_token_stream_root,
                "parent_changed_span": list(result.parent_changed_span),
                "child_changed_span": list(result.child_changed_span),
                "parent_changed_line_range": list(result.parent_changed_line_range),
                "child_changed_line_range": list(result.child_changed_line_range),
                "common_prefix_line_count": result.common_prefix_line_count,
                "common_suffix_line_count": result.common_suffix_line_count,
                "reused_parent_observation_count": result.reused_parent_observation_count,
                "retokenized_child_token_count": result.retokenized_child_token_count,
                "lexically_scanned_child_bytes": result.lexically_scanned_child_bytes,
                "child_total_bytes": result.child_total_bytes,
                "byte_shift_after_change": result.byte_shift_after_change,
                "line_shift_after_change": result.line_shift_after_change,
                "incremental_witness_root_hash216": result.witness_root_hash216,
                "full_reference_token_stream_root": equivalence["full_token_stream_root"],
                "equivalence_root_hash216": equivalence["equivalence_root_hash216"],
                "incremental_equals_full_tokenization": True,
                "unchanged_regions_lexically_rescanned_by_incremental_callable": False,
                "full_reference_used_for_equality_validation": True,
                "preflight_mutation_performed": False,
                "ingestion_epoch_unchanged": True,
                "vm81_state_unchanged": True,
                "applicability_facts": applicability,
            },
            "witness_root": result.witness_root_hash216,
        }
    except Exception as exc:
        return _active_failure(
            "incremental_tokenization",
            f"REJECT_INCREMENTAL_TOKENIZATION_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def _import_prior_decisions(
    record: Mapping[str, Any],
    active: Dict[str, Mapping[str, Any]],
    not_applicable: Dict[str, Mapping[str, Any]],
    superseded: Dict[str, Mapping[str, Any]],
) -> None:
    for row in record.get("decisions", []) or []:
        if not isinstance(row, Mapping):
            continue
        authority_id = str(row.get("authority_id") or "")
        proof = row.get("proof")
        if not authority_id or not isinstance(proof, Mapping):
            continue
        state = row.get("state")
        if state == ACTIVE_IN_PATH or "observed" in proof:
            active[authority_id] = dict(proof)
        elif state == NOT_APPLICABLE or "mechanically_proven" in proof:
            not_applicable[authority_id] = dict(proof)
        elif state == EXPLICITLY_SUPERSEDED or "later_pass" in proof:
            superseded[authority_id] = dict(proof)


def build_checkpoint7_inherited_authority_reachability(
    preflight: Mapping[str, Any],
    surface: Mapping[str, Any],
    payload: Optional[Mapping[str, Any]] = None,
    *,
    semantic_cache: Any = None,
    retrieval_runtime: Any = None,
    pattern_repo_root: Any = None,
    source_reuse_service: Any = None,
) -> Dict[str, Any]:
    """Compose Checkpoint 7 over the validated Checkpoint 6 reachability slice."""

    prior = build_checkpoint6_inherited_authority_reachability(
        preflight,
        surface,
        payload,
        semantic_cache=semantic_cache,
        retrieval_runtime=retrieval_runtime,
        pattern_repo_root=pattern_repo_root,
    )
    active: Dict[str, Mapping[str, Any]] = {}
    not_applicable: Dict[str, Mapping[str, Any]] = {}
    superseded: Dict[str, Mapping[str, Any]] = {}
    _import_prior_decisions(prior, active, not_applicable, superseded)

    facts = content_reuse_context_facts(payload)
    if facts["content_source_domain_present"] is False:
        not_applicable["content_addressed_source_reuse"] = {
            "mechanically_proven": True,
            "predicate": "content_source_domain_present == false",
            "observed_facts": facts,
            "reason": "operation payload contains no Pass 165 content-addressed source reuse domain",
        }
    else:
        content_proof = observe_content_addressed_source_reuse(
            payload,
            facts=facts,
            source_reuse_service=source_reuse_service,
        )
        if "mechanically_proven" in content_proof:
            not_applicable["content_addressed_source_reuse"] = content_proof
        else:
            active["content_addressed_source_reuse"] = content_proof

    if facts["incremental_tokenization_domain_present"] is False:
        not_applicable["incremental_tokenization"] = {
            "mechanically_proven": True,
            "predicate": "incremental_tokenization_domain_present == false",
            "observed_facts": facts,
            "reason": (
                "operation contains no predecessor source/token stream or changed-region "
                "contract requiring incremental tokenization"
            ),
        }
    else:
        active["incremental_tokenization"] = observe_incremental_tokenization(
            payload,
            facts=facts,
            source_reuse_service=source_reuse_service,
        )

    operation_id = str(preflight.get("operation") or surface.get("symbol") or "operation")
    record = build_authority_reachability(
        operation_id,
        active_in_path=active,
        not_applicable=not_applicable,
        explicitly_superseded=superseded,
        required_authorities=CHECKPOINT7_REQUIRED_AUTHORITIES,
    )
    record["checkpoint_scope"] = list(CHECKPOINT7_REQUIRED_AUTHORITIES)
    record["checkpoint7_authority_map"] = {
        key: dict(value) for key, value in CHECKPOINT7_AUTHORITY_MAP.items()
    }
    record["content_reuse_applicability_facts"] = facts
    for key in (
        "continuation_applicability_facts",
        "pattern_cache_applicability_facts",
        "retrieval_reuse_applicability_facts",
        "checkpoint6_native_callable_map",
    ):
        if key in prior:
            value = prior[key]
            record[key] = dict(value) if isinstance(value, Mapping) else value
    record["prior_checkpoint_reachability_root_hash72"] = prior.get(
        "reachability_root_hash72"
    )
    record["checkpoint"] = 7
    return record


__all__ = [
    "VERSION",
    "CONTENT_SOURCE_REQUEST_SCHEMA",
    "INCREMENTAL_TOKENIZATION_REQUEST_SCHEMA",
    "CHECKPOINT7_AUTHORITIES",
    "CHECKPOINT7_REQUIRED_AUTHORITIES",
    "CHECKPOINT7_AUTHORITY_MAP",
    "INCREMENTAL_TOKENIZATION_MARKERS",
    "content_reuse_context_facts",
    "observe_content_addressed_source_reuse",
    "observe_incremental_tokenization",
    "build_checkpoint7_inherited_authority_reachability",
]
