"""
HHS Commit Acceptance Gate v1
============================

Strict acceptance gate.
"""

from pathlib import Path
import json, subprocess

from hhs_runtime.hhs_repo_paths_v1 import repo_root
from hhs_runtime.hhs_language_runtime_validator_cli_v1 import validate_repo_language_runtime
from hhs_runtime.hhs_unified_hash72_ledger_v1 import absorb_json_artifacts, verify_unified_ledger
from hhs_runtime.hhs_git_hash72_binding_v1 import bind_git_state_to_unified_ledger
from hhs_runtime.hhs_dependency_audit_v1 import run_dependency_audit
from hhs_runtime.hhs_immutable_manifest_v1 import validate_manifest

FORBIDDEN_STRINGS = ["/mnt/data"]

class CommitAcceptanceError(Exception): pass

def _scan(root: Path):
    hits=[]
    for p in root.rglob("*.py"):
        t=p.read_text(encoding="utf-8")
        for s in FORBIDDEN_STRINGS:
            if s in t: hits.append(str(p))
    return hits

def _run(p):
    r=subprocess.run(["python",str(p)],capture_output=True,text=True)
    return {"ok":r.returncode==0,"stderr":r.stderr}

def run_commit_acceptance_gate():
    root=repo_root()

    if _scan(root): raise CommitAcceptanceError("forbidden paths")

    dep=run_dependency_audit()
    if not dep["ok"]: raise CommitAcceptanceError(json.dumps(dep))

    man=validate_manifest()
    if not man["ok"]: raise CommitAcceptanceError(json.dumps(man))

    rt=validate_repo_language_runtime()
    if rt.get("status")!="ACCEPTED": raise CommitAcceptanceError(json.dumps(rt))

    for s in ["hhs_runtime_certification_v2.py","hhs_v1_bundle_runner-2.py","hhs_realtime_phase_certification_v1.py"]:
        if not _run(root/s)["ok"]: raise CommitAcceptanceError(s)

    arts=list((root/"data"/"runtime").glob("*.json"))
    if not absorb_json_artifacts(arts)["verification"]["ok"]:
        raise CommitAcceptanceError("ledger invalid")

    if not verify_unified_ledger()["ok"]:
        raise CommitAcceptanceError("unified invalid")

    git=bind_git_state_to_unified_ledger(root)

    return {"status":"ACCEPTED","git":git.to_dict()}

if __name__=="__main__":
    print(json.dumps(run_commit_acceptance_gate(),indent=2))
