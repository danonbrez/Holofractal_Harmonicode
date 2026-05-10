# ============================================================================
# hhs_graph/hhs_multimodal_receipt_graph_v1.py
# HARMONICODE / HHS
# MULTIMODAL RECEIPT GRAPH
#
# PURPOSE
# -------
# Persistent runtime memory substrate for:
#
#   - receipt-chain storage
#   - replay execution
#   - vector indexing
#   - branch/rejoin topology
#   - sandbox overlays
#   - multimodal routing
#   - prediction systems
#   - adaptive runtime learning
#
# ============================================================================

from __future__ import annotations

import math
import time
import uuid

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any

# ============================================================================
# GRAPH NODE
# ============================================================================

@dataclass
class HHSGraphNode:

    node_id: str

    parent_id: Optional[str]

    created_at: float

    step: int

    state_hash72: str

    receipt_hash72: str

    witness_flags: int

    transport_flux: int

    orientation_flux: int

    constraint_flux: int

    vector: List[float]

    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# GRAPH EDGE
# ============================================================================

@dataclass
class HHSGraphEdge:

    source_id: str

    target_id: str

    edge_type: str

    weight: float = 1.0

# ============================================================================
# SANDBOX OVERLAY
# ============================================================================

@dataclass
class HHSSandboxOverlay:

    sandbox_id: str

    active_nodes: Set[str] = field(default_factory=set)

    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# MULTIMODAL RECEIPT GRAPH
# ============================================================================

class HHSMultimodalReceiptGraph:

    """
    Persistent graph-memory substrate.
    """

    def __init__(self):

        self.nodes: Dict[
            str,
            HHSGraphNode
        ] = {}

        self.edges: List[
            HHSGraphEdge
        ] = []

        self.hash_index: Dict[
            str,
            str
        ] = {}

        self.step_index: Dict[
            int,
            List[str]
        ] = {}

        self.sandboxes: Dict[
            str,
            HHSSandboxOverlay
        ] = {}

    # =====================================================================
    # NODE INGESTION
    # =====================================================================

    def ingest_runtime_state(
        self,
        runtime_packet: Dict
    ) -> HHSGraphNode:

        runtime = runtime_packet["runtime"]

        node_id = str(uuid.uuid4())

        parent_id = None

        if len(self.nodes) > 0:

            parent_id = list(self.nodes.keys())[-1]

        vector = (
            runtime_packet["vector_record"]["vector"]
        )

        node = HHSGraphNode(

            node_id=node_id,

            parent_id=parent_id,

            created_at=time.time(),

            step=runtime["step"],

            state_hash72=
                runtime["state_hash72"],

            receipt_hash72=
                runtime["receipt_hash72"],

            witness_flags=
                runtime["witness_flags"],

            transport_flux=
                runtime["transport_flux"],

            orientation_flux=
                runtime["orientation_flux"],

            constraint_flux=
                runtime["constraint_flux"],

            vector=vector
        )

        self.nodes[node_id] = node

        self.hash_index[
            node.state_hash72
        ] = node_id

        if node.step not in self.step_index:
            self.step_index[node.step] = []

        self.step_index[node.step].append(node_id)

        if parent_id is not None:

            self.edges.append(

                HHSGraphEdge(

                    source_id=parent_id,

                    target_id=node_id,

                    edge_type="receipt_chain",

                    weight=1.0
                )
            )

        return node

    # =====================================================================
    # VECTOR SEARCH
    # =====================================================================

    def cosine_similarity(
        self,
        a: List[float],
        b: List[float]
    ) -> float:

        dot = 0.0

        norm_a = 0.0

        norm_b = 0.0

        for x, y in zip(a, b):

            dot += x * y

            norm_a += x * x

            norm_b += y * y

        if norm_a == 0.0:
            return 0.0

        if norm_b == 0.0:
            return 0.0

        return dot / (
            math.sqrt(norm_a)
            * math.sqrt(norm_b)
        )

    # ---------------------------------------------------------------------

    def nearest_neighbors(
        self,
        vector: List[float],
        top_k: int = 5
    ):

        results = []

        for node in self.nodes.values():

            similarity = self.cosine_similarity(
                vector,
                node.vector
            )

            results.append(
                (similarity, node)
            )

        results.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return results[:top_k]

    # =====================================================================
    # HASH SEARCH
    # =====================================================================

    def get_by_hash72(
        self,
        hash72: str
    ) -> Optional[HHSGraphNode]:

        node_id = self.hash_index.get(hash72)

        if node_id is None:
            return None

        return self.nodes[node_id]

    # =====================================================================
    # REPLAY
    # =====================================================================

    def replay_chain(
        self,
        start_node_id: str
    ) -> List[HHSGraphNode]:

        replay = []

        current = start_node_id

        while current is not None:

            node = self.nodes[current]

            replay.append(node)

            current = node.parent_id

        replay.reverse()

        return replay

    # =====================================================================
    # BRANCHING
    # =====================================================================

    def create_branch(
        self,
        source_node_id: str,
        metadata: Optional[Dict] = None
    ):

        branch_id = str(uuid.uuid4())

        sandbox = HHSSandboxOverlay(

            sandbox_id=branch_id,

            metadata=metadata or {}
        )

        sandbox.active_nodes.add(source_node_id)

        self.sandboxes[branch_id] = sandbox

        return sandbox

    # =====================================================================
    # SANDBOX OVERLAY
    # =====================================================================

    def sandbox_ingest(
        self,
        sandbox_id: str,
        node_id: str
    ):

        sandbox = self.sandboxes[sandbox_id]

        sandbox.active_nodes.add(node_id)

    # =====================================================================
    # GRAPH EXPORT
    # =====================================================================

    def export_graph_summary(self):

        return {

            "nodes":
                len(self.nodes),

            "edges":
                len(self.edges),

            "sandboxes":
                len(self.sandboxes),

            "indexed_hashes":
                len(self.hash_index),
        }

    # =====================================================================
    # PREDICTION ROUTING
    # =====================================================================

    def predict_next_states(
        self,
        current_node_id: str,
        top_k: int = 5
    ):

        node = self.nodes[current_node_id]

        return self.nearest_neighbors(
            node.vector,
            top_k=top_k
        )

# ============================================================================
# SELF TEST
# ============================================================================

def graph_self_test():

    graph = HHSMultimodalReceiptGraph()

    packet = {

        "runtime": {

            "step": 1,

            "state_hash72":
                "abc123",

            "receipt_hash72":
                "xyz789",

            "witness_flags":
                5,

            "transport_flux":
                10,

            "orientation_flux":
                0,

            "constraint_flux":
                2,
        },

        "vector_record": {

            "vector":
                [0.1] * 72
        }
    }

    node = graph.ingest_runtime_state(packet)

    print()

    print("GRAPH SUMMARY")

    print(graph.export_graph_summary())

    print()

    print("NODE")

    print(node)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    graph_self_test()