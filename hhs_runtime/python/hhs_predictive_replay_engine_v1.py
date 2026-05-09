# hhs_runtime/python/hhs_predictive_replay_engine_v1.py
#
# HARMONICODE / HHS
# Predictive Replay + Trace Projection Engine
#
# PURPOSE:
#
#   Replays validated HASH72 execution traces
#   and predicts future closure-compatible states
#   using:
#
#       receipt-chain continuity
#       graph-neighborhood projection
#       modality-consensus filtering
#       closure-weighted branch scoring
#
# ============================================================

from __future__ import annotations

import math
import json
import hashlib

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set

# ============================================================
# IMPORTS
# ============================================================

from hhs_virtual_memory_overlay_v1 import (
    HHSVirtualMemoryOverlayEngine,
)

from hhs_multimodal_graph_kernel_v1 import (
    HHSMultimodalGraphKernel,
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

# ============================================================
# UTILS
# ============================================================

def sha256_hex(data: str) -> str:

    return hashlib.sha256(
        data.encode()
    ).hexdigest()

# ============================================================
# REPLAY NODE
# ============================================================

@dataclass
class ReplayProjection:

    state72: str

    score: float

    depth: int

    source_trace: str

    modality_consensus: float

    closure_score: float

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# ENGINE
# ============================================================

@dataclass
class HHSPredictiveReplayEngine:

    graph: HHSMultimodalGraphKernel

    overlays: HHSVirtualMemoryOverlayEngine

    replay_cache: Dict[
        str,
        List[ReplayProjection]
    ] = field(
        default_factory=dict
    )

    # ========================================================
    # TRACE REPLAY
    # ========================================================

    def replay_trace(
        self,
        overlay_name: str,
        trace_id: str,
        future_depth: int = 4,
    ) -> List[ReplayProjection]:

        if overlay_name not in self.overlays.overlays:
            return []

        overlay = self.overlays.overlays[
            overlay_name
        ]

        if trace_id not in overlay.traces:
            return []

        trace = overlay.traces[trace_id]

        if not trace.node_sequence:
            return []

        terminal_node = trace.node_sequence[-1]

        visited = set()

        projections: List[
            ReplayProjection
        ] = []

        self._recursive_project(
            overlay_name=overlay_name,
            current_node=terminal_node,
            current_depth=0,
            max_depth=future_depth,
            visited=visited,
            projections=projections,
            source_trace=trace_id,
        )

        projections.sort(
            key=lambda p: -p.score
        )

        cache_key = (
            overlay_name
            + ":"
            + trace_id
        )

        self.replay_cache[
            cache_key
        ] = projections

        return projections

    # ========================================================
    # INTERNAL PROJECT
    # ========================================================

    def _recursive_project(
        self,
        overlay_name: str,
        current_node: str,
        current_depth: int,
        max_depth: int,
        visited: Set[str],
        projections: List[ReplayProjection],
        source_trace: str,
    ):

        if current_depth >= max_depth:
            return

        if current_node in visited:
            return

        visited.add(current_node)

        overlay = self.overlays.overlays[
            overlay_name
        ]

        edges = self.graph.edges.get(
            current_node,
            [],
        )

        for edge in edges:

            target = edge.target

            if target not in overlay.active_nodes:
                continue

            node = self.graph.nodes[target]

            closure_score = float(
                node.payload.get(
                    "closure_score",
                    0.0,
                )
            )

            modality_consensus = (
                self.compute_modality_consensus(
                    target
                )
            )

            score = (
                edge.weight
                * 0.50
                + closure_score * 0.30
                + modality_consensus * 0.20
            )

            projection = ReplayProjection(

                state72=node.state_hash72,

                score=score,

                depth=current_depth + 1,

                source_trace=source_trace,

                modality_consensus=
                    modality_consensus,

                closure_score=
                    closure_score,

                metadata={
                    "node_id":
                        target,
                    "relation":
                        edge.relation,
                }
            )

            projections.append(
                projection
            )

            self._recursive_project(
                overlay_name,
                target,
                current_depth + 1,
                max_depth,
                visited,
                projections,
                source_trace,
            )

    # ========================================================
    # MODALITY CONSENSUS
    # ========================================================

    def compute_modality_consensus(
        self,
        node_id: str
    ) -> float:

        node = self.graph.nodes[node_id]

        state72 = node.state_hash72

        same_state = []

        for n in self.graph.nodes.values():

            if n.state_hash72 == state72:
                same_state.append(n)

        if not same_state:
            return 0.0

        modalities = set(
            n.modality
            for n in same_state
        )

        return min(
            1.0,
            len(modalities) / 8.0
        )

    # ========================================================
    # BEST FUTURE STATE
    # ========================================================

    def best_future_state(
        self,
        overlay_name: str,
        trace_id: str,
    ) -> Optional[ReplayProjection]:

        projections = self.replay_trace(
            overlay_name,
            trace_id,
        )

        if not projections:
            return None

        return projections[0]

    # ========================================================
    # CONSENSUS FILTER
    # ========================================================

    def consensus_filter(
        self,
        projections: List[ReplayProjection],
        minimum_consensus: float = 0.25,
    ) -> List[ReplayProjection]:

        out = []

        for p in projections:

            if (
                p.modality_consensus
                >= minimum_consensus
            ):
                out.append(p)

        return out

    # ========================================================
    # CLOSURE FILTER
    # ========================================================

    def closure_filter(
        self,
        projections: List[ReplayProjection],
        minimum_closure: float = 0.50,
    ) -> List[ReplayProjection]:

        out = []

        for p in projections:

            if (
                p.closure_score
                >= minimum_closure
            ):
                out.append(p)

        return out

    # ========================================================
    # EXPORT
    # ========================================================

    def export_projection_json(
        self,
        projections: List[ReplayProjection],
    ) -> Dict:

        return {

            "projection_count":
                len(projections),

            "projections": [

                {

                    "state72":
                        p.state72,

                    "score":
                        p.score,

                    "depth":
                        p.depth,

                    "closure_score":
                        p.closure_score,

                    "modality_consensus":
                        p.modality_consensus,

                    "source_trace":
                        p.source_trace,

                    "metadata":
                        p.metadata,
                }

                for p in projections
            ]
        }

# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    from hhs_receipt_vector_cache_v1 import (
        HHSReceiptVectorCache,
    )

    from hhs_multimodal_graph_kernel_v1 import (
        HHSMultimodalGraphKernel,
        MODALITY_RUNTIME,
        MODALITY_TEXT,
        MODALITY_AUDIO,
    )

    from hhs_virtual_memory_overlay_v1 import (
        HHSVirtualMemoryOverlayEngine,
    )

    cache = HHSReceiptVectorCache()

    graph = HHSMultimodalGraphKernel(
        cache=cache
    )

    # ========================================================
    # INSERT TEST NODES
    # ========================================================

    A = graph.insert_node(
        modality=MODALITY_RUNTIME,
        state_hash72=
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        receipt_hash72=
            "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        payload={
            "closure_score": 0.95
        }
    )

    B = graph.insert_node(
        modality=MODALITY_TEXT,
        state_hash72=
            "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        receipt_hash72=
            "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",
        payload={
            "closure_score": 0.82
        }
    )

    C = graph.insert_node(
        modality=MODALITY_AUDIO,
        state_hash72=
            "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE",
        receipt_hash72=
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
        payload={
            "closure_score": 0.77
        }
    )

    graph.connect(
        A,
        B,
        relation="semantic",
        weight=0.95,
    )

    graph.connect(
        B,
        C,
        relation="projection",
        weight=0.88,
    )

    overlays = HHSVirtualMemoryOverlayEngine(
        graph=graph
    )

    overlays.create_overlay(
        "sandbox_predictive"
    )

    overlays.build_overlay_from_state(
        "sandbox_predictive",
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        depth=6,
    )

    trace = overlays.capture_trace(
        "sandbox_predictive",
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        depth=6,
    )

    engine = HHSPredictiveReplayEngine(

        graph=graph,
        overlays=overlays,
    )

    projections = engine.replay_trace(
        "sandbox_predictive",
        trace.trace_id,
        future_depth=5,
    )

    projections = engine.consensus_filter(
        projections,
        minimum_consensus=0.10,
    )

    projections = engine.closure_filter(
        projections,
        minimum_closure=0.50,
    )

    print("\n=== FUTURE PROJECTIONS ===\n")

    for p in projections:

        print(
            p.depth,
            round(p.score, 4),
            round(p.closure_score, 4),
            round(p.modality_consensus, 4),
            p.state72[:24],
        )

    print("\n=== EXPORT ===\n")

    print(
        json.dumps(
            engine.export_projection_json(
                projections
            ),
            indent=2,
        )
    )