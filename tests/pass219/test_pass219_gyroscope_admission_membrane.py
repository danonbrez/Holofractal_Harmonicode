from __future__ import annotations

import pytest

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    PRODUCTS,
    advance_gyroscope,
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.gyroscope_admission_membrane import (
    GENESIS_CLOSURE_Q,
    GENESIS_RESONATOR_Q,
    GyroscopeAdmissionError,
    build_chirality_polarity_witness,
    build_prime_boundary_projection,
    build_rml5_admission,
    certify_reciprocal_transition,
    construct_admissible_reciprocal_path,
    flip_chiral_pair_half_turn,
    genesis_exact_rational_witness,
    seal_rml5_proof_bundle,
)


def _signs() -> dict[str, int]:
    return {"xy": 1, "yx": -1, "zw": 1, "wz": -1}


def _phases(
    *,
    x: int = 0,
    y: int = 12,
    z: int = 24,
    w: int = 36,
    signs: dict[str, int] | None = None,
) -> dict[str, int]:
    actual_signs = _signs() if signs is None else signs
    primitives = {"x": x, "y": y, "z": z, "w": w}
    return {
        **primitives,
        "xy": expected_product_phase(x, actual_signs["xy"]),
        "yx": expected_product_phase(y, actual_signs["yx"]),
        "zw": expected_product_phase(z, actual_signs["zw"]),
        "wz": expected_product_phase(w, actual_signs["wz"]),
    }


def _state(
    *,
    state_id: str = "rml5:s0",
    signs: dict[str, int] | None = None,
    x: int = 0,
    y: int = 12,
    z: int = 24,
    w: int = 36,
) -> dict[str, object]:
    actual_signs = _signs() if signs is None else signs
    return build_gyroscope_state(
        _phases(x=x, y=y, z=z, w=w, signs=actual_signs),
        actual_signs,
        state_id=state_id,
    )


def _prime_hash() -> str:
    return "a" * 64


def test_genesis_exact_rational_constants_are_bound_without_float_authority() -> None:
    witness = genesis_exact_rational_witness()
    assert GENESIS_RESONATOR_Q == "179971179971/1000000"
    assert GENESIS_CLOSURE_Q == "1001/1000"
    assert witness["resonator_constant_q"] == GENESIS_RESONATOR_Q
    assert witness["closure_constant_q"] == GENESIS_CLOSURE_Q
    assert witness["resonator_numerator"] == 179971179971
    assert witness["resonator_denominator"] == 1000000
    assert witness["closure_numerator"] == 1001
    assert witness["closure_denominator"] == 1000
    assert witness["a_squared_q"] == "1"
    assert witness["floating_point_representation_authority"] is False


def test_chirality_projects_to_opposed_typed_plus_minus_a_squared_without_scalarizing() -> None:
    witness = build_chirality_polarity_witness(_state())
    assert witness["all_chiral_pairs_opposed"] is True
    pairs = {(row["forward_product"], row["reverse_product"]): row for row in witness["pairs"]}
    assert pairs[("xy", "yx")]["forward_polarity"] == "+a^2"
    assert pairs[("xy", "yx")]["reverse_polarity"] == "-a^2"
    assert pairs[("zw", "wz")]["forward_polarity"] == "+a^2"
    assert pairs[("zw", "wz")]["reverse_polarity"] == "-a^2"
    assert witness["polarity_projection_is_rotor_identity"] is False
    assert witness["scalar_projection_substitution_authority"] is False


def test_nonopposed_chiral_pair_is_visible_and_not_silently_normalized() -> None:
    signs = {"xy": 1, "yx": 1, "zw": 1, "wz": -1}
    state = _state(signs=signs)
    witness = build_chirality_polarity_witness(state)
    assert witness["all_chiral_pairs_opposed"] is False
    assert witness["pairs"][0]["opposite_chirality"] is False


def test_p_minus_one_p_plus_one_projection_is_exact_and_projection_only() -> None:
    projection = build_prime_boundary_projection(
        11,
        prime_witness_sha256=_prime_hash(),
        prime_witness_verified=True,
    )
    assert projection["p_lower_boundary"] == 10
    assert projection["q_upper_boundary"] == 12
    assert projection["p_plus_q"] == 22
    assert projection["two_P"] == 22
    assert projection["pq"] == 120
    assert projection["P_squared_minus_one"] == 120
    assert projection["P_squared"] == 121
    assert projection["projection_equalities_verified"] is True
    assert projection["projection_only"] is True
    assert projection["scalar_projection_substitution_authority"] is False


def test_prime_projection_requires_upstream_verified_prime_witness_and_odd_p() -> None:
    with pytest.raises(GyroscopeAdmissionError, match="PRIME_WITNESS_VERIFIED"):
        build_prime_boundary_projection(
            11,
            prime_witness_sha256=_prime_hash(),
            prime_witness_verified=False,
        )
    with pytest.raises(GyroscopeAdmissionError, match="ODD_P_GREATER_THAN_TWO"):
        build_prime_boundary_projection(
            12,
            prime_witness_sha256=_prime_hash(),
            prime_witness_verified=True,
        )


def test_reciprocal_transition_exactly_restores_phase_address_without_erasing_ancestry() -> None:
    state = _state()
    deltas = {
        "x": 7,
        "y": -5,
        "z": 11,
        "w": -13,
        "xy": 7,
        "yx": -5,
        "zw": 11,
        "wz": -13,
    }
    forward = advance_gyroscope(state, deltas, transition_id="forward")
    certificate = certify_reciprocal_transition(forward)
    assert certificate["ambient_state_index_restored"] is True
    assert certificate["phase_coordinates_restored"] is True
    assert certificate["forward_inverse_steps_cancel_exactly"] is True
    assert certificate["restored_product_geometry_admissible"] is True
    assert certificate["phase_transition_is_bijective"] is True
    assert certificate["information_discarded_by_phase_transform"] is False
    assert certificate["receipt_ancestry_is_rewound_or_erased"] is False
    assert certificate["physical_thermodynamic_entropy_claimed"] is False


def test_u36_pair_flip_preserves_opposed_chirality_and_is_self_inverse() -> None:
    source = _state()
    first = flip_chiral_pair_half_turn(source, pair_index=0, transition_id="flip-xy-yx")
    assert first["phase_inversion_steps"] == 36
    assert first["phase_inversion_u"] == "u^36"
    assert first["pair_opposition_preserved"] is True
    assert first["product_geometry_preserved"] is True
    assert first["next_state"]["quarter_turn_signs"]["xy"] == -1
    assert first["next_state"]["quarter_turn_signs"]["yx"] == 1

    second = flip_chiral_pair_half_turn(
        first["next_state"], pair_index=0, transition_id="flip-xy-yx-back"
    )
    assert second["next_state"]["phases"] == source["phases"]
    assert second["next_state"]["quarter_turn_signs"] == source["quarter_turn_signs"]
    assert second["next_state"]["ambient_state_index"] == source["ambient_state_index"]


def test_constructive_path_connects_different_chirality_sector_and_phase_coordinates() -> None:
    source = _state(state_id="source")
    target_signs = {"xy": -1, "yx": 1, "zw": -1, "wz": 1}
    target = _state(
        state_id="target",
        signs=target_signs,
        x=17,
        y=3,
        z=68,
        w=9,
    )
    path = construct_admissible_reciprocal_path(source, target, path_id="source-to-target")
    assert path["target_reached_exactly"] is True
    assert path["all_moves_reversible"] is True
    assert path["strong_connectivity_proven_for_rml5_balanced_chirality_manifold"] is True
    assert path["ambient_72_pow_8_exhaustively_enumerated"] is False
    assert any(move["kind"] == "CHIRAL_PAIR_U36_FLIP" for move in path["moves"])
    assert any(move["kind"] == "COUPLED_GENERATOR_PRODUCT_PHASE_MOVE" for move in path["moves"])


def test_path_rejects_candidate_that_is_product_admissible_but_chirality_unbalanced() -> None:
    source = _state()
    bad_signs = {"xy": 1, "yx": 1, "zw": 1, "wz": -1}
    target = _state(signs=bad_signs)
    with pytest.raises(GyroscopeAdmissionError, match="TARGET_CHIRALITY_NOT_ADMISSIBLE"):
        construct_admissible_reciprocal_path(source, target, path_id="reject-bad-target")


def test_rml5_state_admission_binds_genesis_chirality_prime_and_zero_closure_constraints() -> None:
    admission = build_rml5_admission(
        _state(),
        P=11,
        prime_witness_sha256=_prime_hash(),
        prime_witness_verified=True,
        omega_verified=True,
        delta_e_zero_verified=True,
        psi_zero_verified=True,
    )
    assert admission["state_admitted"] is True
    assert admission["omega_verified"] is True
    assert admission["delta_e_zero_constraint_verified"] is True
    assert admission["psi_zero_constraint_verified"] is True
    assert admission["genesis_exact_rational_witness"]["resonator_constant_q"] == GENESIS_RESONATOR_Q
    assert admission["chirality_polarity_witness"]["all_chiral_pairs_opposed"] is True
    assert admission["prime_boundary_projection"]["projection_equalities_verified"] is True
    assert admission["topology_proof_obligations"]["discrete_s7_embedding"] == "REPAIR_FORWARD_REQUIRED"


def test_rml5_admission_fails_closed_when_system_closure_witness_is_missing() -> None:
    with pytest.raises(GyroscopeAdmissionError, match="OMEGA_VERIFIED"):
        build_rml5_admission(
            _state(),
            P=11,
            prime_witness_sha256=_prime_hash(),
            prime_witness_verified=True,
            omega_verified=False,
            delta_e_zero_verified=True,
            psi_zero_verified=True,
        )


def test_proof_bundle_requires_bijective_transition_and_does_not_gain_hash_authority() -> None:
    state = _state()
    admission = build_rml5_admission(
        state,
        P=11,
        prime_witness_sha256=_prime_hash(),
        prime_witness_verified=True,
        omega_verified=True,
        delta_e_zero_verified=True,
        psi_zero_verified=True,
    )
    steps = {channel: 0 for channel in CHANNELS}
    steps["x"] = 5
    steps["xy"] = 5
    transition = advance_gyroscope(state, steps, transition_id="bundle-forward")
    inverse = certify_reciprocal_transition(transition)
    bundle = seal_rml5_proof_bundle(admission, inverse)
    assert bundle["genesis_identity_active"] is True
    assert bundle["ers_native_phase_transport"] is True
    assert bundle["omega"] is True
    assert bundle["phase_transition_bijective"] is True
    assert bundle["ready_for_existing_vm81_admission_authority"] is True
    assert bundle["canonical_vm81_mutation_authority"] is False
    assert bundle["canonical_hash72_mint_authority"] is False
    assert bundle["canonical_hash216_persistence_authority"] is False
    assert bundle["physical_zero_entropy_claimed"] is False


def test_rml5_preserves_all_eight_channel_identity_and_rejects_float_contamination() -> None:
    state = _state()
    assert tuple(state["phases"].keys()) == CHANNELS
    contaminated = dict(state)
    contaminated["phases"] = dict(state["phases"])
    contaminated["phases"]["x"] = 1.0
    with pytest.raises(GyroscopeAdmissionError, match="FLOAT_CANONICAL_AUTHORITY_FORBIDDEN"):
        build_chirality_polarity_witness(contaminated)
    assert set(PRODUCTS) == {"xy", "yx", "zw", "wz"}
