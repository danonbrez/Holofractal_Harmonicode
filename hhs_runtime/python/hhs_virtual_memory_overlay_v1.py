# hhs_runtime/python/hhs_virtual_memory_overlay_v1.py
#
# HARMONICODE / HHS
# Virtual Memory Overlay Engine
#
# PURPOSE:
#
#   Creates sandboxed predictive memory layers
#   over the HASH72 receipt-chain manifold.
#
# CORE:
#
#   successful validated execution traces become:
#
#       searchable
#       replayable
#       forkable
#       mergeable
#       predictive
#
#   without mutating canonical receipt history.
#
# ============================================================

from __future__ import annotations

import json
import math
import hashlib

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple

# ============================================================
# IMPORTS
# ============================================================

from hhs_multimodal_graph_kernel_v1 import (
    HHSMultimodalGraphKernel,
    GraphNode,
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
# MEMORY TRACE
# ============================================================

@dataclass
class MemoryTrace:

    trace_id: str

    root_state72: str

    node_sequence: List[str]

    closure_score: float

    modality_mix: Dict[str, int]

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# MEMORY OVERLAY
# ============================================================

@dataclass
class VirtualMemoryOverlay:

    layer_name: str

    active_nodes: Set[str] = field(
        default_factory=set
    )

    traces: Dict[str, MemoryTrace] = field(
        default_factory=dict
    )

    prediction_cache: Dict[str, List[str]] = field(
        default_factory=dict
    )

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# ENGINE
# ============================================================

@dataclass
class HHSVirtualMemoryOverlayEngine:

    graph: HHSMultimodalGraphKernel

    overlays: Dict[str, VirtualMemoryOverlay] = field(
        default_factory=dict
    )

    # ========================================================
    # CREATE OVERLAY
    # ========================================================

    def create_overlay(
        self,
        layer_name: str,
        metadata: Optional[Dict] = None,
    ) -> VirtualMemoryOverlay:

        overlay = VirtualMemoryOverlay(
            layer_name=layer_name,
            metadata=metadata or {},
        )

        self.overlays[layer_name] = overlay

        return overlay

    # ========================================================
    # BUILD OVERLAY
    # ========================================================

    def build_overlay_from_state(
        self,
        layer_name: str,
        root_state72: str,
        depth: int = 4,
    ) -> VirtualMemoryOverlay:

        if layer_name not in self.overlays:

            self.create_overlay(layer_name)

        overlay = self.overlays[layer_name]

        nearest = self.graph.nearest_nodes(
            root_state72,
            top_k=1,
        )

        if not nearest:
            return overlay

        _, root_node = nearest[0]

        walked = self.graph.graph_walk(
            root_node.node_id,
            depth=depth,
        )

        for node_id in walked:

            overlay.active_nodes.add(node_id)

            self.graph.nodes[
                node_id
            ].sandbox_layers.add(
                layer_name
            )

        return overlay

    # ========================================================
    # TRACE CAPTURE
    # ========================================================

    def capture_trace(
        self,
        layer_name: str,
        root_state72: str,
        depth: int = 6,
    ) -> Optional[MemoryTrace]:

        if layer_name not in self.overlays:
            return None

        overlay = self.overlays[layer_name]

        nearest = self.graph.nearest_nodes(
            root_state72,
            top_k=1,
        )

        if not nearest:
            return None

        _, root = nearest[0]

        sequence = self.graph.graph_walk(
            root.node_id,
            depth=depth,
        )

        closure_score = self.compute_trace_closure(
            sequence
        )

        modality_mix = {}

        for node_id in sequence:

            node = self.graph.nodes[node_id]

            modality_mix[node.modality] = (
                modality_mix.get(
                    node.modality,
                    0,
                ) + 1
            )

        trace_id = sha256_hex(
            root_state72
            + layer_name
            + str(sequence)
        )

        trace = MemoryTrace(
            trace_id=trace_id,
            root_state72=root_state72,
            node_sequence=sequence,
            closure_score=closure_score,
            modality_mix=modality_mix,
        )

        overlay.traces[trace_id] = trace

        return trace

    # ========================================================
    # TRACE CLOSURE
    # ========================================================

    def compute_trace_closure(
        self,
        sequence: List[str]
    ) -> float:

        if not sequence:
            return 0.0

        closure = 0.0

        for node_id in sequence:

            node = self.graph.nodes[node_id]

            payload = node.payload

            closure += float(
                payload.get(
                    "closure_score",
                    0.0,
                )
            )

        return closure / len(sequence)

    # ========================================================
    # PREDICT
    # ========================================================

    def predict_next_states(
        self,
        layer_name: str,
        state72: str,
        top_k: int = 8,
    ) -> List[Tuple[float, str]]:

        if layer_name not in self.overlays:
            return []

        overlay = self.overlays[layer_name]

        nearest = self.graph.nearest_nodes(
            state72,
            top_k=top_k,
        )

        out = []

        for dist, node in nearest:

            if node.node_id not in overlay.active_nodes:
                continue

            for edge in self.graph.edges.get(
                node.node_id,
                [],
            ):

                target = self.graph.nodes[
                    edge.target
                ]

                score = (
                    edge.weight
                    + (1.0 / (1.0 + dist))
                )

                out.append(
                    (
                        score,
                        target.state_hash72,
                    )
                )

        out.sort(
            key=lambda x: -x[0]
        )

        return out[:top_k]

    # ========================================================
    # OVERLAY MERGE
    # ========================================================

    def merge_overlays(
        self,
        A: str,
        B: str,
        out_name: str,
    ) -> Optional[VirtualMemoryOverlay]:

        if A not in self.overlays:
            return None

        if B not in self.overlays:
            return None

        OA = self.overlays[A]
        OB = self.overlays[B]

        OUT = self.create_overlay(
            out_name
        )

        OUT.active_nodes = (
            OA.active_nodes
            | OB.active_nodes
        )

        OUT.traces.update(OA.traces)
        OUT.traces.update(OB.traces)

        return OUT

    # ========================================================
    # EXPORT
    # ========================================================

    def export_overlay_json(
        self,
        layer_name: str,
    ) -> Dict:

        if layer_name not in self.overlays:
            return {}

        overlay = self.overlays[layer_name]

        return {

            "layer_name":
                overlay.layer_name,

            "node_count":
                len(overlay.active_nodes),

            "trace_count":
                len(overlay.traces),

            "nodes":
                list(overlay.active_nodes),

            "traces": [
                {
                    "trace_id":
                        t.trace_id,

                    "closure_score":
                        t.closure_score,

                    "modality_mix":
                        t.modality_mix,

                    "length":
                        len(t.node_sequence),
                }
                for t in overlay.traces.values()
            ]
        }

# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    from hhs_receipt_vector_cache_v1 import (
        HHSReceiptVectorCache
    )

    from hhs_multimodal_graph_kernel_v1 import (
        HHSMultimodalGraphKernel,
        MODALITY_RUNTIME,
        MODALITY_TEXT,
    )

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

    graph = HHSMultimodalGraphKernel(
        cache=cache
    )

    receipt_node = cache.nodes[sig]

    runtime_node = graph.import_receipt_node(
        receipt_node,
        modality=MODALITY_RUNTIME,
    )

    text_node = graph.insert_node(
        modality=MODALITY_TEXT,
        state_hash72=STATE,
        receipt_hash72=RECEIPT,
        payload={
            "text":
                "closure manifold runtime"
        }
    )

    graph.connect(
        runtime_node,
        text_node,
        relation="semantic_projection",
        weight=0.95,
    )

    engine = HHSVirtualMemoryOverlayEngine(
        graph=graph
    )

    engine.build_overlay_from_state(
        "sandbox_A",
        STATE,
        depth=4,
    )

    trace = engine.capture_trace(
        "sandbox_A",
        STATE,
        depth=4,
    )

    print("\n=== TRACE ===")

    print(trace)

    print("\n=== PREDICTIONS ===")

    preds = engine.predict_next_states(
        "sandbox_A",
        STATE,
    )

    for p in preds:
        print(p)

    print("\n=== EXPORT ===")

    print(
        json.dumps(
            engine.export_overlay_json(
                "sandbox_A"
            ),
            indent=2,
        )
    )