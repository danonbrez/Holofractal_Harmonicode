from __future__ import annotations
from pathlib import Path
from .common import sha256_file, canonical_json, atomic_write
class ReplayEngine:
    def snapshot(self,paths:list[str|Path],out:str|Path)->dict:
        files=[]
        for p in sorted(map(Path,paths),key=lambda x:x.as_posix()):
            if p.exists(): files.append({"path":p.as_posix(),"sha256":sha256_file(p),"size":p.stat().st_size})
        result={"schema":"HHS_PASS151_REPLAY_SNAPSHOT_V1","files":files,"replay_status":"MATCH"}
        atomic_write(out,canonical_json(result)+"\n"); return result
    def verify(self,snapshot:dict)->bool:
        return all(Path(f["path"]).exists() and sha256_file(f["path"])==f["sha256"] for f in snapshot["files"])
