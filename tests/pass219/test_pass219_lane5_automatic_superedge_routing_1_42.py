from __future__ import annotations

import pytest

from hhs_backend.runtime.hhs_pass219_lane5_automatic_superedge_routing_1_42 import (
    Pass219Lane5AutomaticSuperedgeRouter,
)


def _state(seed: int) -> list[int]:
    mask = (1 << 64) - 1
    return [
        ((seed + 1) * 0x9E3779B97F4A7C15 + cell * 0x517CC1B727220A95) & mask
        for cell in range(81)
    ]


def _steps(count: int, salt: int) -> list[list[dict[str, int]]]:
    result = []
    for index in range(count):
        bit_a = (index * 7 + salt) % 64
        bit_b = (index * 13 + salt + 11) % 64
        result.append([
            {
                "cell": (index * 17 + salt) % 81,
                "control_g": (index * 23 + salt * 5) % 243,
                "xor_mask": (1 << bit_a) | (1 << bit_b),
            }
        ])
    return result


def _persist_six_edges(router, parent):
    counts = (4, 6, 8, 5, 7, 9)
    salts = (3, 17, 29, 41, 53, 67)
    current = list(parent)
    jumps = []
    states = [list(parent)]
    for index, (count, salt) in enumerate(zip(counts, salts), start=1):
        jump = router.hierarchy.memory.jump_store.build_validated_jump(
            jump_id=f"edge-{index}",
            parent_state=current,
            steps=_steps(count, salt),
            tick=(index * 5005) % 20020,
            cycle_index=100 + index,
            layer_index=7,
        )
        router.hierarchy.memory.persist_validated_jump(parent_state=current, jump=jump)
        current = list(jump.child_state)
        jumps.append(jump)
        states.append(list(current))
    return jumps, states


def test_repeated_exact_level0_route_promotes_and_survives_restart(tmp_path) -> None:
    root = tmp_path / "lane5-auto-promotion"
    key = bytes(range(32))
    parent = _state(142)

    with Pass219Lane5AutomaticSuperedgeRouter(root, vector_key=key) as router:
        jumps, states = _persist_six_edges(router, parent)
        first = router.observe_level0_route(
            current_state=parent,
            jump_ids=["edge-1", "edge-2", "edge-3"],
            goal_hash216=jumps[2].child_hash216,
            tick=5005,
            cycle_index=110,
        )
        assert first["observation_count"] == 1
        assert first["promoted_superedge_id"] is None

        second = router.observe_level0_route(
            current_state=parent,
            jump_ids=["edge-1", "edge-2", "edge-3"],
            goal_hash216=jumps[2].child_hash216,
            tick=5005,
            cycle_index=110,
        )
        assert second["observation_count"] == 2
        assert second["promotion_gain_retrievals"] == 2
        assert second["promoted_superedge_id"].startswith("auto-se-")
        assert second["promotion"]["hierarchy_level"] == 1

        plan = router.plan_route(
            current_state=parent,
            goal_hash216=jumps[2].child_hash216,
            tick=5005,
            cycle_index=111,
            layer_index=7,
        )
        assert plan["found"] is True
        assert plan["retrieval_count"] == 1
        assert plan["max_hierarchy_level"] == 1
        assert plan["edges"][0]["candidate_id"] == second["promoted_superedge_id"]
        reused = router.execute_plan(current_state=parent, plan=plan)
        assert reused["terminal_state"] == states[3]
        assert reused["intermediate_vm81_transitions_executed"] == 0

    with Pass219Lane5AutomaticSuperedgeRouter(root, vector_key=key) as reopened:
        status = reopened.status()
        assert status["observed_routes"] == 1
        assert status["exact_observations"] == 2
        assert status["promoted_routes"] == 1
        observation = reopened.observations()[0]
        assert observation["observed_count"] == 2
        assert observation["promoted_superedge_id"] == second["promoted_superedge_id"]
        plan = reopened.plan_route(
            current_state=parent,
            goal_hash216=jumps[2].child_hash216,
            tick=5005,
            cycle_index=112,
            layer_index=7,
        )
        assert plan["retrieval_count"] == 1
        assert plan["edges"][0]["candidate_id"] == observation["promoted_superedge_id"]


def test_cross_level_mixed_route_then_higher_level_auto_promotion(tmp_path) -> None:
    root = tmp_path / "lane5-cross-level"
    key = bytes([37]) * 32
    parent = _state(73)

    with Pass219Lane5AutomaticSuperedgeRouter(root, vector_key=key) as router:
        jumps, states = _persist_six_edges(router, parent)
        router.hierarchy.promote_path(
            superedge_id="super-A",
            current_state=parent,
            jump_ids=["edge-1", "edge-2", "edge-3"],
            goal_hash216=jumps[2].child_hash216,
            tick=0,
            cycle_index=120,
        )

        mixed = router.plan_route(
            current_state=parent,
            goal_hash216=jumps[4].child_hash216,
            tick=0,
            cycle_index=121,
            layer_index=7,
        )
        assert mixed["found"] is True
        assert mixed["retrieval_count"] == 3
        assert [edge["candidate_kind"] for edge in mixed["edges"]] == [
            "SUPEREDGE", "LEVEL0", "LEVEL0"
        ]
        assert [edge["candidate_id"] for edge in mixed["edges"]] == [
            "super-A", "edge-4", "edge-5"
        ]
        mixed_reuse = router.execute_plan(current_state=parent, plan=mixed)
        assert mixed_reuse["terminal_state"] == states[5]

        router.hierarchy.promote_path(
            superedge_id="super-B",
            current_state=states[3],
            jump_ids=["edge-4", "edge-5", "edge-6"],
            goal_hash216=jumps[5].child_hash216,
            tick=0,
            cycle_index=122,
        )
        plan_two = router.plan_route(
            current_state=parent,
            goal_hash216=jumps[5].child_hash216,
            tick=0,
            cycle_index=123,
            layer_index=7,
        )
        assert plan_two["retrieval_count"] == 2
        assert [edge["candidate_id"] for edge in plan_two["edges"]] == ["super-A", "super-B"]

        first = router.observe_superedge_chain(
            current_state=parent,
            component_superedge_ids=["super-A", "super-B"],
            goal_hash216=jumps[5].child_hash216,
            tick=0,
            cycle_index=124,
        )
        second = router.observe_superedge_chain(
            current_state=parent,
            component_superedge_ids=["super-A", "super-B"],
            goal_hash216=jumps[5].child_hash216,
            tick=0,
            cycle_index=124,
        )
        assert first["promoted_superedge_id"] is None
        assert second["promotion"]["hierarchy_level"] == 2
        assert second["promotion"]["base_hops"] == 6
        assert second["promotion"]["total_span"] == 39

        compressed = router.plan_route(
            current_state=parent,
            goal_hash216=jumps[5].child_hash216,
            tick=0,
            cycle_index=125,
            layer_index=7,
        )
        assert compressed["retrieval_count"] == 1
        assert compressed["max_hierarchy_level"] == 2
        assert compressed["edges"][0]["candidate_id"] == second["promoted_superedge_id"]
        final = router.execute_plan(current_state=parent, plan=compressed)
        assert final["terminal_state"] == states[6]
        assert final["represented_transitions"] == 39


def test_quarantine_impossible_goal_and_wrong_parent_fail_closed(tmp_path) -> None:
    root = tmp_path / "lane5-auto-negative"
    key = bytes([53]) * 32
    parent = _state(19)

    with Pass219Lane5AutomaticSuperedgeRouter(root, vector_key=key) as router:
        jumps, states = _persist_six_edges(router, parent)
        router.hierarchy.promote_path(
            superedge_id="super-A",
            current_state=parent,
            jump_ids=["edge-1", "edge-2", "edge-3"],
            goal_hash216=jumps[2].child_hash216,
            tick=0,
            cycle_index=130,
        )
        router.memory.quarantine("edge-2")
        with pytest.raises(ValueError, match="quarantined|edge"):
            router.observe_level0_route(
                current_state=parent,
                jump_ids=["edge-1", "edge-2", "edge-3"],
                goal_hash216=jumps[2].child_hash216,
                tick=0,
                cycle_index=131,
            )
        blocked = router.plan_route(
            current_state=parent,
            goal_hash216=jumps[2].child_hash216,
            tick=0,
            cycle_index=132,
            layer_index=7,
        )
        assert blocked["found"] is False

        impossible_hash = router.native.state_root(_state(999))
        impossible = router.plan_route(
            current_state=states[3],
            goal_hash216=impossible_hash,
            tick=0,
            cycle_index=133,
            layer_index=7,
            max_retrievals=4,
        )
        assert impossible["found"] is False

        reachable = router.plan_route(
            current_state=states[3],
            goal_hash216=jumps[5].child_hash216,
            tick=0,
            cycle_index=134,
            layer_index=7,
        )
        assert reachable["found"] is True
        wrong = list(states[3])
        wrong[0] ^= 1
        with pytest.raises(ValueError, match="parent"):
            router.execute_plan(current_state=wrong, plan=reachable)
