"""Pass 217 Checkpoint 8 sparse projection and exact delta-frontier composition.

Checkpoint 8 extends the validated Checkpoint 7 authority slice with the next
Pass 214/215 frozen classes:

* sparse_5184_projection -> Pass 165 ``MultimodalLearningService.project_5184``;
* dependency_complete_frontier -> Pass 215 Iteration 4
  ``execute_continuation_delta`` changed-coordinate to Q4-block frontier;
* residual_only_processing -> the same Pass 215 Iteration 4 delta call, which
  computes sparse W*delta(input) updates without full-row recomputation.

The two Pass 215 classes are separate witnesses from one inherited delta call,
not duplicate implementations. Absent domains are mechanically
NOT_APPLICABLE. Partial or malformed applicable context fails closed.
"""

from __future__ import annotations

import base64
import binascii
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from hhs_runtime.hhs_cumulative_execution_authority_v1 import (
    ACTIVE_IN_PATH,
    EXPLICITLY_SUPERSEDED,
    NOT_APPLICABLE,
    build_authority_reachability,
)
from hhs_runtime.hhs_pass217_checkpoint7_content_reuse_v1 import (
    CHECKPOINT7_REQUIRED_AUTHORITIES,
    build_checkpoint7_inherited_authority_reachability,
)


VERSION = "PASS_217_CUMULATIVE_EXECUTION_COMPOSER_CHECKPOINT_8_V1"
SPARSE_PROJECTION_REQUEST_SCHEMA = "HHS_PASS217_SPARSE_5184_PROJECTION_REQUEST_V1"
LINEAR_DELTA_REQUEST_SCHEMA = "HHS_PASS217_EXACT_LINEAR_CONTINUATION_DELTA_REQUEST_V1"

CHECKPOINT8_AUTHORITIES = (
    "sparse_5184_projection",
    "dependency_complete_frontier",
    "residual_only_processing",
)
CHECKPOINT8_REQUIRED_AUTHORITIES = CHECKPOINT7_REQUIRED_AUTHORITIES + CHECKPOINT8_AUTHORITIES

CHECKPOINT8_AUTHORITY_MAP: Dict[str, Dict[str, Any]] = {
    "sparse_5184_projection": {
        "origin_pass": 165,
        "module": "hhs_runtime.pass165.ingestion",
        "symbol": "MultimodalLearningService.project_5184",
        "callable_role": "deterministic sparse token/edge projection into one 81x64 frame",
        "frame_coordinates": 5184,
        "frame_bytes": 648,
        "mutation_authority": False,
    },
    "dependency_complete_frontier": {
        "origin_pass": 215,
        "origin_iteration": 4,
        "module": "hhs_backend.runtime.hhs_pass215_iteration4_exact_linear_execution_v1",
        "symbol": "execute_continuation_delta",
        "callable_role": "changed input coordinates mapped to affected Q4 block frontier",
        "benchmark_authority_only": True,
        "mutation_authority": False,
    },
    "residual_only_processing": {
        "origin_pass": 215,
        "origin_iteration": 4,
        "module": "hhs_backend.runtime.hhs_pass215_iteration4_exact_linear_execution_v1",
        "symbol": "execute_continuation_delta",
        "callable_role": "sparse exact W times input delta accumulation over parent output",
        "benchmark_authority_only": True,
        "mutation_authority": False,
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


def _request_candidates(
    payload: Optional[Mapping[str, Any]],
    *,
    named_key: str,
    schema: str,
) -> List[Mapping[str, Any]]:
    found: List[Mapping[str, Any]] = []
    for mapping in _walk_mappings(dict(payload or {})):
        named = mapping.get(named_key)
        if isinstance(named, Mapping):
            found.append(named)
        if mapping.get("schema") == schema:
            found.append(mapping)
    return _unique_mappings(found)


def _projection_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="sparse_5184_projection",
        schema=SPARSE_PROJECTION_REQUEST_SCHEMA,
    )


def _delta_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="linear_continuation_delta",
        schema=LINEAR_DELTA_REQUEST_SCHEMA,
    )


def checkpoint8_context_facts(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    projection = _projection_candidates(payload)
    delta = _delta_candidates(payload)
    exact_projection = [
        row for row in projection if row.get("schema") == SPARSE_PROJECTION_REQUEST_SCHEMA
    ]
    exact_delta = [row for row in delta if row.get("schema") == LINEAR_DELTA_REQUEST_SCHEMA]
    return {
        "schema": "HHS_PASS217_CHECKPOINT8_APPLICABILITY_FACTS_V1",
        "sparse_projection_domain_present": bool(projection),
        "sparse_projection_candidate_count": len(projection),
        "sparse_projection_exact_schema_count": len(exact_projection),
        "linear_delta_domain_present": bool(delta),
        "linear_delta_candidate_count": len(delta),
        "linear_delta_exact_schema_count": len(exact_delta),
        "sparse_projection_request_schema": SPARSE_PROJECTION_REQUEST_SCHEMA,
        "linear_delta_request_schema": LINEAR_DELTA_REQUEST_SCHEMA,
    }


def _active_failure(
    authority_id: str,
    reason: str,
    facts: Mapping[str, Any],
) -> Dict[str, Any]:
    return {
        "observed": False,
        "path": ["kernel_runtime_autocomposer", authority_id],
        "traversal_witness": {
            "schema": "HHS_PASS217_CHECKPOINT8_TRAVERSAL_FAILURE_V1",
            "status": "REJECT_CHECKPOINT8_INHERITED_TRAVERSAL",
            "authority_id": authority_id,
            "reason": str(reason),
            "authority_map": dict(CHECKPOINT8_AUTHORITY_MAP[authority_id]),
            "applicability_facts": dict(facts),
        },
        "witness_root": "",
    }


def _decode_source_bytes(request: Mapping[str, Any]) -> bytes:
    has_text = "source_text" in request
    has_b64 = "source_bytes_b64" in request
    if has_text == has_b64:
        raise ValueError("REJECT_PASS165_PROJECTION_SOURCE_ENCODING_AMBIGUOUS_OR_MISSING")
    if has_text:
        text = request.get("source_text")
        if not isinstance(text, str) or not text:
            raise ValueError("REJECT_PASS165_PROJECTION_SOURCE_TEXT_INVALID")
        return text.encode("utf-8")
    encoded = request.get("source_bytes_b64")
    if not isinstance(encoded, str) or not encoded:
        raise ValueError("REJECT_PASS165_PROJECTION_SOURCE_BASE64_INVALID")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("REJECT_PASS165_PROJECTION_SOURCE_BASE64_INVALID") from exc
    if not raw:
        raise ValueError("REJECT_PASS165_PROJECTION_SOURCE_BYTES_EMPTY")
    return raw


def _load_projection_service(projection_service: Any = None) -> Any:
    if projection_service is not None:
        return projection_service
    from hhs_runtime.pass165.ingestion import MultimodalLearningService

    return MultimodalLearningService()


def observe_sparse_5184_projection(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    projection_service: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint8_context_facts(payload))
    candidates = _projection_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "sparse_5184_projection",
            "REJECT_PASS165_SPARSE_PROJECTION_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != SPARSE_PROJECTION_REQUEST_SCHEMA:
        return _active_failure(
            "sparse_5184_projection",
            "REJECT_PASS165_SPARSE_PROJECTION_REQUEST_SCHEMA",
            applicability,
        )

    try:
        raw = _decode_source_bytes(request)
        provenance = request.get("provenance")
        authorization_scope = request.get("authorization_scope")
        declared_media_type = request.get("declared_media_type")
        if not isinstance(provenance, str) or not provenance:
            raise ValueError("REJECT_PASS165_SPARSE_PROJECTION_PROVENANCE_MISSING")
        if not isinstance(authorization_scope, str) or not authorization_scope:
            raise ValueError("REJECT_PASS165_SPARSE_PROJECTION_AUTHORIZATION_MISSING")
        if declared_media_type is not None and not isinstance(declared_media_type, str):
            raise ValueError("REJECT_PASS165_SPARSE_PROJECTION_MEDIA_TYPE_INVALID")

        service = _load_projection_service(projection_service)
        source = service.capture_source(
            raw,
            declared_media_type=declared_media_type,
            provenance=provenance,
            authorization_scope=authorization_scope,
        )
        tokenizer = getattr(service, "_tokenizer", None)
        if tokenizer is None or not callable(getattr(tokenizer, "tokenize", None)):
            raise ValueError("REJECT_PASS165_SPARSE_PROJECTION_TOKENIZER_UNAVAILABLE")
        tokens = tokenizer.tokenize(source)
        chunks, edges = service.chunk_tokens(tokens)
        snapshot = service.project_5184(tokens, edges)
        projection_bytes = snapshot.to_bytes()

        from hhs_runtime.core.hash72_digest_v1 import hash72_digest
        from hhs_runtime.pass163.vmrc import COORDINATES, SNAPSHOT_BYTES

        if COORDINATES != 5184 or SNAPSHOT_BYTES != 648 or len(projection_bytes) != 648:
            raise ValueError("REJECT_PASS165_SPARSE_PROJECTION_GEOMETRY_INVALID")
        projection_root = hash72_digest(b"", projection_bytes)
        if not isinstance(projection_root, str) or len(projection_root) != 72:
            raise ValueError("REJECT_PASS165_SPARSE_PROJECTION_ROOT_INVALID")

        info = CHECKPOINT8_AUTHORITY_MAP["sparse_5184_projection"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "sparse_5184_projection",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_SPARSE_5184_PROJECTION_TRAVERSAL_V1",
                "status": "ADMIT_SPARSE_5184_PROJECTION_TRAVERSAL",
                "repository_native_callable": dict(info),
                "source_hash": source.source_hash,
                "detected_media_type": source.detected_media_type,
                "token_count": len(tokens),
                "chunk_count": len(chunks),
                "graph_edge_count": len(edges),
                "projection_coordinates": COORDINATES,
                "projection_bytes": SNAPSHOT_BYTES,
                "projection_popcount": sum(byte.bit_count() for byte in projection_bytes),
                "projection_hash72": projection_root,
                "preflight_mutation_authority": False,
                "applicability_facts": applicability,
            },
            "witness_root": projection_root,
        }
    except Exception as exc:
        return _active_failure(
            "sparse_5184_projection",
            f"REJECT_PASS165_SPARSE_5184_PROJECTION_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def _exact_int_vector(value: Any, *, label: str) -> tuple[int, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"REJECT_PASS215_{label}_VECTOR_MISSING")
    output: list[int] = []
    for item in value:
        if not isinstance(item, int) or isinstance(item, bool):
            raise ValueError(f"REJECT_PASS215_{label}_VECTOR_NONINTEGER")
        output.append(int(item))
    if not output:
        raise ValueError(f"REJECT_PASS215_{label}_VECTOR_EMPTY")
    return tuple(output)


def _exact_rational_output(value: Any) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError("REJECT_PASS215_PARENT_OUTPUT_MISSING")
    output: list[tuple[int, int]] = []
    for item in value:
        if isinstance(item, Mapping):
            numerator = item.get("numerator")
            denominator = item.get("denominator")
        elif (
            isinstance(item, Sequence)
            and not isinstance(item, (str, bytes, bytearray))
            and len(item) == 2
        ):
            numerator, denominator = item
        else:
            raise ValueError("REJECT_PASS215_PARENT_OUTPUT_RATIONAL_INVALID")
        if (
            not isinstance(numerator, int)
            or isinstance(numerator, bool)
            or not isinstance(denominator, int)
            or isinstance(denominator, bool)
            or denominator <= 0
        ):
            raise ValueError("REJECT_PASS215_PARENT_OUTPUT_RATIONAL_INVALID")
        output.append((int(numerator), int(denominator)))
    if not output:
        raise ValueError("REJECT_PASS215_PARENT_OUTPUT_EMPTY")
    return tuple(output)


def _delta_failure_proofs(
    reason: str,
    facts: Mapping[str, Any],
) -> Dict[str, Dict[str, Any]]:
    return {
        authority_id: _active_failure(authority_id, reason, facts)
        for authority_id in CHECKPOINT8_AUTHORITIES[1:]
    }


def observe_exact_delta_frontier_chain(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    delta_compiled_tensor: Any = None,
) -> Dict[str, Dict[str, Any]]:
    applicability = dict(facts or checkpoint8_context_facts(payload))
    candidates = _delta_candidates(payload)
    if len(candidates) != 1:
        return _delta_failure_proofs(
            "REJECT_PASS215_LINEAR_DELTA_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != LINEAR_DELTA_REQUEST_SCHEMA:
        return _delta_failure_proofs(
            "REJECT_PASS215_LINEAR_DELTA_REQUEST_SCHEMA",
            applicability,
        )

    try:
        if delta_compiled_tensor is None:
            raise ValueError("REJECT_PASS215_LINEAR_DELTA_COMPILED_TENSOR_MISSING")
        parent_input = _exact_int_vector(request.get("parent_input"), label="PARENT_INPUT")
        child_input = _exact_int_vector(request.get("child_input"), label="CHILD_INPUT")
        parent_output = _exact_rational_output(request.get("parent_output"))

        tensor_name = request.get("tensor_name")
        descriptor_root = request.get("descriptor_root_hash216")
        source_sha256 = request.get("source_sha256")
        if tensor_name != getattr(delta_compiled_tensor, "name", None):
            raise ValueError("REJECT_PASS215_LINEAR_DELTA_TENSOR_NAME_MISMATCH")
        if descriptor_root != getattr(delta_compiled_tensor, "descriptor_root_hash216", None):
            raise ValueError("REJECT_PASS215_LINEAR_DELTA_DESCRIPTOR_ROOT_MISMATCH")
        if source_sha256 != getattr(delta_compiled_tensor, "source_sha256", None):
            raise ValueError("REJECT_PASS215_LINEAR_DELTA_SOURCE_SHA_MISMATCH")

        from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4

        output, work = i4.execute_continuation_delta(
            delta_compiled_tensor,
            parent_input,
            parent_output,
            child_input,
        )
        changed = tuple(
            index
            for index, (left, right) in enumerate(zip(parent_input, child_input))
            if left != right
        )
        if not changed:
            raise ValueError("REJECT_PASS215_LINEAR_DELTA_CHANGED_COORDINATES_EMPTY")
        if len(parent_input) != len(child_input):
            raise ValueError("REJECT_PASS215_LINEAR_DELTA_INPUT_GEOMETRY_MISMATCH")
        changed_blocks = tuple(sorted({index // i4.Q4_0_BLOCK_ELEMENTS for index in changed}))
        ne1 = int(getattr(delta_compiled_tensor, "ne1"))
        if int(work.get("changed_input_coordinates", -1)) != len(changed):
            raise ValueError("REJECT_PASS215_LINEAR_DELTA_CHANGED_COORDINATE_WORK_MISMATCH")
        if int(work.get("compiled_descriptor_hits", -1)) != ne1 * len(changed_blocks):
            raise ValueError("REJECT_PASS215_LINEAR_DELTA_FRONTIER_WORK_MISMATCH")
        if int(work.get("delta_weight_products", -1)) != ne1 * len(changed):
            raise ValueError("REJECT_PASS215_LINEAR_DELTA_RESIDUAL_PRODUCT_WORK_MISMATCH")
        if int(work.get("full_output_rows_recomputed", -1)) != 0:
            raise ValueError("REJECT_PASS215_LINEAR_DELTA_FULL_ROW_RECOMPUTE")
        if int(work.get("continuation_output_rows_updated", -1)) != ne1:
            raise ValueError("REJECT_PASS215_LINEAR_DELTA_UPDATED_ROW_COUNT_MISMATCH")

        output_root = i4.output_root(delta_compiled_tensor.name, child_input, output)
        common_path = (
            "hhs_backend.runtime.hhs_pass215_iteration4_exact_linear_execution_v1."
            "execute_continuation_delta"
        )
        frontier_info = CHECKPOINT8_AUTHORITY_MAP["dependency_complete_frontier"]
        residual_info = CHECKPOINT8_AUTHORITY_MAP["residual_only_processing"]

        return {
            "dependency_complete_frontier": {
                "observed": True,
                "path": [
                    "kernel_runtime_autocomposer",
                    "dependency_complete_frontier",
                    common_path,
                ],
                "traversal_witness": {
                    "schema": "HHS_PASS217_DEPENDENCY_COMPLETE_FRONTIER_TRAVERSAL_V1",
                    "status": "ADMIT_DEPENDENCY_COMPLETE_FRONTIER_TRAVERSAL",
                    "repository_native_callable": dict(frontier_info),
                    "tensor_name": delta_compiled_tensor.name,
                    "descriptor_root_hash216": delta_compiled_tensor.descriptor_root_hash216,
                    "source_sha256": delta_compiled_tensor.source_sha256,
                    "changed_input_coordinates": list(changed),
                    "changed_input_coordinate_count": len(changed),
                    "affected_q4_block_frontier": list(changed_blocks),
                    "affected_q4_block_count": len(changed_blocks),
                    "compiled_descriptor_hits": int(work["compiled_descriptor_hits"]),
                    "dependency_complete": True,
                    "applicability_facts": applicability,
                },
                "witness_root": output_root,
            },
            "residual_only_processing": {
                "observed": True,
                "path": [
                    "kernel_runtime_autocomposer",
                    "residual_only_processing",
                    common_path,
                ],
                "traversal_witness": {
                    "schema": "HHS_PASS217_RESIDUAL_ONLY_PROCESSING_TRAVERSAL_V1",
                    "status": "ADMIT_RESIDUAL_ONLY_PROCESSING_TRAVERSAL",
                    "repository_native_callable": dict(residual_info),
                    "changed_input_coordinate_count": len(changed),
                    "delta_weight_products": int(work["delta_weight_products"]),
                    "delta_output_accumulations": int(work["delta_output_accumulations"]),
                    "full_output_rows_recomputed": int(work["full_output_rows_recomputed"]),
                    "continuation_output_rows_updated": int(work["continuation_output_rows_updated"]),
                    "residual_only": True,
                    "output_root_hash216": output_root,
                    "applicability_facts": applicability,
                },
                "witness_root": output_root,
            },
        }
    except Exception as exc:
        return _delta_failure_proofs(
            f"REJECT_PASS215_EXACT_DELTA_FRONTIER_TRAVERSAL:{type(exc).__name__}:{exc}",
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


def build_checkpoint8_inherited_authority_reachability(
    preflight: Mapping[str, Any],
    surface: Mapping[str, Any],
    payload: Optional[Mapping[str, Any]] = None,
    *,
    semantic_cache: Any = None,
    retrieval_runtime: Any = None,
    pattern_repo_root: Any = None,
    source_reuse_service: Any = None,
    projection_service: Any = None,
    delta_compiled_tensor: Any = None,
) -> Dict[str, Any]:
    """Compose Checkpoint 8 over the validated Checkpoint 7 reachability slice."""

    prior = build_checkpoint7_inherited_authority_reachability(
        preflight,
        surface,
        payload,
        semantic_cache=semantic_cache,
        retrieval_runtime=retrieval_runtime,
        pattern_repo_root=pattern_repo_root,
        source_reuse_service=source_reuse_service,
    )
    active: Dict[str, Mapping[str, Any]] = {}
    not_applicable: Dict[str, Mapping[str, Any]] = {}
    superseded: Dict[str, Mapping[str, Any]] = {}
    _import_prior_decisions(prior, active, not_applicable, superseded)

    facts = checkpoint8_context_facts(payload)

    if facts["sparse_projection_domain_present"] is False:
        not_applicable["sparse_5184_projection"] = {
            "mechanically_proven": True,
            "predicate": "sparse_projection_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no Pass 165 sparse 5184 projection request domain",
        }
    else:
        active["sparse_5184_projection"] = observe_sparse_5184_projection(
            payload,
            facts=facts,
            projection_service=projection_service,
        )

    if facts["linear_delta_domain_present"] is False:
        for authority_id in CHECKPOINT8_AUTHORITIES[1:]:
            not_applicable[authority_id] = {
                "mechanically_proven": True,
                "predicate": "linear_delta_domain_present == false",
                "observed_facts": facts,
                "reason": (
                    "operation contains no exact parent/child linear continuation-delta domain "
                    "requiring dependency-frontier or residual-only processing"
                ),
            }
    else:
        active.update(
            observe_exact_delta_frontier_chain(
                payload,
                facts=facts,
                delta_compiled_tensor=delta_compiled_tensor,
            )
        )

    operation_id = str(preflight.get("operation") or surface.get("symbol") or "operation")
    record = build_authority_reachability(
        operation_id,
        active_in_path=active,
        not_applicable=not_applicable,
        explicitly_superseded=superseded,
        required_authorities=CHECKPOINT8_REQUIRED_AUTHORITIES,
    )
    record["checkpoint_scope"] = list(CHECKPOINT8_REQUIRED_AUTHORITIES)
    record["checkpoint8_authority_map"] = {
        key: dict(value) for key, value in CHECKPOINT8_AUTHORITY_MAP.items()
    }
    record["checkpoint8_applicability_facts"] = facts
    for key in (
        "continuation_applicability_facts",
        "pattern_cache_applicability_facts",
        "retrieval_reuse_applicability_facts",
        "checkpoint6_native_callable_map",
        "content_reuse_applicability_facts",
        "checkpoint7_authority_map",
    ):
        if key in prior:
            value = prior[key]
            record[key] = dict(value) if isinstance(value, Mapping) else value
    record["prior_checkpoint_reachability_root_hash72"] = prior.get(
        "reachability_root_hash72"
    )
    record["checkpoint"] = 8
    return record


__all__ = [
    "VERSION",
    "SPARSE_PROJECTION_REQUEST_SCHEMA",
    "LINEAR_DELTA_REQUEST_SCHEMA",
    "CHECKPOINT8_AUTHORITIES",
    "CHECKPOINT8_REQUIRED_AUTHORITIES",
    "CHECKPOINT8_AUTHORITY_MAP",
    "checkpoint8_context_facts",
    "observe_sparse_5184_projection",
    "observe_exact_delta_frontier_chain",
    "build_checkpoint8_inherited_authority_reachability",
]
