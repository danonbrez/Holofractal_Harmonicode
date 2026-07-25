"""Live boot-reachable cognition coordinator for the HHS runtime.

The coordinator converts committed live kernel packets into replay-safe semantic
memory, prediction, attractor, goal-alignment, consensus, research, and
recursive-toolchain surfaces. It never mutates VM81 state; it consumes only
already-authorized runtime packets.
"""

from __future__ import annotations

import copy
import json
import os
import threading
import time
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Mapping, Optional

from hhs_backend.runtime.distributed_consensus_runtime import distributed_consensus_runtime
from hhs_backend.runtime.runtime_adaptive_goal_engine import runtime_adaptive_goal_engine
from hhs_backend.runtime.runtime_agentic_cognition_layer import runtime_agentic_cognition_layer
from hhs_backend.runtime.runtime_autonomous_research_layer import runtime_autonomous_research_layer
from hhs_backend.runtime.runtime_multinode_goal_consensus import runtime_multinode_goal_consensus
from hhs_backend.runtime.runtime_prediction_engine import runtime_prediction_engine
from hhs_backend.runtime.runtime_recursive_toolchain_layer import runtime_recursive_toolchain_layer
from hhs_backend.runtime.runtime_replay_engine import runtime_replay_engine
from hhs_backend.runtime.runtime_semantic_memory_engine import TYPE_RUNTIME, runtime_semantic_memory_engine
from hhs_storage.runtime_state_store_v1 import runtime_state_store

VERSION = "HHS_LIVE_COGNITION_RUNTIME_V1"
STATUS_SCHEMA = "HHS_LIVE_COGNITION_STATUS_V1"
TICK_SCHEMA = "HHS_LIVE_COGNITION_TICK_V1"


def to_cognition_data(value: Any) -> Any:
    if is_dataclass(value):
        return {key: to_cognition_data(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): to_cognition_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_cognition_data(item) for item in value]
    return value


class HHSRuntimeCognitionCoordinator:
    """Authority-separated coordinator for the boot-reachable cognitive stack."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.enabled = os.environ.get("HHS_COGNITION_AUTO_TICK", "1").lower() not in {
            "0", "false", "no", "off"
        }
        self.replay_horizon = max(1, int(os.environ.get("HHS_COGNITION_REPLAY_HORIZON", "8")))
        self.initialized = False
        self.started_at: Optional[float] = None
        self.processed_ticks = 0
        self.duplicate_ticks = 0
        self.failed_ticks = 0
        self.last_runtime_identity: Optional[tuple[Any, ...]] = None
        self.last_runtime: Dict[str, Any] = {}
        self.last_result: Dict[str, Any] = {}
        self.errors: list[str] = []

    def initialize(self) -> Dict[str, Any]:
        with self._lock:
            if not self.initialized:
                self.initialized = True
                self.started_at = time.time()
            return self.status()

    @staticmethod
    def _runtime_identity(packet: Mapping[str, Any]) -> tuple[Any, ...]:
        runtime = dict(packet.get("runtime") or {})
        return (
            runtime.get("step"),
            runtime.get("state_hash72"),
            runtime.get("receipt_hash72"),
        )

    def process_packet(
        self,
        packet: Mapping[str, Any],
        *,
        emission: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Consume one committed live packet without acquiring VM mutation authority."""

        if not self.initialized:
            self.initialize()
        if not self.enabled:
            return {
                "schema": TICK_SCHEMA,
                "processed": False,
                "status": "COGNITION_AUTO_TICK_DISABLED",
            }

        packet_dict = copy.deepcopy(dict(packet))
        runtime = dict(packet_dict.get("runtime") or {})
        state_hash72 = str(runtime.get("state_hash72") or "")
        if not state_hash72:
            raise ValueError("live cognition packet requires runtime.state_hash72")

        identity = self._runtime_identity(packet_dict)
        with self._lock:
            if identity == self.last_runtime_identity:
                self.duplicate_ticks += 1
                return {
                    "schema": TICK_SCHEMA,
                    "processed": False,
                    "status": "DUPLICATE_COMMITTED_RUNTIME_STATE",
                    "runtime_identity": list(identity),
                    "processed_ticks": self.processed_ticks,
                }

        try:
            runtime_state_store.store_replay_record(packet_dict)
            runtime_replay_engine.ingest_live_packet(packet_dict)

            semantic_record = runtime_semantic_memory_engine.ingest_memory(
                memory_type=TYPE_RUNTIME,
                semantic_text=json.dumps(runtime, sort_keys=True, separators=(",", ":"), default=str),
                hash72=state_hash72,
                metadata={
                    "source": "live_fastapi_workflow.tick_once",
                    "runtime_step": runtime.get("step"),
                    "receipt_hash72": runtime.get("receipt_hash72"),
                    "event_hash72": (emission or {}).get("event_hash72"),
                    "authority": "COMMITTED_RUNTIME_PACKET_OBSERVER_ONLY",
                },
            )

            replay = runtime_replay_engine.live_replay_window(limit=self.replay_horizon)
            replay_equivalent = runtime_replay_engine.verify_replay_equivalence(replay)
            trajectory = runtime_prediction_engine.score_replay(replay)
            attractors = runtime_prediction_engine.detect_attractor_fields(replay)
            reinforcements = runtime_adaptive_goal_engine.reinforce_stable_attractors(replay)

            alignments = []
            for goal in list(runtime_adaptive_goal_engine.goals.values()):
                if getattr(goal, "state", "active") == "active":
                    alignments.append(runtime_adaptive_goal_engine.score_goal_alignment(goal, replay))

            synchronized_goals = []
            if runtime_multinode_goal_consensus.goals:
                synchronized_goals = runtime_multinode_goal_consensus.synchronize_federated_goals()

            result = {
                "schema": TICK_SCHEMA,
                "processed": True,
                "runtime_identity": list(identity),
                "semantic_memory_id": semantic_record.memory_id,
                "replay_id": replay.replay_id,
                "replay_frames": replay.total_frames,
                "replay_equivalent": replay_equivalent,
                "trajectory": to_cognition_data(trajectory),
                "attractors": to_cognition_data(attractors),
                "reinforcements": to_cognition_data(reinforcements),
                "goal_alignments": to_cognition_data(alignments),
                "synchronized_goals": to_cognition_data(synchronized_goals),
                "authority_rule": "COGNITION_OBSERVES_COMMITTED_RUNTIME_STATE_AND_NEVER_MUTATES_VM81",
            }

            with self._lock:
                self.last_runtime_identity = identity
                self.last_runtime = runtime
                self.last_result = result
                self.processed_ticks += 1
            return copy.deepcopy(result)
        except Exception as exc:
            with self._lock:
                self.failed_ticks += 1
                self.errors.append(f"{type(exc).__name__}:{exc}")
                self.errors = self.errors[-16:]
            raise

    def create_goal(
        self,
        objective: str,
        target_hash72: Optional[str] = None,
        *,
        stability_bias: float = 1.0,
        entropy_penalty: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        target = str(target_hash72 or self.last_runtime.get("state_hash72") or "")
        if not target:
            raise ValueError("target_hash72 is required before the first live cognition tick")
        return to_cognition_data(runtime_adaptive_goal_engine.create_goal(
            objective=objective,
            target_hash72=target,
            stability_bias=stability_bias,
            entropy_penalty=entropy_penalty,
            metadata=metadata,
        ))

    def create_task(
        self,
        objective: str,
        *,
        goal_id: Optional[str] = None,
        target_hash72: Optional[str] = None,
        replay_context: str = "live_runtime",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        goal = runtime_adaptive_goal_engine.goals.get(str(goal_id or ""))
        if goal_id and goal is None:
            raise KeyError(f"unknown goal: {goal_id}")
        if goal is None:
            goal_data = self.create_goal(objective, target_hash72, metadata=metadata)
            goal = runtime_adaptive_goal_engine.goals[goal_data["goal_id"]]
        task = runtime_agentic_cognition_layer.create_cognition_task(
            objective=objective,
            goal=goal,
            replay_context=replay_context,
            metadata=metadata,
        )
        return to_cognition_data(task)

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        task = runtime_agentic_cognition_layer.tasks.get(task_id)
        if task is None:
            raise KeyError(f"unknown cognition task: {task_id}")
        return to_cognition_data(runtime_agentic_cognition_layer.execute_cognition_task(task))

    def task_status(self, task_id: str) -> Dict[str, Any]:
        if task_id not in runtime_agentic_cognition_layer.tasks:
            raise KeyError(f"unknown cognition task: {task_id}")
        return to_cognition_data(runtime_agentic_cognition_layer.task_status(task_id))

    def execute_research(
        self,
        objective: str,
        *,
        originating_goal: str = "api.runtime.research",
        exploration_horizon: int = 10,
    ) -> Dict[str, Any]:
        return to_cognition_data(runtime_autonomous_research_layer.execute_research_cycle(
            research_objective=objective,
            originating_goal=originating_goal,
            exploration_horizon=exploration_horizon,
        ))

    def execute_toolchain(self, originating_task: str, graph_seed: str) -> Dict[str, Any]:
        return to_cognition_data(runtime_recursive_toolchain_layer.execute_recursive_toolchain(
            originating_task=originating_task,
            graph_seed=graph_seed,
        ))

    def goals(self) -> Dict[str, Any]:
        return {
            "goals": to_cognition_data(list(runtime_adaptive_goal_engine.goals.values())),
            "metrics": runtime_adaptive_goal_engine.metrics(),
        }

    def goal_status(self, goal_id: str) -> Dict[str, Any]:
        status = runtime_adaptive_goal_engine.goal_status(goal_id)
        if status is None:
            raise KeyError(f"unknown goal: {goal_id}")
        return to_cognition_data(status)

    def adapt_goal(self, goal_id: str, horizon: int = 10) -> Dict[str, Any]:
        goal = runtime_adaptive_goal_engine.goals.get(goal_id)
        if goal is None:
            raise KeyError(f"unknown goal: {goal_id}")
        return to_cognition_data(runtime_adaptive_goal_engine.adaptive_route(
            goal.objective,
            horizon=horizon,
        ))

    def semantic_ingest(
        self,
        memory_type: str,
        semantic_text: str,
        *,
        hash72: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return to_cognition_data(runtime_semantic_memory_engine.ingest_memory(
            memory_type=memory_type,
            semantic_text=semantic_text,
            hash72=hash72,
            metadata=metadata,
        ))

    def semantic_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        return {
            "query": query,
            "limit": limit,
            "results": to_cognition_data(runtime_semantic_memory_engine.semantic_search(
                query,
                limit=limit,
            )),
            "metrics": runtime_semantic_memory_engine.metrics(),
        }

    def semantic_graph(self) -> Dict[str, Any]:
        return {
            "graph": runtime_semantic_memory_engine.export_memory_graph(),
            "metrics": runtime_semantic_memory_engine.metrics(),
        }

    def generate_prediction(self, horizon: int = 10) -> Dict[str, Any]:
        return to_cognition_data(runtime_prediction_engine.generate_predictive_replay(
            horizon=horizon,
        ))

    def consensus_status(self) -> Dict[str, Any]:
        return {
            "metrics": distributed_consensus_runtime.metrics(),
            "proposals": to_cognition_data(list(distributed_consensus_runtime.proposals.values())),
            "votes": to_cognition_data(list(distributed_consensus_runtime.votes.values())),
        }

    def create_consensus_proposal(
        self,
        proposal_type: str,
        target_hash72: str,
        *,
        quorum_required: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return to_cognition_data(distributed_consensus_runtime.create_consensus_proposal(
            proposal_type=proposal_type,
            target_hash72=target_hash72,
            quorum_required=quorum_required,
            metadata=metadata,
        ))

    def submit_consensus_vote(
        self,
        proposal_id: str,
        node_id: str,
        approved: bool,
        *,
        confidence: float = 1.0,
    ) -> Dict[str, Any]:
        if proposal_id not in distributed_consensus_runtime.proposals:
            raise KeyError(f"unknown consensus proposal: {proposal_id}")
        return to_cognition_data(distributed_consensus_runtime.submit_vote(
            proposal_id=proposal_id,
            node_id=node_id,
            approved=approved,
            confidence=confidence,
        ))

    def collect_consensus(self, proposal_id: str) -> Dict[str, Any]:
        result = distributed_consensus_runtime.collect_consensus_votes(proposal_id)
        if result is None:
            raise KeyError(f"unknown consensus proposal: {proposal_id}")
        return to_cognition_data(result)

    def toolchain_status(self, toolchain_id: Optional[str] = None) -> Dict[str, Any]:
        if toolchain_id:
            if toolchain_id not in runtime_recursive_toolchain_layer.toolchains:
                raise KeyError(f"unknown toolchain: {toolchain_id}")
            return to_cognition_data(runtime_recursive_toolchain_layer.toolchain_status(toolchain_id))
        return {
            "metrics": runtime_recursive_toolchain_layer.metrics(),
            "toolchains": to_cognition_data(list(runtime_recursive_toolchain_layer.toolchains.values())),
        }

    def research_status(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        if task_id:
            if task_id not in runtime_autonomous_research_layer.tasks:
                raise KeyError(f"unknown research task: {task_id}")
            return to_cognition_data(runtime_autonomous_research_layer.task_status(task_id))
        return {
            "metrics": runtime_autonomous_research_layer.metrics(),
            "tasks": to_cognition_data(list(runtime_autonomous_research_layer.tasks.values())),
        }

    def register_multinode_goal(
        self,
        originating_node: str,
        objective: str,
        target_hash72: str,
        *,
        consensus_weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return to_cognition_data(runtime_multinode_goal_consensus.register_multinode_goal(
            originating_node=originating_node,
            objective=objective,
            target_hash72=target_hash72,
            consensus_weight=consensus_weight,
            metadata=metadata,
        ))

    def multinode_goal_status(self) -> Dict[str, Any]:
        return {
            "metrics": runtime_multinode_goal_consensus.metrics(),
            "goals": to_cognition_data(list(runtime_multinode_goal_consensus.goals.values())),
            "alignments": to_cognition_data(
                list(runtime_multinode_goal_consensus.distributed_alignments.values())
            ),
        }

    def synchronize_multinode_goals(self) -> Dict[str, Any]:
        return {
            "synchronized": to_cognition_data(
                runtime_multinode_goal_consensus.synchronize_federated_goals()
            ),
            "metrics": runtime_multinode_goal_consensus.metrics(),
        }

    def status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "schema": STATUS_SCHEMA,
                "version": VERSION,
                "initialized": self.initialized,
                "enabled": self.enabled,
                "started_at": self.started_at,
                "processed_ticks": self.processed_ticks,
                "duplicate_ticks": self.duplicate_ticks,
                "failed_ticks": self.failed_ticks,
                "last_runtime": copy.deepcopy(self.last_runtime),
                "last_result": copy.deepcopy(self.last_result),
                "errors": list(self.errors),
                "layers": {
                    "semantic_memory": runtime_semantic_memory_engine.metrics(),
                    "adaptive_goals": runtime_adaptive_goal_engine.metrics(),
                    "prediction": runtime_prediction_engine.metrics(),
                    "replay": runtime_replay_engine.metrics(),
                    "agentic_cognition": runtime_agentic_cognition_layer.metrics(),
                    "autonomous_research": runtime_autonomous_research_layer.metrics(),
                    "recursive_toolchain": runtime_recursive_toolchain_layer.metrics(),
                    "distributed_consensus": distributed_consensus_runtime.metrics(),
                    "multinode_goal_consensus": runtime_multinode_goal_consensus.metrics(),
                },
                "authority_boundary": {
                    "vm81_mutation": "DENIED",
                    "committed_packet_observation": "AUTHORIZED",
                    "semantic_memory_append": "RECEIPT_GUARDED",
                    "prediction": "NON_AUTHORITATIVE",
                    "goal_bias": "NO_INVARIANT_OVERRIDE",
                },
            }


live_cognition_runtime = HHSRuntimeCognitionCoordinator()
