"""Dependency-scoped I086 native Lane5 Conway transition integration."""
import pytest

from hhs_backend.runtime.hhs_pass219_lane5_recursive_hash216_composition_graph_1_40 import (
    Pass219Lane5RecursiveHash216CompositionGraph,
)
from hhs_runtime.hhs_pass220_i086_conway_lane5_candidate_v1 import (
    occupancy_from_native, register_and_reuse_conway_candidate,
)
from hhs_runtime.hhs_pass220_i086_conway_life_projection_v1 import conway_step


def test_authenticated_native_conway_blinker(tmp_path):
    parent = [0] * 81
    for col in (3, 4, 5):
        parent[4 * 9 + col] = 1
    with Pass219Lane5RecursiveHash216CompositionGraph(
        tmp_path / "i086-conway-native", vector_key=bytes(range(32)),
        backend="CPU_REFERENCE",
    ) as graph:
        result = register_and_reuse_conway_candidate(
            graph=graph, parent_state=parent, jump_id="i086-blinker",
            frame_id=0, tick=5005, cycle_index=48, layer_index=7,
        )
        assert int(result["after"]) == conway_step(occupancy_from_native(parent))
        assert result["native_path_receipt"]["accepted"] is True
        assert result["intermediate_vm81_transitions_executed"] == 0
        assert result["candidate_only"] is True
        assert result["canonical_vm81_mutation_authority"] is False
        assert len(result["inherited_hash216_array_index_root_sha256"]) == 64


def test_native_conway_rejects_unrepresentable_fixed_point(tmp_path):
    with Pass219Lane5RecursiveHash216CompositionGraph(
        tmp_path / "i086-fixed-point", vector_key=bytes(range(32)),
        backend="CPU_REFERENCE",
    ) as graph:
        with pytest.raises(ValueError, match="two nonempty"):
            register_and_reuse_conway_candidate(
                graph=graph, parent_state=[0] * 81, jump_id="i086-empty",
                frame_id=0, tick=0, cycle_index=0,
            )


def test_native_conway_rejects_invalid_native_words():
    with pytest.raises(ValueError):
        occupancy_from_native([0] * 80)
    with pytest.raises(ValueError):
        occupancy_from_native([0] * 80 + [1 << 64])
