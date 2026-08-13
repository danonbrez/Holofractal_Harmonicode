from __future__ import annotations

from copy import deepcopy
import struct

import pytest

from hhs_backend.runtime.hhs_pass215_iteration2_open_transformer_container_v1 import (
    STORAGE_QUANTIZED,
    ContainerTensor,
)
from hhs_backend.runtime.hhs_pass215_iteration3_quant_block_structure_v1 import (
    RAW_BLOCK_STREAM,
    SPLIT_SCALE_CODE_DICTIONARY,
    WHOLE_BLOCK_DICTIONARY,
    Pass215Iteration3ValidationError,
    SUPPORTED_LAYOUTS,
    analyze_tensor,
    build_block_structure_evidence,
    decode_fixed_dictionary,
    decompose_blocks,
    encode_fixed_dictionary,
    validate_block_structure_evidence,
)


def _gguf_string(value: str) -> bytes:
    raw = value.encode("utf-8")
    return struct.pack("<Q", len(raw)) + raw


def _align(value: int, alignment: int = 32) -> int:
    return (value + alignment - 1) // alignment * alignment


def _build_gguf_fixture(*, include_unsupported: bool = False) -> bytes:
    metadata = bytearray()
    metadata += _gguf_string("general.architecture")
    metadata += struct.pack("<I", 8)
    metadata += _gguf_string("llama")
    metadata += _gguf_string("general.alignment")
    metadata += struct.pack("<I", 4)
    metadata += struct.pack("<I", 32)

    q4_blocks = []
    for index in range(100):
        scale = b"\x34\x12"
        code = bytes((index,)) + b"\xa5" * 15
        q4_blocks.append(scale + code)
    q4_payload = b"".join(q4_blocks)
    q8_block = b"\x78\x56" + bytes(range(32))
    q8_payload = q8_block * 10
    f32_payload = bytes.fromhex("0000803f00000040")
    q4k_payload = bytes(range(144)) if include_unsupported else b""

    tensor_defs = [
        ("blk.0.attn_q.weight", 3200, 2, q4_payload),
        ("blk.1.attn_v.weight", 320, 8, q8_payload),
        ("output_norm.weight", 2, 0, f32_payload),
    ]
    if include_unsupported:
        tensor_defs.append(("blk.1.ffn_gate.weight", 256, 12, q4k_payload))

    relative_offsets = []
    cursor = 0
    for _, _, _, payload in tensor_defs:
        cursor = _align(cursor)
        relative_offsets.append(cursor)
        cursor += len(payload)

    infos = bytearray()
    for (name, elements, type_code, _), offset in zip(tensor_defs, relative_offsets):
        infos += _gguf_string(name)
        infos += struct.pack("<I", 1)
        infos += struct.pack("<Q", elements)
        infos += struct.pack("<I", type_code)
        infos += struct.pack("<Q", offset)

    prefix = b"GGUF" + struct.pack("<IQQ", 3, len(tensor_defs), 2) + bytes(metadata) + bytes(infos)
    data_start = _align(len(prefix))
    raw = bytearray(prefix + b"\x00" * (data_start - len(prefix)))
    data = bytearray(cursor)
    for (_, _, _, payload), offset in zip(tensor_defs, relative_offsets):
        data[offset : offset + len(payload)] = payload
    raw += data
    return bytes(raw)


def _tensor(name: str, storage_type: str, raw: bytes) -> ContainerTensor:
    layout = SUPPORTED_LAYOUTS[storage_type]
    import hashlib
    return ContainerTensor(
        name=name,
        shape=(len(raw) // layout.block_bytes * layout.block_elements,),
        storage_type=storage_type,
        storage_type_code=2 if storage_type == "Q4_0" else 8,
        storage_class=STORAGE_QUANTIZED,
        data_offset=0,
        data_size=len(raw),
        source_sha256=hashlib.sha256(raw).hexdigest(),
        block_elements=layout.block_elements,
        block_bytes=layout.block_bytes,
        header_index=0,
    )


def test_fixed_dictionary_round_trip_and_first_occurrence_order() -> None:
    items = [b"aa", b"bb", b"aa", b"cc", b"bb"]
    encoded = encode_fixed_dictionary(items, item_size=2)
    assert encoded.unique_values == (b"aa", b"bb", b"cc")
    recovered, consumed = decode_fixed_dictionary(encoded.encoded)
    assert recovered == tuple(items)
    assert consumed == len(encoded.encoded)
    assert encoded.index_width == 1


def test_q4_q8_block_decomposition_is_bit_exact() -> None:
    q4 = (b"\x01\x02" + b"\x03" * 16) * 3
    q8 = (b"\x04\x05" + b"\x06" * 32) * 2
    q4_result = decompose_blocks(q4, SUPPORTED_LAYOUTS["Q4_0"])
    q8_result = decompose_blocks(q8, SUPPORTED_LAYOUTS["Q8_0"])
    assert q4_result.reconstruct() == q4
    assert q8_result.reconstruct() == q8
    assert len(q4_result.scale_stream) == 6
    assert len(q4_result.code_stream) == 48
    assert len(q8_result.scale_stream) == 4
    assert len(q8_result.code_stream) == 64


def test_predeclared_candidate_selection_preserves_losing_costs() -> None:
    repeated_block = b"\x01\x02" + b"\x03" * 16
    whole_raw = repeated_block * 100
    whole_result = analyze_tensor(_tensor("blk.0.repeat.weight", "Q4_0", whole_raw), whole_raw)
    assert whole_result["selected_representation"] == WHOLE_BLOCK_DICTIONARY
    assert whole_result["candidate_encoded_bytes"][RAW_BLOCK_STREAM] == len(whole_raw)
    assert whole_result["candidate_encoded_bytes"][SPLIT_SCALE_CODE_DICTIONARY] > whole_result["selected_encoded_bytes"]

    split_blocks = []
    for index in range(100):
        split_blocks.append(b"\x34\x12" + bytes((index,)) + b"\xa5" * 15)
    split_raw = b"".join(split_blocks)
    split_result = analyze_tensor(_tensor("blk.1.split.weight", "Q4_0", split_raw), split_raw)
    assert split_result["selected_representation"] == SPLIT_SCALE_CODE_DICTIONARY
    assert split_result["selected_encoded_bytes"] < len(split_raw)
    assert split_result["whole_block_dictionary"]["encoded_bytes"] > len(split_raw)


def test_raw_wins_tie_or_dictionary_overhead() -> None:
    raw = b"\x01\x02" + bytes(range(16))
    result = analyze_tensor(_tensor("output.weight", "Q4_0", raw), raw)
    assert result["selected_representation"] == RAW_BLOCK_STREAM
    assert result["selected_encoded_bytes"] == len(raw)


def test_realistic_fixture_builds_layer_and_passthrough_accounting() -> None:
    raw = _build_gguf_fixture(include_unsupported=True)
    evidence = build_block_structure_evidence(
        raw,
        filename="fixture.gguf",
        source={"kind": "repository_generated_fixture", "repo_id": None, "revision": None},
    )
    validate_block_structure_evidence(evidence)
    assert evidence["container"]["format"] == "GGUF"
    assert evidence["global"]["supported_tensor_count"] == 2
    assert evidence["global"]["semantic_exactness"] is True
    assert evidence["global"]["unsupported_passthrough_bytes"] == 144
    assert evidence["global"]["opaque_float_storage_bytes_excluded"] == 8
    assert {item["layer"] for item in evidence["per_layer"]} == {"blk.0", "blk.1"}
    assert any(item["reason"] == "QUANTIZED_LAYOUT_UNCONTRACTED_PASSTHROUGH" for item in evidence["unsupported_passthrough"])
    assert evidence["claims"]["canonical_float_interpretation_performed"] is False
    assert evidence["authority"]["runtime_mutation_authority_promoted"] is False


def test_evidence_tamper_and_digest_mismatch_fail_closed() -> None:
    raw = _build_gguf_fixture()
    with pytest.raises(Pass215Iteration3ValidationError, match="SOURCE_SHA256_MISMATCH"):
        build_block_structure_evidence(
            raw,
            filename="fixture.gguf",
            source={"kind": "repository_generated_fixture"},
            expected_sha256="0" * 64,
        )
    evidence = build_block_structure_evidence(
        raw,
        filename="fixture.gguf",
        source={"kind": "repository_generated_fixture"},
    )
    changed = deepcopy(evidence)
    changed["global"]["selected_gain_bytes_vs_raw"] += 1
    with pytest.raises(Pass215Iteration3ValidationError):
        validate_block_structure_evidence(changed)


def test_evidence_contains_no_json_float_numbers() -> None:
    evidence = build_block_structure_evidence(
        _build_gguf_fixture(),
        filename="fixture.gguf",
        source={"kind": "repository_generated_fixture"},
    )

    def walk(value):
        assert not isinstance(value, float)
        if isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(evidence)
