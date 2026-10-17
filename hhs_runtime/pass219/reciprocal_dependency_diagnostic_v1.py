"""Pass 219 reciprocal dependency diagnostic.

Candidate-only, pure, non-authoritative. Does not call VM81 or mint Hash72/216
canonical state. Maintains input order and original evidence identifiers.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class Verdict(str, Enum):
    ADMISSIBLE = "+1"
    UNRESOLVED = "0"
    FORBIDDEN = "-1"


@dataclass(frozen=True)
class Dependency:
    sources: tuple[str, ...]
    targets: tuple[str, ...]
    relation: str
    evidence_ids: tuple[str, ...] = ()
    proven_forbidden: bool = False
    unresolved: bool = False

    def __post_init__(self) -> None:
        if not self.sources or not self.targets or not self.relation:
            raise ValueError("Dependency must have sources, targets and relation")
        if any(not part for part in self.sources + self.targets):
            raise ValueError("Dependency endpoints must be named")
        if self.proven_forbidden and self.unresolved:
            raise ValueError("An edge cannot simultaneously be proven and unresolved")


@dataclass(frozen=True)
class DependencyEvaluation:
    verdict: Verdict
    reachable_nodes: tuple[str, ...]
    examined_edges: tuple[int, ...]
    unresolved_edges: tuple[int, ...]
    forbidden_edges: tuple[int, ...]
    truncated: bool
    # Diagnostic only: downstream authorization still requires E01-E18
    # evaluation and canonical Lane 5 / VM81 admission.


def evaluate_dependency_scope(
    starting_nodes: Sequence[str],
    dependencies: Sequence[Dependency],
    *,
    max_edges: int = 4096,
    max_nodes: int = 4096,
) -> DependencyEvaluation:
    """Bounded causal reachability across ordered joint-source hyperedges.

    A hyperedge fires only after every source is reachable. The procedure
    computes a least fixed point; cycles are retained, not treated as faults.
    Incomplete proof or search limits produce UNRESOLVED, never admission.
    """
    if max_edges < 1 or max_nodes < 1:
        raise ValueError("Limits must be positive")
    nodes = tuple(dict.fromkeys(starting_nodes))
    if not nodes or any(not n for n in nodes):
        raise ValueError("Nonempty starting_nodes required")
    if len(nodes) > max_nodes:
        return DependencyEvaluation(Verdict.UNRESOLVED, nodes, (), (), (), True)
    reached = set(nodes)
    visited = list(nodes)
    examined = []
    examined_set: set[int] = set()
    truncated = False
    changed = True
    while changed:
        changed = False
        for idx, edge in enumerate(dependencies):
            if idx in examined_set or not all(s in reached for s in edge.sources):
                continue
            if len(examined) >= max_edges:
                truncated = True
                break
            examined_set.add(idx)
            examined.append(idx)
            for target in edge.targets:
                if target not in reached:
                    if len(visited) >= max_nodes:
                        truncated = True
                        break
                    reached.add(target)
                    visited.append(target)
                    changed = True
            if truncated:
                break
        if truncated:
            break
    unresolved = tuple(i for i in examined if dependencies[i].unresolved)
    forbidden = tuple(i for i in examined if dependencies[i].proven_forbidden)
    if forbidden:
        verdict = Verdict.FORBIDDEN
    elif truncated or unresolved:
        verdict = Verdict.UNRESOLVED
    else:
        verdict = Verdict.ADMISSIBLE
    return DependencyEvaluation(
        verdict, tuple(visited), tuple(examined), unresolved, forbidden, truncated
    )
