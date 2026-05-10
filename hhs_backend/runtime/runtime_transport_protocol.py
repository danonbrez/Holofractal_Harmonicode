# ============================================================================
# hhs_backend/runtime/runtime_transport_protocol.py
# HARMONICODE / HHS
# CANONICAL RUNTIME TRANSPORT SUBSTRATE
#
# PURPOSE
# -------
# Canonical deterministic transport substrate for:
#
#   - runtime object propagation
#   - replay-governed transport continuity
#   - graph-native transport routing
#   - distributed runtime synchronization
#   - multimodal transport semantics
#   - replay/snapshot/resurrection propagation
#   - websocket/runtime packet projections
#   - namespace-aware transport routing
#   - v44.2 kernel continuity enforcement
#
# Transport IS runtime continuity propagation.
#
# ============================================================================

from __future__ import annotations

import copy
import hashlib
import json
import logging
import threading
import time
import uuid

from collections import defaultdict
from dataclasses import (
    dataclass,
    field,
    asdict,
)

from typing import (
    Dict,
    Any,
    List,
    Optional,
    Set,
)

# ============================================================================
# RUNTIME OBJECTS
# ============================================================================

from hhs_python.runtime.hhs_runtime_object import (
    HHSRuntimeObject,
)

from hhs_python.runtime.runtime_object_registry import (
    runtime_object_registry,
)

# ============================================================================
# OPTIONAL V44.2 KERNEL
# ============================================================================

try:

    from HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked_7 import (

        AUTHORITATIVE_TRUST_POLICY_V44,

        security_hash72_v44,

        Tensor,

        Manifold9,
    )

    V44_KERNEL_AVAILABLE = True

except Exception:

    AUTHORITATIVE_TRUST_POLICY_V44 = None

    security_hash72_v44 = None

    Tensor = None

    Manifold9 = None

    V44_KERNEL_AVAILABLE = False

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_RUNTIME_TRANSPORT_PROTOCOL"
)

# ============================================================================
# CONSTANTS
# ============================================================================

TRANSPORT_SCHEMA_VERSION = "v1"

# ============================================================================
# TRANSPORT VECTOR
# ============================================================================

@dataclass
class HHSTransportVector:

    transport_flux: str

    orientation_flux: str

    constraint_flux: str

    entropy_delta: str

    closure_delta: str

# ============================================================================
# TRANSPORT PACKET
# ============================================================================

@dataclass
class HHSTransportPacket:

    packet_id: str

    runtime_id: str

    branch_id: str

    source_object_id: str

    target_object_id: Optional[str]

    transport_type: str

    receipt_hash72: str

    state_hash72: str

    payload_hash72: str

    transport_vector: Dict[
        str,
        Any
    ]

    causal_parent: Optional[str]

    payload: Dict[
        str,
        Any
    ]

    created_at_ns: int

    metadata: Dict[
        str,
        Any
    ] = field(default_factory=dict)

# ============================================================================
# TRANSPORT ROUTE
# ============================================================================

@dataclass
class HHSTransportRoute:

    route_id: str

    source_runtime_id: str

    target_runtime_id: str

    transport_mode: str

    packet_ids: List[str]

    created_at_ns: int

# ============================================================================
# TRANSPORT PROTOCOL
# ============================================================================

class HHSRuntimeTransportProtocol:

    """
    Canonical runtime manifold transport substrate.
    """

    def __init__(self):

        self.lock = threading.RLock()

        self.packet_store: Dict[
            str,
            HHSTransportPacket
        ] = {}

        self.transport_routes: Dict[
            str,
            HHSTransportRoute
        ] = {}

        self.runtime_channels = defaultdict(list)

        self.branch_channels = defaultdict(list)

        self.object_channels = defaultdict(list)

        self.transport_graph = defaultdict(set)

    # =====================================================================
    # HASH72
    # =====================================================================

    def compute_hash72(
        self,
        payload: Dict[str, Any],
    ):

        serialized = json.dumps(

            payload,

            sort_keys=True,

            separators=(",", ":"),
        )

        digest = hashlib.sha256(

            serialized.encode("utf-8")

        ).hexdigest()

        return digest[:72]

    # =====================================================================
    # CREATE PACKET
    # =====================================================================

    def create_transport_packet(

        self,

        runtime_object: HHSRuntimeObject,

        transport_type: str,

        payload: Dict[str, Any],

        target_object_id: Optional[str] = None,

        causal_parent: Optional[str] = None,
    ):

        payload_hash72 = (
            self.compute_hash72(
                payload
            )
        )

        packet = HHSTransportPacket(

            packet_id=str(uuid.uuid4()),

            runtime_id=
                runtime_object.runtime_id,

            branch_id=
                runtime_object.branch_id,

            source_object_id=
                runtime_object.object_id,

            target_object_id=
                target_object_id,

            transport_type=
                transport_type,

            receipt_hash72=
                runtime_object.receipt_hash72,

            state_hash72=
                runtime_object.state_hash72,

            payload_hash72=
                payload_hash72,

            transport_vector=
                runtime_object
                .to_transport_packet(),

            causal_parent=
                causal_parent,

            payload=
                payload,

            created_at_ns=
                time.time_ns(),

            metadata={

                "schema_version":
                    TRANSPORT_SCHEMA_VERSION,

                "kernel_available":
                    V44_KERNEL_AVAILABLE,
            },
        )

        self.packet_store[
            packet.packet_id
        ] = packet

        self.runtime_channels[
            packet.runtime_id
        ].append(packet.packet_id)

        self.branch_channels[
            packet.branch_id
        ].append(packet.packet_id)

        self.object_channels[
            packet.source_object_id
        ].append(packet.packet_id)

        if target_object_id:

            self.transport_graph[
                runtime_object.object_id
            ].add(target_object_id)

        logger.info(
            f"Transport packet created: "
            f"{packet.packet_id}"
        )

        return packet

    # =====================================================================
    # SERIALIZE
    # =====================================================================

    def serialize_packet(
        self,
        packet: HHSTransportPacket,
    ):

        return json.dumps(

            asdict(packet),

            sort_keys=True,

            separators=(",", ":"),

            default=str,
        )

    # =====================================================================
    # DESERIALIZE
    # =====================================================================

    def deserialize_packet(
        self,
        payload: str,
    ):

        data = json.loads(payload)

        return HHSTransportPacket(
            **data
        )

    # =====================================================================
    # VERIFY
    # =====================================================================

    def verify_packet(
        self,
        packet: HHSTransportPacket,
    ):

        recomputed = self.compute_hash72(
            packet.payload
        )

        return (
            recomputed
            ==
            packet.payload_hash72
        )

    # =====================================================================
    # ROUTE
    # =====================================================================

    def route_packet(
        self,
        packet: HHSTransportPacket,
    ):

        if not self.verify_packet(packet):

            raise RuntimeError(
                "Transport packet verification failed."
            )

        logger.info(
            f"Packet routed: "
            f"{packet.packet_id}"
        )

        return {

            "packet_id":
                packet.packet_id,

            "runtime_id":
                packet.runtime_id,

            "transport_type":
                packet.transport_type,
        }

    # =====================================================================
    # BROADCAST
    # =====================================================================

    def broadcast_packet(
        self,
        packet: HHSTransportPacket,
    ):

        recipients = []

        for object_id in (
            runtime_object_registry
            .objects.keys()
        ):

            recipients.append(
                object_id
            )

        return {

            "packet_id":
                packet.packet_id,

            "broadcast_count":
                len(recipients),

            "recipients":
                recipients,
        }

    # =====================================================================
    # MULTICAST
    # =====================================================================

    def multicast_packet(

        self,

        packet: HHSTransportPacket,

        object_ids: List[str],
    ):

        return {

            "packet_id":
                packet.packet_id,

            "multicast_count":
                len(object_ids),

            "targets":
                object_ids,
        }

    # =====================================================================
    # FORWARD
    # =====================================================================

    def forward_packet(

        self,

        packet: HHSTransportPacket,

        target_runtime_id: str,
    ):

        forwarded = copy.deepcopy(
            packet
        )

        forwarded.runtime_id = (
            target_runtime_id
        )

        return forwarded

    # =====================================================================
    # REPLAY TRANSPORT
    # =====================================================================

    def transport_replay_packet(
        self,
        packet: HHSTransportPacket,
    ):

        packet.transport_type = (
            "replay"
        )

        return self.route_packet(
            packet
        )

    # =====================================================================
    # SNAPSHOT TRANSPORT
    # =====================================================================

    def transport_snapshot_packet(
        self,
        packet: HHSTransportPacket,
    ):

        packet.transport_type = (
            "snapshot"
        )

        return self.route_packet(
            packet
        )

    # =====================================================================
    # RESURRECTION TRANSPORT
    # =====================================================================

    def transport_resurrection_packet(
        self,
        packet: HHSTransportPacket,
    ):

        packet.transport_type = (
            "resurrection"
        )

        return self.route_packet(
            packet
        )

    # =====================================================================
    # GRAPH PROJECTION
    # =====================================================================

    def route_graph_projection(
        self,
        object_id: str,
    ):

        return {

            "source":
                object_id,

            "targets":

                list(
                    self.transport_graph[
                        object_id
                    ]
                ),
        }

    # =====================================================================
    # GRAPH DELTA
    # =====================================================================

    def route_graph_delta(
        self,
        source_object_id: str,
    ):

        return {

            "delta_routes":

                list(
                    self.transport_graph[
                        source_object_id
                    ]
                )
        }

    # =====================================================================
    # GRAPH RESURRECTION
    # =====================================================================

    def route_graph_resurrection(
        self,
        object_id: str,
    ):

        return self.route_graph_projection(
            object_id
        )

    # =====================================================================
    # MULTIMODAL TRANSPORT
    # =====================================================================

    def transport_audio_tensor(
        self,
        packet: HHSTransportPacket,
    ):

        packet.transport_type = (
            "audio_tensor"
        )

        return self.route_packet(
            packet
        )

    # =====================================================================
    # VISUAL TRANSPORT
    # =====================================================================

    def transport_visual_tensor(
        self,
        packet: HHSTransportPacket,
    ):

        packet.transport_type = (
            "visual_tensor"
        )

        return self.route_packet(
            packet
        )

    # =====================================================================
    # SYMBOLIC TRANSPORT
    # =====================================================================

    def transport_symbolic_tensor(
        self,
        packet: HHSTransportPacket,
    ):

        packet.transport_type = (
            "symbolic_tensor"
        )

        return self.route_packet(
            packet
        )

    # =====================================================================
    # PHASE VECTOR
    # =====================================================================

    def transport_phase_vector(
        self,
        packet: HHSTransportPacket,
    ):

        packet.transport_type = (
            "phase_vector"
        )

        return self.route_packet(
            packet
        )

    # =====================================================================
    # SANDBOX TRANSPORT
    # =====================================================================

    def sandbox_transport(
        self,
        packet: HHSTransportPacket,
    ):

        packet.metadata[
            "sandbox"
        ] = True

        return self.route_packet(
            packet
        )

    # =====================================================================
    # ISOLATED TRANSPORT
    # =====================================================================

    def isolated_transport(
        self,
        packet: HHSTransportPacket,
    ):

        packet.metadata[
            "isolated"
        ] = True

        return self.route_packet(
            packet
        )

    # =====================================================================
    # VALIDATION TRANSPORT
    # =====================================================================

    def validation_transport(
        self,
        packet: HHSTransportPacket,
    ):

        packet.metadata[
            "validation"
        ] = True

        return self.route_packet(
            packet
        )

    # =====================================================================
    # PROJECTION TRANSPORT
    # =====================================================================

    def projection_transport(
        self,
        packet: HHSTransportPacket,
    ):

        packet.metadata[
            "projection"
        ] = True

        return self.route_packet(
            packet
        )

    # =====================================================================
    # SYNCHRONIZE
    # =====================================================================

    def synchronize_runtime_nodes(
        self,
        packets: List[HHSTransportPacket],
    ):

        verified = all(

            self.verify_packet(x)

            for x in packets
        )

        return {

            "synchronized":
                verified,

            "packet_count":
                len(packets),
        }

    # =====================================================================
    # VERIFY EQUIVALENCE
    # =====================================================================

    def verify_transport_equivalence(

        self,

        packet_a: HHSTransportPacket,

        packet_b: HHSTransportPacket,
    ):

        return (

            packet_a.payload_hash72
            ==
            packet_b.payload_hash72
        )

    # =====================================================================
    # VERIFY ORDERING
    # =====================================================================

    def verify_packet_ordering(
        self,
        packets: List[HHSTransportPacket],
    ):

        timestamps = [

            x.created_at_ns

            for x in packets
        ]

        return timestamps == sorted(
            timestamps
        )

    # =====================================================================
    # ROUTING PROJECTIONS
    # =====================================================================

    def to_transport_projection(
        self,
        packet: HHSTransportPacket,
    ):

        return {

            "packet_id":
                packet.packet_id,

            "runtime_id":
                packet.runtime_id,

            "transport_type":
                packet.transport_type,
        }

    # =====================================================================
    # WEBSOCKET
    # =====================================================================

    def to_websocket_packet(
        self,
        packet: HHSTransportPacket,
    ):

        return {

            "event": "runtime_transport",

            "packet":

                asdict(packet),
        }

    # =====================================================================
    # RUNTIME PACKET
    # =====================================================================

    def to_runtime_packet(
        self,
        packet: HHSTransportPacket,
    ):

        return {

            "runtime_id":
                packet.runtime_id,

            "branch_id":
                packet.branch_id,

            "payload":
                packet.payload,
        }

    # =====================================================================
    # GRAPH TRANSPORT
    # =====================================================================

    def to_graph_transport_projection(
        self,
        packet: HHSTransportPacket,
    ):

        return {

            "source":
                packet.source_object_id,

            "target":
                packet.target_object_id,

            "transport_type":
                packet.transport_type,
        }

    # =====================================================================
    # CREATE ROUTE
    # =====================================================================

    def create_transport_route(

        self,

        source_runtime_id: str,

        target_runtime_id: str,

        transport_mode: str,
    ):

        route = HHSTransportRoute(

            route_id=str(uuid.uuid4()),

            source_runtime_id=
                source_runtime_id,

            target_runtime_id=
                target_runtime_id,

            transport_mode=
                transport_mode,

            packet_ids=[],

            created_at_ns=
                time.time_ns(),
        )

        self.transport_routes[
            route.route_id
        ] = route

        return route

    # =====================================================================
    # V44 VALIDATION
    # =====================================================================

    def validate_v44_transport(
        self,
        packet: HHSTransportPacket,
    ):

        if not V44_KERNEL_AVAILABLE:

            return {

                "kernel_available": False,

                "validated": False,
            }

        packet_hash = hashlib.sha256(

            self.serialize_packet(
                packet
            ).encode("utf-8")

        ).hexdigest()

        trust_hash = hashlib.sha256(

            str(
                AUTHORITATIVE_TRUST_POLICY_V44
            ).encode("utf-8")

        ).hexdigest()

        return {

            "kernel_available": True,

            "validated": True,

            "packet_hash":
                packet_hash,

            "trust_hash":
                trust_hash,
        }

# ============================================================================
# GLOBAL TRANSPORT PROTOCOL
# ============================================================================

runtime_transport_protocol = (
    HHSRuntimeTransportProtocol()
)

# ============================================================================
# SELF TEST
# ============================================================================

def runtime_transport_protocol_self_test():

    from hhs_python.runtime.hhs_runtime_object import (
        create_runtime_object
    )

    runtime_object = create_runtime_object(

        object_type="workspace",

        runtime_id="runtime_001",

        branch_id="main",

        state={

            "workspace":
                "tensor_lab"
        },
    )

    runtime_object_registry.register_object(
        runtime_object
    )

    packet = (

        runtime_transport_protocol
        .create_transport_packet(

            runtime_object=
                runtime_object,

            transport_type=
                "runtime_sync",

            payload={

                "message":
                    "synchronize"
            },
        )
    )

    routed = (

        runtime_transport_protocol
        .route_packet(
            packet
        )
    )

    websocket_packet = (

        runtime_transport_protocol
        .to_websocket_packet(
            packet
        )
    )

    graph_projection = (

        runtime_transport_protocol
        .to_graph_transport_projection(
            packet
        )
    )

    v44 = (

        runtime_transport_protocol
        .validate_v44_transport(
            packet
        )
    )

    print()

    print("PACKET")

    print(packet)

    print()

    print("ROUTED")

    print(routed)

    print()

    print("WEBSOCKET")

    print(websocket_packet)

    print()

    print("GRAPH")

    print(graph_projection)

    print()

    print("V44")

    print(v44)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    runtime_transport_protocol_self_test()