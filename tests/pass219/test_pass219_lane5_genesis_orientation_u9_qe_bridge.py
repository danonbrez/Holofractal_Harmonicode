from __future__ import annotations

import pytest

from hhs_runtime.pass219.lane5_genesis_orientation_u9_qe_bridge import (
    CENTERED_LO_SHU,
    EIGENVECTOR0_TENSOR,
    MAGNITUDE_TABLE,
    ORIENTATION_TABLE,
    Lane5GenesisBridgeError,
    genesis_projection_witness,
    qe_admissible_class,
    qe_constraint_receipt,
    self_test,
    u9_tensor_orbit,
)


def test_genesis_orientation_and_vm81_construction_close_exactly() -> None:
    witness = genesis_projection_witness()
    assert witness["status"] == "PASS"
    assert all(witness["checks"].values())

    assert witness["centered_loshu"] == [list(row) for row in CENTERED_LO_SHU]
    assert witness["native_eigenvector0"] == [
        list(row) for row in EIGENVECTOR0_TENSOR
    ]
    assert witness["orientation_table"] == [list(row) for row in ORIENTATION_TABLE]
    assert witness["magnitude_table"] == [list(row) for row in MAGNITUDE_TABLE]

    vm81 = witness["vm81_construction"]
    assert vm81 == {
        "phase_cover_positions": 72,
        "genesis_nucleus_cells": 9,
        "vm81_cells": 81,
        "rule": "72+9=81",
        "kronecker_scalar_construction_authority": False,
    }

    policy = witness["projection_policy"]
    assert policy["orientation_is_state_bearing"] is True
    assert policy["flat_scalar_substitution_authorized"] is False
    assert policy["scalar_projection_requires_admitted_pipeline"] is True


def test_u9_is_address_orbit_not_fourier_substitution() -> None:
    witness = genesis_projection_witness()
    u9 = witness["u9"]

    assert u9["full_orbit_closes"] is True
    assert u9["one_step_scalar_eigenclaim"] is False
    assert u9["conventional_fourier_mode_substitution_authorized"] is False

    orbit = u9_tensor_orbit()
    assert len(orbit) == 10
    assert len(set(orbit[:-1])) == 9
    assert orbit[0] == orbit[-1]
    assert orbit[1] != orbit[0]


def test_qe_is_constraint_selected_and_fails_closed_when_ambiguous() -> None:
    assert qe_admissible_class(2, 2, 0, range(1, 9)) == (1,)
    assert qe_admissible_class(2, 2, 2, range(1, 9)) == (2, 3, 4, 5, 6, 7, 8)

    unique = qe_constraint_receipt(2, 2, 0, range(1, 9))
    assert unique["decision"] == "COMMIT"
    assert unique["selected_qe"] == 1
    assert unique["qe_is_free_parameter"] is False

    ambiguous = qe_constraint_receipt(2, 2, 2, range(1, 9))
    assert ambiguous["decision"] == "UNRESOLVED"
    assert ambiguous["selected_qe"] is None
    assert ambiguous["surrounding_tensor_constraints_required"] is True


def test_qe_rejects_invalid_candidate_domains() -> None:
    with pytest.raises(Lane5GenesisBridgeError, match="positive numerator"):
        qe_constraint_receipt(0, 2, 0, [1])
    with pytest.raises(Lane5GenesisBridgeError, match="nonempty"):
        qe_constraint_receipt(2, 2, 0, [])
    with pytest.raises(Lane5GenesisBridgeError, match="positive exact integers"):
        qe_constraint_receipt(2, 2, 0, [0, 1])


def test_cycle3_self_test() -> None:
    assert self_test()["status"] == "PASS"
