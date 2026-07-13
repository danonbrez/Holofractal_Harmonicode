from hhs_backend.runtime.hhs_capability_contract_v1 import capability_contract_self_test, validate_capability_contract, build_capability_contract
from hhs_backend.runtime.hhs_capability_provider_registry_v1 import capability_provider_registry_self_test, validate_provider_record, build_default_provider_registry
from hhs_backend.runtime.hhs_capability_resolution_v1 import capability_resolution_self_test, resolve_capability
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import provider_execution_proposal_self_test, build_provider_execution_proposal, validate_provider_execution_proposal
from hhs_backend.runtime.hhs_capability_policy_gate_v1 import capability_policy_gate_self_test, evaluate_capability_policy_gate
from hhs_backend.runtime.hhs_provider_invocation_receipt_v1 import provider_invocation_receipt_self_test, invoke_provider_with_receipt, validate_provider_invocation_receipt
from hhs_backend.runtime.hhs_provider_result_ingress_v1 import provider_result_ingress_self_test, ingress_provider_result
from hhs_backend.runtime.hhs_capability_fallback_plan_v1 import capability_fallback_plan_self_test, build_capability_fallback_plan, validate_capability_fallback_plan
from hhs_backend.runtime.hhs_universal_capability_fabric_v1 import universal_capability_fabric_self_test, run_universal_capability_fabric


def test_capability_contracts_and_registry():
    assert capability_contract_self_test()["ok"]
    assert capability_provider_registry_self_test()["ok"]
    bad_contract = dict(build_capability_contract("OCR"), raw_provider_output_is_canonical=True)
    assert not validate_capability_contract(bad_contract)["ok"]
    registry = build_default_provider_registry()
    bad_provider = dict(registry["providers"][0], private_truth_pipeline_allowed=True)
    assert not validate_provider_record(bad_provider)["ok"]


def test_resolution_and_proposal_do_not_authorize_mutation():
    assert capability_resolution_self_test()["ok"]
    resolved = resolve_capability("OCR")
    assert resolved["ok"]
    assert not resolved["capability_selection_grants_execution_authority"]
    assert provider_execution_proposal_self_test()["ok"]
    proposal = build_provider_execution_proposal(capability_class="OCR", project_id="project:test", input_payload="%PDF")
    bad = dict(proposal, successful_invocation_implies_admitted_mutation=True)
    assert not validate_provider_execution_proposal(bad)["ok"]


def test_policy_receipt_and_ingress_require_runtime_pipeline():
    assert capability_policy_gate_self_test()["ok"]
    assert provider_invocation_receipt_self_test()["ok"]
    assert provider_result_ingress_self_test()["ok"]
    proposal = build_provider_execution_proposal(capability_class="OCR", project_id="project:test", input_payload="%PDF")
    decision = evaluate_capability_policy_gate(proposal)
    assert decision["ok"]
    assert not decision["provider_result_canonical_on_return"]
    receipt = invoke_provider_with_receipt(proposal, simulated_raw_result="raw text")
    assert validate_provider_invocation_receipt(receipt)["ok"]
    ingress = ingress_provider_result(receipt, project_id="project:test", output_modality="TEXT")
    assert ingress["ok"]
    assert not ingress["provider_output_is_canonical_without_runtime_admission"]


def test_fallback_and_fabric():
    assert capability_fallback_plan_self_test()["ok"]
    plan = build_capability_fallback_plan("OCR", failed_attempts=[{"provider_id": "provider:a", "status": "FAILED"}])
    assert validate_capability_fallback_plan(plan)["ok"]
    assert plan["failed_attempt_history"]
    assert universal_capability_fabric_self_test()["ok"]
    run = run_universal_capability_fabric(project_id="project:test", capability_class="OCR", input_payload="%PDF", simulated_raw_result="text")
    assert run["ok"]
    assert run["provider_never_becomes_canonical_authority"]
    assert run["raw_provider_result_reentered_universal_modality_pipeline"]
    assert run["successful_invocation_does_not_equal_admitted_mutation"]


def test_unregistered_capability_rejected():
    rejected = run_universal_capability_fabric(project_id="project:test", capability_class="NOPE", input_payload="x")
    assert not rejected["ok"]
    assert rejected["status"] == "REJECT_UNIVERSAL_CAPABILITY_FABRIC_RUN"
