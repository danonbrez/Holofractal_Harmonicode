"""Context-independent replay for the Pass 077 compiler workspace."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root, stable
from .hhs_pass077_contracts_v1 import REPLAY_CAPSULE_SCHEMA
from .hhs_pass077_program_graph_v1 import build_program_graph
from .hhs_pass077_workspace_runtime_v1 import build_pass077_release_bundle

DEFAULT_CAPSULE = "native_projects/hhs_compiler_artifact_pipeline/artifacts/PASS_077_COMPILER_REPLAY_CAPSULE.json"

class Pass077ReplayError(RuntimeError):
    pass


def _root(root=None) -> Path:
    return Path(root).resolve() if root else Path(__file__).resolve().parents[2]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_replay_capsule(root=None, *, bundle: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    repo = _root(root); release = stable(bundle or build_pass077_release_bundle())
    source_paths = [node["relative_path"] for node in build_program_graph()["nodes"] if node["kind"] == "PASS077_NATIVE_MODULE"]
    artifact_paths = [
        "native_projects/hhs_compiler_artifact_pipeline/artifacts/HHS_PASS_077_COMPILER_ARTIFACT_PIPELINE_RELEASE_BUNDLE.json",
        "native_projects/hhs_compiler_artifact_pipeline/artifacts/PASS_077_REGISTERED_TARGET_CONTRACT.json",
        "native_projects/hhs_compiler_artifact_pipeline/artifacts/PASS_077_EQUIVALENCE_RECEIPT.json",
        "native_projects/hhs_compiler_artifact_pipeline/artifacts/PASS_077_LINEAGE_CERTIFICATE.json",
        "native_projects/hhs_compiler_artifact_pipeline/artifacts/PASS_077_ADMITTED_ARTIFACT_PACKAGE.hhspkg",
    ]
    body = {
        "schema": REPLAY_CAPSULE_SCHEMA,
        "pass_id": "PASS_077",
        "parent_pass": "PASS_076",
        "frozen_platform_pass": "PASS_072",
        "source_bindings": [{"relative_path": path, "sha256": _sha(repo / path)} for path in sorted(source_paths)],
        "artifact_bindings": [{"relative_path": path, "sha256": _sha(repo / path)} for path in sorted(artifact_paths)],
        "expected_product_root_hash72": release["product_root_hash72"],
        "expected_workspace_state_root_hash72": release["workspace_state"]["workspace_state_root_hash72"],
        "expected_artifact_payload_root_hash72": release["workspace_state"]["compiled_artifacts"]["artifact:pass077:portable"]["artifact_payload_root_hash72"],
        "expected_package_root_hash72": release["workspace_state"]["export_packages"]["package:pass077:portable"]["package_root_hash72"],
        "expected_lineage_root_hash72": release["workspace_state"]["lineage_certificates"]["lineage:pass077:portable"]["lineage_root_hash72"],
        "expected_equivalence_root_hash72": release["workspace_state"]["equivalence_receipts"]["equivalence:pass077:portable"]["receipt_root_hash72"],
        "expected_program_graph_root_hash72": build_program_graph()["program_graph_root_hash72"],
        "thread_context_required": False,
        "llm_context_window_required": False,
        "host_path_used_as_identity": False,
        "repository_state_authoritative": True,
    }
    body["capsule_root_hash72"] = product_root("pass077_replay_capsule", body)
    return stable(body)


def load_capsule(root=None, relative_path: str = DEFAULT_CAPSULE) -> Dict[str, Any]:
    return json.loads((_root(root) / relative_path).read_text(encoding="utf-8"))


def verify_capsule(root=None, capsule: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    repo = _root(root); value = stable(capsule or load_capsule(repo)); body = dict(value); supplied = body.pop("capsule_root_hash72", "")
    if supplied != product_root("pass077_replay_capsule", body):
        raise Pass077ReplayError("REJECT_PASS077_REPLAY_CAPSULE_ROOT_MISMATCH")
    mismatches = []
    for binding in [*value.get("source_bindings", []), *value.get("artifact_bindings", [])]:
        path = repo / binding["relative_path"]
        if not path.is_file() or _sha(path) != binding["sha256"]:
            mismatches.append(binding["relative_path"])
    if mismatches:
        raise Pass077ReplayError("REJECT_PASS077_REPLAY_BINDING_MISMATCH:" + ",".join(mismatches))
    return {"status": "PASS", "capsule_root_hash72": supplied, "verified_source_bindings": len(value["source_bindings"]), "verified_artifact_bindings": len(value["artifact_bindings"])}


def replay_compiler_workspace(root=None, capsule: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    value = stable(capsule or load_capsule(root)); verification = verify_capsule(root, value); observed = build_pass077_release_bundle(); graph = build_program_graph()
    comparisons = {
        "product_root_matches": observed["product_root_hash72"] == value["expected_product_root_hash72"],
        "workspace_state_root_matches": observed["workspace_state"]["workspace_state_root_hash72"] == value["expected_workspace_state_root_hash72"],
        "artifact_payload_root_matches": observed["workspace_state"]["compiled_artifacts"]["artifact:pass077:portable"]["artifact_payload_root_hash72"] == value["expected_artifact_payload_root_hash72"],
        "package_root_matches": observed["workspace_state"]["export_packages"]["package:pass077:portable"]["package_root_hash72"] == value["expected_package_root_hash72"],
        "lineage_root_matches": observed["workspace_state"]["lineage_certificates"]["lineage:pass077:portable"]["lineage_root_hash72"] == value["expected_lineage_root_hash72"],
        "equivalence_root_matches": observed["workspace_state"]["equivalence_receipts"]["equivalence:pass077:portable"]["receipt_root_hash72"] == value["expected_equivalence_root_hash72"],
        "program_graph_root_matches": graph["program_graph_root_hash72"] == value["expected_program_graph_root_hash72"],
    }
    result = {
        "schema": "HHS_PASS_077_CONTEXT_INDEPENDENT_REPLAY_V1",
        "status": "PASS" if all(comparisons.values()) else "REJECTED",
        "comparisons": comparisons,
        "capsule_verification": verification,
        "thread_context_used": False,
        "llm_context_window_used": False,
        "host_path_used_as_identity": False,
    }
    result["replay_root_hash72"] = product_root("pass077_context_independent_replay", result)
    return stable(result)
