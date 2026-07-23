"""Checkpoint-repaired native Hash72/u^72 witness adapter.

The alphabet is recovered from 642 conflict-free Pass 132 witness mappings.
The ring transition law is the preserved Pass 014/015 C ABI law.  A parent
witness replay is mandatory before this adapter is treated as usable.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import ctypes
import json
import os
import subprocess

from .canonical import canonical_json

HASH72_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"
HASH72_LEN = 72


class NativeBuildError(RuntimeError):
    pass


class _Ring(ctypes.Structure):
    _fields_ = [
        ("positions", ctypes.c_uint8 * 72),
        ("rotation_profile", ctypes.c_int64 * 72),
        ("dna", ctypes.c_char * 73),
        ("trace_count", ctypes.c_uint64),
        ("zero_sum", ctypes.c_uint8),
        ("last_index", ctypes.c_uint8),
        ("last_delta", ctypes.c_int64),
    ]


def _compile_native() -> Path:
    here = Path(__file__).resolve().parent
    src = here / "native" / "pass133_checkpoint_native.c"
    build = here / "build"
    build.mkdir(exist_ok=True)
    lib = build / "libhhs_pass133_checkpoint.so"
    if not lib.exists() or lib.stat().st_mtime_ns < src.stat().st_mtime_ns:
        proc = subprocess.run(
            ["gcc", "-O2", "-std=c11", "-shared", "-fPIC", str(src), "-o", str(lib)],
            capture_output=True,
            text=True,
        )
        if proc.returncode:
            raise NativeBuildError(proc.stderr.strip() or "native build failed")
    return lib


_LIB = ctypes.CDLL(str(_compile_native()))
_LIB.hhs_pass133_hash72_init.argtypes = [ctypes.POINTER(_Ring)]
_LIB.hhs_pass133_hash72_rotate.argtypes = [ctypes.POINTER(_Ring), ctypes.c_uint8, ctypes.c_int64]
_LIB.hhs_pass133_hash72_rotate.restype = ctypes.c_uint8
_LIB.hhs_pass133_hash72_validate.argtypes = [ctypes.POINTER(_Ring)]
_LIB.hhs_pass133_hash72_validate.restype = ctypes.c_uint8
_LIB.hhs_pass133_hash72_reverse.argtypes = [ctypes.POINTER(_Ring), ctypes.POINTER(_Ring)]
_LIB.hhs_pass133_hash72_reverse.restype = ctypes.c_uint8
_LIB.hhs_pass133_validate_diagonal_sudoku.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
_LIB.hhs_pass133_validate_diagonal_sudoku.restype = ctypes.c_uint8
_LIB.hhs_pass133_loshu_vm81_order.argtypes = [ctypes.POINTER(ctypes.c_uint8)]


@dataclass(frozen=True)
class Hash72Witness:
    schema: str
    label: str
    canonical_payload: str
    dna: str
    digest: str
    zero_sum: bool
    trace_count: int
    rotation_profile: list[int]
    positions: list[int]
    authority: str = "CHECKPOINT_REPAIRED_NATIVE_U72"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class NativeHash72Ring:
    def __init__(self) -> None:
        self._ring = _Ring()
        _LIB.hhs_pass133_hash72_init(ctypes.byref(self._ring))

    def rotate(self, index: int, delta: int) -> bool:
        return bool(_LIB.hhs_pass133_hash72_rotate(ctypes.byref(self._ring), index, delta))

    def export(self) -> dict[str, Any]:
        return {
            "positions": [int(v) for v in self._ring.positions],
            "rotation_profile": [int(v) for v in self._ring.rotation_profile],
            "dna": bytes(self._ring.dna).split(b"\x00",1)[0].decode("ascii"),
            "trace_count": int(self._ring.trace_count),
            "zero_sum": bool(self._ring.zero_sum),
            "last_index": int(self._ring.last_index),
            "last_delta": int(self._ring.last_delta),
        }

    def reverse(self) -> "NativeHash72Ring":
        out = NativeHash72Ring.__new__(NativeHash72Ring)
        out._ring = _Ring()
        if not _LIB.hhs_pass133_hash72_reverse(ctypes.byref(self._ring), ctypes.byref(out._ring)):
            raise RuntimeError("Hash72 reverse failed")
        return out


def make_hash72_witness(label: str, value: Any, *, width: int = 72, canonical_payload: str | None = None) -> Hash72Witness:
    payload = canonical_payload if canonical_payload is not None else canonical_json(value)
    ring = NativeHash72Ring()
    for offset, byte in enumerate(f"{label}\u241f{payload}".encode("utf-8")):
        delta = ((byte + offset) % 72) or 72
        if not ring.rotate(offset % 72, delta):
            raise RuntimeError("Hash72 zero-sum closure failure")
    state = ring.export()
    width = max(1, min(72, int(width)))
    return Hash72Witness(
        schema="HHS_HASH72_KERNEL_WITNESS_V1",
        label=label,
        canonical_payload=payload,
        dna=state["dna"],
        digest=state["dna"][:width],
        zero_sum=state["zero_sum"],
        trace_count=state["trace_count"],
        rotation_profile=state["rotation_profile"],
        positions=state["positions"],
    )


def validate_diagonal_sudoku_native(grid: list[list[int]]) -> bool:
    flat = [v for row in grid for v in row]
    if len(flat) != 81:
        return False
    arr = (ctypes.c_uint8 * 81)(*flat)
    return bool(_LIB.hhs_pass133_validate_diagonal_sudoku(arr))


def native_loshu_vm81_order() -> list[int]:
    arr = (ctypes.c_uint8 * 81)()
    _LIB.hhs_pass133_loshu_vm81_order(arr)
    return [int(v) for v in arr]


def verify_parent_witness(manifest_path: str | Path) -> dict[str, Any]:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    expected = manifest["release_manifest_witness"]
    actual = make_hash72_witness(
        expected["label"],
        None,
        canonical_payload=expected["canonical_payload"],
    ).to_dict()
    fields = ["dna", "positions", "rotation_profile", "trace_count", "zero_sum"]
    matches = {field: actual[field] == expected[field] for field in fields}
    return {
        "schema": "HHS_PASS133_PARENT_HASH72_REPAIR_VERIFICATION_V1",
        "ok": all(matches.values()),
        "matches": matches,
        "expected_digest": expected["digest"],
        "actual_digest": actual["digest"],
        "alphabet": HASH72_ALPHABET,
        "alphabet_length": len(HASH72_ALPHABET),
        "native_backend": str(_compile_native()),
    }
