"""Pass 220 I090 — exact ORIGINAL 81x64 RNA frame and 5184-char offset ingress.

Connects I089 RML4/RML11/I070/I065 Hash216 *candidate* ancestry to
the preexisting Pass219 12-route BigInt/RNA VM5184 frame API, and to the
preexisting fixed-width HHS rational-scientific 5184-character offset
serialization. Both are reversible in their OWN types; a 648-byte
binary VM81 frame is NOT the same object as a 5184-character normalized
source, nor does their shared 5184 positional geometry prove equal
underlying payloads.

Optional native_probe delegates to original Pass219 C++ RNA
execution-binding conformance, never to hidden or unsigned canonical
VM81 mutation. Signed environmental admission remains a separate gate.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Sequence

from hhs_runtime.hhs_pass220_i089_rml4_rml11_vm81_hash216_candidate_binding_v1 import (
    bind_i089_original_phase_vm81_candidate,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    VM81_WORD_BITS, VM81_WORD_COUNT, VM81_FRAME_BYTES,
    build_execution_cases, raw_le_to_words, words_to_raw_le,
    unpack_vm81_binding_words, vm81_rna_bigint_execution_binding_probe,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    SERIALIZED_CHARACTERS, CELL_TOKEN_CHARACTERS, VM81_CELLS,
    serialize_offsets_5184, deserialize_offsets_5184,
    normalize_offsets, repeated_lo_shu_reference,
)
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    validate_serialized5184, hydrate_hash216_geometry,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import (
    hash72 as inherited_candidate_hash72,
)

SCHEMA="HHS_PASS220_I090_ORIGINAL_VM81_RNA_BIGINT_5184_INGRESS_V1"
ORIGINAL_FRAME_LAYOUT={
    "bigint_limb_words":(0,1,2,3,4,5,6),
    "header_word":7,
    "glyph_words":(8,79),
    "lane_metadata_word":80,
}
AUTHORITY={
    "original_RNA_candidate_route_only":True,
    "original_signed_environmental_gate_is_sole_canonical_mutation":True,
    "candidate_hash72_not_ledger_mint":True,
    "candidate_hash216_not_canonical_persistence":True,
    "mutation_authorized":False,
    "signed_environmental_admission_invoked":False,
    "native_vm81_raw_payload_mutated":False,
    "floating_point_authority":False,
}


class I090IngressError(ValueError):
    pass


def _canonical(value:Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      ensure_ascii=False,allow_nan=False).encode("utf-8")


def _index(value:Any,maximum:int,label:str)->int:
    if isinstance(value,bool) or not isinstance(value,int) or not 0<=value<maximum:
        raise I090IngressError(f"{label} must be exact integer in [0,{maximum})")
    return value


def _offsets(source:Sequence[int]|None)->tuple[int,...]:
    if source is None:
        result=normalize_offsets(repeated_lo_shu_reference())
    else:
        if isinstance(source,(str,bytes,bytearray)) or not isinstance(source,(tuple,list)):
            raise I090IngressError("typed 81 source offset positions required")
        result=tuple(source)
    if len(result)!=VM81_CELLS:
        raise I090IngressError("exactly 81 positioned normalization offsets required")
    for index,offset in enumerate(result):
        if isinstance(offset,bool) or not isinstance(offset,int) or not 0<=offset<=8:
            raise I090IngressError(f"offset position {index}: exact 0..8 required")
    return result


def bind_i090_physical_vm81_ingress(
    *, opcode:int=0, nucleus_index:int=0, phase_channel:int=0,
    normalization_offsets:Sequence[int]|None=None,
    native_probe:str|None=None,
)->dict[str,Any]:
    """Bind genuine typed and raw ingress without new signing/commit authority."""
    op=_index(opcode,12,"directional opcode")
    nucleus=_index(nucleus_index,9,"VM81 nucleus")
    phase=_index(phase_channel,8,"phase channel")
    if native_probe is not None and (not isinstance(native_probe,str) or not native_probe):
        raise I090IngressError("native probe path must be a nonempty string")

    i089=bind_i089_original_phase_vm81_candidate(nucleus,phase_channel=phase)
    if (
        i089.get("candidate_only") is not True
        or i089.get("signed_vm81_mutation") is not False
        or i089.get("original_i065_three_plane_hydration_roundtrip") is not True
    ):
        raise I090IngressError("parent I089 original VM81/Hash216 evidence diverged")

    cases=build_execution_cases()
    if len(cases)!=12 or [c["opcode"] for c in cases]!=list(range(12)):
        raise I090IngressError("original six-lane pq/qp execution ABI changed")
    bigint=cases[0]["bigint"]
    if isinstance(bigint,bool) or not isinstance(bigint,int) or not 0<=bigint<(1<<448):
        raise I090IngressError("original native BigInt limb capacity exceeded")
    digest_rows=[]
    for case in cases:
        raw=case["raw_bytes"]
        words=raw_le_to_words(raw)
        restored=unpack_vm81_binding_words(words)
        meta={
            "opcode":case["opcode"],"lane":case["lane"],
            "direction":case["direction"],"source":case["source"],
            "target":case["target"]
        }
        if (
            len(raw)!=VM81_FRAME_BYTES
            or len(words)!=VM81_WORD_COUNT
            or words_to_raw_le(words)!=raw
            or restored["bigint"]!=bigint
            or restored["metadata"]!=meta
            or len(restored["glyph_stream"])!=72
            or sha256(raw).hexdigest()!=case["raw_sha256"]
        ):
            raise I090IngressError("original RNA candidate raw/typed roundtrip mismatch")
        digest_rows.append({
            "opcode":case["opcode"],"lane":case["lane"],
            "direction":case["direction"],"source":case["source"],
            "target":case["target"],"raw_frame_sha256":case["raw_sha256"],
        })
    if len(set(row["raw_frame_sha256"] for row in digest_rows))!=12:
        raise I090IngressError("12 directional raw frame identities must stay distinct")

    offsets=_offsets(normalization_offsets)
    normalized=serialize_offsets_5184(offsets)
    if (
        len(normalized)!=SERIALIZED_CHARACTERS
        or deserialize_offsets_5184(normalized)!=offsets
        or validate_serialized5184(normalized)!=offsets
        or CELL_TOKEN_CHARACTERS!=VM81_WORD_BITS
    ):
        raise I090IngressError("original 5184-character scientific normalization drift")
    selected=cases[op]
    reconstructed=raw_le_to_words(selected["raw_bytes"])
    typed=unpack_vm81_binding_words(reconstructed)
    if typed["metadata"]["opcode"]!=op:
        raise I090IngressError("typed direction/ABI original metadata mismatch")
    binary5184="".join(f"{value:08b}" for value in selected["raw_bytes"])
    if len(binary5184)!=VM81_WORD_COUNT*VM81_WORD_BITS:
        raise I090IngressError("original raw VM81 physical bit count mismatch")
    # Byte-order is explicit: 8 bytes per LE word. This "binary5184"
    # is a true raw frame BIT VIEW; I065 palindrome-canonical binary
    # is a different constrained state and is NOT assumed here.
    reconstructed_raw=bytes(
        int(binary5184[k:k+8],2) for k in range(0,len(binary5184),8)
    )
    if reconstructed_raw!=selected["raw_bytes"]:
        raise I090IngressError("exact raw bit/byte roundtrip mismatch")

    actual_native=None
    if native_probe is not None:
        actual_native=vm81_rna_bigint_execution_binding_probe(native_probe)
        binding=actual_native["binding_result"]
        native=actual_native["native_execution"]
        if (
            native["case_count"]!=12
            or native["all_native_candidate_routes_green"] is not True
            or binding["existing_cpp_rna_route_reused"] is not True
            or binding["native_rna_candidate_execution_exact"] is not True
            or actual_native["authority"]["canonical_vm81_mutation"] is not False
        ):
            raise I090IngressError("original C++ RNA candidate ABI native conformance failed")

    framed={
        "schema":SCHEMA,
        "original_i089_source_identity_sha256":i089["candidate_source_identity_sha256"],
        "original_i089_parent_hash216":i089["source_bound_candidate_hash216"],
        "original_i089_rml4_phase_state_sha256":i089["original_rml4_state_sha256"],
        "original_i089_exact_word_quotient_sha256":i089["i088_exact_word_quotient_sha256"],
        "original_parent_previous_hash72":i089["source_bound_receipt_hash72"],
        "physical_81x64_frame_sha256":selected["raw_sha256"],
        "original_directional_lane":typed["metadata"],
        "fixed_5184_character_normalized_sha256":sha256(normalized.encode("ascii")).hexdigest(),
        "normalization_offsets_81_sha256":sha256(_canonical(offsets)).hexdigest(),
        "original_vm81_frame_not_native_signed_commit":True,
    }
    change=inherited_candidate_hash72(framed)
    previous=i089["source_bound_receipt_hash72"]
    receipt=inherited_candidate_hash72({
        "schema":SCHEMA,"previous":previous,"change":change,
        "parent_hash216":i089["source_bound_candidate_hash216"],
        "actual_frame_and_exact_source":framed,
        "authority":AUTHORITY,
    })
    candidate=previous+change+receipt
    if (
        any(len(v)!=72 for v in (previous,change,receipt))
        or len(candidate)!=216
        or hydrate_hash216_geometry(candidate)["roundtrip_exact"] is not True
    ):
        raise I090IngressError("original I065 Hash216 replay admission failed")

    return {
        "schema":SCHEMA,
        "original_i089_source_identity_sha256":i089["candidate_source_identity_sha256"],
        "i089_source_bound_parent_candidate_hash216":i089["source_bound_candidate_hash216"],
        "physical_frame_layout":dict(ORIGINAL_FRAME_LAYOUT),
        "vm81_words":VM81_WORD_COUNT,
        "word_bits":VM81_WORD_BITS,
        "raw_frame_bytes":VM81_FRAME_BYTES,
        "raw_frame_bit_count":len(binary5184),
        "original_frame_bigint_bits_capacity":448,
        "original_glyph_words":72,
        "all_original_twelve_directional_frames":digest_rows,
        "all_twelve_raw_frames_exact_and_distinct":True,
        "selected_original_directional_metadata":typed["metadata"],
        "selected_original_raw_vm81_sha256":selected["raw_sha256"],
        "selected_original_bigint_decimal":str(bigint),
        "selected_original_bigint_integrity_verified":True,
        "fixed_rational_scientific_character_count":len(normalized),
        "fixed_rational_scientific_token_width":CELL_TOKEN_CHARACTERS,
        "normalized_81_offsets_count":len(offsets),
        "normalization_offsets":list(offsets),
        "normalization_source_sha256":framed["fixed_5184_character_normalized_sha256"],
        "raw_bit_view_exact_roundtrip":True,
        "raw_vm81_bit_view_is_i065_palindromic_binary_claim":False,
        "raw_frame_and_scientific_serialization_are_distinct_types":True,
        "original_vm81_RNA_execution_probe_supplied":native_probe is not None,
        "original_vm81_RNA_cpp_route_executed":actual_native is not None,
        "original_native_probe_report_sha256":(
            actual_native["report_sha256"] if actual_native is not None else None
        ),
        "original_native_RNA_conformance_verified":(
            actual_native["native_execution"]["all_native_candidate_routes_green"]
            if actual_native is not None else False
        ),
        "candidate_previous_hash72":previous,
        "candidate_change_hash72":change,
        "candidate_receipt_hash72":receipt,
        "candidate_hash216":candidate,
        "original_i065_hash216_three_plane_roundtrip":True,
        "source_binding_sha256":sha256(_canonical(framed)).hexdigest(),
        "authority":dict(AUTHORITY),
        "canonical_signed_environmental_admission_proven":False,
        "candidate_only":True,
    }
