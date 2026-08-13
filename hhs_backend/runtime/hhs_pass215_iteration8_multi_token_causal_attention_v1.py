"""Pass 215 Iteration 8 exact multi-token causal attention closure.

Extends the frozen Iteration 7 coordinate-forward benchmark to four exact
external hidden-state controls.  Authenticated ``blk.0`` is executed with
nonzero-position RoPE, causal cross-token QK attention, exact closed-form
softmax ratios, and the inherited exact RMSNorm/SiLU/Q4_0 transition substrate.

Benchmark authority only: no operational-runtime/canonical mutation, numeric
transcendental approximation, token-embedding execution, arbitrary-sequence
claim, dense-forward replacement, or full-model-forward claim is introduced.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v4 as i4
from hhs_backend.runtime import hhs_pass215_iteration5_exact_nonlinear_symbolic_v1 as i5
from hhs_backend.runtime import hhs_pass215_iteration6_authenticated_block_graph_v1 as i6
from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7

CONTRACT = "HHS-P215-I8-EXACT-MULTI-TOKEN-CAUSAL-ATTENTION-CLOSURE"
PASS_NUMBER = 215
ITERATION = 8
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_8_MULTI_TOKEN_CAUSAL_ATTENTION_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_8_MULTI_TOKEN_CAUSAL_ATTENTION_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_8_MULTI_TOKEN_CAUSAL_ATTENTION_REPLAY_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_8_MULTI_TOKEN_CAUSAL_ATTENTION_BENCHMARK"

ITERATION7_CLOSURE_HEAD = "5308b37a00232b5ddff058a6dbc048795c279ee8"
ITERATION7_CLOSURE_TREE = "956ac4ad178e179d602192d907362ad176624bd0"
ITERATION7_VALIDATED_SOURCE_HEAD = "ce85b690be00067d7457215b031806b9517be474"
ITERATION7_VALIDATED_SOURCE_TREE = "ded8a17efb4551d55951f05f9629a00ac0ecb557"
ITERATION7_STAGE_SUITE_ROOT_HASH216 = "7f38ddf3447fde09b3ce91e54198ae43ba0fbcc72738ea668657d2bcef1cb30b"
ITERATION7_FINAL_OUTPUT_ROOT_HASH216 = "268426ee9d97b92c0d43c651bfddb5c99a0a9d109b953b881782681d45719244"
ITERATION7_SYMBOLIC_DAG_ROOT_HASH216 = "5371aa51686d039f83ffb6f94fb297c29758c8f08db3e715c6d5abc62cb39b09"
ITERATION7_SUITE_ROOT_HASH216 = "61bc64a3dbb0dd9c44bceef66404c2c5c5d5b246a000f9c23c189f9179535b85"
ITERATION7_EVIDENCE_ROOT_HASH216 = "4b9951e2df79cf5685673b6558fbb5440cdf1b04dfe10989785fd5ac69166c33"
ITERATION7_RECEIPT_HASH72 = "XrToLi8/mSkOyEF)i0puagJI<S+fW*VWqcj1RK29baDI/8I0tepwo?O3IlaRt2eQZugltWff"
ITERATION7_ARTIFACT_SHA256 = "e1fa7281eae41c966356e899ab2e51e9f0012f5ef86c783203c42c5f818dbbf0"

REAL_MODEL_SHA256 = i7.REAL_MODEL_SHA256
SEQUENCE_LENGTH = 4
EMBEDDING_WIDTH = i7.EMBEDDING_WIDTH
FFN_WIDTH = i7.FFN_WIDTH
HEAD_COUNT = i7.HEAD_COUNT
HEAD_DIMENSION = i7.HEAD_DIMENSION
ROPE_THETA = (10_000, 1)
I8_SYMBOLIC_OPS = frozenset(set(i7.SYMBOLIC_OPS) | {"powq", "sin", "cos"})


class Pass215Iteration8Error(RuntimeError):
    pass


class Pass215Iteration8ValidationError(Pass215Iteration8Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration8ValidationError(f"PASS215_I8_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


class MultiTokenSymbolicDAG(i7.SymbolicDAG):
    """Iteration-8 hash-consed DAG with exact RoPE closed-form nodes."""

    def intern(self, op: str, inputs: Sequence[str] = (), attributes: Mapping[str, Any] | None = None, *, commutative: bool = False) -> str:
        if op not in I8_SYMBOLIC_OPS:
            raise Pass215Iteration8ValidationError(f"PASS215_I8_SYMBOLIC_OP_INVALID:{op}")
        attrs = dict(attributes or {})
        _reject_floats(attrs)
        normalized_inputs = tuple(sorted(str(x) for x in inputs)) if commutative else tuple(str(x) for x in inputs)
        canonical = {"op": op, "inputs": list(normalized_inputs), "attributes": attrs}
        root = i4base.hash216("pass215-i8-multi-token-symbolic-node", i4base.canonical_bytes(canonical))
        prior = self._nodes.get(root)
        if prior is not None:
            if prior != canonical:
                raise Pass215Iteration8ValidationError("PASS215_I8_SYMBOLIC_HASH_COLLISION")
            return root
        self._nodes[root] = canonical
        self._order.append(root)
        self._histogram[op] += 1
        return root

    def powq(self, base: str, numerator: int, denominator: int = 1) -> str:
        exponent = self.q(numerator, denominator)
        if exponent == self.q(0):
            return self.q(1)
        if exponent == self.q(1):
            return base
        return self.intern("powq", (base, exponent), {
            "semantic": "iteration5.exact_rational_power_closed_form",
            "numeric_transcendental_evaluation_performed": False,
        })

    def sin(self, value: str) -> str:
        if value == self.q(0):
            return self.q(0)
        return self.intern("sin", (value,), {
            "semantic": "iteration5.exact_sin_closed_form",
            "numeric_transcendental_evaluation_performed": False,
        })

    def cos(self, value: str) -> str:
        if value == self.q(0):
            return self.q(1)
        return self.intern("cos", (value,), {
            "semantic": "iteration5.exact_cos_closed_form",
            "numeric_transcendental_evaluation_performed": False,
        })

    def manifest(self) -> Mapping[str, Any]:
        return {
            "unique_node_count": len(self._nodes),
            "operator_histogram": {op: int(self._histogram.get(op, 0)) for op in sorted(I8_SYMBOLIC_OPS)},
            "ordered_node_root_hash216": i4base.hash216(
                "pass215-i8-multi-token-symbolic-dag-order",
                i4base.canonical_bytes(self._order),
            ),
            "hash_consistent_reuse": True,
            "recursive_tree_duplication_required": False,
            "numeric_transcendental_evaluation_performed": False,
        }


def _token_control_input(position: int) -> tuple[int, ...]:
    if not 0 <= position < SEQUENCE_LENGTH:
        raise Pass215Iteration8ValidationError("PASS215_I8_TOKEN_POSITION_INVALID")
    base = i4.deterministic_vector(EMBEDDING_WIDTH)
    return tuple(int(base[(index + position) % len(base)]) + position for index in range(len(base)))


def _token_manifest(dag: MultiTokenSymbolicDAG, stage: str, position: int, values: Sequence[str]) -> Mapping[str, Any]:
    vector = tuple(values)
    if not vector:
        raise Pass215Iteration8ValidationError(f"PASS215_I8_STAGE_VECTOR_EMPTY:{stage}:{position}")
    return {
        "position": position,
        "coordinate_count": len(vector),
        "vector_root_hash216": dag.vector(vector, f"{stage}:token:{position}"),
        "coordinate_suite_root_hash216": i4base.hash216(
            "pass215-i8-stage-token-coordinate-suite",
            i4base.canonical_bytes({"stage": stage, "position": position, "coordinate_roots": list(vector)}),
        ),
    }


def _stage_manifest(dag: MultiTokenSymbolicDAG, stage: str, tokens: Sequence[Sequence[str]]) -> Mapping[str, Any]:
    records = [_token_manifest(dag, stage, position, values) for position, values in enumerate(tokens)]
    return {
        "stage": stage,
        "sequence_length": len(records),
        "token_records": records,
        "stage_root_hash216": i4base.hash216(
            "pass215-i8-stage-token-suite",
            i4base.canonical_bytes({"stage": stage, "token_records": records}),
        ),
    }


def _rope_head(dag: MultiTokenSymbolicDAG, values: Sequence[str], *, position: int) -> tuple[str, ...]:
    if len(values) != HEAD_DIMENSION or HEAD_DIMENSION % 2:
        raise Pass215Iteration8ValidationError("PASS215_I8_ROPE_HEAD_GEOMETRY_INVALID")
    if position < 0:
        raise Pass215Iteration8ValidationError("PASS215_I8_ROPE_POSITION_INVALID")
    if position == 0:
        return tuple(values)
    theta = dag.q(*ROPE_THETA)
    output: list[str] = []
    for pair_index in range(HEAD_DIMENSION // 2):
        frequency = dag.powq(theta, -2 * pair_index, HEAD_DIMENSION)
        angle = dag.mul(dag.q(position), frequency)
        cosine = dag.cos(angle)
        sine = dag.sin(angle)
        left, right = values[2 * pair_index], values[2 * pair_index + 1]
        output.append(dag.add(dag.mul(left, cosine), dag.mul(dag.q(-1), right, sine)))
        output.append(dag.add(dag.mul(left, sine), dag.mul(right, cosine)))
    return tuple(output)


def _rope_token(dag: MultiTokenSymbolicDAG, values: Sequence[str], *, position: int) -> tuple[str, ...]:
    if len(values) != EMBEDDING_WIDTH:
        raise Pass215Iteration8ValidationError("PASS215_I8_ROPE_TOKEN_GEOMETRY_INVALID")
    output: list[str] = []
    for head in range(HEAD_COUNT):
        start = head * HEAD_DIMENSION
        output.extend(_rope_head(dag, values[start:start + HEAD_DIMENSION], position=position))
    return tuple(output)


def _exact_causal_softmax(dag: MultiTokenSymbolicDAG, scores: Sequence[str]) -> tuple[tuple[str, ...], Mapping[str, Any]]:
    if not scores:
        raise Pass215Iteration8ValidationError("PASS215_I8_SOFTMAX_EMPTY")
    if len(scores) == 1:
        one = dag.q(1)
        return (one,), {
            "context_length": 1,
            "anchor_root_hash216": scores[0],
            "numerator_roots": [one],
            "denominator_root_hash216": one,
            "normalization": "EXACT_SINGLETON_IDENTITY",
            "numeric_exponential_approximation_performed": False,
        }
    anchor = scores[0]
    numerators = [dag.q(1)]
    for score in scores[1:]:
        shifted = dag.add(score, dag.mul(dag.q(-1), anchor))
        numerators.append(dag.exp(shifted))
    denominator = dag.add(*numerators)
    inverse = dag.inv(denominator)
    probabilities = tuple(dag.mul(value, inverse) for value in numerators)
    return probabilities, {
        "context_length": len(scores),
        "anchor_root_hash216": anchor,
        "numerator_roots": list(numerators),
        "denominator_root_hash216": denominator,
        "normalization": "FIRST_SCORE_EXACT_SHIFT_THEN_EXP_RATIO",
        "numeric_exponential_approximation_performed": False,
    }


def _expected_causal_edges() -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (head, query, key)
        for query in range(SEQUENCE_LENGTH)
        for head in range(HEAD_COUNT)
        for key in range(query + 1)
    )


def _attention_work_geometry() -> Mapping[str, int]:
    contexts = SEQUENCE_LENGTH * (SEQUENCE_LENGTH + 1) // 2
    shifted = SEQUENCE_LENGTH * (SEQUENCE_LENGTH - 1) // 2
    edges = HEAD_COUNT * contexts
    return {
        "causal_qk_edges": edges,
        "qk_dot_logical_products": edges * HEAD_DIMENSION,
        "qk_dot_logical_additions": edges * (HEAD_DIMENSION - 1),
        "attention_scale_multiplications": edges,
        "softmax_shifted_exponentials": HEAD_COUNT * shifted,
        "softmax_denominator_logical_additions": HEAD_COUNT * shifted,
        "softmax_denominator_inverses": HEAD_COUNT * (SEQUENCE_LENGTH - 1),
        "softmax_probability_products": HEAD_COUNT * (contexts - 1),
        "weighted_value_logical_products": edges * HEAD_DIMENSION,
        "weighted_value_logical_additions": HEAD_COUNT * HEAD_DIMENSION * shifted,
        "rope_total_pair_slots_q_and_k": SEQUENCE_LENGTH * HEAD_COUNT * (HEAD_DIMENSION // 2) * 2,
        "rope_nonzero_position_pair_rotations_q_and_k": (SEQUENCE_LENGTH - 1) * HEAD_COUNT * (HEAD_DIMENSION // 2) * 2,
        "rope_position_zero_identity_pairs_q_and_k": HEAD_COUNT * (HEAD_DIMENSION // 2) * 2,
    }


def _iteration7_bindings() -> Mapping[str, Any]:
    if len(ITERATION7_RECEIPT_HASH72) != 72:
        raise Pass215Iteration8ValidationError("PASS215_I8_ITERATION7_RECEIPT_LENGTH_INVALID")
    return {
        "iteration7_closure_head": ITERATION7_CLOSURE_HEAD,
        "iteration7_closure_tree": ITERATION7_CLOSURE_TREE,
        "iteration7_validated_source_head": ITERATION7_VALIDATED_SOURCE_HEAD,
        "iteration7_validated_source_tree": ITERATION7_VALIDATED_SOURCE_TREE,
        "iteration7_stage_suite_root_hash216": ITERATION7_STAGE_SUITE_ROOT_HASH216,
        "iteration7_final_output_root_hash216": ITERATION7_FINAL_OUTPUT_ROOT_HASH216,
        "iteration7_symbolic_dag_root_hash216": ITERATION7_SYMBOLIC_DAG_ROOT_HASH216,
        "iteration7_suite_root_hash216": ITERATION7_SUITE_ROOT_HASH216,
        "iteration7_evidence_root_hash216": ITERATION7_EVIDENCE_ROOT_HASH216,
        "iteration7_receipt_hash72": ITERATION7_RECEIPT_HASH72,
        "iteration7_artifact_sha256": ITERATION7_ARTIFACT_SHA256,
    }


def _execute_multi_token_forward(raw: bytes, i6_evidence: Mapping[str, Any]) -> Mapping[str, Any]:
    dag = MultiTokenSymbolicDAG()
    stages: dict[str, Mapping[str, Any]] = {}
    linear_work = {"row_transitions": 0, "logical_weight_products": 0, "logical_accumulation_additions": 0}

    def record(stage: str, tokens: Sequence[Sequence[str]]) -> tuple[tuple[str, ...], ...]:
        normalized = tuple(tuple(values) for values in tokens)
        stages[stage] = _stage_manifest(dag, stage, normalized)
        return normalized

    hidden = record("hidden_state_input", tuple(
        tuple(dag.q(value) for value in _token_control_input(position))
        for position in range(SEQUENCE_LENGTH)
    ))
    bindings = i6_evidence["authenticated_block_tensor_bindings"]
    attn_weights = i7._norm_values(bindings["norm_tensors"][i6.NORM_TENSORS[0]])
    ffn_weights = i7._norm_values(bindings["norm_tensors"][i6.NORM_TENSORS[1]])
    linears = i7._compile_linears(raw)
    attn_norm = record("rmsnorm_attn", tuple(i7._exact_rmsnorm_dag(dag, values, attn_weights) for values in hidden))

    def linear(stage: str, tensor: str, tokens: Sequence[Sequence[str]]) -> tuple[tuple[str, ...], ...]:
        outputs = []
        for position, inputs in enumerate(tokens):
            values, work = i7._linear_symbolic(dag, linears[tensor], inputs, stage=f"{stage}:token:{position}")
            for key in linear_work:
                linear_work[key] += int(work[key])
            outputs.append(tuple(values))
        return record(stage, outputs)

    q_values = linear("linear_attn_q", "blk.0.attn_q.weight", attn_norm)
    k_values = linear("linear_attn_k", "blk.0.attn_k.weight", attn_norm)
    v_values = linear("linear_attn_v", "blk.0.attn_v.weight", attn_norm)
    q_rope = record("rope_q", tuple(_rope_token(dag, values, position=p) for p, values in enumerate(q_values)))
    k_rope = record("rope_k", tuple(_rope_token(dag, values, position=p) for p, values in enumerate(k_values)))

    score_tokens, scale_tokens, probability_tokens = [], [], []
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
            head_scores = []
            for key in range(query + 1):
                score = i7._dot(dag, q_rope[query][start:end], k_rope[key][start:end])
                head_scores.append(score)
                query_scores.append(score)
                causal_edges.append({"head": head, "query_position": query, "key_position": key})
            scaled = tuple(dag.mul(score, scale) for score in head_scores)
            probs, sm = _exact_causal_softmax(dag, scaled)
            by_query_head[(query, head)] = probs
            query_scaled.extend(scaled)
            query_probs.extend(probs)
            softmax_records.append({
                "head": head,
                "query_position": query,
                "causal_key_positions": list(range(query + 1)),
                **sm,
                "probability_roots": list(probs),
            })
        score_tokens.append(tuple(query_scores))
        scale_tokens.append(tuple(query_scaled))
        probability_tokens.append(tuple(query_probs))
    record("attention_qk_dot", score_tokens)
    record("attention_scale", scale_tokens)
    record("attention_softmax", probability_tokens)

    weighted_tokens = []
    for query in range(SEQUENCE_LENGTH):
        weighted: list[str] = []
        for head in range(HEAD_COUNT):
            start = head * HEAD_DIMENSION
            probs = by_query_head[(query, head)]
            for dimension in range(HEAD_DIMENSION):
                terms = tuple(dag.mul(probs[key], v_values[key][start + dimension]) for key in range(query + 1))
                weighted.append(dag.add(*terms))
        weighted_tokens.append(tuple(weighted))
    weighted = record("attention_weighted_value", weighted_tokens)
    concatenated = record("attention_concat", weighted)
    attn_output = linear("linear_attn_output", "blk.0.attn_output.weight", concatenated)
    post_attn = record("residual_attention", tuple(
        tuple(dag.add(left, right) for left, right in zip(hidden[p], attn_output[p]))
        for p in range(SEQUENCE_LENGTH)
    ))
    ffn_norm = record("rmsnorm_ffn", tuple(i7._exact_rmsnorm_dag(dag, values, ffn_weights) for values in post_attn))
    gate = linear("linear_ffn_gate", "blk.0.ffn_gate.weight", ffn_norm)
    activated = record("silu", tuple(tuple(i7._silu(dag, value) for value in values) for values in gate))
    up = linear("linear_ffn_up", "blk.0.ffn_up.weight", ffn_norm)
    gated = record("ffn_gate_product", tuple(
        tuple(dag.mul(left, right) for left, right in zip(activated[p], up[p]))
        for p in range(SEQUENCE_LENGTH)
    ))
    down = linear("linear_ffn_down", "blk.0.ffn_down.weight", gated)
    output = record("residual_ffn", tuple(
        tuple(dag.add(left, right) for left, right in zip(post_attn[p], down[p]))
        for p in range(SEQUENCE_LENGTH)
    ))

    if tuple(stages) != i6.GRAPH_OPS:
        raise Pass215Iteration8ValidationError("PASS215_I8_EXECUTED_STAGE_TOPOLOGY_INVALID")
    if any(len(values) != EMBEDDING_WIDTH for values in output):
        raise Pass215Iteration8ValidationError("PASS215_I8_FINAL_OUTPUT_GEOMETRY_INVALID")
    observed_edges = tuple((r["head"], r["query_position"], r["key_position"]) for r in causal_edges)
    if observed_edges != _expected_causal_edges():
        raise Pass215Iteration8ValidationError("PASS215_I8_CAUSAL_EDGE_SET_INVALID")
    zero_identity = q_rope[0] == q_values[0] and k_rope[0] == k_values[0]
    nonzero_changes = all(q_rope[p] != q_values[p] and k_rope[p] != k_values[p] for p in range(1, SEQUENCE_LENGTH))
    singleton_identity = all(by_query_head[(0, head)] == (dag.q(1),) for head in range(HEAD_COUNT))
    if not zero_identity or not nonzero_changes or not singleton_identity:
        raise Pass215Iteration8ValidationError("PASS215_I8_EXACT_ATTENTION_CONTROL_FAILED")

    expected_linear = {
        "row_transitions": 2976 * SEQUENCE_LENGTH,
        "logical_weight_products": 995328 * SEQUENCE_LENGTH,
        "logical_accumulation_additions": 992352 * SEQUENCE_LENGTH,
    }
    if linear_work != expected_linear:
        raise Pass215Iteration8ValidationError("PASS215_I8_LINEAR_WORK_GEOMETRY_INVALID")

    token_output_roots = [
        i4base.hash216("pass215-i8-final-token-coordinate-roots", i4base.canonical_bytes({"position": p, "roots": list(values)}))
        for p, values in enumerate(output)
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
        "executed_stage_suite_root_hash216": i4base.hash216("pass215-i8-executed-stage-suite", i4base.canonical_bytes(stages)),
        "causal_attention_root_hash216": i4base.hash216("pass215-i8-causal-attention-suite", i4base.canonical_bytes(attention_payload)),
        "final_output_token_roots": token_output_roots,
        "final_output_root_hash216": i4base.hash216("pass215-i8-final-output-token-suite", i4base.canonical_bytes(token_output_roots)),
        "final_output_token_count": len(output),
        "final_output_coordinate_count": sum(len(values) for values in output),
        "causal_edges": causal_edges,
        "softmax_records": softmax_records,
        "symbolic_dag": dag.manifest(),
        "linear_transition_work": linear_work,
        "attention_transition_work": _attention_work_geometry(),
        "rope_controls": {
            "position_zero_exact_identity": zero_identity,
            "all_nonzero_positions_change_q_and_k_roots": nonzero_changes,
            "positions": list(range(SEQUENCE_LENGTH)),
            "theta": {"numerator": ROPE_THETA[0], "denominator": ROPE_THETA[1]},
            "head_dimension": HEAD_DIMENSION,
        },
        "causal_controls": {
            "future_edges_materialized": False,
            "observed_edge_count": len(causal_edges),
            "expected_edge_count": len(_expected_causal_edges()),
            "edge_set_exact": observed_edges == _expected_causal_edges(),
            "singleton_softmax_exact_identity": singleton_identity,
            "softmax_denominators_use_causal_terms_only": all(
                r["context_length"] == r["query_position"] + 1
                and r["causal_key_positions"] == list(range(r["query_position"] + 1))
                for r in softmax_records
            ),
        },
        "linears": linears,
    }


def build_multi_token_attention_evidence(raw: bytes, *, filename: str, source: Mapping[str, Any], expected_sha256: str | None = None) -> Mapping[str, Any]:
    _reject_floats(source)
    actual_sha = sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration8ValidationError("PASS215_I8_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration8ValidationError("PASS215_I8_AUTHENTICATED_REAL_MODEL_IDENTITY_MISMATCH")

    i6_evidence = i6.build_block_graph_evidence(raw, filename=filename, source=source, expected_sha256=expected_sha256)
    i6.validate_block_graph_evidence(i6_evidence)
    if i6_evidence["block_graph"]["graph_root_hash216"] != i7.ITERATION6_BLOCK_GRAPH_ROOT_HASH216:
        raise Pass215Iteration8ValidationError("PASS215_I8_ITERATION6_GRAPH_ROOT_MISMATCH")
    execution = _execute_multi_token_forward(raw, i6_evidence)
    linears = execution.pop("linears")
    q4_control = i7._q4_row_semantic_control(linears["blk.0.attn_q.weight"])
    if not q4_control["exact"]:
        raise Pass215Iteration8ValidationError("PASS215_I8_Q4_ROW_SEMANTIC_CONTROL_FAILED")

    inherited = {
        **_iteration7_bindings(),
        "iteration6_block_graph_root_hash216": i7.ITERATION6_BLOCK_GRAPH_ROOT_HASH216,
        "iteration6_suite_root_hash216": i7.ITERATION6_SUITE_ROOT_HASH216,
        "iteration5_nonlinear_suite_root_hash216": i6.ITERATION5_NONLINEAR_SUITE_ROOT_HASH216,
        "iteration4_suite_output_root_hash216": i5.ITERATION4_SUITE_OUTPUT_ROOT_HASH216,
        "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
        "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    }
    source_record = {**dict(source), "filename": filename, "file_size_bytes": len(raw), "file_sha256": actual_sha, "expected_sha256_verified": expected_sha256 is None or actual_sha == expected_sha256}
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
        "inherits": inherited,
        "source": source_record,
        "forward_geometry": {
            "block": "blk.0",
            "sequence_length": SEQUENCE_LENGTH,
            "embedding_width": EMBEDDING_WIDTH,
            "ffn_width": FFN_WIDTH,
            "head_count": HEAD_COUNT,
            "head_dimension": HEAD_DIMENSION,
            "causal_attention": True,
            "token_input_surface": "deterministic_exact_external_hidden_state_controls",
            "token_embedding_lookup_executed": False,
            "executed_graph_node_count_per_token": len(i6.GRAPH_OPS),
        },
        "multi_token_coordinate_forward": execution,
        "exact_controls": {
            "q4_0_factored_row_matches_iteration4_exact_execution": q4_control,
            "iteration7_terminal_roots_bound": {"exact": True, **_iteration7_bindings()},
            "rope_position_zero_exact_identity": {"exact": execution["rope_controls"]["position_zero_exact_identity"], "position": 0},
            "rope_nonzero_positions_materialized": {"exact": execution["rope_controls"]["all_nonzero_positions_change_q_and_k_roots"], "positions": list(range(1, SEQUENCE_LENGTH))},
            "causal_edge_set_exact": {"exact": execution["causal_controls"]["edge_set_exact"], "future_edges_materialized": False, "edge_count": execution["causal_controls"]["observed_edge_count"]},
            "softmax_causal_denominators_exact": {"exact": execution["causal_controls"]["softmax_denominators_use_causal_terms_only"], "numeric_exponential_approximation_performed": False},
            "singleton_softmax_exact_identity": {"exact": execution["causal_controls"]["singleton_softmax_exact_identity"], "query_position": 0},
        },
        "claims": {
            "authenticated_iteration7_roots_inherited_unchanged": True,
            "contracted_sequence_length_four_blk0_forward_executed": True,
            "multi_token_symbolic_coordinate_forward_materialized": True,
            "nonzero_position_rope_executed_symbolically": True,
            "causal_attention_mask_enforced_by_edge_construction": True,
            "cross_token_qk_scores_materialized": True,
            "exact_causal_softmax_ratios_materialized": True,
            "all_four_terminal_token_coordinate_roots_materialized": True,
            "factored_q4_0_symbolic_row_transitions_executed": True,
            "exact_closed_form_nonlinear_transitions_executed": True,
            "general_arbitrary_sequence_length_transformer_forward_executed": False,
            "token_embedding_lookup_executed": False,
            "full_model_forward_executed": False,
            "numeric_transcendental_evaluation_performed": False,
            "approximate_transcendental_evaluation_performed": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "runtime_mutation_performed": False,
            "canonical_mutation_performed": False,
        },
    }
    roots = {
        "stage_suite_root_hash216": execution["executed_stage_suite_root_hash216"],
        "causal_attention_root_hash216": execution["causal_attention_root_hash216"],
        "final_output_root_hash216": execution["final_output_root_hash216"],
        "symbolic_dag_order_root_hash216": execution["symbolic_dag"]["ordered_node_root_hash216"],
    }
    suite_root = i4base.hash216("pass215-i8-multi-token-causal-attention-suite", i4base.canonical_bytes(roots))
    evidence["multi_token_attention_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216("pass215-i8-multi-token-causal-attention-evidence", i4base.canonical_bytes(evidence))
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION8_MULTI_TOKEN_CAUSAL_ATTENTION"},
        {"sequence": 8, "parent_hash72": ITERATION7_RECEIPT_HASH72, "evidence_root_hash216": evidence_root, "multi_token_attention_suite_root_hash216": suite_root},
    )
    _reject_floats(evidence)
    return evidence


def build_multi_token_attention_evidence_from_path(path: str | Path, *, source: Mapping[str, Any], expected_sha256: str | None = None) -> Mapping[str, Any]:
    target = Path(path)
    return build_multi_token_attention_evidence(target.read_bytes(), filename=target.name, source=source, expected_sha256=expected_sha256)


def validate_multi_token_attention_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT or evidence.get("iteration") != ITERATION:
        raise Pass215Iteration8ValidationError("PASS215_I8_EVIDENCE_IDENTITY_INVALID")
    authority = evidence.get("authority")
    if not isinstance(authority, Mapping) or authority.get("runtime_mutation_authority_promoted") is not False or authority.get("canonical_mutation_authorized") is not False or authority.get("migration_active") is not False or authority.get("no_float_canonical_authority") is not True:
        raise Pass215Iteration8ValidationError("PASS215_I8_FORBIDDEN_AUTHORITY_ESCALATION")
    required_inherited = {
        **_iteration7_bindings(),
        "iteration6_block_graph_root_hash216": i7.ITERATION6_BLOCK_GRAPH_ROOT_HASH216,
        "iteration6_suite_root_hash216": i7.ITERATION6_SUITE_ROOT_HASH216,
        "iteration5_nonlinear_suite_root_hash216": i6.ITERATION5_NONLINEAR_SUITE_ROOT_HASH216,
        "iteration4_suite_output_root_hash216": i5.ITERATION4_SUITE_OUTPUT_ROOT_HASH216,
        "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
        "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    }
    if evidence.get("inherits") != required_inherited:
        raise Pass215Iteration8ValidationError("PASS215_I8_INHERITED_ROOT_BINDING_INVALID")
    source = evidence.get("source")
    if not isinstance(source, Mapping) or source.get("file_sha256") != REAL_MODEL_SHA256:
        raise Pass215Iteration8ValidationError("PASS215_I8_SOURCE_BINDING_INVALID")
    geometry = evidence.get("forward_geometry")
    if not isinstance(geometry, Mapping) or geometry.get("sequence_length") != SEQUENCE_LENGTH or geometry.get("embedding_width") != EMBEDDING_WIDTH or geometry.get("head_count") != HEAD_COUNT or geometry.get("head_dimension") != HEAD_DIMENSION or geometry.get("causal_attention") is not True or geometry.get("token_embedding_lookup_executed") is not False:
        raise Pass215Iteration8ValidationError("PASS215_I8_GEOMETRY_INVALID")
    execution = evidence.get("multi_token_coordinate_forward")
    if not isinstance(execution, Mapping):
        raise Pass215Iteration8ValidationError("PASS215_I8_EXECUTION_MISSING")
    stages = execution.get("stage_records")
    if not isinstance(stages, Mapping) or tuple(stages) != i6.GRAPH_OPS:
        raise Pass215Iteration8ValidationError("PASS215_I8_STAGE_SET_INVALID")
    if any(not isinstance(stages[s], Mapping) or stages[s].get("sequence_length") != SEQUENCE_LENGTH for s in i6.GRAPH_OPS):
        raise Pass215Iteration8ValidationError("PASS215_I8_STAGE_SEQUENCE_INVALID")
    if execution.get("final_output_token_count") != SEQUENCE_LENGTH or execution.get("final_output_coordinate_count") != SEQUENCE_LENGTH * EMBEDDING_WIDTH:
        raise Pass215Iteration8ValidationError("PASS215_I8_FINAL_OUTPUT_COUNT_INVALID")
    roots = execution.get("final_output_token_roots")
    if not isinstance(roots, list) or len(roots) != SEQUENCE_LENGTH or not all(isinstance(x, str) and len(x) == 64 for x in roots):
        raise Pass215Iteration8ValidationError("PASS215_I8_FINAL_TOKEN_ROOTS_INVALID")
    expected_linear = {"row_transitions": 2976 * SEQUENCE_LENGTH, "logical_weight_products": 995328 * SEQUENCE_LENGTH, "logical_accumulation_additions": 992352 * SEQUENCE_LENGTH}
    if execution.get("linear_transition_work") != expected_linear or execution.get("attention_transition_work") != _attention_work_geometry():
        raise Pass215Iteration8ValidationError("PASS215_I8_WORK_GEOMETRY_INVALID")
    edges = execution.get("causal_edges")
    if not isinstance(edges, list):
        raise Pass215Iteration8ValidationError("PASS215_I8_CAUSAL_EDGES_MISSING")
    observed = tuple((r.get("head"), r.get("query_position"), r.get("key_position")) for r in edges if isinstance(r, Mapping))
    if observed != _expected_causal_edges() or any(k > q for _h, q, k in observed):
        raise Pass215Iteration8ValidationError("PASS215_I8_CAUSAL_EDGES_INVALID")
    softmax_records = execution.get("softmax_records")
    if not isinstance(softmax_records, list) or len(softmax_records) != SEQUENCE_LENGTH * HEAD_COUNT:
        raise Pass215Iteration8ValidationError("PASS215_I8_SOFTMAX_RECORD_SET_INVALID")
    for record in softmax_records:
        if not isinstance(record, Mapping):
            raise Pass215Iteration8ValidationError("PASS215_I8_SOFTMAX_RECORD_INVALID")
        position = int(record.get("query_position", -1))
        expected_keys = list(range(position + 1))
        if record.get("causal_key_positions") != expected_keys or record.get("context_length") != len(expected_keys) or len(record.get("probability_roots", [])) != len(expected_keys):
            raise Pass215Iteration8ValidationError("PASS215_I8_SOFTMAX_CAUSAL_DENOMINATOR_INVALID")
    controls = evidence.get("exact_controls")
    if not isinstance(controls, Mapping) or not all(isinstance(r, Mapping) and r.get("exact") is True for r in controls.values()):
        raise Pass215Iteration8ValidationError("PASS215_I8_EXACT_CONTROL_INVALID")
    claims = evidence.get("claims")
    if not isinstance(claims, Mapping):
        raise Pass215Iteration8ValidationError("PASS215_I8_CLAIMS_MISSING")
    for key in (
        "authenticated_iteration7_roots_inherited_unchanged", "contracted_sequence_length_four_blk0_forward_executed",
        "multi_token_symbolic_coordinate_forward_materialized", "nonzero_position_rope_executed_symbolically",
        "causal_attention_mask_enforced_by_edge_construction", "cross_token_qk_scores_materialized",
        "exact_causal_softmax_ratios_materialized", "all_four_terminal_token_coordinate_roots_materialized",
        "factored_q4_0_symbolic_row_transitions_executed", "exact_closed_form_nonlinear_transitions_executed",
    ):
        if claims.get(key) is not True:
            raise Pass215Iteration8ValidationError(f"PASS215_I8_REQUIRED_CLAIM_FALSE:{key}")
    for key in (
        "general_arbitrary_sequence_length_transformer_forward_executed", "token_embedding_lookup_executed",
        "full_model_forward_executed", "numeric_transcendental_evaluation_performed",
        "approximate_transcendental_evaluation_performed", "canonical_float_interpretation_performed",
        "dense_forward_replaced", "runtime_mutation_performed", "canonical_mutation_performed",
    ):
        if claims.get(key) is not False:
            raise Pass215Iteration8ValidationError(f"PASS215_I8_BOUNDARY_CLAIM_INVALID:{key}")
    without_root = dict(evidence)
    recorded_root = without_root.pop("evidence_root_hash216", None)
    recorded_receipt = without_root.pop("receipt_hash72", None)
    expected_root = i4base.hash216("pass215-i8-multi-token-causal-attention-evidence", i4base.canonical_bytes(without_root))
    if recorded_root != expected_root:
        raise Pass215Iteration8ValidationError("PASS215_I8_EVIDENCE_ROOT_MISMATCH")
    expected_receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION8_MULTI_TOKEN_CAUSAL_ATTENTION"},
        {"sequence": 8, "parent_hash72": ITERATION7_RECEIPT_HASH72, "evidence_root_hash216": expected_root, "multi_token_attention_suite_root_hash216": evidence["multi_token_attention_suite_root_hash216"]},
    )
    if recorded_receipt != expected_receipt:
        raise Pass215Iteration8ValidationError("PASS215_I8_RECEIPT_MISMATCH")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_multi_token_attention_evidence(left)
    validate_multi_token_attention_evidence(right)
    for key in ("multi_token_attention_suite_root_hash216", "evidence_root_hash216", "receipt_hash72"):
        if left.get(key) != right.get(key):
            raise Pass215Iteration8ValidationError("PASS215_I8_CROSS_PROCESS_REPLAY_MISMATCH")
    left_exec, right_exec = left["multi_token_coordinate_forward"], right["multi_token_coordinate_forward"]
    for key in ("executed_stage_suite_root_hash216", "causal_attention_root_hash216", "final_output_root_hash216"):
        if left_exec.get(key) != right_exec.get(key):
            raise Pass215Iteration8ValidationError(f"PASS215_I8_EXECUTION_REPLAY_MISMATCH:{key}")
    return {
        "schema": REPLAY_SCHEMA,
        "semantic_exactness": True,
        "cross_process_replay": True,
        "multi_token_attention_suite_root_hash216": left["multi_token_attention_suite_root_hash216"],
        "stage_suite_root_hash216": left_exec["executed_stage_suite_root_hash216"],
        "causal_attention_root_hash216": left_exec["causal_attention_root_hash216"],
        "final_output_root_hash216": left_exec["final_output_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }


__all__ = [
    "CONTRACT", "PASS_NUMBER", "ITERATION", "EVIDENCE_SCHEMA", "VALIDATION_SCHEMA", "REPLAY_SCHEMA",
    "ITERATION7_CLOSURE_HEAD", "ITERATION7_CLOSURE_TREE", "ITERATION7_STAGE_SUITE_ROOT_HASH216",
    "ITERATION7_FINAL_OUTPUT_ROOT_HASH216", "ITERATION7_SYMBOLIC_DAG_ROOT_HASH216", "ITERATION7_SUITE_ROOT_HASH216",
    "ITERATION7_EVIDENCE_ROOT_HASH216", "ITERATION7_RECEIPT_HASH72", "ITERATION7_ARTIFACT_SHA256",
    "REAL_MODEL_SHA256", "SEQUENCE_LENGTH", "EMBEDDING_WIDTH", "FFN_WIDTH", "HEAD_COUNT", "HEAD_DIMENSION",
    "I8_SYMBOLIC_OPS", "MultiTokenSymbolicDAG", "Pass215Iteration8Error", "Pass215Iteration8ValidationError",
    "build_multi_token_attention_evidence", "build_multi_token_attention_evidence_from_path",
    "validate_multi_token_attention_evidence", "compare_replay",
]
