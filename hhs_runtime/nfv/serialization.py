from __future__ import annotations

from typing import Any
import json
import struct

from .core import CONTRACT_ID, NFVError, NFVObject, TransitionPackage, canonical_bytes, hash216
from .graph import DependencyGraph

MAGIC = b"HNFV"
SERIALIZATION_VERSION = 1
HEADER = struct.Struct(">4sBBQ")
KIND_OBJECT = 1
KIND_PACKAGE = 2
KIND_GRAPH = 3
DEFAULT_MAX_PAYLOAD = 16 * 1024 * 1024

_OBJECT_FIELDS = {
    "domain", "contract_id", "object_type", "state", "constraints", "dependencies",
    "authority_root", "version", "generation", "receipt_head", "lifecycle", "object_index",
}
_PACKAGE_FIELDS = {
    "package_index", "target_index", "constructor", "prior_commitment", "candidate_state",
    "inverse_state", "authority_root", "status", "receipt",
}


def _reject_float(_value: str) -> None:
    raise NFVError("NFV_FLOAT_FORBIDDEN", "authoritative serialization does not accept floating-point values")


def _reject_constant(_value: str) -> None:
    raise NFVError("NFV_FLOAT_FORBIDDEN", "non-finite numeric constants are forbidden")


def _no_duplicate_fields(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise NFVError("NFV_DUPLICATE_SERIALIZATION_FIELD", "duplicate field rejected", {"field": key})
        result[key] = value
    return result


def _validate_authoritative_value(value: Any, *, depth: int = 0, max_depth: int = 64) -> None:
    if depth > max_depth:
        raise NFVError("RESOURCE_BOUNDED", "serialization recursion depth exceeded")
    if value is None or isinstance(value, (bool, int, str)):
        return
    if isinstance(value, float):
        raise NFVError("NFV_FLOAT_FORBIDDEN", "authoritative serialization does not accept floats")
    if isinstance(value, list):
        for item in value:
            _validate_authoritative_value(item, depth=depth + 1, max_depth=max_depth)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise NFVError("NFV_NONSTRING_SERIALIZATION_KEY", "serialized field keys must be strings")
            _validate_authoritative_value(item, depth=depth + 1, max_depth=max_depth)
        return
    raise NFVError("NFV_UNSUPPORTED_SERIALIZATION_TYPE", "unsupported authoritative field type", {"type": type(value).__name__})


def _encode(kind: int, value: Any, *, max_payload: int = DEFAULT_MAX_PAYLOAD) -> bytes:
    _validate_authoritative_value(value)
    payload = canonical_bytes(value)
    if len(payload) > max_payload:
        raise NFVError("RESOURCE_BOUNDED", "serialized payload exceeds declared bound", {"size": len(payload), "max": max_payload})
    return HEADER.pack(MAGIC, SERIALIZATION_VERSION, kind, len(payload)) + payload


def _decode(data: bytes | bytearray | memoryview, *, expected_kind: int, max_payload: int = DEFAULT_MAX_PAYLOAD) -> dict[str, Any]:
    raw = bytes(data)
    if len(raw) < HEADER.size:
        raise NFVError("NFV_TRUNCATED_SERIALIZATION", "serialization header is incomplete")
    magic, version, kind, payload_size = HEADER.unpack(raw[: HEADER.size])
    if magic != MAGIC:
        raise NFVError("NFV_SERIALIZATION_MAGIC_MISMATCH", "serialization magic is invalid")
    if version != SERIALIZATION_VERSION:
        raise NFVError("NFV_UNSUPPORTED_SERIALIZATION_VERSION", "serialization version is unsupported")
    if kind != expected_kind:
        raise NFVError("NFV_SERIALIZATION_KIND_MISMATCH", "serialized record kind is invalid")
    if payload_size > max_payload:
        raise NFVError("RESOURCE_BOUNDED", "declared serialized payload exceeds bound")
    expected_size = HEADER.size + payload_size
    if len(raw) < expected_size:
        raise NFVError("NFV_TRUNCATED_SERIALIZATION", "serialized payload is incomplete")
    if len(raw) != expected_size:
        raise NFVError("NFV_TRAILING_SERIALIZATION_DATA", "trailing bytes are forbidden")
    payload = raw[HEADER.size:]
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_no_duplicate_fields,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except UnicodeDecodeError as exc:
        raise NFVError("NFV_INVALID_UTF8", "serialized payload is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise NFVError("NFV_INVALID_CANONICAL_JSON", "serialized payload is not valid JSON", {"position": exc.pos}) from exc
    if not isinstance(value, dict):
        raise NFVError("NFV_INVALID_SERIALIZATION_ROOT", "serialized root must be an object")
    _validate_authoritative_value(value)
    if canonical_bytes(value) != payload:
        raise NFVError("NFV_NONCANONICAL_SERIALIZATION", "payload is not minimally and canonically encoded")
    return value


def serialize_object(obj: NFVObject, *, max_payload: int = DEFAULT_MAX_PAYLOAD) -> bytes:
    return _encode(KIND_OBJECT, obj.to_dict(), max_payload=max_payload)


def deserialize_object(data: bytes | bytearray | memoryview, *, max_payload: int = DEFAULT_MAX_PAYLOAD) -> NFVObject:
    value = _decode(data, expected_kind=KIND_OBJECT, max_payload=max_payload)
    if set(value) != _OBJECT_FIELDS:
        raise NFVError("NFV_OBJECT_SCHEMA_MISMATCH", "serialized object fields are not canonical")
    if value["domain"] != "HHS-NFV-OBJECT-V1" or value["contract_id"] != CONTRACT_ID:
        raise NFVError("NFV_OBJECT_SCHEMA_MISMATCH", "serialized object domain or contract is invalid")
    return NFVObject(
        object_type=value["object_type"], state=value["state"], constraints=tuple(value["constraints"]),
        dependencies=tuple(value["dependencies"]), authority_root=value["authority_root"],
        version=int(value["version"]), generation=int(value["generation"]),
        receipt_head=value["receipt_head"], object_index=value["object_index"], lifecycle=value["lifecycle"],
    )


def serialize_package(package: TransitionPackage, *, max_payload: int = DEFAULT_MAX_PAYLOAD) -> bytes:
    return _encode(KIND_PACKAGE, package.to_dict(), max_payload=max_payload)


def deserialize_package(data: bytes | bytearray | memoryview, *, max_payload: int = DEFAULT_MAX_PAYLOAD) -> TransitionPackage:
    value = _decode(data, expected_kind=KIND_PACKAGE, max_payload=max_payload)
    if set(value) != _PACKAGE_FIELDS:
        raise NFVError("NFV_PACKAGE_SCHEMA_MISMATCH", "serialized package fields are not canonical")
    expected_index = hash216({
        "domain": "HHS-NFV-PACKAGE-V1", "target": value["target_index"],
        "constructor": value["constructor"], "prior": value["prior_commitment"],
        "candidate": value["candidate_state"], "inverse": value["inverse_state"],
        "authority_root": value["authority_root"],
    })
    if expected_index != value["package_index"]:
        raise NFVError("NFV_PACKAGE_IDENTITY_MISMATCH", "serialized package index is invalid")
    return TransitionPackage(
        package_index=value["package_index"], target_index=value["target_index"], constructor=value["constructor"],
        prior_commitment=value["prior_commitment"], candidate_state=value["candidate_state"],
        inverse_state=value["inverse_state"], authority_root=value["authority_root"],
        status=value["status"], receipt=value["receipt"],
    )


def serialize_graph(graph: DependencyGraph, *, max_payload: int = DEFAULT_MAX_PAYLOAD) -> bytes:
    return _encode(KIND_GRAPH, graph.to_dict(), max_payload=max_payload)


def deserialize_graph(data: bytes | bytearray | memoryview, *, max_payload: int = DEFAULT_MAX_PAYLOAD) -> DependencyGraph:
    return DependencyGraph.from_dict(_decode(data, expected_kind=KIND_GRAPH, max_payload=max_payload))
