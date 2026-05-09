# hhs_runtime/python/hhs_multimodal_graph_kernel_v1.py
#
# HARMONICODE / HHS
# Multimodal graph-kernel manifold
#
# PURPOSE:
#   Unified multimodal receipt-chain graph substrate.
#
#   This layer formalizes:
#
#   - symbolic state graphs
#   - receipt-chain adjacency
#   - modality translation
#   - replay traversal
#   - tensor-linked search
#   - semantic manifold routing
#   - virtual memory overlays
#
# CORE:
#   all modalities become graph projections
#   over the same HASH72 receipt manifold
#
# ============================================================

from __future__ import annotations

import json
import math
import hashlib

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional

# ============================================================
# IMPORTS
# ============================================================

from hhs_receipt_vector_cache_v1 import (
    HHSReceiptVectorCache,
    ReceiptNode,
    hash72_distance,
)

# ============================================================
# HASH72
# ============================================================

HASH72 = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "-+*/()<>!?"
)

HASH72_INDEX = {
    c: i for i, c in enumerate(HASH72)
}

# ============================================================
# UTILS
# ============================================================

def wrap72(v: int) -> int:
    return v % 72


def sha256_hex(data: str) -> str:

    return hashlib.sha256(
        data.encode()
    ).hexdigest()


# ============================================================
# MODALITY TYPES
# ============================================================

MODALITY_TEXT      = "text"
MODALITY_CODE      = "code"
MODALITY_AUDIO     = "audio"
MODALITY_IMAGE     = "image"
MODALITY_VIDEO     = "video"
MODALITY_SYMBOLIC  = "symbolic"
MODALITY_RUNTIME   = "runtime"
MODALITY_GENOMIC   = "genomic"

# ============================================================
# GRAPH EDGE
# ============================================================

@dataclass
class GraphEdge:

    source: str
    target: str

    relation: str

    weight: float = 1.0

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# GRAPH NODE
# ============================================================

@dataclass
class GraphNode:

    node_id: str

    modality: str

    state_hash72: str

    receipt_hash72: str

    payload: Dict = field(
        default_factory=dict
    )

    vector_signature: List[int] = field(
        default_factory=list
    )

    sandbox_layers: Set[str] = field(
        default_factory=set
    )

# ============================================================
# GRAPH KERNEL
# ============================================================

@dataclass
class HHSMultimodalGraphKernel:

    cache: HHSReceiptVectorCache

    nodes: Dict[str, GraphNode] = field(
        default_factory=dict
    )

    edges: Dict[str, List[GraphEdge]] = field(
        default_factory=dict
    )

    modality_index: Dict[str, Set[str]] = field(
        default_factory=dict
    )

    state_index: Dict[str, Set[str]] = field(
        default_factory=dict
    )

    # ========================================================
    # NODE INSERT
    # ========================================================

    def insert_node(
        self,
        modality: str,
        state_hash72: str,
        receipt_hash72: str,
        payload: Optional[Dict] = None,
        sandbox_layer: Optional[str] = None,
    ) -> str:

        node_id = sha256_hex(
            modality
            + state_hash72
            + receipt_hash72
        )

        vec = self.hash72_vector(
            state_hash72
        )

        node = GraphNode(
            node_id=node_id,
            modality=modality,
            state_hash72=state_hash72,
            receipt_hash72=receipt_hash72,
            payload=payload or {},
            vector_signature=vec,
        )

        if sandbox_layer:
            node.sandbox_layers.add(
                sandbox_layer
            )

        self.nodes[node_id] = node

        if modality not in self.modality_index:
            self.modality_index[modality] = set()

        self.modality_index[modality].add(
            node_id
        )

        if state_hash72 not in self.state_index:
            self.state_index[state_hash72] = set()

        self.state_index[state_hash72].add(
            node_id
        )

        return node_id

    # ========================================================
    # EDGE
    # ========================================================

    def connect(
        self,
        source: str,
        target: str,
        relation: str,
        weight: float = 1.0,
        metadata: Optional[Dict] = None,
    ) -> None:

        edge = GraphEdge(
            source=source,
            target=target,
            relation=relation,
            weight=weight,
            metadata=metadata or {},
        )

        if source not in self.edges:
            self.edges[source] = []

        self.edges[source].append(edge)

    # ========================================================
    # VECTOR
    # ========================================================

    def hash72_vector(
        self,
        h: str
    ) -> List[int]:

        return [
            HASH72_INDEX[c]
            for c in h
        ]

    # ========================================================
    # DISTANCE
    # ========================================================

    def vector_distance(
        self,
        a: List[int],
        b: List[int],
    ) -> float:

        total = 0.0

        for x, y in zip(a, b):

            d = abs(x - y)

            total += min(d, 72 - d)

        return total

    # ========================================================
    # SEARCH
    # ========================================================

    def nearest_nodes(
        self,
        state_hash72: str,
        modality: Optional[str] = None,
        top_k: int = 8,
    ) -> List[Tuple[float, GraphNode]]:

        vec = self.hash72_vector(
            state_hash72
        )

        out = []

        node_ids = (
            self.modality_index.get(
                modality,
                set(),
            )
            if modality
            else self.nodes.keys()
        )

        for node_id in node_ids:

            node = self.nodes[node_id]

            dist = self.vector_distance(
                vec,
                node.vector_signature,
            )

            out.append((dist, node))

        out.sort(
            key=lambda x: x[0]
        )

        return out[:top_k]

    # ========================================================
    # MODALITY TRANSLATION
    # ========================================================

    def modality_projection(
        self,
        source_state72: str,
        target_modality: str,
        top_k: int = 5,
    ) -> List[GraphNode]:

        nearest = self.nearest_nodes(
            source_state72,
            modality=target_modality,
            top_k=top_k,
        )

        return [
            node for _, node in nearest
        ]

    # ========================================================
    # GRAPH WALK
    # ========================================================

    def graph_walk(
        self,
        root_node: str,
        depth: int = 4,
    ) -> List[str]:

        visited = set()
        out = []

        def dfs(node_id: str, d: int):

            if d > depth:
                return

            if node_id in visited:
                return

            visited.add(node_id)

            out.append(node_id)

            for edge in self.edges.get(
                node_id,
                [],
            ):

                dfs(edge.target, d + 1)

        dfs(root_node, 0)

        return out

    # ========================================================
    # VIRTUAL MEMORY
    # ========================================================

    def build_virtual_memory(
        self,
        layer_name: str,
        root_state72: str,
        depth: int = 4,
    ) -> List[GraphNode]:

        nearest = self.nearest_nodes(
            root_state72,
            top_k=1,
        )

        if not nearest:
            return []

        _, root = nearest[0]

        walked = self.graph_walk(
            root.node_id,
            depth=depth,
        )

        out = []

        for node_id in walked:

            node = self.nodes[node_id]

            node.sandbox_layers.add(
                layer_name
            )

            out.append(node)

        return out

    # ========================================================
    # RECEIPT IMPORT
    # ========================================================

    def import_receipt_node(
        self,
        receipt: ReceiptNode,
        modality: str = MODALITY_RUNTIME,
    ) -> str:

        node_id = self.insert_node(
            modality=modality,
            state_hash72=receipt.state_hash72,
            receipt_hash72=receipt.receipt_hash72,
            payload={
                "closure_score":
                    receipt.closure_score,

                "tensor_count":
                    receipt.tensor_count,

                "genomic_signature":
                    receipt.genomic_signature,

                "metadata":
                    receipt.metadata,
            }
        )

        if receipt.parent_signature:

            if receipt.parent_signature in self.cache.nodes:

                parent_receipt = (
                    self.cache.nodes[
                        receipt.parent_signature
                    ]
                )

                parent_node = self.insert_node(
                    modality=modality,
                    state_hash72=parent_receipt.state_hash72,
                    receipt_hash72=parent_receipt.receipt_hash72,
                    payload=parent_receipt.metadata,
                )

                self.connect(
                    parent_node,
                    node_id,
                    relation="receipt_chain",
                    weight=1.0,
                )

        return node_id

    # ========================================================
    # EXPORT
    # ========================================================

    def export_json(self) -> Dict:

        return {

            "node_count":
                len(self.nodes),

            "edge_count":
                sum(
                    len(v)
                    for v in self.edges.values()
                ),

            "modalities":
                {
                    k: len(v)
                    for k, v in self.modality_index.items()
                },

            "nodes": [
                {
                    "node_id":
                        n.node_id,

                    "modality":
                        n.modality,

                    "state_hash72":
                        n.state_hash72,

                    "receipt_hash72":
                        n.receipt_hash72,

                    "sandbox_layers":
                        list(n.sandbox_layers),
                }
                for n in self.nodes.values()
            ]
        }

# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    cache = HHSReceiptVectorCache()

    PREV = (
        "2jDWVX51QbuxI6>1pQ0y?oVxa4BELNQR2Q8ki)vi9X3tFrzLuC5JxQBpOUVm(ARNW8cEOYMW"
    )

    STATE = (
        "EYavwAcdQcwAMb3cxQ1A2s-DhcBFNQUuNrTWUA2*UAaBFsBOyHbQFQCtRY-s1IRRYbgfpznr"
    )

    RECEIPT = (
        "cVzbjxzEONoD!3(fQybgrehO>(Y3qDSBZphEI9j4Phf4s9y)qP(b<yd0F-1cBWkoo5mVdFpL"
    )

    sig = cache.insert_receipt(
        prev72=PREV,
        state72=STATE,
        receipt72=RECEIPT,
        witness_flags=0xFFFF,
        tensor_count=2,
        genomic_signature="1-12-14-71",
    )

    kernel = HHSMultimodalGraphKernel(
        cache=cache
    )

    receipt_node = cache.nodes[sig]

    runtime_node = kernel.import_receipt_node(
        receipt_node,
        modality=MODALITY_RUNTIME,
    )

    text_node = kernel.insert_node(
        modality=MODALITY_TEXT,
        state_hash72=STATE,
        receipt_hash72=RECEIPT,
        payload={
            "text":
                "harmonic runtime closure"
        }
    )

    kernel.connect(
        runtime_node,
        text_node,
        relation="semantic_projection",
        weight=0.95,
    )

    memory = kernel.build_virtual_memory(
        "sandbox_A",
        STATE,
        depth=3,
    )

    print("\n=== GRAPH SUMMARY ===")

    print(
        json.dumps(
            kernel.export_json(),
            indent=2,
        )
    )

    print("\n=== MEMORY LAYER ===")
    print(len(memory))