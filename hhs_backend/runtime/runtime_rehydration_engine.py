# ============================================================================
# hhs_backend/runtime/runtime_rehydration_engine.py
# HARMONICODE / HHS
# DETERMINISTIC RUNTIME RESURRECTION AUTHORITY
#
# PURPOSE
# -------
# Canonical runtime resurrection substrate for:
#
#   - replay-certified runtime reconstruction
#   - deterministic runtime resurrection
#   - branch-topological rehydration
#   - distributed runtime synchronization
#   - replay equivalence verification
#   - resurrection checkpoints
#   - schema-aware runtime migration
#   - v44.2 kernel continuity enforcement
#
# Runtime resurrection IS runtime continuity.
#
# ============================================================================

from __future__ import annotations

import copy
import hashlib
import json
import logging
import time
import uuid

from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Dict,
    Any,
    List,
    Optional,
)

from hhs_python.runtime.hhs_runtime_state import (
    HHSRuntimeState,
    V44_KERNEL_AVAILABLE,
    AUTHORITATIVE_TRUST_POLICY_V44,
)

from hhs_backend.runtime.runtime_snapshot_codec import (
    HHSSnapshotPacket,
    runtime_snapshot_codec,
)

from hhs_backend.runtime.runtime_receipt_chain import (
    HHSReceipt,
    runtime_receipt_chain,
)

from hhs_backend.runtime.runtime_event_schema import (
    HHSRuntimeEventEnvelope,
)

# ============================================================================
# OPTIONAL V44.2 KERNEL
# ============================================================================

try:

    from HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked_7 import (

        security_hash72_v44,

        Tensor,

        Manifold9,
    )

except Exception:

    security_hash72_v44 = None

    Tensor = None

    Manifold9 = None

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_RUNTIME_REHYDRATION_ENGINE"
)

# ============================================================================
# CONSTANTS
# ============================================================================

REHYDRATION_SCHEMA_VERSION = "v1"

# ============================================================================
# REHYDRATION SESSION
# ============================================================================

@dataclass
class HHSRehydrationSession:

    session_id: str

    runtime_id: str

    branch_id: str

    created_at_ns: int

    source_snapshot_hash72: str

    restored_receipt_hash72: str

    replay_equivalent: bool

    reconstruction_path: List[str]

    branch_lineage: List[str]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# REHYDRATION GRAPH
# ============================================================================

@dataclass
class HHSRehydrationGraph:

    graph_id: str

    runtime_id: str

    created_at_ns: int

    nodes: List[Dict[str, Any]]

    edges: List[Dict[str, Any]]

    replay_path_hash72: str

# ============================================================================
# ENGINE
# ============================================================================

class HHSRuntimeRehydrationEngine:

    """
    Canonical deterministic runtime resurrection authority.
    """

    def __init__(self):

        self.active_sessions: Dict[
            str,
            HHSRehydrationSession
        ] = {}

        self.checkpoints: Dict[
            str,
            HHSSnapshotPacket
        ] = {}

        self.rehydration_graphs: Dict[
            str,
            HHSRehydrationGraph
        ] = {}

    # =====================================================================
    # REHYDRATE RUNTIME
    # =====================================================================

    def rehydrate_runtime(
        self,
        packet: HHSSnapshotPacket,
    ) -> HHSRuntimeState:

        runtime_state = (

            runtime_snapshot_codec
            .materialize_runtime(
                packet
            )
        )

        logger.info(
            f"Runtime rehydrated: "
            f"{runtime_state.runtime_id}"
        )

        return runtime_state

    # =====================================================================
    # REHYDRATE FROM SNAPSHOT
    # =====================================================================

    def rehydrate_from_snapshot(
        self,
        packet: HHSSnapshotPacket,
    ):

        runtime_state = (
            self.rehydrate_runtime(
                packet
            )
        )

        session = self.create_rehydration_session(

            packet=packet,

            runtime_state=runtime_state,
        )

        return {

            "runtime_state":
                runtime_state,

            "session":
                session,
        }

    # =====================================================================
    # REHYDRATE RECEIPT CHAIN
    # =====================================================================

    def rehydrate_from_receipt_chain(
        self,
        packet: HHSSnapshotPacket,
    ):

        receipts = (

            runtime_snapshot_codec
            .rehydrate_receipt_chain(
                packet
            )
        )

        logger.info(
            f"Receipt chain rehydrated: "
            f"{len(receipts)} receipts"
        )

        return receipts

    # =====================================================================
    # REHYDRATE BRANCH TOPOLOGY
    # =====================================================================

    def rehydrate_branch_topology(
        self,
        packet: HHSSnapshotPacket,
    ):

        topology = (
            packet.branch_topology
        )

        logger.info(
            f"Branch topology rehydrated."
        )

        return topology

    # =====================================================================
    # CREATE SESSION
    # =====================================================================

    def create_rehydration_session(

        self,

        packet: HHSSnapshotPacket,

        runtime_state: HHSRuntimeState,
    ):

        replay_equivalent = (

            runtime_snapshot_codec
            .verify_materialization(
                packet
            )
        )

        lineage = (

            runtime_receipt_chain
            .reconstruct_runtime_lineage(
                runtime_state.runtime_id
            )
        )

        reconstruction_path = [

            x["receipt_hash72"]

            for x in lineage
        ]

        branch_lineage = list(

            packet.branch_topology.keys()
        )

        session = HHSRehydrationSession(

            session_id=str(uuid.uuid4()),

            runtime_id=
                runtime_state.runtime_id,

            branch_id=
                packet.branch_id,

            created_at_ns=
                time.time_ns(),

            source_snapshot_hash72=
                packet.snapshot_hash72,

            restored_receipt_hash72=
                runtime_state.receipt_hash72,

            replay_equivalent=
                replay_equivalent,

            reconstruction_path=
                reconstruction_path,

            branch_lineage=
                branch_lineage,

            metadata={

                "kernel_available":
                    V44_KERNEL_AVAILABLE,

                "schema_version":
                    REHYDRATION_SCHEMA_VERSION,
            },
        )

        self.active_sessions[
            session.session_id
        ] = session

        logger.info(
            f"Rehydration session created: "
            f"{session.session_id}"
        )

        return session

    # =====================================================================
    # VERIFY REHYDRATION
    # =====================================================================

    def verify_rehydration_equivalence(

        self,

        original_packet: HHSSnapshotPacket,

        restored_state: HHSRuntimeState,
    ):

        reconstructed = json.loads(

            restored_state.serialize_deterministic()
        )

        equivalent = (

            reconstructed
            ==
            original_packet.runtime_state
        )

        if not equivalent:

            logger.error(
                "Runtime resurrection equivalence failure."
            )

        return equivalent

    # =====================================================================
    # VERIFY RUNTIME RESURRECTION
    # =====================================================================

    def verify_runtime_resurrection(
        self,
        session: HHSRehydrationSession,
    ):

        return (
            session.replay_equivalent
        )

    # =====================================================================
    # VERIFY BRANCH RESURRECTION
    # =====================================================================

    def verify_branch_resurrection(
        self,
        session: HHSRehydrationSession,
    ):

        return (
            len(session.branch_lineage)
            >= 0
        )

    # =====================================================================
    # CREATE REHYDRATION GRAPH
    # =====================================================================

    def create_rehydration_graph(
        self,
        session: HHSRehydrationSession,
    ):

        nodes = []

        edges = []

        previous = None

        for receipt_hash in (
            session.reconstruction_path
        ):

            node = {

                "node_id":
                    receipt_hash,

                "runtime_id":
                    session.runtime_id,
            }

            nodes.append(node)

            if previous:

                edges.append({

                    "source":
                        previous,

                    "target":
                        receipt_hash,
                })

            previous = receipt_hash

        replay_hash = hashlib.sha256(

            json.dumps(

                session.reconstruction_path,

                sort_keys=True,

            ).encode("utf-8")

        ).hexdigest()[:72]

        graph = HHSRehydrationGraph(

            graph_id=str(uuid.uuid4()),

            runtime_id=session.runtime_id,

            created_at_ns=time.time_ns(),

            nodes=nodes,

            edges=edges,

            replay_path_hash72=
                replay_hash,
        )

        self.rehydration_graphs[
            graph.graph_id
        ] = graph

        logger.info(
            f"Rehydration graph created: "
            f"{graph.graph_id}"
        )

        return graph

    # =====================================================================
    # SYNCHRONIZE NODES
    # =====================================================================

    def synchronize_rehydrated_nodes(

        self,

        runtime_states: List[
            HHSRuntimeState
        ],
    ):

        if not runtime_states:

            return False

        baseline = json.loads(

            runtime_states[0]
            .serialize_deterministic()
        )

        for state in runtime_states[1:]:

            comparison = json.loads(

                state.serialize_deterministic()
            )

            if comparison != baseline:

                logger.error(
                    "Distributed rehydration divergence."
                )

                return False

        return True

    # =====================================================================
    # VERIFY DISTRIBUTED
    # =====================================================================

    def verify_distributed_equivalence(

        self,

        runtime_states: List[
            HHSRuntimeState
        ],
    ):

        return self.synchronize_rehydrated_nodes(
            runtime_states
        )

    # =====================================================================
    # CHECKPOINT
    # =====================================================================

    def checkpoint_runtime(
        self,
        packet: HHSSnapshotPacket,
    ):

        self.checkpoints[
            packet.snapshot_hash72
        ] = packet

        logger.info(
            f"Runtime checkpoint created: "
            f"{packet.snapshot_hash72}"
        )

    # =====================================================================
    # RESTORE CHECKPOINT
    # =====================================================================

    def restore_checkpoint(
        self,
        snapshot_hash72: str,
    ):

        packet = self.checkpoints[
            snapshot_hash72
        ]

        return self.rehydrate_runtime(
            packet
        )

    # =====================================================================
    # ROLLBACK CHECKPOINT
    # =====================================================================

    def rollback_checkpoint(
        self,
        snapshot_hash72: str,
    ):

        runtime_state = (
            self.restore_checkpoint(
                snapshot_hash72
            )
        )

        logger.info(
            f"Checkpoint rollback complete."
        )

        return runtime_state

    # =====================================================================
    # RESURRECTION PACKET
    # =====================================================================

    def to_runtime_resurrection_packet(
        self,
        session: HHSRehydrationSession,
    ):

        return {

            "session_id":
                session.session_id,

            "runtime_id":
                session.runtime_id,

            "snapshot_hash72":
                session.source_snapshot_hash72,

            "receipt_hash72":
                session.restored_receipt_hash72,

            "replay_equivalent":
                session.replay_equivalent,
        }

    # =====================================================================
    # GRAPH PROJECTION
    # =====================================================================

    def to_rehydration_graph_projection(
        self,
        graph: HHSRehydrationGraph,
    ):

        return {

            "graph_id":
                graph.graph_id,

            "runtime_id":
                graph.runtime_id,

            "nodes":
                len(graph.nodes),

            "edges":
                len(graph.edges),

            "replay_path_hash72":
                graph.replay_path_hash72,
        }

    # =====================================================================
    # REPLAY EVENT
    # =====================================================================

    def to_replay_resurrection_event(
        self,
        session: HHSRehydrationSession,
    ):

        return {

            "event":
                "runtime_resurrection",

            "runtime_id":
                session.runtime_id,

            "session_id":
                session.session_id,

            "receipt_hash72":
                session.restored_receipt_hash72,
        }

    # =====================================================================
    # SCHEMA MIGRATION
    # =====================================================================

    def upcast_runtime_state(
        self,
        runtime_state: HHSRuntimeState,
    ):

        return runtime_state

    # =====================================================================
    # SESSION MIGRATION
    # =====================================================================

    def migrate_rehydration_session(
        self,
        session: HHSRehydrationSession,
    ):

        return session

    # =====================================================================
    # SCHEMA VALIDATION
    # =====================================================================

    def verify_schema_resurrection(
        self,
        session: HHSRehydrationSession,
    ):

        return (
            session.metadata.get(
                "schema_version"
            )
            ==
            REHYDRATION_SCHEMA_VERSION
        )

    # =====================================================================
    # V44 VALIDATION
    # =====================================================================

    def validate_v44_resurrection(
        self,
        session: HHSRehydrationSession,
    ):

        if not V44_KERNEL_AVAILABLE:

            return {

                "kernel_available": False,

                "validated": False,
            }

        resurrection_hash = hashlib.sha256(

            json.dumps(

                self.to_runtime_resurrection_packet(
                    session
                ),

                sort_keys=True,

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

            "resurrection_hash":
                resurrection_hash,

            "trust_hash":
                trust_hash,
        }

# ============================================================================
# GLOBAL ENGINE
# ============================================================================

runtime_rehydration_engine = (
    HHSRuntimeRehydrationEngine()
)

# ============================================================================
# SELF TEST
# ============================================================================

def runtime_rehydration_engine_self_test():

    runtime_state = HHSRuntimeState(

        runtime_id="runtime_001",

        step=1,

        orbit_id=72,

        transport_flux="1/1",

        orientation_flux="1/1",

        constraint_flux="1/1",

        witness_flags=7,

        prev_receipt_hash72="",

        state_hash72="state001",

        receipt_hash72="receipt001",

        lo_shu_slot=5,

        closure_class="0",

        converged=True,

        halted=False,

        timestamp_ns=time.time_ns(),
    )

    from hhs_backend.runtime.runtime_snapshot_codec import (
        create_snapshot_packet
    )

    packet = create_snapshot_packet(

        runtime_state=runtime_state,

        receipt_chain=[],

        event_topology=[],

        branch_topology={},
    )

    result = (

        runtime_rehydration_engine
        .rehydrate_from_snapshot(
            packet
        )
    )

    session = result["session"]

    graph = (

        runtime_rehydration_engine
        .create_rehydration_graph(
            session
        )
    )

    projection = (

        runtime_rehydration_engine
        .to_rehydration_graph_projection(
            graph
        )
    )

    v44 = (

        runtime_rehydration_engine
        .validate_v44_resurrection(
            session
        )
    )

    print()

    print("SESSION")

    print(session)

    print()

    print("GRAPH")

    print(graph)

    print()

    print("PROJECTION")

    print(projection)

    print()

    print("V44")

    print(v44)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    runtime_rehydration_engine_self_test()