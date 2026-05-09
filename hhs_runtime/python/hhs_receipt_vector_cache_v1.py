# hhs_runtime/python/hhs_receipt_vector_cache_v1.py
#
# HARMONICODE / HHS
# Shared multimodal receipt-chain vector cache
#
# PURPOSE:
#   Deterministic receipt-chain storage layer for:
#
#   - VM execution traces
#   - successful closure states
#   - tensor evolution paths
#   - sandbox replay branches
#   - semantic/runtime retrieval
#   - adaptive prediction layers
#
# DESIGN:
#   - deterministic
#   - append-only
#   - replay stable
#   - graph searchable
#   - no hidden mutation
#   - all states linked by receipt hash
#
# ============================================================

from __future__ import annotations

import json
import math
import hashlib
import time

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple

# ============================================================
# IMPORTS
# ============================================================

from hhs_sprite_map_engine_v1 import (
    SpriteMap216,
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

HASH72_INDEX = {c: i for i, c in enumerate(HASH72)}

# ============================================================
# UTILS
# ============================================================

def wrap72(v: int) -> int:
    return v % 72


def hash72_distance(a: str, b: str) -> int:

    total = 0

    for x, y in zip(a, b):

        dx = HASH72_INDEX[x]
        dy = HASH72_INDEX[y]

        d = abs(dx - dy)

        total += min(d, 72 - d)

    return total


def sha256_hex(data: str) -> str:

    return hashlib.sha256(
        data.encode()
    ).hexdigest()


# ============================================================
# RECEIPT NODE
# ============================================================

@dataclass
class ReceiptNode:

    receipt_hash72: str

    prev_hash72: str
    state_hash72: str

    witness_flags: int

    timestamp: float

    replay_signature: str

    metadata: Dict = field(default_factory=dict)

    parent_signature: Optional[str] = None

    children: Set[str] = field(default_factory=set)

    sandbox_layers: Set[str] = field(default_factory=set)

    closure_score: float = 0.0

    tensor_count: int = 0

    genomic_signature: Optional[str] = None


# ============================================================
# VECTOR CACHE
# ============================================================

@dataclass
class HHSReceiptVectorCache:

    nodes: Dict[str, ReceiptNode] = field(
        default_factory=dict
    )

    sprite_maps: Dict[str, SpriteMap216] = field(
        default_factory=dict
    )

    receipt_index: Dict[str, str] = field(
        default_factory=dict
    )

    state_index: Dict[str, Set[str]] = field(
        default_factory=dict
    )

    sandbox_index: Dict[str, Set[str]] = field(
        default_factory=dict
    )

    closure_index: List[Tuple[float, str]] = field(
        default_factory=list
    )

    # ========================================================
    # INSERT
    # ========================================================

    def insert_receipt(
        self,
        prev72: str,
        state72: str,
        receipt72: str,
        witness_flags: int = 0,
        metadata: Optional[Dict] = None,
        parent_signature: Optional[str] = None,
        sandbox_layer: Optional[str] = None,
        tensor_count: int = 0,
        genomic_signature: Optional[str] = None,
    ) -> str:

        sprite = SpriteMap216.from_receipt_triplet(
            prev72,
            state72,
            receipt72,
            witness_flags=witness_flags,
        )

        replay_signature = sprite.replay_signature()

        closure_score = self.compute_closure_score(
            sprite
        )

        node = ReceiptNode(
            receipt_hash72=receipt72,
            prev_hash72=prev72,
            state_hash72=state72,
            witness_flags=witness_flags,
            timestamp=time.time(),
            replay_signature=replay_signature,
            metadata=metadata or {},
            parent_signature=parent_signature,
            closure_score=closure_score,
            tensor_count=tensor_count,
            genomic_signature=genomic_signature,
        )

        if sandbox_layer:
            node.sandbox_layers.add(sandbox_layer)

        self.nodes[replay_signature] = node

        self.sprite_maps[replay_signature] = sprite

        self.receipt_index[receipt72] = replay_signature

        if state72 not in self.state_index:
            self.state_index[state72] = set()

        self.state_index[state72].add(
            replay_signature
        )

        if sandbox_layer:

            if sandbox_layer not in self.sandbox_index:
                self.sandbox_index[sandbox_layer] = set()

            self.sandbox_index[sandbox_layer].add(
                replay_signature
            )

        if parent_signature:

            if parent_signature in self.nodes:

                self.nodes[parent_signature].children.add(
                    replay_signature
                )

        self.closure_index.append(
            (
                closure_score,
                replay_signature,
            )
        )

        self.closure_index.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        return replay_signature

    # ========================================================
    # CLOSURE
    # ========================================================

    def compute_closure_score(
        self,
        sprite: SpriteMap216
    ) -> float:

        vals = sprite.state_vector.values

        reciprocal_pairs = 0

        for i in range(len(vals)):

            a = vals[i]
            b = vals[(i + 36) % 72]

            if abs((a + 36) % 72 - b) <= 2:
                reciprocal_pairs += 1

        reciprocal_score = (
            reciprocal_pairs / 72.0
        )

        loshu = sprite.loshu_core

        row_sums = loshu.closure_sum_rows()
        col_sums = loshu.closure_sum_cols()

        target = sum(row_sums) / 3.0

        drift = 0.0

        for v in row_sums + col_sums:
            drift += abs(v - target)

        drift_score = 1.0 / (1.0 + drift)

        return (
            reciprocal_score * 0.6
            + drift_score * 0.4
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def search_nearest_state(
        self,
        state72: str,
        top_k: int = 10,
    ) -> List[Tuple[int, ReceiptNode]]:

        results = []

        for node in self.nodes.values():

            dist = hash72_distance(
                state72,
                node.state_hash72,
            )

            results.append((dist, node))

        results.sort(key=lambda x: x[0])

        return results[:top_k]

    def search_by_closure(
        self,
        min_score: float = 0.8,
    ) -> List[ReceiptNode]:

        out = []

        for score, sig in self.closure_index:

            if score < min_score:
                break

            out.append(self.nodes[sig])

        return out

    def search_by_sandbox(
        self,
        sandbox_name: str,
    ) -> List[ReceiptNode]:

        out = []

        refs = self.sandbox_index.get(
            sandbox_name,
            set()
        )

        for sig in refs:

            if sig in self.nodes:
                out.append(self.nodes[sig])

        return out

    def search_prediction_candidates(
        self,
        state72: str,
        witness_mask: Optional[int] = None,
        top_k: int = 8,
    ) -> List[ReceiptNode]:

        nearest = self.search_nearest_state(
            state72,
            top_k=64,
        )

        out = []

        for dist, node in nearest:

            if witness_mask is not None:

                if (
                    node.witness_flags
                    & witness_mask
                ) != witness_mask:
                    continue

            out.append(node)

            if len(out) >= top_k:
                break

        return out

    # ========================================================
    # SANDBOX
    # ========================================================

    def create_virtual_sandbox(
        self,
        name: str,
        root_signature: str,
        max_depth: int = 4,
    ) -> List[ReceiptNode]:

        if root_signature not in self.nodes:
            return []

        visited = set()

        out = []

        def dfs(sig: str, depth: int):

            if depth > max_depth:
                return

            if sig in visited:
                return

            visited.add(sig)

            node = self.nodes[sig]

            node.sandbox_layers.add(name)

            out.append(node)

            for child in node.children:
                dfs(child, depth + 1)

        dfs(root_signature, 0)

        self.sandbox_index[name] = visited

        return out

    # ========================================================
    # PREDICTION
    # ========================================================

    def predict_next_receipts(
        self,
        current_state72: str,
        top_k: int = 5,
    ) -> List[Tuple[float, ReceiptNode]]:

        candidates = self.search_prediction_candidates(
            current_state72,
            top_k=64,
        )

        out = []

        for node in candidates:

            dist = hash72_distance(
                current_state72,
                node.state_hash72,
            )

            similarity = 1.0 - (dist / (72.0 * 36.0))

            score = (
                similarity * 0.5
                + node.closure_score * 0.5
            )

            out.append((score, node))

        out.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        return out[:top_k]

    # ========================================================
    # EXPORT
    # ========================================================

    def export_json(self) -> Dict:

        return {
            "node_count": len(self.nodes),
            "sandbox_count": len(self.sandbox_index),
            "receipt_count": len(self.receipt_index),

            "nodes": [
                {
                    "replay_signature":
                        n.replay_signature,

                    "receipt_hash72":
                        n.receipt_hash72,

                    "state_hash72":
                        n.state_hash72,

                    "closure_score":
                        n.closure_score,

                    "children":
                        list(n.children),

                    "sandbox_layers":
                        list(n.sandbox_layers),
                }
                for n in self.nodes.values()
            ]
        }

    def save_json(
        self,
        path: str
    ) -> None:

        with open(path, "w") as f:

            json.dump(
                self.export_json(),
                f,
                indent=2,
            )


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
        metadata={
            "source": "vm81",
            "runtime": "freeze",
        },
        sandbox_layer="root",
        tensor_count=2,
        genomic_signature="1-12-14-71",
    )

    print("\n=== INSERTED ===")
    print(sig)

    preds = cache.predict_next_receipts(
        STATE
    )

    print("\n=== PREDICTIONS ===")

    for score, node in preds:

        print(
            f"{score:.4f}",
            node.replay_signature,
        )

    cache.create_virtual_sandbox(
        "branch_A",
        sig,
    )

    print("\n=== EXPORT ===")
    print(
        json.dumps(
            cache.export_json(),
            indent=2,
        )
    )