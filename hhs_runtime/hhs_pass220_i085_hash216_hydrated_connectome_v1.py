"""I085 Lane 5 Hash216 hydration-derived neural connectome.

The source of connectivity is existing I065/VM81 exact hydration and native
Pass 219 1.39/1.40 authenticated composition memory. Not a synthetic edge
list or a separate trained FlyWire topology. Actual native transition paths
are read and validated, never invented from neuron index distance.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    EXPANDED_VERTICES,
    HASH216_PLANES,
    compress_hash72_vertex_geometry,
    hash72_vertex_geometry,
    hydrate_hash216_geometry,
    lane5_optimization_witness,
)
from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    LANE_ORDER,
    split_hash216,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import hash72
from hhs_runtime.hhs_pass220_i085_particle_neural_layer_membrane_v1 import (
    NativeLayerMembraneError,
    bind_explicit_native_neuron,
    exact_int,
)

SCHEMA = "HHS_PASS_220_I085_LANE5_HASH216_HYDRATED_CONNECTOME_V1"
SOURCE_I065 = "HHS_PASS_220_I065_LOSSLESS_EMERGENT_COMPRESSION_HYDRATION_V1"
SOURCE_I140 = "HHS_PASS_219_LANE5_RECURSIVE_HASH216_COMPOSITION_GRAPH_1_40"


def _validate_addresses(addresses: Sequence[int]) -> tuple[int, ...]:
    if isinstance(addresses, (str, bytes)) or not isinstance(addresses, (tuple, list)):
        raise NativeLayerMembraneError("connectome addresses must be an ordered sequence")
    if not addresses or len(addresses) > EXPANDED_VERTICES:
        raise NativeLayerMembraneError("connectome address query must contain 1..5184 positions")
    normalized = tuple(exact_int(k, "connectome address") for k in addresses)
    if any(not 0 <= k < EXPANDED_VERTICES for k in normalized):
        raise NativeLayerMembraneError("connectome vertex escaped VM81/Hash72 [0,5183]")
    if len(set(normalized)) != len(normalized):
        raise NativeLayerMembraneError("connectome addresses must be unique, preserving query order")
    return normalized


def hydrate_neuron_connectome(
    *, neuron_id: int, nucleus_index: int, particle_id: int,
    addresses: Sequence[int] = (0, 71, 72, 2591, 2592, 5183),
) -> dict[str, Any]:
    """Read existing exact Lane 5 Hash216 generator relations on demand.

    PREVIOUS/CHANGE/RECEIPT ordered symbol pairs are coupled over exactly
    the SAME 5184 VM81 coordinates; palindromic mirror positions are
    inherited from I065. This is the HHS phase-connectome geometry, not
    arbitrary guessed biological synapses or executed weights.
    """
    ids = _validate_addresses(addresses)
    native = bind_explicit_native_neuron(
        neuron_id=neuron_id, nucleus_index=nucleus_index,
        particle_id=particle_id,
    )
    source_hash216 = native["i070_candidate_hash216"]
    lanes = split_hash216(source_hash216)
    hydrated = hydrate_hash216_geometry(source_hash216)
    if (
        hydrated["roundtrip_exact"] is not True
        or hydrated["hash216_positions"] != 216
        or hydrated["full_attached_components"] != 15552
    ):
        raise NativeLayerMembraneError("inherited Hash216 hydration failed closure")
    optimization = lane5_optimization_witness(1)
    if (
        optimization["expanded_vertex_materialization_required_for_search"] is not False
        or optimization["stream_generator_then_hydrate_on_demand"] is not True
        or optimization["candidate_search_only"] is not True
    ):
        raise NativeLayerMembraneError("Lane 5 on-demand hydration invariant lost")
    ordered_planes = []
    for role, plane_hash72 in zip(LANE_ORDER, lanes):
        vertices = hash72_vertex_geometry(plane_hash72)
        if compress_hash72_vertex_geometry(vertices) != plane_hash72:
            raise NativeLayerMembraneError("lossless Hash72 plane recompression failed")
        ordered_planes.append(vertices)
    if tuple(plane["role"] for plane in hydrated["planes"]) != tuple(LANE_ORDER):
        raise NativeLayerMembraneError("Hash216 ordered plane provenance changed")
    edges = []
    for k in ids:
        aligned = [plane[k] for plane in ordered_planes]
        original = aligned[0]
        keys = ("linear5184", "source_position72", "coupled_position72",
                "hash72_row", "hash72_column", "vm81_cell", "local64", "mirror5184")
        if any(any(plane[field] != original[field] for field in keys) for plane in aligned[1:]):
            raise NativeLayerMembraneError("ordered planes lost shared VM81 address")
        if original["mirror5184"] != 5183 - k:
            raise NativeLayerMembraneError("palindromic mirror connectivity lost")
        vertex = hydrated["vertex72_geometry"][original["source_position72"]]
        if tuple(plane["source_symbol"] for plane in aligned) != tuple(vertex["symbols"]):
            raise NativeLayerMembraneError("Hash216 source symbol/order diverged")
        edges.append({
            "linear5184": k,
            "source_position72": original["source_position72"],
            "coupled_position72": original["coupled_position72"],
            "vm81_cell": original["vm81_cell"],
            "vm81_local64": original["local64"],
            "mirror5184": original["mirror5184"],
            "ordered_phase_relations": [
                {
                    "role": role,
                    "source_symbol": item["source_symbol"],
                    "coupled_symbol": item["coupled_symbol"],
                    "source_sha256_codeword": vertex["sha256_codewords"][i],
                }
                for i, (role, item) in enumerate(zip(LANE_ORDER, aligned))
            ],
        })
    result = {
        "schema": SCHEMA,
        "connectome_source": SOURCE_I065,
        "neural_layer": native["particle_layer"],
        "neuron_id": native["native_neuron_id"],
        "explicit_nucleus_index": native["explicit_nucleus_index"],
        "lane5_candidate_hash216": source_hash216,
        "generator_roots": list(hydrated["planes"]),
        "full_hydrated_positions_per_plane": EXPANDED_VERTICES,
        "planes": HASH216_PLANES,
        "query_positions": list(ids),
        "hydrated_connections": edges,
        "exact_rehydration_roundtrip": True,
        "hash72_generator_recovered": True,
        "source_hhs_phase_geometry": True,
        "synthetic_connectome": False,
        "candidate_only": True,
        "canonical_vm81_mutation": False,
        "synaptic_weight_execution_claimed": False,
    }
    result["connectome_candidate_hash72"] = hash72(result)
    return result


def hydrate_persistent_connectome_path(
    *, graph: Any, current_state: Sequence[int], jump_ids: Sequence[str],
    goal_hash216: str, tick: int, cycle_index: int, particle_id: int,
) -> dict[str, Any]:
    """Invoke the REAL persisted Lane 5 1.40 native rehydration API.

    Only records actually persisted and authenticated by 1.39/1.40 may be
    returned. A Hash216 phase relation is not promoted to a neuron-neuron
    synapse or canonical VM81 state without separate native admission.
    """
    from hhs_backend.runtime.hhs_pass219_lane5_recursive_hash216_composition_graph_1_40 import (
        Pass219Lane5RecursiveHash216CompositionGraph,
    )
    if not isinstance(graph, Pass219Lane5RecursiveHash216CompositionGraph):
        raise NativeLayerMembraneError("persisted connectome must use native Lane 5 1.40 graph")
    layer = exact_int(particle_id, "particle_id")
    if not 0 <= layer < 10368:
        raise NativeLayerMembraneError("connectome particle layer out of range")
    frame = exact_int(tick, "tick")
    cycle = exact_int(cycle_index, "cycle_index")
    if frame < 0 or cycle < 0:
        raise NativeLayerMembraneError("native composition clock cannot be negative")
    if isinstance(jump_ids, (str, bytes)) or not isinstance(jump_ids, (tuple, list)):
        raise NativeLayerMembraneError("ordered persistent route IDs required")
    if not jump_ids or any(not isinstance(j, str) or not j for j in jump_ids):
        raise NativeLayerMembraneError("persisted route must have authentic jump IDs")
    if len(set(jump_ids)) != len(jump_ids):
        raise NativeLayerMembraneError("persistent path cannot repeat a jump")
    # The persistent Lane 5 1.39 record already binds an EXACT layer_index.
    # Do not attach the resulting authenticated state transition to an
    # unrelated particle/neural layer simply because the hashes validate.
    stored = {record.jump_id: record for record in graph.memory.records()}
    for jump_id in jump_ids:
        if jump_id not in stored:
            raise NativeLayerMembraneError("unpersisted neural Hash216 edge")
        record = stored[jump_id]
        if record.quarantined or type(record.layer_index) is not int or record.layer_index != layer:
            raise NativeLayerMembraneError("native persisted edge's neural layer binding diverged")
    split_hash216(goal_hash216)
    reused = graph.reuse_path(
        current_state=current_state,
        jump_ids=jump_ids,
        goal_hash216=goal_hash216,
        tick=frame,
        cycle_index=cycle,
    )
    receipt = reused["native_path_receipt"]
    path = reused["path"]
    if (
        reused["candidate_only"] is not True
        or reused["intermediate_vm81_transitions_executed"] != 0
        or reused["edge_retrievals"] != len(jump_ids)
        or path["jump_ids"] != list(jump_ids)
        or path["terminal_hash216"] != goal_hash216
        or receipt["accepted"] is not True
        or receipt["exact_adjacency"] is not True
        or receipt["persistent_edges_authenticated"] is not True
        or receipt["path_sealed"] is not True
    ):
        raise NativeLayerMembraneError("Lane 5 native persisted composition witness failed")
    return {
        "schema": SCHEMA + "_PERSISTED_NATIVE_PATH_V1",
        "connectome_source": SOURCE_I140,
        "particle_layer": layer,
        "ordered_jump_ids": list(jump_ids),
        "start_hash216": path["start_hash216"],
        "terminal_hash216": path["terminal_hash216"],
        "path_hash216": path["path_hash216"],
        "retrieved_edges": reused["edge_retrievals"],
        "represented_transitions": reused["represented_transitions"],
        "native_receipt": receipt,
        "candidate_only": True,
        "canonical_vm81_mutation": False,
        "synaptic_weight_execution_claimed": False,
    }


__all__ = [
    "SCHEMA", "SOURCE_I065", "SOURCE_I140",
    "hydrate_neuron_connectome", "hydrate_persistent_connectome_path",
]
