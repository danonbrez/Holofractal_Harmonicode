"""Pass 220 dependency-scoped tests for modality-independent Lane 5 hydration plans."""
from __future__ import annotations

import pytest

from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import (
    Hash216CompositionCandidate,
    Pass219Lane5Hash216GPUPhaseInterlaceOptimizer,
)


def _state(seed: int) -> list[int]:
    mask = (1 << 64) - 1
    return [((seed + 1) * 0x9E3779B97F4A7C15 + c) & mask for c in range(81)]


def test_exact_hydration_and_nonexact_composition_require_vm81_replay() -> None:
    with Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(backend="CPU_REFERENCE") as optimizer:
        exact = optimizer.native_state_hash216(_state(3))
        other = optimizer.native_state_hash216(_state(7))
        assert exact != other
        first = optimizer.search_hash216(
            query_hash216=exact,
            candidates=[
                Hash216CompositionCandidate("dna", other, True),
                Hash216CompositionCandidate("music", exact, True),
            ],
            tick=11, cycle_index=4, top_k=2,
        )
        second = optimizer.search_hash216(
            query_hash216=exact,
            candidates=[
                Hash216CompositionCandidate("music", other, True),
                Hash216CompositionCandidate("dna", exact, True),
            ],
            tick=11, cycle_index=4, top_k=2,
        )
        for result in (first, second):
            assert [p["strategy"] for p in result["hydration_plan"]] == [
                "HYDRATE_EXACT", "VERIFY_COMPOSITION"
            ]
            assert [p["candidate_hash216"] for p in result["hydration_plan"]] == [exact, other]
            assert all(p["requires_exact_cpu_vm81_replay"] for p in result["hydration_plan"])
            assert result["candidate_only"] is True
            assert result["canonical_vm81_mutation_authority"] is False


def test_unvalidated_candidate_fails_before_hydration() -> None:
    with Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(backend="CPU_REFERENCE") as optimizer:
        exact = optimizer.native_state_hash216(_state(3))
        with pytest.raises(ValueError, match="unvalidated"):
            optimizer.search_hash216(
                query_hash216=exact,
                candidates=[Hash216CompositionCandidate("unverified", exact, False)],
                tick=0, cycle_index=0,
            )


def test_empty_candidate_search_has_stable_hydration_plan() -> None:
    with Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(backend="CPU_REFERENCE") as optimizer:
        exact = optimizer.native_state_hash216(_state(3))
        response = optimizer.search_hash216(
            query_hash216=exact, candidates=[], tick=0, cycle_index=0,
        )
        assert response["candidate_count"] == 0
        assert response["ranked"] == []
        assert response["hydration_plan"] == []
        assert response["candidate_only"] is True
