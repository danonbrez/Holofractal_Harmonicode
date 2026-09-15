from __future__ import annotations

from hhs_runtime.pass219.fold_primitive_probe import (
    AB_RATIO_FORWARD,
    AB_RATIO_REVERSE,
    PHASE_RATIO_FORWARD,
    PHASE_RATIO_REVERSE,
    ab_p4_probe,
    combined_fold_probe,
    directed_ratio_flip,
    gyroscope_half_turn_probe,
    ordered_pq_probe,
    orthogonal_polarity_probe,
    pair_flip,
    pair_flip_round_trip,
    p_sign_probe,
    phase_relation_probe,
)


def test_generic_pair_flip_is_an_exact_involution() -> None:
    pairs = [
        ("x", "y"),
        ("z", "w"),
        ("a", "b"),
        ("p", "q"),
        ("A", "B"),
        ("P+", "P-"),
    ]
    for left, right in pairs:
        assert pair_flip(left, right) == (right, left)
        assert pair_flip_round_trip(left, right) is True


def test_directed_ratio_flips_are_distinct_and_involutive() -> None:
    assert directed_ratio_flip(PHASE_RATIO_FORWARD) == PHASE_RATIO_REVERSE
    assert directed_ratio_flip(PHASE_RATIO_REVERSE) == PHASE_RATIO_FORWARD
    assert directed_ratio_flip(AB_RATIO_FORWARD) == AB_RATIO_REVERSE
    assert directed_ratio_flip(AB_RATIO_REVERSE) == AB_RATIO_FORWARD


def test_ab_p4_probe_keeps_directional_closure_separate_from_commutative_shadow() -> None:
    probe = ab_p4_probe(5, 5, 125)
    assert probe["AB_equals_P4"] is True
    assert probe["ratio_roles_are_distinct"] is True
    assert probe["ratio_flip_is_involutive"] is True
    assert probe["full_directional_closure_scalarized"] is False
    assert probe["directional_closure_source"] == "P^4=(A^2(A/B)*B^2(B/A))/P^2"
    assert probe["commutative_shadow_source"] == "AB=P^4"


def test_orthogonal_polarity_flip_preserves_shared_c2_exactly() -> None:
    probe = orthogonal_polarity_probe(5)
    assert probe["forward"] == {"a2": 25, "b2": 50, "c2": 75}
    assert probe["reverse"] == {"a2": 50, "b2": 25, "c2": 75}
    assert probe["forward_closes"] is True
    assert probe["reverse_closes"] is True
    assert probe["shared_c2"] is True
    assert probe["round_trip_restores"] is True


def test_ordered_pq_retains_direction_while_scalar_shadow_is_shared() -> None:
    probe = ordered_pq_probe(5)
    assert probe["p"] == 4
    assert probe["q"] == 6
    assert probe["forward"] == ("pq", 4, 6)
    assert probe["reverse"] == ("qp", 6, 4)
    assert probe["scalar_projection_agrees"] is True
    assert probe["ordered_identity_collapsed"] is False
    assert probe["round_trip_restores"] is True


def test_phase_relation_preserves_ordered_reciprocal_identity() -> None:
    probe = phase_relation_probe()
    assert probe["forward"] == "xy/wz"
    assert probe["reverse"] == "zw/yx"
    assert probe["operand_map_involutive"] is True
    assert probe["ratio_flip_is_involutive"] is True
    assert probe["commutative_product_collapse_permitted"] is False


def test_each_runtime_chiral_pair_half_turn_is_self_inverse_and_admissible() -> None:
    probe = gyroscope_half_turn_probe()
    assert probe["phase_inversion_steps"] == 36
    assert probe["source_chirality_opposed"] is True
    assert probe["xy_yx_individual_round_trip"] is True
    assert probe["zw_wz_individual_round_trip"] is True
    assert probe["combined_disjoint_round_trip"] is True
    assert probe["xy_yx_product_geometry_preserved"] is True
    assert probe["zw_wz_product_geometry_preserved"] is True
    assert probe["combined_product_geometry_preserved"] is True


def test_P_sign_flip_preserves_squared_magnitude() -> None:
    probe = p_sign_probe(5)
    assert probe["forward"] == 5
    assert probe["reverse"] == -5
    assert probe["P2_forward"] == probe["P2_reverse"] == 25
    assert probe["squared_magnitude_shared"] is True
    assert probe["round_trip_restores"] is True


def test_combined_fold_exposes_minimal_candidate_primitive_classes() -> None:
    report = combined_fold_probe(P=5, A=5, B=125)
    combined = report["combined"]
    assert combined["all_typed_pair_axes_share_order_2_signature"] is True
    assert combined["all_runtime_chiral_half_turns_round_trip"] is True
    assert combined["orthogonal_c2_shared"] is True
    assert combined["P2_shared_across_sign_flip"] is True
    assert combined["AB_P4_shadow_shared"] is True
    assert combined["pq_scalar_shadow_shared"] is True
    assert combined["phase_ratio_direction_preserved"] is True
    assert combined["u36_is_exact_shortest_antipodal_Z72_fold"] is True
    assert combined["same_5184_tensor_shape_required"] is True
    assert combined["canonical_state_recomputed_from_scratch_required"] is False
    assert report["candidate_primitive_classes"] == [
        "TYPED_ORDER_2_PAIR_FLIP",
        "DIRECTED_RATIO_RECIPROCAL_FLIP",
        "SELF_INVERSE_U36_CHIRAL_PAIR_ROTATION",
        "FIXED_ORTHOGONAL_MAGNITUDE_WITNESS",
        "COMMUTATIVE_SHADOW_INVARIANT",
        "EXACT_SHORTEST_Z72_ANTIPODAL_DISPLACEMENT",
    ]
    assert report["authority"]["canonical_equation_rewrite"] is False
    assert report["authority"]["vm81_mutation"] is False
    assert report["authority"]["hash72_minting"] is False
    assert report["authority"]["hash216_persistence"] is False
