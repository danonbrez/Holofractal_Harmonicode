"""Pass 220 I085: two exact 5,184-address neural sweeps per Hash216 array.

One physical carrier = one neural layer, 10,368 layers total. At a native
address tick k in [0,5183], the two paired layer addresses are (k, 5184+k).
Each *complete* two-sweep logical cycle uses ONE inherited Pass174 Hash216Array
with PREVIOUS/CHANGE/RECEIPT lane order and 216 SHA-256 position indexes.

This is an exact scheduling/lineage contract, not a simulated 86.8B neuron
loop, not a second optimizer, and not a realtime 60fps execution assertion.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any

from hhs_backend.runtime.hhs_pass194_multimodal_storage_training_v1 import (
    GENESIS_IDENTITY, LEGACY_FOUNDATION_ROOT,
)
from hhs_runtime.pass174.runtime import Hash216Array
from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    coordinate_5184, split_hash216,
)
from hhs_runtime.hhs_pass220_i070_i_tensor_lane5_vm81_bridge_v1 import (
    build_lane5_vm81_candidate,
)
from hhs_runtime.hhs_pass220_i085_particle_neural_layer_membrane_v1 import (
    LAYER_COUNT, LAYER_WIDTH, NOMINAL_OUTPUT_FPS,
    NEURON_COUNT, NativeLayerMembraneError, exact_int, layer_at_particle,
)

SCHEMA = "HHS_PASS_220_I085_TWO_5184_SWEEPS_ONE_HASH216_ARRAY_V1"
SWEEPS = 2
NATIVE_TICKS_PER_SWEEP = LAYER_WIDTH
NATIVE_TICKS_PER_TWO_SWEEPS = LAYER_COUNT
SOURCE_NUCLEUS_INDEX = 4


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


@lru_cache(maxsize=1)
def inherited_hash216_generator() -> str:
    """Read the *actual* I070 Lane5 candidate root, never synthesize one."""
    candidate = build_lane5_vm81_candidate(SOURCE_NUCLEUS_INDEX)
    if (
        candidate["candidate_hydration"]["roundtrip_exact"] is not True
        or candidate["inherited_i069_hydration"]["roundtrip_exact"] is not True
        or candidate["authority"]["canonical_vm81_mutation_authority"] is not False
    ):
        raise NativeLayerMembraneError("inherited native Hash216 generator not admitted")
    source = candidate["candidate_hash216"]
    split_hash216(source)
    return source


def address_tick(*, frame_id: int, sweep: int, position5184: int) -> dict[str, Any]:
    """O(1) exact position map; no per-neuron execution or dense graph."""
    f = exact_int(frame_id, "frame_id")
    which = exact_int(sweep, "sweep")
    k = exact_int(position5184, "position5184")
    if f < 0 or not 0 <= which < SWEEPS or not 0 <= k < LAYER_WIDTH:
        raise NativeLayerMembraneError("two-sweep tick address outside exact domain")
    particle = which * LAYER_WIDTH + k
    layer = layer_at_particle(particle)
    coord = coordinate_5184(k)
    if layer.physical_layer != which or layer.layer_id != particle:
        raise NativeLayerMembraneError("layer/tick transport lost original mesh identity")
    return {
        "schema": SCHEMA + "_TICK_ADDRESS",
        "frame_id": f,
        "sweep": which,
        "position5184": k,
        "native_tick_in_array": particle,
        "absolute_native_tick": f * LAYER_COUNT + particle,
        "physical_particle_layer": particle,
        "vm81_cell": coord["vm81_cell"],
        "vm81_local64": coord["local64"],
        "hash72_row": coord["hash72_row"],
        "hash72_column": coord["hash72_column"],
        "mirror5184": LAYER_WIDTH - 1 - k,
        "neuron_interval_start": str(layer.native_neuron_start),
        "neuron_interval_stop_exclusive": str(layer.native_neuron_stop),
        "native_neuron_count": str(layer.neuron_count),
    }


def paired_tick(*, frame_id: int, position5184: int) -> dict[str, Any]:
    first = address_tick(frame_id=frame_id, sweep=0, position5184=position5184)
    second = address_tick(frame_id=frame_id, sweep=1, position5184=position5184)
    if second["physical_particle_layer"] - first["physical_particle_layer"] != LAYER_WIDTH:
        raise NativeLayerMembraneError("reciprocal physical-layer pair lost")
    return {
        "schema": SCHEMA + "_PAIRED_NATIVE_TICK",
        "position5184": first["position5184"],
        "layer0": first,
        "layer1": second,
        "same_hash72_vm81_coordinate": (
            first["vm81_cell"] == second["vm81_cell"]
            and first["vm81_local64"] == second["vm81_local64"]
            and first["hash72_row"] == second["hash72_row"]
            and first["hash72_column"] == second["hash72_column"]
        ),
        "source_physics_untouched": True,
    }


def compose_single_hash216_array(*, frame_id: int) -> dict[str, Any]:
    """One inherited 216-index lineage for BOTH full 5184-neural sweeps."""
    frame = exact_int(frame_id, "frame_id")
    if frame < 0:
        raise NativeLayerMembraneError("frame_id cannot be negative")
    root = inherited_hash216_generator()
    previous, change, receipt = split_hash216(root)
    operation_body = {
        "schema": SCHEMA,
        "logical_frame": frame,
        "source_i070_candidate_hash216": root,
        "two_ordered_sweeps": (
            {"sweep": 0, "layer_first": 0, "layer_last": 5183},
            {"sweep": 1, "layer_first": 5184, "layer_last": 10367},
        ),
        "ticks_per_sweep": LAYER_WIDTH,
        "neural_layer_count": LAYER_COUNT,
        "total_neuron_addresses": str(NEURON_COUNT),
        "source_connectome": "LANE5_I065_I070_I082_HASH216_HYDRATION",
        "canonical_vm81_mutation_authority": False,
    }
    operation_identity = sha256(
        b"HHS-P220-I085-TWO-SWEEP-ARRAY-V1\0" + _canonical(operation_body)
    ).hexdigest()
    array = Hash216Array.build(
        previous, change, receipt,
        genesis_identity=GENESIS_IDENTITY,
        logical_step=frame,
        operation_identity=operation_identity,
        legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
    )
    array.verify()
    if array.combined != root or len(array.character_indexes_sha256) != 216:
        raise NativeLayerMembraneError("two-sweep Hash216 array diverged from I070")
    result = {
        "schema": SCHEMA,
        "frame_id": frame,
        "one_hash216_array_per_two_sweeps": True,
        "native_tick_count": LAYER_COUNT,
        "native_ticks_per_sweep": LAYER_WIDTH,
        "sweep_count": SWEEPS,
        "phase_coordinate_count": LAYER_WIDTH,
        "neural_address_count": str(NEURON_COUNT),
        "nominal_presentation_fps": NOMINAL_OUTPUT_FPS,
        "source_i070_candidate_hash216": root,
        "hash216_array_logical_identity_sha256": array.logical_identity_sha256,
        "hash216_array_index_root_sha256": array.index_root_sha256,
        "hash216_array_character_indexes": len(array.character_indexes_sha256),
        "ordered_lane_roles": ["PREVIOUS", "CHANGE", "RECEIPT"],
        "array_operation_identity_sha256": operation_identity,
        "selected_positions": {
            "first": paired_tick(frame_id=frame, position5184=0),
            "middle": paired_tick(frame_id=frame, position5184=2592),
            "last": paired_tick(frame_id=frame, position5184=5183),
        },
        "native_search_source": "LANE5_PASS219_1_37_TO_1_48",
        "stored_composition_source": "LANE5_PASS219_1_39_TO_1_40",
        "candidate_only": True,
        "canonical_vm81_commit": False,
        "full_weighted_neural_execution_proven": False,
        "realtime_60fps_native_neural_latency_proven": False,
    }
    return result



def search_authentic_lane5_tick(
    *, graph: Any, frame_id: int, sweep: int, position5184: int,
    current_state: tuple[int, ...] | list[int], goal_hash216: str,
    frame_array: dict[str, Any], max_hops: int = 1, beam_width: int = 16,
) -> dict[str, Any]:
    """Real 1.37/1.40 Lane 5 one-tick search using the composed array scope.

    Authenticated persisted edges are read from Lane5; if none exists the
    native search returns a fail-closed candidate miss. Never infer new edges.
    """
    from hhs_backend.runtime.hhs_pass219_lane5_recursive_hash216_composition_graph_1_40 import (
        Pass219Lane5RecursiveHash216CompositionGraph,
    )
    from hhs_python.runtime.hhs_pass219_lane5_recursive_composition_graph_bridge import CYCLE
    if not isinstance(graph, Pass219Lane5RecursiveHash216CompositionGraph):
        raise NativeLayerMembraneError("one-tick search requires real Lane5 native graph")
    a = address_tick(frame_id=frame_id, sweep=sweep, position5184=position5184)
    if not isinstance(frame_array, dict):
        raise NativeLayerMembraneError("one-tick search requires a sealed Hash216 array")
    # The frame-level 216-position array is computed once for both 5184 sweeps.
    # Validate its provenance before using it for any native graph query.
    expected = compose_single_hash216_array(frame_id=frame_id)
    for key in (
        "frame_id", "source_i070_candidate_hash216",
        "hash216_array_logical_identity_sha256",
        "hash216_array_index_root_sha256", "one_hash216_array_per_two_sweeps",
    ):
        if frame_array.get(key) != expected[key]:
            raise NativeLayerMembraneError("one-tick Hash216 array lineage mismatch")
    hops = exact_int(max_hops, "max_hops")
    beam = exact_int(beam_width, "beam_width")
    if hops < 1 or beam < 1:
        raise NativeLayerMembraneError("one-tick native search bounds invalid")
    split_hash216(goal_hash216)
    clock = a["absolute_native_tick"]
    output = graph.search(
        current_state=current_state,
        goal_hash216=goal_hash216,
        tick=clock % CYCLE,
        cycle_index=clock // CYCLE,
        max_hops=hops, beam_width=beam,
        layer_index=a["physical_particle_layer"],
    )
    if output.get("candidate_only") is not True:
        raise NativeLayerMembraneError("Lane5 search illegally promoted native candidate")
    if output.get("found") is True:
        receipt = output.get("native_path_receipt", {})
        if (
            receipt.get("accepted") is not True
            or receipt.get("exact_adjacency") is not True
            or receipt.get("persistent_edges_authenticated") is not True
            or output.get("canonical_vm81_mutation_authority") is not False
            or output.get("intermediate_vm81_transitions_executed") != 0
        ):
            raise NativeLayerMembraneError("one-tick native Lane5 search witness invalid")
        by_id = {record.jump_id: record for record in graph.memory.records()}
        for jump_id in output["path"]["jump_ids"]:
            record = by_id.get(jump_id)
            if (
                record is None or record.quarantined
                or record.layer_index != a["physical_particle_layer"]
            ):
                raise NativeLayerMembraneError("native composition edge crossed physical neural layer")
    return {
        "schema": SCHEMA + "_NATIVE_LANE5_ONE_TICK_QUERY",
        "address": a,
        "frame_hash216_array_index_root_sha256": expected["hash216_array_index_root_sha256"],
        "native_phase_cycle": CYCLE,
        "native_tick_phase": clock % CYCLE,
        "native_cycle_index": clock // CYCLE,
        "native_query": output,
        "hydrated_persistent_edges_authenticated": bool(output.get("found") is True),
        "candidate_only": True,
        "new_connectome_edges_synthesized": False,
        "canonical_vm81_mutation_authority": False,
    }


def validate_two_sweep_exact_cover(frame_id: int) -> dict[str, Any]:
    """Exhaustively verify all 10368 addresses, without visiting 86B neurons."""
    frame = exact_int(frame_id, "frame_id")
    if frame < 0:
        raise NativeLayerMembraneError("negative cycle frame")
    next_absolute = frame * LAYER_COUNT
    next_neuron = 0
    for sweep in range(SWEEPS):
        for k in range(LAYER_WIDTH):
            address = address_tick(frame_id=frame, sweep=sweep, position5184=k)
            if address["absolute_native_tick"] != next_absolute:
                raise NativeLayerMembraneError("native two-sweep tick discontinuity")
            if int(address["neuron_interval_start"]) != next_neuron:
                raise NativeLayerMembraneError("two-sweep neuron address gap/overlap")
            next_absolute += 1
            next_neuron = int(address["neuron_interval_stop_exclusive"])
    if next_neuron != NEURON_COUNT or next_absolute != (frame + 1) * LAYER_COUNT:
        raise NativeLayerMembraneError("two-sweep native cycle failed closure")
    return {
        "schema": SCHEMA + "_EXACT_COVER",
        "frame_id": frame,
        "sweep_count": SWEEPS,
        "addresses_verified": LAYER_COUNT,
        "neuron_addresses_covered": str(NEURON_COUNT),
        "no_dense_neuron_iteration": True,
        "full_exact_cover": True,
    }


def self_test() -> dict[str, Any]:
    root = compose_single_hash216_array(frame_id=0)
    cover = validate_two_sweep_exact_cover(0)
    if root["native_tick_count"] != cover["addresses_verified"]:
        raise NativeLayerMembraneError("Hash216 two-sweep witness and cover mismatch")
    return {
        "schema": SCHEMA + "_SELF_TEST",
        "status": "PASS",
        "array": root,
        "cover": cover,
    }


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))
