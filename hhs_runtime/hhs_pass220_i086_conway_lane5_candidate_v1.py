"""I086 Conway-to-inherited-Lane5 authenticated candidate transition adapter.

No native execution engine, tensor gate, graph, or Hash216 authority is replaced.
The occupancy bit occupies bit zero of each of the 81 uint64 VM81 cells.
Only existing 1.38/1.39 jump validation and 1.40 reuse authenticate the result.
"""
from __future__ import annotations

from typing import Sequence

from hhs_backend.runtime.hhs_pass219_lane5_recursive_hash216_composition_graph_1_40 import (
    Pass219Lane5RecursiveHash216CompositionGraph,
)
from hhs_runtime.hhs_pass220_i086_conway_life_projection_v1 import (
    MASK, conway_step,
)
from hhs_runtime.hhs_pass220_i085_two_sweep_hash216_clock_v1 import (
    compose_single_hash216_array,
)

UINT64_MAX = (1 << 64) - 1


def occupancy_from_native(state: Sequence[int]) -> int:
    if len(state) != 81 or any(
        type(word) is not int or word < 0 or word > UINT64_MAX for word in state
    ):
        raise ValueError("Conway requires exactly 81 exact uint64 native cells")
    return sum((word & 1) << i for i, word in enumerate(state))


def register_and_reuse_conway_candidate(
    *,
    graph: Pass219Lane5RecursiveHash216CompositionGraph,
    parent_state: Sequence[int],
    jump_id: str,
    frame_id: int,
    tick: int,
    cycle_index: int,
    layer_index: int = 0,
) -> dict:
    """Register and rehydrate a Conway transition via inherited native services.

    The 1.38 jump ABI requires at least two nonempty transition steps. If fewer
    than two occupancy bits change, fail closed rather than fabricate events.
    """
    if not isinstance(graph, Pass219Lane5RecursiveHash216CompositionGraph):
        raise TypeError("real inherited Lane5 1.40 graph required")
    if not jump_id or type(frame_id) is not int or frame_id < 0:
        raise ValueError("invalid jump identity or frame")
    if any(type(x) is not int or x < 0 for x in (tick, cycle_index, layer_index)):
        raise ValueError("invalid native tick, cycle or layer")
    parent = tuple(parent_state)
    before = occupancy_from_native(parent)
    after = conway_step(before)
    changed = [i for i in range(81) if ((before ^ after) >> i) & 1]
    if len(changed) < 2:
        raise ValueError("Conway transition not representable as two nonempty native jump steps")
    split = len(changed) // 2
    steps = [
        [{"cell": i, "control_g": 0, "xor_mask": 1} for i in changed[:split]],
        [{"cell": i, "control_g": 0, "xor_mask": 1} for i in changed[split:]],
    ]
    jump = graph.memory.jump_store.build_validated_jump(
        jump_id=jump_id, parent_state=parent, steps=steps,
        tick=tick, cycle_index=cycle_index, layer_index=layer_index,
    )
    expected = tuple(word ^ (((before ^ after) >> i) & 1)
                     for i, word in enumerate(parent))
    if jump.child_state != expected or occupancy_from_native(jump.child_state) != after:
        raise ValueError("native 1.38 transition diverged from Conway B3/S23")
    persisted = graph.memory.persist_validated_jump(parent_state=parent, jump=jump)
    result = graph.reuse_path(
        current_state=parent, jump_ids=[jump_id],
        goal_hash216=jump.child_hash216, tick=tick, cycle_index=cycle_index,
    )
    receipt = result["native_path_receipt"]
    if (
        receipt.get("accepted") is not True
        or receipt.get("exact_adjacency") is not True
        or receipt.get("persistent_edges_authenticated") is not True
        or result["path"]["exact_target"] is not True
        or result["intermediate_vm81_transitions_executed"] != 0
        or tuple(result["terminal_state"]) != expected
    ):
        raise ValueError("authenticated native Conway candidate rejected")
    frame = compose_single_hash216_array(frame_id=frame_id)
    return {
        "schema": "HHS_PASS220_I086_AUTHENTICATED_CONWAY_LANE5_CANDIDATE_V1",
        "before": str(before), "after": str(after),
        "changed_cells": changed,
        "parent_hash216": jump.parent_hash216,
        "child_hash216": jump.child_hash216,
        "native_path_receipt": receipt,
        "persistent_receipt": persisted,
        "inherited_hash216_array_index_root_sha256":
            frame["hash216_array_index_root_sha256"],
        "intermediate_vm81_transitions_executed": 0,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
    }
