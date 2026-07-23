"""Pass 074 unified native HHS workspace program.

The workspace owns product projections and product-local state. Pass 072
remains the frozen platform foundation. Every client and every development
agent invokes one dispatcher through one canonical request envelope.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional
import json

from .hhs_development_network_protocol_v1 import (
    ALIGNMENT_DECISION_SCHEMA,
    AGENT_SCHEMA,
    CHANGE_PROPOSAL_SCHEMA,
    HANDOFF_SCHEMA,
    HEALING_PLAN_SCHEMA,
    TEST_RECORD_SCHEMA,
    build_bounded_healing_plan,
    build_handoff_capsule,
    canonical_agent,
    canonical_change_proposal,
    canonical_test_record,
    development_protocol_contract,
    evaluate_proposal_alignment,
)
from .hhs_workspace_contracts_v1 import (
    BUFFER_SCHEMA,
    EVENT_SCHEMA,
    FROZEN_PASS072_SYSTEM_ROOT_HASH72,
    OBJECT_INDEX_SCHEMA,
    OPERATION_REGISTRY_SCHEMA,
    PASS_ID,
    PROJECT_SCHEMA,
    SESSION_SCHEMA,
    VERSION,
    ContractError,
    canonical_request,
    product_root,
    response_envelope,
    stable,
)

AUTHORITY_REQUIRED = {"MUTATE", "COMPILE", "EMULATE"}


def operation_registry() -> Dict[str, Any]:
    operations = [
        ("workspace.project.create", "INGRESS", "Create or resolve a native workspace project", True),
        ("workspace.session.open", "INGRESS", "Open a project-scoped workspace session", True),
        ("workspace.buffer.open", "INGRESS", "Create a presentation-only editor buffer", True),
        ("workspace.agent.register", "INGRESS", "Register a non-authorizing human, LLM, tool, or CI agent identity", True),
        ("workspace.change.propose", "INGRESS", "Submit a repository-native capability-bearing change proposal", True),
        ("workspace.state.get", "QUERY", "Read canonical product runtime state", True),
        ("workspace.project.index", "QUERY", "Read the project object index", True),
        ("workspace.buffer.update", "MUTATE", "Mutate an editor projection under authority and alignment", True),
        ("workspace.source.commit", "MUTATE", "Commit a buffer as a source artifact", True),
        ("workspace.test.record", "MUTATE", "Attach witnessed test evidence to a change proposal", True),
        ("workspace.handoff.create", "MUTATE", "Create a context-independent agent handoff capsule", True),
        ("workspace.source.inspect", "EXECUTE", "Run bounded source inspection", True),
        ("workspace.alignment.evaluate", "EXECUTE", "Evaluate post-freeze reciprocal development constraints", True),
        ("workspace.healing.plan", "EXECUTE", "Create a bounded product-local self-healing plan", True),
        ("workspace.interpreter.execute", "EXECUTE", "Reserved Pass 076 interpreter surface", False),
        ("workspace.compiler.compile", "COMPILE", "Reserved Pass 077 compiler surface", False),
        ("workspace.emulator.run", "EMULATE", "Reserved Pass 078 emulator surface", False),
    ]
    payload = {
        "schema": OPERATION_REGISTRY_SCHEMA,
        "version": VERSION,
        "operations": [
            {
                "operation_id": op,
                "operation_class": cls,
                "description": desc,
                "implemented": implemented,
                "unified_api_only": True,
                "private_authority_path": False,
            }
            for op, cls, desc, implemented in operations
        ],
    }
    payload["operation_registry_root_hash72"] = product_root("pass074_operation_registry", payload)
    return stable(payload)


class HHSNativeWorkspaceRuntime:
    def __init__(self, *, initial_state: Optional[Mapping[str, Any]] = None) -> None:
        self.registry = operation_registry()
        self.development_protocol = development_protocol_contract()
        self.sequence = 0
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.buffers: Dict[str, Dict[str, Any]] = {}
        self.artifacts: Dict[str, Dict[str, Any]] = {}
        self.receipts: Dict[str, Dict[str, Any]] = {}
        self.events: list[Dict[str, Any]] = []
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.proposals: Dict[str, Dict[str, Any]] = {}
        self.alignment_decisions: Dict[str, Dict[str, Any]] = {}
        self.test_records: Dict[str, Dict[str, Any]] = {}
        self.handoffs: Dict[str, Dict[str, Any]] = {}
        self.healing_plans: Dict[str, Dict[str, Any]] = {}
        if initial_state:
            self._restore(initial_state)

    @staticmethod
    def _authority_ok(request: Mapping[str, Any]) -> bool:
        return all(
            str(request.get(x) or "")
            for x in ("role_contract_ref", "task_assignment_ref", "capability_lease_ref")
        )

    def _next(self) -> int:
        self.sequence += 1
        return self.sequence

    def _state_payload(self) -> Dict[str, Any]:
        return {
            "schema": "HHS_NATIVE_WORKSPACE_RUNTIME_STATE_V1",
            "version": VERSION,
            "pass_id": PASS_ID,
            "frozen_platform_root_hash72": FROZEN_PASS072_SYSTEM_ROOT_HASH72,
            "development_protocol_root_hash72": self.development_protocol[
                "development_protocol_root_hash72"
            ],
            "sequence": self.sequence,
            "projects": stable(self.projects),
            "sessions": stable(self.sessions),
            "buffers": stable(self.buffers),
            "artifacts": stable(self.artifacts),
            "receipts": stable(self.receipts),
            "events": stable(self.events),
            "agents": stable(self.agents),
            "proposals": stable(self.proposals),
            "alignment_decisions": stable(self.alignment_decisions),
            "test_records": stable(self.test_records),
            "handoffs": stable(self.handoffs),
            "healing_plans": stable(self.healing_plans),
            "operation_registry_root_hash72": self.registry["operation_registry_root_hash72"],
            "workspace_state_is_product_state_not_platform_state": True,
            "repository_state_authoritative_over_conversation_state": True,
        }

    def snapshot(self) -> Dict[str, Any]:
        payload = self._state_payload()
        payload["workspace_state_root_hash72"] = product_root("pass074_workspace_state", payload)
        return stable(payload)

    def _restore(self, state: Mapping[str, Any]) -> None:
        supplied = dict(state)
        expected = supplied.pop("workspace_state_root_hash72", "")
        observed = product_root("pass074_workspace_state", supplied)
        if expected != observed:
            raise ContractError("REJECT_WORKSPACE_STATE_ROOT_MISMATCH")
        if supplied.get("frozen_platform_root_hash72") != FROZEN_PASS072_SYSTEM_ROOT_HASH72:
            raise ContractError("REJECT_FROZEN_PLATFORM_ROOT_MISMATCH")
        if supplied.get("development_protocol_root_hash72") != self.development_protocol[
            "development_protocol_root_hash72"
        ]:
            raise ContractError("REJECT_DEVELOPMENT_PROTOCOL_ROOT_MISMATCH")
        self.sequence = int(supplied.get("sequence", 0))
        for attr in (
            "projects",
            "sessions",
            "buffers",
            "artifacts",
            "receipts",
            "agents",
            "proposals",
            "alignment_decisions",
            "test_records",
            "handoffs",
            "healing_plans",
        ):
            setattr(self, attr, deepcopy(supplied.get(attr, {})))
        self.events = deepcopy(supplied.get("events", []))

    def _event(self, request: Mapping[str, Any], status: str, refs: Iterable[str]) -> Dict[str, Any]:
        sequence = self._next()
        body = {
            "schema": EVENT_SCHEMA,
            "sequence": sequence,
            "request_id": request["request_id"],
            "project_id": request["project_id"],
            "session_id": request["session_id"],
            "operation_class": request["operation_class"],
            "operation_id": request["payload"].get("operation_id"),
            "status": status,
            "object_refs": list(refs),
            "previous_event_root_hash72": self.events[-1]["event_root_hash72"] if self.events else "GENESIS",
        }
        body["event_root_hash72"] = product_root("pass074_runtime_event", body)
        self.events.append(stable(body))
        return body

    def _receipt(self, request: Mapping[str, Any], status: str, result: Mapping[str, Any]) -> Dict[str, Any]:
        receipt_id = f"receipt:{request['request_id']}"
        body = {
            "schema": "HHS_WORKSPACE_OPERATION_RECEIPT_V1",
            "receipt_id": receipt_id,
            "request_id": request["request_id"],
            "project_id": request["project_id"],
            "operation_id": request["payload"].get("operation_id"),
            "operation_class": request["operation_class"],
            "status": status,
            "request_root_hash72": request["request_root_hash72"],
            "result_commitment_root_hash72": product_root("pass074_receipt_result", result),
            "alignment_decision_ref": str(result.get("alignment_decision_ref") or ""),
            "console_output_is_not_receipt": True,
        }
        body["receipt_root_hash72"] = product_root("pass074_operation_receipt", body)
        self.receipts[receipt_id] = stable(body)
        return body

    def _reject(
        self,
        request: Mapping[str, Any],
        code: str,
        *,
        unavailable: bool = False,
        extra_refs: Iterable[str] = (),
        result_extra: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        status = "UNAVAILABLE" if unavailable else "REJECTED"
        result = {"ok": False, "code": code, **dict(result_extra or {})}
        receipt = self._receipt(request, status, result)
        refs = [*extra_refs, receipt["receipt_id"]]
        event = self._event(request, status, refs)
        return response_envelope(
            request,
            status=status,
            receipt_refs=[receipt["receipt_id"]],
            diagnostics=[{"code": code, "severity": "ERROR"}],
            runtime_state_ref=self.snapshot()["workspace_state_root_hash72"],
            result={**result, "event_root_hash72": event["event_root_hash72"]},
        )

    def _effect_alignment_decision(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        payload = request["payload"]
        foundation_change = bool(payload.get("foundation_change_requested")) or str(
            payload.get("target_scope") or "NATIVE_PRODUCT"
        ) == "PASS_072_FOUNDATION"
        decision_id = f"alignment:{request['request_id']}"
        admitted = not foundation_change
        body = {
            "schema": ALIGNMENT_DECISION_SCHEMA,
            "alignment_decision_id": decision_id,
            "request_id": request["request_id"],
            "project_id": request["project_id"],
            "operation_id": payload.get("operation_id"),
            "decision": "ADMIT_PRODUCT_LOCAL_EFFECT" if admitted else "REJECT_FOUNDATION_MUTATION",
            "admitted": admitted,
            "target_scope": "PASS_072_FOUNDATION" if foundation_change else "NATIVE_PRODUCT",
            "platform_root_checked": FROZEN_PASS072_SYSTEM_ROOT_HASH72,
            "foundation_mutation_permitted": False,
            "reversible_alignment_patch_required_for_foundation_change": True,
        }
        body["alignment_decision_root_hash72"] = product_root("pass074_effect_alignment", body)
        self.alignment_decisions[decision_id] = stable(body)
        if request["project_id"] in self.projects:
            self._append_project_object(request["project_id"], decision_id)
        return body

    def dispatch(self, request_payload: Mapping[str, Any]) -> Dict[str, Any]:
        request = canonical_request(request_payload)
        operation_id = str(request["payload"].get("operation_id") or "")
        definitions = {x["operation_id"]: x for x in self.registry["operations"]}
        definition = definitions.get(operation_id)
        if not definition:
            return self._reject(request, "REJECT_UNREGISTERED_OPERATION")
        if definition["operation_class"] != request["operation_class"]:
            return self._reject(request, "REJECT_OPERATION_CLASS_MISMATCH")
        if not definition["implemented"]:
            return self._reject(request, "TYPED_UNAVAILABLE_FUTURE_NATIVE_PRODUCT", unavailable=True)
        if request["operation_class"] in AUTHORITY_REQUIRED and not self._authority_ok(request):
            return self._reject(request, "REJECT_MUTATION_WITHOUT_AUTHORITY_AND_LEASE")

        alignment = None
        if request["operation_class"] in AUTHORITY_REQUIRED:
            alignment = self._effect_alignment_decision(request)
            if not alignment["admitted"]:
                return self._reject(
                    request,
                    "REJECT_FOUNDATION_MUTATION_REQUIRES_REVERSIBLE_ALIGNMENT_PATCH",
                    extra_refs=[alignment["alignment_decision_id"]],
                    result_extra={"alignment_decision_ref": alignment["alignment_decision_id"]},
                )

        handler = getattr(self, "_op_" + operation_id.replace(".", "_"))
        try:
            result, result_refs, artifact_refs = handler(request)
        except ContractError as exc:
            return self._reject(request, str(exc))
        if alignment:
            result = {**result, "alignment_decision_ref": alignment["alignment_decision_id"]}
            result_refs = [*result_refs, alignment["alignment_decision_id"]]
        receipt = self._receipt(request, "ADMITTED", result)
        refs = [*result_refs, *artifact_refs, receipt["receipt_id"]]
        event = self._event(request, "ADMITTED", refs)
        state = self.snapshot()
        return response_envelope(
            request,
            status="ADMITTED",
            result_object_refs=result_refs,
            artifact_refs=artifact_refs,
            receipt_refs=[receipt["receipt_id"]],
            runtime_state_ref=state["workspace_state_root_hash72"],
            result={**result, "event_root_hash72": event["event_root_hash72"]},
        )

    def _require_project(self, project_id: str) -> Dict[str, Any]:
        project = self.projects.get(project_id)
        if not project:
            raise ContractError("REJECT_PROJECT_NOT_FOUND")
        return project

    def _append_project_object(self, project_id: str, object_id: str) -> None:
        project = self._require_project(project_id)
        if object_id not in project["object_ids"]:
            project["object_ids"].append(object_id)

    def _op_workspace_project_create(self, request: Mapping[str, Any]):
        project_id = request["project_id"]
        existing = self.projects.get(project_id)
        if existing:
            return {"project": existing, "created": False}, [project_id], []
        project = {
            "schema": PROJECT_SCHEMA,
            "project_id": project_id,
            "name": str(request["payload"].get("name") or project_id),
            "platform_dependency_root_hash72": FROZEN_PASS072_SYSTEM_ROOT_HASH72,
            "development_protocol_root_hash72": self.development_protocol[
                "development_protocol_root_hash72"
            ],
            "object_ids": [],
            "artifact_ids": [],
            "workspace_is_projection_over_runtime_state": True,
        }
        project["project_root_hash72"] = product_root("pass074_workspace_project", project)
        self.projects[project_id] = stable(project)
        return {"project": project, "created": True}, [project_id], []

    def _op_workspace_session_open(self, request: Mapping[str, Any]):
        self._require_project(request["project_id"])
        session_id = request["session_id"]
        session = {
            "schema": SESSION_SCHEMA,
            "session_id": session_id,
            "project_id": request["project_id"],
            "client_surface": str(request.get("client_surface") or "EXTERNAL"),
            "opened_at_sequence": self.sequence + 1,
            "runtime_state_is_authoritative": True,
        }
        session["session_root_hash72"] = product_root("pass074_workspace_session", session)
        self.sessions[session_id] = stable(session)
        return {"session": session}, [session_id], []

    def _op_workspace_buffer_open(self, request: Mapping[str, Any]):
        self._require_project(request["project_id"])
        buffer_id = str(request["payload"].get("buffer_id") or f"buffer:{request['request_id']}")
        text = str(request["payload"].get("text") or "")
        buffer = {
            "schema": BUFFER_SCHEMA,
            "buffer_id": buffer_id,
            "project_id": request["project_id"],
            "name": str(request["payload"].get("name") or "untitled.hhs"),
            "text": text,
            "revision": 0,
            "committed_artifact_ref": "",
            "editor_buffer_is_not_canonical_source": True,
        }
        buffer["buffer_root_hash72"] = product_root("pass074_editor_buffer", buffer)
        self.buffers[buffer_id] = stable(buffer)
        self._append_project_object(request["project_id"], buffer_id)
        return {"buffer": buffer}, [buffer_id], []

    def _op_workspace_agent_register(self, request: Mapping[str, Any]):
        self._require_project(request["project_id"])
        agent = canonical_agent(request["payload"], project_id=request["project_id"])
        self.agents[agent["agent_id"]] = agent
        self._append_project_object(request["project_id"], agent["agent_id"])
        return {"agent": agent}, [agent["agent_id"]], []

    def _op_workspace_change_propose(self, request: Mapping[str, Any]):
        self._require_project(request["project_id"])
        proposer = str(request["payload"].get("proposer_agent_ref") or "")
        if proposer not in self.agents:
            raise ContractError("REJECT_PROPOSER_AGENT_NOT_REGISTERED")
        proposal = canonical_change_proposal(
            request["payload"],
            project_id=request["project_id"],
            proposer_agent_ref=proposer,
            base_workspace_state_root_hash72=self.snapshot()["workspace_state_root_hash72"],
        )
        self.proposals[proposal["proposal_id"]] = proposal
        self._append_project_object(request["project_id"], proposal["proposal_id"])
        return {"proposal": proposal}, [proposal["proposal_id"]], []

    def _op_workspace_buffer_update(self, request: Mapping[str, Any]):
        buffer_id = str(request["payload"].get("buffer_id") or "")
        if buffer_id not in self.buffers:
            raise ContractError("REJECT_BUFFER_NOT_FOUND")
        current = deepcopy(self.buffers[buffer_id])
        current.pop("buffer_root_hash72", None)
        current["text"] = str(request["payload"].get("text") or "")
        current["revision"] = int(current["revision"]) + 1
        current["committed_artifact_ref"] = ""
        current["buffer_root_hash72"] = product_root("pass074_editor_buffer", current)
        self.buffers[buffer_id] = stable(current)
        return {"buffer": current, "canonical_source_changed": False}, [buffer_id], []

    def _op_workspace_source_commit(self, request: Mapping[str, Any]):
        buffer_id = str(request["payload"].get("buffer_id") or "")
        if buffer_id not in self.buffers:
            raise ContractError("REJECT_BUFFER_NOT_FOUND")
        buffer = self.buffers[buffer_id]
        artifact_id = str(
            request["payload"].get("artifact_id") or f"artifact:{buffer_id}:{buffer['revision']}"
        )
        artifact = {
            "schema": "HHS_COMMITTED_SOURCE_ARTIFACT_V1",
            "artifact_id": artifact_id,
            "project_id": request["project_id"],
            "source_buffer_ref": buffer_id,
            "source_buffer_revision": buffer["revision"],
            "name": buffer["name"],
            "content": buffer["text"],
            "lineage": {"parent_artifact_ref": buffer.get("committed_artifact_ref") or "GENESIS"},
            "compiled_artifact_self_authorizes": False,
        }
        artifact["artifact_root_hash72"] = product_root("pass074_source_artifact", artifact)
        self.artifacts[artifact_id] = stable(artifact)
        self.buffers[buffer_id]["committed_artifact_ref"] = artifact_id
        project = self._require_project(request["project_id"])
        if artifact_id not in project["artifact_ids"]:
            project["artifact_ids"].append(artifact_id)
        return {"artifact": artifact, "buffer_remains_projection": True}, [buffer_id], [artifact_id]

    def _op_workspace_test_record(self, request: Mapping[str, Any]):
        proposal_ref = str(request["payload"].get("proposal_ref") or "")
        if proposal_ref not in self.proposals:
            raise ContractError("REJECT_TEST_RECORD_WITHOUT_PROPOSAL")
        record = canonical_test_record(request["payload"], project_id=request["project_id"])
        self.test_records[record["test_record_id"]] = record
        self._append_project_object(request["project_id"], record["test_record_id"])
        return {"test_record": record}, [record["test_record_id"], proposal_ref], []

    def _op_workspace_handoff_create(self, request: Mapping[str, Any]):
        for field in ("from_agent_ref", "to_agent_ref"):
            agent_ref = str(request["payload"].get(field) or "")
            if agent_ref not in self.agents:
                raise ContractError(f"REJECT_HANDOFF_AGENT_NOT_REGISTERED:{field}")
        for proposal_ref in request["payload"].get("proposal_refs", []):
            if proposal_ref not in self.proposals:
                raise ContractError("REJECT_HANDOFF_PROPOSAL_NOT_FOUND")
        for test_ref in request["payload"].get("test_record_refs", []):
            if test_ref not in self.test_records:
                raise ContractError("REJECT_HANDOFF_TEST_RECORD_NOT_FOUND")
        capsule = build_handoff_capsule(
            request["payload"],
            project_id=request["project_id"],
            workspace_state_root_hash72=self.snapshot()["workspace_state_root_hash72"],
        )
        self.handoffs[capsule["handoff_id"]] = capsule
        self._append_project_object(request["project_id"], capsule["handoff_id"])
        return {"handoff": capsule}, [capsule["handoff_id"]], []

    def _op_workspace_source_inspect(self, request: Mapping[str, Any]):
        buffer_id = str(request["payload"].get("buffer_id") or "")
        artifact_id = str(request["payload"].get("artifact_id") or "")
        if artifact_id:
            source = self.artifacts.get(artifact_id)
            source_ref = artifact_id
            text = str(source.get("content") if source else "")
        else:
            source = self.buffers.get(buffer_id)
            source_ref = buffer_id
            text = str(source.get("text") if source else "")
        if source is None:
            raise ContractError("REJECT_SOURCE_NOT_FOUND")
        diagnostics = []
        if not text.strip():
            diagnostics.append({"code": "EMPTY_SOURCE", "severity": "WARNING"})
        result = {
            "source_ref": source_ref,
            "line_count": 0 if not text else text.count("\n") + 1,
            "character_count": len(text),
            "balanced_delimiters": all(
                text.count(a) == text.count(b) for a, b in (("(", ")"), ("[", "]"), ("{", "}"))
            ),
            "diagnostics": diagnostics,
            "execution_kind": "BOUNDED_SOURCE_INSPECTION_NOT_INTERPRETER_EXECUTION",
        }
        result["inspection_root_hash72"] = product_root("pass074_source_inspection", result)
        return result, [source_ref], []

    def _op_workspace_alignment_evaluate(self, request: Mapping[str, Any]):
        proposal_ref = str(request["payload"].get("proposal_ref") or "")
        proposal = self.proposals.get(proposal_ref)
        if not proposal:
            raise ContractError("REJECT_ALIGNMENT_PROPOSAL_NOT_FOUND")
        decision = evaluate_proposal_alignment(proposal)
        decision_id = f"proposal-alignment:{proposal_ref}"
        decision = {**decision, "alignment_decision_id": decision_id}
        self.alignment_decisions[decision_id] = stable(decision)
        self._append_project_object(request["project_id"], decision_id)
        return {"alignment_decision": decision}, [decision_id, proposal_ref], []

    def _op_workspace_healing_plan(self, request: Mapping[str, Any]):
        proposal_ref = str(request["payload"].get("proposal_ref") or "")
        test_record_ref = str(request["payload"].get("test_record_ref") or "")
        proposal = self.proposals.get(proposal_ref)
        record = self.test_records.get(test_record_ref)
        if not proposal:
            raise ContractError("REJECT_HEALING_PROPOSAL_NOT_FOUND")
        if not record:
            raise ContractError("REJECT_HEALING_TEST_RECORD_NOT_FOUND")
        requested_by = str(request["payload"].get("requested_by_agent_ref") or "")
        if requested_by not in self.agents:
            raise ContractError("REJECT_HEALING_AGENT_NOT_REGISTERED")
        plan = build_bounded_healing_plan(
            proposal=proposal,
            test_record=record,
            requested_by_agent_ref=requested_by,
        )
        self.healing_plans[plan["healing_plan_id"]] = plan
        self._append_project_object(request["project_id"], plan["healing_plan_id"])
        return {"healing_plan": plan}, [plan["healing_plan_id"], proposal_ref, test_record_ref], []

    def _op_workspace_state_get(self, request: Mapping[str, Any]):
        state = self.snapshot()
        return {"state": state}, [], []

    def _op_workspace_project_index(self, request: Mapping[str, Any]):
        project = self._require_project(request["project_id"])
        index = {
            "schema": OBJECT_INDEX_SCHEMA,
            "project_id": request["project_id"],
            "object_refs": sorted(project["object_ids"]),
            "artifact_refs": sorted(project["artifact_ids"]),
            "runtime_state_is_authoritative": True,
        }
        index["project_object_index_root_hash72"] = product_root("pass074_project_object_index", index)
        return {"index": index}, list(index["object_refs"]), list(index["artifact_refs"])

    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        value = self.artifacts.get(artifact_id)
        return deepcopy(value) if value else None

    def get_receipt(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        value = self.receipts.get(receipt_id)
        return deepcopy(value) if value else None

    def get_events_after(self, sequence: int = 0) -> list[Dict[str, Any]]:
        return [deepcopy(e) for e in self.events if int(e["sequence"]) > int(sequence)]


def build_demo_workspace(runtime: Optional[HHSNativeWorkspaceRuntime] = None) -> Dict[str, Any]:
    from .hhs_workspace_contracts_v1 import make_request

    rt = runtime or HHSNativeWorkspaceRuntime()
    authority = {
        "role_contract_ref": "role:workspace-developer",
        "task_assignment_ref": "task:pass074-demo",
        "capability_lease_ref": "lease:pass074-demo",
    }
    requests = [
        make_request(
            request_id="req:project",
            project_id="project:pass074-demo",
            session_id="session:pass074-demo",
            operation_class="INGRESS",
            operation_id="workspace.project.create",
            payload={"name": "Pass 074 IDE Workspace"},
        ),
        make_request(
            request_id="req:session",
            project_id="project:pass074-demo",
            session_id="session:pass074-demo",
            operation_class="INGRESS",
            operation_id="workspace.session.open",
            client_surface="REPLAY",
        ),
        make_request(
            request_id="req:agent:human",
            project_id="project:pass074-demo",
            session_id="session:pass074-demo",
            operation_class="INGRESS",
            operation_id="workspace.agent.register",
            payload={
                "agent_id": "agent:human:developer",
                "agent_kind": "HUMAN",
                "display_name": "Human Developer",
                "capabilities": ["requirements", "review", "authority.request"],
            },
        ),
        make_request(
            request_id="req:agent:llm",
            project_id="project:pass074-demo",
            session_id="session:pass074-demo",
            operation_class="INGRESS",
            operation_id="workspace.agent.register",
            payload={
                "agent_id": "agent:llm:builder",
                "agent_kind": "LLM",
                "display_name": "LLM Builder",
                "capabilities": ["code.proposal", "test.analysis", "repair.plan"],
            },
        ),
        make_request(
            request_id="req:buffer",
            project_id="project:pass074-demo",
            session_id="session:pass074-demo",
            operation_class="INGRESS",
            operation_id="workspace.buffer.open",
            payload={
                "buffer_id": "buffer:main",
                "name": "main.hhs",
                "text": "project pass074_demo {\n  source main\n}\n",
            },
        ),
        make_request(
            request_id="req:commit",
            project_id="project:pass074-demo",
            session_id="session:pass074-demo",
            operation_class="MUTATE",
            operation_id="workspace.source.commit",
            payload={"buffer_id": "buffer:main", "artifact_id": "artifact:main:0"},
            **authority,
        ),
        make_request(
            request_id="req:proposal",
            project_id="project:pass074-demo",
            session_id="session:pass074-demo",
            operation_class="INGRESS",
            operation_id="workspace.change.propose",
            payload={
                "proposal_id": "proposal:demo:1",
                "program_id": "program:pass074-demo",
                "proposer_agent_ref": "agent:llm:builder",
                "summary": "Add reusable bounded source inspection",
                "new_capability_statement": "Inspect committed sources through the unified Runtime API",
                "reusable_capabilities": ["source.inspection"],
                "reachable_entrypoint": "workspace.source.inspect",
                "affected_product_paths": ["native_projects/hhs_ide_workspace"],
                "requested_tests": ["tests/test_hhs_pass074_unified_ide_workspace_v1.py"],
            },
        ),
        make_request(
            request_id="req:alignment",
            project_id="project:pass074-demo",
            session_id="session:pass074-demo",
            operation_class="EXECUTE",
            operation_id="workspace.alignment.evaluate",
            payload={"proposal_ref": "proposal:demo:1"},
        ),
        make_request(
            request_id="req:inspect",
            project_id="project:pass074-demo",
            session_id="session:pass074-demo",
            operation_class="EXECUTE",
            operation_id="workspace.source.inspect",
            payload={"artifact_id": "artifact:main:0"},
        ),
        make_request(
            request_id="req:handoff",
            project_id="project:pass074-demo",
            session_id="session:pass074-demo",
            operation_class="MUTATE",
            operation_id="workspace.handoff.create",
            payload={
                "handoff_id": "handoff:demo:1",
                "from_agent_ref": "agent:llm:builder",
                "to_agent_ref": "agent:human:developer",
                "proposal_refs": ["proposal:demo:1"],
                "test_record_refs": [],
                "required_actions": ["REVIEW_ALIGNMENT_DECISION", "RUN_TESTS"],
            },
            **authority,
        ),
    ]
    responses = [rt.dispatch(x) for x in requests]
    return {"runtime": rt, "requests": requests, "responses": responses, "snapshot": rt.snapshot()}


def build_pass074_release_bundle() -> Dict[str, Any]:
    demo = build_demo_workspace()
    snapshot = demo["snapshot"]
    registry = operation_registry()
    protocol = development_protocol_contract()
    body = {
        "schema": "HHS_PASS_074_UNIFIED_WORKSPACE_RELEASE_BUNDLE_V1",
        "version": VERSION,
        "pass_id": PASS_ID,
        "project_id": "HHS_NATIVE_IDE_WORKSPACE",
        "parent_native_pass": "PASS_073",
        "platform_dependency": {
            "pass_id": "PASS_072",
            "total_system_root_hash72": FROZEN_PASS072_SYSTEM_ROOT_HASH72,
            "foundation_modified": False,
        },
        "operation_registry": registry,
        "development_protocol": protocol,
        "demo_workspace_state": snapshot,
        "demo_response_roots": [x["response_root_hash72"] for x in demo["responses"]],
        "client_surfaces": ["GUI", "CLI", "EXTERNAL_API", "REPLAY_RUNNER", "HUMAN_AGENT", "LLM_AGENT", "CI_AGENT"],
        "ui_surfaces": [
            "WorkspaceShell",
            "ProjectExplorer",
            "EditorPanel",
            "RuntimeConsole",
            "ArtifactPanel",
            "ReceiptPanel",
            "ExecutionPanel",
            "AgentNetworkPanel",
            "AlignmentPanel",
            "IterationPanel",
            "StatusBar",
        ],
        "reserved_future_surfaces": [
            "HarmonicodeEditor",
            "InterpreterConsole",
            "CompilerPipeline",
            "EmulatorRuntime",
            "AutonomousRepairExecutor",
        ],
        "one_runtime": True,
        "one_authority_chain": True,
        "one_project_model": True,
        "one_ingress_contract": True,
        "one_egress_contract": True,
        "canonical_agent_exchange": True,
        "alignment_gate_on_product_effects": True,
        "context_independent_agent_handoff": True,
        "bounded_self_healing_plan_surface": True,
        "open_ended_development_above_frozen_foundation": True,
        "new_orphan_modules": 0,
    }
    body["product_root_hash72"] = product_root("pass074_release_bundle", body)
    return stable(body)


def write_release_artifacts(root: Optional[str | Path] = None) -> Dict[str, Any]:
    repo = Path(root).resolve() if root else Path(__file__).resolve().parents[2]
    out = repo / "native_projects/hhs_ide_workspace/artifacts"
    out.mkdir(parents=True, exist_ok=True)
    bundle = build_pass074_release_bundle()
    (out / "HHS_PASS_074_UNIFIED_WORKSPACE_RELEASE_BUNDLE.json").write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    snapshot = bundle["demo_workspace_state"]
    (out / "PASS_074_WORKSPACE_STATE_SNAPSHOT.json").write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    registry = bundle["operation_registry"]
    (out / "PASS_074_API_OPERATION_REGISTRY.json").write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    protocol = bundle["development_protocol"]
    (out / "PASS_074_DEVELOPMENT_NETWORK_PROTOCOL.json").write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return bundle


if __name__ == "__main__":
    print(json.dumps(write_release_artifacts(), indent=2, sort_keys=True))
