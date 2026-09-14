"""ctypes bridge for Pass 219 Lane 5 Hash216/GPU phase interlace 1.37."""
from __future__ import annotations

import ctypes
import os
import pathlib
import platform
import subprocess
from ctypes import POINTER, Structure, c_uint8, c_uint32, c_uint64
from typing import Sequence

VERSION = 0x00010025
CYCLE = 20_020
QUARTER = 5_005
LANES = 4
MATRIX_ENTRIES = 16
HHS_EXACT_STATUS_OK = 0


class HHSExactPass219Lane5PhaseInterlaceAuthorityV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("full_cycle", c_uint32),
        ("quarter_cycle", c_uint32),
        ("lane_count", c_uint32),
        ("phase_states_per_lane", c_uint32),
        ("base_periods", c_uint32 * LANES),
        ("fixed_full_cycle_20020", c_uint8),
        ("quarter_sync_5005", c_uint8),
        ("prime_matrix_fingerprint_routing", c_uint8),
        ("consecutive_prime_cells_supported", c_uint8),
        ("validated_hash216_read_only", c_uint8),
        ("hash216_three_hash72_vector_search", c_uint8),
        ("pass205_continuation_hash216_bound", c_uint8),
        ("pass207_gpu_vector_search_bound", c_uint8),
        ("four_lane_parallel_encoding_search", c_uint8),
        ("gpu_candidate_only", c_uint8),
        ("exact_cpu_vm81_replay_required", c_uint8),
        ("canonical_vm81_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("requires_lane5_mediation", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("floating_point_canonical_authority", c_uint8),
        ("reserved0", c_uint8 * 6),
    ]


class HHSExactPass219Lane5PhaseAddressV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("tick_mod_cycle", c_uint32),
        ("quarter_index", c_uint32),
        ("residues", c_uint32 * LANES),
        ("phases", c_uint32 * LANES),
        ("address_signature64", c_uint64),
    ]


class HHSExactPass219Lane5PrimeMatrixV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("cell", c_uint32 * MATRIX_ENTRIES),
        ("offset", c_uint32 * LANES),
    ]


class HHSExactPass219Lane5PrimeRouteReceiptV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("tick_mod_cycle", c_uint32),
        ("routed_slot", c_uint32 * LANES),
        ("matrix_signature64", c_uint64),
        ("route_signature64", c_uint64),
        ("prime_cells_validated", c_uint8),
        ("upper_triangular", c_uint8),
        ("invertible_mod_cycle", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("requires_exact_cpu_vm81_replay", c_uint8),
    ]


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def _runtime_path() -> pathlib.Path:
    root = _repo_root()
    system = platform.system().lower()
    if system == "windows":
        name = "hhs_runtime.dll"
    elif system == "darwin":
        name = "libhhs_runtime.dylib"
    else:
        name = "libhhs_runtime.so"
    return root / "hhs_runtime" / "builds" / name


def _load_runtime() -> ctypes.CDLL:
    root = _repo_root()
    path = _runtime_path()
    disable = os.environ.get("HHS_DISABLE_C_AUTOBUILD", "").lower() in {
        "1", "true", "yes", "on"
    }
    if not path.exists() and not disable:
        subprocess.run(
            ["make", "c-abi"],
            cwd=str(root),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    if not path.exists():
        raise FileNotFoundError(f"HHS exact runtime shared library not found: {path}")
    return ctypes.CDLL(str(path))


class Pass219Lane5PhaseInterlaceBridge:
    def __init__(self) -> None:
        self.lib = _load_runtime()
        self.lib.hhs_exact_pass219_lane5_phase_interlace_version.argtypes = []
        self.lib.hhs_exact_pass219_lane5_phase_interlace_version.restype = c_uint32
        self.lib.hhs_exact_pass219_lane5_phase_interlace_authority.argtypes = [
            POINTER(HHSExactPass219Lane5PhaseInterlaceAuthorityV1)
        ]
        self.lib.hhs_exact_pass219_lane5_phase_interlace_authority.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_phase_address.argtypes = [
            c_uint64, POINTER(HHSExactPass219Lane5PhaseAddressV1)
        ]
        self.lib.hhs_exact_pass219_lane5_phase_address.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_prime_route.argtypes = [
            c_uint64,
            POINTER(HHSExactPass219Lane5PrimeMatrixV1),
            POINTER(HHSExactPass219Lane5PrimeRouteReceiptV1),
        ]
        self.lib.hhs_exact_pass219_lane5_prime_route.restype = ctypes.c_int

    def version(self) -> int:
        return int(self.lib.hhs_exact_pass219_lane5_phase_interlace_version())

    def authority(self) -> dict[str, object]:
        value = HHSExactPass219Lane5PhaseInterlaceAuthorityV1()
        status = self.lib.hhs_exact_pass219_lane5_phase_interlace_authority(ctypes.byref(value))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Lane 5 phase-interlace authority failed: {status}")
        result: dict[str, object] = {}
        for name, _ in value._fields_:
            item = getattr(value, name)
            if name == "base_periods":
                result[name] = [int(x) for x in item]
            elif name == "reserved0":
                continue
            else:
                result[name] = int(item)
        return result

    def phase_address(self, tick: int) -> dict[str, object]:
        if int(tick) < 0:
            raise ValueError("tick must be nonnegative")
        value = HHSExactPass219Lane5PhaseAddressV1()
        status = self.lib.hhs_exact_pass219_lane5_phase_address(
            int(tick), ctypes.byref(value)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Lane 5 phase address failed: {status}")
        return {
            "tick_mod_cycle": int(value.tick_mod_cycle),
            "quarter_index": int(value.quarter_index),
            "residues": [int(x) for x in value.residues],
            "phases": [int(x) for x in value.phases],
            "address_signature64": int(value.address_signature64),
        }

    def prime_route(
        self,
        tick: int,
        matrix: Sequence[Sequence[int]],
        offsets: Sequence[int],
    ) -> dict[str, object]:
        if int(tick) < 0:
            raise ValueError("tick must be nonnegative")
        if len(matrix) != LANES or any(len(row) != LANES for row in matrix):
            raise ValueError("prime matrix must be 4x4")
        if len(offsets) != LANES:
            raise ValueError("prime offsets must contain four values")

        native = HHSExactPass219Lane5PrimeMatrixV1()
        native.struct_size = ctypes.sizeof(native)
        native.version = VERSION
        ordinal = 0
        for row in matrix:
            for value in row:
                integer = int(value)
                if integer < 0 or integer > 0xFFFFFFFF:
                    raise ValueError("matrix value outside uint32")
                native.cell[ordinal] = integer
                ordinal += 1
        for index, value in enumerate(offsets):
            integer = int(value)
            if integer < 0 or integer > 0xFFFFFFFF:
                raise ValueError("offset outside uint32")
            native.offset[index] = integer

        receipt = HHSExactPass219Lane5PrimeRouteReceiptV1()
        status = self.lib.hhs_exact_pass219_lane5_prime_route(
            int(tick), ctypes.byref(native), ctypes.byref(receipt)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError(f"Lane 5 prime route rejected: status={status}")
        return {
            "tick_mod_cycle": int(receipt.tick_mod_cycle),
            "routed_slot": [int(x) for x in receipt.routed_slot],
            "matrix_signature64": int(receipt.matrix_signature64),
            "route_signature64": int(receipt.route_signature64),
            "prime_cells_validated": bool(receipt.prime_cells_validated),
            "upper_triangular": bool(receipt.upper_triangular),
            "invertible_mod_cycle": bool(receipt.invertible_mod_cycle),
            "candidate_only": bool(receipt.candidate_only),
            "canonical_mutation_authority": bool(receipt.canonical_mutation_authority),
            "canonical_hash72_authority": bool(receipt.canonical_hash72_authority),
            "canonical_hash216_authority": bool(receipt.canonical_hash216_authority),
            "requires_exact_cpu_vm81_replay": bool(receipt.requires_exact_cpu_vm81_replay),
        }


__all__ = [
    "CYCLE",
    "LANES",
    "QUARTER",
    "VERSION",
    "Pass219Lane5PhaseInterlaceBridge",
]
