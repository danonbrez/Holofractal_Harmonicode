from __future__ import annotations
from collections import defaultdict, deque
from typing import Dict, Iterable, List, Set
from .model import EdgeType, OperationNode, TypedEdge, Pass152Error


class TypedDependencyGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, OperationNode] = {}
        self.edges: list[TypedEdge] = []
        self._out: dict[str, set[str]] = defaultdict(set)
        self._in: dict[str, set[str]] = defaultdict(set)

    def add_node(self, node: OperationNode) -> None:
        if node.node_id in self.nodes:
            raise Pass152Error(f"duplicate node: {node.node_id}")
        if node.horizon < 1:
            raise Pass152Error("candidate horizon must be >= 1")
        self.nodes[node.node_id] = node

    def add_edge(self, source: str, target: str, edge_type: EdgeType) -> None:
        if source not in self.nodes or target not in self.nodes:
            raise Pass152Error("edge endpoints must exist")
        edge = TypedEdge(source, target, edge_type)
        if edge in self.edges:
            return
        self.edges.append(edge)
        self._out[source].add(target)
        self._in[target].add(source)
        self.nodes[target].dependencies.add(source)
        self.nodes[target].edge_types[source] = edge_type
        if self.has_cycle():
            self.edges.pop()
            self._out[source].remove(target)
            self._in[target].remove(source)
            self.nodes[target].dependencies.remove(source)
            self.nodes[target].edge_types.pop(source, None)
            raise Pass152Error("dependency cycle rejected")

    def dependents(self, node_id: str) -> list[str]:
        return sorted(self._out.get(node_id, set()))

    def dependencies(self, node_id: str) -> list[str]:
        return sorted(self._in.get(node_id, set()))

    def has_cycle(self) -> bool:
        indegree = {n: len(self._in.get(n, set())) for n in self.nodes}
        q = deque(sorted(n for n, d in indegree.items() if d == 0))
        visited = 0
        while q:
            n = q.popleft(); visited += 1
            for nxt in sorted(self._out.get(n, set())):
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    q.append(nxt)
        return visited != len(self.nodes)

    def topological_order(self) -> list[str]:
        indegree = {n: len(self._in.get(n, set())) for n in self.nodes}
        q = deque(sorted(n for n, d in indegree.items() if d == 0))
        out = []
        while q:
            n = q.popleft(); out.append(n)
            for nxt in sorted(self._out.get(n, set())):
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    q.append(nxt)
        if len(out) != len(self.nodes):
            raise Pass152Error("graph is cyclic")
        return out

    def descendants(self, node_id: str) -> list[str]:
        seen: Set[str] = set(); stack = list(self._out.get(node_id, set()))
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n); stack.extend(self._out.get(n, set()))
        return sorted(seen)

    def critical_cost(self, node_id: str) -> float:
        memo: dict[str, float] = {}
        def visit(n: str) -> float:
            if n in memo:
                return memo[n]
            children = self._out.get(n, set())
            own = float(self.nodes[n].estimated_cost)
            memo[n] = own + (max((visit(c) for c in children), default=0.0))
            return memo[n]
        return visit(node_id)

    def serialize(self) -> dict:
        return {
            "schema": "HHS_PASS152_TYPED_DEPENDENCY_GRAPH_V1",
            "nodes": [
                {
                    "node_id": n.node_id,
                    "operation_id": n.operation_id,
                    "dependencies": sorted(n.dependencies),
                    "mandatory": n.mandatory,
                    "estimated_cost": str(n.estimated_cost),
                    "candidate_root": n.candidate_root,
                    "semantic_version": n.semantic_version,
                    "phase_id": n.phase_id,
                    "lane_id": n.lane_id,
                    "horizon": n.horizon,
                }
                for n in sorted(self.nodes.values(), key=lambda x: x.node_id)
            ],
            "edges": [
                {"source": e.source, "target": e.target, "edge_type": e.edge_type.value}
                for e in sorted(self.edges, key=lambda e: (e.source, e.target, e.edge_type.value))
            ],
        }
