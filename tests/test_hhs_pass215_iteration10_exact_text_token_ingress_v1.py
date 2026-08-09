from __future__ import annotations

import struct

import pytest

from hhs_backend.runtime import hhs_pass215_iteration2_open_transformer_container_v1 as i2
from hhs_backend.runtime import hhs_pass215_iteration10_exact_text_token_ingress_v1 as i10


def _s(value: str) -> bytes:
    raw = value.encode("utf-8")
    return struct.pack("<Q", len(raw)) + raw


def _entry(key: str, value_type: int, payload: bytes) -> bytes:
    return _s(key) + struct.pack("<I", value_type) + payload


def _minimal_tokenizer_header() -> bytes:
    tokens = ("<unk>", "<s>", "</s>", "▁", "a", "▁a", "b", "▁b", "!")
    entries: list[bytes] = []
    token_payload = struct.pack("<IQ", i2._GGUF_STRING, len(tokens)) + b"".join(_s(value) for value in tokens)
    entries.append(_entry("tokenizer.ggml.tokens", i2._GGUF_ARRAY, token_payload))
    type_payload = struct.pack("<IQ", i2._GGUF_INT32, len(tokens)) + b"".join(
        struct.pack("<i", value) for value in (2, 3, 3, 1, 1, 1, 1, 1, 1)
    )
    entries.append(_entry("tokenizer.ggml.token_type", i2._GGUF_ARRAY, type_payload))
    score_values = (0.0, 0.0, 0.0, -4.0, -3.0, 1.0, -3.0, 1.0, 0.5)
    score_payload = struct.pack("<IQ", i2._GGUF_FLOAT32, len(tokens)) + b"".join(struct.pack("<f", value) for value in score_values)
    entries.append(_entry("tokenizer.ggml.scores", i2._GGUF_ARRAY, score_payload))
    entries.append(_entry("tokenizer.ggml.model", i2._GGUF_STRING, _s("llama")))
    entries.append(_entry("tokenizer.ggml.bos_token_id", i2._GGUF_UINT32, struct.pack("<I", 1)))
    entries.append(_entry("tokenizer.ggml.eos_token_id", i2._GGUF_UINT32, struct.pack("<I", 2)))
    entries.append(_entry("tokenizer.ggml.unknown_token_id", i2._GGUF_UINT32, struct.pack("<I", 0)))
    entries.append(_entry("tokenizer.ggml.padding_token_id", i2._GGUF_UINT32, struct.pack("<I", 0xFFFFFFFF)))
    entries.append(_entry("tokenizer.ggml.add_bos_token", i2._GGUF_BOOL, b"\x01"))
    entries.append(_entry("tokenizer.ggml.add_eos_token", i2._GGUF_BOOL, b"\x00"))
    entries.append(_entry("tokenizer.ggml.add_space_prefix", i2._GGUF_BOOL, b"\x01"))
    return b"GGUF" + struct.pack("<IQQ", 3, 1, len(entries)) + b"".join(entries)


def _synthetic_tokenizer() -> dict:
    tokens = ("<unk>", "<s>", "</s>", "▁", "a", "▁a", "b", "▁b", "!")
    score_pairs = ((0, 1), (0, 1), (0, 1), (-4, 1), (-3, 1), (1, 1), (-3, 1), (1, 1), (1, 2))
    return {
        "tokenizer_model": "llama",
        "tokens": tokens,
        "token_types": (2, 3, 3, 1, 1, 1, 1, 1, 1),
        "vocabulary_size": len(tokens),
        "score_pairs": score_pairs,
        "score_bits": tuple(f"{index:08x}" for index in range(len(tokens))),
        "special_token_ids": {
            "tokenizer.ggml.bos_token_id": 1,
            "tokenizer.ggml.eos_token_id": 2,
            "tokenizer.ggml.unknown_token_id": 0,
        },
        "inactive_special_token_ids": {"tokenizer.ggml.padding_token_id": 0xFFFFFFFF},
        "boolean_metadata": {
            "tokenizer.ggml.add_bos_token": True,
            "tokenizer.ggml.add_eos_token": False,
        },
        "normalization_boolean_metadata": {"tokenizer.ggml.add_space_prefix": True},
        "precompiled_charsmap_present": False,
    }


def test_iteration9_frozen_binding_is_exact() -> None:
    bindings = i10._iteration9_bindings()
    assert bindings["iteration9_closure_head"] == "8a9ca8907edb94d84ce828639145b94a119c2571"
    assert bindings["iteration9_closure_tree"] == "cc40fca257d1265882cdc3973205a6962117eb40"
    assert bindings["iteration9_suite_root_hash216"] == "5f544e489fb05cf6675e6034a9acf552d53e1dd83801c6941384de868d9e4a94"
    assert bindings["iteration9_evidence_root_hash216"] == "71e36d07d2e5c016cfdae8356eb50abb5d750aefc796a2ad3f413d0391d06261"


def test_binary32_decoder_is_exact_for_normal_values() -> None:
    assert i10.decode_binary32_exact(bytes.fromhex("0000c03f")) == (3, 2)
    assert i10.decode_binary32_exact(bytes.fromhex("000000bf")) == (-1, 2)
    assert i10.decode_binary32_exact(bytes.fromhex("00000000")) == (0, 1)
    assert i10.decode_binary32_exact(bytes.fromhex("00000080")) == (0, 1)


def test_binary32_decoder_preserves_smallest_subnormal_exactly() -> None:
    numerator, denominator = i10.decode_binary32_exact(bytes.fromhex("01000000"))
    assert numerator == 1
    assert denominator == 1 << 149


def test_binary32_decoder_rejects_nonfinite_storage() -> None:
    with pytest.raises(i10.Pass215Iteration10ValidationError, match="NONFINITE"):
        i10.decode_binary32_exact(bytes.fromhex("0000807f"))
    with pytest.raises(i10.Pass215Iteration10ValidationError, match="NONFINITE"):
        i10.decode_binary32_exact(bytes.fromhex("0100807f"))


def test_exact_rational_score_comparison_uses_no_float() -> None:
    assert i10._compare_pairs((3, 2), (4, 3)) == 1
    assert i10._compare_pairs((-3, 2), (-4, 3)) == -1
    assert i10._compare_pairs((2, 4), (1, 2)) == 0


def test_selected_score_reader_binds_bits_and_exact_rationals() -> None:
    metadata = i10._read_exact_tokenizer_metadata(_minimal_tokenizer_header())
    assert metadata["tokenizer_model"] == "llama"
    assert metadata["score_count"] == metadata["vocabulary_size"] == 9
    assert metadata["score_pairs"][5] == (1, 1)
    assert metadata["score_float_interpretation_performed"] is False
    assert metadata["inactive_special_token_ids"]["tokenizer.ggml.padding_token_id"] == 0xFFFFFFFF
    assert len(metadata["score_storage_bits_root_hash216"]) == 64
    assert len(metadata["exact_score_root_hash216"]) == 64


def test_contracted_normalization_adds_sentencepiece_space_marker() -> None:
    tokenizer = _synthetic_tokenizer()
    policy = i10._normalization_policy(tokenizer)
    normalized, mode = i10._normalize_contracted_text("a b!", policy, tokenizer["tokens"])
    assert normalized == "▁a▁b!"
    assert mode == "U+2581"


def test_sentencepiece_pair_merge_uses_exact_scores_and_bos() -> None:
    result = i10._tokenize_sentencepiece_bpe("a b!", _synthetic_tokenizer())
    assert result["normalized_text"] == "▁a▁b!"
    assert result["token_ids"] == [1, 5, 7, 8]
    assert result["tokens"] == ["<s>", "▁a", "▁b", "!"]
    assert result["token_count"] == 4
    assert result["score_float_interpretation_performed"] is False


def test_equal_score_pair_merge_tie_breaks_to_smaller_left_position() -> None:
    tokenizer = {
        "tokenizer_model": "llama",
        "tokens": ("<unk>", "a", "b", "c", "ab", "bc"),
        "token_types": (2, 1, 1, 1, 1, 1),
        "vocabulary_size": 6,
        "score_pairs": ((0, 1), (0, 1), (0, 1), (0, 1), (1, 1), (1, 1)),
        "score_bits": ("00000000",) * 6,
        "special_token_ids": {"tokenizer.ggml.unknown_token_id": 0},
        "inactive_special_token_ids": {},
        "boolean_metadata": {"tokenizer.ggml.add_bos_token": False, "tokenizer.ggml.add_eos_token": False},
        "normalization_boolean_metadata": {"tokenizer.ggml.add_space_prefix": False},
        "precompiled_charsmap_present": False,
    }
    result = i10._tokenize_sentencepiece_bpe("abc", tokenizer)
    assert result["merge_trace"][0]["piece"] == "ab"
    assert result["token_ids"] == [4, 3]


def test_byte_fallback_is_source_vocabulary_bound() -> None:
    tokens = ("<unk>", "<0x78>")
    tokenizer = {
        "tokenizer_model": "llama",
        "tokens": tokens,
        "token_types": (2, 6),
        "vocabulary_size": 2,
        "score_pairs": ((0, 1), (0, 1)),
        "score_bits": ("00000000", "00000000"),
        "special_token_ids": {"tokenizer.ggml.unknown_token_id": 0},
        "inactive_special_token_ids": {},
        "boolean_metadata": {"tokenizer.ggml.add_bos_token": False, "tokenizer.ggml.add_eos_token": False},
        "normalization_boolean_metadata": {"tokenizer.ggml.add_space_prefix": False},
        "precompiled_charsmap_present": False,
    }
    result = i10._tokenize_sentencepiece_bpe("x", tokenizer)
    assert result["token_ids"] == [1]
    assert result["core_token_records"][0]["fallback"] == "BYTE_OR_UNK"


def test_precompiled_charsmap_fails_closed_for_iteration10_scope() -> None:
    tokenizer = _synthetic_tokenizer()
    tokenizer["precompiled_charsmap_present"] = True
    with pytest.raises(i10.Pass215Iteration10ValidationError, match="PRECOMPILED_CHARMAP_UNSUPPORTED"):
        i10._normalization_policy(tokenizer)


def test_float_evidence_authority_fails_closed() -> None:
    with pytest.raises(i10.Pass215Iteration10ValidationError, match="FLOAT_FORBIDDEN"):
        i10._reject_floats({"bad": 1.0})
