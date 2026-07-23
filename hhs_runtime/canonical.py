"""Canonical exact-serialization utilities for Pass 133.

No floating-point values are admitted.  All integer encodings use canonical
network byte order and all container encodings are self-delimiting.
"""
from __future__ import annotations

from dataclasses import is_dataclass, asdict
from hashlib import sha256
from typing import Any, Iterable, Iterator, Mapping, Sequence, Tuple
import json


class CanonicalEncodingError(ValueError):
    pass


def reject_floats(value: Any, path: str = "$" ) -> None:
    if isinstance(value, float):
        raise CanonicalEncodingError(f"floating-point value prohibited at {path}")
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, Mapping):
        for key, item in value.items():
            reject_floats(key, f"{path}.<key>")
            reject_floats(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple, set, frozenset)):
        for idx, item in enumerate(value):
            reject_floats(item, f"{path}[{idx}]")


def canonical_json(value: Any) -> str:
    reject_floats(value)
    if is_dataclass(value):
        value = asdict(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    )


def canonical_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def sha256_hex(value: bytes | bytearray | memoryview | str | Any) -> str:
    if isinstance(value, str):
        raw = value.encode("utf-8")
    elif isinstance(value, (bytes, bytearray, memoryview)):
        raw = bytes(value)
    else:
        raw = canonical_bytes(value)
    return sha256(raw).hexdigest()


def int_to_min_bytes(value: int) -> bytes:
    if not isinstance(value, int) or value < 0:
        raise CanonicalEncodingError("expected non-negative integer")
    return value.to_bytes(max(1, (value.bit_length() + 7) // 8), "big")


def min_bytes_to_int(raw: bytes) -> int:
    if not raw:
        raise CanonicalEncodingError("empty integer encoding")
    if len(raw) > 1 and raw[0] == 0:
        raise CanonicalEncodingError("non-canonical leading zero")
    return int.from_bytes(raw, "big")


def uleb128_encode(value: int) -> bytes:
    if not isinstance(value, int) or value < 0:
        raise CanonicalEncodingError("ULEB128 requires non-negative integer")
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def uleb128_decode(data: bytes, offset: int = 0) -> Tuple[int, int]:
    value = 0
    shift = 0
    start = offset
    while offset < len(data):
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            if uleb128_encode(value) != data[start:offset]:
                raise CanonicalEncodingError("non-canonical ULEB128")
            return value, offset
        shift += 7
        if shift > 4096:
            raise CanonicalEncodingError("ULEB128 exceeds bound")
    raise CanonicalEncodingError("truncated ULEB128")


TLV_MAGIC = b"HHS-P133-TLV\x01"


def encode_tlv(fields: Sequence[tuple[int, bytes]], *, magic: bytes = TLV_MAGIC) -> bytes:
    seen: set[int] = set()
    out = bytearray(magic)
    out += uleb128_encode(len(fields))
    for tag, payload in sorted(fields, key=lambda item: item[0]):
        if tag <= 0 or tag in seen:
            raise CanonicalEncodingError(f"invalid or duplicate TLV tag {tag}")
        seen.add(tag)
        raw = bytes(payload)
        out += uleb128_encode(tag)
        out += uleb128_encode(len(raw))
        out += raw
    return bytes(out)


def decode_tlv(data: bytes, *, magic: bytes = TLV_MAGIC) -> dict[int, bytes]:
    raw = bytes(data)
    if not raw.startswith(magic):
        raise CanonicalEncodingError("TLV magic/version mismatch")
    offset = len(magic)
    count, offset = uleb128_decode(raw, offset)
    fields: dict[int, bytes] = {}
    last_tag = 0
    for _ in range(count):
        tag, offset = uleb128_decode(raw, offset)
        length, offset = uleb128_decode(raw, offset)
        if tag <= last_tag or tag in fields:
            raise CanonicalEncodingError("TLV tags not strictly increasing")
        end = offset + length
        if end > len(raw):
            raise CanonicalEncodingError("truncated TLV payload")
        fields[tag] = raw[offset:end]
        last_tag = tag
        offset = end
    if offset != len(raw):
        raise CanonicalEncodingError("trailing TLV bytes")
    return fields


def bytes_to_bigint(raw: bytes) -> int:
    data = bytes(raw)
    if not data or data[0] == 0:
        raise CanonicalEncodingError("BigInt envelope must begin with non-zero magic")
    return int.from_bytes(data, "big")


def bigint_to_bytes(value: int) -> bytes:
    if not isinstance(value, int) or value <= 0:
        raise CanonicalEncodingError("BigInt envelope must be a positive integer")
    return value.to_bytes((value.bit_length() + 7) // 8, "big")


def pack_int_sequence(values: Iterable[int]) -> bytes:
    values = list(values)
    out = bytearray(uleb128_encode(len(values)))
    for value in values:
        raw = int_to_min_bytes(value)
        out += uleb128_encode(len(raw))
        out += raw
    return bytes(out)


def unpack_int_sequence(data: bytes) -> list[int]:
    offset = 0
    count, offset = uleb128_decode(data, offset)
    out: list[int] = []
    for _ in range(count):
        length, offset = uleb128_decode(data, offset)
        end = offset + length
        if end > len(data):
            raise CanonicalEncodingError("truncated integer sequence")
        out.append(min_bytes_to_int(data[offset:end]))
        offset = end
    if offset != len(data):
        raise CanonicalEncodingError("trailing integer-sequence bytes")
    return out
