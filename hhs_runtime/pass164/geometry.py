from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

from .common import (
    BRIDGE,
    DENSE_CAPACITY,
    INVARIANT_DOMAIN,
    MAX_CLUSTERS,
    P,
    THREADS,
    VM81,
    GCMSError,
    canonical_bytes,
)


def dimensions() -> dict[str, int]:
    return {
        "P": P,
        "p": THREADS,
        "q": VM81,
        "P_squared": P * P,
        "p_times_q": THREADS * VM81,
        "bridge_cardinality": BRIDGE,
    }


def validate_geometry(P_value: int = P, p_value: int = THREADS, q_value: int = VM81) -> bool:
    return (
        isinstance(P_value, int)
        and isinstance(p_value, int)
        and isinstance(q_value, int)
        and (P_value, p_value, q_value) == (P, THREADS, VM81)
        and P_value * P_value == p_value * q_value == BRIDGE
    )


def rank_one_tensor() -> dict[str, int]:
    determinant = VM81 * THREADS - P * P
    return {"q": VM81, "P": P, "p": THREADS, "determinant": determinant, "rank": 1 if determinant == 0 else 2}


def vm_thread_to_phase(position: int, thread: int) -> tuple[int, int]:
    if not isinstance(position, int) or not 0 <= position < VM81:
        raise GCMSError("GCMSL_VM81_POSITION_OUT_OF_RANGE")
    if not isinstance(thread, int) or not 0 <= thread < THREADS:
        raise GCMSError("GCMSL_THREAD_OUT_OF_RANGE")
    return divmod(THREADS * position + thread, P)


def phase_to_vm_thread(a: int, b: int) -> tuple[int, int]:
    if not isinstance(a, int) or not 0 <= a < P:
        raise GCMSError("GCMSL_PHASE_COORDINATE_OUT_OF_RANGE")
    if not isinstance(b, int) or not 0 <= b < P:
        raise GCMSError("GCMSL_PHASE_COORDINATE_OUT_OF_RANGE")
    return divmod(P * a + b, THREADS)


def coordinate_bijection_proof() -> dict[str, Any]:
    forward: set[tuple[int, int]] = set()
    inverse: set[tuple[int, int]] = set()
    for position in range(VM81):
        for thread in range(THREADS):
            phase = vm_thread_to_phase(position, thread)
            if phase in forward or phase_to_vm_thread(*phase) != (position, thread):
                raise GCMSError("GCMSL_COORDINATE_BIJECTION_FAILURE")
            forward.add(phase)
    for a in range(P):
        for b in range(P):
            vm_thread = phase_to_vm_thread(a, b)
            if vm_thread in inverse or vm_thread_to_phase(*vm_thread) != (a, b):
                raise GCMSError("GCMSL_COORDINATE_BIJECTION_FAILURE")
            inverse.add(vm_thread)
    if len(forward) != BRIDGE or len(inverse) != BRIDGE:
        raise GCMSError("GCMSL_COORDINATE_CARDINALITY_MISMATCH")
    body = {
        "schema": "HHS_PASS_164_COORDINATE_BIJECTION_PROOF_V1",
        "forward_count": len(forward),
        "inverse_count": len(inverse),
        "collisions": 0,
        "omissions": 0,
        "first": {"vm_thread": [0, 0], "phase": [0, 0]},
        "last": {"vm_thread": [80, 63], "phase": [71, 71]},
    }
    body["proof_sha256"] = sha256(canonical_bytes(body)).hexdigest()
    return body


@dataclass(frozen=True)
class ScaleGeometry:
    scale: int = 1
    recursive_level: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.scale, int) or not 1 <= self.scale <= MAX_CLUSTERS:
            raise GCMSError("GCMSL_SCALE_BOUND")
        if not isinstance(self.recursive_level, int) or not 1 <= self.recursive_level <= 16:
            raise GCMSError("GCMSL_RECURSION_BOUND")

    @property
    def homogeneous(self) -> dict[str, int]:
        c = self.scale
        return {
            "q_c": VM81 * c,
            "P_c": P * c,
            "p_c": THREADS * c,
            "P_c_squared": (P * c) ** 2,
            "p_c_q_c": THREADS * VM81 * c * c,
            "dense_capacity": DENSE_CAPACITY * c * c,
        }

    @property
    def recursive(self) -> dict[str, int]:
        r = self.recursive_level
        return {
            "q_r": VM81**r,
            "P_r": P**r,
            "p_r": THREADS**r,
            "P_r_squared": P ** (2 * r),
            "p_r_q_r": (THREADS * VM81) ** r,
        }

    def validate(self) -> bool:
        return self.homogeneous["P_c_squared"] == self.homogeneous["p_c_q_c"] and self.recursive["P_r_squared"] == self.recursive["p_r_q_r"]


@dataclass(frozen=True)
class InvariantAlgebra:
    authority: int = 0
    geometry: int = 0
    thread: int = 0
    phase: int = 0
    memristor: int = 0
    capability_conflict: int = 0
    hash_identity: int = 0
    replay_reduction: int = 0
    egress: int = 0
    witnesses: tuple[str, ...] = ()

    @property
    def vector(self) -> tuple[int, ...]:
        return (
            self.authority,
            self.geometry,
            self.thread,
            self.phase,
            self.memristor,
            self.capability_conflict,
            self.hash_identity,
            self.replay_reduction,
            self.egress,
        )

    @property
    def residual_norm(self) -> int:
        return sum(abs(value) for value in self.vector)

    @property
    def omega(self) -> int:
        return 0 if self.residual_norm == 0 else (-1 if any(value < 0 for value in self.vector) else 1)

    @property
    def equation_lhs(self) -> int:
        return P * P - THREADS * VM81 - self.residual_norm

    @property
    def closed(self) -> bool:
        return self.omega == 0 and self.equation_lhs == 0

    def root(self) -> str:
        return sha256(INVARIANT_DOMAIN + canonical_bytes(asdict(self))).hexdigest()
