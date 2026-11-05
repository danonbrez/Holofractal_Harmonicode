"""Pass 220 I078 Python binding for VM81 candidate-boundary expansion.

The binding calls the native additive exact ABI. It does not reproduce the
I077/I078 admission, UQCEL, 1001/1000 scaling, or Hash216 logic in Python.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path

SCHEMA = "HHS_PASS_220_I078_VM81_CANDIDATE_BOUNDARY_EXPANSION_V1"
VM81_WORDS = 81
HASH72_STRLEN = 73
HASH216_STRLEN = 217
SHA256_HEX_STRLEN = 65


class I078BoundaryError(RuntimeError):
    pass


class VM81Frame(ctypes.Structure):
    _fields_ = [("words", ctypes.c_uint64 * VM81_WORDS)]


class _Descriptor(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("node_count", ctypes.c_uint32),
        ("frame_words", ctypes.c_uint32),
        ("scale_numerator", ctypes.c_uint32),
        ("scale_denominator", ctypes.c_uint32),
        ("root_seed_numerator", ctypes.c_uint64),
        ("root_seed_denominator", ctypes.c_uint32),
        ("i077_binding_required", ctypes.c_uint8),
        ("downstream_candidate_ingress", ctypes.c_uint8),
        ("byte_exact_candidate_identity", ctypes.c_uint8),
        ("uqcel_identity_evaluation", ctypes.c_uint8),
        ("exact_rational_scale1001", ctypes.c_uint8),
        ("zero_energy_fixed_point", ctypes.c_uint8),
        ("delta_e_zero_required", ctypes.c_uint8),
        ("psi_zero_required", ctypes.c_uint8),
        ("omega_true_required", ctypes.c_uint8),
        ("deterministic_replay_required", ctypes.c_uint8),
        ("fail_closed_invalid_candidate", ctypes.c_uint8),
        ("host_matrixpower_authority", ctypes.c_uint8),
        ("host_square_matrix_fallback_authority", ctypes.c_uint8),
        ("floating_point_authority", ctypes.c_uint8),
        ("numeric_exponent_evaluation_authority", ctypes.c_uint8),
        ("canonical_vm81_mutation_authority", ctypes.c_uint8),
        ("canonical_hash72_commit_authority", ctypes.c_uint8),
        ("canonical_hash216_commit_authority", ctypes.c_uint8),
        ("canonical_persistence_authority", ctypes.c_uint8),
        ("external_egress_authority", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8 * 4),
    ]


class _Boundary(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("decision", ctypes.c_uint32),
        ("reason", ctypes.c_uint32),
        ("node_id", ctypes.c_uint32),
        ("frame_words", ctypes.c_uint32),
        ("scale_numerator", ctypes.c_uint32),
        ("scale_denominator", ctypes.c_uint32),
        ("scale_words_verified", ctypes.c_uint32),
        ("zero_word_count", ctypes.c_uint32),
        ("zero_fixed_point_words_verified", ctypes.c_uint32),
        ("i077_execution_verified", ctypes.c_uint8),
        ("candidate_frame_exact", ctypes.c_uint8),
        ("uqcel_identity_evaluated", ctypes.c_uint8),
        ("uqcel_transition_matches_i077", ctypes.c_uint8),
        ("exact_scale1001_verified", ctypes.c_uint8),
        ("zero_energy_fixed_point_verified", ctypes.c_uint8),
        ("delta_e_zero", ctypes.c_uint8),
        ("psi_zero", ctypes.c_uint8),
        ("omega_true", ctypes.c_uint8),
        ("deterministic_replay_verified", ctypes.c_uint8),
        ("fail_closed_boundary", ctypes.c_uint8),
        ("host_matrixpower_used", ctypes.c_uint8),
        ("square_matrix_fallback_used", ctypes.c_uint8),
        ("floating_point_used", ctypes.c_uint8),
        ("numeric_exponent_evaluated", ctypes.c_uint8),
        ("canonical_state_persisted", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8 * 7),
        ("delta_e_numerator", ctypes.c_int64),
        ("delta_e_denominator", ctypes.c_uint64),
        ("psi_numerator", ctypes.c_int64),
        ("psi_denominator", ctypes.c_uint64),
        ("candidate_sha256", ctypes.c_char * SHA256_HEX_STRLEN),
        ("scale_witness_sha256", ctypes.c_char * SHA256_HEX_STRLEN),
        ("i077_receipt_hash72", ctypes.c_char * HASH72_STRLEN),
        ("i077_transition_hash216", ctypes.c_char * HASH216_STRLEN),
        ("boundary_change_hash72", ctypes.c_char * HASH72_STRLEN),
        ("boundary_receipt_hash72", ctypes.c_char * HASH72_STRLEN),
        ("boundary_hash216", ctypes.c_char * HASH216_STRLEN),
        ("boundary_identity216", ctypes.c_char * HASH216_STRLEN),
    ]


@dataclass(frozen=True)
class CandidateBoundary:
    schema: str
    node_id: int
    decision: int
    reason: int
    frame_words: int
    scale_numerator: int
    scale_denominator: int
    scale_words_verified: int
    zero_word_count: int
    zero_fixed_point_words_verified: int
    delta_e_numerator: int
    delta_e_denominator: int
    psi_numerator: int
    psi_denominator: int
    candidate_sha256: str
    scale_witness_sha256: str
    i077_receipt_hash72: str
    i077_transition_hash216: str
    boundary_change_hash72: str
    boundary_receipt_hash72: str
    boundary_hash216: str
    boundary_identity216: str
    i077_execution_verified: bool
    candidate_frame_exact: bool
    uqcel_identity_evaluated: bool
    uqcel_transition_matches_i077: bool
    exact_scale1001_verified: bool
    zero_energy_fixed_point_verified: bool
    delta_e_zero: bool
    psi_zero: bool
    omega_true: bool
    deterministic_replay_verified: bool
    fail_closed_boundary: bool
    host_matrixpower_used: bool
    square_matrix_fallback_used: bool
    floating_point_used: bool
    numeric_exponent_evaluated: bool
    canonical_state_persisted: bool


def _decode(value: bytes) -> str:
    return value.split(b"\0", 1)[0].decode("ascii")


class VM81CandidateBoundaryExecutor:
    def __init__(self, exact_abi_library: str | Path):
        self.library_path = str(Path(exact_abi_library))
        self._lib = ctypes.CDLL(self.library_path)
        self._lib.hhs_exact_pass220_i078_version.argtypes = []
        self._lib.hhs_exact_pass220_i078_version.restype = ctypes.c_uint32
        self._lib.hhs_exact_pass220_i078_descriptor.argtypes = [
            ctypes.POINTER(_Descriptor)
        ]
        self._lib.hhs_exact_pass220_i078_descriptor.restype = ctypes.c_int
        self._lib.hhs_exact_pass220_i078_reference_candidate.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(VM81Frame),
        ]
        self._lib.hhs_exact_pass220_i078_reference_candidate.restype = ctypes.c_int
        self._lib.hhs_exact_pass220_i078_expand_candidate_boundary.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(VM81Frame),
            ctypes.POINTER(_Boundary),
        ]
        self._lib.hhs_exact_pass220_i078_expand_candidate_boundary.restype = ctypes.c_int

        self.version = int(self._lib.hhs_exact_pass220_i078_version())
        descriptor = _Descriptor()
        status = int(
            self._lib.hhs_exact_pass220_i078_descriptor(
                ctypes.byref(descriptor)
            )
        )
        if status != 0:
            raise I078BoundaryError(f"I078_DESCRIPTOR_REJECTED:{status}")

        self.descriptor = {
            "node_count": int(descriptor.node_count),
            "frame_words": int(descriptor.frame_words),
            "scale_numerator": int(descriptor.scale_numerator),
            "scale_denominator": int(descriptor.scale_denominator),
            "root_seed_numerator": int(descriptor.root_seed_numerator),
            "root_seed_denominator": int(descriptor.root_seed_denominator),
            "i077_binding_required": bool(descriptor.i077_binding_required),
            "downstream_candidate_ingress": bool(
                descriptor.downstream_candidate_ingress
            ),
            "byte_exact_candidate_identity": bool(
                descriptor.byte_exact_candidate_identity
            ),
            "uqcel_identity_evaluation": bool(
                descriptor.uqcel_identity_evaluation
            ),
            "exact_rational_scale1001": bool(
                descriptor.exact_rational_scale1001
            ),
            "zero_energy_fixed_point": bool(
                descriptor.zero_energy_fixed_point
            ),
            "delta_e_zero_required": bool(descriptor.delta_e_zero_required),
            "psi_zero_required": bool(descriptor.psi_zero_required),
            "omega_true_required": bool(descriptor.omega_true_required),
            "deterministic_replay_required": bool(
                descriptor.deterministic_replay_required
            ),
            "fail_closed_invalid_candidate": bool(
                descriptor.fail_closed_invalid_candidate
            ),
            "host_matrixpower_authority": bool(
                descriptor.host_matrixpower_authority
            ),
            "host_square_matrix_fallback_authority": bool(
                descriptor.host_square_matrix_fallback_authority
            ),
            "floating_point_authority": bool(
                descriptor.floating_point_authority
            ),
            "numeric_exponent_evaluation_authority": bool(
                descriptor.numeric_exponent_evaluation_authority
            ),
            "canonical_vm81_mutation_authority": bool(
                descriptor.canonical_vm81_mutation_authority
            ),
            "canonical_hash72_commit_authority": bool(
                descriptor.canonical_hash72_commit_authority
            ),
            "canonical_hash216_commit_authority": bool(
                descriptor.canonical_hash216_commit_authority
            ),
            "canonical_persistence_authority": bool(
                descriptor.canonical_persistence_authority
            ),
            "external_egress_authority": bool(
                descriptor.external_egress_authority
            ),
        }

    def reference_candidate(self, node_id: int) -> VM81Frame:
        frame = VM81Frame()
        status = int(
            self._lib.hhs_exact_pass220_i078_reference_candidate(
                int(node_id), ctypes.byref(frame)
            )
        )
        if status != 0:
            raise I078BoundaryError(
                f"I078_REFERENCE_CANDIDATE_REJECTED:{status}:{node_id}"
            )
        return frame

    def expand(
        self,
        node_id: int,
        candidate: VM81Frame,
    ) -> CandidateBoundary:
        native = _Boundary()
        status = int(
            self._lib.hhs_exact_pass220_i078_expand_candidate_boundary(
                int(node_id),
                ctypes.byref(candidate),
                ctypes.byref(native),
            )
        )
        if status != 0 or native.decision != 1:
            raise I078BoundaryError(
                f"I078_BOUNDARY_REJECTED:{status}:{native.reason}"
            )
        return CandidateBoundary(
            schema=SCHEMA,
            node_id=int(native.node_id),
            decision=int(native.decision),
            reason=int(native.reason),
            frame_words=int(native.frame_words),
            scale_numerator=int(native.scale_numerator),
            scale_denominator=int(native.scale_denominator),
            scale_words_verified=int(native.scale_words_verified),
            zero_word_count=int(native.zero_word_count),
            zero_fixed_point_words_verified=int(
                native.zero_fixed_point_words_verified
            ),
            delta_e_numerator=int(native.delta_e_numerator),
            delta_e_denominator=int(native.delta_e_denominator),
            psi_numerator=int(native.psi_numerator),
            psi_denominator=int(native.psi_denominator),
            candidate_sha256=_decode(bytes(native.candidate_sha256)),
            scale_witness_sha256=_decode(bytes(native.scale_witness_sha256)),
            i077_receipt_hash72=_decode(bytes(native.i077_receipt_hash72)),
            i077_transition_hash216=_decode(
                bytes(native.i077_transition_hash216)
            ),
            boundary_change_hash72=_decode(
                bytes(native.boundary_change_hash72)
            ),
            boundary_receipt_hash72=_decode(
                bytes(native.boundary_receipt_hash72)
            ),
            boundary_hash216=_decode(bytes(native.boundary_hash216)),
            boundary_identity216=_decode(bytes(native.boundary_identity216)),
            i077_execution_verified=bool(native.i077_execution_verified),
            candidate_frame_exact=bool(native.candidate_frame_exact),
            uqcel_identity_evaluated=bool(native.uqcel_identity_evaluated),
            uqcel_transition_matches_i077=bool(
                native.uqcel_transition_matches_i077
            ),
            exact_scale1001_verified=bool(
                native.exact_scale1001_verified
            ),
            zero_energy_fixed_point_verified=bool(
                native.zero_energy_fixed_point_verified
            ),
            delta_e_zero=bool(native.delta_e_zero),
            psi_zero=bool(native.psi_zero),
            omega_true=bool(native.omega_true),
            deterministic_replay_verified=bool(
                native.deterministic_replay_verified
            ),
            fail_closed_boundary=bool(native.fail_closed_boundary),
            host_matrixpower_used=bool(native.host_matrixpower_used),
            square_matrix_fallback_used=bool(
                native.square_matrix_fallback_used
            ),
            floating_point_used=bool(native.floating_point_used),
            numeric_exponent_evaluated=bool(
                native.numeric_exponent_evaluated
            ),
            canonical_state_persisted=bool(
                native.canonical_state_persisted
            ),
        )

    def expand_reference(self, node_id: int) -> CandidateBoundary:
        return self.expand(node_id, self.reference_candidate(node_id))


__all__ = [
    "CandidateBoundary",
    "I078BoundaryError",
    "VM81CandidateBoundaryExecutor",
    "VM81Frame",
]
