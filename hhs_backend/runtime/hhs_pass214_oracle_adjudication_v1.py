"""Integrity loader for Pass 214 Iteration 3 oracle-model authority."""
from __future__ import annotations

import gzip
from hashlib import sha256
from pathlib import Path

_PAYLOAD = Path(__file__).with_name("pass214_i3_payload") / "runtime.py.gz"
_PAYLOAD_SHA256 = "d571523e81e7a0c8757bf1c164ffd6c4217ad5c0e07ddd8c804ce082727cf158"
_SOURCE_SHA256 = "33f25c0ad2b39777770b636c8c1367cc1412b5d36d00d5a8e4918018b58c1b15"

_raw = _PAYLOAD.read_bytes()
if sha256(_raw).hexdigest() != _PAYLOAD_SHA256:
    raise RuntimeError("PASS214_ITERATION3_RUNTIME_PAYLOAD_SHA256_MISMATCH")
_source = gzip.decompress(_raw)
if sha256(_source).hexdigest() != _SOURCE_SHA256:
    raise RuntimeError("PASS214_ITERATION3_RUNTIME_SOURCE_SHA256_MISMATCH")
exec(compile(_source, str(Path(__file__)), "exec"), globals(), globals())
