from __future__ import annotations

import pytest

from hhs_backend.runtime.hhs_pass219_lane5_recursive_hash216_composition_graph_1_40 import (
    Pass219Lane5RecursiveHash216CompositionGraph,
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


def _persist_linear_three_edge_graph(graph, parent):
    jump1 = graph.memory.jump_store.build_validated_jump(
        jump_id="edge-1",
        parent_state=parent,
        steps=_steps(4, 3),
        tick=5005,
        cycle_index=48,
        layer_index=7,
    )
    graph.memory.persist_validated_jump(parent_state=parent, jump=jump1)

    state1 = list(jump1.child_state)
    jump2 = graph.memory.jump_store.build_validated_jump(
        jump_id="edge-2",
        parent_state=state1,
        steps=_steps(6, 17),
        tick=10010,
        cycle_index=49,
        layer_index=7,
    )
    graph.memory.persist_validated_jump(parent_state=state1, jump=jump2)

    state2 = list(jump2.child_state)
    jump3 = graph.memory.jump_store.build_validated_jump(
        jump_id="edge-3",
        parent_state=state2,
        steps=_steps(8, 29),
        tick=15015,
        cycle_index=50,
        layer_index=7,
    )
    graph.memory.persist_validated_jump(parent_state=state2, jump=jump3)
    return jump1, jump2, jump3


def test_recursive_hash216_graph_survives_restart_finds_and_reuses_three_hops(tmp_path) -> None:
    root = tmp_path / "lane5-graph"
    key = bytes(range(32))
    parent = _state(140)

    with Pass219Lane5RecursiveHash216CompositionGraph(
        root,
        vector_key=key,
        backend="CPU_REFERENCE",
    ) as graph:
        jump1, jump2, jump3 = _persist_linear_three_edge_graph(graph, parent)
        expected_terminal = list(jump3.child_state)
        expected_terminal_hash216 = jump3.child_hash216
        expected_span = jump1.jump_span + jump2.jump_span + jump3.jump_span
        assert expected_span == 18
        assert graph.status()["active_edges"] == 3
        assert graph.status()["active_vertices"] == 4

    with Pass219Lane5RecursiveHash216CompositionGraph(
        root,
        vector_key=key,
        backend="CPU_REFERENCE",
    ) as reopened:
        status = reopened.status()
        assert status["active_edges"] == 3
        assert status["persistent_composition_graph"] is True
        assert status["recursive_multi_hop_search"] is True
        assert status["exact_hash216_adjacency_required"] is True
        assert status["gpu_vector_frontier_ranking"] is True
        assert status["candidate_only"] is True
        assert status["canonical_vm81_mutation_authority"] is False

        result = reopened.search(
            current_state=parent,
            goal_hash216=expected_terminal_hash216,
            tick=20018,
            cycle_index=50,
            max_hops=3,
            beam_width=4,
            layer_index=7,
        )
        assert result["found"] is True
        assert result["exact_target"] is True
        assert result["path"]["jump_ids"] == ["edge-1", "edge-2", "edge-3"]
        assert result["path"]["hop_count"] == 3
        assert result["path"]["total_span"] == expected_span
        assert result["represented_transitions"] == expected_span
        assert result["intermediate_vm81_transitions_executed"] == 0
        assert result["terminal_state"] == expected_terminal
        assert result["native_path_receipt"]["accepted"] is True
        assert result["native_path_receipt"]["exact_adjacency"] is True
        assert result["native_path_receipt"]["persistent_edges_authenticated"] is True
        assert result["native_path_receipt"]["path_sealed"] is True
        assert result["candidate_only"] is True
        assert result["canonical_vm81_mutation_authority"] is False
        assert result["requires_signed_environmental_vm81_admission"] is True

        reused = reopened.reuse_path(
            current_state=parent,
            jump_ids=result["path"]["jump_ids"],
            goal_hash216=expected_terminal_hash216,
            tick=20018,
            cycle_index=50,
        )
        assert reused["terminal_state"] == expected_terminal
        assert reused["path"]["path_hash216"] == result["path"]["path_hash216"]
        assert reused["edge_retrievals"] == 3
        assert reused["represented_transitions"] == expected_span
        assert reused["intermediate_vm81_transitions_executed"] == 0
        assert all(
            edge["intermediate_transitions_executed_on_reuse"] == 0
            for edge in reused["edge_receipts"]
        )


def test_recursive_graph_wrong_order_and_wrong_start_fail_closed(tmp_path) -> None:
    root = tmp_path / "lane5-graph-negative"
    key = bytes([77]) * 32
    parent = _state(72)

    with Pass219Lane5RecursiveHash216CompositionGraph(
        root,
        vector_key=key,
        backend="CPU_REFERENCE",
    ) as graph:
        _, _, jump3 = _persist_linear_three_edge_graph(graph, parent)
        with pytest.raises(ValueError, match="adjacency"):
            graph.reuse_path(
                current_state=parent,
                jump_ids=["edge-2", "edge-1", "edge-3"],
                goal_hash216=jump3.child_hash216,
                tick=0,
                cycle_index=2,
            )
        wrong = list(parent)
        wrong[0] ^= 1
        with pytest.raises(ValueError, match="adjacency"):
            graph.reuse_path(
                current_state=wrong,
                jump_ids=["edge-1", "edge-2", "edge-3"],
                goal_hash216=jump3.child_hash216,
                tick=0,
                cycle_index=2,
            )


def test_recursive_graph_quarantine_breaks_route_without_exposing_authority(tmp_path) -> None:
    root = tmp_path / "lane5-graph-quarantine"
    key = bytes([19]) * 32
    parent = _state(31)

    with Pass219Lane5RecursiveHash216CompositionGraph(
        root,
        vector_key=key,
        backend="CPU_REFERENCE",
    ) as graph:
        _, _, jump3 = _persist_linear_three_edge_graph(graph, parent)
        graph.memory.quarantine("edge-2")
        result = graph.search(
            current_state=parent,
            goal_hash216=jump3.child_hash216,
            tick=5005,
            cycle_index=12,
            max_hops=3,
            beam_width=4,
            layer_index=7,
        )
        assert result["found"] is True
        assert result["exact_target"] is False
        assert result["path"]["jump_ids"] == ["edge-1"]
        assert result["candidate_only"] is True
        assert result["canonical_vm81_mutation_authority"] is False
        assert result["gpu_may_commit_hash72"] is False
        assert result["gpu_may_commit_hash216"] is False
        assert result["canonical_persistence_authority"] is False
        assert result["requires_signed_environmental_vm81_admission"] is True
        with pytest.raises(ValueError, match="quarantined"):
            graph.reuse_path(
                current_state=parent,
                jump_ids=["edge-1", "edge-2", "edge-3"],
                goal_hash216=jump3.child_hash216,
                tick=5005,
                cycle_index=12,
            )
