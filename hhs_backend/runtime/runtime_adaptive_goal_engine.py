# ============================================================================
# hhs_backend/runtime/runtime_adaptive_goal_engine.py
# HARMONICODE / HHS
# ADAPTIVE GOAL ENGINE
#
# PURPOSE
# -------
# Canonical adaptive cognition layer for:
#
#   - persistent runtime goals
#   - attractor reinforcement
#   - trajectory prioritization
#   - replay biasing
#   - convergence optimization
#   - adaptive routing
#   - semantic goal alignment
#   - multimodal objective persistence
#
# Goal adaptation MUST NOT mutate deterministic runtime invariants.
#
# ============================================================================

from __future__ import annotations

import logging
import statistics
import threading
import time
import uuid

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple

from hhs_backend.runtime.runtime_prediction_engine import (
    runtime_prediction_engine,
    HHSTrajectoryScore
)

from hhs_backend.runtime.runtime_replay_engine import (
    runtime_replay_engine,
    HHSReplayResult
)

from hhs_backend.runtime.runtime_semantic_memory_engine import (
    runtime_semantic_memory_engine
)

from hhs_backend.runtime.runtime_multimodal_embedding_router import (
    runtime_multimodal_embedding_router
)

from hhs_storage.runtime_state_store_v1 import (
    runtime_state_store
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_ADAPTIVE_GOAL_ENGINE"
)

# ============================================================================
# GOAL STATES
# ============================================================================

STATE_ACTIVE = "active"

STATE_SATISFIED = "satisfied"

STATE_SUPPRESSED = "suppressed"

STATE_ENTROPIC = "entropic"

# ============================================================================
# GOAL
# ============================================================================

@dataclass
class HHSRuntimeGoal:

    goal_id: str

    created_at: float

    objective: str

    target_hash72: str

    stability_bias: float

    entropy_penalty: float

    state: str = STATE_ACTIVE

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# GOAL ALIGNMENT
# ============================================================================

@dataclass
class HHSGoalAlignmentScore:

    alignment_id: str

    created_at: float

    goal_id: str

    replay_id: str

    alignment_score: float

    stability_score: float

    entropy_score: float

    convergence_score: float

# ============================================================================
# ATTRACTOR REINFORCEMENT
# ============================================================================

@dataclass
class HHSAttractorReinforcement:

    reinforcement_id: str

    created_at: float

    attractor_hash72: str

    reinforcement_strength: float

    trajectory_count: int

# ============================================================================
# ENGINE
# ============================================================================

class HHSRuntimeAdaptiveGoalEngine:

    """
    Canonical adaptive runtime goal cognition layer.
    """

    def __init__(self):

        self.lock = threading.RLock()

        self.goals: Dict[
            str,
            HHSRuntimeGoal
        ] = {}

        self.alignments: Dict[
            str,
            HHSGoalAlignmentScore
        ] = {}

        self.reinforcements: Dict[
            str,
            HHSAttractorReinforcement
        ] = {}

        self.total_goals = 0

        self.total_alignments = 0

        self.total_reinforcements = 0

    # =====================================================================
    # GOALS
    # =====================================================================

    def create_goal(

        self,

        objective: str,

        target_hash72: str,

        stability_bias: float = 1.0,

        entropy_penalty: float = 0.5,

        metadata: Optional[Dict] = None
    ) -> HHSRuntimeGoal:

        with self.lock:

            goal = HHSRuntimeGoal(

                goal_id=str(uuid.uuid4()),

                created_at=time.time(),

                objective=objective,

                target_hash72=target_hash72,

                stability_bias=stability_bias,

                entropy_penalty=entropy_penalty,

                metadata=metadata or {}
            )

            self.goals[
                goal.goal_id
            ] = goal

            runtime_semantic_memory_engine.ingest_memory(

                memory_type="goal",

                semantic_text=objective,

                hash72=target_hash72,

                metadata={

                    "goal_id":
                        goal.goal_id
                }
            )

            self.total_goals += 1

            logger.info(
                f"Goal created: "
                f"{goal.goal_id}"
            )

            return goal

    # =====================================================================
    # ALIGNMENT
    # =====================================================================

    def score_goal_alignment(

        self,

        goal: HHSRuntimeGoal,

        replay: HHSReplayResult
    ) -> HHSGoalAlignmentScore:

        prediction_score = (

            runtime_prediction_engine
            .score_replay(replay)
        )

        trajectory_hashes = []

        for frame in replay.frames:

            runtime = frame.runtime_packet.get(
                "runtime",
                {}
            )

            trajectory_hashes.append(

                runtime.get(
                    "state_hash72",
                    ""
                )
            )

        matches = sum(

            1

            for h in trajectory_hashes

            if h == goal.target_hash72
        )

        replay_size = max(
            len(trajectory_hashes),
            1
        )

        convergence_score = (
            matches / replay_size
        )

        stability_score = (
            prediction_score.stability_score
            * goal.stability_bias
        )

        entropy_score = (
            prediction_score.entropy_score
            * goal.entropy_penalty
        )

        alignment_score = (

            convergence_score * 0.5

            +

            stability_score * 0.4

            -

            entropy_score * 0.1
        )

        result = HHSGoalAlignmentScore(

            alignment_id=str(uuid.uuid4()),

            created_at=time.time(),

            goal_id=goal.goal_id,

            replay_id=replay.replay_id,

            alignment_score=alignment_score,

            stability_score=stability_score,

            entropy_score=entropy_score,

            convergence_score=convergence_score
        )

        self.alignments[
            result.alignment_id
        ] = result

        self.total_alignments += 1

        logger.info(
            f"Goal alignment scored: "
            f"{result.alignment_id}"
        )

        return result

    # =====================================================================
    # TRAJECTORY PRIORITIZATION
    # =====================================================================

    def prioritize_replay_trajectories(

        self,

        goal: HHSRuntimeGoal,

        trajectories: List[HHSReplayResult]
    ):

        ranked = []

        for replay in trajectories:

            alignment = (
                self.score_goal_alignment(
                    goal,
                    replay
                )
            )

            ranked.append(
                (
                    alignment.alignment_score,
                    replay,
                    alignment
                )
            )

        ranked.sort(

            key=lambda x: x[0],

            reverse=True
        )

        return ranked

    # =====================================================================
    # ATTRACTOR REINFORCEMENT
    # =====================================================================

    def reinforce_stable_attractors(
        self,
        replay: HHSReplayResult
    ):

        attractors = (

            runtime_prediction_engine
            .detect_attractor_fields(
                replay
            )
        )

        reinforcements = []

        for attractor in attractors:

            strength = (

                attractor.stability
                * attractor.frequency
            )

            reinforcement = (
                HHSAttractorReinforcement(

                    reinforcement_id=
                        str(uuid.uuid4()),

                    created_at=time.time(),

                    attractor_hash72=
                        attractor.dominant_hash72,

                    reinforcement_strength=
                        strength,

                    trajectory_count=
                        attractor.frequency
                )
            )

            self.reinforcements[
                reinforcement.reinforcement_id
            ] = reinforcement

            runtime_semantic_memory_engine.ingest_memory(

                memory_type="reinforcement",

                semantic_text=(
                    f"ATTRACTOR "
                    f"{attractor.dominant_hash72}"
                ),

                hash72=attractor.dominant_hash72,

                metadata={

                    "strength":
                        strength
                }
            )

            reinforcements.append(
                reinforcement
            )

            self.total_reinforcements += 1

        logger.info(
            "Stable attractors reinforced"
        )

        return reinforcements

    # =====================================================================
    # ENTROPY SUPPRESSION
    # =====================================================================

    def suppress_entropy_paths(

        self,

        replay: HHSReplayResult,

        threshold: float = 0.75
    ):

        prediction = (

            runtime_prediction_engine
            .score_replay(replay)
        )

        if prediction.entropy_score > threshold:

            logger.warning(
                "Entropic replay suppressed"
            )

            return {

                "suppressed": True,

                "entropy_score":
                    prediction.entropy_score
            }

        return {

            "suppressed": False,

            "entropy_score":
                prediction.entropy_score
        }

    # =====================================================================
    # ADAPTIVE ROUTING
    # =====================================================================

    def adaptive_route(

        self,

        query: str,

        horizon: int = 10
    ):

        semantic = (

            runtime_semantic_memory_engine
            .semantic_search(
                query,
                limit=5
            )
        )

        replay = (

            runtime_replay_engine
            .predictive_replay(
                horizon=horizon
            )
        )

        runtime_replay_engine.verify_replay_equivalence(
            replay
        )

        prediction = (

            runtime_prediction_engine
            .score_replay(replay)
        )

        reinforcement = (
            self.reinforce_stable_attractors(
                replay
            )
        )

        return {

            "semantic":
                semantic,

            "prediction":
                prediction,

            "reinforcement":
                reinforcement,

            "replay":
                replay
        }

    # =====================================================================
    # MULTIMODAL GOAL ROUTING
    # =====================================================================

    def multimodal_goal_projection(

        self,

        goal: HHSRuntimeGoal
    ):

        projection = (

            runtime_multimodal_embedding_router
            .project_text_to_image(
                goal.objective
            )
        )

        attractors = (

            runtime_multimodal_embedding_router
            .route_multimodal_attractor(
                modality="symbolic"
            )
        )

        return {

            "projection":
                projection,

            "attractors":
                attractors
        }

    # =====================================================================
    # STATUS
    # =====================================================================

    def goal_status(
        self,
        goal_id: str
    ):

        goal = self.goals.get(goal_id)

        if goal is None:
            return None

        related = [

            alignment

            for alignment in self.alignments.values()

            if alignment.goal_id == goal_id
        ]

        avg_alignment = 0.0

        if related:

            avg_alignment = statistics.mean(

                alignment.alignment_score

                for alignment in related
            )

        return {

            "goal":
                goal,

            "average_alignment":
                avg_alignment,

            "alignments":
                len(related)
        }

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        alignments = [

            alignment.alignment_score

            for alignment in self.alignments.values()
        ]

        avg_alignment = 0.0

        if alignments:

            avg_alignment = statistics.mean(
                alignments
            )

        return {

            "goals":
                self.total_goals,

            "alignments":
                self.total_alignments,

            "reinforcements":
                self.total_reinforcements,

            "average_alignment":
                avg_alignment
        }

# ============================================================================
# GLOBAL ENGINE
# ============================================================================

runtime_adaptive_goal_engine = (
    HHSRuntimeAdaptiveGoalEngine()
)

# ============================================================================
# SELF TEST
# ============================================================================

def adaptive_goal_self_test():

    goal = (

        runtime_adaptive_goal_engine
        .create_goal(

            objective=
                "stabilize replay "
                "convergence attractor",

            target_hash72=
                "abc123",

            stability_bias=1.2,

            entropy_penalty=0.3
        )
    )

    replay = (

        runtime_replay_engine
        .predictive_replay(
            horizon=5
        )
    )

    runtime_replay_engine.verify_replay_equivalence(
        replay
    )

    alignment = (

        runtime_adaptive_goal_engine
        .score_goal_alignment(
            goal,
            replay
        )
    )

    reinforcement = (

        runtime_adaptive_goal_engine
        .reinforce_stable_attractors(
            replay
        )
    )

    projection = (

        runtime_adaptive_goal_engine
        .multimodal_goal_projection(
            goal
        )
    )

    print()

    print("GOAL METRICS")

    print(
        runtime_adaptive_goal_engine.metrics()
    )

    print()

    print("ALIGNMENT")

    print(alignment)

    print()

    print("REINFORCEMENT")

    print(reinforcement)

    print()

    print("PROJECTION")

    print(projection)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    adaptive_goal_self_test()