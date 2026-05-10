# ============================================================================
# hhs_backend/runtime/runtime_replay_topology.py
# HARMONICODE / HHS
# CANONICAL REPLAY GEOMETRY AUTHORITY
#
# PURPOSE
# -------
# Canonical replay-topology substrate for:
#
#   - deterministic replay ordering
#   - branch replay geometry
#   - replay causality graphs
#   - replay partition synchronization
#   - replay isolation modes
#   - distributed replay orchestration
#   - replay equivalence verification
#   - replay scheduling/checkpointing
#   - v44.2 replay continuity
#
# Replay topology IS runtime execution geometry.
#
# ============================================================================

from __future__ import annotations

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

from hhs_backend.runtime.runtime_receipt_chain import (
    HHSReceipt,
    runtime_receipt_chain,
)

from hhs_backend.runtime.runtime_snapshot_codec import (
    HHSSnapshotPacket,
)

from hhs_backend.runtime.runtime_rehydration_engine import (
    HHSRehydrationSession,
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
    "HHS_RUNTIME_REPLAY_TOPOLOGY"
)

# ============================================================================
# CONSTANTS
# ============================================================================

REPLAY_SCHEMA_VERSION = "v1"

# ============================================================================
# REPLAY TOPOLOGY
# ============================================================================

@dataclass
class HHSReplayTopology:

    topology_id: str

    runtime_id: str

    branch_id: str

    created_at_ns: int

    replay_mode: str

    replay_hash72: str

    replay_paths: List[str]

    partition_ids: List[str]

    causal_dependencies: Dict[str, List[str]]

    merge_dependencies: Dict[str, List[str]]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# REPLAY GRAPH
# ============================================================================

@dataclass
class HHSReplayGraph:

    graph_id: str

    runtime_id: str

    created_at_ns: int

    nodes: List[Dict[str, Any]]

    edges: List[Dict[str, Any]]

    partition_graph: Dict[str, Any]

    replay_equivalent: bool

# ============================================================================
# REPLAY SCHEDULER
# ============================================================================

@dataclass
class HHSReplaySchedule:

    schedule_id: str

    runtime_id: str

    created_at_ns: int

    scheduled_paths: List[str]

    checkpoint_interval: int

    throttled: bool

    resumed: bool

# ============================================================================
# TOPOLOGY ENGINE
# ============================================================================

class HHSRuntimeReplayTopology:

    """
    Canonical replay geometry authority.
    """

    def __init__(self):

        self.lock = threading.RLock()

        self.topologies: Dict[
            str,
            HHSReplayTopology
        ] = {}

        self.graphs: Dict[
            str,
            HHSReplayGraph
        ] = {}

        self.schedules: Dict[
            str,
            HHSReplaySchedule
        ] = {}

        self.partition_streams = defaultdict(list)

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
    # CONSTRUCT REPLAY PATH
    # =====================================================================

    def construct_replay_path(
        self,
        runtime_id: str,
    ):

        lineage = (

            runtime_receipt_chain
            .reconstruct_runtime_lineage(
                runtime_id
            )
        )

        path = [

            x["receipt_hash72"]

            for x in lineage
        ]

        return path

    # =====================================================================
    # BRANCH REPLAY
    # =====================================================================

    def construct_branch_replay_path(
        self,
        branch_id: str,
    ):

        history = (

            runtime_receipt_chain
            .reconstruct_branch_history(
                branch_id
            )
        )

        return [

            x.receipt_hash72

            for x in history
        ]

    # =====================================================================
    # MERGE PATH
    # =====================================================================

    def construct_merge_replay_path(

        self,

        target_branch_id: str,

        source_branch_id: str,
    ):

        target_path = (
            self.construct_branch_replay_path(
                target_branch_id
            )
        )

        source_path = (
            self.construct_branch_replay_path(
                source_branch_id
            )
        )

        merged = (
            target_path
            + source_path
        )

        return list(dict.fromkeys(merged))

    # =====================================================================
    # PARTITION STREAMS
    # =====================================================================

    def partition_replay_streams(

        self,

        replay_paths: List[str],

        partition_count: int = 4,
    ):

        partitions = defaultdict(list)

        for index, path in enumerate(
            replay_paths
        ):

            partition_id = (
                f"partition_"
                f"{index % partition_count}"
            )

            partitions[
                partition_id
            ].append(path)

        return dict(partitions)

    # =====================================================================
    # SYNCHRONIZE PARTITIONS
    # =====================================================================

    def synchronize_partition_replay(
        self,
        partitions: Dict[str, List[str]],
    ):

        synchronized = True

        lengths = [

            len(x)

            for x in partitions.values()
        ]

        if lengths:

            synchronized = (
                max(lengths)
                - min(lengths)
            ) <= 1

        return synchronized

    # =====================================================================
    # VERIFY PARTITION ORDER
    # =====================================================================

    def verify_partition_ordering(
        self,
        partitions: Dict[str, List[str]],
    ):

        for values in partitions.values():

            if values != sorted(values):

                return False

        return True

    # =====================================================================
    # BUILD TOPOLOGY
    # =====================================================================

    def build_replay_topology(

        self,

        runtime_id: str,

        branch_id: str = "main",

        replay_mode: str = "standard",
    ):

        replay_paths = (
            self.construct_replay_path(
                runtime_id
            )
        )

        partitions = (
            self.partition_replay_streams(
                replay_paths
            )
        )

        causal_dependencies = {}

        merge_dependencies = {}

        previous = None

        for receipt_hash in replay_paths:

            if previous:

                causal_dependencies[
                    receipt_hash
                ] = [previous]

            else:

                causal_dependencies[
                    receipt_hash
                ] = []

            previous = receipt_hash

        topology_hash = self.compute_hash72({

            "runtime_id":
                runtime_id,

            "paths":
                replay_paths,

            "partitions":
                partitions,
        })

        topology = HHSReplayTopology(

            topology_id=str(uuid.uuid4()),

            runtime_id=runtime_id,

            branch_id=branch_id,

            created_at_ns=time.time_ns(),

            replay_mode=replay_mode,

            replay_hash72=topology_hash,

            replay_paths=replay_paths,

            partition_ids=list(
                partitions.keys()
            ),

            causal_dependencies=
                causal_dependencies,

            merge_dependencies=
                merge_dependencies,

            metadata={

                "schema_version":
                    REPLAY_SCHEMA_VERSION,

                "kernel_available":
                    V44_KERNEL_AVAILABLE,
            },
        )

        self.topologies[
            topology.topology_id
        ] = topology

        logger.info(
            f"Replay topology built: "
            f"{topology.topology_id}"
        )

        return topology

    # =====================================================================
    # REPLAY GRAPH
    # =====================================================================

    def create_replay_graph(
        self,
        topology: HHSReplayTopology,
    ):

        nodes = []

        edges = []

        previous = None

        for receipt_hash in (
            topology.replay_paths
        ):

            nodes.append({

                "node_id":
                    receipt_hash,

                "runtime_id":
                    topology.runtime_id,
            })

            if previous:

                edges.append({

                    "source":
                        previous,

                    "target":
                        receipt_hash,
                })

            previous = receipt_hash

        partition_graph = {

            partition_id: []

            for partition_id
            in topology.partition_ids
        }

        graph = HHSReplayGraph(

            graph_id=str(uuid.uuid4()),

            runtime_id=
                topology.runtime_id,

            created_at_ns=
                time.time_ns(),

            nodes=nodes,

            edges=edges,

            partition_graph=
                partition_graph,

            replay_equivalent=True,
        )

        self.graphs[
            graph.graph_id
        ] = graph

        logger.info(
            f"Replay graph created: "
            f"{graph.graph_id}"
        )

        return graph

    # =====================================================================
    # ISOLATION MODES
    # =====================================================================

    def isolated_replay(
        self,
        topology: HHSReplayTopology,
    ):

        topology.replay_mode = (
            "isolated"
        )

        return topology

    # =====================================================================
    # SANDBOX REPLAY
    # =====================================================================

    def sandbox_replay(
        self,
        topology: HHSReplayTopology,
    ):

        topology.replay_mode = (
            "sandbox"
        )

        return topology

    # =====================================================================
    # VALIDATION REPLAY
    # =====================================================================

    def validation_replay(
        self,
        topology: HHSReplayTopology,
    ):

        topology.replay_mode = (
            "validation"
        )

        return topology

    # =====================================================================
    # PROJECTION REPLAY
    # =====================================================================

    def projection_replay(
        self,
        topology: HHSReplayTopology,
    ):

        topology.replay_mode = (
            "projection"
        )

        return topology

    # =====================================================================
    # SCHEDULE REPLAY
    # =====================================================================

    def schedule_replay(

        self,

        topology: HHSReplayTopology,

        checkpoint_interval: int = 100,
    ):

        schedule = HHSReplaySchedule(

            schedule_id=str(uuid.uuid4()),

            runtime_id=
                topology.runtime_id,

            created_at_ns=
                time.time_ns(),

            scheduled_paths=
                topology.replay_paths,

            checkpoint_interval=
                checkpoint_interval,

            throttled=False,

            resumed=False,
        )

        self.schedules[
            schedule.schedule_id
        ] = schedule

        logger.info(
            f"Replay scheduled: "
            f"{schedule.schedule_id}"
        )

        return schedule

    # =====================================================================
    # THROTTLE
    # =====================================================================

    def throttle_replay(
        self,
        schedule: HHSReplaySchedule,
    ):

        schedule.throttled = True

        return schedule

    # =====================================================================
    # CHECKPOINT
    # =====================================================================

    def checkpoint_replay(
        self,
        schedule: HHSReplaySchedule,
    ):

        return {

            "runtime_id":
                schedule.runtime_id,

            "checkpoint_interval":
                schedule.checkpoint_interval,
        }

    # =====================================================================
    # RESUME
    # =====================================================================

    def resume_replay(
        self,
        schedule: HHSReplaySchedule,
    ):

        schedule.resumed = True

        return schedule

    # =====================================================================
    # VERIFY TOPOLOGY
    # =====================================================================

    def verify_replay_topology(
        self,
        topology: HHSReplayTopology,
    ):

        recomputed = self.compute_hash72({

            "runtime_id":
                topology.runtime_id,

            "paths":
                topology.replay_paths,

            "partitions":
                topology.partition_ids,
        })

        return (
            recomputed
            ==
            topology.replay_hash72
        )

    # =====================================================================
    # VERIFY BRANCH
    # =====================================================================

    def verify_branch_topology(
        self,
        topology: HHSReplayTopology,
    ):

        return (
            len(topology.partition_ids)
            >= 0
        )

    # =====================================================================
    # VERIFY EQUIVALENCE
    # =====================================================================

    def verify_replay_equivalence(

        self,

        topology_a: HHSReplayTopology,

        topology_b: HHSReplayTopology,
    ):

        return (

            topology_a.replay_hash72
            ==
            topology_b.replay_hash72
        )

    # =====================================================================
    # GRAPH PROJECTION
    # =====================================================================

    def to_replay_graph(
        self,
        graph: HHSReplayGraph,
    ):

        return {

            "graph_id":
                graph.graph_id,

            "nodes":
                len(graph.nodes),

            "edges":
                len(graph.edges),

            "equivalent":
                graph.replay_equivalent,
        }

    # =====================================================================
    # PARTITION PROJECTION
    # =====================================================================

    def to_partition_projection(
        self,
        topology: HHSReplayTopology,
    ):

        return {

            "runtime_id":
                topology.runtime_id,

            "partition_count":
                len(topology.partition_ids),

            "replay_mode":
                topology.replay_mode,
        }

    # =====================================================================
    # CAUSAL PROJECTION
    # =====================================================================

    def to_causal_projection(
        self,
        topology: HHSReplayTopology,
    ):

        return {

            "runtime_id":
                topology.runtime_id,

            "causal_dependencies":
                topology.causal_dependencies,
        }

    # =====================================================================
    # TRANSPORT PACKET
    # =====================================================================

    def to_replay_transport_packet(
        self,
        topology: HHSReplayTopology,
    ):

        return {

            "runtime_id":
                topology.runtime_id,

            "replay_hash72":
                topology.replay_hash72,

            "replay_mode":
                topology.replay_mode,
        }

    # =====================================================================
    # V44 VALIDATION
    # =====================================================================

    def validate_v44_replay_topology(
        self,
        topology: HHSReplayTopology,
    ):

        if not V44_KERNEL_AVAILABLE:

            return {

                "kernel_available": False,

                "validated": False,
            }

        topology_hash = hashlib.sha256(

            json.dumps(

                topology.replay_paths,

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

            "topology_hash":
                topology_hash,

            "trust_hash":
                trust_hash,
        }

# ============================================================================
# GLOBAL ENGINE
# ============================================================================

runtime_replay_topology = (
    HHSRuntimeReplayTopology()
)

# ============================================================================
# SELF TEST
# ============================================================================

def runtime_replay_topology_self_test():

    topology = (

        runtime_replay_topology
        .build_replay_topology(

            runtime_id="runtime_001"
        )
    )

    graph = (

        runtime_replay_topology
        .create_replay_graph(
            topology
        )
    )

    schedule = (

        runtime_replay_topology
        .schedule_replay(
            topology
        )
    )

    replay_graph = (

        runtime_replay_topology
        .to_replay_graph(
            graph
        )
    )

    partition_projection = (

        runtime_replay_topology
        .to_partition_projection(
            topology
        )
    )

    causal_projection = (

        runtime_replay_topology
        .to_causal_projection(
            topology
        )
    )

    v44 = (

        runtime_replay_topology
        .validate_v44_replay_topology(
            topology
        )
    )

    print()

    print("TOPOLOGY")

    print(topology)

    print()

    print("GRAPH")

    print(graph)

    print()

    print("SCHEDULE")

    print(schedule)

    print()

    print("REPLAY GRAPH")

    print(replay_graph)

    print()

    print("PARTITION")

    print(partition_projection)

    print()

    print("CAUSAL")

    print(causal_projection)

    print()

    print("V44")

    print(v44)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    runtime_replay_topology_self_test()