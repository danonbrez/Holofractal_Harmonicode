"""Read-only reusable-operation discovery registry for Pass 214 reconciliation.

Every coded operation is addressable. Proven-equivalent operations share a
registry identity; unresolved operations remain distinct. The registry never
imports, invokes, mutates, or replaces the underlying runtime authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass214_semantic_equivalence_v1 import SCHEMA as RECONCILIATION_SCHEMA

REGISTRY_SCHEMA = "HHS_PASS_214_REUSABLE_OPERATION_REGISTRY_V1"
CLASSIFICATION = "HHS_PASS_214_READ_ONLY_REUSABLE_OPERATION_DISCOVERY_SURFACE"


class ReusableOperationRegistryError(RuntimeError):
    pass


@dataclass(frozen=True)
class ReusableOperationBinding:
    cluster_id: str
    normalized_semantic_name: str
    migration_action: str
    member_operation_keys: tuple[str, ...]
    member_paths: tuple[str, ...]
    preferred_binding: Mapping[str, Any] | None


@dataclass(frozen=True)
class OperationRegistryRecord:
    registry_id: str
    registry_status: str
    operation_key: str
    normalized_semantic_name: str
    raw_name: str
    kind: str
    family: str
    authority: str
    reuse_status: str
    python_exposure: str
    path: str
    line: int
    pass_number: int | None
    migration_requirement: str


class ReusableOperationRegistry:
    """Read-only view over every coded operation and each proven reuse cluster."""

    def __init__(self, reconciliation: Mapping[str, Any]) -> None:
        if reconciliation.get("schema") != RECONCILIATION_SCHEMA:
            raise ReusableOperationRegistryError("RECONCILIATION_SCHEMA_MISMATCH")
        policy = reconciliation.get("policy", {})
        if not policy.get("name_similarity_is_never_equivalence_proof"):
            raise ReusableOperationRegistryError("UNSAFE_EQUIVALENCE_POLICY")
        if not policy.get("every_coded_operation_has_registry_identity"):
            raise ReusableOperationRegistryError("INCOMPLETE_OPERATION_REGISTRY_POLICY")

        rows = reconciliation.get("reusable_operation_registry_entries")
        operations = reconciliation.get("operation_registry_entries")
        if not isinstance(rows, list) or not isinstance(operations, list):
            raise ReusableOperationRegistryError("REGISTRY_ENTRIES_MISSING")

        self._bindings: tuple[ReusableOperationBinding, ...] = tuple(
            ReusableOperationBinding(
                cluster_id=str(row["cluster_id"]),
                normalized_semantic_name=str(row["normalized_semantic_name"]),
                migration_action=str(row["migration_action"]),
                member_operation_keys=tuple(str(x) for x in row["member_operation_keys"]),
                member_paths=tuple(str(x) for x in row["member_paths"]),
                preferred_binding=row.get("preferred_binding"),
            )
            for row in rows
        )
        self._operations: tuple[OperationRegistryRecord, ...] = tuple(
            OperationRegistryRecord(
                registry_id=str(row["registry_id"]),
                registry_status=str(row["registry_status"]),
                operation_key=str(row["operation_key"]),
                normalized_semantic_name=str(row["normalized_semantic_name"]),
                raw_name=str(row["raw_name"]),
                kind=str(row["kind"]),
                family=str(row["family"]),
                authority=str(row["authority"]),
                reuse_status=str(row["reuse_status"]),
                python_exposure=str(row["python_exposure"]),
                path=str(row["path"]),
                line=int(row["line"]),
                pass_number=None if row.get("pass_number") is None else int(row["pass_number"]),
                migration_requirement=str(row["migration_requirement"]),
            )
            for row in operations
        )
        self._by_cluster = {x.cluster_id: x for x in self._bindings}
        self._by_operation_key = {x.operation_key: x for x in self._operations}
        by_name: dict[str, list[ReusableOperationBinding]] = {}
        op_by_name: dict[str, list[OperationRegistryRecord]] = {}
        by_registry_id: dict[str, list[OperationRegistryRecord]] = {}
        for binding in self._bindings:
            by_name.setdefault(binding.normalized_semantic_name, []).append(binding)
        for operation in self._operations:
            op_by_name.setdefault(operation.normalized_semantic_name, []).append(operation)
            by_registry_id.setdefault(operation.registry_id, []).append(operation)
        self._by_name = {k: tuple(v) for k, v in by_name.items()}
        self._operations_by_name = {k: tuple(v) for k, v in op_by_name.items()}
        self._by_registry_id = {k: tuple(v) for k, v in by_registry_id.items()}

        if len(self._by_operation_key) != len(self._operations):
            raise ReusableOperationRegistryError("DUPLICATE_OPERATION_KEY")

    @property
    def schema(self) -> str:
        return REGISTRY_SCHEMA

    @property
    def classification(self) -> str:
        return CLASSIFICATION

    def list_bindings(self) -> tuple[ReusableOperationBinding, ...]:
        return self._bindings

    def list_operations(self) -> tuple[OperationRegistryRecord, ...]:
        return self._operations

    def get(self, cluster_id: str) -> ReusableOperationBinding:
        try:
            return self._by_cluster[cluster_id]
        except KeyError as exc:
            raise ReusableOperationRegistryError(f"UNKNOWN_REUSE_CLUSTER:{cluster_id}") from exc

    def get_operation(self, operation_key: str) -> OperationRegistryRecord:
        try:
            return self._by_operation_key[operation_key]
        except KeyError as exc:
            raise ReusableOperationRegistryError(f"UNKNOWN_OPERATION_KEY:{operation_key}") from exc

    def registry_members(self, registry_id: str) -> tuple[OperationRegistryRecord, ...]:
        return self._by_registry_id.get(registry_id, ())

    def find(self, semantic_name: str) -> tuple[ReusableOperationBinding, ...]:
        from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import _normalize
        return self._by_name.get(_normalize(semantic_name), ())

    def find_operations(self, semantic_name: str) -> tuple[OperationRegistryRecord, ...]:
        from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import _normalize
        return self._operations_by_name.get(_normalize(semantic_name), ())

    def preferred_bindings(self, semantic_name: str) -> tuple[Mapping[str, Any], ...]:
        return tuple(
            x.preferred_binding
            for x in self.find(semantic_name)
            if x.preferred_binding is not None
        )

    def migration_candidates(self, action: str | None = None) -> tuple[ReusableOperationBinding, ...]:
        if action is None:
            return self._bindings
        return tuple(x for x in self._bindings if x.migration_action == action)

    def isolation_backlog(self) -> tuple[OperationRegistryRecord, ...]:
        return tuple(
            x for x in self._operations
            if x.migration_requirement == "REQUIRES_REUSABLE_EXTRACTION_OR_ADAPTER"
        )

    def execute(self, *args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise ReusableOperationRegistryError("DISCOVERY_REGISTRY_IS_NOT_EXECUTION_AUTHORITY")


def build_registry(reconciliation: Mapping[str, Any]) -> ReusableOperationRegistry:
    return ReusableOperationRegistry(reconciliation)
