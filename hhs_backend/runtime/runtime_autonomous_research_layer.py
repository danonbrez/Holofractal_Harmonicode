# ============================================================================
# hhs_backend/runtime/runtime_autonomous_research_layer.py
# HARMONICODE / HHS
# AUTONOMOUS RESEARCH LAYER
#
# PURPOSE
# -------
# Canonical autonomous discovery substrate for:
#
#   - replay-guided research exploration
#   - adaptive semantic expansion
#   - recursive hypothesis generation
#   - multimodal knowledge synthesis
#   - federated discovery coordination
#   - distributed research planning
#   - attractor-guided knowledge acquisition
#   - world-model expansion
#
# Research cognition MUST remain replay-safe and consensus-governed.
#
# ============================================================================

from __future__ import annotations

import logging
import statistics
import threading
import time
import uuid

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from hhs_backend.runtime.runtime_replay_engine import (
    runtime_replay_engine,
    HHSReplayResult,
)

from hhs_backend.runtime.runtime_prediction_engine import (
    runtime_prediction_engine,
)

from hhs_backend.runtime.runtime_semantic_memory_engine import (
    runtime_semantic_memory_engine,
)

from hhs_backend.runtime.runtime_multimodal_embedding_router import (
    runtime_multimodal_embedding_router,
)

from hhs_backend.runtime.runtime_multinode_goal_consensus import (
    runtime_multinode_goal_consensus,
)

from hhs_backend.runtime.distributed_consensus_runtime import (
    distributed_consensus_runtime,
)

from hhs_storage.runtime_state_store_v1 import (
    runtime_state_store,
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_AUTONOMOUS_RESEARCH"
)

# ============================================================================
# RESEARCH STATES
# ============================================================================

STATE_PENDING = "pending"

STATE_EXPLORING = "exploring"

STATE_SYNTHESIZED = "synthesized"

STATE_EXPANDED = "expanded"

STATE_COORDINATED = "coordinated"

STATE_QUARANTINED = "quarantined"

STATE_COMPLETED = "completed"

# ============================================================================
# RESEARCH TASK
# ============================================================================

@dataclass
class HHSResearchTask:

    task_id: str

    created_at: float

    research_objective: str

    originating_goal: str

    exploration_horizon: int

    execution_state: str = STATE_PENDING

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# RESEARCH HYPOTHESIS
# ============================================================================

@dataclass
class HHSResearchHypothesis:

    hypothesis_id: str

    created_at: float

    task_id: str

    hypothesis_text: str

    support_score: float

    source_hash72: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# KNOWLEDGE EXPANSION
# ============================================================================

@dataclass
class HHSKnowledgeExpansion:

    expansion_id: str

    created_at: float

    task_id: str

    expanded_nodes: int

    semantic_links: int

    coherence_score: float

# ============================================================================
# FEDERATED RESEARCH PLAN
# ============================================================================

@dataclass
class HHSFederatedResearchPlan:

    plan_id: str

    created_at: float

    task_id: str

    assigned_nodes: List[str]

    consensus_state: str

    quorum_required: int

# ============================================================================
# AUTONOMOUS RESEARCH LAYER
# ============================================================================

class HHSRuntimeAutonomousResearchLayer:

    """
    Canonical replay-governed autonomous discovery layer.
    """

    def __init__(self):

        self.lock = threading.RLock()

        self.tasks: Dict[
            str,
            HHSResearchTask
        ] = {}

        self.hypotheses: Dict[
            str,
            HHSResearchHypothesis
        ] = {}

        self.expansions: Dict[
            str,
            HHSKnowledgeExpansion
        ] = {}

        self.federated_plans: Dict[
            str,
            HHSFederatedResearchPlan
        ] = {}

        self.total_tasks = 0

        self.total_hypotheses = 0

        self.total_expansions = 0

        self.total_federated_plans = 0

    # =====================================================================
    # TASK CREATION
    # =====================================================================

    def create_research_task(

        self,

        research_objective: str,

        originating_goal: str,

        exploration_horizon: int = 10,

        metadata: Optional[Dict] = None,
    ) -> HHSResearchTask:

        with self.lock:

            task = HHSResearchTask(

                task_id=str(uuid.uuid4()),

                created_at=time.time(),

                research_objective=research_objective,

                originating_goal=originating_goal,

                exploration_horizon=exploration_horizon,

                metadata=metadata or {},
            )

            self.tasks[
                task.task_id
            ] = task

            runtime_semantic_memory_engine.ingest_memory(

                memory_type="research_task",

                semantic_text=research_objective,

                metadata={

                    "task_id":
                        task.task_id,

                    "originating_goal":
                        originating_goal,
                },
            )

            runtime_state_store.store_event(

                event_type="research.task.created",

                source="autonomous_research_layer",

                payload={

                    "task_id":
                        task.task_id,

                    "objective":
                        research_objective,

                    "originating_goal":
                        originating_goal,

                    "exploration_horizon":
                        exploration_horizon,
                },
            )

            self.total_tasks += 1

            logger.info(
                f"Research task created: {task.task_id}"
            )

            return task

    # =====================================================================
    # REPLAY-GUIDED EXPLORATION
    # =====================================================================

    def explore_replay_knowledge_space(
        self,
        task: HHSResearchTask,
    ) -> HHSReplayResult:

        task.execution_state = STATE_EXPLORING

        replay = (

            runtime_replay_engine
            .predictive_replay(
                horizon=task.exploration_horizon
            )
        )

        runtime_replay_engine.verify_replay_equivalence(
            replay
        )

        prediction = (
            runtime_prediction_engine
            .score_replay(replay)
        )

        runtime_state_store.store_event(

            event_type="research.replay.explored",

            source="autonomous_research_layer",

            payload={

                "task_id":
                    task.task_id,

                "replay_id":
                    replay.replay_id,

                "trajectory_score":
                    prediction.score,

                "entropy_score":
                    prediction.entropy_score,
            },
        )

        if prediction.entropy_score > 0.9:

            task.execution_state = STATE_QUARANTINED

            logger.warning(
                f"Research task quarantined during replay exploration: "
                f"{task.task_id}"
            )

        return replay

    # =====================================================================
    # HYPOTHESIS SYNTHESIS
    # =====================================================================

    def generate_research_hypotheses(

        self,

        task: HHSResearchTask,

        replay: HHSReplayResult,

        limit: int = 8,
    ) -> List[HHSResearchHypothesis]:

        hypotheses = []

        attractors = (

            runtime_prediction_engine
            .detect_attractor_fields(
                replay
            )
        )

        semantic_context = (

            runtime_semantic_memory_engine
            .semantic_search(
                task.research_objective,
                limit=limit,
            )
        )

        for index, attractor in enumerate(attractors[:limit]):

            context_text = ""

            if index < len(semantic_context):

                context_text = semantic_context[
                    index
                ].semantic_text

            hypothesis_text = (

                f"Research hypothesis for objective "
                f"'{task.research_objective}': "
                f"attractor {attractor.dominant_hash72} "
                f"with stability {attractor.stability:.6f} "
                f"may connect to semantic context "
                f"'{context_text}'."
            )

            support_score = min(

                1.0,

                attractor.stability
                + (
                    semantic_context[index].similarity
                    if index < len(semantic_context)
                    else 0.0
                ) / 2.0,
            )

            hypothesis = HHSResearchHypothesis(

                hypothesis_id=str(uuid.uuid4()),

                created_at=time.time(),

                task_id=task.task_id,

                hypothesis_text=hypothesis_text,

                support_score=support_score,

                source_hash72=attractor.dominant_hash72,

                metadata={

                    "frequency":
                        attractor.frequency,

                    "stability":
                        attractor.stability,
                },
            )

            self.hypotheses[
                hypothesis.hypothesis_id
            ] = hypothesis

            runtime_semantic_memory_engine.ingest_memory(

                memory_type="research_hypothesis",

                semantic_text=hypothesis_text,

                hash72=attractor.dominant_hash72,

                metadata={

                    "task_id":
                        task.task_id,

                    "hypothesis_id":
                        hypothesis.hypothesis_id,

                    "support_score":
                        support_score,
                },
            )

            hypotheses.append(hypothesis)

            self.total_hypotheses += 1

        task.execution_state = STATE_SYNTHESIZED

        logger.info(
            f"Hypotheses generated for task: {task.task_id}"
        )

        return hypotheses

    # =====================================================================
    # SEMANTIC TOPOLOGY EXPANSION
    # =====================================================================

    def expand_semantic_knowledge_graph(

        self,

        task: HHSResearchTask,

        hypotheses: List[HHSResearchHypothesis],
    ) -> HHSKnowledgeExpansion:

        expanded_nodes = 0

        semantic_links = 0

        support_scores = []

        previous_memory_id = None

        for hypothesis in hypotheses:

            memory = runtime_semantic_memory_engine.ingest_memory(

                memory_type="knowledge_expansion",

                semantic_text=hypothesis.hypothesis_text,

                hash72=hypothesis.source_hash72,

                metadata={

                    "task_id":
                        task.task_id,

                    "hypothesis_id":
                        hypothesis.hypothesis_id,
                },
            )

            expanded_nodes += 1

            support_scores.append(
                hypothesis.support_score
            )

            if previous_memory_id is not None:

                runtime_semantic_memory_engine.link_memories(

                    previous_memory_id,

                    memory.memory_id,

                    relationship="research_expansion",

                    weight=hypothesis.support_score,
                )

                semantic_links += 1

            previous_memory_id = memory.memory_id

        coherence_score = 0.0

        if support_scores:

            coherence_score = statistics.mean(
                support_scores
            )

        expansion = HHSKnowledgeExpansion(

            expansion_id=str(uuid.uuid4()),

            created_at=time.time(),

            task_id=task.task_id,

            expanded_nodes=expanded_nodes,

            semantic_links=semantic_links,

            coherence_score=coherence_score,
        )

        self.expansions[
            expansion.expansion_id
        ] = expansion

        self.total_expansions += 1

        task.execution_state = STATE_EXPANDED

        runtime_state_store.store_event(

            event_type="research.knowledge.expanded",

            source="autonomous_research_layer",

            payload={

                "task_id":
                    task.task_id,

                "expansion_id":
                    expansion.expansion_id,

                "expanded_nodes":
                    expanded_nodes,

                "semantic_links":
                    semantic_links,

                "coherence_score":
                    coherence_score,
            },
        )

        logger.info(
            f"Knowledge graph expanded for task: {task.task_id}"
        )

        return expansion

    # =====================================================================
    # FEDERATED RESEARCH COORDINATION
    # =====================================================================

    def coordinate_distributed_research(
        self,
        task: HHSResearchTask,
    ) -> HHSFederatedResearchPlan:

        proposal = (

            distributed_consensus_runtime
            .create_consensus_proposal(

                proposal_type="research_task",

                target_hash72=task.task_id,

                quorum_required=2,

                metadata={

                    "objective":
                        task.research_objective,

                    "originating_goal":
                        task.originating_goal,
                },
            )
        )

        distributed_consensus_runtime.submit_vote(

            proposal.proposal_id,

            node_id="research_node_1",

            approved=True,

            confidence=0.94,
        )

        distributed_consensus_runtime.submit_vote(

            proposal.proposal_id,

            node_id="research_node_2",

            approved=True,

            confidence=0.91,
        )

        quorum = (

            distributed_consensus_runtime
            .collect_consensus_votes(
                proposal.proposal_id
            )
        )

        plan = HHSFederatedResearchPlan(

            plan_id=str(uuid.uuid4()),

            created_at=time.time(),

            task_id=task.task_id,

            assigned_nodes=[

                "research_node_1",

                "research_node_2",
            ],

            consensus_state=(
                "approved"
                if quorum and quorum["approved"]
                else "rejected"
            ),

            quorum_required=2,
        )

        self.federated_plans[
            plan.plan_id
        ] = plan

        self.total_federated_plans += 1

        task.execution_state = STATE_COORDINATED

        runtime_state_store.store_event(

            event_type="research.distributed.coordinated",

            source="autonomous_research_layer",

            payload={

                "task_id":
                    task.task_id,

                "plan_id":
                    plan.plan_id,

                "consensus_state":
                    plan.consensus_state,
            },
        )

        logger.info(
            f"Distributed research coordinated: {plan.plan_id}"
        )

        return plan

    # =====================================================================
    # MULTIMODAL KNOWLEDGE SYNTHESIS
    # =====================================================================

    def synthesize_multimodal_knowledge(
        self,
        task: HHSResearchTask,
    ):

        text_projection = (

            runtime_multimodal_embedding_router
            .project_text_to_image(
                task.research_objective
            )
        )

        symbolic_projection = (

            runtime_multimodal_embedding_router
            .project_audio_to_symbolic(
                f"RESEARCH::{task.research_objective}"
            )
        )

        replay_projection = (

            runtime_multimodal_embedding_router
            .project_replay_to_multimodal(
                horizon=task.exploration_horizon
            )
        )

        runtime_state_store.store_event(

            event_type="research.multimodal.synthesized",

            source="autonomous_research_layer",

            payload={

                "task_id":
                    task.task_id,

                "text_projection":
                    text_projection["projection"].projection_id,

                "symbolic_projection":
                    symbolic_projection["projection"].projection_id,

                "replay_projections":
                    len(replay_projection),
            },
        )

        return {

            "text_projection":
                text_projection,

            "symbolic_projection":
                symbolic_projection,

            "replay_projection":
                replay_projection,
        }

    # =====================================================================
    # FULL RESEARCH CYCLE
    # =====================================================================

    def execute_research_cycle(

        self,

        research_objective: str,

        originating_goal: str = "autonomous_research",

        exploration_horizon: int = 10,
    ):

        task = self.create_research_task(

            research_objective=research_objective,

            originating_goal=originating_goal,

            exploration_horizon=exploration_horizon,
        )

        replay = self.explore_replay_knowledge_space(
            task
        )

        if task.execution_state == STATE_QUARANTINED:

            return {

                "task":
                    task,

                "quarantined":
                    True,
            }

        hypotheses = self.generate_research_hypotheses(

            task,

            replay,
        )

        expansion = self.expand_semantic_knowledge_graph(

            task,

            hypotheses,
        )

        federated_plan = self.coordinate_distributed_research(
            task
        )

        multimodal = self.synthesize_multimodal_knowledge(
            task
        )

        task.execution_state = STATE_COMPLETED

        runtime_state_store.store_event(

            event_type="research.cycle.completed",

            source="autonomous_research_layer",

            payload={

                "task_id":
                    task.task_id,

                "hypotheses":
                    len(hypotheses),

                "expansion_id":
                    expansion.expansion_id,

                "federated_plan_id":
                    federated_plan.plan_id,
            },
        )

        return {

            "task":
                task,

            "replay":
                replay,

            "hypotheses":
                hypotheses,

            "expansion":
                expansion,

            "federated_plan":
                federated_plan,

            "multimodal":
                multimodal,
        }

    # =====================================================================
    # STATUS
    # =====================================================================

    def task_status(
        self,
        task_id: str,
    ):

        task = self.tasks.get(task_id)

        hypotheses = [

            hypothesis

            for hypothesis in self.hypotheses.values()

            if hypothesis.task_id == task_id
        ]

        expansions = [

            expansion

            for expansion in self.expansions.values()

            if expansion.task_id == task_id
        ]

        plans = [

            plan

            for plan in self.federated_plans.values()

            if plan.task_id == task_id
        ]

        return {

            "task":
                task,

            "hypotheses":
                hypotheses,

            "expansions":
                expansions,

            "federated_plans":
                plans,
        }

    # =====================================================================
    # METRICS
    # =====================================================================

    def metrics(self):

        support_scores = [

            hypothesis.support_score

            for hypothesis in self.hypotheses.values()
        ]

        coherence_scores = [

            expansion.coherence_score

            for expansion in self.expansions.values()
        ]

        avg_support = 0.0

        avg_coherence = 0.0

        if support_scores:

            avg_support = statistics.mean(
                support_scores
            )

        if coherence_scores:

            avg_coherence = statistics.mean(
                coherence_scores
            )

        return {

            "tasks":
                self.total_tasks,

            "hypotheses":
                self.total_hypotheses,

            "expansions":
                self.total_expansions,

            "federated_plans":
                self.total_federated_plans,

            "average_hypothesis_support":
                avg_support,

            "average_expansion_coherence":
                avg_coherence,
        }

# ============================================================================
# GLOBAL LAYER
# ============================================================================

runtime_autonomous_research_layer = (
    HHSRuntimeAutonomousResearchLayer()
)

# ============================================================================
# SELF TEST
# ============================================================================

def autonomous_research_self_test():

    result = (

        runtime_autonomous_research_layer
        .execute_research_cycle(

            research_objective=(
                "discover replay-governed "
                "semantic attractor topology"
            ),

            originating_goal="self_test_goal",

            exploration_horizon=5,
        )
    )

    print()

    print("AUTONOMOUS RESEARCH METRICS")

    print(

        runtime_autonomous_research_layer
        .metrics()
    )

    print()

    print("RESULT")

    print(result)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    autonomous_research_self_test()