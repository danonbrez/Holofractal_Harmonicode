from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import hashlib
import json
import shutil

import pytest
from fastapi.testclient import TestClient

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    ContractError,
    make_request,
    product_root,
)
from native_projects.hhs_harmonicode_language.hhs_harmonicode_parser_v1 import parse_source
from native_projects.hhs_harmonicode_language.hhs_typed_ir_v1 import build_typed_ir, validate_typed_ir
from native_projects.hhs_harmonicode_language.hhs_agent_test_acceleration_v1 import test_catalog as build_test_catalog
from native_projects.hhs_harmonicode_language.hhs_pass075_api_v1 import create_language_workspace_app
from native_projects.hhs_harmonicode_language.hhs_pass075_contracts_v1 import LANGUAGE_REPLAY_CAPSULE_SCHEMA
from native_projects.hhs_harmonicode_language.hhs_pass075_replay_runner_v1 import (
    Pass075ReplayError,
    replay_language_workspace,
    verify_capsule,
)
from native_projects.hhs_harmonicode_language.hhs_pass075_workspace_runtime_v1 import (
    HHSNativeLanguageWorkspaceRuntime,
    build_pass075_demo,
    build_pass075_release_bundle,
    operation_registry,
)

PROJECT = "project:test:075"
SESSION = "session:test:075"
AUTHORITY = {
    "role_contract_ref": "role:test:075",
    "task_assignment_ref": "task:test:075",
    "capability_lease_ref": "lease:test:075",
}
SOURCE = """PHASE_GATE := {
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


def req(request_id, operation_class, operation_id, payload=None, authority=False):
    kwargs = AUTHORITY if authority else {}
    return make_request(
        request_id=request_id,
        project_id=PROJECT,
        session_id=SESSION,
        operation_class=operation_class,
        operation_id=operation_id,
        payload=payload or {},
        **kwargs,
    )


def prepared_runtime(*, commit_source=True, parse=True):
    rt = HHSNativeLanguageWorkspaceRuntime()
    assert rt.dispatch(req("req:project", "INGRESS", "workspace.project.create", {"name": "Test 075"}))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:session", "INGRESS", "workspace.session.open"))["status"] == "ADMITTED"
    for agent_id, kind in (("agent:human:reviewer", "HUMAN"), ("agent:llm:builder", "LLM")):
        assert rt.dispatch(req(f"req:{kind}", "INGRESS", "workspace.agent.register", {"agent_id": agent_id, "agent_kind": kind, "capabilities": ["language", "test"]}))["status"] == "ADMITTED"
    assert rt.dispatch(req("req:buffer", "INGRESS", "workspace.buffer.open", {"buffer_id": "buffer:main", "name": "main.hhs", "text": SOURCE}))["status"] == "ADMITTED"
    if commit_source:
        assert rt.dispatch(req("req:source:commit", "MUTATE", "workspace.source.commit", {"buffer_id": "buffer:main", "artifact_id": "artifact:source:0"}, authority=True))["status"] == "ADMITTED"
    if parse:
        payload = {"artifact_id": "artifact:source:0"} if commit_source else {"buffer_id": "buffer:main"}
        payload.update({"document_id": "language-doc:main", "ir_id": "typed-ir:main"})
        assert rt.dispatch(req("req:parse", "EXECUTE", "workspace.language.parse", payload))["status"] == "ADMITTED"
    return rt


def aligned_runtime():
    rt = prepared_runtime()
    proposal = rt.dispatch(req("req:proposal", "INGRESS", "workspace.change.propose", {
        "proposal_id": "proposal:language",
        "program_id": "program:language",
        "proposer_agent_ref": "agent:llm:builder",
        "summary": "Add typed language service",
        "new_capability_statement": "Parse Harmonicode into reusable typed IR",
        "reusable_capabilities": ["harmonicode.parse", "typed-ir.validate"],
        "reachable_entrypoint": "workspace.language.parse",
        "affected_product_paths": ["native_projects/hhs_harmonicode_language"],
        "requested_tests": ["tests/test_hhs_pass075_harmonicode_language_service_v1.py"],
    }))
    assert proposal["status"] == "ADMITTED"
    decision = rt.dispatch(req("req:align", "EXECUTE", "workspace.alignment.evaluate", {"proposal_ref": "proposal:language"}))
    assert decision["result"]["alignment_decision"]["admitted"] is True
    return rt


def test_parser_preserves_exact_source_spans():
    ast = parse_source("x==1/y\nxy≠yx\n")
    assert ast["nodes"][0]["source_span"]["start"] == 0
    assert ast["nodes"][0]["source_span"]["end"] == 6
    assert ast["nodes"][0]["source_text"] == "x==1/y"
    assert ast["nodes"][1]["source_text"] == "xy≠yx"
    assert ast["source_spans_preserved"] is True


def test_parser_preserves_gate_children_and_order():
    ast = parse_source(SOURCE)
    gate = ast["nodes"][0]
    assert gate["kind"] == "GateDeclaration"
    assert [x["kind"] for x in gate["children"]][:3] == ["AssertEquality", "AssertEquality", "DistinctChain"]
    assert ast["nodes"][1]["kind"] == "GateInvocation"


def test_parser_is_deterministic_and_nonexecuting():
    left = parse_source(SOURCE)
    right = parse_source(SOURCE)
    assert left == right
    assert left["ast_root_hash72"] == right["ast_root_hash72"]
    assert left["parser_executes_program_effects"] is False


def test_typed_ir_preserves_required_metadata():
    ast = parse_source(SOURCE)
    ir = build_typed_ir(ast, ir_id="ir:test", source_ref="artifact:source", source_kind="COMMITTED_SOURCE_ARTIFACT", source_root_hash72="root:source", source_sha256=ast["source_sha256"])
    assert ir["schema"] == "HHS_TYPED_IR_V1"
    for key in (
        "source_spans_preserved", "symbol_identity_preserved", "type_information_preserved",
        "authority_requirements_preserved", "effect_declarations_preserved",
        "invariant_bindings_preserved", "artifact_lineage_preserved", "reconstruction_recipe_preserved",
    ):
        assert ir[key] is True
    assert ir["execution_permitted"] is False
    assert all(len(x["invariant_bindings"]) == 4 for x in ir["blocks"])


def test_ordered_product_identity_is_not_collapsed():
    ir = build_typed_ir(parse_source("xy≠yx"), ir_id="ir:ordered", source_ref="inline", source_kind="INLINE_EPHEMERAL_SOURCE", source_root_hash72="root", source_sha256="sha")
    spellings = [x["spelling"] for x in ir["symbol_table"]]
    assert "xy" in spellings and "yx" in spellings
    assert len({x["symbol_id"] for x in ir["symbol_table"] if x["spelling"] in {"xy", "yx"}}) == 2
    assert validate_typed_ir(ir, source_text="xy≠yx")["valid"] is True


def test_unauthorized_ordered_product_equality_is_quarantined():
    source = "xy=yx"
    ir = build_typed_ir(parse_source(source), ir_id="ir:bad-order", source_ref="inline", source_kind="INLINE_EPHEMERAL_SOURCE", source_root_hash72="root", source_sha256="sha")
    validation = validate_typed_ir(ir, source_text=source)
    assert validation["status"] == "QUARANTINED"
    assert "UNAUTHORIZED_ORDERED_PRODUCT_COMMUTATION" in {x["code"] for x in validation["diagnostics"]}


def test_unbalanced_source_is_quarantined():
    result = prepared_runtime(commit_source=False, parse=False).dispatch(req("req:bad", "EXECUTE", "workspace.language.parse", {"source_text": "G := { x=y", "ir_id": "typed-ir:bad"}))
    assert result["status"] == "ADMITTED"
    assert result["result"]["validation"]["status"] == "QUARANTINED"
    assert "UNCLOSED_DELIMITER" in {x["code"] for x in result["result"]["typed_ir"]["diagnostics"]}


def test_tampered_ir_root_is_rejected_by_validation():
    rt = prepared_runtime()
    ir = deepcopy(rt.typed_ir_objects["typed-ir:main"])
    ir["blocks"][0]["node_kind"] = "Tampered"
    validation = validate_typed_ir(ir, source_text=SOURCE)
    assert validation["valid"] is False
    assert "IR_ROOT_MISMATCH" in {x["code"] for x in validation["diagnostics"]}


def test_pass075_registry_extends_one_unified_api():
    registry = operation_registry()
    definitions = {x["operation_id"]: x for x in registry["operations"]}
    assert definitions["workspace.language.parse"]["implemented"] is True
    assert definitions["workspace.language.ir.commit"]["operation_class"] == "MUTATE"
    assert definitions["workspace.tests.accelerate"]["unified_api_only"] is True
    assert definitions["workspace.interpreter.execute"]["implemented"] is False
    assert not any(x["private_authority_path"] for x in registry["operations"])


def test_language_parse_uses_committed_source_lineage():
    rt = prepared_runtime()
    ir = rt.typed_ir_objects["typed-ir:main"]
    assert ir["source_kind"] == "COMMITTED_SOURCE_ARTIFACT"
    assert ir["source_ref"] == "artifact:source:0"
    assert ir["source_root_hash72"] == rt.artifacts["artifact:source:0"]["artifact_root_hash72"]


def test_editor_buffer_parse_is_derived_but_cannot_be_committed_as_ir():
    rt = prepared_runtime(commit_source=False)
    assert rt.typed_ir_objects["typed-ir:main"]["source_kind"] == "EDITOR_BUFFER_PROJECTION"
    response = rt.dispatch(req("req:ir:commit:buffer", "MUTATE", "workspace.language.ir.commit", {"typed_ir_ref": "typed-ir:main", "validation_ref": "validation:typed-ir:main"}, authority=True))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_IR_COMMIT_WITHOUT_COMMITTED_SOURCE_LINEAGE"


def test_ir_commit_requires_authority_and_lease():
    rt = prepared_runtime()
    response = rt.dispatch(req("req:ir:noauth", "MUTATE", "workspace.language.ir.commit", {"typed_ir_ref": "typed-ir:main", "validation_ref": "validation:typed-ir:main"}))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_MUTATION_WITHOUT_AUTHORITY_AND_LEASE"


def test_valid_ir_commit_creates_lineaged_non_authorizing_artifact():
    rt = prepared_runtime()
    response = rt.dispatch(req("req:ir:commit", "MUTATE", "workspace.language.ir.commit", {"typed_ir_ref": "typed-ir:main", "validation_ref": "validation:typed-ir:main", "artifact_id": "artifact:ir:0"}, authority=True))
    assert response["status"] == "ADMITTED"
    artifact = rt.artifacts["artifact:ir:0"]
    assert artifact["source_artifact_ref"] == "artifact:source:0"
    assert artifact["execution_authority"] is False
    assert artifact["compiled_artifact_self_authorizes"] is False


def test_symbol_query_and_ir_query_are_runtime_projections():
    rt = prepared_runtime()
    symbols = rt.dispatch(req("req:symbols", "QUERY", "workspace.language.symbols", {"typed_ir_ref": "typed-ir:main"}))
    ir = rt.dispatch(req("req:ir:get", "QUERY", "workspace.language.ir.get", {"typed_ir_ref": "typed-ir:main"}))
    assert symbols["result"]["symbol_index"]["symbol_count"] >= 8
    assert ir["result"]["typed_ir"]["ir_root_hash72"] == rt.typed_ir_objects["typed-ir:main"]["ir_root_hash72"]


def test_pass075_api_uses_existing_canonical_routes():
    rt = prepared_runtime(parse=False)
    client = TestClient(create_language_workspace_app(rt))
    response = client.post("/api/hhs/v1/execute", json=req("req:api:parse", "EXECUTE", "workspace.language.parse", {"artifact_id": "artifact:source:0", "ir_id": "typed-ir:api"}))
    assert response.status_code == 200
    assert response.json()["status"] == "ADMITTED"
    assert "typed-ir:api" in rt.typed_ir_objects


def test_snapshot_round_trip_preserves_language_state():
    rt = aligned_runtime()
    snapshot = rt.snapshot()
    restored = HHSNativeLanguageWorkspaceRuntime(initial_state=snapshot)
    assert restored.snapshot() == snapshot


def test_snapshot_tampering_is_rejected():
    snapshot = prepared_runtime().snapshot()
    snapshot["typed_ir_objects"]["typed-ir:main"]["ir_id"] = "tampered"
    with pytest.raises(ContractError, match="REJECT_PASS075_WORKSPACE_STATE_ROOT_MISMATCH"):
        HHSNativeLanguageWorkspaceRuntime(initial_state=snapshot)


def test_test_acceleration_requires_aligned_proposal():
    rt = prepared_runtime()
    response = rt.dispatch(req("req:tests:no-proposal", "EXECUTE", "workspace.tests.accelerate", {"proposal_ref": "missing", "typed_ir_ref": "typed-ir:main", "coordinating_agent_refs": ["agent:llm:builder"]}))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_TEST_ACCELERATION_PROPOSAL_NOT_FOUND"


def test_test_acceleration_rejects_unregistered_agents():
    rt = aligned_runtime()
    response = rt.dispatch(req("req:tests:bad-agent", "EXECUTE", "workspace.tests.accelerate", {
        "proposal_ref": "proposal:language", "typed_ir_ref": "typed-ir:main",
        "alignment_decision_ref": "proposal-alignment:proposal:language",
        "coordinating_agent_refs": ["agent:missing"],
    }))
    assert response["status"] == "REJECTED"
    assert "REJECT_TEST_ACCELERATION_AGENT_NOT_REGISTERED" in response["diagnostics"][0]["code"]


def test_agent_coordinated_test_plan_is_deterministic_and_non_authorizing():
    def build():
        rt = aligned_runtime()
        response = rt.dispatch(req("req:tests", "EXECUTE", "workspace.tests.accelerate", {
            "proposal_ref": "proposal:language", "typed_ir_ref": "typed-ir:main",
            "alignment_decision_ref": "proposal-alignment:proposal:language",
            "coordinating_agent_refs": ["agent:llm:builder", "agent:human:reviewer"],
            "plan_id": "test-plan:language",
        }))
        assert response["status"] == "ADMITTED"
        return response["result"]["test_acceleration_plan"]
    left, right = build(), build()
    assert left == right
    assert left["test_execution_performed"] is False
    assert left["agent_recommendation_is_not_test_evidence"] is True
    assert left["test_plan_confers_no_mutation_authority"] is True
    assert {x["assigned_agent_ref"] for x in left["parallel_shards"]} == {"agent:human:reviewer", "agent:llm:builder"}


def test_test_catalog_is_repository_relative_and_rooted():
    catalog = build_test_catalog()
    assert catalog["catalog_is_repository_relative"] is True
    assert all(not x["path"].startswith("/") for x in catalog["tests"])
    assert len(catalog["catalog_root_hash72"]) == 72


def test_foundation_directed_ir_commit_is_rejected():
    rt = prepared_runtime()
    response = rt.dispatch(req("req:foundation", "MUTATE", "workspace.language.ir.commit", {
        "typed_ir_ref": "typed-ir:main", "validation_ref": "validation:typed-ir:main",
        "target_scope": "PASS_072_FOUNDATION",
    }, authority=True))
    assert response["status"] == "REJECTED"
    assert response["diagnostics"][0]["code"] == "REJECT_FOUNDATION_MUTATION_REQUIRES_REVERSIBLE_ALIGNMENT_PATCH"


def test_release_bundle_is_native_product_and_not_interpreter_execution():
    bundle = build_pass075_release_bundle()
    assert bundle["platform_dependency"]["total_system_root_hash72"] == FROZEN_PASS072_SYSTEM_ROOT_HASH72
    assert bundle["platform_dependency"]["foundation_modified"] is False
    assert bundle["workspace_dependency"]["parent_files_modified"] is False
    assert bundle["interpreter_execution_available"] is False
    assert bundle["new_orphan_modules"] == 0
    assert len(bundle["product_root_hash72"]) == 72


def test_demo_closes_typed_ir_validation_and_test_plan():
    snapshot = build_pass075_demo()["snapshot"]
    assert snapshot["language_validations"]["validation:typed-ir:pass075:main"]["valid"] is True
    assert snapshot["test_acceleration_plans"]["test-plan:pass075:language"]["parallel_shards"]
    assert snapshot["interpreter_execution_available"] is False


def _capsule(tmp_path: Path):
    demo = build_pass075_demo()
    source_paths = [
        "native_projects/hhs_harmonicode_language/hhs_pass075_contracts_v1.py",
        "native_projects/hhs_harmonicode_language/hhs_harmonicode_parser_v1.py",
        "native_projects/hhs_harmonicode_language/hhs_typed_ir_v1.py",
        "native_projects/hhs_harmonicode_language/hhs_harmonicode_language_service_v1.py",
        "native_projects/hhs_harmonicode_language/hhs_agent_test_acceleration_v1.py",
        "native_projects/hhs_harmonicode_language/hhs_pass075_workspace_runtime_v1.py",
    ]
    repo = Path(__file__).resolve().parents[1]
    bindings = []
    for rel in source_paths:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / rel, target)
        bindings.append({"relative_path": rel, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    snapshot = demo["snapshot"]
    ir = snapshot["typed_ir_objects"]["typed-ir:pass075:main"]
    plan = snapshot["test_acceleration_plans"]["test-plan:pass075:language"]
    capsule = {
        "schema": LANGUAGE_REPLAY_CAPSULE_SCHEMA,
        "thread_context_required": False,
        "llm_context_window_required": False,
        "host_path_required": False,
        "repository_state_authoritative": True,
        "source_bindings": bindings,
        "workspace_state": snapshot,
        "expected_workspace_state_root_hash72": snapshot["workspace_state_root_hash72"],
        "expected_typed_ir_ref": "typed-ir:pass075:main",
        "expected_typed_ir_root_hash72": ir["ir_root_hash72"],
        "expected_test_plan_ref": "test-plan:pass075:language",
        "expected_test_plan_root_hash72": plan["test_plan_root_hash72"],
    }
    capsule["capsule_root_hash72"] = product_root("pass075_language_replay_capsule", capsule)
    return capsule


def test_context_independent_replay_uses_repository_state_not_llm_context(tmp_path):
    capsule = _capsule(tmp_path)
    verification = verify_capsule(tmp_path, capsule)
    receipt = replay_language_workspace(tmp_path, capsule)
    assert verification["ok"] is True
    assert receipt["ok"] is True
    assert receipt["thread_context_used"] is False
    assert receipt["llm_context_window_used"] is False
    assert receipt["host_path_used_as_identity"] is False


def test_replay_rejects_source_binding_tampering(tmp_path):
    capsule = _capsule(tmp_path)
    path = tmp_path / capsule["source_bindings"][0]["relative_path"]
    path.write_text(path.read_text(encoding="utf-8") + "\n# tampered\n", encoding="utf-8")
    with pytest.raises(Pass075ReplayError, match="REJECT_SOURCE_BINDING_DIGEST_MISMATCH"):
        verify_capsule(tmp_path, capsule)


def test_replay_capsule_root_tampering_is_rejected(tmp_path):
    capsule = _capsule(tmp_path)
    capsule["expected_typed_ir_root_hash72"] = "tampered"
    with pytest.raises(Pass075ReplayError, match="REJECT_PASS075_REPLAY_CAPSULE_ROOT_MISMATCH"):
        verify_capsule(tmp_path, capsule)
