"""
HHS Distributed Verification v1
===============================

Produces a portable verification receipt that another machine / agent / runner
can recompute and compare against the local unified ledger and Git binding.

This is deterministic local verification. It does not perform networking.
External distribution is achieved by copying the receipt between nodes or
including it in CI artifacts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict
import json
import platform

from hhs_runtime.hhs_git_hash72_binding_v1 import read_git_state
from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_repo_paths_v1 import repo_root, runtime_artifact_path
from hhs_runtime.hhs_unified_hash72_ledger_v1 import verify_unified_ledger
from hhs_runtime.hhs_filesystem_hash72_ledger_v1 import verify_filesystem_ledger


@dataclass(frozen=True)
class DistributedVerificationReceipt:
    verifier_id: str
    repo_root: str
    platform: Dict[str, str]
    git_state: Dict[str, Any]
    unified_ledger: Dict[str, Any]
    filesystem_ledger: Dict[str, Any]
    status: str
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def local_platform_fingerprint() -> Dict[str, str]:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "python": platform.python_version(),
        "machine": platform.machine(),
    }


def make_distributed_verification_receipt(*, verifier_id: str = "local") -> DistributedVerificationReceipt:
    root = repo_root()
    git_state = read_git_state(root)
    unified = verify_unified_ledger()
    fs_ledger_path = runtime_artifact_path("hhs_filesystem_ledger.json")
    filesystem = verify_filesystem_ledger(fs_ledger_path)
    status = "VERIFIED" if unified.get("ok") and filesystem.get("ok") else "FAILED"
    core = {
        "verifier_id": verifier_id,
        "repo_root": str(root),
        "platform": local_platform_fingerprint(),
        "git_state": git_state,
        "unified_ledger": unified,
        "filesystem_ledger": filesystem,
        "status": status,
    }
    receipt_hash72 = hash72_digest(("hhs_distributed_verification_receipt_v1", core), width=24)
    return DistributedVerificationReceipt(receipt_hash72=receipt_hash72, **core)


def write_distributed_verification_receipt(*, verifier_id: str = "local", path: str | Path | None = None) -> Dict[str, Any]:
    receipt = make_distributed_verification_receipt(verifier_id=verifier_id)
    out = Path(path) if path is not None else runtime_artifact_path(f"hhs_distributed_verification_{verifier_id}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt.to_dict(), indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return receipt.to_dict()


def compare_distributed_receipts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "head_commit_match": a.get("git_state", {}).get("head_commit") == b.get("git_state", {}).get("head_commit"),
        "unified_tip_match": a.get("unified_ledger", {}).get("tip_hash72") == b.get("unified_ledger", {}).get("tip_hash72"),
        "filesystem_tip_match": a.get("filesystem_ledger", {}).get("tip_hash72") == b.get("filesystem_ledger", {}).get("tip_hash72"),
        "both_verified": a.get("status") == "VERIFIED" and b.get("status") == "VERIFIED",
    }
    return {
        "status": "MATCH" if all(checks.values()) else "DIVERGED",
        "checks": checks,
        "a_receipt_hash72": a.get("receipt_hash72"),
        "b_receipt_hash72": b.get("receipt_hash72"),
    }


if __name__ == "__main__":
    print(json.dumps(write_distributed_verification_receipt(), indent=2, sort_keys=True, ensure_ascii=False))
