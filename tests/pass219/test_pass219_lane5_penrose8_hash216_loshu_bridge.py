from __future__ import annotations

from fractions import Fraction
from hashlib import sha256

import pytest

from hhs_runtime.core.hash72_validator_v1 import HASH72_ALPHABET
from hhs_runtime.pass219.lane5_penrose8_hash216_loshu_bridge import (
    LO_SHU_OUTER_EXPRESSIONS,
    PENROSE8_REAL_PHASE_ORDER,
    PYTHAGOREAN_LINEAGE_CLOSURE,
    TRUTH3_ADDRESSES,
    Penrose8Hash216BridgeError,
    full_penrose8_hash216_bridge_receipt,
    gaussian_det2,
    hash216_lineage_witness,
    hash72_coordinate_chart,
    incidence_twistor,
    massless_momentum_spinor,
    minkowski_hermitian_matrix,
    penrose8_projection_witness,
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


def test_three_bit_addresses_bind_to_native_outer_tensor_and_penrose8_order() -> None:
    assert TRUTH3_ADDRESSES == (
        "000", "001", "010", "011", "100", "101", "110", "111"
    )
    assert LO_SHU_OUTER_EXPRESSIONS == (
        "xy", "x+y", "yx", "xy-zw", "wz-yx", "wz", "z+w", "zw"
    )
    assert len(PENROSE8_REAL_PHASE_ORDER) == 8


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


def test_full_bridge_closes_without_runtime_or_hash_mint_authority() -> None:
    result = full_penrose8_hash216_bridge_receipt(*_triplet())
    assert result["status"] == "PASS"
    assert all(result["checks"].values())
    assert result["bindings"]["global"] == (
        "9 nuclei * 8 outer coordinates = 72 = u^72 = Hash72 geometry"
    )
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
