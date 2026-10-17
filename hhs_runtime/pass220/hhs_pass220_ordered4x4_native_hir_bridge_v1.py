"""Read-only ctypes binding for native 4x4 HIR candidate lowering.

The native C ABI performs exact source-locked frame construction. This wrapper
does not compute HHS MatrixTimes, matrix power, matrix division, s or v.
"""
from __future__ import annotations
import ctypes
from dataclasses import dataclass
from pathlib import Path

from hhs_runtime.pass220.hhs_pass220_ordered_4x4_neg4_matrix_tensor_v1 import (
    SOURCE_PATH, SOURCE_SHA256, MatrixTensorHIRReject, stage_hir,
)

class _Frame(ctypes.Structure):
    _fields_ = [("words", ctypes.c_uint64 * 81)]

class _Witness(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("rows", ctypes.c_uint32),
        ("columns", ctypes.c_uint32),
        ("matrix_occurrences", ctypes.c_uint32),
        ("literal_cells", ctypes.c_uint32),
        ("exponent_magnitude", ctypes.c_uint32),
        ("exponent_negative", ctypes.c_uint8),
        ("numerator_negative_operand_count", ctypes.c_uint8),
        ("source_identity_verified", ctypes.c_uint8),
        ("ordered_topology_verified", ctypes.c_uint8),
        ("typed_s_unresolved", ctypes.c_uint8),
        ("typed_v_unresolved", ctypes.c_uint8),
        ("matrix_power_value_derived", ctypes.c_uint8),
        ("native_matrix_division_evaluated", ctypes.c_uint8),
        ("vm81_admission_executed", ctypes.c_uint8),
        ("hash72_commit_authority", ctypes.c_uint8),
        ("hash216_commit_authority", ctypes.c_uint8),
        ("canonical_vm81_mutation_authority", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8 * 2),
        ("source_sha256", ctypes.c_uint8 * 32),
        ("topology_sha256", ctypes.c_uint8 * 32),
    ]

@dataclass(frozen=True)
class CandidateHIRFrame:
    source_sha256: str
    topology_sha256: str
    words: tuple[int, ...]
    typed_s_unresolved: bool
    typed_v_unresolved: bool
    source_identity_verified: bool
    ordered_topology_verified: bool
    vm81_admission_executed: bool
    matrix_power_value_derived: bool
    hash72_commit_authority: bool
    hash216_commit_authority: bool
    canonical_vm81_mutation_authority: bool

class Ordered4x4NativeHIRBridge:
    def __init__(self, shared_library: str | Path):
        self._lib = ctypes.CDLL(str(shared_library))
        self._lower = self._lib.hhs_exact_pass220_ordered4x4_lower
        self._lower.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(_Frame), ctypes.POINTER(_Witness),
        ]
        self._lower.restype = ctypes.c_int

    def lower(self, *, root: str | Path | None = None) -> CandidateHIRFrame:
        # First enforce the source's full ordered AST and frozen identity.
        hir = stage_hir(root)
        repo = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[2]
        source = (repo / SOURCE_PATH).read_bytes()
        raw = (ctypes.c_uint8 * len(source)).from_buffer_copy(source)
        frame, witness = _Frame(), _Witness()
        result = self._lower(raw, len(source), ctypes.byref(frame), ctypes.byref(witness))
        if result != 0:
            raise MatrixTensorHIRReject(f"NATIVE_HIR_LOWER_REJECTED:{result}")
        if bytes(witness.source_sha256).hex() != SOURCE_SHA256 or hir["source_sha256"] != SOURCE_SHA256:
            raise MatrixTensorHIRReject("NATIVE_SOURCE_IDENTITY_MISMATCH")
        if not (witness.ordered_topology_verified and witness.source_identity_verified):
            raise MatrixTensorHIRReject("NATIVE_HIR_TOPOLOGY_NOT_VERIFIED")
        if not (witness.rows == witness.columns == 4
                and witness.literal_cells == 64
                and witness.exponent_magnitude == 4
                and witness.exponent_negative == 1
                and witness.numerator_negative_operand_count == 2
                and witness.typed_s_unresolved == 1
                and witness.typed_v_unresolved == 1):
            raise MatrixTensorHIRReject("NATIVE_4X4_HIR_DESCRIPTOR_DRIFT")
        if any((witness.matrix_power_value_derived, witness.native_matrix_division_evaluated,
                witness.vm81_admission_executed, witness.hash72_commit_authority,
                witness.hash216_commit_authority, witness.canonical_vm81_mutation_authority)):
            raise MatrixTensorHIRReject("NATIVE_HIR_AUTHORITY_ESCALATION")
        return CandidateHIRFrame(
            source_sha256=bytes(witness.source_sha256).hex(),
            topology_sha256=bytes(witness.topology_sha256).hex(),
            words=tuple(frame.words),
            typed_s_unresolved=True,
            typed_v_unresolved=True,
            source_identity_verified=True,
            ordered_topology_verified=True,
            vm81_admission_executed=False,
            matrix_power_value_derived=False,
            hash72_commit_authority=False,
            hash216_commit_authority=False,
            canonical_vm81_mutation_authority=False,
        )
