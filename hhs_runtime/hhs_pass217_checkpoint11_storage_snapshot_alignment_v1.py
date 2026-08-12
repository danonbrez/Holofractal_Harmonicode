"""Pass 217 Checkpoint 11 encrypted-vector reuse, snapshot reuse, and multimodal alignment.

This checkpoint extends the validated Checkpoint 10 cumulative authority slice with:

* encrypted_vector_store -> Pass 174 persistent AES-GCM vector retrieval;
* snapshot_reuse -> Pass 197 authenticated checkpoint/resume reuse;
* multimodal_cross_alignment -> Pass 165 common exact 5,184-coordinate projection
  geometry across distinct admitted modality classes.

The multimodal witness proves shared registered projection geometry and exact source
identity preservation only. It does not claim semantic equivalence between unlike
modalities. Absent domains are mechanically NOT_APPLICABLE; partial or malformed
applicable context fails closed.
"""

from __future__ import annotations

from base64 import b64decode
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from hhs_runtime.hhs_cumulative_execution_authority_v1 import (
    ACTIVE_IN_PATH,
    EXPLICITLY_SUPERSEDED,
    NOT_APPLICABLE,
    build_authority_reachability,
)
from hhs_runtime.hhs_pass217_checkpoint10_recovery_index_graph_v1 import (
    CHECKPOINT10_REQUIRED_AUTHORITIES,
    build_checkpoint10_inherited_authority_reachability,
)


VERSION = "PASS_217_CUMULATIVE_EXECUTION_COMPOSER_CHECKPOINT_11_V1"
ENCRYPTED_VECTOR_STORE_REQUEST_SCHEMA = "HHS_PASS217_ENCRYPTED_VECTOR_STORE_REQUEST_V1"
SNAPSHOT_REUSE_REQUEST_SCHEMA = "HHS_PASS217_SNAPSHOT_REUSE_REQUEST_V1"
MULTIMODAL_CROSS_ALIGNMENT_REQUEST_SCHEMA = "HHS_PASS217_MULTIMODAL_CROSS_ALIGNMENT_REQUEST_V1"

CHECKPOINT11_AUTHORITIES = (
    "encrypted_vector_store",
    "snapshot_reuse",
    "multimodal_cross_alignment",
)
CHECKPOINT11_REQUIRED_AUTHORITIES = CHECKPOINT10_REQUIRED_AUTHORITIES + CHECKPOINT11_AUTHORITIES

CHECKPOINT11_AUTHORITY_MAP: Dict[str, Dict[str, Any]] = {
    "encrypted_vector_store": {
        "origin_pass": 174,
        "later_contract_alignment_pass": 194,
        "module": "hhs_runtime.pass174.storage",
        "symbol": "PersistentEncryptedVectorStore.retrieve",
        "implementation_symbol": "EncryptedVectorStore.retrieve",
        "status_symbol": "PersistentEncryptedVectorStore.storage_status",
        "callable_role": (
            "authenticated AES-GCM retrieval of an already-persisted Hash216-bound "
            "whole-frame vector payload without altering store identity"
        ),
        "runtime_authority": True,
        "persistent_private_vector_required": True,
    },
    "snapshot_reuse": {
        "origin_pass": 197,
        "foundation_pass": 163,
        "later_contract_alignment_pass": 194,
        "module": "hhs_backend.runtime.hhs_pass197_ab_hydration_calibration_v1",
        "symbol": "Pass197ABHydrationCalibration.run",
        "callable_role": (
            "resume from an authenticated existing calibration checkpoint while "
            "reusing completed exact parameter states"
        ),
        "runtime_authority": True,
    },
    "multimodal_cross_alignment": {
        "origin_pass": 165,
        "later_contract_alignment_pass": 194,
        "module": "hhs_runtime.pass165.ingestion",
        "symbol": "MultimodalLearningService.analyze",
        "projection_symbol": "MultimodalLearningService.project_5184",
        "callable_role": (
            "distinct admitted modalities traverse one deterministic tokenizer/chunker/"
            "projector contract into the common exact 81x64 projection geometry"
        ),
        "runtime_authority": True,
        "semantic_equivalence_claimed": False,
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


def _encrypted_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="encrypted_vector_store",
        schema=ENCRYPTED_VECTOR_STORE_REQUEST_SCHEMA,
    )


def _snapshot_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="snapshot_reuse",
        schema=SNAPSHOT_REUSE_REQUEST_SCHEMA,
    )


def _multimodal_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="multimodal_cross_alignment",
        schema=MULTIMODAL_CROSS_ALIGNMENT_REQUEST_SCHEMA,
    )


def checkpoint11_context_facts(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    encrypted = _encrypted_candidates(payload)
    snapshot = _snapshot_candidates(payload)
    multimodal = _multimodal_candidates(payload)
    return {
        "schema": "HHS_PASS217_CHECKPOINT11_APPLICABILITY_FACTS_V1",
        "encrypted_vector_store_domain_present": bool(encrypted),
        "encrypted_vector_store_candidate_count": len(encrypted),
        "encrypted_vector_store_exact_schema_count": sum(
            row.get("schema") == ENCRYPTED_VECTOR_STORE_REQUEST_SCHEMA for row in encrypted
        ),
        "snapshot_reuse_domain_present": bool(snapshot),
        "snapshot_reuse_candidate_count": len(snapshot),
        "snapshot_reuse_exact_schema_count": sum(
            row.get("schema") == SNAPSHOT_REUSE_REQUEST_SCHEMA for row in snapshot
        ),
        "multimodal_cross_alignment_domain_present": bool(multimodal),
        "multimodal_cross_alignment_candidate_count": len(multimodal),
        "multimodal_cross_alignment_exact_schema_count": sum(
            row.get("schema") == MULTIMODAL_CROSS_ALIGNMENT_REQUEST_SCHEMA for row in multimodal
        ),
    }


def _active_failure(authority_id: str, reason: str, facts: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "observed": False,
        "path": ["kernel_runtime_autocomposer", authority_id],
        "traversal_witness": {
            "schema": "HHS_PASS217_CHECKPOINT11_TRAVERSAL_FAILURE_V1",
            "status": "REJECT_CHECKPOINT11_INHERITED_TRAVERSAL",
            "authority_id": authority_id,
            "reason": str(reason),
            "authority_map": dict(CHECKPOINT11_AUTHORITY_MAP[authority_id]),
            "applicability_facts": dict(facts),
        },
        "witness_root": "",
    }


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise TypeError("REJECT_CHECKPOINT11_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN")
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple, set)):
        for child in value:
            _reject_float(child)


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _hash216(domain: str, value: Any) -> str:
    raw = _canonical_bytes(value)
    return sha256(domain.encode("utf-8") + b"\0" + len(raw).to_bytes(8, "big") + raw).hexdigest()


def _sha256_hex(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"REJECT_CHECKPOINT11_{label}_SHA256_INVALID")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"REJECT_CHECKPOINT11_{label}_SHA256_INVALID") from exc
    return value


def observe_encrypted_vector_store(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    encrypted_vector_store: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint11_context_facts(payload))
    candidates = _encrypted_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "encrypted_vector_store",
            "REJECT_ENCRYPTED_VECTOR_STORE_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != ENCRYPTED_VECTOR_STORE_REQUEST_SCHEMA:
        return _active_failure(
            "encrypted_vector_store",
            "REJECT_ENCRYPTED_VECTOR_STORE_REQUEST_SCHEMA",
            applicability,
        )
    try:
        _reject_float(request)
        if encrypted_vector_store is None:
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_RUNTIME_MISSING")
        if not callable(getattr(encrypted_vector_store, "retrieve", None)):
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_RETRIEVE_UNAVAILABLE")
        if not callable(getattr(encrypted_vector_store, "storage_status", None)):
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_PERSISTENT_STATUS_REQUIRED")

        operation_key = request.get("operation_key")
        if not isinstance(operation_key, str) or not operation_key:
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_OPERATION_KEY_INVALID")
        expected_object_id = _sha256_hex(request.get("expected_object_id"), "VECTOR_OBJECT_ID")
        expected_store_root = _sha256_hex(
            request.get("expected_store_root_sha256"), "VECTOR_STORE_ROOT"
        )
        expected_snapshot_sha = _sha256_hex(
            request.get("expected_snapshot_sha256"), "VECTOR_SNAPSHOT"
        )
        legacy_root = _sha256_hex(request.get("legacy_foundation_root"), "LEGACY_ROOT")
        genesis_identity = _sha256_hex(request.get("genesis_identity"), "GENESIS_IDENTITY")
        expected_output_hash72 = request.get("expected_output_hash72")
        if not isinstance(expected_output_hash72, str) or not expected_output_hash72:
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_OUTPUT_HASH72_INVALID")

        before_root = encrypted_vector_store.root()
        before_status = encrypted_vector_store.storage_status()
        if before_root != expected_store_root:
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_ROOT_MISMATCH")
        if before_status.get("logical_root_sha256") != expected_store_root:
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_STATUS_ROOT_MISMATCH")
        if before_status.get("authenticated_encryption") != "AES_GCM":
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_AEAD_REQUIRED")
        if before_status.get("plaintext_persisted") is not False:
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_PLAINTEXT_PERSISTENCE")

        obj, snapshot = encrypted_vector_store.retrieve(
            operation_key,
            legacy_foundation_root=legacy_root,
            genesis_identity=genesis_identity,
        )
        if obj.object_id != expected_object_id:
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_OBJECT_ID_MISMATCH")
        if obj.output_hash72 != expected_output_hash72:
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_OUTPUT_HASH72_MISMATCH")
        if sha256(snapshot).hexdigest() != expected_snapshot_sha:
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_SNAPSHOT_MISMATCH")
        obj.hash216.verify()

        after_root = encrypted_vector_store.root()
        after_status = encrypted_vector_store.storage_status()
        if after_root != before_root or after_status.get("logical_root_sha256") != before_root:
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_RETRIEVAL_MUTATED_ROOT")
        if after_status.get("objects") != before_status.get("objects"):
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_RETRIEVAL_MUTATED_COUNT")
        if after_status.get("quarantined") != before_status.get("quarantined"):
            raise ValueError("REJECT_ENCRYPTED_VECTOR_STORE_RETRIEVAL_MUTATED_QUARANTINE")

        info = CHECKPOINT11_AUTHORITY_MAP["encrypted_vector_store"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "encrypted_vector_store",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_ENCRYPTED_VECTOR_STORE_TRAVERSAL_V1",
                "status": "ADMIT_ENCRYPTED_VECTOR_STORE_TRAVERSAL",
                "repository_native_callable": dict(info),
                "operation_key": operation_key,
                "object_id": obj.object_id,
                "output_hash72": obj.output_hash72,
                "hash216_identity_sha256": obj.hash216.logical_identity_sha256,
                "hash216_index_root_sha256": obj.hash216.index_root_sha256,
                "snapshot_sha256": expected_snapshot_sha,
                "snapshot_bytes": len(snapshot),
                "store_root_sha256": before_root,
                "key_version": obj.key_version,
                "authenticated_encryption": before_status.get("authenticated_encryption"),
                "plaintext_persisted": before_status.get("plaintext_persisted"),
                "retrieval_mutated_store": False,
                "applicability_facts": applicability,
            },
            "witness_root": obj.object_id,
        }
    except Exception as exc:
        return _active_failure(
            "encrypted_vector_store",
            f"REJECT_ENCRYPTED_VECTOR_STORE_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def observe_snapshot_reuse(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    snapshot_reuse_runtime: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint11_context_facts(payload))
    candidates = _snapshot_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "snapshot_reuse",
            "REJECT_SNAPSHOT_REUSE_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != SNAPSHOT_REUSE_REQUEST_SCHEMA:
        return _active_failure(
            "snapshot_reuse",
            "REJECT_SNAPSHOT_REUSE_REQUEST_SCHEMA",
            applicability,
        )
    try:
        _reject_float(request)
        if snapshot_reuse_runtime is None:
            raise ValueError("REJECT_SNAPSHOT_REUSE_RUNTIME_MISSING")
        checkpoint_path = getattr(snapshot_reuse_runtime, "checkpoint_path", None)
        if checkpoint_path is None or not checkpoint_path.exists():
            raise ValueError("REJECT_SNAPSHOT_REUSE_PREEXISTING_CHECKPOINT_REQUIRED")
        config = request.get("config")
        if not isinstance(config, Mapping):
            raise ValueError("REJECT_SNAPSHOT_REUSE_CONFIG_REQUIRED")
        expected_config = request.get("expected_config_hash72")
        expected_checkpoint = request.get("expected_checkpoint_hash72")
        expected_state = request.get("expected_state_root_hash72")
        expected_report = request.get("expected_report_hash72")
        for value, label in (
            (expected_config, "CONFIG_HASH72"),
            (expected_checkpoint, "CHECKPOINT_HASH72"),
            (expected_state, "STATE_ROOT_HASH72"),
            (expected_report, "REPORT_HASH72"),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(f"REJECT_SNAPSHOT_REUSE_{label}_INVALID")
        expected_completed = request.get("expected_completed_state_count")
        if (
            not isinstance(expected_completed, int)
            or isinstance(expected_completed, bool)
            or expected_completed <= 0
        ):
            raise ValueError("REJECT_SNAPSHOT_REUSE_COMPLETED_STATE_COUNT_INVALID")

        before_raw = checkpoint_path.read_bytes()
        before = json.loads(before_raw)
        if before.get("schema") != "HHS_PASS_197_AB_HYDRATION_CHECKPOINT_V1":
            raise ValueError("REJECT_SNAPSHOT_REUSE_CHECKPOINT_SCHEMA")
        if before.get("config_hash72") != expected_config:
            raise ValueError("REJECT_SNAPSHOT_REUSE_CONFIG_HASH_MISMATCH")
        if before.get("checkpoint_hash72") != expected_checkpoint:
            raise ValueError("REJECT_SNAPSHOT_REUSE_CHECKPOINT_HASH_MISMATCH")
        if len(before.get("completed") or {}) != expected_completed:
            raise ValueError("REJECT_SNAPSHOT_REUSE_COMPLETED_STATE_COUNT_MISMATCH")

        report = snapshot_reuse_runtime.run(config, resume=True)
        if report.get("state_root_hash72") != expected_state:
            raise ValueError("REJECT_SNAPSHOT_REUSE_STATE_ROOT_MISMATCH")
        if report.get("report_hash72") != expected_report:
            raise ValueError("REJECT_SNAPSHOT_REUSE_REPORT_HASH_MISMATCH")
        if report.get("closed") is not True:
            raise ValueError("REJECT_SNAPSHOT_REUSE_REPORT_NOT_CLOSED")

        after_raw = checkpoint_path.read_bytes()
        after = json.loads(after_raw)
        if after_raw != before_raw:
            raise ValueError("REJECT_SNAPSHOT_REUSE_CHECKPOINT_MUTATED")
        if after.get("checkpoint_hash72") != expected_checkpoint:
            raise ValueError("REJECT_SNAPSHOT_REUSE_CHECKPOINT_IDENTITY_CHANGED")
        if len(after.get("completed") or {}) != expected_completed:
            raise ValueError("REJECT_SNAPSHOT_REUSE_COMPLETED_SET_CHANGED")

        info = CHECKPOINT11_AUTHORITY_MAP["snapshot_reuse"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "snapshot_reuse",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_SNAPSHOT_REUSE_TRAVERSAL_V1",
                "status": "ADMIT_SNAPSHOT_REUSE_TRAVERSAL",
                "repository_native_callable": dict(info),
                "config_hash72": expected_config,
                "checkpoint_hash72": expected_checkpoint,
                "checkpoint_content_sha256": sha256(before_raw).hexdigest(),
                "completed_state_count_reused": expected_completed,
                "state_root_hash72": expected_state,
                "report_hash72": expected_report,
                "checkpoint_bytes_unchanged": True,
                "resume_reused_preexisting_checkpoint": True,
                "full_replay_executed": bool((report.get("replay") or {}).get("full_replay_executed")),
                "deterministic_replay": bool((report.get("replay") or {}).get("deterministic")),
                "applicability_facts": applicability,
            },
            "witness_root": expected_checkpoint,
        }
    except Exception as exc:
        return _active_failure(
            "snapshot_reuse",
            f"REJECT_SNAPSHOT_REUSE_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def _decode_multimodal_sources(request: Mapping[str, Any]) -> tuple[tuple[str, bytes, str], ...]:
    sources = request.get("sources")
    if not isinstance(sources, Sequence) or isinstance(sources, (str, bytes, bytearray)):
        raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_SOURCES_SEQUENCE_REQUIRED")
    if not 2 <= len(sources) <= 8:
        raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_SOURCE_COUNT_BOUND")
    output: list[tuple[str, bytes, str]] = []
    for row in sources:
        if not isinstance(row, Mapping):
            raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_SOURCE_MAPPING_REQUIRED")
        modality = row.get("declared_media_type")
        encoded = row.get("source_b64")
        expected_sha = row.get("expected_source_sha256")
        if not isinstance(modality, str) or not modality:
            raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_MODALITY_INVALID")
        if not isinstance(encoded, str) or not encoded:
            raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_SOURCE_B64_INVALID")
        _sha256_hex(expected_sha, "MULTIMODAL_SOURCE")
        try:
            raw = b64decode(encoded, validate=True)
        except Exception as exc:
            raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_SOURCE_B64_INVALID") from exc
        if not raw or sha256(raw).hexdigest() != expected_sha:
            raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_SOURCE_HASH_MISMATCH")
        output.append((modality.upper(), raw, expected_sha))
    if len({row[0] for row in output}) < 2:
        raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_DISTINCT_MODALITIES_REQUIRED")
    return tuple(output)


def observe_multimodal_cross_alignment(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    multimodal_alignment_service: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint11_context_facts(payload))
    candidates = _multimodal_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "multimodal_cross_alignment",
            "REJECT_MULTIMODAL_ALIGNMENT_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != MULTIMODAL_CROSS_ALIGNMENT_REQUEST_SCHEMA:
        return _active_failure(
            "multimodal_cross_alignment",
            "REJECT_MULTIMODAL_ALIGNMENT_REQUEST_SCHEMA",
            applicability,
        )
    try:
        _reject_float(request)
        if multimodal_alignment_service is None:
            raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_SERVICE_MISSING")
        provenance = request.get("provenance")
        authorization_scope = request.get("authorization_scope")
        if not isinstance(provenance, str) or not provenance:
            raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_PROVENANCE_REQUIRED")
        if not isinstance(authorization_scope, str) or not authorization_scope:
            raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_AUTHORIZATION_REQUIRED")
        sources = _decode_multimodal_sources(request)

        from hhs_runtime.pass165.ingestion import COORDINATES, PROJECTOR_VERSION, SNAPSHOT_BYTES

        before_status = multimodal_alignment_service.status()
        records: list[dict[str, Any]] = []
        detected_modalities: set[str] = set()
        for index, (declared, raw, expected_sha) in enumerate(sources):
            result = multimodal_alignment_service.analyze(
                raw,
                declared_media_type=declared,
                provenance=f"{provenance}:{index}",
                authorization_scope=authorization_scope,
            )
            if result.source.source_hash != expected_sha:
                raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_ANALYZED_SOURCE_HASH_MISMATCH")
            if result.source.detected_media_type != declared:
                raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_DETECTED_MODALITY_MISMATCH")
            if len(result.projection_bytes) != SNAPSHOT_BYTES:
                raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_PROJECTION_GEOMETRY")
            if not result.projection_hash72:
                raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_PROJECTION_ROOT_MISSING")
            detected_modalities.add(result.source.detected_media_type)
            records.append({
                "ordinal": index,
                "declared_media_type": declared,
                "detected_media_type": result.source.detected_media_type,
                "source_sha256": result.source.source_hash,
                "token_stream_root_sha256": result.token_stream_root,
                "chunk_graph_root_sha256": result.chunk_graph_root,
                "projection_hash72": result.projection_hash72,
                "projection_bytes": len(result.projection_bytes),
                "token_count": len(result.tokens),
                "chunk_count": len(result.chunks),
                "graph_edge_count": len(result.graph_edges),
            })
        if len(detected_modalities) < 2:
            raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_DISTINCT_DETECTED_MODALITIES_REQUIRED")
        after_status = multimodal_alignment_service.status()
        if after_status != before_status:
            raise ValueError("REJECT_MULTIMODAL_ALIGNMENT_PREFLIGHT_MUTATED_SERVICE")

        alignment_body = {
            "schema": "HHS_PASS217_MULTIMODAL_COMMON_PROJECTION_ALIGNMENT_V1",
            "projector_version": PROJECTOR_VERSION,
            "projection_coordinates": COORDINATES,
            "projection_bytes": SNAPSHOT_BYTES,
            "modalities": sorted(detected_modalities),
            "records": records,
            "semantic_equivalence_claimed": False,
            "alignment_claim": "COMMON_EXACT_PROJECTION_GEOMETRY_ONLY",
        }
        alignment_root = _hash216("pass217-checkpoint11-multimodal-alignment", alignment_body)
        info = CHECKPOINT11_AUTHORITY_MAP["multimodal_cross_alignment"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "multimodal_cross_alignment",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_MULTIMODAL_CROSS_ALIGNMENT_TRAVERSAL_V1",
                "status": "ADMIT_MULTIMODAL_CROSS_ALIGNMENT_TRAVERSAL",
                "repository_native_callable": dict(info),
                **alignment_body,
                "alignment_root_hash216": alignment_root,
                "preflight_mutated_service": False,
                "applicability_facts": applicability,
            },
            "witness_root": alignment_root,
        }
    except Exception as exc:
        return _active_failure(
            "multimodal_cross_alignment",
            f"REJECT_MULTIMODAL_ALIGNMENT_TRAVERSAL:{type(exc).__name__}:{exc}",
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


def build_checkpoint11_inherited_authority_reachability(
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
    parametric_template: Any = None,
    parametric_base_entry: Any = None,
    parametric_opening_boundary: Any = None,
    parametric_validation_key: Optional[bytes] = None,
    compiled_rom_store: Any = None,
    physical_recovery_runtime: Any = None,
    physical_protected_payload: Any = None,
    receipt_vector_index: Any = None,
    receipt_vector_receipt: Any = None,
    sql_context_db: Any = None,
    encrypted_vector_store: Any = None,
    snapshot_reuse_runtime: Any = None,
    multimodal_alignment_service: Any = None,
) -> Dict[str, Any]:
    prior = build_checkpoint10_inherited_authority_reachability(
        preflight,
        surface,
        payload,
        semantic_cache=semantic_cache,
        retrieval_runtime=retrieval_runtime,
        pattern_repo_root=pattern_repo_root,
        source_reuse_service=source_reuse_service,
        projection_service=projection_service,
        delta_compiled_tensor=delta_compiled_tensor,
        parametric_template=parametric_template,
        parametric_base_entry=parametric_base_entry,
        parametric_opening_boundary=parametric_opening_boundary,
        parametric_validation_key=parametric_validation_key,
        compiled_rom_store=compiled_rom_store,
        physical_recovery_runtime=physical_recovery_runtime,
        physical_protected_payload=physical_protected_payload,
        receipt_vector_index=receipt_vector_index,
        receipt_vector_receipt=receipt_vector_receipt,
        sql_context_db=sql_context_db,
    )
    active: Dict[str, Mapping[str, Any]] = {}
    not_applicable: Dict[str, Mapping[str, Any]] = {}
    superseded: Dict[str, Mapping[str, Any]] = {}
    _import_prior_decisions(prior, active, not_applicable, superseded)
    facts = checkpoint11_context_facts(payload)

    if facts["encrypted_vector_store_domain_present"] is False:
        not_applicable["encrypted_vector_store"] = {
            "mechanically_proven": True,
            "predicate": "encrypted_vector_store_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no authenticated persistent encrypted-vector retrieval domain",
        }
    else:
        active["encrypted_vector_store"] = observe_encrypted_vector_store(
            payload,
            facts=facts,
            encrypted_vector_store=encrypted_vector_store,
        )

    if facts["snapshot_reuse_domain_present"] is False:
        not_applicable["snapshot_reuse"] = {
            "mechanically_proven": True,
            "predicate": "snapshot_reuse_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no preexisting authenticated Pass 197 checkpoint reuse domain",
        }
    else:
        active["snapshot_reuse"] = observe_snapshot_reuse(
            payload,
            facts=facts,
            snapshot_reuse_runtime=snapshot_reuse_runtime,
        )

    if facts["multimodal_cross_alignment_domain_present"] is False:
        not_applicable["multimodal_cross_alignment"] = {
            "mechanically_proven": True,
            "predicate": "multimodal_cross_alignment_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no distinct-modality common-projection alignment domain",
        }
    else:
        active["multimodal_cross_alignment"] = observe_multimodal_cross_alignment(
            payload,
            facts=facts,
            multimodal_alignment_service=multimodal_alignment_service,
        )

    operation_id = str(preflight.get("operation") or surface.get("symbol") or "operation")
    record = build_authority_reachability(
        operation_id,
        active_in_path=active,
        not_applicable=not_applicable,
        explicitly_superseded=superseded,
        required_authorities=CHECKPOINT11_REQUIRED_AUTHORITIES,
    )
    record["checkpoint_scope"] = list(CHECKPOINT11_REQUIRED_AUTHORITIES)
    record["checkpoint11_authority_map"] = {
        key: dict(value) for key, value in CHECKPOINT11_AUTHORITY_MAP.items()
    }
    record["checkpoint11_applicability_facts"] = facts
    for key in (
        "continuation_applicability_facts",
        "pattern_cache_applicability_facts",
        "retrieval_reuse_applicability_facts",
        "checkpoint6_native_callable_map",
        "content_reuse_applicability_facts",
        "checkpoint7_authority_map",
        "checkpoint8_applicability_facts",
        "checkpoint8_authority_map",
        "checkpoint9_applicability_facts",
        "checkpoint9_authority_map",
        "checkpoint10_applicability_facts",
        "checkpoint10_authority_map",
    ):
        if key in prior:
            value = prior[key]
            record[key] = dict(value) if isinstance(value, Mapping) else value
    record["prior_checkpoint_reachability_root_hash72"] = prior.get("reachability_root_hash72")
    record["checkpoint"] = 11
    return record


__all__ = [
    "VERSION",
    "ENCRYPTED_VECTOR_STORE_REQUEST_SCHEMA",
    "SNAPSHOT_REUSE_REQUEST_SCHEMA",
    "MULTIMODAL_CROSS_ALIGNMENT_REQUEST_SCHEMA",
    "CHECKPOINT11_AUTHORITIES",
    "CHECKPOINT11_REQUIRED_AUTHORITIES",
    "CHECKPOINT11_AUTHORITY_MAP",
    "checkpoint11_context_facts",
    "observe_encrypted_vector_store",
    "observe_snapshot_reuse",
    "observe_multimodal_cross_alignment",
    "build_checkpoint11_inherited_authority_reachability",
]
