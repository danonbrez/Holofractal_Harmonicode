"""Integrity loader for Pass 214 Iteration 4 callable-oracle tests."""
from __future__ import annotations

import gzip
from hashlib import sha256
from pathlib import Path

_PAYLOAD = Path(__file__).with_name("pass214_i4_test_payload") / "test.py.gz"
_PAYLOAD_SHA256 = "731d4bba2fab5243f29c3b4772c0634d658261930c6f3a2312706c2ae416a297"
_SOURCE_SHA256 = "f413e3514dbfd97f4c59dbedeabca885380adbc466f984508ca1317b53a76ec5"

_raw = _PAYLOAD.read_bytes()
if sha256(_raw).hexdigest() != _PAYLOAD_SHA256:
    raise RuntimeError("PASS214_ITERATION4_TEST_PAYLOAD_SHA256_MISMATCH")
_source = gzip.decompress(_raw)
if sha256(_source).hexdigest() != _SOURCE_SHA256:
    raise RuntimeError("PASS214_ITERATION4_TEST_SOURCE_SHA256_MISMATCH")
exec(compile(_source, str(Path(__file__)), "exec"), globals(), globals())
