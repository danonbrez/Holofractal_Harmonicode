"""Pass 215 Iteration 7 exact symbolic coordinate forward for authenticated blk.0.

Iteration 7 executes the frozen Iteration 6 sequence-length-one block graph as a
hash-addressed symbolic DAG. Q4_0 linear rows are represented as exact factored
transition generators bound to the authenticated source SHA and immutable
Iteration 4 descriptor. Nonlinear transitions remain exact closed-form symbolic
operations; no numerical transcendental approximation or Python float authority
is introduced.

This is benchmark authority only. It does not mutate the operational runtime,
promote canonical mutation authority, replace dense forward execution, or claim
a general multi-token/full-model transformer forward.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v4 as i4
from hhs_backend.runtime import hhs_pass215_iteration5_exact_nonlinear_symbolic_v1 as i5
from hhs_backend.runtime import hhs_pass215_iteration6_authenticated_block_graph_v1 as i6

CONTRACT = "HHS-P215-I7-EXACT-SYMBOLIC-COORDINATE-BLOCK-FORWARD"
PASS_NUMBER = 215
ITERATION = 7
CONTRACT_VERSION = "1.0.0-iteration7"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_7_SYMBOLIC_COORDINATE_FORWARD_BENCHMARK"
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_7_SYMBOLIC_COORDINATE_FORWARD_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_7_SYMBOLIC_COORDINATE_FORWARD_VALIDATION_V1"

ITERATION6_VALIDATED_HEAD = "684a06a54d6b1282fd549f97f99095724f4452cc"
ITERATION6_VALIDATED_TREE = "86b5e7e5e70de09fb5084b76a2f40cb1855352f9"
ITERATION6_BLOCK_GRAPH_ROOT_HASH216 = "ab4e9d2310936652fdeb049276e08bbc0b9e803787c91ef96713f49bfb1b7c06"
ITERATION6_SUITE_ROOT_HASH216 = "ea8c31224dca961ad9afdce8431509cb93f4d74a8209dd714664edc0881dc9b5"
ITERATION6_EVIDENCE_ROOT_HASH216 = "85e0a02a70db8330c808a771bf1fbf6084802074b48a4d1b6f990768e23f133a"
ITERATION6_RECEIPT_HASH72 = "D*7BmWaC!cnAcSZGhYBHad*pf!J/xZL2!8Wyto8hczrq32GAD98-n8W0>w/Hp4GGusIBKzZJ"
ITERATION6_ARTIFACT_SHA256 = "a20b7e75d506943f22bd3d14a5f3b3f92885a88132f978290e827ae4155f6495"

REAL_MODEL_SHA256 = i6.REAL_MODEL_SHA256
EMBEDDING_WIDTH = 288
FFN_WIDTH = 768
HEAD_DIMENSION = 48
HEAD_COUNT = 6
SEQUENCE_LENGTH = 1
RMS_EPSILON = (1, 100_000)

SYMBOLIC_OPS = frozenset({
    "q",
    "vector",
    "add",
    "mul",
    "inv",
    "rsqrt",
    "exp",
    "q4_0_linear_row",
    "dot",
})


class Pass215Iteration7Error(RuntimeError):
    pass


class Pass215Iteration7ValidationError(Pass215Iteration7Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration7ValidationError(f"PASS215_I7_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _normal_rational(numerator: int, denominator: int = 1) -> tuple[int, int]:
    return i5.q_pair(i5.q(int(numerator), int(denominator)))


def _rat_json(value: tuple[int, int]) -> Mapping[str, int]:
    n, d = _normal_rational(value[0], value[1])
    return {"numerator": n, "denominator": d}


class SymbolicDAG:
    """Hash-consed exact symbolic transition DAG.

    Nodes refer to dependency roots instead of recursively embedding prior trees.
    This preserves exact semantics while measuring generator/transition complexity
    rather than duplicated expanded expression size.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, Mapping[str, Any]] = {}
        self._order: list[str] = []
        self._histogram: Counter[str] = Counter()

    def intern(
        self,
        op: str,
        inputs: Sequence[str] = (),
        attributes: Mapping[str, Any] | None = None,
        *,
        commutative: bool = False,
    ) -> str:
        if op not in SYMBOLIC_OPS:
            raise Pass215Iteration7ValidationError(f"PASS215_I7_SYMBOLIC_OP_INVALID:{op}")
        attrs = dict(attributes or {})
        _reject_floats(attrs)
        normalized_inputs = tuple(sorted(str(value) for value in inputs)) if commutative else tuple(str(value) for value in inputs)
        canonical = {
            "op": op,
            "inputs": list(normalized_inputs),
            "attributes": attrs,
        }
        root = i4base.hash216(
            "pass215-i7-symbolic-coordinate-node",
            i4base.canonical_bytes(canonical),
        )
        prior = self._nodes.get(root)
        if prior is not None:
            if prior != canonical:
                raise Pass215Iteration7ValidationError("PASS215_I7_SYMBOLIC_HASH_COLLISION")
            return root
        self._nodes[root] = canonical
        self._order.append(root)
        self._histogram[op] += 1
        return root

    def q(self, numerator: int, denominator: int = 1) -> str:
        n, d = _normal_rational(numerator, denominator)
        return self.intern("q", attributes={"numerator": n, "denominator": d})

    def add(self, *inputs: str) -> str:
        if not inputs:
            return self.q(0)
        if len(inputs) == 1:
            return inputs[0]
        return self.intern("add", inputs, {"semantic": "exact_add"}, commutative=True)

    def mul(self, *inputs: str) -> str:
        if not inputs:
            return self.q(1)
        if len(inputs) == 1:
            return inputs[0]
        return self.intern("mul", inputs, {"semantic": "exact_mul"}, commutative=True)

    def inv(self, value: str) -> str:
        return self.intern("inv", (value,), {"semantic": "exact_inverse"})

    def rsqrt(self, value: str) -> str:
        return self.intern(
            "rsqrt",
            (value,),
            {
                "semantic": "iteration5.exact_rsqrt_closed_form",
                "numeric_transcendental_evaluation_performed": False,
            },
        )

    def exp(self, value: str) -> str:
        return self.intern(
            "exp",
            (value,),
            {
                "semantic": "iteration5.exact_exp_closed_form",
                "numeric_transcendental_evaluation_performed": False,
            },
        )

    def vector(self, values: Sequence[str], stage: str) -> str:
        if not values:
            raise Pass215Iteration7ValidationError(f"PASS215_I7_VECTOR_EMPTY:{stage}")
        return self.intern(
            "vector",
            tuple(values),
            {"stage": stage, "coordinate_count": len(values), "ordered": True},
        )

    def manifest(self) -> Mapping[str, Any]:
        ordered_root = i4base.hash216(
            "pass215-i7-symbolic-dag-order",
            i4base.canonical_bytes(self._order),
        )
        histogram = {op: int(self._histogram.get(op, 0)) for op in sorted(SYMBOLIC_OPS)}
        return {
            "unique_node_count": len(self._nodes),
            "operator_histogram": histogram,
            "ordered_node_root_hash216": ordered_root,
            "hash_consistent_reuse": True,
            "recursive_tree_duplication_required": False,
        }


def _vector_manifest(dag: SymbolicDAG, stage: str, values: Sequence[str]) -> Mapping[str, Any]:
    vector_root = dag.vector(values, stage)
    return {
        "stage": stage,
        "coordinate_count": len(values),
        "vector_root_hash216": vector_root,
        "coordinate_suite_root_hash216": i4base.hash216(
            "pass215-i7-stage-coordinate-suite",
            i4base.canonical_bytes({"stage": stage, "coordinate_roots": list(values)}),
        ),
    }


def _norm_values(binding: Mapping[str, Any]) -> tuple[tuple[int, int], ...]:
    values = binding.get("values")
    if not isinstance(values, list) or not values:
        raise Pass215Iteration7ValidationError("PASS215_I7_NORM_VALUES_MISSING")
    output: list[tuple[int, int]] = []
    for record in values:
        if not isinstance(record, Mapping):
            raise Pass215Iteration7ValidationError("PASS215_I7_NORM_VALUE_INVALID")
        output.append(_normal_rational(int(record["numerator"]), int(record["denominator"])))
    return tuple(output)


def _exact_rmsnorm_dag(
    dag: SymbolicDAG,
    values: Sequence[str],
    weights: Sequence[tuple[int, int]],
) -> tuple[str, ...]:
    if not values or len(values) != len(weights):
        raise Pass215Iteration7ValidationError("PASS215_I7_RMSNORM_GEOMETRY_INVALID")
    squares = tuple(dag.mul(value, value) for value in values)
    sum_square = dag.add(*squares)
    mean_square = dag.mul(sum_square, dag.q(1, len(values)))
    radicand = dag.add(mean_square, dag.q(*RMS_EPSILON))
    normalization = dag.rsqrt(radicand)
    output = []
    for value, weight in zip(values, weights):
        output.append(dag.mul(value, dag.q(weight[0], weight[1]), normalization))
    return tuple(output)


def _compile_linears(raw: bytes) -> Mapping[str, Any]:
    parsed = i4base.parse_gguf(raw)
    by_name = {tensor.name: tensor for tensor in parsed.tensors}
    compiled: dict[str, Any] = {}
    for name, shape in i4base.TARGET_OPERATORS.items():
        tensor = by_name.get(name)
        if tensor is None:
            raise Pass215Iteration7ValidationError(f"PASS215_I7_LINEAR_TENSOR_MISSING:{name}")
        payload = raw[tensor.data_offset : tensor.data_offset + tensor.data_size]
        descriptor, _record = i4.compile_q4_tensor(tensor, payload, shape)
        compiled[name] = descriptor
    return compiled


def _linear_symbolic(
    dag: SymbolicDAG,
    compiled: Any,
    inputs: Sequence[str],
    *,
    stage: str,
) -> tuple[tuple[str, ...], Mapping[str, int]]:
    if len(inputs) != compiled.ne0:
        raise Pass215Iteration7ValidationError(f"PASS215_I7_LINEAR_INPUT_GEOMETRY:{compiled.name}")
    input_vector_root = dag.vector(inputs, stage + ":input")
    outputs: list[str] = []
    for row_index in range(compiled.ne1):
        outputs.append(
            dag.intern(
                "q4_0_linear_row",
                (input_vector_root,),
                {
                    "stage": stage,
                    "tensor": compiled.name,
                    "row_index": row_index,
                    "input_width": compiled.ne0,
                    "descriptor_root_hash216": compiled.descriptor_root_hash216,
                    "source_sha256": compiled.source_sha256,
                    "semantic_form": "sum_j(exact_q4_weight[row,j]*input[j])",
                    "factored_generator": True,
                },
            )
        )
    return tuple(outputs), {
        "row_transitions": compiled.ne1,
        "logical_weight_products": compiled.ne0 * compiled.ne1,
        "logical_accumulation_additions": (compiled.ne0 - 1) * compiled.ne1,
    }


def _rational_linear_row(
    compiled: Any,
    row_index: int,
    inputs: Sequence[tuple[int, int]],
) -> tuple[int, int]:
    if not 0 <= row_index < compiled.ne1 or len(inputs) != compiled.ne0:
        raise Pass215Iteration7ValidationError("PASS215_I7_RATIONAL_ROW_GEOMETRY_INVALID")
    total = i5.q(0)
    row = compiled.rows[row_index]
    for block_index, block in enumerate(row):
        base = block_index * i4base.Q4_0_BLOCK_ELEMENTS
        scale = i5.q(block.scale_numerator, block.scale_denominator)
        for local_index, quant in enumerate(block.quant_integers):
            value = i5.q(inputs[base + local_index][0], inputs[base + local_index][1])
            total = i5.add(total, i5.mul(i5.q(int(quant)), scale, value))
    return i5.q_pair(total)


def _q4_row_semantic_control(compiled: Any) -> Mapping[str, Any]:
    integer_input = i4.deterministic_vector(compiled.ne0)
    exact_output, _work = i4.execute_factored(compiled, integer_input, descriptors_are_reused=True)
    rational_input = tuple((int(value), 1) for value in integer_input)
    selected_rows = (0, compiled.ne1 // 2, compiled.ne1 - 1)
    reconstructed = tuple(_rational_linear_row(compiled, index, rational_input) for index in selected_rows)
    expected = tuple(exact_output[index] for index in selected_rows)
    return {
        "exact": reconstructed == expected,
        "tensor": compiled.name,
        "selected_rows": list(selected_rows),
        "reconstructed": [_rat_json(value) for value in reconstructed],
        "expected": [_rat_json(value) for value in expected],
    }


def _dot(dag: SymbolicDAG, left: Sequence[str], right: Sequence[str]) -> str:
    if len(left) != len(right) or not left:
        raise Pass215Iteration7ValidationError("PASS215_I7_DOT_GEOMETRY_INVALID")
    products = tuple(dag.mul(l, r) for l, r in zip(left, right))
    return dag.intern(
        "dot",
        products,
        {"width": len(left), "semantic": "exact_sum_of_exact_products"},
    )


def _silu(dag: SymbolicDAG, value: str) -> str:
    negative = dag.mul(dag.q(-1), value)
    exponential = dag.exp(negative)
    denominator = dag.add(dag.q(1), exponential)
    sigmoid = dag.inv(denominator)
    return dag.mul(value, sigmoid)


def _execute_coordinate_forward(
    raw: bytes,
    i6_evidence: Mapping[str, Any],
) -> Mapping[str, Any]:
    dag = SymbolicDAG()
    stage_records: dict[str, Mapping[str, Any]] = {}
    linear_work = {"row_transitions": 0, "logical_weight_products": 0, "logical_accumulation_additions": 0}

    def record(stage: str, values: Sequence[str]) -> tuple[str, ...]:
        vector = tuple(values)
        stage_records[stage] = _vector_manifest(dag, stage, vector)
        return vector

    hidden = record(
        "hidden_state_input",
        tuple(dag.q(value) for value in i4.deterministic_vector(EMBEDDING_WIDTH)),
    )

    bindings = i6_evidence["authenticated_block_tensor_bindings"]
    attn_weights = _norm_values(bindings["norm_tensors"][i6.NORM_TENSORS[0]])
    ffn_weights = _norm_values(bindings["norm_tensors"][i6.NORM_TENSORS[1]])
    linears = _compile_linears(raw)

    attn_norm = record("rmsnorm_attn", _exact_rmsnorm_dag(dag, hidden, attn_weights))

    def linear(stage: str, tensor_name: str, inputs: Sequence[str]) -> tuple[str, ...]:
        values, work = _linear_symbolic(dag, linears[tensor_name], inputs, stage=stage)
        for key in linear_work:
            linear_work[key] += int(work[key])
        return record(stage, values)

    q_values = linear("linear_attn_q", "blk.0.attn_q.weight", attn_norm)
    k_values = linear("linear_attn_k", "blk.0.attn_k.weight", attn_norm)
    v_values = linear("linear_attn_v", "blk.0.attn_v.weight", attn_norm)

    # Iteration 6 contracts position zero; RoPE is therefore exact identity.
    q_rope = record("rope_q", q_values)
    k_rope = record("rope_k", k_values)

    scores: list[str] = []
    for head in range(HEAD_COUNT):
        start = head * HEAD_DIMENSION
        end = start + HEAD_DIMENSION
        scores.append(_dot(dag, q_rope[start:end], k_rope[start:end]))
    score_values = record("attention_qk_dot", scores)

    scale = dag.rsqrt(dag.q(HEAD_DIMENSION))
    scaled_values = record("attention_scale", tuple(dag.mul(score, scale) for score in score_values))

    # Sequence length one makes every per-head softmax exactly [1]. We still
    # materialize the stage root and upstream score/scale coordinates.
    probabilities = record("attention_softmax", tuple(dag.q(1) for _ in range(HEAD_COUNT)))
    if len(probabilities) != HEAD_COUNT or any(root != dag.q(1) for root in probabilities):
        raise Pass215Iteration7ValidationError("PASS215_I7_SINGLE_TOKEN_SOFTMAX_IDENTITY_FAILED")

    weighted = record("attention_weighted_value", v_values)
    concatenated = record("attention_concat", weighted)
    attn_output = linear("linear_attn_output", "blk.0.attn_output.weight", concatenated)
    post_attn = record(
        "residual_attention",
        tuple(dag.add(left, right) for left, right in zip(hidden, attn_output)),
    )

    ffn_norm = record("rmsnorm_ffn", _exact_rmsnorm_dag(dag, post_attn, ffn_weights))
    gate = linear("linear_ffn_gate", "blk.0.ffn_gate.weight", ffn_norm)
    activated = record("silu", tuple(_silu(dag, value) for value in gate))
    up = linear("linear_ffn_up", "blk.0.ffn_up.weight", ffn_norm)
    gated = record("ffn_gate_product", tuple(dag.mul(left, right) for left, right in zip(activated, up)))
    down = linear("linear_ffn_down", "blk.0.ffn_down.weight", gated)
    output = record(
        "residual_ffn",
        tuple(dag.add(left, right) for left, right in zip(post_attn, down)),
    )

    if tuple(stage_records) != i6.GRAPH_OPS:
        raise Pass215Iteration7ValidationError("PASS215_I7_EXECUTED_STAGE_TOPOLOGY_INVALID")
    if len(output) != EMBEDDING_WIDTH:
        raise Pass215Iteration7ValidationError("PASS215_I7_FINAL_OUTPUT_GEOMETRY_INVALID")

    stage_root = i4base.hash216(
        "pass215-i7-executed-stage-suite",
        i4base.canonical_bytes(stage_records),
    )
    output_root = i4base.hash216(
        "pass215-i7-final-output-coordinate-roots",
        i4base.canonical_bytes(list(output)),
    )
    return {
        "stage_records": stage_records,
        "executed_stage_suite_root_hash216": stage_root,
        "final_output_coordinate_roots": list(output),
        "final_output_root_hash216": output_root,
        "final_output_coordinate_count": len(output),
        "symbolic_dag": dag.manifest(),
        "linear_transition_work": linear_work,
        "linears": linears,
    }


def build_symbolic_forward_evidence(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    _reject_floats(source)
    actual_sha = sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration7ValidationError("PASS215_I7_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration7ValidationError("PASS215_I7_AUTHENTICATED_REAL_MODEL_IDENTITY_MISMATCH")

    i6_evidence = i6.build_block_graph_evidence(
        raw,
        filename=filename,
        source=source,
        expected_sha256=expected_sha256,
    )
    i6.validate_block_graph_evidence(i6_evidence)
    if i6_evidence["block_graph"]["graph_root_hash216"] != ITERATION6_BLOCK_GRAPH_ROOT_HASH216:
        raise Pass215Iteration7ValidationError("PASS215_I7_ITERATION6_GRAPH_ROOT_MISMATCH")
    if i6_evidence["block_graph_suite_root_hash216"] != ITERATION6_SUITE_ROOT_HASH216:
        raise Pass215Iteration7ValidationError("PASS215_I7_ITERATION6_SUITE_ROOT_MISMATCH")
    if i6_evidence["evidence_root_hash216"] != ITERATION6_EVIDENCE_ROOT_HASH216:
        raise Pass215Iteration7ValidationError("PASS215_I7_ITERATION6_EVIDENCE_ROOT_MISMATCH")
    if i6_evidence["receipt_hash72"] != ITERATION6_RECEIPT_HASH72:
        raise Pass215Iteration7ValidationError("PASS215_I7_ITERATION6_RECEIPT_MISMATCH")

    execution = _execute_coordinate_forward(raw, i6_evidence)
    linears = execution.pop("linears")
    control = _q4_row_semantic_control(linears["blk.0.attn_q.weight"])
    if not control["exact"]:
        raise Pass215Iteration7ValidationError("PASS215_I7_Q4_ROW_SEMANTIC_CONTROL_FAILED")

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
            "iteration6_validated_head": ITERATION6_VALIDATED_HEAD,
            "iteration6_validated_tree": ITERATION6_VALIDATED_TREE,
            "iteration6_block_graph_root_hash216": ITERATION6_BLOCK_GRAPH_ROOT_HASH216,
            "iteration6_suite_root_hash216": ITERATION6_SUITE_ROOT_HASH216,
            "iteration6_evidence_root_hash216": ITERATION6_EVIDENCE_ROOT_HASH216,
            "iteration6_receipt_hash72": ITERATION6_RECEIPT_HASH72,
            "iteration6_artifact_sha256": ITERATION6_ARTIFACT_SHA256,
            "iteration5_nonlinear_suite_root_hash216": i6.ITERATION5_NONLINEAR_SUITE_ROOT_HASH216,
            "iteration4_suite_output_root_hash216": i5.ITERATION4_SUITE_OUTPUT_ROOT_HASH216,
            "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "source": source_record,
        "forward_geometry": {
            "block": "blk.0",
            "sequence_length": SEQUENCE_LENGTH,
            "embedding_width": EMBEDDING_WIDTH,
            "ffn_width": FFN_WIDTH,
            "head_count": HEAD_COUNT,
            "head_dimension": HEAD_DIMENSION,
            "executed_graph_node_count": len(i6.GRAPH_OPS),
        },
        "symbolic_coordinate_forward": execution,
        "exact_controls": {
            "q4_0_factored_row_matches_iteration4_exact_execution": control,
            "rope_position_zero_exact_identity": {"exact": True, "position": 0},
            "single_token_softmax_exact_identity": {"exact": True, "sequence_length": 1},
            "iteration6_graph_root_bound": {"exact": True, "root_hash216": ITERATION6_BLOCK_GRAPH_ROOT_HASH216},
        },
        "claims": {
            "authenticated_iteration6_block_graph_inherited_unchanged": True,
            "coordinate_level_complete_block_forward_executed": True,
            "symbolic_coordinate_forward_materialized": True,
            "complete_sequence_length_one_blk0_forward_executed": True,
            "final_288_coordinate_roots_materialized": True,
            "factored_q4_0_symbolic_row_transitions_executed": True,
            "exact_closed_form_nonlinear_transitions_executed": True,
            "general_multi_token_transformer_layer_forward_executed": False,
            "full_transformer_layer_forward_executed": False,
            "full_model_forward_executed": False,
            "numeric_transcendental_evaluation_performed": False,
            "approximate_transcendental_evaluation_performed": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "runtime_mutation_performed": False,
            "canonical_mutation_performed": False,
        },
    }
    execution_roots = {
        "stage_suite_root_hash216": execution["executed_stage_suite_root_hash216"],
        "final_output_root_hash216": execution["final_output_root_hash216"],
        "symbolic_dag_order_root_hash216": execution["symbolic_dag"]["ordered_node_root_hash216"],
    }
    suite_root = i4base.hash216(
        "pass215-i7-symbolic-coordinate-forward-suite",
        i4base.canonical_bytes(execution_roots),
    )
    evidence["symbolic_forward_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216(
        "pass215-i7-symbolic-coordinate-forward-evidence",
        i4base.canonical_bytes(evidence),
    )
    receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION7_SYMBOLIC_COORDINATE_FORWARD"},
        {
            "sequence": 7,
            "parent_hash72": ITERATION6_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "symbolic_forward_suite_root_hash216": suite_root,
        },
    )
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = receipt
    _reject_floats(evidence)
    return evidence


def build_symbolic_forward_evidence_from_path(
    path: str | Path,
    *,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    target = Path(path)
    return build_symbolic_forward_evidence(
        target.read_bytes(),
        filename=target.name,
        source=source,
        expected_sha256=expected_sha256,
    )


def validate_symbolic_forward_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration7ValidationError("PASS215_I7_EVIDENCE_IDENTITY_INVALID")
    required_inherits = {
        "iteration6_validated_head": ITERATION6_VALIDATED_HEAD,
        "iteration6_validated_tree": ITERATION6_VALIDATED_TREE,
        "iteration6_block_graph_root_hash216": ITERATION6_BLOCK_GRAPH_ROOT_HASH216,
        "iteration6_suite_root_hash216": ITERATION6_SUITE_ROOT_HASH216,
        "iteration6_evidence_root_hash216": ITERATION6_EVIDENCE_ROOT_HASH216,
        "iteration6_receipt_hash72": ITERATION6_RECEIPT_HASH72,
        "iteration6_artifact_sha256": ITERATION6_ARTIFACT_SHA256,
        "iteration5_nonlinear_suite_root_hash216": i6.ITERATION5_NONLINEAR_SUITE_ROOT_HASH216,
        "iteration4_suite_output_root_hash216": i5.ITERATION4_SUITE_OUTPUT_ROOT_HASH216,
        "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
        "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    }
    if evidence.get("inherits") != required_inherits:
        raise Pass215Iteration7ValidationError("PASS215_I7_INHERITED_ROOT_BINDING_INVALID")
    authority = evidence.get("authority")
    if not isinstance(authority, Mapping):
        raise Pass215Iteration7ValidationError("PASS215_I7_AUTHORITY_MISSING")
    if authority.get("runtime_mutation_authority_promoted") is not False or authority.get("canonical_mutation_authorized") is not False or authority.get("migration_active") is not False:
        raise Pass215Iteration7ValidationError("PASS215_I7_FORBIDDEN_AUTHORITY_ESCALATION")
    source = evidence.get("source")
    if not isinstance(source, Mapping) or source.get("file_sha256") != REAL_MODEL_SHA256:
        raise Pass215Iteration7ValidationError("PASS215_I7_SOURCE_BINDING_INVALID")
    execution = evidence.get("symbolic_coordinate_forward")
    if not isinstance(execution, Mapping):
        raise Pass215Iteration7ValidationError("PASS215_I7_EXECUTION_MISSING")
    stages = execution.get("stage_records")
    if not isinstance(stages, Mapping) or tuple(stages) != i6.GRAPH_OPS:
        raise Pass215Iteration7ValidationError("PASS215_I7_STAGE_SET_INVALID")
    if execution.get("final_output_coordinate_count") != EMBEDDING_WIDTH:
        raise Pass215Iteration7ValidationError("PASS215_I7_FINAL_OUTPUT_COUNT_INVALID")
    roots = execution.get("final_output_coordinate_roots")
    if not isinstance(roots, list) or len(roots) != EMBEDDING_WIDTH or not all(isinstance(value, str) and len(value) == 64 for value in roots):
        raise Pass215Iteration7ValidationError("PASS215_I7_FINAL_OUTPUT_ROOTS_INVALID")
    work = execution.get("linear_transition_work")
    if not isinstance(work, Mapping):
        raise Pass215Iteration7ValidationError("PASS215_I7_LINEAR_WORK_MISSING")
    if int(work.get("row_transitions", -1)) != 2976:
        raise Pass215Iteration7ValidationError("PASS215_I7_LINEAR_ROW_TRANSITION_COUNT_INVALID")
    if int(work.get("logical_weight_products", -1)) != 995328:
        raise Pass215Iteration7ValidationError("PASS215_I7_LOGICAL_WEIGHT_PRODUCT_COUNT_INVALID")
    if int(work.get("logical_accumulation_additions", -1)) != 992352:
        raise Pass215Iteration7ValidationError("PASS215_I7_LOGICAL_ACCUMULATION_COUNT_INVALID")
    claims = evidence.get("claims")
    if not isinstance(claims, Mapping):
        raise Pass215Iteration7ValidationError("PASS215_I7_CLAIMS_MISSING")
    for key in (
        "authenticated_iteration6_block_graph_inherited_unchanged",
        "coordinate_level_complete_block_forward_executed",
        "symbolic_coordinate_forward_materialized",
        "complete_sequence_length_one_blk0_forward_executed",
        "final_288_coordinate_roots_materialized",
        "factored_q4_0_symbolic_row_transitions_executed",
        "exact_closed_form_nonlinear_transitions_executed",
    ):
        if claims.get(key) is not True:
            raise Pass215Iteration7ValidationError(f"PASS215_I7_REQUIRED_CLAIM_FALSE:{key}")
    for key in (
        "general_multi_token_transformer_layer_forward_executed",
        "full_transformer_layer_forward_executed",
        "full_model_forward_executed",
        "numeric_transcendental_evaluation_performed",
        "approximate_transcendental_evaluation_performed",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "runtime_mutation_performed",
        "canonical_mutation_performed",
    ):
        if claims.get(key) is not False:
            raise Pass215Iteration7ValidationError(f"PASS215_I7_BOUNDARY_CLAIM_INVALID:{key}")
    controls = evidence.get("exact_controls")
    if not isinstance(controls, Mapping) or not all(isinstance(record, Mapping) and record.get("exact") is True for record in controls.values()):
        raise Pass215Iteration7ValidationError("PASS215_I7_EXACT_CONTROL_INVALID")

    without_root = dict(evidence)
    recorded_root = without_root.pop("evidence_root_hash216", None)
    recorded_receipt = without_root.pop("receipt_hash72", None)
    expected_root = i4base.hash216(
        "pass215-i7-symbolic-coordinate-forward-evidence",
        i4base.canonical_bytes(without_root),
    )
    if recorded_root != expected_root:
        raise Pass215Iteration7ValidationError("PASS215_I7_EVIDENCE_ROOT_MISMATCH")
    expected_receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION7_SYMBOLIC_COORDINATE_FORWARD"},
        {
            "sequence": 7,
            "parent_hash72": ITERATION6_RECEIPT_HASH72,
            "evidence_root_hash216": expected_root,
            "symbolic_forward_suite_root_hash216": evidence["symbolic_forward_suite_root_hash216"],
        },
    )
    if recorded_receipt != expected_receipt:
        raise Pass215Iteration7ValidationError("PASS215_I7_RECEIPT_MISMATCH")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_symbolic_forward_evidence(left)
    validate_symbolic_forward_evidence(right)
    keys = (
        "symbolic_forward_suite_root_hash216",
        "evidence_root_hash216",
        "receipt_hash72",
    )
    if any(left.get(key) != right.get(key) for key in keys):
        raise Pass215Iteration7ValidationError("PASS215_I7_CROSS_PROCESS_REPLAY_MISMATCH")
    left_execution = left["symbolic_coordinate_forward"]
    right_execution = right["symbolic_coordinate_forward"]
    if left_execution.get("final_output_root_hash216") != right_execution.get("final_output_root_hash216"):
        raise Pass215Iteration7ValidationError("PASS215_I7_OUTPUT_REPLAY_MISMATCH")
    return {
        "schema": "HHS_PASS_215_ITERATION_7_SYMBOLIC_COORDINATE_FORWARD_REPLAY_V1",
        "semantic_exactness": True,
        "cross_process_replay": True,
        "symbolic_forward_suite_root_hash216": left["symbolic_forward_suite_root_hash216"],
        "final_output_root_hash216": left_execution["final_output_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }


__all__ = [
    "CONTRACT",
    "PASS_NUMBER",
    "ITERATION",
    "EVIDENCE_SCHEMA",
    "VALIDATION_SCHEMA",
    "ITERATION6_VALIDATED_HEAD",
    "ITERATION6_VALIDATED_TREE",
    "ITERATION6_BLOCK_GRAPH_ROOT_HASH216",
    "ITERATION6_SUITE_ROOT_HASH216",
    "ITERATION6_EVIDENCE_ROOT_HASH216",
    "ITERATION6_RECEIPT_HASH72",
    "ITERATION6_ARTIFACT_SHA256",
    "REAL_MODEL_SHA256",
    "SYMBOLIC_OPS",
    "SymbolicDAG",
    "Pass215Iteration7Error",
    "Pass215Iteration7ValidationError",
    "build_symbolic_forward_evidence",
    "build_symbolic_forward_evidence_from_path",
    "validate_symbolic_forward_evidence",
    "compare_replay",
]
