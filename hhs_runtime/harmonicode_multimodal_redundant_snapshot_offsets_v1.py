"""Pass 142 — Multimodal redundant symbolic global-state snapshots.

Canonical multimodal snapshots are symbol-table compressed, deterministically
compressed, encoded as four data offsets plus one XOR parity offset, and embedded
inside fork-local operation receipts.  Dependency graph nodes index those offset
fields.  Reconstruction is byte exact and fails closed beyond one unavailable
shard.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PASS_ID = "PASS_142_MULTIMODAL_REDUNDANT_SYMBOLIC_SNAPSHOT_OFFSETS"
SCHEMA = "HHS_MULTIMODAL_SNAPSHOT_OFFSET_API_V1"
AUTHORITY = "A1_EXECUTION_EVIDENCE"
DATA_SHARDS = 4
TOTAL_SHARDS = 5

class SnapshotError(ValueError):
    pass

def canonical_json(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256(x: bytes | bytearray) -> str:
    return hashlib.sha256(bytes(x)).hexdigest()

def hash72(x: bytes | bytearray) -> str:
    # Stable 72-glyph projection retained as a distinct projection, not authority.
    digest = hashlib.sha512(bytes(x)).hexdigest() + hashlib.sha256(bytes(x)).hexdigest()
    return digest[:72]

def _xor(parts: list[bytes], width: int) -> bytes:
    out = bytearray(width)
    for part in parts:
        for i, b in enumerate(part):
            out[i] ^= b
    return bytes(out)

def _split4(payload: bytes) -> tuple[list[bytes], int]:
    width = max(1, (len(payload) + DATA_SHARDS - 1) // DATA_SHARDS)
    padded = payload + b"\0" * (width * DATA_SHARDS - len(payload))
    return [padded[i*width:(i+1)*width] for i in range(DATA_SHARDS)], width

def _collect_strings(value: Any, counts: dict[str, int]) -> None:
    if isinstance(value, str):
        counts[value] = counts.get(value, 0) + 1
    elif isinstance(value, dict):
        for k, v in value.items():
            counts[str(k)] = counts.get(str(k), 0) + 1
            _collect_strings(v, counts)
    elif isinstance(value, list):
        for v in value:
            _collect_strings(v, counts)

def _symbol_encode(value: Any, index: dict[str, int]) -> Any:
    if isinstance(value, str):
        return ["$s", index[value]] if value in index else value
    if isinstance(value, list):
        return ["$l", [_symbol_encode(v, index) for v in value]]
    if isinstance(value, dict):
        rows=[]
        for k in sorted(value):
            ek = ["$s", index[k]] if k in index else k
            rows.append([ek, _symbol_encode(value[k], index)])
        return ["$d", rows]
    return value

def _symbol_decode(value: Any, symbols: list[str]) -> Any:
    if isinstance(value, list) and len(value) == 2 and value[0] == "$s":
        return symbols[value[1]]
    if isinstance(value, list) and len(value) == 2 and value[0] == "$l":
        return [_symbol_decode(v, symbols) for v in value[1]]
    if isinstance(value, list) and len(value) == 2 and value[0] == "$d":
        out={}
        for k, v in value[1]:
            dk = _symbol_decode(k, symbols) if isinstance(k, list) else k
            out[dk] = _symbol_decode(v, symbols)
        return out
    return value

def symbolic_compress(value: Any) -> tuple[bytes, dict[str, Any]]:
    counts: dict[str, int] = {}
    _collect_strings(value, counts)
    # Include repeated strings and long strings where dictionary substitution helps.
    symbols = sorted((s for s,c in counts.items() if c > 1 or len(s) >= 16), key=lambda s: (-counts[s], s))
    encoded = {"symbols": symbols, "value": _symbol_encode(value, {s:i for i,s in enumerate(symbols)})}
    symbolic = canonical_json(encoded)
    compressed = zlib.compress(symbolic, level=9)
    return compressed, {
        "symbol_count": len(symbols),
        "symbolic_bytes": len(symbolic),
        "compressed_bytes": len(compressed),
        "codec": "HHS_SYMBOL_TABLE_JSON+ZLIB9",
    }

def symbolic_expand(payload: bytes) -> Any:
    try:
        encoded = json.loads(zlib.decompress(payload))
        return _symbol_decode(encoded["value"], encoded["symbols"])
    except Exception as exc:
        raise SnapshotError("SYMBOLIC_EXPANSION_FAILED") from exc

def _normalize_modalities(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or not rows:
        raise SnapshotError("MODALITIES_REQUIRED")
    out=[]
    seen=set()
    for row in rows:
        if not isinstance(row, dict): raise SnapshotError("MODALITY_NOT_OBJECT")
        mid=str(row.get("id", "")); mime=str(row.get("mime_type", ""))
        if not mid or mid in seen or not mime: raise SnapshotError("INVALID_MODALITY_ID_OR_MIME")
        seen.add(mid)
        if "data_base64" in row:
            try: raw=base64.b64decode(row["data_base64"], validate=True)
            except Exception as exc: raise SnapshotError("INVALID_MODALITY_BASE64") from exc
        elif "text" in row:
            raw=str(row["text"]).encode("utf-8")
        elif "json" in row:
            raw=canonical_json(row["json"])
        else:
            raise SnapshotError("MODALITY_PAYLOAD_REQUIRED")
        out.append({"id":mid,"mime_type":mime,"encoding":"base64","data_base64":base64.b64encode(raw).decode(),
                    "byte_length":len(raw),"sha256":sha256(raw),"hash72":hash72(raw)})
    return out

def _topological(ops: list[dict[str, Any]]) -> list[str]:
    ids={str(o.get("id","")) for o in ops}
    if "" in ids or len(ids)!=len(ops): raise SnapshotError("INVALID_OR_DUPLICATE_OPERATION_ID")
    deps={str(o["id"]):[str(x) for x in o.get("depends_on",[])] for o in ops}
    for oid, ds in deps.items():
        if oid in ds or any(d not in ids for d in ds): raise SnapshotError("INVALID_OPERATION_DEPENDENCY")
    indeg={x:0 for x in ids}; children={x:[] for x in ids}
    for x,ds in deps.items():
        indeg[x]=len(ds)
        for d in ds: children[d].append(x)
    ready=sorted(x for x,n in indeg.items() if n==0); order=[]
    while ready:
        x=ready.pop(0); order.append(x)
        for y in sorted(children[x]):
            indeg[y]-=1
            if indeg[y]==0: ready.append(y); ready.sort()
    if len(order)!=len(ids): raise SnapshotError("DEPENDENCY_CYCLE")
    return order

@dataclass
class MultimodalSnapshotOffsets:
    def encode(self, request: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(request, dict): raise SnapshotError("REQUEST_NOT_OBJECT")
        operations=request.get("forked_operations")
        if not isinstance(operations,list) or len(operations)<TOTAL_SHARDS:
            raise SnapshotError("AT_LEAST_FIVE_FORKED_OPERATIONS_REQUIRED")
        order=_topological(operations)
        modalities=_normalize_modalities(request.get("modalities"))
        global_state={
            "request_id":str(request.get("request_id","")),
            "state":request.get("global_state",{}),
            "modalities":modalities,
            "dependency_order":order,
            "operation_metadata":[{"id":str(o["id"]),"depends_on":[str(x) for x in o.get("depends_on",[])],
                                   "operation":o.get("operation",{})} for o in sorted(operations,key=lambda x:str(x["id"]))],
        }
        canonical=canonical_json(global_state)
        compressed, stats=symbolic_compress(global_state)
        data,width=_split4(compressed); parity=_xor(data,width); shards=data+[parity]
        snapshot_root=sha256(canonical); compressed_root=sha256(compressed)
        graph_root=sha256(canonical_json({"order":order,"deps":{str(o["id"]):o.get("depends_on",[]) for o in operations}}))
        receipts=[]
        byid={str(o["id"]):o for o in operations}
        for pos, oid in enumerate(order):
            op=byid[oid]; shard_index=pos % TOTAL_SHARDS; shard=shards[shard_index]
            offset={
                "offset_slot":shard_index,
                "offset_kind":"PARITY" if shard_index==4 else "DATA",
                "offset_start":shard_index*width,
                "offset_length":len(shard),
                "payload_base64":base64.b64encode(shard).decode(),
                "payload_root":sha256(shard),
                "snapshot_root":snapshot_root,
                "compressed_root":compressed_root,
                "compressed_length":len(compressed),
                "shard_width":width,
                "graph_root":graph_root,
            }
            rec={"receipt_id":f"{request.get('request_id','snapshot')}:{oid}","operation_id":oid,
                 "depends_on":[str(x) for x in op.get("depends_on",[])],"operation":op.get("operation",{}),
                 "dependency_index":{"topological_offset":pos,"parent_offsets":[order.index(str(x)) for x in op.get("depends_on",[])]},
                 "global_snapshot_offset":offset}
            rec["receipt_root"]=sha256(canonical_json(rec)); receipts.append(rec)
        index={"graph_root":graph_root,"snapshot_root":snapshot_root,"compressed_root":compressed_root,
               "topological_order":order,"nodes":{r["operation_id"]:{"receipt_id":r["receipt_id"],
               "topological_offset":r["dependency_index"]["topological_offset"],
               "parent_offsets":r["dependency_index"]["parent_offsets"],
               "snapshot_offset_slot":r["global_snapshot_offset"]["offset_slot"],
               "receipt_root":r["receipt_root"]} for r in receipts}}
        out={"pass_id":PASS_ID,"schema":SCHEMA,"authority":AUTHORITY,"request_id":global_state["request_id"],
             "snapshot":{"snapshot_root":snapshot_root,"canonical_length":len(canonical),"compressed_root":compressed_root,
                         "compressed_length":len(compressed),"data_shards":4,"parity_shards":1,"symbolic_compression":stats},
             "fork_receipts":receipts,"dependency_graph_index":index}
        out["receipt_root"]=sha256(canonical_json(out))
        return out

    def validate_receipt(self, receipt: dict[str, Any]) -> dict[str, Any]:
        errors=[]
        rr=receipt.get("receipt_root")
        if rr!=sha256(canonical_json({k:v for k,v in receipt.items() if k!="receipt_root"})): errors.append("RECEIPT_ROOT_MISMATCH")
        recs=receipt.get("fork_receipts",[])
        for r in recs:
            root0=r.get("receipt_root")
            if root0!=sha256(canonical_json({k:v for k,v in r.items() if k!="receipt_root"})): errors.append(f"FORK_ROOT_MISMATCH:{r.get('operation_id')}")
        idx=receipt.get("dependency_graph_index",{})
        if idx.get("snapshot_root")!=receipt.get("snapshot",{}).get("snapshot_root"): errors.append("INDEX_SNAPSHOT_MISMATCH")
        return {"valid":not errors,"errors":errors}

    def reconstruct(self, receipt: dict[str, Any]) -> dict[str, Any]:
        val=self.validate_receipt(receipt)
        if not val["valid"]: raise SnapshotError("RECEIPT_INVALID")
        slots: dict[int, bytes] = {}
        bad=[]
        for r in receipt["fork_receipts"]:
            o=r["global_snapshot_offset"]; i=int(o["offset_slot"])
            try: b=base64.b64decode(o["payload_base64"],validate=True)
            except Exception: bad.append(i); continue
            if sha256(b)!=o["payload_root"]: bad.append(i); continue
            if i in slots and slots[i]!=b: raise SnapshotError("CONFLICTING_REDUNDANT_OFFSETS")
            slots[i]=b
        missing=[i for i in range(TOTAL_SHARDS) if i not in slots]
        if len(missing)>1: raise SnapshotError("UNRECOVERABLE_OFFSET_REDUNDANCY_EXCEEDED")
        width=int(receipt["fork_receipts"][0]["global_snapshot_offset"]["shard_width"])
        recovered=[]
        if missing:
            m=missing[0]
            slots[m]=_xor([slots[i] for i in range(TOTAL_SHARDS) if i!=m],width)
            recovered.append(m)
        data=b"".join(slots[i] for i in range(DATA_SHARDS))
        clen=int(receipt["snapshot"]["compressed_length"]); compressed=data[:clen]
        if sha256(compressed)!=receipt["snapshot"]["compressed_root"]: raise SnapshotError("COMPRESSED_ROOT_MISMATCH")
        state=symbolic_expand(compressed); canonical=canonical_json(state)
        if sha256(canonical)!=receipt["snapshot"]["snapshot_root"]: raise SnapshotError("SNAPSHOT_ROOT_MISMATCH")
        # Revalidate every embedded modality.
        for m in state["modalities"]:
            raw=base64.b64decode(m["data_base64"])
            if sha256(raw)!=m["sha256"] or hash72(raw)!=m["hash72"]: raise SnapshotError("MODALITY_IDENTITY_MISMATCH")
        return {"status":"SNAPSHOT_RECOVERED" if recovered else "SNAPSHOT_REPLAYED",
                "recovered_offset_slots":recovered,"snapshot_root":sha256(canonical),
                "dependency_graph_root":receipt["dependency_graph_index"]["graph_root"],"global_state_snapshot":state}

    def query_dependency(self, receipt: dict[str, Any], operation_id: str) -> dict[str, Any]:
        idx=receipt.get("dependency_graph_index",{}); nodes=idx.get("nodes",{})
        if operation_id not in nodes: raise SnapshotError("OPERATION_NOT_INDEXED")
        node=nodes[operation_id]; order=idx["topological_order"]
        parents=[order[i] for i in node["parent_offsets"]]
        children=[oid for oid,n in nodes.items() if node["topological_offset"] in n["parent_offsets"]]
        return {"operation_id":operation_id,"node":node,"parents":parents,"children":sorted(children),
                "graph_root":idx["graph_root"],"snapshot_root":idx["snapshot_root"]}

def main(argv=None) -> int:
    p=argparse.ArgumentParser(prog="hhs-pass142")
    sub=p.add_subparsers(dest="cmd",required=True)
    e=sub.add_parser("encode"); e.add_argument("request"); e.add_argument("--output")
    r=sub.add_parser("reconstruct"); r.add_argument("receipt"); r.add_argument("--output")
    q=sub.add_parser("index-query"); q.add_argument("receipt"); q.add_argument("operation_id"); q.add_argument("--output")
    ns=p.parse_args(argv); rt=MultimodalSnapshotOffsets()
    if ns.cmd=="encode": out=rt.encode(json.loads(Path(ns.request).read_text()))
    elif ns.cmd=="reconstruct": out=rt.reconstruct(json.loads(Path(ns.receipt).read_text()))
    else: out=rt.query_dependency(json.loads(Path(ns.receipt).read_text()),ns.operation_id)
    text=json.dumps(out,indent=2,sort_keys=True)
    if ns.output: Path(ns.output).write_text(text+"\n")
    else: print(text)
    return 0

if __name__=="__main__": raise SystemExit(main())
