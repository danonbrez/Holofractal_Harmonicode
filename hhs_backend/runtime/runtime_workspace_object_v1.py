"""
HHS Runtime Workspace Object v1
===============================

Pass 049 common object envelope for the Visual Runtime OS workspace.  The
workspace is projection/request authority only; every canonical object carries
identity, provenance, Hash72/u^72 witnesses, lifecycle state, mutation roots,
and reconstruction metadata.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional
import time
import uuid

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness

VERSION = "PASS_049_HHS_VISUAL_RUNTIME_OS_WORKSPACE_V1"
AUTHORITY = "HHS_RUNTIME_WORKSPACE_AUTHORITY_V1"
OBJECT_SCHEMA = "HHS_RUNTIME_WORKSPACE_OBJECT_V1"
REFERENCE_SCHEMA = "HHS_WORKSPACE_OBJECT_REFERENCE_V1"
RECONSTRUCTION_RECIPE_SCHEMA = "HHS_WORKSPACE_RECONSTRUCTION_RECIPE_V1"

OBJECT_TYPES = [
    "PROJECT",
    "DIRECTORY",
    "SOURCE_DOCUMENT",
    "SYMBOLIC_SOURCE_DOCUMENT",
    "MULTIMODAL_OBJECT",
    "SEMANTIC_MEMORY_OBJECT",
    "RUNTIME_GRAPH_OBJECT",
    "COMPILED_ARTIFACT",
    "EMULATOR_SESSION",
    "RECEIPT_CHAIN",
    "LEDGER_VIEW",
    "REPLAY_BRANCH",
    "WORKSPACE_SNAPSHOT",
    "EXTERNAL_REFERENCE",
]

LIFECYCLE_STATES = [
    "INGRESSED",
    "UNRESOLVED",
    "INDEXED",
    "PROJECTED",
    "EDITABLE",
    "DIRTY_PRESENTATION_ONLY",
    "MUTATION_PENDING",
    "MUTATION_ADMITTED",
    "MUTATION_REJECTED",
    "COMPILED",
    "EXECUTABLE",
    "EMULATING",
    "PAUSED",
    "SNAPSHOTTED",
    "COMPACTED",
    "ARCHIVED",
    "TOMBSTONED",
    "RECONSTRUCTING",
    "CORRUPT_REJECTED",
    "ACTIVE",
]

PRESENTATION_ONLY_STATES = [
    "panel.resize",
    "panel.move",
    "canvas.zoom",
    "canvas.pan",
    "selection.change",
    "editor.cursor.move",
]


def hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def _now_ms() -> int:
    return int(time.time() * 1000)


def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"


@dataclass(frozen=True)
class WorkspaceObjectEnvelope:
    schema: str = OBJECT_SCHEMA
    version: str = VERSION
    object_id: str = field(default_factory=lambda: _unique("object"))
    project_id: str = "project:default"
    object_type: str = "SYMBOLIC_SOURCE_DOCUMENT"
    modality: str = "HARMONICODE_SOURCE"
    name: str = "main.hhs"
    source_parent_ids: List[str] = field(default_factory=list)
    derived_child_ids: List[str] = field(default_factory=list)
    canonical_payload_ref: str = "workspace-blob://unresolved"
    source_root_hash72: str = ""
    current_root_hash72: str = ""
    schema_id: str = "HHS_SYMBOLIC_SOURCE_DOCUMENT_V1"
    lifecycle_state: str = "ACTIVE"
    mutation_sequence: int = 0
    receipt_tip_hash72: str = ""
    reconstruction_recipe_id: str = ""
    authority: str = AUTHORITY
    source_provenance: Dict[str, Any] = field(default_factory=dict)
    created_at_unix_ms: int = field(default_factory=_now_ms)
    updated_at_unix_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_reconstruction_recipe(
    *,
    object_id: str,
    source_root_hash72: str,
    steps: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    recipe = {
        "schema": RECONSTRUCTION_RECIPE_SCHEMA,
        "version": VERSION,
        "recipe_id": _unique("recipe"),
        "object_id": object_id,
        "source_root_hash72": source_root_hash72,
        "steps": [dict(step) for step in (steps or [])],
        "expanded_metadata_retained": False,
        "authority": AUTHORITY,
    }
    recipe["recipe_root_hash72"] = hash72(RECONSTRUCTION_RECIPE_SCHEMA, recipe)
    return recipe


def create_workspace_object(
    *,
    project_id: str = "project:default",
    object_type: str = "SYMBOLIC_SOURCE_DOCUMENT",
    modality: str = "HARMONICODE_SOURCE",
    name: str = "main.hhs",
    payload: Any = "",
    schema_id: str = "HHS_SYMBOLIC_SOURCE_DOCUMENT_V1",
    source_parent_ids: Optional[Iterable[str]] = None,
    lifecycle_state: str = "ACTIVE",
    source_provenance: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    source_root = hash72("HHS_WORKSPACE_OBJECT_SOURCE_V1", {
        "project_id": project_id,
        "name": name,
        "modality": modality,
        "payload": payload,
    })
    object_id = _unique("object")
    recipe = build_reconstruction_recipe(
        object_id=object_id,
        source_root_hash72=source_root,
        steps=[{
            "operation": "reconstruct_from_canonical_payload_ref",
            "payload_policy": "ROOT_PLUS_CANONICAL_SOURCE_OBJECT",
        }],
    )
    envelope = WorkspaceObjectEnvelope(
        object_id=object_id,
        project_id=project_id,
        object_type=object_type,
        modality=modality,
        name=name,
        source_parent_ids=list(source_parent_ids or []),
        canonical_payload_ref=f"workspace-blob://{source_root}",
        source_root_hash72=source_root,
        current_root_hash72=source_root,
        schema_id=schema_id,
        lifecycle_state=lifecycle_state,
        receipt_tip_hash72=source_root,
        reconstruction_recipe_id=recipe["recipe_id"],
        source_provenance=dict(source_provenance or {}),
    ).to_dict()
    envelope["reconstruction_recipe"] = recipe
    envelope["object_root_hash72"] = hash72(OBJECT_SCHEMA, envelope)
    return envelope


def workspace_object_reference(obj: Mapping[str, Any]) -> Dict[str, Any]:
    ref = {
        "schema": REFERENCE_SCHEMA,
        "version": VERSION,
        "project_id": obj.get("project_id"),
        "object_id": obj.get("object_id"),
        "object_type": obj.get("object_type"),
        "source_uri": obj.get("source_provenance", {}).get("source_uri") or obj.get("canonical_payload_ref"),
        "root_hash72": obj.get("current_root_hash72") or obj.get("object_root_hash72"),
        "lifecycle_state": obj.get("lifecycle_state"),
        "authority": AUTHORITY,
    }
    ref["reference_root_hash72"] = hash72(REFERENCE_SCHEMA, ref)
    return ref


def validate_workspace_object(obj: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if obj.get("schema") != OBJECT_SCHEMA:
        reasons.append("REJECT_WORKSPACE_OBJECT_SCHEMA_MISMATCH")
    if not obj.get("object_id"):
        reasons.append("REJECT_WORKSPACE_OBJECT_UNKNOWN")
    if not obj.get("project_id"):
        reasons.append("REJECT_WORKSPACE_PROJECT_UNKNOWN")
    if obj.get("object_type") not in OBJECT_TYPES:
        reasons.append("REJECT_WORKSPACE_OBJECT_TYPE_UNKNOWN")
    if obj.get("lifecycle_state") not in LIFECYCLE_STATES:
        reasons.append("REJECT_WORKSPACE_OBJECT_LIFECYCLE_UNKNOWN")
    if not obj.get("source_root_hash72") or not obj.get("current_root_hash72"):
        reasons.append("REJECT_WORKSPACE_OBJECT_ROOT_MISMATCH")
    if obj.get("authority") != AUTHORITY:
        reasons.append("REJECT_WORKSPACE_AUTHORITY_UNAVAILABLE")
    if not obj.get("reconstruction_recipe_id"):
        reasons.append("REJECT_WORKSPACE_OBJECT_WITHOUT_RECONSTRUCTION_RECIPE")
    ok = not reasons
    return {
        "schema": "HHS_RUNTIME_WORKSPACE_OBJECT_VALIDATION_V1",
        "version": VERSION,
        "ok": ok,
        "status": "ADMIT_WORKSPACE_OBJECT" if ok else "REJECT_WORKSPACE_OBJECT",
        "reasons": sorted(dict.fromkeys(reasons)),
        "object_id": obj.get("object_id"),
        "object_root_hash72": obj.get("object_root_hash72") or hash72(OBJECT_SCHEMA, dict(obj)),
    }


def workspace_object_self_test() -> Dict[str, Any]:
    obj = create_workspace_object(payload="a²+b²=c²", source_provenance={"source_uri": "workspace://project/default/main.hhs"})
    validation = validate_workspace_object(obj)
    ref = workspace_object_reference(obj)
    rejected = validate_workspace_object({**obj, "authority": "LOCAL_FRONTEND_CACHE"})
    return {
        "schema": "HHS_RUNTIME_WORKSPACE_OBJECT_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(validation["ok"] and not rejected["ok"] and ref.get("reference_root_hash72")),
        "object": obj,
        "validation": validation,
        "reference": ref,
        "frontend_cache_authority_rejection": rejected,
        "hard_invariant": "NO_LOCAL_FRONTEND_CACHE_IS_AUTHORITATIVE",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(workspace_object_self_test(), indent=2, sort_keys=True, default=str))
