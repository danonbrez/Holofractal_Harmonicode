"""Pass 075 extension of the Pass 074 unified HHS workspace runtime."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Mapping, Optional
import json

from native_projects.hhs_ide_workspace.hhs_native_workspace_project_v1 import (
    HHSNativeWorkspaceRuntime,
    operation_registry as pass074_operation_registry,
)
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    ContractError,
    product_root,
    stable,
)

from .hhs_agent_test_acceleration_v1 import build_test_acceleration_plan, test_catalog
from .hhs_harmonicode_language_service_v1 import HarmonicodeLanguageService
from .hhs_pass075_contracts_v1 import (
    LANGUAGE_REPLAY_CAPSULE_SCHEMA,
    PASS_ID,
    PARENT_NATIVE_PASS,
    TYPED_IR_ARTIFACT_SCHEMA,
    VERSION,
)

BASE_STATE_ATTRS = (
    "projects", "sessions", "buffers", "artifacts", "receipts", "agents",
    "proposals", "alignment_decisions", "test_records", "handoffs", "healing_plans",
)


def operation_registry() -> Dict[str, Any]:
    registry = deepcopy(pass074_operation_registry())
    registry.pop("operation_registry_root_hash72", None)
    registry["version"] = VERSION
    registry["parent_operation_registry_root_hash72"] = pass074_operation_registry()["operation_registry_root_hash72"]
    registry["operations"].extend([
        {
            "operation_id": "workspace.language.parse",
            "operation_class": "EXECUTE",
            "description": "Parse Harmonicode source into a span-preserving derived language document and HHS_TYPED_IR_V1",
            "implemented": True,
            "unified_api_only": True,
            "private_authority_path": False,
        },
        {
            "operation_id": "workspace.language.validate",
            "operation_class": "EXECUTE",
            "description": "Validate HHS_TYPED_IR_V1 identity, spans, types, effects, lineage, and invariant bindings",
            "implemented": True,
            "unified_api_only": True,
            "private_authority_path": False,
        },
        {
            "operation_id": "workspace.language.symbols",
            "operation_class": "QUERY",
            "description": "Project the typed symbol index for an IR object",
            "implemented": True,
            "unified_api_only": True,
            "private_authority_path": False,
        },
        {
            "operation_id": "workspace.language.ir.get",
            "operation_class": "QUERY",
            "description": "Read a derived HHS_TYPED_IR_V1 object",
            "implemented": True,
            "unified_api_only": True,
            "private_authority_path": False,
        },
        {
            "operation_id": "workspace.language.ir.commit",
            "operation_class": "MUTATE",
            "description": "Commit validated typed IR with committed-source lineage under authority and lease",
            "implemented": True,
            "unified_api_only": True,
            "private_authority_path": False,
        },
        {
            "operation_id": "workspace.tests.accelerate",
            "operation_class": "EXECUTE",
            "description": "Build an aligned agent-coordinated deterministic test selection and sharding plan",
            "implemented": True,
            "unified_api_only": True,
            "private_authority_path": False,
        },
    ])
    registry["operation_registry_root_hash72"] = product_root("pass075_operation_registry", registry)
    return stable(registry)


class HHSNativeLanguageWorkspaceRuntime(HHSNativeWorkspaceRuntime):
    def __init__(self, *, initial_state: Optional[Mapping[str, Any]] = None) -> None:
        super().__init__(initial_state=None)
        self.registry = operation_registry()
        self.language_service = HarmonicodeLanguageService()
        self.language_documents: Dict[str, Dict[str, Any]] = {}
        self.typed_ir_objects: Dict[str, Dict[str, Any]] = {}
        self.language_validations: Dict[str, Dict[str, Any]] = {}
        self.test_acceleration_plans: Dict[str, Dict[str, Any]] = {}
        if initial_state:
            self._restore_pass075(initial_state)

    def _state_payload(self) -> Dict[str, Any]:
        payload = super()._state_payload()
        payload.update({
            "schema": "HHS_NATIVE_LANGUAGE_WORKSPACE_RUNTIME_STATE_V1",
            "version": VERSION,
            "pass_id": PASS_ID,
            "parent_native_pass": PARENT_NATIVE_PASS,
            "language_documents": stable(self.language_documents),
            "typed_ir_objects": stable(self.typed_ir_objects),
            "language_validations": stable(self.language_validations),
            "test_acceleration_plans": stable(self.test_acceleration_plans),
            "test_catalog_root_hash72": test_catalog()["catalog_root_hash72"],
            "interpreter_execution_available": False,
            "compiler_execution_available": False,
            "emulator_execution_available": False,
        })
        return payload

    def snapshot(self) -> Dict[str, Any]:
        payload = self._state_payload()
        payload["workspace_state_root_hash72"] = product_root("pass075_language_workspace_state", payload)
        return stable(payload)

    def _restore_pass075(self, state: Mapping[str, Any]) -> None:
        supplied = deepcopy(dict(state))
        expected = str(supplied.pop("workspace_state_root_hash72", ""))
        if expected != product_root("pass075_language_workspace_state", supplied):
            raise ContractError("REJECT_PASS075_WORKSPACE_STATE_ROOT_MISMATCH")
        if supplied.get("pass_id") != PASS_ID:
            raise ContractError("REJECT_PASS075_STATE_ID_MISMATCH")
        if supplied.get("frozen_platform_root_hash72") != FROZEN_PASS072_SYSTEM_ROOT_HASH72:
            raise ContractError("REJECT_FROZEN_PLATFORM_ROOT_MISMATCH")
        if supplied.get("operation_registry_root_hash72") != self.registry["operation_registry_root_hash72"]:
            raise ContractError("REJECT_PASS075_OPERATION_REGISTRY_ROOT_MISMATCH")
        self.sequence = int(supplied.get("sequence", 0))
        for attr in BASE_STATE_ATTRS:
            setattr(self, attr, deepcopy(supplied.get(attr, {})))
        self.events = deepcopy(supplied.get("events", []))
        for attr in ("language_documents", "typed_ir_objects", "language_validations", "test_acceleration_plans"):
            setattr(self, attr, deepcopy(supplied.get(attr, {})))

    def _resolve_source(self, request: Mapping[str, Any]):
        payload = request["payload"]
        artifact_id = str(payload.get("artifact_id") or "")
        buffer_id = str(payload.get("buffer_id") or "")
        if artifact_id:
            artifact = self.artifacts.get(artifact_id)
            if not artifact:
                raise ContractError("REJECT_LANGUAGE_SOURCE_ARTIFACT_NOT_FOUND")
            return str(artifact.get("content") or ""), artifact_id, "COMMITTED_SOURCE_ARTIFACT", str(artifact.get("artifact_root_hash72") or "")
        if buffer_id:
            buffer = self.buffers.get(buffer_id)
            if not buffer:
                raise ContractError("REJECT_LANGUAGE_SOURCE_BUFFER_NOT_FOUND")
            return str(buffer.get("text") or ""), buffer_id, "EDITOR_BUFFER_PROJECTION", str(buffer.get("buffer_root_hash72") or "")
        if "source_text" in payload:
            text = str(payload.get("source_text") or "")
            return text, f"inline:{request['request_id']}", "INLINE_EPHEMERAL_SOURCE", product_root("pass075_inline_source", {"text": text})
        raise ContractError("REJECT_LANGUAGE_SOURCE_NOT_SPECIFIED")

    def _op_workspace_language_parse(self, request: Mapping[str, Any]):
        self._require_project(request["project_id"])
        source, source_ref, source_kind, source_root = self._resolve_source(request)
        document_id = str(request["payload"].get("document_id") or f"language-doc:{request['request_id']}")
        ir_id = str(request["payload"].get("ir_id") or f"typed-ir:{request['request_id']}")
        parsed = self.language_service.parse(
            source,
            document_id=document_id,
            ir_id=ir_id,
            source_ref=source_ref,
            source_kind=source_kind,
            source_root_hash72=source_root,
            parent_ir_ref=str(request["payload"].get("parent_ir_ref") or ""),
        )
        self.language_documents[document_id] = parsed["document"]
        self.typed_ir_objects[ir_id] = parsed["typed_ir"]
        validation_id = f"validation:{ir_id}"
        validation = {**parsed["validation"], "validation_id": validation_id}
        self.language_validations[validation_id] = stable(validation)
        for ref in (document_id, ir_id, validation_id):
            self._append_project_object(request["project_id"], ref)
        return {
            "document": parsed["document"],
            "typed_ir": parsed["typed_ir"],
            "validation": validation,
            "derived_projection_not_canonical_source": True,
            "execution_attempted": False,
        }, [document_id, ir_id, validation_id, source_ref], []

    def _op_workspace_language_validate(self, request: Mapping[str, Any]):
        ir_id = str(request["payload"].get("typed_ir_ref") or "")
        ir = self.typed_ir_objects.get(ir_id)
        if not ir:
            raise ContractError("REJECT_TYPED_IR_NOT_FOUND")
        document = next((x for x in self.language_documents.values() if x.get("source_ref") == ir.get("source_ref")), None)
        source_text = str(document.get("normalized_source") if document else "")
        validation = self.language_service.validate(ir, source_text=source_text)
        validation_id = str(request["payload"].get("validation_id") or f"validation:{ir_id}:{request['request_id']}")
        validation = {**validation, "validation_id": validation_id}
        self.language_validations[validation_id] = stable(validation)
        self._append_project_object(request["project_id"], validation_id)
        return {"validation": validation}, [ir_id, validation_id], []

    def _op_workspace_language_symbols(self, request: Mapping[str, Any]):
        ir_id = str(request["payload"].get("typed_ir_ref") or "")
        ir = self.typed_ir_objects.get(ir_id)
        if not ir:
            raise ContractError("REJECT_TYPED_IR_NOT_FOUND")
        return {"symbol_index": self.language_service.symbols(ir)}, [ir_id], []

    def _op_workspace_language_ir_get(self, request: Mapping[str, Any]):
        ir_id = str(request["payload"].get("typed_ir_ref") or "")
        ir = self.typed_ir_objects.get(ir_id)
        if not ir:
            raise ContractError("REJECT_TYPED_IR_NOT_FOUND")
        return {"typed_ir": deepcopy(ir)}, [ir_id], []

    def _op_workspace_language_ir_commit(self, request: Mapping[str, Any]):
        ir_id = str(request["payload"].get("typed_ir_ref") or "")
        ir = self.typed_ir_objects.get(ir_id)
        if not ir:
            raise ContractError("REJECT_TYPED_IR_NOT_FOUND")
        if ir.get("source_kind") != "COMMITTED_SOURCE_ARTIFACT" or ir.get("source_ref") not in self.artifacts:
            raise ContractError("REJECT_IR_COMMIT_WITHOUT_COMMITTED_SOURCE_LINEAGE")
        validation_ref = str(request["payload"].get("validation_ref") or f"validation:{ir_id}")
        validation = self.language_validations.get(validation_ref)
        if not validation or not validation.get("valid"):
            raise ContractError("REJECT_IR_COMMIT_WITHOUT_VALID_VALIDATION")
        artifact_id = str(request["payload"].get("artifact_id") or f"artifact:typed-ir:{ir_id}")
        artifact = {
            "schema": TYPED_IR_ARTIFACT_SCHEMA,
            "artifact_id": artifact_id,
            "project_id": request["project_id"],
            "typed_ir_ref": ir_id,
            "typed_ir_root_hash72": ir["ir_root_hash72"],
            "source_artifact_ref": ir["source_ref"],
            "source_artifact_root_hash72": ir["source_root_hash72"],
            "validation_ref": validation_ref,
            "validation_root_hash72": validation["validation_root_hash72"],
            "content": deepcopy(ir),
            "execution_authority": False,
            "compiled_artifact_self_authorizes": False,
        }
        artifact["artifact_root_hash72"] = product_root("pass075_typed_ir_artifact", artifact)
        self.artifacts[artifact_id] = stable(artifact)
        project = self._require_project(request["project_id"])
        if artifact_id not in project["artifact_ids"]:
            project["artifact_ids"].append(artifact_id)
        return {"typed_ir_artifact": artifact}, [ir_id, validation_ref], [artifact_id]

    def _op_workspace_tests_accelerate(self, request: Mapping[str, Any]):
        proposal_ref = str(request["payload"].get("proposal_ref") or "")
        ir_ref = str(request["payload"].get("typed_ir_ref") or "")
        proposal = self.proposals.get(proposal_ref)
        ir = self.typed_ir_objects.get(ir_ref)
        if not proposal:
            raise ContractError("REJECT_TEST_ACCELERATION_PROPOSAL_NOT_FOUND")
        if not ir:
            raise ContractError("REJECT_TEST_ACCELERATION_IR_NOT_FOUND")
        decision_ref = str(request["payload"].get("alignment_decision_ref") or f"proposal-alignment:{proposal_ref}")
        decision = self.alignment_decisions.get(decision_ref)
        if not decision:
            raise ContractError("REJECT_TEST_ACCELERATION_ALIGNMENT_NOT_FOUND")
        agent_refs = [str(x) for x in request["payload"].get("coordinating_agent_refs", [])]
        agents = []
        for ref in agent_refs:
            agent = self.agents.get(ref)
            if not agent:
                raise ContractError(f"REJECT_TEST_ACCELERATION_AGENT_NOT_REGISTERED:{ref}")
            agents.append(agent)
        plan_id = str(request["payload"].get("plan_id") or f"test-plan:{request['request_id']}")
        plan = build_test_acceleration_plan(
            plan_id=plan_id,
            project_id=request["project_id"],
            proposal=proposal,
            typed_ir=ir,
            coordinating_agents=agents,
            alignment_decision=decision,
            requested_tests=request["payload"].get("requested_tests", []),
        )
        self.test_acceleration_plans[plan_id] = plan
        self._append_project_object(request["project_id"], plan_id)
        return {"test_acceleration_plan": plan}, [plan_id, proposal_ref, ir_ref, decision_ref, *agent_refs], []


def build_pass075_demo(runtime: Optional[HHSNativeLanguageWorkspaceRuntime] = None) -> Dict[str, Any]:
    from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import make_request

    rt = runtime or HHSNativeLanguageWorkspaceRuntime()
    project_id = "project:pass075-demo"
    session_id = "session:pass075-demo"
    authority = {
        "role_contract_ref": "role:workspace-language-developer",
        "task_assignment_ref": "task:pass075-language-service",
        "capability_lease_ref": "lease:pass075-language-service",
    }
    source = """PHASE_GATE := {
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
    requests = [
        make_request(request_id="req:075:project", project_id=project_id, session_id=session_id, operation_class="INGRESS", operation_id="workspace.project.create", payload={"name": "Pass 075 Harmonicode Language Workspace"}),
        make_request(request_id="req:075:session", project_id=project_id, session_id=session_id, operation_class="INGRESS", operation_id="workspace.session.open", client_surface="REPLAY"),
        make_request(request_id="req:075:agent:human", project_id=project_id, session_id=session_id, operation_class="INGRESS", operation_id="workspace.agent.register", payload={"agent_id": "agent:human:language-reviewer", "agent_kind": "HUMAN", "capabilities": ["language.review", "test.review"]}),
        make_request(request_id="req:075:agent:llm", project_id=project_id, session_id=session_id, operation_class="INGRESS", operation_id="workspace.agent.register", payload={"agent_id": "agent:llm:language-builder", "agent_kind": "LLM", "capabilities": ["language.parse", "test.plan"]}),
        make_request(request_id="req:075:buffer", project_id=project_id, session_id=session_id, operation_class="INGRESS", operation_id="workspace.buffer.open", payload={"buffer_id": "buffer:pass075:main", "name": "main.hhs", "text": source}),
        make_request(request_id="req:075:source:commit", project_id=project_id, session_id=session_id, operation_class="MUTATE", operation_id="workspace.source.commit", payload={"buffer_id": "buffer:pass075:main", "artifact_id": "artifact:pass075:source:0"}, **authority),
        make_request(request_id="req:075:parse", project_id=project_id, session_id=session_id, operation_class="EXECUTE", operation_id="workspace.language.parse", payload={"artifact_id": "artifact:pass075:source:0", "document_id": "language-doc:pass075:main", "ir_id": "typed-ir:pass075:main"}),
        make_request(request_id="req:075:ir:commit", project_id=project_id, session_id=session_id, operation_class="MUTATE", operation_id="workspace.language.ir.commit", payload={"typed_ir_ref": "typed-ir:pass075:main", "validation_ref": "validation:typed-ir:pass075:main", "artifact_id": "artifact:pass075:typed-ir:0"}, **authority),
        make_request(request_id="req:075:proposal", project_id=project_id, session_id=session_id, operation_class="INGRESS", operation_id="workspace.change.propose", payload={
            "proposal_id": "proposal:pass075:language",
            "program_id": "program:hhs-harmonicode-language-service",
            "proposer_agent_ref": "agent:llm:language-builder",
            "summary": "Add a reusable typed Harmonicode language service",
            "new_capability_statement": "Parse committed Harmonicode source into span-preserving HHS_TYPED_IR_V1 and coordinate deterministic tests",
            "reusable_capabilities": ["harmonicode.parse", "typed-ir.validate", "tests.accelerate"],
            "reachable_entrypoint": "workspace.language.parse",
            "affected_product_paths": ["native_projects/hhs_harmonicode_language"],
            "requested_tests": ["tests/test_hhs_pass075_harmonicode_language_service_v1.py"],
        }),
        make_request(request_id="req:075:alignment", project_id=project_id, session_id=session_id, operation_class="EXECUTE", operation_id="workspace.alignment.evaluate", payload={"proposal_ref": "proposal:pass075:language"}),
        make_request(request_id="req:075:tests", project_id=project_id, session_id=session_id, operation_class="EXECUTE", operation_id="workspace.tests.accelerate", payload={
            "proposal_ref": "proposal:pass075:language",
            "typed_ir_ref": "typed-ir:pass075:main",
            "alignment_decision_ref": "proposal-alignment:proposal:pass075:language",
            "coordinating_agent_refs": ["agent:human:language-reviewer", "agent:llm:language-builder"],
            "plan_id": "test-plan:pass075:language",
        }),
    ]
    responses = [rt.dispatch(request) for request in requests]
    return {"runtime": rt, "requests": requests, "responses": responses, "snapshot": rt.snapshot()}


def build_pass075_release_bundle() -> Dict[str, Any]:
    demo = build_pass075_demo()
    snapshot = demo["snapshot"]
    registry = operation_registry()
    ir = snapshot["typed_ir_objects"]["typed-ir:pass075:main"]
    validation = snapshot["language_validations"]["validation:typed-ir:pass075:main"]
    plan = snapshot["test_acceleration_plans"]["test-plan:pass075:language"]
    body = {
        "schema": "HHS_PASS_075_HARMONICODE_LANGUAGE_RELEASE_BUNDLE_V1",
        "pass_id": PASS_ID,
        "version": VERSION,
        "parent_native_pass": PARENT_NATIVE_PASS,
        "platform_dependency": {"pass_id": "PASS_072", "total_system_root_hash72": FROZEN_PASS072_SYSTEM_ROOT_HASH72, "foundation_modified": False},
        "workspace_dependency": {"pass_id": "PASS_074", "parent_files_modified": False},
        "operation_registry": registry,
        "typed_ir_root_hash72": ir["ir_root_hash72"],
        "validation_root_hash72": validation["validation_root_hash72"],
        "test_plan_root_hash72": plan["test_plan_root_hash72"],
        "workspace_state": snapshot,
        "test_catalog": test_catalog(),
        "interpreter_execution_available": False,
        "compiler_execution_available": False,
        "emulator_execution_available": False,
        "new_orphan_modules": 0,
        "thread_context_required": False,
        "llm_context_window_required": False,
        "host_path_required": False,
    }
    body["product_root_hash72"] = product_root("pass075_release_bundle", body)
    return stable(body)


def write_release_artifacts(root: Optional[str | Path] = None) -> Dict[str, Any]:
    repo = Path(root).resolve() if root else Path(__file__).resolve().parents[2]
    out = repo / "native_projects/hhs_harmonicode_language/artifacts"
    out.mkdir(parents=True, exist_ok=True)
    bundle = build_pass075_release_bundle()
    artifacts = {
        "HHS_PASS_075_HARMONICODE_LANGUAGE_RELEASE_BUNDLE.json": bundle,
        "PASS_075_LANGUAGE_WORKSPACE_STATE.json": bundle["workspace_state"],
        "PASS_075_TYPED_IR.json": bundle["workspace_state"]["typed_ir_objects"]["typed-ir:pass075:main"],
        "PASS_075_TYPED_IR_VALIDATION.json": bundle["workspace_state"]["language_validations"]["validation:typed-ir:pass075:main"],
        "PASS_075_TEST_ACCELERATION_PLAN.json": bundle["workspace_state"]["test_acceleration_plans"]["test-plan:pass075:language"],
        "PASS_075_TEST_CAPABILITY_CATALOG.json": bundle["test_catalog"],
        "PASS_075_API_OPERATION_REGISTRY.json": bundle["operation_registry"],
    }
    for name, value in artifacts.items():
        (out / name).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return bundle


if __name__ == "__main__":
    print(json.dumps(write_release_artifacts(), indent=2, sort_keys=True, ensure_ascii=False))
