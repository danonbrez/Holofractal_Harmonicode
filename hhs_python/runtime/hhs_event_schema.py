# hhs_python/runtime/hhs_event_schema.py
#
# HHS / HARMONICODE
# Canonical Runtime Event Schema
#
# Runtime Principle:
#
#   events
#   =
#   canonical runtime causality packets
#
# NOT:
#
#   logging artifacts
#

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, Optional, List
import hashlib
import json
import time
import uuid


HASH72_LEN = 72
HASH216_LEN = 216


# ============================================================
# HASH HELPERS
# ============================================================

def _hash72(data: str) -> str:
    h = hashlib.sha512(data.encode()).hexdigest()
    return h[:HASH72_LEN]


def _hash216(data: str) -> str:
    h1 = hashlib.sha512(data.encode()).hexdigest()
    h2 = hashlib.sha256(data.encode()).hexdigest()
    return (h1 + h2)[:HASH216_LEN]


# ============================================================
# EVENT TYPES
# ============================================================

class HHSEventType(str, Enum):

    # --------------------------------------------------------
    # Runtime execution
    # --------------------------------------------------------

    STEP = "STEP"
    HALT = "HALT"

    CONVERGENCE = "CONVERGENCE"

    # --------------------------------------------------------
    # Receipts / replay
    # --------------------------------------------------------

    RECEIPT_COMMIT = "RECEIPT_COMMIT"
    REPLAY_COMMIT = "REPLAY_COMMIT"

    SNAPSHOT = "SNAPSHOT"
    RESTORE = "RESTORE"

    # --------------------------------------------------------
    # Branch topology
    # --------------------------------------------------------

    BRANCH = "BRANCH"
    REJOIN = "REJOIN"

    # --------------------------------------------------------
    # Runtime transport
    # --------------------------------------------------------

    TRANSPORT_UPDATE = "TRANSPORT_UPDATE"

    # --------------------------------------------------------
    # Graph topology
    # --------------------------------------------------------

    GRAPH_UPDATE = "GRAPH_UPDATE"

    # --------------------------------------------------------
    # Projection / observability
    # --------------------------------------------------------

    PROJECTION_UPDATE = "PROJECTION_UPDATE"

    # --------------------------------------------------------
    # Runtime objects
    # --------------------------------------------------------

    OBJECT_ADD = "OBJECT_ADD"
    OBJECT_REMOVE = "OBJECT_REMOVE"

    # --------------------------------------------------------
    # Consensus / governance
    # --------------------------------------------------------

    CONSENSUS_UPDATE = "CONSENSUS_UPDATE"
    GOVERNANCE_UPDATE = "GOVERNANCE_UPDATE"

    # --------------------------------------------------------
    # Runtime lifecycle
    # --------------------------------------------------------

    RUNTIME_INIT = "RUNTIME_INIT"
    RUNTIME_RESET = "RUNTIME_RESET"

    # --------------------------------------------------------
    # Generic
    # --------------------------------------------------------

    CUSTOM = "CUSTOM"


# ============================================================
# EVENT FLAGS
# ============================================================

class HHSEventFlags:

    REPLAYABLE = 1 << 0
    RECONSTRUCTIBLE = 1 << 1

    TRANSPORT_SYNCHRONIZED = 1 << 2
    GRAPH_SYNCHRONIZED = 1 << 3

    CONVERGED = 1 << 4
    HALTED = 1 << 5

    BRANCHED = 1 << 6
    REJOINED = 1 << 7

    RECEIPT_COMMITTED = 1 << 8
    SNAPSHOT_EVENT = 1 << 9

    OBSERVABLE = 1 << 10
    CANONICAL = 1 << 11


# ============================================================
# EVENT LINEAGE
# ============================================================

@dataclass
class HHSEventLineage:

    parent_event_hash216: Optional[str] = None

    receipt_lineage: List[str] = field(
        default_factory=list
    )

    replay_lineage: List[str] = field(
        default_factory=list
    )

    branch_lineage: List[str] = field(
        default_factory=list
    )

    graph_lineage: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def compute_hash216(self) -> str:

        return _hash216(
            json.dumps(
                asdict(self),
                sort_keys=True,
                default=str,
            )
        )


# ============================================================
# CANONICAL EVENT
# ============================================================

@dataclass
class HHSEvent:
    """
    Canonical runtime causality packet.
    """

    runtime_id: str

    event_type: HHSEventType

    payload: Dict[str, Any]

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    event_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    event_hash72: str = ""
    event_hash216: str = ""

    # --------------------------------------------------------
    # Runtime continuity
    # --------------------------------------------------------

    state_hash216: str = ""
    receipt_hash216: str = ""

    transport_hash216: str = ""
    graph_hash216: str = ""

    # --------------------------------------------------------
    # Runtime topology
    # --------------------------------------------------------

    branch_id: str = "root"

    parent_branch_id: Optional[str] = None

    # --------------------------------------------------------
    # Event sequencing
    # --------------------------------------------------------

    sequence: int = 0

    epoch: int = 0

    timestamp_ns: int = field(
        default_factory=time.time_ns
    )

    # --------------------------------------------------------
    # Witnessing
    # --------------------------------------------------------

    witness_flags: int = 0

    event_flags: int = (
        HHSEventFlags.REPLAYABLE
        | HHSEventFlags.RECONSTRUCTIBLE
        | HHSEventFlags.OBSERVABLE
        | HHSEventFlags.CANONICAL
    )

    # --------------------------------------------------------
    # Continuity
    # --------------------------------------------------------

    replayable: bool = True
    reconstructible: bool = True

    synchronized: bool = False
    converged: bool = False
    halted: bool = False

    # --------------------------------------------------------
    # Lineage
    # --------------------------------------------------------

    lineage: HHSEventLineage = field(
        default_factory=HHSEventLineage
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # ========================================================
    # HASHING
    # ========================================================

    def compute_hashes(self):

        payload = {
            "runtime_id": self.runtime_id,

            "event_id": self.event_id,

            "event_type": self.event_type.value,

            "payload": self.payload,

            "state_hash216": self.state_hash216,
            "receipt_hash216": self.receipt_hash216,

            "transport_hash216": self.transport_hash216,
            "graph_hash216": self.graph_hash216,

            "branch_id": self.branch_id,
            "parent_branch_id": self.parent_branch_id,

            "sequence": self.sequence,
            "epoch": self.epoch,

            "timestamp_ns": self.timestamp_ns,

            "witness_flags": self.witness_flags,
            "event_flags": self.event_flags,

            "replayable": self.replayable,
            "reconstructible": self.reconstructible,

            "synchronized": self.synchronized,
            "converged": self.converged,
            "halted": self.halted,

            "lineage": asdict(self.lineage),
        }

        serialized = json.dumps(
            payload,
            sort_keys=True,
            default=str,
        )

        self.event_hash72 = _hash72(
            serialized
        )

        self.event_hash216 = _hash216(
            serialized
        )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def serialize(self) -> Dict[str, Any]:

        self.compute_hashes()

        return asdict(self)

    @classmethod
    def deserialize(
        cls,
        payload: Dict[str, Any]
    ) -> "HHSEvent":

        event_type = HHSEventType(
            payload["event_type"]
        )

        payload = dict(payload)
        payload["event_type"] = event_type

        if "lineage" in payload:
            payload["lineage"] = HHSEventLineage(
                **payload["lineage"]
            )

        return cls(**payload)

    # ========================================================
    # LINEAGE
    # ========================================================

    def attach_parent(
        self,
        parent_event: "HHSEvent"
    ):

        self.lineage.parent_event_hash216 = (
            parent_event.event_hash216
        )

    def commit_receipt(
        self,
        receipt_hash216: str
    ):

        self.lineage.receipt_lineage.append(
            receipt_hash216
        )

    def commit_replay(
        self,
        replay_hash216: str
    ):

        self.lineage.replay_lineage.append(
            replay_hash216
        )

    def commit_branch(
        self,
        branch_hash216: str
    ):

        self.lineage.branch_lineage.append(
            branch_hash216
        )

    def commit_graph(
        self,
        graph_hash216: str
    ):

        self.lineage.graph_lineage.append(
            graph_hash216
        )

    # ========================================================
    # EVENT FLAGS
    # ========================================================

    def set_flag(
        self,
        flag: int
    ):

        self.event_flags |= flag

    def clear_flag(
        self,
        flag: int
    ):

        self.event_flags &= ~flag

    def has_flag(
        self,
        flag: int
    ) -> bool:

        return bool(
            self.event_flags & flag
        )

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(self) -> Dict[str, Any]:

        self.compute_hashes()

        return {
            "runtime_id": self.runtime_id,

            "event_id": self.event_id,

            "event_type": self.event_type.value,

            "event_hash72": self.event_hash72,
            "event_hash216": self.event_hash216,

            "state_hash216": self.state_hash216,
            "receipt_hash216": self.receipt_hash216,

            "branch_id": self.branch_id,

            "sequence": self.sequence,
            "epoch": self.epoch,

            "replayable": self.replayable,
            "reconstructible": self.reconstructible,

            "converged": self.converged,
            "halted": self.halted,

            "timestamp_ns": self.timestamp_ns,
        }


# ============================================================
# EVENT STREAM
# ============================================================

@dataclass
class HHSEventStream:
    """
    Canonical runtime event continuity stream.
    """

    runtime_id: str

    events: List[HHSEvent] = field(
        default_factory=list
    )

    stream_hash216: str = ""

    event_sequence: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # ========================================================
    # APPEND
    # ========================================================

    def append_event(
        self,
        event: HHSEvent
    ):

        self.event_sequence += 1

        event.sequence = self.event_sequence

        event.compute_hashes()

        self.events.append(event)

        self.compute_hash216()

    # ========================================================
    # HASHING
    # ========================================================

    def compute_hash216(self):

        payload = {
            "runtime_id": self.runtime_id,

            "events": [
                e.event_hash216
                for e in self.events
            ],

            "event_sequence": self.event_sequence,
        }

        self.stream_hash216 = _hash216(
            json.dumps(
                payload,
                sort_keys=True,
                default=str,
            )
        )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def serialize(self) -> Dict[str, Any]:

        self.compute_hash216()

        return {
            "runtime_id": self.runtime_id,

            "stream_hash216": self.stream_hash216,

            "event_sequence": self.event_sequence,

            "events": [
                e.serialize()
                for e in self.events
            ],
        }