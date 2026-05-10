# ============================================================================
# hhs_backend/runtime/runtime_prediction_engine.py
# HARMONICODE / HHS
# CANONICAL RUNTIME PREDICTION ENGINE
#
# PURPOSE
# -------
# Adaptive predictive cognition layer for:
#
#   - replay trajectory scoring
#   - branch ranking
#   - convergence prediction
#   - attractor detection
#   - replay prioritization
#   - adaptive runtime routing
#   - predictive graph traversal
#   - future-state inference
#
# Prediction MUST remain isolated from live execution mutation.
#
# ============================================================================

from __future__ import annotations

import logging
import math
import statistics
import time
import uuid

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from hhs_backend.runtime.runtime_replay_engine import (
    runtime_replay_engine,
    HHSReplayResult
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger("HHS_PREDICTION")

# ============================================================================
# TRAJECTORY SCORE
# ============================================================================

@dataclass
class HHSTrajectoryScore:

    trajectory_id: str

    created_at: float

    replay_id: str

    score: float

    convergence_probability: float

    entropy_score: float

    stability_score: float

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# ATTRACTOR FIELD
# ============================================================================

@dataclass
class HHSAttractorField:

    field_id: str

    created_at: float

    dominant_hash72: str

    frequency: int

    stability: float

    member_hashes: List[str]

# ============================================================================
# PREDICTION ENGINE
# ============================================================================

class HHSRuntimePredictionEngine:

    """
    Canonical adaptive runtime prediction engine.
    """

    def __init__(self):

        self.trajectory_scores: Dict[
            str,
            HHSTrajectoryScore
        ] = {}

        self.attractor_fields: Dict[
            str,
            HHSAttractorField
        ] = {}

        self.total_predictions = 0

        self.total_trajectory_scores = 0

    # =====================================================================
    # TRAJECTORY SCORING
    # =====================================================================

    def score_replay(
        self,
        replay: HHSReplayResult
    ) -> HHSTrajectoryScore:

        hashes = []

        steps = []

        for frame in replay.frames:

            runtime = frame.runtime_packet.get(
                "runtime",
                {}
            )

            hashes.append(
                runtime.get(
                    "state_hash72",
                    ""
                )
            )

            steps.append(
                runtime.get(
                    "step",
                    0
                )
            )

        unique_hashes = len(set(hashes))

        total_hashes = max(len(hashes), 1)

        stability_score = (
            unique_hashes / total_hashes
        )

        entropy_score = (
            1.0 - stability_score
        )

        convergence_probability = min(

            1.0,

            stability_score
            + (0.25 if replay.replay_equivalent else 0.0)
        )

        trajectory_score = (

            convergence_probability
            * 0.6

            +

            stability_score
            * 0.3

            +

            (1.0 - entropy_score)
            * 0.1
        )

        result = HHSTrajectoryScore(

            trajectory_id=str(uuid.uuid4()),

            created_at=time.time(),

            replay_id=replay.replay_id,

            score=trajectory_score,

            convergence_probability=
                convergence_probability,

            entropy_score=
                entropy_score,

            stability_score=
                stability_score,

            metadata={

                "total_frames":
                    replay.total_frames,

                "unique_hashes":
                    unique_hashes
            }
        )

        self.trajectory_scores[
            result.trajectory_id
        ] = result

        self.total_trajectory_scores += 1

        logger.info(
            f"Trajectory scored: "
            f"{result.trajectory_id}"
        )

        return result

    # =====================================================================
    # ATTRACTOR DETECTION
    # =====================================================================

    def detect_attractor_fields(
        self,
        replay: HHSReplayResult
    ):

        frequencies = {}

        for frame in replay.frames:

            runtime = frame.runtime_packet.get(
                "runtime",
                {}
            )

            h = runtime.get(
                "state_hash72",
                ""
            )

            frequencies[h] = (
                frequencies.get(h, 0)
                + 1
            )

        attractors = []

        for h, freq in frequencies.items():

            stability = freq / max(
                replay.total_frames,
                1
            )

            field = HHSAttractorField(

                field_id=str(uuid.uuid4()),

                created_at=time.time(),

                dominant_hash72=h,

                frequency=freq,

                stability=stability,

                member_hashes=[h]
            )

            self.attractor_fields[
                field.field_id
            ] = field

            attractors.append(field)

        attractors.sort(

            key=lambda x: x.stability,

            reverse=True
        )

        return attractors

    # =====================================================================
    # BRANCH RANKING
    # =====================================================================

    def rank_replays(
        self,
        replays: List[HHSReplayResult]
    ):

        scored = []

        for replay in replays:

            score = self.score_replay(
                replay
            )

            scored.append(
                (score.score, replay, score)
            )

        scored.sort(

            key=lambda x: x[0],

            reverse=True
        )

        return scored

    # =====================================================================
    # PREDICTIVE TRAJECTORY
    # =====================================================================

    def generate_predictive_replay(
        self,
        horizon: int = 10
    ):

        replay = (
            runtime_replay_engine
            .predictive_replay(
                horizon=horizon
            )
        )

        runtime_replay_engine.verify_replay_equivalence(
            replay
        )

        score = self.score_replay(
            replay
        )

        attractors = self.detect_attractor_fields(
            replay
        )

        self.total_predictions += 1

        return {

            "replay":
                replay,

            "trajectory_score":
                score,

            "attractors":
                attractors
        }

    # =====================================================================
    # ADAPTIVE ROUTING
    # =====================================================================

    def select_optimal_trajectory(
        self,
        trajectories: List[HHSReplayResult]
    ):

        ranked = self.rank_replays(
            trajectories
        )

        if not ranked:
            return None

        best = ranked[0]

        return {

            "score":
                best[0],

            "replay":
                best[1],

            "trajectory":
                best[2]
        }

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        scores = [

            s.score

            for s in self.trajectory_scores.values()
        ]

        avg_score = 0.0

        if scores:

            avg_score = statistics.mean(scores)

        return {

            "total_predictions":
                self.total_predictions,

            "trajectory_scores":
                len(self.trajectory_scores),

            "attractor_fields":
                len(self.attractor_fields),

            "average_trajectory_score":
                avg_score
        }

# ============================================================================
# GLOBAL ENGINE
# ============================================================================

runtime_prediction_engine = (
    HHSRuntimePredictionEngine()
)

# ============================================================================
# SELF TEST
# ============================================================================

def prediction_engine_self_test():

    prediction = (

        runtime_prediction_engine
        .generate_predictive_replay(
            horizon=5
        )
    )

    print()

    print("PREDICTION METRICS")

    print(
        runtime_prediction_engine.metrics()
    )

    print()

    print("TRAJECTORY SCORE")

    print(
        prediction["trajectory_score"]
    )

    print()

    print("ATTRACTORS")

    print(
        prediction["attractors"]
    )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    prediction_engine_self_test()