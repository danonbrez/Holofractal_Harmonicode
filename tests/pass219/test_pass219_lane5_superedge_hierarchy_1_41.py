from __future__ import annotations

import json

import pytest

from hhs_backend.runtime.hhs_pass219_lane5_superedge_hierarchy_1_41 import (
    Pass219Lane5SuperedgeHierarchy,
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


def _persist_six_edges(hierarchy, parent):
    counts = (4, 6, 8, 5, 7, 9)
    salts = (3, 17, 29, 41, 53, 67)
    current = list(parent)
    jumps = []
    states = [list(parent)]
    for index, (count, salt) in enumerate(zip(counts, salts), start=1):
        jump = hierarchy.memory.jump_store.build_validated_jump(
            jump_id=f"edge-{index}",
            parent_state=current,
            steps=_steps(count, salt),
            tick=(index * 5005) % 20020,
            cycle_index=70 + index,
            layer_index=7,
        )
        hierarchy.memory.persist_validated_jump(parent_state=current, jump=jump)
        current = list(jump.child_state)
        jumps.append(jump)
        states.append(list(current))
    return jumps, states


def _promote_level_one_pair(hierarchy, parent, jumps, states):
    a = hierarchy.promote_path(
        superedge_id="super-A",
        current_state=parent,
        jump_ids=["edge-1", "edge-2", "edge-3"],
        goal_hash216=jumps[2].child_hash216,
        tick=20018,
        cycle_index=80,
    )
    b = hierarchy.promote_path(
        superedge_id="super-B",
        current_state=states[3],
        jump_ids=["edge-4", "edge-5", "edge-6"],
        goal_hash216=jumps[5].child_hash216,
        tick=5004,
        cycle_index=82,
    )
    return a, b


def test_superedge_hierarchy_restart_level1_level2_and_one_snapshot_reuse(tmp_path) -> None:
    root = tmp_path / "lane5-superedges"
    key = bytes(range(32))
    parent = _state(141)

    with Pass219Lane5SuperedgeHierarchy(root, vector_key=key) as hierarchy:
        jumps, states = _persist_six_edges(hierarchy, parent)
        a, b = _promote_level_one_pair(hierarchy, parent, jumps, states)
        assert a["hierarchy_level"] == 1
        assert a["base_hops"] == 3
        assert a["total_span"] == 18
        assert b["hierarchy_level"] == 1
        assert b["base_hops"] == 3
        assert b["total_span"] == 21
        assert hierarchy.status()["levels"] == {1: 2}

    with Pass219Lane5SuperedgeHierarchy(root, vector_key=key) as reopened:
        status = reopened.status()
        assert status["active_superedges"] == 2
        assert status["restart_rehydratable_superedges"] is True
        assert status["one_snapshot_direct_reuse"] is True
        assert status["candidate_only"] is True
        assert status["canonical_vm81_mutation_authority"] is False

        reused_a = reopened.reuse(current_state=parent, superedge_id="super-A")
        assert reused_a["hierarchy_level"] == 1
        assert reused_a["child_state"] == states[3]
        assert reused_a["persistent_snapshot_retrievals"] == 1
        assert reused_a["component_snapshot_retrievals"] == 0
        assert reused_a["represented_transitions"] == 18
        assert reused_a["intermediate_vm81_transitions_executed"] == 0

        ranked = reopened.search(
            current_state=parent,
            goal_hash216=jumps[2].child_hash216,
            tick=20018,
            cycle_index=80,
            layer_index=7,
            top_k=4,
        )
        assert ranked["superedge_hierarchy"] is True
        assert ranked["ranked"][0]["candidate_id"] == "super-A"
        assert ranked["ranked"][0]["hash216_distance"] == 0

        promoted = reopened.promote_superedges(
            superedge_id="super-AB",
            current_state=parent,
            component_superedge_ids=["super-A", "super-B"],
            goal_hash216=jumps[5].child_hash216,
            tick=15015,
            cycle_index=84,
        )
        assert promoted["hierarchy_level"] == 2
        assert promoted["direct_component_count"] == 2
        assert promoted["base_hops"] == 6
        assert promoted["total_span"] == 39
        assert promoted["leaf_jump_ids"] == [
            "edge-1", "edge-2", "edge-3", "edge-4", "edge-5", "edge-6"
        ]

    with Pass219Lane5SuperedgeHierarchy(root, vector_key=key) as reopened_again:
        status = reopened_again.status()
        assert status["active_superedges"] == 3
        assert status["levels"] == {1: 2, 2: 1}
        reused = reopened_again.reuse(current_state=parent, superedge_id="super-AB")
        assert reused["hierarchy_level"] == 2
        assert reused["child_state"] == states[6]
        assert reused["base_hops"] == 6
        assert reused["represented_transitions"] == 39
        assert reused["persistent_snapshot_retrievals"] == 1
        assert reused["component_snapshot_retrievals"] == 0
        assert reused["intermediate_vm81_transitions_executed"] == 0
        assert reused["native_receipt"]["one_snapshot_direct_reuse"] is True
        assert reused["candidate_only"] is True
        assert reused["canonical_vm81_mutation_authority"] is False
        assert reused["requires_signed_environmental_vm81_admission"] is True


def test_superedge_dependency_quarantine_revokes_higher_level_reuse(tmp_path) -> None:
    root = tmp_path / "lane5-superedge-revocation"
    key = bytes([31]) * 32
    parent = _state(73)

    with Pass219Lane5SuperedgeHierarchy(root, vector_key=key) as hierarchy:
        jumps, states = _persist_six_edges(hierarchy, parent)
        _promote_level_one_pair(hierarchy, parent, jumps, states)
        hierarchy.promote_superedges(
            superedge_id="super-AB",
            current_state=parent,
            component_superedge_ids=["super-A", "super-B"],
            goal_hash216=jumps[5].child_hash216,
            tick=15015,
            cycle_index=84,
        )
        hierarchy.memory.quarantine("edge-2")
        with pytest.raises(ValueError, match="dependency"):
            hierarchy.reuse(current_state=parent, superedge_id="super-AB")
        records = {record.superedge_id: record for record in hierarchy.records()}
        assert records["super-AB"].quarantined is True


def test_superedge_wrong_parent_and_id_collision_fail_closed(tmp_path) -> None:
    root = tmp_path / "lane5-superedge-negative"
    key = bytes([47]) * 32
    parent = _state(19)

    with Pass219Lane5SuperedgeHierarchy(root, vector_key=key) as hierarchy:
        jumps, states = _persist_six_edges(hierarchy, parent)
        hierarchy.promote_path(
            superedge_id="super-A",
            current_state=parent,
            jump_ids=["edge-1", "edge-2", "edge-3"],
            goal_hash216=jumps[2].child_hash216,
            tick=0,
            cycle_index=9,
        )
        wrong = list(parent)
        wrong[0] ^= 1
        with pytest.raises(ValueError, match="parent"):
            hierarchy.reuse(current_state=wrong, superedge_id="super-A")
        with pytest.raises(ValueError, match="collision"):
            hierarchy.promote_path(
                superedge_id="super-A",
                current_state=states[3],
                jump_ids=["edge-4", "edge-5", "edge-6"],
                goal_hash216=jumps[5].child_hash216,
                tick=0,
                cycle_index=10,
            )


def test_superedge_tampered_row_isolated_on_restart(tmp_path) -> None:
    root = tmp_path / "lane5-superedge-tamper"
    key = bytes([59]) * 32
    parent = _state(88)

    with Pass219Lane5SuperedgeHierarchy(root, vector_key=key) as hierarchy:
        jumps, states = _persist_six_edges(hierarchy, parent)
        _promote_level_one_pair(hierarchy, parent, jumps, states)
        hierarchy._connection.execute(
            "UPDATE lane5_superedges SET component_ids_json=? WHERE superedge_id=?",
            (json.dumps(["edge-3", "edge-2", "edge-1"]), "super-A"),
        )
        hierarchy._connection.commit()

    with Pass219Lane5SuperedgeHierarchy(root, vector_key=key) as reopened:
        records = {record.superedge_id: record for record in reopened.records()}
        assert records["super-A"].quarantined is True
        assert records["super-B"].quarantined is False
        reused_b = reopened.reuse(current_state=states[3], superedge_id="super-B")
        assert reused_b["child_state"] == states[6]


def test_superedge_rejects_fractional_vm5184_words(tmp_path) -> None:
    root = tmp_path / "lane5-superedge-fractional"
    key = bytes([71]) * 32
    parent = _state(97)

    with Pass219Lane5SuperedgeHierarchy(root, vector_key=key) as hierarchy:
        jumps, _ = _persist_six_edges(hierarchy, parent)
        fractional = list(parent)
        fractional[0] = float(fractional[0]) + 0.5
        with pytest.raises((TypeError, ValueError), match="integer|word|exact"):
            hierarchy.promote_path(
                superedge_id="fractional",
                current_state=fractional,
                jump_ids=["edge-1", "edge-2", "edge-3"],
                goal_hash216=jumps[2].child_hash216,
                tick=0,
                cycle_index=11,
            )
