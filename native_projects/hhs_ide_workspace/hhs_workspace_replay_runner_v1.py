"""Context-independent Pass 074 workspace verification and replay runner."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional
import hashlib
import json

from .hhs_native_workspace_project_v1 import HHSNativeWorkspaceRuntime
from .hhs_workspace_contracts_v1 import REPLAY_CAPSULE_SCHEMA, product_root

DEFAULT_CAPSULE = "native_projects/hhs_ide_workspace/artifacts/PASS_074_WORKSPACE_REPLAY_CAPSULE.json"


class ReplayCapsuleError(RuntimeError):
    pass


def _root(root=None):
    return Path(root).resolve() if root else Path(__file__).resolve().parents[2]


def _sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(value: str):
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ReplayCapsuleError("REJECT_NONCANONICAL_REPLAY_PATH")
    return path


def load_capsule(root=None, relative_path: str = DEFAULT_CAPSULE):
    path = _root(root) / _relative(relative_path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != REPLAY_CAPSULE_SCHEMA:
        raise ReplayCapsuleError("REJECT_REPLAY_CAPSULE_SCHEMA")
    return value


def verify_capsule(root=None, capsule: Optional[Mapping[str, Any]] = None):
    repo = _root(root)
    value = dict(capsule or load_capsule(repo))
    if value.get("thread_context_required") or value.get("llm_context_window_required") or value.get("host_path_required"):
        raise ReplayCapsuleError("REJECT_CONTEXT_OR_HOST_DEPENDENCY")

    supplied_capsule_root = str(value.get("workspace_replay_capsule_root_hash72") or "")
    capsule_root_matches = True
    if supplied_capsule_root:
        unsigned = dict(value)
        unsigned.pop("workspace_replay_capsule_root_hash72", None)
        observed_capsule_root = product_root("pass074_workspace_replay_capsule", unsigned)
        capsule_root_matches = observed_capsule_root == supplied_capsule_root
        if not capsule_root_matches:
            raise ReplayCapsuleError("REJECT_REPLAY_CAPSULE_ROOT_MISMATCH")

    verified = []
    for item in value.get("source_bindings", []):
        path = repo / _relative(str(item["relative_path"]))
        observed = _sha(path)
        if observed != item["sha256"]:
            raise ReplayCapsuleError(f"REJECT_SOURCE_DIGEST:{item['relative_path']}")
        verified.append(item["relative_path"])

    product_root_matches = True
    bundle_path_value = str(value.get("release_bundle_relative_path") or "")
    if bundle_path_value:
        bundle = json.loads((repo / _relative(bundle_path_value)).read_text(encoding="utf-8"))
        product_root_matches = bundle.get("product_root_hash72") == value.get("expected_product_root_hash72")
        if not product_root_matches:
            raise ReplayCapsuleError("REJECT_REPLAY_PRODUCT_ROOT_MISMATCH")

    return {
        "ok": True,
        "source_binding_count": len(verified),
        "capsule_root_matches": capsule_root_matches,
        "product_root_matches": product_root_matches,
        "thread_context_used": False,
        "host_path_used_as_identity": False,
    }


def replay_workspace(root=None, capsule: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    value = dict(capsule or load_capsule(root))
    verification = verify_capsule(root, value)
    runtime = HHSNativeWorkspaceRuntime(initial_state=value["workspace_state"])
    observed = runtime.snapshot()["workspace_state_root_hash72"]
    expected = value["expected_workspace_state_root_hash72"]
    return {
        "schema": "HHS_WORKSPACE_REPLAY_RECEIPT_V1",
        "ok": verification["ok"] and observed == expected,
        "expected_workspace_state_root_hash72": expected,
        "observed_workspace_state_root_hash72": observed,
        "state_root_matches": observed == expected,
        "capsule_root_matches": verification["capsule_root_matches"],
        "product_root_matches": verification["product_root_matches"],
        "thread_context_used": False,
        "host_path_used_as_identity": False,
        "repository_state_authoritative": True,
        "platform_foundation_modified": False,
    }
