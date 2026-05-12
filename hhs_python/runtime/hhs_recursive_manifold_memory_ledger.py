# hhs_python/runtime/hhs_recursive_manifold_memory_ledger.py
#
# HHS / HARMONICODE
# Recursive Manifold Memory Ledger
#
# Canonical Runtime OS Causal Ancestry Substrate
#
# Runtime Principle:
#
#   memory
#   =
#   recursive topology-preserving causal inheritance
#
# NOT:
#
#   stored historical snapshots
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# Runtime Primitive:
#
#   recursive topology-preserving manifold ancestry
#

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
import hashlib
import json
import time


HASH216_WIDTH = 216


def _hash216(data: str) -> str:
    h1 = hashlib.sha512(data.encode()).hexdigest()
    h2 = hashlib.sha256(data.encode()).hexdigest()
    return (h1 + h2)[:HASH216_WIDTH]


@dataclass(frozen=True)
class HHSLedgerWitness:
    witness_id: str
    forward_hash216: str
    reciprocal_hash216: str

    persistable: bool = True
    reconstructible: bool = True
    ancestry_equivalent: bool = True
    phase_entangled: bool = True
    temporally_equivalent: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        return (
            self.persistable
            and self.reconstructible
            and self.ancestry_equivalent
            and self.phase_entangled
            and self.temporally_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


@dataclass(frozen=True)
class HHSManifoldLedgerEntry:
    entry_id: str

    parent_entry_hash216: str
    ancestor_root_hash216: str

    projection_hash216: str
    execution_hash216: str
    transport_hash216: str
    governance_hash216: str
    origin_hash216: str
    replay_hash216: str
    semantic_hash216: str
    causal_hash216: str
    temporal_hash216: str
    identity_hash216: str

    forward_lineage_hash216: str
    reciprocal_lineage_hash216: str

    ledger_topology_hash216: str

    persistable: bool = True
    reconstructible: bool = True
    ancestry_equivalent: bool = True
    phase_entangled: bool = True
    temporally_equivalent: bool = True

    fork_count: int = 0
    branch_depth: int = 0
    replay_depth: int = 0

    freeze_required: bool = False
    rollback_required: bool = False
    correction_required: bool = False

    lineage_witness: Optional[HHSLedgerWitness] = None
    replay_witness: Optional[HHSLedgerWitness] = None
    ancestry_witness: Optional[HHSLedgerWitness] = None
    reciprocal_witness: Optional[HHSLedgerWitness] = None

    entry_proof_hash216: str = ""
    timestamp_ns: int = field(default_factory=time.time_ns)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        if not self.persistable:
            return False
        if not self.reconstructible:
            return False
        if not self.ancestry_equivalent:
            return False
        if not self.phase_entangled:
            return False
        if not self.temporally_equivalent:
            return False
        if self.rollback_required and not self.freeze_required:
            return False
        if self.fork_count < 0 or self.branch_depth < 0 or self.replay_depth < 0:
            return False

        for witness in (
            self.lineage_witness,
            self.replay_witness,
            self.ancestry_witness,
            self.reciprocal_witness,
        ):
            if witness is not None and not witness.validate():
                return False

        return True

    def closure_hash216(self) -> str:
        payload = {
            "entry_id": self.entry_id,
            "parent_entry": self.parent_entry_hash216,
            "ancestor_root": self.ancestor_root_hash216,
            "projection": self.projection_hash216,
            "execution": self.execution_hash216,
            "transport": self.transport_hash216,
            "governance": self.governance_hash216,
            "origin": self.origin_hash216,
            "replay": self.replay_hash216,
            "semantic": self.semantic_hash216,
            "causal": self.causal_hash216,
            "temporal": self.temporal_hash216,
            "identity": self.identity_hash216,
            "forward_lineage": self.forward_lineage_hash216,
            "reciprocal_lineage": self.reciprocal_lineage_hash216,
            "topology": self.ledger_topology_hash216,
            "fork_count": self.fork_count,
            "branch_depth": self.branch_depth,
            "replay_depth": self.replay_depth,
            "freeze_required": self.freeze_required,
            "rollback_required": self.rollback_required,
            "correction_required": self.correction_required,
        }
        return _hash216(json.dumps(payload, sort_keys=True))

    def receipt(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "closure_hash216": self.closure_hash216(),
            "entry_proof_hash216": self.entry_proof_hash216,
            "parent_entry_hash216": self.parent_entry_hash216,
            "ancestor_root_hash216": self.ancestor_root_hash216,
            "persistable": self.persistable,
            "reconstructible": self.reconstructible,
            "ancestry_equivalent": self.ancestry_equivalent,
            "freeze_required": self.freeze_required,
            "rollback_required": self.rollback_required,
            "correction_required": self.correction_required,
            "valid": self.validate(),
            "timestamp_ns": self.timestamp_ns,
        }


class HHSRecursiveManifoldMemoryLedger:
    """
    Canonical Runtime OS recursive manifold memory substrate.

    Every entry is a topology-preserving causal ancestry artifact.
    """

    def __init__(self):
        self.entry_registry: Dict[str, HHSManifoldLedgerEntry] = {}
        self.entry_lineage: Dict[str, List[str]] = {}
        self.entry_dependencies: Dict[str, Set[str]] = {}

        self.parent_field: Dict[str, str] = {}
        self.ancestor_root_field: Dict[str, str] = {}

        self.projection_field: Dict[str, str] = {}
        self.execution_field: Dict[str, str] = {}
        self.transport_field: Dict[str, str] = {}
        self.governance_field: Dict[str, str] = {}
        self.origin_field: Dict[str, str] = {}
        self.replay_field: Dict[str, str] = {}
        self.semantic_field: Dict[str, str] = {}
        self.causal_field: Dict[str, str] = {}
        self.temporal_field: Dict[str, str] = {}
        self.identity_field: Dict[str, str] = {}

    def append_entry(self, entry: HHSManifoldLedgerEntry) -> bool:
        if not entry.validate():
            return False

        self.entry_registry[entry.entry_id] = entry

        if entry.entry_id not in self.entry_lineage:
            self.entry_lineage[entry.entry_id] = []

        self.entry_lineage[entry.entry_id].append(entry.closure_hash216())

        self.parent_field[entry.entry_id] = entry.parent_entry_hash216
        self.ancestor_root_field[entry.entry_id] = entry.ancestor_root_hash216

        self.projection_field[entry.entry_id] = entry.projection_hash216
        self.execution_field[entry.entry_id] = entry.execution_hash216
        self.transport_field[entry.entry_id] = entry.transport_hash216
        self.governance_field[entry.entry_id] = entry.governance_hash216
        self.origin_field[entry.entry_id] = entry.origin_hash216
        self.replay_field[entry.entry_id] = entry.replay_hash216
        self.semantic_field[entry.entry_id] = entry.semantic_hash216
        self.causal_field[entry.entry_id] = entry.causal_hash216
        self.temporal_field[entry.entry_id] = entry.temporal_hash216
        self.identity_field[entry.entry_id] = entry.identity_hash216

        if entry.entry_id not in self.entry_dependencies:
            self.entry_dependencies[entry.entry_id] = set()

        if entry.parent_entry_hash216:
            parent_id = self._entry_id_by_closure(entry.parent_entry_hash216)
            if parent_id is not None:
                self.entry_dependencies[parent_id].add(entry.entry_id)

        return True

    def connect_entry_dependency(self, source_entry: str, target_entry: str) -> bool:
        if source_entry not in self.entry_registry:
            return False
        if target_entry not in self.entry_registry:
            return False

        self.entry_dependencies[source_entry].add(target_entry)
        return True

    def _entry_id_by_closure(self, closure_hash216: str) -> Optional[str]:
        for entry_id, entry in self.entry_registry.items():
            if entry.closure_hash216() == closure_hash216:
                return entry_id
        return None

    def validate_ledger(self) -> bool:
        for entry in self.entry_registry.values():
            if not entry.validate():
                return False
        return True

    def ancestry_equivalent(self) -> bool:
        for entry in self.entry_registry.values():
            if not entry.ancestry_equivalent:
                return False
        return True

    def reconstructible(self) -> bool:
        for entry in self.entry_registry.values():
            if not entry.reconstructible:
                return False
        return True

    def entry_cone(self, entry_id: str) -> Set[str]:
        visited: Set[str] = set()

        def walk(node: str):
            if node in visited:
                return
            visited.add(node)
            for nxt in self.entry_dependencies.get(node, set()):
                walk(nxt)

        walk(entry_id)
        return visited

    def field_hash216(self) -> str:
        payload = {
            "entry_registry": sorted(
                [entry.closure_hash216() for entry in self.entry_registry.values()]
            ),
            "lineage": self.entry_lineage,
            "dependencies": {
                k: sorted(list(v)) for k, v in self.entry_dependencies.items()
            },
            "parent": self.parent_field,
            "ancestor_root": self.ancestor_root_field,
            "projection": self.projection_field,
            "execution": self.execution_field,
            "transport": self.transport_field,
            "governance": self.governance_field,
            "origin": self.origin_field,
            "replay": self.replay_field,
            "semantic": self.semantic_field,
            "causal": self.causal_field,
            "temporal": self.temporal_field,
            "identity": self.identity_field,
        }
        return _hash216(json.dumps(payload, sort_keys=True))

    def authoritative_entry(self) -> Optional[HHSManifoldLedgerEntry]:
        if not self.entry_registry:
            return None

        ordered = sorted(
            self.entry_registry.values(),
            key=lambda e: (
                e.branch_depth,
                e.replay_depth,
                e.closure_hash216(),
                e.ledger_topology_hash216,
            ),
        )
        return ordered[0]

    def receipt(self) -> Dict[str, Any]:
        authoritative = self.authoritative_entry()

        return {
            "field_hash216": self.field_hash216(),
            "entry_count": len(self.entry_registry),
            "dependency_count": sum(len(v) for v in self.entry_dependencies.values()),
            "ancestry_equivalent": self.ancestry_equivalent(),
            "reconstructible": self.reconstructible(),
            "authoritative_entry": authoritative.entry_id if authoritative else None,
            "valid": self.validate_ledger(),
            "timestamp_ns": time.time_ns(),
        }