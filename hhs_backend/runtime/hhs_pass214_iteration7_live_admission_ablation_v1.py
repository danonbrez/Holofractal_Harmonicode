"""Integrity-loaded Pass 214 Iteration 7 live-admission and ablation bridge."""
from __future__ import annotations

import gzip
from hashlib import sha256
from pathlib import Path

_PAYLOAD = Path(__file__).with_name("pass214_i7_payload") / "runtime.py.gz"
_EXPECTED_GZIP_SHA256 = "4b348a07b59ada0ec471e0e28cdd82d654c7e25928144ea3b1aafe881b8b6750"
_EXPECTED_SOURCE_SHA256 = "23702a3420453d95fba1f87fb5675992d97dbaf63ed910dfc5aa5e1b117212e0"

compressed = _PAYLOAD.read_bytes()
if sha256(compressed).hexdigest() != _EXPECTED_GZIP_SHA256:
    raise RuntimeError("PASS214_I7_RUNTIME_PAYLOAD_GZIP_HASH_MISMATCH")
source = gzip.decompress(compressed)
if sha256(source).hexdigest() != _EXPECTED_SOURCE_SHA256:
    raise RuntimeError("PASS214_I7_RUNTIME_PAYLOAD_SOURCE_HASH_MISMATCH")
exec(compile(source, str(_PAYLOAD) + "::runtime.py", "exec"), globals(), globals())
