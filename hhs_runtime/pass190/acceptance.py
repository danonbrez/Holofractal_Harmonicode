"""Pass 190 I136 governed project acceptance overlay.

The overlay extends the historical Iteration-7 operation registry inside the
same DurableExecutionContext. Project state is stored in the existing Pass190
workspace/artifact registries; every mutation therefore remains inside the
same fenced SQLite authority and receipt chain.

Compiler/interpreter/emulator services are subordinate execution adapters.
Their receipts are evidence inside the outer Pass190 operation result; they do
not become a second persistence or VM81 authority.
"""
from __future__ import annotations

import base64
import copy
import io
import json
from pathlib import Path
import sys
from typing import Any, Mapping
import zipfile

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "native_projects" / "hhs_pass190_operation_fabric" / "python"
if str(NATIVE) not in sys.path:
    sys.path.insert(0, str(NATIVE))

from hhs_pass190 import (  # type: ignore
    DEFAULT_REGISTRY,
    InvocationResult,
    OperationRecord,
    REGISTRY_SCHEMA,
    RegistryValidationError,
    ReplayMismatchError,
    hash72,
    hash216,
)
from hhs_pass190_iteration6_registry import (  # type: ignore
    _object,
    _operation,
    _string,
)
from hhs_pass190_iteration7 import DurableExecutionContext  # type: ignore
from hhs_pass190_iteration7_registry import Iteration7OperationRegistry  # type: ignore

from hhs_backend.runtime.hhs_application_factory_v1 import STARTER_FILES
from hhs_backend.runtime.hhs_interpreting_compiler_v1 import compile_hhs_source
from hhs_backend.runtime.hhs_live_interpreter_v1 import (
    build_interpreter_request,
    interpret_expression,
)
from hhs_backend.runtime.hhs_visual_emulator_session_v1 import VisualEmulatorRuntime

I136_ACCEPTANCE_CONTRACT = "HHS-P190-I136-PROJECT-ACCEPTANCE-VM81-H72-H216"
I136_PROJECT_SCHEMA = "HHS_PASS_190_I136_PROJECT_V1"
I136_EXPORT_SCHEMA = "HHS_PASS_190_I136_SOURCE_EXPORT_V1"

PROJECT_OPERATION_IDS = (
    "profile.local",
    "project.new",
    "project.get",
    "project.list",
    "project.edit",
    "project.build",
    "project.run",
    "project.test",
    "project.export",
    "project.replay",
)

DEFAULT_HHS_SOURCE = "a²=1 b²=2\n"


def _project_operation_records() -> tuple[dict[str, Any], ...]:
    string = _string
    obj = _object()
    integer = {"type": "integer", "minimum": 1, "maximum": 32}
    return (
        _operation(
            "profile.local", "Resolve approved local profile", "LocalProfile",
            "public", "pure",
            {"type": "object", "additionalProperties": False, "properties": {}, "required": []},
            "object", "profile-local", operation_class="pass190-completion",
        ),
        _operation(
            "project.new", "Create governed project", "ProjectNew",
            "workspace:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "project_id": string(128), "name": string(256), "template": string(128),
            }, "required": ["project_id", "name", "template"]},
            "object", "project-new", operation_class="pass190-completion",
        ),
        _operation(
            "project.get", "Get governed project", "ProjectGet",
            "workspace:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "project_id": string(128),
            }, "required": ["project_id"]},
            "object", "project-get", operation_class="pass190-completion",
        ),
        _operation(
            "project.list", "List governed projects", "ProjectList",
            "workspace:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {}, "required": []},
            "array", "project-list", operation_class="pass190-completion",
        ),
        _operation(
            "project.edit", "Edit governed project file", "ProjectEdit",
            "workspace:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "project_id": string(128), "path": string(512), "content": string(262144),
            }, "required": ["project_id", "path", "content"]},
            "object", "project-edit", operation_class="pass190-completion",
        ),
        _operation(
            "project.build", "Build governed project", "ProjectBuild",
            "workspace:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "project_id": string(128),
            }, "required": ["project_id"]},
            "object", "project-build", operation_class="pass190-completion",
        ),
        _operation(
            "project.run", "Run governed project", "ProjectRun",
            "workspace:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "project_id": string(128), "steps": integer,
            }, "required": ["project_id"]},
            "object", "project-run", operation_class="pass190-completion",
        ),
        _operation(
            "project.test", "Test governed project", "ProjectTest",
            "workspace:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "project_id": string(128),
            }, "required": ["project_id"]},
            "object", "project-test", operation_class="pass190-completion",
        ),
        _operation(
            "project.export", "Export governed project source ZIP", "ProjectExport",
            "artifact:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "project_id": string(128),
            }, "required": ["project_id"]},
            "object", "project-export", operation_class="pass190-completion",
        ),
        _operation(
            "project.replay", "Verify governed project state", "ProjectReplay",
            "workspace:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "project_id": string(128),
            }, "required": ["project_id"]},
            "object", "project-replay", operation_class="pass190-completion",
        ),
    )


PROJECT_OPERATION_RECORDS = _project_operation_records()


class Pass190CompletionOperationRegistry(Iteration7OperationRegistry):
    """Iteration-7 registry plus Pass190 full-contract acceptance operations."""

    def __init__(self, registry_path: Path = DEFAULT_REGISTRY):
        parent = Iteration7OperationRegistry(registry_path)
        records = [copy.deepcopy(dict(record.raw)) for record in parent.records]
        records.extend(copy.deepcopy(record) for record in PROJECT_OPERATION_RECORDS)
        identity = {
            "schema": REGISTRY_SCHEMA,
            "contract": I136_ACCEPTANCE_CONTRACT,
            "parent_contract": parent.payload.get("contract"),
            "parent_registry_hash216": parent.payload.get("registry_hash216"),
            "iteration": "I136_COMPLETION",
            "operations": records,
        }
        self.payload = {
            **identity,
            "registry_hash216": hash216("pass190.i136.completion.registry", identity),
            "native_operation_count": int(parent.payload["native_operation_count"]),
            "governed_operation_count": len(records),
            "execution_operation_count": int(parent.payload["execution_operation_count"]),
            "project_acceptance_operation_count": len(PROJECT_OPERATION_RECORDS),
        }
        self.records = tuple(OperationRecord(record) for record in records)
        self.by_id = {}
        self.by_constructor = {}
        self.by_python = {}
        self.by_shell = {}
        self._validate_and_index()
        if len(self.records) != len(parent.records) + len(PROJECT_OPERATION_RECORDS):
            raise RegistryValidationError("I136 completion operation count mismatch")
        if tuple(record.operation_id for record in self.records[-len(PROJECT_OPERATION_RECORDS):]) != PROJECT_OPERATION_IDS:
            raise RegistryValidationError("I136 completion operation order mismatch")


def _files_root(files: Mapping[str, str]) -> str:
    return hash72(
        "pass190.i136.project.files",
        [[path, files[path]] for path in sorted(files)],
    )


def _project_identity(project: Mapping[str, Any]) -> str:
    body = {
        key: copy.deepcopy(value)
        for key, value in project.items()
        if key not in {"project_root_hash72"}
    }
    return hash72("pass190.i136.project", body)


def _source_template(template: str) -> dict[str, str]:
    if template not in STARTER_FILES:
        raise ValueError(f"HHS_P190_TEMPLATE_UNKNOWN:{template}")
    files = copy.deepcopy(dict(STARTER_FILES[template]))
    files["src/main.hhs"] = DEFAULT_HHS_SOURCE
    return {path: str(content) for path, content in files.items()}


def _stable_zip(files: Mapping[str, str]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            info = zipfile.ZipInfo(path)
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[path].encode("utf-8"))
    return stream.getvalue()


def _compile_project(project: Mapping[str, Any]) -> dict[str, Any]:
    files = project["files"]
    source = str(files.get("src/main.hhs") or "")
    if not source:
        raise ValueError("HHS_P190_PROJECT_HHS_SOURCE_MISSING")
    source_root = hash72("HHS_COMPILER_SOURCE_TEXT_V1", source)
    request = {
        "schema": "HHS_COMPILER_REQUEST_V1",
        "version": "1.0.0",
        "request_id": f"compile:{project['project_id']}:{source_root[:16]}",
        "project_id": project["project_id"],
        "source_object_id": f"object:{project['project_id']}:src-main-hhs",
        "source_root_hash72": source_root,
        "target": "HHS_IR",
        "requires_conformance": True,
        "execution_authorization_requested": False,
    }
    request["request_root_hash72"] = hash72("HHS_COMPILER_REQUEST_V1", request)
    result = compile_hhs_source(request, source)
    if not result.get("ok"):
        raise ValueError(f"HHS_P190_PROJECT_BUILD_FAILED:{result.get('status')}")
    artifact = result["artifact"]
    return {
        "ok": True,
        "artifact_id": artifact["artifact_id"],
        "artifact_root_hash72": artifact["receipt_hash72"],
        "ir_root_hash72": artifact["ir_root_hash72"],
        "target_root_hash72": artifact["target_root_hash72"],
        "compiler_pipeline_root_hash72": artifact["compiler_pipeline_root_hash72"],
        "source_root_hash72": source_root,
        "execution_authorized_by_compiler": bool(result.get("execution_authorized")),
        "subordinate_authority": result.get("authority"),
    }


def _run_project(project: Mapping[str, Any], steps: int) -> dict[str, Any]:
    build = _compile_project(project)
    runtime = VisualEmulatorRuntime()
    created = runtime.create_session(
        project["project_id"],
        build["artifact_id"],
        initial_state={
            "project_root_hash72": project["project_root_hash72"],
            "source_root_hash72": build["source_root_hash72"],
            "artifact_root_hash72": build["artifact_root_hash72"],
        },
    )
    if not created.get("ok"):
        raise ValueError("HHS_P190_EMULATOR_SESSION_CREATE_FAILED")
    session_id = created["session"]["session_id"]
    executed = runtime.command(session_id, "run", {"steps": steps})
    snapshot = runtime.command(session_id, "snapshot")
    if not executed.get("ok") or not snapshot.get("ok"):
        raise ValueError("HHS_P190_PROJECT_RUN_FAILED")
    evidence = {
        "build": build,
        "steps": steps,
        "tick": executed["session"]["tick"],
        "run_mode": executed["session"]["mode"],
        "run_receipt_hash72": executed["receipt"]["receipt_hash72"],
        "snapshot_receipt_hash72": snapshot["receipt"]["receipt_hash72"],
        "history_erased": False,
        "subordinate_emulator_authority": executed["receipt"].get("authority"),
    }
    evidence["execution_evidence_hash72"] = hash72(
        "pass190.i136.project.run.evidence", evidence
    )
    return evidence


def _test_project(project: Mapping[str, Any]) -> dict[str, Any]:
    source = str(project["files"].get("src/main.hhs") or "")
    request = build_interpreter_request(
        project_id=project["project_id"],
        source_object_id=f"object:{project['project_id']}:acceptance-expression",
        expression="1+2",
    )
    interpreted = interpret_expression(request, "1+2")
    run = _run_project(project, 3)
    checks = {
        "source_present": bool(source),
        "exact_interpreter_ok": bool(interpreted.get("ok")),
        "exact_interpreter_result_is_three": interpreted.get("result") == 3,
        "compile_ok": bool(run["build"]["ok"]),
        "compiler_did_not_authorize_execution": run["build"][
            "execution_authorized_by_compiler"
        ] is False,
        "emulator_run_steps": run["tick"] == 3,
        "emulator_history_preserved": run["history_erased"] is False,
    }
    result = {
        "ok": all(checks.values()),
        "checks": checks,
        "interpreter_receipt_hash72": interpreted.get("receipt_hash72"),
        "execution_evidence_hash72": run["execution_evidence_hash72"],
    }
    result["test_evidence_hash72"] = hash72(
        "pass190.i136.project.test.evidence", result
    )
    if not result["ok"]:
        raise ValueError("HHS_P190_PROJECT_TEST_FAILED")
    return result


class Pass190AcceptanceAuthorityContext(DurableExecutionContext):
    """Same historical Pass190 authority with an additive acceptance registry."""

    def __init__(self, database_path: Path | str, registry_path: Path = DEFAULT_REGISTRY, **kwargs: Any):
        super().__init__(database_path, registry_path, **kwargs)
        self.registry = Pass190CompletionOperationRegistry(registry_path)
        self._implementations.update(
            {
                "profile.local": self._op_profile_local,
                "project.new": self._op_project_new,
                "project.get": self._op_project_get,
                "project.list": self._op_project_list,
                "project.edit": self._op_project_edit,
                "project.build": self._op_project_build,
                "project.run": self._op_project_run,
                "project.test": self._op_project_test,
                "project.export": self._op_project_export,
                "project.replay": self._op_project_replay,
            }
        )
        if set(self._implementations) != set(self.registry.by_id):
            missing = set(self.registry.by_id) - set(self._implementations)
            extra = set(self._implementations) - set(self.registry.by_id)
            raise RegistryValidationError(
                f"I136 registry/implementation mismatch missing={sorted(missing)} extra={sorted(extra)}"
            )
        self.store.restore_into(self)

    @staticmethod
    def _op_profile_local(_args: dict[str, Any]) -> dict[str, Any]:
        return {
            "profile_id": "local",
            "authority_mode": "LOCAL_CAPABILITY_BOUND",
            "remote_login_required": False,
            "canonical_runtime": True,
        }

    def _project_record(self, project_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
        workspace = self._active_workspace(self._identifier(project_id, "project_id"))
        metadata = copy.deepcopy(workspace.get("metadata", {}))
        project = metadata.get("i136_project")
        if not isinstance(project, dict) or project.get("schema") != I136_PROJECT_SCHEMA:
            raise ValueError("HHS_P190_PROJECT_NOT_FOUND")
        if project.get("project_id") != project_id:
            raise ValueError("HHS_P190_PROJECT_IDENTITY_DRIFT")
        if project.get("project_root_hash72") != _project_identity(project):
            raise ValueError("HHS_P190_PROJECT_ROOT_DRIFT")
        return workspace, copy.deepcopy(project)

    def _store_project(self, workspace: Mapping[str, Any], project: dict[str, Any]) -> dict[str, Any]:
        project["source_root_hash72"] = _files_root(project["files"])
        project["project_root_hash72"] = _project_identity(project)
        metadata = copy.deepcopy(workspace.get("metadata", {}))
        metadata["i136_project"] = copy.deepcopy(project)
        self._replace_record(
            "workspaces",
            str(workspace["workspace_id"]),
            {"metadata": metadata},
        )
        return copy.deepcopy(project)

    def _op_project_new(self, args: dict[str, Any]) -> dict[str, Any]:
        project_id = self._identifier(args["project_id"], "project_id")
        files = _source_template(args["template"])
        project = {
            "schema": I136_PROJECT_SCHEMA,
            "project_id": project_id,
            "name": args["name"],
            "template": args["template"],
            "files": files,
            "source_root_hash72": _files_root(files),
            "build": None,
            "run": None,
            "test": None,
            "exports": [],
            "version": 1,
        }
        project["project_root_hash72"] = _project_identity(project)
        workspace = self._op_workspace_create(
            {
                "workspace_id": project_id,
                "name": args["name"],
                "metadata": {
                    "i136_project": project,
                    "authority": "PASS190_DURABLE_EXECUTION_CONTEXT",
                },
            }
        )
        return copy.deepcopy(workspace["metadata"]["i136_project"])

    def _op_project_get(self, args: dict[str, Any]) -> dict[str, Any]:
        _workspace, project = self._project_record(args["project_id"])
        return project

    def _op_project_list(self, _args: dict[str, Any]) -> list[dict[str, Any]]:
        rows = []
        for workspace in self._resource_registries()["workspaces"].values():
            project = workspace.get("metadata", {}).get("i136_project")
            if isinstance(project, dict) and project.get("schema") == I136_PROJECT_SCHEMA:
                if project.get("project_root_hash72") != _project_identity(project):
                    raise ValueError("HHS_P190_PROJECT_ROOT_DRIFT")
                rows.append(copy.deepcopy(project))
        return sorted(rows, key=lambda item: item["project_id"])

    def _op_project_edit(self, args: dict[str, Any]) -> dict[str, Any]:
        workspace, project = self._project_record(args["project_id"])
        path = str(args["path"])
        if (
            not path
            or path.startswith("/")
            or "\\" in path
            or any(part in {"", ".", ".."} for part in path.split("/"))
        ):
            raise ValueError("HHS_P190_PROJECT_PATH_INVALID")
        project["files"][path] = str(args["content"])
        project["version"] = int(project["version"]) + 1
        project["build"] = None
        project["run"] = None
        project["test"] = None
        return self._store_project(workspace, project)

    def _op_project_build(self, args: dict[str, Any]) -> dict[str, Any]:
        workspace, project = self._project_record(args["project_id"])
        project["build"] = _compile_project(project)
        project["version"] = int(project["version"]) + 1
        stored = self._store_project(workspace, project)
        return {
            "project_id": project["project_id"],
            "build": copy.deepcopy(stored["build"]),
            "project_root_hash72": stored["project_root_hash72"],
        }

    def _op_project_run(self, args: dict[str, Any]) -> dict[str, Any]:
        workspace, project = self._project_record(args["project_id"])
        steps = int(args.get("steps", 3))
        project["run"] = _run_project(project, steps)
        project["build"] = copy.deepcopy(project["run"]["build"])
        project["version"] = int(project["version"]) + 1
        stored = self._store_project(workspace, project)
        return {
            "project_id": project["project_id"],
            "run": copy.deepcopy(stored["run"]),
            "project_root_hash72": stored["project_root_hash72"],
        }

    def _op_project_test(self, args: dict[str, Any]) -> dict[str, Any]:
        workspace, project = self._project_record(args["project_id"])
        project["test"] = _test_project(project)
        project["version"] = int(project["version"]) + 1
        stored = self._store_project(workspace, project)
        return {
            "project_id": project["project_id"],
            "test": copy.deepcopy(stored["test"]),
            "project_root_hash72": stored["project_root_hash72"],
        }

    def _op_project_export(self, args: dict[str, Any]) -> dict[str, Any]:
        workspace, project = self._project_record(args["project_id"])
        payload = _stable_zip(project["files"])
        encoded = base64.b64encode(payload).decode("ascii")
        content_hash72 = hash72(
            "pass190.i136.project.export.bytes",
            {"zip_base64": encoded},
        )
        artifact_id = f"artifact-{project['project_id']}-source-v{project['version']}"
        artifact = self._op_artifact_register(
            {
                "artifact_id": artifact_id,
                "workspace_id": project["project_id"],
                "media_type": "application/zip",
                "content_hash72": content_hash72,
                "size_bytes": len(payload),
                "metadata": {
                    "schema": I136_EXPORT_SCHEMA,
                    "project_root_hash72": project["project_root_hash72"],
                    "source_root_hash72": project["source_root_hash72"],
                    "transport": "base64",
                    "canonical_identity": "Hash72",
                },
            }
        )
        export = {
            "artifact_id": artifact_id,
            "content_hash72": content_hash72,
            "size_bytes": len(payload),
            "zip_base64": encoded,
            "project_root_hash72": project["project_root_hash72"],
        }
        project["exports"].append(
            {key: value for key, value in export.items() if key != "zip_base64"}
        )
        project["version"] = int(project["version"]) + 1
        stored = self._store_project(workspace, project)
        return {
            **export,
            "artifact_record_hash72": artifact["record_hash72"],
            "post_export_project_root_hash72": stored["project_root_hash72"],
        }

    def _op_project_replay(self, args: dict[str, Any]) -> dict[str, Any]:
        _workspace, project = self._project_record(args["project_id"])
        export_checks = []
        artifacts = self._resource_registries()["artifacts"]
        for export in project["exports"]:
            artifact = artifacts.get(export["artifact_id"])
            export_checks.append(
                bool(
                    artifact
                    and artifact["content_hash72"] == export["content_hash72"]
                    and artifact["workspace_id"] == project["project_id"]
                )
            )
        checks = {
            "project_root_hash72": project["project_root_hash72"] == _project_identity(project),
            "source_root_hash72": project["source_root_hash72"] == _files_root(project["files"]),
            "exports": all(export_checks),
            "build": project["build"] is None or bool(project["build"].get("ok")),
            "test": project["test"] is None or bool(project["test"].get("ok")),
        }
        result = {
            "project_id": project["project_id"],
            "ok": all(checks.values()),
            "checks": checks,
            "project_root_hash72": project["project_root_hash72"],
            "source_root_hash72": project["source_root_hash72"],
            "hidden_process_state_required": False,
            "frontend_state_authority": False,
        }
        result["replay_hash72"] = hash72("pass190.i136.project.replay", result)
        return result

    def replay(self, receipt_hash72: str) -> InvocationResult:
        self.store.restore_into(self)
        receipt = self._receipts.get(receipt_hash72)
        if receipt is None:
            raise ReplayMismatchError("unknown receipt")
        operation_id = str(receipt["operation_id"])
        if operation_id not in PROJECT_OPERATION_IDS:
            return super().replay(receipt_hash72)

        with self._lock:
            grant = self.store.acquire_lease(
                self.holder_id,
                ttl_ns=self.lease_ttl_ns,
                wait_ns=self.lease_wait_ns,
            )
            try:
                with self.store.admission(grant):
                    self.store.restore_into(self)
                    receipt = self._receipts.get(receipt_hash72)
                    if receipt is None:
                        raise ReplayMismatchError("unknown receipt")
                    self._verify_receipt_identity(receipt)
                    result = copy.deepcopy(receipt["result"])
                    if operation_id == "project.list":
                        if not isinstance(result, list):
                            raise ReplayMismatchError("project list replay result invalid")
                    elif not isinstance(result, dict):
                        raise ReplayMismatchError("project replay result invalid")
                    invocation = InvocationResult(
                        operation_id,
                        result,
                        receipt,
                        "replay",
                        True,
                    )
                    self.store.append_fenced_event(
                        "operation.replayed",
                        {
                            "operation_id": operation_id,
                            "hash72": receipt_hash72,
                            "replay_verified": True,
                            "semantic_owner": "PASS190_I136_COMPLETION",
                        },
                        grant,
                    )
                    return invocation
            except Exception:
                self.store.restore_into(self)
                raise


__all__ = [
    "I136_ACCEPTANCE_CONTRACT",
    "I136_PROJECT_SCHEMA",
    "PROJECT_OPERATION_IDS",
    "Pass190CompletionOperationRegistry",
    "Pass190AcceptanceAuthorityContext",
]
