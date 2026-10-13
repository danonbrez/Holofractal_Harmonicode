"""Bounded, read-only P-indexed cross-modal bridge candidate discovery.

Traverses explicit, already-known P/modality records. Arithmetic relations
are exact; modality changes require declared same-P bridge candidates.
Neither graph adjacency nor declaration proves a reversible converter or
grants Lane 5/VM81/Hash72/Hash216 admission.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from hashlib import sha256
import json

SCHEMA = "HHS_PASS220_CROSS_MODAL_P_BRIDGE_SEARCH_V1"

class BridgeSearchError(ValueError):
    pass

@dataclass(frozen=True, order=True)
class Node:
    P: int
    modality: str

    def __post_init__(self):
        if isinstance(self.P, bool) or not isinstance(self.P, int) or self.P < 0:
            raise BridgeSearchError("EXACT_NONNEGATIVE_P_REQUIRED")
        if not isinstance(self.modality, str) or not self.modality or not self.modality.isidentifier():
            raise BridgeSearchError("MODALITY_IDENTIFIER_REQUIRED")


def relations(a: int, b: int) -> tuple[str, ...]:
    """Source-to-target exact arithmetic edges; no host floats or division."""
    found = []
    if b == a + 1:
        found.append("SUCCESSOR")
    if a > 0 and b == a - 1:
        found.append("PREDECESSOR")
    if b == a * a:
        found.append("SQUARE")
    if a == b * b:
        found.append("ROOT_SQUARE")
    if a > 1 and b > a and b % a == 0:
        found.append("FACTOR_TO_MULTIPLE")
    if b > 1 and a > b and a % b == 0:
        found.append("MULTIPLE_TO_FACTOR")
    return tuple(found)


def find_bridge(
    source: Node,
    target: Node,
    known_nodes: tuple[Node, ...],
    *,
    declared_same_p_bridges: tuple[tuple[str, str], ...] = (),
    max_hops: int = 8,
) -> dict:
    if isinstance(max_hops, bool) or not isinstance(max_hops, int) or not 0 <= max_hops <= 64:
        raise BridgeSearchError("BOUNDED_HOP_COUNT_REQUIRED")
    available = set(known_nodes)
    if source not in available or target not in available:
        raise BridgeSearchError("ENDPOINT_NOT_IN_INHERITED_INDEX")
    declarations = set()
    for left, right in declared_same_p_bridges:
        if not isinstance(left, str) or not isinstance(right, str) or not left or not right:
            raise BridgeSearchError("INVALID_MODALITY_BRIDGE_DECLARATION")
        declarations.add((left, right))
    ordered = sorted(available)
    frontier = deque([(source, (source,), ())])
    visited = {source}
    outcome = None
    while frontier:
        current, path, edges = frontier.popleft()
        if current == target:
            outcome = (path, edges)
            break
        if len(edges) >= max_hops:
            continue
        for candidate in ordered:
            if candidate in visited:
                continue
            kinds = (
                relations(current.P, candidate.P)
                if current.modality == candidate.modality
                else ()
            )
            if current.P == candidate.P and (
                current.modality, candidate.modality
            ) in declarations:
                kinds = ("DECLARED_SAME_P_MODALITY_BRIDGE",)
            if not kinds:
                continue
            visited.add(candidate)
            frontier.append((candidate, path + (candidate,), edges + (kinds[0],)))
    if outcome is None:
        return {
            "schema": SCHEMA, "found": False, "exhaustive": False,
            "reason": "NO_PATH_IN_BOUNDED_EXPLICIT_CANDIDATE_GRAPH",
            "candidate_only": True, "native_admission": False,
        }
    path, edges = outcome
    record = {
        "schema": SCHEMA,
        "found": True,
        "source": {"P": str(source.P), "modality": source.modality},
        "target": {"P": str(target.P), "modality": target.modality},
        "path": [{"P": str(n.P), "modality": n.modality} for n in path],
        "edge_kinds": list(edges),
        "hops": len(edges),
        "candidate_only": True,
        "type_converter_executed": False,
        "exact_external_type_roundtrip_verified": False,
        "native_admission": False,
        "hash72_minted": False,
        "hash216_persisted": False,
    }
    record["candidate_sha256"] = sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":")
    ).encode("ascii")).hexdigest()
    return record
