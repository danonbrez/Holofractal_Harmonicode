"""I086 actual inherited 1.39/1.40 composition integration, without native edits."""
import pytest

from hhs_backend.runtime.hhs_pass219_lane5_recursive_hash216_composition_graph_1_40 import (
    Pass219Lane5RecursiveHash216CompositionGraph,
)
from hhs_runtime.hhs_pass220_i086_native_orbit_composition_v1 import (
    compose_authenticated_orbit,
)


def test_native_persisted_two_segment_closed_orbit_and_negative_cases(tmp_path):
    mask = (1 << 64) - 1
    initial = [((73 * 0x9E3779B97F4A7C15) + i * 0x517CC1B727220A95) & mask
               for i in range(81)]
    step_a = [{"cell": 2, "control_g": 10, "xor_mask": 1 << 5}]
    step_b = [{"cell": 3, "control_g": 11, "xor_mask": 1 << 7}]
    with Pass219Lane5RecursiveHash216CompositionGraph(
        tmp_path / "i086-authenticated", vector_key=bytes(range(32)),
        backend="CPU_REFERENCE",
    ) as graph:
        forward = graph.memory.jump_store.build_validated_jump(
            jump_id="i086-forward", parent_state=initial,
            steps=[step_a, step_b], tick=5005, cycle_index=48, layer_index=7,
        )
        graph.memory.persist_validated_jump(parent_state=initial, jump=forward)
        child = graph.memory.reuse(
            current_state=initial, jump_id="i086-forward"
        )["child_state"]
        backward = graph.memory.jump_store.build_validated_jump(
            jump_id="i086-backward", parent_state=child,
            steps=[step_b, step_a], tick=5006, cycle_index=48, layer_index=7,
        )
        graph.memory.persist_validated_jump(parent_state=child, jump=backward)
        assert backward.child_hash216 == graph.native.state_root(initial)

        for invalid in (True, 1.0, "1", -1, 1 << 64):
            bad = list(initial)
            bad[0] = invalid
            with pytest.raises((TypeError, ValueError)):
                compose_authenticated_orbit(
                    graph=graph, initial_state=bad,
                    segments=[["i086-forward"], ["i086-backward"]],
                    frame_id=0, tick=0, cycle_index=0,
                )
        with pytest.raises(ValueError, match="81"):
            compose_authenticated_orbit(
                graph=graph, initial_state=initial[:-1],
                segments=[["i086-forward"]], frame_id=0,
                tick=0, cycle_index=0,
            )

        orbit = compose_authenticated_orbit(
            graph=graph, initial_state=initial,
            segments=[["i086-forward"], ["i086-backward"]],
            frame_id=0, tick=0, cycle_index=0,
        )
        assert orbit["orbit_closed"] is True
        assert orbit["authenticated_segment_count"] == 2
        assert orbit["represented_transitions"] == 4
        assert orbit["candidate_only"] is True
        assert orbit["canonical_vm81_mutation_authority"] is False
        assert len(orbit["composition_receipt_sha256"]) == 64

        with pytest.raises(ValueError, match="does not return"):
            compose_authenticated_orbit(
                graph=graph, initial_state=initial,
                segments=[["i086-forward"]], frame_id=0, tick=0,
                cycle_index=0,
            )
        with pytest.raises(ValueError, match="unknown or quarantined"):
            compose_authenticated_orbit(
                graph=graph, initial_state=initial,
                segments=[["missing"]], frame_id=0, tick=0, cycle_index=0,
            )
        with pytest.raises(ValueError, match="nonempty"):
            compose_authenticated_orbit(
                graph=graph, initial_state=initial,
                segments=[], frame_id=0, tick=0, cycle_index=0,
            )
