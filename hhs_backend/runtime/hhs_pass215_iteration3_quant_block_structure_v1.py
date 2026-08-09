"""Pass 215 Iteration 3: reversible quantization-block decomposition.

This measurement layer decomposes supported GGUF quantized blocks into exact
scale/metadata bytes and packed code bytes, proves byte-exact reconstruction,
and attributes repeated structure using predeclared reversible dictionary
candidates. It does not interpret stored floating-point scale bits as canonical
numbers and cannot promote mutation authority.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import canonical_bytes, hash216
from hhs_backend.runtime.hhs_pass215_iteration1_transformer_ingestion_v1 import (
    FROZEN_PROFILE_GIT_BLOB_SHA1,
    PASS213_GATE_PRESERVATION_ROOT_HASH216,
    PASS214_AUTHORITY_ROOT_HASH216,
    PASS214_TERMINAL_RECEIPT_HASH72,
    PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    _exact_fraction,
)
from hhs_backend.runtime.hhs_pass215_iteration2_open_transformer_container_v1 import (
    STORAGE_FLOAT_OPAQUE,
    STORAGE_QUANTIZED,
    ContainerTensor,
    ParsedContainer,
    _measure_stream,
    build_container_evidence,
    parse_gguf,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest

CONTRACT = "HHS-P215-I3-REVERSIBLE-QUANTIZATION-BLOCK-DECOMPOSITION-STRUCTURE-ATTRIBUTION"
PASS_NUMBER = 215
ITERATION = 3
CONTRACT_VERSION = "1.0.0-iteration3"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_3_QUANTIZATION_BLOCK_STRUCTURE_ATTRIBUTION"
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_3_BLOCK_STRUCTURE_EVIDENCE_V1"
ITERATION2_EVIDENCE_ROOT_HASH216 = "0c18a5055b01bee0401d9ad0b3caba9c5d214d80a6dd809b190e106681b22e70"
ITERATION2_RECEIPT_HASH72 = "eazJ?HQncuTLTNwn9-UO!PSBI2I)GHgBuN/h75y2Iyi0Nkkd845iC+u/xb?o(CBRQ56DqKLz"
ITERATION2_CANONICAL_TENSOR_BYTES = 18_335_232
REAL_MODEL_SHA256 = "6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04"

RAW_BLOCK_STREAM = "RAW_BLOCK_STREAM"
WHOLE_BLOCK_DICTIONARY = "WHOLE_BLOCK_DICTIONARY_V1"
SPLIT_SCALE_CODE_DICTIONARY = "SPLIT_SCALE_CODE_DICTIONARY_V1"
_DICTIONARY_MAGIC = b"I3D1"
_DICTIONARY_HEADER_BYTES = 23


class Pass215Iteration3Error(RuntimeError):
    pass


class Pass215Iteration3ValidationError(Pass215Iteration3Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration3ValidationError(f"PASS215_I3_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _sha256(raw: bytes) -> str:
    return sha256(raw).hexdigest()


@dataclass(frozen=True)
class QuantBlockLayout:
    storage_type: str
    block_elements: int
    block_bytes: int
    scale_bytes: int
    code_bytes: int

    def to_dict(self) -> Mapping[str, int | str]:
        return {
            "storage_type": self.storage_type,
            "block_elements": self.block_elements,
            "block_bytes": self.block_bytes,
            "scale_bytes": self.scale_bytes,
            "code_bytes": self.code_bytes,
        }


SUPPORTED_LAYOUTS: Mapping[str, QuantBlockLayout] = {
    "Q4_0": QuantBlockLayout("Q4_0", 32, 18, 2, 16),
    "Q8_0": QuantBlockLayout("Q8_0", 32, 34, 2, 32),
}


@dataclass(frozen=True)
class DictionaryEncoding:
    item_size: int
    value_count: int
    unique_count: int
    index_width: int
    encoded: bytes
    unique_values: tuple[bytes, ...]

    def to_metrics(self) -> Mapping[str, Any]:
        return {
            "item_size": self.item_size,
            "value_count": self.value_count,
            "unique_count": self.unique_count,
            "repeated_occurrences": self.value_count - self.unique_count,
            "index_width_bytes": self.index_width,
            "header_bytes": _DICTIONARY_HEADER_BYTES,
            "dictionary_payload_bytes": self.unique_count * self.item_size,
            "reference_bytes": self.value_count * self.index_width,
            "encoded_bytes": len(self.encoded),
            "encoded_sha256": _sha256(self.encoded),
            "unique_fraction_exact": _exact_fraction(self.unique_count, self.value_count),
            "repeat_fraction_exact": _exact_fraction(self.value_count - self.unique_count, self.value_count),
        }


def _index_width(unique_count: int) -> int:
    if unique_count <= 0:
        raise Pass215Iteration3ValidationError("PASS215_I3_DICTIONARY_UNIQUE_COUNT_INVALID")
    if unique_count == 1:
        return 0
    return ((unique_count - 1).bit_length() + 7) // 8


def encode_fixed_dictionary(items: Sequence[bytes], *, item_size: int) -> DictionaryEncoding:
    if item_size <= 0 or item_size > 65535:
        raise Pass215Iteration3ValidationError("PASS215_I3_DICTIONARY_ITEM_SIZE_INVALID")
    if not items:
        raise Pass215Iteration3ValidationError("PASS215_I3_DICTIONARY_EMPTY")
    unique: list[bytes] = []
    lookup: dict[bytes, int] = {}
    indexes: list[int] = []
    for index, item in enumerate(items):
        value = bytes(item)
        if len(value) != item_size:
            raise Pass215Iteration3ValidationError(f"PASS215_I3_DICTIONARY_ITEM_LENGTH_INVALID:{index}")
        position = lookup.get(value)
        if position is None:
            position = len(unique)
            lookup[value] = position
            unique.append(value)
        indexes.append(position)
    width = _index_width(len(unique))
    encoded = bytearray()
    encoded += _DICTIONARY_MAGIC
    encoded += item_size.to_bytes(2, "little")
    encoded += len(items).to_bytes(8, "little")
    encoded += len(unique).to_bytes(8, "little")
    encoded += bytes((width,))
    for value in unique:
        encoded += value
    if width:
        for position in indexes:
            encoded += position.to_bytes(width, "little")
    result = DictionaryEncoding(
        item_size=item_size,
        value_count=len(items),
        unique_count=len(unique),
        index_width=width,
        encoded=bytes(encoded),
        unique_values=tuple(unique),
    )
    recovered, consumed = decode_fixed_dictionary(result.encoded)
    if consumed != len(result.encoded) or tuple(recovered) != tuple(bytes(item) for item in items):
        raise Pass215Iteration3ValidationError("PASS215_I3_DICTIONARY_ROUND_TRIP_FAILED")
    return result


def decode_fixed_dictionary(raw: bytes, *, offset: int = 0) -> tuple[tuple[bytes, ...], int]:
    if offset < 0 or offset + _DICTIONARY_HEADER_BYTES > len(raw):
        raise Pass215Iteration3ValidationError("PASS215_I3_DICTIONARY_TRUNCATED")
    if raw[offset : offset + 4] != _DICTIONARY_MAGIC:
        raise Pass215Iteration3ValidationError("PASS215_I3_DICTIONARY_MAGIC_INVALID")
    cursor = offset + 4
    item_size = int.from_bytes(raw[cursor : cursor + 2], "little")
    cursor += 2
    value_count = int.from_bytes(raw[cursor : cursor + 8], "little")
    cursor += 8
    unique_count = int.from_bytes(raw[cursor : cursor + 8], "little")
    cursor += 8
    index_width = raw[cursor]
    cursor += 1
    if item_size <= 0 or value_count <= 0 or unique_count <= 0 or unique_count > value_count:
        raise Pass215Iteration3ValidationError("PASS215_I3_DICTIONARY_HEADER_INVALID")
    if index_width != _index_width(unique_count):
        raise Pass215Iteration3ValidationError("PASS215_I3_DICTIONARY_INDEX_WIDTH_INVALID")
    dictionary_bytes = unique_count * item_size
    reference_bytes = value_count * index_width
    end = cursor + dictionary_bytes + reference_bytes
    if end > len(raw):
        raise Pass215Iteration3ValidationError("PASS215_I3_DICTIONARY_TRUNCATED")
    unique = tuple(
        raw[cursor + index * item_size : cursor + (index + 1) * item_size]
        for index in range(unique_count)
    )
    cursor += dictionary_bytes
    if index_width == 0:
        result = (unique[0],) * value_count
    else:
        values: list[bytes] = []
        for index in range(value_count):
            start = cursor + index * index_width
            position = int.from_bytes(raw[start : start + index_width], "little")
            if position >= unique_count:
                raise Pass215Iteration3ValidationError("PASS215_I3_DICTIONARY_REFERENCE_INVALID")
            values.append(unique[position])
        result = tuple(values)
    return result, end


@dataclass(frozen=True)
class DecomposedBlocks:
    layout: QuantBlockLayout
    blocks: tuple[bytes, ...]
    scales: tuple[bytes, ...]
    codes: tuple[bytes, ...]

    @property
    def raw(self) -> bytes:
        return b"".join(self.blocks)

    @property
    def scale_stream(self) -> bytes:
        return b"".join(self.scales)

    @property
    def code_stream(self) -> bytes:
        return b"".join(self.codes)

    def reconstruct(self) -> bytes:
        if not (len(self.blocks) == len(self.scales) == len(self.codes)):
            raise Pass215Iteration3ValidationError("PASS215_I3_BLOCK_VECTOR_LENGTH_MISMATCH")
        return b"".join(scale + code for scale, code in zip(self.scales, self.codes))


def decompose_blocks(raw: bytes, layout: QuantBlockLayout) -> DecomposedBlocks:
    if layout.scale_bytes + layout.code_bytes != layout.block_bytes:
        raise Pass215Iteration3ValidationError("PASS215_I3_LAYOUT_GEOMETRY_INVALID")
    if not raw or len(raw) % layout.block_bytes:
        raise Pass215Iteration3ValidationError("PASS215_I3_BLOCK_STREAM_GEOMETRY_INVALID")
    blocks = tuple(raw[index : index + layout.block_bytes] for index in range(0, len(raw), layout.block_bytes))
    scales = tuple(block[: layout.scale_bytes] for block in blocks)
    codes = tuple(block[layout.scale_bytes :] for block in blocks)
    result = DecomposedBlocks(layout=layout, blocks=blocks, scales=scales, codes=codes)
    if result.reconstruct() != raw:
        raise Pass215Iteration3ValidationError("PASS215_I3_BLOCK_RECONSTRUCTION_FAILED")
    return result


def _repeat_metrics(items: Sequence[bytes], *, item_size: int) -> Mapping[str, Any]:
    if not items:
        raise Pass215Iteration3ValidationError("PASS215_I3_REPEAT_SET_EMPTY")
    counts = Counter(bytes(item) for item in items)
    unique_count = len(counts)
    repeated_occurrences = len(items) - unique_count
    return {
        "item_size": item_size,
        "value_count": len(items),
        "unique_count": unique_count,
        "repeated_occurrences": repeated_occurrences,
        "repeated_distinct_values": sum(1 for count in counts.values() if count > 1),
        "maximum_multiplicity": max(counts.values()),
        "exact_repeat_source_bytes": repeated_occurrences * item_size,
        "unique_fraction_exact": _exact_fraction(unique_count, len(items)),
        "repeat_fraction_exact": _exact_fraction(repeated_occurrences, len(items)),
    }


def _layer_key(name: str) -> str:
    parts = name.split(".")
    if len(parts) >= 2 and parts[0] == "blk" and parts[1].isdigit():
        return f"blk.{int(parts[1])}"
    return "__non_layer__"


def analyze_tensor(tensor: ContainerTensor, raw: bytes) -> Mapping[str, Any]:
    layout = SUPPORTED_LAYOUTS.get(tensor.storage_type)
    if layout is None:
        raise Pass215Iteration3ValidationError(f"PASS215_I3_LAYOUT_UNSUPPORTED:{tensor.storage_type}:{tensor.name}")
    if tensor.block_elements != layout.block_elements or tensor.block_bytes != layout.block_bytes:
        raise Pass215Iteration3ValidationError(f"PASS215_I3_LAYOUT_BINDING_MISMATCH:{tensor.name}")
    if len(raw) != tensor.data_size or _sha256(raw) != tensor.source_sha256:
        raise Pass215Iteration3ValidationError(f"PASS215_I3_TENSOR_SOURCE_BINDING_MISMATCH:{tensor.name}")
    decomposed = decompose_blocks(raw, layout)
    scale_dictionary = encode_fixed_dictionary(decomposed.scales, item_size=layout.scale_bytes)
    code_dictionary = encode_fixed_dictionary(decomposed.codes, item_size=layout.code_bytes)
    whole_dictionary = encode_fixed_dictionary(decomposed.blocks, item_size=layout.block_bytes)
    split_encoded = scale_dictionary.encoded + code_dictionary.encoded
    recovered_scales, split_offset = decode_fixed_dictionary(split_encoded, offset=0)
    recovered_codes, split_end = decode_fixed_dictionary(split_encoded, offset=split_offset)
    reconstructed = b"".join(scale + code for scale, code in zip(recovered_scales, recovered_codes))
    if split_end != len(split_encoded) or reconstructed != raw:
        raise Pass215Iteration3ValidationError(f"PASS215_I3_SPLIT_RECONSTRUCTION_FAILED:{tensor.name}")
    recovered_blocks, whole_end = decode_fixed_dictionary(whole_dictionary.encoded)
    whole_reconstructed = b"".join(recovered_blocks)
    if whole_end != len(whole_dictionary.encoded) or whole_reconstructed != raw:
        raise Pass215Iteration3ValidationError(f"PASS215_I3_WHOLE_RECONSTRUCTION_FAILED:{tensor.name}")

    candidate_sizes = {
        RAW_BLOCK_STREAM: len(raw),
        WHOLE_BLOCK_DICTIONARY: len(whole_dictionary.encoded),
        SPLIT_SCALE_CODE_DICTIONARY: len(split_encoded),
    }
    rank = {RAW_BLOCK_STREAM: 0, WHOLE_BLOCK_DICTIONARY: 1, SPLIT_SCALE_CODE_DICTIONARY: 2}
    selected = min(candidate_sizes, key=lambda key: (candidate_sizes[key], rank[key]))
    selected_bytes = candidate_sizes[selected]
    result = {
        "name": tensor.name,
        "layer": _layer_key(tensor.name),
        "storage_type": tensor.storage_type,
        "shape": list(tensor.shape),
        "source_bytes": len(raw),
        "source_sha256": tensor.source_sha256,
        "block_count": len(decomposed.blocks),
        "layout": layout.to_dict(),
        "scale_stream_bytes": len(decomposed.scale_stream),
        "scale_stream_sha256": _sha256(decomposed.scale_stream),
        "code_stream_bytes": len(decomposed.code_stream),
        "code_stream_sha256": _sha256(decomposed.code_stream),
        "scale_repeat_metrics": _repeat_metrics(decomposed.scales, item_size=layout.scale_bytes),
        "code_repeat_metrics": _repeat_metrics(decomposed.codes, item_size=layout.code_bytes),
        "whole_block_repeat_metrics": _repeat_metrics(decomposed.blocks, item_size=layout.block_bytes),
        "scale_dictionary": scale_dictionary.to_metrics(),
        "code_dictionary": code_dictionary.to_metrics(),
        "whole_block_dictionary": whole_dictionary.to_metrics(),
        "candidate_encoded_bytes": candidate_sizes,
        "selected_representation": selected,
        "selected_encoded_bytes": selected_bytes,
        "selected_gain_bytes_vs_raw": len(raw) - selected_bytes,
        "selected_ratio_exact": _exact_fraction(len(raw), selected_bytes),
        "split_reconstruction_sha256": _sha256(reconstructed),
        "whole_reconstruction_sha256": _sha256(whole_reconstructed),
        "semantic_exactness": reconstructed == raw == whole_reconstructed,
    }
    _reject_floats(result)
    return result


def _aggregate(records: Sequence[Mapping[str, Any]], *, key: str) -> list[Mapping[str, Any]]:
    groups: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        groups.setdefault(str(record[key]), []).append(record)
    output: list[Mapping[str, Any]] = []
    for group_name in sorted(groups):
        members = groups[group_name]
        raw_bytes = sum(int(item["source_bytes"]) for item in members)
        selected_bytes = sum(int(item["selected_encoded_bytes"]) for item in members)
        selected_counts = Counter(str(item["selected_representation"]) for item in members)
        output.append({
            key: group_name,
            "tensor_count": len(members),
            "block_count": sum(int(item["block_count"]) for item in members),
            "source_bytes": raw_bytes,
            "selected_encoded_bytes": selected_bytes,
            "selected_gain_bytes_vs_raw": raw_bytes - selected_bytes,
            "selected_ratio_exact": _exact_fraction(raw_bytes, selected_bytes),
            "scale_stream_bytes": sum(int(item["scale_stream_bytes"]) for item in members),
            "code_stream_bytes": sum(int(item["code_stream_bytes"]) for item in members),
            "scale_repeat_source_bytes": sum(int(item["scale_repeat_metrics"]["exact_repeat_source_bytes"]) for item in members),
            "code_repeat_source_bytes": sum(int(item["code_repeat_metrics"]["exact_repeat_source_bytes"]) for item in members),
            "whole_block_repeat_source_bytes": sum(int(item["whole_block_repeat_metrics"]["exact_repeat_source_bytes"]) for item in members),
            "selected_representation_counts": dict(sorted(selected_counts.items())),
            "semantic_exactness": all(bool(item["semantic_exactness"]) for item in members),
        })
    return output


def build_block_structure_evidence(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
    frozen_profile_blob_sha1: str = FROZEN_PROFILE_GIT_BLOB_SHA1,
) -> Mapping[str, Any]:
    if frozen_profile_blob_sha1 != FROZEN_PROFILE_GIT_BLOB_SHA1:
        raise Pass215Iteration3ValidationError("PASS215_I3_FROZEN_PROFILE_BLOB_MISMATCH")
    _reject_floats(source)
    actual_sha = _sha256(raw)
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration3ValidationError("PASS215_I3_SOURCE_SHA256_MISMATCH")
    parsed: ParsedContainer = parse_gguf(raw)
    if parsed.file_sha256 != actual_sha:
        raise Pass215Iteration3ValidationError("PASS215_I3_CONTAINER_SHA256_INTERNAL_MISMATCH")

    i2_evidence = build_container_evidence(
        raw,
        filename=filename,
        source=source,
        expected_sha256=expected_sha256,
        frozen_profile_blob_sha1=frozen_profile_blob_sha1,
    )
    real_open = source.get("kind") == "public_open_transformer"
    if real_open and actual_sha == REAL_MODEL_SHA256:
        if i2_evidence["evidence_root_hash216"] != ITERATION2_EVIDENCE_ROOT_HASH216:
            raise Pass215Iteration3ValidationError("PASS215_I3_ITERATION2_BASELINE_ROOT_MISMATCH")
        if int(i2_evidence["accounting"]["canonical_quantized_or_integer_tensor_bytes"]) != ITERATION2_CANONICAL_TENSOR_BYTES:
            raise Pass215Iteration3ValidationError("PASS215_I3_ITERATION2_BASELINE_BYTES_MISMATCH")

    supported_records: list[Mapping[str, Any]] = []
    unsupported: list[Mapping[str, Any]] = []
    opaque_float_bytes = 0
    scale_stream_parts: list[bytes] = []
    code_stream_parts: list[bytes] = []
    supported_source_bytes = 0
    quantized_source_bytes = 0
    for tensor in sorted(parsed.tensors, key=lambda item: (item.data_offset, item.header_index)):
        payload = raw[tensor.data_offset : tensor.data_offset + tensor.data_size]
        if tensor.storage_class == STORAGE_FLOAT_OPAQUE:
            opaque_float_bytes += tensor.data_size
            continue
        if tensor.storage_class != STORAGE_QUANTIZED:
            unsupported.append({
                "name": tensor.name,
                "storage_type": tensor.storage_type,
                "storage_class": tensor.storage_class,
                "source_bytes": tensor.data_size,
                "reason": "NON_QUANTIZED_CANONICAL_STORAGE_OUTSIDE_ITERATION3_BLOCK_SCOPE",
            })
            continue
        quantized_source_bytes += tensor.data_size
        layout = SUPPORTED_LAYOUTS.get(tensor.storage_type)
        if layout is None:
            unsupported.append({
                "name": tensor.name,
                "storage_type": tensor.storage_type,
                "storage_class": tensor.storage_class,
                "source_bytes": tensor.data_size,
                "reason": "QUANTIZED_LAYOUT_UNCONTRACTED_PASSTHROUGH",
            })
            continue
        record = analyze_tensor(tensor, payload)
        supported_records.append(record)
        supported_source_bytes += tensor.data_size
        decomposed = decompose_blocks(payload, layout)
        scale_stream_parts.append(decomposed.scale_stream)
        code_stream_parts.append(decomposed.code_stream)

    if not supported_records:
        raise Pass215Iteration3ValidationError("PASS215_I3_SUPPORTED_QUANTIZED_TENSOR_SET_EMPTY")
    unsupported_bytes = sum(int(item["source_bytes"]) for item in unsupported)
    scale_stream = b"".join(scale_stream_parts)
    code_stream = b"".join(code_stream_parts)
    scale_pass212 = _measure_stream("__pass215_i3_supported_scale_stream__", scale_stream)
    code_pass212 = _measure_stream("__pass215_i3_supported_code_stream__", code_stream)

    source_record = dict(source)
    source_record.update({
        "filename": filename,
        "file_size_bytes": len(raw),
        "file_sha256": actual_sha,
        "expected_sha256_verified": expected_sha256 is None or expected_sha256 == actual_sha,
    })
    per_layer = _aggregate(supported_records, key="layer")
    per_type = _aggregate(supported_records, key="storage_type")
    selected_bytes = sum(int(item["selected_encoded_bytes"]) for item in supported_records) + unsupported_bytes
    raw_compared_bytes = supported_source_bytes + unsupported_bytes
    global_record = {
        "supported_tensor_count": len(supported_records),
        "supported_block_count": sum(int(item["block_count"]) for item in supported_records),
        "supported_source_bytes": supported_source_bytes,
        "quantized_source_bytes": quantized_source_bytes,
        "unsupported_passthrough_bytes": unsupported_bytes,
        "raw_compared_bytes": raw_compared_bytes,
        "selected_reversible_bytes": selected_bytes,
        "selected_gain_bytes_vs_raw": raw_compared_bytes - selected_bytes,
        "selected_ratio_exact": _exact_fraction(raw_compared_bytes, selected_bytes),
        "scale_stream_bytes": len(scale_stream),
        "code_stream_bytes": len(code_stream),
        "opaque_float_storage_bytes_excluded": opaque_float_bytes,
        "semantic_exactness": all(bool(item["semantic_exactness"]) for item in supported_records),
    }
    evidence: dict[str, Any] = {
        "schema": EVIDENCE_SCHEMA,
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "authority": {
            "pass214_authority_root_hash216": PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
            "pass213_gate_preservation_root_hash216": PASS213_GATE_PRESERVATION_ROOT_HASH216,
            "frozen_profile_git_blob_sha1": FROZEN_PROFILE_GIT_BLOB_SHA1,
            "benchmark_authority_promoted": True,
            "pass215_authorized": True,
            "pass213_gates_preserved": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
        "source": source_record,
        "container": {
            "format": parsed.format,
            "version": parsed.version,
            "architecture": parsed.architecture,
            "tensor_count": len(parsed.tensors),
            "tensor_inventory_root_hash216": hash216(
                "pass215-i3-container-tensor-inventory",
                canonical_bytes([tensor.to_dict() for tensor in parsed.tensors]),
            ),
        },
        "iteration2_baseline": {
            "evidence_root_hash216": i2_evidence["evidence_root_hash216"],
            "receipt_hash72": i2_evidence["receipt_hash72"],
            "canonical_source_bytes": int(i2_evidence["accounting"]["canonical_quantized_or_integer_tensor_bytes"]),
            "canonical_admitted_bytes": int(i2_evidence["canonical_quantized_stream_measurement"]["admitted_bytes"]),
            "canonical_incidence_fraction_exact": i2_evidence["canonical_quantized_stream_measurement"]["incidence_fraction_exact"],
            "canonical_protected_storage_bytes": int(i2_evidence["canonical_quantized_stream_measurement"]["protected_storage_bytes"]),
        },
        "supported_layouts": {key: value.to_dict() for key, value in sorted(SUPPORTED_LAYOUTS.items())},
        "predeclared_reversible_candidates": [
            RAW_BLOCK_STREAM,
            WHOLE_BLOCK_DICTIONARY,
            SPLIT_SCALE_CODE_DICTIONARY,
        ],
        "per_tensor": supported_records,
        "per_layer": per_layer,
        "per_storage_type": per_type,
        "unsupported_passthrough": unsupported,
        "global": global_record,
        "decomposed_pass212_measurements": {
            "scale_stream": scale_pass212,
            "code_stream": code_pass212,
        },
        "claims": {
            "real_open_transformer_measured": bool(real_open),
            "quantization_blocks_decomposed_exactly": True,
            "quantization_blocks_reconstructed_bit_exactly": bool(global_record["semantic_exactness"]),
            "block_structure_attributed": True,
            "dictionary_representation_is_runtime_authority": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "exact_nonlinear_transformer_operators_implemented": False,
            "fifty_billion_desktop_feasibility_claimed": False,
            "arbitrary_compression_claimed": False,
            "block_dictionary_compression_claimed": bool(global_record["selected_gain_bytes_vs_raw"] > 0),
        },
    }
    _reject_floats(evidence)
    root = hash216("pass215-i3-block-structure-evidence", canonical_bytes(evidence))
    receipt = hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION3_BLOCK_STRUCTURE_EVIDENCE"},
        {
            "sequence": 3,
            "parent_hash72": ITERATION2_RECEIPT_HASH72,
            "pass214_terminal_receipt_hash72": PASS214_TERMINAL_RECEIPT_HASH72,
            "iteration2_evidence_root_hash216": i2_evidence["evidence_root_hash216"],
            "evidence_root_hash216": root,
        },
    )
    return {**evidence, "evidence_root_hash216": root, "receipt_hash72": receipt}


def validate_block_structure_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration3ValidationError("PASS215_I3_EVIDENCE_SCHEMA_INVALID")
    authority = evidence.get("authority")
    if not isinstance(authority, Mapping):
        raise Pass215Iteration3ValidationError("PASS215_I3_AUTHORITY_MISSING")
    if authority.get("frozen_profile_git_blob_sha1") != FROZEN_PROFILE_GIT_BLOB_SHA1:
        raise Pass215Iteration3ValidationError("PASS215_I3_PROFILE_BINDING_INVALID")
    for forbidden in ("runtime_mutation_authority_promoted", "canonical_mutation_authorized", "migration_active"):
        if authority.get(forbidden) is not False:
            raise Pass215Iteration3ValidationError(f"PASS215_I3_FORBIDDEN_AUTHORITY:{forbidden}")
    baseline = evidence.get("iteration2_baseline")
    if not isinstance(baseline, Mapping):
        raise Pass215Iteration3ValidationError("PASS215_I3_BASELINE_MISSING")
    source = evidence.get("source")
    if not isinstance(source, Mapping):
        raise Pass215Iteration3ValidationError("PASS215_I3_SOURCE_MISSING")
    if source.get("file_sha256") == REAL_MODEL_SHA256 and baseline.get("evidence_root_hash216") != ITERATION2_EVIDENCE_ROOT_HASH216:
        raise Pass215Iteration3ValidationError("PASS215_I3_BASELINE_ROOT_INVALID")
    per_tensor = evidence.get("per_tensor")
    if not isinstance(per_tensor, list) or not per_tensor:
        raise Pass215Iteration3ValidationError("PASS215_I3_PER_TENSOR_MISSING")
    for item in per_tensor:
        if not isinstance(item, Mapping) or item.get("semantic_exactness") is not True:
            raise Pass215Iteration3ValidationError("PASS215_I3_TENSOR_EXACTNESS_INVALID")
        sizes = item.get("candidate_encoded_bytes")
        if not isinstance(sizes, Mapping) or set(sizes) != {RAW_BLOCK_STREAM, WHOLE_BLOCK_DICTIONARY, SPLIT_SCALE_CODE_DICTIONARY}:
            raise Pass215Iteration3ValidationError("PASS215_I3_CANDIDATE_SET_INVALID")
        raw_bytes = int(item["source_bytes"])
        selected_bytes = int(item["selected_encoded_bytes"])
        if int(sizes[RAW_BLOCK_STREAM]) != raw_bytes or selected_bytes > raw_bytes:
            raise Pass215Iteration3ValidationError("PASS215_I3_SELECTION_ACCOUNTING_INVALID")
        if selected_bytes != min(int(value) for value in sizes.values()):
            raise Pass215Iteration3ValidationError("PASS215_I3_SELECTION_NOT_MINIMAL")
    global_record = evidence.get("global")
    if not isinstance(global_record, Mapping) or global_record.get("semantic_exactness") is not True:
        raise Pass215Iteration3ValidationError("PASS215_I3_GLOBAL_EXACTNESS_INVALID")
    if int(global_record["selected_reversible_bytes"]) > int(global_record["raw_compared_bytes"]):
        raise Pass215Iteration3ValidationError("PASS215_I3_GLOBAL_SELECTION_INVALID")
    claims = evidence.get("claims")
    if not isinstance(claims, Mapping):
        raise Pass215Iteration3ValidationError("PASS215_I3_CLAIMS_MISSING")
    for false_claim in (
        "dictionary_representation_is_runtime_authority",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "exact_nonlinear_transformer_operators_implemented",
        "fifty_billion_desktop_feasibility_claimed",
        "arbitrary_compression_claimed",
    ):
        if claims.get(false_claim) is not False:
            raise Pass215Iteration3ValidationError(f"PASS215_I3_CLAIM_BOUNDARY_VIOLATED:{false_claim}")
    expected_compression_claim = int(global_record["selected_gain_bytes_vs_raw"]) > 0
    if claims.get("block_dictionary_compression_claimed") is not expected_compression_claim:
        raise Pass215Iteration3ValidationError("PASS215_I3_COMPRESSION_CLAIM_ACCOUNTING_INVALID")
    payload = dict(evidence)
    root = payload.pop("evidence_root_hash216", None)
    receipt = payload.pop("receipt_hash72", None)
    expected_root = hash216("pass215-i3-block-structure-evidence", canonical_bytes(payload))
    if root != expected_root:
        raise Pass215Iteration3ValidationError("PASS215_I3_EVIDENCE_ROOT_MISMATCH")
    expected_receipt = hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION3_BLOCK_STRUCTURE_EVIDENCE"},
        {
            "sequence": 3,
            "parent_hash72": ITERATION2_RECEIPT_HASH72,
            "pass214_terminal_receipt_hash72": PASS214_TERMINAL_RECEIPT_HASH72,
            "iteration2_evidence_root_hash216": baseline["evidence_root_hash216"],
            "evidence_root_hash216": expected_root,
        },
    )
    if receipt != expected_receipt:
        raise Pass215Iteration3ValidationError("PASS215_I3_RECEIPT_MISMATCH")


def build_block_structure_evidence_from_path(
    path: Path,
    *,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
    frozen_profile_blob_sha1: str = FROZEN_PROFILE_GIT_BLOB_SHA1,
) -> Mapping[str, Any]:
    target = Path(path)
    return build_block_structure_evidence(
        target.read_bytes(),
        filename=target.name,
        source=source,
        expected_sha256=expected_sha256,
        frozen_profile_blob_sha1=frozen_profile_blob_sha1,
    )


__all__ = [
    "CONTRACT",
    "PASS_NUMBER",
    "ITERATION",
    "CONTRACT_VERSION",
    "RUNTIME_CLASSIFICATION",
    "EVIDENCE_SCHEMA",
    "ITERATION2_EVIDENCE_ROOT_HASH216",
    "ITERATION2_RECEIPT_HASH72",
    "RAW_BLOCK_STREAM",
    "WHOLE_BLOCK_DICTIONARY",
    "SPLIT_SCALE_CODE_DICTIONARY",
    "QuantBlockLayout",
    "DictionaryEncoding",
    "SUPPORTED_LAYOUTS",
    "Pass215Iteration3Error",
    "Pass215Iteration3ValidationError",
    "encode_fixed_dictionary",
    "decode_fixed_dictionary",
    "decompose_blocks",
    "analyze_tensor",
    "build_block_structure_evidence",
    "build_block_structure_evidence_from_path",
    "validate_block_structure_evidence",
]
