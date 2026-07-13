from hhs_backend.runtime.hhs_deterministic_manifold_execution_v1 import (
 deterministic_manifold_execution_self_test, run_deterministic_manifold_execution,
 apply_scoped_phase_cancellation, independently_revalidate,
)

def test_pass063_self_test(): assert deterministic_manifold_execution_self_test()["ok"]

def test_canonical_algebra_uses_existing_runtime_path():
 r=run_deterministic_manifold_execution(); assert r["ok"]
 assert r["formal_state"]["linguistic_interpretation_inserted"] is False
 assert r["constraint_propagation"]["parallel_semantics_created"] is False

def test_contradiction_is_local_not_global():
 r=run_deterministic_manifold_execution(); c=r["local_conflicts"]
 assert c["conflict_count"]==1
 assert c["contradiction_implies_global_failure"] is False
 assert c["conflicts"][0]["global_failure"] is False

def test_scoped_cancellation_preserves_unaffected_structure():
 r=run_deterministic_manifold_execution(); x=r["phase_cancellation"]
 assert x["minimum_necessary_cancellation"]
 assert x["unaffected_structure_preserved"]
 assert x["negative_phase_acquired_global_rejection_authority"] is False

def test_overbroad_cancellation_rejected():
 r=run_deterministic_manifold_execution()
 bad=apply_scoped_phase_cancellation(r["constraint_propagation"],r["local_conflicts"],requested_scope=["relation:02","relation:05","relation:12"])
 assert "REJECT_PHASE_CANCELLATION_EXCEEDS_CONFLICT_SCOPE" in bad["reasons"]

def test_revalidation_required():
 r=run_deterministic_manifold_execution(); bad=independently_revalidate(r["closure"],local_revalidation=False)
 assert "REJECT_SURVIVING_STATE_WITHOUT_INDEPENDENT_REVALIDATION" in bad["reasons"]
