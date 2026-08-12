from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any


def _normalize(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"__fraction__": [value.numerator, value.denominator]}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, bytes):
        return {"__bytes_hex__": value.hex()}
    if isinstance(value, dict):
        return {str(k): _normalize(value[k]) for k in sorted(value, key=lambda x: str(x))}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, set):
        return sorted((_normalize(v) for v in value), key=lambda v: canonical_json(v))
    if isinstance(value, float):
        raise TypeError("IEEE float cannot acquire canonical Pass 145 authority")
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if hasattr(value, "to_dict"):
        return _normalize(value.to_dict())
    raise TypeError(f"unsupported canonical value: {type(value).__name__}")


def canonical_json(value: Any) -> str:
    return json.dumps(_normalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def hash72(label: str, value: Any) -> str:
    """Use the inherited deterministic Hash72-facing helper lazily.

    The helper is already part of the Pass 111+ receipt substrate. Pass 145
    never introduces a competing truth hash. Importing Pass 145 storage or
    canonicalization surfaces must not eagerly activate predictive-continuation
    machinery, so the inherited helper is resolved only when an actual Hash72
    operation is requested.

    SHA-256 is retained only for byte-integrity interoperability and is always
    explicitly labeled.
    """

    from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import (
        _hash as inherited_hash72,
    )

    return inherited_hash72(label, _normalize(value))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_id(prefix: str, label: str, value: Any, width: int = 24) -> str:
    """Collision-resistant database identifier derived from canonical evidence.

    Hash72 remains the semantic/root witness. SHA-256 is used only as an
    interoperable storage-address projection over the full canonical payload;
    it cannot overwrite or substitute the authoritative Hash72 fields.
    """
    payload = canonical_json(value)
    witness = hash72(label, value)
    projected = hashlib.sha256(f"{label}\x1f{witness}\x1f{payload}".encode("utf-8")).hexdigest()
    width = max(8, min(int(width), len(projected)))
    return f"{prefix}-{projected[:width]}"
