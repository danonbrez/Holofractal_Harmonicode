from hhs_backend.runtime.live_cognition_runtime_v1 import HHSRuntimeCognitionCoordinator
from hhs_backend.runtime.runtime_adaptive_goal_engine import runtime_adaptive_goal_engine
from hhs_backend.runtime.runtime_agentic_cognition_layer import runtime_agentic_cognition_layer
from hhs_backend.runtime.runtime_replay_engine import HHSRuntimeReplayEngine


def _packet(step: int, symbol: str):
    return {
        "runtime": {
            "step": step,
            "state_hash72": symbol * 72,
            "receipt_hash72": symbol.upper() * 72,
            "converged": False,
            "halted": False,
        },
        "graph_node": {"step": step},
        "vector_record": {"step": step},
    }


def _seeded_coordinator(step: int = 201, symbol: str = "g"):
    coordinator = HHSRuntimeCognitionCoordinator()
    coordinator.process_packet(
        _packet(step, symbol),
        emission={"event_hash72": "h" * 72},
    )
    return coordinator


def _seeded_task(step: int = 201, symbol: str = "g"):
    coordinator = _seeded_coordinator(step=step, symbol=symbol)
    task_data = coordinator.create_task(
        "analyze committed runtime",
        target_hash72=symbol * 72,
    )
    return coordinator, runtime_agentic_cognition_layer.tasks[task_data["task_id"]]


def test_replay_engine_accepts_live_packets_and_generates_prediction():
    engine = HHSRuntimeReplayEngine()
    first = engine.ingest_live_packet(_packet(1, "a"))
    duplicate = engine.ingest_live_packet(_packet(1, "a"))
    engine.ingest_live_packet(_packet(2, "b"))

    replay = engine.live_replay_window(limit=8)
    predictive = engine.predictive_replay(horizon=3)

    assert first["ingested"] is True
    assert duplicate["duplicate"] is True
    assert replay.total_frames == 2
    assert engine.verify_replay_equivalence(replay) is True
    assert predictive.total_frames == 3
    assert predictive.frames[0].runtime_packet["runtime"]["step"] == 3


def test_live_cognition_processes_each_committed_state_once():
    coordinator = HHSRuntimeCognitionCoordinator()
    before_goals = runtime_adaptive_goal_engine.metrics()["goals"]

    result = coordinator.process_packet(
        _packet(101, "c"),
        emission={"event_hash72": "e" * 72},
    )
    duplicate = coordinator.process_packet(
        _packet(101, "c"),
        emission={"event_hash72": "e" * 72},
    )
    goal = coordinator.create_goal("hold live state", "c" * 72)
    second = coordinator.process_packet(
        _packet(102, "d"),
        emission={"event_hash72": "f" * 72},
    )
    status = coordinator.status()

    assert result["processed"] is True
    assert result["semantic_memory_id"]
    assert result["replay_equivalent"] is True
    assert duplicate["processed"] is False
    assert duplicate["status"] == "DUPLICATE_COMMITTED_RUNTIME_STATE"
    assert goal["goal_id"]
    assert second["processed"] is True
    assert status["processed_ticks"] == 2
    assert status["duplicate_ticks"] == 1
    assert status["layers"]["adaptive_goals"]["goals"] >= before_goals + 1
    assert status["authority_boundary"]["vm81_mutation"] == "DENIED"


def test_agentic_execution_plan_generation_is_callable():
    _, task = _seeded_task()
    plan = runtime_agentic_cognition_layer.generate_execution_plan(task, replay_horizon=3)
    assert plan.task_id == task.task_id
    assert plan.steps


def test_agentic_semantic_routing_is_callable():
    _, task = _seeded_task(step=211, symbol="k")
    routing = runtime_agentic_cognition_layer.route_semantic_execution(task)
    assert "semantic" in routing
    assert "multimodal" in routing


def test_agentic_federated_scheduling_is_callable():
    _, task = _seeded_task(step=221, symbol="l")
    schedule = runtime_agentic_cognition_layer.schedule_federated_cognition(task)
    assert schedule.task_id == task.task_id
    assert schedule.consensus_state == "approved"


def test_explicit_agentic_cognition_cycle_is_callable():
    coordinator, task = _seeded_task(step=231, symbol="m")
    cognition = coordinator.execute_task(task.task_id)
    assert cognition["task"]["task_id"] == task.task_id


def test_explicit_autonomous_research_cycle_is_callable():
    coordinator = _seeded_coordinator(step=301, symbol="i")
    research = coordinator.execute_research(
        "map committed replay attractors",
        originating_goal="test_goal",
        exploration_horizon=2,
    )
    assert research["task"]["task_id"]


def test_explicit_recursive_toolchain_cycle_is_callable():
    coordinator = _seeded_coordinator(step=401, symbol="j")
    toolchain = coordinator.execute_toolchain(
        "test_cognition_task",
        "compose replay-safe semantic operators",
    )
    assert toolchain["toolchain"]["toolchain_id"]
