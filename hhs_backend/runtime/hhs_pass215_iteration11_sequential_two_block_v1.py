"""Pass 215 Iteration 11 authenticated sequential two-block exact symbolic forward.

Preserves the frozen Iteration 10 text/token/embedding/blk.0 closure,
authenticates exact GGUF integer architecture metadata and the real blk.1 tensor
set, then executes blk.0 -> blk.1 sequentially for the same four-token text
witness inside one shared hash-consed symbolic DAG. Benchmark authority only:
no numeric transcendental approximation, Python-float canonical authority,
full-model/logit/generation claim, runtime mutation, canonical mutation, or
migration authority is introduced.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration2_open_transformer_container_v1 as i2
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration6_authenticated_block_graph_v1 as i6
from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7
from hhs_backend.runtime import hhs_pass215_iteration8_multi_token_causal_attention_v1 as i8
from hhs_backend.runtime import hhs_pass215_iteration9_authenticated_token_ingress_v2 as i9
from hhs_backend.runtime import hhs_pass215_iteration10_exact_text_token_ingress_v1 as i10

CONTRACT = "HHS-P215-I11-AUTHENTICATED-SEQUENTIAL-TWO-BLOCK-SYMBOLIC-FORWARD"
PASS_NUMBER = 215
ITERATION = 11
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_11_SEQUENTIAL_TWO_BLOCK_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_11_SEQUENTIAL_TWO_BLOCK_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_11_SEQUENTIAL_TWO_BLOCK_REPLAY_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_11_AUTHENTICATED_SEQUENTIAL_TWO_BLOCK_BENCHMARK"

ITERATION10_CLOSURE_HEAD = "aa7951d8be9ecef963e7d311f2e351b5c729a7e7"
ITERATION10_CLOSURE_TREE = "f2d823a22369ed932c1b2b6b2dc02dc55455a147"
ITERATION10_SCORE_STORAGE_ROOT_HASH216 = "c7b509f622556cc321a52fd348b2dda41d51ea96e39cc71bc42fef4ec77dbe95"
ITERATION10_EXACT_SCORE_ROOT_HASH216 = "d85f1debadf2e5fcd53fd4d4465bc99363ea173227a983534624c73e8f3e047c"
ITERATION10_TOKENIZATION_ROOT_HASH216 = "0f235d84816e54c35d9b4f1425c66a9bb129ac52fc1ce109f3937b4095996837"
ITERATION10_EMBEDDING_ROOT_HASH216 = "4c983072112a06ba41bbb94ca42d79f3e76dd25cf16091ffaa17961860ecc5e3"
ITERATION10_STAGE_SUITE_ROOT_HASH216 = "a879c3c00ddaee609ea62768ed6de06eb450fa2331eb05f1c8b30c19bfbbb065"
ITERATION10_CAUSAL_ATTENTION_ROOT_HASH216 = "e3746a9aab00dec1fd0c64cde4618fbc3b7e19d549a3107d4a5fce363b470ea2"
ITERATION10_FINAL_OUTPUT_ROOT_HASH216 = "05390b8c68285aa810bb8a1b37ea9f14dbf022709047a75ae402d50db5ca3a87"
ITERATION10_SYMBOLIC_DAG_ROOT_HASH216 = "175d6b80b4e6ba742843cdc4d155f035061f3a02e525543bae540e008bb9eee3"
ITERATION10_SUITE_ROOT_HASH216 = "c495f652c6056ee76353c188b70d58641d4934ba6662817978d96862d3e71d31"
ITERATION10_EVIDENCE_ROOT_HASH216 = "8e7accbeb1433d19e4056cb142c87796f891f99d96d02b0b5d4eecb1687f5658"
ITERATION10_RECEIPT_HASH72 = "dXWZm)?0Q2Lf6BLg!>hgEzRXB4IAbO922jV?vPCo7WBkOscF6qfS<X<sFZ-1NugyfpiW<QhS"
ITERATION10_CLOSURE_ARTIFACT_SHA256 = "89183f168de906d8a9b5c54455a51bdb8ff6e1259d1a045c0477f6b892ce6a2d"

REAL_MODEL_SHA256 = i10.REAL_MODEL_SHA256
CONTRACTED_PROMPT = i10.CONTRACTED_PROMPT
SEQUENCE_LENGTH = i10.SEQUENCE_LENGTH
EMBEDDING_WIDTH = i10.EMBEDDING_WIDTH
FFN_WIDTH = i8.FFN_WIDTH
HEAD_COUNT = i8.HEAD_COUNT
HEAD_DIMENSION = i8.HEAD_DIMENSION
BLOCK_INDEXES = (0, 1)
ARCHITECTURE_KEYS = {
    "block_count": "llama.block_count",
    "embedding_length": "llama.embedding_length",
    "feed_forward_length": "llama.feed_forward_length",
    "head_count": "llama.attention.head_count",
}
LINEAR_SUFFIX_SHAPES: Mapping[str, tuple[int, int]] = {
    "attn_q.weight": (EMBEDDING_WIDTH, EMBEDDING_WIDTH),
    "attn_k.weight": (EMBEDDING_WIDTH, EMBEDDING_WIDTH),
    "attn_v.weight": (EMBEDDING_WIDTH, EMBEDDING_WIDTH),
    "attn_output.weight": (EMBEDDING_WIDTH, EMBEDDING_WIDTH),
    "ffn_gate.weight": (EMBEDDING_WIDTH, FFN_WIDTH),
    "ffn_up.weight": (EMBEDDING_WIDTH, FFN_WIDTH),
    "ffn_down.weight": (FFN_WIDTH, EMBEDDING_WIDTH),
}
NORM_SUFFIXES = ("attn_norm.weight", "ffn_norm.weight")
GRAPH_OPS = i6.GRAPH_OPS


class Pass215Iteration11Error(RuntimeError):
    pass


class Pass215Iteration11ValidationError(Pass215Iteration11Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration11ValidationError(f"PASS215_I11_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _iteration10_bindings() -> Mapping[str, Any]:
    return {
        "iteration10_closure_head": ITERATION10_CLOSURE_HEAD,
        "iteration10_closure_tree": ITERATION10_CLOSURE_TREE,
        "iteration10_score_storage_root_hash216": ITERATION10_SCORE_STORAGE_ROOT_HASH216,
        "iteration10_exact_score_root_hash216": ITERATION10_EXACT_SCORE_ROOT_HASH216,
        "iteration10_tokenization_root_hash216": ITERATION10_TOKENIZATION_ROOT_HASH216,
        "iteration10_embedding_root_hash216": ITERATION10_EMBEDDING_ROOT_HASH216,
        "iteration10_stage_suite_root_hash216": ITERATION10_STAGE_SUITE_ROOT_HASH216,
        "iteration10_causal_attention_root_hash216": ITERATION10_CAUSAL_ATTENTION_ROOT_HASH216,
        "iteration10_final_output_root_hash216": ITERATION10_FINAL_OUTPUT_ROOT_HASH216,
        "iteration10_symbolic_dag_root_hash216": ITERATION10_SYMBOLIC_DAG_ROOT_HASH216,
        "iteration10_suite_root_hash216": ITERATION10_SUITE_ROOT_HASH216,
        "iteration10_evidence_root_hash216": ITERATION10_EVIDENCE_ROOT_HASH216,
        "iteration10_receipt_hash72": ITERATION10_RECEIPT_HASH72,
        "iteration10_closure_artifact_sha256": ITERATION10_CLOSURE_ARTIFACT_SHA256,
    }


def _validate_frozen_iteration10_evidence(evidence: Mapping[str, Any]) -> None:
    i10.validate_exact_text_token_ingress_evidence(evidence)
    tokenizer = evidence["authenticated_tokenizer"]
    text = evidence["contracted_text_ingress"]
    embedding = evidence["authenticated_embedding_ingress"]
    execution = evidence["text_derived_coordinate_forward"]
    checks = {
        "score_storage": (tokenizer["score_storage_bits_root_hash216"], ITERATION10_SCORE_STORAGE_ROOT_HASH216),
        "exact_score": (tokenizer["exact_score_root_hash216"], ITERATION10_EXACT_SCORE_ROOT_HASH216),
        "tokenization": (text["tokenization_root_hash216"], ITERATION10_TOKENIZATION_ROOT_HASH216),
        "embedding": (embedding["embedding_suite_root_hash216"], ITERATION10_EMBEDDING_ROOT_HASH216),
        "stage": (execution["executed_stage_suite_root_hash216"], ITERATION10_STAGE_SUITE_ROOT_HASH216),
        "causal": (execution["causal_attention_root_hash216"], ITERATION10_CAUSAL_ATTENTION_ROOT_HASH216),
        "output": (execution["final_output_root_hash216"], ITERATION10_FINAL_OUTPUT_ROOT_HASH216),
        "dag": (execution["symbolic_dag"]["ordered_node_root_hash216"], ITERATION10_SYMBOLIC_DAG_ROOT_HASH216),
        "suite": (evidence["exact_text_token_ingress_suite_root_hash216"], ITERATION10_SUITE_ROOT_HASH216),
        "evidence": (evidence["evidence_root_hash216"], ITERATION10_EVIDENCE_ROOT_HASH216),
        "receipt": (evidence["receipt_hash72"], ITERATION10_RECEIPT_HASH72),
    }
    for name, (actual, expected) in checks.items():
        if actual != expected:
            raise Pass215Iteration11ValidationError(f"PASS215_I11_ITERATION10_ROOT_MISMATCH:{name}")


def _is_integer_metadata_type(value_type: int) -> bool:
    return value_type in {
        i2._GGUF_UINT8, i2._GGUF_INT8, i2._GGUF_UINT16, i2._GGUF_INT16,
        i2._GGUF_UINT32, i2._GGUF_INT32, i2._GGUF_UINT64, i2._GGUF_INT64,
    }


def _read_architecture_metadata(raw: bytes) -> Mapping[str, Any]:
    parsed = i4base.parse_gguf(raw)
    reader = i2._Reader(raw)
    if reader.read(4) != b"GGUF":
        raise Pass215Iteration11ValidationError("PASS215_I11_GGUF_MAGIC_INVALID")
    version = reader.u32()
    if version not in (2, 3):
        raise Pass215Iteration11ValidationError("PASS215_I11_GGUF_VERSION_UNSUPPORTED")
    tensor_count = reader.u64()
    metadata_count = reader.u64()
    if tensor_count <= 0 or metadata_count > 1_000_000:
        raise Pass215Iteration11ValidationError("PASS215_I11_GGUF_HEADER_INVALID")
    wanted = {value: key for key, value in ARCHITECTURE_KEYS.items()}
    values: dict[str, int] = {}
    selected_types: dict[str, int] = {}
    for _ in range(metadata_count):
        key = reader.string()
        value_type = reader.u32()
        if key in wanted:
            if not _is_integer_metadata_type(value_type):
                raise Pass215Iteration11ValidationError(f"PASS215_I11_ARCH_METADATA_TYPE_INVALID:{key}")
            values[wanted[key]] = int(i2._read_gguf_value(reader, value_type, summarize_arrays=False))
            selected_types[key] = int(value_type)
            continue
        i2._read_gguf_value(reader, value_type, summarize_arrays=True)
    missing = [name for name in ARCHITECTURE_KEYS if name not in values]
    if missing:
        raise Pass215Iteration11ValidationError("PASS215_I11_ARCH_METADATA_MISSING:" + ",".join(missing))
    record = {
        "architecture": parsed.architecture,
        "block_count": values["block_count"],
        "embedding_length": values["embedding_length"],
        "feed_forward_length": values["feed_forward_length"],
        "head_count": values["head_count"],
        "head_dimension": values["embedding_length"] // values["head_count"] if values["head_count"] else 0,
        "selected_metadata_types": selected_types,
        "integer_metadata_only": True,
    }
    _require_architecture_geometry(record)
    record["architecture_root_hash216"] = i4base.hash216(
        "pass215-i11-authenticated-architecture-geometry", i4base.canonical_bytes(record)
    )
    return record


def _require_architecture_geometry(record: Mapping[str, Any]) -> None:
    if record.get("architecture") != "llama":
        raise Pass215Iteration11ValidationError(f"PASS215_I11_ARCHITECTURE_UNSUPPORTED:{record.get('architecture')}")
    if int(record.get("block_count", 0)) < 2:
        raise Pass215Iteration11ValidationError("PASS215_I11_BLOCK_COUNT_TOO_SMALL")
    expected = {
        "embedding_length": EMBEDDING_WIDTH,
        "feed_forward_length": FFN_WIDTH,
        "head_count": HEAD_COUNT,
        "head_dimension": HEAD_DIMENSION,
    }
    for key, value in expected.items():
        if int(record.get(key, -1)) != value:
            raise Pass215Iteration11ValidationError(f"PASS215_I11_ARCHITECTURE_GEOMETRY_MISMATCH:{key}")


def _block_tensor_names(block_index: int) -> Mapping[str, Any]:
    if block_index < 0:
        raise Pass215Iteration11ValidationError("PASS215_I11_BLOCK_INDEX_INVALID")
    prefix = f"blk.{block_index}."
    return {
        "norms": tuple(prefix + suffix for suffix in NORM_SUFFIXES),
        "linears": {prefix + suffix: shape for suffix, shape in LINEAR_SUFFIX_SHAPES.items()},
    }


def _bind_block_tensors(raw: bytes, block_index: int) -> Mapping[str, Any]:
    parsed = i4base.parse_gguf(raw)
    by_name = {tensor.name: tensor for tensor in parsed.tensors}
    names = _block_tensor_names(block_index)
    norm_bindings: dict[str, Mapping[str, Any]] = {}
    for name in names["norms"]:
        tensor = by_name.get(name)
        if tensor is None:
            raise Pass215Iteration11ValidationError(f"PASS215_I11_NORM_TENSOR_MISSING:{name}")
        payload = raw[tensor.data_offset:tensor.data_offset + tensor.data_size]
        norm_bindings[name] = i6._bind_norm_tensor(tensor, payload, EMBEDDING_WIDTH)
    linears: dict[str, Any] = {}
    linear_records: dict[str, Mapping[str, Any]] = {}
    for name, shape in names["linears"].items():
        tensor = by_name.get(name)
        if tensor is None:
            raise Pass215Iteration11ValidationError(f"PASS215_I11_LINEAR_TENSOR_MISSING:{name}")
        payload = raw[tensor.data_offset:tensor.data_offset + tensor.data_size]
        compiled, descriptor = i4base.compile_q4_tensor(tensor, payload, shape)
        linears[name] = compiled
        linear_records[name] = {
            "name": name,
            "shape": list(shape),
            "storage_type": tensor.storage_type,
            "source_sha256": tensor.source_sha256,
            "source_bytes": tensor.data_size,
            "block_count": compiled.block_count,
            "descriptor_root_hash216": compiled.descriptor_root_hash216,
            "descriptor": descriptor,
        }
    roots = {
        "norm_roots": {name: record["canonical_value_root_hash216"] for name, record in norm_bindings.items()},
        "linear_descriptor_roots": {name: record["descriptor_root_hash216"] for name, record in linear_records.items()},
    }
    binding_root = i4base.hash216(
        "pass215-i11-authenticated-block-tensor-bindings",
        i4base.canonical_bytes({"block_index": block_index, **roots}),
    )
    return {
        "block_index": block_index,
        "norm_tensors": norm_bindings,
        "linear_tensors": linear_records,
        "compiled_linears": linears,
        "required_tensor_count": len(norm_bindings) + len(linears),
        "block_tensor_binding_root_hash216": binding_root,
    }


def _stage_name(block_index: int, stage: str) -> str:
    return stage if block_index == 0 else f"blk.{block_index}/{stage}"


def _expected_linear_work_per_block() -> Mapping[str, int]:
    return {
        "row_transitions": 2976 * SEQUENCE_LENGTH,
        "logical_weight_products": 995328 * SEQUENCE_LENGTH,
        "logical_accumulation_additions": 992352 * SEQUENCE_LENGTH,
    }


def _execute_block(
    dag: i8.MultiTokenSymbolicDAG,
    hidden_inputs: Sequence[Sequence[str]],
    block_binding: Mapping[str, Any],
    *,
    block_index: int,
) -> Mapping[str, Any]:
    if block_index not in BLOCK_INDEXES:
        raise Pass215Iteration11ValidationError("PASS215_I11_BLOCK_OUTSIDE_CONTRACT")
    if len(hidden_inputs) != SEQUENCE_LENGTH or any(len(row) != EMBEDDING_WIDTH for row in hidden_inputs):
        raise Pass215Iteration11ValidationError("PASS215_I11_BLOCK_INPUT_GEOMETRY_INVALID")
    stages: dict[str, Mapping[str, Any]] = {}
    linear_work = {"row_transitions": 0, "logical_weight_products": 0, "logical_accumulation_additions": 0}

    def record(base_stage: str, tokens: Sequence[Sequence[str]]) -> tuple[tuple[str, ...], ...]:
        normalized = tuple(tuple(values) for values in tokens)
        stage = _stage_name(block_index, base_stage)
        stages[stage] = i8._stage_manifest(dag, stage, normalized)
        return normalized

    hidden = record("hidden_state_input", hidden_inputs)
    names = _block_tensor_names(block_index)
    norms = block_binding["norm_tensors"]
    attn_weights = i7._norm_values(norms[names["norms"][0]])
    ffn_weights = i7._norm_values(norms[names["norms"][1]])
    linears = block_binding["compiled_linears"]
    attn_norm = record("rmsnorm_attn", tuple(i7._exact_rmsnorm_dag(dag, values, attn_weights) for values in hidden))

    def linear(base_stage: str, suffix: str, tokens: Sequence[Sequence[str]]) -> tuple[tuple[str, ...], ...]:
        tensor_name = f"blk.{block_index}.{suffix}"
        stage_for_row = _stage_name(block_index, base_stage)
        outputs = []
        for position, inputs in enumerate(tokens):
            values, work = i7._linear_symbolic(
                dag, linears[tensor_name], inputs, stage=f"{stage_for_row}:token:{position}"
            )
            for key in linear_work:
                linear_work[key] += int(work[key])
            outputs.append(tuple(values))
        return record(base_stage, outputs)

    q_values = linear("linear_attn_q", "attn_q.weight", attn_norm)
    k_values = linear("linear_attn_k", "attn_k.weight", attn_norm)
    v_values = linear("linear_attn_v", "attn_v.weight", attn_norm)
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
            for key_position in range(query + 1):
                score = i7._dot(dag, q_rope[query][start:end], k_rope[key_position][start:end])
                head_scores.append(score)
                query_scores.append(score)
                causal_edges.append({"head": head, "query_position": query, "key_position": key_position})
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
                    dag.mul(probabilities[k], v_values[k][start + dimension])
                    for k in range(query + 1)
                )
                weighted.append(dag.add(*terms))
        weighted_tokens.append(tuple(weighted))
    weighted_values = record("attention_weighted_value", weighted_tokens)
    concatenated = record("attention_concat", weighted_values)
    attn_output = linear("linear_attn_output", "attn_output.weight", concatenated)
    post_attn = record("residual_attention", tuple(
        tuple(dag.add(left, right) for left, right in zip(hidden[position], attn_output[position]))
        for position in range(SEQUENCE_LENGTH)
    ))
    ffn_norm = record("rmsnorm_ffn", tuple(i7._exact_rmsnorm_dag(dag, values, ffn_weights) for values in post_attn))
    gate = linear("linear_ffn_gate", "ffn_gate.weight", ffn_norm)
    activated = record("silu", tuple(tuple(i7._silu(dag, value) for value in values) for values in gate))
    up = linear("linear_ffn_up", "ffn_up.weight", ffn_norm)
    gated = record("ffn_gate_product", tuple(
        tuple(dag.mul(left, right) for left, right in zip(activated[position], up[position]))
        for position in range(SEQUENCE_LENGTH)
    ))
    down = linear("linear_ffn_down", "ffn_down.weight", gated)
    output = record("residual_ffn", tuple(
        tuple(dag.add(left, right) for left, right in zip(post_attn[position], down[position]))
        for position in range(SEQUENCE_LENGTH)
    ))

    expected_stages = tuple(_stage_name(block_index, value) for value in GRAPH_OPS)
    if tuple(stages) != expected_stages:
        raise Pass215Iteration11ValidationError(f"PASS215_I11_BLOCK_STAGE_TOPOLOGY_INVALID:{block_index}")
    observed_edges = tuple((x["head"], x["query_position"], x["key_position"]) for x in causal_edges)
    if observed_edges != i8._expected_causal_edges():
        raise Pass215Iteration11ValidationError(f"PASS215_I11_CAUSAL_EDGE_SET_INVALID:{block_index}")
    zero_identity = q_rope[0] == q_values[0] and k_rope[0] == k_values[0]
    nonzero_changes = all(q_rope[p] != q_values[p] and k_rope[p] != k_values[p] for p in range(1, SEQUENCE_LENGTH))
    singleton_identity = all(by_query_head[(0, head)] == (dag.q(1),) for head in range(HEAD_COUNT))
    if not zero_identity or not nonzero_changes or not singleton_identity:
        raise Pass215Iteration11ValidationError(f"PASS215_I11_ATTENTION_CONTROL_FAILED:{block_index}")
    if linear_work != _expected_linear_work_per_block():
        raise Pass215Iteration11ValidationError(f"PASS215_I11_LINEAR_WORK_INVALID:{block_index}")

    if block_index == 0:
        final_token_label = "pass215-i9-final-token-coordinate-roots"
        stage_label = "pass215-i9-executed-stage-suite"
        attention_label = "pass215-i9-causal-attention-suite"
        output_label = "pass215-i9-final-output-token-suite"
    else:
        final_token_label = "pass215-i11-final-token-coordinate-roots"
        stage_label = "pass215-i11-block-stage-suite"
        attention_label = "pass215-i11-block-causal-attention-suite"
        output_label = "pass215-i11-block-final-output-token-suite"
    token_output_roots = [
        i4base.hash216(final_token_label, i4base.canonical_bytes({"position": p, "roots": list(values)}))
        for p, values in enumerate(output)
    ]
    attention_payload = {
        "causal_edges": causal_edges,
        "softmax_records": softmax_records,
        "qk_stage_root": stages[_stage_name(block_index, "attention_qk_dot")]["stage_root_hash216"],
        "scale_stage_root": stages[_stage_name(block_index, "attention_scale")]["stage_root_hash216"],
        "softmax_stage_root": stages[_stage_name(block_index, "attention_softmax")]["stage_root_hash216"],
        "weighted_stage_root": stages[_stage_name(block_index, "attention_weighted_value")]["stage_root_hash216"],
    }
    return {
        "block_index": block_index,
        "stage_records": stages,
        "executed_stage_suite_root_hash216": i4base.hash216(stage_label, i4base.canonical_bytes(stages)),
        "causal_attention_root_hash216": i4base.hash216(attention_label, i4base.canonical_bytes(attention_payload)),
        "final_output_token_roots": token_output_roots,
        "final_output_root_hash216": i4base.hash216(output_label, i4base.canonical_bytes(token_output_roots)),
        "final_output_token_count": len(output),
        "final_output_coordinate_count": sum(len(values) for values in output),
        "output_coordinate_roots": output,
        "input_coordinate_roots": tuple(tuple(values) for values in hidden),
        "causal_edges": causal_edges,
        "softmax_records": softmax_records,
        "linear_transition_work": linear_work,
        "attention_transition_work": i8._attention_work_geometry(),
        "rope_controls": {
            "position_zero_exact_identity": zero_identity,
            "all_nonzero_positions_change_q_and_k_roots": nonzero_changes,
        },
        "causal_controls": {
            "future_edges_materialized": False,
            "edge_set_exact": True,
            "singleton_softmax_exact_identity": singleton_identity,
            "softmax_denominators_use_causal_terms_only": all(
                item["context_length"] == item["query_position"] + 1
                and item["causal_key_positions"] == list(range(item["query_position"] + 1))
                for item in softmax_records
            ),
        },
    }


def _sum_work(left: Mapping[str, int], right: Mapping[str, int]) -> Mapping[str, int]:
    return {key: int(left[key]) + int(right[key]) for key in left}


def _sequential_link_root(block0_output: Sequence[Sequence[str]], block1_input: Sequence[Sequence[str]]) -> str:
    left = tuple(tuple(row) for row in block0_output)
    right = tuple(tuple(row) for row in block1_input)
    if left != right:
        raise Pass215Iteration11ValidationError("PASS215_I11_BLOCK_SEQUENTIAL_LINK_INVALID")
    return i4base.hash216(
        "pass215-i11-blk0-to-blk1-coordinate-link",
        i4base.canonical_bytes({"blk0_output": [list(row) for row in left], "blk1_input": [list(row) for row in right]}),
    )


def build_sequential_two_block_evidence(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    _reject_floats(source)
    actual_sha = sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration11ValidationError("PASS215_I11_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration11ValidationError("PASS215_I11_AUTHENTICATED_MODEL_IDENTITY_MISMATCH")
    if prompt != CONTRACTED_PROMPT:
        raise Pass215Iteration11ValidationError("PASS215_I11_PROMPT_OUTSIDE_CONTRACT")

    i10_evidence = i10.build_exact_text_token_ingress_evidence(
        raw, filename=filename, source=source, prompt=prompt, expected_sha256=expected_sha256
    )
    _validate_frozen_iteration10_evidence(i10_evidence)
    architecture = _read_architecture_metadata(raw)
    tokenizer = i10._read_exact_tokenizer_metadata(raw)
    tokenization = i10._tokenize_sentencepiece_bpe(prompt, tokenizer)
    token_ids = tuple(int(value) for value in tokenization["token_ids"])
    if token_ids != (1, 15043, 3186, 29991):
        raise Pass215Iteration11ValidationError("PASS215_I11_FROZEN_TEXT_TOKEN_IDS_CHANGED")
    embeddings = i9._extract_authenticated_embeddings(raw, tokenizer, token_ids)
    if embeddings["embedding_suite_root_hash216"] != ITERATION10_EMBEDDING_ROOT_HASH216:
        raise Pass215Iteration11ValidationError("PASS215_I11_FROZEN_EMBEDDING_ROOT_CHANGED")

    block0_binding = _bind_block_tensors(raw, 0)
    block1_binding = _bind_block_tensors(raw, 1)
    if block0_binding["required_tensor_count"] != 9 or block1_binding["required_tensor_count"] != 9:
        raise Pass215Iteration11ValidationError("PASS215_I11_BLOCK_TENSOR_COUNT_INVALID")
    dag = i8.MultiTokenSymbolicDAG()
    hidden = tuple(tuple(dag.q(n, d) for n, d in row) for row in embeddings["rows"])
    block0 = _execute_block(dag, hidden, block0_binding, block_index=0)
    block0_manifest = dag.manifest()
    frozen_blk0 = {
        "stage": (block0["executed_stage_suite_root_hash216"], ITERATION10_STAGE_SUITE_ROOT_HASH216),
        "causal": (block0["causal_attention_root_hash216"], ITERATION10_CAUSAL_ATTENTION_ROOT_HASH216),
        "output": (block0["final_output_root_hash216"], ITERATION10_FINAL_OUTPUT_ROOT_HASH216),
        "dag": (block0_manifest["ordered_node_root_hash216"], ITERATION10_SYMBOLIC_DAG_ROOT_HASH216),
    }
    for name, (actual, expected) in frozen_blk0.items():
        if actual != expected:
            raise Pass215Iteration11ValidationError(f"PASS215_I11_REEXECUTED_BLK0_ROOT_MISMATCH:{name}")

    block1 = _execute_block(dag, block0["output_coordinate_roots"], block1_binding, block_index=1)
    link_root = _sequential_link_root(block0["output_coordinate_roots"], block1["input_coordinate_roots"])
    full_manifest = dag.manifest()
    total_linear = _sum_work(block0["linear_transition_work"], block1["linear_transition_work"])
    expected_total_linear = {key: 2 * int(value) for key, value in _expected_linear_work_per_block().items()}
    if total_linear != expected_total_linear:
        raise Pass215Iteration11ValidationError("PASS215_I11_TOTAL_LINEAR_WORK_INVALID")
    total_attention = {key: 2 * int(value) for key, value in i8._attention_work_geometry().items()}
    block_binding_roots = {
        "blk.0": block0_binding["block_tensor_binding_root_hash216"],
        "blk.1": block1_binding["block_tensor_binding_root_hash216"],
    }
    two_block_payload = {
        "architecture_root_hash216": architecture["architecture_root_hash216"],
        "block_binding_roots": block_binding_roots,
        "blk0_frozen_final_output_root_hash216": block0["final_output_root_hash216"],
        "sequential_link_root_hash216": link_root,
        "blk1_final_output_root_hash216": block1["final_output_root_hash216"],
        "full_symbolic_dag_root_hash216": full_manifest["ordered_node_root_hash216"],
        "total_linear_transition_work": total_linear,
        "total_attention_transition_work": total_attention,
    }
    two_block_root = i4base.hash216(
        "pass215-i11-authenticated-sequential-two-block-forward", i4base.canonical_bytes(two_block_payload)
    )
    source_record = {
        **dict(source), "filename": filename, "file_size_bytes": len(raw), "file_sha256": actual_sha,
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
            "no_float_canonical_authority": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
        "inherits": {
            **_iteration10_bindings(),
            "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "source": source_record,
        "authenticated_architecture": architecture,
        "contracted_text_ingress": {
            "input_text": tokenization["input_text"],
            "normalized_text": tokenization["normalized_text"],
            "token_ids": list(token_ids),
            "tokens": list(tokenization["tokens"]),
            "tokenization_root_hash216": ITERATION10_TOKENIZATION_ROOT_HASH216,
        },
        "authenticated_embedding_ingress": {
            "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"],
            "selected_token_ids": list(token_ids),
            "embedding_lookup_work": embeddings["embedding_lookup_work"],
        },
        "authenticated_block_tensor_bindings": {
            "block_count_bound": 2,
            "required_tensor_count": 18,
            "block_binding_roots": block_binding_roots,
            "blk.0": {"norm_tensors": block0_binding["norm_tensors"], "linear_tensors": block0_binding["linear_tensors"]},
            "blk.1": {"norm_tensors": block1_binding["norm_tensors"], "linear_tensors": block1_binding["linear_tensors"]},
        },
        "sequential_two_block_forward": {
            "block_order": [0, 1],
            "stage_count": len(block0["stage_records"]) + len(block1["stage_records"]),
            "block0": {key: value for key, value in block0.items() if key not in ("output_coordinate_roots", "input_coordinate_roots")},
            "block1": {key: value for key, value in block1.items() if key not in ("output_coordinate_roots", "input_coordinate_roots")},
            "blk0_to_blk1_sequential_link_root_hash216": link_root,
            "blk1_input_equals_blk0_output": True,
            "total_linear_transition_work": total_linear,
            "total_attention_transition_work": total_attention,
            "symbolic_dag": full_manifest,
            "two_block_forward_root_hash216": two_block_root,
        },
        "exact_controls": {
            "iteration10_frozen_roots_reexecuted_and_bound": {"exact": True, **_iteration10_bindings()},
            "authenticated_block_count_at_least_two": {"exact": int(architecture["block_count"]) >= 2, "block_count": architecture["block_count"]},
            "authenticated_geometry_matches_frozen_execution": {
                "exact": True,
                "embedding_length": architecture["embedding_length"],
                "feed_forward_length": architecture["feed_forward_length"],
                "head_count": architecture["head_count"],
                "head_dimension": architecture["head_dimension"],
            },
            "blk0_reexecution_matches_iteration10": {
                "exact": True,
                "stage_suite_root_hash216": block0["executed_stage_suite_root_hash216"],
                "causal_attention_root_hash216": block0["causal_attention_root_hash216"],
                "final_output_root_hash216": block0["final_output_root_hash216"],
                "symbolic_dag_root_hash216": block0_manifest["ordered_node_root_hash216"],
            },
            "blk1_input_is_exact_blk0_output": {"exact": True, "sequential_link_root_hash216": link_root},
            "both_blocks_causal_edge_sets_exact": {"exact": True, "future_edges_materialized": False},
        },
        "claims": {
            "authenticated_iteration10_roots_inherited_unchanged": True,
            "authenticated_model_block_geometry_bound": True,
            "authenticated_blk1_tensor_set_bound": True,
            "contracted_four_token_blk0_reexecuted_exactly": True,
            "contracted_four_token_blk1_forward_executed": True,
            "contracted_four_token_two_block_sequential_forward_executed": True,
            "multi_block_transformer_forward_executed": True,
            "general_arbitrary_text_tokenizer_conformance_claimed": False,
            "general_arbitrary_sequence_length_transformer_forward_executed": False,
            "all_model_blocks_executed": False,
            "full_model_forward_executed": False,
            "final_output_norm_executed": False,
            "output_logits_executed": False,
            "generation_or_sampling_executed": False,
            "numeric_transcendental_evaluation_performed": False,
            "approximate_transcendental_evaluation_performed": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "runtime_mutation_performed": False,
            "canonical_mutation_performed": False,
        },
    }
    roots = {
        "iteration10_suite_root_hash216": ITERATION10_SUITE_ROOT_HASH216,
        "architecture_root_hash216": architecture["architecture_root_hash216"],
        "blk0_binding_root_hash216": block_binding_roots["blk.0"],
        "blk1_binding_root_hash216": block_binding_roots["blk.1"],
        "sequential_link_root_hash216": link_root,
        "blk1_final_output_root_hash216": block1["final_output_root_hash216"],
        "two_block_forward_root_hash216": two_block_root,
        "full_symbolic_dag_root_hash216": full_manifest["ordered_node_root_hash216"],
    }
    suite_root = i4base.hash216(
        "pass215-i11-authenticated-sequential-two-block-suite", i4base.canonical_bytes(roots)
    )
    evidence["sequential_two_block_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216(
        "pass215-i11-authenticated-sequential-two-block-evidence", i4base.canonical_bytes(evidence)
    )
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION11_SEQUENTIAL_TWO_BLOCK_FORWARD"},
        {"sequence": 11, "parent_hash72": ITERATION10_RECEIPT_HASH72, "evidence_root_hash216": evidence_root,
         "sequential_two_block_suite_root_hash216": suite_root},
    )
    _reject_floats(evidence)
    return evidence


def build_sequential_two_block_evidence_from_path(
    path: str | Path,
    *,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    target = Path(path)
    return build_sequential_two_block_evidence(
        target.read_bytes(), filename=target.name, source=source, prompt=prompt, expected_sha256=expected_sha256
    )


def validate_sequential_two_block_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration11ValidationError("PASS215_I11_SCHEMA_OR_CONTRACT_INVALID")
    inherits = evidence.get("inherits")
    if not isinstance(inherits, Mapping):
        raise Pass215Iteration11ValidationError("PASS215_I11_INHERITANCE_MISSING")
    for key, expected in _iteration10_bindings().items():
        if inherits.get(key) != expected:
            raise Pass215Iteration11ValidationError(f"PASS215_I11_FROZEN_BINDING_INVALID:{key}")
    architecture = evidence.get("authenticated_architecture")
    text = evidence.get("contracted_text_ingress")
    embeddings = evidence.get("authenticated_embedding_ingress")
    bindings = evidence.get("authenticated_block_tensor_bindings")
    forward = evidence.get("sequential_two_block_forward")
    claims = evidence.get("claims")
    if not all(isinstance(value, Mapping) for value in (architecture, text, embeddings, bindings, forward, claims)):
        raise Pass215Iteration11ValidationError("PASS215_I11_REQUIRED_SECTION_MISSING")
    _require_architecture_geometry(architecture)
    if text.get("input_text") != CONTRACTED_PROMPT or text.get("token_ids") != [1, 15043, 3186, 29991]:
        raise Pass215Iteration11ValidationError("PASS215_I11_TEXT_INGRESS_INVALID")
    if text.get("tokenization_root_hash216") != ITERATION10_TOKENIZATION_ROOT_HASH216:
        raise Pass215Iteration11ValidationError("PASS215_I11_TOKENIZATION_ROOT_INVALID")
    if embeddings.get("embedding_suite_root_hash216") != ITERATION10_EMBEDDING_ROOT_HASH216:
        raise Pass215Iteration11ValidationError("PASS215_I11_EMBEDDING_ROOT_INVALID")
    if int(bindings.get("block_count_bound", 0)) != 2 or int(bindings.get("required_tensor_count", 0)) != 18:
        raise Pass215Iteration11ValidationError("PASS215_I11_BLOCK_BINDING_COUNT_INVALID")
    if forward.get("block_order") != [0, 1] or int(forward.get("stage_count", 0)) != 42:
        raise Pass215Iteration11ValidationError("PASS215_I11_BLOCK_ORDER_OR_STAGE_COUNT_INVALID")
    if forward.get("blk1_input_equals_blk0_output") is not True:
        raise Pass215Iteration11ValidationError("PASS215_I11_SEQUENTIALITY_CLAIM_INVALID")
    block0, block1 = forward["block0"], forward["block1"]
    if block0["executed_stage_suite_root_hash216"] != ITERATION10_STAGE_SUITE_ROOT_HASH216:
        raise Pass215Iteration11ValidationError("PASS215_I11_BLK0_STAGE_ROOT_INVALID")
    if block0["causal_attention_root_hash216"] != ITERATION10_CAUSAL_ATTENTION_ROOT_HASH216:
        raise Pass215Iteration11ValidationError("PASS215_I11_BLK0_CAUSAL_ROOT_INVALID")
    if block0["final_output_root_hash216"] != ITERATION10_FINAL_OUTPUT_ROOT_HASH216:
        raise Pass215Iteration11ValidationError("PASS215_I11_BLK0_OUTPUT_ROOT_INVALID")
    if block1["final_output_token_count"] != SEQUENCE_LENGTH or block1["final_output_coordinate_count"] != SEQUENCE_LENGTH * EMBEDDING_WIDTH:
        raise Pass215Iteration11ValidationError("PASS215_I11_BLK1_OUTPUT_GEOMETRY_INVALID")
    if any(block["causal_controls"]["edge_set_exact"] is not True or block["causal_controls"]["future_edges_materialized"] is not False for block in (block0, block1)):
        raise Pass215Iteration11ValidationError("PASS215_I11_CAUSAL_CONTROL_INVALID")
    expected_total_linear = {key: 2 * int(value) for key, value in _expected_linear_work_per_block().items()}
    if forward.get("total_linear_transition_work") != expected_total_linear:
        raise Pass215Iteration11ValidationError("PASS215_I11_TOTAL_LINEAR_WORK_VALIDATION_INVALID")
    expected_total_attention = {key: 2 * int(value) for key, value in i8._attention_work_geometry().items()}
    if forward.get("total_attention_transition_work") != expected_total_attention:
        raise Pass215Iteration11ValidationError("PASS215_I11_TOTAL_ATTENTION_WORK_VALIDATION_INVALID")
    required_true = (
        "authenticated_iteration10_roots_inherited_unchanged", "authenticated_model_block_geometry_bound",
        "authenticated_blk1_tensor_set_bound", "contracted_four_token_blk0_reexecuted_exactly",
        "contracted_four_token_blk1_forward_executed", "contracted_four_token_two_block_sequential_forward_executed",
        "multi_block_transformer_forward_executed",
    )
    required_false = (
        "general_arbitrary_text_tokenizer_conformance_claimed", "general_arbitrary_sequence_length_transformer_forward_executed",
        "all_model_blocks_executed", "full_model_forward_executed", "final_output_norm_executed",
        "output_logits_executed", "generation_or_sampling_executed", "numeric_transcendental_evaluation_performed",
        "approximate_transcendental_evaluation_performed", "canonical_float_interpretation_performed",
        "dense_forward_replaced", "runtime_mutation_performed", "canonical_mutation_performed",
    )
    if any(claims.get(key) is not True for key in required_true):
        raise Pass215Iteration11ValidationError("PASS215_I11_REQUIRED_TRUE_CLAIM_INVALID")
    if any(claims.get(key) is not False for key in required_false):
        raise Pass215Iteration11ValidationError("PASS215_I11_REQUIRED_FALSE_CLAIM_INVALID")
    roots = {
        "iteration10_suite_root_hash216": ITERATION10_SUITE_ROOT_HASH216,
        "architecture_root_hash216": architecture["architecture_root_hash216"],
        "blk0_binding_root_hash216": bindings["block_binding_roots"]["blk.0"],
        "blk1_binding_root_hash216": bindings["block_binding_roots"]["blk.1"],
        "sequential_link_root_hash216": forward["blk0_to_blk1_sequential_link_root_hash216"],
        "blk1_final_output_root_hash216": block1["final_output_root_hash216"],
        "two_block_forward_root_hash216": forward["two_block_forward_root_hash216"],
        "full_symbolic_dag_root_hash216": forward["symbolic_dag"]["ordered_node_root_hash216"],
    }
    expected_suite = i4base.hash216(
        "pass215-i11-authenticated-sequential-two-block-suite", i4base.canonical_bytes(roots)
    )
    if evidence.get("sequential_two_block_suite_root_hash216") != expected_suite:
        raise Pass215Iteration11ValidationError("PASS215_I11_SUITE_ROOT_INVALID")
    body = dict(evidence)
    evidence_root = body.pop("evidence_root_hash216", None)
    receipt = body.pop("receipt_hash72", None)
    expected_evidence = i4base.hash216(
        "pass215-i11-authenticated-sequential-two-block-evidence", i4base.canonical_bytes(body)
    )
    if evidence_root != expected_evidence:
        raise Pass215Iteration11ValidationError("PASS215_I11_EVIDENCE_ROOT_INVALID")
    expected_receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION11_SEQUENTIAL_TWO_BLOCK_FORWARD"},
        {"sequence": 11, "parent_hash72": ITERATION10_RECEIPT_HASH72, "evidence_root_hash216": evidence_root,
         "sequential_two_block_suite_root_hash216": expected_suite},
    )
    if receipt != expected_receipt:
        raise Pass215Iteration11ValidationError("PASS215_I11_RECEIPT_INVALID")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_sequential_two_block_evidence(left)
    validate_sequential_two_block_evidence(right)
    lf, rf = left["sequential_two_block_forward"], right["sequential_two_block_forward"]
    identities = {
        "architecture_root_hash216": left["authenticated_architecture"]["architecture_root_hash216"] == right["authenticated_architecture"]["architecture_root_hash216"],
        "blk0_binding_root_hash216": left["authenticated_block_tensor_bindings"]["block_binding_roots"]["blk.0"] == right["authenticated_block_tensor_bindings"]["block_binding_roots"]["blk.0"],
        "blk1_binding_root_hash216": left["authenticated_block_tensor_bindings"]["block_binding_roots"]["blk.1"] == right["authenticated_block_tensor_bindings"]["block_binding_roots"]["blk.1"],
        "sequential_link_root_hash216": lf["blk0_to_blk1_sequential_link_root_hash216"] == rf["blk0_to_blk1_sequential_link_root_hash216"],
        "blk1_final_output_root_hash216": lf["block1"]["final_output_root_hash216"] == rf["block1"]["final_output_root_hash216"],
        "full_symbolic_dag_root_hash216": lf["symbolic_dag"]["ordered_node_root_hash216"] == rf["symbolic_dag"]["ordered_node_root_hash216"],
        "two_block_forward_root_hash216": lf["two_block_forward_root_hash216"] == rf["two_block_forward_root_hash216"],
        "suite_root_hash216": left["sequential_two_block_suite_root_hash216"] == right["sequential_two_block_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"] == right["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"] == right["receipt_hash72"],
    }
    return {
        "schema": REPLAY_SCHEMA,
        "cross_process_replay": all(identities.values()),
        "semantic_exactness": all(identities.values()),
        "identities": identities,
        "blk1_final_output_root_hash216": lf["block1"]["final_output_root_hash216"],
        "two_block_forward_root_hash216": lf["two_block_forward_root_hash216"],
        "suite_root_hash216": left["sequential_two_block_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }


__all__ = [
    "CONTRACT", "PASS_NUMBER", "ITERATION", "EVIDENCE_SCHEMA", "VALIDATION_SCHEMA", "REPLAY_SCHEMA",
    "REAL_MODEL_SHA256", "CONTRACTED_PROMPT", "SEQUENCE_LENGTH", "EMBEDDING_WIDTH", "FFN_WIDTH",
    "HEAD_COUNT", "HEAD_DIMENSION", "BLOCK_INDEXES", "ARCHITECTURE_KEYS", "LINEAR_SUFFIX_SHAPES",
    "Pass215Iteration11Error", "Pass215Iteration11ValidationError", "_iteration10_bindings",
    "_read_architecture_metadata", "_require_architecture_geometry", "_block_tensor_names", "_bind_block_tensors",
    "_execute_block", "_expected_linear_work_per_block", "_sequential_link_root",
    "build_sequential_two_block_evidence", "build_sequential_two_block_evidence_from_path",
    "validate_sequential_two_block_evidence", "compare_replay",
]
