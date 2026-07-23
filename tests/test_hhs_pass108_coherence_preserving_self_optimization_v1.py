import pytest

from hhs_runtime.hhs_pass108_coherence_preserving_self_optimization_v1 import (
    CoherencePreservingOptimizer,
    DependencyRootedExactCache,
    OptimizationError,
    OptimizationLease,
    pass108_self_test,
)


@pytest.fixture(scope="module")
def result():
    return pass108_self_test()


def test_pass108_executes_real_full_admitted_capability_audit(result):
    assert result["status"] == "PASS"
    assert result["full_admitted_capability_set_audited"] is True
    assert result["admitted_capability_count"] == 3
    assert result["real_backend_compilations_executed"] == 3
    assert result["real_negative_attacks_executed_after_optimization"] is True


def test_pass108_proves_real_efficiency_gain(result):
    optimization = result["optimization"]
    assert optimization["baseline_profile"]["deterministic_work_units"] == 2
    assert optimization["optimized_profile"]["deterministic_work_units"] == 1
    assert optimization["optimized_profile"]["real_execution_count"] == 1
    assert optimization["optimized_profile"]["cache_hit_count"] == 1
    assert optimization["observed_work_unit_reduction"] == 1


def test_pass108_preserves_complete_coherence(result):
    optimization = result["optimization"]
    assert optimization["coherence_vector_preserved"] is True
    assert optimization["capability_preservation_ratio"] == "1/1"
    assert optimization["negative_boundary_preservation_ratio"] == "77/77"
    assert optimization["exactness_preserved"] is True
    assert optimization["authority_path_preserved"] is True
    assert optimization["provenance_preserved"] is True
    assert result["capability_devolution_detected"] is False


def test_pass108_rejects_stale_cache(result):
    assert result["optimization"]["stale_dependency_rejection"] == "REJECT_STALE_CACHE_RESULT"


def test_pass108_requires_exact_optimization_lease():
    optimizer = CoherencePreservingOptimizer()
    baseline = {"baseline_root_hash72": "root", "coherence_vector_root_hash72": "dep", "negative_boundary_coherence": {}}
    profile = {"profile_root_hash72": "p", "coherence_roots": ["x"], "deterministic_work_units": 2}
    candidate = {
        "target_capability_id": "cap",
        "optimization_class": "EXACT_DEPENDENCY_ROOTED_RESULT_REUSE",
        "candidate_root_hash72": "c",
    }
    bad = OptimizationLease("bad", "other", "EXACT_DEPENDENCY_ROOTED_RESULT_REUSE")
    with pytest.raises(OptimizationError) as exc:
        optimizer.apply_and_validate(baseline, profile, candidate, bad)
    assert exc.value.code == "REJECT_AUTHORITY_BYPASS_OPTIMIZATION"


def test_pass108_cache_is_dependency_rooted():
    cache = DependencyRootedExactCache()
    calls = {"count": 0}
    def execute():
        calls["count"] += 1
        return {"status": "PASS", "root_hash72": "r"}
    first, hit1 = cache.get_or_execute("cap", "dep1", execute)
    second, hit2 = cache.get_or_execute("cap", "dep1", execute)
    third, hit3 = cache.get_or_execute("cap", "dep2", execute)
    assert first == second == third
    assert (hit1, hit2, hit3) == (False, True, False)
    assert calls["count"] == 2


def test_pass108_service_registered_and_derived():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    registry = make_default_service_registry()
    service = next(x for x in registry.services() if x["name"] == "runtime.coherence_preserving_self_optimization.pass108")
    assert service["conformance_decision"]["derivation_complete"] is True
    assert "zero_bypass_runtime_interposer" in service["guards"]
    assert "capability_devolution_prohibited" in service["guards"]
