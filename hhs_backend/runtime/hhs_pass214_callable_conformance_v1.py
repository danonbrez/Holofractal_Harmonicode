"""Integrity-loading entrypoint for the Pass 214 Iteration 2 runtime source."""
from __future__ import annotations

import gzip as _gzip
from hashlib import sha256 as _sha256
from pathlib import Path as _Path

_PAYLOAD_DIRECTORY = _Path(__file__).with_name("pass214_i2_payload")
_PARTS = tuple(_PAYLOAD_DIRECTORY / f"runtime.py.gz.part{index:02d}" for index in range(9))
_EXPECTED_PART_SHA256 = (
    "54cc65a171ab58db0a6b6cb5ff2839496bd524e51f14a5df0dd1419eb91abb26",
    "890c3e13b7c98a37cdf7e5c0dd78bd8a34d92cbd68d8a0b16aaa914dc176bfaf",
    "1bb59a1776a8383f50b345b1bf40e65d7de513a040add5ca3f2fdb473fb6f50c",
    "ecd62a84f1bbd3fb1bf21a6896ea1353c766b920877da084118bd10077c172f8",
    "1e5dc80d3dc4a98805165299ed1735c0eae6d67d14d04940c0d8b21d7ebc1b37",
    "e47bacc1075800b5f4c9e4d5c9627aa0925bd961a71a9d4d849f0a20feb27db1",
    "803e82db57831a5068507602ac15bcef4952f2753a7147a848a1ae0f35fcfab9",
    "df56da497509d0e1205b70a5c9f5900575c454288b45de030d361408664358e6",
    "f3b5a73103db7c327e1be00cb95f9f9617470e87471b6b9c885c8581fd0221df",
)
_EXPECTED_GZIP_SHA256 = "dfd474f5e1901062fba80cb9b8fe50eb2d6c16c7a086ac7d9a1abca29d30af17"
_EXPECTED_SOURCE_SHA256 = "a9f043d837e42fc2232d0f3074f8f7737e2d6645e334599786ad94d05cd72f96"

_payload_parts: list[bytes] = []
for _path, _expected in zip(_PARTS, _EXPECTED_PART_SHA256, strict=True):
    _part = _path.read_bytes()
    if _sha256(_part).hexdigest() != _expected:
        raise RuntimeError(f"PASS214_ITERATION2_RUNTIME_PART_INTEGRITY_FAILURE:{_path.name}")
    _payload_parts.append(_part)
_payload = b"".join(_payload_parts)
if _sha256(_payload).hexdigest() != _EXPECTED_GZIP_SHA256:
    raise RuntimeError("PASS214_ITERATION2_RUNTIME_GZIP_INTEGRITY_FAILURE")
_source = _gzip.decompress(_payload)
if _sha256(_source).hexdigest() != _EXPECTED_SOURCE_SHA256:
    raise RuntimeError("PASS214_ITERATION2_RUNTIME_SOURCE_INTEGRITY_FAILURE")
exec(compile(_source, __file__, "exec"), globals(), globals())
