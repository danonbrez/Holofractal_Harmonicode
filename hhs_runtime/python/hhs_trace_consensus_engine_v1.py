# hhs_runtime/python/hhs_trace_consensus_engine_v1.py
#
# HARMONICODE / HHS
# Trace Consensus + Multi-Agent Closure Engine
#
# PURPOSE:
#
#   Executes closure voting across:
#
#       runtime traces
#       replay predictions
#       multimodal graph projections
#       virtual overlays
#       receipt continuity
#
#   Produces:
#
#       consensus-approved state transitions
#       weighted closure projections
#       branch rejection filtering
#       replay stabilization
#
# ============================================================

from __future__ import annotations

import math
import json
import hashlib

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

# ============================================================
# IMPORTS
# ============================================================

from hhs_predictive_replay_engine_v1 import (
    HHSPredictiveReplayEngine,
    ReplayProjection,
)

from hhs_virtual_memory_overlay_v1 import (
    HHSVirtualMemoryOverlayEngine,
)

from hhs_multimodal_graph_kernel_v1 import (
    HHSMultimodalGraphKernel,
)

# ============================================================
# CONSENSUS TYPES
# ============================================================

CONSENSUS_ACCEPT = "accept"
CONSENSUS_REJECT = "reject"
CONSENSUS_UNSTABLE = "unstable"

# ============================================================
# AGENT VOTE
# ============================================================

@dataclass
class HHSTraceVote:

    agent_id: str

    state72: str

    decision: str

    confidence: float

    closure_score: float

    modality_consensus: float

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# CONSENSUS RESULT
# ============================================================

@dataclass
class HHSConsensusResult:

    state72: str

    final_decision: str

    final_score: float

    accepted_votes: int

    rejected_votes: int

    unstable_votes: int

    total_votes: int

    vote_details: List[HHSTraceVote]

    metadata: Dict = field(
        default_factory=dict
    )

# ============================================================
# ENGINE
# ============================================================

@dataclass
class HHSTraceConsensusEngine:

    replay_engine: HHSPredictiveReplayEngine

    graph: HHSMultimodalGraphKernel

    overlays: HHSVirtualMemoryOverlayEngine

    # ========================================================
    # MULTI-AGENT CONSENSUS
    # ========================================================

    def run_consensus(
        self,
        overlay_name: str,
        trace_id: str,
        agent_count: int = 5,
        future_depth: int = 5,
    ) -> List[HHSConsensusResult]:

        projections = (
            self.replay_engine.replay_trace(
                overlay_name=overlay_name,
                trace_id=trace_id,
                future_depth=future_depth,
            )
        )

        grouped = self.group_by_state(
            projections
        )

        results = []

        for state72, plist in grouped.items():

            votes = self.generate_votes(
                state72,
                plist,
                agent_count,
            )

            result = self.resolve_votes(
                state72,
                votes,
            )

            results.append(result)

        results.sort(
            key=lambda r: -r.final_score
        )

        return results

    # ========================================================
    # GROUP STATES
    # ========================================================

    def group_by_state(
        self,
        projections: List[ReplayProjection],
    ) -> Dict[str, List[ReplayProjection]]:

        grouped = {}

        for p in projections:

            grouped.setdefault(
                p.state72,
                []
            ).append(p)

        return grouped

    # ========================================================
    # GENERATE AGENT VOTES
    # ========================================================

    def generate_votes(
        self,
        state72: str,
        projections: List[ReplayProjection],
        agent_count: int,
    ) -> List[HHSTraceVote]:

        votes = []

        for idx in range(agent_count):

            agent_id = f"agent_{idx}"

            confidence = (
                self.compute_agent_confidence(
                    projections,
                    idx,
                )
            )

            closure_score = (
                self.average_closure(
                    projections
                )
            )

            modality_consensus = (
                self.average_modality(
                    projections
                )
            )

            decision = self.make_decision(
                confidence,
                closure_score,
                modality_consensus,
            )

            vote = HHSTraceVote(

                agent_id=agent_id,

                state72=state72,

                decision=decision,

                confidence=confidence,

                closure_score=
                    closure_score,

                modality_consensus=
                    modality_consensus,

                metadata={
                    "projection_count":
                        len(projections)
                }
            )

            votes.append(vote)

        return votes

    # ========================================================
    # CONFIDENCE
    # ========================================================

    def compute_agent_confidence(
        self,
        projections: List[ReplayProjection],
        agent_index: int,
    ) -> float:

        if not projections:
            return 0.0

        total = 0.0

        for p in projections:

            modifier = (
                1.0
                - (agent_index * 0.03)
            )

            total += (
                p.score * modifier
            )

        return min(
            1.0,
            total / len(projections)
        )

    # ========================================================
    # AVERAGES
    # ========================================================

    def average_closure(
        self,
        projections: List[ReplayProjection],
    ) -> float:

        if not projections:
            return 0.0

        return sum(
            p.closure_score
            for p in projections
        ) / len(projections)

    def average_modality(
        self,
        projections: List[ReplayProjection],
    ) -> float:

        if not projections:
            return 0.0

        return sum(
            p.modality_consensus
            for p in projections
        ) / len(projections)

    # ========================================================
    # DECISION
    # ========================================================

    def make_decision(
        self,
        confidence: float,
        closure_score: float,
        modality_consensus: float,
    ) -> str:

        composite = (

            confidence * 0.40
            + closure_score * 0.35
            + modality_consensus * 0.25
        )

        if composite >= 0.70:
            return CONSENSUS_ACCEPT

        if composite >= 0.45:
            return CONSENSUS_UNSTABLE

        return CONSENSUS_REJECT

    # ========================================================
    # RESOLVE
    # ========================================================

    def resolve_votes(
        self,
        state72: str,
        votes: List[HHSTraceVote],
    ) -> HHSConsensusResult:

        accept = 0
        reject = 0
        unstable = 0

        score = 0.0

        for v in votes:

            score += v.confidence

            if v.decision == CONSENSUS_ACCEPT:
                accept += 1

            elif v.decision == CONSENSUS_REJECT:
                reject += 1

            else:
                unstable += 1

        total = len(votes)

        final_score = score / max(1, total)

        if accept > reject and accept >= unstable:
            final_decision = CONSENSUS_ACCEPT

        elif reject > accept:
            final_decision = CONSENSUS_REJECT

        else:
            final_decision = CONSENSUS_UNSTABLE

        return HHSConsensusResult(

            state72=state72,

            final_decision=
                final_decision,

            final_score=
                final_score,

            accepted_votes=
                accept,

            rejected_votes=
                reject,

            unstable_votes=
                unstable,

            total_votes=
                total,

            vote_details=
                votes,

            metadata={
                "accept_ratio":
                    accept / max(1, total),
            }
        )

    # ========================================================
    # FILTER ACCEPTED
    # ========================================================

    def accepted_results(
        self,
        results: List[HHSConsensusResult],
    ) -> List[HHSConsensusResult]:

        return [

            r for r in results

            if r.final_decision
                == CONSENSUS_ACCEPT
        ]

    # ========================================================
    # FILTER STABLE
    # ========================================================

    def stable_results(
        self,
        results: List[HHSConsensusResult],
        minimum_score: float = 0.75,
    ) -> List[HHSConsensusResult]:

        return [

            r for r in results

            if (
                r.final_score
                >= minimum_score
            )
        ]

    # ========================================================
    # EXPORT
    # ========================================================

    def export_results_json(
        self,
        results: List[HHSConsensusResult],
    ) -> Dict:

        return {

            "result_count":
                len(results),

            "results": [

                {

                    "state72":
                        r.state72,

                    "decision":
                        r.final_decision,

                    "score":
                        r.final_score,

                    "accepted":
                        r.accepted_votes,

                    "rejected":
                        r.rejected_votes,

                    "unstable":
                        r.unstable_votes,

                    "votes":
                        r.total_votes,
                }

                for r in results
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
    )

    from hhs_virtual_memory_overlay_v1 import (
        HHSVirtualMemoryOverlayEngine,
    )

    cache = HHSReceiptVectorCache()

    graph = HHSMultimodalGraphKernel(
        cache=cache
    )

    node_a = graph.insert_node(

        modality=MODALITY_RUNTIME,

        state_hash72=
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",

        receipt_hash72=
            "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",

        payload={
            "closure_score": 0.95
        }
    )

    node_b = graph.insert_node(

        modality=MODALITY_TEXT,

        state_hash72=
            "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",

        receipt_hash72=
            "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",

        payload={
            "closure_score": 0.80
        }
    )

    graph.connect(
        node_a,
        node_b,
        relation="semantic",
        weight=0.90,
    )

    overlays = HHSVirtualMemoryOverlayEngine(
        graph=graph
    )

    overlays.create_overlay(
        "sandbox_consensus"
    )

    overlays.build_overlay_from_state(
        "sandbox_consensus",
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        depth=4,
    )

    trace = overlays.capture_trace(
        "sandbox_consensus",
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        depth=4,
    )

    replay_engine = HHSPredictiveReplayEngine(

        graph=graph,
        overlays=overlays,
    )

    consensus_engine = HHSTraceConsensusEngine(

        replay_engine=replay_engine,

        graph=graph,

        overlays=overlays,
    )

    results = consensus_engine.run_consensus(

        overlay_name="sandbox_consensus",

        trace_id=trace.trace_id,

        agent_count=7,

        future_depth=5,
    )

    print("\n=== CONSENSUS RESULTS ===\n")

    for r in results:

        print(
            r.final_decision,
            round(r.final_score, 4),
            r.accepted_votes,
            r.rejected_votes,
            r.state72[:24],
        )

    print("\n=== JSON EXPORT ===\n")

    print(
        json.dumps(
            consensus_engine.export_results_json(
                results
            ),
            indent=2,
        )
    )