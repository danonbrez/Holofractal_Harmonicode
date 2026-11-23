from __future__ import annotations

import pytest

from hhs_runtime.pass220.hnan_perimeter_topology_v1 import (
    ADDRESS_MATRIX, LO_SHU_MATRIX, PERIMETER,
    perimeter_orbit, perimeter_step, topology_receipt,
)


def test_perimeter_cycle_is_eight_unique_addresses_and_center_is_not_routed():
    assert len(set(PERIMETER)) == 8
    assert "HNAN" not in PERIMETER
    assert ADDRESS_MATRIX[1][1] == "HNAN"
    for address in PERIMETER:
        orbit = perimeter_orbit(address, 8)
        assert orbit[0] == orbit[-1] == address
        assert len(set(orbit[:-1])) == 8
        assert all(orbit[k] != address for k in range(1, 8))


def test_neighbor_degree_two_and_row_major_loshu_mapping():
    assert LO_SHU_MATRIX == ((4, 9, 2), (3, 5, 7), (8, 1, 6))
    assert perimeter_step("011") == "000"
    assert perimeter_step("010") == "100"
    edges = tuple((address, perimeter_step(address)) for address in PERIMETER)
    assert all(sum(a == v or b == v for a, b in edges) == 2 for v in PERIMETER)


@pytest.mark.parametrize("address", ["HNAN", "999", "", 4, True])
def test_center_and_foreign_addresses_are_rejected(address):
    with pytest.raises(ValueError):
        perimeter_step(address)


@pytest.mark.parametrize("steps", [-1, 1.0, True, "8"])
def test_non_exact_or_negative_steps_are_rejected(steps):
    with pytest.raises(ValueError):
        perimeter_orbit("000", steps)


def test_topology_receipt_preserves_noncanonical_authority_boundary():
    receipt = topology_receipt()
    assert receipt["status"] == "PASS", receipt["checks"]
    assert all(receipt["checks"].values())
    assert receipt["projection_period"] == 8
    assert receipt["phase_period_verified"] is False
    assert receipt["vm81_state_period_verified"] is False
    assert receipt["native_admission_verified"] is False
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["hash72_mint_authority"] is False
    assert receipt["hash216_persistence_authority"] is False
    assert len(receipt["receipt_sha256"]) == 64
