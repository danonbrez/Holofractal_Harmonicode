from __future__ import annotations
import os, subprocess, time
from pathlib import Path
from .common import append_jsonl, sha256_file, sha256_text, canonical_json
class DeterministicContractExecutor:
    def __init__(self, root:str|Path, trace_path:str|Path, allowlist:set[str]|None=None):
        self.root=Path(root).resolve(); self.trace_path=Path(trace_path); self.allowlist=allowlist or {"python3","node","gcc","make","sh","bash"}
    def plan(self, obligation_ids:list[str], actions:list[dict])->dict:
        normalized=sorted(actions,key=lambda x:(x.get("order",0),canonical_json(x)))
        return {"schema":"HHS_PASS151_EXECUTOR_PLAN_V1","obligation_ids":sorted(obligation_ids),"actions":normalized,"plan_root":sha256_text(canonical_json(normalized))}
    def run(self, argv:list[str], obligation_ids:list[str], timeout_s:int=30, cwd:str|Path|None=None)->dict:
        if not argv or Path(argv[0]).name not in self.allowlist: raise PermissionError("TOOL_NOT_ALLOWLISTED")
        work=(Path(cwd).resolve() if cwd else self.root)
        if self.root not in (work,*work.parents): raise PermissionError("WORKSPACE_ESCAPE")
        before=self._snapshot(); start=time.time_ns()
        try:
            cp=subprocess.run(argv,cwd=work,text=True,capture_output=True,timeout=timeout_s,check=False,env={**os.environ,"PYTHONHASHSEED":"0"})
            status="EXITED"; code=cp.returncode; out=cp.stdout; err=cp.stderr
        except subprocess.TimeoutExpired as e:
            status="RESOURCE_BOUNDED"; code=None; out=e.stdout or ""; err=e.stderr or ""
        after=self._snapshot(); changed=sorted(set(before)^set(after)|{p for p in set(before)&set(after) if before[p]!=after[p]})
        rec={"schema":"HHS_PASS151_EXECUTOR_TRACE_V1","argv":argv,"cwd":str(work.relative_to(self.root)),"obligation_ids":sorted(obligation_ids),"status":status,"exit_code":code,"stdout":out,"stderr":err,"stdout_sha256":sha256_text(out),"stderr_sha256":sha256_text(err),"changed_files":changed,"duration_ns":time.time_ns()-start}
        append_jsonl(self.trace_path,rec); return rec
    def _snapshot(self):
        out={}
        for p in self.root.rglob("*"):
            if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts:
                try: out[p.relative_to(self.root).as_posix()]=sha256_file(p)
                except OSError: pass
        return out
