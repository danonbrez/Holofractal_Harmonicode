"""ctypes bridge for Pass 219 Lane 5 persistent Hash216 composition memory 1.39."""
from __future__ import annotations

import ctypes
import hashlib
import operator
import os
import pathlib
import platform
import subprocess
from ctypes import POINTER, Structure, c_uint8, c_uint32, c_uint64

from hhs_python.runtime.hhs_pass219_lane5_composition_jump_bridge import (
    signature64_from_hash216,
)

VERSION = 0x00010027
CYCLE = 20_020
SNAPSHOT_BYTES = 648
HHS_EXACT_STATUS_OK = 0
UINT32_MAX = (1 << 32) - 1
UINT64_MAX = (1 << 64) - 1


class HHSExactPass219Lane5PersistentCompositionAuthorityV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("full_cycle", c_uint32),
        ("snapshot_bytes", c_uint32),
        ("pass174_persistent_encrypted_vector_store_bound", c_uint8),
        ("pass194_hash216_positional_index_bound", c_uint8),
        ("sqlite_wal_required", c_uint8),
        ("sqlite_synchronous_full_required", c_uint8),
        ("aes_gcm_authenticated_snapshot_encryption", c_uint8),
        ("restart_rehydration_supported", c_uint8),
        ("metadata_hash216_seal_required", c_uint8),
        ("vm5184_little_endian_word_frame", c_uint8),
        ("recursive_layer_index_persisted", c_uint8),
        ("gpu_vector_search_candidate_only", c_uint8),
        ("canonical_vm81_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("floating_point_canonical_authority", c_uint8),
    ]


class HHSExactPass219Lane5PersistentCompositionDescriptorV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("jump_span", c_uint32),
        ("phase_slot", c_uint32),
        ("cycle_index", c_uint64),
        ("layer_index", c_uint32),
        ("snapshot_bytes", c_uint32),
        ("parent_signature64", c_uint64),
        ("child_signature64", c_uint64),
        ("composition_signature64", c_uint64),
        ("metadata_signature64", c_uint64),
        ("vector_object_signature64", c_uint64),
        ("persisted", c_uint8),
        ("encrypted", c_uint8),
        ("authenticated", c_uint8),
        ("metadata_sealed", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved0", c_uint8 * 6),
    ]


class HHSExactPass219Lane5PersistentCompositionReceiptV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("jump_span", c_uint32),
        ("phase_slot", c_uint32),
        ("cycle_index", c_uint64),
        ("layer_index", c_uint32),
        ("snapshot_bytes", c_uint32),
        ("descriptor_signature64", c_uint64),
        ("persistence_signature64", c_uint64),
        ("accepted", c_uint8),
        ("restart_rehydratable", c_uint8),
        ("encrypted_vector_bound", c_uint8),
        ("metadata_hash216_bound", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved0", c_uint8 * 6),
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


def signature64_from_text(value: str) -> int:
    if not isinstance(value, str) or not value:
        raise ValueError("persistent identity text must be nonempty")
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "little") or 1


def _exact_unsigned(value: object, *, name: str, maximum: int) -> int:
    try:
        integer = operator.index(value)
    except TypeError as exc:
        raise ValueError(f"{name} must be an exact integer") from exc
    if integer < 0 or integer > maximum:
        raise ValueError(f"{name} outside unsigned ABI range")
    return int(integer)


class Pass219Lane5PersistentCompositionMemoryBridge:
    def __init__(self) -> None:
        self.lib = _load_runtime()
        self.lib.hhs_exact_pass219_lane5_persistent_composition_memory_version.argtypes = []
        self.lib.hhs_exact_pass219_lane5_persistent_composition_memory_version.restype = c_uint32
        self.lib.hhs_exact_pass219_lane5_persistent_composition_memory_authority.argtypes = [
            POINTER(HHSExactPass219Lane5PersistentCompositionAuthorityV1)
        ]
        self.lib.hhs_exact_pass219_lane5_persistent_composition_memory_authority.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_persistent_composition_validate.argtypes = [
            POINTER(HHSExactPass219Lane5PersistentCompositionDescriptorV1),
            POINTER(HHSExactPass219Lane5PersistentCompositionReceiptV1),
        ]
        self.lib.hhs_exact_pass219_lane5_persistent_composition_validate.restype = ctypes.c_int

    def version(self) -> int:
        return int(self.lib.hhs_exact_pass219_lane5_persistent_composition_memory_version())

    def authority(self) -> dict[str, int]:
        value = HHSExactPass219Lane5PersistentCompositionAuthorityV1()
        status = self.lib.hhs_exact_pass219_lane5_persistent_composition_memory_authority(
            ctypes.byref(value)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Lane 5 persistent composition authority failed: {status}")
        return {name: int(getattr(value, name)) for name, _ in value._fields_}

    def validate_descriptor(
        self,
        *,
        parent_hash216: str,
        child_hash216: str,
        composition_hash216: str,
        metadata_hash216: str,
        vector_object_id: str,
        jump_span: int,
        phase_slot: int,
        cycle_index: int,
        layer_index: int,
    ) -> dict[str, int | bool]:
        jump_span_exact = _exact_unsigned(jump_span, name="jump_span", maximum=UINT32_MAX)
        phase_slot_exact = _exact_unsigned(phase_slot, name="phase_slot", maximum=UINT32_MAX)
        cycle_index_exact = _exact_unsigned(cycle_index, name="cycle_index", maximum=UINT64_MAX)
        layer_index_exact = _exact_unsigned(layer_index, name="layer_index", maximum=UINT32_MAX)
        value = HHSExactPass219Lane5PersistentCompositionDescriptorV1()
        value.struct_size = ctypes.sizeof(value)
        value.version = VERSION
        value.jump_span = jump_span_exact
        value.phase_slot = phase_slot_exact
        value.cycle_index = cycle_index_exact
        value.layer_index = layer_index_exact
        value.snapshot_bytes = SNAPSHOT_BYTES
        value.parent_signature64 = signature64_from_hash216(parent_hash216)
        value.child_signature64 = signature64_from_hash216(child_hash216)
        value.composition_signature64 = signature64_from_hash216(composition_hash216)
        value.metadata_signature64 = signature64_from_hash216(metadata_hash216)
        value.vector_object_signature64 = signature64_from_text(vector_object_id)
        value.persisted = 1
        value.encrypted = 1
        value.authenticated = 1
        value.metadata_sealed = 1
        value.candidate_only = 1
        value.requires_signed_environmental_vm81_admission = 1
        receipt = HHSExactPass219Lane5PersistentCompositionReceiptV1()
        status = self.lib.hhs_exact_pass219_lane5_persistent_composition_validate(
            ctypes.byref(value), ctypes.byref(receipt)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError(f"Lane 5 persistent composition rejected: status={status}")
        return {
            "jump_span": int(receipt.jump_span),
            "phase_slot": int(receipt.phase_slot),
            "cycle_index": int(receipt.cycle_index),
            "layer_index": int(receipt.layer_index),
            "snapshot_bytes": int(receipt.snapshot_bytes),
            "descriptor_signature64": int(receipt.descriptor_signature64),
            "persistence_signature64": int(receipt.persistence_signature64),
            "accepted": bool(receipt.accepted),
            "restart_rehydratable": bool(receipt.restart_rehydratable),
            "encrypted_vector_bound": bool(receipt.encrypted_vector_bound),
            "metadata_hash216_bound": bool(receipt.metadata_hash216_bound),
            "candidate_only": bool(receipt.candidate_only),
            "canonical_mutation_authority": bool(receipt.canonical_mutation_authority),
            "canonical_hash72_authority": bool(receipt.canonical_hash72_authority),
            "canonical_hash216_authority": bool(receipt.canonical_hash216_authority),
            "canonical_persistence_authority": bool(receipt.canonical_persistence_authority),
            "requires_signed_environmental_vm81_admission": bool(
                receipt.requires_signed_environmental_vm81_admission
            ),
        }


__all__ = [
    "CYCLE", "SNAPSHOT_BYTES", "VERSION",
    "Pass219Lane5PersistentCompositionMemoryBridge",
    "signature64_from_text",
]
