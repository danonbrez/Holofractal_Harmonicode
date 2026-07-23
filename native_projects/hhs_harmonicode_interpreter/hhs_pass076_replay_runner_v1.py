"""Context-independent replay for the Pass 076 interpreter and repair product."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional
import hashlib
import json

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root
from .hhs_exact_symbolic_interpreter_v1 import replay_execution
from .hhs_pass076_contracts_v1 import REPLAY_CAPSULE_SCHEMA, verify_rooted
from .hhs_pass076_workspace_runtime_v1 import HHSNativeInterpreterWorkspaceRuntime

DEFAULT_CAPSULE = "PASS_076_INTERPRETER_REPLAY_CAPSULE.json"


class Pass076ReplayError(RuntimeError):
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
    if value.get("schema") != REPLAY_CAPSULE_SCHEMA:
        raise Pass076ReplayError("REJECT_PASS076_REPLAY_CAPSULE_SCHEMA")
    unsigned = dict(value)
    supplied = str(unsigned.pop("capsule_root_hash72", ""))
    observed = product_root("pass076_interpreter_replay_capsule", unsigned)
    if supplied != observed:
        raise Pass076ReplayError("REJECT_PASS076_REPLAY_CAPSULE_ROOT_MISMATCH")
    checked_sources, checked_artifacts = [], []
    for field, destination in (("source_bindings", checked_sources), ("artifact_bindings", checked_artifacts)):
        for binding in value.get(field, []):
            rel = str(binding.get("relative_path") or "")
            if not rel or rel.startswith(("/", "\\")) or ":\\" in rel or ".." in rel.split("/"):
                raise Pass076ReplayError(f"REJECT_NON_RELATIVE_BINDING:{rel}")
            path = repo / rel
            if not path.is_file():
                raise Pass076ReplayError(f"REJECT_MISSING_BINDING:{rel}")
            if _sha(path) != binding.get("sha256"):
                code = "SOURCE" if field == "source_bindings" else "ARTIFACT"
                raise Pass076ReplayError(f"REJECT_{code}_BINDING_DIGEST_MISMATCH:{rel}")
            destination.append(rel)
    release_rel = str(value.get("release_bundle_relative_path") or "")
    release = json.loads((repo / release_rel).read_text(encoding="utf-8"))
    body = dict(release)
    release_root = str(body.pop("product_root_hash72", ""))
    if release_root != product_root("pass076_release_bundle", body):
        raise Pass076ReplayError("REJECT_PASS076_RELEASE_BUNDLE_ROOT_MISMATCH")
    if release_root != value.get("expected_product_root_hash72"):
        raise Pass076ReplayError("REJECT_PASS076_EXPECTED_PRODUCT_ROOT_MISMATCH")
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


def replay_interpreter_workspace(root=None, capsule: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    repo = _root(root)
    value = dict(capsule or load_capsule(repo))
    verification = verify_capsule(repo, value)
    runtime = HHSNativeInterpreterWorkspaceRuntime(initial_state=value["workspace_state"])
    observed_state = runtime.snapshot()["workspace_state_root_hash72"]
    if observed_state != value.get("expected_workspace_state_root_hash72"):
        raise Pass076ReplayError("REJECT_PASS076_REPLAY_STATE_ROOT_MISMATCH")
    run_ref = str(value.get("expected_execution_run_ref") or "")
    run = runtime.execution_runs.get(run_ref)
    if not run or run.get("execution_run_root_hash72") != value.get("expected_execution_run_root_hash72"):
        raise Pass076ReplayError("REJECT_PASS076_EXECUTION_RUN_MISMATCH")
    executable = runtime.executable_ir_objects.get(str(run.get("executable_ir_ref") or ""))
    if not executable:
        raise Pass076ReplayError("REJECT_PASS076_EXECUTABLE_IR_MISSING")
    replay = replay_execution(run, executable)
    if not replay.get("matches"):
        raise Pass076ReplayError("REJECT_PASS076_EXECUTION_REPLAY_MISMATCH")
    transaction_ref = str(value.get("expected_repair_transaction_ref") or "")
    transaction = runtime.repair_transactions.get(transaction_ref)
    if not transaction or not verify_rooted("pass076_repair_transaction", transaction, "repair_transaction_root_hash72"):
        raise Pass076ReplayError("REJECT_PASS076_REPAIR_TRANSACTION_MISMATCH")
    if transaction.get("repair_transaction_root_hash72") != value.get("expected_repair_transaction_root_hash72"):
        raise Pass076ReplayError("REJECT_PASS076_EXPECTED_REPAIR_ROOT_MISMATCH")
    receipt = {
        "schema": "HHS_PASS_076_INTERPRETER_REPLAY_RECEIPT_V1",
        "ok": True,
        "workspace_state_root_hash72": observed_state,
        "execution_run_root_hash72": run["execution_run_root_hash72"],
        "repair_transaction_root_hash72": transaction["repair_transaction_root_hash72"],
        "execution_replay_root_hash72": replay["replay_verification_root_hash72"],
        "source_binding_count": verification["checked_source_count"],
        "artifact_binding_count": verification["checked_artifact_count"],
        "product_root_hash72": value.get("expected_product_root_hash72", ""),
        "thread_context_used": False,
        "llm_context_window_used": False,
        "host_path_used_as_identity": False,
        "repository_state_authoritative": True,
    }
    receipt["replay_receipt_root_hash72"] = product_root("pass076_interpreter_workspace_replay_receipt", receipt)
    return receipt


if __name__ == "__main__":
    print(json.dumps(replay_interpreter_workspace(), indent=2, sort_keys=True, ensure_ascii=False))
