# hhs_python/runtime/hhs_runtime_state.py
#
# HHS / HARMONICODE
# Canonical Runtime State Authority
#
# Runtime Principle:
#
#   runtime state
#   =
#   canonical deterministic runtime continuity
#
# NOT:
#
#   temporary execution snapshots
#

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import hashlib
import json
import time
import copy


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
# TENSOR81
# ============================================================

@dataclass
class HHSTensor81Cell:

    value: int = 0

    phase: int = 0
    occupied: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class HHSTensor81State:

    cells: List[HHSTensor81Cell] = field(
        default_factory=lambda: [
            HHSTensor81Cell()
            for _ in range(81)
        ]
    )

    topology_hash216: str = ""

    def compute_hash216(self) -> str:

        payload = {
            "cells": [
                {
                    "value": c.value,
                    "phase": c.phase,
                    "occupied": c.occupied,
                }
                for c in self.cells
            ]
        }

        self.topology_hash216 = _hash216(
            json.dumps(payload, sort_keys=True)
        )

        return self.topology_hash216


# ============================================================
# RECEIPT
# ============================================================

@dataclass
class HHSRuntimeReceipt:

    receipt_hash72: str = ""
    receipt_hash216: str = ""

    state_hash72: str = ""
    state_hash216: str = ""

    witness_flags: int = 0

    transport_flux: float = 0.0
    orientation_flux: float = 0.0
    constraint_flux: float = 0.0

    converged: bool = False
    halted: bool = False

    timestamp_ns: int = field(
        default_factory=time.time_ns
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def compute_hashes(self):

        payload = json.dumps(
            asdict(self),
            sort_keys=True,
            default=str,
        )

        self.receipt_hash72 = _hash72(payload)
        self.receipt_hash216 = _hash216(payload)


# ============================================================
# TRANSPORT
# ============================================================

@dataclass
class HHSTransportState:

    transport_hash216: str = ""

    transport_flux: float = 0.0
    orientation_flux: float = 0.0
    constraint_flux: float = 0.0

    synchronized: bool = False
    replayable: bool = False
    reconstructible: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def compute_hash216(self):

        self.transport_hash216 = _hash216(
            json.dumps(
                asdict(self),
                sort_keys=True,
                default=str,
            )
        )

        return self.transport_hash216


# ============================================================
# GRAPH STATE
# ============================================================

@dataclass
class HHSGraphState:

    graph_hash216: str = ""

    node_count: int = 0
    edge_count: int = 0

    topology_sequence: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def compute_hash216(self):

        self.graph_hash216 = _hash216(
            json.dumps(
                asdict(self),
                sort_keys=True,
                default=str,
            )
        )

        return self.graph_hash216


# ============================================================
# EVENT STATE
# ============================================================

@dataclass
class HHSEventState:

    event_sequence: int = 0

    last_event_hash216: str = ""

    websocket_synchronized: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def compute_hash216(self):

        return _hash216(
            json.dumps(
                asdict(self),
                sort_keys=True,
                default=str,
            )
        )


# ============================================================
# RUNTIME OBJECT
# ============================================================

@dataclass
class HHSRuntimeObject:

    object_id: str

    object_type: str

    state_hash216: str = ""

    replayable: bool = False
    reconstructible: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def compute_hash216(self):

        self.state_hash216 = _hash216(
            json.dumps(
                asdict(self),
                sort_keys=True,
                default=str,
            )
        )

        return self.state_hash216


# ============================================================
# CANONICAL RUNTIME STATE
# ============================================================

@dataclass
class HHSRuntimeState:
    """
    Canonical deterministic runtime state authority.

    ALL runtime layers serialize through this object.
    """

    runtime_id: str

    state_hash72: str = ""
    state_hash216: str = ""

    receipt_hash72: str = ""
    receipt_hash216: str = ""

    transport_hash216: str = ""
    projection_hash216: str = ""
    graph_hash216: str = ""

    tensor81_state: HHSTensor81State = field(
        default_factory=HHSTensor81State
    )

    transport_state: HHSTransportState = field(
        default_factory=HHSTransportState
    )

    graph_state: HHSGraphState = field(
        default_factory=HHSGraphState
    )

    event_state: HHSEventState = field(
        default_factory=HHSEventState
    )

    receipt: HHSRuntimeReceipt = field(
        default_factory=HHSRuntimeReceipt
    )

    runtime_objects: Dict[
        str,
        HHSRuntimeObject
    ] = field(default_factory=dict)

    witness_flags: int = 0

    transport_flux: float = 0.0
    orientation_flux: float = 0.0
    constraint_flux: float = 0.0

    branch_id: str = "root"
    parent_branch_id: Optional[str] = None

    converged: bool = False
    halted: bool = False

    replayable: bool = False
    reconstructible: bool = False

    step: int = 0
    epoch: int = 0

    timestamp_ns: int = field(
        default_factory=time.time_ns
    )

    receipt_lineage: List[str] = field(
        default_factory=list
    )

    replay_lineage: List[str] = field(
        default_factory=list
    )

    event_sequence: int = 0
    graph_sequence: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # ========================================================
    # HASHING
    # ========================================================

    def compute_hashes(self):

        self.tensor81_state.compute_hash216()

        self.transport_hash216 = (
            self.transport_state.compute_hash216()
        )

        self.graph_hash216 = (
            self.graph_state.compute_hash216()
        )

        self.receipt.compute_hashes()

        payload = {
            "runtime_id": self.runtime_id,

            "tensor81": (
                self.tensor81_state.topology_hash216
            ),

            "transport": self.transport_hash216,

            "graph": self.graph_hash216,

            "receipt": (
                self.receipt.receipt_hash216
            ),

            "objects": sorted(
                [
                    obj.compute_hash216()
                    for obj in (
                        self.runtime_objects.values()
                    )
                ]
            ),

            "branch_id": self.branch_id,
            "parent_branch_id": self.parent_branch_id,

            "step": self.step,
            "epoch": self.epoch,

            "event_sequence": self.event_sequence,
            "graph_sequence": self.graph_sequence,

            "converged": self.converged,
            "halted": self.halted,

            "replayable": self.replayable,
            "reconstructible": self.reconstructible,
        }

        serialized = json.dumps(
            payload,
            sort_keys=True,
            default=str,
        )

        self.state_hash72 = _hash72(
            serialized
        )

        self.state_hash216 = _hash216(
            serialized
        )

        self.receipt_hash72 = (
            self.receipt.receipt_hash72
        )

        self.receipt_hash216 = (
            self.receipt.receipt_hash216
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
    ) -> "HHSRuntimeState":

        return cls(**copy.deepcopy(payload))

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt_summary(self) -> Dict[str, Any]:

        self.compute_hashes()

        return {
            "runtime_id": self.runtime_id,

            "state_hash72": self.state_hash72,
            "state_hash216": self.state_hash216,

            "receipt_hash72": self.receipt_hash72,
            "receipt_hash216": self.receipt_hash216,

            "branch_id": self.branch_id,

            "step": self.step,
            "epoch": self.epoch,

            "converged": self.converged,
            "halted": self.halted,

            "replayable": self.replayable,
            "reconstructible": self.reconstructible,

            "timestamp_ns": self.timestamp_ns,
        }

    # ========================================================
    # LINEAGE
    # ========================================================

    def commit_receipt(self):

        self.compute_hashes()

        self.receipt_lineage.append(
            self.receipt_hash216
        )

    def commit_replay(self):

        self.compute_hashes()

        self.replay_lineage.append(
            self.state_hash216
        )

    # ========================================================
    # OBJECT MANAGEMENT
    # ========================================================

    def add_runtime_object(
        self,
        obj: HHSRuntimeObject
    ):

        obj.compute_hash216()

        self.runtime_objects[
            obj.object_id
        ] = obj

    def remove_runtime_object(
        self,
        object_id: str
    ):

        if object_id in self.runtime_objects:
            del self.runtime_objects[
                object_id
            ]

    # ========================================================
    # SNAPSHOT / REPLAY
    # ========================================================

    def snapshot(self) -> Dict[str, Any]:

        return self.serialize()

    def restore(
        self,
        snapshot_payload: Dict[str, Any]
    ):

        restored = HHSRuntimeState.deserialize(
            snapshot_payload
        )

        self.__dict__.update(
            restored.__dict__
        )

    # ========================================================
    # EVENTS
    # ========================================================

    def emit_event(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        self.event_sequence += 1

        event_payload = {
            "runtime_id": self.runtime_id,

            "event_sequence": self.event_sequence,

            "event_type": event_type,

            "state_hash216": self.state_hash216,

            "receipt_hash216": self.receipt_hash216,

            "payload": payload,

            "timestamp_ns": time.time_ns(),
        }

        self.event_state.last_event_hash216 = (
            _hash216(
                json.dumps(
                    event_payload,
                    sort_keys=True,
                    default=str,
                )
            )
        )

        return event_payload