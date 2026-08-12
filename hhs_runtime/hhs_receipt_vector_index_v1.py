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
# Pass 216 / Pass 217 authority repair:
#   - no floats in authoritative indexing, scoring, or selection;
#   - integer nanoseconds replace floating wall-clock timestamps;
#   - receipt/state characters are represented by exact ordinals;
#   - witness bits are scaled by 127 so squared integer distance is exactly
#     proportional to the historical normalized Euclidean metric;
#   - ranking uses squared distance, avoiding sqrt without changing order.

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence


MAX_INTEGER_DISTANCE = (1 << 256) - 1
WITNESS_SCALE = 127


# ============================================================
# VECTOR NODE
# ============================================================


@dataclass
class HHSVectorNode:
    receipt_hash72: str
    state_hash72: str
    timestamp: int
    witness_flags: int
    route_trace: List[str]
    vector: List[int]
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# RECEIPT VECTOR INDEX
# ============================================================


class HHSReceiptVectorIndex:
    """Canonical receipt memory graph with exact integer indexing.

    The historical implementation normalized character ordinals by ``127.0``
    and used floating Euclidean distance.  Multiplying that entire metric by
    127 yields an equivalent integer geometry when character coordinates are
    stored as ``ord(ch)`` and binary witness coordinates as ``127 * bit``.
    Squared distance is monotonic with Euclidean distance, so ranking is
    preserved without floating-point canonical authority.
    """

    def __init__(self):
        self.nodes: Dict[str, HHSVectorNode] = {}
        self.state_lookup: Dict[str, List[str]] = {}
        self.route_lookup: Dict[str, List[str]] = {}

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def _require_integer_vector(vector: Sequence[int]) -> None:
        if isinstance(vector, (str, bytes, bytearray)):
            raise TypeError("HHS_RECEIPT_VECTOR_INTEGER_SEQUENCE_REQUIRED")
        for value in vector:
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError("HHS_RECEIPT_VECTOR_FLOAT_OR_NONINTEGER_FORBIDDEN")

    @staticmethod
    def _canonical_bytes(value: Any) -> bytes:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

    # ========================================================
    # INSERT
    # ========================================================

    def insert_receipt(self, receipt):
        if not bool(getattr(receipt, "validation_passed", False)):
            raise ValueError("HHS_RECEIPT_VECTOR_UNVALIDATED_RECEIPT_FORBIDDEN")

        receipt_hash72 = str(getattr(receipt, "receipt_hash72", ""))
        state_hash72 = str(getattr(receipt, "state_hash72", ""))
        if not receipt_hash72 or not state_hash72:
            raise ValueError("HHS_RECEIPT_VECTOR_RECEIPT_OR_STATE_HASH_MISSING")

        witness_flags = getattr(receipt, "witness_flags", None)
        if not isinstance(witness_flags, int) or isinstance(witness_flags, bool) or witness_flags < 0:
            raise TypeError("HHS_RECEIPT_VECTOR_WITNESS_FLAGS_NONINTEGER")

        route_trace = [str(stage) for stage in list(getattr(receipt, "route_trace", []) or [])]
        vector = self.compute_receipt_vector(receipt)

        node = HHSVectorNode(
            receipt_hash72=receipt_hash72,
            state_hash72=state_hash72,
            timestamp=time.time_ns(),
            witness_flags=witness_flags,
            route_trace=route_trace,
            vector=vector,
            metadata={"validation_passed": True},
        )

        existing = self.nodes.get(receipt_hash72)
        if existing is not None:
            if (
                existing.state_hash72 != node.state_hash72
                or existing.witness_flags != node.witness_flags
                or existing.route_trace != node.route_trace
                or existing.vector != node.vector
            ):
                raise ValueError("HHS_RECEIPT_VECTOR_RECEIPT_HASH_IDENTITY_CONFLICT")
            return existing

        self.nodes[receipt_hash72] = node
        self.state_lookup.setdefault(state_hash72, []).append(receipt_hash72)
        for stage in route_trace:
            self.route_lookup.setdefault(stage, []).append(receipt_hash72)
        return node

    # ========================================================
    # VECTOR COMPUTE
    # ========================================================

    def compute_receipt_vector(self, receipt) -> List[int]:
        receipt_hash72 = str(getattr(receipt, "receipt_hash72", ""))
        state_hash72 = str(getattr(receipt, "state_hash72", ""))
        witness_flags = getattr(receipt, "witness_flags", None)
        if not isinstance(witness_flags, int) or isinstance(witness_flags, bool) or witness_flags < 0:
            raise TypeError("HHS_RECEIPT_VECTOR_WITNESS_FLAGS_NONINTEGER")

        vector: List[int] = []

        # Historical coordinate ord(ch)/127.0 multiplied by 127 exactly.
        vector.extend(ord(ch) for ch in receipt_hash72[:72])
        vector.extend(ord(ch) for ch in state_hash72[:72])

        # Historical binary 0.0/1.0 multiplied by 127 exactly.
        for bit in range(32):
            vector.append(WITNESS_SCALE * ((witness_flags >> bit) & 1))

        self._require_integer_vector(vector)
        return vector

    # ========================================================
    # SEARCH
    # ========================================================

    def search_nearest(self, vector: Sequence[int], limit: int = 8) -> List[HHSVectorNode]:
        self._require_integer_vector(vector)
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("HHS_RECEIPT_VECTOR_LIMIT_INVALID")

        scored = []
        for node in self.nodes.values():
            dist = self.vector_distance(vector, node.vector)
            scored.append((dist, node.receipt_hash72, node))

        # Receipt identity is an exact deterministic tie breaker.
        scored.sort(key=lambda item: (item[0], item[1]))
        return [node for _, _, node in scored[:limit]]

    # ========================================================
    # DISTANCE
    # ========================================================

    def vector_distance(self, a: Sequence[int], b: Sequence[int]) -> int:
        self._require_integer_vector(a)
        self._require_integer_vector(b)
        n = min(len(a), len(b))
        if n == 0:
            return MAX_INTEGER_DISTANCE

        acc = 0
        for i in range(n):
            d = int(a[i]) - int(b[i])
            acc += d * d
        return acc

    # ========================================================
    # RECEIPT LOOKUP
    # ========================================================

    def get_receipt_node(self, receipt_hash72: str) -> Optional[HHSVectorNode]:
        return self.nodes.get(str(receipt_hash72))

    # ========================================================
    # STATE LOOKUP
    # ========================================================

    def get_state_cluster(self, state_hash72: str) -> List[HHSVectorNode]:
        refs = self.state_lookup.get(str(state_hash72), [])
        return [self.nodes[ref] for ref in refs if ref in self.nodes]

    # ========================================================
    # ROUTE LOOKUP
    # ========================================================

    def get_route_cluster(self, route_stage: str) -> List[HHSVectorNode]:
        refs = self.route_lookup.get(str(route_stage), [])
        return [self.nodes[ref] for ref in refs if ref in self.nodes]

    # ========================================================
    # CANONICAL INDEX ROOT
    # ========================================================

    def index_root_hash216(self) -> str:
        """Return an exact SHA-256 identity for semantic index contents.

        Observational timestamps are deliberately excluded: two indexes with
        the same validated receipt/state/route geometry have the same root.
        """

        payload = {
            "schema": "HHS_RECEIPT_VECTOR_INDEX_EXACT_INTEGER_V1",
            "distance_metric": "SQUARED_INTEGER_EQUIVALENT_OF_NORMALIZED_EUCLIDEAN_V1",
            "witness_scale": WITNESS_SCALE,
            "nodes": [
                {
                    "receipt_hash72": node.receipt_hash72,
                    "state_hash72": node.state_hash72,
                    "witness_flags": node.witness_flags,
                    "route_trace": list(node.route_trace),
                    "vector": list(node.vector),
                    "validation_passed": bool(node.metadata.get("validation_passed")),
                }
                for _, node in sorted(self.nodes.items())
            ],
        }
        framed = b"HHS-RECEIPT-VECTOR-INDEX-HASH216-V1\0" + self._canonical_bytes(payload)
        return hashlib.sha256(framed).hexdigest()

    # ========================================================
    # STATS
    # ========================================================

    def stats(self):
        return {
            "node_count": len(self.nodes),
            "state_clusters": len(self.state_lookup),
            "route_clusters": len(self.route_lookup),
            "numeric_authority": "EXACT_INTEGER_ONLY",
            "index_root_hash216": self.index_root_hash216(),
        }


# ============================================================
# SINGLETON
# ============================================================

_VECTOR_INDEX_SINGLETON = None


def get_receipt_vector_index():
    global _VECTOR_INDEX_SINGLETON
    if _VECTOR_INDEX_SINGLETON is None:
        _VECTOR_INDEX_SINGLETON = HHSReceiptVectorIndex()
    return _VECTOR_INDEX_SINGLETON


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":
    idx = HHSReceiptVectorIndex()
    print(idx.stats())
