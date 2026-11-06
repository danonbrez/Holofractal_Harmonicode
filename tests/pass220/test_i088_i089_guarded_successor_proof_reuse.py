"""Dependency-scoped I088/I089 exact successor and closed admission boundary."""
from copy import deepcopy
import pytest

from hhs_runtime.hhs_pass220_i088_i089_guarded_successor_proof_reuse_v1 import (
    I088UnprovenClosure, prepare_successor_constraint_witness,
    require_globally_admitted_reuse,
)


def _candidate():
    return prepare_successor_constraint_witness(
        P=4, inherited_proof_sha256="a" * 64,
        required_constraints=("P^2=pq+Delta", "AB=P^4", "BA=-P^4"),
    )


def test_successor_projection_preserves_exact_inherited_core_and_order():
    witness = _candidate()
    assert (witness["p"], witness["P"], witness["q"]) == (3, 4, 5)
    assert witness["inherited_exact_core"]["delta"] == 1
    assert witness["ordered_required_constraints"] == (
        "P^2=pq+Delta", "AB=P^4", "BA=-P^4")
    assert witness == _candidate()
    assert witness["fold_executed"] is False
    assert witness["vm81_admitted"] is False
    assert witness["persistent_reuse_authorized"] is False


@pytest.mark.parametrize("P", (False, 0, 2, 3, 5, 1.0))
def test_unsupported_successor_domain_fails_closed(P):
    with pytest.raises(I088UnprovenClosure):
        prepare_successor_constraint_witness(
            P=P, inherited_proof_sha256="a" * 64,
            required_constraints=("global-constraint",))


def test_disagreement_and_forged_admission_fail_closed():
    witness = _candidate()
    with pytest.raises(I088UnprovenClosure, match="trusted native"):
        require_globally_admitted_reuse(witness)
    for field, value in (("all_global_constraints_proven", True),
                         ("vm81_admitted", True),
                         ("ordered_required_constraints", ("AB=P^4",))):
        forged = deepcopy(witness)
        forged[field] = value
        with pytest.raises(I088UnprovenClosure, match="drift"):
            require_globally_admitted_reuse(forged)
    with pytest.raises(I088UnprovenClosure):
        prepare_successor_constraint_witness(
            P=4, inherited_proof_sha256="a" * 64,
            required_constraints=("AB=P^4", "AB=P^4"))
