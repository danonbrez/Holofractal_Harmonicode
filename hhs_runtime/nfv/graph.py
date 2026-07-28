from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .core import NFVError, canonical, hash216

EDGE_TYPES = frozenset(
    {
        "VALUE_DEPENDS_ON",
        "CONSTRAINT_DEPENDS_ON",
        "AUTHORITY_DEPENDS_ON",
        "PROVENANCE_DEPENDS_ON",
        "RECEIPT_DEPENDS_ON",
        "RESOURCE_DEPENDS_ON",
        "CLOSURE_DEPENDS_ON",
        "ALGORITHM_DEPENDS_ON",
        "SCHEMA_DEPENDS_ON",
        "VERSION_DEPENDS_ON",
        "PROJECTION_DEPENDS_ON",
        "REVERSAL_DEPENDS_ON",
        "PARENT_DEPENDS_ON",
        "CHILD_DEPENDS_ON",
        "MODULUS_DEPENDS_ON",
        "CARRY_DEPENDS_ON",
        "LOSHU_ORIENTATION_DEPENDS_ON",
        "AUDIO_LANE_DEPENDS_ON",
        "FOURIER_BASIS_DEPENDS_ON",
        "CONVOLUTION_KERNEL_DEPENDS_ON",
        "INTERACTION_FIELD_DEPENDS_ON",
    }
)


@dataclass(frozen=True)
class DependencyEdge:
    source: str
    target: str
    edge_type: str
    order: int = 0
    edge_index: str = ""

    def __post_init__(self) -> None:
        if not self.source or not self.target:
            raise NFVError("NFV_INVALID_DEPENDENCY_EDGE", "source and target are mandatory")
        if self.edge_type not in EDGE_TYPES:
            raise NFVError("NFV_UNKNOWN_DEPENDENCY_EDGE", "edge type is not registered", {"edge_type": self.edge_type})
        if self.order < 0:
            raise NFVError("NFV_INVALID_DEPENDENCY_ORDER", "edge order must be nonnegative")
        expected = hash216(
            {
                "domain": "HHS-NFV-DEPENDENCY-EDGE-V1",
                "source": self.source,
                "target": self.target,
                "edge_type": self.edge_type,
                "order": self.order,
            }
        )
        if self.edge_index and self.edge_index != expected:
            raise NFVError("NFV_DEPENDENCY_EDGE_IDENTITY_MISMATCH", "edge index is not canonical")
        object.__setattr__(self, "edge_index", expected)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DependencyGraph:
    def __init__(
        self,
        *,
        max_nodes: int = 1024,
        max_edges: int = 4096,
        cycle_profile: Mapping[str, Any] | None = None,
    ) -> None:
        if max_nodes <= 0 or max_edges <= 0:
            raise NFVError("NFV_INVALID_GRAPH_BOUND", "graph bounds must be positive")
        self.max_nodes = int(max_nodes)
        self.max_edges = int(max_edges)
        self.cycle_profile = canonical(cycle_profile) if cycle_profile is not None else None
        if self.cycle_profile is not None:
            required = {"cycle_type", "convergence_predicate", "maximum_iterations", "termination_state", "resource_bound"}
            if set(self.cycle_profile) != required:
                raise NFVError("NFV_INVALID_CYCLE_PROFILE", "cycle profile fields are incomplete")
            if int(self.cycle_profile["maximum_iterations"]) <= 0 or int(self.cycle_profile["resource_bound"]) <= 0:
                raise NFVError("NFV_INVALID_CYCLE_PROFILE", "cycle bounds must be positive")
        self._nodes: dict[str, Any] = {}
        self._edges: dict[str, DependencyEdge] = {}

    @property
    def nodes(self) -> dict[str, Any]:
        return dict(self._nodes)

    @property
    def edges(self) -> tuple[DependencyEdge, ...]:
        return tuple(sorted(self._edges.values(), key=lambda edge: (edge.target, edge.order, edge.source, edge.edge_type)))

    def add_node(self, node_id: str, payload: Any) -> None:
        if not node_id:
            raise NFVError("NFV_INVALID_DEPENDENCY_NODE", "node id is mandatory")
        if node_id in self._nodes:
            if canonical(self._nodes[node_id]) != canonical(payload):
                raise NFVError("NFV_DEPENDENCY_NODE_CONFLICT", "node id already binds different payload")
            return
        if len(self._nodes) >= self.max_nodes:
            raise NFVError("RESOURCE_BOUNDED", "maximum dependency node count reached")
        self._nodes[node_id] = canonical(payload)

    def add_edge(self, edge: DependencyEdge) -> None:
        if edge.source not in self._nodes or edge.target not in self._nodes:
            raise NFVError("NFV_UNKNOWN_DEPENDENCY_NODE", "edge endpoints must exist before linking")
        if edge.edge_index in self._edges:
            return
        if len(self._edges) >= self.max_edges:
            raise NFVError("RESOURCE_BOUNDED", "maximum dependency edge count reached")
        self._edges[edge.edge_index] = edge
        if self.cycle_profile is None and self._has_cycle():
            del self._edges[edge.edge_index]
            raise NFVError("NFV_UNDECLARED_DEPENDENCY_CYCLE", "dependency graph must remain acyclic")

    def dependencies_of(self, node_id: str) -> tuple[str, ...]:
        self._require_node(node_id)
        return tuple(
            edge.source
            for edge in sorted(self._edges.values(), key=lambda item: (item.order, item.source, item.edge_type))
            if edge.target == node_id
        )

    def dependents_of(self, node_id: str) -> tuple[str, ...]:
        self._require_node(node_id)
        return tuple(
            edge.target
            for edge in sorted(self._edges.values(), key=lambda item: (item.order, item.target, item.edge_type))
            if edge.source == node_id
        )

    def ready_nodes(self, resolved: Iterable[str]) -> tuple[str, ...]:
        resolved_set = set(resolved)
        unknown = resolved_set.difference(self._nodes)
        if unknown:
            raise NFVError("NFV_UNKNOWN_DEPENDENCY_NODE", "resolved set includes unknown nodes", {"nodes": sorted(unknown)})
        ready = [
            node_id
            for node_id in sorted(self._nodes)
            if node_id not in resolved_set and set(self.dependencies_of(node_id)).issubset(resolved_set)
        ]
        return tuple(ready)

    def topological_order(self) -> tuple[str, ...]:
        if self.cycle_profile is not None and self._has_cycle():
            raise NFVError("NFV_RECURRENT_GRAPH_REQUIRES_ITERATIVE_EXECUTOR", "cyclic graph has no DAG topological order")
        incoming = {node_id: set(self.dependencies_of(node_id)) for node_id in self._nodes}
        ready = sorted(node_id for node_id, dependencies in incoming.items() if not dependencies)
        order: list[str] = []
        while ready:
            node_id = ready.pop(0)
            order.append(node_id)
            for dependent in self.dependents_of(node_id):
                incoming[dependent].discard(node_id)
                if not incoming[dependent] and dependent not in order and dependent not in ready:
                    ready.append(dependent)
                    ready.sort()
        if len(order) != len(self._nodes):
            raise NFVError("NFV_DEPENDENCY_CYCLE", "graph could not be topologically ordered")
        return tuple(order)

    def graph_index(self) -> str:
        return hash216(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "HHS_NFV_DEPENDENCY_GRAPH_V1",
            "max_nodes": self.max_nodes,
            "max_edges": self.max_edges,
            "cycle_profile": self.cycle_profile,
            "nodes": [{"node_id": node_id, "payload": self._nodes[node_id]} for node_id in sorted(self._nodes)],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "DependencyGraph":
        allowed = {"schema", "max_nodes", "max_edges", "cycle_profile", "nodes", "edges"}
        if set(value) != allowed or value.get("schema") != "HHS_NFV_DEPENDENCY_GRAPH_V1":
            raise NFVError("NFV_INVALID_DEPENDENCY_GRAPH_SCHEMA", "dependency graph schema is not canonical")
        graph = cls(
            max_nodes=int(value["max_nodes"]),
            max_edges=int(value["max_edges"]),
            cycle_profile=value["cycle_profile"],
        )
        for node in value["nodes"]:
            if set(node) != {"node_id", "payload"}:
                raise NFVError("NFV_INVALID_DEPENDENCY_NODE", "serialized node fields are invalid")
            graph.add_node(str(node["node_id"]), node["payload"])
        for edge_value in value["edges"]:
            graph.add_edge(DependencyEdge(**edge_value))
        return graph

    def _require_node(self, node_id: str) -> None:
        if node_id not in self._nodes:
            raise NFVError("NFV_UNKNOWN_DEPENDENCY_NODE", "dependency node is not registered", {"node_id": node_id})

    def _has_cycle(self) -> bool:
        visiting: set[str] = set()
        visited: set[str] = set()
        adjacency: dict[str, list[str]] = {node_id: [] for node_id in self._nodes}
        for edge in self._edges.values():
            adjacency[edge.source].append(edge.target)

        def visit(node_id: str) -> bool:
            if node_id in visiting:
                return True
            if node_id in visited:
                return False
            visiting.add(node_id)
            for dependent in sorted(adjacency[node_id]):
                if visit(dependent):
                    return True
            visiting.remove(node_id)
            visited.add(node_id)
            return False

        return any(visit(node_id) for node_id in sorted(self._nodes) if node_id not in visited)
