"""
HHS Attention Operator v1
=========================

Receipt-oriented attention kernel over Lo Shu phase embedding states.

Standard attention scores anonymous float vectors.  This operator scores fully
qualified HHS states:

    score(Q,K) = phase + geometry + dna + hash + invariant gate

No floating point math is required in the core path.  All score components are
integer/rational witnesses and every attention edge emits a Hash72 receipt.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

from hhs_runtime.hhs_loshu_phase_embedding_v1 import (
    FORBIDDEN_ADJACENCIES,
    LO_SHU_SIDE,
    TORUS_ORDER,
    EmbeddingReceipt,
    PhaseEmbeddingState,
    embed_sequence,
    hash72_digest,
)


@dataclass(frozen=True)
class AttentionWeights:
    """Integer weights for exact attention scoring."""

    phase: int = 5
    geometry: int = 3
    dna: int = 4
    hash72: int = 2
    invariant: int = 8


@dataclass(frozen=True)
class AttentionScore:
    """Exact component score for one query/key edge."""

    query_hash72: str
    key_hash72: str
    query_token: str
    key_token: str
    query_position: int
    key_position: int
    query_dimension: int
    key_dimension: int
    phase_score: Fraction
    geometry_score: Fraction
    dna_score: Fraction
    hash72_score: Fraction
    invariant_score: Fraction
    weighted_score: Fraction
    allowed: bool
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        for key, value in list(data.items()):
            if isinstance(value, Fraction):
                data[key] = f"{value.numerator}/{value.denominator}"
        return data


@dataclass(frozen=True)
class AttentionReceipt:
    """Receipt for a full HHS attention pass."""

    module: str
    embedding_receipt_hash72: str
    weights: AttentionWeights
    scores: List[AttentionScore]
    best_edges: List[AttentionScore]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "module": self.module,
            "embedding_receipt_hash72": self.embedding_receipt_hash72,
            "weights": asdict(self.weights),
            "scores": [score.to_dict() for score in self.scores],
            "best_edges": [score.to_dict() for score in self.best_edges],
            "receipt_hash72": self.receipt_hash72,
        }


def _all_invariants_ok(state: PhaseEmbeddingState) -> bool:
    return all(state.invariants.values())


def phase_similarity(query: PhaseEmbeddingState, key: PhaseEmbeddingState) -> Fraction:
    """
    Closed u^72 phase similarity.

    Identical phase = 1. Opposite half-turn = 0. Intermediate distance decays
    linearly on the cyclic ring.  This is a rational shadow of phase alignment,
    not a float dot product.
    """

    delta = abs(query.phase_index - key.phase_index) % TORUS_ORDER
    cyclic_distance = min(delta, TORUS_ORDER - delta)
    return Fraction(TORUS_ORDER // 2 - cyclic_distance, TORUS_ORDER // 2)


def loshu_geometry_similarity(query: PhaseEmbeddingState, key: PhaseEmbeddingState) -> Fraction:
    """
    9x9 Lo Shu address proximity score using Chebyshev neighborhood distance.

    Same cell = 1. Immediate 3x3 neighborhood = high score. Distance 8 = 0.
    """

    dr = abs(query.lo_shu.row - key.lo_shu.row)
    dc = abs(query.lo_shu.col - key.lo_shu.col)
    distance = max(dr, dc)
    return Fraction(LO_SHU_SIDE - 1 - distance, LO_SHU_SIDE - 1)


def dna_compatibility(query: PhaseEmbeddingState, key: PhaseEmbeddingState) -> Fraction:
    """
    Ordered xyzw compatibility score.

    Rewards exact symbol matches and reverse-complement matches. Fails closed if
    the edge boundary creates a forbidden adjacency such as xz or yw.
    """

    q = query.xyzw_dna
    k = key.xyzw_dna
    if (q[-1], k[0]) in FORBIDDEN_ADJACENCIES:
        return Fraction(0, 1)

    exact = sum(1 for a, b in zip(q, k) if a == b)
    reverse = sum(1 for a, b in zip(q, reversed(k)) if a == b)
    return Fraction(exact + reverse, 2 * min(len(q), len(k)))


def hash72_similarity(query: PhaseEmbeddingState, key: PhaseEmbeddingState) -> Fraction:
    """Prefix/symbol agreement over Hash72 receipts."""

    length = min(len(query.hash72), len(key.hash72))
    if length == 0:
        return Fraction(0, 1)
    matches = sum(1 for a, b in zip(query.hash72[:length], key.hash72[:length]) if a == b)
    return Fraction(matches, length)


def invariant_gate_score(query: PhaseEmbeddingState, key: PhaseEmbeddingState) -> Fraction:
    """Fail-closed invariant score."""

    return Fraction(1, 1) if _all_invariants_ok(query) and _all_invariants_ok(key) else Fraction(0, 1)


def score_edge(
    query: PhaseEmbeddingState,
    key: PhaseEmbeddingState,
    weights: AttentionWeights | None = None,
) -> AttentionScore:
    """Score one query/key edge and emit an edge receipt."""

    weights = weights or AttentionWeights()
    p = phase_similarity(query, key)
    g = loshu_geometry_similarity(query, key)
    d = dna_compatibility(query, key)
    h = hash72_similarity(query, key)
    inv = invariant_gate_score(query, key)

    numerator = (
        weights.phase * p
        + weights.geometry * g
        + weights.dna * d
        + weights.hash72 * h
        + weights.invariant * inv
    )
    denominator = weights.phase + weights.geometry + weights.dna + weights.hash72 + weights.invariant
    weighted = numerator / denominator
    allowed = bool(inv) and bool(d)
    if not allowed:
        weighted = Fraction(0, 1)

    receipt = hash72_digest(
        (
            "hhs_attention_edge_v1",
            query.receipt_hash72,
            key.receipt_hash72,
            p,
            g,
            d,
            h,
            inv,
            weighted,
            allowed,
        )
    )
    return AttentionScore(
        query_hash72=query.hash72,
        key_hash72=key.hash72,
        query_token=query.token,
        key_token=key.token,
        query_position=query.position,
        key_position=key.position,
        query_dimension=query.dimension,
        key_dimension=key.dimension,
        phase_score=p,
        geometry_score=g,
        dna_score=d,
        hash72_score=h,
        invariant_score=inv,
        weighted_score=weighted,
        allowed=allowed,
        receipt_hash72=receipt,
    )


def attention_pass(
    embedding: EmbeddingReceipt,
    weights: AttentionWeights | None = None,
    top_k: int = 1,
    include_self_edges: bool = False,
) -> AttentionReceipt:
    """Run HHS attention over every state in an embedding receipt."""

    weights = weights or AttentionWeights()
    if top_k <= 0:
        raise ValueError("top_k must be positive")

    scores: List[AttentionScore] = []
    best_edges: List[AttentionScore] = []
    states = embedding.states

    for query in states:
        query_scores: List[AttentionScore] = []
        for key in states:
            if not include_self_edges and query.receipt_hash72 == key.receipt_hash72:
                continue
            edge = score_edge(query, key, weights)
            scores.append(edge)
            query_scores.append(edge)
        query_scores.sort(key=lambda edge: (edge.weighted_score, edge.receipt_hash72), reverse=True)
        best_edges.extend(query_scores[:top_k])

    receipt = hash72_digest(
        (
            "hhs_attention_operator_v1",
            embedding.receipt_hash72,
            asdict(weights),
            [edge.receipt_hash72 for edge in best_edges],
            len(scores),
        )
    )
    return AttentionReceipt(
        module="hhs_attention_operator_v1",
        embedding_receipt_hash72=embedding.receipt_hash72,
        weights=weights,
        scores=scores,
        best_edges=best_edges,
        receipt_hash72=receipt,
    )


def attend_tokens(
    tokens: Sequence[str],
    d_model: int = 72,
    dimensions: int = 4,
    top_k: int = 1,
) -> AttentionReceipt:
    """Convenience entry point: tokens -> embedding -> HHS attention receipt."""

    embedding = embed_sequence(tokens, d_model=d_model, dimensions=dimensions)
    return attention_pass(embedding, top_k=top_k)


def demo() -> Dict[str, object]:
    receipt = attend_tokens(["HHS", "Hash72", "LoShu", "xyzw"], d_model=72, dimensions=3, top_k=2)
    return receipt.to_dict()


if __name__ == "__main__":
    import json

    print(json.dumps(demo(), indent=2, sort_keys=True))
