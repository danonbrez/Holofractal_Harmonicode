"""
HHS Runtime Workspace Project v1
================================

Canonical project model for the Visual Runtime OS workspace.  A project is a
manifest of canonical workspace objects, roots, receipt tips, layout state, and
reconstruction recipes; it is not a plain browser-side directory dump.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Iterable, List, Mapping, Optional
import time
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import (
    AUTHORITY,
    VERSION,
    create_workspace_object,
    hash72,
    validate_workspace_object,
    workspace_object_reference,
)

PROJECT_SCHEMA = "HHS_RUNTIME_WORKSPACE_PROJECT_V1"
MANIFEST_SCHEMA = "HHS_WORKSPACE_PERSISTENCE_MANIFEST_V1"
STATUS_SCHEMA = "HHS_VISUAL_RUNTIME_OS_WORKSPACE_V1"

PROJECT_STATUS_STATES = [
    "WORKSPACE_DISCONNECTED",
    "WORKSPACE_CONNECTING",
    "WORKSPACE_READ_ONLY",
    "WORKSPACE_LIVE",
    "WORKSPACE_EXECUTING",
    "WORKSPACE_REPLAYING",
    "WORKSPACE_RECONSTRUCTING",
    "WORKSPACE_DEGRADED",
    "WORKSPACE_AUTHORITY_REJECTED",
]


def _now_ms() -> int:
    return int(time.time() * 1000)


def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"


@dataclass(frozen=True)
class WorkspaceProject:
    schema: str = PROJECT_SCHEMA
    version: str = VERSION
    project_id: str = field(default_factory=lambda: _unique("project"))
    name: str = "Untitled HHS Workspace"
    status: str = "WORKSPACE_LIVE"
    object_registry: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    object_order: List[str] = field(default_factory=list)
    receipt_tip_hash72: str = ""
    semantic_index_root_hash72: str = ""
    workspace_layout_root_hash72: str = ""
    authority: str = AUTHORITY
    created_at_unix_ms: int = field(default_factory=_now_ms)
    updated_at_unix_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_workspace_project(name: str = "Untitled HHS Workspace") -> Dict[str, Any]:
    project = WorkspaceProject(name=name).to_dict()
    project["object_registry_root_hash72"] = hash72("HHS_WORKSPACE_EMPTY_OBJECT_REGISTRY_V1", {})
    project["semantic_index_root_hash72"] = hash72("HHS_WORKSPACE_EMPTY_SEMANTIC_INDEX_V1", {})
    project["workspace_layout_root_hash72"] = hash72("HHS_WORKSPACE_LAYOUT_STATE_V1", {"layout": "default_docked_panels"})
    project["project_root_hash72"] = hash72(PROJECT_SCHEMA, project)
    project["receipt_tip_hash72"] = project["project_root_hash72"]
    project["manifest"] = build_project_manifest(project)
    return project


def build_project_manifest(project: Mapping[str, Any]) -> Dict[str, Any]:
    registry = dict(project.get("object_registry") or {})
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "version": VERSION,
        "project_id": project.get("project_id"),
        "project_root_hash72": project.get("project_root_hash72") or hash72(PROJECT_SCHEMA, dict(project)),
        "object_registry_root_hash72": hash72("HHS_WORKSPACE_OBJECT_REGISTRY_V1", registry),
        "receipt_tip_hash72": project.get("receipt_tip_hash72") or "",
        "artifact_registry_root_hash72": hash72("HHS_WORKSPACE_ARTIFACT_REGISTRY_V1", {}),
        "semantic_index_root_hash72": project.get("semantic_index_root_hash72") or hash72("HHS_WORKSPACE_SEMANTIC_INDEX_V1", {}),
        "workspace_layout_root_hash72": project.get("workspace_layout_root_hash72") or hash72("HHS_WORKSPACE_LAYOUT_STATE_V1", {}),
        "reconstruction_recipe_id": f"recipe:{project.get('project_id', 'unknown')}:manifest",
        "storage_mode": "ROOTS_PLUS_CANONICAL_OBJECTS",
        "expanded_metadata_retained": False,
        "authority": AUTHORITY,
    }
    manifest["manifest_root_hash72"] = hash72(MANIFEST_SCHEMA, manifest)
    return manifest


def register_project_object(project: Mapping[str, Any], obj: Mapping[str, Any]) -> Dict[str, Any]:
    validation = validate_workspace_object(obj)
    if not validation.get("ok"):
        return {
            "schema": "HHS_WORKSPACE_PROJECT_OBJECT_REGISTRATION_REJECTION_V1",
            "version": VERSION,
            "ok": False,
            "status": "REJECT_WORKSPACE_OBJECT_REGISTRATION",
            "validation": validation,
        }
    updated = dict(project)
    registry = dict(updated.get("object_registry") or {})
    object_id = str(obj.get("object_id"))
    registry[object_id] = dict(obj)
    order = list(updated.get("object_order") or [])
    if object_id not in order:
        order.append(object_id)
    order = sorted(order)
    updated["object_registry"] = registry
    updated["object_order"] = order
    updated["object_registry_root_hash72"] = hash72("HHS_WORKSPACE_OBJECT_REGISTRY_V1", {k: registry[k] for k in sorted(registry)})
    updated["updated_at_unix_ms"] = _now_ms()
    updated["project_root_hash72"] = hash72(PROJECT_SCHEMA, updated)
    updated["receipt_tip_hash72"] = hash72("HHS_WORKSPACE_PROJECT_REGISTER_OBJECT_RECEIPT_V1", {
        "project_root_hash72": updated["project_root_hash72"],
        "object_id": object_id,
        "object_root_hash72": obj.get("object_root_hash72"),
    })
    updated["manifest"] = build_project_manifest(updated)
    return {
        "schema": "HHS_WORKSPACE_PROJECT_OBJECT_REGISTRATION_V1",
        "version": VERSION,
        "ok": True,
        "status": "WORKSPACE_OBJECT_REGISTERED",
        "project": updated,
        "object_reference": workspace_object_reference(obj),
        "receipt_hash72": updated["receipt_tip_hash72"],
    }


def open_workspace_project(project: Mapping[str, Any]) -> Dict[str, Any]:
    manifest = dict(project.get("manifest") or build_project_manifest(project))
    reasons: List[str] = []
    if manifest.get("schema") != MANIFEST_SCHEMA:
        reasons.append("REJECT_PROJECT_MANIFEST_INVALID")
    if manifest.get("expanded_metadata_retained"):
        reasons.append("REJECT_WORKSPACE_PERSISTENCE_EXPANDED_METADATA")
    if manifest.get("authority") != AUTHORITY:
        reasons.append("REJECT_WORKSPACE_AUTHORITY_UNAVAILABLE")
    ok = not reasons
    return {
        "schema": "HHS_WORKSPACE_PROJECT_OPEN_RESULT_V1",
        "version": VERSION,
        "ok": ok,
        "status": "WORKSPACE_LIVE" if ok else "WORKSPACE_AUTHORITY_REJECTED",
        "project_id": project.get("project_id"),
        "manifest": manifest,
        "reasons": reasons,
    }


def fork_workspace_project(project: Mapping[str, Any], name: Optional[str] = None) -> Dict[str, Any]:
    fork = dict(project)
    parent_root = fork.get("project_root_hash72")
    fork["project_id"] = _unique("project")
    fork["name"] = name or f"{project.get('name', 'Workspace')} fork"
    fork["parent_project_root_hash72"] = parent_root
    fork["fork_root_hash72"] = hash72("HHS_WORKSPACE_PROJECT_FORK_V1", {"parent": parent_root, "fork_id": fork["project_id"]})
    fork["project_root_hash72"] = hash72(PROJECT_SCHEMA, fork)
    fork["manifest"] = build_project_manifest(fork)
    return {
        "schema": "HHS_WORKSPACE_PROJECT_FORK_RESULT_V1",
        "version": VERSION,
        "ok": True,
        "status": "WORKSPACE_PROJECT_FORKED",
        "parent_project_root_hash72": parent_root,
        "project": fork,
    }


def runtime_workspace_project_self_test() -> Dict[str, Any]:
    project = create_workspace_project("Pass049 Workspace")
    obj = create_workspace_object(project_id=project["project_id"], payload="a²+b²=c²")
    registration = register_project_object(project, obj)
    opened = open_workspace_project(registration["project"])
    forked = fork_workspace_project(registration["project"])
    rejected = open_workspace_project({**registration["project"], "manifest": {"schema": MANIFEST_SCHEMA, "expanded_metadata_retained": True}})
    return {
        "schema": "HHS_RUNTIME_WORKSPACE_PROJECT_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(registration.get("ok") and opened.get("ok") and forked.get("ok") and not rejected.get("ok")),
        "project": registration["project"],
        "opened": opened,
        "forked": forked,
        "invalid_manifest_rejection": rejected,
        "workspace_states": PROJECT_STATUS_STATES,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(runtime_workspace_project_self_test(), indent=2, sort_keys=True, default=str))
