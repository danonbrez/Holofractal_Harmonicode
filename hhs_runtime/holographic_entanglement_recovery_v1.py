"""Pass 140 — Holographic Entanglement Tracking.

Deterministic corruption detection and bounded recovery using content metadata,
XOR parity stripes, dependency/data-flow receipts, and post-recovery readmission.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PASS_ID = "PASS_140_HOLOGRAPHIC_ENTANGLEMENT_TRACKING"
SCHEMA = "HHS_HOLOGRAPHIC_RECOVERY_API_V1"
AUTHORITY = "A1_EXECUTION_EVIDENCE"
DATA_SHARDS = 4
PARITY_SHARDS = 1

class RecoveryError(ValueError): pass

def canonical_json(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def root(x: Any) -> str:
    b = x if isinstance(x, (bytes, bytearray)) else canonical_json(x)
    return hashlib.sha256(bytes(b)).hexdigest()

def hash72(hex_root: str) -> str:
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    n = int(hex_root, 16)
    out = []
    for _ in range(72): out.append(alphabet[n & 63]); n >>= 6
    return "".join(reversed(out))

def _xor(parts: list[bytes], width: int) -> bytes:
    out = bytearray(width)
    for p in parts:
        for i, v in enumerate(p): out[i] ^= v
    return bytes(out)

def _chunk(data: bytes, n: int = DATA_SHARDS) -> tuple[list[bytes], int]:
    width = max(1, (len(data) + n - 1) // n)
    padded = data + b"\0" * (width * n - len(data))
    return [padded[i*width:(i+1)*width] for i in range(n)], width

@dataclass(frozen=True)
class ArtifactInput:
    artifact_id: str
    path: str
    data: bytes
    dependencies: tuple[str, ...]

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "ArtifactInput":
        if not isinstance(row, dict): raise RecoveryError("ARTIFACT_NOT_OBJECT")
        aid = str(row.get("artifact_id", "")).strip()
        path = str(row.get("path", aid)).strip()
        if not aid or not path: raise RecoveryError("ARTIFACT_ID_AND_PATH_REQUIRED")
        deps = row.get("dependencies", [])
        if not isinstance(deps, list) or any(not isinstance(x, str) for x in deps): raise RecoveryError("INVALID_DEPENDENCIES")
        if "content_b64" in row:
            try: data = base64.b64decode(row["content_b64"], validate=True)
            except Exception as exc: raise RecoveryError("INVALID_BASE64") from exc
        elif "content" in row and isinstance(row["content"], str): data = row["content"].encode()
        else: raise RecoveryError("CONTENT_REQUIRED")
        return cls(aid, path, data, tuple(deps))

class HolographicRecovery:
    def encode(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict): raise RecoveryError("REQUEST_NOT_OBJECT")
        rid = str(payload.get("request_id", "")).strip()
        rows = payload.get("artifacts")
        if not rid or not isinstance(rows, list) or not rows: raise RecoveryError("REQUEST_ID_AND_ARTIFACTS_REQUIRED")
        artifacts = [ArtifactInput.from_row(r) for r in rows]
        ids = [a.artifact_id for a in artifacts]
        if len(set(ids)) != len(ids): raise RecoveryError("DUPLICATE_ARTIFACT_ID")
        idset = set(ids)
        for a in artifacts:
            missing = set(a.dependencies) - idset
            if missing: raise RecoveryError("UNKNOWN_DEPENDENCY:" + ",".join(sorted(missing)))
        graph = {a.artifact_id: list(a.dependencies) for a in artifacts}
        self._topological(graph)
        graph_root = root(graph)
        encoded=[]
        for a in artifacts:
            chunks,width = _chunk(a.data)
            parity = _xor(chunks,width)
            content_root = root(a.data)
            meta = {
                "artifact_id":a.artifact_id,"path":a.path,"size":len(a.data),
                "mime":mimetypes.guess_type(a.path)[0] or "application/octet-stream",
                "content_root":content_root,"hash72":hash72(content_root),
                "dependencies":list(a.dependencies),"dependency_graph_root":graph_root,
                "data_shards":DATA_SHARDS,"parity_shards":PARITY_SHARDS,"shard_width":width,
            }
            meta_root=root(meta)
            shards=[]
            for i,b in enumerate(chunks+[parity]):
                sh={"index":i,"kind":"data" if i<DATA_SHARDS else "parity","payload_b64":base64.b64encode(b).decode(),"payload_root":root(b),"meta_root":meta_root}
                sh["shard_root"]=root(sh); shards.append(sh)
            encoded.append({"metadata":meta,"metadata_root":meta_root,"shards":shards,"artifact_receipt_root":root({"metadata_root":meta_root,"shard_roots":[s["shard_root"] for s in shards]})})
        result={"schema":SCHEMA,"pass_id":PASS_ID,"authority":AUTHORITY,"request_id":rid,"dependency_graph":graph,"dependency_graph_root":graph_root,"artifacts":encoded,
                "invariants":{"one_shard_loss_per_stripe_recoverable":True,"metadata_pattern_bound":True,"dependency_receipts_bound":True,"byte_exact_readmission_required":True,"no_authority_promotion":True}}
        result["receipt_root"]=root(result)
        return result

    def recover(self, encoded: dict[str, Any]) -> dict[str, Any]:
        self._validate_envelope(encoded)
        graph=encoded["dependency_graph"]; order=self._topological(graph)
        recovered=[]; failures=[]
        by_id={a["metadata"]["artifact_id"]:a for a in encoded["artifacts"]}
        valid_roots={}
        for aid in order:
            art=by_id[aid]; meta=art["metadata"]
            if root(meta)!=art.get("metadata_root") or meta.get("dependency_graph_root")!=encoded["dependency_graph_root"]:
                failures.append({"artifact_id":aid,"status":"METADATA_CORRUPT"}); continue
            shard_bytes={}; bad=[]
            for s in art.get("shards",[]):
                try:b=base64.b64decode(s["payload_b64"],validate=True)
                except Exception: bad.append(s.get("index")); continue
                body=dict(s); claimed=body.pop("shard_root",None)
                if claimed!=root(body) or s.get("payload_root")!=root(b) or s.get("meta_root")!=art["metadata_root"]: bad.append(s.get("index")); continue
                shard_bytes[s["index"]]=b
            missing=[i for i in range(DATA_SHARDS+1) if i not in shard_bytes]
            if len(missing)>1:
                failures.append({"artifact_id":aid,"status":"UNRECOVERABLE_REDUNDANCY_EXCEEDED","missing":missing}); continue
            width=meta["shard_width"]
            if missing:
                idx=missing[0]
                shard_bytes[idx]=_xor([shard_bytes[i] for i in range(DATA_SHARDS+1) if i!=idx],width)
            data=b"".join(shard_bytes[i] for i in range(DATA_SHARDS))[:meta["size"]]
            dep_ok=all(d in valid_roots for d in meta["dependencies"])
            content_ok=root(data)==meta["content_root"] and hash72(meta["content_root"])==meta["hash72"]
            if not dep_ok or not content_ok:
                failures.append({"artifact_id":aid,"status":"READMISSION_FAILED","dependency_ok":dep_ok,"content_ok":content_ok}); continue
            valid_roots[aid]=meta["content_root"]
            recovered.append({"artifact_id":aid,"path":meta["path"],"content_b64":base64.b64encode(data).decode(),"content_root":meta["content_root"],"recovered_shard":missing[0] if missing else None,"status":"BYTE_EXACT_RECOVERED" if missing else "INTACT_REVALIDATED","dependencies_verified":True})
        result={"schema":"HHS_HOLOGRAPHIC_RECOVERY_RESULT_V1","pass_id":PASS_ID,"source_receipt_root":encoded["receipt_root"],"recovery_order":order,"recovered":recovered,"failures":failures,"conclusion":"RECOVERY_CLOSED" if not failures else "RECOVERY_PARTIAL_OR_FAILED"}
        result["receipt_root"]=root(result); return result

    def analyze_impact(self, encoded: dict[str, Any], damaged_ids: list[str]) -> dict[str, Any]:
        self._validate_envelope(encoded); graph=encoded["dependency_graph"]
        unknown=set(damaged_ids)-set(graph)
        if unknown: raise RecoveryError("UNKNOWN_DAMAGED_ARTIFACT")
        impacted=set(damaged_ids); changed=True
        while changed:
            changed=False
            for node,deps in graph.items():
                if node not in impacted and impacted.intersection(deps): impacted.add(node); changed=True
        out={"damaged":sorted(damaged_ids),"impacted":sorted(impacted),"recovery_order":[x for x in self._topological(graph) if x in impacted]}
        out["analysis_root"]=root(out); return out

    def validate_receipt(self, receipt: dict[str, Any]) -> dict[str, Any]:
        try:self._validate_envelope(receipt); valid=True
        except Exception:valid=False
        return {"valid":valid}

    def _validate_envelope(self,e:dict[str,Any])->None:
        if not isinstance(e,dict) or e.get("schema")!=SCHEMA or "receipt_root" not in e: raise RecoveryError("INVALID_ENVELOPE")
        body=dict(e); claimed=body.pop("receipt_root")
        if claimed!=root(body): raise RecoveryError("RECEIPT_ROOT_MISMATCH")
        if e.get("dependency_graph_root")!=root(e.get("dependency_graph")): raise RecoveryError("GRAPH_ROOT_MISMATCH")

    def _topological(self, graph:dict[str,list[str]])->list[str]:
        temp=set(); perm=set(); out=[]
        def visit(n):
            if n in temp: raise RecoveryError("DEPENDENCY_CYCLE")
            if n in perm:return
            temp.add(n)
            for d in graph[n]: visit(d)
            temp.remove(n);perm.add(n);out.append(n)
        for n in sorted(graph):visit(n)
        return out

def main(argv=None)->int:
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    e=sub.add_parser("encode");e.add_argument("request",type=Path);e.add_argument("--output",type=Path)
    r=sub.add_parser("recover");r.add_argument("receipt",type=Path);r.add_argument("--output",type=Path)
    ns=ap.parse_args(argv); runtime=HolographicRecovery(); obj=json.loads((ns.request if ns.cmd=="encode" else ns.receipt).read_text())
    result=runtime.encode(obj) if ns.cmd=="encode" else runtime.recover(obj)
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if ns.output: ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(text)
    print(text,end="");return 0
if __name__=="__main__":raise SystemExit(main())
