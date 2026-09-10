from __future__ import annotations

import pytest

from hhs_runtime.pass219.bott8_native_correspondence import PASS188_B8_ORDER
from hhs_runtime.pass219.classical_bott_correspondence import (
    KO_COEFFICIENT_GROUPS,
    STABLE_O_HOMOTOPY_GROUPS,
    ClassicalBottCorrespondenceError,
    audit_rml5_generators_on_classical_bott_bridge,
    build_classical_bott_grade_reference,
    build_classical_bott_native_correspondence,
)
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    build_gyroscope_state,
    expected_product_phase,
)


def _state(
    *,
    x: int = 71,
    y: int = 0,
    z: int = 35,
    w: int = 71,
    xy_sign: int = 1,
    zw_sign: int = 1,
    state_id: str = "rml9:test",
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


def test_classical_real_bott_reference_tables_are_exact_and_period8() -> None:
    assert KO_COEFFICIENT_GROUPS == ("Z", "Z2", "Z2", "0", "Z", "0", "0", "0")
    assert STABLE_O_HOMOTOPY_GROUPS == ("Z2", "Z2", "0", "Z", "0", "0", "0", "Z")
    for grade in range(-64, 65):
        witness = build_classical_bott_grade_reference(grade)
        residue = grade % 8
        assert witness["residue_mod8"] == residue
        assert witness["shifted_residue_mod8"] == residue
        assert witness["native_b8_ordered_tag"] == PASS188_B8_ORDER[residue]
        assert witness["shifted_native_b8_ordered_tag"] == PASS188_B8_ORDER[residue]
        assert witness["ko_coefficient_group"] == KO_COEFFICIENT_GROUPS[residue]
        assert witness["stable_o_homotopy_group"] == STABLE_O_HOMOTOPY_GROUPS[residue]
        assert witness["ko_period8_reference_preserved"] is True
        assert witness["stable_o_period8_reference_preserved"] is True
        assert witness["stable_o_matches_ko_successor_reference"] is True
        assert witness["native_b8_tag_period8_preserved"] is True
        assert witness["phase_channel_is_ko_element"] is False
        assert witness["phase72_is_homotopy_group_coordinate"] is False
        assert witness["classical_bott_theorem_reproved_by_runtime"] is False


def test_rml9_packet_binds_all_eight_live_native_grades_to_classical_reference() -> None:
    state = _state()
    packet = build_classical_bott_native_correspondence(state)
    assert packet["b8_order"] == list(PASS188_B8_ORDER)
    assert packet["ko_coefficient_groups_mod8"] == list(KO_COEFFICIENT_GROUPS)
    assert packet["stable_o_homotopy_groups_mod8"] == list(STABLE_O_HOMOTOPY_GROUPS)
    assert packet["all_eight_grade_references_bound"] is True
    assert packet["all_ko_period8_references_preserved"] is True
    assert packet["all_stable_o_period8_references_preserved"] is True
    assert packet["all_stable_o_match_ko_successor_reference"] is True
    assert packet["direct_period8_residue_bridge_verified"] is True
    assert len(packet["rml6_s7_point_sha256"]) == 64
    assert len(packet["rml7_s4_point_sha256"]) == 64

    rows = packet["basis_rows"]
    assert [row["ordered_tag"] for row in rows] == list(PASS188_B8_ORDER)
    for q, row in enumerate(rows):
        assert row["basis8"] == q
        assert row["phase72"] == state["phases"][row["ordered_tag"]]
        ref = row["classical_period8_reference"]
        assert ref["residue_mod8"] == q
        assert ref["native_b8_ordered_tag"] == row["ordered_tag"]
        assert row["classical_annotation_replaces_live_phase_state"] is False


def test_rml9_preserves_authority_and_does_not_scalarize_topology() -> None:
    packet = build_classical_bott_native_correspondence(_state())
    assert packet["classical_reference_is_typed_annotation_not_scalar_substitution"] is True
    assert packet["classical_bott_theorem_reproved_by_hhs"] is False
    assert packet["full_s3_fiber_closure_claimed"] is False
    assert packet["physical_topological_hardware_theorem_claimed"] is False
    assert packet["canonical_vm81_mutation_authority"] is False
    assert packet["canonical_hash72_mint_authority"] is False
    assert packet["canonical_hash216_persistence_authority"] is False
    assert packet["floating_point_authority"] is False
    assert packet["scalar_projection_substitution_authority"] is False


def test_complete_rml5_generator_partition_carries_through_classical_bott_bridge() -> None:
    audit = audit_rml5_generators_on_classical_bott_bridge(_state())
    assert audit["total_generator_cases"] == 290
    assert audit["same_base_fiber_preserving_cases"] == 4
    assert audit["base_moving_cases"] == 286
    assert audit["inverse_hopf_base_restoration_failures"] == 0
    assert audit["bott8_order_structurally_invariant_across_generator_targets"] is True
    assert audit["classical_grade_annotation_preserved_across_generator_targets"] is True
    assert audit["ko_period8_reference_bound_to_all_eight_native_grades"] is True
    assert audit["stable_o_period8_reference_bound_to_all_eight_native_grades"] is True
    assert audit["generator_motion_reclassified_by_ko_group"] is False
    assert audit["phase_transition_authority_expanded"] is False
    assert audit["classical_bott_theorem_reproved_by_hhs"] is False
    assert audit["canonical_vm81_mutation_authority"] is False


def test_rml9_rejects_float_grade_authority() -> None:
    with pytest.raises(ClassicalBottCorrespondenceError, match="CLASSICAL_BOTT_GRADE_EXACT_INTEGER_REQUIRED"):
        build_classical_bott_grade_reference(1.0)  # type: ignore[arg-type]
