"""Pass 219 constitutional CPU/GPU candidate binding.

GPU and CPU acceleration outputs remain non-authoritative candidates.  This
adapter requires exact CPU/GPU equality and complete constitutional invariant
preservation before a candidate can be eligible for the existing singleton
VM81 admission path.  It never mutates VM81 and never mints Hash72/Hash216
commit authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import hmac
from typing import Iterable, Tuple

from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import EthicsState
from hhs_runtime.hhs_pass219_constitutional_modality_registry_v1 import (
    BASE_INVARIANTS,
    build_modality_trace,
    get_modality_contract,
)

VERSION = "HHS_PASS219_CONSTITUTIONAL_CPU_GPU_CANDIDATE_BINDING_V1"
AUTHORITY = "CANDIDATE_ONLY_NO_VM81_HASH72_HASH216_MUTATION_AUTHORITY"


@dataclass(frozen=True)
class ComputeCandidateEnvelope:
    candidate_id: str
    cpu_exact: bytes
    gpu_candidate: bytes
    upstream_trace_hash72: str
    provenance: Tuple[str, ...]
    preserved_invariants: Tuple[str, ...] = BASE_INVARIANTS
    gpu_verified_against_cpu: bool = True
    deterministic_integer_only: bool = True
    gpu_mutation_authority: bool = False
    gpu_hash72_authority: bool = False
    gpu_hash216_authority: bool = False
    ranking_confers_authority: bool = False
    performance_confers_authority: bool = False

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id is required")
        if not self.upstream_trace_hash72.strip():
            raise ValueError("upstream_trace_hash72 is required")
        if not self.provenance:
            raise ValueError("provenance is required")


@dataclass(frozen=True)
class ComputeCandidateEvaluation:
    state: EthicsState
    failed_predicates: Tuple[str, ...]
    cpu_digest: str
    gpu_digest: str
    exact_cpu_gpu_equal: bool
    vm81_admission_eligible: bool
    mutation_authority: bool = False
    hash72_commit_authority: bool = False
    hash216_commit_authority: bool = False


def _digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def evaluate_compute_candidate(envelope: ComputeCandidateEnvelope) -> ComputeCandidateEvaluation:
    """Fail closed unless CPU/GPU candidates are exact and non-authoritative."""
    failures = []
    cpu_digest = _digest(envelope.cpu_exact)
    gpu_digest = _digest(envelope.gpu_candidate)
    exact_equal = hmac.compare_digest(envelope.cpu_exact, envelope.gpu_candidate)

    if not exact_equal:
        failures.append("CPU_GPU_EXACT_EQUALITY")
    if not envelope.gpu_verified_against_cpu:
        failures.append("GPU_CPU_VERIFICATION_REQUIRED")
    if not envelope.deterministic_integer_only:
        failures.append("CANONICAL_FLOAT_OR_NONDETERMINISM_REJECTED")
    if envelope.gpu_mutation_authority:
        failures.append("GPU_MUTATION_AUTHORITY_REJECTED")
    if envelope.gpu_hash72_authority:
        failures.append("GPU_HASH72_AUTHORITY_REJECTED")
    if envelope.gpu_hash216_authority:
        failures.append("GPU_HASH216_AUTHORITY_REJECTED")
    if envelope.ranking_confers_authority:
        failures.append("RANKING_AUTHORITY_REJECTED")
    if envelope.performance_confers_authority:
        failures.append("PERFORMANCE_AUTHORITY_REJECTED")

    required = set(BASE_INVARIANTS)
    preserved = set(envelope.preserved_invariants)
    if not required.issubset(preserved):
        failures.append("COMPUTE_INVARIANT_LOSS")

    cpu_trace = build_modality_trace(
        "cpu_candidate",
        local_state=EthicsState.PASS if not failures else EthicsState.FAIL,
        preserved_invariants=envelope.preserved_invariants,
        provenance_preserved=bool(envelope.provenance),
    )
    gpu_trace = build_modality_trace(
        "gpu_candidate",
        local_state=EthicsState.PASS if not failures else EthicsState.FAIL,
        preserved_invariants=envelope.preserved_invariants,
        provenance_preserved=bool(envelope.provenance),
    )
    if not cpu_trace.preservation_complete or not gpu_trace.preservation_complete:
        failures.append("COMPUTE_MODALITY_PRESERVATION_INCOMPLETE")

    # Registry topology is an inherited hard boundary: neither candidate lane
    # may become canonical admission authority.
    if get_modality_contract("cpu_candidate").mutation_authority:
        failures.append("CPU_REGISTRY_AUTHORITY_VIOLATION")
    if get_modality_contract("gpu_candidate").mutation_authority:
        failures.append("GPU_REGISTRY_AUTHORITY_VIOLATION")

    failures = tuple(dict.fromkeys(failures))
    state = EthicsState.FAIL if failures else EthicsState.PASS
    return ComputeCandidateEvaluation(
        state=state,
        failed_predicates=failures,
        cpu_digest=cpu_digest,
        gpu_digest=gpu_digest,
        exact_cpu_gpu_equal=exact_equal,
        vm81_admission_eligible=(state is EthicsState.PASS),
    )


def bind_driver_status(
    *,
    candidate_id: str,
    cpu_exact: bytes,
    gpu_candidate: bytes,
    upstream_trace_hash72: str,
    provenance: Iterable[str],
    verified_against_cpu: bool,
    deterministic_integer_only: bool,
) -> ComputeCandidateEvaluation:
    """Adapter for inherited Pass 207 status fields without importing native ABI."""
    return evaluate_compute_candidate(
        ComputeCandidateEnvelope(
            candidate_id=candidate_id,
            cpu_exact=bytes(cpu_exact),
            gpu_candidate=bytes(gpu_candidate),
            upstream_trace_hash72=upstream_trace_hash72,
            provenance=tuple(str(x) for x in provenance),
            gpu_verified_against_cpu=bool(verified_against_cpu),
            deterministic_integer_only=bool(deterministic_integer_only),
        )
    )


__all__ = [
    "VERSION",
    "AUTHORITY",
    "ComputeCandidateEnvelope",
    "ComputeCandidateEvaluation",
    "evaluate_compute_candidate",
    "bind_driver_status",
]
