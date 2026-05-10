# hhs_runtime/python/hhs_virtual_memory_layer_v1.py
#
# HARMONICODE / HHS
# Virtual Sandbox Memory Layer
#
# PURPOSE:
#
#   Creates isolated predictive memory environments over the
#   multimodal Hash72 receipt graph.
#
# FEATURES:
#
#   - Virtual branch sandboxes
#   - Predictive replay chains
#   - Receipt-chain memory isolation
#   - Constraint-safe branch simulation
#   - Closure-preserving replay
#   - Consensus memory overlays
#
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from collections import defaultdict

import hashlib
import json
import time
import copy

# ============================================================
# IMPORT GRAPH
# ============================================================

from hhs_multimodal_receipt_graph_v1 import (
    HHSMultimodalReceiptGraph,
)

# ============================================================
# SANDBOX TRACE
# ============================================================

@dataclass
class HHSSandboxTrace:

    trace_id: str

    receipt_chain: List[str] = field(
        default_factory=list
    )

    predicted_chain: List[str] = field(
        default_factory=list
    )

    closure_flags: Dict = field(
        default_factory=dict
    )

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# SANDBOX MEMORY
# ============================================================

@dataclass
class HHSSandboxMemory:

    sandbox_id: str

    created_at: float = field(
        default_factory=time.time
    )

    node_ids: Set[str] = field(
        default_factory=set
    )

    traces: List[
        HHSSandboxTrace
    ] = field(
        default_factory=list
    )

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# VIRTUAL MEMORY LAYER
# ============================================================

class HHSVirtualMemoryLayer:

    def __init__(
        self,
        graph: HHSMultimodalReceiptGraph,
    ):

        self.graph = graph

        self.sandboxes: Dict[
            str,
            HHSSandboxMemory
        ] = {}

    # ========================================================
    # CREATE SANDBOX
    # ========================================================

    def create_sandbox(

        self,

        sandbox_name: str,

        metadata: Optional[Dict] = None,

    ) -> str:

        sandbox_id = hashlib.sha256(

            sandbox_name.encode()

        ).hexdigest()[:24]

        self.sandboxes[sandbox_id] = HHSSandboxMemory(

            sandbox_id=sandbox_id,

            metadata=metadata or {},
        )

        return sandbox_id

    # ========================================================
    # ADD RECEIPT
    # ========================================================

    def add_receipt_to_sandbox(

        self,

        sandbox_id: str,

        hash72: str,

    ):

        if sandbox_id not in self.sandboxes:
            return

        node_id = self.graph.make_node_id(
            hash72
        )

        if node_id in self.graph.nodes:

            self.sandboxes[
                sandbox_id
            ].node_ids.add(node_id)

    # ========================================================
    # BUILD TRACE
    # ========================================================

    def build_trace(

        self,

        sandbox_id: str,

        start_hash72: str,

        depth: int = 8,

    ) -> Optional[HHSSandboxTrace]:

        if sandbox_id not in self.sandboxes:
            return None

        node_id = self.graph.make_node_id(
            start_hash72
        )

        if node_id not in self.graph.nodes:
            return None

        trace = HHSSandboxTrace(

            trace_id=hashlib.sha256(

                (
                    sandbox_id
                    + start_hash72
                    + str(time.time())
                ).encode()

            ).hexdigest()[:24]
        )

        current = node_id

        for _ in range(depth):

            node = self.graph.nodes.get(
                current
            )

            if not node:
                break

            trace.receipt_chain.append(
                node.hash72
            )

            outgoing = self.graph.adjacency.get(
                current,
                []
            )

            next_node = None

            for edge in outgoing:

                if edge.edge_type == "parent":

                    next_node = edge.target
                    break

            if not next_node:
                break

            current = next_node

        self.sandboxes[
            sandbox_id
        ].traces.append(trace)

        return trace

    # ========================================================
    # PREDICT TRACE
    # ========================================================

    def predict_trace(

        self,

        sandbox_id: str,

        hash72: str,

        top_k: int = 4,

    ):

        if sandbox_id not in self.sandboxes:
            return []

        preds = self.graph.replay_predict(

            hash72=hash72,

            top_k=top_k,
        )

        predicted = []

        for p in preds:

            predicted.append(
                p["predicted"]
            )

        return predicted

    # ========================================================
    # CONSENSUS MEMORY
    # ========================================================

    def consensus_memory(

        self,

        sandbox_id: str,

        hash72: str,

        radius: float = 2.0,

    ):

        if sandbox_id not in self.sandboxes:
            return []

        cluster = self.graph.consensus_cluster(

            hash72=hash72,

            radius=radius,
        )

        return cluster

    # ========================================================
    # FORK SANDBOX
    # ========================================================

    def fork_sandbox(

        self,

        sandbox_id: str,

        new_name: str,

    ) -> Optional[str]:

        if sandbox_id not in self.sandboxes:
            return None

        original = self.sandboxes[
            sandbox_id
        ]

        new_id = self.create_sandbox(
            new_name
        )

        self.sandboxes[
            new_id
        ] = copy.deepcopy(original)

        self.sandboxes[
            new_id
        ].sandbox_id = new_id

        return new_id

    # ========================================================
    # EXPORT SANDBOX
    # ========================================================

    def export_sandbox(
        self,
        sandbox_id: str,
    ):

        if sandbox_id not in self.sandboxes:
            return None

        sb = self.sandboxes[
            sandbox_id
        ]

        return {

            "sandbox_id":
                sb.sandbox_id,

            "created_at":
                sb.created_at,

            "node_count":
                len(sb.node_ids),

            "trace_count":
                len(sb.traces),

            "metadata":
                sb.metadata,

            "traces": [

                {

                    "trace_id":
                        t.trace_id,

                    "receipt_chain":
                        t.receipt_chain,

                    "predicted_chain":
                        t.predicted_chain,

                    "closure_flags":
                        t.closure_flags,
                }

                for t in sb.traces
            ]
        }

# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    from hhs_multimodal_receipt_graph_v1 import (
        HHSMultimodalReceiptGraph,
        HHSGraphNode,
    )

    graph = HHSMultimodalReceiptGraph()

    h0 = (
        "2jDWVX51QbuxI6>1pQ0y?oVxa4BELNQR"
        "2Q8ki)vi9X3tFrzLuC5JxQBpOUVm(ARN"
        "W8cEOYMW"
    )

    h1 = (
        "EYavwAcdQcwAMb3cxQ1A2s-DhcBFNQUu"
        "NrTWUA2*UAaBFsBOyHbQFQCtRY-s1IRR"
        "Ybgfpznr"
    )

    graph.create_receipt_node(

        receipt_hash72=h0,

        parent_hash72=None,

        witness=0,

        step=0,
    )

    graph.create_receipt_node(

        receipt_hash72=h1,

        parent_hash72=h0,

        witness=0x1800,

        step=18,
    )

    graph.create_vector_record(h0)
    graph.create_vector_record(h1)

    vmemory = HHSVirtualMemoryLayer(
        graph
    )

    sandbox_id = vmemory.create_sandbox(
        "sandbox-alpha"
    )

    vmemory.add_receipt_to_sandbox(
        sandbox_id,
        h0,
    )

    vmemory.add_receipt_to_sandbox(
        sandbox_id,
        h1,
    )

    trace = vmemory.build_trace(

        sandbox_id,

        h0,

        depth=4,
    )

    preds = vmemory.predict_trace(

        sandbox_id,

        h0,
    )

    consensus = vmemory.consensus_memory(

        sandbox_id,

        h0,
    )

    print("\n=== TRACE ===\n")

    print(
        json.dumps(
            trace.receipt_chain,
            indent=2,
        )
    )

    print("\n=== PREDICTIONS ===\n")

    print(
        json.dumps(
            preds,
            indent=2,
        )
    )

    print("\n=== CONSENSUS ===\n")

    print(
        json.dumps(
            consensus,
            indent=2,
        )
    )

    print("\n=== EXPORT ===\n")

    print(
        json.dumps(

            vmemory.export_sandbox(
                sandbox_id
            ),

            indent=2,
        )
    )