"""Integrity-loading test module for Pass 214 Iteration 2."""
from __future__ import annotations

import gzip as _gzip
from hashlib import sha256 as _sha256
from pathlib import Path as _Path

_PAYLOAD_DIRECTORY = _Path(__file__).with_name("pass214_i2_test_payload")
_PARTS = tuple(_PAYLOAD_DIRECTORY / f"test.py.gz.part{index:02d}" for index in range(3))
_EXPECTED_PART_SHA256 = (
    "c9d0de353efe63ad86eda7ae0c75614b72a25ecb70e03e4e03cb3bcee9448fdc",
    "421df397feda40820ef45838335d94a0af45b6c3b41cfdccf2eac09ffb659c98",
    "3ee08b33e4994ea950b1251271838a6e26a83618d81d803e86b8d6a5c8bb3141",
)
_EXPECTED_GZIP_SHA256 = "f98290bea53efd6ff48d9a6800f40db06e6c51faf196b8b6199f67c1459478ee"
_EXPECTED_SOURCE_SHA256 = "fce0987869de3bbb5145ac80dfc51aa35c8ba66cb738a469656852876b959ae4"

_payload_parts: list[bytes] = []
for _path, _expected in zip(_PARTS, _EXPECTED_PART_SHA256, strict=True):
    _part = _path.read_bytes()
    if _sha256(_part).hexdigest() != _expected:
        raise RuntimeError(f"PASS214_ITERATION2_TEST_PART_INTEGRITY_FAILURE:{_path.name}")
    _payload_parts.append(_part)
_payload = b"".join(_payload_parts)
if _sha256(_payload).hexdigest() != _EXPECTED_GZIP_SHA256:
    raise RuntimeError("PASS214_ITERATION2_TEST_GZIP_INTEGRITY_FAILURE")
_source = _gzip.decompress(_payload)
if _sha256(_source).hexdigest() != _EXPECTED_SOURCE_SHA256:
    raise RuntimeError("PASS214_ITERATION2_TEST_SOURCE_INTEGRITY_FAILURE")
exec(compile(_source, __file__, "exec"), globals(), globals())
