import pytest

from hhs_runtime.hhs_pass220_h36_hash72_unit_bridge_v1 import (
    H36,
    Pass220H36Hash72BridgeError,
    VERBATIM_UNIT_RATIO,
    h36_hash72_unit_bridge_self_test,
    h36_hash72_unit_ratio_witness,
)


def test_verbatim_h36_hash72_ratio_is_retained():
    assert VERBATIM_UNIT_RATIO == (
        "(e/H36=(mc^2)/u^144)="
        "(a^2/P^4)*(c^2(a^2+b^2))="
        "(xy+zw)/(q-p)"
    )


def test_exact_unit_ratio_closes_all_four_views():
    witness = h36_hash72_unit_ratio_witness()
    assert witness["all_ratios_exact_unit"] is True
    assert witness["ratios"] == {
        "e_over_H36": "1",
        "mc2_over_u144": "1",
        "a2_over_P4_times_c2_times_a2_plus_b2": "1",
        "xy_plus_zw_over_q_minus_p": "1",
    }


def test_h36_hash72_u144_numeric_projection_locks_at_36():
    witness = h36_hash72_unit_ratio_witness()
    assert H36 == 36
    assert witness["H36"] == 36
    assert witness["HASH72_projection"] == 36
    assert witness["u144_projection"] == 36
    assert witness["H36_equals_HASH72_projection"] is True
    assert witness["u144_equals_HASH72_projection"] is True


def test_energy_and_mc2_are_projection_locks_not_symbol_rebindings():
    witness = h36_hash72_unit_ratio_witness()
    assert witness["energy_e_projection"] == 36
    assert witness["mc2_projection"] == 36
    assert witness["energy_e_equals_H36_projection"] is True
    assert witness["mc2_equals_u144_projection"] is True
    assert witness["native_m_symbol_solved"] is False
    assert witness["typed_mc2_compound_preserved"] is True
    assert witness["typed_e_symbol_not_rebound_to_basis_e"] is True


def test_middle_and_ordered_ratios_close_exactly_to_one():
    witness = h36_hash72_unit_ratio_witness()
    assert witness["P4"] == 9
    assert witness["P4_not_one"] is True
    assert witness["middle_ratio_numerator"] == 9
    assert witness["middle_ratio_denominator"] == 9
    assert witness["xy_plus_zw"] == 2
    assert witness["q_minus_p"] == 2


def test_canonical_universal_constraint_dependency_is_bound():
    witness = h36_hash72_unit_ratio_witness()
    assert witness["canonical_universal_constraint_fragments_present"] is True
    assert len(witness["canonical_universal_constraint_sha256"]) == 64


@pytest.mark.parametrize(
    "kwargs",
    (
        {"a2": 2},
        {"b2": 3},
        {"c2": 4},
        {"p4": 1},
        {"p4": 8},
        {"p2_minus_pq": 2},
        {"xy": 2},
        {"zw": -1},
        {"q_minus_p": 3},
        {"energy_e_projection": 35},
        {"mc2_projection": 35},
        {"a2": 1.0},
        {"b2": True},
    ),
)
def test_ratio_bridge_drift_fails_closed(kwargs):
    with pytest.raises(Pass220H36Hash72BridgeError):
        h36_hash72_unit_ratio_witness(**kwargs)


def test_self_test_closes_without_authority_escalation():
    result = h36_hash72_unit_bridge_self_test()
    assert result["ok"] is True
    assert all(result["checks"].values())
    assert result["floating_point_authority"] is False
    assert result["canonical_hash72_authority"] is False
    assert result["canonical_hash216_authority"] is False
    assert result["canonical_vm81_mutation_authority"] is False
