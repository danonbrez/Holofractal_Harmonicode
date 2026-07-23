"""Context-independent replay for the Pass 075 native language product."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional
import hashlib
import json

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root
from .hhs_pass075_contracts_v1 import LANGUAGE_REPLAY_CAPSULE_SCHEMA
from .hhs_pass075_workspace_runtime_v1 import HHSNativeLanguageWorkspaceRuntime

DEFAULT_CAPSULE = "PASS_075_LANGUAGE_REPLAY_CAPSULE.json"


class Pass075ReplayError(RuntimeError):
    pass


def _root(root=None) -> Path:
    return Path(root).resolve() if root else Path(__file__).resolve().parents[2]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_capsule(root=None, relative_path: str = DEFAULT_CAPSULE) -> Dict[str, Any]:
    return json.loads((_root(root) / relative_path).read_text(encoding="utf-8"))


def verify_capsule(root=None, capsule: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    repo = _root(root)
    value = dict(capsule or load_capsule(repo))
    if value.get("schema") != LANGUAGE_REPLAY_CAPSULE_SCHEMA:
        raise Pass075ReplayError("REJECT_PASS075_REPLAY_CAPSULE_SCHEMA")
    unsigned = dict(value)
    supplied = str(unsigned.pop("capsule_root_hash72", ""))
    observed = product_root("pass075_language_replay_capsule", unsigned)
    if supplied != observed:
        raise Pass075ReplayError("REJECT_PASS075_REPLAY_CAPSULE_ROOT_MISMATCH")
    checked_sources = []
    checked_artifacts = []
    for field, destination in (("source_bindings", checked_sources), ("artifact_bindings", checked_artifacts)):
        for binding in value.get(field, []):
            rel = str(binding.get("relative_path") or "")
            if not rel or rel.startswith(("/", "\\")) or ":\\" in rel or ".." in rel.split("/"):
                raise Pass075ReplayError(f"REJECT_NON_RELATIVE_BINDING:{rel}")
            path = repo / rel
            if not path.is_file():
                raise Pass075ReplayError(f"REJECT_MISSING_BINDING:{rel}")
            observed_sha = _sha(path)
            if observed_sha != binding.get("sha256"):
                code = "SOURCE" if field == "source_bindings" else "ARTIFACT"
                raise Pass075ReplayError(f"REJECT_{code}_BINDING_DIGEST_MISMATCH:{rel}")
            destination.append(rel)
    release_rel = str(value.get("release_bundle_relative_path") or "")
    if release_rel:
        release = json.loads((repo / release_rel).read_text(encoding="utf-8"))
        release_body = dict(release)
        release_root = str(release_body.pop("product_root_hash72", ""))
        observed_release_root = product_root("pass075_release_bundle", release_body)
        if release_root != observed_release_root or release_root != value.get("expected_product_root_hash72"):
            raise Pass075ReplayError("REJECT_PASS075_RELEASE_PRODUCT_ROOT_MISMATCH")
    return {
        "ok": True,
        "capsule_root_hash72": supplied,
        "checked_source_count": len(checked_sources),
        "checked_artifact_count": len(checked_artifacts),
        "checked_sources": checked_sources,
        "checked_artifacts": checked_artifacts,
        "thread_context_used": False,
        "llm_context_window_used": False,
        "host_path_used_as_identity": False,
    }


def replay_language_workspace(root=None, capsule: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    repo = _root(root)
    value = dict(capsule or load_capsule(repo))
    verification = verify_capsule(repo, value)
    runtime = HHSNativeLanguageWorkspaceRuntime(initial_state=value["workspace_state"])
    observed = runtime.snapshot()["workspace_state_root_hash72"]
    expected = value["expected_workspace_state_root_hash72"]
    if observed != expected:
        raise Pass075ReplayError("REJECT_PASS075_REPLAY_STATE_ROOT_MISMATCH")
    ir_ref = value["expected_typed_ir_ref"]
    ir = runtime.typed_ir_objects.get(ir_ref)
    if not ir or ir.get("ir_root_hash72") != value["expected_typed_ir_root_hash72"]:
        raise Pass075ReplayError("REJECT_PASS075_REPLAY_TYPED_IR_MISMATCH")
    plan_ref = value["expected_test_plan_ref"]
    plan = runtime.test_acceleration_plans.get(plan_ref)
    if not plan or plan.get("test_plan_root_hash72") != value["expected_test_plan_root_hash72"]:
        raise Pass075ReplayError("REJECT_PASS075_REPLAY_TEST_PLAN_MISMATCH")
    receipt = {
        "schema": "HHS_PASS_075_LANGUAGE_REPLAY_RECEIPT_V1",
        "ok": True,
        "workspace_state_root_hash72": observed,
        "typed_ir_root_hash72": ir["ir_root_hash72"],
        "test_plan_root_hash72": plan["test_plan_root_hash72"],
        "source_binding_count": verification["checked_source_count"],
        "artifact_binding_count": verification["checked_artifact_count"],
        "product_root_hash72": value.get("expected_product_root_hash72", ""),
        "thread_context_used": False,
        "llm_context_window_used": False,
        "host_path_used_as_identity": False,
        "repository_state_authoritative": True,
    }
    receipt["replay_receipt_root_hash72"] = product_root("pass075_language_replay_receipt", receipt)
    return receipt


if __name__ == "__main__":
    print(json.dumps(replay_language_workspace(), indent=2, sort_keys=True, ensure_ascii=False))
