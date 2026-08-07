"""Integrity loader for Pass 214 Iteration 4 callable-oracle authority."""
from __future__ import annotations

import gzip
from hashlib import sha256
from pathlib import Path

_PAYLOAD = Path(__file__).with_name("pass214_i4_payload") / "runtime.py.gz"
_PAYLOAD_SHA256 = "392d655df87628832fbd14d19301bc7dc8c002cf69b571fc6f12ab867961930d"
_SOURCE_SHA256 = "a946cde1338bc33eb6873c13125b306a45882dec46fd29ac4820ce38ea5612a9"

_raw = _PAYLOAD.read_bytes()
if sha256(_raw).hexdigest() != _PAYLOAD_SHA256:
    raise RuntimeError("PASS214_ITERATION4_RUNTIME_PAYLOAD_SHA256_MISMATCH")
_source = gzip.decompress(_raw)
if sha256(_source).hexdigest() != _SOURCE_SHA256:
    raise RuntimeError("PASS214_ITERATION4_RUNTIME_SOURCE_SHA256_MISMATCH")
exec(compile(_source, str(Path(__file__)), "exec"), globals(), globals())
