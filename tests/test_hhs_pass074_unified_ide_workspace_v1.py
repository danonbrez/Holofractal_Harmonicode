from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from native_projects.hhs_ide_workspace.hhs_native_workspace_project_v1 import (
    FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    HHSNativeWorkspaceRuntime,
    build_demo_workspace,
    build_pass074_release_bundle,
    operation_registry,
)
from native_projects.hhs_ide_workspace.hhs_unified_runtime_api_v1 import create_workspace_app
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    REQUEST_SCHEMA,
    RESPONSE_SCHEMA,
    ContractError,
    canonical_request,
    make_request,
)
from native_projects.hhs_ide_workspace.hhs_workspace_replay_runner_v1 import replay_workspace, verify_capsule

AUTH = {
    "role_contract_ref": "role:test-developer",
    "task_assignment_ref": "task:test-pass074",
    "capability_lease_ref": "lease:test-pass074",
}


def req(request_id, operation_class, operation_id, payload=None, *, surface="TEST", authority=False):
    return make_request(
        request_id=request_id,
        project_id="project:test",
        session_id="session:test",
        operation_class=operation_class,
        operation_id=operation_id,
        payload=payload or {},
        client_surface=surface,
        **(AUTH if authority else {}),
    )


def prepared_runtime():
    rt = HHSNativeWorkspaceRuntime()
    assert rt.dispatch(req("req:p", "INGRESS", "workspace.project.create", {"name": "Test"}))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:s", "INGRESS", "workspace.session.open"))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:b", "INGRESS", "workspace.buffer.open", {"buffer_id": "buffer:main", "name": "main.hhs", "text": "x=(1)"}))["status"] == "ADMITTED"
    return rt


def test_pass074_request_and_response_envelopes_are_canonical():
    request = req("req:canonical", "INGRESS", "workspace.project.create")
    assert request["schema"] == REQUEST_SCHEMA
    assert len(request["request_root_hash72"]) == 72
    response = HHSNativeWorkspaceRuntime().dispatch(request)
    assert response["schema"] == RESPONSE_SCHEMA
    assert len(response["response_root_hash72"]) == 72


def test_pass074_rejects_modified_request_root():
    request = req("req:tamper", "INGRESS", "workspace.project.create")
    request["payload"]["name"] = "tampered"
    with pytest.raises(ContractError, match="REJECT_REQUEST_ROOT_MISMATCH"):
        canonical_request(request)


def test_pass074_all_clients_use_same_dispatch_contract():
    roots = []
    for surface in ("GUI", "CLI", "EXTERNAL_API"):
        rt = HHSNativeWorkspaceRuntime()
        response = rt.dispatch(req("req:same", "INGRESS", "workspace.project.create", {"name": "Same"}, surface=surface))
        roots.append(response["result"]["project"]["project_root_hash72"])
    assert len(set(roots)) == 1


def test_pass074_editor_buffer_is_not_canonical_source():
    rt = prepared_runtime()
    buffer = rt.buffers["buffer:main"]
    assert buffer["editor_buffer_is_not_canonical_source"] is True
    assert buffer["committed_artifact_ref"] == ""
    assert not rt.artifacts


def test_pass074_mutation_requires_authority_task_and_lease():
    rt = prepared_runtime()
    response = rt.dispatch(req("req:unauthorized", "MUTATE", "workspace.buffer.update", {"buffer_id": "buffer:main", "text": "changed"}))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_MUTATION_WITHOUT_AUTHORITY_AND_LEASE"
    assert rt.buffers["buffer:main"]["text"] == "x=(1)"


def test_pass074_authorized_buffer_mutation_does_not_mutate_source_artifact():
    rt = prepared_runtime()
    response = rt.dispatch(req("req:update", "MUTATE", "workspace.buffer.update", {"buffer_id": "buffer:main", "text": "x=(2)"}, authority=True))
    assert response["status"] == "ADMITTED"
    assert response["result"]["canonical_source_changed"] is False
    assert not rt.artifacts


def test_pass074_commit_creates_lineaged_artifact_and_receipt():
    rt = prepared_runtime()
    response = rt.dispatch(req("req:commit", "MUTATE", "workspace.source.commit", {"buffer_id": "buffer:main", "artifact_id": "artifact:main:0"}, authority=True))
    assert response["status"] == "ADMITTED"
    artifact = rt.get_artifact("artifact:main:0")
    assert artifact["lineage"]["parent_artifact_ref"] == "GENESIS"
    assert artifact["compiled_artifact_self_authorizes"] is False
    assert rt.get_receipt("receipt:req:commit")["console_output_is_not_receipt"] is True


def test_pass074_inspection_is_bounded_not_private_interpreter():
    rt = prepared_runtime()
    response = rt.dispatch(req("req:inspect", "EXECUTE", "workspace.source.inspect", {"buffer_id": "buffer:main"}))
    assert response["status"] == "ADMITTED"
    assert response["result"]["execution_kind"] == "BOUNDED_SOURCE_INSPECTION_NOT_INTERPRETER_EXECUTION"
    assert response["result"]["balanced_delimiters"] is True


def test_pass074_future_interpreter_compiler_emulator_are_typed_unavailable():
    rt = prepared_runtime()
    cases = [
        ("EXECUTE", "workspace.interpreter.execute"),
        ("COMPILE", "workspace.compiler.compile"),
        ("EMULATE", "workspace.emulator.run"),
    ]
    for i, (cls, op) in enumerate(cases):
        response = rt.dispatch(req(f"req:future:{i}", cls, op, authority=True))
        assert response["status"] == "UNAVAILABLE"
        assert response["diagnostics"][0]["code"] == "TYPED_UNAVAILABLE_FUTURE_NATIVE_PRODUCT"


def test_pass074_event_stream_is_committed_projection():
    rt = prepared_runtime()
    events = rt.get_events_after(1)
    assert events
    assert [x["sequence"] for x in events] == sorted(x["sequence"] for x in events)
    assert all(len(x["event_root_hash72"]) == 72 for x in events)
    for left, right in zip(rt.events, rt.events[1:]):
        assert right["previous_event_root_hash72"] == left["event_root_hash72"]


def test_pass074_snapshot_reconstructs_exact_state():
    rt = prepared_runtime()
    rt.dispatch(req("req:commit2", "MUTATE", "workspace.source.commit", {"buffer_id": "buffer:main", "artifact_id": "artifact:main:0"}, authority=True))
    snapshot = rt.snapshot()
    restored = HHSNativeWorkspaceRuntime(initial_state=snapshot)
    assert restored.snapshot() == snapshot


def test_pass074_snapshot_tampering_is_rejected():
    snapshot = prepared_runtime().snapshot()
    snapshot["buffers"]["buffer:main"]["text"] = "tampered"
    with pytest.raises(ContractError, match="REJECT_WORKSPACE_STATE_ROOT_MISMATCH"):
        HHSNativeWorkspaceRuntime(initial_state=snapshot)


def test_pass074_operation_registry_has_no_private_authority_paths():
    registry = operation_registry()
    assert registry["schema"] == "HHS_API_OPERATION_REGISTRY_V1"
    assert all(x["unified_api_only"] for x in registry["operations"])
    assert not any(x["private_authority_path"] for x in registry["operations"])


def test_pass074_project_index_is_runtime_projection():
    rt = prepared_runtime()
    response = rt.dispatch(req("req:index", "QUERY", "workspace.project.index"))
    index = response["result"]["index"]
    assert index["runtime_state_is_authoritative"] is True
    assert index["object_refs"] == ["buffer:main"]


def test_pass074_fastapi_routes_use_unified_dispatcher():
    rt = HHSNativeWorkspaceRuntime()
    client = TestClient(create_workspace_app(rt))
    response = client.post("/api/hhs/v1/ingress", json=req("req:api", "INGRESS", "workspace.project.create", {"name": "API"}, surface="GUI"))
    assert response.status_code == 200
    assert response.json()["status"] == "ADMITTED"
    assert "project:test" in rt.projects


def test_pass074_api_rejects_wrong_route_operation_class():
    client = TestClient(create_workspace_app())
    response = client.post("/api/hhs/v1/ingress", json=req("req:wrong", "QUERY", "workspace.state.get"))
    assert response.status_code == 400
    assert "REJECT_ROUTE_OPERATION_CLASS_MISMATCH" in response.text


def test_pass074_artifact_receipt_and_state_getters_project_runtime_objects():
    rt = prepared_runtime()
    rt.dispatch(req("req:commit3", "MUTATE", "workspace.source.commit", {"buffer_id": "buffer:main", "artifact_id": "artifact:main:0"}, authority=True))
    client = TestClient(create_workspace_app(rt))
    assert client.get("/api/hhs/v1/artifacts/artifact:main:0").status_code == 200
    assert client.get("/api/hhs/v1/receipts/receipt:req:commit3").status_code == 200
    assert client.get("/api/hhs/v1/state/project:test").status_code == 200


def test_pass074_websocket_events_are_existing_committed_events():
    rt = prepared_runtime()
    client = TestClient(create_workspace_app(rt))
    with client.websocket_connect("/api/hhs/v1/events?after=0") as ws:
        first = ws.receive_json()
        assert first == rt.events[0]


def test_pass074_release_bundle_is_native_product_not_foundation_mutation():
    bundle = build_pass074_release_bundle()
    assert bundle["platform_dependency"]["total_system_root_hash72"] == FROZEN_PASS072_SYSTEM_ROOT_HASH72
    assert bundle["platform_dependency"]["foundation_modified"] is False
    assert bundle["new_orphan_modules"] == 0
    assert len(bundle["product_root_hash72"]) == 72


def test_pass074_replay_capsule_is_context_and_path_independent(tmp_path):
    demo = build_demo_workspace()
    source = Path(__file__).resolve().parents[1] / "native_projects/hhs_ide_workspace/hhs_workspace_contracts_v1.py"
    capsule = {
        "schema": "HHS_WORKSPACE_REPLAY_CAPSULE_V1",
        "thread_context_required": False,
        "llm_context_window_required": False,
        "host_path_required": False,
        "source_bindings": [{"relative_path": "contracts.py", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}],
        "workspace_state": demo["snapshot"],
        "expected_workspace_state_root_hash72": demo["snapshot"]["workspace_state_root_hash72"],
    }
    shutil.copy2(source, tmp_path / "contracts.py")
    assert verify_capsule(tmp_path, capsule)["ok"] is True
    receipt = replay_workspace(tmp_path, capsule)
    assert receipt["ok"] is True
    assert receipt["thread_context_used"] is False
    assert receipt["host_path_used_as_identity"] is False


def network_runtime():
    rt = prepared_runtime()
    for agent_id, kind in (("agent:human:reviewer", "HUMAN"), ("agent:llm:builder", "LLM")):
        response = rt.dispatch(req(
            f"req:register:{kind.lower()}", "INGRESS", "workspace.agent.register",
            {"agent_id": agent_id, "agent_kind": kind, "capabilities": ["code", "review"]},
        ))
        assert response["status"] == "ADMITTED"
    return rt


def submit_aligned_proposal(rt, proposal_id="proposal:capability:1"):
    response = rt.dispatch(req(
        f"req:{proposal_id}", "INGRESS", "workspace.change.propose",
        {
            "proposal_id": proposal_id,
            "program_id": "program:workspace-extension",
            "proposer_agent_ref": "agent:llm:builder",
            "summary": "Add a reusable workspace capability",
            "new_capability_statement": "Expose reusable repository analysis through the unified API",
            "reusable_capabilities": ["repository.analysis"],
            "reachable_entrypoint": "workspace.source.inspect",
            "affected_product_paths": ["native_projects/hhs_ide_workspace"],
            "requested_tests": ["tests/test_hhs_pass074_unified_ide_workspace_v1.py"],
        },
    ))
    assert response["status"] == "ADMITTED"
    return response


def test_pass074_development_protocol_is_open_ended_above_frozen_foundation():
    rt = HHSNativeWorkspaceRuntime()
    protocol = rt.development_protocol
    assert protocol["platform_boundary"]["frozen_pass"] == "PASS_072"
    assert protocol["open_ended_development"]["fixed_terminal_pass"] is False
    assert protocol["open_ended_development"]["future_passes_admissible_while_constraints_hold"] is True
    assert protocol["product_constraint"]["new_orphan_modules_permitted"] is False


def test_pass074_agent_registration_confers_no_authority():
    rt = network_runtime()
    agent = rt.agents["agent:llm:builder"]
    assert agent["schema"] == "HHS_DEVELOPMENT_AGENT_IDENTITY_V1"
    assert agent["registration_confers_no_platform_authority"] is True
    response = rt.dispatch(req(
        "req:agent-no-authority", "MUTATE", "workspace.buffer.update",
        {"buffer_id": "buffer:main", "text": "unauthorized"},
    ))
    assert response["status"] == "REJECTED"


def test_pass074_change_proposal_requires_registered_agent():
    rt = prepared_runtime()
    response = rt.dispatch(req(
        "req:proposal-unregistered", "INGRESS", "workspace.change.propose",
        {
            "proposal_id": "proposal:no-agent",
            "program_id": "program:no-agent",
            "proposer_agent_ref": "agent:missing",
            "new_capability_statement": "Capability",
            "reusable_capabilities": ["capability"],
            "reachable_entrypoint": "workspace.source.inspect",
            "affected_product_paths": ["native_projects/hhs_ide_workspace"],
        },
    ))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_PROPOSER_AGENT_NOT_REGISTERED"


def test_pass074_alignment_admits_reachable_reusable_product_proposal():
    rt = network_runtime()
    submit_aligned_proposal(rt)
    response = rt.dispatch(req(
        "req:evaluate-aligned", "EXECUTE", "workspace.alignment.evaluate",
        {"proposal_ref": "proposal:capability:1"},
    ))
    decision = response["result"]["alignment_decision"]
    assert response["status"] == "ADMITTED"
    assert decision["admitted"] is True
    assert decision["decision"] == "ADMIT_PROPOSAL_TO_TEST"
    assert decision["capability_constraint_satisfied"] is True


def test_pass074_alignment_rejects_orphan_like_proposal():
    rt = network_runtime()
    response = rt.dispatch(req(
        "req:orphan-proposal", "INGRESS", "workspace.change.propose",
        {
            "proposal_id": "proposal:orphan",
            "program_id": "program:orphan",
            "proposer_agent_ref": "agent:llm:builder",
            "summary": "Disconnected file",
            "affected_product_paths": ["native_projects/hhs_ide_workspace/orphan.py"],
        },
    ))
    assert response["status"] == "ADMITTED"
    evaluated = rt.dispatch(req(
        "req:evaluate-orphan", "EXECUTE", "workspace.alignment.evaluate",
        {"proposal_ref": "proposal:orphan"},
    ))
    decision = evaluated["result"]["alignment_decision"]
    assert decision["admitted"] is False
    assert "MISSING_REUSABLE_CAPABILITY" in decision["reasons"]
    assert "MISSING_REACHABLE_ENTRYPOINT" in decision["reasons"]


def test_pass074_direct_foundation_mutation_is_rejected_even_with_authority():
    rt = prepared_runtime()
    response = rt.dispatch(req(
        "req:foundation-mutation", "MUTATE", "workspace.buffer.update",
        {
            "buffer_id": "buffer:main",
            "text": "foundation mutation",
            "foundation_change_requested": True,
            "target_scope": "PASS_072_FOUNDATION",
        },
        authority=True,
    ))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_FOUNDATION_MUTATION_REQUIRES_REVERSIBLE_ALIGNMENT_PATCH"
    decision_ref = response["result"]["alignment_decision_ref"]
    assert rt.alignment_decisions[decision_ref]["foundation_mutation_permitted"] is False
    assert rt.buffers["buffer:main"]["text"] == "x=(1)"


def test_pass074_every_admitted_product_mutation_has_alignment_receipt():
    rt = prepared_runtime()
    response = rt.dispatch(req(
        "req:aligned-update", "MUTATE", "workspace.buffer.update",
        {"buffer_id": "buffer:main", "text": "aligned"},
        authority=True,
    ))
    assert response["status"] == "ADMITTED"
    decision_ref = response["result"]["alignment_decision_ref"]
    assert rt.alignment_decisions[decision_ref]["decision"] == "ADMIT_PRODUCT_LOCAL_EFFECT"
    receipt = rt.get_receipt("receipt:req:aligned-update")
    assert receipt["alignment_decision_ref"] == decision_ref


def test_pass074_failed_test_record_generates_bounded_product_healing_plan():
    rt = network_runtime()
    submit_aligned_proposal(rt)
    record_response = rt.dispatch(req(
        "req:test-record", "MUTATE", "workspace.test.record",
        {
            "test_record_id": "test-record:1",
            "proposal_ref": "proposal:capability:1",
            "status": "FAIL",
            "passed": 5,
            "failed": 1,
            "commands": ["pytest -q"],
            "diagnostics": [{"code": "ASSERTION_FAILED"}],
        },
        authority=True,
    ))
    assert record_response["status"] == "ADMITTED"
    plan_response = rt.dispatch(req(
        "req:healing-plan", "EXECUTE", "workspace.healing.plan",
        {
            "proposal_ref": "proposal:capability:1",
            "test_record_ref": "test-record:1",
            "requested_by_agent_ref": "agent:llm:builder",
        },
    ))
    plan = plan_response["result"]["healing_plan"]
    assert plan["schema"] == "HHS_BOUNDED_SELF_HEALING_PLAN_V1"
    assert plan["auto_apply"] is False
    assert plan["foundation_mutation_permitted"] is False
    assert plan["rollback_required"] is True


def test_pass074_healing_rejects_frozen_foundation_scope():
    rt = network_runtime()
    rt.dispatch(req(
        "req:foundation-proposal", "INGRESS", "workspace.change.propose",
        {
            "proposal_id": "proposal:foundation",
            "program_id": "program:foundation",
            "proposer_agent_ref": "agent:llm:builder",
            "new_capability_statement": "Foundation repair",
            "reusable_capabilities": ["repair"],
            "reachable_entrypoint": "workspace.repair",
            "affected_product_paths": [],
            "affected_foundation_paths": ["hhs_runtime/foundation.py"],
            "reversible_alignment_patch_ref": "patch:foundation:1",
        },
    ))
    rt.dispatch(req(
        "req:foundation-test", "MUTATE", "workspace.test.record",
        {
            "test_record_id": "test-record:foundation",
            "proposal_ref": "proposal:foundation",
            "status": "FAIL",
            "failed": 1,
        },
        authority=True,
    ))
    response = rt.dispatch(req(
        "req:foundation-heal", "EXECUTE", "workspace.healing.plan",
        {
            "proposal_ref": "proposal:foundation",
            "test_record_ref": "test-record:foundation",
            "requested_by_agent_ref": "agent:llm:builder",
        },
    ))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_AUTOMATED_HEALING_OF_FROZEN_FOUNDATION"


def test_pass074_agent_handoff_is_context_independent_and_non_authorizing():
    rt = network_runtime()
    submit_aligned_proposal(rt)
    response = rt.dispatch(req(
        "req:handoff", "MUTATE", "workspace.handoff.create",
        {
            "handoff_id": "handoff:1",
            "from_agent_ref": "agent:llm:builder",
            "to_agent_ref": "agent:human:reviewer",
            "proposal_refs": ["proposal:capability:1"],
            "test_record_refs": [],
            "required_actions": ["REVIEW", "TEST"],
        },
        authority=True,
    ))
    capsule = response["result"]["handoff"]
    assert capsule["thread_context_required"] is False
    assert capsule["llm_context_window_required"] is False
    assert capsule["repository_state_authoritative"] is True
    assert capsule["handoff_confers_no_authority"] is True


def test_pass074_demo_exercises_human_llm_exchange_and_alignment():
    demo = build_demo_workspace()
    snapshot = demo["snapshot"]
    assert "agent:human:developer" in snapshot["agents"]
    assert "agent:llm:builder" in snapshot["agents"]
    assert "proposal:demo:1" in snapshot["proposals"]
    assert "proposal-alignment:proposal:demo:1" in snapshot["alignment_decisions"]
    assert "handoff:demo:1" in snapshot["handoffs"]
