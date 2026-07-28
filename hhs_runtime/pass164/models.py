from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .common import GCMSError


@dataclass(frozen=True)
class BackendDeclaration:
    backend_id: str
    architecture: str
    subgroup_width: int
    max_workgroup_size: int
    memory_limit_bytes: int
    deterministic: bool
    supported_operations: tuple[str, ...]
    canonical_representation: str = "PASS163_BASE64_ABI"

    def __post_init__(self) -> None:
        if not self.backend_id or not self.architecture:
            raise GCMSError("GCMSL_BACKEND_ID_REQUIRED")
        if min(self.subgroup_width, self.max_workgroup_size, self.memory_limit_bytes) < 1:
            raise GCMSError("GCMSL_BACKEND_BOUND")


@dataclass(frozen=True)
class ClusterRecord:
    cluster_id: str
    level: int
    tile_index: int
    backend: BackendDeclaration
    capability_scope: str = ""
    required_participant: bool = True

    @property
    def capability_zero(self) -> bool:
        return not bool(self.capability_scope)


@dataclass(frozen=True)
class ClusterOperation:
    operation_id: str
    epoch: int
    level: int
    cluster_id: str
    vm81_position: int
    thread: int
    phase: int
    trit: int
    operation_class: str
    incoming_hash72: str
    read_set_root: str
    write_set_root: str
    dependency_root: str
    parameter_root: str
    capability_scope: str
    architecture_backend: str
    expected_output_root: str | None
    resource_bound: int
    reciprocal_pair_id: str | None = None
    noncommutative_order: int | None = None

    @property
    def coordinate(self) -> tuple[int, int]:
        return self.vm81_position, self.thread

    @property
    def reduction_key(self) -> tuple[Any, ...]:
        order = -1 if self.noncommutative_order is None else self.noncommutative_order
        return (
            self.epoch,
            self.level,
            self.phase,
            self.cluster_id,
            order,
            self.vm81_position,
            self.thread,
            self.operation_id,
        )


@dataclass(frozen=True)
class BackendResult:
    backend_id: str
    operation_id: str
    coordinate: tuple[int, int]
    trit: int
    normalized_result_sha256: str
    physical_completion_slot: int


@dataclass(frozen=True)
class ClusterEdge:
    edge_id: str
    level: int
    source_cluster: str
    destination_cluster: str
    domain: str
    source: str
    destination: str
    epoch: int
    exact_weight: str
    polarity: int
    u72_offset: int
    xyzw_weights: tuple[str, str, str, str]
    hash216_vector: str
    admitted_history: tuple[str, ...] = ()
