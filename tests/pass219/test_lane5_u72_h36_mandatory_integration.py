from __future__ import annotations

from pathlib import Path

from hhs_runtime.pass219.lane5_mandatory_optimization_dispatcher import (
    MANDATORY_CAPABILITY_ROLES,
    MANDATORY_LANE5_LINEAGE,
    Pass219Lane5LatencyCompositionAgent,
    U72_H36_CAPABILITY_ID,
)


def test_u72_h36_optimizer_is_mandatory_and_typed(tmp_path: Path) -> None:
    assert U72_H36_CAPABILITY_ID in MANDATORY_LANE5_LINEAGE
    assert MANDATORY_CAPABILITY_ROLES[U72_H36_CAPABILITY_ID] == (
        "EXACT_DYNAMIC_SCALAR_COORDINATE_OPTIMIZATION"
    )
    with Pass219Lane5LatencyCompositionAgent(state_root=tmp_path) as agent:
        status = agent.status()
    assert status["u72_h36_dynamic_scalar_optimizer"] == "CALLABLE_EXACT_PROOF"
    assert status["u72_h36_logical_coordinate_work_ratio"] == "1/72"


def test_u72_h36_optimizer_is_callable_through_latency_agent(tmp_path: Path) -> None:
    with Pass219Lane5LatencyCompositionAgent(state_root=tmp_path) as agent:
        report = agent.optimize_u72_h36_dynamic_cycle()

    assert report["optimization_selected"] == U72_H36_CAPABILITY_ID
    assert report["mandatory_optimization_dispatch"] is True
    assert report["dynamic_cycle"]["full_u72_cycle_closed"] is True
    assert report["optimization"]["reference_coordinate_visits"] == 5184
    assert report["optimization"]["optimized_coordinate_updates"] == 72
    assert report["optimization"]["avoided_coordinate_visits"] == 5112
    assert report["optimization"]["exact_reference_equality_every_transition"] is True
    assert report["authority"]["new_canonical_vm81_mutation_authority"] is False
    assert report["authority"]["new_hash72_minting_authority"] is False
    assert report["authority"]["new_hash216_persistence_authority"] is False
    assert report["authority"]["floating_point_authority"] is False
