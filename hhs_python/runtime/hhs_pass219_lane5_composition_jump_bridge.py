"""ctypes bridge for Pass 219 Lane 5 Hash216 composition-jump store 1.38."""
from __future__ import annotations

import ctypes
import os
import pathlib
import platform
import subprocess
from ctypes import POINTER, Structure, c_uint8, c_uint32, c_uint64

VERSION = 0x00010026
CYCLE = 20_020
HHS_EXACT_STATUS_OK = 0


class HHSExactPass219Lane5CompositionJumpAuthorityV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("full_cycle", c_uint32),
        ("validated_hash216_jump_store", c_uint8),
        ("exact_registration_replay_required", c_uint8),
        ("direct_candidate_reuse_allowed", c_uint8),
        ("prime_fingerprint_search_bound", c_uint8),
        ("recursive_layer_tagged", c_uint8),
        ("immutable_composition_seal_required", c_uint8),
        ("gpu_vector_search_candidate_only", c_uint8),
        ("canonical_vm81_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("floating_point_canonical_authority", c_uint8),
        ("reserved0", c_uint8 * 3),
    ]


class HHSExactPass219Lane5CompositionJumpDescriptorV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("jump_span", c_uint32),
        ("phase_slot", c_uint32),
        ("cycle_index", c_uint64),
        ("layer_index", c_uint32),
        ("reserved0", c_uint32),
        ("parent_signature64", c_uint64),
        ("child_signature64", c_uint64),
        ("composition_signature64", c_uint64),
        ("validated", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved1", c_uint8 * 2),
    ]


class HHSExactPass219Lane5CompositionJumpReceiptV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("jump_span", c_uint32),
        ("phase_slot", c_uint32),
        ("cycle_index", c_uint64),
        ("layer_index", c_uint32),
        ("reserved0", c_uint32),
        ("descriptor_signature64", c_uint64),
        ("reuse_signature64", c_uint64),
        ("accepted", c_uint8),
        ("validated_hash216_lineage", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved1", c_uint8),
    ]


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def _runtime_path() -> pathlib.Path:
    root = _repo_root()
    system = platform.system().lower()
    name = "hhs_runtime.dll" if system == "windows" else (
        "libhhs_runtime.dylib" if system == "darwin" else "libhhs_runtime.so"
    )
    return root / "hhs_runtime" / "builds" / name


def _load_runtime() -> ctypes.CDLL:
    root = _repo_root()
    path = _runtime_path()
    disable = os.environ.get("HHS_DISABLE_C_AUTOBUILD", "").lower() in {
        "1", "true", "yes", "on"
    }
    if not path.exists() and not disable:
        subprocess.run(
            ["make", "c-abi"], cwd=str(root), check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
    if not path.exists():
        raise FileNotFoundError(f"HHS exact runtime shared library not found: {path}")
    return ctypes.CDLL(str(path))


def signature64_from_hash216(value: str) -> int:
    if len(value) != 216:
        raise ValueError("Hash216 value must contain exactly 216 symbols")
    acc = 0x9E3779B97F4A7C15
    for byte in value.encode("ascii"):
        acc ^= byte
        acc = ((acc << 7) | (acc >> 57)) & ((1 << 64) - 1)
        acc = (acc * 0x100000001B3) & ((1 << 64) - 1)
    return acc or 1


class Pass219Lane5CompositionJumpBridge:
    def __init__(self) -> None:
        self.lib = _load_runtime()
        self.lib.hhs_exact_pass219_lane5_composition_jump_version.argtypes = []
        self.lib.hhs_exact_pass219_lane5_composition_jump_version.restype = c_uint32
        self.lib.hhs_exact_pass219_lane5_composition_jump_authority.argtypes = [
            POINTER(HHSExactPass219Lane5CompositionJumpAuthorityV1)
        ]
        self.lib.hhs_exact_pass219_lane5_composition_jump_authority.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_composition_jump_validate.argtypes = [
            POINTER(HHSExactPass219Lane5CompositionJumpDescriptorV1),
            POINTER(HHSExactPass219Lane5CompositionJumpReceiptV1),
        ]
        self.lib.hhs_exact_pass219_lane5_composition_jump_validate.restype = ctypes.c_int

    def version(self) -> int:
        return int(self.lib.hhs_exact_pass219_lane5_composition_jump_version())

    def authority(self) -> dict[str, int]:
        value = HHSExactPass219Lane5CompositionJumpAuthorityV1()
        status = self.lib.hhs_exact_pass219_lane5_composition_jump_authority(ctypes.byref(value))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Lane 5 composition-jump authority failed: {status}")
        return {
            name: int(getattr(value, name))
            for name, _ in value._fields_
            if name != "reserved0"
        }

    def validate_descriptor(
        self,
        *,
        parent_hash216: str,
        child_hash216: str,
        composition_hash216: str,
        jump_span: int,
        phase_slot: int,
        cycle_index: int,
        layer_index: int,
    ) -> dict[str, int | bool]:
        if min(int(jump_span), int(phase_slot), int(cycle_index), int(layer_index)) < 0:
            raise ValueError("composition-jump coordinates must be nonnegative")
        value = HHSExactPass219Lane5CompositionJumpDescriptorV1()
        value.struct_size = ctypes.sizeof(value)
        value.version = VERSION
        value.jump_span = int(jump_span)
        value.phase_slot = int(phase_slot)
        value.cycle_index = int(cycle_index)
        value.layer_index = int(layer_index)
        value.parent_signature64 = signature64_from_hash216(parent_hash216)
        value.child_signature64 = signature64_from_hash216(child_hash216)
        value.composition_signature64 = signature64_from_hash216(composition_hash216)
        value.validated = 1
        value.candidate_only = 1
        value.requires_signed_environmental_vm81_admission = 1
        receipt = HHSExactPass219Lane5CompositionJumpReceiptV1()
        status = self.lib.hhs_exact_pass219_lane5_composition_jump_validate(
            ctypes.byref(value), ctypes.byref(receipt)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError(f"Lane 5 composition jump rejected: status={status}")
        return {
            "jump_span": int(receipt.jump_span),
            "phase_slot": int(receipt.phase_slot),
            "cycle_index": int(receipt.cycle_index),
            "layer_index": int(receipt.layer_index),
            "descriptor_signature64": int(receipt.descriptor_signature64),
            "reuse_signature64": int(receipt.reuse_signature64),
            "accepted": bool(receipt.accepted),
            "validated_hash216_lineage": bool(receipt.validated_hash216_lineage),
            "candidate_only": bool(receipt.candidate_only),
            "canonical_mutation_authority": bool(receipt.canonical_mutation_authority),
            "canonical_hash72_authority": bool(receipt.canonical_hash72_authority),
            "canonical_hash216_authority": bool(receipt.canonical_hash216_authority),
            "requires_signed_environmental_vm81_admission": bool(
                receipt.requires_signed_environmental_vm81_admission
            ),
        }


__all__ = [
    "CYCLE", "VERSION", "Pass219Lane5CompositionJumpBridge", "signature64_from_hash216"
]
