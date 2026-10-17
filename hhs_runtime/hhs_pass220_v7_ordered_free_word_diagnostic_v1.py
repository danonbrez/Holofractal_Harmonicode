"""V7 exact ordered free-word *diagnostic*, never the HHS canonical algebra.

The unsigned and signed ordered words here belong to a separate comparison
model over an additive Z-module on noncommuting x/y/z/w words. This model does
not grant scalar substitution, matrix inversion, VM81 proof, or zero-state
interpretations to canonical HHS cells.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from hashlib import sha256
from pathlib import Path

from hhs_runtime.hhs_pass220_v7_ordered_matrix_geometry_v1 import (
    ROWS, V7SourceError, parse_quotient,
)

BASIS=("x","y","z","w","xy","yx","zw","wz","wx")
SIGNED_CENTER=(("x",1),("y",1),("z",-1),("w",-1),
               ("xy",1),("yx",1),("zw",-1),("wz",-1))
EXPECTED_COLS=(
    {"yx":1,"wz":-1},
    {"x":2,"y":2,"z":-2,"xy":1,"yx":1,"zw":-1,"wz":-1},
    {"yx":-1,"wx":1},
)
EXPECTED_ROWS=(
    {"y":1,"w":1,"yx":1,"wx":1},
    {"x":1,"y":1,"z":-1,"w":-1,"zw":-2,"wz":-2},
    {"x":1,"z":-1,"xy":1,"zw":1},
)

def check(ok:bool,why:str)->None:
    if not ok:
        raise V7SourceError(why)

def lex_ordered_terms(spelling:str)->list[dict]:
    """Read plus/minus and each word in its ORIGINAL left-to-right order."""
    i=0
    terms=[]
    while i<len(spelling):
        sign=1
        start=i
        if spelling[i] in "+-":
            sign=-1 if spelling[i]=="-" else 1
            i+=1
        j=i
        while i<len(spelling) and spelling[i] in "xyzw":
            i+=1
        check(i>j,"UNKNOWN_ORDERED_WORD")
        word=spelling[j:i]
        check(word in BASIS,"UNREGISTERED_DIAGNOSTIC_WORD")
        terms.append({"word":word,"coefficient":sign,"relative_offset":j,
                      "signed_span":[start,i]})
        check(i==len(spelling) or spelling[i] in "+-",
              "ILLEGAL_OPERATOR_SEPARATOR")
    check(bool(terms),"EMPTY_CELL")
    return terms

def as_exact_word_vector(terms:list[dict])->dict[str,int]:
    # Only identical words are coefficient-combined: xy and yx are DISTINCT.
    accum:Counter[str]=Counter()
    for term in terms:
        accum[term["word"]]+=term["coefficient"]
    return {word:accum[word] for word in BASIS if accum[word]!=0}

def compute(raw:bytes)->dict:
    geometry=parse_quotient(raw)  # exact V7 source and nine positions
    cells=[]
    word_tokens=[]
    for site,cell in enumerate(geometry["source_bound_macro_sites"]):
        parsed=lex_ordered_terms(cell["raw_source_expression"])
        if site==4:
            check([(t["word"],t["coefficient"]) for t in parsed]==list(SIGNED_CENTER),
                  "CENTER_ORDER_OR_SIGN")
        for term in parsed:
            copy=dict(term)
            copy.update({
                "site":site,"row":site//3,"col":site%3,
                "absolute_source_byte_offset":cell["source_byte_offset"]+term["relative_offset"],
                "native_typed_value":"UNRESOLVED",
            })
            word_tokens.append(copy)
        cells.append({
            "site":site,"row":site//3,"col":site%3,
            "cell_source_sha256":cell["occurrence_sha256"],
            "ordered_terms":parsed,
            "free_word_vector":as_exact_word_vector(parsed),
            "native_cell_proof":"UNRESOLVED",
        })
    row_vectors=[]
    col_vectors=[]
    for i in range(3):
        row_terms=[term for c in cells[i*3:i*3+3] for term in c["ordered_terms"]]
        col_terms=[term for c in cells[i::3] for term in c["ordered_terms"]]
        row_vectors.append(as_exact_word_vector(row_terms))
        col_vectors.append(as_exact_word_vector(col_terms))
    check(tuple(row_vectors)==EXPECTED_ROWS,"FREE_WORD_ROW_CHECK")
    check(tuple(col_vectors)==EXPECTED_COLS,"FREE_WORD_COLUMN_CHECK")
    diagonal_vectors=[
        as_exact_word_vector([t for i in (0,4,8) for t in cells[i]["ordered_terms"]]),
        as_exact_word_vector([t for i in (2,4,6) for t in cells[i]["ordered_terms"]]),
    ]
    check(diagonal_vectors[0]!=diagonal_vectors[1],"DIAGONAL_FORMALLY_DISTINCT")
    check("xy"!= "yx" and "zw"!="wz" and "wx"!="xw","WORD_DISTINCTION")
    digest=sha256(raw).hexdigest()
    return {
        "schema":"HHS_PASS220_V7_NONCANONICAL_ORDERED_FREE_WORD_DIAGNOSTIC_V1",
        "exact_source_sha256":digest,
        "ordered_word_basis":list(BASIS),
        "term_occurrences":word_tokens,
        "cells":cells,
        "row_vectors":row_vectors,
        "column_vectors":col_vectors,
        "diagonal_vectors":diagonal_vectors,
        "free_word_projection_has_equal_row_column_magic_sum":False,
        "native_hnan_15_rules_verified_by_separate_C":False,
        "matrix_ordered_quotient_admissibility_verified":False,
        "matrix_native_inverse_or_division_proved":False,
        "signed_environmental_vm81_admission_verified":False,
        "canonical_hash72_hash216_transition_verified":False,
        "classification":"DIAGNOSTIC_FREE_WORD_COMPARISON_NOT_HHS_VM81_PROOF",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    record=compute(a.source.read_bytes())
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("V7_ORDERED_FREE_WORD_DIAGNOSTIC=PASS")
    print("V7_COLUMN0=yx-wz")
    print("V7_COLUMN2=wx-yx")
    print("V7_MATRIX_QUOTIENT_SEMANTICS=UNRESOLVED")

if __name__=="__main__":
    main()
