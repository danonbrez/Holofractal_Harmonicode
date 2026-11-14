"""Pass220 V172: read-only inherited VM81-word -> octonion phase projection.

Accepts an explicit 81-word observation frame, never manufactures a
canonical VM81 frame from the browser Module194 tensor. Calls the inherited
Pass219 octonion_from_vm81, validate_surface, and multiply C functions.
Selected four group addresses and full source identity are retained.
The fold of 64-bit words to mod-72 phases is lossy: it cannot prove that
Module194's 81-entry typed A/B products equal the octonion basis products.
"""
from __future__ import annotations
import ctypes as C
from hashlib import sha256
import json
from typing import Any

from hhs_runtime.hhs_pass220_v171_module194_native_ordered_phase_product_v1 import (
    inspect_native_ordered_products,
)
from hhs_runtime.hhs_pass220_v160_module194_source_address_preflight_v1 import address

SCHEMA="HHS_PASS220_V172_MODULE194_VM81_OCTONION_PROJECTION_V1"
MAX_WORD=(1<<64)-1
ORDERED=((0,1,"xy"),(1,0,"yx"),(2,3,"zw"),(3,2,"wz"))


class V172OctonionError(ValueError):
    pass


class VM81Frame(C.Structure):
    _fields_=[("words",C.c_uint64*81)]


class OctonionState(C.Structure):
    _fields_=[(k,C.c_uint32) for k in ("struct_size","version")]+[
        (k,C.c_uint8) for k in ("x","y","z","w","xy","yx","zw","wz")
    ]


class OctonionProduct(C.Structure):
    _fields_=[(k,C.c_uint32) for k in ("struct_size","version")]+[
        (k,C.c_uint8) for k in (
            "left_basis","right_basis","left_phase","right_phase",
            "raw_additive_phase","phase","orientation","closure",
            "ordered_pair_index","reserved0")
    ]+[("ordered_tag",C.c_uint16)]


class OctonionSurface(C.Structure):
    _fields_=[(k,C.c_uint32) for k in (
        "struct_size","version","product_count","noncommutative_generator_pairs"
    )]+[("state",OctonionState),("products",OctonionProduct*64)]


def observe_vm81_octonion(
    source:bytes,
    native_library:C.CDLL,
    frame_words:tuple[int,...],
    group_cells:tuple[int,int,int,int],
    *,
    repository_root:Any=".",
    require_upload_identity:bool=True,
)->dict:
    inherited=inspect_native_ordered_products(
        source,native_library,repository_root=repository_root,
        require_upload_identity=require_upload_identity)
    if (inherited.get("inherited_native_phase_product_executed") is not True or
        inherited.get("canonical_vm81_admission") is not False or
        inherited.get("native_basis_to_module194_operand_equivalence_proved") is not False):
        raise V172OctonionError("V172_INHERITED_SCOPE_REJECTED")
    if not isinstance(native_library,C.CDLL):
        raise V172OctonionError("V172_NATIVE_CDLL_REQUIRED")
    if (type(frame_words) is not tuple or len(frame_words)!=81 or
        any(type(w) is not int or not 0<=w<=MAX_WORD for w in frame_words)):
        raise V172OctonionError("V172_EXACT_81_WORD_FRAME_REQUIRED")
    if (type(group_cells) is not tuple or len(group_cells)!=4 or
        any(type(c) is not int or not 0<=c<81 for c in group_cells) or
        len(set(group_cells))!=4):
        raise V172OctonionError("V172_FOUR_DISTINCT_GROUP_ADDRESSES_REQUIRED")
    # Group ids are the existing Module194 0..80 addresses, not new cells.
    groups=[address(i*64) for i in group_cells]
    if any(g["group"]!=i or g["reciprocal_cluster"]!=0
           for i,g in zip(group_cells,groups)):
        raise V172OctonionError("V172_GROUP_ADDRESS_DRIFT")
    frame=VM81Frame((C.c_uint64*81)(*frame_words))
    surface=OctonionSurface()
    project=native_library.hhs_exact_pass219_octonion_from_vm81
    project.argtypes=[C.POINTER(VM81Frame)]+[C.c_uint8]*4+[C.POINTER(OctonionSurface)]
    project.restype=C.c_int
    validate=native_library.hhs_exact_pass219_octonion_validate_surface
    validate.argtypes=[C.POINTER(OctonionSurface)]
    validate.restype=C.c_int
    multiply=native_library.hhs_exact_pass219_octonion_multiply
    multiply.argtypes=[C.POINTER(OctonionState),C.c_uint8,C.c_uint8,C.POINTER(OctonionProduct)]
    multiply.restype=C.c_int
    if project(C.byref(frame),*group_cells,C.byref(surface))!=0:
        raise V172OctonionError("V172_NATIVE_PROJECTION_REJECTED")
    if (validate(C.byref(surface))!=0 or
        surface.product_count!=64 or
        surface.noncommutative_generator_pairs!=2 or
        surface.struct_size!=C.sizeof(OctonionSurface) or
        surface.state.struct_size!=C.sizeof(OctonionState)):
        raise V172OctonionError("V172_NATIVE_SURFACE_INVALID")
    observations=[]
    for left,right,name in ORDERED:
        direct=OctonionProduct()
        if multiply(C.byref(surface.state),left,right,C.byref(direct))!=0:
            raise V172OctonionError("V172_NATIVE_MULTIPLY_REJECTED")
        entry=surface.products[left*8+right]
        fields=("left_basis","right_basis","left_phase","right_phase",
                "raw_additive_phase","phase","orientation","closure",
                "ordered_pair_index","ordered_tag")
        if any(getattr(direct,k)!=getattr(entry,k) for k in fields):
            raise V172OctonionError("V172_PRODUCT_SURFACE_DISAGREEMENT")
        if (direct.orientation != (1 if name in ("xy","zw") else 2)
            or direct.ordered_pair_index!=left*8+right):
            raise V172OctonionError("V172_ORDERED_ORIENTATION_DRIFT")
        observations.append({"channel":name,**{k:int(getattr(direct,k)) for k in fields}})
    if (observations[0]["ordered_tag"]==observations[1]["ordered_tag"] or
        observations[2]["ordered_tag"]==observations[3]["ordered_tag"]):
        raise V172OctonionError("V172_ORDER_COLLAPSE")
    seed_bytes=b"".join(w.to_bytes(8,"little") for w in frame_words)
    result={
        "schema":SCHEMA,
        "module194_source_sha256":inherited["source_sha256"],
        "module194_typed_packet_sha256":inherited["typed_packet_sha256"],
        "upstream_c_phase_observation_sha256":inherited["observation_sha256"],
        "observation_frame_sha256":sha256(seed_bytes).hexdigest(),
        "selected_group_cells":list(group_cells),
        "selected_lo_shu_weights":[g["lo_shu"] for g in groups],
        "native_octonion_version":int(surface.version),
        "native_octonion_product_count":int(surface.product_count),
        "native_phase_channels":[int(getattr(surface.state,k)) for k in
            ("x","y","z","w","xy","yx","zw","wz")],
        "native_ordered_products":observations,
        "native_vm81_octonion_projection_executed":True,
        "input_frame_is_canonical_admitted_vm81":False,
        "source_81_tensor_to_frame_equivalence_proved":False,
        "phase_word_fold_is_reversible":False,
        "module194_AB_BA_multiplication_proved":False,
        "input_specific_lean_certificate_constructed":False,
        "physics_force_equivalence_proved":False,
        "canonical_vm81_admission":False,
        "hash72_hash216_minted":False,
    }
    result["observation_sha256"]=sha256(json.dumps(
        result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return result
