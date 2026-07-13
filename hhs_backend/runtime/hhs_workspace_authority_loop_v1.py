"""Workspace authority loop for Pass 049 Visual Runtime OS."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from hhs_backend.runtime.hhs_workspace_command_router_v1 import build_workspace_command, COMMAND_TIERS
from hhs_backend.runtime.runtime_workspace_project_v1 import create_workspace_project, fork_workspace_project, open_workspace_project
from hhs_backend.runtime.runtime_workspace_object_v1 import VERSION, AUTHORITY, create_workspace_object, hash72
from hhs_backend.runtime.multimodal_workspace_ingress_v1 import ingest_workspace_source
from hhs_backend.runtime.hhs_symbolic_document_service_v1 import create_symbolic_document, propose_source_patch, admit_symbolic_patch
from hhs_backend.runtime.hhs_live_interpreter_v1 import build_interpreter_request, interpret_expression
from hhs_backend.runtime.hhs_interpreting_compiler_v1 import build_compiler_request, compile_hhs_source
from hhs_backend.runtime.hhs_visual_emulator_session_v1 import VisualEmulatorRuntime
from hhs_backend.runtime.hhs_workspace_semantic_memory_v1 import build_workspace_semantic_query, execute_workspace_semantic_query
from hhs_backend.runtime.hhs_workspace_graph_projection_v1 import build_workspace_graph_projection


class WorkspaceAuthorityLoop:
    def __init__(self) -> None:
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.command_history: list[Dict[str, Any]] = []
        self.emulator = VisualEmulatorRuntime()

    def submit(self, operation: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        payload_dict = dict(payload or {})
        command = build_workspace_command(
            operation,
            project_id=str(payload_dict.get("project_id") or "project:default"),
            object_id=payload_dict.get("object_id"),
            payload=payload_dict,
        )
        base = {
            "schema": "HHS_WORKSPACE_AUTHORITY_LOOP_DECISION_V1",
            "version": VERSION,
            "command": command,
            "gui_mutated_runtime_truth": False,
            "websocket_feedback_required": command.get("authority_tier") != "PRESENTATION_ONLY",
            "authority": AUTHORITY,
        }
        if payload_dict.get("frontend_mutated_runtime_truth"):
            base.update({"ok": False, "status": "REJECT_GUI_DIRECT_WORKSPACE_MUTATION", "reasons": ["REJECT_GUI_DIRECT_WORKSPACE_MUTATION"]})
            return self._remember(base)
        if command.get("authority_tier") == "PRESENTATION_ONLY":
            base.update({"ok": True, "status": "PRESENTATION_ONLY_LOCAL_STATE", "canonical_runtime_mutated": False})
            base["decision_hash72"] = hash72("HHS_WORKSPACE_AUTHORITY_LOOP_DECISION_V1", base)
            return self._remember(base)

        result: Dict[str, Any]
        if operation == "project.create":
            project = create_workspace_project(str(payload_dict.get("name") or "HHS Workspace"))
            self.projects[project["project_id"]] = project
            result = {"ok": True, "status": "WORKSPACE_PROJECT_OPENED", "project": project}
        elif operation == "project.fork":
            project = self.projects.get(str(payload_dict.get("project_id"))) or create_workspace_project("Fork Source")
            result = fork_workspace_project(project, payload_dict.get("name"))
        elif operation == "ingress.register":
            project = self.projects.get(str(payload_dict.get("project_id"))) or create_workspace_project("Ingress Project")
            result = ingest_workspace_source(
                project=project,
                source_name=str(payload_dict.get("source_name") or "main.hhs"),
                payload=payload_dict.get("source_payload") or payload_dict.get("payload") or "",
                declared_modality=str(payload_dict.get("declared_modality") or "HARMONICODE_SOURCE"),
            )
            if result.get("ok") and result.get("registration", {}).get("project"):
                self.projects[result["registration"]["project"]["project_id"]] = result["registration"]["project"]
        elif operation == "source.patch":
            document = payload_dict.get("document") or create_symbolic_document(str(payload_dict.get("project_id") or "project:default"), "main.hhs", str(payload_dict.get("old_text") or ""))
            patch = propose_source_patch(document=document, replacement_text=str(payload_dict.get("replacement_text") or ""))
            result = admit_symbolic_patch(document, patch, str(payload_dict.get("replacement_text") or ""))
        elif operation == "interpret.execute":
            request = build_interpreter_request(
                project_id=str(payload_dict.get("project_id") or "project:default"),
                source_object_id=str(payload_dict.get("source_object_id") or "object:expression"),
                expression=str(payload_dict.get("expression") or "1+1"),
            )
            result = interpret_expression(request, str(payload_dict.get("expression") or "1+1"))
        elif operation == "compile.execute":
            request = build_compiler_request(
                str(payload_dict.get("project_id") or "project:default"),
                str(payload_dict.get("source_object_id") or "object:source"),
                str(payload_dict.get("source_text") or "a²=1"),
                str(payload_dict.get("target") or "HHS_IR"),
            )
            result = compile_hhs_source(request, str(payload_dict.get("source_text") or "a²=1"))
        elif operation == "emulator.create":
            result = self.emulator.create_session(str(payload_dict.get("project_id") or "project:default"), str(payload_dict.get("program_artifact_id") or "artifact:hhs-ir"))
        elif operation.startswith("emulator."):
            result = self.emulator.command(str(payload_dict.get("session_id") or "emulator:missing"), operation.split(".", 1)[1], payload_dict)
        elif operation == "memory.search":
            query = build_workspace_semantic_query(str(payload_dict.get("query_text") or ""), project_id=str(payload_dict.get("project_id") or "project:default"))
            result = execute_workspace_semantic_query(query, payload_dict.get("objects") or [])
        elif operation == "graph.query":
            result = build_workspace_graph_projection(payload_dict.get("nodes") or [], payload_dict.get("edges") or [], project_id=str(payload_dict.get("project_id") or "project:default"))
            result["ok"] = True
        else:
            result = {"ok": False, "status": "REJECT_UNWITNESSED_WORKSPACE_TRANSFORMATION", "reasons": ["REJECT_UNWITNESSED_WORKSPACE_TRANSFORMATION"]}
        base.update({
            "ok": bool(result.get("ok")),
            "status": result.get("status") or ("WORKSPACE_COMMAND_ADMITTED" if result.get("ok") else "WORKSPACE_COMMAND_REJECTED"),
            "result": result,
            "receipt_hash72": hash72("HHS_WORKSPACE_AUTHORITY_LOOP_RECEIPT_V1", {"command": command, "result": result}),
        })
        base["decision_hash72"] = hash72("HHS_WORKSPACE_AUTHORITY_LOOP_DECISION_V1", base)
        return self._remember(base)

    def _remember(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        self.command_history.append(decision)
        self.command_history = self.command_history[-64:]
        return decision

    def status(self) -> Dict[str, Any]:
        return {
            "schema": "HHS_WORKSPACE_AUTHORITY_LOOP_STATUS_V1",
            "version": VERSION,
            "project_count": len(self.projects),
            "command_history_count": len(self.command_history),
            "authority": AUTHORITY,
        }


def workspace_authority_loop_self_test() -> Dict[str, Any]:
    loop = WorkspaceAuthorityLoop()
    presentation = loop.submit("panel.resize", {"width": 100})
    project = loop.submit("project.create", {"name": "Authority Workspace"})
    ingress = loop.submit("ingress.register", {"project_id": project["result"]["project"]["project_id"], "source_name": "main.hhs", "source_payload": "a²=1", "declared_modality": "HARMONICODE_SOURCE"})
    patch = loop.submit("source.patch", {"project_id": project["result"]["project"]["project_id"], "replacement_text": "a²=1\nb²=2"})
    interpret = loop.submit("interpret.execute", {"expression": "1+2"})
    compile_result = loop.submit("compile.execute", {"source_text": "a²=1", "target": "HHS_IR"})
    emu_create = loop.submit("emulator.create", {"program_artifact_id": "artifact:hhs-ir"})
    emu_step = loop.submit("emulator.step", {"session_id": emu_create["result"]["session"]["session_id"]})
    direct = loop.submit("source.patch", {"frontend_mutated_runtime_truth": True, "replacement_text": "x=1"})
    return {
        "schema": "HHS_WORKSPACE_AUTHORITY_LOOP_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(presentation.get("ok") and project.get("ok") and ingress.get("ok") and patch.get("ok") and interpret.get("ok") and compile_result.get("ok") and emu_create.get("ok") and emu_step.get("ok") and not direct.get("ok")),
        "status": loop.status(),
        "presentation": presentation,
        "project": project,
        "ingress": ingress,
        "patch": patch,
        "interpret": interpret,
        "compile": compile_result,
        "emulator_create": emu_create,
        "emulator_step": emu_step,
        "direct_gui_mutation_rejection": direct,
        "hard_invariant": "WORKSPACE_IS_REQUEST_PROJECTION_LAYER_NOT_RUNTIME_AUTHORITY",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(workspace_authority_loop_self_test(), indent=2, sort_keys=True, default=str))
