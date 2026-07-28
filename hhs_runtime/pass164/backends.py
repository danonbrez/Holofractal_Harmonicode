from __future__ import annotations

from hashlib import sha256
from typing import Sequence

from .common import canonical_bytes
from .models import BackendDeclaration, BackendResult, ClusterOperation


class CPUReferenceBackend:
    declaration = BackendDeclaration(
        "cpu-reference",
        "CPU_REFERENCE",
        1,
        1,
        1 << 30,
        True,
        ("GCMSL_OPERATION_SUBMIT", "GCMSL_CLUSTER_REDUCE"),
    )

    def execute(self, operations: Sequence[ClusterOperation]) -> tuple[BackendResult, ...]:
        return tuple(self._result(operation, slot) for slot, operation in enumerate(operations))

    def _result(self, operation: ClusterOperation, slot: int) -> BackendResult:
        normalized = {
            "operation_id": operation.operation_id,
            "coordinate": operation.coordinate,
            "trit": operation.trit,
            "backend_semantics": "EXACT_INTEGER_REFERENCE",
        }
        return BackendResult(
            self.declaration.backend_id,
            operation.operation_id,
            operation.coordinate,
            operation.trit,
            sha256(canonical_bytes(normalized)).hexdigest(),
            slot,
        )


class SimulatedGPUBackend(CPUReferenceBackend):
    declaration = BackendDeclaration(
        "simulated-gpu",
        "DETERMINISTIC_SIMULATED_GPU",
        32,
        256,
        1 << 30,
        True,
        ("GCMSL_OPERATION_SUBMIT", "GCMSL_CLUSTER_REDUCE"),
    )

    def execute(self, operations: Sequence[ClusterOperation]) -> tuple[BackendResult, ...]:
        return tuple(self._result(operation, slot) for slot, operation in enumerate(reversed(tuple(operations))))
