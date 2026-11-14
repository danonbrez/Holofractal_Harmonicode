"""Pass220 V171: real inherited native C ordered phase product observations.

Executes existing hhs_exact_phase_product for xy/yx and zw/wz.
Does NOT pretend the four basis products are the 81-address Module194
input-specific products AB and BA; their equivalence has not been proved.
The V170 source/Lean premise inspection runs first. No new native operator.
"""
from __future__ import annotations

import ctypes as C
from hashlib import sha256
import json
from typing import Any

from hhs_runtime.hhs_pass220_v170_module194_ordered_product_proof_dependency_v1 import (
    inspect_ordered_product_dependency,
)
from hhs_runtime.hhs_pass220_v167_module194_typed_closure_packet_v1 import (
    typed_packet,
)
from hhs_python.runtime.hhs_exact_ctypes_bridge import HHSExactPhaseProduct

SCHEMA = "HHS_PASS220_V171_MODULE194_NATIVE_ORDERED_PHASE_PRODUCT_V1"
ORDERED_BASIS = (("xy",0,1,0,1,0x5859),
                 ("yx",1,0,36,2,0x5958),
                 ("zw",2,3,0,1,0x5A57),
                 ("wz",3,2,36,2,0x575A))


class V171NativeProductError(ValueError):
    pass


def inspect_native_ordered_products(
    source: bytes, native_library: Any, *,
    repository_root: Any = ".",
    require_upload_identity: bool = True,
) -> dict:
    previous=inspect_ordered_product_dependency(
        source,native_library,repository_root=repository_root,
        require_upload_identity=require_upload_identity)
    if (previous.get("canonical_vm81_admission") is not False
        or previous.get("input_specific_direct_product_equation_proved") is not False
        or previous.get("input_specific_reverse_product_equation_proved") is not False):
        raise V171NativeProductError("V171_UPSTREAM_PROOF_PROMOTION_REJECTED")
    if not isinstance(native_library,C.CDLL):
        raise V171NativeProductError("V171_NATIVE_CDLL_REQUIRED")
    op=native_library.hhs_exact_phase_product
    op.argtypes=[C.c_uint8,C.c_uint8,C.POINTER(HHSExactPhaseProduct)]
    op.restype=C.c_int
    values=[]
    for name,left,right,phase,orientation,tag in ORDERED_BASIS:
        out=HHSExactPhaseProduct()
        status=op(left,right,C.byref(out))
        if (status!=0 or out.struct_size!=C.sizeof(HHSExactPhaseProduct)
            or out.left_basis!=left or out.right_basis!=right
            or out.phase!=phase or out.orientation!=orientation
            or out.ordered_tag!=tag or out.closure!=1):
            raise V171NativeProductError("V171_NATIVE_ORDERED_PRODUCT_REJECTED:"+name)
        values.append({
            "channel":name,"left_basis":left,"right_basis":right,
            "phase72":int(out.phase),"raw_additive_phase72":int(out.raw_additive_phase),
            "orientation":int(out.orientation),
            "ordered_tag":int(out.ordered_tag),"closure":int(out.closure),
            "native_abi_version":int(out.abi_version),
        })
    if not (values[0]["ordered_tag"]!=values[1]["ordered_tag"]
            and values[2]["ordered_tag"]!=values[3]["ordered_tag"]
            and values[0]["phase72"]==values[2]["phase72"]==0
            and values[1]["phase72"]==values[3]["phase72"]==36):
        raise V171NativeProductError("V171_NATIVE_DIRECTION_COLLAPSE")
    packet=typed_packet()
    leaves=packet["A"][2]
    if len(leaves)!=81 or len({tuple(x[1]) for x in leaves})!=81:
        raise V171NativeProductError("V171_MODULE194_SOURCE_ADDRESSES_REJECTED")
    payload={
        "schema":SCHEMA,
        "source_sha256":previous["module194_source_sha256"],
        "typed_packet_sha256":previous["module194_typed_packet_sha256"],
        "ordered_product_lean_sha256":previous["ordered_product_lean_source_sha256"],
        "inherited_hnan_signature64":previous["inherited_native_hnan_signature64"],
        "module194_source_group_addresses":81,
        "native_ordered_phase_products":values,
    }
    payload["observation_sha256"]=sha256(
        json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    payload.update({
        "inherited_native_phase_product_executed":True,
        "native_module194_AB_value_identified":False,
        "native_module194_BA_value_identified":False,
        "native_basis_to_module194_operand_equivalence_proved":False,
        "lean_input_specific_product_certificate_constructed":False,
        "module194_hnan_interior_outer_closure_proved":False,
        "physical_force_equivalence_verified":False,
        "canonical_vm81_admission":False,
        "hash72_hash216_minted":False,
    })
    return payload
