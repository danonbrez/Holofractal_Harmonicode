from __future__ import annotations

import pytest

from hhs_runtime.pass219.dynamic_octonion_gyroscope import build_gyroscope_state
from hhs_runtime.pass219.relativistic_thermo_gyroscope_null_fold import (
    BRANCH_LABELS,
    RelativisticGyroscopeError,
    build_null_fold_transition,
    build_relativistic_projection,
    build_thermodynamic_reciprocal_projection,
)


def _state():
    return build_gyroscope_state(
        {
            "x": 0,
            "y": 0,
            "z": 0,
            "w": 0,
            "xy": 18,
            "yx": 54,
            "zw": 18,
            "wz": 54,
        },
        {"xy": 1, "yx": -1, "zw": 1, "wz": -1},
        state_id="relativistic-null-fold-fixture",
    )


def test_exact_relativistic_complement_exposes_all_three_branches_without_square_root():
    state = _state()
    positive = build_relativistic_projection(
        state,
        projection_id="velocity:positive",
        projection_kind="VELOCITY_TIME_DILATION",
        kappa_numerator=1,
        kappa_denominator=4,
    )
    null = build_relativistic_projection(
        state,
        projection_id="velocity:null",
        projection_kind="VELOCITY_TIME_DILATION",
        kappa_numerator=1,
        kappa_denominator=1,
    )
    negative = build_relativistic_projection(
        state,
        projection_id="velocity:negative",
        projection_kind="VELOCITY_TIME_DILATION",
        kappa_numerator=5,
        kappa_denominator=4,
    )

    assert positive["rho_squared"] == {"numerator": 3, "denominator": 4}
    assert positive["branch"] == 1
    assert null["rho_squared"] == {"numerator": 0, "denominator": 1}
    assert null["branch"] == 0
    assert negative["rho_squared"] == {"numerator": -1, "denominator": 4}
    assert negative["branch"] == -1
    assert [positive["branch_label"], null["branch_label"], negative["branch_label"]] == [
        BRANCH_LABELS[1],
        BRANCH_LABELS[0],
        BRANCH_LABELS[-1],
    ]
    assert not positive["square_root_evaluated"]
    assert not null["typed_projection_zero_is_state_zero"]
    assert not negative["floating_point_canonical_authority"]


def test_velocity_and_gravity_are_typed_ingress_to_same_exact_constructor():
    state = _state()
    velocity = build_relativistic_projection(
        state,
        projection_id="velocity",
        projection_kind="VELOCITY_TIME_DILATION",
        kappa_numerator=1,
        kappa_denominator=9,
    )
    gravity = build_relativistic_projection(
        state,
        projection_id="gravity",
        projection_kind="GRAVITATIONAL_TIME_DILATION",
        kappa_numerator=1,
        kappa_denominator=9,
    )

    assert velocity["common_constructor"] == gravity["common_constructor"] == "rho^2=1-kappa"
    assert velocity["rho_squared"] == gravity["rho_squared"] == {"numerator": 8, "denominator": 9}
    assert velocity["source_expression"] == "1-v^2/c^2"
    assert gravity["source_expression"] == "1-2GM/(rc^2)"
    assert velocity["gyroscope"]["phases"] == gravity["gyroscope"]["phases"]
    assert velocity["gyroscope"]["channel_order"] == ["x", "y", "z", "w", "xy", "yx", "zw", "wz"]


def test_null_fold_uses_existing_u36_pair_flip_and_preserves_complete_ordered_payload_reversibly():
    witness = build_null_fold_transition(
        _state(),
        transition_id="velocity:null-fold:0",
        projection_kind="VELOCITY_TIME_DILATION",
        before_kappa_numerator=3,
        before_kappa_denominator=4,
        after_kappa_numerator=5,
        after_kappa_denominator=4,
        pair_index=0,
    )

    assert witness["branch_sequence"] == [1, 0, -1]
    assert witness["null_fold_operator"] == "u^36"
    assert witness["phase_transport"]["phase_inversion_u"] == "u^36"
    assert witness["phase_transport"]["pair"] == ["xy", "yx"]
    assert witness["phase_transport"]["pair_opposition_preserved"]
    assert witness["phase_transport"]["product_geometry_preserved"]
    assert witness["reciprocal_phase_transport_self_inverse"]
    assert witness["original_phase_payload_exactly_restored_by_inverse"]
    assert witness["zero_sum_fold_is_projection_not_state_annihilation"]
    assert witness["ordered_noncommutative_products_preserved"]
    assert not witness["information_discarded_by_fold"]


def test_gravitational_null_fold_can_use_orthogonal_reciprocal_pair():
    witness = build_null_fold_transition(
        _state(),
        transition_id="gravity:null-fold:1",
        projection_kind="GRAVITATIONAL_TIME_DILATION",
        before_kappa_numerator=7,
        before_kappa_denominator=8,
        after_kappa_numerator=9,
        after_kappa_denominator=8,
        pair_index=1,
    )
    assert witness["phase_transport"]["pair"] == ["zw", "wz"]
    assert witness["before_projection"]["source_expression"] == "1-2GM/(rc^2)"
    assert witness["fold_projection"]["branch"] == 0
    assert witness["after_projection"]["branch"] == -1


def test_thermodynamic_reciprocal_projection_is_exact_symmetric_and_zero_at_fixed_point():
    state = _state()
    forward = build_thermodynamic_reciprocal_projection(
        state,
        projection_id="thermo:3/2",
        G_numerator=3,
        G_denominator=2,
    )
    reciprocal = build_thermodynamic_reciprocal_projection(
        state,
        projection_id="thermo:2/3",
        G_numerator=2,
        G_denominator=3,
    )
    fixed = build_thermodynamic_reciprocal_projection(
        state,
        projection_id="thermo:1",
        G_numerator=1,
        G_denominator=1,
    )

    assert forward["reciprocal_closure"] == {"numerator": 1, "denominator": 6}
    assert reciprocal["reciprocal_closure"] == forward["reciprocal_closure"]
    assert forward["theta"] == {"numerator": 1, "denominator": 2}
    assert reciprocal["theta"] == {"numerator": -1, "denominator": 3}
    assert forward["reciprocal_log_terms_cancel_symbolically"]
    assert not forward["logarithms_evaluated"]
    assert fixed["fixed_point_G_equals_one"]
    assert fixed["reciprocal_closure_zero"]
    assert fixed["reciprocal_closure"] == {"numerator": 0, "denominator": 1}


def test_projection_fails_closed_on_float_tamper_invalid_domains_and_wrong_branch_order():
    state = _state()
    with pytest.raises(RelativisticGyroscopeError, match="EXACT_INTEGER_REQUIRED"):
        build_relativistic_projection(
            state,
            projection_id="float",
            projection_kind="VELOCITY_TIME_DILATION",
            kappa_numerator=1.0,
            kappa_denominator=2,
        )
    with pytest.raises(RelativisticGyroscopeError, match="DENOMINATOR_ZERO"):
        build_relativistic_projection(
            state,
            projection_id="zero-den",
            projection_kind="GRAVITATIONAL_TIME_DILATION",
            kappa_numerator=1,
            kappa_denominator=0,
        )
    with pytest.raises(RelativisticGyroscopeError, match="POSITIVE_REQUIRED"):
        build_thermodynamic_reciprocal_projection(
            state,
            projection_id="bad-g",
            G_numerator=0,
            G_denominator=1,
        )
    with pytest.raises(RelativisticGyroscopeError, match="POSITIVE_BEFORE_BRANCH"):
        build_null_fold_transition(
            state,
            transition_id="bad-before",
            projection_kind="VELOCITY_TIME_DILATION",
            before_kappa_numerator=5,
            before_kappa_denominator=4,
            after_kappa_numerator=6,
            after_kappa_denominator=5,
            pair_index=0,
        )

    tampered = dict(state)
    tampered["phases"] = dict(state["phases"])
    tampered["phases"]["x"] = 1
    with pytest.raises(RelativisticGyroscopeError, match="SHA256_MISMATCH"):
        build_relativistic_projection(
            tampered,
            projection_id="tampered",
            projection_kind="GENERIC_RELATIVISTIC_COMPLEMENT",
            kappa_numerator=1,
            kappa_denominator=2,
        )
