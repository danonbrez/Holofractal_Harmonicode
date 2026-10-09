"""Typed Python ingress to the existing native Lane 5 1.34 candidate mediator.

This module is NOT an alternative optimizer, an ethical classifier, an
unsigned signature generator, or a canonical VM81 authority. It requires
already prepared, typed RNA/VM5184/Hash216 native signatures and calls the
existing compiled C Lane 5 mediation function. Full 5184-character canonical
state and ordered 216-character prompt/response witness are retained intact
as sidecar data: the C ABI's 64-bit signatures are never treated as lossless
substitutes for their underlying native tensor state.
"""
from __future__ import annotations

import ctypes
from ctypes import Structure, c_uint8, c_uint32, c_uint64
from dataclasses import dataclass
from typing import Any, Mapping

VERSION = 0x00010022
NAMESPACE = 0x00021905
MAX_REFS = 64
DECISION_CANDIDATE_READY = 1
HHS_EXACT_STATUS_OK = 0
SIGNATURE_FIELDS = (
    "request_signature64", "candidate_signature64",
    "parent_hash216_signature64", "bigint_address_signature64",
    "hydration_signature64", "compression_signature64",
    "capability_registry_signature64", "learning_iteration_signature64",
    "rna_prepared_signature64", "rna_decision_signature64",
)


class Lane5NativeMediationError(RuntimeError):
    """Native Lane 5 admission failed or was not available."""


class Lane5Request(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("namespace_id", c_uint32),
        ("hash216_reference_count", c_uint32),
        ("capability_reference_count", c_uint32),
        ("learning_stage", c_uint32),
        *((field, c_uint64) for field in SIGNATURE_FIELDS),
        ("hash216_reference_signature64", c_uint64 * MAX_REFS),
        ("capability_reference_signature64", c_uint64 * MAX_REFS),
    ]


class Lane5Receipt(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("namespace_id", c_uint32),
        ("decision", c_uint32),
        ("learning_stage", c_uint32),
        ("hash216_reference_count", c_uint32),
        ("capability_reference_count", c_uint32),
        *((field, c_uint64) for field in SIGNATURE_FIELDS),
        ("closure_signature64", c_uint64),
        ("mediation_signature64", c_uint64),
        ("hash216_references_validated", c_uint8),
        ("capability_registry_validated", c_uint8),
        ("exact_vm5184_bound", c_uint8),
        ("rna_cell_wall_bound", c_uint8),
        ("zero_sum_closure_passed", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("requires_environmental_admission", c_uint8),
        ("reserved0", c_uint8 * 5),
    ]


def _uint(value: Any, field: str, bits: int = 64, *, positive: bool = True) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Lane5NativeMediationError(f"{field}: integer required (no floating projection)")
    if not (int(positive) <= value < (1 << bits)):
        raise Lane5NativeMediationError(f"{field}: invalid exact unsigned range")
    return value


@dataclass(frozen=True)
class PreparedLane5Candidate:
    """An inherited prepared request, never fabricated from prompt strings.

    Callers must obtain signatures from the existing native preparation,
    hydration, lineage, capability and RNA decision lanes. The full canonical
    tensor state and ordered prompt/response witness are kept unchanged.
    """
    signatures: Mapping[str, int]
    hash216_references: tuple[int, ...]
    capability_references: tuple[int, ...]
    learning_stage: int
    raw5184: str
    ordered_transition_word216: str

    def __post_init__(self) -> None:
        if not isinstance(self.raw5184, str) or len(self.raw5184) != 5184:
            raise Lane5NativeMediationError("exact 5184-character state is required")
        if not isinstance(self.ordered_transition_word216, str) or len(self.ordered_transition_word216) != 216:
            raise Lane5NativeMediationError("ordered 216-character transition is required")
        if set(self.signatures) != set(SIGNATURE_FIELDS):
            raise Lane5NativeMediationError("all native prepared signature fields are required")
        for name in SIGNATURE_FIELDS:
            _uint(self.signatures[name], name, positive=name != "compression_signature64")
        _uint(self.learning_stage, "learning_stage", bits=32)
        for field, values in (
            ("hash216_references", self.hash216_references),
            ("capability_references", self.capability_references),
        ):
            if not isinstance(values, tuple) or not (1 <= len(values) <= MAX_REFS):
                raise Lane5NativeMediationError(f"{field}: expected 1..64 native references")
            for i, value in enumerate(values):
                _uint(value, f"{field}[{i}]")

    def native_request(self) -> Lane5Request:
        r = Lane5Request()
        r.struct_size = ctypes.sizeof(Lane5Request)
        r.version = VERSION
        r.namespace_id = NAMESPACE
        r.hash216_reference_count = len(self.hash216_references)
        r.capability_reference_count = len(self.capability_references)
        r.learning_stage = self.learning_stage
        for key in SIGNATURE_FIELDS:
            setattr(r, key, self.signatures[key])
        for i, v in enumerate(self.hash216_references):
            r.hash216_reference_signature64[i] = v
        for i, v in enumerate(self.capability_references):
            r.capability_reference_signature64[i] = v
        return r


def _native_library() -> Any:
    # Reuse the repository's existing exact runtime loader, not a new VM81
    # instance or a substitute Python evaluator.
    from hhs_python.runtime import hhs_uqcel_ctypes_bridge
    return hhs_uqcel_ctypes_bridge._LIB


def mediate_prepared_candidate(
    candidate: PreparedLane5Candidate, *, native_library: Any = None
) -> dict[str, Any]:
    if not isinstance(candidate, PreparedLane5Candidate):
        raise Lane5NativeMediationError("typed prepared Lane 5 candidate required")
    lib = native_library if native_library is not None else _native_library()
    try:
        version_function = lib.hhs_exact_pass219_lane5_nucleus_version
        mediate = lib.hhs_exact_pass219_lane5_mediate_candidate
    except AttributeError as exc:
        raise Lane5NativeMediationError("native Lane 5 mediation ABI unavailable") from exc

    version_function.restype = c_uint32
    mediate.argtypes = [ctypes.POINTER(Lane5Request), ctypes.POINTER(Lane5Receipt)]
    mediate.restype = ctypes.c_int
    if int(version_function()) != VERSION:
        raise Lane5NativeMediationError("native Lane 5 ABI version mismatch")

    request = candidate.native_request()
    receipt = Lane5Receipt()
    result = int(mediate(ctypes.byref(request), ctypes.byref(receipt)))
    if result != HHS_EXACT_STATUS_OK:
        raise Lane5NativeMediationError(f"native Lane 5 rejected candidate: status={result}")
    expected_echo = (
        ("version", VERSION), ("namespace_id", NAMESPACE),
        ("struct_size", ctypes.sizeof(Lane5Receipt)),
        ("learning_stage", candidate.learning_stage),
        ("hash216_reference_count", len(candidate.hash216_references)),
        ("capability_reference_count", len(candidate.capability_references)),
        *((field, getattr(request, field)) for field in SIGNATURE_FIELDS),
    )
    if any(getattr(receipt, key) != value for key, value in expected_echo):
        raise Lane5NativeMediationError("native Lane 5 receipt/provenance mismatch")
    positive_flags = (
        "hash216_references_validated", "capability_registry_validated",
        "exact_vm5184_bound", "rna_cell_wall_bound", "zero_sum_closure_passed",
        "candidate_only", "requires_environmental_admission",
    )
    forbidden_flags = (
        "canonical_mutation_authority", "canonical_hash72_authority",
        "canonical_hash216_authority", "canonical_persistence_authority",
    )
    if (
        receipt.decision != DECISION_CANDIDATE_READY
        or receipt.closure_signature64 == 0
        or receipt.mediation_signature64 == 0
        or any(getattr(receipt, flag) != 1 for flag in positive_flags)
        or any(getattr(receipt, flag) != 0 for flag in forbidden_flags)
    ):
        raise Lane5NativeMediationError("native Lane 5 authority/closure invariant failure")

    return {
        "schema": "HHS_NATIVE_LANE5_MEDIATION_PROJECTION_V1",
        "status": "CANDIDATE_READY_NOT_CANONICAL_MUTATION",
        "native_abi_version": VERSION,
        "native_namespace_id": NAMESPACE,
        "native_decision": receipt.decision,
        "native_learning_stage": receipt.learning_stage,
        "closure_signature64": int(receipt.closure_signature64),
        "mediation_signature64": int(receipt.mediation_signature64),
        # The full raw 5184 carrier and ordered transition are retained by
        # the caller's PreparedLane5Candidate; they must never be exposed in
        # ordinary health, receipt, or model-visible result projections.
        "ordered_transition_word216_length": len(candidate.ordered_transition_word216),
        "raw5184_character_count": len(candidate.raw5184),
        "raw_state_exposed_in_result": False,
        "full_native_state_recoverable_from_signature64_alone": False,
        "native_input_signatures": {k: getattr(request, k) for k in SIGNATURE_FIELDS},
        "native_hash216_reference_signatures": list(candidate.hash216_references),
        "native_capability_reference_signatures": list(candidate.capability_references),
        "read_only_candidate": True,
        "requires_signed_environmental_vm81_admission": True,
        "canonical_mutation_admitted": False,
        "external_signature_provenance_independently_verified": False,
    }
