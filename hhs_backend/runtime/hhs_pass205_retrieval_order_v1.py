"""Deterministic candidate ordering for Pass 205 vector retrieval."""
from __future__ import annotations

from typing import Any, Sequence

from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
    CLASSIFICATION,
    CONTRACT,
    ContinuationRejected,
    _canonical_bytes,
    _json,
    _learning_full,
    _now_ms,
    _parse_json,
    _popcount_distance,
    _validate_words,
)


def deterministic_retrieve(
    self,
    *,
    target_state_words: Sequence[int],
    schema_root216: str | None = None,
    constraint_root216: str | None = None,
    top_k: int = 32,
) -> dict[str, Any]:
    """Retrieve with canonical compatible and rejected candidate ordering."""
    target = _validate_words(target_state_words)
    schema_root = schema_root216 or self.schema_root216
    constraint_root = constraint_root216 or self.constraint_root216
    target_projection = self.native.project_full(target)
    target_features = _learning_full(target, target_projection)
    query_root = self.native.hash216_bytes(_canonical_bytes({
        "state": target,
        "schema_root216": schema_root,
        "constraint_root216": constraint_root,
    }))
    compatible: list[tuple[int, str, list[int]]] = []
    rejected: list[dict[str, str]] = []
    with self._connect() as connection:
        rows = connection.execute(
            """SELECT v.continuation_root216,v.schema_root216,v.constraint_root216,
                      v.features_json,s.state_json
               FROM vectors v JOIN snapshots s USING(continuation_root216)
               ORDER BY v.continuation_root216"""
        ).fetchall()
    for row in rows:
        root = str(row["continuation_root216"])
        reasons: list[str] = []
        if str(row["schema_root216"]) != schema_root:
            reasons.append("SCHEMA_ROOT_MISMATCH")
        if str(row["constraint_root216"]) != constraint_root:
            reasons.append("CONSTRAINT_ROOT_MISMATCH")
        if reasons:
            rejected.append({
                "continuation_root216": root,
                "reason": ",".join(sorted(reasons)),
            })
            continue
        features = [int(value) for value in _parse_json(str(row["features_json"]))]
        state = [int(value) for value in _parse_json(str(row["state_json"]))]
        compatible.append((_popcount_distance(features, target_features), root, state))
    if not compatible:
        raise ContinuationRejected("no continuation-compatible snapshot exists")

    compatible.sort(key=lambda item: (item[0], item[1]))
    rejected.sort(key=lambda item: (item["continuation_root216"], item["reason"]))
    shortlist_size = max(1, min(int(top_k), len(compatible)))
    shortlist = compatible[:shortlist_size]
    reranked = sorted(
        (
            _popcount_distance(state, target),
            vector_cost,
            root,
        )
        for vector_cost, root, state in shortlist
    )
    exact_cost, vector_cost, selected = reranked[0]
    ranked_payload = [
        {
            "continuation_root216": root,
            "vector_distance": int(vcost),
            "exact_delta_cost": int(ecost),
        }
        for ecost, vcost, root in reranked
    ]
    retrieval_identity = {
        "query_root216": query_root,
        "selected_parent_root216": selected,
        "ranked_candidates": ranked_payload,
        "rejected_candidates": rejected,
    }
    retrieval_root = self.native.hash216_bytes(_canonical_bytes(retrieval_identity))
    with self._transaction() as connection:
        connection.execute(
            "INSERT OR REPLACE INTO retrievals VALUES (?,?,?,?,?,?,?)",
            (
                retrieval_root, query_root, selected, _json(ranked_payload), _json(rejected),
                int(exact_cost), _now_ms(),
            ),
        )
    return {
        "schema": "HHS_PASS_205_COMPATIBLE_SNAPSHOT_RETRIEVAL_V2",
        "contract": CONTRACT,
        "classification": CLASSIFICATION,
        "ok": True,
        "retrieval_root216": retrieval_root,
        "query_root216": query_root,
        "selected_parent_root216": selected,
        "selected_parent_receipt_hash72": self.snapshot(selected, include_payloads=False)["receipt_hash72"],
        "vector_distance": int(vector_cost),
        "exact_delta_cost": int(exact_cost),
        "ranked_candidates": ranked_payload,
        "rejected_candidates": rejected,
        "approximate_similarity_is_authority": False,
        "exact_rerank_applied": True,
        "candidate_ordering": "CANONICAL_ROOT_REASON_ORDER",
    }


__all__ = ["deterministic_retrieve"]
