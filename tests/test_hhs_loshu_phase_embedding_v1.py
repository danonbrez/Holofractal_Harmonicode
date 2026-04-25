"""
Basic tests for HHS Lo Shu Phase Embedding.
"""

from hhs_runtime.hhs_loshu_phase_embedding_v1 import (
    PHASE_BASE,
    TORUS_ORDER,
    adjacency_identity_ok,
    embed_token,
    lo_shu_address,
    phase_index,
)


def test_adjacency_identity() -> None:
    assert adjacency_identity_ok()


def test_phase_index_range() -> None:
    n = phase_index(position=5, dimension=3, d_model=72)
    assert 0 <= n < TORUS_ORDER


def test_lo_shu_address_range() -> None:
    address = lo_shu_address(phase_n=10, dimension=2)
    assert 0 <= address.cell_index < 81
    assert 0 <= address.row < 9
    assert 0 <= address.col < 9


def test_embed_token_invariants() -> None:
    state = embed_token(token="test", position=1, dimension=1, d_model=72)
    for value in state.invariants.values():
        assert value


def test_hash72_length() -> None:
    state = embed_token(token="abc", position=0, dimension=0, d_model=72)
    assert len(state.hash72) > 0
    assert len(state.receipt_hash72) > 0
