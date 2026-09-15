from __future__ import annotations

from hhs_runtime.pass219.platonic_multistate_fold_probe import (
    build_four_state_chiral_orbit,
    tetrahedral_multistate_translation_probe,
)


def test_two_disjoint_u36_involutions_generate_four_exact_mechanical_states() -> None:
    orbit = build_four_state_chiral_orbit()
    assert orbit["unique_mechanical_state_count"] == 4
    assert orbit["g0_self_inverse"] is True
    assert orbit["g1_self_inverse"] is True
    assert orbit["disjoint_generators_commute_mechanically"] is True
    assert orbit["all_states_admissible"] is True
    assert orbit["all_states_balanced_chirality"] is True
    assert orbit["receipt_ancestry_collapsed"] is False
    assert orbit["mechanical_orbit_signature"] == "C2_X_C2_DISJOINT_U36_FOLD_ORBIT"


def test_tetrahedral_closure_matches_four_state_complete_relation() -> None:
    report = tetrahedral_multistate_translation_probe()
    branch = report["platonic_branch"]
    assert branch == {
        "p": 3,
        "q": 3,
        "vertices": 4,
        "edges": 6,
        "faces": 4,
        "euler": 2,
    }
    assert report["hydration_quantum"] == 5184
    assert report["incidence"]["degree_by_state"] == {
        "S00": 3,
        "S01": 3,
        "S10": 3,
        "S11": 3,
    }
    assert report["incidence"]["vertex_valence_matches_q3"] is True
    assert report["incidence"]["face_count_matches"] is True
    assert report["incidence"]["euler_closure_matches"] is True
    assert report["incidence"]["complete_pair_relation_is_tetrahedral_K4"] is True


def test_every_tetrahedral_state_pair_translates_exactly_and_reversibly() -> None:
    report = tetrahedral_multistate_translation_probe()
    translation = report["translation"]
    assert translation["undirected_relation_count"] == 6
    assert translation["directed_translation_count"] == 12
    assert translation["all_pairs_exactly_translatable"] is True
    assert translation["all_routes_reversible"] is True
    assert translation["all_routes_use_only_existing_u36_fold_primitive"] is True
    assert translation["move_count_histogram"] == {1: 8, 2: 4}
    assert translation["move_count_histogram_matches_two_generator_orbit"] is True
    for route in translation["directed_routes"]:
        assert route["target_reached_exactly"] is True
        assert route["all_moves_reversible"] is True
        assert route["move_count"] in (1, 2)
        assert all(kind == "CHIRAL_PAIR_U36_FLIP" for kind in route["moves"])


def test_multistate_result_reuses_existing_local_fold_and_preserves_authority() -> None:
    report = tetrahedral_multistate_translation_probe()
    primitive = report["primitive_result"]
    assert primitive["new_local_fold_primitive_required"] is False
    assert primitive["two_commuting_order2_u36_generators_create_four_state_orbit"] is True
    assert primitive["platonic_incidence_lifts_pairwise_folds_to_multistate_relation"] is True
    assert primitive["two_fold_diagonals_exist"] is True
    assert primitive["two_fold_diagonals_are_superedge_candidates_only"] is True
    assert primitive["more_than_two_states_entangled_in_one_incidence_closure"] is True
    assert report["authority"] == {
        "diagnostic_only": True,
        "canonical_geometry_mutation": False,
        "vm81_mutation": False,
        "hash72_minting": False,
        "hash216_persistence": False,
        "floating_point_authority": False,
        "ordered_product_collapse": False,
    }
