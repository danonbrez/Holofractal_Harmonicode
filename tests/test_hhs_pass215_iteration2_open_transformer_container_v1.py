from __future__ import annotations

from copy import deepcopy
import json
import struct

import pytest

from hhs_backend.runtime.hhs_pass215_iteration2_open_transformer_container_v1 import (
    Pass215Iteration2ValidationError,
    STORAGE_FLOAT_OPAQUE,
    STORAGE_INTEGER,
    STORAGE_QUANTIZED,
    build_container_evidence,
    parse_gguf,
    parse_safetensors,
    validate_container_evidence,
)


def _gguf_string(value: str) -> bytes:
    raw = value.encode("utf-8")
    return struct.pack("<Q", len(raw)) + raw


def _build_gguf_fixture(*, overlap: bool = False, unsupported_type: bool = False) -> bytes:
    metadata = bytearray()
    metadata += _gguf_string("general.architecture")
    metadata += struct.pack("<I", 8)  # GGUF_TYPE_STRING
    metadata += _gguf_string("llama")
    metadata += _gguf_string("general.alignment")
    metadata += struct.pack("<I", 4)  # GGUF_TYPE_UINT32
    metadata += struct.pack("<I", 32)

    infos = bytearray()
    infos += _gguf_string("blk.0.attn_q.weight")
    infos += struct.pack("<I", 1)
    infos += struct.pack("<Q", 32)
    infos += struct.pack("<I", 99 if unsupported_type else 2)  # Q4_0
    infos += struct.pack("<Q", 0)
    infos += _gguf_string("output_norm.weight")
    infos += struct.pack("<I", 1)
    infos += struct.pack("<Q", 2)
    infos += struct.pack("<I", 0)  # F32, opaque only
    infos += struct.pack("<Q", 8 if overlap else 32)

    prefix = b"GGUF" + struct.pack("<IQQ", 3, 2, 2) + bytes(metadata) + bytes(infos)
    data_start = (len(prefix) + 31) // 32 * 32
    raw = bytearray(prefix + b"\x00" * (data_start - len(prefix)))
    raw += bytes(range(18))  # one Q4_0 block
    raw += b"\x00" * 14
    raw += bytes.fromhex("0000803f00000040")  # stored F32 bit patterns; never interpreted
    return bytes(raw)


def _build_safetensors_fixture(*, overlap: bool = False) -> bytes:
    header = {
        "int.weight": {"dtype": "I8", "shape": [4], "data_offsets": [0, 4]},
        "float.weight": {
            "dtype": "F32",
            "shape": [2],
            "data_offsets": [2 if overlap else 4, 10 if overlap else 12],
        },
        "__metadata__": {"format": "pt", "note": "opaque float storage test"},
    }
    header_raw = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    data = b"\x01\x02\x03\x04" + bytes.fromhex("0000803f00000040")
    return len(header_raw).to_bytes(8, "little") + header_raw + data


def test_gguf_preserves_quantized_and_float_storage_without_float_semantics() -> None:
    raw = _build_gguf_fixture()
    parsed = parse_gguf(raw)
    assert parsed.format == "GGUF"
    assert parsed.version == 3
    assert parsed.architecture == "llama"
    assert parsed.alignment == 32
    assert len(parsed.tensors) == 2
    first, second = parsed.tensors
    assert first.storage_type == "Q4_0"
    assert first.storage_class == STORAGE_QUANTIZED
    assert first.data_size == 18
    assert first.block_elements == 32
    assert first.block_bytes == 18
    assert second.storage_type == "F32"
    assert second.storage_class == STORAGE_FLOAT_OPAQUE
    assert second.data_size == 8


def test_gguf_rejects_overlap_and_uncontracted_type() -> None:
    with pytest.raises(Pass215Iteration2ValidationError, match="TENSOR_OVERLAP"):
        parse_gguf(_build_gguf_fixture(overlap=True))
    with pytest.raises(Pass215Iteration2ValidationError, match="GGML_TYPE_UNSUPPORTED"):
        parse_gguf(_build_gguf_fixture(unsupported_type=True))


def test_safetensors_preserves_integer_and_opaque_float_ranges() -> None:
    parsed = parse_safetensors(_build_safetensors_fixture())
    assert parsed.format == "SAFETENSORS"
    assert len(parsed.tensors) == 2
    classes = {tensor.name: tensor.storage_class for tensor in parsed.tensors}
    assert classes == {
        "float.weight": STORAGE_FLOAT_OPAQUE,
        "int.weight": STORAGE_INTEGER,
    }
    assert sum(tensor.data_size for tensor in parsed.tensors) == 12


def test_safetensors_rejects_overlapping_ranges() -> None:
    with pytest.raises(Pass215Iteration2ValidationError, match="TENSOR_OVERLAP"):
        parse_safetensors(_build_safetensors_fixture(overlap=True))


def test_container_evidence_separates_storage_and_canonical_streams() -> None:
    raw = _build_gguf_fixture()
    evidence = build_container_evidence(
        raw,
        filename="fixture.gguf",
        source={"kind": "repository_generated_fixture", "repo_id": None, "revision": None},
        expected_sha256=None,
    )
    validate_container_evidence(evidence)
    accounting = evidence["accounting"]
    assert accounting["tensor_payload_bytes"] == 26
    assert accounting["canonical_quantized_or_integer_tensor_bytes"] == 18
    assert accounting["opaque_float_tensor_bytes"] == 8
    assert evidence["storage_stream_measurement"]["source_bytes"] == 26
    assert evidence["canonical_quantized_stream_measurement"]["source_bytes"] == 18
    assert evidence["claims"]["canonical_quantized_subset_bit_exact_reproduction"] is True
    assert evidence["claims"]["full_network_canonical_reproduction"] is False
    assert evidence["claims"]["canonical_float_interpretation_performed"] is False


def test_container_evidence_rejects_digest_mismatch_and_tampering() -> None:
    raw = _build_gguf_fixture()
    with pytest.raises(Pass215Iteration2ValidationError, match="SOURCE_SHA256_MISMATCH"):
        build_container_evidence(
            raw,
            filename="fixture.gguf",
            source={"kind": "repository_generated_fixture"},
            expected_sha256="0" * 64,
        )
    evidence = build_container_evidence(
        raw,
        filename="fixture.gguf",
        source={"kind": "repository_generated_fixture"},
    )
    changed = deepcopy(evidence)
    changed["accounting"]["opaque_float_tensor_bytes"] += 1
    with pytest.raises(Pass215Iteration2ValidationError):
        validate_container_evidence(changed)


def test_evidence_contains_no_json_float_numbers() -> None:
    evidence = build_container_evidence(
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
