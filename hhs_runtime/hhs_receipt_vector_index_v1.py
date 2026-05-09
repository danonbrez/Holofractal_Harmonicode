# hhs_runtime/hhs_receipt_vector_index_v1.py
#
# HARMONICODE / HHS
# Receipt Vector Index v1
#
# Canonical memory geometry layer.
#
# Receipts are the ONLY canonical memory anchors.
#
# This layer stores:
#
#   receipt_hash72
#   state_hash72
#   witness topology
#   execution traces
#   replay vectors
#   semantic embeddings
#
# All adaptive prediction layers MUST route through here.
#

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

# ============================================================
# VECTOR NODE
# ============================================================


@dataclass
class HHSVectorNode:

    receipt_hash72: str

    state_hash72: str

    timestamp: float

    witness_flags: int

    route_trace: List[str]

    vector: List[float]

    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================
# RECEIPT VECTOR INDEX
# ============================================================


class HHSReceiptVectorIndex:

    """
    Canonical receipt memory graph.

    All replay prediction layers route through this system.
    """

    def __init__(self):

        self.nodes: Dict[str, HHSVectorNode] = {}

        self.state_lookup: Dict[str, List[str]] = {}

        self.route_lookup: Dict[str, List[str]] = {}

    # ========================================================
    # INSERT
    # ========================================================

    def insert_receipt(self, receipt):

        vector = self.compute_receipt_vector(receipt)

        node = HHSVectorNode(
            receipt_hash72=receipt.receipt_hash72,
            state_hash72=receipt.state_hash72,
            timestamp=time.time(),
            witness_flags=receipt.witness_flags,
            route_trace=receipt.route_trace,
            vector=vector,
            metadata={
                "validation_passed":
                    receipt.validation_passed,
            },
        )

        self.nodes[receipt.receipt_hash72] = node

        # ----------------------------------------------------
        # STATE LOOKUP
        # ----------------------------------------------------

        if receipt.state_hash72 not in self.state_lookup:
            self.state_lookup[receipt.state_hash72] = []

        self.state_lookup[
            receipt.state_hash72
        ].append(receipt.receipt_hash72)

        # ----------------------------------------------------
        # ROUTE LOOKUP
        # ----------------------------------------------------

        for stage in receipt.route_trace:

            if stage not in self.route_lookup:
                self.route_lookup[stage] = []

            self.route_lookup[stage].append(
                receipt.receipt_hash72
            )

    # ========================================================
    # VECTOR COMPUTE
    # ========================================================

    def compute_receipt_vector(
        self,
        receipt,
    ) -> List[float]:

        vector = []

        # ----------------------------------------------------
        # HASH72 RECEIPT VECTOR
        # ----------------------------------------------------

        for ch in receipt.receipt_hash72[:72]:

            v = ord(ch) / 127.0

            vector.append(v)

        # ----------------------------------------------------
        # HASH72 STATE VECTOR
        # ----------------------------------------------------

        for ch in receipt.state_hash72[:72]:

            v = ord(ch) / 127.0

            vector.append(v)

        # ----------------------------------------------------
        # WITNESS VECTOR
        # ----------------------------------------------------

        for bit in range(32):

            b = (
                receipt.witness_flags >> bit
            ) & 1

            vector.append(float(b))

        return vector

    # ========================================================
    # SEARCH
    # ========================================================

    def search_nearest(
        self,
        vector: List[float],
        limit: int = 8,
    ) -> List[HHSVectorNode]:

        scored = []

        for node in self.nodes.values():

            dist = self.vector_distance(
                vector,
                node.vector,
            )

            scored.append((dist, node))

        scored.sort(key=lambda x: x[0])

        return [
            node
            for _, node in scored[:limit]
        ]

    # ========================================================
    # DISTANCE
    # ========================================================

    def vector_distance(
        self,
        a: List[float],
        b: List[float],
    ) -> float:

        n = min(len(a), len(b))

        if n == 0:
            return float("inf")

        acc = 0.0

        for i in range(n):

            d = a[i] - b[i]

            acc += d * d

        return math.sqrt(acc)

    # ========================================================
    # RECEIPT LOOKUP
    # ========================================================

    def get_receipt_node(
        self,
        receipt_hash72: str,
    ) -> Optional[HHSVectorNode]:

        return self.nodes.get(receipt_hash72)

    # ========================================================
    # STATE LOOKUP
    # ========================================================

    def get_state_cluster(
        self,
        state_hash72: str,
    ) -> List[HHSVectorNode]:

        refs = self.state_lookup.get(
            state_hash72,
            [],
        )

        out = []

        for ref in refs:

            node = self.nodes.get(ref)

            if node:
                out.append(node)

        return out

    # ========================================================
    # ROUTE LOOKUP
    # ========================================================

    def get_route_cluster(
        self,
        route_stage: str,
    ) -> List[HHSVectorNode]:

        refs = self.route_lookup.get(
            route_stage,
            [],
        )

        out = []

        for ref in refs:

            node = self.nodes.get(ref)

            if node:
                out.append(node)

        return out

    # ========================================================
    # STATS
    # ========================================================

    def stats(self):

        return {
            "node_count":
                len(self.nodes),

            "state_clusters":
                len(self.state_lookup),

            "route_clusters":
                len(self.route_lookup),
        }

# ============================================================
# SINGLETON
# ============================================================

_VECTOR_INDEX_SINGLETON = None


def get_receipt_vector_index():

    global _VECTOR_INDEX_SINGLETON

    if _VECTOR_INDEX_SINGLETON is None:

        _VECTOR_INDEX_SINGLETON = (
            HHSReceiptVectorIndex()
        )

    return _VECTOR_INDEX_SINGLETON

# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":

    idx = HHSReceiptVectorIndex()

    print(idx.stats())