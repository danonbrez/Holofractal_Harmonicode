from __future__ import annotations

import copy

import pytest

from hhs_runtime.pass219.harmonic_geometry_circuit_i182 import (
    HarmonicGeometryConstraintError,
    PLATONIC_PAIRS,
    Q_H,
    build_geometry_constraint_receipt,
    derive_dodecahedral_closure,
    derive_platonic_closure,
    factor_witness,
    hydration_factorization_witnesses,
    pentagonal_quantization_witness,
    validate_platonic_candidate,
    verify_geometry_constraint_receipt,
)


def _assert_no_float(value):
    if isinstance(value, dict):
        for item in value.values():
            _assert_no_float(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _assert_no_float(item)
    else:
        assert not isinstance(value, float)


def test_5184_hydration_factorization_is_exact():
    witnesses = hydration_factorization_witnesses()
    pairs = {(item.left, item.right) for item in witnesses}
    assert pairs == {(72, 72), (64, 81), (36, 144), (48, 108)}
    assert {item.product for item in witnesses} == {Q_H}


def test_pentagonal_quantization_closes_exactly():
    witness = pentagonal_quantization_witness()
    assert witness["hydration_quantum"] == 5184
    assert witness["half_sector"] == 36
    assert witness["external"] == 72
    assert witness["interior"] == 108
    assert witness["supplementary"] == 144
    assert witness["sides"] * witness["external"] == 360
    assert witness["zero_phase_closure"] == 0
    _assert_no_float(witness)


def test_all_five_platonic_incidence_branches_derive_by_constraints():
    observed = {}
    for pair in sorted(PLATONIC_PAIRS):
        closure = derive_platonic_closure(*pair)
        closure.verify()
        observed[pair] = (closure.vertices, closure.edges, closure.faces)

    assert observed == {
        (3, 3): (4, 6, 4),
        (3, 4): (6, 12, 8),
        (3, 5): (12, 30, 20),
        (4, 3): (8, 12, 6),
        (5, 3): (20, 30, 12),
    }


def test_dodecahedron_is_derived_from_5_3_closure_without_vertex_table_authority():
    closure = derive_dodecahedral_closure()
    assert (closure.p, closure.q) == (5, 3)
    assert (closure.vertices, closure.edges, closure.faces) == (20, 30, 12)
    assert closure.p * closure.faces == 2 * closure.edges
    assert closure.q * closure.vertices == 2 * closure.edges
    assert closure.vertices - closure.edges + closure.faces == 2


def test_malformed_factorization_fails_closed():
    with pytest.raises(HarmonicGeometryConstraintError, match="5184_FACTOR_WITNESS_INVALID"):
        factor_witness(36, 143)


def test_noninteger_canonical_input_fails_closed():
    with pytest.raises(HarmonicGeometryConstraintError, match="NONINTEGER_CANONICAL_INPUT"):
        derive_platonic_closure(5.0, 3)  # type: ignore[arg-type]


def test_non_platonic_pair_fails_closed():
    with pytest.raises(HarmonicGeometryConstraintError, match="PLATONIC_PAIR_NOT_ADMISSIBLE"):
        derive_platonic_closure(5, 4)


def test_tampered_dodecahedral_incidence_fails_closed():
    with pytest.raises(HarmonicGeometryConstraintError):
        validate_platonic_candidate(p=5, q=3, vertices=20, edges=31, faces=12)


def test_receipt_is_deterministic_exact_and_non_authority_minting():
    first = build_geometry_constraint_receipt()
    second = build_geometry_constraint_receipt()
    assert first == second
    assert first["witness_sha256"] == second["witness_sha256"]
    assert first["vm81_authority_minted"] is False
    assert first["hash72_authority_minted"] is False
    assert first["hash216_persistence_authority"] is False
    assert first["authoritative_vertex_table_used"] is False
    assert verify_geometry_constraint_receipt(first) is True
    _assert_no_float(first)


def test_tampered_receipt_fails_closed():
    receipt = build_geometry_constraint_receipt()
    tampered = copy.deepcopy(receipt)
    tampered["dodecahedron"]["edges"] = 31
    with pytest.raises(HarmonicGeometryConstraintError, match="RECEIPT_MISMATCH"):
        verify_geometry_constraint_receipt(tampered)
