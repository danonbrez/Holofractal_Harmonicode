"""Pass 215 Iteration 13 authenticated terminal model head.

Preserves the frozen Iteration 12 six-block closure and extends the same shared
exact symbolic DAG through the authenticated terminal output RMSNorm and the
explicit Q8_0 output projection of the real GGUF.  Every vocabulary row is
materialized as a source-bound exact Q8_0 transition generator.  No numerical
transcendental approximation or Python-float canonical authority is introduced.

This completes the contracted four-token text -> logits symbolic forward only.
Autoregressive continuation, token selection/sampling, arbitrary sequence
length, dense-forward replacement, runtime mutation, canonical mutation, and
migration remain outside authority.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration3_quant_block_structure_v1 as i3
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration5_exact_nonlinear_symbolic_v1 as i5
from hhs_backend.runtime import hhs_pass215_iteration6_authenticated_block_graph_v1 as i6
from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7
from hhs_backend.runtime import hhs_pass215_iteration8_multi_token_causal_attention_v1 as i8
from hhs_backend.runtime import hhs_pass215_iteration9_authenticated_token_ingress_v2 as i9
from hhs_backend.runtime import hhs_pass215_iteration10_exact_text_token_ingress_v1 as i10
from hhs_backend.runtime import hhs_pass215_iteration11_sequential_two_block_v1 as i11
from hhs_backend.runtime import hhs_pass215_iteration12_all_six_block_forward_v1 as i12

CONTRACT = "HHS-P215-I13-AUTHENTICATED-TERMINAL-MODEL-HEAD"
PASS_NUMBER = 215
ITERATION = 13
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_13_TERMINAL_MODEL_HEAD_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_13_TERMINAL_MODEL_HEAD_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_13_TERMINAL_MODEL_HEAD_REPLAY_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_13_AUTHENTICATED_TERMINAL_MODEL_HEAD_BENCHMARK"

ITERATION12_CLOSURE_HEAD = "7d2bfa13071692db4d9370a29b09711bd1424cd3"
ITERATION12_CLOSURE_TREE = "2b22da9ec696f91a8e2e56177d05fd07bb0eadc9"
ITERATION12_ALL_BLOCK_BINDING_ROOT_HASH216 = "35d820643d7fcb06cb085cd27d220e3485737b770eb6cb015ccd4b229ef95d74"
ITERATION12_SEQUENTIAL_CHAIN_ROOT_HASH216 = "dec707625c00d81a7057b2a36c7f0d2505ac32e17590417a7c96977a804459e7"
ITERATION12_ALL_STAGE_ROOT_HASH216 = "a03f033dfba165aebe427199d25925a601101108c5824d59b7c5ea41346010e3"
ITERATION12_ALL_CAUSAL_ROOT_HASH216 = "9451874aabe8083676b44fa228642f16c108705af1cbd05cb2cef8dd431842fb"
ITERATION12_FINAL_BLOCK_OUTPUT_ROOT_HASH216 = "374646cb52aa186358dab2ee8d2f9a5ee023234603c05fdef2c534fa0f2b9ad4"
ITERATION12_FULL_DAG_ROOT_HASH216 = "f024c2a858f25b86ccd4f21adb0dcbc1d51234472565aa83a958bafc6ca6a2dd"
ITERATION12_ALL_BLOCK_FORWARD_ROOT_HASH216 = "0b0ca3bb2a28be60de6a5e783ba583bc3cc0ef3be5211be98ea08bf687139c4e"
ITERATION12_SUITE_ROOT_HASH216 = "77e585b4d7604da8222b9d070a6b26e27a3a9bac7a86f5247882cfee6cfcf5a0"
ITERATION12_EVIDENCE_ROOT_HASH216 = "4eab17d68688073ca47c1fba115ed1fee5f78484538bf4ef8fcf462ae21581f0"
ITERATION12_RECEIPT_HASH72 = "BUDqOLYVgj8Wst5qWsfXL3atMEsax6uhjs-BOQjajv<cWn?hBEUW8wIb-1(drPEMx?VtVdM7"
ITERATION12_CLOSURE_ARTIFACT_SHA256 = "0bf86bb4bc09b8560dbde7d644257b8d52a39c0988b8424862e3a33a32595033"

REAL_MODEL_SHA256 = i12.REAL_MODEL_SHA256
CONTRACTED_PROMPT = i12.CONTRACTED_PROMPT
FROZEN_TOKEN_IDS = i12.FROZEN_TOKEN_IDS
SEQUENCE_LENGTH = i12.SEQUENCE_LENGTH
EMBEDDING_WIDTH = i12.EMBEDDING_WIDTH
AUTHENTICATED_BLOCK_COUNT = i12.AUTHENTICATED_BLOCK_COUNT
OUTPUT_NORM_TENSOR = "output_norm.weight"
OUTPUT_TENSOR = "output.weight"
OUTPUT_STORAGE_TYPE = "Q8_0"
Q8_LAYOUT = i3.SUPPORTED_LAYOUTS[OUTPUT_STORAGE_TYPE]
Q8_BLOCKS_PER_ROW = EMBEDDING_WIDTH // Q8_LAYOUT.block_elements
Q8_ROW_BYTES = Q8_BLOCKS_PER_ROW * Q8_LAYOUT.block_bytes
I13_SYMBOLIC_OPS = frozenset(set(i8.I8_SYMBOLIC_OPS) | {"q8_0_linear_row"})


class Pass215Iteration13Error(RuntimeError):
    pass


class Pass215Iteration13ValidationError(Pass215Iteration13Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration13ValidationError(f"PASS215_I13_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _iteration12_bindings() -> Mapping[str, Any]:
    return {
        "iteration12_closure_head": ITERATION12_CLOSURE_HEAD,
        "iteration12_closure_tree": ITERATION12_CLOSURE_TREE,
        "iteration12_all_block_binding_root_hash216": ITERATION12_ALL_BLOCK_BINDING_ROOT_HASH216,
        "iteration12_sequential_chain_root_hash216": ITERATION12_SEQUENTIAL_CHAIN_ROOT_HASH216,
        "iteration12_all_stage_root_hash216": ITERATION12_ALL_STAGE_ROOT_HASH216,
        "iteration12_all_causal_root_hash216": ITERATION12_ALL_CAUSAL_ROOT_HASH216,
        "iteration12_final_block_output_root_hash216": ITERATION12_FINAL_BLOCK_OUTPUT_ROOT_HASH216,
        "iteration12_full_dag_root_hash216": ITERATION12_FULL_DAG_ROOT_HASH216,
        "iteration12_all_block_forward_root_hash216": ITERATION12_ALL_BLOCK_FORWARD_ROOT_HASH216,
        "iteration12_suite_root_hash216": ITERATION12_SUITE_ROOT_HASH216,
        "iteration12_evidence_root_hash216": ITERATION12_EVIDENCE_ROOT_HASH216,
        "iteration12_receipt_hash72": ITERATION12_RECEIPT_HASH72,
        "iteration12_closure_artifact_sha256": ITERATION12_CLOSURE_ARTIFACT_SHA256,
    }


def _validate_frozen_iteration12_evidence(evidence: Mapping[str, Any]) -> None:
    i12.validate_all_six_block_evidence(evidence)
    bindings = evidence["authenticated_all_block_tensor_bindings"]
    forward = evidence["sequential_all_block_forward"]
    checks = {
        "all_binding": (bindings["all_block_binding_root_hash216"], ITERATION12_ALL_BLOCK_BINDING_ROOT_HASH216),
        "sequential_chain": (forward["sequential_chain_root_hash216"], ITERATION12_SEQUENTIAL_CHAIN_ROOT_HASH216),
        "all_stage": (forward["all_stage_suite_root_hash216"], ITERATION12_ALL_STAGE_ROOT_HASH216),
        "all_causal": (forward["all_causal_attention_root_hash216"], ITERATION12_ALL_CAUSAL_ROOT_HASH216),
        "final_block": (forward["final_block_output_root_hash216"], ITERATION12_FINAL_BLOCK_OUTPUT_ROOT_HASH216),
        "dag": (forward["symbolic_dag"]["ordered_node_root_hash216"], ITERATION12_FULL_DAG_ROOT_HASH216),
        "all_block": (forward["all_block_forward_root_hash216"], ITERATION12_ALL_BLOCK_FORWARD_ROOT_HASH216),
        "suite": (evidence["all_six_block_suite_root_hash216"], ITERATION12_SUITE_ROOT_HASH216),
        "evidence": (evidence["evidence_root_hash216"], ITERATION12_EVIDENCE_ROOT_HASH216),
        "receipt": (evidence["receipt_hash72"], ITERATION12_RECEIPT_HASH72),
    }
    for name, (actual, expected) in checks.items():
        if actual != expected:
            raise Pass215Iteration13ValidationError(f"PASS215_I13_ITERATION12_ROOT_MISMATCH:{name}")
    if evidence["claims"]["all_model_blocks_executed"] is not True:
        raise Pass215Iteration13ValidationError("PASS215_I13_ITERATION12_ALL_BLOCK_AUTHORITY_MISSING")
    if evidence["claims"]["full_model_forward_executed"] is not False:
        raise Pass215Iteration13ValidationError("PASS215_I13_ITERATION12_FULL_MODEL_BOUNDARY_CHANGED")


class TerminalHeadSymbolicDAG(i8.MultiTokenSymbolicDAG):
    """Preserve every Iteration-8/12 node identity and add exact Q8 rows."""

    def intern(
        self,
        op: str,
        inputs: Sequence[str] = (),
        attributes: Mapping[str, Any] | None = None,
        *,
        commutative: bool = False,
    ) -> str:
        if op in i8.I8_SYMBOLIC_OPS:
            return super().intern(op, inputs, attributes, commutative=commutative)
        if op != "q8_0_linear_row":
            raise Pass215Iteration13ValidationError(f"PASS215_I13_SYMBOLIC_OP_INVALID:{op}")
        attrs = dict(attributes or {})
        _reject_floats(attrs)
        normalized_inputs = tuple(sorted(str(x) for x in inputs)) if commutative else tuple(str(x) for x in inputs)
        canonical = {"op": op, "inputs": list(normalized_inputs), "attributes": attrs}
        root = i4base.hash216("pass215-i13-terminal-head-node", i4base.canonical_bytes(canonical))
        prior = self._nodes.get(root)
        if prior is not None:
            if prior != canonical:
                raise Pass215Iteration13ValidationError("PASS215_I13_SYMBOLIC_HASH_COLLISION")
            return root
        self._nodes[root] = canonical
        self._order.append(root)
        self._histogram[op] += 1
        return root

    def prefix_manifest(self) -> Mapping[str, Any]:
        return i8.MultiTokenSymbolicDAG.manifest(self)

    def manifest(self) -> Mapping[str, Any]:
        return {
            "unique_node_count": len(self._nodes),
            "operator_histogram": {op: int(self._histogram.get(op, 0)) for op in sorted(I13_SYMBOLIC_OPS)},
            "ordered_node_root_hash216": i4base.hash216(
                "pass215-i13-terminal-head-dag-order", i4base.canonical_bytes(self._order)
            ),
            "hash_consistent_reuse": True,
            "recursive_tree_duplication_required": False,
            "numeric_transcendental_evaluation_performed": False,
        }


def _decode_q8_block(block: bytes) -> tuple[tuple[int, int], tuple[int, ...]]:
    if len(block) != Q8_LAYOUT.block_bytes:
        raise Pass215Iteration13ValidationError("PASS215_I13_Q8_BLOCK_LENGTH_INVALID")
    scale = i4base.decode_binary16_exact(block[:Q8_LAYOUT.scale_bytes])
    codes = tuple(int.from_bytes(block[index:index + 1], "little", signed=True) for index in range(2, 34))
    if len(codes) != Q8_LAYOUT.block_elements:
        raise Pass215Iteration13ValidationError("PASS215_I13_Q8_CODE_COUNT_INVALID")
    return scale, codes


def _decode_q8_row(row_raw: bytes) -> tuple[tuple[int, int], ...]:
    if len(row_raw) != Q8_ROW_BYTES:
        raise Pass215Iteration13ValidationError("PASS215_I13_Q8_ROW_BYTE_GEOMETRY_INVALID")
    values: list[tuple[int, int]] = []
    for offset in range(0, len(row_raw), Q8_LAYOUT.block_bytes):
        scale, codes = _decode_q8_block(row_raw[offset:offset + Q8_LAYOUT.block_bytes])
        for code in codes:
            values.append(i5.q_pair(i5.mul(i5.q(code), i5.q(scale[0], scale[1]))))
    if len(values) != EMBEDDING_WIDTH:
        raise Pass215Iteration13ValidationError("PASS215_I13_Q8_ROW_COORDINATE_COUNT_INVALID")
    return tuple(values)


def _q8_dot_flat(row: Sequence[tuple[int, int]], inputs: Sequence[int]) -> tuple[int, int]:
    if len(row) != EMBEDDING_WIDTH or len(inputs) != EMBEDDING_WIDTH:
        raise Pass215Iteration13ValidationError("PASS215_I13_Q8_CONTROL_GEOMETRY_INVALID")
    total = i5.q(0)
    for weight, value in zip(row, inputs):
        total = i5.add(total, i5.mul(i5.q(weight[0], weight[1]), i5.q(int(value))))
    return i5.q_pair(total)


def _q8_dot_blockwise(row_raw: bytes, inputs: Sequence[int]) -> tuple[int, int]:
    if len(row_raw) != Q8_ROW_BYTES or len(inputs) != EMBEDDING_WIDTH:
        raise Pass215Iteration13ValidationError("PASS215_I13_Q8_CONTROL_GEOMETRY_INVALID")
    total = i5.q(0)
    input_offset = 0
    for offset in range(0, len(row_raw), Q8_LAYOUT.block_bytes):
        scale, codes = _decode_q8_block(row_raw[offset:offset + Q8_LAYOUT.block_bytes])
        inner = i5.q(0)
        for code, value in zip(codes, inputs[input_offset:input_offset + Q8_LAYOUT.block_elements]):
            inner = i5.add(inner, i5.mul(i5.q(code), i5.q(int(value))))
        total = i5.add(total, i5.mul(i5.q(scale[0], scale[1]), inner))
        input_offset += Q8_LAYOUT.block_elements
    return i5.q_pair(total)


def _bind_terminal_tensors(raw: bytes, vocabulary_size: int) -> Mapping[str, Any]:
    parsed = i4base.parse_gguf(raw)
    by_name = {tensor.name: tensor for tensor in parsed.tensors}
    norm_tensor = by_name.get(OUTPUT_NORM_TENSOR)
    if norm_tensor is None:
        raise Pass215Iteration13ValidationError("PASS215_I13_OUTPUT_NORM_MISSING")
    norm_payload = raw[norm_tensor.data_offset:norm_tensor.data_offset + norm_tensor.data_size]
    try:
        norm_binding = i6._bind_norm_tensor(norm_tensor, norm_payload, EMBEDDING_WIDTH)
    except i6.Pass215Iteration6ValidationError as exc:
        raise Pass215Iteration13ValidationError(f"PASS215_I13_OUTPUT_NORM_INVALID:{exc}") from exc

    output_tensor = by_name.get(OUTPUT_TENSOR)
    if output_tensor is None:
        raise Pass215Iteration13ValidationError("PASS215_I13_EXPLICIT_OUTPUT_TENSOR_MISSING")
    expected_shape = (EMBEDDING_WIDTH, vocabulary_size)
    if output_tensor.storage_type != OUTPUT_STORAGE_TYPE or tuple(output_tensor.shape) != expected_shape:
        raise Pass215Iteration13ValidationError(
            f"PASS215_I13_OUTPUT_GEOMETRY_INVALID:{output_tensor.storage_type}:{tuple(output_tensor.shape)}"
        )
    expected_bytes = Q8_ROW_BYTES * vocabulary_size
    if output_tensor.data_size != expected_bytes:
        raise Pass215Iteration13ValidationError("PASS215_I13_OUTPUT_BYTE_COUNT_INVALID")
    output_payload = raw[output_tensor.data_offset:output_tensor.data_offset + output_tensor.data_size]
    source_sha = sha256(output_payload).hexdigest()
    if source_sha != output_tensor.source_sha256:
        raise Pass215Iteration13ValidationError("PASS215_I13_OUTPUT_SOURCE_SHA_MISMATCH")
    descriptor = {
        "name": OUTPUT_TENSOR,
        "shape": list(expected_shape),
        "storage_type": OUTPUT_STORAGE_TYPE,
        "source_sha256": source_sha,
        "source_bytes": len(output_payload),
        "block_elements": Q8_LAYOUT.block_elements,
        "block_bytes": Q8_LAYOUT.block_bytes,
        "blocks_per_row": Q8_BLOCKS_PER_ROW,
        "row_bytes": Q8_ROW_BYTES,
        "row_count": vocabulary_size,
        "logical_weight_count": EMBEDDING_WIDTH * vocabulary_size,
        "factored_generator": True,
        "semantic_form": "sum_j(exact_q8_weight[row,j]*input[j])",
    }
    descriptor_root = i4base.hash216(
        "pass215-i13-authenticated-q8-output-descriptor", i4base.canonical_bytes(descriptor)
    )
    descriptor["descriptor_root_hash216"] = descriptor_root
    topology = {
        "terminal_norm_tensor": OUTPUT_NORM_TENSOR,
        "output_projection_tensor": OUTPUT_TENSOR,
        "output_projection_tied_to_embedding": False,
        "explicit_output_projection": True,
        "embedding_width": EMBEDDING_WIDTH,
        "vocabulary_size": vocabulary_size,
        "output_storage_type": OUTPUT_STORAGE_TYPE,
        "terminal_norm_storage_type": norm_binding["storage_type"],
    }
    topology_root = i4base.hash216(
        "pass215-i13-authenticated-terminal-topology", i4base.canonical_bytes(topology)
    )
    return {
        "topology": {**topology, "topology_root_hash216": topology_root},
        "output_norm": norm_binding,
        "output_projection": descriptor,
        "output_payload": output_payload,
    }


def _q8_semantic_control(binding: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = binding["output_payload"]
    descriptor = binding["output_projection"]
    row_count = int(descriptor["row_count"])
    selected_rows = (0, row_count // 2, row_count - 1)
    inputs = tuple(int(value) for value in i4base.deterministic_vector(EMBEDDING_WIDTH))
    records = []
    exact = True
    for row_index in selected_rows:
        start = row_index * Q8_ROW_BYTES
        row_raw = payload[start:start + Q8_ROW_BYTES]
        flat = _q8_dot_flat(_decode_q8_row(row_raw), inputs)
        blockwise = _q8_dot_blockwise(row_raw, inputs)
        exact = exact and flat == blockwise
        records.append({
            "row_index": row_index,
            "row_source_sha256": sha256(row_raw).hexdigest(),
            "flat_exact": {"numerator": flat[0], "denominator": flat[1]},
            "block_factored_exact": {"numerator": blockwise[0], "denominator": blockwise[1]},
            "exact": flat == blockwise,
        })
    return {
        "exact": exact,
        "selected_rows": list(selected_rows),
        "records": records,
        "control_root_hash216": i4base.hash216(
            "pass215-i13-q8-row-semantic-control", i4base.canonical_bytes(records)
        ),
    }


def _reconstruct_six_block_prefix(
    raw: bytes,
    *,
    prompt: str,
    frozen_evidence: Mapping[str, Any],
) -> Mapping[str, Any]:
    architecture = i11._read_architecture_metadata(raw)
    i12._require_all_block_architecture(architecture)
    tokenizer = i10._read_exact_tokenizer_metadata(raw)
    tokenization = i10._tokenize_sentencepiece_bpe(prompt, tokenizer)
    token_ids = tuple(int(value) for value in tokenization["token_ids"])
    if token_ids != FROZEN_TOKEN_IDS:
        raise Pass215Iteration13ValidationError("PASS215_I13_FROZEN_TOKEN_IDS_CHANGED")
    embeddings = i9._extract_authenticated_embeddings(raw, tokenizer, token_ids)
    bindings = {index: i11._bind_block_tensors(raw, index) for index in i12.BLOCK_INDEXES}
    dag = TerminalHeadSymbolicDAG()
    hidden = tuple(tuple(dag.q(n, d) for n, d in row) for row in embeddings["rows"])
    blocks: dict[int, Mapping[str, Any]] = {}
    block0 = i11._execute_block(dag, hidden, bindings[0], block_index=0)
    blocks[0] = block0
    block1 = i11._execute_block(dag, block0["output_coordinate_roots"], bindings[1], block_index=1)
    blocks[1] = block1
    previous = block1
    for block_index in i12.EXTENSION_BLOCK_INDEXES:
        current = i12._execute_extension_block(
            dag, previous["output_coordinate_roots"], bindings[block_index], block_index=block_index
        )
        blocks[block_index] = current
        previous = current
    if tuple(blocks) != i12.BLOCK_INDEXES:
        raise Pass215Iteration13ValidationError("PASS215_I13_PREFIX_BLOCK_CHAIN_INCOMPLETE")
    prefix_manifest = dag.prefix_manifest()
    expected_forward = frozen_evidence["sequential_all_block_forward"]
    if prefix_manifest["ordered_node_root_hash216"] != ITERATION12_FULL_DAG_ROOT_HASH216:
        raise Pass215Iteration13ValidationError("PASS215_I13_PREFIX_DAG_ROOT_CHANGED")
    if blocks[5]["final_output_root_hash216"] != ITERATION12_FINAL_BLOCK_OUTPUT_ROOT_HASH216:
        raise Pass215Iteration13ValidationError("PASS215_I13_PREFIX_FINAL_BLOCK_ROOT_CHANGED")
    per_block_outputs = {
        f"blk.{index}": blocks[index]["final_output_root_hash216"] for index in i12.BLOCK_INDEXES
    }
    if per_block_outputs != expected_forward["per_block_final_output_roots"]:
        raise Pass215Iteration13ValidationError("PASS215_I13_PREFIX_PER_BLOCK_OUTPUT_ROOTS_CHANGED")
    return {
        "dag": dag,
        "blocks": blocks,
        "architecture": architecture,
        "tokenizer": tokenizer,
        "tokenization": tokenization,
        "embeddings": embeddings,
        "prefix_manifest": prefix_manifest,
    }


def _execute_terminal_head(
    dag: TerminalHeadSymbolicDAG,
    final_hidden: Sequence[Sequence[str]],
    binding: Mapping[str, Any],
) -> Mapping[str, Any]:
    if len(final_hidden) != SEQUENCE_LENGTH or any(len(row) != EMBEDDING_WIDTH for row in final_hidden):
        raise Pass215Iteration13ValidationError("PASS215_I13_FINAL_HIDDEN_GEOMETRY_INVALID")
    norm_weights = i7._norm_values(binding["output_norm"])
    normalized = tuple(i7._exact_rmsnorm_dag(dag, row, norm_weights) for row in final_hidden)
    norm_stage = i8._stage_manifest(dag, "terminal_output_norm", normalized)
    norm_token_roots = [record["vector_root_hash216"] for record in norm_stage["token_records"]]
    norm_root = i4base.hash216(
        "pass215-i13-terminal-output-norm-token-suite", i4base.canonical_bytes(norm_token_roots)
    )

    descriptor = binding["output_projection"]
    vocab_size = int(descriptor["row_count"])
    logits: list[tuple[str, ...]] = []
    for position, row in enumerate(normalized):
        input_root = dag.vector(row, f"terminal_output_projection:token:{position}:input")
        token_logits = tuple(
            dag.intern(
                "q8_0_linear_row",
                (input_root,),
                {
                    "stage": f"terminal_output_projection:token:{position}",
                    "tensor": OUTPUT_TENSOR,
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
        logits.append(token_logits)
    logits_stage = i8._stage_manifest(dag, "terminal_output_logits", logits)
    logit_token_roots = [record["vector_root_hash216"] for record in logits_stage["token_records"]]
    logits_root = i4base.hash216(
        "pass215-i13-terminal-logit-token-suite", i4base.canonical_bytes(logit_token_roots)
    )
    projection_work = {
        "row_transitions": SEQUENCE_LENGTH * vocab_size,
        "logical_weight_products": SEQUENCE_LENGTH * vocab_size * EMBEDDING_WIDTH,
        "logical_accumulation_additions": SEQUENCE_LENGTH * vocab_size * (EMBEDDING_WIDTH - 1),
        "q8_block_scale_applications": SEQUENCE_LENGTH * vocab_size * Q8_BLOCKS_PER_ROW,
    }
    return {
        "terminal_norm_stage": norm_stage,
        "terminal_norm_root_hash216": norm_root,
        "terminal_norm_token_roots": norm_token_roots,
        "logits_stage": logits_stage,
        "logits_root_hash216": logits_root,
        "logit_token_roots": logit_token_roots,
        "logit_token_count": SEQUENCE_LENGTH,
        "vocabulary_size": vocab_size,
        "logit_coordinate_count": SEQUENCE_LENGTH * vocab_size,
        "projection_transition_work": projection_work,
    }


def build_terminal_model_head_evidence(
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
        raise Pass215Iteration13ValidationError("PASS215_I13_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration13ValidationError("PASS215_I13_AUTHENTICATED_MODEL_IDENTITY_MISMATCH")
    if prompt != CONTRACTED_PROMPT:
        raise Pass215Iteration13ValidationError("PASS215_I13_PROMPT_OUTSIDE_CONTRACT")

    frozen = i12.build_all_six_block_evidence(
        raw, filename=filename, source=source, prompt=prompt, expected_sha256=expected_sha256
    )
    _validate_frozen_iteration12_evidence(frozen)
    prefix = _reconstruct_six_block_prefix(raw, prompt=prompt, frozen_evidence=frozen)
    tokenizer = prefix["tokenizer"]
    vocab_size = int(tokenizer["vocabulary_size"])
    terminal_binding = _bind_terminal_tensors(raw, vocab_size)
    q8_control = _q8_semantic_control(terminal_binding)
    if not q8_control["exact"]:
        raise Pass215Iteration13ValidationError("PASS215_I13_Q8_SEMANTIC_CONTROL_FAILED")
    terminal = _execute_terminal_head(
        prefix["dag"], prefix["blocks"][5]["output_coordinate_roots"], terminal_binding
    )
    full_manifest = prefix["dag"].manifest()
    topology_record = terminal_binding["topology"]
    norm_record = terminal_binding["output_norm"]
    projection_record = terminal_binding["output_projection"]
    terminal_payload = {
        "iteration12_all_block_forward_root_hash216": ITERATION12_ALL_BLOCK_FORWARD_ROOT_HASH216,
        "terminal_topology_root_hash216": topology_record["topology_root_hash216"],
        "output_norm_value_root_hash216": norm_record["canonical_value_root_hash216"],
        "output_projection_descriptor_root_hash216": projection_record["descriptor_root_hash216"],
        "terminal_norm_root_hash216": terminal["terminal_norm_root_hash216"],
        "logits_root_hash216": terminal["logits_root_hash216"],
        "full_symbolic_dag_root_hash216": full_manifest["ordered_node_root_hash216"],
        "projection_transition_work": terminal["projection_transition_work"],
    }
    full_model_forward_root = i4base.hash216(
        "pass215-i13-authenticated-terminal-model-head-forward", i4base.canonical_bytes(terminal_payload)
    )
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
            **_iteration12_bindings(),
            "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "source": source_record,
        "contracted_text_ingress": {
            "input_text": prefix["tokenization"]["input_text"],
            "normalized_text": prefix["tokenization"]["normalized_text"],
            "token_ids": list(FROZEN_TOKEN_IDS),
            "tokens": list(prefix["tokenization"]["tokens"]),
        },
        "authenticated_terminal_topology": topology_record,
        "authenticated_output_norm": {key: value for key, value in norm_record.items()},
        "authenticated_output_projection": {key: value for key, value in projection_record.items()},
        "exact_q8_semantic_control": q8_control,
        "terminal_model_head_forward": {
            **terminal,
            "iteration12_prefix_symbolic_dag_root_hash216": prefix["prefix_manifest"]["ordered_node_root_hash216"],
            "symbolic_dag": full_manifest,
            "full_model_forward_root_hash216": full_model_forward_root,
            "total_linear_transition_work_including_six_blocks": {
                "row_transitions": i12._expected_linear_work_total()["row_transitions"] + terminal["projection_transition_work"]["row_transitions"],
                "logical_weight_products": i12._expected_linear_work_total()["logical_weight_products"] + terminal["projection_transition_work"]["logical_weight_products"],
                "logical_accumulation_additions": i12._expected_linear_work_total()["logical_accumulation_additions"] + terminal["projection_transition_work"]["logical_accumulation_additions"],
            },
        },
        "claims": {
            "authenticated_iteration12_roots_inherited_unchanged": True,
            "all_model_blocks_executed": True,
            "authenticated_terminal_output_norm_executed": True,
            "authenticated_explicit_q8_output_projection_executed": True,
            "output_logits_executed": True,
            "contracted_four_token_full_model_forward_executed": True,
            "full_model_forward_executed": True,
            "general_arbitrary_sequence_length_transformer_forward_executed": False,
            "generation_or_sampling_executed": False,
            "autoregressive_continuation_executed": False,
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
        "iteration12_suite_root_hash216": ITERATION12_SUITE_ROOT_HASH216,
        "terminal_topology_root_hash216": topology_record["topology_root_hash216"],
        "terminal_norm_root_hash216": terminal["terminal_norm_root_hash216"],
        "logits_root_hash216": terminal["logits_root_hash216"],
        "q8_semantic_control_root_hash216": q8_control["control_root_hash216"],
        "full_model_forward_root_hash216": full_model_forward_root,
    }
    suite_root = i4base.hash216("pass215-i13-terminal-model-head-suite", i4base.canonical_bytes(suite_payload))
    evidence["terminal_model_head_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216("pass215-i13-terminal-model-head-evidence", i4base.canonical_bytes(evidence))
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION13_TERMINAL_MODEL_HEAD"},
        {
            "sequence": 13,
            "parent_hash72": ITERATION12_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "suite_root_hash216": suite_root,
            "full_model_forward_root_hash216": full_model_forward_root,
        },
    )
    _reject_floats(evidence)
    return evidence


def build_terminal_model_head_evidence_from_path(
    path: str | Path,
    *,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    source_path = Path(path)
    return build_terminal_model_head_evidence(
        source_path.read_bytes(),
        filename=source_path.name,
        source=source,
        prompt=prompt,
        expected_sha256=expected_sha256,
    )


def validate_terminal_model_head_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration13ValidationError("PASS215_I13_SCHEMA_OR_CONTRACT_INVALID")
    if evidence.get("inherits") != {**_iteration12_bindings(), "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216, "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216}:
        raise Pass215Iteration13ValidationError("PASS215_I13_INHERITANCE_INVALID")
    topology = evidence.get("authenticated_terminal_topology", {})
    if topology.get("terminal_norm_tensor") != OUTPUT_NORM_TENSOR or topology.get("output_projection_tensor") != OUTPUT_TENSOR:
        raise Pass215Iteration13ValidationError("PASS215_I13_TERMINAL_TOPOLOGY_INVALID")
    if topology.get("output_projection_tied_to_embedding") is not False or topology.get("explicit_output_projection") is not True:
        raise Pass215Iteration13ValidationError("PASS215_I13_OUTPUT_TOPOLOGY_AUTHORITY_INVALID")
    if int(topology.get("embedding_width", 0)) != EMBEDDING_WIDTH or int(topology.get("vocabulary_size", 0)) <= 0:
        raise Pass215Iteration13ValidationError("PASS215_I13_TERMINAL_GEOMETRY_INVALID")
    projection = evidence.get("authenticated_output_projection", {})
    if projection.get("storage_type") != OUTPUT_STORAGE_TYPE or int(projection.get("row_bytes", 0)) != Q8_ROW_BYTES:
        raise Pass215Iteration13ValidationError("PASS215_I13_OUTPUT_PROJECTION_BINDING_INVALID")
    control = evidence.get("exact_q8_semantic_control", {})
    if control.get("exact") is not True:
        raise Pass215Iteration13ValidationError("PASS215_I13_Q8_CONTROL_NOT_EXACT")
    forward = evidence.get("terminal_model_head_forward", {})
    vocab = int(topology["vocabulary_size"])
    expected_work = {
        "row_transitions": SEQUENCE_LENGTH * vocab,
        "logical_weight_products": SEQUENCE_LENGTH * vocab * EMBEDDING_WIDTH,
        "logical_accumulation_additions": SEQUENCE_LENGTH * vocab * (EMBEDDING_WIDTH - 1),
        "q8_block_scale_applications": SEQUENCE_LENGTH * vocab * Q8_BLOCKS_PER_ROW,
    }
    if forward.get("projection_transition_work") != expected_work:
        raise Pass215Iteration13ValidationError("PASS215_I13_OUTPUT_WORK_INVALID")
    if int(forward.get("logit_coordinate_count", 0)) != SEQUENCE_LENGTH * vocab:
        raise Pass215Iteration13ValidationError("PASS215_I13_LOGIT_COUNT_INVALID")
    if forward.get("iteration12_prefix_symbolic_dag_root_hash216") != ITERATION12_FULL_DAG_ROOT_HASH216:
        raise Pass215Iteration13ValidationError("PASS215_I13_PREFIX_DAG_BINDING_INVALID")
    claims = evidence.get("claims", {})
    required_true = (
        "authenticated_iteration12_roots_inherited_unchanged",
        "all_model_blocks_executed",
        "authenticated_terminal_output_norm_executed",
        "authenticated_explicit_q8_output_projection_executed",
        "output_logits_executed",
        "contracted_four_token_full_model_forward_executed",
        "full_model_forward_executed",
    )
    required_false = (
        "general_arbitrary_sequence_length_transformer_forward_executed",
        "generation_or_sampling_executed",
        "autoregressive_continuation_executed",
        "numeric_transcendental_evaluation_performed",
        "approximate_transcendental_evaluation_performed",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "runtime_mutation_authority_promoted",
        "canonical_mutation_authorized",
        "migration_active",
    )
    if not all(claims.get(key) is True for key in required_true):
        raise Pass215Iteration13ValidationError("PASS215_I13_REQUIRED_TRUE_CLAIM_INVALID")
    if not all(claims.get(key) is False for key in required_false):
        raise Pass215Iteration13ValidationError("PASS215_I13_REQUIRED_FALSE_CLAIM_INVALID")
    stripped = dict(evidence)
    receipt = stripped.pop("receipt_hash72", None)
    evidence_root = stripped.pop("evidence_root_hash216", None)
    suite_root = stripped.get("terminal_model_head_suite_root_hash216")
    expected_evidence_root = i4base.hash216(
        "pass215-i13-terminal-model-head-evidence", i4base.canonical_bytes(stripped)
    )
    if evidence_root != expected_evidence_root:
        raise Pass215Iteration13ValidationError("PASS215_I13_EVIDENCE_ROOT_INVALID")
    expected_receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION13_TERMINAL_MODEL_HEAD"},
        {
            "sequence": 13,
            "parent_hash72": ITERATION12_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "suite_root_hash216": suite_root,
            "full_model_forward_root_hash216": forward["full_model_forward_root_hash216"],
        },
    )
    if receipt != expected_receipt:
        raise Pass215Iteration13ValidationError("PASS215_I13_RECEIPT_INVALID")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_terminal_model_head_evidence(left)
    validate_terminal_model_head_evidence(right)
    keys = (
        "terminal_model_head_suite_root_hash216",
        "evidence_root_hash216",
        "receipt_hash72",
    )
    for key in keys:
        if left[key] != right[key]:
            raise Pass215Iteration13ValidationError(f"PASS215_I13_REPLAY_MISMATCH:{key}")
    lf = left["terminal_model_head_forward"]
    rf = right["terminal_model_head_forward"]
    for key in ("terminal_norm_root_hash216", "logits_root_hash216", "full_model_forward_root_hash216"):
        if lf[key] != rf[key]:
            raise Pass215Iteration13ValidationError(f"PASS215_I13_REPLAY_FORWARD_MISMATCH:{key}")
    return {
        "schema": REPLAY_SCHEMA,
        "cross_process_replay": True,
        "semantic_exactness": True,
        "terminal_norm_root_hash216": lf["terminal_norm_root_hash216"],
        "logits_root_hash216": lf["logits_root_hash216"],
        "full_model_forward_root_hash216": lf["full_model_forward_root_hash216"],
        "suite_root_hash216": left["terminal_model_head_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }
