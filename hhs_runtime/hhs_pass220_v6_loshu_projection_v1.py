"""V6: exact-rational Lo Shu projection of original 3-line ordered source.

Conditional numeric coordinate evaluation, NOT native == truth or signed VM81
authority. Preserve xy/zw/yxwz as typed source symbols, never commute them.
"""
from __future__ import annotations
import argparse
import json
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

OUTER="List((u^72==xy)/List(List(x==-y,x+y==0,xy,y==a^2/x),List(z==-w,z+w==0,zw,w==a^2/w),List(c^2-b^2-a^2,a^2==c^2-b^2,b^2==c^2-a^2==xy+zw,c^2==a^2+b^2)/((xy+zw)/b^2==a^2+x+y-z-w)),-List(1==zw,1==xy,6==b^2c^2==b^2+c^2+a^2,(-(e^2==c^2+d^2==b^6==8))))==xA==-yB\\*(List(List(List(x==-y,x+y==0,xy,y==a^2/x),List(z==-w,z+w==0,zw,w==a^2/w),List(c^2-b^2-a^2,a^2==c^2-b^2,b^2==c^2-a^2==xy+zw,c^2==a^2+b^2)/((xy+zw)/b^2==a^2+x+y-z-w)),-List(1==zw,1==xy,6==b^2c^2==b^2+c^2+a^2,(-(e^2==c^2+d^2==b^6==8))))/(u^36==(yxwz)/a^2))"
WHERE="where P⁴=AB=c⁴ and A/B≠B/A but P²=pq+(c²/(a²+b²)) and (p+q)/P(q-p)=(xy+zw)/b²"
MATRIX="((b⁴,P⁴=AB=c⁴,b²=c²-a²),(c²=a²+b²,d²=b²+c²,((b⁶-a²)(c²+b⁴))/(d²+b²)),(e²=b⁶=c²+d²,a²=(xy+zw)/(c²-a²),b²c²=a²+b²+c²))"
SOURCE=OUTER+"\n"+WHERE+"\n"+MATRIX+"\n"
CELLS=["b⁴","P⁴=AB=c⁴","b²=c²-a²","c²=a²+b²",
       "d²=b²+c²","((b⁶-a²)(c²+b⁴))/(d²+b²)",
       "e²=b⁶=c²+d²","a²=(xy+zw)/(c²-a²)","b²c²=a²+b²+c²"]

class V6ProjectionError(ValueError): pass

def check(ok,code):
    if not ok: raise V6ProjectionError(code)

def slots(expression):
    depth=0; positions=[]; i=0
    while i<len(expression):
        ch=expression[i]
        if ch=="(": depth+=1
        elif ch==")":
            depth-=1;check(depth>=0,"PAREN_UNDERFLOW")
        elif expression[i:i+2]=="==":
            positions.append((i,depth));i+=1
        i+=1
    check(depth==0,"PAREN_UNCLOSED")
    return positions

def project(raw):
    try: text=raw.decode("utf-8")
    except UnicodeDecodeError as exc: raise V6ProjectionError("BAD_UTF8") from exc
    check(text==SOURCE,"VERBATIM_SOURCE_CHANGED")
    gates=slots(OUTER)
    check(len(gates)==40 and [i for i,d in gates if d==0]==[243,247],
          "ORDERED_GATE_GEOMETRY")
    check(all(gates[i+20][0]-gates[i][0]==244 for i in range(1,19)),
          "COPY_ADDRESS_DISTINCTNESS")
    a2,b2,c2,d2,e2,xy,zw=[Fraction(i) for i in (1,2,3,5,8,1,1)]
    check(c2==a2+b2 and d2==b2+c2 and e2==c2+d2,"ROOTS")
    check(c2-a2!=0 and d2+b2!=0,"PROJECTED_DENOMINATOR")
    values=[
        b2**2,c2**2,c2-a2,a2+b2,b2+c2,
        ((b2**3-a2)*(c2+b2**2))/(d2+b2),
        b2**3,(xy+zw)/(c2-a2),b2*c2]
    check([int(v) for v in values]==[4,9,2,3,5,7,8,1,6],"LOSHU_PROJECTION")
    mat=[values[0:3],values[3:6],values[6:9]]
    row_sums=[sum(row) for row in mat]
    col_sums=[sum(mat[i][j] for i in range(3)) for j in range(3)]
    diagonal_sums=[sum(mat[i][i] for i in range(3)),
                   sum(mat[i][2-i] for i in range(3))]
    check(row_sums==col_sums==[15]*3 and diagonal_sums==[15,15],
          "MAGIC_SQUARE_SUM")
    check(sorted(values)==list(map(Fraction,range(1,10))),"LOSHU_PERMUTATION")
    centered=[[int(v-5) for v in row] for row in mat]
    check(all(sum(row)==0 for row in centered),"CENTERED_ROW")
    check(all(sum(centered[i][j] for i in range(3))==0 for j in range(3)),
          "CENTERED_COLUMN")
    check(sum(centered[i][i] for i in range(3))==
          sum(centered[i][2-i] for i in range(3))==0,"CENTERED_DIAGONAL")
    root=sha256(raw).digest()
    matrix_start=len((OUTER+"\n"+WHERE+"\n").encode("utf-8"))
    origin=0; witness=[]
    for n,(cell,value) in enumerate(zip(CELLS,values)):
        at=MATRIX.find(cell,origin)
        check(at>=0,"CELL_ORDER")
        byte_offset=matrix_start+len(MATRIX[:at].encode("utf-8"))
        fp=sha256(
            b"HHS-PASS220-V6-PROJECTED-CELL\0"+root+
            n.to_bytes(2,"big")+byte_offset.to_bytes(8,"big")+
            cell.encode("utf-8")).hexdigest()
        witness.append({"index":n,"row":n//3,"col":n%3,
                        "original_expression":cell,"source_byte_offset":byte_offset,
                        "projected_exact_value":str(value),
                        "centered_value":str(value-5),
                        "occurrence_sha256":fp,"native_gate_truth":"UNRESOLVED"})
        origin=at+len(cell)
    check(len({w["source_byte_offset"] for w in witness})==9,"CELL_OFFSET")
    return {
        "schema":"HHS_PASS220_V6_CONDITIONAL_LOSHU_EXACT_PROJECTION_V1",
        "source_sha256":root.hex(),"source_bytes":len(raw),
        "raw_escaped_asterisk_preserved":("\\"+"*") in OUTER,
        "ordered_native_carrier_spellings":["xy","zw","yxwz","b^2c^2","xA","-yB"],
        "outer_boolean_gate_count":40,"outer_gate_offsets":[243,247],
        "ordered_inner_copy_pairs":18,"copy_source_offset_delta":244,
        "assumed_projection_roots":{"a²":1,"b²":2,"c²":3,"d²":5,
                                    "e²":8,"xy":1,"zw":1},
        "matrix":[[int(v) for v in row] for row in mat],
        "zero_centered_matrix":centered,
        "row_sums":[int(x) for x in row_sums],
        "column_sums":[int(x) for x in col_sums],
        "diagonal_sums":[int(x) for x in diagonal_sums],
        "rational_polynomial_vertex":str(values[5]),
        "projected_phase_ratio":str((xy+zw)/b2),
        "nucleus_coordinate":5,
        "source_bound_cell_positions":witness,
        "all_40_native_boolean_gates_proven":False,
        "native_negative_List_mask_proven":False,
        "native_where_constraints_proven":False,
        "native_typed_AB_noncommutation_proven":False,
        "signed_vm81_admission_verified":False,
        "canonical_hash72_hash216_transition_verified":False,
        "classification":"EXACT_CONDITIONAL_LOSHU_PROJECTION_NOT_NATIVE_VM81_PROOF"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=project(a.source.read_bytes())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("V6_LOSHU_GRID=4,9,2/3,5,7/8,1,6")
    print("V6_LOSHU_MAGIC_SUMS=15")
    print("V6_ZERO_CENTER_MAGIC_SUMS=0")
    print("V6_CANONICAL_40_GATE_TRUTH_UNRESOLVED")
if __name__=="__main__":main()
