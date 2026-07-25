from hhs_backend.runtime.live_cognition_runtime_v1 import HHSRuntimeCognitionCoordinator
from hhs_backend.runtime.runtime_adaptive_goal_engine import runtime_adaptive_goal_engine
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


def test_explicit_cognition_research_and_toolchain_cycles_are_callable():
    coordinator = HHSRuntimeCognitionCoordinator()
    coordinator.process_packet(
        _packet(201, "g"),
        emission={"event_hash72": "h" * 72},
    )

    task = coordinator.create_task(
        "analyze committed runtime",
        target_hash72="g" * 72,
    )
    cognition = coordinator.execute_task(task["task_id"])
    research = coordinator.execute_research(
        "map committed replay attractors",
        originating_goal="test_goal",
        exploration_horizon=2,
    )
    toolchain = coordinator.execute_toolchain(
        "test_cognition_task",
        "compose replay-safe semantic operators",
    )

    assert cognition["task"]["task_id"] == task["task_id"]
    assert research["task"]["task_id"]
    assert toolchain["toolchain"]["toolchain_id"]
