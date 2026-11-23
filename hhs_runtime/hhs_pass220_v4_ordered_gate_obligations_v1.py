"""Pass 220 V4 ordered gate proof obligations (never canonical gate truth).

Extract two separately addressed tensor copies from exact source bytes and
bind every ordered lexical edge to the native Pass159 source/receipt fingerprint.
This tool creates neither semantic proof witnesses nor VM81 commitments.
"""
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

SOURCE_SHA256 = "124900427b60ff688e3cff10f2178e76d121168273fcd3caec0782ca2a067344"
SOURCE_BYTES = 527
GATE_COUNT = 40


class ObligationError(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ObligationError(reason)


def build_obligations(data: bytes, native_receipt: dict[str, Any]) -> dict[str, Any]:
    require(len(data) == SOURCE_BYTES and data.endswith(b"\n"), "V4_BYTE_LENGTH")
    digest = sha256(data).digest()
    require(digest.hex() == SOURCE_SHA256, "V4_SOURCE_SHA256")
    require(native_receipt["source_sha256"] == SOURCE_SHA256, "NATIVE_SOURCE_MISMATCH")
    require(native_receipt["source_bytes"] == SOURCE_BYTES, "NATIVE_LENGTH_MISMATCH")
    require(native_receipt["gate_count"] == GATE_COUNT, "NATIVE_COUNT_MISMATCH")
    proof = native_receipt["proof"]
    require(proof["global_gate_truth"] == "UNRESOLVED", "UNAUTHORIZED_GATE_PROMOTION")
    require(not any(value for key,value in proof.items() if key != "global_gate_truth"),
            "UNAUTHORIZED_AUTHORITY_PROMOTION")
    body = data[:-1]
    depth = [0] * len(body)
    active: list[int] = []
    match: dict[int,int] = {}
    slots: list[tuple[int,int,int]] = []
    for i,ch in enumerate(body):
        depth[i] = len(active)
        if ch == 40:
            active.append(i)
        elif ch == 41:
            require(bool(active), "UNMATCHED_CLOSE")
            match[active.pop()] = i
        elif ch == 61 and body[i:i+2] == b"==":
            slots.append((i,len(active),active[-1] if active else -1))
    require(not active, "UNCLOSED_SOURCE")
    require(len(slots) == GATE_COUNT, "GATE_COUNT")

    nodes: list[dict[str, Any]] = []
    for number,(position,level,opening) in enumerate(slots):
        start = opening+1
        end = match[opening] if opening>=0 else len(body)
        lhs_start = start
        j=start
        while j<position:
            if depth[j]==level and body[j:j+2]==b"==":
                lhs_start=j+2; j+=2
            elif depth[j]==level and body[j:j+1]==b",":
                lhs_start=j+1
            j+=1
        rhs_end=end
        j=position+2
        while j<end:
            if depth[j]==level and (body[j:j+2]==b"==" or body[j:j+1]==b","):
                rhs_end=j; break
            j+=1
        lhs=body[lhs_start:position].decode("ascii")
        rhs=body[position+2:rhs_end].decode("ascii")
        require(bool(lhs) and bool(rhs), "EMPTY_EQ_OPERAND")
        identity=sha256(
            b"GATE"+digest+number.to_bytes(4,"big")+position.to_bytes(4,"big")
        ).hexdigest()
        original=native_receipt["gates"][number]
        require(original["index"]==number and original["offset"]==position,
                "NATIVE_GATE_POSITION_MISMATCH")
        require(original["parenthesis_depth"]==level and
                original["occurrence_sha256"]==identity,
                "NATIVE_GATE_PROVENANCE_MISMATCH")
        require(original["truth"]=="UNRESOLVED", "UNAUTHORIZED_GATE_TRUTH")
        family=("PHASE_72" if number==0 else "PHASE_36" if number==39
                else "OUTER_CHAIN" if number in (19,20)
                else "LEFT_COPY" if number<19 else "RIGHT_COPY")
        nodes.append({
            "index":number,"source_offset":position,"depth":level,
            "container_open_offset":opening,
            "lhs":lhs,"rhs":rhs,
            "lhs_span":[lhs_start,position],"rhs_span":[position+2,rhs_end],
            "family":family,"occurrence_sha256":identity,
            "ordered_edge_sha256":sha256(
                b"ORDERED_EQ\0"+lhs.encode()+b"\0==\0"+rhs.encode()
            ).hexdigest(),
            "native_boolean_truth":"UNRESOLVED","proof_provider":None,
        })
    require([(g["source_offset"],g["depth"]) for g in nodes if g["depth"]==0]
            ==[(253,0),(256,0)], "OUTER_CHAIN_OFFSETS")
    require((nodes[0]["lhs"],nodes[0]["rhs"])==("u^72","x*y"), "PHASE72_GATE")
    require((nodes[39]["lhs"],nodes[39]["rhs"])==
            ("u^36","(y*x*w*z)/a^2"), "PHASE36_GATE")
    require(nodes[19]["rhs"]==nodes[20]["lhs"]=="x", "OUTER_CHAIN_MIDDLE")
    require(nodes[20]["rhs"].startswith("-y*(List(") and
            nodes[20]["rhs"].endswith("/(u^36==(y*x*w*z)/a^2))"),
            "OUTER_CHAIN_ORDER")
    pairs=[]
    for left in range(1,19):
        right=left+20
        a,b=nodes[left],nodes[right]
        require(a["family"]=="LEFT_COPY" and b["family"]=="RIGHT_COPY",
                "COPY_FAMILY")
        require(a["lhs"]==b["lhs"] and a["rhs"]==b["rhs"],
                "COPY_OPERATOR_DRIFT")
        require(b["source_offset"]-a["source_offset"]==250,"COPY_ADDRESS_DRIFT")
        require(a["occurrence_sha256"]!=b["occurrence_sha256"],
                "COPY_PROVENANCE_COLLAPSE")
        require(a["ordered_edge_sha256"]==b["ordered_edge_sha256"],
                "COPY_EDGE_MISMATCH")
        pairs.append({
            "left_gate":left,"right_gate":right,"address_delta":250,
            "ordered_edge_sha256":a["ordered_edge_sha256"],
            "cross_copy_truth":"UNRESOLVED",
        })
    return {
        "schema":"HHS_PASS220_V4_ORDERED_GATE_PROOF_OBLIGATIONS_V1",
        "source_sha256":SOURCE_SHA256,"source_bytes":SOURCE_BYTES,
        "native_provenance_run":native_receipt["workflow_run_id"],
        "native_source_hash216":native_receipt["source_hash216"],
        "gate_count":len(nodes),
        "families":{
            "LEFT_COPY":18,"RIGHT_COPY":18,"OUTER_CHAIN":2,
            "PHASE_72":1,"PHASE_36":1,
        },
        "gates":nodes,"copy_pairs":pairs,
        "copy_relation":"SAME_ORDERED_OPERANDS_DISTINCT_ADDRESSES_NOT_TRUTH",
        "shared_environment_root":None,
        "shared_environment_proven":False,
        "cross_layer_revalidation_proven":False,
        "typed_denominator_admissibility_proven":False,
        "all_40_gate_truths_proven":False,
        "pqc_signed_vm81_admission_verified":False,
        "canonical_hash72_hash216_transition_verified":False,
        "classification":"SOURCE_BOUND_PROOF_OBLIGATION_GRAPH_ONLY",
    }


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--native-receipt",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    result=build_obligations(
        args.source.read_bytes(),
        json.loads(args.native_receipt.read_text(encoding="utf-8")),
    )
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8",
    )
    print("V4_40_GATE_OBLIGATION_GRAPH_SOURCE_BOUND")
    print("identical_ordered_copy_edges="+str(len(result["copy_pairs"])))
    print("native_40_gate_truth=UNRESOLVED")
    print("signed_vm81_admission=NOT_PERFORMED")


if __name__=="__main__":
    main()
