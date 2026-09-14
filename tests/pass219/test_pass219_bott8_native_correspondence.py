from __future__ import annotations

from hhs_runtime.pass219.bott8_native_correspondence import (
    H8_AXIS_ORDER,
    PASS188_B8_ORDER,
    PASS188_CHECKSUM_EXPECTED,
    PASS188_HYDRATED_STATES,
    PASS188_TRANSITION_TABLE,
    audit_pass188_native_hydration_parity,
    audit_rml5_generators_on_bott8_hopf_bridge,
    build_bott8_hopf_correspondence,
    build_period8_grade_witness,
    pass188_bott_step,
    pass188_transition_class,
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
    state_id: str = "rml8:test",
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


def test_pass188_order_and_transition_table_match_inherited_native_contract() -> None:
    assert PASS188_B8_ORDER == ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
    assert tuple(pass188_bott_step(q) for q in range(8)) == PASS188_TRANSITION_TABLE
    assert PASS188_TRANSITION_TABLE == (1, 0, 0, 0, 0, 0, 7, 6)
    assert pass188_transition_class(0) == "HHS_P188_PERIOD_TWO_ACTIVE"
    assert pass188_transition_class(1) == "HHS_P188_PERIOD_TWO_ACTIVE"
    assert pass188_transition_class(6) == "HHS_P188_PERIOD_TWO_ACTIVE"
    assert pass188_transition_class(7) == "HHS_P188_PERIOD_TWO_ACTIVE"
    for q in (2, 3, 4, 5):
        assert pass188_transition_class(q) == "HHS_P188_ASYMMETRIC_DRIFT_COLLAPSE"


def test_bott8_grade_is_exactly_periodic_mod8_without_promoting_classical_theorem() -> None:
    for grade in range(-32, 33):
        witness = build_period8_grade_witness(grade)
        assert witness["period8_identity_preserved"] is True
        assert witness["ordered_identity_preserved"] is True
        assert witness["residue_mod8"] == witness["shifted_residue_mod8"]
        assert witness["ordered_tag"] == witness["shifted_ordered_tag"]
        assert witness["classical_k_theory_bott_theorem_claimed"] is False


def test_rml8_packet_retains_all_eight_live_phases_h8_bits_and_hopf_base() -> None:
    state = _state()
    packet = build_bott8_hopf_correspondence(state)
    assert packet["b8_order"] == list(PASS188_B8_ORDER)
    assert packet["h8_axis_order"] == list(H8_AXIS_ORDER)
    assert packet["pass188_transition_table"] == list(PASS188_TRANSITION_TABLE)
    assert packet["pass188_transition_table_matches_inherited_contract"] is True
    assert packet["all_eight_live_phase_coordinates_retained"] is True
    assert packet["system_internal_bott8_correspondence_verified"] is True
    assert packet["rml7_exact_unit_s4_identity_verified"] is True
    assert len(packet["rml7_s4_point_sha256"]) == 64

    rows = packet["basis_rows"]
    assert [row["ordered_tag"] for row in rows] == list(PASS188_B8_ORDER)
    for row in rows:
        tag = row["ordered_tag"]
        assert row["phase72"] == state["phases"][tag]
        assert row["pass188_projection_output_basis8"] == pass188_bott_step(row["basis8"])
        assert tuple(row["h8_binary_coordinates"].keys()) == H8_AXIS_ORDER
        assert row["pass188_projection_is_full_phase_transition_authority"] is False

    assert rows[0]["h8_binary_coordinates"] == {
        H8_AXIS_ORDER[0]: 0,
        H8_AXIS_ORDER[1]: 0,
        H8_AXIS_ORDER[2]: 0,
    }
    assert rows[7]["h8_binary_coordinates"] == {
        H8_AXIS_ORDER[0]: 1,
        H8_AXIS_ORDER[1]: 1,
        H8_AXIS_ORDER[2]: 1,
    }


def test_full_pass188_hydration_recomputes_native_checksum_and_zero_drift() -> None:
    audit = audit_pass188_native_hydration_parity()
    assert audit["hydrated_states"] == PASS188_HYDRATED_STATES == 1_259_712
    assert audit["active_period_two_states"] == 629_856
    assert audit["asymmetric_collapse_states"] == 629_856
    assert audit["gear_preserved_states"] == PASS188_HYDRATED_STATES
    assert audit["coordinate_drift_states"] == 0
    assert audit["deterministic_checksum"] == PASS188_CHECKSUM_EXPECTED
    assert audit["deterministic_checksum_hex"] == "0x11e3bbf0214751c3"
    assert audit["checksum_matches_inherited_native_pass188"] is True
    assert audit["full_hydrated_address_count_matches"] is True
    assert audit["all_gears_preserved"] is True
    assert audit["zero_coordinate_drift"] is True
    assert audit["transition_table_matches"] is True


def test_rml7_generator_partition_is_bound_to_bott8_without_overwriting_phase_authority() -> None:
    audit = audit_rml5_generators_on_bott8_hopf_bridge(_state())
    assert audit["total_generator_cases"] == 290
    assert audit["same_base_fiber_preserving_cases"] == 4
    assert audit["base_moving_cases"] == 286
    assert audit["inverse_hopf_base_restoration_failures"] == 0
    assert audit["classification_partition_complete"] is True
    assert audit["all_explicit_inverses_restore_hopf_base"] is True
    assert audit["bott8_order_defined_for_every_balanced_rml5_state"] is True
    assert audit["generator_target_bott8_order_is_structurally_invariant"] is True
    assert audit["pass188_projection_is_not_generator_phase_authority"] is True
    assert audit["classical_k_theory_bott_periodicity_theorem_proven"] is False


def test_pass188_projection_does_not_replace_reversible_rml5_state() -> None:
    packet = build_bott8_hopf_correspondence(_state())
    assert packet["pass188_basis_projection_replaces_rml5_phase_state"] is False
    assert packet["rml5_reciprocal_phase_reversibility_overwritten"] is False
    assert packet["classical_k_theory_bott_periodicity_theorem_proven"] is False
    assert packet["physical_topological_hardware_claim"] is False
    assert packet["canonical_vm81_mutation_authority"] is False
    assert packet["canonical_hash72_mint_authority"] is False
    assert packet["canonical_hash216_persistence_authority"] is False
    assert packet["floating_point_authority"] is False
    assert packet["scalar_projection_substitution_authority"] is False
