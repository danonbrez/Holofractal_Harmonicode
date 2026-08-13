"""Pass 215 Iteration 9 repair-forward tokenizer sentinel handling.

The first authenticated real-model run established that the GGUF may carry a
special-token metadata scalar (notably padding_token_id) outside the vocabulary
as an inactive/sentinel value.  Version 2 preserves every raw integer metadata
value as authenticated evidence, classifies in-range IDs as active and
out-of-range IDs as inactive sentinels, and permits only active IDs to
participate in deterministic ingress selection.

All exact embedding and downstream symbolic execution remains inherited from
Iteration 9 v1; no runtime/canonical mutation authority is introduced.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

from hhs_backend.runtime import hhs_pass215_iteration2_open_transformer_container_v1 as i2
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v4 as i4
from hhs_backend.runtime import hhs_pass215_iteration5_exact_nonlinear_symbolic_v1 as i5
from hhs_backend.runtime import hhs_pass215_iteration6_authenticated_block_graph_v1 as i6
from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7
from hhs_backend.runtime import hhs_pass215_iteration8_multi_token_causal_attention_v1 as i8
from hhs_backend.runtime import hhs_pass215_iteration9_authenticated_token_ingress_v1 as v1

CONTRACT = v1.CONTRACT
PASS_NUMBER = v1.PASS_NUMBER
ITERATION = v1.ITERATION
EVIDENCE_SCHEMA = v1.EVIDENCE_SCHEMA
VALIDATION_SCHEMA = v1.VALIDATION_SCHEMA
REPLAY_SCHEMA = v1.REPLAY_SCHEMA
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_9_AUTHENTICATED_TOKEN_INGRESS_BENCHMARK_V2_SENTINEL_AWARE"

REAL_MODEL_SHA256 = v1.REAL_MODEL_SHA256
SEQUENCE_LENGTH = v1.SEQUENCE_LENGTH
EMBEDDING_WIDTH = v1.EMBEDDING_WIDTH
TOKEN_EMBEDDING_TENSOR = v1.TOKEN_EMBEDDING_TENSOR
Q4_0_ROW_BYTES = v1.Q4_0_ROW_BYTES
TOKEN_ARRAY_KEY = v1.TOKEN_ARRAY_KEY
TOKEN_TYPE_ARRAY_KEY = v1.TOKEN_TYPE_ARRAY_KEY
TOKENIZER_MODEL_KEY = v1.TOKENIZER_MODEL_KEY
SPECIAL_TOKEN_KEYS = v1.SPECIAL_TOKEN_KEYS
TOKENIZER_BOOL_KEYS = v1.TOKENIZER_BOOL_KEYS

Pass215Iteration9Error = v1.Pass215Iteration9Error
Pass215Iteration9ValidationError = v1.Pass215Iteration9ValidationError
_reject_floats = v1._reject_floats
_select_token_ids = v1._select_token_ids
_decode_q4_0_embedding_row = v1._decode_q4_0_embedding_row
_extract_authenticated_embeddings = v1._extract_authenticated_embeddings
_execute_forward_from_embeddings = v1._execute_forward_from_embeddings
_iteration8_bindings = v1._iteration8_bindings
_validate_frozen_iteration8_evidence = v1._validate_frozen_iteration8_evidence


def _is_integer_metadata_type(value_type: int) -> bool:
    return value_type in {
        i2._GGUF_UINT8, i2._GGUF_INT8, i2._GGUF_UINT16, i2._GGUF_INT16,
        i2._GGUF_UINT32, i2._GGUF_INT32, i2._GGUF_UINT64, i2._GGUF_INT64,
    }


def _read_tokenizer_metadata(raw: bytes) -> Mapping[str, Any]:
    reader = i2._Reader(raw)
    if reader.read(4) != b"GGUF":
        raise Pass215Iteration9ValidationError("PASS215_I9_GGUF_MAGIC_INVALID")
    version = reader.u32()
    if version not in (2, 3):
        raise Pass215Iteration9ValidationError("PASS215_I9_GGUF_VERSION_UNSUPPORTED")
    tensor_count = reader.u64()
    metadata_count = reader.u64()
    if tensor_count <= 0 or metadata_count > 1_000_000:
        raise Pass215Iteration9ValidationError("PASS215_I9_GGUF_HEADER_INVALID")

    tokens: tuple[str, ...] | None = None
    token_types: tuple[int, ...] | None = None
    tokenizer_model: str | None = None
    raw_special_ids: dict[str, int] = {}
    booleans: dict[str, bool] = {}
    selected_types: dict[str, int] = {}

    for _ in range(metadata_count):
        key = reader.string()
        value_type = reader.u32()
        if key == TOKEN_ARRAY_KEY:
            if value_type != i2._GGUF_ARRAY:
                raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_ARRAY_TYPE_INVALID")
            element_type = reader.u32()
            count = reader.u64()
            if element_type != i2._GGUF_STRING or not 1 <= count <= 10_000_000:
                raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_ARRAY_GEOMETRY_INVALID")
            tokens = tuple(reader.string() for _ in range(count))
            selected_types[key] = value_type
            continue
        if key == TOKEN_TYPE_ARRAY_KEY:
            if value_type != i2._GGUF_ARRAY:
                raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_TYPE_ARRAY_TYPE_INVALID")
            element_type = reader.u32()
            count = reader.u64()
            if not _is_integer_metadata_type(element_type) or count > 10_000_000:
                raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_TYPE_ARRAY_GEOMETRY_INVALID")
            token_types = tuple(
                int(i2._read_gguf_value(reader, element_type, summarize_arrays=False))
                for _ in range(count)
            )
            selected_types[key] = value_type
            continue
        if key == TOKENIZER_MODEL_KEY:
            if value_type != i2._GGUF_STRING:
                raise Pass215Iteration9ValidationError("PASS215_I9_TOKENIZER_MODEL_TYPE_INVALID")
            tokenizer_model = reader.string()
            selected_types[key] = value_type
            continue
        if key in SPECIAL_TOKEN_KEYS:
            if not _is_integer_metadata_type(value_type):
                raise Pass215Iteration9ValidationError(f"PASS215_I9_SPECIAL_TOKEN_TYPE_INVALID:{key}")
            raw_special_ids[key] = int(i2._read_gguf_value(reader, value_type, summarize_arrays=False))
            selected_types[key] = value_type
            continue
        if key in TOKENIZER_BOOL_KEYS:
            if value_type != i2._GGUF_BOOL:
                raise Pass215Iteration9ValidationError(f"PASS215_I9_TOKENIZER_BOOL_TYPE_INVALID:{key}")
            booleans[key] = bool(i2._read_gguf_value(reader, value_type, summarize_arrays=False))
            selected_types[key] = value_type
            continue
        i2._read_gguf_value(reader, value_type, summarize_arrays=True)

    if tokens is None or not tokens:
        raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_VOCABULARY_MISSING")
    if token_types is not None and len(token_types) != len(tokens):
        raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_TYPE_COUNT_MISMATCH")

    active_special_ids = {
        key: token_id for key, token_id in raw_special_ids.items()
        if 0 <= token_id < len(tokens)
    }
    inactive_special_ids = {
        key: token_id for key, token_id in raw_special_ids.items()
        if not 0 <= token_id < len(tokens)
    }
    vocabulary_root = i4base.hash216(
        "pass215-i9-authenticated-token-vocabulary",
        i4base.canonical_bytes(list(tokens)),
    )
    token_type_root = None
    if token_types is not None:
        token_type_root = i4base.hash216(
            "pass215-i9-authenticated-token-types",
            i4base.canonical_bytes(list(token_types)),
        )
    special_root = i4base.hash216(
        "pass215-i9-authenticated-special-token-metadata",
        i4base.canonical_bytes({
            "raw": raw_special_ids,
            "active": active_special_ids,
            "inactive": inactive_special_ids,
        }),
    )
    return {
        "version": version,
        "vocabulary_size": len(tokens),
        "tokens": tokens,
        "token_types": token_types,
        "tokenizer_model": tokenizer_model,
        "special_token_ids": active_special_ids,
        "raw_special_token_ids": raw_special_ids,
        "inactive_special_token_ids": inactive_special_ids,
        "special_token_metadata_root_hash216": special_root,
        "boolean_metadata": booleans,
        "selected_metadata_types": selected_types,
        "vocabulary_root_hash216": vocabulary_root,
        "token_type_root_hash216": token_type_root,
        "float_metadata_interpreted": False,
        "inactive_special_ids_are_not_selected": True,
    }


def build_authenticated_token_ingress_evidence(raw: bytes, *, filename: str, source: Mapping[str, Any], expected_sha256: str | None = None) -> Mapping[str, Any]:
    _reject_floats(source)
    actual_sha = sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration9ValidationError("PASS215_I9_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration9ValidationError("PASS215_I9_AUTHENTICATED_REAL_MODEL_IDENTITY_MISMATCH")

    i8_evidence = i8.build_multi_token_attention_evidence(
        raw, filename=filename, source=source, expected_sha256=expected_sha256
    )
    _validate_frozen_iteration8_evidence(i8_evidence)

    tokenizer = _read_tokenizer_metadata(raw)
    token_ids = _select_token_ids(tokenizer)
    embeddings = _extract_authenticated_embeddings(raw, tokenizer, token_ids)
    i6_evidence = i6.build_block_graph_evidence(
        raw, filename=filename, source=source, expected_sha256=expected_sha256
    )
    i6.validate_block_graph_evidence(i6_evidence)
    execution = _execute_forward_from_embeddings(raw, i6_evidence, embeddings["rows"])
    linears = execution.pop("linears")
    q4_control = i7._q4_row_semantic_control(linears["blk.0.attn_q.weight"])
    if not q4_control["exact"]:
        raise Pass215Iteration9ValidationError("PASS215_I9_Q4_ROW_SEMANTIC_CONTROL_FAILED")

    tokenizer_record = {
        "tokenizer_model": tokenizer["tokenizer_model"],
        "vocabulary_size": tokenizer["vocabulary_size"],
        "vocabulary_root_hash216": tokenizer["vocabulary_root_hash216"],
        "token_type_root_hash216": tokenizer["token_type_root_hash216"],
        "raw_special_token_ids": tokenizer["raw_special_token_ids"],
        "special_token_ids": tokenizer["special_token_ids"],
        "inactive_special_token_ids": tokenizer["inactive_special_token_ids"],
        "special_token_metadata_root_hash216": tokenizer["special_token_metadata_root_hash216"],
        "inactive_special_ids_are_not_selected": True,
        "boolean_metadata": tokenizer["boolean_metadata"],
        "selected_metadata_types": tokenizer["selected_metadata_types"],
        "float_metadata_interpreted": False,
    }
    source_record = {
        **dict(source),
        "filename": filename,
        "file_size_bytes": len(raw),
        "file_sha256": actual_sha,
        "expected_sha256_verified": expected_sha256 is None or actual_sha == expected_sha256,
    }
    evidence: dict[str, Any] = {
        "schema": EVIDENCE_SCHEMA,
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "repair_forward": {
            "supersedes_runtime_module": "hhs_pass215_iteration9_authenticated_token_ingress_v1",
            "reason": "GGUF special-token metadata may encode inactive out-of-range sentinel IDs",
            "raw_sentinel_metadata_preserved": True,
            "inactive_sentinel_selection_forbidden": True,
        },
        "authority": {
            "pass215_benchmark_authority_active": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
            "no_float_canonical_authority": True,
        },
        "inherits": {
            **_iteration8_bindings(),
            "iteration7_suite_root_hash216": i8.ITERATION7_SUITE_ROOT_HASH216,
            "iteration6_block_graph_root_hash216": i7.ITERATION6_BLOCK_GRAPH_ROOT_HASH216,
            "iteration5_nonlinear_suite_root_hash216": i6.ITERATION5_NONLINEAR_SUITE_ROOT_HASH216,
            "iteration4_suite_output_root_hash216": i5.ITERATION4_SUITE_OUTPUT_ROOT_HASH216,
            "iteration3_evidence_root_hash216": i4base.ITERATION3_EVIDENCE_ROOT_HASH216,
            "iteration2_evidence_root_hash216": i4base.ITERATION2_EVIDENCE_ROOT_HASH216,
            "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "source": source_record,
        "authenticated_tokenizer": tokenizer_record,
        "authenticated_token_ingress": {
            "selection_policy": "ORDERED_UNIQUE_ACTIVE_SPECIAL_TOKEN_IDS_THEN_LOWEST_UNUSED_IDS",
            "selected_token_ids": list(token_ids),
            "selected_tokens": embeddings["selected_tokens"],
            "embedding_tensor": embeddings["tensor_binding"],
            "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"],
            "embedding_lookup_work": embeddings["embedding_lookup_work"],
            "text_tokenization_executed": False,
        },
        "forward_geometry": {
            "block": "blk.0",
            "sequence_length": SEQUENCE_LENGTH,
            "embedding_width": EMBEDDING_WIDTH,
            "ffn_width": i8.FFN_WIDTH,
            "head_count": i8.HEAD_COUNT,
            "head_dimension": i8.HEAD_DIMENSION,
            "causal_attention": True,
            "token_input_surface": "AUTHENTICATED_GGUF_TOKEN_IDS_TO_EXACT_Q4_0_EMBEDDING_ROWS",
            "token_embedding_lookup_executed": True,
        },
        "token_ingress_coordinate_forward": execution,
        "exact_controls": {
            "iteration8_frozen_roots_reexecuted_and_bound": {"exact": True, **_iteration8_bindings()},
            "q4_0_factored_row_matches_iteration4_exact_execution": q4_control,
            "selected_token_ids_unique_and_in_range": {"exact": len(set(token_ids)) == SEQUENCE_LENGTH and all(0 <= token_id < tokenizer["vocabulary_size"] for token_id in token_ids)},
            "inactive_special_ids_not_selected": {"exact": all(token_id not in token_ids for token_id in tokenizer["inactive_special_token_ids"].values()), "inactive_special_token_ids": tokenizer["inactive_special_token_ids"]},
            "embedding_rows_source_bound": {"exact": True, "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"]},
            "causal_edge_set_exact": {"exact": execution["causal_controls"]["edge_set_exact"], "future_edges_materialized": False},
            "rope_position_zero_identity": {"exact": execution["rope_controls"]["position_zero_exact_identity"]},
            "rope_nonzero_positions_materialized": {"exact": execution["rope_controls"]["all_nonzero_positions_change_q_and_k_roots"]},
            "singleton_softmax_identity": {"exact": execution["causal_controls"]["singleton_softmax_exact_identity"]},
        },
        "claims": {
            "authenticated_iteration8_roots_inherited_unchanged": True,
            "authenticated_tokenizer_metadata_bound": True,
            "inactive_special_token_sentinels_preserved": True,
            "authenticated_token_ids_selected": True,
            "exact_q4_0_token_embedding_lookup_executed": True,
            "contracted_four_token_embedding_ingress_executed": True,
            "contracted_sequence_length_four_blk0_forward_executed": True,
            "cross_token_causal_attention_executed": True,
            "exact_closed_form_nonlinear_transitions_executed": True,
            "text_tokenization_executed": False,
            "general_arbitrary_sequence_length_transformer_forward_executed": False,
            "multi_block_transformer_forward_executed": False,
            "full_model_forward_executed": False,
            "output_logits_executed": False,
            "numeric_transcendental_evaluation_performed": False,
            "approximate_transcendental_evaluation_performed": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "runtime_mutation_performed": False,
            "canonical_mutation_performed": False,
        },
    }
    roots = {
        "tokenizer_vocabulary_root_hash216": tokenizer["vocabulary_root_hash216"],
        "special_token_metadata_root_hash216": tokenizer["special_token_metadata_root_hash216"],
        "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"],
        "stage_suite_root_hash216": execution["executed_stage_suite_root_hash216"],
        "causal_attention_root_hash216": execution["causal_attention_root_hash216"],
        "final_output_root_hash216": execution["final_output_root_hash216"],
        "symbolic_dag_root_hash216": execution["symbolic_dag"]["ordered_node_root_hash216"],
    }
    suite_root = i4base.hash216("pass215-i9-authenticated-token-ingress-suite", i4base.canonical_bytes(roots))
    evidence["token_ingress_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216("pass215-i9-authenticated-token-ingress-evidence", i4base.canonical_bytes(evidence))
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION9_AUTHENTICATED_TOKEN_INGRESS"},
        {"sequence": 9, "parent_hash72": v1.ITERATION8_RECEIPT_HASH72, "evidence_root_hash216": evidence_root, "token_ingress_suite_root_hash216": suite_root},
    )
    _reject_floats(evidence)
    return evidence


def build_authenticated_token_ingress_evidence_from_path(path: str | Path, *, source: Mapping[str, Any], expected_sha256: str | None = None) -> Mapping[str, Any]:
    target = Path(path)
    return build_authenticated_token_ingress_evidence(
        target.read_bytes(), filename=target.name, source=source, expected_sha256=expected_sha256
    )


def validate_authenticated_token_ingress_evidence(evidence: Mapping[str, Any]) -> None:
    v1.validate_authenticated_token_ingress_evidence(evidence)
    tokenizer = evidence.get("authenticated_tokenizer")
    if not isinstance(tokenizer, Mapping):
        raise Pass215Iteration9ValidationError("PASS215_I9_V2_TOKENIZER_MISSING")
    raw_ids = tokenizer.get("raw_special_token_ids")
    active_ids = tokenizer.get("special_token_ids")
    inactive_ids = tokenizer.get("inactive_special_token_ids")
    if not isinstance(raw_ids, Mapping) or not isinstance(active_ids, Mapping) or not isinstance(inactive_ids, Mapping):
        raise Pass215Iteration9ValidationError("PASS215_I9_V2_SPECIAL_TOKEN_CLASSIFICATION_MISSING")
    if dict(raw_ids) != {**dict(active_ids), **dict(inactive_ids)}:
        raise Pass215Iteration9ValidationError("PASS215_I9_V2_SPECIAL_TOKEN_PARTITION_INVALID")
    vocab_size = int(tokenizer["vocabulary_size"])
    if any(not 0 <= int(value) < vocab_size for value in active_ids.values()):
        raise Pass215Iteration9ValidationError("PASS215_I9_V2_ACTIVE_SPECIAL_ID_RANGE_INVALID")
    if any(0 <= int(value) < vocab_size for value in inactive_ids.values()):
        raise Pass215Iteration9ValidationError("PASS215_I9_V2_INACTIVE_SPECIAL_ID_RANGE_INVALID")
    selected = set(int(value) for value in evidence["authenticated_token_ingress"]["selected_token_ids"])
    if any(int(value) in selected for value in inactive_ids.values()):
        raise Pass215Iteration9ValidationError("PASS215_I9_V2_INACTIVE_SPECIAL_ID_SELECTED")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_authenticated_token_ingress_evidence(left)
    validate_authenticated_token_ingress_evidence(right)
    return v1.compare_replay(left, right)


__all__ = [
    "CONTRACT", "PASS_NUMBER", "ITERATION", "EVIDENCE_SCHEMA", "VALIDATION_SCHEMA", "REPLAY_SCHEMA",
    "REAL_MODEL_SHA256", "SEQUENCE_LENGTH", "EMBEDDING_WIDTH", "TOKEN_EMBEDDING_TENSOR", "Q4_0_ROW_BYTES",
    "Pass215Iteration9Error", "Pass215Iteration9ValidationError", "_read_tokenizer_metadata", "_select_token_ids",
    "_decode_q4_0_embedding_row", "build_authenticated_token_ingress_evidence",
    "build_authenticated_token_ingress_evidence_from_path", "validate_authenticated_token_ingress_evidence", "compare_replay",
]
