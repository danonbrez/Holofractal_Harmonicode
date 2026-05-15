from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import time

# =========================================================
# Event Types
# =========================================================

EVENT_RUNTIME = "runtime"

EVENT_REPLAY = "replay"

EVENT_GRAPH = "graph"

EVENT_TRANSPORT = "transport"

EVENT_RECEIPT = "receipt"

EVENT_CERTIFICATION = "certification"

# =========================================================
# Base Event
# =========================================================

@dataclass(slots=True)
class HHSEvent:

    event_type: str

    timestamp_ns: int = field(

        default_factory=time.time_ns
    )

    runtime_id: str = (
        "hhs_runtime"
    )

    sequence_id: int = 0

    authority: str = (
        "runtime_authoritative"
    )

    payload: Dict[str, Any] = field(

        default_factory=dict
    )

    # -----------------------------------------------------

    def to_dict(
        self
    ) -> Dict[str, Any]:

        return asdict(self)

# =========================================================
# Runtime Event
# =========================================================

@dataclass(slots=True)
class RuntimeEventPayload:

    operation: str

    runtime_status: str

    step: int

    phase: str

    uptime: float

    receipt_hash72:
        Optional[str] = None

    source_hash72:
        Optional[str] = None

    closure_state: str = "stable"

    transport_flux: float = 0.0

    orientation_flux: float = 0.0

    constraint_flux: float = 0.0

    entropy_delta: float = 0.0

# ---------------------------------------------------------

@dataclass(slots=True)
class RuntimeEvent(HHSEvent):

    EVENT_TYPE = EVENT_RUNTIME

    @classmethod
    def build(

        cls,

        runtime_payload:
            RuntimeEventPayload,

        *,

        sequence_id: int = 0

    ) -> "RuntimeEvent":

        return cls(

            event_type=
                cls.EVENT_TYPE,

            sequence_id=
                sequence_id,

            payload=
                asdict(
                    runtime_payload
                )
        )

# =========================================================
# Replay Event
# =========================================================

@dataclass(slots=True)
class ReplayEventPayload:

    replay_tick: int

    replay_status: str

    timeline_position: int

    branch_id: str = "main"

    replay_mode: str = "live"

    replay_hash72:
        Optional[str] = None

# ---------------------------------------------------------

@dataclass(slots=True)
class ReplayEvent(HHSEvent):

    EVENT_TYPE = EVENT_REPLAY

    @classmethod
    def build(

        cls,

        replay_payload:
            ReplayEventPayload,

        *,

        sequence_id: int = 0

    ) -> "ReplayEvent":

        return cls(

            event_type=
                cls.EVENT_TYPE,

            sequence_id=
                sequence_id,

            payload=
                asdict(
                    replay_payload
                )
        )

# =========================================================
# Graph Event
# =========================================================

@dataclass(slots=True)
class GraphNode:

    node_id: str

    node_type: str

    x: float

    y: float

    z: float

    authority: str = "runtime"

# ---------------------------------------------------------

@dataclass(slots=True)
class GraphEdge:

    source: str

    target: str

    edge_type: str

# ---------------------------------------------------------

@dataclass(slots=True)
class GraphEventPayload:

    graph_tick: int

    projection: str

    nodes: List[GraphNode] = field(

        default_factory=list
    )

    edges: List[GraphEdge] = field(

        default_factory=list
    )

# ---------------------------------------------------------

@dataclass(slots=True)
class GraphEvent(HHSEvent):

    EVENT_TYPE = EVENT_GRAPH

    @classmethod
    def build(

        cls,

        graph_payload:
            GraphEventPayload,

        *,

        sequence_id: int = 0

    ) -> "GraphEvent":

        return cls(

            event_type=
                cls.EVENT_TYPE,

            sequence_id=
                sequence_id,

            payload={

                "graph_tick":
                    graph_payload.graph_tick,

                "projection":
                    graph_payload.projection,

                "nodes": [

                    asdict(node)

                    for node
                    in graph_payload.nodes
                ],

                "edges": [

                    asdict(edge)

                    for edge
                    in graph_payload.edges
                ]
            }
        )

# =========================================================
# Transport Event
# =========================================================

@dataclass(slots=True)
class TransportEventPayload:

    transport_tick: int

    transport_flux: float

    continuity: str

    throughput: float

    orientation_phase: float = 0.0

    closure_pressure: float = 0.0

# ---------------------------------------------------------

@dataclass(slots=True)
class TransportEvent(HHSEvent):

    EVENT_TYPE = EVENT_TRANSPORT

    @classmethod
    def build(

        cls,

        transport_payload:
            TransportEventPayload,

        *,

        sequence_id: int = 0

    ) -> "TransportEvent":

        return cls(

            event_type=
                cls.EVENT_TYPE,

            sequence_id=
                sequence_id,

            payload=
                asdict(
                    transport_payload
                )
        )

# =========================================================
# Receipt Event
# =========================================================

@dataclass(slots=True)
class ReceiptEventPayload:

    receipt_hash72: str

    source_hash72: str

    operation: str

    closure_class: str

    witness_flags: int

    converged: bool

    halted: bool

# ---------------------------------------------------------

@dataclass(slots=True)
class ReceiptEvent(HHSEvent):

    EVENT_TYPE = EVENT_RECEIPT

    @classmethod
    def build(

        cls,

        receipt_payload:
            ReceiptEventPayload,

        *,

        sequence_id: int = 0

    ) -> "ReceiptEvent":

        return cls(

            event_type=
                cls.EVENT_TYPE,

            sequence_id=
                sequence_id,

            payload=
                asdict(
                    receipt_payload
                )
        )

# =========================================================
# Certification Event
# =========================================================

@dataclass(slots=True)
class CertificationEventPayload:

    certification_status: str

    authority_level: str

    passed: bool

    certification_hash72:
        Optional[str] = None

# ---------------------------------------------------------

@dataclass(slots=True)
class CertificationEvent(HHSEvent):

    EVENT_TYPE = EVENT_CERTIFICATION

    @classmethod
    def build(

        cls,

        certification_payload:
            CertificationEventPayload,

        *,

        sequence_id: int = 0

    ) -> "CertificationEvent":

        return cls(

            event_type=
                cls.EVENT_TYPE,

            sequence_id=
                sequence_id,

            payload=
                asdict(
                    certification_payload
                )
        )

# =========================================================
# Decoder
# =========================================================

EVENT_CLASS_REGISTRY = {

    EVENT_RUNTIME:
        RuntimeEvent,

    EVENT_REPLAY:
        ReplayEvent,

    EVENT_GRAPH:
        GraphEvent,

    EVENT_TRANSPORT:
        TransportEvent,

    EVENT_RECEIPT:
        ReceiptEvent,

    EVENT_CERTIFICATION:
        CertificationEvent
}

# ---------------------------------------------------------

def decode_event(
    payload: Dict[str, Any]
) -> HHSEvent:

    event_type = payload.get(
        "event_type"
    )

    if not event_type:

        raise ValueError(

            "missing event_type"
        )

    event_class = (
        EVENT_CLASS_REGISTRY
            .get(event_type)
    )

    if not event_class:

        raise ValueError(

            f"unknown event_type: "
            f"{event_type}"
        )

    return event_class(

        event_type=
            payload.get(
                "event_type"
            ),

        timestamp_ns=
            payload.get(
                "timestamp_ns",
                time.time_ns()
            ),

        runtime_id=
            payload.get(
                "runtime_id",
                "hhs_runtime"
            ),

        sequence_id=
            payload.get(
                "sequence_id",
                0
            ),

        authority=
            payload.get(
                "authority",
                "runtime_authoritative"
            ),

        payload=
            payload.get(
                "payload",
                {}
            )
    )

# =========================================================
# Schema Registry
# =========================================================

EVENT_SCHEMA_REGISTRY = {

    EVENT_RUNTIME:
        RuntimeEvent,

    EVENT_REPLAY:
        ReplayEvent,

    EVENT_GRAPH:
        GraphEvent,

    EVENT_TRANSPORT:
        TransportEvent,

    EVENT_RECEIPT:
        ReceiptEvent,

    EVENT_CERTIFICATION:
        CertificationEvent
}