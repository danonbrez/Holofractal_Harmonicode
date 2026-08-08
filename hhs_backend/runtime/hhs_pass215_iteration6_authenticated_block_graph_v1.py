"""Pass 215 Iteration 6 authenticated transformer-block symbolic graph.

This layer binds the complete dependency graph of authenticated ``blk.0`` to the
frozen Iteration 5 nonlinear algebra and Iteration 4 Q4_0 descriptors. IEEE norm
weights are decoded to exact rationals from storage bits without Python float
interpretation.

Iteration 6 composes and authenticates the complete block graph. It deliberately
does not claim coordinate-level evaluation of the complete block, numerical
transcendental approximation, dense-forward replacement, or runtime mutation.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v4 as i4
from hhs_backend.runtime import hhs_pass215_iteration5_exact_nonlinear_symbolic_v1 as i5

CONTRACT = "HHS-P215-I6-AUTHENTICATED-TRANSFORMER-BLOCK-SYMBOLIC-GRAPH"
PASS_NUMBER = 215
ITERATION = 6
CONTRACT_VERSION = "1.0.0-iteration6"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_6_AUTHENTICATED_BLOCK_GRAPH_BENCHMARK"
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_6_AUTHENTICATED_BLOCK_GRAPH_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_6_AUTHENTICATED_BLOCK_GRAPH_VALIDATION_V1"

ITERATION5_VALIDATED_HEAD = "e384058b1dedbcf7e67ca6bfc9d5c3c8531be58b"
ITERATION5_VALIDATED_TREE = "45674a23be7b7994b153a53454aec38104fb12df"
ITERATION5_NONLINEAR_SUITE_ROOT_HASH216 = "26c5ac1697094d1680dbdd829fe1c2492746bf9dbad41a389aa6d1bfed3184cc"
ITERATION5_EVIDENCE_ROOT_HASH216 = "f2e5c94e053e14e8060f6bf3da15ebb9b50d3059f7834205c3b776653bb41d00"
ITERATION5_RECEIPT_HASH72 = "Z9XYF<Nsxk/5uv7-wcggO4G-Fva6JNNrUsI6uy*p7lHnrz0A6DmuuzSsOjJXw1JvDZ2OA4K1"
ITERATION5_ARTIFACT_SHA256 = "746c66f63ebd78342aad270db0bcc1e5ce18f35b7d2440ccf9f359edd78c5939"

REAL_MODEL_SHA256 = i4.REAL_MODEL_SHA256
NORM_TENSORS = ("blk.0.attn_norm.weight", "blk.0.ffn_norm.weight")
LINEAR_TENSORS = tuple(i4base.TARGET_OPERATORS)
EXPECTED_BLOCK_TENSORS = NORM_TENSORS + LINEAR_TENSORS
ROPE_HEAD_DIMENSION = 48
ROPE_POSITION = 0

GRAPH_OPS = (
    "hidden_state_input",
    "rmsnorm_attn",
    "linear_attn_q",
    "linear_attn_k",
    "linear_attn_v",
    "rope_q",
    "rope_k",
    "attention_qk_dot",
    "attention_scale",
    "attention_softmax",
    "attention_weighted_value",
    "attention_concat",
    "linear_attn_output",
    "residual_attention",
    "rmsnorm_ffn",
    "linear_ffn_gate",
    "silu",
    "linear_ffn_up",
    "ffn_gate_product",
    "linear_ffn_down",
    "residual_ffn",
)


class Pass215Iteration6Error(RuntimeError):
    pass


class Pass215Iteration6ValidationError(Pass215Iteration6Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration6ValidationError(f"PASS215_I6_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _normal_rational(numerator: int, denominator: int) -> tuple[int, int]:
    expr = i5.q(int(numerator), int(denominator))
    return i5.q_pair(expr)


def _binary_rational(sign: int, significand: int, binary_exponent: int) -> tuple[int, int]:
    numerator = int(sign) * int(significand)
    denominator = 1
    if binary_exponent >= 0:
        numerator <<= binary_exponent
    else:
        denominator <<= -binary_exponent
    return _normal_rational(numerator, denominator)


def decode_binary32_exact(raw: bytes) -> tuple[int, int]:
    """Decode IEEE binary32 bytes to an exact rational with integer bit logic."""
    if len(raw) != 4:
        raise Pass215Iteration6ValidationError("PASS215_I6_BINARY32_LENGTH_INVALID")
    bits = int.from_bytes(raw, "little")
    sign = -1 if (bits >> 31) & 1 else 1
    exponent_field = (bits >> 23) & 0xFF
    fraction = bits & 0x7FFFFF
    if exponent_field == 0xFF:
        raise Pass215Iteration6ValidationError("PASS215_I6_BINARY32_NAN_OR_INFINITY")
    if exponent_field == 0:
        if fraction == 0:
            return (0, 1)
        significand = fraction
        binary_exponent = -149
    else:
        significand = (1 << 23) + fraction
        binary_exponent = exponent_field - 150
    return _binary_rational(sign, significand, binary_exponent)


def decode_bfloat16_exact(raw: bytes) -> tuple[int, int]:
    """Decode BF16 storage bits to an exact rational without float conversion."""
    if len(raw) != 2:
        raise Pass215Iteration6ValidationError("PASS215_I6_BFLOAT16_LENGTH_INVALID")
    bits = int.from_bytes(raw, "little")
    sign = -1 if (bits >> 15) & 1 else 1
    exponent_field = (bits >> 7) & 0xFF
    fraction = bits & 0x7F
    if exponent_field == 0xFF:
        raise Pass215Iteration6ValidationError("PASS215_I6_BFLOAT16_NAN_OR_INFINITY")
    if exponent_field == 0:
        if fraction == 0:
            return (0, 1)
        significand = fraction
        binary_exponent = -133
    else:
        significand = (1 << 7) + fraction
        binary_exponent = exponent_field - 134
    return _binary_rational(sign, significand, binary_exponent)


def _decode_scalar_payload(storage_type: str, payload: bytes) -> tuple[tuple[int, int], ...]:
    if storage_type == "F32":
        width = 4
        decoder = decode_binary32_exact
    elif storage_type == "F16":
        width = 2
        decoder = i4base.decode_binary16_exact
    elif storage_type == "BF16":
        width = 2
        decoder = decode_bfloat16_exact
    else:
        raise Pass215Iteration6ValidationError(
            f"PASS215_I6_NORM_STORAGE_UNSUPPORTED:{storage_type}"
        )
    if len(payload) % width:
        raise Pass215Iteration6ValidationError("PASS215_I6_NORM_PAYLOAD_GEOMETRY_INVALID")
    return tuple(decoder(payload[index : index + width]) for index in range(0, len(payload), width))


def _rational_json(value: tuple[int, int]) -> Mapping[str, int]:
    n, d = _normal_rational(value[0], value[1])
    return {"numerator": n, "denominator": d}


def _bind_norm_tensor(tensor: Any, payload: bytes, expected_width: int) -> Mapping[str, Any]:
    if tuple(tensor.shape) != (expected_width,):
        raise Pass215Iteration6ValidationError(
            f"PASS215_I6_NORM_GEOMETRY_MISMATCH:{tensor.name}:{tuple(tensor.shape)}"
        )
    values = _decode_scalar_payload(str(tensor.storage_type), payload)
    if len(values) != expected_width:
        raise Pass215Iteration6ValidationError(
            f"PASS215_I6_NORM_VALUE_COUNT_MISMATCH:{tensor.name}"
        )
    source_sha = sha256(payload).hexdigest()
    if source_sha != tensor.source_sha256:
        raise Pass215Iteration6ValidationError(
            f"PASS215_I6_NORM_SOURCE_SHA_MISMATCH:{tensor.name}"
        )
    value_payload = [_rational_json(value) for value in values]
    return {
        "name": tensor.name,
        "shape": [expected_width],
        "storage_type": tensor.storage_type,
        "source_sha256": source_sha,
        "source_bytes": len(payload),
        "value_count": len(values),
        "decoder": f"PASS215_I6_{tensor.storage_type}_IEEE_BITS_TO_EXACT_RATIONAL_V1",
        "canonical_value_root_hash216": i4base.hash216(
            "pass215-i6-exact-norm-values",
            i4base.canonical_bytes({"tensor": tensor.name, "values": value_payload}),
        ),
        "canonical_float_interpretation_performed": False,
        "values": value_payload,
    }


def _bind_linear_tensor(tensor: Any, payload: bytes) -> Mapping[str, Any]:
    expected_shape = i4base.TARGET_OPERATORS.get(tensor.name)
    if expected_shape is None:
        raise Pass215Iteration6ValidationError(
            f"PASS215_I6_LINEAR_TENSOR_NOT_CONTRACTED:{tensor.name}"
        )
    compiled, descriptor = i4.compile_q4_tensor(tensor, payload, expected_shape)
    return {
        "name": tensor.name,
        "shape": list(expected_shape),
        "storage_type": tensor.storage_type,
        "source_sha256": tensor.source_sha256,
        "source_bytes": tensor.data_size,
        "block_count": compiled.block_count,
        "descriptor_root_hash216": compiled.descriptor_root_hash216,
        "descriptor": descriptor,
        "coordinate_forward_executed": False,
    }


def _graph_node(op: str, inputs: Sequence[str], attributes: Mapping[str, Any]) -> Mapping[str, Any]:
    if op not in GRAPH_OPS:
        raise Pass215Iteration6ValidationError(f"PASS215_I6_GRAPH_OP_INVALID:{op}")
    _reject_floats(attributes)
    canonical = {
        "op": op,
        "inputs": list(inputs),
        "attributes": dict(attributes),
    }
    node_id = i4base.hash216("pass215-i6-block-graph-node", i4base.canonical_bytes(canonical))
    return {**canonical, "node_hash216": node_id}


def _compose_graph(
    *,
    embedding_width: int,
    ffn_width: int,
    norm_bindings: Mapping[str, Mapping[str, Any]],
    linear_bindings: Mapping[str, Mapping[str, Any]],
) -> Mapping[str, Any]:
    if embedding_width <= 0 or embedding_width % ROPE_HEAD_DIMENSION:
        raise Pass215Iteration6ValidationError("PASS215_I6_EMBEDDING_HEAD_GEOMETRY_INVALID")
    if ffn_width <= 0:
        raise Pass215Iteration6ValidationError("PASS215_I6_FFN_GEOMETRY_INVALID")
    head_count = embedding_width // ROPE_HEAD_DIMENSION
    nodes: list[Mapping[str, Any]] = []

    def append(op: str, inputs: Sequence[str], attributes: Mapping[str, Any]) -> str:
        node = _graph_node(op, inputs, attributes)
        nodes.append(node)
        return str(node["node_hash216"])

    deterministic_input = i4.deterministic_vector(embedding_width)
    hidden = append(
        "hidden_state_input",
        (),
        {
            "shape": [1, embedding_width],
            "domain": "external_exact_hidden_state",
            "deterministic_control_input_root_hash216": i4base.hash216(
                "pass215-i6-block-input-control", i4base.canonical_bytes(list(deterministic_input))
            ),
            "coordinate_values_materialized_for_graph_execution": False,
        },
    )
    attn_norm = append(
        "rmsnorm_attn",
        (hidden,),
        {
            "shape": [1, embedding_width],
            "weight_tensor": NORM_TENSORS[0],
            "weight_root_hash216": norm_bindings[NORM_TENSORS[0]]["canonical_value_root_hash216"],
            "epsilon": i5.expr_to_json(i5.q(1, 100_000)),
            "semantic_operator": "iteration5.exact_rmsnorm",
        },
    )
    q_node = append(
        "linear_attn_q",
        (attn_norm,),
        {
            "output_shape": [1, embedding_width],
            "tensor": "blk.0.attn_q.weight",
            "descriptor_root_hash216": linear_bindings["blk.0.attn_q.weight"]["descriptor_root_hash216"],
            "semantic_operator": "iteration4.q4_0_factored_exact_block_kernel",
        },
    )
    k_node = append(
        "linear_attn_k",
        (attn_norm,),
        {
            "output_shape": [1, embedding_width],
            "tensor": "blk.0.attn_k.weight",
            "descriptor_root_hash216": linear_bindings["blk.0.attn_k.weight"]["descriptor_root_hash216"],
            "semantic_operator": "iteration4.q4_0_factored_exact_block_kernel",
        },
    )
    v_node = append(
        "linear_attn_v",
        (attn_norm,),
        {
            "output_shape": [1, embedding_width],
            "tensor": "blk.0.attn_v.weight",
            "descriptor_root_hash216": linear_bindings["blk.0.attn_v.weight"]["descriptor_root_hash216"],
            "semantic_operator": "iteration4.q4_0_factored_exact_block_kernel",
        },
    )
    q_rope = append(
        "rope_q",
        (q_node,),
        {
            "shape": [1, head_count, ROPE_HEAD_DIMENSION],
            "position": ROPE_POSITION,
            "rotary_dimension": ROPE_HEAD_DIMENSION,
            "theta": i5.expr_to_json(i5.q(10_000)),
            "semantic_operator": "iteration5.exact_rope",
        },
    )
    k_rope = append(
        "rope_k",
        (k_node,),
        {
            "shape": [1, head_count, ROPE_HEAD_DIMENSION],
            "position": ROPE_POSITION,
            "rotary_dimension": ROPE_HEAD_DIMENSION,
            "theta": i5.expr_to_json(i5.q(10_000)),
            "semantic_operator": "iteration5.exact_rope",
        },
    )
    scores = append(
        "attention_qk_dot",
        (q_rope, k_rope),
        {
            "shape": [head_count, 1, 1],
            "head_dimension": ROPE_HEAD_DIMENSION,
            "semantic_operator": "exact_rational_symbolic_dot",
        },
    )
    scaled = append(
        "attention_scale",
        (scores,),
        {
            "shape": [head_count, 1, 1],
            "head_dimension": ROPE_HEAD_DIMENSION,
            "semantic_operator": "iteration5.exact_attention_scale",
        },
    )
    probabilities = append(
        "attention_softmax",
        (scaled,),
        {
            "shape": [head_count, 1, 1],
            "sequence_length": 1,
            "semantic_operator": "iteration5.exact_softmax",
            "single_token_exact_identity": True,
        },
    )
    weighted = append(
        "attention_weighted_value",
        (probabilities, v_node),
        {
            "shape": [1, head_count, ROPE_HEAD_DIMENSION],
            "semantic_operator": "exact_symbolic_weighted_sum",
        },
    )
    concatenated = append(
        "attention_concat",
        (weighted,),
        {
            "shape": [1, embedding_width],
            "head_count": head_count,
            "head_dimension": ROPE_HEAD_DIMENSION,
        },
    )
    attn_output = append(
        "linear_attn_output",
        (concatenated,),
        {
            "output_shape": [1, embedding_width],
            "tensor": "blk.0.attn_output.weight",
            "descriptor_root_hash216": linear_bindings["blk.0.attn_output.weight"]["descriptor_root_hash216"],
            "semantic_operator": "iteration4.q4_0_factored_exact_block_kernel",
        },
    )
    post_attn = append(
        "residual_attention",
        (hidden, attn_output),
        {
            "shape": [1, embedding_width],
            "semantic_operator": "exact_symbolic_add",
        },
    )
    ffn_norm = append(
        "rmsnorm_ffn",
        (post_attn,),
        {
            "shape": [1, embedding_width],
            "weight_tensor": NORM_TENSORS[1],
            "weight_root_hash216": norm_bindings[NORM_TENSORS[1]]["canonical_value_root_hash216"],
            "epsilon": i5.expr_to_json(i5.q(1, 100_000)),
            "semantic_operator": "iteration5.exact_rmsnorm",
        },
    )
    gate = append(
        "linear_ffn_gate",
        (ffn_norm,),
        {
            "output_shape": [1, ffn_width],
            "tensor": "blk.0.ffn_gate.weight",
            "descriptor_root_hash216": linear_bindings["blk.0.ffn_gate.weight"]["descriptor_root_hash216"],
            "semantic_operator": "iteration4.q4_0_factored_exact_block_kernel",
        },
    )
    activated = append(
        "silu",
        (gate,),
        {
            "shape": [1, ffn_width],
            "semantic_operator": "iteration5.exact_silu",
        },
    )
    up = append(
        "linear_ffn_up",
        (ffn_norm,),
        {
            "output_shape": [1, ffn_width],
            "tensor": "blk.0.ffn_up.weight",
            "descriptor_root_hash216": linear_bindings["blk.0.ffn_up.weight"]["descriptor_root_hash216"],
            "semantic_operator": "iteration4.q4_0_factored_exact_block_kernel",
        },
    )
    gated = append(
        "ffn_gate_product",
        (activated, up),
        {
            "shape": [1, ffn_width],
            "semantic_operator": "exact_symbolic_elementwise_mul",
        },
    )
    down = append(
        "linear_ffn_down",
        (gated,),
        {
            "output_shape": [1, embedding_width],
            "tensor": "blk.0.ffn_down.weight",
            "descriptor_root_hash216": linear_bindings["blk.0.ffn_down.weight"]["descriptor_root_hash216"],
            "semantic_operator": "iteration4.q4_0_factored_exact_block_kernel",
        },
    )
    output = append(
        "residual_ffn",
        (post_attn, down),
        {
            "shape": [1, embedding_width],
            "semantic_operator": "exact_symbolic_add",
        },
    )
    if tuple(node["op"] for node in nodes) != GRAPH_OPS:
        raise Pass215Iteration6ValidationError("PASS215_I6_GRAPH_TOPOLOGY_INVALID")
    graph_payload = {
        "nodes": nodes,
        "output_node_hash216": output,
        "embedding_width": embedding_width,
        "ffn_width": ffn_width,
        "head_count": head_count,
        "head_dimension": ROPE_HEAD_DIMENSION,
        "sequence_length": 1,
    }
    graph_root = i4base.hash216(
        "pass215-i6-authenticated-block-graph", i4base.canonical_bytes(graph_payload)
    )
    return {**graph_payload, "graph_root_hash216": graph_root}


def _exact_controls() -> Mapping[str, Any]:
    one = i5.q(1)
    rope_input = (i5.q(3), i5.q(-4), i5.q(5), i5.q(6))
    rope_output, _ = i5.exact_rope(rope_input, position=0, rotary_dimension=4)
    softmax_output, _ = i5.exact_softmax((i5.q(17, 5),))
    return {
        "binary32_one_exact": {
            "exact": decode_binary32_exact(bytes.fromhex("0000803f")) == (1, 1),
            "value": _rational_json(decode_binary32_exact(bytes.fromhex("0000803f"))),
        },
        "binary32_negative_two_exact": {
            "exact": decode_binary32_exact(bytes.fromhex("000000c0")) == (-2, 1),
            "value": _rational_json(decode_binary32_exact(bytes.fromhex("000000c0"))),
        },
        "rope_position_zero_identity": {
            "exact": rope_output == rope_input,
            "root_hash216": i5.expr_root("pass215-i6-rope-zero-control", rope_output),
        },
        "single_token_softmax_identity": {
            "exact": softmax_output == (one,),
            "output": [i5.expr_to_json(value) for value in softmax_output],
        },
        "iteration5_receipt_bound": {
            "exact": len(ITERATION5_RECEIPT_HASH72) == 72,
            "receipt_hash72": ITERATION5_RECEIPT_HASH72,
        },
    }


def build_block_graph_evidence(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    _reject_floats(source)
    actual_sha = sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration6ValidationError("PASS215_I6_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration6ValidationError("PASS215_I6_AUTHENTICATED_REAL_MODEL_IDENTITY_MISMATCH")

    parsed = i4base.parse_gguf(raw)
    by_name = {tensor.name: tensor for tensor in parsed.tensors}
    missing = [name for name in EXPECTED_BLOCK_TENSORS if name not in by_name]
    if missing:
        raise Pass215Iteration6ValidationError(
            "PASS215_I6_REQUIRED_BLOCK_TENSOR_MISSING:" + ",".join(missing)
        )

    embedding_width = i4base.TARGET_OPERATORS["blk.0.attn_q.weight"][0]
    ffn_width = i4base.TARGET_OPERATORS["blk.0.ffn_down.weight"][0]

    norm_bindings: dict[str, Mapping[str, Any]] = {}
    for name in NORM_TENSORS:
        tensor = by_name[name]
        payload = raw[tensor.data_offset : tensor.data_offset + tensor.data_size]
        norm_bindings[name] = _bind_norm_tensor(tensor, payload, embedding_width)

    linear_bindings: dict[str, Mapping[str, Any]] = {}
    for name in LINEAR_TENSORS:
        tensor = by_name[name]
        payload = raw[tensor.data_offset : tensor.data_offset + tensor.data_size]
        linear_bindings[name] = _bind_linear_tensor(tensor, payload)

    graph = _compose_graph(
        embedding_width=embedding_width,
        ffn_width=ffn_width,
        norm_bindings=norm_bindings,
        linear_bindings=linear_bindings,
    )
    controls = _exact_controls()
    if not all(bool(record["exact"]) for record in controls.values()):
        raise Pass215Iteration6ValidationError("PASS215_I6_EXACT_CONTROL_FAILED")

    tensor_roots = {
        name: (
            norm_bindings[name]["canonical_value_root_hash216"]
            if name in norm_bindings
            else linear_bindings[name]["descriptor_root_hash216"]
        )
        for name in EXPECTED_BLOCK_TENSORS
    }
    suite_payload = {
        "tensor_roots": tensor_roots,
        "graph_root_hash216": graph["graph_root_hash216"],
        "control_roots": {
            "rope_position_zero_identity": controls["rope_position_zero_identity"]["root_hash216"],
            "single_token_softmax_identity": i4base.hash216(
                "pass215-i6-single-token-softmax-control",
                i4base.canonical_bytes(controls["single_token_softmax_identity"]["output"]),
            ),
        },
    }
    suite_root = i4base.hash216(
        "pass215-i6-authenticated-block-graph-suite", i4base.canonical_bytes(suite_payload)
    )
    source_record = {
        **dict(source),
        "filename": filename,
        "file_size_bytes": len(raw),
        "file_sha256": actual_sha,
        "expected_sha256_verified": expected_sha256 is None or actual_sha == expected_sha256,
        "container_architecture": parsed.architecture,
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
            "iteration5_validated_head": ITERATION5_VALIDATED_HEAD,
            "iteration5_validated_tree": ITERATION5_VALIDATED_TREE,
            "iteration5_nonlinear_suite_root_hash216": ITERATION5_NONLINEAR_SUITE_ROOT_HASH216,
            "iteration5_evidence_root_hash216": ITERATION5_EVIDENCE_ROOT_HASH216,
            "iteration5_receipt_hash72": ITERATION5_RECEIPT_HASH72,
            "iteration5_artifact_sha256": ITERATION5_ARTIFACT_SHA256,
            "iteration4_suite_output_root_hash216": i5.ITERATION4_SUITE_OUTPUT_ROOT_HASH216,
            "iteration4_terminal_evidence_hash216": i5.ITERATION4_TERMINAL_EVIDENCE_HASH216,
            "iteration3_evidence_root_hash216": i4base.ITERATION3_EVIDENCE_ROOT_HASH216,
            "iteration2_evidence_root_hash216": i4base.ITERATION2_EVIDENCE_ROOT_HASH216,
            "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "source": source_record,
        "authenticated_block_tensor_bindings": {
            "norm_tensors": norm_bindings,
            "linear_tensors": linear_bindings,
            "tensor_binding_roots_hash216": tensor_roots,
            "required_tensor_count": len(EXPECTED_BLOCK_TENSORS),
            "all_required_tensors_bound": set(tensor_roots) == set(EXPECTED_BLOCK_TENSORS),
        },
        "block_graph": graph,
        "exact_controls": controls,
        "claims": {
            "authenticated_complete_blk0_dependency_graph_composed": True,
            "real_norm_weights_exactly_decoded_from_ieee_bits": True,
            "all_seven_q4_0_linear_descriptors_compiled": True,
            "iteration5_nonlinear_semantics_bound_into_graph": True,
            "complete_block_tensor_set_authenticated": True,
            "coordinate_level_complete_block_forward_executed": False,
            "symbolic_coordinate_forward_materialized": False,
            "full_transformer_layer_forward_executed": False,
            "numeric_transcendental_evaluation_performed": False,
            "approximate_transcendental_evaluation_performed": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "runtime_mutation_performed": False,
            "canonical_mutation_performed": False,
        },
        "suite_payload": suite_payload,
        "block_graph_suite_root_hash216": suite_root,
    }
    evidence_root = i4base.hash216(
        "pass215-i6-authenticated-block-graph-evidence", i4base.canonical_bytes(evidence)
    )
    receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION6_AUTHENTICATED_BLOCK_GRAPH"},
        {
            "sequence": 6,
            "parent_hash72": ITERATION5_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "block_graph_suite_root_hash216": suite_root,
        },
    )
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = receipt
    _reject_floats(evidence)
    return evidence


def build_block_graph_evidence_from_path(
    path: str | Path,
    *,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    target = Path(path)
    return build_block_graph_evidence(
        target.read_bytes(),
        filename=target.name,
        source=source,
        expected_sha256=expected_sha256,
    )


def validate_block_graph_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration6ValidationError("PASS215_I6_EVIDENCE_IDENTITY_INVALID")
    authority = evidence.get("authority")
    if not isinstance(authority, Mapping):
        raise Pass215Iteration6ValidationError("PASS215_I6_AUTHORITY_MISSING")
    for key in ("runtime_mutation_authority_promoted", "canonical_mutation_authorized", "migration_active"):
        if authority.get(key) is not False:
            raise Pass215Iteration6ValidationError(f"PASS215_I6_FORBIDDEN_AUTHORITY:{key}")

    required_inherits = {
        "iteration5_validated_head": ITERATION5_VALIDATED_HEAD,
        "iteration5_validated_tree": ITERATION5_VALIDATED_TREE,
        "iteration5_nonlinear_suite_root_hash216": ITERATION5_NONLINEAR_SUITE_ROOT_HASH216,
        "iteration5_evidence_root_hash216": ITERATION5_EVIDENCE_ROOT_HASH216,
        "iteration5_receipt_hash72": ITERATION5_RECEIPT_HASH72,
        "iteration5_artifact_sha256": ITERATION5_ARTIFACT_SHA256,
        "iteration4_suite_output_root_hash216": i5.ITERATION4_SUITE_OUTPUT_ROOT_HASH216,
        "iteration4_terminal_evidence_hash216": i5.ITERATION4_TERMINAL_EVIDENCE_HASH216,
        "iteration3_evidence_root_hash216": i4base.ITERATION3_EVIDENCE_ROOT_HASH216,
        "iteration2_evidence_root_hash216": i4base.ITERATION2_EVIDENCE_ROOT_HASH216,
        "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
        "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    }
    if evidence.get("inherits") != required_inherits:
        raise Pass215Iteration6ValidationError("PASS215_I6_INHERITED_ROOT_BINDING_INVALID")

    source = evidence.get("source")
    if not isinstance(source, Mapping) or source.get("file_sha256") != REAL_MODEL_SHA256:
        raise Pass215Iteration6ValidationError("PASS215_I6_SOURCE_BINDING_INVALID")

    bindings = evidence.get("authenticated_block_tensor_bindings")
    if not isinstance(bindings, Mapping):
        raise Pass215Iteration6ValidationError("PASS215_I6_TENSOR_BINDINGS_MISSING")
    roots = bindings.get("tensor_binding_roots_hash216")
    if not isinstance(roots, Mapping) or set(roots) != set(EXPECTED_BLOCK_TENSORS):
        raise Pass215Iteration6ValidationError("PASS215_I6_TENSOR_BINDING_SET_INVALID")
    if bindings.get("all_required_tensors_bound") is not True:
        raise Pass215Iteration6ValidationError("PASS215_I6_TENSOR_BINDING_INCOMPLETE")

    graph = evidence.get("block_graph")
    if not isinstance(graph, Mapping):
        raise Pass215Iteration6ValidationError("PASS215_I6_GRAPH_MISSING")
    nodes = graph.get("nodes")
    if not isinstance(nodes, list) or tuple(node.get("op") for node in nodes) != GRAPH_OPS:
        raise Pass215Iteration6ValidationError("PASS215_I6_GRAPH_TOPOLOGY_INVALID")
    graph_without_root = dict(graph)
    recorded_graph_root = graph_without_root.pop("graph_root_hash216", None)
    expected_graph_root = i4base.hash216(
        "pass215-i6-authenticated-block-graph", i4base.canonical_bytes(graph_without_root)
    )
    if recorded_graph_root != expected_graph_root:
        raise Pass215Iteration6ValidationError("PASS215_I6_GRAPH_ROOT_MISMATCH")

    controls = evidence.get("exact_controls")
    if not isinstance(controls, Mapping) or set(controls) != set(_exact_controls()):
        raise Pass215Iteration6ValidationError("PASS215_I6_CONTROL_SET_INVALID")
    if not all(isinstance(record, Mapping) and record.get("exact") is True for record in controls.values()):
        raise Pass215Iteration6ValidationError("PASS215_I6_CONTROL_NOT_EXACT")

    claims = evidence.get("claims")
    if not isinstance(claims, Mapping):
        raise Pass215Iteration6ValidationError("PASS215_I6_CLAIMS_MISSING")
    for key in (
        "authenticated_complete_blk0_dependency_graph_composed",
        "real_norm_weights_exactly_decoded_from_ieee_bits",
        "all_seven_q4_0_linear_descriptors_compiled",
        "iteration5_nonlinear_semantics_bound_into_graph",
        "complete_block_tensor_set_authenticated",
    ):
        if claims.get(key) is not True:
            raise Pass215Iteration6ValidationError(f"PASS215_I6_REQUIRED_CLAIM_FALSE:{key}")
    for key in (
        "coordinate_level_complete_block_forward_executed",
        "symbolic_coordinate_forward_materialized",
        "full_transformer_layer_forward_executed",
        "numeric_transcendental_evaluation_performed",
        "approximate_transcendental_evaluation_performed",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "runtime_mutation_performed",
        "canonical_mutation_performed",
    ):
        if claims.get(key) is not False:
            raise Pass215Iteration6ValidationError(f"PASS215_I6_BOUNDARY_CLAIM_INVALID:{key}")

    suite_payload = evidence.get("suite_payload")
    if not isinstance(suite_payload, Mapping):
        raise Pass215Iteration6ValidationError("PASS215_I6_SUITE_PAYLOAD_MISSING")
    expected_suite_root = i4base.hash216(
        "pass215-i6-authenticated-block-graph-suite", i4base.canonical_bytes(suite_payload)
    )
    if evidence.get("block_graph_suite_root_hash216") != expected_suite_root:
        raise Pass215Iteration6ValidationError("PASS215_I6_SUITE_ROOT_MISMATCH")

    body = dict(evidence)
    recorded_root = body.pop("evidence_root_hash216", None)
    recorded_receipt = body.pop("receipt_hash72", None)
    expected_root = i4base.hash216(
        "pass215-i6-authenticated-block-graph-evidence", i4base.canonical_bytes(body)
    )
    if recorded_root != expected_root:
        raise Pass215Iteration6ValidationError("PASS215_I6_EVIDENCE_ROOT_MISMATCH")
    expected_receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION6_AUTHENTICATED_BLOCK_GRAPH"},
        {
            "sequence": 6,
            "parent_hash72": ITERATION5_RECEIPT_HASH72,
            "evidence_root_hash216": expected_root,
            "block_graph_suite_root_hash216": expected_suite_root,
        },
    )
    if recorded_receipt != expected_receipt:
        raise Pass215Iteration6ValidationError("PASS215_I6_RECEIPT_MISMATCH")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_block_graph_evidence(left)
    validate_block_graph_evidence(right)
    keys = ("block_graph_suite_root_hash216", "evidence_root_hash216", "receipt_hash72")
    if any(left.get(key) != right.get(key) for key in keys):
        raise Pass215Iteration6ValidationError("PASS215_I6_CROSS_PROCESS_REPLAY_MISMATCH")
    return {
        "schema": "HHS_PASS_215_ITERATION_6_BLOCK_GRAPH_REPLAY_VALIDATION_V1",
        "semantic_exactness": True,
        "cross_process_replay": True,
        "block_graph_suite_root_hash216": left["block_graph_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }


__all__ = [
    "CONTRACT",
    "PASS_NUMBER",
    "ITERATION",
    "EVIDENCE_SCHEMA",
    "VALIDATION_SCHEMA",
    "REAL_MODEL_SHA256",
    "NORM_TENSORS",
    "LINEAR_TENSORS",
    "EXPECTED_BLOCK_TENSORS",
    "GRAPH_OPS",
    "Pass215Iteration6Error",
    "Pass215Iteration6ValidationError",
    "decode_binary32_exact",
    "decode_bfloat16_exact",
    "build_block_graph_evidence",
    "build_block_graph_evidence_from_path",
    "validate_block_graph_evidence",
    "compare_replay",
]
