"""I086 composition-only orbit queries over inherited authenticated Lane 5 objects.

No native graph mutation, synthetic edges, or replacement scheduler.
A closed orbit is represented by ordered authenticated path *segments*, each
simple under the inherited 1.40 rules. Closure is checked across segments.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Sequence

from hhs_backend.runtime.hhs_pass219_lane5_recursive_hash216_composition_graph_1_40 import (
    Pass219Lane5RecursiveHash216CompositionGraph,
)
from hhs_runtime.hhs_pass220_i085_two_sweep_hash216_clock_v1 import (
    compose_single_hash216_array,
)
from hhs_runtime.hhs_pass220_i085_particle_neural_layer_membrane_v1 import exact_int

SCHEMA = "HHS_PASS_220_I086_COMPOSED_NATIVE_HASH216_ORBIT_V1"


def compose_authenticated_orbit(
    *,
    graph: Pass219Lane5RecursiveHash216CompositionGraph,
    initial_state: Sequence[int],
    segments: Sequence[Sequence[str]],
    frame_id: int,
    tick: int,
    cycle_index: int,
) -> dict[str, Any]:
    """Compose existing authenticated simple paths; final root must equal initial root.

    Each segment delegates all state hydration and edge validation to 1.40.
    The resulting orbit receipt is a candidate-level exact Hash216 return.
    """
    if not isinstance(graph, Pass219Lane5RecursiveHash216CompositionGraph):
        raise TypeError("I086 requires inherited Lane 5 1.40 graph")
    frame = exact_int(frame_id, "frame_id")
    tick = exact_int(tick, "tick")
    cycle = exact_int(cycle_index, "cycle_index")
    if min(frame, tick, cycle) < 0:
        raise ValueError("negative orbit clock")
    if not segments or any(not segment for segment in segments):
        raise ValueError("orbit must contain nonempty native path segments")
    current = tuple(int(v) for v in initial_state)
    root = graph.native.state_root(current)
    array = compose_single_hash216_array(frame_id=frame)
    lineage = []
    total_span = 0
    for segment_index, segment in enumerate(segments):
        # Resolve the terminal from authenticated persistent records; reuse_path
        # then checks exact adjacency, hydration, and the signed native receipt.
        by_id = {record.jump_id: record for record in graph.memory.records()}
        final = by_id.get(str(segment[-1]))
        if final is None or final.quarantined:
            raise ValueError("unknown or quarantined terminal edge")
        result = graph.reuse_path(
            current_state=current,
            jump_ids=segment,
            goal_hash216=final.child_hash216,
            tick=tick + segment_index,
            cycle_index=cycle,
        )
        receipt = result["native_path_receipt"]
        if (receipt.get("accepted") is not True
                or receipt.get("exact_adjacency") is not True
                or receipt.get("persistent_edges_authenticated") is not True
                or result["path"]["exact_target"] is not True
                or result["intermediate_vm81_transitions_executed"] != 0):
            raise ValueError("native orbit segment admission failed")
        current = tuple(result["terminal_state"])
        total_span += result["represented_transitions"]
        lineage.append(result["path"]["path_hash216"])
    terminal = graph.native.state_root(current)
    if terminal != root:
        raise ValueError("composed orbit does not return to original Hash216 root")
    body = {
        "schema": SCHEMA,
        "start_hash216": root,
        "terminal_hash216": terminal,
        "ordered_segment_path_hash216": lineage,
        "total_span": total_span,
        "frame_array_index_root_sha256": array["hash216_array_index_root_sha256"],
    }
    seal = sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        **body,
        "composition_receipt_sha256": seal,
        "orbit_closed": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "fundamental_period_proven": False,
        "authenticated_segment_count": len(lineage),
        "represented_transitions": total_span,
    }
