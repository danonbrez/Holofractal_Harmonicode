"""Pass220 I092: original C ABI Hash216 indexed reference preflight of I090.

This is an actual ORIGINAL native reference_init/reference_verify and
256-bit-per-token index witness, not a host-language reimplementation.
It binds I091's original signed environmental admission contract to an
I090 three-lane candidate *without signing that candidate as a parent*
or claiming that it has genuine committed-state ancestry.

It also exercises native corruption and directed lane-order negatives.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any

from hhs_runtime.hhs_pass220_i091_original_signed_vm81_environment_test_admission_v1 import (
    PUBLIC_SIGNED_FUNCTION,
    bind_i091_original_signed_vm81_admission,
)
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    hydrate_hash216_geometry, hash72_vertex_geometry,
)

SCHEMA="HHS_PASS220_I092_ORIGINAL_NATIVE_HASH216_PARENT_PREFLIGHT_V1"
SOURCE_BOUNDARY="I090_SOURCE_BOUND_THREE_PLANE_CANDIDATE_ONLY"
ORIGINAL_NATIVE_REFERENCE_INIT="hhs_exact_pass219_vm81_pqc_hash216_reference_init"
ORIGINAL_NATIVE_REFERENCE_VERIFY="hhs_exact_pass219_vm81_pqc_hash216_reference_verify"
NATIVE_PROBE_MODES=("verify","tamper-index","reverse-lanes")
POSITIONS_216=216
NO_MUTATION_AUTHORITY={
    "canonical_Hash72_mint":False,
    "canonical_Hash216_signed_transition":False,
    "original_signed_environmental_mutation_invoked":False,
    "candidate_parent_proven_previously_committed":False,
    "I090_source_envelope_is_inherited_native_UQCEL_envelope":False,
    "original_native_reference_self_consistency_only":True,
    "original_signed_environmental_entrypoint_unchanged":True,
    "production_authority":False,
}


class I092NativePreflightError(ValueError):
    pass


def _canonical(value:Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      ensure_ascii=False,allow_nan=False).encode("utf-8")


def _native_probe(binary:str,mode:str,lanes:tuple[str,str,str])->dict[str,Any]:
    if mode not in NATIVE_PROBE_MODES:
        raise I092NativePreflightError("unregistered native Hash216 mode")
    if not isinstance(binary,str) or not binary:
        raise I092NativePreflightError("original native probe path required")
    executable=Path(binary)
    if not executable.is_file():
        raise I092NativePreflightError("actual compiled original reference probe absent")
    completed=subprocess.run(
        [str(executable),mode,*lanes],
        check=True,capture_output=True,text=True,
    )
    result:dict[str,Any]={}
    for token in completed.stdout.strip().split():
        if "=" not in token:
            raise I092NativePreflightError("native output invalid")
        key,value=token.split("=",1)
        if not key or key in result:
            raise I092NativePreflightError("native output duplicate/empty field")
        if key in ("native_parent_identity216","native_source_triplet216"):
            result[key]=value
        elif value.isdigit():
            result[key]=int(value)
        else:
            raise I092NativePreflightError("native output malformed numeric field")
    return result


def bind_i092_original_native_hash216_parent_preflight(
    *, opcode:int=0,nucleus_index:int=0,phase_channel:int=0,
    native_reference_probe:str|None=None,
)->dict[str,Any]:
    """Verify exact THREE candidate lanes via original native index resolver.

    A verified self-consistent parent-reference is *not* proven to be
    a committed historical parent. Do not send it to the signed
    environmental gate merely because the indexed proof succeeds.
    """
    parent=bind_i091_original_signed_vm81_admission(
        opcode=opcode,nucleus_index=nucleus_index,phase_channel=phase_channel,
        native_probe=None,
    )
    if (
        parent.get("native_signed_positive_test_executed") is not False
        or parent.get("real_native_I090_parent_candidate_hash216_signed_as_genesis") is not False
        or parent.get("production_canonical_admission_verified") is not False
    ):
        raise I092NativePreflightError("original I091 test/source authority drift")
    candidate=parent["original_i090_source_bound_parent_candidate_hash216"]
    if len(candidate)!=POSITIONS_216:
        raise I092NativePreflightError("I090 complete three-plane source required")
    lanes=tuple(candidate[i:i+72] for i in range(0,POSITIONS_216,72))
    if len(lanes)!=3 or any(len(word)!=72 for word in lanes):
        raise I092NativePreflightError("original Hash72 candidate plane geometry drift")
    for word in lanes:
        vertices=hash72_vertex_geometry(word)
        if len(vertices)!=72:
            raise I092NativePreflightError("source plane not in original Hash72 alphabet")
    if hydrate_hash216_geometry(candidate)["roundtrip_exact"] is not True:
        raise I092NativePreflightError("original I065 candidate hydration failure")

    validated:dict[str,Any]|None=None
    corrupt:dict[str,Any]|None=None
    ordered:dict[str,Any]|None=None
    if native_reference_probe is not None:
        validated=_native_probe(native_reference_probe,"verify",lanes)
        corrupt=_native_probe(native_reference_probe,"tamper-index",lanes)
        ordered=_native_probe(native_reference_probe,"reverse-lanes",lanes)
        for idx,proof in enumerate((validated,corrupt,ordered)):
            if (
                proof.get("mode")!=idx
                or proof.get("original_native_reference_verified")!=1
                or proof.get("original_native_index_count")!=216
                or proof.get("original_triplet_exact")!=1
                or proof.get("candidate_distinct_from_native_genesis")!=1
                or proof.get("native_source_triplet216")!=candidate
                or proof.get("canonical_signed_admission_invoked")!=0
                or proof.get("canonical_vm81_mutation")!=0
                or proof.get("previous_committed_parent_proven")!=0
            ):
                raise I092NativePreflightError("actual original native reference proof failed")
        if corrupt.get("tampered_index_rejected")!=1:
            raise I092NativePreflightError("original native index-tamper rejection missing")
        if ordered.get("reversed_lanes_distinct")!=1:
            raise I092NativePreflightError("native ordered parent lanes were aliased")
        native_identity=validated.get("native_parent_identity216")
        if not isinstance(native_identity,str) or len(native_identity)!=216:
            raise I092NativePreflightError("native derived transition identity missing")
        if native_identity!=ordered.get("native_parent_identity216"):
            raise I092NativePreflightError("original parent identity changed outside negative")
    else:
        native_identity=None

    provenance={
        "schema":SCHEMA,
        "inherited_i091_source_witness_sha256":parent["source_witness_sha256"],
        "inherited_i090_source_bound_candidate_hash216":candidate,
        "I090_prior_candidate_sha256":sha256(candidate.encode("ascii")).hexdigest(),
        "inherited_i090_signed_frame_sha256":parent["original_i090_frame_sha256"],
        "original_source_quotient_ancestry_sha256":parent[
            "original_i089_quotient_clifford_chain_sha256"],
        "original_native_verified_transition_identity216":native_identity,
        "signed_mutation_entrypoint_not_invoked":PUBLIC_SIGNED_FUNCTION,
    }
    return {
        "schema":SCHEMA,
        "original_candidate_hash216":candidate,
        "candidate_previous_hash72":lanes[0],
        "candidate_change_hash72":lanes[1],
        "candidate_receipt_hash72":lanes[2],
        "source_previous_change_receipt_exact":True,
        "original_i090_source_identity_sha256":parent["original_i090_source_binding_sha256"],
        "original_i091_source_witness_sha256":parent["source_witness_sha256"],
        "native_probe_supplied":native_reference_probe is not None,
        "original_native_216_index_reference_verified":validated is not None,
        "original_native_parent_identity216":native_identity,
        "original_native_hash216_index_tamper_rejected":corrupt is not None,
        "original_native_ordered_lane_reversal_distinguished":ordered is not None,
        "original_i065_candidate_hydration_roundtrip":True,
        "native_reference_operation_is_read_only":True,
        "native_reference_is_not_committed_state_ancestry":True,
        "native_signed_environmental_gate_not_invoked":True,
        "original_i090_source_sha256":parent["original_i090_frame_sha256"],
        "original_signed_gate_public_symbol":PUBLIC_SIGNED_FUNCTION,
        "provenance_sha256":sha256(_canonical(provenance)).hexdigest(),
        "authority":dict(NO_MUTATION_AUTHORITY),
        "candidate_only":True,
    }
