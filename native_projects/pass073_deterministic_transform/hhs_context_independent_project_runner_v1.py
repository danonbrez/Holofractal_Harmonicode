"""Context-independent native HHS project verification and replay runner.

The runner treats repository objects—not conversation state—as authoritative.
It validates the development capsule and source bindings before importing the
project entrypoint and replaying the expected semantic product root.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional
import hashlib
import importlib
import json

CAPSULE_SCHEMA = "HHS_CONTEXT_INDEPENDENT_NATIVE_DEVELOPMENT_CAPSULE_V1"
DEFAULT_CAPSULE = "PASS_073_CONTEXT_INDEPENDENT_DEVELOPMENT_CAPSULE.json"


class DevelopmentCapsuleError(RuntimeError):
    """Raised when repository-native resume state is incomplete or altered."""


def _repo_root(root: Optional[str | Path] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[2]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise DevelopmentCapsuleError(f"REJECT_NONCANONICAL_CAPSULE_PATH:{value}")
    return path


def load_development_capsule(
    root: Optional[str | Path] = None,
    capsule_relative_path: str = DEFAULT_CAPSULE,
) -> Dict[str, Any]:
    repo = _repo_root(root)
    path = repo / _relative_path(capsule_relative_path)
    if not path.is_file():
        raise DevelopmentCapsuleError(f"REJECT_DEVELOPMENT_CAPSULE_NOT_FOUND:{capsule_relative_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != CAPSULE_SCHEMA:
        raise DevelopmentCapsuleError("REJECT_DEVELOPMENT_CAPSULE_SCHEMA_MISMATCH")
    return payload


def verify_development_capsule(
    root: Optional[str | Path] = None,
    capsule: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    repo = _repo_root(root)
    value = dict(capsule or load_development_capsule(repo))
    if not value.get("restart_safe"):
        raise DevelopmentCapsuleError("REJECT_NON_RESTART_SAFE_PROJECT_STATE")
    if value.get("thread_context_required") or value.get("llm_context_window_required"):
        raise DevelopmentCapsuleError("REJECT_CONVERSATION_CONTEXT_AS_PROJECT_DEPENDENCY")
    if value.get("host_path_required"):
        raise DevelopmentCapsuleError("REJECT_HOST_PATH_AS_CANONICAL_PROJECT_IDENTITY")

    results = []
    for binding in value.get("source_bindings", []):
        relative = str(binding["relative_path"])
        path = repo / _relative_path(relative)
        if not path.is_file():
            raise DevelopmentCapsuleError(f"REJECT_SOURCE_BINDING_NOT_FOUND:{relative}")
        observed = _sha256(path)
        expected = str(binding["sha256"])
        if observed != expected:
            raise DevelopmentCapsuleError(
                f"REJECT_SOURCE_BINDING_DIGEST_MISMATCH:{relative}:expected={expected}:observed={observed}"
            )
        results.append({"relative_path": relative, "sha256": observed, "verified": True})

    manifest_relative = str(value["canonical_inputs_manifest_relative_path"])
    manifest_path = repo / _relative_path(manifest_relative)
    observed_manifest = _sha256(manifest_path)
    expected_manifest = str(value["canonical_inputs_manifest_sha256"])
    if observed_manifest != expected_manifest:
        raise DevelopmentCapsuleError(
            "REJECT_CAPSULE_CANONICAL_INPUT_MANIFEST_DIGEST_MISMATCH"
        )

    resume = dict(value.get("resume_contract", {}))
    required_resume = {"python_module", "callable", "typed_input", "expected_product_root_hash72"}
    if not required_resume <= set(resume):
        raise DevelopmentCapsuleError("REJECT_INCOMPLETE_CAPSULE_RESUME_CONTRACT")

    return {
        "schema": "HHS_CONTEXT_INDEPENDENT_DEVELOPMENT_CAPSULE_VERIFICATION_V1",
        "ok": True,
        "pass_id": value.get("pass_id"),
        "project_id": value.get("project_id"),
        "source_binding_count": len(results),
        "source_bindings": results,
        "canonical_input_manifest_verified": True,
        "restart_safe": True,
        "thread_context_required": False,
        "host_path_required": False,
        "repository_state_is_authoritative": True,
        "development_capsule_root_hash72": value.get("development_capsule_root_hash72"),
    }


def resume_project_from_capsule(
    root: Optional[str | Path] = None,
    *,
    resolution_mode: str = "AUTO",
    capsule_relative_path: str = DEFAULT_CAPSULE,
) -> Dict[str, Any]:
    repo = _repo_root(root)
    capsule = load_development_capsule(repo, capsule_relative_path)
    verification = verify_development_capsule(repo, capsule)
    contract = dict(capsule["resume_contract"])
    module = importlib.import_module(str(contract["python_module"]))
    function = getattr(module, str(contract["callable"]), None)
    if not callable(function):
        raise DevelopmentCapsuleError("REJECT_CAPSULE_ENTRYPOINT_NOT_CALLABLE")

    bundle = function(
        dict(contract["typed_input"]),
        root=repo,
        write_artifacts=False,
        resolution_mode=resolution_mode,
    )
    observed = str(bundle["product_artifact"]["product_artifact_root_hash72"])
    expected = str(contract["expected_product_root_hash72"])
    matches = observed == expected
    return {
        "schema": "HHS_CONTEXT_INDEPENDENT_PROJECT_RESUME_RECEIPT_V1",
        "ok": verification["ok"] and bool(bundle["ok"]) and matches,
        "pass_id": capsule["pass_id"],
        "project_id": capsule["project_id"],
        "resolution_mode": bundle["execution_environment"]["execution_mode"],
        "expected_product_root_hash72": expected,
        "observed_product_root_hash72": observed,
        "product_root_matches": matches,
        "capsule_verified": verification["ok"],
        "thread_context_used": False,
        "host_path_used_as_identity": False,
        "foundation_delta": bundle["product_release_manifest"]["foundation_delta"],
    }
