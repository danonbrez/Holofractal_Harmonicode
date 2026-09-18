"""Pass 220 I003 bridge: I002 holographic query ranking over inherited Lane 5 search.

The bridge is candidate-only. It composes two read-only ranking views over the
same validated Hash216 candidate identities and never widens VM81/Hash72/
Hash216 admission or commit authority.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import (
    Hash216CompositionCandidate,
    Pass219Lane5Hash216GPUPhaseInterlaceOptimizer,
)
from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    rank_and_sample_candidates,
    split_hash216,
)

SCHEMA = "HHS_PASS_220_I003_HOLOGRAPHIC_LANE5_QUERY_BRIDGE_V1"
PHASE_SLOTS = {"xy": (0, 36), "yx": (36, 0), "zw": (18, 54), "wz": (54, 18)}


class Pass220I003BridgeError(ValueError):
    pass


def _candidate_ids(items: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    ids = []
    for item in items:
        candidate_id = item.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            raise Pass220I003BridgeError("candidate_id must be a nonempty string")
        ids.append(candidate_id)
    if len(set(ids)) != len(ids):
        raise Pass220I003BridgeError("candidate IDs must be unique")
    return tuple(ids)


def _validate_phase(phase: str) -> tuple[int, int]:
    try:
        return PHASE_SLOTS[phase]
    except KeyError as exc:
        raise Pass220I003BridgeError("unknown reciprocal phase") from exc


class Pass220HolographicLane5QueryBridge:
    """Compose I002 metadata ranking with inherited Lane 5 Hash216 ranking."""

    def __init__(
        self,
        *,
        baseline: Pass219Lane5Hash216GPUPhaseInterlaceOptimizer | None = None,
        backend: str = "CPU_REFERENCE",
        require_physical_gpu: bool = False,
    ) -> None:
        self._owns_baseline = baseline is None
        self.baseline = baseline or Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(
            backend=backend,
            require_physical_gpu=require_physical_gpu,
        )

    def close(self) -> None:
        if self._owns_baseline:
            self.baseline.close()

    def __enter__(self) -> "Pass220HolographicLane5QueryBridge":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def search(
        self,
        *,
        phase: str,
        query: Mapping[str, Any],
        candidates: Sequence[Mapping[str, Any]],
        tick: int,
        cycle_index: int,
        sample_ordinal: int = 0,
        top_k: int = 32,
    ) -> dict[str, Any]:
        phase_slot, inverse_phase_slot = _validate_phase(phase)
        query_hash216 = str(query.get("hash216", ""))
        split_hash216(query_hash216)
        ids = _candidate_ids(candidates)

        lane5_candidates = []
        for candidate_id, candidate in zip(ids, candidates):
            candidate_hash216 = str(candidate.get("hash216", ""))
            split_hash216(candidate_hash216)
            lane5_candidates.append(
                Hash216CompositionCandidate(
                    candidate_id=candidate_id,
                    hash216=candidate_hash216,
                    validated=True,
                    jump_span=int(candidate.get("jump_span", 1)),
                    lineage_signature=str(candidate.get("lineage_signature", candidate_hash216)),
                )
            )

        baseline = self.baseline.search_hash216(
            query_hash216=query_hash216,
            candidates=lane5_candidates,
            tick=int(tick),
            cycle_index=int(cycle_index),
            top_k=top_k,
        )
        holographic = rank_and_sample_candidates(
            query,
            candidates,
            sample_ordinal=sample_ordinal,
        )

        baseline_ids = tuple(item["candidate_id"] for item in baseline["ranked"])
        holographic_ids = tuple(item["candidate_id"] for item in holographic["ranked"][: max(0, int(top_k))])
        return {
            "schema": SCHEMA,
            "phase": phase,
            "phase_slot": phase_slot,
            "inverse_phase_slot": inverse_phase_slot,
            "query_hash216": query_hash216,
            "candidate_count": len(candidates),
            "baseline": baseline,
            "holographic": holographic,
            "baseline_ranked_ids": baseline_ids,
            "holographic_ranked_ids": holographic_ids,
            "same_candidate_identity_set": set(ids) == {item.candidate_id for item in lane5_candidates},
            "probability_allocates_search_effort_only": True,
            "candidate_only": True,
            "hash72_commit_authority": False,
            "hash216_commit_authority": False,
            "canonical_vm81_mutation_authority": False,
            "requires_exact_cpu_vm81_replay": True,
        }


__all__ = [
    "PHASE_SLOTS",
    "Pass220HolographicLane5QueryBridge",
    "Pass220I003BridgeError",
]
