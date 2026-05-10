# hhs_runtime/python/hhs_multimodal_receipt_graph_v1.py
#
# HARMONICODE / HHS
# Multimodal Receipt Graph Layer
#
# PURPOSE:
#
#   Unified graph memory substrate for:
#
#       Hash72 receipt chains
#       execution traces
#       multimodal embeddings
#       sandbox memory layers
#       replay prediction
#       branch divergence tracking
#       closure-state retrieval
#
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

import math
import hashlib
import json
import time

# ============================================================
# NODE TYPES
# ============================================================

NODE_RECEIPT = "receipt"
NODE_TRACE = "trace"
NODE_MODALITY = "modality"
NODE_SANDBOX = "sandbox"
NODE_BRANCH = "branch"
NODE_VECTOR = "vector"

# ============================================================
# EDGE TYPES
# ============================================================

EDGE_PARENT = "parent"
EDGE_REPLAY = "replay"
EDGE_PREDICT = "predict"
EDGE_MODALITY = "modality"
EDGE_CONSENSUS = "consensus"
EDGE_SANDBOX = "sandbox"

# ============================================================
# GRAPH NODE
# ============================================================

@dataclass
class HHSGraphNode:

    node_id: str

    node_type: str

    hash72: str

    metadata: Dict = field(
        default_factory=dict
    )

    created_at: float = field(
        default_factory=time.time
    )

# ============================================================
# GRAPH EDGE
# ============================================================

@dataclass
class HHSGraphEdge:

    source: str

    target: str

    edge_type: str

    weight: float = 1.0

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# VECTOR RECORD
# ============================================================

@dataclass
class HHSVectorRecord:

    vector_id: str

    hash72: str

    dimensions: List[float]

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# GRAPH DATABASE
# ============================================================

class HHSMultimodalReceiptGraph:

    def __init__(self):

        self.nodes: Dict[
            str,
            HHSGraphNode
        ] = {}

        self.edges: List[
            HHSGraphEdge
        ] = []

        self.adjacency: Dict[
            str,
            List[HHSGraphEdge]
        ] = defaultdict(list)

        self.vector_records: Dict[
            str,
            HHSVectorRecord
        ] = {}

        self.sandbox_layers: Dict[
            str,
            Set[str]
        ] = defaultdict(set)

    # ========================================================
    # ADD NODE
    # ========================================================

    def add_node(
        self,
        node: HHSGraphNode,
    ):

        self.nodes[node.node_id] = node

    # ========================================================
    # ADD EDGE
    # ========================================================

    def add_edge(
        self,
        edge: HHSGraphEdge,
    ):

        self.edges.append(edge)

        self.adjacency[
            edge.source
        ].append(edge)

    # ========================================================
    # CREATE RECEIPT NODE
    # ========================================================

    def create_receipt_node(

        self,

        receipt_hash72: str,

        parent_hash72: Optional[str],

        witness: int,

        step: int,

        metadata: Optional[Dict] = None,

    ) -> str:

        node_id = self.make_node_id(
            receipt_hash72
        )

        node = HHSGraphNode(

            node_id=node_id,

            node_type=NODE_RECEIPT,

            hash72=receipt_hash72,

            metadata={
                "parent":
                    parent_hash72,

                "witness":
                    witness,

                "step":
                    step,

                **(metadata or {})
            }
        )

        self.add_node(node)

        if parent_hash72:

            parent_id = self.make_node_id(
                parent_hash72
            )

            if parent_id in self.nodes:

                self.add_edge(
                    HHSGraphEdge(
                        source=parent_id,
                        target=node_id,
                        edge_type=EDGE_PARENT,
                        weight=1.0,
                    )
                )

        return node_id

    # ========================================================
    # CREATE VECTOR
    # ========================================================

    def create_vector_record(

        self,

        hash72: str,

        metadata: Optional[Dict] = None,

    ) -> str:

        vector = self.hash72_to_vector(
            hash72
        )

        vector_id = hashlib.sha256(

            hash72.encode()

        ).hexdigest()

        self.vector_records[
            vector_id
        ] = HHSVectorRecord(

            vector_id=vector_id,

            hash72=hash72,

            dimensions=vector,

            metadata=metadata or {},
        )

        return vector_id

    # ========================================================
    # HASH72 → VECTOR
    # ========================================================

    def hash72_to_vector(
        self,
        hash72: str,
    ) -> List[float]:

        vec = []

        for c in hash72:

            x = ord(c)

            v = (
                (
                    (x * 131)
                    % 997
                )
                / 997.0
            )

            vec.append(v)

        return vec

    # ========================================================
    # VECTOR DISTANCE
    # ========================================================

    def vector_distance(

        self,

        a: List[float],

        b: List[float],

    ) -> float:

        n = min(len(a), len(b))

        if n == 0:
            return 0.0

        acc = 0.0

        for i in range(n):

            d = a[i] - b[i]

            acc += d * d

        return math.sqrt(acc)

    # ========================================================
    # SEARCH NEAREST
    # ========================================================

    def search_nearest(

        self,

        hash72: str,

        top_k: int = 8,

    ):

        query = self.hash72_to_vector(
            hash72
        )

        scored = []

        for rec in self.vector_records.values():

            dist = self.vector_distance(

                query,
                rec.dimensions,
            )

            scored.append(
                (dist, rec)
            )

        scored.sort(
            key=lambda x: x[0]
        )

        return scored[:top_k]

    # ========================================================
    # SANDBOX LAYER
    # ========================================================

    def create_sandbox_layer(
        self,
        sandbox_id: str,
    ):

        if sandbox_id not in self.sandbox_layers:
            self.sandbox_layers[
                sandbox_id
            ] = set()

    # ========================================================
    # ADD TO SANDBOX
    # ========================================================

    def add_to_sandbox(

        self,

        sandbox_id: str,

        node_id: str,

    ):

        self.sandbox_layers[
            sandbox_id
        ].add(node_id)

    # ========================================================
    # GET SANDBOX
    # ========================================================

    def get_sandbox_nodes(
        self,
        sandbox_id: str,
    ):

        ids = self.sandbox_layers.get(
            sandbox_id,
            set()
        )

        return [

            self.nodes[n]

            for n in ids

            if n in self.nodes
        ]

    # ========================================================
    # REPLAY PREDICTION
    # ========================================================

    def replay_predict(

        self,

        hash72: str,

        top_k: int = 4,

    ):

        nearest = self.search_nearest(

            hash72,
            top_k=top_k,
        )

        predictions = []

        for dist, rec in nearest:

            node_id = self.make_node_id(
                rec.hash72
            )

            outgoing = self.adjacency.get(
                node_id,
                []
            )

            for edge in outgoing:

                if edge.edge_type != EDGE_PARENT:
                    continue

                target = self.nodes.get(
                    edge.target
                )

                if not target:
                    continue

                predictions.append({

                    "source":
                        rec.hash72,

                    "predicted":
                        target.hash72,

                    "distance":
                        dist,

                    "metadata":
                        target.metadata,
                })

        return predictions

    # ========================================================
    # CONSENSUS CLUSTER
    # ========================================================

    def consensus_cluster(

        self,

        hash72: str,

        radius: float = 2.0,

    ):

        query = self.hash72_to_vector(
            hash72
        )

        cluster = []

        for rec in self.vector_records.values():

            dist = self.vector_distance(

                query,
                rec.dimensions,
            )

            if dist <= radius:

                cluster.append({

                    "hash72":
                        rec.hash72,

                    "distance":
                        dist,
                })

        cluster.sort(
            key=lambda x: x["distance"]
        )

        return cluster

    # ========================================================
    # NODE ID
    # ========================================================

    def make_node_id(
        self,
        hash72: str,
    ) -> str:

        return hashlib.sha256(

            hash72.encode()

        ).hexdigest()[:24]

    # ========================================================
    # EXPORT
    # ========================================================

    def export_json(self):

        return {

            "nodes": [

                {

                    "node_id":
                        n.node_id,

                    "node_type":
                        n.node_type,

                    "hash72":
                        n.hash72,

                    "metadata":
                        n.metadata,
                }

                for n in self.nodes.values()
            ],

            "edges": [

                {

                    "source":
                        e.source,

                    "target":
                        e.target,

                    "edge_type":
                        e.edge_type,

                    "weight":
                        e.weight,
                }

                for e in self.edges
            ],

            "sandbox_layers": {

                k: list(v)

                for k, v

                in self.sandbox_layers.items()
            }
        }

# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    graph = HHSMultimodalReceiptGraph()

    root = graph.create_receipt_node(

        receipt_hash72=
            "2jDWVX51QbuxI6>1pQ0y?oVxa4BELNQR2Q8ki)vi9X3tFrzLuC5JxQBpOUVm(ARNW8cEOYMW",

        parent_hash72=None,

        witness=0,

        step=0,
    )

    node2 = graph.create_receipt_node(

        receipt_hash72=
            "EYavwAcdQcwAMb3cxQ1A2s-DhcBFNQUuNrTWUA2*UAaBFsBOyHbQFQCtRY-s1IRRYbgfpznr",

        parent_hash72=
            "2jDWVX51QbuxI6>1pQ0y?oVxa4BELNQR2Q8ki)vi9X3tFrzLuC5JxQBpOUVm(ARNW8cEOYMW",

        witness=0x1800,

        step=18,
    )

    graph.create_vector_record(

        "2jDWVX51QbuxI6>1pQ0y?oVxa4BELNQR2Q8ki)vi9X3tFrzLuC5JxQBpOUVm(ARNW8cEOYMW"
    )

    graph.create_vector_record(

        "EYavwAcdQcwAMb3cxQ1A2s-DhcBFNQUuNrTWUA2*UAaBFsBOyHbQFQCtRY-s1IRRYbgfpznr"
    )

    graph.create_sandbox_layer(
        "sandbox-alpha"
    )

    graph.add_to_sandbox(
        "sandbox-alpha",
        root,
    )

    graph.add_to_sandbox(
        "sandbox-alpha",
        node2,
    )

    print("\n=== REPLAY PREDICTION ===\n")

    preds = graph.replay_predict(

        "2jDWVX51QbuxI6>1pQ0y?oVxa4BELNQR2Q8ki)vi9X3tFrzLuC5JxQBpOUVm(ARNW8cEOYMW"
    )

    print(
        json.dumps(
            preds,
            indent=2,
        )
    )

    print("\n=== SANDBOX ===\n")

    sandbox = graph.get_sandbox_nodes(
        "sandbox-alpha"
    )

    for node in sandbox:

        print(
            node.node_type,
            node.hash72[:24]
        )