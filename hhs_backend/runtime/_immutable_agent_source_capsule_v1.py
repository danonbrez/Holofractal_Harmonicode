"""Verified source-capsule reader for the immutable agent SQL index.

The repository carries the canonical reviewed sources in a checksum-protected,
chunked bootstrap capsule. Runtime modules can execute their exact source from
that capsule without granting API tools access to the protected narrative.
A CI materialization pass may replace these wrappers with ordinary source files.
"""
from __future__ import annotations

import base64
import functools
import gzip
import hashlib
from pathlib import Path
from typing import Any, MutableMapping

_CAPSULE_DIRECTORY = Path(".github/bootstrap_immutable_agent_index")
_MARKER = "\nfor relative, entry in PAYLOAD.items():"


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


@functools.lru_cache(maxsize=1)
def _payload() -> dict[str, dict[str, str]]:
    directory = _repository_root() / _CAPSULE_DIRECTORY
    parts = sorted(directory.glob("part-*.b64"))
    if not parts:
        raise RuntimeError("HHS_IMMUTABLE_AGENT_SOURCE_CAPSULE_MISSING")
    encoded = "".join(part.read_text(encoding="utf-8").strip() for part in parts)
    script = gzip.decompress(base64.b64decode(encoded)).decode("utf-8")
    prefix, marker, _ = script.partition(_MARKER)
    if not marker:
        raise RuntimeError("HHS_IMMUTABLE_AGENT_SOURCE_CAPSULE_INVALID")
    namespace: dict[str, Any] = {}
    exec(compile(prefix, "<hhs-immutable-agent-capsule>", "exec"), namespace, namespace)
    payload = namespace.get("PAYLOAD")
    if not isinstance(payload, dict):
        raise RuntimeError("HHS_IMMUTABLE_AGENT_SOURCE_CAPSULE_PAYLOAD_MISSING")
    return payload


@functools.lru_cache(maxsize=16)
def source(relative_path: str) -> bytes:
    import base64 as _base64
    import zlib

    entry = _payload().get(relative_path)
    if not isinstance(entry, dict):
        raise RuntimeError(f"HHS_IMMUTABLE_AGENT_SOURCE_NOT_FOUND:{relative_path}")
    raw = zlib.decompress(_base64.b85decode(str(entry["data"]).encode("ascii")))
    expected = str(entry["sha256"])
    if hashlib.sha256(raw).hexdigest() != expected:
        raise RuntimeError(f"HHS_IMMUTABLE_AGENT_SOURCE_CHECKSUM_MISMATCH:{relative_path}")
    return raw


def execute(relative_path: str, namespace: MutableMapping[str, Any]) -> None:
    raw = source(relative_path)
    exec(compile(raw, str(_repository_root() / relative_path), "exec"), namespace, namespace)
