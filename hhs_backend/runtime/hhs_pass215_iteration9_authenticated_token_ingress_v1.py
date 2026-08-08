"""Pass 215 Iteration 9 authenticated tokenizer and token-embedding ingress.

Iteration 9 replaces the four deterministic external hidden-state controls from
Iteration 8 with four exact rows from the authenticated GGUF token embedding
matrix.  Token IDs are selected deterministically from authenticated tokenizer
metadata; the corresponding Q4_0 rows are decoded directly from source bytes
using the frozen Iteration 4 binary16/rational and nibble semantics.

The selected exact embeddings then enter the frozen four-position causal blk.0
symbolic topology from Iteration 8.  Arbitrary text tokenization, arbitrary
sequence length, multi-block/full-model execution, numeric transcendental
approximation, dense-forward replacement, runtime mutation, and canonical
mutation remain outside this benchmark authority.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration2_open_transformer_container_v1 as i2
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v4 as i4
from hhs_backend.runtime import hhs_pass215_iteration5_exact_nonlinear_symbolic_v1 as i5
from hhs_backend.runtime import hhs_pass215_iteration6_authenticated_block_graph_v1 as i6
from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7
from hhs_backend.runtime import hhs_pass215_iteration8_multi_token_causal_attention_v1 as i8

CONTRACT = "HHS-P215-I9-AUTHENTICATED-TOKENIZER-TOKEN-EMBEDDING-INGRESS"
PASS_NUMBER = 215
ITERATION = 9
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_9_AUTHENTICATED_TOKEN_INGRESS_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_9_AUTHENTICATED_TOKEN_INGRESS_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_9_AUTHENTICATED_TOKEN_INGRESS_REPLAY_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_9_AUTHENTICATED_TOKEN_INGRESS_BENCHMARK"

ITERATION8_CLOSURE_HEAD = "a1deea46accf94dac0322d215e74a1e6616a4e1b"
ITERATION8_CLOSURE_TREE = "4ec05cb3f6555005220098a55cab1dec0e0dfa61"
ITERATION8_STAGE_SUITE_ROOT_HASH216 = "dbcc426e3629a8083f180094405ceffb5ef4da3035b3851ed95f8b7d0c0f3b1a"
ITERATION8_CAUSAL_ATTENTION_ROOT_HASH216 = "07c9e6cc21f7ed2e199644de322cd4d1bb9e3b2388ffba39baa42596310a4fde"
ITERATION8_FINAL_OUTPUT_ROOT_HASH216 = "5782d725ab356dbb33207ce59767b8cae1895b7bb859eeb40c2772e9d767a041"
ITERATION8_SYMBOLIC_DAG_ROOT_HASH216 = "5bf30a850b8ce083c7c01c3a56fd83e18de28ca2c0aeb6d5f439cd384f9122b0"
ITERATION8_SUITE_ROOT_HASH216 = "a21a7aedf633678510a701f93b39f785ce50c599228a6c194473ae6faea35b71"
ITERATION8_EVIDENCE_ROOT_HASH216 = "8ae3bdfb8768c37dfd4c66a491b985b3089378c655a7292ee406bbaa615c8465"
ITERATION8_RECEIPT_HASH72 = "eiQHZ*rGQTWvLkh!RK*>i-0B1e9Wol>oqFKv<UurZ1fNu8oDtU/Do!ar4gjkzmpF2B7cFqrb"
ITERATION8_SOURCE_ARTIFACT_SHA256 = "6450cf0080ae229785e6a0a862f9b16ec5506c70b4787ad7cc569eca4b6c7130"

REAL_MODEL_SHA256 = i8.REAL_MODEL_SHA256
SEQUENCE_LENGTH = i8.SEQUENCE_LENGTH
EMBEDDING_WIDTH = i8.EMBEDDING_WIDTH
FFN_WIDTH = i8.FFN_WIDTH
HEAD_COUNT = i8.HEAD_COUNT
HEAD_DIMENSION = i8.HEAD_DIMENSION
TOKEN_EMBEDDING_TENSOR = "token_embd.weight"
Q4_0_ROW_BYTES = (EMBEDDING_WIDTH // i4base.Q4_0_BLOCK_ELEMENTS) * i4base.Q4_0_BLOCK_BYTES

TOKEN_ARRAY_KEY = "tokenizer.ggml.tokens"
TOKEN_TYPE_ARRAY_KEY = "tokenizer.ggml.token_type"
TOKENIZER_MODEL_KEY = "tokenizer.ggml.model"
SPECIAL_TOKEN_KEYS = (
    "tokenizer.ggml.bos_token_id",
    "tokenizer.ggml.eos_token_id",
    "tokenizer.ggml.unknown_token_id",
    "tokenizer.ggml.separator_token_id",
    "tokenizer.ggml.padding_token_id",
)
TOKENIZER_BOOL_KEYS = (
    "tokenizer.ggml.add_bos_token",
    "tokenizer.ggml.add_eos_token",
)


class Pass215Iteration9Error(RuntimeError):
    pass


class Pass215Iteration9ValidationError(Pass215Iteration9Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration9ValidationError(f"PASS215_I9_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _is_integer_metadata_type(value_type: int) -> bool:
    return value_type in {
        i2._GGUF_UINT8, i2._GGUF_INT8, i2._GGUF_UINT16, i2._GGUF_INT16,
        i2._GGUF_UINT32, i2._GGUF_INT32, i2._GGUF_UINT64, i2._GGUF_INT64,
    }


def _read_tokenizer_metadata(raw: bytes) -> Mapping[str, Any]:
    """Read only tokenizer metadata needed for authenticated token ingress.

    Frozen Iteration 2 continues to summarize generic arrays.  This selected-key
    reader materializes only UTF-8 token strings and integer token types; float
    metadata (notably tokenizer scores) is never decoded to Python floats.
    """
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
    special_ids: dict[str, int] = {}
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
            token_types = tuple(int(i2._read_gguf_value(reader, element_type, summarize_arrays=False)) for _ in range(count))
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
            special_ids[key] = int(i2._read_gguf_value(reader, value_type, summarize_arrays=False))
            selected_types[key] = value_type
            continue
        if key in TOKENIZER_BOOL_KEYS:
            if value_type != i2._GGUF_BOOL:
                raise Pass215Iteration9ValidationError(f"PASS215_I9_TOKENIZER_BOOL_TYPE_INVALID:{key}")
            booleans[key] = bool(i2._read_gguf_value(reader, value_type, summarize_arrays=False))
            selected_types[key] = value_type
            continue
        # Consume every non-selected metadata value through the frozen parser.
        # Float scalars/arrays remain opaque bit records or are only traversed.
        i2._read_gguf_value(reader, value_type, summarize_arrays=True)

    if tokens is None or not tokens:
        raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_VOCABULARY_MISSING")
    if token_types is not None and len(token_types) != len(tokens):
        raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_TYPE_COUNT_MISMATCH")
    for key, token_id in special_ids.items():
        if not 0 <= token_id < len(tokens):
            raise Pass215Iteration9ValidationError(f"PASS215_I9_SPECIAL_TOKEN_ID_RANGE:{key}")

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
    return {
        "version": version,
        "vocabulary_size": len(tokens),
        "tokens": tokens,
        "token_types": token_types,
        "tokenizer_model": tokenizer_model,
        "special_token_ids": special_ids,
        "boolean_metadata": booleans,
        "selected_metadata_types": selected_types,
        "vocabulary_root_hash216": vocabulary_root,
        "token_type_root_hash216": token_type_root,
        "float_metadata_interpreted": False,
    }


def _select_token_ids(tokenizer: Mapping[str, Any]) -> tuple[int, ...]:
    vocab_size = int(tokenizer["vocabulary_size"])
    if vocab_size < SEQUENCE_LENGTH:
        raise Pass215Iteration9ValidationError("PASS215_I9_VOCABULARY_TOO_SMALL")
    specials = tokenizer.get("special_token_ids")
    if not isinstance(specials, Mapping):
        raise Pass215Iteration9ValidationError("PASS215_I9_SPECIAL_TOKEN_MAP_INVALID")
    selected: list[int] = []
    for key in SPECIAL_TOKEN_KEYS:
        if key in specials:
            token_id = int(specials[key])
            if 0 <= token_id < vocab_size and token_id not in selected:
                selected.append(token_id)
            if len(selected) == SEQUENCE_LENGTH:
                break
    for token_id in range(vocab_size):
        if len(selected) == SEQUENCE_LENGTH:
            break
        if token_id not in selected:
            selected.append(token_id)
    if len(selected) != SEQUENCE_LENGTH or len(set(selected)) != SEQUENCE_LENGTH:
        raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_SELECTION_FAILED")
    return tuple(selected)


def _decode_q4_0_embedding_row(row_raw: bytes) -> tuple[tuple[int, int], ...]:
    if len(row_raw) != Q4_0_ROW_BYTES:
        raise Pass215Iteration9ValidationError("PASS215_I9_EMBEDDING_ROW_BYTE_GEOMETRY_INVALID")
    values: list[tuple[int, int]] = []
    cursor = 0
    while cursor < len(row_raw):
        block = row_raw[cursor:cursor + i4base.Q4_0_BLOCK_BYTES]
        cursor += i4base.Q4_0_BLOCK_BYTES
        if len(block) != i4base.Q4_0_BLOCK_BYTES:
            raise Pass215Iteration9ValidationError("PASS215_I9_EMBEDDING_BLOCK_TRUNCATED")
        scale_n, scale_d = i4base.decode_binary16_exact(block[:2])
        quants = i4base.decode_q4_0_codes(block[2:])
        for quant in quants:
            values.append(i5.q_pair(i5.q(int(quant) * scale_n, scale_d)))
    if len(values) != EMBEDDING_WIDTH:
        raise Pass215Iteration9ValidationError("PASS215_I9_EMBEDDING_ROW_COORDINATE_COUNT_INVALID")
    return tuple(values)


def _extract_authenticated_embeddings(raw: bytes, tokenizer: Mapping[str, Any], token_ids: Sequence[int]) -> Mapping[str, Any]:
    parsed = i4base.parse_gguf(raw)
    by_name = {tensor.name: tensor for tensor in parsed.tensors}
    tensor = by_name.get(TOKEN_EMBEDDING_TENSOR)
    if tensor is None:
        raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_EMBEDDING_TENSOR_MISSING")
    vocab_size = int(tokenizer["vocabulary_size"])
    expected_shape = (EMBEDDING_WIDTH, vocab_size)
    if tensor.storage_type != "Q4_0" or tuple(tensor.shape) != expected_shape:
        raise Pass215Iteration9ValidationError(
            f"PASS215_I9_TOKEN_EMBEDDING_GEOMETRY_INVALID:{tensor.storage_type}:{tuple(tensor.shape)}"
        )
    expected_bytes = Q4_0_ROW_BYTES * vocab_size
    if tensor.data_size != expected_bytes:
        raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_EMBEDDING_BYTE_COUNT_INVALID")
    payload = raw[tensor.data_offset:tensor.data_offset + tensor.data_size]
    if sha256(payload).hexdigest() != tensor.source_sha256:
        raise Pass215Iteration9ValidationError("PASS215_I9_TOKEN_EMBEDDING_SOURCE_SHA_MISMATCH")

    tokens = tokenizer["tokens"]
    token_types = tokenizer.get("token_types")
    rows: list[tuple[tuple[int, int], ...]] = []
    records: list[Mapping[str, Any]] = []
    for position, raw_id in enumerate(token_ids):
        token_id = int(raw_id)
        if not 0 <= token_id < vocab_size:
            raise Pass215Iteration9ValidationError("PASS215_I9_SELECTED_TOKEN_ID_RANGE_INVALID")
        start = token_id * Q4_0_ROW_BYTES
        row_raw = payload[start:start + Q4_0_ROW_BYTES]
        row = _decode_q4_0_embedding_row(row_raw)
        row_payload = [
            {"numerator": int(numerator), "denominator": int(denominator)}
            for numerator, denominator in row
        ]
        row_root = i4base.hash216(
            "pass215-i9-exact-token-embedding-row",
            i4base.canonical_bytes({"token_id": token_id, "coordinates": row_payload}),
        )
        record = {
            "position": position,
            "token_id": token_id,
            "token": str(tokens[token_id]),
            "token_type": None if token_types is None else int(token_types[token_id]),
            "row_source_offset_bytes": start,
            "row_source_bytes": len(row_raw),
            "row_source_sha256": sha256(row_raw).hexdigest(),
            "coordinate_count": len(row),
            "embedding_row_root_hash216": row_root,
        }
        rows.append(row)
        records.append(record)
    suite_root = i4base.hash216(
        "pass215-i9-exact-token-embedding-suite",
        i4base.canonical_bytes(records),
    )
    return {
        "rows": tuple(rows),
        "selected_tokens": records,
        "embedding_suite_root_hash216": suite_root,
        "tensor_binding": {
            "name": tensor.name,
            "shape": list(expected_shape),
            "storage_type": tensor.storage_type,
            "source_sha256": tensor.source_sha256,
            "source_bytes": tensor.data_size,
            "row_bytes": Q4_0_ROW_BYTES,
            "blocks_per_row": EMBEDDING_WIDTH // i4base.Q4_0_BLOCK_ELEMENTS,
        },
        "embedding_lookup_work": {
            "selected_token_count": len(records),
            "q4_0_blocks_decoded": len(records) * (EMBEDDING_WIDTH // i4base.Q4_0_BLOCK_ELEMENTS),
            "exact_embedding_coordinates_materialized": len(records) * EMBEDDING_WIDTH,
            "source_row_bytes_read": len(records) * Q4_0_ROW_BYTES,
        },
    }


def _iteration8_bindings() -> Mapping[str, Any]:
    return {
        "iteration8_closure_head": ITERATION8_CLOSURE_HEAD,
        "iteration8_closure_tree": ITERATION8_CLOSURE_TREE,
        "iteration8_stage_suite_root_hash216": ITERATION8_STAGE_SUITE_ROOT_HASH216,
        "iteration8_causal_attention_root_hash216": ITERATION8_CAUSAL_ATTENTION_ROOT_HASH216,
        "iteration8_final_output_root_hash216": ITERATION8_FINAL_OUTPUT_ROOT_HASH216,
        "iteration8_symbolic_dag_root_hash216": ITERATION8_SYMBOLIC_DAG_ROOT_HASH216,
        "iteration8_suite_root_hash216": ITERATION8_SUITE_ROOT_HASH216,
        "iteration8_evidence_root_hash216": ITERATION8_EVIDENCE_ROOT_HASH216,
        "iteration8_receipt_hash72": ITERATION8_RECEIPT_HASH72,
        "iteration8_source_artifact_sha256": ITERATION8_SOURCE_ARTIFACT_SHA256,
    }


def _validate_frozen_iteration8_evidence(evidence: Mapping[str, Any]) -> None:
    i8.validate_multi_token_attention_evidence(evidence)
    execution = evidence["multi_token_coordinate_forward"]
    required = {
        "executed_stage_suite_root_hash216": ITERATION8_STAGE_SUITE_ROOT_HASH216,
        "causal_attention_root_hash216": ITERATION8_CAUSAL_ATTENTION_ROOT_HASH216,
        "final_output_root_hash216": ITERATION8_FINAL_OUTPUT_ROOT_HASH216,
    }
    for key, expected in required.items():
        if execution.get(key) != expected:
            raise Pass215Iteration9ValidationError(f"PASS215_I9_ITERATION8_ROOT_MISMATCH:{key}")
    if execution["symbolic_dag"].get("ordered_node_root_hash216") != ITERATION8_SYMBOLIC_DAG_ROOT_HASH216:
        raise Pass215Iteration9ValidationError("PASS215_I9_ITERATION8_DAG_ROOT_MISMATCH")
    if evidence.get("multi_token_attention_suite_root_hash216") != ITERATION8_SUITE_ROOT_HASH216:
        raise Pass215Iteration9ValidationError("PASS215_I9_ITERATION8_SUITE_ROOT_MISMATCH")
    if evidence.get("evidence_root_hash216") != ITERATION8_EVIDENCE_ROOT_HASH216:
        raise Pass215Iteration9ValidationError("PASS215_I9_ITERATION8_EVIDENCE_ROOT_MISMATCH")
    if evidence.get("receipt_hash72") != ITERATION8_RECEIPT_HASH72:
        raise Pass215Iteration9ValidationError("PASS215_I9_ITERATION8_RECEIPT_MISMATCH")


def _execute_forward_from_embeddings(raw: bytes, i6_evidence: Mapping[str, Any], embedding_rows: Sequence[Sequence[tuple[int, int]]]) -> Mapping[str, Any]:
    if len(embedding_rows) != SEQUENCE_LENGTH or any(len(row) != EMBEDDING_WIDTH for row in embedding_rows):
        raise Pass215Iteration9ValidationError("PASS215_I9_EMBEDDING_INPUT_GEOMETRY_INVALID")
    dag = i8.MultiTokenSymbolicDAG()
    stages: dict[str, Mapping[str, Any]] = {}
    linear_work = {"row_transitions": 0, "logical_weight_products": 0, "logical_accumulation_additions": 0}

    def record(stage: str, tokens: Sequence[Sequence[str]]) -> tuple[tuple[str, ...], ...]:
        normalized = tuple(tuple(values) for values in tokens)
        stages[stage] = i8._stage_manifest(dag, stage, normalized)
        return normalized

    hidden = record("hidden_state_input", tuple(
        tuple(dag.q(numerator, denominator) for numerator, denominator in row)
        for row in embedding_rows
    ))
    bindings = i6_evidence["authenticated_block_tensor_bindings"]
    attn_weights = i7._norm_values(bindings["norm_tensors"][i6.NORM_TENSORS[0]])
    ffn_weights = i7._norm_values(bindings["norm_tensors"][i6.NORM_TENSORS[1]])
    linears = i7._compile_linears(raw)
    attn_norm = record("rmsnorm_attn", tuple(i7._exact_rmsnorm_dag(dag, values, attn_weights) for values in hidden))

    def linear(stage: str, tensor_name: str, tokens: Sequence[Sequence[str]]) -> tuple[tuple[str, ...], ...]:
        outputs = []
        for position, inputs in enumerate(tokens):
            values, work = i7._linear_symbolic(dag, linears[tensor_name], inputs, stage=f"{stage}:token:{position}")
            for key in linear_work:
                linear_work[key] += int(work[key])
            outputs.append(tuple(values))
        return record(stage, outputs)

    q_values = linear("linear_attn_q", "blk.0.attn_q.weight", attn_norm)
    k_values = linear("linear_attn_k", "blk.0.attn_k.weight", attn_norm)
    v_values = linear("linear_attn_v", "blk.0.attn_v.weight", attn_norm)
    q_rope = record("rope_q", tuple(i8._rope_token(dag, values, position=p) for p, values in enumerate(q_values)))
    k_rope = record("rope_k", tuple(i8._rope_token(dag, values, position=p) for p, values in enumerate(k_values)))

    score_tokens: list[tuple[str, ...]] = []
    scale_tokens: list[tuple[str, ...]] = []
    probability_tokens: list[tuple[str, ...]] = []
    softmax_records: list[Mapping[str, Any]] = []
    causal_edges: list[Mapping[str, int]] = []
    by_query_head: dict[tuple[int, int], tuple[str, ...]] = {}
    scale = dag.rsqrt(dag.q(HEAD_DIMENSION))
    for query in range(SEQUENCE_LENGTH):
        query_scores: list[str] = []
        query_scaled: list[str] = []
        query_probs: list[str] = []
        for head in range(HEAD_COUNT):
            start, end = head * HEAD_DIMENSION, (head + 1) * HEAD_DIMENSION
            head_scores: list[str] = []
            for key in range(query + 1):
                score = i7._dot(dag, q_rope[query][start:end], k_rope[key][start:end])
                head_scores.append(score)
                query_scores.append(score)
                causal_edges.append({"head": head, "query_position": query, "key_position": key})
            scaled = tuple(dag.mul(score, scale) for score in head_scores)
            probabilities, softmax_record = i8._exact_causal_softmax(dag, scaled)
            by_query_head[(query, head)] = probabilities
            query_scaled.extend(scaled)
            query_probs.extend(probabilities)
            softmax_records.append({
                "head": head,
                "query_position": query,
                "causal_key_positions": list(range(query + 1)),
                **softmax_record,
                "probability_roots": list(probabilities),
            })
        score_tokens.append(tuple(query_scores))
        scale_tokens.append(tuple(query_scaled))
        probability_tokens.append(tuple(query_probs))
    record("attention_qk_dot", score_tokens)
    record("attention_scale", scale_tokens)
    record("attention_softmax", probability_tokens)

    weighted_tokens: list[tuple[str, ...]] = []
    for query in range(SEQUENCE_LENGTH):
        weighted: list[str] = []
        for head in range(HEAD_COUNT):
            start = head * HEAD_DIMENSION
            probabilities = by_query_head[(query, head)]
            for dimension in range(HEAD_DIMENSION):
                terms = tuple(
                    dag.mul(probabilities[key], v_values[key][start + dimension])
                    for key in range(query + 1)
                )
                weighted.append(dag.add(*terms))
        weighted_tokens.append(tuple(weighted))
    weighted_values = record("attention_weighted_value", weighted_tokens)
    concatenated = record("attention_concat", weighted_values)
    attn_output = linear("linear_attn_output", "blk.0.attn_output.weight", concatenated)
    post_attn = record("residual_attention", tuple(
        tuple(dag.add(left, right) for left, right in zip(hidden[position], attn_output[position]))
        for position in range(SEQUENCE_LENGTH)
    ))
    ffn_norm = record("rmsnorm_ffn", tuple(i7._exact_rmsnorm_dag(dag, values, ffn_weights) for values in post_attn))
    gate = linear("linear_ffn_gate", "blk.0.ffn_gate.weight", ffn_norm)
    activated = record("silu", tuple(tuple(i7._silu(dag, value) for value in values) for values in gate))
    up = linear("linear_ffn_up", "blk.0.ffn_up.weight", ffn_norm)
    gated = record("ffn_gate_product", tuple(
        tuple(dag.mul(left, right) for left, right in zip(activated[position], up[position]))
        for position in range(SEQUENCE_LENGTH)
    ))
    down = linear("linear_ffn_down", "blk.0.ffn_down.weight", gated)
    output = record("residual_ffn", tuple(
        tuple(dag.add(left, right) for left, right in zip(post_attn[position], down[position]))
        for position in range(SEQUENCE_LENGTH)
    ))

    if tuple(stages) != i6.GRAPH_OPS:
        raise Pass215Iteration9ValidationError("PASS215_I9_EXECUTED_STAGE_TOPOLOGY_INVALID")
    if any(len(values) != EMBEDDING_WIDTH for values in output):
        raise Pass215Iteration9ValidationError("PASS215_I9_FINAL_OUTPUT_GEOMETRY_INVALID")
    observed_edges = tuple((r["head"], r["query_position"], r["key_position"]) for r in causal_edges)
    if observed_edges != i8._expected_causal_edges():
        raise Pass215Iteration9ValidationError("PASS215_I9_CAUSAL_EDGE_SET_INVALID")
    zero_identity = q_rope[0] == q_values[0] and k_rope[0] == k_values[0]
    nonzero_changes = all(q_rope[p] != q_values[p] and k_rope[p] != k_values[p] for p in range(1, SEQUENCE_LENGTH))
    singleton_identity = all(by_query_head[(0, head)] == (dag.q(1),) for head in range(HEAD_COUNT))
    if not zero_identity or not nonzero_changes or not singleton_identity:
        raise Pass215Iteration9ValidationError("PASS215_I9_EXACT_ATTENTION_CONTROL_FAILED")

    expected_linear = {
        "row_transitions": 2976 * SEQUENCE_LENGTH,
        "logical_weight_products": 995328 * SEQUENCE_LENGTH,
        "logical_accumulation_additions": 992352 * SEQUENCE_LENGTH,
    }
    if linear_work != expected_linear:
        raise Pass215Iteration9ValidationError("PASS215_I9_LINEAR_WORK_GEOMETRY_INVALID")

    token_output_roots = [
        i4base.hash216(
            "pass215-i9-final-token-coordinate-roots",
            i4base.canonical_bytes({"position": position, "roots": list(values)}),
        )
        for position, values in enumerate(output)
    ]
    attention_payload = {
        "causal_edges": causal_edges,
        "softmax_records": softmax_records,
        "qk_stage_root": stages["attention_qk_dot"]["stage_root_hash216"],
        "scale_stage_root": stages["attention_scale"]["stage_root_hash216"],
        "softmax_stage_root": stages["attention_softmax"]["stage_root_hash216"],
        "weighted_stage_root": stages["attention_weighted_value"]["stage_root_hash216"],
    }
    return {
        "stage_records": stages,
        "executed_stage_suite_root_hash216": i4base.hash216("pass215-i9-executed-stage-suite", i4base.canonical_bytes(stages)),
        "causal_attention_root_hash216": i4base.hash216("pass215-i9-causal-attention-suite", i4base.canonical_bytes(attention_payload)),
        "final_output_token_roots": token_output_roots,
        "final_output_root_hash216": i4base.hash216("pass215-i9-final-output-token-suite", i4base.canonical_bytes(token_output_roots)),
        "final_output_token_count": len(output),
        "final_output_coordinate_count": sum(len(values) for values in output),
        "causal_edges": causal_edges,
        "softmax_records": softmax_records,
        "symbolic_dag": dag.manifest(),
        "linear_transition_work": linear_work,
        "attention_transition_work": i8._attention_work_geometry(),
        "rope_controls": {
            "position_zero_exact_identity": zero_identity,
            "all_nonzero_positions_change_q_and_k_roots": nonzero_changes,
        },
        "causal_controls": {
            "future_edges_materialized": False,
            "edge_set_exact": observed_edges == i8._expected_causal_edges(),
            "singleton_softmax_exact_identity": singleton_identity,
            "softmax_denominators_use_causal_terms_only": all(
                record["context_length"] == record["query_position"] + 1
                and record["causal_key_positions"] == list(range(record["query_position"] + 1))
                for record in softmax_records
            ),
        },
        "linears": linears,
    }


def build_authenticated_token_ingress_evidence(raw: bytes, *, filename: str, source: Mapping[str, Any], expected_sha256: str | None = None) -> Mapping[str, Any]:
    _reject_floats(source)
    actual_sha = sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration9ValidationError("PASS215_I9_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration9ValidationError("PASS215_I9_AUTHENTICATED_REAL_MODEL_IDENTITY_MISMATCH")

    # Re-execute Iteration 8 on the same authenticated bytes and bind all frozen
    # roots before changing the ingress surface.
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
        "special_token_ids": tokenizer["special_token_ids"],
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
            "selection_policy": "ORDERED_UNIQUE_SPECIAL_TOKEN_IDS_THEN_LOWEST_UNUSED_IDS",
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
            "ffn_width": FFN_WIDTH,
            "head_count": HEAD_COUNT,
            "head_dimension": HEAD_DIMENSION,
            "causal_attention": True,
            "token_input_surface": "AUTHENTICATED_GGUF_TOKEN_IDS_TO_EXACT_Q4_0_EMBEDDING_ROWS",
            "token_embedding_lookup_executed": True,
        },
        "token_ingress_coordinate_forward": execution,
        "exact_controls": {
            "iteration8_frozen_roots_reexecuted_and_bound": {"exact": True, **_iteration8_bindings()},
            "q4_0_factored_row_matches_iteration4_exact_execution": q4_control,
            "selected_token_ids_unique_and_in_range": {"exact": len(set(token_ids)) == SEQUENCE_LENGTH and all(0 <= token_id < tokenizer["vocabulary_size"] for token_id in token_ids)},
            "embedding_rows_source_bound": {"exact": True, "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"]},
            "causal_edge_set_exact": {"exact": execution["causal_controls"]["edge_set_exact"], "future_edges_materialized": False},
            "rope_position_zero_identity": {"exact": execution["rope_controls"]["position_zero_exact_identity"]},
            "rope_nonzero_positions_materialized": {"exact": execution["rope_controls"]["all_nonzero_positions_change_q_and_k_roots"]},
            "singleton_softmax_identity": {"exact": execution["causal_controls"]["singleton_softmax_exact_identity"]},
        },
        "claims": {
            "authenticated_iteration8_roots_inherited_unchanged": True,
            "authenticated_tokenizer_metadata_bound": True,
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
        {
            "sequence": 9,
            "parent_hash72": ITERATION8_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "token_ingress_suite_root_hash216": suite_root,
        },
    )
    _reject_floats(evidence)
    return evidence


def build_authenticated_token_ingress_evidence_from_path(path: str | Path, *, source: Mapping[str, Any], expected_sha256: str | None = None) -> Mapping[str, Any]:
    target = Path(path)
    return build_authenticated_token_ingress_evidence(
        target.read_bytes(), filename=target.name, source=source, expected_sha256=expected_sha256
    )


def validate_authenticated_token_ingress_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT or evidence.get("iteration") != ITERATION:
        raise Pass215Iteration9ValidationError("PASS215_I9_EVIDENCE_IDENTITY_INVALID")
    authority = evidence.get("authority")
    if not isinstance(authority, Mapping) or authority.get("runtime_mutation_authority_promoted") is not False or authority.get("canonical_mutation_authorized") is not False or authority.get("migration_active") is not False or authority.get("no_float_canonical_authority") is not True:
        raise Pass215Iteration9ValidationError("PASS215_I9_FORBIDDEN_AUTHORITY_ESCALATION")
    inherited = evidence.get("inherits")
    if not isinstance(inherited, Mapping) or any(inherited.get(key) != value for key, value in _iteration8_bindings().items()):
        raise Pass215Iteration9ValidationError("PASS215_I9_ITERATION8_BINDING_INVALID")
    source = evidence.get("source")
    if not isinstance(source, Mapping) or source.get("file_sha256") != REAL_MODEL_SHA256:
        raise Pass215Iteration9ValidationError("PASS215_I9_SOURCE_BINDING_INVALID")
    tokenizer = evidence.get("authenticated_tokenizer")
    if not isinstance(tokenizer, Mapping) or int(tokenizer.get("vocabulary_size", 0)) <= 0 or tokenizer.get("float_metadata_interpreted") is not False:
        raise Pass215Iteration9ValidationError("PASS215_I9_TOKENIZER_BINDING_INVALID")
    ingress = evidence.get("authenticated_token_ingress")
    if not isinstance(ingress, Mapping):
        raise Pass215Iteration9ValidationError("PASS215_I9_INGRESS_MISSING")
    token_ids = ingress.get("selected_token_ids")
    if not isinstance(token_ids, list) or len(token_ids) != SEQUENCE_LENGTH or len(set(token_ids)) != SEQUENCE_LENGTH:
        raise Pass215Iteration9ValidationError("PASS215_I9_SELECTED_TOKEN_IDS_INVALID")
    selected = ingress.get("selected_tokens")
    if not isinstance(selected, list) or len(selected) != SEQUENCE_LENGTH:
        raise Pass215Iteration9ValidationError("PASS215_I9_SELECTED_TOKEN_RECORDS_INVALID")
    tensor = ingress.get("embedding_tensor")
    if not isinstance(tensor, Mapping) or tensor.get("name") != TOKEN_EMBEDDING_TENSOR or tensor.get("storage_type") != "Q4_0" or tensor.get("row_bytes") != Q4_0_ROW_BYTES:
        raise Pass215Iteration9ValidationError("PASS215_I9_EMBEDDING_TENSOR_BINDING_INVALID")
    work = ingress.get("embedding_lookup_work")
    if not isinstance(work, Mapping) or work.get("selected_token_count") != SEQUENCE_LENGTH or work.get("q4_0_blocks_decoded") != 36 or work.get("exact_embedding_coordinates_materialized") != 1152 or work.get("source_row_bytes_read") != 648:
        raise Pass215Iteration9ValidationError("PASS215_I9_EMBEDDING_WORK_INVALID")
    execution = evidence.get("token_ingress_coordinate_forward")
    if not isinstance(execution, Mapping) or execution.get("final_output_token_count") != SEQUENCE_LENGTH or execution.get("final_output_coordinate_count") != 1152:
        raise Pass215Iteration9ValidationError("PASS215_I9_FORWARD_GEOMETRY_INVALID")
    linear = execution.get("linear_transition_work")
    if linear != {"row_transitions": 11904, "logical_weight_products": 3981312, "logical_accumulation_additions": 3969408}:
        raise Pass215Iteration9ValidationError("PASS215_I9_LINEAR_WORK_INVALID")
    if execution.get("attention_transition_work") != i8._attention_work_geometry():
        raise Pass215Iteration9ValidationError("PASS215_I9_ATTENTION_WORK_INVALID")
    claims = evidence.get("claims")
    if not isinstance(claims, Mapping):
        raise Pass215Iteration9ValidationError("PASS215_I9_CLAIMS_MISSING")
    for key in (
        "authenticated_iteration8_roots_inherited_unchanged",
        "authenticated_tokenizer_metadata_bound",
        "authenticated_token_ids_selected",
        "exact_q4_0_token_embedding_lookup_executed",
        "contracted_four_token_embedding_ingress_executed",
        "contracted_sequence_length_four_blk0_forward_executed",
        "cross_token_causal_attention_executed",
        "exact_closed_form_nonlinear_transitions_executed",
    ):
        if claims.get(key) is not True:
            raise Pass215Iteration9ValidationError(f"PASS215_I9_REQUIRED_CLAIM_FALSE:{key}")
    for key in (
        "text_tokenization_executed",
        "general_arbitrary_sequence_length_transformer_forward_executed",
        "multi_block_transformer_forward_executed",
        "full_model_forward_executed",
        "output_logits_executed",
        "numeric_transcendental_evaluation_performed",
        "approximate_transcendental_evaluation_performed",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "runtime_mutation_performed",
        "canonical_mutation_performed",
    ):
        if claims.get(key) is not False:
            raise Pass215Iteration9ValidationError(f"PASS215_I9_BOUNDARY_CLAIM_INVALID:{key}")
    controls = evidence.get("exact_controls")
    if not isinstance(controls, Mapping) or not all(isinstance(record, Mapping) and record.get("exact") is True for record in controls.values()):
        raise Pass215Iteration9ValidationError("PASS215_I9_EXACT_CONTROL_INVALID")

    without_root = dict(evidence)
    recorded_root = without_root.pop("evidence_root_hash216", None)
    recorded_receipt = without_root.pop("receipt_hash72", None)
    expected_root = i4base.hash216("pass215-i9-authenticated-token-ingress-evidence", i4base.canonical_bytes(without_root))
    if recorded_root != expected_root:
        raise Pass215Iteration9ValidationError("PASS215_I9_EVIDENCE_ROOT_MISMATCH")
    expected_receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION9_AUTHENTICATED_TOKEN_INGRESS"},
        {
            "sequence": 9,
            "parent_hash72": ITERATION8_RECEIPT_HASH72,
            "evidence_root_hash216": expected_root,
            "token_ingress_suite_root_hash216": evidence["token_ingress_suite_root_hash216"],
        },
    )
    if recorded_receipt != expected_receipt:
        raise Pass215Iteration9ValidationError("PASS215_I9_RECEIPT_MISMATCH")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_authenticated_token_ingress_evidence(left)
    validate_authenticated_token_ingress_evidence(right)
    for key in ("token_ingress_suite_root_hash216", "evidence_root_hash216", "receipt_hash72"):
        if left.get(key) != right.get(key):
            raise Pass215Iteration9ValidationError("PASS215_I9_CROSS_PROCESS_REPLAY_MISMATCH")
    left_execution = left["token_ingress_coordinate_forward"]
    right_execution = right["token_ingress_coordinate_forward"]
    for key in ("executed_stage_suite_root_hash216", "causal_attention_root_hash216", "final_output_root_hash216"):
        if left_execution.get(key) != right_execution.get(key):
            raise Pass215Iteration9ValidationError(f"PASS215_I9_EXECUTION_REPLAY_MISMATCH:{key}")
    if left["authenticated_token_ingress"].get("embedding_suite_root_hash216") != right["authenticated_token_ingress"].get("embedding_suite_root_hash216"):
        raise Pass215Iteration9ValidationError("PASS215_I9_EMBEDDING_REPLAY_MISMATCH")
    return {
        "schema": REPLAY_SCHEMA,
        "semantic_exactness": True,
        "cross_process_replay": True,
        "tokenizer_vocabulary_root_hash216": left["authenticated_tokenizer"]["vocabulary_root_hash216"],
        "embedding_suite_root_hash216": left["authenticated_token_ingress"]["embedding_suite_root_hash216"],
        "stage_suite_root_hash216": left_execution["executed_stage_suite_root_hash216"],
        "causal_attention_root_hash216": left_execution["causal_attention_root_hash216"],
        "final_output_root_hash216": left_execution["final_output_root_hash216"],
        "token_ingress_suite_root_hash216": left["token_ingress_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }


__all__ = [
    "CONTRACT", "PASS_NUMBER", "ITERATION", "EVIDENCE_SCHEMA", "VALIDATION_SCHEMA", "REPLAY_SCHEMA",
    "ITERATION8_CLOSURE_HEAD", "ITERATION8_CLOSURE_TREE", "ITERATION8_STAGE_SUITE_ROOT_HASH216",
    "ITERATION8_CAUSAL_ATTENTION_ROOT_HASH216", "ITERATION8_FINAL_OUTPUT_ROOT_HASH216",
    "ITERATION8_SYMBOLIC_DAG_ROOT_HASH216", "ITERATION8_SUITE_ROOT_HASH216", "ITERATION8_EVIDENCE_ROOT_HASH216",
    "ITERATION8_RECEIPT_HASH72", "REAL_MODEL_SHA256", "TOKEN_EMBEDDING_TENSOR", "Q4_0_ROW_BYTES",
    "Pass215Iteration9Error", "Pass215Iteration9ValidationError", "_read_tokenizer_metadata", "_select_token_ids",
    "_decode_q4_0_embedding_row", "build_authenticated_token_ingress_evidence",
    "build_authenticated_token_ingress_evidence_from_path", "validate_authenticated_token_ingress_evidence", "compare_replay",
]
