"""ctypes bridge for the additive Pass 207 VM81 GPU hyperthread driver.

The native ABI exposes 5,184 stable logical lanes per batch (81 VM81 cells ×
64 logical hyperthreads). GPU output is always a candidate and is verified
against the exact CPU reference before it can be returned as verified.
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import pathlib
import platform
import subprocess
from ctypes import (
    POINTER,
    Structure,
    c_char,
    c_size_t,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    c_void_p,
)
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

API_VERSION = 1
CELL_COUNT = 81
BITS_PER_CELL = 64
LOGICAL_LANES = CELL_COUNT * BITS_PER_CELL
PHASE_DIMENSION = 72
CONTROL_COUNT = 243
Q_COUNT = LOGICAL_LANES * CONTROL_COUNT
PROJECTION_CHANNELS = 32
CACHE_KEY_BYTES = 32
UINT64_MASK = (1 << 64) - 1

BACKEND_AUTO = 0
BACKEND_CPU_REFERENCE = 1
BACKEND_OPENCL = 2

STATUS_OK = 0


class HHSPass207GPUConfig(Structure):
    _fields_ = [
        ("api_version", c_uint32),
        ("requested_backend", c_uint32),
        ("device_index", c_uint32),
        ("cache_capacity_bytes", c_uint64),
        ("cache_capacity_entries", c_uint32),
        ("verify_against_cpu", c_uint8),
        ("require_physical_gpu", c_uint8),
        ("reserved", c_uint8 * 6),
    ]


class HHSPass207Batch(Structure):
    _fields_ = [
        ("batch_size", c_uint32),
        ("state_soa", POINTER(c_uint64)),
        ("projection_soa", POINTER(c_uint32)),
        ("delta_offsets", POINTER(c_uint32)),
        ("delta_cells", POINTER(c_uint32)),
        ("delta_controls", POINTER(c_uint8)),
        ("delta_xor_masks", POINTER(c_uint64)),
        ("hydration_offsets", POINTER(c_uint32)),
        ("hydration_q", POINTER(c_uint32)),
        ("delta_count", c_uint32),
        ("hydration_count", c_uint32),
        ("input_cache_key", POINTER(c_uint8)),
        ("output_cache_key", POINTER(c_uint8)),
        ("reuse_cached_inputs", c_uint8),
        ("retain_outputs", c_uint8),
        ("reserved", c_uint8 * 6),
    ]


class HHSPass207BatchOutput(Structure):
    _fields_ = [
        ("child_state_soa", POINTER(c_uint64)),
        ("child_projection_soa", POINTER(c_uint32)),
        ("frontier_soa", POINTER(c_uint8)),
        ("hydration_valid", POINTER(c_uint8)),
    ]


class HHSPass207GPUStatus(Structure):
    _fields_ = [
        ("selected_backend", c_uint32),
        ("physical_gpu", c_uint8),
        ("deterministic_integer_only", c_uint8),
        ("verified_against_cpu", c_uint8),
        ("cache_input_hit", c_uint8),
        ("cache_output_retained", c_uint8),
        ("reserved", c_uint8 * 3),
        ("device_index", c_uint32),
        ("platform_count", c_uint32),
        ("device_count", c_uint32),
        ("logical_hyperthreads_per_cell", c_uint32),
        ("logical_lanes_per_batch", c_uint32),
        ("physical_workgroup_size", c_uint32),
        ("stable_lane_identity", c_uint8),
        ("disjoint_lane_writes", c_uint8),
        ("canonical_reduction_order", c_uint8),
        ("reserved_topology", c_uint8),
        ("dispatch_count", c_uint64),
        ("vector_dispatch_count", c_uint64),
        ("input_bytes_uploaded", c_uint64),
        ("output_bytes_downloaded", c_uint64),
        ("cache_hits", c_uint64),
        ("cache_misses", c_uint64),
        ("cache_evictions", c_uint64),
        ("cache_resident_bytes", c_uint64),
        ("cache_entries", c_uint32),
        ("backend_name", c_char * 32),
        ("device_name", c_char * 128),
        ("last_error", c_char * 256),
    ]


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def _source_paths() -> tuple[pathlib.Path, ...]:
    root = _repo_root()
    c_dir = root / "hhs_runtime" / "c"
    return (
        c_dir / "hhs_pass207_gpu_driver.c",
        c_dir / "hhs_pass207_gpu_driver.h",
        *(c_dir / f"hhs_pass207_gpu_driver_part{index}.inc" for index in range(1, 6)),
    )


def _library_path() -> pathlib.Path:
    root = _repo_root()
    system = platform.system().lower()
    if system == "windows":
        name = "hhs_pass207_gpu_driver.dll"
    elif system == "darwin":
        name = "libhhs_pass207_gpu_driver.dylib"
    else:
        name = "libhhs_pass207_gpu_driver.so"
    return root / "hhs_runtime" / "builds" / name


def build_native_library(*, force: bool = False) -> pathlib.Path:
    source, header, *segments = _source_paths()
    output = _library_path()
    if output.exists() and not force:
        newest_input = max(path.stat().st_mtime for path in (source, header, *segments))
        if output.stat().st_mtime >= newest_input:
            return output
    output.parent.mkdir(parents=True, exist_ok=True)
    cc = os.environ.get("CC", "cc")
    system = platform.system().lower()
    command = [
        cc,
        "-std=c11",
        "-O3",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-pedantic",
        f"-I{source.parent}",
    ]
    if system == "windows":
        command.extend(["-shared"])
    elif system == "darwin":
        command.extend(["-fPIC", "-dynamiclib"])
    else:
        command.extend(["-fPIC", "-shared"])
    command.append(str(source))
    if system not in {"windows", "darwin"}:
        command.append("-ldl")
    command.extend(["-o", str(output)])
    completed = subprocess.run(
        command,
        cwd=str(_repo_root()),
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Pass 207 GPU driver build failed:\n"
            + " ".join(command)
            + "\n"
            + completed.stdout
            + completed.stderr
        )
    return output


def _load_library() -> ctypes.CDLL:
    output = _library_path()
    disable = os.environ.get("HHS_DISABLE_PASS207_C_AUTOBUILD", "").lower() in {
        "1", "true", "yes", "on"
    }
    if not output.exists() and disable:
        raise FileNotFoundError(f"Pass 207 native GPU driver missing: {output}")
    if not output.exists():
        build_native_library()
    return ctypes.CDLL(str(output))


_LIB = _load_library()

_LIB.hhs_pass207_lane_address.argtypes = [c_uint8, c_uint8, POINTER(c_uint8)]
_LIB.hhs_pass207_lane_address.restype = c_uint16
_LIB.hhs_pass207_lane_decode.argtypes = [c_uint16, POINTER(c_uint8), POINTER(c_uint8)]
_LIB.hhs_pass207_lane_decode.restype = c_uint8
_LIB.hhs_pass207_lane_phase_coordinate.argtypes = [c_uint16, POINTER(c_uint8), POINTER(c_uint8)]
_LIB.hhs_pass207_lane_phase_coordinate.restype = c_uint8
_LIB.hhs_pass207_gpu_default_config.argtypes = []
_LIB.hhs_pass207_gpu_default_config.restype = HHSPass207GPUConfig
_LIB.hhs_pass207_gpu_create.argtypes = [POINTER(HHSPass207GPUConfig), POINTER(c_void_p)]
_LIB.hhs_pass207_gpu_create.restype = c_uint32
_LIB.hhs_pass207_gpu_destroy.argtypes = [c_void_p]
_LIB.hhs_pass207_gpu_destroy.restype = None
_LIB.hhs_pass207_gpu_get_status.argtypes = [c_void_p, POINTER(HHSPass207GPUStatus)]
_LIB.hhs_pass207_gpu_get_status.restype = c_uint32
_LIB.hhs_pass207_gpu_dispatch.argtypes = [c_void_p, POINTER(HHSPass207Batch), POINTER(HHSPass207BatchOutput)]
_LIB.hhs_pass207_gpu_dispatch.restype = c_uint32
_LIB.hhs_pass207_gpu_vector_distance72.argtypes = [
    c_void_p,
    POINTER(c_uint8),
    POINTER(c_uint8),
    c_uint32,
    POINTER(c_uint8),
    c_uint8,
    POINTER(c_uint32),
]
_LIB.hhs_pass207_gpu_vector_distance72.restype = c_uint32
_LIB.hhs_pass207_gpu_status_string.argtypes = [c_uint32]
_LIB.hhs_pass207_gpu_status_string.restype = ctypes.c_char_p


def _decode_text(value: object) -> str:
    return bytes(value).split(b"\0", 1)[0].decode("utf-8", errors="replace")


def _status_name(code: int) -> str:
    raw = _LIB.hhs_pass207_gpu_status_string(int(code))
    return raw.decode("ascii") if raw else f"STATUS_{code}"


def _cache_key(value: bytes | str | None) -> bytes:
    if value is None:
        return bytes(CACHE_KEY_BYTES)
    raw = value.encode("utf-8") if isinstance(value, str) else bytes(value)
    return raw if len(raw) == CACHE_KEY_BYTES else hashlib.sha256(raw).digest()


def _validate_u64(value: int) -> int:
    result = int(value)
    if result < 0 or result > UINT64_MASK:
        raise ValueError("value outside uint64")
    return result


@dataclass(frozen=True)
class DriverResult:
    child_states: list[list[int]]
    child_projections: list[list[list[int]]]
    frontiers: list[list[int]]
    hydration_valid: list[bool]
    status: dict[str, Any]
