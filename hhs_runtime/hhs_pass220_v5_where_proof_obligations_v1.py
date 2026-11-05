"""V5 Unicode where-clause proof obligations: positional metadata, never truth."""
from __future__ import annotations
import argparse
import json
from hashlib import sha256
from pathlib import Path

CLAUSE="where P⁴=AB=c⁴ and A/B≠B/A but P²=pq+(c²/(a²+b²)) and (p+q)/P(q-p)=(xy+zw)/b²"
RELATIONS=[
    ("P⁴","=","AB","P4_TO_AB"),
    ("AB","=","c⁴","AB_TO_C4"),
    ("A/B","≠","B/A","RECIPROCAL_DISTINCT"),
    ("P²","=","pq+(c²/(a²+b²))","P2_TYPED_RATIO"),
    ("(p+q)/P(q-p)","=","(xy+zw)/b²","PQ_PHASE_RATIO"),
]

class V5SourceError(ValueError):
    pass

def check(ok,code):
    if not ok: raise V5SourceError(code)

def compile_obligations(full:bytes,outer:bytes)->dict:
    check(full.count(b"\n")==2 and full.endswith(b"\n"),"FULL_BOUNDARY")
    check(outer.endswith(b"\n") and full.startswith(outer),"OUTER_BOUNDARY")
    try: source=full.decode("utf-8"); expression=outer.decode("utf-8").rstrip("\n")
    except UnicodeDecodeError as exc: raise V5SourceError("UTF8") from exc
    check(source==expression+"\n"+CLAUSE+"\n","SOURCE_CONTENT_CHANGED")
    check(len(expression)==528,"OUTER_LENGTH")
    gates=[]; depth=0; i=0
    while i<len(expression):
        ch=expression[i]
        if ch=="(": depth+=1
        elif ch==")":
            depth-=1
            check(depth>=0,"PAREN_UNDERFLOW")
        elif expression.startswith("==",i):
            gates.append((i,depth));i+=1
        i+=1
    check(depth==0 and len(gates)==40,"GATE_COUNT")
    check([i for i,d in gates if d==0]==[253,257],"OUTER_CHAIN")
    check(gates[39][0]==511,"HALF_PHASE_SOURCE")
    check(all(gates[i+20][0]-gates[i][0]==252 for i in range(1,19)),"COPY_ADDRESS")
    check(expression[253:263]=="==xA==-yB*","OUTER_CARRIER_ORDER")
    sha=sha256(full).digest()
    entries=[]
    for lhs,operator,rhs,label in RELATIONS:
        spelling=lhs+operator+rhs
        check(CLAUSE.count(spelling)==1,"WHERE_RELATION_AMBIGUITY")
        op_chars=CLAUSE.index(spelling)+len(lhs)
        offset=len(outer)+len(CLAUSE[:op_chars].encode("utf-8"))
        token=operator.encode("utf-8")
        identity=sha256(
            b"HHS-P220-V5-WHERE-OBLIGATION\0"+sha+
            offset.to_bytes(8,"big")+len(token).to_bytes(2,"big")+token+
            lhs.encode("utf-8")+b"\0"+rhs.encode("utf-8")
        ).hexdigest()
        entries.append(dict(
            label=label,lhs=lhs,operator=operator,rhs=rhs,
            source_operator_byte_offset=offset,
            exact_source_obligation_sha256=identity,
            native_truth="UNRESOLVED",global_typed_environment_root=None,
        ))
    check(len({r["source_operator_byte_offset"] for r in entries})==5,"WHERE_ADDRESS_COLLISION")
    carriers=[
        dict(spelling="xA",offset=255,typed_operator="UNRESOLVED_ORDERED_CARRIER"),
        dict(spelling="-yB",offset=259,typed_operator="UNRESOLVED_ORDERED_SIGNED_CARRIER"),
    ]
    check(expression[255:257]=="xA" and expression[259:262]=="-yB","TYPED_CARRIERS_CHANGED")
    return dict(
        schema="HHS_PASS220_V5_SOURCE_BOUND_AB_WHERE_OBLIGATIONS_V1",
        full_source_sha256=sha.hex(),outer_component_sha256=sha256(outer).hexdigest(),
        full_source_bytes=len(full),outer_source_bytes=len(outer),
        where_declarative_equals_count=4,where_directional_distinction_count=1,
        where_obligations=entries,typed_carriers=carriers,
        outer_boolean_gate_count=40,top_level_gate_offsets=[253,257],
        paired_inner_gate_count=18,paired_gate_source_delta=252,
        global_environment_verified=False,all_40_gate_truths_proven=False,
        where_native_semantics_proven=False,signed_vm81_admission_verified=False,
        canonical_hash72_hash216_transition_verified=False,
        classification="SOURCE_BOUND_V5_AB_WHERE_OBLIGATIONS_ONLY",
    )

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--full",type=Path,required=True)
    p.add_argument("--outer",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=compile_obligations(a.full.read_bytes(),a.outer.read_bytes())
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("V5_FIVE_WHERE_OBLIGATIONS_SOURCE_BOUND")
    print("V5_WHERE_AND_40_GATE_TRUTHS_UNRESOLVED")

if __name__=="__main__": main()
