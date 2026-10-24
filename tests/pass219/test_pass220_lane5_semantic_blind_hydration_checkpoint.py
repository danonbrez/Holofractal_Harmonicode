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


def test_observed_integer_cost_selection_is_candidate_only_and_order_independent() -> None:
    with Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(backend="CPU_REFERENCE") as optimizer:
        exact = optimizer.native_state_hash216(_state(3))
        other = optimizer.native_state_hash216(_state(7))
        search = optimizer.search_hash216(
            query_hash216=exact,
            candidates=[
                Hash216CompositionCandidate("dna", exact, True),
                Hash216CompositionCandidate("music", other, True),
            ],
            tick=11, cycle_index=4, top_k=2,
        )
        records = [
            {"candidate_id": "dna", "elapsed_ns": 900, "receipt_hash216": exact},
            {"candidate_id": "music", "elapsed_ns": 120, "receipt_hash216": other},
        ]
        first = optimizer.select_by_observed_cost(search_result=search, observations=records)
        second = optimizer.select_by_observed_cost(search_result=search, observations=list(reversed(records)))
        assert first == second
        assert [item["candidate_id"] for item in first["ranked_by_exact_elapsed_ns"]] == [
            "music", "dna"
        ]
        assert first["candidate_only"] is True
        assert first["observation_receipts_verified"] is False
        assert first["canonical_vm81_mutation_authority"] is False
        assert all(item["requires_exact_cpu_vm81_replay"] for item in first["ranked_by_exact_elapsed_ns"])


def test_observed_cost_rejects_unverified_shapes_and_never_invents_costs() -> None:
    with Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(backend="CPU_REFERENCE") as optimizer:
        exact = optimizer.native_state_hash216(_state(3))
        other = optimizer.native_state_hash216(_state(7))
        search = optimizer.search_hash216(
            query_hash216=exact,
            candidates=[
                Hash216CompositionCandidate("a", exact, True),
                Hash216CompositionCandidate("b", other, True),
            ],
            tick=0, cycle_index=0, top_k=2,
        )
        empty = optimizer.select_by_observed_cost(search_result=search, observations=[])
        assert empty["measured_candidates"] == 0
        assert empty["unmeasured_candidates"] == 2
        assert empty["ranked_by_exact_elapsed_ns"] == []
        for elapsed in (1.0, True, -1):
            with pytest.raises(ValueError, match="elapsed_ns"):
                optimizer.select_by_observed_cost(
                    search_result=search,
                    observations=[{"candidate_id": "a", "elapsed_ns": elapsed, "receipt_hash216": exact}],
                )
        with pytest.raises(ValueError, match="does not match"):
            optimizer.select_by_observed_cost(
                search_result=search,
                observations=[{"candidate_id": "a", "elapsed_ns": 1, "receipt_hash216": other}],
            )
        with pytest.raises(ValueError, match="duplicate"):
            optimizer.select_by_observed_cost(
                search_result=search,
                observations=[
                    {"candidate_id": "a", "elapsed_ns": 1, "receipt_hash216": exact},
                    {"candidate_id": "a", "elapsed_ns": 2, "receipt_hash216": exact},
                ],
            )
