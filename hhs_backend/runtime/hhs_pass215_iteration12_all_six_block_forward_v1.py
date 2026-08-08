"""Pass 215 Iteration 12 authenticated all-six-block exact symbolic forward.

Iteration 12 preserves the frozen Iteration 11 two-block closure and extends the
same four-token text-derived hidden state through every transformer block declared
by the authenticated GGUF.  The model declares exactly six blocks.  Blocks 0 and
1 are replayed with the frozen Iteration 11 namespaces and must reproduce every
frozen prefix identity before blocks 2-5 are admitted.  All six blocks execute in
one shared hash-consed symbolic DAG with exact adjacent coordinate-root links.

Benchmark authority only: final output normalization, output projection/logits,
generation/sampling, arbitrary sequence length, numeric transcendental
approximation, Python-float canonical authority, dense-forward replacement,
runtime mutation, canonical mutation, and migration remain outside authority.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7
from hhs_backend.runtime import hhs_pass215_iteration8_multi_token_causal_attention_v1 as i8
from hhs_backend.runtime import hhs_pass215_iteration9_authenticated_token_ingress_v2 as i9
from hhs_backend.runtime import hhs_pass215_iteration10_exact_text_token_ingress_v1 as i10
from hhs_backend.runtime import hhs_pass215_iteration11_sequential_two_block_v1 as i11

CONTRACT = "HHS-P215-I12-AUTHENTICATED-ALL-SIX-BLOCK-SYMBOLIC-FORWARD"
PASS_NUMBER = 215
ITERATION = 12
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_12_ALL_SIX_BLOCK_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_12_ALL_SIX_BLOCK_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_12_ALL_SIX_BLOCK_REPLAY_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_12_AUTHENTICATED_ALL_SIX_BLOCK_BENCHMARK"

ITERATION11_CLOSURE_HEAD = "0c01c900b4d9afa6f741c86a5bcb61d5ddf613e7"
ITERATION11_CLOSURE_TREE = "bb301228b067a2eab031ad974bc5605c9af003a3"
ITERATION11_ARCHITECTURE_ROOT_HASH216 = "6f2837183d79c1fc751822e05eac06b4d4711c12c89c7a955bf77ecea32fcc52"
ITERATION11_BLK0_BINDING_ROOT_HASH216 = "bc225999c88110bd47e1ceceecc96d8ef9e8ec0752ddf659a9a4c35647109bff"
ITERATION11_BLK1_BINDING_ROOT_HASH216 = "3f55a20a7d34b45f6b73ab4e6f0ff138a8fd1e5de74fe259ae5a3a7ed8ba1087"
ITERATION11_SEQUENTIAL_LINK_ROOT_HASH216 = "ec7a6b35493f55dc5b7df8099f0ff9aa402d51fea15f67c59c8b3a9fc6294074"
ITERATION11_BLK1_STAGE_SUITE_ROOT_HASH216 = "f3b9c1886d9b37c9b4b1de974c57936f79e1aea8520d403e34495688ef9810d0"
ITERATION11_BLK1_CAUSAL_ATTENTION_ROOT_HASH216 = "d780232058b51855ba95a7696b6bee57840602a3f883e2a8a7b3039979aada64"
ITERATION11_BLK1_FINAL_OUTPUT_ROOT_HASH216 = "d88fac2044fbca53f8d4a397a39ae4f6e5de4b82fdad39e3eafbee9fde0025bb"
ITERATION11_FULL_SYMBOLIC_DAG_ROOT_HASH216 = "b8f9fdbe81cc718b3c59fcb43dd8ca590d7aaf17802f0a957640c00cf4837cbd"
ITERATION11_TWO_BLOCK_FORWARD_ROOT_HASH216 = "608e136d9080e8b109b4450b1985f8b456f052a8540ea07461a96b04d010a1ff"
ITERATION11_SUITE_ROOT_HASH216 = "cc62c770950310e1331636dd5fff2b2a0c3ca17e4a3499aae4d6dcd2ae147de8"
ITERATION11_EVIDENCE_ROOT_HASH216 = "610aa83b8b794d7055400df8bcb63be652d90f1d4659c839bc3d58c3a6402942"
ITERATION11_RECEIPT_HASH72 = "<GT6vip06+KOyycGmt1q79Ahi4m1qhtSc*>+auiGN3xNEHyhYEDD5nBB+*dy)0fD+z+HFS!K"
ITERATION11_CLOSURE_ARTIFACT_SHA256 = "16f5898d8df2f707d85f504f47eb83948fcd0f232a48c81a8e07851c7a291255"

REAL_MODEL_SHA256 = i11.REAL_MODEL_SHA256
CONTRACTED_PROMPT = i11.CONTRACTED_PROMPT
SEQUENCE_LENGTH = i11.SEQUENCE_LENGTH
EMBEDDING_WIDTH = i11.EMBEDDING_WIDTH
FFN_WIDTH = i11.FFN_WIDTH
HEAD_COUNT = i11.HEAD_COUNT
HEAD_DIMENSION = i11.HEAD_DIMENSION
AUTHENTICATED_BLOCK_COUNT = 6
BLOCK_INDEXES = tuple(range(AUTHENTICATED_BLOCK_COUNT))
EXTENSION_BLOCK_INDEXES = tuple(range(2, AUTHENTICATED_BLOCK_COUNT))
GRAPH_OPS = i11.GRAPH_OPS
FROZEN_TOKEN_IDS = (1, 15043, 3186, 29991)


class Pass215Iteration12Error(RuntimeError):
    pass


class Pass215Iteration12ValidationError(Pass215Iteration12Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration12ValidationError(f"PASS215_I12_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _iteration11_bindings() -> Mapping[str, Any]:
    return {
        "iteration11_closure_head": ITERATION11_CLOSURE_HEAD,
        "iteration11_closure_tree": ITERATION11_CLOSURE_TREE,
        "iteration11_architecture_root_hash216": ITERATION11_ARCHITECTURE_ROOT_HASH216,
        "iteration11_blk0_binding_root_hash216": ITERATION11_BLK0_BINDING_ROOT_HASH216,
        "iteration11_blk1_binding_root_hash216": ITERATION11_BLK1_BINDING_ROOT_HASH216,
        "iteration11_sequential_link_root_hash216": ITERATION11_SEQUENTIAL_LINK_ROOT_HASH216,
        "iteration11_blk1_stage_suite_root_hash216": ITERATION11_BLK1_STAGE_SUITE_ROOT_HASH216,
        "iteration11_blk1_causal_attention_root_hash216": ITERATION11_BLK1_CAUSAL_ATTENTION_ROOT_HASH216,
        "iteration11_blk1_final_output_root_hash216": ITERATION11_BLK1_FINAL_OUTPUT_ROOT_HASH216,
        "iteration11_full_symbolic_dag_root_hash216": ITERATION11_FULL_SYMBOLIC_DAG_ROOT_HASH216,
        "iteration11_two_block_forward_root_hash216": ITERATION11_TWO_BLOCK_FORWARD_ROOT_HASH216,
        "iteration11_suite_root_hash216": ITERATION11_SUITE_ROOT_HASH216,
        "iteration11_evidence_root_hash216": ITERATION11_EVIDENCE_ROOT_HASH216,
        "iteration11_receipt_hash72": ITERATION11_RECEIPT_HASH72,
        "iteration11_closure_artifact_sha256": ITERATION11_CLOSURE_ARTIFACT_SHA256,
    }


def _validate_frozen_iteration11_evidence(evidence: Mapping[str, Any]) -> None:
    i11.validate_sequential_two_block_evidence(evidence)
    architecture = evidence["authenticated_architecture"]
    bindings = evidence["authenticated_block_tensor_bindings"]
    forward = evidence["sequential_two_block_forward"]
    checks = {
        "architecture": (architecture["architecture_root_hash216"], ITERATION11_ARCHITECTURE_ROOT_HASH216),
        "blk0_binding": (bindings["block_binding_roots"]["blk.0"], ITERATION11_BLK0_BINDING_ROOT_HASH216),
        "blk1_binding": (bindings["block_binding_roots"]["blk.1"], ITERATION11_BLK1_BINDING_ROOT_HASH216),
        "sequential_link": (forward["blk0_to_blk1_sequential_link_root_hash216"], ITERATION11_SEQUENTIAL_LINK_ROOT_HASH216),
        "blk1_stage": (forward["block1"]["executed_stage_suite_root_hash216"], ITERATION11_BLK1_STAGE_SUITE_ROOT_HASH216),
        "blk1_causal": (forward["block1"]["causal_attention_root_hash216"], ITERATION11_BLK1_CAUSAL_ATTENTION_ROOT_HASH216),
        "blk1_output": (forward["block1"]["final_output_root_hash216"], ITERATION11_BLK1_FINAL_OUTPUT_ROOT_HASH216),
        "full_dag": (forward["symbolic_dag"]["ordered_node_root_hash216"], ITERATION11_FULL_SYMBOLIC_DAG_ROOT_HASH216),
        "two_block": (forward["two_block_forward_root_hash216"], ITERATION11_TWO_BLOCK_FORWARD_ROOT_HASH216),
        "suite": (evidence["sequential_two_block_suite_root_hash216"], ITERATION11_SUITE_ROOT_HASH216),
        "evidence": (evidence["evidence_root_hash216"], ITERATION11_EVIDENCE_ROOT_HASH216),
        "receipt": (evidence["receipt_hash72"], ITERATION11_RECEIPT_HASH72),
    }
    if int(architecture["block_count"]) != AUTHENTICATED_BLOCK_COUNT:
        raise Pass215Iteration12ValidationError("PASS215_I12_ITERATION11_BLOCK_COUNT_MISMATCH")
    for name, (actual, expected) in checks.items():
        if actual != expected:
            raise Pass215Iteration12ValidationError(f"PASS215_I12_ITERATION11_ROOT_MISMATCH:{name}")


def _require_all_block_architecture(record: Mapping[str, Any]) -> None:
    try:
        i11._require_architecture_geometry(record)
    except i11.Pass215Iteration11ValidationError as exc:
        raise Pass215Iteration12ValidationError(f"PASS215_I12_ARCHITECTURE_GEOMETRY_INVALID:{exc}") from exc
    if int(record.get("block_count", 0)) != AUTHENTICATED_BLOCK_COUNT:
        raise Pass215Iteration12ValidationError("PASS215_I12_AUTHENTICATED_BLOCK_COUNT_NOT_SIX")


def _expected_linear_work_total(block_count: int = AUTHENTICATED_BLOCK_COUNT) -> Mapping[str, int]:
    if block_count <= 0:
        raise Pass215Iteration12ValidationError("PASS215_I12_BLOCK_COUNT_INVALID")
    one = i11._expected_linear_work_per_block()
    return {key: block_count * int(value) for key, value in one.items()}


def _expected_attention_work_total(block_count: int = AUTHENTICATED_BLOCK_COUNT) -> Mapping[str, int]:
    if block_count <= 0:
        raise Pass215Iteration12ValidationError("PASS215_I12_BLOCK_COUNT_INVALID")
    one = i8._attention_work_geometry()
    return {key: block_count * int(value) for key, value in one.items()}


def _execute_extension_block(
    dag: i8.MultiTokenSymbolicDAG,
    hidden_inputs: Sequence[Sequence[str]],
    block_binding: Mapping[str, Any],
    *,
    block_index: int,
) -> Mapping[str, Any]:
    """Execute one exact block after the frozen Iteration 11 prefix."""
    if block_index not in EXTENSION_BLOCK_INDEXES:
        raise Pass215Iteration12ValidationError("PASS215_I12_EXTENSION_BLOCK_OUTSIDE_CONTRACT")
    if len(hidden_inputs) != SEQUENCE_LENGTH or any(len(row) != EMBEDDING_WIDTH for row in hidden_inputs):
        raise Pass215Iteration12ValidationError("PASS215_I12_BLOCK_INPUT_GEOMETRY_INVALID")
    stages: dict[str, Mapping[str, Any]] = {}
    linear_work = {"row_transitions": 0, "logical_weight_products": 0, "logical_accumulation_additions": 0}

    def record(base_stage: str, tokens: Sequence[Sequence[str]]) -> tuple[tuple[str, ...], ...]:
        normalized = tuple(tuple(values) for values in tokens)
        stage = i11._stage_name(block_index, base_stage)
        stages[stage] = i8._stage_manifest(dag, stage, normalized)
        return normalized

    hidden = record("hidden_state_input", hidden_inputs)
    names = i11._block_tensor_names(block_index)
    norms = block_binding["norm_tensors"]
    attn_weights = i7._norm_values(norms[names["norms"][0]])
    ffn_weights = i7._norm_values(norms[names["norms"][1]])
    linears = block_binding["compiled_linears"]
    attn_norm = record("rmsnorm_attn", tuple(i7._exact_rmsnorm_dag(dag, values, attn_weights) for values in hidden))

    def linear(base_stage: str, suffix: str, tokens: Sequence[Sequence[str]]) -> tuple[tuple[str, ...], ...]:
        tensor_name = f"blk.{block_index}.{suffix}"
        stage_for_row = i11._stage_name(block_index, base_stage)
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

    expected_stages = tuple(i11._stage_name(block_index, value) for value in GRAPH_OPS)
    if tuple(stages) != expected_stages:
        raise Pass215Iteration12ValidationError(f"PASS215_I12_BLOCK_STAGE_TOPOLOGY_INVALID:{block_index}")
    observed_edges = tuple((x["head"], x["query_position"], x["key_position"]) for x in causal_edges)
    if observed_edges != i8._expected_causal_edges():
        raise Pass215Iteration12ValidationError(f"PASS215_I12_CAUSAL_EDGE_SET_INVALID:{block_index}")
    zero_identity = q_rope[0] == q_values[0] and k_rope[0] == k_values[0]
    nonzero_changes = all(q_rope[p] != q_values[p] and k_rope[p] != k_values[p] for p in range(1, SEQUENCE_LENGTH))
    singleton_identity = all(by_query_head[(0, head)] == (dag.q(1),) for head in range(HEAD_COUNT))
    if not zero_identity or not nonzero_changes or not singleton_identity:
        raise Pass215Iteration12ValidationError(f"PASS215_I12_ATTENTION_CONTROL_FAILED:{block_index}")
    if linear_work != i11._expected_linear_work_per_block():
        raise Pass215Iteration12ValidationError(f"PASS215_I12_LINEAR_WORK_INVALID:{block_index}")

    token_output_roots = [
        i4base.hash216(
            f"pass215-i12-blk{block_index}-final-token-coordinate-roots",
            i4base.canonical_bytes({"position": p, "roots": list(values)}),
        )
        for p, values in enumerate(output)
    ]
    attention_payload = {
        "block_index": block_index,
        "causal_edges": causal_edges,
        "softmax_records": softmax_records,
        "qk_stage_root": stages[i11._stage_name(block_index, "attention_qk_dot")]["stage_root_hash216"],
        "scale_stage_root": stages[i11._stage_name(block_index, "attention_scale")]["stage_root_hash216"],
        "softmax_stage_root": stages[i11._stage_name(block_index, "attention_softmax")]["stage_root_hash216"],
        "weighted_stage_root": stages[i11._stage_name(block_index, "attention_weighted_value")]["stage_root_hash216"],
    }
    return {
        "block_index": block_index,
        "stage_records": stages,
        "executed_stage_suite_root_hash216": i4base.hash216(
            f"pass215-i12-blk{block_index}-stage-suite", i4base.canonical_bytes(stages)
        ),
        "causal_attention_root_hash216": i4base.hash216(
            f"pass215-i12-blk{block_index}-causal-attention-suite", i4base.canonical_bytes(attention_payload)
        ),
        "final_output_token_roots": token_output_roots,
        "final_output_root_hash216": i4base.hash216(
            f"pass215-i12-blk{block_index}-final-output-token-suite", i4base.canonical_bytes(token_output_roots)
        ),
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


def _sum_work(records: Sequence[Mapping[str, int]]) -> Mapping[str, int]:
    if not records:
        raise Pass215Iteration12ValidationError("PASS215_I12_WORK_RECORDS_EMPTY")
    keys = tuple(records[0])
    return {key: sum(int(record[key]) for record in records) for key in keys}


def _sequential_link_root(
    source_block: int,
    target_block: int,
    source_output: Sequence[Sequence[str]],
    target_input: Sequence[Sequence[str]],
) -> str:
    if target_block != source_block + 1:
        raise Pass215Iteration12ValidationError("PASS215_I12_NONADJACENT_BLOCK_LINK")
    left = tuple(tuple(row) for row in source_output)
    right = tuple(tuple(row) for row in target_input)
    if left != right:
        raise Pass215Iteration12ValidationError("PASS215_I12_BLOCK_SEQUENTIAL_LINK_INVALID")
    if (source_block, target_block) == (0, 1):
        root = i11._sequential_link_root(left, right)
        if root != ITERATION11_SEQUENTIAL_LINK_ROOT_HASH216:
            raise Pass215Iteration12ValidationError("PASS215_I12_FROZEN_BLK0_BLK1_LINK_CHANGED")
        return root
    return i4base.hash216(
        "pass215-i12-adjacent-block-coordinate-link",
        i4base.canonical_bytes({
            "source_block": source_block,
            "target_block": target_block,
            "source_output": [list(row) for row in left],
            "target_input": [list(row) for row in right],
        }),
    )


def _prefix_two_block_root(
    architecture: Mapping[str, Any],
    block_binding_roots: Mapping[str, str],
    block0: Mapping[str, Any],
    block1: Mapping[str, Any],
    prefix_manifest: Mapping[str, Any],
    link_root: str,
) -> str:
    total_linear = _sum_work([block0["linear_transition_work"], block1["linear_transition_work"]])
    total_attention = _sum_work([block0["attention_transition_work"], block1["attention_transition_work"]])
    payload = {
        "architecture_root_hash216": architecture["architecture_root_hash216"],
        "block_binding_roots": {"blk.0": block_binding_roots["blk.0"], "blk.1": block_binding_roots["blk.1"]},
        "blk0_frozen_final_output_root_hash216": block0["final_output_root_hash216"],
        "sequential_link_root_hash216": link_root,
        "blk1_final_output_root_hash216": block1["final_output_root_hash216"],
        "full_symbolic_dag_root_hash216": prefix_manifest["ordered_node_root_hash216"],
        "total_linear_transition_work": total_linear,
        "total_attention_transition_work": total_attention,
    }
    return i4base.hash216(
        "pass215-i11-authenticated-sequential-two-block-forward", i4base.canonical_bytes(payload)
    )


def build_all_six_block_evidence(
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
        raise Pass215Iteration12ValidationError("PASS215_I12_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration12ValidationError("PASS215_I12_AUTHENTICATED_MODEL_IDENTITY_MISMATCH")
    if prompt != CONTRACTED_PROMPT:
        raise Pass215Iteration12ValidationError("PASS215_I12_PROMPT_OUTSIDE_CONTRACT")

    # Re-execute and validate the complete frozen Iteration 11 prefix first.
    i11_evidence = i11.build_sequential_two_block_evidence(
        raw, filename=filename, source=source, prompt=prompt, expected_sha256=expected_sha256
    )
    _validate_frozen_iteration11_evidence(i11_evidence)

    architecture = i11._read_architecture_metadata(raw)
    _require_all_block_architecture(architecture)
    if architecture["architecture_root_hash216"] != ITERATION11_ARCHITECTURE_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_ARCHITECTURE_ROOT_CHANGED")
    tokenizer = i10._read_exact_tokenizer_metadata(raw)
    tokenization = i10._tokenize_sentencepiece_bpe(prompt, tokenizer)
    token_ids = tuple(int(value) for value in tokenization["token_ids"])
    if token_ids != FROZEN_TOKEN_IDS:
        raise Pass215Iteration12ValidationError("PASS215_I12_FROZEN_TEXT_TOKEN_IDS_CHANGED")
    embeddings = i9._extract_authenticated_embeddings(raw, tokenizer, token_ids)
    if embeddings["embedding_suite_root_hash216"] != i11.ITERATION10_EMBEDDING_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_FROZEN_EMBEDDING_ROOT_CHANGED")

    bindings = {index: i11._bind_block_tensors(raw, index) for index in BLOCK_INDEXES}
    if any(binding["required_tensor_count"] != 9 for binding in bindings.values()):
        raise Pass215Iteration12ValidationError("PASS215_I12_BLOCK_TENSOR_COUNT_INVALID")
    block_binding_roots = {
        f"blk.{index}": bindings[index]["block_tensor_binding_root_hash216"] for index in BLOCK_INDEXES
    }
    if block_binding_roots["blk.0"] != ITERATION11_BLK0_BINDING_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_BLK0_BINDING_ROOT_CHANGED")
    if block_binding_roots["blk.1"] != ITERATION11_BLK1_BINDING_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_BLK1_BINDING_ROOT_CHANGED")
    all_binding_root = i4base.hash216(
        "pass215-i12-authenticated-all-six-block-tensor-bindings",
        i4base.canonical_bytes(block_binding_roots),
    )

    dag = i8.MultiTokenSymbolicDAG()
    hidden = tuple(tuple(dag.q(n, d) for n, d in row) for row in embeddings["rows"])
    blocks: dict[int, Mapping[str, Any]] = {}
    links: list[Mapping[str, Any]] = []

    block0 = i11._execute_block(dag, hidden, bindings[0], block_index=0)
    blocks[0] = block0
    block1 = i11._execute_block(dag, block0["output_coordinate_roots"], bindings[1], block_index=1)
    blocks[1] = block1
    link01 = _sequential_link_root(0, 1, block0["output_coordinate_roots"], block1["input_coordinate_roots"])
    links.append({"source_block": 0, "target_block": 1, "link_root_hash216": link01, "exact": True})
    prefix_manifest = dag.manifest()
    prefix_checks = {
        "blk1_stage": (block1["executed_stage_suite_root_hash216"], ITERATION11_BLK1_STAGE_SUITE_ROOT_HASH216),
        "blk1_causal": (block1["causal_attention_root_hash216"], ITERATION11_BLK1_CAUSAL_ATTENTION_ROOT_HASH216),
        "blk1_output": (block1["final_output_root_hash216"], ITERATION11_BLK1_FINAL_OUTPUT_ROOT_HASH216),
        "prefix_dag": (prefix_manifest["ordered_node_root_hash216"], ITERATION11_FULL_SYMBOLIC_DAG_ROOT_HASH216),
    }
    for name, (actual, expected) in prefix_checks.items():
        if actual != expected:
            raise Pass215Iteration12ValidationError(f"PASS215_I12_FROZEN_PREFIX_ROOT_CHANGED:{name}")
    prefix_two_block_root = _prefix_two_block_root(
        architecture, block_binding_roots, block0, block1, prefix_manifest, link01
    )
    if prefix_two_block_root != ITERATION11_TWO_BLOCK_FORWARD_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_FROZEN_TWO_BLOCK_FORWARD_ROOT_CHANGED")

    previous = block1
    for block_index in EXTENSION_BLOCK_INDEXES:
        current = _execute_extension_block(
            dag, previous["output_coordinate_roots"], bindings[block_index], block_index=block_index
        )
        link_root = _sequential_link_root(
            block_index - 1,
            block_index,
            previous["output_coordinate_roots"],
            current["input_coordinate_roots"],
        )
        links.append({
            "source_block": block_index - 1,
            "target_block": block_index,
            "link_root_hash216": link_root,
            "exact": True,
        })
        blocks[block_index] = current
        previous = current

    if tuple(blocks) != BLOCK_INDEXES or len(links) != AUTHENTICATED_BLOCK_COUNT - 1:
        raise Pass215Iteration12ValidationError("PASS215_I12_BLOCK_CHAIN_INCOMPLETE")
    full_manifest = dag.manifest()
    total_linear = _sum_work([blocks[index]["linear_transition_work"] for index in BLOCK_INDEXES])
    total_attention = _sum_work([blocks[index]["attention_transition_work"] for index in BLOCK_INDEXES])
    if total_linear != _expected_linear_work_total():
        raise Pass215Iteration12ValidationError("PASS215_I12_TOTAL_LINEAR_WORK_INVALID")
    if total_attention != _expected_attention_work_total():
        raise Pass215Iteration12ValidationError("PASS215_I12_TOTAL_ATTENTION_WORK_INVALID")

    per_block_stage_roots = {
        f"blk.{index}": blocks[index]["executed_stage_suite_root_hash216"] for index in BLOCK_INDEXES
    }
    per_block_causal_roots = {
        f"blk.{index}": blocks[index]["causal_attention_root_hash216"] for index in BLOCK_INDEXES
    }
    per_block_output_roots = {
        f"blk.{index}": blocks[index]["final_output_root_hash216"] for index in BLOCK_INDEXES
    }
    all_stage_root = i4base.hash216(
        "pass215-i12-all-six-block-stage-suite", i4base.canonical_bytes(per_block_stage_roots)
    )
    all_causal_root = i4base.hash216(
        "pass215-i12-all-six-block-causal-attention-suite", i4base.canonical_bytes(per_block_causal_roots)
    )
    sequential_chain_root = i4base.hash216(
        "pass215-i12-all-six-block-sequential-link-chain", i4base.canonical_bytes(links)
    )
    all_block_payload = {
        "architecture_root_hash216": architecture["architecture_root_hash216"],
        "all_block_binding_root_hash216": all_binding_root,
        "block_binding_roots": block_binding_roots,
        "sequential_chain_root_hash216": sequential_chain_root,
        "per_block_final_output_roots": per_block_output_roots,
        "final_block_output_root_hash216": blocks[5]["final_output_root_hash216"],
        "all_stage_suite_root_hash216": all_stage_root,
        "all_causal_attention_root_hash216": all_causal_root,
        "full_symbolic_dag_root_hash216": full_manifest["ordered_node_root_hash216"],
        "total_linear_transition_work": total_linear,
        "total_attention_transition_work": total_attention,
    }
    all_block_forward_root = i4base.hash216(
        "pass215-i12-authenticated-all-six-block-forward", i4base.canonical_bytes(all_block_payload)
    )

    block_records = {
        f"blk.{index}": {
            key: value
            for key, value in blocks[index].items()
            if key not in ("output_coordinate_roots", "input_coordinate_roots")
        }
        for index in BLOCK_INDEXES
    }
    binding_records = {
        f"blk.{index}": {
            "norm_tensors": bindings[index]["norm_tensors"],
            "linear_tensors": bindings[index]["linear_tensors"],
        }
        for index in BLOCK_INDEXES
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
            "no_float_canonical_authority": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
        "inherits": {
            **_iteration11_bindings(),
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
            "tokenization_root_hash216": i11.ITERATION10_TOKENIZATION_ROOT_HASH216,
        },
        "authenticated_embedding_ingress": {
            "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"],
            "selected_token_ids": list(token_ids),
            "embedding_lookup_work": embeddings["embedding_lookup_work"],
        },
        "authenticated_all_block_tensor_bindings": {
            "authenticated_model_block_count": AUTHENTICATED_BLOCK_COUNT,
            "block_count_bound": len(bindings),
            "required_tensor_count": sum(binding["required_tensor_count"] for binding in bindings.values()),
            "block_binding_roots": block_binding_roots,
            "all_block_binding_root_hash216": all_binding_root,
            **binding_records,
        },
        "sequential_all_block_forward": {
            "block_order": list(BLOCK_INDEXES),
            "executed_block_count": len(blocks),
            "stage_count": sum(len(blocks[index]["stage_records"]) for index in BLOCK_INDEXES),
            "blocks": block_records,
            "sequential_links": links,
            "all_adjacent_inputs_equal_previous_outputs": True,
            "iteration11_prefix": {
                "blk0_binding_root_hash216": block_binding_roots["blk.0"],
                "blk1_binding_root_hash216": block_binding_roots["blk.1"],
                "blk0_to_blk1_sequential_link_root_hash216": link01,
                "blk1_stage_suite_root_hash216": block1["executed_stage_suite_root_hash216"],
                "blk1_causal_attention_root_hash216": block1["causal_attention_root_hash216"],
                "blk1_final_output_root_hash216": block1["final_output_root_hash216"],
                "two_block_symbolic_dag_root_hash216": prefix_manifest["ordered_node_root_hash216"],
                "two_block_forward_root_hash216": prefix_two_block_root,
            },
            "per_block_stage_roots": per_block_stage_roots,
            "per_block_causal_attention_roots": per_block_causal_roots,
            "per_block_final_output_roots": per_block_output_roots,
            "all_stage_suite_root_hash216": all_stage_root,
            "all_causal_attention_root_hash216": all_causal_root,
            "sequential_chain_root_hash216": sequential_chain_root,
            "final_block_output_root_hash216": blocks[5]["final_output_root_hash216"],
            "total_linear_transition_work": total_linear,
            "total_attention_transition_work": total_attention,
            "symbolic_dag": full_manifest,
            "all_block_forward_root_hash216": all_block_forward_root,
        },
        "exact_controls": {
            "iteration11_frozen_roots_reexecuted_and_bound": {"exact": True, **_iteration11_bindings()},
            "authenticated_block_count_exactly_six": {"exact": True, "block_count": architecture["block_count"]},
            "all_six_block_tensor_sets_bound": {"exact": True, "required_tensor_count": 54},
            "iteration11_two_block_prefix_reproduced_before_extension": {
                "exact": True,
                "full_symbolic_dag_root_hash216": prefix_manifest["ordered_node_root_hash216"],
                "two_block_forward_root_hash216": prefix_two_block_root,
            },
            "all_adjacent_block_coordinate_links_exact": {"exact": True, "link_count": len(links)},
            "all_six_causal_edge_sets_exact": {"exact": True, "future_edges_materialized": False},
        },
        "claims": {
            "authenticated_iteration11_roots_inherited_unchanged": True,
            "authenticated_all_six_block_tensor_sets_bound": True,
            "iteration11_two_block_prefix_reexecuted_exactly": True,
            "contracted_four_token_all_six_blocks_sequential_forward_executed": True,
            "multi_block_transformer_forward_executed": True,
            "all_model_blocks_executed": True,
            "general_arbitrary_text_tokenizer_conformance_claimed": False,
            "general_arbitrary_sequence_length_transformer_forward_executed": False,
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
        "iteration11_suite_root_hash216": ITERATION11_SUITE_ROOT_HASH216,
        "architecture_root_hash216": architecture["architecture_root_hash216"],
        "all_block_binding_root_hash216": all_binding_root,
        "sequential_chain_root_hash216": sequential_chain_root,
        "all_stage_suite_root_hash216": all_stage_root,
        "all_causal_attention_root_hash216": all_causal_root,
        "final_block_output_root_hash216": blocks[5]["final_output_root_hash216"],
        "all_block_forward_root_hash216": all_block_forward_root,
        "full_symbolic_dag_root_hash216": full_manifest["ordered_node_root_hash216"],
    }
    suite_root = i4base.hash216(
        "pass215-i12-authenticated-all-six-block-suite", i4base.canonical_bytes(roots)
    )
    evidence["all_six_block_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216(
        "pass215-i12-authenticated-all-six-block-evidence", i4base.canonical_bytes(evidence)
    )
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION12_ALL_SIX_BLOCK_FORWARD"},
        {
            "sequence": 12,
            "parent_hash72": ITERATION11_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "all_six_block_suite_root_hash216": suite_root,
        },
    )
    _reject_floats(evidence)
    return evidence


def build_all_six_block_evidence_from_path(
    path: str | Path,
    *,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    target = Path(path)
    return build_all_six_block_evidence(
        target.read_bytes(), filename=target.name, source=source, prompt=prompt, expected_sha256=expected_sha256
    )


def _validate_block_record(block: Mapping[str, Any], block_index: int) -> None:
    if int(block.get("block_index", -1)) != block_index:
        raise Pass215Iteration12ValidationError(f"PASS215_I12_BLOCK_INDEX_RECORD_INVALID:{block_index}")
    if int(block.get("final_output_token_count", 0)) != SEQUENCE_LENGTH:
        raise Pass215Iteration12ValidationError(f"PASS215_I12_BLOCK_TOKEN_COUNT_INVALID:{block_index}")
    if int(block.get("final_output_coordinate_count", 0)) != SEQUENCE_LENGTH * EMBEDDING_WIDTH:
        raise Pass215Iteration12ValidationError(f"PASS215_I12_BLOCK_COORDINATE_COUNT_INVALID:{block_index}")
    controls = block.get("causal_controls", {})
    if controls.get("edge_set_exact") is not True or controls.get("future_edges_materialized") is not False:
        raise Pass215Iteration12ValidationError(f"PASS215_I12_BLOCK_CAUSAL_CONTROL_INVALID:{block_index}")
    if block.get("linear_transition_work") != i11._expected_linear_work_per_block():
        raise Pass215Iteration12ValidationError(f"PASS215_I12_BLOCK_LINEAR_WORK_INVALID:{block_index}")
    if block.get("attention_transition_work") != i8._attention_work_geometry():
        raise Pass215Iteration12ValidationError(f"PASS215_I12_BLOCK_ATTENTION_WORK_INVALID:{block_index}")


def validate_all_six_block_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration12ValidationError("PASS215_I12_SCHEMA_OR_CONTRACT_INVALID")
    inherits = evidence.get("inherits")
    if not isinstance(inherits, Mapping):
        raise Pass215Iteration12ValidationError("PASS215_I12_INHERITANCE_MISSING")
    for key, expected in _iteration11_bindings().items():
        if inherits.get(key) != expected:
            raise Pass215Iteration12ValidationError(f"PASS215_I12_FROZEN_BINDING_INVALID:{key}")

    architecture = evidence.get("authenticated_architecture")
    text = evidence.get("contracted_text_ingress")
    embeddings = evidence.get("authenticated_embedding_ingress")
    bindings = evidence.get("authenticated_all_block_tensor_bindings")
    forward = evidence.get("sequential_all_block_forward")
    claims = evidence.get("claims")
    if not all(isinstance(value, Mapping) for value in (architecture, text, embeddings, bindings, forward, claims)):
        raise Pass215Iteration12ValidationError("PASS215_I12_REQUIRED_SECTION_MISSING")
    _require_all_block_architecture(architecture)
    if architecture.get("architecture_root_hash216") != ITERATION11_ARCHITECTURE_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_ARCHITECTURE_ROOT_INVALID")
    if text.get("input_text") != CONTRACTED_PROMPT or tuple(text.get("token_ids", ())) != FROZEN_TOKEN_IDS:
        raise Pass215Iteration12ValidationError("PASS215_I12_TEXT_INGRESS_INVALID")
    if text.get("tokenization_root_hash216") != i11.ITERATION10_TOKENIZATION_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_TOKENIZATION_ROOT_INVALID")
    if embeddings.get("embedding_suite_root_hash216") != i11.ITERATION10_EMBEDDING_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_EMBEDDING_ROOT_INVALID")
    if int(bindings.get("block_count_bound", 0)) != AUTHENTICATED_BLOCK_COUNT:
        raise Pass215Iteration12ValidationError("PASS215_I12_BLOCK_BINDING_COUNT_INVALID")
    if int(bindings.get("required_tensor_count", 0)) != 54:
        raise Pass215Iteration12ValidationError("PASS215_I12_REQUIRED_TENSOR_COUNT_INVALID")
    binding_roots = bindings.get("block_binding_roots")
    if not isinstance(binding_roots, Mapping) or tuple(binding_roots) != tuple(f"blk.{i}" for i in BLOCK_INDEXES):
        raise Pass215Iteration12ValidationError("PASS215_I12_BLOCK_BINDING_ROOT_SET_INVALID")
    if binding_roots["blk.0"] != ITERATION11_BLK0_BINDING_ROOT_HASH216 or binding_roots["blk.1"] != ITERATION11_BLK1_BINDING_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_FROZEN_PREFIX_BINDING_ROOT_INVALID")
    expected_binding_root = i4base.hash216(
        "pass215-i12-authenticated-all-six-block-tensor-bindings", i4base.canonical_bytes(binding_roots)
    )
    if bindings.get("all_block_binding_root_hash216") != expected_binding_root:
        raise Pass215Iteration12ValidationError("PASS215_I12_ALL_BLOCK_BINDING_ROOT_INVALID")

    if forward.get("block_order") != list(BLOCK_INDEXES) or int(forward.get("executed_block_count", 0)) != AUTHENTICATED_BLOCK_COUNT:
        raise Pass215Iteration12ValidationError("PASS215_I12_BLOCK_ORDER_INVALID")
    if int(forward.get("stage_count", 0)) != len(GRAPH_OPS) * AUTHENTICATED_BLOCK_COUNT:
        raise Pass215Iteration12ValidationError("PASS215_I12_STAGE_COUNT_INVALID")
    if forward.get("all_adjacent_inputs_equal_previous_outputs") is not True:
        raise Pass215Iteration12ValidationError("PASS215_I12_SEQUENTIALITY_CLAIM_INVALID")
    blocks = forward.get("blocks")
    links = forward.get("sequential_links")
    prefix = forward.get("iteration11_prefix")
    if not isinstance(blocks, Mapping) or not isinstance(links, list) or not isinstance(prefix, Mapping):
        raise Pass215Iteration12ValidationError("PASS215_I12_FORWARD_SUBSECTION_MISSING")
    if tuple(blocks) != tuple(f"blk.{i}" for i in BLOCK_INDEXES):
        raise Pass215Iteration12ValidationError("PASS215_I12_BLOCK_RECORD_SET_INVALID")
    for index in BLOCK_INDEXES:
        _validate_block_record(blocks[f"blk.{index}"], index)
    if len(links) != AUTHENTICATED_BLOCK_COUNT - 1:
        raise Pass215Iteration12ValidationError("PASS215_I12_SEQUENTIAL_LINK_COUNT_INVALID")
    for index, link in enumerate(links):
        if link.get("source_block") != index or link.get("target_block") != index + 1 or link.get("exact") is not True:
            raise Pass215Iteration12ValidationError(f"PASS215_I12_SEQUENTIAL_LINK_RECORD_INVALID:{index}")
    if links[0]["link_root_hash216"] != ITERATION11_SEQUENTIAL_LINK_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_FROZEN_FIRST_LINK_INVALID")

    expected_prefix = {
        "blk0_binding_root_hash216": ITERATION11_BLK0_BINDING_ROOT_HASH216,
        "blk1_binding_root_hash216": ITERATION11_BLK1_BINDING_ROOT_HASH216,
        "blk0_to_blk1_sequential_link_root_hash216": ITERATION11_SEQUENTIAL_LINK_ROOT_HASH216,
        "blk1_stage_suite_root_hash216": ITERATION11_BLK1_STAGE_SUITE_ROOT_HASH216,
        "blk1_causal_attention_root_hash216": ITERATION11_BLK1_CAUSAL_ATTENTION_ROOT_HASH216,
        "blk1_final_output_root_hash216": ITERATION11_BLK1_FINAL_OUTPUT_ROOT_HASH216,
        "two_block_symbolic_dag_root_hash216": ITERATION11_FULL_SYMBOLIC_DAG_ROOT_HASH216,
        "two_block_forward_root_hash216": ITERATION11_TWO_BLOCK_FORWARD_ROOT_HASH216,
    }
    if dict(prefix) != expected_prefix:
        raise Pass215Iteration12ValidationError("PASS215_I12_ITERATION11_PREFIX_INVALID")
    if blocks["blk.1"]["executed_stage_suite_root_hash216"] != ITERATION11_BLK1_STAGE_SUITE_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_BLK1_STAGE_ROOT_INVALID")
    if blocks["blk.1"]["causal_attention_root_hash216"] != ITERATION11_BLK1_CAUSAL_ATTENTION_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_BLK1_CAUSAL_ROOT_INVALID")
    if blocks["blk.1"]["final_output_root_hash216"] != ITERATION11_BLK1_FINAL_OUTPUT_ROOT_HASH216:
        raise Pass215Iteration12ValidationError("PASS215_I12_BLK1_OUTPUT_ROOT_INVALID")

    expected_total_linear = _expected_linear_work_total()
    expected_total_attention = _expected_attention_work_total()
    if forward.get("total_linear_transition_work") != expected_total_linear:
        raise Pass215Iteration12ValidationError("PASS215_I12_TOTAL_LINEAR_WORK_VALIDATION_INVALID")
    if forward.get("total_attention_transition_work") != expected_total_attention:
        raise Pass215Iteration12ValidationError("PASS215_I12_TOTAL_ATTENTION_WORK_VALIDATION_INVALID")
    if expected_total_attention.get("causal_qk_edges") != 360:
        raise Pass215Iteration12ValidationError("PASS215_I12_CAUSAL_EDGE_GEOMETRY_INVALID")

    per_stage = {f"blk.{i}": blocks[f"blk.{i}"]["executed_stage_suite_root_hash216"] for i in BLOCK_INDEXES}
    per_causal = {f"blk.{i}": blocks[f"blk.{i}"]["causal_attention_root_hash216"] for i in BLOCK_INDEXES}
    per_output = {f"blk.{i}": blocks[f"blk.{i}"]["final_output_root_hash216"] for i in BLOCK_INDEXES}
    if forward.get("per_block_stage_roots") != per_stage or forward.get("per_block_causal_attention_roots") != per_causal or forward.get("per_block_final_output_roots") != per_output:
        raise Pass215Iteration12ValidationError("PASS215_I12_PER_BLOCK_ROOT_PROJECTION_INVALID")
    expected_stage_root = i4base.hash216(
        "pass215-i12-all-six-block-stage-suite", i4base.canonical_bytes(per_stage)
    )
    expected_causal_root = i4base.hash216(
        "pass215-i12-all-six-block-causal-attention-suite", i4base.canonical_bytes(per_causal)
    )
    expected_chain_root = i4base.hash216(
        "pass215-i12-all-six-block-sequential-link-chain", i4base.canonical_bytes(links)
    )
    if forward.get("all_stage_suite_root_hash216") != expected_stage_root:
        raise Pass215Iteration12ValidationError("PASS215_I12_ALL_STAGE_ROOT_INVALID")
    if forward.get("all_causal_attention_root_hash216") != expected_causal_root:
        raise Pass215Iteration12ValidationError("PASS215_I12_ALL_CAUSAL_ROOT_INVALID")
    if forward.get("sequential_chain_root_hash216") != expected_chain_root:
        raise Pass215Iteration12ValidationError("PASS215_I12_CHAIN_ROOT_INVALID")
    if forward.get("final_block_output_root_hash216") != per_output["blk.5"]:
        raise Pass215Iteration12ValidationError("PASS215_I12_FINAL_BLOCK_OUTPUT_ROOT_INVALID")

    required_true = (
        "authenticated_iteration11_roots_inherited_unchanged",
        "authenticated_all_six_block_tensor_sets_bound",
        "iteration11_two_block_prefix_reexecuted_exactly",
        "contracted_four_token_all_six_blocks_sequential_forward_executed",
        "multi_block_transformer_forward_executed",
        "all_model_blocks_executed",
    )
    required_false = (
        "general_arbitrary_text_tokenizer_conformance_claimed",
        "general_arbitrary_sequence_length_transformer_forward_executed",
        "full_model_forward_executed",
        "final_output_norm_executed",
        "output_logits_executed",
        "generation_or_sampling_executed",
        "numeric_transcendental_evaluation_performed",
        "approximate_transcendental_evaluation_performed",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "runtime_mutation_performed",
        "canonical_mutation_performed",
    )
    if any(claims.get(key) is not True for key in required_true):
        raise Pass215Iteration12ValidationError("PASS215_I12_REQUIRED_TRUE_CLAIM_INVALID")
    if any(claims.get(key) is not False for key in required_false):
        raise Pass215Iteration12ValidationError("PASS215_I12_REQUIRED_FALSE_CLAIM_INVALID")

    all_block_payload = {
        "architecture_root_hash216": architecture["architecture_root_hash216"],
        "all_block_binding_root_hash216": bindings["all_block_binding_root_hash216"],
        "block_binding_roots": binding_roots,
        "sequential_chain_root_hash216": expected_chain_root,
        "per_block_final_output_roots": per_output,
        "final_block_output_root_hash216": per_output["blk.5"],
        "all_stage_suite_root_hash216": expected_stage_root,
        "all_causal_attention_root_hash216": expected_causal_root,
        "full_symbolic_dag_root_hash216": forward["symbolic_dag"]["ordered_node_root_hash216"],
        "total_linear_transition_work": expected_total_linear,
        "total_attention_transition_work": expected_total_attention,
    }
    expected_forward_root = i4base.hash216(
        "pass215-i12-authenticated-all-six-block-forward", i4base.canonical_bytes(all_block_payload)
    )
    if forward.get("all_block_forward_root_hash216") != expected_forward_root:
        raise Pass215Iteration12ValidationError("PASS215_I12_ALL_BLOCK_FORWARD_ROOT_INVALID")
    roots = {
        "iteration11_suite_root_hash216": ITERATION11_SUITE_ROOT_HASH216,
        "architecture_root_hash216": architecture["architecture_root_hash216"],
        "all_block_binding_root_hash216": bindings["all_block_binding_root_hash216"],
        "sequential_chain_root_hash216": expected_chain_root,
        "all_stage_suite_root_hash216": expected_stage_root,
        "all_causal_attention_root_hash216": expected_causal_root,
        "final_block_output_root_hash216": per_output["blk.5"],
        "all_block_forward_root_hash216": expected_forward_root,
        "full_symbolic_dag_root_hash216": forward["symbolic_dag"]["ordered_node_root_hash216"],
    }
    expected_suite = i4base.hash216(
        "pass215-i12-authenticated-all-six-block-suite", i4base.canonical_bytes(roots)
    )
    if evidence.get("all_six_block_suite_root_hash216") != expected_suite:
        raise Pass215Iteration12ValidationError("PASS215_I12_SUITE_ROOT_INVALID")
    body = dict(evidence)
    evidence_root = body.pop("evidence_root_hash216", None)
    receipt = body.pop("receipt_hash72", None)
    expected_evidence = i4base.hash216(
        "pass215-i12-authenticated-all-six-block-evidence", i4base.canonical_bytes(body)
    )
    if evidence_root != expected_evidence:
        raise Pass215Iteration12ValidationError("PASS215_I12_EVIDENCE_ROOT_INVALID")
    expected_receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION12_ALL_SIX_BLOCK_FORWARD"},
        {
            "sequence": 12,
            "parent_hash72": ITERATION11_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "all_six_block_suite_root_hash216": expected_suite,
        },
    )
    if receipt != expected_receipt:
        raise Pass215Iteration12ValidationError("PASS215_I12_RECEIPT_INVALID")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_all_six_block_evidence(left)
    validate_all_six_block_evidence(right)
    lf = left["sequential_all_block_forward"]
    rf = right["sequential_all_block_forward"]
    lb = left["authenticated_all_block_tensor_bindings"]
    rb = right["authenticated_all_block_tensor_bindings"]
    identities = {
        "architecture_root_hash216": left["authenticated_architecture"]["architecture_root_hash216"] == right["authenticated_architecture"]["architecture_root_hash216"],
        "all_block_binding_root_hash216": lb["all_block_binding_root_hash216"] == rb["all_block_binding_root_hash216"],
        "block_binding_roots": lb["block_binding_roots"] == rb["block_binding_roots"],
        "sequential_links": lf["sequential_links"] == rf["sequential_links"],
        "sequential_chain_root_hash216": lf["sequential_chain_root_hash216"] == rf["sequential_chain_root_hash216"],
        "per_block_final_output_roots": lf["per_block_final_output_roots"] == rf["per_block_final_output_roots"],
        "final_block_output_root_hash216": lf["final_block_output_root_hash216"] == rf["final_block_output_root_hash216"],
        "all_stage_suite_root_hash216": lf["all_stage_suite_root_hash216"] == rf["all_stage_suite_root_hash216"],
        "all_causal_attention_root_hash216": lf["all_causal_attention_root_hash216"] == rf["all_causal_attention_root_hash216"],
        "full_symbolic_dag_root_hash216": lf["symbolic_dag"]["ordered_node_root_hash216"] == rf["symbolic_dag"]["ordered_node_root_hash216"],
        "all_block_forward_root_hash216": lf["all_block_forward_root_hash216"] == rf["all_block_forward_root_hash216"],
        "suite_root_hash216": left["all_six_block_suite_root_hash216"] == right["all_six_block_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"] == right["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"] == right["receipt_hash72"],
    }
    return {
        "schema": REPLAY_SCHEMA,
        "cross_process_replay": all(identities.values()),
        "semantic_exactness": all(identities.values()),
        "identities": identities,
        "final_block_output_root_hash216": lf["final_block_output_root_hash216"],
        "all_block_forward_root_hash216": lf["all_block_forward_root_hash216"],
        "full_symbolic_dag_root_hash216": lf["symbolic_dag"]["ordered_node_root_hash216"],
        "suite_root_hash216": left["all_six_block_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }


__all__ = [
    "CONTRACT", "PASS_NUMBER", "ITERATION", "EVIDENCE_SCHEMA", "VALIDATION_SCHEMA", "REPLAY_SCHEMA",
    "REAL_MODEL_SHA256", "CONTRACTED_PROMPT", "SEQUENCE_LENGTH", "EMBEDDING_WIDTH", "FFN_WIDTH",
    "HEAD_COUNT", "HEAD_DIMENSION", "AUTHENTICATED_BLOCK_COUNT", "BLOCK_INDEXES", "EXTENSION_BLOCK_INDEXES",
    "Pass215Iteration12Error", "Pass215Iteration12ValidationError", "_iteration11_bindings",
    "_validate_frozen_iteration11_evidence", "_require_all_block_architecture", "_expected_linear_work_total",
    "_expected_attention_work_total", "_execute_extension_block", "_sequential_link_root",
    "build_all_six_block_evidence", "build_all_six_block_evidence_from_path",
    "validate_all_six_block_evidence", "compare_replay",
]
