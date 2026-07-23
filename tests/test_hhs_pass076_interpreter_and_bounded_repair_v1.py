from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    ContractError,
    canonical_request,
    make_request,
    product_root,
)
from native_projects.hhs_harmonicode_interpreter.hhs_exact_symbolic_interpreter_v1 import (
    evaluate_term,
    execute_program,
    initialize_state,
)
from native_projects.hhs_harmonicode_interpreter.hhs_executable_ir_v1 import verify_executable_ir
from native_projects.hhs_harmonicode_interpreter.hhs_pass076_api_v1 import create_interpreter_workspace_app
from native_projects.hhs_harmonicode_interpreter.hhs_pass076_workspace_runtime_v1 import (
    HHSNativeInterpreterWorkspaceRuntime,
    build_pass076_demo,
    operation_registry,
)

GOOD_SOURCE = """PHASE_GATE := {
  x==1/y;
  z==1/w;
  xy≠yx;
  Δe=0;
  Ψ=0;
  Θ15=true;
  Ω=true
}
PHASE_GATE
"""
BAD_SOURCE = GOOD_SOURCE.replace("Ω=true", "Ω=false")
AUTH = {
    "role_contract_ref": "role:test-interpreter",
    "task_assignment_ref": "task:test-pass076",
    "capability_lease_ref": "lease:test-pass076",
}


def req(rid, cls, op, payload=None, auth=False, project="project:test", session="session:test"):
    return make_request(
        request_id=rid,
        project_id=project,
        session_id=session,
        operation_class=cls,
        operation_id=op,
        payload=payload or {},
        **(AUTH if auth else {}),
    )


def prepare(source=GOOD_SOURCE):
    rt = HHSNativeInterpreterWorkspaceRuntime()
    assert rt.dispatch(req("req:project", "INGRESS", "workspace.project.create", {"name": "Test"}))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:session", "INGRESS", "workspace.session.open"))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:human", "INGRESS", "workspace.agent.register", {"agent_id": "agent:human:test", "agent_kind": "HUMAN", "capabilities": ["review"]}))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:llm", "INGRESS", "workspace.agent.register", {"agent_id": "agent:llm:test", "agent_kind": "LLM", "capabilities": ["build", "repair"]}))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:buffer", "INGRESS", "workspace.buffer.open", {"buffer_id": "buffer:main", "name": "native_projects/demo/main.hhs", "text": source}))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:source", "MUTATE", "workspace.source.commit", {"buffer_id": "buffer:main", "artifact_id": "artifact:source"}, auth=True))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:parse", "EXECUTE", "workspace.language.parse", {"artifact_id": "artifact:source", "document_id": "doc:main", "ir_id": "ir:main"}))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:ir", "MUTATE", "workspace.language.ir.commit", {"typed_ir_ref": "ir:main", "validation_ref": "validation:ir:main", "artifact_id": "artifact:ir"}, auth=True))["status"] == "ADMITTED"
    return rt


def lower(rt):
    response = rt.dispatch(req("req:lower", "EXECUTE", "workspace.interpreter.lower", {"typed_ir_artifact_ref": "artifact:ir", "executable_ir_id": "exec:main"}))
    assert response["status"] == "ADMITTED"
    return rt.executable_ir_objects["exec:main"]


def execute(rt, executable_ref="exec:main", run_id="run:main"):
    return rt.dispatch(req("req:execute:" + run_id.replace(":", "-"), "EXECUTE", "workspace.interpreter.execute", {"executable_ir_ref": executable_ref, "run_id": run_id}, auth=True))


def prepare_repair(rt):
    assert rt.dispatch(req("req:proposal", "INGRESS", "workspace.change.propose", {
        "proposal_id": "proposal:repair",
        "program_id": "program:interpreter",
        "proposer_agent_ref": "agent:llm:test",
        "summary": "Repair invariant fixture",
        "new_capability_statement": "Repair a product-local Harmonicode program",
        "reusable_capabilities": ["repair.execute", "repair.rollback"],
        "reachable_entrypoint": "workspace.repair.execute",
        "affected_product_paths": ["native_projects/demo"],
        "requested_tests": ["tests/test_hhs_pass076_interpreter_and_bounded_repair_v1.py"],
    }))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:align", "EXECUTE", "workspace.alignment.evaluate", {"proposal_ref": "proposal:repair"}))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:testfail", "MUTATE", "workspace.test.record", {
        "test_record_id": "test:fail",
        "proposal_ref": "proposal:repair",
        "status": "FAIL",
        "passed": 0,
        "failed": 1,
        "commands": ["workspace.interpreter.execute"],
        "evidence_refs": ["run:bad"],
    }, auth=True))["status"] == "ADMITTED"
    response = rt.dispatch(req("req:heal", "EXECUTE", "workspace.healing.plan", {
        "proposal_ref": "proposal:repair",
        "test_record_ref": "test:fail",
        "requested_by_agent_ref": "agent:llm:test",
    }))
    assert response["status"] == "ADMITTED"
    return "healing:proposal:repair:test:fail"


def repair_request(rt, *, new="Ω=true", expected_root=None, target_path="native_projects/demo/main.hhs", transaction="repair:omega"):
    return req("req:repair:" + transaction.replace(":", "-"), "MUTATE", "workspace.repair.execute", {
        "healing_plan_ref": "healing:proposal:repair:test:fail",
        "target_artifact_ref": "artifact:source",
        "target_path": target_path,
        "expected_pre_artifact_root_hash72": expected_root or rt.artifacts["artifact:source"]["artifact_root_hash72"],
        "replacements": [{"old": "Ω=false", "new": new, "expected_count": 1}],
        "transaction_id": transaction,
        "post_artifact_id": f"artifact:{transaction}:source",
    }, auth=True)


def test_registry_implements_interpreter_and_repair_without_private_paths():
    definitions = {x["operation_id"]: x for x in operation_registry()["operations"]}
    assert definitions["workspace.interpreter.execute"]["implemented"] is True
    assert definitions["workspace.repair.execute"]["operation_class"] == "MUTATE"
    assert definitions["workspace.compiler.compile"]["implemented"] is False
    assert definitions["workspace.emulator.run"]["implemented"] is False
    assert not any(x.get("private_authority_path") for x in definitions.values())


def test_lowering_requires_committed_typed_ir_artifact():
    rt = prepare()
    response = rt.dispatch(req("req:badlower", "EXECUTE", "workspace.interpreter.lower", {"typed_ir_artifact_ref": "missing"}))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_COMMITTED_TYPED_IR_ARTIFACT_NOT_FOUND"


def test_lowering_revalidates_source_and_typed_ir():
    rt = prepare()
    executable = lower(rt)
    assert executable["typed_ir_revalidated_before_lowering"] is True
    assert executable["lowering_executes_no_program_effects"] is True
    assert executable["statement_count"] == 9
    assert verify_executable_ir(executable) is True


def test_tampered_source_artifact_is_rejected_by_lowering():
    rt = prepare()
    rt.artifacts["artifact:source"]["content"] += "\nΩ=false"
    response = rt.dispatch(req("req:tamper-source", "EXECUTE", "workspace.interpreter.lower", {"typed_ir_artifact_ref": "artifact:ir", "executable_ir_id": "exec:bad"}))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_EXECUTABLE_IR_SOURCE_ARTIFACT_ROOT"


def test_tampered_typed_ir_artifact_is_rejected_by_lowering():
    rt = prepare()
    rt.artifacts["artifact:ir"]["content"]["blocks"][0]["node_kind"] = "Tampered"
    response = rt.dispatch(req("req:tamper-ir", "EXECUTE", "workspace.interpreter.lower", {"typed_ir_artifact_ref": "artifact:ir", "executable_ir_id": "exec:bad"}))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_EXECUTABLE_IR_TYPED_ARTIFACT_ROOT"


def test_interpreter_requires_runtime_authority_even_for_execute_class():
    rt = prepare(); lower(rt)
    response = rt.dispatch(req("req:noauth", "EXECUTE", "workspace.interpreter.execute", {"executable_ir_ref": "exec:main", "run_id": "run:noauth"}))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_INTERPRETER_EXECUTION_WITHOUT_AUTHORITY_AND_LEASE"


def test_exact_symbolic_evaluator_rejects_floats():
    with pytest.raises(ContractError, match="REJECT_NON_EXACT_LITERAL"):
        evaluate_term("1.5", {})


def test_exact_rational_arithmetic_is_normalized():
    assert evaluate_term("1/2 + 1/3", {}) == {"type": "EXACT_RATIONAL", "numerator": 5, "denominator": 6}


def test_symbolic_reciprocal_is_preserved_without_guessing_value():
    value = evaluate_term("1/y", {})
    assert value["type"] == "SYMBOLIC_EXPRESSION"
    assert value["operator"] == "DIVIDE"
    assert value["operands"][1] == {"type": "SYMBOL", "name": "y"}


def test_successful_execution_closes_required_invariants():
    rt = prepare(); lower(rt)
    response = execute(rt)
    assert response["status"] == "ADMITTED"
    run = response["result"]["execution_run"]
    assert run["status"] == "CLOSED"
    assert run["closed"] is True
    assert all(x == "SATISFIED" for x in run["final_state"]["invariant_status"].values())
    assert run["step_count"] == 9


def test_failed_invariant_is_witnessed_not_silently_closed():
    rt = prepare(BAD_SOURCE); lower(rt)
    response = execute(rt, run_id="run:bad")
    run = response["result"]["execution_run"]
    assert run["status"] == "FAILED"
    assert run["closed"] is False
    assert run["final_state"]["invariant_status"]["Ω"] == "UNRESOLVED_OR_FAILED"
    assert {x["code"] for x in run["final_state"]["diagnostics"]} == {"REQUIRED_INVARIANT_CLOSURE_FAILED"}


def test_ordered_product_distinctness_is_preserved_at_execution():
    rt = prepare(); lower(rt); run = execute(rt)["result"]["execution_run"]
    distinct = [x for x in run["step_receipts"] if x["operation"] == "EVALUATE_DISTINCTNESS"]
    assert len(distinct) == 1
    assert distinct[0]["outcome"]["satisfied"] is True
    observation = distinct[0]["outcome"]["observations"][0]
    assert observation["left_value"]["name"] == "xy"
    assert observation["right_value"]["name"] == "yx"


def test_step_receipts_form_an_ordered_chain():
    rt = prepare(); lower(rt); run = execute(rt)["result"]["execution_run"]
    receipts = run["step_receipts"]
    assert receipts[0]["previous_step_receipt_root_hash72"] == "GENESIS"
    for previous, current in zip(receipts, receipts[1:]):
        assert current["previous_step_receipt_root_hash72"] == previous["step_receipt_root_hash72"]
        assert current["previous_state_root_hash72"] == previous["resulting_state_root_hash72"]


def test_execution_is_deterministic_for_same_run_identity():
    rt = prepare(); executable = lower(rt)
    left = execute_program(run_id="run:deterministic", executable_ir=executable)
    right = execute_program(run_id="run:deterministic", executable_ir=executable)
    assert left == right


def test_execution_root_changes_with_run_identity_but_semantics_match():
    rt = prepare(); executable = lower(rt)
    left = execute_program(run_id="run:left", executable_ir=executable)
    right = execute_program(run_id="run:right", executable_ir=executable)
    assert left["execution_run_root_hash72"] != right["execution_run_root_hash72"]
    assert left["final_state"]["bindings"] == right["final_state"]["bindings"]


def test_bounded_execution_stops_before_unbounded_progress():
    rt = prepare(); executable = lower(rt)
    run = execute_program(run_id="run:bounded", executable_ir=executable, max_steps=2)
    assert run["status"] == "BOUNDED_STOP"
    assert run["step_count"] == 2


def test_single_step_and_state_projection_use_unified_runtime():
    rt = prepare(); lower(rt)
    first = rt.dispatch(req("req:step1", "EXECUTE", "workspace.interpreter.step", {"executable_ir_ref": "exec:main", "run_id": "run:step"}, auth=True))
    assert first["status"] == "ADMITTED"
    state_ref = "interpreter-state:run:step"
    query = rt.dispatch(req("req:state", "QUERY", "workspace.interpreter.state.get", {"state_ref": state_ref}))
    assert query["status"] == "ADMITTED"
    assert query["result"]["interpreter_state"]["step_count"] == 1


def test_step_after_terminal_state_is_rejected():
    rt = prepare(); lower(rt)
    state, plan = initialize_state("run:terminal", rt.executable_ir_objects["exec:main"])
    rt.execution_plans["exec:main"] = plan
    rt.interpreter_states["interpreter-state:run:terminal"] = state
    for index in range(len(plan)):
        result = rt.dispatch(req(f"req:term{index}", "EXECUTE", "workspace.interpreter.step", {"state_ref": "interpreter-state:run:terminal"}, auth=True))
        assert result["status"] == "ADMITTED"
    extra = rt.dispatch(req("req:term-extra", "EXECUTE", "workspace.interpreter.step", {"state_ref": "interpreter-state:run:terminal"}, auth=True))
    assert extra["status"] == "REJECTED"
    assert extra["diagnostics"][0]["code"] == "REJECT_STEP_AFTER_TERMINAL_STATE"


def test_replay_reproduces_exact_execution_root():
    rt = prepare(); lower(rt); execute(rt)
    response = rt.dispatch(req("req:replay", "EXECUTE", "workspace.interpreter.replay", {"execution_run_ref": "run:main", "replay_id": "replay:main"}))
    assert response["status"] == "ADMITTED"
    assert response["result"]["replay_verification"]["matches"] is True


def test_interpreter_test_execution_is_evidence_candidate_not_authority():
    demo = build_pass076_demo()["runtime"]
    # The demo has no Pass075 acceleration plan, so create a minimal deterministic plan binding.
    demo.test_acceleration_plans["plan:test"] = {"test_plan_root_hash72": product_root("plan", {"id": "plan:test"})}
    response = demo.dispatch(req("req:tests", "EXECUTE", "workspace.tests.execute", {
        "test_plan_ref": "plan:test",
        "executable_ir_ref": "executable-ir:repair:pass076:omega",
        "run_id": "run:test-evidence",
        "test_execution_id": "test-exec:main",
    }, auth=True, project="project:pass076-demo", session="session:pass076-demo"))
    assert response["status"] == "ADMITTED"
    evidence = response["result"]["test_execution"]
    assert evidence["status"] == "PASS"
    assert evidence["this_execution_is_evidence_candidate_not_mutation_authority"] is True


def test_repair_requires_mutation_authority():
    rt = prepare(BAD_SOURCE); lower(rt); execute(rt, run_id="run:bad"); prepare_repair(rt)
    request = repair_request(rt)
    request = deepcopy(request)
    request["role_contract_ref"] = request["task_assignment_ref"] = request["capability_lease_ref"] = ""
    request.pop("request_root_hash72", None)
    response = rt.dispatch(canonical_request(request))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_MUTATION_WITHOUT_AUTHORITY_AND_LEASE"


def test_repair_rejects_foundation_target_path():
    rt = prepare(BAD_SOURCE); lower(rt); execute(rt, run_id="run:bad"); prepare_repair(rt)
    response = rt.dispatch(repair_request(rt, target_path="hhs_foundation/main.hhs"))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"].startswith("REJECT_REPAIR_TARGETS_FROZEN_FOUNDATION")


def test_repair_rejects_stale_precondition_root():
    rt = prepare(BAD_SOURCE); lower(rt); execute(rt, run_id="run:bad"); prepare_repair(rt)
    response = rt.dispatch(repair_request(rt, expected_root="stale"))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_REPAIR_STALE_PRECONDITION_ROOT"


def test_repair_rejects_wrong_exact_replacement_count():
    rt = prepare(BAD_SOURCE); lower(rt); execute(rt, run_id="run:bad"); prepare_repair(rt)
    request = repair_request(rt)
    request = deepcopy(request); request["payload"]["replacements"][0]["expected_count"] = 2; request.pop("request_root_hash72", None)
    response = rt.dispatch(canonical_request(request))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"].startswith("REJECT_REPAIR_EXPECTED_COUNT_MISMATCH")


def test_successful_repair_creates_new_lineaged_source_and_closed_execution():
    rt = prepare(BAD_SOURCE); lower(rt); execute(rt, run_id="run:bad"); prepare_repair(rt)
    response = rt.dispatch(repair_request(rt))
    assert response["status"] == "ADMITTED"
    assert response["result"]["mutation_applied"] is True
    transaction = response["result"]["repair_transaction"]
    assert transaction["status"] == "APPLIED_PRODUCT_LOCAL"
    post = rt.artifacts["artifact:repair:omega:source"]
    assert post["lineage"]["parent_artifact_ref"] == "artifact:source"
    assert response["result"]["repaired_execution"]["closed"] is True
    assert rt.artifacts["artifact:source"]["content"] == BAD_SOURCE


def test_failed_repair_postcondition_does_not_commit_candidate_artifact():
    rt = prepare(BAD_SOURCE); lower(rt); execute(rt, run_id="run:bad"); prepare_repair(rt)
    response = rt.dispatch(repair_request(rt, new="Ω=0", transaction="repair:badpost"))
    assert response["status"] == "ADMITTED"
    assert response["result"]["mutation_applied"] is False
    assert response["result"]["repair_transaction"]["status"] == "REJECTED_POSTCONDITION_FAILED"
    assert "artifact:repair:badpost:source" not in rt.artifacts


def test_rollback_creates_new_continuation_without_history_erasure():
    rt = prepare(BAD_SOURCE); lower(rt); execute(rt, run_id="run:bad"); prepare_repair(rt)
    rt.dispatch(repair_request(rt))
    response = rt.dispatch(req("req:rollback", "MUTATE", "workspace.repair.rollback", {
        "transaction_ref": "repair:omega",
        "rollback_ref": "rollback:repair:omega",
        "rollback_execution_id": "rollback-exec:omega",
        "restored_artifact_id": "artifact:restored",
    }, auth=True))
    assert response["status"] == "ADMITTED"
    execution = response["result"]["rollback_execution"]
    assert execution["new_continuation_created"] is True
    assert execution["history_erased"] is False
    assert rt.artifacts["artifact:restored"]["content"] == BAD_SOURCE
    assert rt.artifacts["artifact:repair:omega:source"]["content"] == GOOD_SOURCE


def test_repair_receipt_does_not_self_authorize_future_mutation():
    demo = build_pass076_demo()["snapshot"]
    receipt = next(iter(demo["repair_test_receipts"].values()))
    assert receipt["passed"] is True
    assert receipt["this_receipt_does_not_self_authorize_future_mutation"] is True


def test_snapshot_round_trip_preserves_interpreter_and_repair_state():
    snapshot = build_pass076_demo()["snapshot"]
    restored = HHSNativeInterpreterWorkspaceRuntime(initial_state=snapshot)
    assert restored.snapshot() == snapshot


def test_snapshot_tampering_is_rejected():
    snapshot = build_pass076_demo()["snapshot"]
    snapshot["repair_transactions"]["repair:pass076:omega"]["status"] = "TAMPERED"
    with pytest.raises(ContractError, match="REJECT_PASS076_WORKSPACE_STATE_ROOT_MISMATCH"):
        HHSNativeInterpreterWorkspaceRuntime(initial_state=snapshot)


def test_api_uses_same_canonical_execute_route():
    rt = prepare(); lower(rt)
    client = TestClient(create_interpreter_workspace_app(rt))
    response = client.post("/api/hhs/v1/execute", json=req("req:api", "EXECUTE", "workspace.interpreter.execute", {"executable_ir_ref": "exec:main", "run_id": "run:api"}, auth=True))
    assert response.status_code == 200
    assert response.json()["status"] == "ADMITTED"
    assert response.json()["result"]["execution_closed"] is True


def test_compiler_and_emulator_remain_typed_unavailable():
    rt = prepare()
    compiler = rt.dispatch(req("req:compile", "COMPILE", "workspace.compiler.compile", auth=True))
    emulator = rt.dispatch(req("req:emulate", "EMULATE", "workspace.emulator.run", auth=True))
    assert compiler["status"] == emulator["status"] == "UNAVAILABLE"
    assert compiler["diagnostics"][0]["code"] == "TYPED_UNAVAILABLE_FUTURE_NATIVE_PRODUCT"


def test_demo_closes_repair_without_foundation_mutation():
    demo = build_pass076_demo()
    snapshot = demo["snapshot"]
    assert snapshot["execution_runs"]["execution:pass076:failing"]["status"] == "FAILED"
    assert snapshot["execution_runs"]["execution:repair:pass076:omega"]["status"] == "CLOSED"
    transaction = snapshot["repair_transactions"]["repair:pass076:omega"]
    assert transaction["foundation_mutated"] is False
    assert transaction["history_erased"] is False
