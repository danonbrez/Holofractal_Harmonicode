"""Integrity loader for Pass 214 Iteration 3 tests."""
from __future__ import annotations

import gzip
from hashlib import sha256
from pathlib import Path

_PAYLOAD = Path(__file__).with_name("pass214_i3_test_payload") / "test.py.gz"
_PAYLOAD_SHA256 = "4a0914add2be09b424240ff0761a47d375e99145db427e552cf9486562856486"
_SOURCE_SHA256 = "d6d476dd85dc69ee5fe47ba7c86b03ee8e8a3f4805aede244ee66e586c7f2a97"
_raw = _PAYLOAD.read_bytes()
if sha256(_raw).hexdigest() != _PAYLOAD_SHA256:
    raise RuntimeError("PASS214_ITERATION3_TEST_PAYLOAD_SHA256_MISMATCH")
_source = gzip.decompress(_raw)
if sha256(_source).hexdigest() != _SOURCE_SHA256:
    raise RuntimeError("PASS214_ITERATION3_TEST_SOURCE_SHA256_MISMATCH")
exec(compile(_source, str(Path(__file__)), "exec"), globals(), globals())
