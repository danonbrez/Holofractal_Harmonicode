from __future__ import annotations

from fractions import Fraction

from hhs_runtime.pass219.lane5_feynman_discrete_orbit_bridge import (
    CONFIGURATION_PATH_WEIGHT,
    HHS_WEIGHT_POLICY,
    INGRESS_EGRESS_PHASE_BINDING,
    INGRESS_EGRESS_X_BINDING,
    MIXED_REPRESENTATION_WEIGHT,
    PARTITION_TRACE_SYMBOL,
    TWISTOR_SYMBOL,
    carried_action_descriptor,
    cycle8_receipt,
    explicit_old_state_euler_weight_admission,
    history_kernel_receipt,
    ingress_egress_zero_normalization_receipt,
    partition_trace,
    self_test,
    spectral_phase_receipt,
)


def test_u9_history_sum_collapses_exactly_on_reachable_pairs() -> None:
    for n in range(19):
        receipt = history_kernel_receipt(n)
        assert receipt["status"] == "PASS"
        assert receipt["nonzero_count"] == 9
        assert receipt["reachable_pair_history_count"] == 1
        assert receipt["unreachable_pair_history_count"] == 0
        assert len(receipt["source_to_endpoint"]) == 9


def test_partition_trace_has_exact_nine_cycle_and_no_Z_collision() -> None:
    assert tuple(partition_trace(n) for n in range(1, 10)) == (
        0, 0, 0, 0, 0, 0, 0, 0, 9
    )
    assert partition_trace(18) == 9
    assert PARTITION_TRACE_SYMBOL == "partition_trace"
    assert TWISTOR_SYMBOL == "Z"
    assert PARTITION_TRACE_SYMBOL != TWISTOR_SYMBOL


def test_carried_generator_owns_admitted_discrete_weight() -> None:
    descriptor = carried_action_descriptor()
    assert descriptor["status"] == "PASS"
    assert descriptor["canonical_f2_exists"] is True
    assert descriptor["admitted_hhs_feynman_weight"] is True
    assert descriptor["mixed_representation_weight"] == MIXED_REPRESENTATION_WEIGHT
    assert descriptor["configuration_path_weight"] == CONFIGURATION_PATH_WEIGHT
    assert descriptor["ordered_update"] == "KICK_THEN_DRIFT"


def test_simultaneous_old_state_euler_fails_closed_for_curved_potential() -> None:
    rejected = explicit_old_state_euler_weight_admission(
        h=Fraction(1, 4),
        mass=1,
        potential_curvature=2,
    )
    assert Fraction(*rejected["cross_derivative_mismatch"]) == Fraction(1, 8)
    assert rejected["status"] == "REJECTED_NO_TYPE2_GENERATOR"
    assert rejected["canonical_f2_exists"] is False
    assert rejected["admitted_hhs_feynman_weight"] is False
    assert rejected["weight_policy"] == HHS_WEIGHT_POLICY
    assert rejected["literal_external_zero_amplitude_claimed"] is False


def test_zero_cross_mismatch_is_only_a_necessary_condition() -> None:
    unresolved = explicit_old_state_euler_weight_admission(
        h=Fraction(1, 4),
        mass=1,
        potential_curvature=0,
    )
    assert unresolved["status"] == "NECESSARY_INTEGRABILITY_CONDITION_ONLY"
    assert unresolved["canonical_f2_exists"] is None
    assert unresolved["admitted_hhs_feynman_weight"] is None


def test_spectrum_binds_i025_native_u72_to_cycle5_scalar_face() -> None:
    mode0 = spectral_phase_receipt(0)
    mode4 = spectral_phase_receipt(4)
    assert mode0["native_energy"] == "0"
    assert mode0["scalar_projection_energy"] == "0"
    assert mode4["native_energy"] == "u72*(2*pi*4/9)/(tau*theta)"
    assert mode4["scalar_projection_energy"] == (
        "4*pi*4/(9*ubar^2*tau*theta)"
    )
    assert mode4["degeneracy"] == 8
    assert mode4["phase_constant_across_degenerate_outer_sector"] is True
    assert mode4["ordinary_ubar_power_rewrite_authorized"] is False


def test_existing_ingress_egress_codec_and_zero_bigint_are_reused() -> None:
    receipt = ingress_egress_zero_normalization_receipt()
    assert receipt["status"] == "PASS"
    assert receipt["source_literals"] == (
        INGRESS_EGRESS_X_BINDING,
        INGRESS_EGRESS_PHASE_BINDING,
    )
    assert receipt["source_strings_parsed_as_numbers"] is False
    assert receipt["canonical_zero_serialization_length"] == 5184
    assert receipt["scalar_bigint_zero"] == 0
    assert receipt["zero_normalization_shorthand"] == "(0000000)"
    assert receipt["zero_normalization_shorthand_is_canonical_serialization"] is False


def test_full_cycle8_receipt_preserves_gauge_and_authority_boundaries() -> None:
    receipt = cycle8_receipt(
        pi0=(Fraction(1), Fraction(2)),
        pi1=(Fraction(3), Fraction(-1)),
    )
    assert receipt["status"] == "PASS"
    assert all(receipt["checks"].values())
    assert receipt["partition_trace_n1_to_9"] == (0,0,0,0,0,0,0,0,9)
    assert receipt["z_gauge"][
        "absolute_z_magnitude_gate_requires_gauge_root_match"
    ] is True
    assert receipt["z_gauge"]["cross_gauge_absolute_magnitude_authorized"] is False
    assert receipt["continuum_path_integral_claimed"] is False
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_mint_authority"] is False
    assert receipt["canonical_hash216_mint_authority"] is False
    assert receipt["canonical_persistence_authority"] is False
    assert receipt["floating_point_canonical_authority"] is False


def test_cycle8_self_test() -> None:
    result = self_test()
    assert result["status"] == "PASS"
    assert result["fixture_is_canonical_genesis_spinor"] is False
