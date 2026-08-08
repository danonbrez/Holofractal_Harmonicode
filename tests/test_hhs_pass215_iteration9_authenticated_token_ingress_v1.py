from __future__ import annotations

import struct

import pytest

from hhs_backend.runtime import hhs_pass215_iteration2_open_transformer_container_v1 as i2
from hhs_backend.runtime import hhs_pass215_iteration8_multi_token_causal_attention_v1 as i8
from hhs_backend.runtime import hhs_pass215_iteration9_authenticated_token_ingress_v1 as i9


def _s(value: str) -> bytes:
    raw = value.encode("utf-8")
    return struct.pack("<Q", len(raw)) + raw


def _metadata_entry(key: str, value_type: int, payload: bytes) -> bytes:
    return _s(key) + struct.pack("<I", value_type) + payload


def _tokenizer_header() -> bytes:
    entries = []
    tokens = ("<unk>", "<s>", "</s>", "hello")
    token_payload = struct.pack("<IQ", i2._GGUF_STRING, len(tokens)) + b"".join(_s(value) for value in tokens)
    entries.append(_metadata_entry(i9.TOKEN_ARRAY_KEY, i2._GGUF_ARRAY, token_payload))
    type_payload = struct.pack("<IQ", i2._GGUF_INT32, len(tokens)) + b"".join(struct.pack("<i", value) for value in (2, 3, 3, 1))
    entries.append(_metadata_entry(i9.TOKEN_TYPE_ARRAY_KEY, i2._GGUF_ARRAY, type_payload))
    entries.append(_metadata_entry(i9.TOKENIZER_MODEL_KEY, i2._GGUF_STRING, _s("llama")))
    entries.append(_metadata_entry("tokenizer.ggml.bos_token_id", i2._GGUF_UINT32, struct.pack("<I", 1)))
    entries.append(_metadata_entry("tokenizer.ggml.eos_token_id", i2._GGUF_UINT32, struct.pack("<I", 2)))
    entries.append(_metadata_entry("tokenizer.ggml.unknown_token_id", i2._GGUF_UINT32, struct.pack("<I", 0)))
    # Unselected float scores are consumed through frozen opaque-bit parsing.
    scores = struct.pack("<IQ", i2._GGUF_FLOAT32, 4) + b"\x00\x00\x80\x3f" * 4
    entries.append(_metadata_entry("tokenizer.ggml.scores", i2._GGUF_ARRAY, scores))
    entries.append(_metadata_entry("tokenizer.ggml.add_bos_token", i2._GGUF_BOOL, b"\x01"))
    return b"GGUF" + struct.pack("<IQQ", 3, 1, len(entries)) + b"".join(entries)


def test_iteration8_frozen_binding_is_exact() -> None:
    bindings = i9._iteration8_bindings()
    assert bindings["iteration8_closure_head"] == "a1deea46accf94dac0322d215e74a1e6616a4e1b"
    assert bindings["iteration8_closure_tree"] == "4ec05cb3f6555005220098a55cab1dec0e0dfa61"
    assert bindings["iteration8_suite_root_hash216"] == "a21a7aedf633678510a701f93b39f785ce50c599228a6c194473ae6faea35b71"
    assert bindings["iteration8_evidence_root_hash216"] == "8ae3bdfb8768c37dfd4c66a491b985b3089378c655a7292ee406bbaa615c8465"
    assert bindings["iteration8_receipt_hash72"] == i9.ITERATION8_RECEIPT_HASH72


def test_selected_tokenizer_reader_materializes_only_safe_fields() -> None:
    metadata = i9._read_tokenizer_metadata(_tokenizer_header())
    assert metadata["tokenizer_model"] == "llama"
    assert metadata["vocabulary_size"] == 4
    assert metadata["tokens"] == ("<unk>", "<s>", "</s>", "hello")
    assert metadata["token_types"] == (2, 3, 3, 1)
    assert metadata["special_token_ids"]["tokenizer.ggml.bos_token_id"] == 1
    assert metadata["boolean_metadata"]["tokenizer.ggml.add_bos_token"] is True
    assert metadata["float_metadata_interpreted"] is False
    assert isinstance(metadata["vocabulary_root_hash216"], str)
    assert len(metadata["vocabulary_root_hash216"]) == 64


def test_token_selection_prefers_unique_specials_then_lowest_unused() -> None:
    metadata = i9._read_tokenizer_metadata(_tokenizer_header())
    assert i9._select_token_ids(metadata) == (1, 2, 0, 3)


def test_token_selection_rejects_small_vocabulary() -> None:
    with pytest.raises(i9.Pass215Iteration9ValidationError, match="VOCABULARY_TOO_SMALL"):
        i9._select_token_ids({"vocabulary_size": 3, "special_token_ids": {}})


def test_q4_embedding_row_decodes_exact_rational_coordinates() -> None:
    block = b"\x00\x3c" + b"\x98" * 16  # scale 1; low nibbles -> 0, high -> 1
    row = i9._decode_q4_0_embedding_row(block * 9)
    assert len(row) == 288
    for block_index in range(9):
        start = block_index * 32
        assert row[start:start + 16] == ((0, 1),) * 16
        assert row[start + 16:start + 32] == ((1, 1),) * 16


def test_q4_embedding_row_rejects_wrong_byte_geometry() -> None:
    with pytest.raises(i9.Pass215Iteration9ValidationError, match="ROW_BYTE_GEOMETRY"):
        i9._decode_q4_0_embedding_row(b"\x00" * (i9.Q4_0_ROW_BYTES - 1))


def test_embedding_row_geometry_matches_frozen_q4_layout() -> None:
    assert i9.EMBEDDING_WIDTH == 288
    assert i9.Q4_0_ROW_BYTES == 162
    assert i9.Q4_0_ROW_BYTES == (288 // 32) * 18


def test_iteration8_causal_work_geometry_is_preserved() -> None:
    work = i8._attention_work_geometry()
    assert work["causal_qk_edges"] == 60
    assert work["qk_dot_logical_products"] == 2880
    assert work["softmax_shifted_exponentials"] == 36
    assert work["weighted_value_logical_products"] == 2880
    assert work["rope_nonzero_position_pair_rotations_q_and_k"] == 864


def test_float_evidence_authority_fails_closed() -> None:
    with pytest.raises(i9.Pass215Iteration9ValidationError, match="FLOAT_FORBIDDEN"):
        i9._reject_floats({"bad": 1.0})
