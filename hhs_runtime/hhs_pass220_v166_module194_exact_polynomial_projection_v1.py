"""Pass 220 V166: independently check 81 symbolic fractalization projections.

Two separate obligations:
(1) Inherited V165 requires a real C HNAN 1.63 scope witness and source bytes.
(2) This module independently expands all 81 polynomial *coordinate
    projections* into exact integer coefficients and compares them with
    direct binomial references, preserving original ordered AST separately.

This scalar polynomial audit does not commute native HNAN operators, prove
A/B orientation, or make any physical/VM81 admission claim.
"""
from __future__ import annotations
from hashlib import sha256
from math import comb
import json
from typing import Any

from hhs_runtime.hhs_pass220_v165_module194_ordered_fractal_tensor_v1 import (
    inspect_ordered_tensor, flattened_source_tensor,
)

SCHEMA="HHS_PASS_220_V166_MODULE194_EXACT_POLYNOMIAL_PROJECTION_V1"
WEIGHTS=(4,9,2,3,5,7,8,1,6)


class V166ProjectionError(ValueError):
    pass


def _add(a:dict,b:dict)->dict:
    out=dict(a)
    for exp,value in b.items():
        out[exp]=out.get(exp,0)+value
    return {e:v for e,v in out.items() if v}


def _mul(a:dict,b:dict)->dict:
    out={}
    for (ai,bi),av in a.items():
        for (aj,bj),bv in b.items():
            k=(ai+aj,bi+bj)
            out[k]=out.get(k,0)+av*bv
    return {e:v for e,v in out.items() if v}


def _polynomial(node:Any)->dict:
    if not isinstance(node,tuple) or not node:
        raise V166ProjectionError("V166_SYMBOLIC_AST_REQUIRED")
    op=node[0]
    if op=="CellSymbol" and len(node)==2 and node[1] in ("a","b"):
        return {(1,0):1} if node[1]=="a" else {(0,1):1}
    if op=="Power" and len(node)==3 and type(node[2]) is int and 0<=node[2]<=16:
        base=_polynomial(node[1])
        out={(0,0):1}
        for _ in range(node[2]):
            out=_mul(out,base)
        return out
    if op=="Sum" and len(node)==3:
        return _add(_polynomial(node[1]),_polynomial(node[2]))
    if op=="OrderedWeight" and len(node)==3 and type(node[1]) is int:
        return {e:node[1]*v for e,v in _polynomial(node[2]).items()}
    raise V166ProjectionError("V166_UNREGISTERED_AST_OPERATOR")


def _expected_inner(row:int,col:int)->dict:
    # Independent direct coefficient oracle: without rewriting source AST.
    if type(row) is not int or type(col) is not int or not (0<=row<3 and 0<=col<3):
        raise V166ProjectionError("V166_REFERENCE_ADDRESS_RANGE")
    if col==0:
        n=2
        return ({(n,0):1} if row==0 else
                {(2*n,0):1} if row==1 else
                {(2*n,0):1,(4*n,0):1})
    if col==1:
        n=4
        return ({(n,0):1} if row==0 else
                {(2*n,0):1} if row==1 else
                {(2*n,0):1,(4*n,0):1})
    if row==0:
        return {(4,0):1,(0,2):1}
    powers=(2,) if row==1 else (2,4)
    result={}
    for power in powers:
        for k in range(power+1):
            e=(4*(power-k),2*k)
            result[e]=result.get(e,0)+comb(power,k)
    return result


def _canonical_poly(poly:dict)->list:
    return [[a,b,c] for (a,b),c in sorted(poly.items())]


def inspect_exact_projection(source:bytes,native_library:Any,*,
                             require_upload_identity:bool=True)->dict:
    witness=inspect_ordered_tensor(
        source,native_library,require_upload_identity=require_upload_identity)
    if (witness.get("ordered_81_source_entries")!=81
        or witness.get("vm81_admission") is not False
        or witness.get("native_hnan_ab_ba_for_fractal_tensor_proved") is not False):
        raise V166ProjectionError("V166_INHERITED_SCOPE_REJECTED")
    entries=flattened_source_tensor()
    if len(entries)!=81:
        raise V166ProjectionError("V166_ADDRESS_COUNT")
    seen=set()
    coefficients=[]
    for i,j,r,k,node in entries:
        address=(i,j,r,k)
        if address in seen or any(type(v) is not int or not 0<=v<3 for v in address):
            raise V166ProjectionError("V166_DUPLICATE_OR_BAD_ADDRESS")
        seen.add(address)
        weight=WEIGHTS[i*3+j]
        if (not isinstance(node,tuple) or len(node)!=3 or
            node[0]!="OrderedWeight" or node[1]!=weight):
            raise V166ProjectionError("V166_LOSHU_WEIGHT_OR_ORDER")
        observed=_polynomial(node)
        expected={e:weight*v for e,v in _expected_inner(r,k).items()}
        if observed!=expected:
            raise V166ProjectionError("V166_EXACT_POLYNOMIAL_MISMATCH")
        coefficients.append([*address,_canonical_poly(observed)])
    if len(seen)!=81:
        raise V166ProjectionError("V166_ADDRESS_COVERAGE")
    digest=sha256(json.dumps(coefficients,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {
        "schema":SCHEMA,
        "module194_source_sha256":witness["module194_source_sha256"],
        "inherited_native_hnan_system_signature64":witness["inherited_native_hnan_global_signature64"],
        "original_ordered_tensor_ast_sha256":witness["fractalization_ast_sha256"],
        "exact_projection_coefficient_sha256":digest,
        "exact_polynomial_projection_entries_verified":81,
        "exact_integer_coefficients_only":True,
        "original_ordered_tensor_preserved":True,
        "native_ab_ba_closure_for_input_proved":False,
        "typed_interior_outer_closure_proved":False,
        "complete_196_module_source_coverage_verified":False,
        "physical_force_equivalence_proved":False,
        "vm81_admission":False,
        "hash72_hash216_minted":False,
    }
