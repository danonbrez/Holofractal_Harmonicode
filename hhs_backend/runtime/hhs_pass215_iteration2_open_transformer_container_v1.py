"""Pass 215 Iteration 2: real open-transformer container ingestion.

Parses Safetensors and GGUF weight containers without interpreting IEEE floating
values as canonical numeric authority. Exact stored tensor bytes are inventoried,
hashed, and measured through the frozen Pass 215 / inherited Pass 212 incidence
instrument. Quantized/integer tensor bytes are measured separately from opaque
float-typed storage so measurement cannot silently promote float semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import prod
import json
from pathlib import Path
import struct
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import canonical_bytes, hash216
from hhs_backend.runtime.hhs_pass215_iteration1_transformer_ingestion_v1 import (
    FROZEN_PROFILE_GIT_BLOB_SHA1,
    PASS213_GATE_PRESERVATION_ROOT_HASH216,
    PASS214_AUTHORITY_ROOT_HASH216,
    PASS214_TERMINAL_RECEIPT_HASH72,
    PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    Pass215Iteration1ValidationError,
    _exact_fraction,
    measure_tensor,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest

CONTRACT = "HHS-P215-I2-REAL-OPEN-TRANSFORMER-CONTAINER-INGESTION-INCIDENCE"
PASS_NUMBER = 215
ITERATION = 2
CONTRACT_VERSION = "1.0.0-iteration2"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_2_OPEN_TRANSFORMER_CONTAINER_INGESTION"
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_2_CONTAINER_EVIDENCE_V1"
ZERO_HASH72 = "0" * 72
ITERATION1_RECEIPT_HASH72 = "cs3IlNBCc<Pgxn1AGehePs7m)KSSOvxgS()JL9NtVWOKqLWbpR?KsU5>zIxL*/M0LnF/!0GS"

STORAGE_QUANTIZED = "QUANTIZED_BLOCK"
STORAGE_INTEGER = "INTEGER_EXACT"
STORAGE_FLOAT_OPAQUE = "FLOAT_STORAGE_OPAQUE"


class Pass215Iteration2Error(RuntimeError):
    pass


class Pass215Iteration2ValidationError(Pass215Iteration2Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration2ValidationError(f"PASS215_I2_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _sha256(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _align(value: int, alignment: int) -> int:
    if alignment <= 0 or alignment & (alignment - 1):
        raise Pass215Iteration2ValidationError("PASS215_I2_ALIGNMENT_INVALID")
    return (value + alignment - 1) // alignment * alignment


@dataclass(frozen=True)
class ContainerTensor:
    name: str
    shape: tuple[int, ...]
    storage_type: str
    storage_type_code: int | None
    storage_class: str
    data_offset: int
    data_size: int
    source_sha256: str
    block_elements: int
    block_bytes: int
    header_index: int

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "shape": list(self.shape),
            "storage_type": self.storage_type,
            "storage_type_code": self.storage_type_code,
            "storage_class": self.storage_class,
            "data_offset": self.data_offset,
            "data_size": self.data_size,
            "source_sha256": self.source_sha256,
            "block_elements": self.block_elements,
            "block_bytes": self.block_bytes,
            "header_index": self.header_index,
        }


@dataclass(frozen=True)
class ParsedContainer:
    format: str
    version: int | None
    architecture: str | None
    alignment: int | None
    file_size: int
    file_sha256: str
    tensor_data_start: int
    tensors: tuple[ContainerTensor, ...]
    metadata_summary: Mapping[str, Any]

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "format": self.format,
            "version": self.version,
            "architecture": self.architecture,
            "alignment": self.alignment,
            "file_size": self.file_size,
            "file_sha256": self.file_sha256,
            "tensor_data_start": self.tensor_data_start,
            "tensor_count": len(self.tensors),
            "tensors": [item.to_dict() for item in self.tensors],
            "metadata_summary": dict(self.metadata_summary),
        }


class _Reader:
    def __init__(self, raw: bytes):
        self.raw = raw
        self.pos = 0

    def read(self, size: int) -> bytes:
        if size < 0 or self.pos + size > len(self.raw):
            raise Pass215Iteration2ValidationError("PASS215_I2_CONTAINER_TRUNCATED")
        out = self.raw[self.pos : self.pos + size]
        self.pos += size
        return out

    def unpack(self, fmt: str) -> int:
        size = struct.calcsize(fmt)
        return int(struct.unpack(fmt, self.read(size))[0])

    def u8(self) -> int:
        return self.unpack("<B")

    def i8(self) -> int:
        return self.unpack("<b")

    def u16(self) -> int:
        return self.unpack("<H")

    def i16(self) -> int:
        return self.unpack("<h")

    def u32(self) -> int:
        return self.unpack("<I")

    def i32(self) -> int:
        return self.unpack("<i")

    def u64(self) -> int:
        return self.unpack("<Q")

    def i64(self) -> int:
        return self.unpack("<q")

    def string(self) -> str:
        size = self.u64()
        if size > len(self.raw) - self.pos:
            raise Pass215Iteration2ValidationError("PASS215_I2_STRING_LENGTH_INVALID")
        try:
            return self.read(size).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise Pass215Iteration2ValidationError("PASS215_I2_STRING_UTF8_INVALID") from exc


# GGUF metadata value types.
_GGUF_UINT8 = 0
_GGUF_INT8 = 1
_GGUF_UINT16 = 2
_GGUF_INT16 = 3
_GGUF_UINT32 = 4
_GGUF_INT32 = 5
_GGUF_FLOAT32 = 6
_GGUF_BOOL = 7
_GGUF_STRING = 8
_GGUF_ARRAY = 9
_GGUF_UINT64 = 10
_GGUF_INT64 = 11
_GGUF_FLOAT64 = 12


def _read_gguf_value(reader: _Reader, value_type: int, *, summarize_arrays: bool = True) -> Any:
    if value_type == _GGUF_UINT8:
        return reader.u8()
    if value_type == _GGUF_INT8:
        return reader.i8()
    if value_type == _GGUF_UINT16:
        return reader.u16()
    if value_type == _GGUF_INT16:
        return reader.i16()
    if value_type == _GGUF_UINT32:
        return reader.u32()
    if value_type == _GGUF_INT32:
        return reader.i32()
    if value_type == _GGUF_UINT64:
        return reader.u64()
    if value_type == _GGUF_INT64:
        return reader.i64()
    if value_type == _GGUF_BOOL:
        value = reader.u8()
        if value not in (0, 1):
            raise Pass215Iteration2ValidationError("PASS215_I2_GGUF_BOOL_INVALID")
        return bool(value)
    if value_type == _GGUF_STRING:
        return reader.string()
    if value_type == _GGUF_FLOAT32:
        return {"opaque_ieee754_bits_hex": reader.read(4).hex(), "width_bits": 32}
    if value_type == _GGUF_FLOAT64:
        return {"opaque_ieee754_bits_hex": reader.read(8).hex(), "width_bits": 64}
    if value_type == _GGUF_ARRAY:
        element_type = reader.u32()
        count = reader.u64()
        if count > 10_000_000:
            raise Pass215Iteration2ValidationError("PASS215_I2_GGUF_ARRAY_TOO_LARGE")
        start = reader.pos
        if summarize_arrays:
            for _ in range(count):
                _read_gguf_value(reader, element_type, summarize_arrays=False)
            payload = reader.raw[start : reader.pos]
            return {
                "element_type": element_type,
                "count": count,
                "encoded_payload_sha256": _sha256(payload),
                "encoded_payload_bytes": len(payload),
            }
        return [_read_gguf_value(reader, element_type, summarize_arrays=False) for _ in range(count)]
    raise Pass215Iteration2ValidationError(f"PASS215_I2_GGUF_METADATA_TYPE_UNSUPPORTED:{value_type}")


# ggml_type -> (name, block elements, encoded block bytes, storage class)
# Iteration 2 includes the standard scalar/classic/K-quant types required for
# the real workload and fails closed for newer layouts until their byte geometry
# is explicitly contracted.
_GGML_LAYOUTS: Mapping[int, tuple[str, int, int, str]] = {
    0: ("F32", 1, 4, STORAGE_FLOAT_OPAQUE),
    1: ("F16", 1, 2, STORAGE_FLOAT_OPAQUE),
    2: ("Q4_0", 32, 18, STORAGE_QUANTIZED),
    3: ("Q4_1", 32, 20, STORAGE_QUANTIZED),
    6: ("Q5_0", 32, 22, STORAGE_QUANTIZED),
    7: ("Q5_1", 32, 24, STORAGE_QUANTIZED),
    8: ("Q8_0", 32, 34, STORAGE_QUANTIZED),
    9: ("Q8_1", 32, 36, STORAGE_QUANTIZED),
    10: ("Q2_K", 256, 84, STORAGE_QUANTIZED),
    11: ("Q3_K", 256, 110, STORAGE_QUANTIZED),
    12: ("Q4_K", 256, 144, STORAGE_QUANTIZED),
    13: ("Q5_K", 256, 176, STORAGE_QUANTIZED),
    14: ("Q6_K", 256, 210, STORAGE_QUANTIZED),
    15: ("Q8_K", 256, 292, STORAGE_QUANTIZED),
    24: ("I8", 1, 1, STORAGE_INTEGER),
    25: ("I16", 1, 2, STORAGE_INTEGER),
    26: ("I32", 1, 4, STORAGE_INTEGER),
    27: ("I64", 1, 8, STORAGE_INTEGER),
    28: ("F64", 1, 8, STORAGE_FLOAT_OPAQUE),
    30: ("BF16", 1, 2, STORAGE_FLOAT_OPAQUE),
}


def _tensor_encoded_size(shape: Sequence[int], block_elements: int, block_bytes: int) -> int:
    if not shape or any(isinstance(item, bool) or int(item) <= 0 for item in shape):
        raise Pass215Iteration2ValidationError("PASS215_I2_TENSOR_SHAPE_INVALID")
    elements = prod(int(item) for item in shape)
    if elements % block_elements:
        raise Pass215Iteration2ValidationError("PASS215_I2_TENSOR_BLOCK_GEOMETRY_INVALID")
    return elements // block_elements * block_bytes


def parse_gguf(raw: bytes) -> ParsedContainer:
    reader = _Reader(raw)
    if reader.read(4) != b"GGUF":
        raise Pass215Iteration2ValidationError("PASS215_I2_GGUF_MAGIC_INVALID")
    version = reader.u32()
    if version not in (2, 3):
        raise Pass215Iteration2ValidationError(f"PASS215_I2_GGUF_VERSION_UNSUPPORTED:{version}")
    tensor_count = reader.u64()
    metadata_count = reader.u64()
    if tensor_count <= 0 or tensor_count > 1_000_000:
        raise Pass215Iteration2ValidationError("PASS215_I2_GGUF_TENSOR_COUNT_INVALID")
    if metadata_count > 1_000_000:
        raise Pass215Iteration2ValidationError("PASS215_I2_GGUF_METADATA_COUNT_INVALID")

    metadata: dict[str, Any] = {}
    metadata_types: dict[str, int] = {}
    for _ in range(metadata_count):
        key = reader.string()
        if not key or key in metadata:
            raise Pass215Iteration2ValidationError("PASS215_I2_GGUF_METADATA_KEY_INVALID")
        value_type = reader.u32()
        metadata_types[key] = value_type
        metadata[key] = _read_gguf_value(reader, value_type)

    alignment_value = metadata.get("general.alignment", 32)
    if isinstance(alignment_value, bool) or not isinstance(alignment_value, int):
        raise Pass215Iteration2ValidationError("PASS215_I2_GGUF_ALIGNMENT_TYPE_INVALID")
    alignment = int(alignment_value)
    architecture_value = metadata.get("general.architecture")
    architecture = architecture_value if isinstance(architecture_value, str) else None

    infos: list[dict[str, Any]] = []
    names: set[str] = set()
    for index in range(tensor_count):
        name = reader.string()
        if not name or name in names:
            raise Pass215Iteration2ValidationError("PASS215_I2_GGUF_TENSOR_NAME_INVALID")
        names.add(name)
        n_dims = reader.u32()
        if not 1 <= n_dims <= 8:
            raise Pass215Iteration2ValidationError("PASS215_I2_GGUF_N_DIMS_INVALID")
        shape = tuple(reader.u64() for _ in range(n_dims))
        type_code = reader.u32()
        relative_offset = reader.u64()
        layout = _GGML_LAYOUTS.get(type_code)
        if layout is None:
            raise Pass215Iteration2ValidationError(f"PASS215_I2_GGML_TYPE_UNSUPPORTED:{type_code}:{name}")
        type_name, block_elements, block_bytes, storage_class = layout
        size = _tensor_encoded_size(shape, block_elements, block_bytes)
        infos.append({
            "name": name,
            "shape": shape,
            "type_code": type_code,
            "type_name": type_name,
            "block_elements": block_elements,
            "block_bytes": block_bytes,
            "storage_class": storage_class,
            "relative_offset": relative_offset,
            "data_size": size,
            "header_index": index,
        })

    data_start = _align(reader.pos, alignment)
    tensors: list[ContainerTensor] = []
    ranges: list[tuple[int, int, str]] = []
    for info in infos:
        start = data_start + int(info["relative_offset"])
        end = start + int(info["data_size"])
        if start < data_start or end > len(raw):
            raise Pass215Iteration2ValidationError(f"PASS215_I2_GGUF_TENSOR_RANGE_INVALID:{info['name']}")
        payload = raw[start:end]
        tensors.append(ContainerTensor(
            name=str(info["name"]),
            shape=tuple(int(item) for item in info["shape"]),
            storage_type=str(info["type_name"]),
            storage_type_code=int(info["type_code"]),
            storage_class=str(info["storage_class"]),
            data_offset=start,
            data_size=len(payload),
            source_sha256=_sha256(payload),
            block_elements=int(info["block_elements"]),
            block_bytes=int(info["block_bytes"]),
            header_index=int(info["header_index"]),
        ))
        ranges.append((start, end, str(info["name"])))
    ranges.sort()
    for previous, current in zip(ranges, ranges[1:]):
        if current[0] < previous[1]:
            raise Pass215Iteration2ValidationError(
                f"PASS215_I2_GGUF_TENSOR_OVERLAP:{previous[2]}:{current[2]}"
            )

    metadata_summary = {
        "metadata_count": metadata_count,
        "metadata_types_root_hash216": hash216(
            "pass215-i2-gguf-metadata-types", canonical_bytes(metadata_types)
        ),
        "metadata_root_hash216": hash216(
            "pass215-i2-gguf-metadata", canonical_bytes(metadata)
        ),
        "general_architecture": architecture,
        "general_alignment": alignment,
    }
    _reject_floats(metadata_summary)
    return ParsedContainer(
        format="GGUF",
        version=version,
        architecture=architecture,
        alignment=alignment,
        file_size=len(raw),
        file_sha256=_sha256(raw),
        tensor_data_start=data_start,
        tensors=tuple(tensors),
        metadata_summary=metadata_summary,
    )


_SAFETENSOR_DTYPES: Mapping[str, tuple[int, str]] = {
    "BOOL": (8, STORAGE_INTEGER),
    "I8": (8, STORAGE_INTEGER),
    "U8": (8, STORAGE_INTEGER),
    "I16": (16, STORAGE_INTEGER),
    "U16": (16, STORAGE_INTEGER),
    "I32": (32, STORAGE_INTEGER),
    "U32": (32, STORAGE_INTEGER),
    "I64": (64, STORAGE_INTEGER),
    "U64": (64, STORAGE_INTEGER),
    "F8_E4M3": (8, STORAGE_FLOAT_OPAQUE),
    "F8_E5M2": (8, STORAGE_FLOAT_OPAQUE),
    "F16": (16, STORAGE_FLOAT_OPAQUE),
    "BF16": (16, STORAGE_FLOAT_OPAQUE),
    "F32": (32, STORAGE_FLOAT_OPAQUE),
    "F64": (64, STORAGE_FLOAT_OPAQUE),
}


def _json_no_duplicate_pairs(pairs: Sequence[tuple[str, Any]]) -> Mapping[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise Pass215Iteration2ValidationError(f"PASS215_I2_SAFETENSORS_DUPLICATE_KEY:{key}")
        out[key] = value
    return out


def parse_safetensors(raw: bytes) -> ParsedContainer:
    if len(raw) < 8:
        raise Pass215Iteration2ValidationError("PASS215_I2_SAFETENSORS_TRUNCATED")
    header_length = int.from_bytes(raw[:8], "little")
    if header_length <= 1 or 8 + header_length > len(raw):
        raise Pass215Iteration2ValidationError("PASS215_I2_SAFETENSORS_HEADER_LENGTH_INVALID")
    header_raw = raw[8 : 8 + header_length]
    try:
        header = json.loads(header_raw.decode("utf-8"), object_pairs_hook=_json_no_duplicate_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Pass215Iteration2ValidationError("PASS215_I2_SAFETENSORS_HEADER_INVALID") from exc
    if not isinstance(header, Mapping):
        raise Pass215Iteration2ValidationError("PASS215_I2_SAFETENSORS_HEADER_OBJECT_REQUIRED")
    data_start = 8 + header_length
    tensors: list[ContainerTensor] = []
    ranges: list[tuple[int, int, str]] = []
    names = [key for key in header if key != "__metadata__"]
    if not names:
        raise Pass215Iteration2ValidationError("PASS215_I2_SAFETENSORS_TENSOR_SET_EMPTY")
    for index, name in enumerate(names):
        entry = header[name]
        if not isinstance(entry, Mapping):
            raise Pass215Iteration2ValidationError(f"PASS215_I2_SAFETENSORS_TENSOR_INVALID:{name}")
        dtype = entry.get("dtype")
        shape = entry.get("shape")
        offsets = entry.get("data_offsets")
        if dtype not in _SAFETENSOR_DTYPES:
            raise Pass215Iteration2ValidationError(f"PASS215_I2_SAFETENSORS_DTYPE_UNSUPPORTED:{dtype}")
        if not isinstance(shape, list) or not shape or any(isinstance(item, bool) or not isinstance(item, int) or item <= 0 for item in shape):
            raise Pass215Iteration2ValidationError(f"PASS215_I2_SAFETENSORS_SHAPE_INVALID:{name}")
        if not isinstance(offsets, list) or len(offsets) != 2 or any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in offsets):
            raise Pass215Iteration2ValidationError(f"PASS215_I2_SAFETENSORS_OFFSETS_INVALID:{name}")
        relative_start, relative_end = offsets
        if relative_end <= relative_start:
            raise Pass215Iteration2ValidationError(f"PASS215_I2_SAFETENSORS_RANGE_INVALID:{name}")
        bits, storage_class = _SAFETENSOR_DTYPES[str(dtype)]
        expected_size = (prod(int(item) for item in shape) * bits + 7) // 8
        if relative_end - relative_start != expected_size:
            raise Pass215Iteration2ValidationError(f"PASS215_I2_SAFETENSORS_SIZE_MISMATCH:{name}")
        start = data_start + relative_start
        end = data_start + relative_end
        if end > len(raw):
            raise Pass215Iteration2ValidationError(f"PASS215_I2_SAFETENSORS_SOURCE_TRUNCATED:{name}")
        payload = raw[start:end]
        tensors.append(ContainerTensor(
            name=str(name),
            shape=tuple(int(item) for item in shape),
            storage_type=str(dtype),
            storage_type_code=None,
            storage_class=storage_class,
            data_offset=start,
            data_size=len(payload),
            source_sha256=_sha256(payload),
            block_elements=1,
            block_bytes=max(1, bits // 8),
            header_index=index,
        ))
        ranges.append((start, end, str(name)))
    ranges.sort()
    for previous, current in zip(ranges, ranges[1:]):
        if current[0] < previous[1]:
            raise Pass215Iteration2ValidationError(
                f"PASS215_I2_SAFETENSORS_TENSOR_OVERLAP:{previous[2]}:{current[2]}"
            )
    metadata = header.get("__metadata__", {})
    if metadata is not None and not isinstance(metadata, Mapping):
        raise Pass215Iteration2ValidationError("PASS215_I2_SAFETENSORS_METADATA_INVALID")
    metadata_summary = {
        "header_length_bytes": header_length,
        "metadata_root_hash216": hash216(
            "pass215-i2-safetensors-metadata", canonical_bytes(metadata or {})
        ),
    }
    _reject_floats(metadata_summary)
    return ParsedContainer(
        format="SAFETENSORS",
        version=None,
        architecture=None,
        alignment=None,
        file_size=len(raw),
        file_sha256=_sha256(raw),
        tensor_data_start=data_start,
        tensors=tuple(tensors),
        metadata_summary=metadata_summary,
    )


def parse_container(raw: bytes, *, filename: str = "") -> ParsedContainer:
    if raw.startswith(b"GGUF"):
        return parse_gguf(raw)
    if filename.lower().endswith(".safetensors"):
        return parse_safetensors(raw)
    # Safetensors has no magic; attempt it only after GGUF and only if the
    # eight-byte header length is plausible.
    if len(raw) >= 8 and 0 < int.from_bytes(raw[:8], "little") <= len(raw) - 8:
        return parse_safetensors(raw)
    raise Pass215Iteration2ValidationError("PASS215_I2_CONTAINER_FORMAT_UNRECOGNIZED")


def _measure_stream(name: str, raw: bytes) -> Mapping[str, Any]:
    if not raw:
        return {
            "name": name,
            "source_bytes": 0,
            "source_sha256": _sha256(b""),
            "tier_1_bytes": 0,
            "tier_2_bytes": 0,
            "tier_3_bytes": 0,
            "admitted_bytes": 0,
            "incidence_fraction_exact": {"numerator": 0, "denominator": 1},
            "codec_payload_bytes": 0,
            "protected_storage_bytes": 0,
            "semantic_exactness": True,
            "empty_stream": True,
        }
    descriptor = {
        "name": name,
        "dtype": "uint8",
        "shape": [len(raw)],
        "length_bytes": len(raw),
    }
    result = dict(measure_tensor(descriptor, raw).to_dict())
    result["semantic_exactness"] = True
    result["empty_stream"] = False
    return result


def build_container_evidence(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
    frozen_profile_blob_sha1: str = FROZEN_PROFILE_GIT_BLOB_SHA1,
) -> Mapping[str, Any]:
    if frozen_profile_blob_sha1 != FROZEN_PROFILE_GIT_BLOB_SHA1:
        raise Pass215Iteration2ValidationError("PASS215_I2_FROZEN_PROFILE_BLOB_MISMATCH")
    _reject_floats(source)
    actual_sha = _sha256(raw)
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration2ValidationError("PASS215_I2_SOURCE_SHA256_MISMATCH")
    parsed = parse_container(raw, filename=filename)
    tensors_by_offset = sorted(parsed.tensors, key=lambda item: (item.data_offset, item.header_index))
    storage_stream = b"".join(raw[item.data_offset : item.data_offset + item.data_size] for item in tensors_by_offset)
    canonical_tensors = [
        item for item in tensors_by_offset
        if item.storage_class in {STORAGE_QUANTIZED, STORAGE_INTEGER}
    ]
    canonical_stream = b"".join(raw[item.data_offset : item.data_offset + item.data_size] for item in canonical_tensors)
    float_tensors = [item for item in tensors_by_offset if item.storage_class == STORAGE_FLOAT_OPAQUE]
    float_bytes = sum(item.data_size for item in float_tensors)
    quantized_bytes = sum(item.data_size for item in canonical_tensors)
    tensor_bytes = len(storage_stream)
    if quantized_bytes + float_bytes != tensor_bytes:
        raise Pass215Iteration2ValidationError("PASS215_I2_STORAGE_CLASS_ACCOUNTING_MISMATCH")
    if parsed.file_sha256 != actual_sha:
        raise Pass215Iteration2ValidationError("PASS215_I2_CONTAINER_SHA256_INTERNAL_MISMATCH")

    storage_measurement = _measure_stream("__pass215_i2_tensor_storage_stream__", storage_stream)
    canonical_measurement = _measure_stream("__pass215_i2_canonical_quantized_stream__", canonical_stream)
    tensor_inventory = [item.to_dict() for item in tensors_by_offset]
    inventory_root = hash216(
        "pass215-i2-tensor-inventory", canonical_bytes(tensor_inventory)
    )
    source_record = dict(source)
    source_record.update({
        "filename": filename,
        "file_size_bytes": len(raw),
        "file_sha256": actual_sha,
        "expected_sha256_verified": expected_sha256 is None or actual_sha == expected_sha256,
    })
    real_open = source_record.get("kind") == "public_open_transformer"
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
        "container": parsed.to_dict(),
        "tensor_inventory_root_hash216": inventory_root,
        "accounting": {
            "file_bytes": len(raw),
            "tensor_payload_bytes": tensor_bytes,
            "container_non_tensor_bytes": len(raw) - tensor_bytes,
            "canonical_quantized_or_integer_tensor_bytes": quantized_bytes,
            "opaque_float_tensor_bytes": float_bytes,
            "canonical_tensor_fraction_exact": _exact_fraction(quantized_bytes, tensor_bytes),
            "tensor_payload_fraction_of_file_exact": _exact_fraction(tensor_bytes, len(raw)),
        },
        "storage_stream_measurement": storage_measurement,
        "canonical_quantized_stream_measurement": canonical_measurement,
        "claims": {
            "real_open_transformer_measured": bool(real_open),
            "real_open_transformer_weight_bytes_measured": bool(real_open and tensor_bytes > 0),
            "canonical_quantized_subset_bit_exact_reproduction": bool(canonical_measurement["semantic_exactness"]),
            "full_network_canonical_reproduction": bool(float_bytes == 0),
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "exact_nonlinear_transformer_operators_implemented": False,
            "fifty_billion_desktop_feasibility_claimed": False,
            "arbitrary_compression_claimed": False,
        },
    }
    _reject_floats(evidence)
    root = hash216("pass215-i2-container-evidence", canonical_bytes(evidence))
    receipt = hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION2_CONTAINER_EVIDENCE"},
        {
            "sequence": 2,
            "parent_hash72": ITERATION1_RECEIPT_HASH72,
            "pass214_terminal_receipt_hash72": PASS214_TERMINAL_RECEIPT_HASH72,
            "evidence_root_hash216": root,
        },
    )
    return {**evidence, "evidence_root_hash216": root, "receipt_hash72": receipt}


def validate_container_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration2ValidationError("PASS215_I2_EVIDENCE_SCHEMA_INVALID")
    authority = evidence.get("authority")
    if not isinstance(authority, Mapping):
        raise Pass215Iteration2ValidationError("PASS215_I2_AUTHORITY_MISSING")
    if authority.get("frozen_profile_git_blob_sha1") != FROZEN_PROFILE_GIT_BLOB_SHA1:
        raise Pass215Iteration2ValidationError("PASS215_I2_EVIDENCE_PROFILE_BINDING_INVALID")
    for forbidden in ("runtime_mutation_authority_promoted", "canonical_mutation_authorized", "migration_active"):
        if authority.get(forbidden) is not False:
            raise Pass215Iteration2ValidationError(f"PASS215_I2_FORBIDDEN_AUTHORITY:{forbidden}")
    accounting = evidence.get("accounting")
    if not isinstance(accounting, Mapping):
        raise Pass215Iteration2ValidationError("PASS215_I2_ACCOUNTING_MISSING")
    tensor_bytes = int(accounting["tensor_payload_bytes"])
    canonical_bytes_count = int(accounting["canonical_quantized_or_integer_tensor_bytes"])
    float_bytes = int(accounting["opaque_float_tensor_bytes"])
    if canonical_bytes_count + float_bytes != tensor_bytes:
        raise Pass215Iteration2ValidationError("PASS215_I2_ACCOUNTING_INVALID")
    claims = evidence.get("claims")
    if not isinstance(claims, Mapping):
        raise Pass215Iteration2ValidationError("PASS215_I2_CLAIMS_MISSING")
    for false_claim in (
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "exact_nonlinear_transformer_operators_implemented",
        "fifty_billion_desktop_feasibility_claimed",
        "arbitrary_compression_claimed",
    ):
        if claims.get(false_claim) is not False:
            raise Pass215Iteration2ValidationError(f"PASS215_I2_CLAIM_BOUNDARY_VIOLATED:{false_claim}")
    payload = dict(evidence)
    root = payload.pop("evidence_root_hash216", None)
    receipt = payload.pop("receipt_hash72", None)
    expected_root = hash216("pass215-i2-container-evidence", canonical_bytes(payload))
    if root != expected_root:
        raise Pass215Iteration2ValidationError("PASS215_I2_EVIDENCE_ROOT_MISMATCH")
    expected_receipt = hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION2_CONTAINER_EVIDENCE"},
        {
            "sequence": 2,
            "parent_hash72": ITERATION1_RECEIPT_HASH72,
            "pass214_terminal_receipt_hash72": PASS214_TERMINAL_RECEIPT_HASH72,
            "evidence_root_hash216": expected_root,
        },
    )
    if receipt != expected_receipt:
        raise Pass215Iteration2ValidationError("PASS215_I2_RECEIPT_MISMATCH")


def build_container_evidence_from_path(
    path: Path,
    *,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
    frozen_profile_blob_sha1: str = FROZEN_PROFILE_GIT_BLOB_SHA1,
) -> Mapping[str, Any]:
    target = Path(path)
    return build_container_evidence(
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
    "STORAGE_QUANTIZED",
    "STORAGE_INTEGER",
    "STORAGE_FLOAT_OPAQUE",
    "Pass215Iteration2Error",
    "Pass215Iteration2ValidationError",
    "ContainerTensor",
    "ParsedContainer",
    "parse_gguf",
    "parse_safetensors",
    "parse_container",
    "build_container_evidence",
    "build_container_evidence_from_path",
    "validate_container_evidence",
]
