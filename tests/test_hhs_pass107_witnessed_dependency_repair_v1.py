from pathlib import Path
import json
import pytest

from hhs_runtime.hhs_pass107_witnessed_dependency_repair_v1 import (
    CanonicalDependencyContract,
    RepairError,
    RepairLease,
    WitnessedDependencyRepairAgent,
    pass107_self_test,
)


@pytest.fixture(scope="module")
def result():
    return pass107_self_test()


def test_pass107_executes_complete_repair_loop(result):
    assert result["status"] == "PASS"
    assert result["agent_final_state"] == "REPAIRED"
    assert result["real_production_workload_executed"] is True
    assert result["new_capability_admission_created"] is True
    assert result["parallel_repair_implementation_used"] is False
    assert result["mock_components"] == []


def test_pass107_localizes_dependency_binding_root_cause(result):
    cause = result["root_cause"]
    assert cause["root_cause_class"] == "BROKEN_DEPENDENCY_BINDING"
    assert cause["localization_confidence"] == "PROVEN_BY_BINDING_CONTRACT_MISMATCH"
    assert len(cause["ordered_dependency_path"]) == 3


def test_pass107_obligation_closes_only_after_production_validation(result):
    obligation = result["repair_obligation"]
    closure = result["repair_closure"]
    assert obligation["repair_status"] == "REPAIRED_AND_PRODUCTION_VALIDATED"
    assert obligation["closure_receipt_root_hash72"] == closure["repair_closure_root_hash72"]
    assert closure["new_capability_admission_root_hash72"]
    assert closure["invocation_admission_root_hash72"]


def test_pass107_repairs_to_existing_real_entrypoint(result):
    binding = result["repaired_binding"]
    assert binding["module"] == "hhs_runtime.hhs_pass105_6_real_c_asm_backend_closure_v1"
    assert binding["function"] == "pass105_6_self_test"


def test_pass107_background_scan_observes_but_does_not_mutate(result):
    scan = result["background_scan"]
    assert scan["broken_count"] == 1
    assert scan["mutation_performed"] is False


def test_pass107_repair_requires_exact_lease(tmp_path: Path):
    contract = CanonicalDependencyContract("cap", "json", "loads", "claim")
    binding = tmp_path / "b.json"
    binding.write_text(json.dumps({"module": "missing", "function": "x"}), encoding="utf-8")
    agent = WitnessedDependencyRepairAgent(contract)
    agent.observe_failure(binding)
    agent.trace_dependencies(binding)
    agent.open_obligation()
    proposal = agent.propose(binding)
    bad_lease = RepairLease("bad", str(binding.resolve()), "WRONG_OPERATION")
    with pytest.raises(RepairError) as exc:
        agent.execute(proposal, bad_lease)
    assert exc.value.code == "REJECT_UNAUTHORIZED_REPAIR_MUTATION"


def test_pass107_failed_repair_rolls_back_exactly(result):
    rollback = result["failed_repair_rollback"]
    assert rollback["repair_status"] == "ROLLED_BACK"
    assert rollback["obligation_remains_open"] is True
    assert rollback["rollback_receipt_root_hash72"]


def test_pass107_service_registered_and_derived():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    registry = make_default_service_registry()
    service = next(x for x in registry.services() if x["name"] == "runtime.witnessed_dependency_repair.pass107")
    assert service["conformance_decision"]["derivation_complete"] is True
    assert "zero_bypass_runtime_interposer" in service["guards"]
    assert "bounded_repair_lease_required" in service["guards"]
