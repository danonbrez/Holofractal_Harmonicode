from __future__ import annotations

from fractions import Fraction
from hashlib import sha256

import pytest

from hhs_runtime.core.hash72_validator_v1 import HASH72_ALPHABET
from hhs_runtime.pass219.lane5_penrose8_hash216_loshu_bridge import (
    CENTER_ROLE,
    LO_SHU_CENTER_EXPRESSION,
    LO_SHU_CENTER_POSITION,
    LO_SHU_OUTER_EXPRESSIONS,
    PENROSE8_REAL_PHASE_ORDER,
    PYTHAGOREAN_LINEAGE_CLOSURE,
    TRUTH3_ADDRESSES,
    U72_SCALAR_PROJECTION_CLOSURE_ASSIGNMENT,
    U72_TYPED_GEOMETRY,
    Z_GAUGE_POLICY,
    Penrose8Hash216BridgeError,
    full_penrose8_hash216_bridge_receipt,
    gaussian_det2,
    hash216_lineage_witness,
    hash72_coordinate_chart,
    incidence_twistor,
    massless_momentum_spinor,
    minkowski_hermitian_matrix,
    penrose8_projection_witness,
    pi_gauge_descriptor,
    self_test,
    twistor_null_form,
    twistor_real8,
)


def _triplet() -> tuple[str, str, str]:
    previous = HASH72_ALPHABET
    next_state = HASH72_ALPHABET[1:] + HASH72_ALPHABET[:1]
    receipt = HASH72_ALPHABET[2:] + HASH72_ALPHABET[:2]
    return previous, next_state, receipt


def test_penrose_incidence_is_exact_null_and_massless() -> None:
    X = minkowski_hermitian_matrix(3, 1, 2, -1)
    Z = incidence_twistor(
        X,
        (Fraction(1), Fraction(2)),
        (Fraction(3), Fraction(-1)),
    )
    assert len(Z) == 4
    assert len(twistor_real8(Z)) == 8
    assert twistor_null_form(Z) == (Fraction(0), Fraction(0))
    momentum = massless_momentum_spinor(
        (Fraction(1), Fraction(2)),
        (Fraction(3), Fraction(-1)),
    )
    assert gaussian_det2(momentum) == (Fraction(0), Fraction(0))

    witness = penrose8_projection_witness()
    assert witness["status"] == "PASS"
    assert all(witness["checks"].values())
    assert witness["projective_quotient_applied"] is False
    assert witness["hhs_projection_contract_only"] is True
    assert witness["identity_class"]["incidence_null_form_zero"].startswith(
        "ALGEBRAIC_IDENTITY"
    )
    assert witness["identity_class"]["massless_momentum_det_zero"].startswith(
        "ALGEBRAIC_IDENTITY"
    )
    assert witness["center_role"] == CENTER_ROLE
    assert witness["center_position"] == list(LO_SHU_CENTER_POSITION)
    assert witness["center_expression"] == LO_SHU_CENTER_EXPRESSION
    assert witness["z_gauge"]["z_gauge"] == Z_GAUGE_POLICY
    assert witness["z_gauge"]["retained_cstar_gauge_freedom"] is True
    assert witness["z_gauge"][
        "absolute_z_magnitude_gate_requires_gauge_root_match"
    ] is True
    assert witness["z_gauge"]["cross_gauge_absolute_magnitude_authorized"] is False


def test_three_bit_addresses_bind_to_native_outer_tensor_and_penrose8_order() -> None:
    assert TRUTH3_ADDRESSES == (
        "000", "001", "010", "011", "100", "101", "110", "111"
    )
    assert LO_SHU_OUTER_EXPRESSIONS == (
        "xy", "x+y", "yx", "xy-zw", "wz-yx", "wz", "z+w", "zw"
    )
    assert len(PENROSE8_REAL_PHASE_ORDER) == 8
    assert LO_SHU_CENTER_POSITION == (1, 1)
    assert LO_SHU_CENTER_EXPRESSION == "x+y-z-w+xy+yx-zw-wz"


def test_hash72_chart_is_nine_nuclei_times_eight_canonical_coordinates() -> None:
    chart = hash72_coordinate_chart()
    assert len(chart) == 72
    assert [row["hash72_index"] for row in chart] == list(range(72))
    assert "".join(row["canonical_character"] for row in chart) == HASH72_ALPHABET

    for nucleus in range(9):
        block = chart[nucleus * 8 : nucleus * 8 + 8]
        assert tuple(row["truth3_address"] for row in block) == TRUTH3_ADDRESSES
        assert tuple(row["penrose8_real_phase_coordinate"] for row in block) == (
            PENROSE8_REAL_PHASE_ORDER
        )
        assert all(row["nucleus_index"] == nucleus for row in block)
        assert all(row["all_nine_nuclei_coupled"] is True for row in block)
        assert all(row["foreign_qudit_count"] == 80 for row in block)
        assert all(row["self_exclusion"] is True for row in block)


def test_hash216_is_ordered_three_hash72_with_216_sha256_coordinate_witnesses() -> None:
    previous, next_state, receipt = _triplet()
    witness = hash216_lineage_witness(previous, next_state, receipt)

    assert witness["status"] == "PASS"
    assert witness["hash216"] == previous + next_state + receipt
    assert len(witness["coordinates"]) == 216
    assert len(witness["sha256_vector"]) == 216

    assert witness["sha256_vector"][0] == sha256(previous[0].encode("ascii")).hexdigest()
    assert witness["sha256_vector"][72] == sha256(next_state[0].encode("ascii")).hexdigest()
    assert witness["sha256_vector"][144] == sha256(receipt[0].encode("ascii")).hexdigest()
    assert witness["pythagorean_lineage_closure"] == PYTHAGOREAN_LINEAGE_CLOSURE
    assert witness["ordered_equality_chain_scalar_rewrite_authorized"] is False


def test_exact_pi_representative_freezes_gauge_per_receipt() -> None:
    first = pi_gauge_descriptor(
        (Fraction(1), Fraction(2)),
        (Fraction(3), Fraction(-1)),
    )
    same = pi_gauge_descriptor(
        (Fraction(1), Fraction(2)),
        (Fraction(3), Fraction(-1)),
    )
    rescaled = pi_gauge_descriptor(
        (Fraction(2), Fraction(4)),
        (Fraction(6), Fraction(-2)),
    )
    assert first["gauge_root_sha256"] == same["gauge_root_sha256"]
    assert first["gauge_root_sha256"] != rescaled["gauge_root_sha256"]
    assert first["cross_gauge_absolute_magnitude_authorized"] is False


def test_full_bridge_closes_without_runtime_or_hash_mint_authority() -> None:
    result = full_penrose8_hash216_bridge_receipt(*_triplet())
    assert result["status"] == "PASS"
    assert all(result["checks"].values())
    assert result["bindings"]["global"] == (
        "9 nuclei * 8 outer coordinates = 72; "
        "U72 typed geometry = Hash72 = 72 Lo-Shu outer coordinates"
    )
    assert result["u72_typed_geometry"] == U72_TYPED_GEOMETRY
    assert result["u72_scalar_projection_closure_assignment"] == (
        U72_SCALAR_PROJECTION_CLOSURE_ASSIGNMENT
    )
    assert result["ordinary_ubar_power_rewrite_authorized"] is False
    assert result["center_role"] == CENTER_ROLE
    assert result["z_gauge_policy"] == Z_GAUGE_POLICY
    assert result["absolute_z_magnitude_gate_requires_gauge_root_match"] is True
    assert result["cross_gauge_absolute_magnitude_authorized"] is False
    assert result["bindings"]["transition"] == (
        "Hash216 = previous72 || next72 || receipt72"
    )
    assert result["bindings"]["digest"].startswith("216 * SHA256")
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_mint_authority"] is False
    assert result["canonical_hash216_mint_authority"] is False
    assert result["canonical_persistence_authority"] is False
    assert result["floating_point_canonical_authority"] is False


def test_float_and_nonhermitian_inputs_fail_closed() -> None:
    with pytest.raises(Penrose8Hash216BridgeError, match="exact"):
        minkowski_hermitian_matrix(1.0, 0, 0, 0)

    bad = (
        ((Fraction(1), Fraction(0)), (Fraction(1), Fraction(1))),
        ((Fraction(1), Fraction(1)), (Fraction(1), Fraction(0))),
    )
    with pytest.raises(Penrose8Hash216BridgeError, match="Hermitian"):
        incidence_twistor(
            bad,
            (Fraction(1), Fraction(0)),
            (Fraction(0), Fraction(0)),
        )


def test_cycle7_self_test() -> None:
    assert self_test()["status"] == "PASS"
