from __future__ import annotations

import pytest

from hhs_backend.runtime import hhs_pass215_iteration8_multi_token_causal_attention_v1 as i8
from hhs_backend.runtime import hhs_pass215_iteration13_terminal_model_head_v1 as i13


def _q8_block(scale_bits: bytes = b"\x00\x3c") -> bytes:
    codes = bytes((index & 0xFF) for index in range(16)) + bytes(((256 - index) & 0xFF) for index in range(1, 17))
    assert len(codes) == 32
    return scale_bits + codes


def test_iteration12_closure_is_frozen_parent() -> None:
    assert i13.ITERATION12_CLOSURE_HEAD == "7d2bfa13071692db4d9370a29b09711bd1424cd3"
    assert i13.ITERATION12_CLOSURE_TREE == "2b22da9ec696f91a8e2e56177d05fd07bb0eadc9"
    assert i13.ITERATION12_FULL_DAG_ROOT_HASH216 == "f024c2a858f25b86ccd4f21adb0dcbc1d51234472565aa83a958bafc6ca6a2dd"


def test_terminal_topology_constants_match_authenticated_model_evidence() -> None:
    assert i13.OUTPUT_NORM_TENSOR == "output_norm.weight"
    assert i13.OUTPUT_TENSOR == "output.weight"
    assert i13.OUTPUT_STORAGE_TYPE == "Q8_0"
    assert i13.EMBEDDING_WIDTH == 288


def test_q8_geometry_is_exact() -> None:
    assert i13.Q8_LAYOUT.block_elements == 32
    assert i13.Q8_LAYOUT.block_bytes == 34
    assert i13.Q8_BLOCKS_PER_ROW == 9
    assert i13.Q8_ROW_BYTES == 306


def test_q8_block_decoder_uses_signed_codes_and_exact_binary16() -> None:
    scale, codes = i13._decode_q8_block(_q8_block())
    assert scale == (1, 1)
    assert codes[:4] == (0, 1, 2, 3)
    assert codes[-4:] == (-13, -14, -15, -16)
    assert len(codes) == 32


def test_q8_row_decoder_materializes_exact_288_coordinates() -> None:
    row = i13._decode_q8_row(_q8_block() * i13.Q8_BLOCKS_PER_ROW)
    assert len(row) == 288
    assert row[1] == (1, 1)
    assert row[31] == (-16, 1)


def test_q8_blockwise_and_flat_semantics_agree() -> None:
    raw = _q8_block() * i13.Q8_BLOCKS_PER_ROW
    values = i13._decode_q8_row(raw)
    inputs = tuple((index % 11) - 5 for index in range(i13.EMBEDDING_WIDTH))
    assert i13._q8_dot_flat(values, inputs) == i13._q8_dot_blockwise(raw, inputs)


def test_q8_nan_or_inf_scale_fails_closed() -> None:
    with pytest.raises(Exception):
        i13._decode_q8_block(b"\x00\x7c" + bytes(32))


def test_terminal_dag_preserves_inherited_node_identity() -> None:
    left = i13.TerminalHeadSymbolicDAG()
    right = i8.MultiTokenSymbolicDAG()
    la = left.q(3, 7)
    lb = left.q(5, 11)
    ra = right.q(3, 7)
    rb = right.q(5, 11)
    assert la == ra
    assert lb == rb
    assert left.add(la, lb) == right.add(ra, rb)
    assert left.prefix_manifest()["ordered_node_root_hash216"] == right.manifest()["ordered_node_root_hash216"]


def test_terminal_dag_adds_q8_generator_without_float_authority() -> None:
    dag = i13.TerminalHeadSymbolicDAG()
    vector = dag.vector((dag.q(1),) * i13.EMBEDDING_WIDTH, "control")
    root = dag.intern("q8_0_linear_row", (vector,), {
        "tensor": i13.OUTPUT_TENSOR,
        "row_index": 0,
        "semantic_form": "sum_j(exact_q8_weight[row,j]*input[j])",
    })
    manifest = dag.manifest()
    assert isinstance(root, str) and len(root) == 64
    assert manifest["operator_histogram"]["q8_0_linear_row"] == 1
    assert manifest["numeric_transcendental_evaluation_performed"] is False


def test_projection_work_for_authenticated_vocabulary_geometry() -> None:
    vocabulary_size = 32000
    assert i13.SEQUENCE_LENGTH * vocabulary_size == 128000
    assert i13.SEQUENCE_LENGTH * vocabulary_size * i13.EMBEDDING_WIDTH == 36864000
    assert i13.SEQUENCE_LENGTH * vocabulary_size * (i13.EMBEDDING_WIDTH - 1) == 36736000
    assert i13.SEQUENCE_LENGTH * vocabulary_size * i13.Q8_BLOCKS_PER_ROW == 1152000


def test_full_linear_work_geometry_includes_terminal_projection() -> None:
    assert 71424 + 128000 == 199424
    assert 23887872 + 36864000 == 60751872
    assert 23816448 + 36736000 == 60552448


def test_float_authority_is_rejected() -> None:
    with pytest.raises(i13.Pass215Iteration13ValidationError, match="PASS215_I13_FLOAT_FORBIDDEN"):
        i13._reject_floats({"bad": 1.25})
