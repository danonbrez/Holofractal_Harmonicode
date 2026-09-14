from __future__ import annotations

import pytest

from hhs_runtime.pass219.discrete_hopf_projection import (
    Q8,
    DiscreteHopfProjectionError,
    audit_rml5_generators_on_hopf_candidate,
    classify_chiral_pair_flip_hopf,
    classify_coupled_generator_hopf,
    hopf_project_embedding,
    hopf_project_s7_point,
    witness_q8_hopf_fiber,
)
from hhs_runtime.pass219.discrete_s7_embedding import build_discrete_s7_embedding
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    build_gyroscope_state,
    expected_product_phase,
)


def _state(
    *,
    x: int = 0,
    y: int = 12,
    z: int = 24,
    w: int = 36,
    xy_sign: int = 1,
    zw_sign: int = 1,
    state_id: str = "rml7:test",
) -> dict[str, object]:
    signs = {"xy": xy_sign, "yx": -xy_sign, "zw": zw_sign, "wz": -zw_sign}
    phases = {
        "x": x,
        "y": y,
        "z": z,
        "w": w,
        "xy": expected_product_phase(x, signs["xy"]),
        "yx": expected_product_phase(y, signs["yx"]),
        "zw": expected_product_phase(z, signs["zw"]),
        "wz": expected_product_phase(w, signs["wz"]),
    }
    return build_gyroscope_state(phases, signs, state_id=state_id)


def test_exact_quaternionic_hopf_projection_maps_s7_to_unit_s4() -> None:
    embedding = build_discrete_s7_embedding(_state())
    hopf = hopf_project_embedding(embedding)
    assert len(hopf["s4_coordinate_numerators"]) == 5
    assert hopf["s4_norm_numerator"] == hopf["s4_norm_denominator"]
    assert hopf["exact_unit_s4_identity_verified"] is True
    assert hopf["quaternion_product_norm_identity_verified"] is True
    assert hopf["floating_point_coordinates_used"] is False
    split = hopf["quaternion_split"]
    assert split["q1_norm_numerator"] + split["q2_norm_numerator"] == split["common_denominator"] ** 2


def test_all_q8_simultaneous_right_actions_preserve_exact_hopf_base() -> None:
    embedding = build_discrete_s7_embedding(_state(x=71, y=7, z=35, w=18))
    source = hopf_project_embedding(embedding)
    for element in Q8:
        witness = witness_q8_hopf_fiber(embedding, element)
        assert witness["same_hopf_base_exactly"] is True
        assert witness["source_s4_point_sha256"] == source["s4_point_sha256"]
        assert witness["transformed_s4_point_sha256"] == source["s4_point_sha256"]
        assert witness["q8_is_unit_quaternion_action"] is True
        assert witness["simultaneous_right_action_on_q1_q2"] is True
        assert witness["full_s3_fiber_closure_claimed"] is False


def test_identity_coupled_move_is_same_hopf_base_and_inverse_exact() -> None:
    witness = classify_coupled_generator_hopf(
        _state(),
        generator="x",
        signed_steps=0,
        transition_id="identity-x",
    )
    assert witness["same_hopf_base"] is True
    assert witness["classification"] == "FIBER_PRESERVING_SAME_HOPF_BASE"
    assert witness["explicit_inverse_restores_exact_hopf_base"] is True
    assert witness["source_s4_point_sha256"] == witness["target_s4_point_sha256"]
    assert witness["source_s4_point_sha256"] == witness["restored_s4_point_sha256"]


@pytest.mark.parametrize("generator", ["x", "y", "z", "w"])
@pytest.mark.parametrize("delta", [-18, -1, 1, 18, 36, 71])
def test_nontrivial_coupled_moves_are_exactly_classified_and_invertible(generator: str, delta: int) -> None:
    witness = classify_coupled_generator_hopf(
        _state(x=71, y=5, z=35, w=70),
        generator=generator,
        signed_steps=delta,
        transition_id=f"{generator}:{delta}",
    )
    assert witness["classification"] in {
        "FIBER_PRESERVING_SAME_HOPF_BASE",
        "BASE_MOVING_HOPF_TRANSPORT",
    }
    assert witness["source_target_exact_unit_s4"] is True
    assert witness["explicit_inverse_restores_exact_hopf_base"] is True
    assert witness["source_s4_point_sha256"] == witness["restored_s4_point_sha256"]
    assert witness["full_fiber_equivariance_claimed"] is False


@pytest.mark.parametrize("pair_index", [0, 1])
def test_u36_pair_flips_are_exactly_classified_and_self_restore_hopf_base(pair_index: int) -> None:
    witness = classify_chiral_pair_flip_hopf(
        _state(),
        pair_index=pair_index,
        transition_id=f"pair:{pair_index}",
    )
    assert witness["classification"] in {
        "FIBER_PRESERVING_SAME_HOPF_BASE",
        "BASE_MOVING_HOPF_TRANSPORT",
    }
    assert witness["source_target_exact_unit_s4"] is True
    assert witness["explicit_inverse_restores_exact_hopf_base"] is True
    assert witness["source_s4_point_sha256"] == witness["restored_s4_point_sha256"]


def test_complete_rml5_generator_family_is_partitioned_on_hopf_candidate() -> None:
    audit = audit_rml5_generators_on_hopf_candidate(_state(x=71, y=0, z=35, w=71))
    assert audit["coupled_z72_cases"] == 288
    assert audit["u36_pair_flip_cases"] == 2
    assert audit["total_generator_cases"] == 290
    assert audit["classification_partition_complete"] is True
    assert audit["same_base_fiber_preserving_cases"] + audit["base_moving_cases"] == 290
    assert audit["same_base_fiber_preserving_cases"] >= 4
    assert audit["inverse_hopf_base_restoration_failures"] == 0
    assert audit["all_explicit_inverses_restore_hopf_base"] is True
    assert audit["rml5_generators_proven_to_map_exact_s7_points_to_exact_s4_base_points"] is True
    assert audit["all_rml5_generators_claimed_fiber_preserving"] is False
    assert audit["full_rml6_discrete_image_s3_fiber_equivariance_proven"] is False
    assert audit["bott_periodicity_correspondence_claimed"] is False


def test_hopf_projection_rejects_non_unit_s7_and_float_input() -> None:
    embedding = build_discrete_s7_embedding(_state())
    point = dict(embedding["s7_point"])
    point["coordinate_numerators"] = list(point["coordinate_numerators"])
    point["coordinate_numerators"][0] += 1
    with pytest.raises(DiscreteHopfProjectionError, match="S7_EXACT_UNIT_NORM_REQUIRED"):
        hopf_project_s7_point(point)

    point = dict(embedding["s7_point"])
    point["common_denominator"] = 1.0
    with pytest.raises(DiscreteHopfProjectionError, match="FLOAT_HOPF_AUTHORITY_FORBIDDEN"):
        hopf_project_s7_point(point)


def test_q8_fiber_witness_rejects_unknown_action() -> None:
    embedding = build_discrete_s7_embedding(_state())
    with pytest.raises(DiscreteHopfProjectionError, match="Q8_ELEMENT_UNSUPPORTED"):
        witness_q8_hopf_fiber(embedding, "+l")
