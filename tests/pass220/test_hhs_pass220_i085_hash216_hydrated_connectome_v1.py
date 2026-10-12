"""Real I065/Hash216 neural connectome rehydration and persisted native routes."""
from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass220_i085_hash216_hydrated_connectome_v1 import (
    SCHEMA, SOURCE_I065, SOURCE_I140,
    hydrate_neuron_connectome, hydrate_persistent_connectome_path,
)
from hhs_runtime.hhs_pass220_i085_particle_neural_layer_membrane_v1 import (
    NativeLayerMembraneError,
    NEURON_COUNT,
)


def test_hash216_hydration_gives_exact_vm81_three_plane_connectome():
    result=hydrate_neuron_connectome(
        neuron_id=0,nucleus_index=0,particle_id=0,
        addresses=(0,71,72,2591,2592,5183),
    )
    assert result["schema"]==SCHEMA
    assert result["connectome_source"]==SOURCE_I065
    assert result["neural_layer"]["layer_id"]==0
    assert result["exact_rehydration_roundtrip"]
    assert result["hash72_generator_recovered"]
    assert result["candidate_only"]
    assert result["synthetic_connectome"] is False
    assert result["synaptic_weight_execution_claimed"] is False
    assert len(result["lane5_candidate_hash216"])==216
    assert len(result["connectome_candidate_hash72"])==72
    assert [p["role"] for p in result["generator_roots"]]==["PREVIOUS","CHANGE","RECEIPT"]
    assert all(p["roundtrip_exact"] and p["expanded_vertices"]==5184 for p in result["generator_roots"])
    for k,connection in zip((0,71,72,2591,2592,5183),result["hydrated_connections"]):
        assert connection["linear5184"]==k
        assert connection["source_position72"]==k//72
        assert connection["coupled_position72"]==k%72
        assert connection["vm81_cell"]==k//64
        assert connection["vm81_local64"]==k%64
        assert connection["mirror5184"]==5183-k
        assert [rel["role"] for rel in connection["ordered_phase_relations"]]==[
            "PREVIOUS","CHANGE","RECEIPT"]
        assert all(len(rel["source_sha256_codeword"])==64 for rel in connection["ordered_phase_relations"])
    assert result==hydrate_neuron_connectome(
        neuron_id=0,nucleus_index=0,particle_id=0,
        addresses=(0,71,72,2591,2592,5183),
    )


def test_full_last_neuron_and_second_original_particle_layer():
    result=hydrate_neuron_connectome(
        neuron_id=NEURON_COUNT-1,nucleus_index=8,particle_id=10367,
        addresses=(5183,0),
    )
    assert result["neural_layer"]["physical_layer"]==1
    assert result["neuron_id"]==str(NEURON_COUNT-1)
    assert result["explicit_nucleus_index"]==8
    assert len(result["hydrated_connections"])==2
    assert result["hydrated_connections"][0]["mirror5184"]==0
    assert result["hydrated_connections"][1]["mirror5184"]==5183


@pytest.mark.parametrize("addresses", [
    (), (5184,), (-1,), (0,0), (1.0,), (True,), ("0",),
    "0", list(range(5184))+[0],
])
def test_invalid_hydration_addresses_fail_closed(addresses):
    with pytest.raises(NativeLayerMembraneError):
        hydrate_neuron_connectome(
            neuron_id=0,nucleus_index=0,particle_id=0,addresses=addresses,
        )


def test_native_hydration_cannot_cross_particles_or_invent_nucleus():
    for kw in (
        dict(neuron_id=0,nucleus_index=0,particle_id=1),
        dict(neuron_id=0,nucleus_index=9,particle_id=0),
        dict(neuron_id=True,nucleus_index=0,particle_id=0),
    ):
        with pytest.raises((NativeLayerMembraneError,ValueError)):
            hydrate_neuron_connectome(**kw)


def test_hydration_refuses_unrelated_graph_and_unpersisted_jump():
    with pytest.raises(NativeLayerMembraneError,match="native Lane 5 1.40"):
        hydrate_persistent_connectome_path(
            graph=object(),current_state=(0,)*81,
            jump_ids=("invented-edge",),goal_hash216="0"*216,
            tick=0,cycle_index=0,particle_id=0,
        )


def _state(seed: int) -> list[int]:
    mask=(1<<64)-1
    return [((seed+1)*0x9E3779B97F4A7C15
             +i*0x517CC1B727220A95)&mask for i in range(81)]


def test_real_persisted_native_lane5_composition_edge_rehydrates(tmp_path):
    """Use production native C/VM81 exact ABI and persistent vector store."""
    from hhs_backend.runtime.hhs_pass219_lane5_recursive_hash216_composition_graph_1_40 import (
        Pass219Lane5RecursiveHash216CompositionGraph,
    )
    parent=_state(115)
    with Pass219Lane5RecursiveHash216CompositionGraph(
        tmp_path/"hhs-native-connectome",
        vector_key=bytes(range(32)),
        backend="CPU_REFERENCE",
    ) as graph:
        jump=graph.memory.jump_store.build_validated_jump(
            jump_id="native-edge-for-layer7",
            parent_state=parent,
            steps=[
                [{"cell":5,"control_g":27,"xor_mask":1<<7}],
                [{"cell":6,"control_g":28,"xor_mask":1<<8}],
            ],
            tick=5005,cycle_index=48,layer_index=7,
        )
        graph.memory.persist_validated_jump(parent_state=parent,jump=jump)
        route=hydrate_persistent_connectome_path(
            graph=graph,current_state=parent,
            jump_ids=["native-edge-for-layer7"],
            goal_hash216=jump.child_hash216,
            tick=5005,cycle_index=48,particle_id=7,
        )
        assert route["schema"]==SCHEMA+"_PERSISTED_NATIVE_PATH_V1"
        assert route["connectome_source"]==SOURCE_I140
        assert route["ordered_jump_ids"]==["native-edge-for-layer7"]
        assert route["retrieved_edges"]==1
        assert route["represented_transitions"]==2
        assert route["candidate_only"] is True
        assert route["canonical_vm81_mutation"] is False
        assert route["synaptic_weight_execution_claimed"] is False
        assert route["native_receipt"]["accepted"] is True
        assert route["native_receipt"]["exact_adjacency"] is True
        assert route["native_receipt"]["persistent_edges_authenticated"] is True
        assert route["native_receipt"]["path_sealed"] is True
        with pytest.raises((KeyError,ValueError)):
            hydrate_persistent_connectome_path(
                graph=graph,current_state=parent,
                jump_ids=["not-persisted"],
                goal_hash216=jump.child_hash216,
                tick=5005,cycle_index=48,particle_id=7,
            )
        wrong=parent.copy()
        wrong[0]^=1
        with pytest.raises(ValueError):
            hydrate_persistent_connectome_path(
                graph=graph,current_state=wrong,
                jump_ids=["native-edge-for-layer7"],
                goal_hash216=jump.child_hash216,
                tick=5005,cycle_index=48,particle_id=7,
            )
