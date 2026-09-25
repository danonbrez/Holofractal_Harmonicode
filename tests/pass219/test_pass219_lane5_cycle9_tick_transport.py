from __future__ import annotations

from fractions import Fraction

import pytest

from hhs_runtime.pass219.lane5_cycle9_tick_transport import (
    BASE_P0,
    Cycle9TransportError,
    admitted_coordinate,
    canonical_coordinate_from_P,
    prove_72_block_transport,
    tick_coordinate,
    transport_state,
    untick_coordinate,
)


def test_base_tick_and_inverse_close_exactly() -> None:
    base = canonical_coordinate_from_P(BASE_P0)
    assert admitted_coordinate(base)
    ticked = tick_coordinate(base)
    assert admitted_coordinate(ticked)
    assert untick_coordinate(ticked) == base


def test_72_blocks_are_72_transitions_with_73_endpoints() -> None:
    receipt = prove_72_block_transport()
    assert receipt["status"] == "PASS"
    assert receipt["source_block_count"] == 72
    assert receipt["forward_transition_count"] == 72
    assert receipt["endpoint_state_count"] == 73
    assert all(receipt["checks"].values())
    assert receipt["final_endpoint"] == {
        "P": {"numerator": 74133185666641251, "denominator": 10**15},
        "p": {"numerator": 73133185666641251, "denominator": 10**15},
        "q": {"numerator": 75133185666641251, "denominator": 10**15},
    }


def test_qe_kernel_delta_and_provenance_are_carried_opaque() -> None:
    state = {
        **canonical_coordinate_from_P(BASE_P0),
        "Qe": 7,
        "Q_e": {"selected": 7, "receipt": "exact"},
        "K_delta": {"tuple": ["x", "v", "Qe"], "exact": True},
        "D_delta": {"denominator": "typed-nonzero"},
        "ordered_provenance": ["genesis", "tick-0"],
        "address_history": [0, 1, 2],
        "constraint_history": ["ideal", "bridge"],
        "hash72_block": {"opaque": "h72"},
        "hash216_lineage": ["previous72", "next72", "receipt72"],
    }
    out = transport_state(state)
    for key in (
        "Qe",
        "Q_e",
        "K_delta",
        "D_delta",
        "ordered_provenance",
        "address_history",
        "constraint_history",
        "hash72_block",
        "hash216_lineage",
    ):
        assert out[key] == state[key]
    checks = out["_cycle9_transport"]["checks"]
    assert checks["qe_carried_if_present"] is True
    assert checks["kernel_delta_material_carried_if_present"] is True
    assert checks["opaque_state_digest_preserved"] is True


def test_transport_does_not_promote_open_bridge_or_runtime_authority() -> None:
    receipt = prove_72_block_transport(carried_state={"Q_e": 1})
    assert receipt["cross_projection_sigma_delta_bridge_closed"] is False
    assert receipt["cross_projection_substitution_authorized"] is False
    assert receipt["t_bridge_01b_workload_interval_certificate_closed"] is False
    assert receipt["qe_semantic_resolution_inferred"] is False
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_mint_authority"] is False
    assert receipt["canonical_hash216_mint_authority"] is False
    assert receipt["canonical_persistence_authority"] is False
    assert receipt["floating_point_authority"] is False


def test_nonadmitted_and_inexact_sources_fail_closed() -> None:
    bad = {"P": BASE_P0, "p": BASE_P0, "q": BASE_P0 + 1}
    assert admitted_coordinate(bad) is False
    with pytest.raises(Cycle9TransportError, match="not admitted"):
        tick_coordinate(bad)
    with pytest.raises(Cycle9TransportError, match="exact int/Fraction"):
        canonical_coordinate_from_P(2.5)


def test_theorem_is_parametric_not_only_the_p0_fixture() -> None:
    receipt = prove_72_block_transport(base_P=Fraction(5, 2))
    assert receipt["status"] == "PASS"
    assert receipt["base_P0"] == {"numerator": 5, "denominator": 2}
    assert receipt["final_endpoint"] == {
        "P": {"numerator": 149, "denominator": 2},
        "p": {"numerator": 147, "denominator": 2},
        "q": {"numerator": 151, "denominator": 2},
    }
