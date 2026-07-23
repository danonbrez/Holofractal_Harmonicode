"""Pass 149 deterministic specification-preserving contract executor.

The executor preserves every obligation verbatim, applies explicit authority order,
and models equality as a constraint membrane over one shared projection rather than
a Boolean comparison or sequential message pipe.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Callable, Iterable, Mapping
import json

@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    text: str
    authority: int
    scope: str = "global"
    supersedes: tuple[str, ...] = ()

@dataclass(frozen=True)
class ProjectionState:
    values: Mapping[str, Any]
    generation: int = 0

class ObligationLedger:
    def __init__(self, obligations: Iterable[Obligation] = ()) -> None:
        self._items: list[Obligation] = []
        self._ids: set[str] = set()
        for item in obligations:
            self.append(item)

    def append(self, item: Obligation) -> None:
        if not item.obligation_id or not item.text:
            raise ValueError("obligation id and text are required")
        if item.obligation_id in self._ids:
            raise ValueError(f"duplicate obligation: {item.obligation_id}")
        self._items.append(item)
        self._ids.add(item.obligation_id)

    def active(self) -> tuple[Obligation, ...]:
        superseded = {x for item in self._items for x in item.supersedes}
        return tuple(sorted((x for x in self._items if x.obligation_id not in superseded),
                            key=lambda x: (-x.authority, self._items.index(x))))

    def digest(self) -> str:
        payload = json.dumps([asdict(x) for x in self._items], sort_keys=True,
                             separators=(",", ":")).encode()
        return sha256(payload).hexdigest()

    def coverage(self, results: Mapping[str, Any]) -> bool:
        return all(x.obligation_id in results for x in self.active())

class EqualityMembrane:
    """A simultaneous limit over all equality sites sharing one state projection."""
    def __init__(self, constraints: Iterable[Callable[[Mapping[str, Any]], Mapping[str, Any]]]):
        self.constraints = tuple(constraints)
        if not self.constraints:
            raise ValueError("at least one constraint is required")

    def project(self, state: ProjectionState) -> ProjectionState:
        current = dict(state.values)
        # Every constraint observes the same generation snapshot. Their updates are
        # merged deterministically; conflicting updates are explicit, never hidden.
        proposals: list[Mapping[str, Any]] = [fn(dict(current)) for fn in self.constraints]
        merged = dict(current)
        owners: dict[str, Any] = {}
        for proposal in proposals:
            for key, value in proposal.items():
                if key in owners and owners[key] != value:
                    raise ValueError(f"projection conflict for {key}")
                owners[key] = value
                merged[key] = value
        return ProjectionState(merged, state.generation + 1)
