"""Pass 141 — Architect Ouroboros Entanglement Entropic Phase Equilibrium.

Safe command-line optimization agent with bounded Architect execution, exact
rational equilibrium scoring, content-addressed multi-root cache, mirror repair,
and authority-preserving cache readmission.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from hhs_runtime.harmonicode_architect_ouroboros_v1 import Architect, ArchitectError

PASS_ID = "PASS_141_ARCHITECT_OUROBOROS_ENTANGLEMENT_ENTROPIC_PHASE_EQUILIBRIUM"
SCHEMA = "HHS_ARCHITECT_EPE_API_V1"
AUTHORITY = "A1_EXECUTION_EVIDENCE"
MAX_CACHE_ROOTS = 9

class EquilibriumError(ValueError): pass

def canonical_json(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def root(x: Any) -> str:
    b = x if isinstance(x, (bytes, bytearray)) else canonical_json(x)
    return hashlib.sha256(bytes(b)).hexdigest()

def _frac_text(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"

@dataclass(frozen=True)
class EthicalPolicy:
    max_cycles: int = 81
    require_proved_release: bool = True
    forbid_authority_patch: bool = True
    allow_cache_write: bool = True

    @classmethod
    def ingress(cls, row: dict[str, Any] | None) -> "EthicalPolicy":
        row = row or {}
        if not isinstance(row, dict): raise EquilibriumError("POLICY_NOT_OBJECT")
        mc = row.get("max_cycles", 81)
        if isinstance(mc, bool) or not isinstance(mc, int) or not 1 <= mc <= 81:
            raise EquilibriumError("INVALID_POLICY_CYCLE_BOUND")
        return cls(mc, bool(row.get("require_proved_release", True)),
                   bool(row.get("forbid_authority_patch", True)),
                   bool(row.get("allow_cache_write", True)))

class NonLocalProofCache:
    def __init__(self, roots: list[str | Path]):
        if not roots or len(roots) > MAX_CACHE_ROOTS: raise EquilibriumError("INVALID_CACHE_ROOT_COUNT")
        self.roots = [Path(x) for x in roots]
        for p in self.roots: p.mkdir(parents=True, exist_ok=True)

    def _path(self, base: Path, key: str) -> Path:
        return base / key[:2] / f"{key}.json"

    def put(self, obj: dict[str, Any]) -> dict[str, Any]:
        payload = canonical_json(obj); key = root(payload)
        written=[]
        for base in self.roots:
            p=self._path(base,key); p.parent.mkdir(parents=True,exist_ok=True)
            if p.exists() and p.read_bytes()!=payload: raise EquilibriumError("CACHE_COLLISION")
            p.write_bytes(payload); written.append(str(p))
        return {"cache_key":key,"replicas":len(written),"paths":written,"payload_root":key}

    def get(self, key: str) -> tuple[dict[str, Any], dict[str, Any]]:
        good=[]; bad=[]
        for base in self.roots:
            p=self._path(base,key)
            if not p.exists(): bad.append({"path":str(p),"status":"MISSING"}); continue
            b=p.read_bytes()
            if root(b)!=key: bad.append({"path":str(p),"status":"CORRUPT"}); continue
            good.append((p,b))
        if not good: raise EquilibriumError("CACHE_OBJECT_UNAVAILABLE")
        source,b=good[0]
        repaired=[]
        for row in bad:
            p=Path(row["path"]); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b); repaired.append(str(p))
        try: obj=json.loads(b)
        except Exception as exc: raise EquilibriumError("CACHE_JSON_INVALID") from exc
        return obj,{"cache_key":key,"source":str(source),"valid_replicas":len(good),"repaired":repaired}

class ArchitectEntropicPhaseEquilibrium:
    def __init__(self, cache_roots: list[str | Path]):
        self.architect=Architect(); self.cache=NonLocalProofCache(cache_roots)

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload,dict): raise EquilibriumError("REQUEST_NOT_OBJECT")
        policy=EthicalPolicy.ingress(payload.get("ethical_policy"))
        arch=payload.get("architect_request")
        if not isinstance(arch,dict): raise EquilibriumError("ARCHITECT_REQUEST_REQUIRED")
        bounded=dict(arch); bounded["max_cycles"]=min(int(arch.get("max_cycles",policy.max_cycles)),policy.max_cycles)
        # Existing Architect patch boundary rejects authority mutation.
        receipt=self.architect.execute(bounded)
        validation=self.architect.validate_receipt(receipt)
        if not validation.get("valid"): raise EquilibriumError("ARCHITECT_RECEIPT_INVALID")
        cycles=receipt.get("cycles",[])
        commits=sum(1 for c in cycles if c.get("decision")=="COMMIT")
        rollbacks=sum(1 for c in cycles if c.get("decision"," ").startswith("ROLLBACK"))
        executed=max(1,len(cycles))
        entropy=Fraction(abs(commits-rollbacks),executed)
        phase_index=(len(cycles)-1)%72
        closure=receipt.get("ouroboros",{}).get("closure")
        proved=bool(receipt.get("release_authorized",False))
        equilibrium=(bool(receipt.get("ouroboros",{}).get("closed")) and proved)
        if policy.require_proved_release and not proved: equilibrium=False
        epe={"commit_count":commits,"rollback_count":rollbacks,"cycle_count":len(cycles),
             "entropic_imbalance":_frac_text(entropy),"phase_index":phase_index,
             "phase_modulus":72,"closure":closure,"equilibrium":equilibrium}
        out={"pass_id":PASS_ID,"schema":SCHEMA,"authority":AUTHORITY,
             "request_id":str(payload.get("request_id",bounded.get("request_id",""))),
             "ethical_policy":policy.__dict__,"architect_receipt":receipt,
             "architect_validation":validation,"equilibrium":epe}
        out["receipt_root"]=root(out)
        if policy.allow_cache_write:
            out["cache_commit"]=self.cache.put(out)
            out["receipt_root"]=root({k:v for k,v in out.items() if k!="receipt_root"})
        return out

    def readmit(self,key:str)->dict[str,Any]:
        obj,cache=self.cache.get(key)
        rr=obj.get("receipt_root")
        body={k:v for k,v in obj.items() if k not in {"receipt_root","cache_commit"}}
        # accept either pre-cache or post-cache root layout deterministically
        valid_root = rr in {root(body), root({k:v for k,v in obj.items() if k!="receipt_root"})}
        aval=self.architect.validate_receipt(obj.get("architect_receipt",{}))
        authorized=bool(valid_root and aval.get("valid") and obj.get("equilibrium",{}).get("equilibrium"))
        return {"cache":cache,"receipt_root_valid":valid_root,"architect_receipt_valid":aval.get("valid",False),
                "equilibrium":obj.get("equilibrium"),"readmitted":authorized,"object":obj}

def main(argv=None):
    p=argparse.ArgumentParser(prog="hhs-pass141")
    p.add_argument("--cache-root",action="append",required=True)
    sub=p.add_subparsers(dest="cmd",required=True)
    o=sub.add_parser("optimize"); o.add_argument("request"); o.add_argument("--output")
    g=sub.add_parser("cache-get"); g.add_argument("key"); g.add_argument("--output")
    ns=p.parse_args(argv); rt=ArchitectEntropicPhaseEquilibrium(ns.cache_root)
    if ns.cmd=="optimize": result=rt.execute(json.loads(Path(ns.request).read_text()))
    else: result=rt.readmit(ns.key)
    text=json.dumps(result,indent=2,sort_keys=True)
    if ns.output: Path(ns.output).write_text(text+"\n")
    else: print(text)
    return 0
if __name__=="__main__": raise SystemExit(main())
