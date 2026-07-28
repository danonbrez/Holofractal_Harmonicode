from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any, Sequence

from .common import (
    MAX_BATCH,
    OP_DOMAIN,
    P,
    REDUCE_DOMAIN,
    THREADS,
    VM81,
    ZERO216,
    GCMSError,
    canonical_bytes,
    hash216,
)
from .geometry import InvariantAlgebra, coordinate_bijection_proof, validate_geometry, vm_thread_to_phase
from .models import BackendResult, ClusterOperation


@dataclass(frozen=True)
class ReductionResult:
    batch_id: str
    incoming_hash72: str
    operations: tuple[ClusterOperation, ...]
    stable_order: tuple[str, ...]
    backend_equivalence_root: str
    reduction_hash216: str
    reduction_positions_hash216: tuple[str, ...]
    invariant: InvariantAlgebra
    required_clusters: tuple[str, ...]
    participating_clusters: tuple[str, ...]


class RuntimeReduceMixin:
    def submit_operation(
        self,
        *,
        cluster_id: str,
        vm81_position: int,
        thread: int,
        phase: int,
        trit: int,
        operation_class: str = "GCMSL_OPERATION_SUBMIT",
        incoming_hash72: str | None = None,
        read_set_root: str = ZERO216,
        write_set_root: str = ZERO216,
        dependency_root: str = ZERO216,
        parameter_root: str | None = None,
        expected_output_root: str | None = None,
        resource_bound: int = 1,
        reciprocal_pair_id: str | None = None,
        noncommutative_order: int | None = None,
    ) -> dict[str, Any]:
        try:
            cluster = self._clusters[cluster_id]
        except KeyError as exc:
            raise GCMSError("GCMSL_CLUSTER_NOT_REGISTERED") from exc
        if cluster.capability_zero:
            raise GCMSError("GCMSL_CAPABILITY_ZERO")
        vm_thread_to_phase(vm81_position, thread)
        if not 0 <= phase < P or trit not in (-1, 0, 1):
            raise GCMSError("GCMSL_PHASE_OR_TRIT_INVALID")
        if not 1 <= resource_bound <= MAX_BATCH:
            raise GCMSError("GCMSL_RESOURCE_BOUND")
        incoming = self.vmrc.state_hash72 if incoming_hash72 is None else incoming_hash72
        if incoming != self.vmrc.state_hash72:
            raise GCMSError("GCMSL_STALE_INCOMING_HASH72")
        body = {
            "epoch": self.vmrc.epoch,
            "level": cluster.level,
            "cluster_id": cluster_id,
            "vm81_position": vm81_position,
            "thread": thread,
            "phase": phase,
            "trit": trit,
            "operation_class": operation_class,
            "incoming_hash72": incoming,
            "read_set_root": read_set_root,
            "write_set_root": write_set_root,
            "dependency_root": dependency_root,
            "parameter_root": parameter_root or self.vmrc.status()["parameter_root"],
            "capability_scope": cluster.capability_scope,
            "architecture_backend": cluster.backend.architecture,
            "expected_output_root": expected_output_root,
            "resource_bound": resource_bound,
            "reciprocal_pair_id": reciprocal_pair_id,
            "noncommutative_order": noncommutative_order,
        }
        positions, operation_id = hash216(
            OP_DOMAIN,
            body,
            previous_root=self._last_reduction_root,
            sequence=self.vmrc.epoch,
        )
        if operation_id in self._operations:
            raise GCMSError("GCMSL_DUPLICATE_CANDIDATE_IDENTITY")
        operation = ClusterOperation(operation_id=operation_id, **body)
        self._operations[operation_id] = operation
        journal = self._record("OPERATION_SUBMIT", {"operation": asdict(operation)})
        return {
            "operation": asdict(operation),
            "positions_hash216": list(positions),
            "receipt": self._receipt(
                "P164_OPERATION_SUBMIT_RECEIPT",
                {
                    "operation_id": operation_id,
                    "mutation_authority": False,
                    "journal_hash": journal["journal_hash"],
                },
            ),
        }

    @staticmethod
    def _normalize(results: Sequence[BackendResult]) -> tuple[tuple[Any, ...], ...]:
        return tuple(
            sorted(
                (
                    item.operation_id,
                    item.coordinate,
                    item.trit,
                    item.normalized_result_sha256,
                )
                for item in results
            )
        )

    def compare_backends(self, operations: Sequence[ClusterOperation]) -> dict[str, Any]:
        cpu = self._cpu.execute(operations)
        gpu = self._gpu.execute(operations)
        normalized = self._normalize(cpu)
        if normalized != self._normalize(gpu):
            raise GCMSError("GCMSL_ARCHITECTURE_RESULT_DIVERGENCE")
        return {
            "equivalent": True,
            "cpu_physical_order": [item.operation_id for item in cpu],
            "gpu_physical_order": [item.operation_id for item in gpu],
            "normalized_order": [item[0] for item in normalized],
            "equivalence_root": sha256(
                b"HHS-P164-BACKEND-EQUIVALENCE-V1\0" + canonical_bytes(normalized)
            ).hexdigest(),
        }

    def _invariant(
        self,
        operations: Sequence[ClusterOperation],
        required: Sequence[str],
        participants: Sequence[str],
        backend_equivalent: bool,
    ) -> InvariantAlgebra:
        return InvariantAlgebra(
            authority=0,
            geometry=0 if validate_geometry() and coordinate_bijection_proof()["collisions"] == 0 else 1,
            thread=0 if all(0 <= item.thread < THREADS and 0 <= item.vm81_position < VM81 for item in operations) else 1,
            phase=0 if all(0 <= item.phase < P for item in operations) else 1,
            memristor=0,
            capability_conflict=0 if all(item.capability_scope for item in operations) else 1,
            hash_identity=0 if len({item.incoming_hash72 for item in operations}) == 1 else 1,
            replay_reduction=(0 if backend_equivalent else 1)
            + (0 if set(required).issubset(participants) else 1),
            egress=0,
        )

    def reduce(
        self,
        operation_ids: Sequence[str],
        *,
        required_clusters: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        if not operation_ids or len(operation_ids) > MAX_BATCH:
            raise GCMSError("GCMSL_BATCH_BOUND")
        if len(set(operation_ids)) != len(operation_ids):
            raise GCMSError("GCMSL_DUPLICATE_CANDIDATE_IDENTITY")
        try:
            operations = tuple(self._operations[item] for item in operation_ids)
        except KeyError as exc:
            raise GCMSError("GCMSL_OPERATION_NOT_FOUND") from exc
        incoming = operations[0].incoming_hash72
        if incoming != self.vmrc.state_hash72 or any(
            item.incoming_hash72 != incoming or item.epoch != self.vmrc.epoch
            for item in operations
        ):
            raise GCMSError("GCMSL_STALE_INCOMING_HASH72")

        pair_counts: dict[str, int] = {}
        writes: dict[tuple[int, int], int] = {}
        for item in operations:
            if item.reciprocal_pair_id:
                pair_counts[item.reciprocal_pair_id] = pair_counts.get(item.reciprocal_pair_id, 0) + 1
            if item.coordinate in writes and writes[item.coordinate] != item.trit:
                raise GCMSError("GCMSL_WRITE_COLLISION")
            writes[item.coordinate] = item.trit
            if item.operation_class == "GCMSL_NONCOMMUTATIVE" and item.noncommutative_order is None:
                raise GCMSError("GCMSL_NONCOMMUTATIVE_ORDER_REQUIRED")
        if any(count != 2 for count in pair_counts.values()):
            raise GCMSError("GCMSL_INCOMPLETE_RECIPROCAL_PAIR")

        stable = tuple(sorted(operations, key=lambda item: item.reduction_key))
        backend = self.compare_backends(stable)
        participants = tuple(sorted({item.cluster_id for item in stable}))
        required = tuple(
            sorted(
                required_clusters
                if required_clusters is not None
                else (
                    item.cluster_id
                    for item in self._clusters.values()
                    if item.required_participant
                )
            )
        )
        invariant = self._invariant(stable, required, participants, backend["equivalent"])
        if not invariant.closed:
            if not set(required).issubset(participants):
                raise GCMSError("GCMSL_INCOMPLETE_REQUIRED_CLUSTER_PARTICIPATION")
            raise GCMSError("GCMSL_UNRESOLVED_INVARIANT_RESIDUAL")
        body = {
            "incoming_hash72": incoming,
            "stable_order": [item.operation_id for item in stable],
            "operations": [asdict(item) for item in stable],
            "backend_equivalence_root": backend["equivalence_root"],
            "invariant_root": invariant.root(),
            "required_clusters": required,
            "participating_clusters": participants,
        }
        positions, reduction_root = hash216(
            REDUCE_DOMAIN,
            body,
            previous_root=self._last_reduction_root,
            sequence=self.vmrc.epoch,
        )
        batch_id = sha256(
            REDUCE_DOMAIN + canonical_bytes(body) + bytes.fromhex(reduction_root)
        ).hexdigest()
        result = ReductionResult(
            batch_id,
            incoming,
            stable,
            tuple(item.operation_id for item in stable),
            backend["equivalence_root"],
            reduction_root,
            positions,
            invariant,
            required,
            participants,
        )
        self._batches[batch_id] = result
        journal = self._record(
            "CLUSTER_REDUCE",
            {
                "batch_id": batch_id,
                "reduction_hash216": reduction_root,
                "stable_order": result.stable_order,
            },
        )
        return {
            "batch": self._serialize(result),
            "backend_equivalence": backend,
            "receipt": self._receipt(
                "P164_CLUSTER_REDUCTION_RECEIPT",
                {
                    "batch_id": batch_id,
                    "reduction_hash216": reduction_root,
                    "omega164": 0,
                    "equation_lhs": 0,
                    "journal_hash": journal["journal_hash"],
                },
            ),
        }

    def _serialize(self, result: ReductionResult) -> dict[str, Any]:
        invariant = result.invariant
        return {
            "batch_id": result.batch_id,
            "incoming_hash72": result.incoming_hash72,
            "stable_order": list(result.stable_order),
            "operations": [asdict(item) for item in result.operations],
            "backend_equivalence_root": result.backend_equivalence_root,
            "reduction_hash216": result.reduction_hash216,
            "reduction_positions_hash216": list(result.reduction_positions_hash216),
            "invariant": {
                **asdict(invariant),
                "residual_norm": invariant.residual_norm,
                "omega164": invariant.omega,
                "equation_lhs": invariant.equation_lhs,
                "closed": invariant.closed,
                "root": invariant.root(),
            },
            "required_clusters": list(result.required_clusters),
            "participating_clusters": list(result.participating_clusters),
        }
