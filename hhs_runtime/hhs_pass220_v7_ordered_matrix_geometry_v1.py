"""Source-bound 3x3 noncommutative denominator and exact 5184-address bijection.

This module neither inverts a matrix nor assigns scalar values to native ordered
carriers. The 9 outer cells are separate positional macros over 9 subcells x 64
bit lanes: a bijection to VM81 (81x64) and the 72x72 Hash72 address lattice.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

SOURCE="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))"
ROWS=[
    ["yx","y+w","wx"],
    ["-xy-wz","x+y-z-w+xy+yx-zw-wz","-zw-yx"],
    ["xy","x-z","zw"],
]
CENTER_TERMS=["x","+y","-z","-w","+xy","+yx","-zw","-wz"]
CARRIERS=("yx","wx","xy","wz","zw")
SITE_COUNT=9
SUBCELLS=9
LANE_BITS=64
VM_CELLS=81
HASH72_SIDE=72
TOTAL_BITS=5184

class V7SourceError(ValueError):
    pass

def require(condition:bool,code:str)->None:
    if not condition:
        raise V7SourceError(code)

def _split_top_level(source:str)->list[str]:
    stack=[]
    ranges=[]
    start=0
    for offset,symbol in enumerate(source):
        if symbol=="(":
            stack.append(offset)
        elif symbol==")":
            require(bool(stack),"UNMATCHED_CLOSE")
            stack.pop()
        elif symbol=="," and not stack:
            ranges.append(source[start:offset])
            start=offset+1
    require(not stack,"UNMATCHED_OPEN")
    ranges.append(source[start:])
    return ranges

def parse_quotient(source_bytes:bytes)->dict:
    require(source_bytes==(SOURCE+"\n").encode("ascii"),"UNAUTHORIZED_SOURCE_MUTATION")
    expr=source_bytes[:-1].decode("ascii")
    prefix="(81*64)/("
    require(expr.startswith(prefix) and expr.endswith(")"),"QUOTIENT_SYNTAX")
    source_rows=_split_top_level(expr[len(prefix):-1])
    require(len(source_rows)==3,"MATRIX_ROW_COUNT")
    parsed=[]
    for row in source_rows:
        require(row.startswith("(") and row.endswith(")"),"ROW_PARENTHESIS")
        entries=_split_top_level(row[1:-1])
        require(len(entries)==3,"MATRIX_CELL_COUNT")
        parsed.append(entries)
    require(parsed==ROWS,"SOURCE_ORDER_DRIFT")
    require("".join(CENTER_TERMS)==parsed[1][1],"CENTER_CHANNEL_ORDER")
    gate_words=[
        {"word":m.group(1),"source_byte_offset":m.start(),
         "word_order":"ORDERED_NATIVE_CHANNEL"}
        for m in re.finditer(r"(?<![A-Za-z])(yx|wx|xy|wz|zw)(?![A-Za-z])",expr)
    ]
    require([x["word"] for x in gate_words]==[
        "yx","wx","xy","wz","xy","yx","zw","wz","zw","yx","xy","zw"
    ],"ORDERED_WORD_INVENTORY")
    root=sha256(source_bytes).digest()
    cells=[]
    cursor=0
    for r,row in enumerate(ROWS):
        for c,cell in enumerate(row):
            offset=expr.find(cell,cursor)
            require(offset>=cursor,"CELL_ADDRESS_PROVENANCE")
            position=3*r+c
            cell_id=sha256(
                b"HHS-PASS220-V7-ORDERED-3X3-CELL\0"+root+
                position.to_bytes(2,"big")+offset.to_bytes(8,"big")+
                cell.encode("ascii")
            ).hexdigest()
            cells.append({
                "row":r,"col":c,"macro_site":position,
                "raw_source_expression":cell,"source_byte_offset":offset,
                "occurrence_sha256":cell_id,
                "type":"ORDERED_NATIVE_TENSOR_CELL",
                "native_semantic_value":"UNRESOLVED",
                "division_operand_status":"UNRESOLVED",
            })
            cursor=offset+len(cell)
    require(len({c["source_byte_offset"] for c in cells})==9,
            "CELL_ADDRESS_COLLISION")
    return {
        "schema":"HHS_PASS220_V7_ORDERED_DENOMINATOR_5184_ADDRESS_BIJECTION_V1",
        "source_sha256":root.hex(),
        "source_bytes":len(source_bytes),
        "numerator_exact_integer":81*64,
        "matrix":[list(row) for row in parsed],
        "matrix_macro_site_count":9,
        "nested_subcells_per_macro":9,
        "bits_per_vm81_cell":64,
        "vm81_cells":81,
        "hash72_lattice":[72,72],
        "fixed_width_positions":5184,
        "ordered_channel_tokens":gate_words,
        "center_ordered_terms":list(CENTER_TERMS),
        "source_bound_macro_sites":cells,
        "matrix_denominator_operation":"NATIVE_ORDERED_QUOTIENT_UNRESOLVED",
        "matrix_inverse_proven":False,
        "global_denominator_admissibility_proven":False,
        "source_specific_native_tensor_truth_proven":False,
        "pqc_signed_vm81_admission_verified":False,
        "canonical_hash72_hash216_transition_verified":False,
        "classification":"SOURCE_BOUND_V7_MATRIX_AND_5184_ADDRESS_GEOMETRY_ONLY",
    }

def to_hash72_address(macro_site:int,subcell:int,bit:int)->tuple[int,int]:
    for name,v,upper in (("macro",macro_site,9),("subcell",subcell,9),
                         ("bit",bit,64)):
        if type(v) is not int or not (0<=v<upper):
            raise V7SourceError("INVALID_"+name.upper()+"_ADDRESS")
    n=((macro_site*9+subcell)*64)+bit
    return (n//72,n%72)

def from_hash72_address(row:int,col:int)->tuple[int,int,int]:
    for name,value in (("row",row),("col",col)):
        if type(value) is not int or not (0<=value<72):
            raise V7SourceError("INVALID_HASH72_"+name.upper())
    n=row*72+col
    vm_cell,bit=divmod(n,64)
    macro_site,subcell=divmod(vm_cell,9)
    return macro_site,subcell,bit

def verify_bijection()->dict:
    locations=set()
    for site in range(9):
        for subcell in range(9):
            for bit in range(64):
                address=to_hash72_address(site,subcell,bit)
                require(address not in locations,"NON_INJECTIVE_ADDRESS")
                locations.add(address)
                require(from_hash72_address(*address)==(site,subcell,bit),
                        "BROKEN_ADDRESS_ROUNDTRIP")
    require(len(locations)==81*64==72*72==5184,"ADDRESS_SPACE_SIZE")
    require(len({(r,c) for r in range(72) for c in range(72)}
               -locations)==0,"INCOMPLETE_ADDRESS_COVERAGE")
    return {
        "macro_cells":9,"subcells_per_macro":9,"bits_per_subcell":64,
        "total_vm81_cells":81,"bijective_positions":5184,
        "hash72_lattice_positions":72**2,
        "address_roundtrip":"VERIFIED",
        "phase_equation_u72_equals_1":"SEPARATE_DECLARED_INVARIANT_NOT_DERIVED",
        "vm81_native_signed_admission":"NOT_PERFORMED",
    }

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    record=parse_quotient(a.source.read_bytes())
    record["address_bijection"]=verify_bijection()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n",
                        encoding="utf-8")
    print("V7_ORDERED_3X3_SOURCE_BOUND=PASS")
    print("V7_VM81_HASH72_5184_ADDRESS_BIJECTION=PASS")
    print("V7_NATIVE_MATRIX_DIVISION_TRUTH=UNRESOLVED")

if __name__=="__main__":main()
