"""
HHS Git Hash72 Binding v1
=========================

Binds the current Git state to the unified Hash72 ledger after acceptance checks
pass. This creates a tamper-evident bridge:

    git commit/worktree state -> Hash72 receipt -> unified ledger tip

The module observes Git metadata only. It does not mutate Git state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List
import subprocess

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger


@dataclass(frozen=True)
class GitHash72BindingReceipt:
    repo_root: str
    head_commit: str
    branch: str
    status_porcelain: List[str]
    dirty: bool
    commit_hash72: str
    unified_ledger_tip_before: str
    unified_ledger_tip_after: str
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"git {' '.join(args)} failed")
    return proc.stdout.strip()


def read_git_state(root: str | Path) -> Dict[str, Any]:
    repo = Path(root)
    head = _git(repo, "rev-parse", "HEAD")
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    status_text = _git(repo, "status", "--porcelain")
    status = [line for line in status_text.splitlines() if line]
    return {
        "repo_root": str(repo),
        "head_commit": head,
        "branch": branch,
        "status_porcelain": status,
        "dirty": bool(status),
    }


def bind_git_state_to_unified_ledger(root: str | Path, *, allow_dirty: bool = True) -> GitHash72BindingReceipt:
    state = read_git_state(root)
    if state["dirty"] and not allow_dirty:
        raise RuntimeError("Git worktree is dirty and allow_dirty=False")

    before = verify_unified_ledger()
    commit_hash72 = hash72_digest(("hhs_git_state_binding_v1", state), width=24)
    payload = {
        "git_state": state,
        "commit_hash72": commit_hash72,
        "unified_ledger_tip_before": before.get("tip_hash72"),
    }
    append_payload("GIT_STATE_BINDING", state["head_commit"], payload)
    after = verify_unified_ledger()
    receipt_hash72 = hash72_digest(("hhs_git_hash72_binding_receipt_v1", payload, after), width=24)
    return GitHash72BindingReceipt(
        repo_root=state["repo_root"],
        head_commit=state["head_commit"],
        branch=state["branch"],
        status_porcelain=state["status_porcelain"],
        dirty=state["dirty"],
        commit_hash72=commit_hash72,
        unified_ledger_tip_before=before.get("tip_hash72", ""),
        unified_ledger_tip_after=after.get("tip_hash72", ""),
        receipt_hash72=receipt_hash72,
    )
