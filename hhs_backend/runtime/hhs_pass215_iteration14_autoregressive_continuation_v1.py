"""Pass 215 Iteration 14 exact deterministic autoregressive continuation.

Extends the frozen Iteration 13 authenticated terminal model head with an exact,
integer/symbolic token-selection policy and append-only KV-state continuation.
The contracted witness is still the authenticated four-token ``Hello world!``
prefix.  Selection is deliberately defined over symbolic logit identities, not
numeric magnitude: the token whose exact Hash216 logit-root identity is
lexicographically minimal is selected, with token id as an explicit tie-breaker.

This establishes deterministic token selection and multi-step autoregressive
state reuse without introducing floating authority or pretending that symbolic
root ordering is numerical argmax/sampling.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7
from hhs_backend.runtime import hhs_pass215_iteration8_multi_token_causal_attention_v1 as i8
from hhs_backend.runtime import hhs_pass215_iteration9_authenticated_token_ingress_v2 as i9
from hhs_backend.runtime import hhs_pass215_iteration10_exact_text_token_ingress_v1 as i10
from hhs_backend.runtime import hhs_pass215_iteration11_sequential_two_block_v1 as i11
from hhs_backend.runtime import hhs_pass215_iteration12_all_six_block_forward_v1 as i12
from hhs_backend.runtime import hhs_pass215_iteration13_terminal_model_head_v1 as i13

CONTRACT = "HHS-P215-I14-EXACT-AUTOREGRESSIVE-CONTINUATION"
PASS_NUMBER = 215
ITERATION = 14
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_14_AUTOREGRESSIVE_CONTINUATION_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_14_AUTOREGRESSIVE_CONTINUATION_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_14_AUTOREGRESSIVE_CONTINUATION_REPLAY_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_14_EXACT_SYMBOLIC_AUTOREGRESSIVE_BENCHMARK"

ITERATION13_CLOSURE_HEAD = "1253bdfaff0eea3688f28ac749df31e4f1613d06"
ITERATION13_CLOSURE_TREE = "cdf253c6c08d0bf0184b501f0395667c5e2a04c8"
ITERATION13_TERMINAL_TOPOLOGY_ROOT_HASH216 = "cc6cdb8d50769ccc6baff3c55732ea4f6cfa1fe2c9a5b3ff8b9cf0e41f9b03b4"
ITERATION13_OUTPUT_NORM_VALUE_ROOT_HASH216 = "5d9db692ebb5b1f2d2ec0507ec4a3d8222620270e67cec8f265a80aeaa4ce063"
ITERATION13_OUTPUT_DESCRIPTOR_ROOT_HASH216 = "bd555175efd71d0c58892d14df30769c971b0a83231108eec9735e660b3e4ce8"
ITERATION13_Q8_SEMANTIC_CONTROL_ROOT_HASH216 = "d7a33b0cd2eae98d4cc2172ed6b2e2ff04c67f29151aabca9f2df097fe3b4622"
ITERATION13_TERMINAL_NORM_ROOT_HASH216 = "4a6cd80b2eb3d16ab92ae9b58c4cf58a38d7bbda23debff275e743af3bfdc42b"
ITERATION13_LOGITS_ROOT_HASH216 = "32fb61d26431c937050d39809b289dbf65c73ecce40b6bd30378e43ecb977ceb"
ITERATION13_FULL_DAG_ROOT_HASH216 = "095aadfa389728fb0fc53df0acd3632bfe09af75b13ca2d64d576c117ac0ccd5"
ITERATION13_FULL_MODEL_FORWARD_ROOT_HASH216 = "c34e78a37f93597adc703c37ecdd59fefb769447946932e0d5eee496b4373dac"
ITERATION13_SUITE_ROOT_HASH216 = "046fff2e286f14d71b71aac2e11ddd0cee12c5d1f39255e695e9af4b632a2acc"
ITERATION13_EVIDENCE_ROOT_HASH216 = "ac57c26fe9119f56c11641297e6f6be8f71aae2fd59bc655445d5b07ad34c2a5"
ITERATION13_RECEIPT_HASH72 = "6a0VdJ2YaxDx6m2RFaI8UxEyyxSi!gW1<xA4bB0OIKrAg*phhTeHRkYh0tWfWvcO1g/*(A<Z"
ITERATION13_CLOSURE_ARTIFACT_SHA256 = "38c606cba6f465e8a8edd763da22feb4c464d6bd3a9118a3a45515b925bf4f65"

REAL_MODEL_SHA256 = i13.REAL_MODEL_SHA256
CONTRACTED_PROMPT = i13.CONTRACTED_PROMPT
FROZEN_TOKEN_IDS = i13.FROZEN_TOKEN_IDS
PREFIX_SEQUENCE_LENGTH = i13.SEQUENCE_LENGTH
EMBEDDING_WIDTH = i13.EMBEDDING_WIDTH
HEAD_COUNT = i8.HEAD_COUNT
HEAD_DIMENSION = i8.HEAD_DIMENSION
AUTHENTICATED_BLOCK_COUNT = i13.AUTHENTICATED_BLOCK_COUNT
VOCABULARY_SIZE = 32000
GENERATED_TOKEN_COUNT = 2
PROCESSED_APPEND_COUNT = 2
SELECTION_POLICY = "LEXICOGRAPHIC_MINIMUM_HASH216_LOGIT_ROOT_THEN_TOKEN_ID"
SELECTION_SEMANTICS = "EXACT_SYMBOLIC_IDENTITY_TOTAL_ORDER_NOT_NUMERIC_ARGMAX"


class Pass215Iteration14Error(RuntimeError):
    pass


class Pass215Iteration14ValidationError(Pass215Iteration14Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration14ValidationError(f"PASS215_I14_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _iteration13_bindings() -> Mapping[str, Any]:
    return {
        "iteration13_closure_head": ITERATION13_CLOSURE_HEAD,
        "iteration13_closure_tree": ITERATION13_CLOSURE_TREE,
        "iteration13_terminal_topology_root_hash216": ITERATION13_TERMINAL_TOPOLOGY_ROOT_HASH216,
        "iteration13_output_norm_value_root_hash216": ITERATION13_OUTPUT_NORM_VALUE_ROOT_HASH216,
        "iteration13_output_descriptor_root_hash216": ITERATION13_OUTPUT_DESCRIPTOR_ROOT_HASH216,
        "iteration13_q8_semantic_control_root_hash216": ITERATION13_Q8_SEMANTIC_CONTROL_ROOT_HASH216,
        "iteration13_terminal_norm_root_hash216": ITERATION13_TERMINAL_NORM_ROOT_HASH216,
        "iteration13_logits_root_hash216": ITERATION13_LOGITS_ROOT_HASH216,
        "iteration13_full_dag_root_hash216": ITERATION13_FULL_DAG_ROOT_HASH216,
        "iteration13_full_model_forward_root_hash216": ITERATION13_FULL_MODEL_FORWARD_ROOT_HASH216,
        "iteration13_suite_root_hash216": ITERATION13_SUITE_ROOT_HASH216,
        "iteration13_evidence_root_hash216": ITERATION13_EVIDENCE_ROOT_HASH216,
        "iteration13_receipt_hash72": ITERATION13_RECEIPT_HASH72,
        "iteration13_closure_artifact_sha256": ITERATION13_CLOSURE_ARTIFACT_SHA256,
    }


def _single_stage_root(stage: str, absolute_position: int, values: Sequence[str]) -> str:
    return i4base.hash216(
        "pass215-i14-incremental-stage",
        i4base.canonical_bytes(
            {"stage": stage, "absolute_position": absolute_position, "coordinate_roots": list(values)}
        ),
    )


def _selection_policy(logit_roots: Sequence[str]) -> Mapping[str, Any]:
    if not logit_roots:
        raise Pass215Iteration14ValidationError("PASS215_I14_LOGIT_VECTOR_EMPTY")
    candidates = []
    for token_id, root in enumerate(logit_roots):
        if not isinstance(root, str) or len(root) != 64:
            raise Pass215Iteration14ValidationError("PASS215_I14_LOGIT_ROOT_INVALID")
        candidates.append((root, token_id))
    selected_root, selected_id = min(candidates)
    candidate_root = i4base.hash216(
        "pass215-i14-selection-candidate-set",
        i4base.canonical_bytes(
            [{"token_id": token_id, "logit_root_hash216": root} for root, token_id in candidates]
        ),
    )
    record = {
        "policy": SELECTION_POLICY,
        "semantics": SELECTION_SEMANTICS,
        "candidate_count": len(candidates),
        "candidate_set_root_hash216": candidate_root,
        "selected_token_id": selected_id,
        "selected_logit_root_hash216": selected_root,
        "total_order_key": ["logit_root_hash216", "token_id"],
        "numeric_logit_magnitude_interpreted": False,
        "numeric_argmax_performed": False,
        "probabilistic_sampling_performed": False,
        "canonical_float_interpretation_performed": False,
    }
    record["selection_root_hash216"] = i4base.hash216(
        "pass215-i14-exact-symbolic-token-selection", i4base.canonical_bytes(record)
    )
    return record


def _project_logits(
    dag: i13.TerminalHeadSymbolicDAG,
    normalized_row: Sequence[str],
    descriptor: Mapping[str, Any],
    *,
    stage: str,
) -> tuple[str, ...]:
    if len(normalized_row) != EMBEDDING_WIDTH:
        raise Pass215Iteration14ValidationError("PASS215_I14_TERMINAL_INPUT_GEOMETRY_INVALID")
    vocab_size = int(descriptor["row_count"])
    if vocab_size != VOCABULARY_SIZE:
        raise Pass215Iteration14ValidationError("PASS215_I14_VOCABULARY_SIZE_CHANGED")
    input_root = dag.vector(tuple(normalized_row), f"{stage}:input")
    return tuple(
        dag.intern(
            "q8_0_linear_row",
            (input_root,),
            {
                "stage": stage,
                "tensor": i13.OUTPUT_TENSOR,
                "row_index": row_index,
                "input_width": EMBEDDING_WIDTH,
                "descriptor_root_hash216": descriptor["descriptor_root_hash216"],
                "source_sha256": descriptor["source_sha256"],
                "semantic_form": descriptor["semantic_form"],
                "factored_generator": True,
            },
        )
        for row_index in range(vocab_size)
    )


def _revalidate_iteration13_semantics(
    prefix: Mapping[str, Any],
    terminal_binding: Mapping[str, Any],
    q8_control: Mapping[str, Any],
    terminal: Mapping[str, Any],
) -> Mapping[str, Any]:
    full_manifest = prefix["dag"].manifest()
    topology = terminal_binding["topology"]
    norm = terminal_binding["output_norm"]
    projection = terminal_binding["output_projection"]
    checks = {
        "terminal_topology": (topology["topology_root_hash216"], ITERATION13_TERMINAL_TOPOLOGY_ROOT_HASH216),
        "output_norm_values": (norm["canonical_value_root_hash216"], ITERATION13_OUTPUT_NORM_VALUE_ROOT_HASH216),
        "output_descriptor": (projection["descriptor_root_hash216"], ITERATION13_OUTPUT_DESCRIPTOR_ROOT_HASH216),
        "q8_control": (q8_control["control_root_hash216"], ITERATION13_Q8_SEMANTIC_CONTROL_ROOT_HASH216),
        "terminal_norm": (terminal["terminal_norm_root_hash216"], ITERATION13_TERMINAL_NORM_ROOT_HASH216),
        "logits": (terminal["logits_root_hash216"], ITERATION13_LOGITS_ROOT_HASH216),
        "full_dag": (full_manifest["ordered_node_root_hash216"], ITERATION13_FULL_DAG_ROOT_HASH216),
    }
    for name, (actual, expected) in checks.items():
        if actual != expected:
            raise Pass215Iteration14ValidationError(f"PASS215_I14_ITERATION13_ROOT_MISMATCH:{name}")
    terminal_payload = {
        "iteration12_all_block_forward_root_hash216": i13.ITERATION12_ALL_BLOCK_FORWARD_ROOT_HASH216,
        "terminal_topology_root_hash216": topology["topology_root_hash216"],
        "output_norm_value_root_hash216": norm["canonical_value_root_hash216"],
        "output_projection_descriptor_root_hash216": projection["descriptor_root_hash216"],
        "terminal_norm_root_hash216": terminal["terminal_norm_root_hash216"],
        "logits_root_hash216": terminal["logits_root_hash216"],
        "full_symbolic_dag_root_hash216": full_manifest["ordered_node_root_hash216"],
        "projection_transition_work": terminal["projection_transition_work"],
    }
    forward_root = i4base.hash216(
        "pass215-i13-authenticated-terminal-model-head-forward", i4base.canonical_bytes(terminal_payload)
    )
    if forward_root != ITERATION13_FULL_MODEL_FORWARD_ROOT_HASH216:
        raise Pass215Iteration14ValidationError("PASS215_I14_ITERATION13_FORWARD_ROOT_MISMATCH")
    return {
        "exact": True,
        **_iteration13_bindings(),
        "reexecuted_full_model_forward_root_hash216": forward_root,
    }


def _materialize_prefix_kv_cache(
    dag: i13.TerminalHeadSymbolicDAG,
    prefix: Mapping[str, Any],
    bindings: Mapping[int, Mapping[str, Any]],
) -> MutableMapping[int, MutableMapping[str, list[tuple[str, ...]]]]:
    before = dag.manifest()["unique_node_count"]
    cache: MutableMapping[int, MutableMapping[str, list[tuple[str, ...]]]] = {}
    for block_index in i12.BLOCK_INDEXES:
        hidden = prefix["blocks"][block_index]["input_coordinate_roots"]
        names = i11._block_tensor_names(block_index)
        norms = bindings[block_index]["norm_tensors"]
        attn_weights = i7._norm_values(norms[names["norms"][0]])
        linears = bindings[block_index]["compiled_linears"]
        attn_norm = tuple(i7._exact_rmsnorm_dag(dag, row, attn_weights) for row in hidden)
        k_values = []
        v_values = []
        for position, values in enumerate(attn_norm):
            stage_k = f"{i11._stage_name(block_index, 'linear_attn_k')}:token:{position}"
            stage_v = f"{i11._stage_name(block_index, 'linear_attn_v')}:token:{position}"
            k, _ = i7._linear_symbolic(
                dag, linears[f"blk.{block_index}.attn_k.weight"], values, stage=stage_k
            )
            v, _ = i7._linear_symbolic(
                dag, linears[f"blk.{block_index}.attn_v.weight"], values, stage=stage_v
            )
            k_values.append(tuple(k))
            v_values.append(tuple(v))
        k_rope = [
            tuple(i8._rope_token(dag, values, position=position))
            for position, values in enumerate(k_values)
        ]
        cache[block_index] = {"k_rope": k_rope, "v": v_values}
    after = dag.manifest()["unique_node_count"]
    if after != before:
        raise Pass215Iteration14ValidationError("PASS215_I14_PREFIX_CACHE_RECONSTRUCTION_ADDED_NODES")
    return cache


def _incremental_attention_work(context_length: int) -> Mapping[str, int]:
    if context_length <= 0:
        raise Pass215Iteration14ValidationError("PASS215_I14_CONTEXT_LENGTH_INVALID")
    edges = HEAD_COUNT * context_length
    shifted = max(context_length - 1, 0)
    return {
        "causal_qk_edges": edges,
        "qk_dot_logical_products": edges * HEAD_DIMENSION,
        "qk_dot_logical_additions": edges * (HEAD_DIMENSION - 1),
        "attention_scale_multiplications": edges,
        "softmax_shifted_exponentials": HEAD_COUNT * shifted,
        "softmax_denominator_logical_additions": HEAD_COUNT * shifted,
        "softmax_denominator_inverses": HEAD_COUNT if context_length > 1 else 0,
        "softmax_probability_products": HEAD_COUNT * context_length if context_length > 1 else 0,
        "weighted_value_logical_products": edges * HEAD_DIMENSION,
        "weighted_value_logical_additions": HEAD_COUNT * HEAD_DIMENSION * shifted,
        "rope_new_position_pair_rotations_q_and_k": HEAD_COUNT * (HEAD_DIMENSION // 2) * 2,
    }


def _execute_incremental_block(
    dag: i13.TerminalHeadSymbolicDAG,
    hidden_row: Sequence[str],
    block_binding: Mapping[str, Any],
    block_cache: MutableMapping[str, list[tuple[str, ...]]],
    *,
    block_index: int,
    absolute_position: int,
    append_index: int,
) -> Mapping[str, Any]:
    if block_index not in i12.BLOCK_INDEXES:
        raise Pass215Iteration14ValidationError("PASS215_I14_BLOCK_INDEX_INVALID")
    if len(hidden_row) != EMBEDDING_WIDTH:
        raise Pass215Iteration14ValidationError("PASS215_I14_INCREMENTAL_HIDDEN_GEOMETRY_INVALID")
    if len(block_cache["k_rope"]) != absolute_position or len(block_cache["v"]) != absolute_position:
        raise Pass215Iteration14ValidationError("PASS215_I14_CACHE_POSITION_MISMATCH")

    names = i11._block_tensor_names(block_index)
    norms = block_binding["norm_tensors"]
    attn_weights = i7._norm_values(norms[names["norms"][0]])
    ffn_weights = i7._norm_values(norms[names["norms"][1]])
    linears = block_binding["compiled_linears"]
    linear_work = {"row_transitions": 0, "logical_weight_products": 0, "logical_accumulation_additions": 0}
    stage_roots: dict[str, str] = {}

    def stage(name: str, values: Sequence[str]) -> tuple[str, ...]:
        row = tuple(values)
        stage_roots[name] = _single_stage_root(
            f"blk.{block_index}/{name}", absolute_position, row
        )
        return row

    def linear(name: str, suffix: str, inputs: Sequence[str]) -> tuple[str, ...]:
        values, work = i7._linear_symbolic(
            dag,
            linears[f"blk.{block_index}.{suffix}"],
            inputs,
            stage=f"pass215-i14:append:{append_index}:blk.{block_index}:{name}:token:{absolute_position}",
        )
        for key in linear_work:
            linear_work[key] += int(work[key])
        return stage(name, values)

    hidden = stage("hidden_state_input", hidden_row)
    attn_norm = stage("rmsnorm_attn", i7._exact_rmsnorm_dag(dag, hidden, attn_weights))
    q_values = linear("linear_attn_q", "attn_q.weight", attn_norm)
    k_values = linear("linear_attn_k", "attn_k.weight", attn_norm)
    v_values = linear("linear_attn_v", "attn_v.weight", attn_norm)
    q_rope = stage("rope_q", i8._rope_token(dag, q_values, position=absolute_position))
    k_rope = stage("rope_k", i8._rope_token(dag, k_values, position=absolute_position))

    all_k = tuple(block_cache["k_rope"]) + (k_rope,)
    all_v = tuple(block_cache["v"]) + (v_values,)
    context_length = len(all_k)
    scale = dag.rsqrt(dag.q(HEAD_DIMENSION))
    weighted: list[str] = []
    score_roots: list[str] = []
    probability_roots: list[str] = []
    softmax_records: list[Mapping[str, Any]] = []
    for head in range(HEAD_COUNT):
        start, end = head * HEAD_DIMENSION, (head + 1) * HEAD_DIMENSION
        scores = tuple(
            i7._dot(dag, q_rope[start:end], all_k[key_position][start:end])
            for key_position in range(context_length)
        )
        score_roots.extend(scores)
        scaled = tuple(dag.mul(score, scale) for score in scores)
        probabilities, softmax_record = i8._exact_causal_softmax(dag, scaled)
        probability_roots.extend(probabilities)
        softmax_records.append(
            {
                "head": head,
                "query_position": absolute_position,
                "causal_key_positions": list(range(context_length)),
                **softmax_record,
                "probability_roots": list(probabilities),
            }
        )
        for dimension in range(HEAD_DIMENSION):
            terms = tuple(
                dag.mul(probabilities[key_position], all_v[key_position][start + dimension])
                for key_position in range(context_length)
            )
            weighted.append(dag.add(*terms))

    stage("attention_qk_dot", score_roots)
    stage("attention_softmax", probability_roots)
    weighted_values = stage("attention_weighted_value", weighted)
    attn_output = linear("linear_attn_output", "attn_output.weight", weighted_values)
    post_attn = stage(
        "residual_attention",
        tuple(dag.add(left, right) for left, right in zip(hidden, attn_output)),
    )
    ffn_norm = stage("rmsnorm_ffn", i7._exact_rmsnorm_dag(dag, post_attn, ffn_weights))
    gate = linear("linear_ffn_gate", "ffn_gate.weight", ffn_norm)
    activated = stage("silu", tuple(i7._silu(dag, value) for value in gate))
    up = linear("linear_ffn_up", "ffn_up.weight", ffn_norm)
    gated = stage(
        "ffn_gate_product",
        tuple(dag.mul(left, right) for left, right in zip(activated, up)),
    )
    down = linear("linear_ffn_down", "ffn_down.weight", gated)
    output = stage(
        "residual_ffn",
        tuple(dag.add(left, right) for left, right in zip(post_attn, down)),
    )

    expected_linear = {
        "row_transitions": 2976,
        "logical_weight_products": 995328,
        "logical_accumulation_additions": 992352,
    }
    if linear_work != expected_linear:
        raise Pass215Iteration14ValidationError(
            f"PASS215_I14_INCREMENTAL_LINEAR_WORK_INVALID:{block_index}"
        )
    block_cache["k_rope"].append(k_rope)
    block_cache["v"].append(v_values)
    block_root = i4base.hash216(
        "pass215-i14-incremental-block-forward",
        i4base.canonical_bytes(
            {
                "append_index": append_index,
                "block_index": block_index,
                "absolute_position": absolute_position,
                "context_length": context_length,
                "stage_roots": stage_roots,
                "linear_work": linear_work,
                "attention_work": _incremental_attention_work(context_length),
                "softmax_records": softmax_records,
            }
        ),
    )
    return {
        "output_coordinate_roots": output,
        "block_forward_root_hash216": block_root,
        "stage_roots": stage_roots,
        "linear_transition_work": linear_work,
        "attention_transition_work": _incremental_attention_work(context_length),
        "context_length": context_length,
        "prior_kv_token_rows_reused": context_length - 1,
        "new_kv_token_rows_materialized": 1,
        "prefix_hidden_rows_recomputed": 0,
    }


def _terminal_generated_position(
    dag: i13.TerminalHeadSymbolicDAG,
    final_hidden_row: Sequence[str],
    terminal_binding: Mapping[str, Any],
    *,
    absolute_position: int,
    append_index: int,
) -> Mapping[str, Any]:
    norm_weights = i7._norm_values(terminal_binding["output_norm"])
    normalized = tuple(i7._exact_rmsnorm_dag(dag, final_hidden_row, norm_weights))
    norm_root = i4base.hash216(
        "pass215-i14-generated-terminal-norm",
        i4base.canonical_bytes(
            {"absolute_position": absolute_position, "coordinate_roots": list(normalized)}
        ),
    )
    stage = f"pass215-i14:append:{append_index}:terminal_output_projection:token:{absolute_position}"
    logits = _project_logits(dag, normalized, terminal_binding["output_projection"], stage=stage)
    logits_root = i4base.hash216(
        "pass215-i14-generated-logit-vector",
        i4base.canonical_bytes(
            {"absolute_position": absolute_position, "logit_roots": list(logits)}
        ),
    )
    projection_work = {
        "row_transitions": VOCABULARY_SIZE,
        "logical_weight_products": VOCABULARY_SIZE * EMBEDDING_WIDTH,
        "logical_accumulation_additions": VOCABULARY_SIZE * (EMBEDDING_WIDTH - 1),
        "q8_block_scale_applications": VOCABULARY_SIZE * i13.Q8_BLOCKS_PER_ROW,
    }
    return {
        "normalized_coordinate_roots": normalized,
        "terminal_norm_root_hash216": norm_root,
        "logit_roots": logits,
        "logits_root_hash216": logits_root,
        "projection_transition_work": projection_work,
    }


def _sum_work(records: Sequence[Mapping[str, int]]) -> Mapping[str, int]:
    if not records:
        return {}
    keys = tuple(records[0])
    return {key: sum(int(record[key]) for record in records) for key in keys}


def build_autoregressive_continuation_evidence(
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
        raise Pass215Iteration14ValidationError("PASS215_I14_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration14ValidationError("PASS215_I14_AUTHENTICATED_MODEL_IDENTITY_MISMATCH")
    if prompt != CONTRACTED_PROMPT:
        raise Pass215Iteration14ValidationError("PASS215_I14_PROMPT_OUTSIDE_CONTRACT")

    frozen12 = i12.build_all_six_block_evidence(
        raw, filename=filename, source=source, prompt=prompt, expected_sha256=expected_sha256
    )
    i13._validate_frozen_iteration12_evidence(frozen12)
    prefix = i13._reconstruct_six_block_prefix(raw, prompt=prompt, frozen_evidence=frozen12)
    tokenizer = prefix["tokenizer"]
    if int(tokenizer["vocabulary_size"]) != VOCABULARY_SIZE:
        raise Pass215Iteration14ValidationError("PASS215_I14_VOCABULARY_CHANGED")
    bindings = {index: i11._bind_block_tensors(raw, index) for index in i12.BLOCK_INDEXES}
    terminal_binding = i13._bind_terminal_tensors(raw, VOCABULARY_SIZE)
    q8_control = i13._q8_semantic_control(terminal_binding)
    if q8_control["exact"] is not True:
        raise Pass215Iteration14ValidationError("PASS215_I14_Q8_SEMANTIC_CONTROL_FAILED")
    terminal = i13._execute_terminal_head(
        prefix["dag"], prefix["blocks"][5]["output_coordinate_roots"], terminal_binding
    )
    parent_control = _revalidate_iteration13_semantics(prefix, terminal_binding, q8_control, terminal)
    cache = _materialize_prefix_kv_cache(prefix["dag"], prefix, bindings)
    if any(len(cache[index]["k_rope"]) != PREFIX_SEQUENCE_LENGTH for index in i12.BLOCK_INDEXES):
        raise Pass215Iteration14ValidationError("PASS215_I14_PREFIX_CACHE_GEOMETRY_INVALID")

    norm_weights = i7._norm_values(terminal_binding["output_norm"])
    last_hidden = prefix["blocks"][5]["output_coordinate_roots"][-1]
    last_normalized = tuple(i7._exact_rmsnorm_dag(prefix["dag"], last_hidden, norm_weights))
    initial_logits = _project_logits(
        prefix["dag"],
        last_normalized,
        terminal_binding["output_projection"],
        stage=f"terminal_output_projection:token:{PREFIX_SEQUENCE_LENGTH - 1}",
    )
    expected_last_vector_root = terminal["logits_stage"]["token_records"][-1]["vector_root_hash216"]
    actual_last_vector_root = prefix["dag"].vector(
        initial_logits, f"terminal_output_logits:token:{PREFIX_SEQUENCE_LENGTH - 1}"
    )
    if actual_last_vector_root != expected_last_vector_root:
        raise Pass215Iteration14ValidationError("PASS215_I14_PARENT_FINAL_LOGIT_VECTOR_CHANGED")

    first_selection = _selection_policy(initial_logits)
    generated_ids = [int(first_selection["selected_token_id"])]
    generated_records: list[Mapping[str, Any]] = [
        {
            "generation_index": 0,
            "selected_from_absolute_position": PREFIX_SEQUENCE_LENGTH - 1,
            **first_selection,
            "token": str(tokenizer["tokens"][generated_ids[0]]),
        }
    ]
    append_records: list[Mapping[str, Any]] = []

    for append_index in range(PROCESSED_APPEND_COUNT):
        token_id = generated_ids[-1]
        absolute_position = PREFIX_SEQUENCE_LENGTH + append_index
        embedding = i9._extract_authenticated_embeddings(raw, tokenizer, (token_id,))
        hidden = tuple(
            prefix["dag"].q(numerator, denominator)
            for numerator, denominator in embedding["rows"][0]
        )
        block_records = []
        for block_index in i12.BLOCK_INDEXES:
            current = _execute_incremental_block(
                prefix["dag"],
                hidden,
                bindings[block_index],
                cache[block_index],
                block_index=block_index,
                absolute_position=absolute_position,
                append_index=append_index,
            )
            block_records.append(
                {key: value for key, value in current.items() if key != "output_coordinate_roots"}
            )
            hidden = current["output_coordinate_roots"]
        final_terminal = _terminal_generated_position(
            prefix["dag"],
            hidden,
            terminal_binding,
            absolute_position=absolute_position,
            append_index=append_index,
        )
        append_root = i4base.hash216(
            "pass215-i14-append-forward",
            i4base.canonical_bytes(
                {
                    "append_index": append_index,
                    "absolute_position": absolute_position,
                    "token_id": token_id,
                    "embedding_row_root_hash216": embedding["selected_tokens"][0][
                        "embedding_row_root_hash216"
                    ],
                    "block_forward_roots": [
                        record["block_forward_root_hash216"] for record in block_records
                    ],
                    "terminal_norm_root_hash216": final_terminal[
                        "terminal_norm_root_hash216"
                    ],
                    "logits_root_hash216": final_terminal["logits_root_hash216"],
                }
            ),
        )
        append_records.append(
            {
                "append_index": append_index,
                "absolute_position": absolute_position,
                "appended_token_id": token_id,
                "appended_token": str(tokenizer["tokens"][token_id]),
                "embedding_row_root_hash216": embedding["selected_tokens"][0][
                    "embedding_row_root_hash216"
                ],
                "block_records": block_records,
                "terminal_norm_root_hash216": final_terminal["terminal_norm_root_hash216"],
                "logits_root_hash216": final_terminal["logits_root_hash216"],
                "projection_transition_work": final_terminal["projection_transition_work"],
                "append_forward_root_hash216": append_root,
                "prefix_recomputed": False,
            }
        )
        if append_index == 0:
            next_selection = _selection_policy(final_terminal["logit_roots"])
            next_id = int(next_selection["selected_token_id"])
            generated_ids.append(next_id)
            generated_records.append(
                {
                    "generation_index": 1,
                    "selected_from_absolute_position": absolute_position,
                    **next_selection,
                    "token": str(tokenizer["tokens"][next_id]),
                }
            )

    if len(generated_ids) != GENERATED_TOKEN_COUNT or len(append_records) != PROCESSED_APPEND_COUNT:
        raise Pass215Iteration14ValidationError("PASS215_I14_GENERATION_LENGTH_INVALID")
    expected_cache_length = PREFIX_SEQUENCE_LENGTH + PROCESSED_APPEND_COUNT
    if any(len(cache[index]["k_rope"]) != expected_cache_length for index in i12.BLOCK_INDEXES):
        raise Pass215Iteration14ValidationError("PASS215_I14_FINAL_CACHE_LENGTH_INVALID")

    all_block_linear = [
        record["linear_transition_work"]
        for append in append_records
        for record in append["block_records"]
    ]
    all_attention = [
        record["attention_transition_work"]
        for append in append_records
        for record in append["block_records"]
    ]
    all_projection = [append["projection_transition_work"] for append in append_records]
    continuation_work = {
        "linear_transition_work": _sum_work(all_block_linear),
        "attention_transition_work": _sum_work(all_attention),
        "terminal_projection_work": _sum_work(all_projection),
        "prefix_hidden_rows_recomputed": 0,
        "prior_kv_token_rows_reused": sum(
            int(record["prior_kv_token_rows_reused"])
            for append in append_records
            for record in append["block_records"]
        ),
        "new_kv_token_rows_materialized": sum(
            int(record["new_kv_token_rows_materialized"])
            for append in append_records
            for record in append["block_records"]
        ),
    }
    continuation_payload = {
        "parent_full_model_forward_root_hash216": ITERATION13_FULL_MODEL_FORWARD_ROOT_HASH216,
        "selection_policy": SELECTION_POLICY,
        "generated_token_ids": generated_ids,
        "selection_roots": [record["selection_root_hash216"] for record in generated_records],
        "append_forward_roots": [record["append_forward_root_hash216"] for record in append_records],
        "final_cache_sequence_length": expected_cache_length,
        "continuation_work": continuation_work,
    }
    continuation_root = i4base.hash216(
        "pass215-i14-exact-autoregressive-continuation",
        i4base.canonical_bytes(continuation_payload),
    )
    dag_manifest = prefix["dag"].manifest()
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
            **_iteration13_bindings(),
            "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "source": source_record,
        "contracted_prefix": {
            "input_text": prompt,
            "token_ids": list(FROZEN_TOKEN_IDS),
            "sequence_length": PREFIX_SEQUENCE_LENGTH,
        },
        "iteration13_semantic_reexecution": parent_control,
        "selection_policy": {
            "name": SELECTION_POLICY,
            "semantics": SELECTION_SEMANTICS,
            "exact_total_order": True,
            "numeric_argmax_performed": False,
            "probabilistic_sampling_performed": False,
            "canonical_float_interpretation_performed": False,
        },
        "generated_continuation": {
            "generated_token_count": GENERATED_TOKEN_COUNT,
            "generated_token_ids": generated_ids,
            "generated_tokens": [str(tokenizer["tokens"][token_id]) for token_id in generated_ids],
            "selection_records": generated_records,
            "processed_append_count": PROCESSED_APPEND_COUNT,
            "append_records": append_records,
            "prefix_sequence_length": PREFIX_SEQUENCE_LENGTH,
            "final_cache_sequence_length": expected_cache_length,
            "prefix_recomputed_for_appends": False,
            "kv_cache_reused": True,
            "continuation_work": continuation_work,
            "continuation_root_hash216": continuation_root,
            "final_symbolic_dag": dag_manifest,
        },
        "claims": {
            "authenticated_iteration13_semantic_roots_inherited_unchanged": True,
            "exact_deterministic_symbolic_token_selection_executed": True,
            "autoregressive_continuation_executed": True,
            "multi_step_generated_continuation_executed": True,
            "prefix_state_reused_without_recomputation": True,
            "kv_cache_reused_across_appended_tokens": True,
            "generated_tokens_appended_and_processed": True,
            "numeric_logit_argmax_executed": False,
            "probabilistic_sampling_executed": False,
            "general_generation_claimed": False,
            "general_arbitrary_sequence_length_transformer_forward_executed": False,
            "numeric_transcendental_evaluation_performed": False,
            "approximate_transcendental_evaluation_performed": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
    }
    suite_payload = {
        "iteration13_full_model_forward_root_hash216": ITERATION13_FULL_MODEL_FORWARD_ROOT_HASH216,
        "selection_policy": SELECTION_POLICY,
        "generated_token_ids": generated_ids,
        "continuation_root_hash216": continuation_root,
        "final_symbolic_dag_root_hash216": dag_manifest["ordered_node_root_hash216"],
    }
    suite_root = i4base.hash216(
        "pass215-i14-autoregressive-continuation-suite", i4base.canonical_bytes(suite_payload)
    )
    evidence["autoregressive_continuation_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216(
        "pass215-i14-autoregressive-continuation-evidence", i4base.canonical_bytes(evidence)
    )
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION14_AUTOREGRESSIVE_CONTINUATION"},
        {
            "sequence": 14,
            "parent_hash72": ITERATION13_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "suite_root_hash216": suite_root,
            "continuation_root_hash216": continuation_root,
        },
    )
    _reject_floats(evidence)
    return evidence


def build_autoregressive_continuation_evidence_from_path(
    path: str | Path,
    *,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    target = Path(path)
    return build_autoregressive_continuation_evidence(
        target.read_bytes(),
        filename=target.name,
        source=source,
        prompt=prompt,
        expected_sha256=expected_sha256,
    )


def validate_autoregressive_continuation_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration14ValidationError("PASS215_I14_SCHEMA_OR_CONTRACT_INVALID")
    inherits = evidence.get("inherits")
    expected_inherits = {
        **_iteration13_bindings(),
        "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
        "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    }
    if inherits != expected_inherits:
        raise Pass215Iteration14ValidationError("PASS215_I14_INHERITANCE_INVALID")
    parent = evidence.get("iteration13_semantic_reexecution", {})
    if parent.get("exact") is not True:
        raise Pass215Iteration14ValidationError("PASS215_I14_PARENT_REEXECUTION_INVALID")
    continuation = evidence.get("generated_continuation", {})
    if continuation.get("generated_token_count") != GENERATED_TOKEN_COUNT:
        raise Pass215Iteration14ValidationError("PASS215_I14_GENERATED_TOKEN_COUNT_INVALID")
    if continuation.get("processed_append_count") != PROCESSED_APPEND_COUNT:
        raise Pass215Iteration14ValidationError("PASS215_I14_APPEND_COUNT_INVALID")
    if continuation.get("prefix_recomputed_for_appends") is not False:
        raise Pass215Iteration14ValidationError("PASS215_I14_PREFIX_RECOMPUTATION_BOUNDARY_INVALID")
    if continuation.get("kv_cache_reused") is not True:
        raise Pass215Iteration14ValidationError("PASS215_I14_KV_CACHE_REUSE_INVALID")
    selections = continuation.get("selection_records", [])
    if len(selections) != GENERATED_TOKEN_COUNT:
        raise Pass215Iteration14ValidationError("PASS215_I14_SELECTION_RECORD_COUNT_INVALID")
    for selection in selections:
        if selection.get("policy") != SELECTION_POLICY:
            raise Pass215Iteration14ValidationError("PASS215_I14_SELECTION_POLICY_CHANGED")
        if selection.get("numeric_argmax_performed") is not False:
            raise Pass215Iteration14ValidationError("PASS215_I14_NUMERIC_ARGMAX_BOUNDARY_CHANGED")
        if selection.get("probabilistic_sampling_performed") is not False:
            raise Pass215Iteration14ValidationError("PASS215_I14_SAMPLING_BOUNDARY_CHANGED")
        if not 0 <= int(selection["selected_token_id"]) < VOCABULARY_SIZE:
            raise Pass215Iteration14ValidationError("PASS215_I14_SELECTED_TOKEN_RANGE_INVALID")
    work = continuation.get("continuation_work", {})
    if work.get("prefix_hidden_rows_recomputed") != 0:
        raise Pass215Iteration14ValidationError("PASS215_I14_PREFIX_RECOMPUTE_WORK_NONZERO")
    if int(work.get("prior_kv_token_rows_reused", 0)) <= 0:
        raise Pass215Iteration14ValidationError("PASS215_I14_KV_REUSE_WORK_MISSING")
    claims = evidence.get("claims", {})
    required_true = (
        "authenticated_iteration13_semantic_roots_inherited_unchanged",
        "exact_deterministic_symbolic_token_selection_executed",
        "autoregressive_continuation_executed",
        "multi_step_generated_continuation_executed",
        "prefix_state_reused_without_recomputation",
        "kv_cache_reused_across_appended_tokens",
        "generated_tokens_appended_and_processed",
    )
    required_false = (
        "numeric_logit_argmax_executed",
        "probabilistic_sampling_executed",
        "general_generation_claimed",
        "general_arbitrary_sequence_length_transformer_forward_executed",
        "numeric_transcendental_evaluation_performed",
        "approximate_transcendental_evaluation_performed",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "runtime_mutation_authority_promoted",
        "canonical_mutation_authorized",
        "migration_active",
    )
    if not all(claims.get(key) is True for key in required_true):
        raise Pass215Iteration14ValidationError("PASS215_I14_REQUIRED_TRUE_CLAIM_INVALID")
    if not all(claims.get(key) is False for key in required_false):
        raise Pass215Iteration14ValidationError("PASS215_I14_REQUIRED_FALSE_CLAIM_INVALID")

    stripped = dict(evidence)
    receipt = stripped.pop("receipt_hash72", None)
    evidence_root = stripped.pop("evidence_root_hash216", None)
    suite_root = stripped.get("autoregressive_continuation_suite_root_hash216")
    expected_evidence_root = i4base.hash216(
        "pass215-i14-autoregressive-continuation-evidence", i4base.canonical_bytes(stripped)
    )
    if evidence_root != expected_evidence_root:
        raise Pass215Iteration14ValidationError("PASS215_I14_EVIDENCE_ROOT_INVALID")
    continuation_root = continuation["continuation_root_hash216"]
    expected_receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION14_AUTOREGRESSIVE_CONTINUATION"},
        {
            "sequence": 14,
            "parent_hash72": ITERATION13_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "suite_root_hash216": suite_root,
            "continuation_root_hash216": continuation_root,
        },
    )
    if receipt != expected_receipt:
        raise Pass215Iteration14ValidationError("PASS215_I14_RECEIPT_INVALID")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_autoregressive_continuation_evidence(left)
    validate_autoregressive_continuation_evidence(right)
    keys = (
        "autoregressive_continuation_suite_root_hash216",
        "evidence_root_hash216",
        "receipt_hash72",
    )
    for key in keys:
        if left[key] != right[key]:
            raise Pass215Iteration14ValidationError(f"PASS215_I14_REPLAY_MISMATCH:{key}")
    lc = left["generated_continuation"]
    rc = right["generated_continuation"]
    for key in (
        "generated_token_ids",
        "continuation_root_hash216",
        "final_symbolic_dag",
    ):
        if lc[key] != rc[key]:
            raise Pass215Iteration14ValidationError(f"PASS215_I14_REPLAY_CONTINUATION_MISMATCH:{key}")
    return {
        "schema": REPLAY_SCHEMA,
        "cross_process_replay": True,
        "semantic_exactness": True,
        "generated_token_ids": lc["generated_token_ids"],
        "continuation_root_hash216": lc["continuation_root_hash216"],
        "final_symbolic_dag_root_hash216": lc["final_symbolic_dag"]["ordered_node_root_hash216"],
        "suite_root_hash216": left["autoregressive_continuation_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }


__all__ = [
    "CONTRACT",
    "PASS_NUMBER",
    "ITERATION",
    "EVIDENCE_SCHEMA",
    "VALIDATION_SCHEMA",
    "REPLAY_SCHEMA",
    "REAL_MODEL_SHA256",
    "CONTRACTED_PROMPT",
    "FROZEN_TOKEN_IDS",
    "PREFIX_SEQUENCE_LENGTH",
    "EMBEDDING_WIDTH",
    "VOCABULARY_SIZE",
    "GENERATED_TOKEN_COUNT",
    "PROCESSED_APPEND_COUNT",
    "SELECTION_POLICY",
    "SELECTION_SEMANTICS",
    "Pass215Iteration14Error",
    "Pass215Iteration14ValidationError",
    "_selection_policy",
    "_incremental_attention_work",
    "build_autoregressive_continuation_evidence",
    "build_autoregressive_continuation_evidence_from_path",
    "validate_autoregressive_continuation_evidence",
    "compare_replay",
]
