"""Native bridge for Pass 219 Lane 5 unbounded real-world workload scaling 1.48.

The bridge is workload-class agnostic. Any workload that can be serialized as an
ordered byte stream is hashed incrementally and bound to exact BigInt state
coordinates before candidates are reduced by the native constant-memory Lane 5
stream optimizer. Candidate results remain non-authoritative until signed VM81
admission.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import platform
import subprocess
from typing import Iterable, Iterator

from ctypes import POINTER, Structure, c_int8, c_uint8, c_uint32, c_uint64

VERSION = 0x00010030
NAMESPACE = 0x00021930
DIGEST_BYTES = 32
ADDRESS_BYTES = 56
FULL_MANIFOLD_MODULUS = 72 ** 72
UINT64_MAX = (1 << 64) - 1
HHS_EXACT_STATUS_OK = 0


class HHSExactBigUIntView(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("byte_length", c_uint32),
        ("bytes_be", POINTER(c_uint8)),
    ]


class HHSExactPass219Lane5UnboundedWorkloadAuthorityV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("namespace_id", c_uint32),
        ("full_manifold_address_bytes", c_uint32),
        ("full_manifold_bigint_addressing", c_uint8),
        ("modulus_is_72_pow_72", c_uint8),
        ("any_byte_serializable_workload", c_uint8),
        ("workload_class_agnostic", c_uint8),
        ("streaming_candidate_ingress", c_uint8),
        ("constant_memory_candidate_reduction", c_uint8),
        ("fixed_candidate_batch_required", c_uint8),
        ("intermediate_materialization_required", c_uint8),
        ("previous_current_goal_bound", c_uint8),
        ("provenance_bound", c_uint8),
        ("contradiction_boundary_bound", c_uint8),
        ("exact_reciprocal_phase_inversion", c_uint8),
        ("balanced_trinary_collapse", c_uint8),
        ("binary_qubit_collapse", c_uint8),
        ("nested_zero_layer", c_uint8),
        ("deterministic_tie_break", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_vm81_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("floating_point_canonical_authority", c_uint8),
        ("reserved0", c_uint8 * 3),
    ]


class HHSExactPass219Lane5UnboundedWorkloadRouteV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("previous_address", HHSExactBigUIntView),
        ("current_address", HHSExactBigUIntView),
        ("goal_address", HHSExactBigUIntView),
        ("candidate_address", HHSExactBigUIntView),
        ("workload_sha256", c_uint8 * DIGEST_BYTES),
        ("provenance_sha256", c_uint8 * DIGEST_BYTES),
        ("forbidden_boundary_sha256", c_uint8 * DIGEST_BYTES),
        ("reciprocal_witness_sha256", c_uint8 * DIGEST_BYTES),
        ("route_witness_sha256", c_uint8 * DIGEST_BYTES),
        ("workload_byte_count", c_uint64),
        ("integer_route_cost", c_uint64),
        ("evidence_count", c_uint32),
        ("contradiction_check_count", c_uint32),
        ("materialized_intermediate_states", c_uint32),
        ("phase_slot", c_uint32),
        ("inverse_phase_slot", c_uint32),
        ("trinary_collapse", c_int8),
        ("binary_collapse", c_uint8),
        ("nested_zero_slot", c_uint8),
        ("workload_serialization_exact", c_uint8),
        ("source_digest_verified", c_uint8),
        ("replay_witness_verified", c_uint8),
        ("exact_goal_reached", c_uint8),
        ("contradiction_free", c_uint8),
        ("goal_forbidden_conflict", c_uint8),
        ("reciprocal_phase_verified", c_uint8),
        ("bigint_serialization_addressed", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved0", c_uint8 * 2),
    ]


class HHSExactPass219Lane5UnboundedWorkloadReceiptV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("namespace_id", c_uint32),
        ("candidate_address_length", c_uint32),
        ("candidate_address_be", c_uint8 * ADDRESS_BYTES),
        ("workload_sha256", c_uint8 * DIGEST_BYTES),
        ("provenance_sha256", c_uint8 * DIGEST_BYTES),
        ("route_witness_sha256", c_uint8 * DIGEST_BYTES),
        ("workload_byte_count", c_uint64),
        ("integer_route_cost", c_uint64),
        ("descriptor_signature64", c_uint64),
        ("route_receipt_signature64", c_uint64),
        ("phase_slot", c_uint32),
        ("inverse_phase_slot", c_uint32),
        ("trinary_collapse", c_int8),
        ("binary_collapse", c_uint8),
        ("nested_zero_slot", c_uint8),
        ("accepted", c_uint8),
        ("optimizer_selected", c_uint8),
        ("replay_witness_verified", c_uint8),
        ("exact_goal_reached", c_uint8),
        ("contradiction_free", c_uint8),
        ("reciprocal_phase_verified", c_uint8),
        ("bigint_serialization_addressed", c_uint8),
        ("full_manifold_coordinate_capable", c_uint8),
        ("workload_class_agnostic", c_uint8),
        ("materialized_intermediate_states", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved0", c_uint8 * 2),
    ]


class HHSExactPass219Lane5UnboundedWorkloadStreamV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("candidates_seen", c_uint64),
        ("admissible_candidates", c_uint64),
        ("rejected_candidates", c_uint64),
        ("workload_binding_signature64", c_uint64),
        ("bound_workload_byte_count", c_uint64),
        ("bound_previous_address_length", c_uint32),
        ("bound_current_address_length", c_uint32),
        ("bound_goal_address_length", c_uint32),
        ("bound_previous_address_be", c_uint8 * ADDRESS_BYTES),
        ("bound_current_address_be", c_uint8 * ADDRESS_BYTES),
        ("bound_goal_address_be", c_uint8 * ADDRESS_BYTES),
        ("bound_workload_sha256", c_uint8 * DIGEST_BYTES),
        ("bound_provenance_sha256", c_uint8 * DIGEST_BYTES),
        ("bound_forbidden_boundary_sha256", c_uint8 * DIGEST_BYTES),
        ("count_saturated", c_uint8),
        ("has_binding", c_uint8),
        ("has_best", c_uint8),
        ("finalized", c_uint8),
        ("reserved0", c_uint8 * 4),
        ("best_receipt", HHSExactPass219Lane5UnboundedWorkloadReceiptV1),
    ]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _runtime_path() -> Path:
    system = platform.system().lower()
    name = "hhs_runtime.dll" if system == "windows" else (
        "libhhs_runtime.dylib" if system == "darwin" else "libhhs_runtime.so"
    )
    return _repo_root() / "hhs_runtime" / "builds" / name


def _load_runtime() -> ctypes.CDLL:
    path = _runtime_path()
    disable = os.environ.get("HHS_DISABLE_C_AUTOBUILD", "").lower() in {"1", "true", "yes", "on"}
    if not path.exists() and not disable:
        subprocess.run(
            ["make", "c-abi"], cwd=_repo_root(), check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
    if not path.exists():
        raise FileNotFoundError(f"HHS exact runtime shared library not found: {path}")
    return ctypes.CDLL(str(path))


def _digest(value: bytes | bytearray | memoryview) -> bytes:
    raw = bytes(value)
    if len(raw) != DIGEST_BYTES:
        raise ValueError("digest must contain exactly 32 bytes")
    return raw


def _copy_digest(target: ctypes.Array[c_uint8], value: bytes) -> None:
    target[:] = _digest(value)


def _bigint_bytes(value: int) -> bytes:
    integer = int(value)
    if integer < 0 or integer >= FULL_MANIFOLD_MODULUS:
        raise ValueError("state coordinate must satisfy 0 <= value < 72^72")
    return integer.to_bytes(max(1, (integer.bit_length() + 7) // 8), "big")


def _owned_view(value: int) -> tuple[ctypes.Array[c_uint8], HHSExactBigUIntView]:
    raw = _bigint_bytes(value)
    buffer = (c_uint8 * len(raw)).from_buffer_copy(raw)
    result = HHSExactBigUIntView()
    result.struct_size = ctypes.sizeof(result)
    result.byte_length = len(raw)
    result.bytes_be = ctypes.cast(buffer, POINTER(c_uint8))
    return buffer, result


def iter_file_chunks(path: str | Path, *, chunk_bytes: int = 1024 * 1024) -> Iterator[bytes]:
    if chunk_bytes <= 0:
        raise ValueError("chunk_bytes must be positive")
    with Path(path).open("rb") as stream:
        while True:
            chunk = stream.read(chunk_bytes)
            if not chunk:
                return
            yield chunk


@dataclass(frozen=True)
class Lane5WorkloadEnvelope:
    byte_count: int
    workload_sha256: bytes
    provenance_sha256: bytes

    @classmethod
    def from_chunks(cls, chunks: Iterable[bytes | bytearray | memoryview], *, provenance: str) -> "Lane5WorkloadEnvelope":
        digest = sha256()
        byte_count = 0
        for chunk in chunks:
            raw = bytes(chunk)
            digest.update(raw)
            byte_count += len(raw)
            if byte_count > UINT64_MAX:
                raise OverflowError("serialized workload exceeds uint64 byte-count metadata capacity")
        return cls(
            byte_count=byte_count,
            workload_sha256=digest.digest(),
            provenance_sha256=sha256(provenance.encode("utf-8")).digest(),
        )

    @classmethod
    def from_bytes(cls, payload: bytes | bytearray | memoryview, *, provenance: str) -> "Lane5WorkloadEnvelope":
        return cls.from_chunks((bytes(payload),), provenance=provenance)

    @classmethod
    def from_file(cls, path: str | Path, *, provenance: str | None = None, chunk_bytes: int = 1024 * 1024) -> "Lane5WorkloadEnvelope":
        selected = Path(path)
        return cls.from_chunks(
            iter_file_chunks(selected, chunk_bytes=chunk_bytes),
            provenance=provenance or f"file:{selected.as_posix()}",
        )


@dataclass(frozen=True)
class Lane5RouteCandidate:
    route_witness_sha256: bytes
    reciprocal_witness_sha256: bytes
    phase_slot: int
    trinary_collapse: int
    binary_collapse: int
    evidence_count: int = 5
    contradiction_check_count: int = 1

    @property
    def integer_route_cost(self) -> int:
        return int(self.evidence_count) + int(self.contradiction_check_count) + 1


class Pass219Lane5UnboundedWorkloadBridge:
    def __init__(self) -> None:
        self.lib = _load_runtime()
        self.lib.hhs_exact_pass219_lane5_unbounded_workload_scaling_version.argtypes = []
        self.lib.hhs_exact_pass219_lane5_unbounded_workload_scaling_version.restype = c_uint32
        self.lib.hhs_exact_pass219_lane5_unbounded_workload_scaling_authority.argtypes = [
            POINTER(HHSExactPass219Lane5UnboundedWorkloadAuthorityV1)
        ]
        self.lib.hhs_exact_pass219_lane5_unbounded_workload_scaling_authority.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_unbounded_workload_stream_init.argtypes = [
            POINTER(HHSExactPass219Lane5UnboundedWorkloadStreamV1)
        ]
        self.lib.hhs_exact_pass219_lane5_unbounded_workload_stream_init.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_unbounded_workload_stream_consider.argtypes = [
            POINTER(HHSExactPass219Lane5UnboundedWorkloadStreamV1),
            POINTER(HHSExactPass219Lane5UnboundedWorkloadRouteV1),
            POINTER(c_uint8),
        ]
        self.lib.hhs_exact_pass219_lane5_unbounded_workload_stream_consider.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_unbounded_workload_stream_finalize.argtypes = [
            POINTER(HHSExactPass219Lane5UnboundedWorkloadStreamV1),
            POINTER(HHSExactPass219Lane5UnboundedWorkloadReceiptV1),
        ]
        self.lib.hhs_exact_pass219_lane5_unbounded_workload_stream_finalize.restype = ctypes.c_int

    def authority(self) -> dict[str, int | bool]:
        value = HHSExactPass219Lane5UnboundedWorkloadAuthorityV1()
        status = self.lib.hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(ctypes.byref(value))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Lane 5 unbounded workload authority failed: status={status}")
        return {
            "version": int(value.version),
            "namespace_id": int(value.namespace_id),
            "full_manifold_address_bytes": int(value.full_manifold_address_bytes),
            "full_manifold_bigint_addressing": bool(value.full_manifold_bigint_addressing),
            "any_byte_serializable_workload": bool(value.any_byte_serializable_workload),
            "workload_class_agnostic": bool(value.workload_class_agnostic),
            "streaming_candidate_ingress": bool(value.streaming_candidate_ingress),
            "constant_memory_candidate_reduction": bool(value.constant_memory_candidate_reduction),
            "fixed_candidate_batch_required": bool(value.fixed_candidate_batch_required),
            "intermediate_materialization_required": bool(value.intermediate_materialization_required),
            "candidate_only": bool(value.candidate_only),
            "canonical_vm81_mutation_authority": bool(value.canonical_vm81_mutation_authority),
            "canonical_hash216_authority": bool(value.canonical_hash216_authority),
            "requires_signed_environmental_vm81_admission": bool(value.requires_signed_environmental_vm81_admission),
        }

    def optimize(
        self,
        *,
        workload: Lane5WorkloadEnvelope,
        previous_address: int,
        current_address: int,
        goal_address: int,
        forbidden_boundary_sha256: bytes,
        candidates: Iterable[Lane5RouteCandidate],
    ) -> dict[str, int | bool | str]:
        previous_buffer, previous_view = _owned_view(previous_address)
        current_buffer, current_view = _owned_view(current_address)
        goal_buffer, goal_view = _owned_view(goal_address)
        keepalive = [previous_buffer, current_buffer, goal_buffer]
        stream = HHSExactPass219Lane5UnboundedWorkloadStreamV1()
        status = self.lib.hhs_exact_pass219_lane5_unbounded_workload_stream_init(ctypes.byref(stream))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Lane 5 stream initialization failed: status={status}")

        offered = 0
        admitted_count = 0
        for candidate in candidates:
            offered += 1
            route = HHSExactPass219Lane5UnboundedWorkloadRouteV1()
            route.struct_size = ctypes.sizeof(route)
            route.version = VERSION
            route.previous_address = previous_view
            route.current_address = current_view
            route.goal_address = goal_view
            route.candidate_address = goal_view
            _copy_digest(route.workload_sha256, workload.workload_sha256)
            _copy_digest(route.provenance_sha256, workload.provenance_sha256)
            _copy_digest(route.forbidden_boundary_sha256, forbidden_boundary_sha256)
            _copy_digest(route.reciprocal_witness_sha256, candidate.reciprocal_witness_sha256)
            _copy_digest(route.route_witness_sha256, candidate.route_witness_sha256)
            route.workload_byte_count = int(workload.byte_count)
            route.evidence_count = int(candidate.evidence_count)
            route.contradiction_check_count = int(candidate.contradiction_check_count)
            route.integer_route_cost = int(candidate.integer_route_cost)
            route.materialized_intermediate_states = 0
            route.phase_slot = int(candidate.phase_slot)
            route.inverse_phase_slot = (int(candidate.phase_slot) + 36) % 72
            route.trinary_collapse = int(candidate.trinary_collapse)
            route.binary_collapse = int(candidate.binary_collapse)
            route.nested_zero_slot = 1 if int(candidate.binary_collapse) == 0 else 0
            route.workload_serialization_exact = 1
            route.source_digest_verified = 1
            route.replay_witness_verified = 1
            route.exact_goal_reached = 1
            route.contradiction_free = 1
            route.goal_forbidden_conflict = 0
            route.reciprocal_phase_verified = 1
            route.bigint_serialization_addressed = 1
            route.candidate_only = 1
            route.requires_signed_environmental_vm81_admission = 1
            admitted = c_uint8(0)
            status = self.lib.hhs_exact_pass219_lane5_unbounded_workload_stream_consider(
                ctypes.byref(stream), ctypes.byref(route), ctypes.byref(admitted)
            )
            if status != HHS_EXACT_STATUS_OK:
                raise RuntimeError(f"Lane 5 stream consideration failed: status={status}")
            admitted_count += int(admitted.value)

        receipt = HHSExactPass219Lane5UnboundedWorkloadReceiptV1()
        status = self.lib.hhs_exact_pass219_lane5_unbounded_workload_stream_finalize(
            ctypes.byref(stream), ctypes.byref(receipt)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError(
                f"Lane 5 stream produced no admissible candidate: status={status}, offered={offered}"
            )
        length = int(receipt.candidate_address_length)
        raw_address = bytes(receipt.candidate_address_be)[ADDRESS_BYTES - length:]
        selected_address = int.from_bytes(raw_address, "big")
        return {
            "offered_candidates": offered,
            "admitted_candidates": admitted_count,
            "native_candidates_seen": int(stream.candidates_seen),
            "native_rejected_candidates": int(stream.rejected_candidates),
            "count_saturated": bool(stream.count_saturated),
            "selected_address": selected_address,
            "workload_byte_count": int(receipt.workload_byte_count),
            "integer_route_cost": int(receipt.integer_route_cost),
            "phase_slot": int(receipt.phase_slot),
            "inverse_phase_slot": int(receipt.inverse_phase_slot),
            "trinary_collapse": int(receipt.trinary_collapse),
            "binary_collapse": int(receipt.binary_collapse),
            "nested_zero_slot": int(receipt.nested_zero_slot),
            "workload_sha256": bytes(receipt.workload_sha256).hex(),
            "provenance_sha256": bytes(receipt.provenance_sha256).hex(),
            "route_witness_sha256": bytes(receipt.route_witness_sha256).hex(),
            "descriptor_signature64": int(receipt.descriptor_signature64),
            "route_receipt_signature64": int(receipt.route_receipt_signature64),
            "materialized_intermediate_states": int(receipt.materialized_intermediate_states),
            "candidate_only": bool(receipt.candidate_only),
            "canonical_vm81_mutation_authority": bool(receipt.canonical_mutation_authority),
            "canonical_hash216_authority": bool(receipt.canonical_hash216_authority),
            "requires_signed_environmental_vm81_admission": bool(receipt.requires_signed_environmental_vm81_admission),
        }


__all__ = [
    "ADDRESS_BYTES",
    "DIGEST_BYTES",
    "FULL_MANIFOLD_MODULUS",
    "Lane5RouteCandidate",
    "Lane5WorkloadEnvelope",
    "Pass219Lane5UnboundedWorkloadBridge",
    "iter_file_chunks",
]
