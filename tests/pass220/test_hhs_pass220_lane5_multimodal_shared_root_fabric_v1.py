from copy import deepcopy
import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_lane5_multimodal_shared_root_fabric_v1 import (
    INVARIANT_GATE,
    INVARIANT_GATE_TEXT,
    LOCAL_CONSTRAINTS,
    MODALITIES,
    PASS166_LANGUAGE_CONTRACT,
    PASS218_RELATIONAL_SEMANTICS,
    ROOT_METADATA_SEED,
    ROOT_METADATA_SEED_TEXT,
    HASH216_LANE_ORDER,
    GENUS3_FACE_CYCLES,
    GENUS3_EDGES,
    GENUS3_VERTEX_FACE_TRIPLES,
    Pass220I042MultimodalError,
    build_multimodal_knowledge_graph,
    build_multimodal_projection_set,
    cross_modal_translation,
    lane5_multimodal_shared_root_self_test,
    lane5_multimodal_shared_root_witness,
    hash216_genus3_polyhedral_surface,
    shared_multimodal_root_payload,
    shared_multimodal_root_sha256,
    validate_multimodal_knowledge_graph,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry





def test_hash216_is_fixed_three_hash72_genus3_nonagonal_surface():
    surface = hash216_genus3_polyhedral_surface()

    assert surface["lane_order"] == ("PREVIOUS", "CHANGE", "RECEIPT")
    assert surface["lane_order"] == HASH216_LANE_ORDER
    assert surface["array_shape"] == (3, 8, 9)
    assert surface["hash72_positions_per_lane"] == 72
    assert surface["hash216_positions"] == 216

    assert surface["faces"] == 8
    assert surface["face_type"] == "FLAT_NONAGON"
    assert surface["sides_per_face"] == 9
    assert surface["vertices"] == 24
    assert surface["edges"] == 36
    assert surface["vertex_valence"] == 3
    assert surface["euler_characteristic"] == -4
    assert surface["orientable_genus"] == 3

    assert len(GENUS3_VERTEX_FACE_TRIPLES) == 24
    assert len(GENUS3_EDGES) == 36
    assert len(GENUS3_FACE_CYCLES) == 8
    assert all(len(face) == 9 for face in GENUS3_FACE_CYCLES)

    assert surface["every_face_neighbors_every_other_face"] is True
    assert surface["unique_face_pairs"] == 28
    assert len(surface["face_pair_multiplicity"]) == 28
    assert all(count in (1, 2) for count in surface["face_pair_multiplicity"].values())
    assert len(surface["repeated_face_pairs"]) == 8

    assert surface["incidence_closure"] == {
        "8x9_equals_72": True,
        "72_equals_2E": True,
        "24x3_equals_72": True,
        "V_minus_E_plus_F": -4,
        "2_minus_2g": -4,
    }

    slots = surface["slots"]
    assert len(slots) == 216
    assert tuple(slot["hash216_index"] for slot in slots) == tuple(range(216))

    for lane in range(3):
        lane_slots = slots[lane * 72:(lane + 1) * 72]
        assert {slot["lane"] for slot in lane_slots} == {lane}
        assert {slot["lane_role"] for slot in lane_slots} == {HASH216_LANE_ORDER[lane]}
        assert tuple(slot["hash72_index"] for slot in lane_slots) == tuple(range(72))
        assert {slot["face"] for slot in lane_slots} == set(range(8))
        assert all(0 <= slot["nonagon_slot"] < 9 for slot in lane_slots)


def test_hash216_surface_face_adjacency_is_complete_k8_with_eight_repeats():
    surface = hash216_genus3_polyhedral_surface()
    multiplicity = surface["face_pair_multiplicity"]

    expected_pairs = {
        f"{a}:{b}"
        for a in range(8)
        for b in range(a + 1, 8)
    }
    assert set(multiplicity) == expected_pairs

    # Every face is a neighbor of all seven others.
    neighbor_sets = []
    for face, cycle in enumerate(surface["face_neighbor_cycles"]):
        assert len(cycle) == 9
        neighbor_set = set(cycle)
        assert face not in neighbor_set
        assert neighbor_set == (set(range(8)) - {face})
        neighbor_sets.append(neighbor_set)

    # Eight extra edge adjacencies beyond K8 account for 36 total edges.
    assert sum(multiplicity.values()) == 36
    assert sum(count - 1 for count in multiplicity.values()) == 8


def test_shared_root_binds_genus3_surface_identity():
    surface = hash216_genus3_polyhedral_surface()
    payload = shared_multimodal_root_payload()
    assert payload["hash216_genus3_surface_root_sha256"] == surface["surface_root_sha256"]
    assert payload["hash216_genus3_array_shape"] == (3, 8, 9)


def test_root_seed_and_invariant_gate_are_exact_rationals():
    assert ROOT_METADATA_SEED_TEXT == "179971.179971"
    assert ROOT_METADATA_SEED.numerator == 179971179971
    assert ROOT_METADATA_SEED.denominator == 1000000
    assert INVARIANT_GATE_TEXT == "1.001"
    assert INVARIANT_GATE.numerator == 1001
    assert INVARIANT_GATE.denominator == 1000

    payload = shared_multimodal_root_payload()
    assert payload["root_metadata_seed"] == {
        "numerator": 179971179971,
        "denominator": 1000000,
    }
    assert payload["invariant_gate"] == {
        "numerator": 1001,
        "denominator": 1000,
    }
    assert payload["coordinate_closure"] == {
        "vm81x64": 5184,
        "hash72_square": 5184,
        "q144xh36": 5184,
    }


def test_shared_root_is_deterministic_and_bound_to_i040_i041_i039_ancestry():
    first = shared_multimodal_root_sha256()
    second = shared_multimodal_root_sha256()
    payload = shared_multimodal_root_payload()

    assert first == second
    assert len(first) == 64
    assert payload["i041_relativistic_projection_root_sha256"] == (
        payload["i040_projection_root_sha256"]
    )
    assert payload["i041_i039_shared_root_sha256"] == (
        payload["i040_i039_shared_root_sha256"]
    )


def test_all_six_modalities_get_exact_5184_hash72_hash216_projection():
    projections = build_multimodal_projection_set()
    assert tuple(projections) == MODALITIES
    assert tuple(projections) == (
        "LANGUAGE",
        "IMAGE",
        "AUDIO",
        "VIDEO",
        "PHYSICS",
        "GAME",
    )

    shared = shared_multimodal_root_sha256()
    for modality, projection in projections.items():
        assert projection["modality_role"] == modality
        assert projection["shared_multimodal_root_sha256"] == shared
        assert projection["projection_bits"] == 5184
        assert projection["projection_bytes"] == 648
        assert len(projection["projection_base64"]) == 864
        assert len(projection["projection_hash72"]) == 72
        assert projection["hash216_position_count"] == 216
        assert len(projection["hash216_positions"]) == 216
        assert projection["hash216_genus3_surface_shape"] == (3, 8, 9)
        assert len(projection["hash216_genus3_surface_root_sha256"]) == 64
        assert len(projection["hash216_genome_root_sha256"]) == 64
        assert projection["token_count"] > 0
        assert projection["source_bytes_retained_in_projection_record"] is False

        assert projection["canonical_vm81_mutation_authority"] is False
        assert projection["canonical_hash72_authority"] is False
        assert projection["canonical_hash216_authority"] is False
        assert projection["canonical_learning_commit_authority"] is False
        assert projection["model_weight_update_authority"] is False
        assert projection["direct_canonical_persistence_authority"] is False
        assert projection["host_float_arithmetic_used"] is False
        assert projection["probability_used"] is False
        assert projection["likelihood_used"] is False
        assert projection["mcmc_used"] is False
        assert projection["parameter_refit_performed"] is False


def test_modality_detectors_and_bindings_are_correct():
    projections = build_multimodal_projection_set()

    assert projections["LANGUAGE"]["source"]["detected_media_type"] == "TEXT"
    assert projections["IMAGE"]["source"]["detected_media_type"] == "IMAGE"
    assert projections["AUDIO"]["source"]["detected_media_type"] == "AUDIO"
    assert projections["VIDEO"]["source"]["detected_media_type"] == "VIDEO"
    assert projections["PHYSICS"]["source"]["detected_media_type"] == "JSON"
    assert projections["GAME"]["source"]["detected_media_type"] == "JSON"

    language = projections["LANGUAGE"]["semantic_binding"]
    assert language["grammar_surface"] == "ORDERED_TOKEN_GRAPH"
    assert language["pass166_contract"] == PASS166_LANGUAGE_CONTRACT
    assert language["pass218_candidate_semantics"] == PASS218_RELATIONAL_SEMANTICS
    assert language["word2vec_live_model_required_for_i042_closure"] is False
    assert language["word2vec_candidate_truth_authority"] is False

    image = projections["IMAGE"]["semantic_binding"]
    assert len(image["sprite_geometry_seed"]) == 64
    assert 0 <= image["color_q144"] < 144
    assert 0 <= image["reciprocal_color_q144"] < 144
    assert image["render_backend_is_projection_only"] is True

    audio = projections["AUDIO"]["semantic_binding"]
    assert audio["polyrhythm_ratio"] == {"numerator": 3, "denominator": 2}
    assert audio["three_pulse_ticks"] == (0, 48, 96)
    assert audio["two_pulse_ticks"] == (0, 72)
    assert audio["audio_clock_is_exact"] is True
    assert audio["pcm_device_output_is_projection_only"] is True

    video = projections["VIDEO"]["semantic_binding"]
    assert video["q144_frame_count"] == 144
    assert video["frame_clock"] == "n/144 turns"
    assert video["video_codec_output_is_projection_only"] is True

    physics = projections["PHYSICS"]["semantic_binding"]
    assert physics["u_data_close"] is True
    assert physics["delta_e"] == 0
    assert physics["psi"] == 0
    assert physics["omega"] is True

    game = projections["GAME"]["semantic_binding"]
    assert game["same_q144_drives_trig_music_color_shader"] is True
    assert game["game_state_is_exact"] is True
    assert game["rendering_is_projection"] is True


def test_cross_modal_translation_covers_every_ordered_pair_and_preserves_root():
    projections = build_multimodal_projection_set()
    shared = shared_multimodal_root_sha256()

    receipts = []
    for source in MODALITIES:
        for target in MODALITIES:
            if source == target:
                continue
            translation = cross_modal_translation(
                projections,
                source_modality=source,
                target_modality=target,
            )
            receipts.append(translation)
            assert translation["source_modality"] == source
            assert translation["target_modality"] == target
            assert translation["shared_multimodal_root_sha256"] == shared
            assert translation["translation_rule"] == (
                "COMMON_ROOT_PLUS_EXPLICIT_PROJECTION_RELATION"
            )
            assert translation["source_provenance_preserved"] is True
            assert translation["target_provenance_preserved"] is True
            assert translation["semantic_guessing_required"] is False
            assert translation["probability_used"] is False
            assert translation["canonical_mutation_authority"] is False

    assert len(receipts) == 30
    assert len({receipt["receipt_sha256"] for receipt in receipts}) == 30

    with pytest.raises(Pass220I042MultimodalError):
        cross_modal_translation(
            projections,
            source_modality="LANGUAGE",
            target_modality="LANGUAGE",
        )


def test_multimodal_knowledge_graph_has_one_root_six_nodes_and_30_translations():
    graph = build_multimodal_knowledge_graph()

    assert graph["modality_count"] == 6
    assert graph["root_edge_count"] == 6
    assert graph["directed_cross_modal_translation_count"] == 30
    assert len(graph["modality_nodes"]) == 6
    assert len(graph["root_edges"]) == 6
    assert len(graph["translation_edges"]) == 30
    assert len(graph["translation_receipts"]) == 30
    assert tuple(graph["projections"]) == MODALITIES
    assert graph["all_modalities_share_root"] is True
    assert graph["all_modalities_have_5184_projection"] is True
    assert graph["all_modalities_have_hash216_genome"] is True

    root = graph["root_node"]
    assert root["node_type"] == "SHARED_EXACT_EXECUTION_ROOT"
    assert root["shared_multimodal_root_sha256"] == (
        graph["shared_multimodal_root_sha256"]
    )

    assert {
        node["modality"] for node in graph["modality_nodes"]
    } == set(MODALITIES)

    assert graph["language_candidate_contract"] == {
        "pass166_contract": PASS166_LANGUAGE_CONTRACT,
        "pass218_candidate_semantics": PASS218_RELATIONAL_SEMANTICS,
        "candidate_only": True,
        "truth_promotion": False,
        "canonical_learning_commit": False,
    }
    assert graph["lane5_role"] == (
        "READ_ONLY_MULTIMODAL_PROJECTION_AND_ROUTING_FABRIC"
    )


def test_graph_validates_and_fails_closed_on_root_or_authority_tampering():
    graph = build_multimodal_knowledge_graph()
    result = validate_multimodal_knowledge_graph(graph)

    assert result["ok"] is True
    assert result["modality_count"] == 6
    assert result["projection_bits_per_modality"] == 5184
    assert result["projection_bytes_per_modality"] == 648
    assert result["hash216_positions_per_modality"] == 216
    assert result["directed_cross_modal_translation_count"] == 30
    assert result["audio_polyrhythm"] == {"numerator": 3, "denominator": 2}
    assert result["language_pass166_candidate_contract_bound"] is True
    assert result["all_modalities_share_root"] is True
    assert result["all_modalities_have_5184_projection"] is True
    assert result["all_modalities_have_hash216_genome"] is True
    assert result["hash216_genus3_surface_closed"] is True
    assert result["hash216_array_shape"] == (3, 8, 9)
    assert result["hash216_polyhedral_counts"] == {"V": 24, "E": 36, "F": 8}
    assert result["exact_multimodal_fabric_closed"] is True

    tampered = deepcopy(graph)
    tampered["all_modalities_share_root"] = False
    with pytest.raises(Pass220I042MultimodalError, match="receipt mismatch"):
        validate_multimodal_knowledge_graph(tampered)

    tampered = deepcopy(graph)
    tampered["canonical_vm81_mutation_authority"] = True
    with pytest.raises(Pass220I042MultimodalError, match="receipt mismatch"):
        validate_multimodal_knowledge_graph(tampered)


def test_witness_and_self_test_close():
    witness = lane5_multimodal_shared_root_witness()
    assert witness["ok"] is True
    assert witness["result"]["exact_multimodal_fabric_closed"] is True
    assert tuple(witness["local_constraints"]) == LOCAL_CONSTRAINTS
    assert witness["root_metadata_seed_text"] == "179971.179971"
    assert witness["invariant_gate_text"] == "1.001"
    assert witness["lane5_role"] == (
        "READ_ONLY_MULTIMODAL_PROJECTION_AND_ROUTING_FABRIC"
    )
    assert witness["canonical_admission_authority"] is False

    self_test = lane5_multimodal_shared_root_self_test()
    assert self_test["ok"] is True


def test_service_registry_declares_i042_constructor():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.lane5_multimodal_shared_root.self_test" in source
    assert "hhs_pass220_lane5_multimodal_shared_root_fabric_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.lane5_multimodal_shared_root.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_lane5_multimodal_shared_root_fabric_v1"
        ),
        "function": "lane5_multimodal_shared_root_self_test",
        "service_type": "pass220_validated_multimodal_projection_constructor",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_I042_LANE5_MULTIMODAL_SHARED_ROOT_FABRIC_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I042_MULTIMODAL_SHARED_ROOT_WITNESS_V1",
        ],
        "validators": [
            "validate_multimodal_knowledge_graph",
            "lane5_multimodal_shared_root_self_test",
        ],
        "rejection_codes": [
            "REJECT_I042_SHARED_ROOT_SPLIT",
            "REJECT_I042_5184_PROJECTION_LOSS",
            "REJECT_I042_HASH216_GENOME_LOSS",
            "REJECT_I042_MODALITY_PROVENANCE_LOSS",
            "REJECT_I042_TRANSLATION_PAIR_GAP",
            "REJECT_I042_LANGUAGE_AUTHORITY_ESCALATION",
            "REJECT_I042_AUDIO_CLOCK_DRIFT",
            "REJECT_I042_FLOAT_OR_PROBABILITY_PATH",
            "REJECT_I042_CANONICAL_AUTHORITY_ESCALATION",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_MULTIMODAL_FABRIC_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True
