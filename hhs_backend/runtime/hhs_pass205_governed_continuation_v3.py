"""Pass 205 governed replay argument repair.

V3 preserves the V2 governed singleton and database schema. It replaces only
reconstructive replay so Hash216 storage-field names are explicitly translated
to the native bridge argument names.
"""
from __future__ import annotations

from typing import Any

from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
    CLOSURE_CLASSIFICATION,
    CONTRACT,
    _canonical_bytes,
    _learning_full,
)
from hhs_backend.runtime.hhs_pass205_governed_continuation_v2 import (
    GOVERNED_PASS205_CONTINUATION_RUNTIME,
    GovernedPass205ContinuationRuntime,
)


def _reconstructive_replay_v3(
    self: GovernedPass205ContinuationRuntime,
    continuation_root216: str,
) -> dict[str, Any]:
    chain: list[dict[str, Any]] = []
    cursor = self.snapshot(continuation_root216)
    while True:
        chain.append(cursor)
        if int(cursor["generation"]) == 0:
            break
        cursor = self.snapshot(str(cursor["parent_root216"]))
    chain.reverse()

    failures: list[dict[str, Any]] = []
    boundary = chain[0]
    reconstructed_state = list(boundary["state_words"])
    reconstructed_projection = self.native.project_full(reconstructed_state)
    reconstructed_learning = _learning_full(reconstructed_state, reconstructed_projection)
    if self.native.state_root(reconstructed_state) != boundary["content_root216"]:
        failures.append({"generation": 0, "reason": "GENESIS_CONTENT_RECONSTRUCTION_MISMATCH"})

    parent = boundary
    for stored in chain[1:]:
        generation = int(stored["generation"])
        generation_reasons: list[str] = []
        events = self._delta_events(str(stored["delta_root216"]))
        child_state, frontier_bits, _, _ = self.native.apply_delta(reconstructed_state, events)
        frontier = [index for index, enabled in enumerate(frontier_bits) if enabled]
        if frontier != list(stored["frontier_cells"]):
            generation_reasons.append("FRONTIER_RECONSTRUCTION_MISMATCH")
        sparse_projection = self.native.project_sparse(child_state, reconstructed_projection, frontier)
        full_projection = self.native.project_full(child_state)
        if sparse_projection != full_projection:
            generation_reasons.append("SPARSE_FULL_PROJECTION_MISMATCH")
        child_learning = _learning_full(child_state, full_projection)
        roots = {
            "content_root216": self.native.state_root(child_state),
            "delta_root216": self.native.delta_root(events),
            "hydration_root216": self.native.hydration_root(events),
            "dependency_root216": self.native.frontier_root(frontier),
            "projection_root216": self.native.projection_root(full_projection),
            "learning_root216": self.native.hash216_bytes(_canonical_bytes(child_learning)),
        }
        for key, value in roots.items():
            if value != stored[key]:
                generation_reasons.append(key.upper() + "_RECONSTRUCTION_MISMATCH")
        native_token = self.native.build_token(
            parent_root=parent["continuation_root216"],
            content_root=roots["content_root216"],
            delta_root=roots["delta_root216"],
            hydration_root=roots["hydration_root216"],
            dependency_root=roots["dependency_root216"],
            projection_root=roots["projection_root216"],
            learning_root=roots["learning_root216"],
            parent_receipt=parent["receipt_hash72"],
            generation=generation,
        )
        if native_token["continuation_root216"] != stored["continuation_root216"]:
            generation_reasons.append("CONTINUATION_ROOT_RECONSTRUCTION_MISMATCH")
        admission = self._admission(str(stored["continuation_root216"]))
        if admission is None:
            generation_reasons.append("VM81_ADMISSION_MISSING")
        else:
            if admission["vm81_receipt_hash72"] != stored["receipt_hash72"]:
                generation_reasons.append("VM81_RECEIPT_RECONSTRUCTION_MISMATCH")
            if native_token["receipt_hash72"] != admission["native_receipt_witness_hash72"]:
                generation_reasons.append("NATIVE_RECEIPT_WITNESS_RECONSTRUCTION_MISMATCH")
        if child_state != list(stored["state_words"]):
            generation_reasons.append("STATE_PAYLOAD_RECONSTRUCTION_MISMATCH")
        if full_projection != stored["projection_channels"]:
            generation_reasons.append("PROJECTION_PAYLOAD_RECONSTRUCTION_MISMATCH")
        if child_learning != stored["learning_features"]:
            generation_reasons.append("LEARNING_PAYLOAD_RECONSTRUCTION_MISMATCH")
        if generation_reasons:
            failures.append(
                {
                    "generation": generation,
                    "continuation_root216": stored["continuation_root216"],
                    "reasons": generation_reasons,
                }
            )
        reconstructed_state = child_state
        reconstructed_projection = full_projection
        reconstructed_learning = child_learning
        parent = stored

    return {
        "schema": "HHS_PASS_205_RECONSTRUCTIVE_REPLAY_V3",
        "contract": CONTRACT,
        "classification": CLOSURE_CLASSIFICATION if not failures else "HHS_PASS_205_REPLAY_REJECTED",
        "ok": not failures,
        "target_root216": continuation_root216,
        "generation_count": len(chain),
        "ordered_roots216": [snapshot["continuation_root216"] for snapshot in chain],
        "ordered_receipts_hash72": [snapshot["receipt_hash72"] for snapshot in chain],
        "reconstructed_from_ordered_deltas": True,
        "native_argument_mapping_explicit": True,
        "reconstructed_target_state_words": reconstructed_state,
        "reconstructed_target_learning_features": reconstructed_learning,
        "failures": failures,
    }


GovernedPass205ContinuationRuntime.replay = _reconstructive_replay_v3
GOVERNED_PASS205_CONTINUATION_RUNTIME.replay = _reconstructive_replay_v3.__get__(
    GOVERNED_PASS205_CONTINUATION_RUNTIME,
    GovernedPass205ContinuationRuntime,
)


__all__ = [
    "GOVERNED_PASS205_CONTINUATION_RUNTIME",
    "GovernedPass205ContinuationRuntime",
]
