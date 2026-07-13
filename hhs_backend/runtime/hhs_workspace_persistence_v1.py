"""Workspace persistence manifest helpers for Pass 049."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from hhs_backend.runtime.runtime_workspace_project_v1 import build_project_manifest, create_workspace_project, open_workspace_project
from hhs_backend.runtime.runtime_workspace_object_v1 import VERSION, AUTHORITY, hash72


def save_workspace_project(project: Mapping[str, Any]) -> Dict[str, Any]:
    manifest = build_project_manifest(project)
    if manifest.get("expanded_metadata_retained"):
        return {"schema": "HHS_WORKSPACE_SAVE_REJECTION_V1", "ok": False, "status": "REJECT_WORKSPACE_PERSISTENCE_EXPANDED_METADATA"}
    save = {
        "schema": "HHS_WORKSPACE_PROJECT_SAVE_RESULT_V1",
        "version": VERSION,
        "ok": True,
        "status": "WORKSPACE_PROJECT_SAVED",
        "project_id": project.get("project_id"),
        "manifest": manifest,
        "atomic_manifest_commit": True,
        "layout_state_separate_from_source_truth": True,
        "authority": AUTHORITY,
    }
    save["save_receipt_hash72"] = hash72("HHS_WORKSPACE_PROJECT_SAVE_RESULT_V1", save)
    return save


def verify_workspace_manifest(manifest: Mapping[str, Any]) -> Dict[str, Any]:
    reasons = []
    if manifest.get("schema") != "HHS_WORKSPACE_PERSISTENCE_MANIFEST_V1":
        reasons.append("REJECT_PROJECT_MANIFEST_INVALID")
    if manifest.get("expanded_metadata_retained"):
        reasons.append("REJECT_WORKSPACE_PERSISTENCE_EXPANDED_METADATA")
    if manifest.get("authority") != AUTHORITY:
        reasons.append("REJECT_WORKSPACE_AUTHORITY_UNAVAILABLE")
    ok = not reasons
    return {
        "schema": "HHS_WORKSPACE_MANIFEST_VERIFICATION_V1",
        "version": VERSION,
        "ok": ok,
        "status": "WORKSPACE_MANIFEST_VERIFIED" if ok else "REJECT_PROJECT_MANIFEST_INVALID",
        "reasons": reasons,
        "manifest_root_hash72": manifest.get("manifest_root_hash72"),
    }


def workspace_persistence_self_test() -> Dict[str, Any]:
    project = create_workspace_project("Persistence Workspace")
    save = save_workspace_project(project)
    verified = verify_workspace_manifest(save["manifest"])
    bad = verify_workspace_manifest({**save["manifest"], "expanded_metadata_retained": True})
    opened = open_workspace_project({**project, "manifest": save["manifest"]})
    return {
        "schema": "HHS_WORKSPACE_PERSISTENCE_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(save.get("ok") and verified.get("ok") and opened.get("ok") and not bad.get("ok")),
        "save": save,
        "verified": verified,
        "bad_manifest_rejection": bad,
        "opened": opened,
        "constraint": "PROJECT_IS_NOT_A_DIRECTORY_DUMP",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(workspace_persistence_self_test(), indent=2, sort_keys=True, default=str))
