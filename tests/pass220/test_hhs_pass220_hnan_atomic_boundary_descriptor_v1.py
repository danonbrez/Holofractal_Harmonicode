"""Dependency-scoped tests for eight-sector candidate admission guard."""
from hhs_runtime.pass220.hhs_pass220_hnan_atomic_boundary_descriptor_v1 import (
    Boundary, HNAN_OUTER_ADDRESSES, HNAN_OUTER_TERMS, inspect_boundaries
)


def make_valid():
    return tuple(Boundary(a, term, f"equation-{i}", f"digest-{i}", f"witness-{i}")
                 for i, (a, term) in enumerate(zip(HNAN_OUTER_ADDRESSES, HNAN_OUTER_TERMS)))


def test_all_eight_distinct_candidates_do_not_mint_native_state():
    result = inspect_boundaries(make_valid())
    assert result.candidate and not result.reasons
    assert not result.native_admitted and not result.hydrogen_verified
    assert result.carrier_modulus == 72 and result.serialization_hz == 81


def test_missing_sector_fails_closed():
    assert not inspect_boundaries(make_valid()[:-1]).candidate


def test_ordered_term_swap_fails_closed():
    xs = list(make_valid())
    xs[0], xs[1] = xs[1], xs[0]
    assert "ordered_hnan_address_mismatch" in inspect_boundaries(tuple(xs)).reasons


def test_repeated_equation_fails_closed():
    xs = list(make_valid())
    xs[1] = Boundary(xs[1].address, xs[1].ordered_term,
                     xs[0].equation_id, xs[0].equation_digest, xs[1].witness_id)
    result = inspect_boundaries(tuple(xs))
    assert not result.candidate
    assert "duplicate_equation_identity" in result.reasons
