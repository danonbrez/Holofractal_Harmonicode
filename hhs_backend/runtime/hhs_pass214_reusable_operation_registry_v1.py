"""Read-only reusable-operation discovery registry for Pass 214 reconciliation.

The registry exposes proven equivalence clusters as reusable capabilities.  It
never imports, invokes, mutates, or replaces the underlying runtime authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

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


class ReusableOperationRegistry:
    """Read-only view over proven semantic-equivalence clusters."""

    def __init__(self, reconciliation: Mapping[str, Any]) -> None:
        if reconciliation.get("schema") != RECONCILIATION_SCHEMA:
            raise ReusableOperationRegistryError("RECONCILIATION_SCHEMA_MISMATCH")
        policy = reconciliation.get("policy", {})
        if not policy.get("name_similarity_is_never_equivalence_proof"):
            raise ReusableOperationRegistryError("UNSAFE_EQUIVALENCE_POLICY")
        rows = reconciliation.get("reusable_operation_registry_entries")
        if not isinstance(rows, list):
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
        self._by_cluster = {x.cluster_id: x for x in self._bindings}
        by_name: dict[str, list[ReusableOperationBinding]] = {}
        for binding in self._bindings:
            by_name.setdefault(binding.normalized_semantic_name, []).append(binding)
        self._by_name = {k: tuple(v) for k, v in by_name.items()}

    @property
    def schema(self) -> str:
        return REGISTRY_SCHEMA

    @property
    def classification(self) -> str:
        return CLASSIFICATION

    def list_bindings(self) -> tuple[ReusableOperationBinding, ...]:
        return self._bindings

    def get(self, cluster_id: str) -> ReusableOperationBinding:
        try:
            return self._by_cluster[cluster_id]
        except KeyError as exc:
            raise ReusableOperationRegistryError(f"UNKNOWN_REUSE_CLUSTER:{cluster_id}") from exc

    def find(self, semantic_name: str) -> tuple[ReusableOperationBinding, ...]:
        from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import _normalize
        return self._by_name.get(_normalize(semantic_name), ())

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

    def execute(self, *args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise ReusableOperationRegistryError("DISCOVERY_REGISTRY_IS_NOT_EXECUTION_AUTHORITY")


def build_registry(reconciliation: Mapping[str, Any]) -> ReusableOperationRegistry:
    return ReusableOperationRegistry(reconciliation)
