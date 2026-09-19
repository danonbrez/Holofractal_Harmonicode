from __future__ import annotations

from hashlib import sha256
from types import SimpleNamespace

import pytest

from hhs_python.runtime.hhs_pass219_lane5_direct_witness_routing_bridge import (
    Lane5DirectWitnessCandidate,
)
from hhs_python.runtime.hhs_pass219_lane5_unbounded_workload_scaling_bridge import (
    Lane5RouteCandidate,
    Lane5WorkloadEnvelope,
)
from hhs_runtime.pass219.lane5_mandatory_optimization_dispatcher import (
    Lane5MandatoryOptimizationError,
    MANDATORY_CAPABILITY_ROLES,
    MANDATORY_LANE5_LINEAGE,
    Pass219Lane5MandatoryOptimizationDispatcher,
)
import hhs_runtime.hhs_pass219_nonagentic_allegorical_warm_hydration_v1 as warm


class _Ranker:
    def __init__(self) -> None:
        self.calls = 0

    def status(self):
        return {"candidate_only": True}

    def search_hash216(self, **kwargs):
        self.calls += 1
        candidates = list(kwargs["candidates"])
        return {
            "schema": "TEST_RANKER",
            "candidate_only": True,
            "gpu_may_commit_hash72": False,
            "gpu_may_commit_hash216": False,
            "canonical_vm81_mutation_authority": False,
            "ranked": [
                {
                    "candidate_id": c.candidate_id,
                    "candidate_hash216": c.hash216,
                    "hash216_distance": 0,
                    "jump_span": c.jump_span,
                    "lineage_signature": c.lineage_signature,
                    "source_ordinal": i,
                    "phase_stream": 0,
                    "routed_slot": 0,
                }
                for i, c in enumerate(candidates)
            ],
        }

    def close(self):
        pass


class _Router:
    def __init__(self, *, found: bool) -> None:
        self.found = found
        self.plan_calls = 0
        self.execute_calls = 0

    def status(self):
        return {"candidate_only": True, "cross_level_exact_routing": True}

    def plan_route(self, **kwargs):
        self.plan_calls += 1
        return {
            "found": self.found,
            "exact_target": self.found,
            "goal_hash216": kwargs["goal_hash216"],
            "route_hash216": "route",
        }

    def execute_plan(self, **kwargs):
        self.execute_calls += 1
        return {
            "represented_transitions": 144,
            "intermediate_vm81_transitions_executed": 0,
            "terminal_hash216": kwargs["plan"]["goal_hash216"],
            "candidate_only": True,
        }

    def close(self):
        pass


def _dispatcher(*, found: bool | None = None):
    obj = object.__new__(Pass219Lane5MandatoryOptimizationDispatcher)
    obj.backend = "CPU_REFERENCE"
    obj.require_physical_gpu = False
    obj.state_root = None
    obj._ranker = _Ranker()
    obj._router = None if found is None else _Router(found=found)
    obj._direct_witness_bridge = None
    obj._unbounded_workload_bridge = None
    return obj


def _candidate(name: str = "c"):
    return SimpleNamespace(
        candidate_id=name,
        hash216="0" * 216,
        validated=True,
        jump_span=1,
        lineage_signature="lineage",
    )


def _direct_candidate(*, route_signature: int, span: int, phase: int):
    return Lane5DirectWitnessCandidate(
        previous_signature64=0x1001,
        current_signature64=0x2002,
        provenance_signature64=0x3003,
        goal_signature64=0x4004,
        forbidden_boundary_signature64=0x5005,
        reciprocal_inverse_signature64=0x6006,
        route_signature64=route_signature,
        represented_span=span,
        phase_slot=phase,
        trinary_collapse=0,
        binary_collapse=0,
        evidence_count=5,
        contradiction_check_count=2,
    )


def test_mandatory_lineage_contains_accumulated_proven_surfaces():
    required = {
        "LANE5_HASH216_GPU_PHASE_INTERLACE_1_37",
        "LANE5_HASH216_COMPOSITION_JUMP_STORE_1_38",
        "LANE5_PERSISTENT_HASH216_COMPOSITION_MEMORY_1_39",
        "LANE5_RECURSIVE_HASH216_COMPOSITION_GRAPH_1_40",
        "LANE5_SUPEREDGE_HIERARCHY_1_41",
        "LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42",
        "LANE5_EXECUTABLE_CAPABILITY_SELF_MODEL_1_43",
        "LANE5_REPOSITORY_CAPABILITY_REVERSE_DISCOVERY_1_44",
        "HASH216_FRACTAL_QUDIT_ADMISSION_1_45",
        "LANE5_DIRECT_WITNESS_ROUTING_1_46",
        "LANE5_UNBOUNDED_WORKLOAD_SCALING_1_48",
        "RML19_ROUTE_COMPOSITION_CERTIFICATE_REUSE",
    }
    assert required.issubset(set(MANDATORY_LANE5_LINEAGE))
    assert MANDATORY_CAPABILITY_ROLES["LANE5_DIRECT_WITNESS_ROUTING_1_46"] == (
        "DIRECT_WITNESS_ROUTE_OPTIMIZATION"
    )
    assert MANDATORY_CAPABILITY_ROLES["LANE5_UNBOUNDED_WORKLOAD_SCALING_1_48"] == (
        "STREAMING_WORKLOAD_ROUTE_REDUCTION"
    )
    assert MANDATORY_CAPABILITY_ROLES["HASH216_FRACTAL_QUDIT_ADMISSION_1_45"] == (
        "POST_SIGNED_ADMISSION_PROOF_HYDRATION"
    )


def test_stateless_search_is_compatible_but_reports_stateful_fast_paths():
    dispatcher = _dispatcher()
    result = dispatcher.search_hash216(
        query_hash216="0" * 216,
        candidates=[_candidate()],
        tick=0,
        cycle_index=0,
        top_k=1,
    )
    assert result["mandatory_optimization_dispatch"] is True
    assert result["optimization_selected"] == "LANE5_HASH216_GPU_PHASE_INTERLACE_1_37"
    assert "LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42" in result[
        "optimization_inapplicable_without_exact_parent_state"
    ]
    assert "LANE5_DIRECT_WITNESS_ROUTING_1_46" in result[
        "typed_optimizers_require_typed_inputs"
    ]
    assert "LANE5_UNBOUNDED_WORKLOAD_SCALING_1_48" in result[
        "typed_optimizers_require_typed_inputs"
    ]
    assert result["fresh_recomputation_forced"] is False
    assert dispatcher._ranker.calls == 1


def test_stateful_exact_route_preempts_fresh_ranking():
    dispatcher = _dispatcher(found=True)
    result = dispatcher.compose_or_reuse(
        current_state=[0] * 81,
        goal_hash216="0" * 216,
        tick=0,
        cycle_index=0,
        fallback_candidates=[_candidate()],
    )
    assert result["mode"] == "STATEFUL_EXACT_REUSE"
    assert result["optimization_selected"] == "LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42"
    assert result["represented_transitions"] == 144
    assert result["intermediate_vm81_transitions_executed"] == 0
    assert dispatcher._ranker.calls == 0
    assert dispatcher._router.plan_calls == 1
    assert dispatcher._router.execute_calls == 1


def test_stateful_miss_falls_back_only_after_reuse_search():
    dispatcher = _dispatcher(found=False)
    result = dispatcher.compose_or_reuse(
        current_state=[0] * 81,
        goal_hash216="0" * 216,
        tick=0,
        cycle_index=0,
        fallback_candidates=[_candidate()],
    )
    assert result["mode"] == "NO_EXACT_REUSABLE_ROUTE_FALLBACK_RANKING"
    assert result["exact_reuse_found"] is False
    assert dispatcher._router.plan_calls == 1
    assert dispatcher._ranker.calls == 1


def test_stateful_composition_without_state_root_fails_closed_not_silently_slow():
    dispatcher = _dispatcher(found=None)
    with pytest.raises(
        Lane5MandatoryOptimizationError,
        match="LANE5_STATEFUL_OPTIMIZATION_REQUIRES_STATE_ROOT",
    ):
        dispatcher.compose_or_reuse(
            current_state=[0] * 81,
            goal_hash216="0" * 216,
            tick=0,
            cycle_index=0,
        )


def test_native_direct_witness_optimizer_is_reachable_from_agent():
    dispatcher = _dispatcher()
    result = dispatcher.optimize_direct_witness_routes(
        [
            _direct_candidate(route_signature=0x9004, span=1_000_000, phase=0),
            _direct_candidate(route_signature=0x9001, span=9_000_000, phase=54),
        ]
    )
    assert result["mode"] == "DIRECT_WITNESS_OPTIMIZED"
    assert result["optimization_selected"] == "LANE5_DIRECT_WITNESS_ROUTING_1_46"
    receipt = result["receipt"]
    assert receipt["accepted"] is True
    assert receipt["optimizer_selected"] is True
    assert receipt["represented_span"] == 9_000_000
    assert receipt["avoided_intermediate_states"] == 8_999_999
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash216_authority"] is False
    assert receipt["requires_signed_environmental_vm81_admission"] is True


def test_native_unbounded_workload_optimizer_is_reachable_from_agent():
    dispatcher = _dispatcher()
    workload = Lane5WorkloadEnvelope.from_bytes(
        b"lane5 mandatory optimization workload",
        provenance="pass219-test",
    )
    result = dispatcher.optimize_unbounded_workload(
        workload=workload,
        previous_address=1,
        current_address=2,
        goal_address=3,
        forbidden_boundary_sha256=sha256(b"forbidden").digest(),
        candidates=[
            Lane5RouteCandidate(
                route_witness_sha256=sha256(b"route-0").digest(),
                reciprocal_witness_sha256=sha256(b"reciprocal-0").digest(),
                phase_slot=0,
                trinary_collapse=0,
                binary_collapse=0,
                evidence_count=7,
                contradiction_check_count=3,
            ),
            Lane5RouteCandidate(
                route_witness_sha256=sha256(b"route-1").digest(),
                reciprocal_witness_sha256=sha256(b"reciprocal-1").digest(),
                phase_slot=18,
                trinary_collapse=1,
                binary_collapse=1,
                evidence_count=5,
                contradiction_check_count=2,
            ),
        ],
    )
    assert result["mode"] == "UNBOUNDED_STREAMING_ROUTE_REDUCTION"
    assert result["optimization_selected"] == "LANE5_UNBOUNDED_WORKLOAD_SCALING_1_48"
    receipt = result["receipt"]
    assert receipt["offered_candidates"] == 2
    assert receipt["selected_address"] == 3
    assert receipt["materialized_intermediate_states"] == 0
    assert receipt["candidate_only"] is True
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash216_authority"] is False
    assert receipt["requires_signed_environmental_vm81_admission"] is True


def test_public_default_factory_is_no_longer_1_37_only(monkeypatch):
    sentinel = object()

    def fake_dispatcher(**kwargs):
        assert kwargs["backend"] == "CPU_REFERENCE"
        assert kwargs["state_root"] == "/tmp/lane5"
        return sentinel

    monkeypatch.setattr(warm, "Pass219Lane5MandatoryOptimizationDispatcher", fake_dispatcher)
    assert warm.default_lane5_search(
        backend="CPU_REFERENCE",
        state_root="/tmp/lane5",
    ) is sentinel


def test_authority_record_never_promotes_cache_or_timing_to_canonical_authority():
    authority = Pass219Lane5MandatoryOptimizationDispatcher._authority_record()
    assert authority["candidate_only"] is True
    assert authority["canonical_vm81_mutation_authority"] is False
    assert authority["canonical_hash72_authority"] is False
    assert authority["canonical_hash216_authority"] is False
    assert authority["canonical_persistence_authority"] is False
    assert authority["floating_point_canonical_authority"] is False
    assert authority["requires_signed_environmental_vm81_admission"] is True
