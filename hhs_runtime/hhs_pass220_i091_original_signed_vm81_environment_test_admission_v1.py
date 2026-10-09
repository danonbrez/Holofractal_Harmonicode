"""Pass220 I091: original signed environmental admission of I090 physical VM81 frames.

The signing operation is NOT a new VM81/Hash72/Hash216 authority. It
invokes only the original Pass219 helper calling the public
hhs_exact_pass219_vm81_environment_admit_signed under an *explicit*
opt-in native test probe with a real ML-DSA-65 OpenSSL provider.

The original native helper creates its own deterministic TEST root
and verifies its own genesis Hash216 parent. The I089/I090
three-plane source-bound candidate ancestry is NOT the same
cryptographic parent or a production signing identity. Verify the
two provenance tracks separately, and hold cross-ancestry linkage
until a genuine original-native witness is available.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

from hhs_runtime.hhs_pass220_i090_original_vm81_rna_bigint_5184_ingress_v1 import (
    bind_i090_physical_vm81_ingress,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    VM81_FRAME_BYTES, build_execution_cases, raw_le_to_words,
    unpack_vm81_binding_words,
)
from hhs_runtime.pass219.vm81_rna_bigint_environment_admission_probe import (
    NEGATIVE_MODES, run_native_admission,
    vm81_rna_bigint_environment_admission_probe,
)
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    hydrate_hash216_geometry,
)

SCHEMA="HHS_PASS220_I091_ORIGINAL_SIGNED_VM81_ENVIRONMENT_TEST_ADMISSION_V1"
PUBLIC_SIGNED_FUNCTION="hhs_exact_pass219_vm81_environment_admit_signed"
REQUIRED_NATIVE_POSITIVE=(
    "provider_available","committed_exact","parent_hash216_verified",
    "child_hash216_verified","inherited_rna_authority_invoked",
    "canonical_receipt_minted","transition_verified",
    "child_identity_matches","signature_verified",
    "environment_verified","authority_handoff_exact",
)
TEST_ONLY_AUTHORITY={
    "only_original_pass219_signed_environment_entrypoint":True,
    "original_PQC_provider_required":True,
    "original_native_test_root_used_by_helper":True,
    "production_signing_key_or_environment_supplied":False,
    "I090_candidate_hash216_is_native_genesis_parent":False,
    "I091_new_mutation_export_created":False,
    "I091_new_canonical_hash72_mint_authority":False,
    "I091_new_hash216_persistence_authority":False,
    "unsigned_vm81_mutation_permitted":False,
    "native_full_HHS_Cl08_algebra_faithfulness_proven":False,
    "canonical_production_deployment_admitted":False,
    "floating_point_authority":False,
}


class I091SignedAdmissionError(ValueError):
    pass


def _canonical(value:Any)->bytes:
    return json.dumps(value,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False).encode("utf-8")


def _index(value:Any,upper:int,label:str)->int:
    if isinstance(value,bool) or not isinstance(value,int) or not 0<=value<upper:
        raise I091SignedAdmissionError(f"{label} requires exact bounded integer")
    return value


def _verify_positive(native:dict[str,int], raw:bytes, committed_raw:bytes,
                     metadata:dict[str,Any], bigint:int)->dict[str,Any]:
    if not isinstance(native,dict) or any(
        isinstance(native.get(key),bool) or native.get(key)!=1
        for key in REQUIRED_NATIVE_POSITIVE
    ):
        raise I091SignedAdmissionError("original ML-DSA-65 signed receipt not valid")
    if (
        native.get("status")!=0
        or native.get("signature_length",0)<=0
        or len(committed_raw)!=VM81_FRAME_BYTES
        or committed_raw!=raw
    ):
        raise I091SignedAdmissionError("signed VM81 committed frame unequal to source")
    restored=unpack_vm81_binding_words(raw_le_to_words(committed_raw))
    if restored["metadata"]!=metadata or restored["bigint"]!=bigint:
        raise I091SignedAdmissionError("original signed receipt lost typed metadata or BigInt")
    return {
        "native_status":native["status"],
        "ML_DSA_65_provider_verified":True,
        "original_signed_admission_verified":True,
        "source_raw_committed_exact":True,
        "committed_source_sha256":sha256(committed_raw).hexdigest(),
        "typed_opcode":metadata["opcode"],
        "original_genesis_parent_hash216_verified_by_helper":True,
        "original_signed_child_hash216_verified_by_helper":True,
        "original_RNA_owns_canonical_receipt":True,
        "original_signed_environment_verified":True,
        "original_signature_length_bytes":native["signature_length"],
        "original_environment_witness_sequence":native["environment_witness_sequence"],
        "native_identity216_exported_in_helper_output":False,
        "original_test_root_not_production_key":True,
    }


def _verify_negative(mode:str,native:dict[str,int],committed_raw:bytes)->dict[str,Any]:
    if mode not in NEGATIVE_MODES:
        raise I091SignedAdmissionError("unregistered original native negative mode")
    if (
        not isinstance(native,dict) or native.get("status",0)==0
        or native.get("canonical_receipt_minted")!=0
        or native.get("committed_zero")!=1
        or committed_raw!=bytes(VM81_FRAME_BYTES)
    ):
        raise I091SignedAdmissionError(
            "original environmental negative prerequisite not fail-closed"
        )
    return {
        "mode":mode,
        "native_failure_status":native["status"],
        "committed_frame_all_zero":True,
        "no_canonical_receipt_minted":True,
        "original_environment_failed_closed":True,
    }


def bind_i091_original_signed_vm81_admission(
    *, opcode:int=0, nucleus_index:int=0, phase_channel:int=0,
    native_probe:str|None=None,
    full_original_twelve_native_cases:bool=False,
)->dict[str,Any]:
    """Execute original signed *test fixture only*, never a new mutator."""
    op=_index(opcode,12,"opcode")
    nucleus=_index(nucleus_index,9,"nucleus")
    phase=_index(phase_channel,8,"phase")
    if native_probe is not None and (not isinstance(native_probe,str) or not native_probe):
        raise I091SignedAdmissionError("nonempty native signed test probe required")
    if not isinstance(full_original_twelve_native_cases,bool):
        raise I091SignedAdmissionError("explicit exact boolean full-suite flag required")
    if native_probe is None and full_original_twelve_native_cases:
        raise I091SignedAdmissionError("full signed test suite requires native provider")

    parent=bind_i090_physical_vm81_ingress(
        opcode=op,nucleus_index=nucleus,phase_channel=phase,
    )
    if (
        parent["selected_original_directional_metadata"]["opcode"]!=op
        or parent["candidate_only"] is not True
        or parent["authority"]["mutation_authorized"] is not False
        or parent["original_vm81_RNA_cpp_route_executed"] is not False
        or parent["canonical_signed_environmental_admission_proven"] is not False
    ):
        raise I091SignedAdmissionError("original I090 authority or source drift")
    if (
        len(parent["candidate_hash216"])!=216
        or parent["candidate_hash216"] != (
            parent["candidate_previous_hash72"]
            + parent["candidate_change_hash72"]
            + parent["candidate_receipt_hash72"]
        )
        or hydrate_hash216_geometry(parent["candidate_hash216"])["roundtrip_exact"] is not True
    ):
        raise I091SignedAdmissionError("original I090 source candidate ancestry drift")

    cases=build_execution_cases()
    if len(cases)!=12 or [item["opcode"] for item in cases]!=list(range(12)):
        raise I091SignedAdmissionError("inherited twelve-direction RNA layout changed")
    chosen=cases[op]
    raw=chosen["raw_bytes"]
    metadata=chosen["restored"]["metadata"]
    if (
        len(raw)!=VM81_FRAME_BYTES
        or chosen["raw_sha256"]!=parent["selected_original_raw_vm81_sha256"]
        or metadata!=parent["selected_original_directional_metadata"]
        or str(chosen["bigint"])!=parent["selected_original_bigint_decimal"]
    ):
        raise I091SignedAdmissionError("I090 signed source frame is not original native frame")
    original_native_positive=None
    original_native_negatives=[]
    full_native=None
    if native_probe is not None:
        signed=run_native_admission(raw,native_probe,"commit")
        original_native_positive=_verify_positive(
            signed["native"],raw,signed["committed_raw"],metadata,chosen["bigint"]
        )
        for mode in NEGATIVE_MODES:
            rejected=run_native_admission(raw,native_probe,mode)
            original_native_negatives.append(
                _verify_negative(mode,rejected["native"],rejected["committed_raw"])
            )
        if len(original_native_negatives)!=len(NEGATIVE_MODES):
            raise I091SignedAdmissionError("original negative suite incomplete")
        if full_original_twelve_native_cases:
            full_native=vm81_rna_bigint_environment_admission_probe(native_probe)
            if (
                full_native["canonical_admission"][
                    "all_twelve_signed_environmental_commits_exact"
                ] is not True
                or full_native["negative_admission"][
                    "all_invalid_prerequisites_fail_closed"
                ] is not True
                or full_native["promotion_result"][
                    "canonical_vm81_commit_observed_only_through_existing_public_boundary"
                ] is not True
            ):
                raise I091SignedAdmissionError("original 12-case signed native gate failed")
    result={
        "schema":SCHEMA,
        "original_i090_source_binding_sha256":parent["source_binding_sha256"],
        "original_i089_quotient_clifford_chain_sha256":parent[
            "original_i089_source_identity_sha256"
        ],
        "original_i090_source_bound_parent_candidate_hash216":parent["candidate_hash216"],
        "original_i090_frame_sha256":parent["selected_original_raw_vm81_sha256"],
        "original_i090_metadata":metadata,
        "original_i090_5184_physical_bit_roundtrip":True,
        "original_i090_5184_scientific_character_source_sha256":parent[
            "normalization_source_sha256"
        ],
        "original_i090_scientific_source_not_identical_to_raw_frame":True,
        "original_public_signed_environmental_entrypoint":PUBLIC_SIGNED_FUNCTION,
        "native_test_probe_supplied":native_probe is not None,
        "native_signed_positive_test_executed":original_native_positive is not None,
        "native_signed_positive_test":original_native_positive,
        "original_signed_environment_negative_modes_tested":original_native_negatives,
        "all_four_original_signed_fail_closed_tests_passed":len(
            original_native_negatives
        )==len(NEGATIVE_MODES) if native_probe is not None else False,
        "native_original_twelve_case_suite_requested":full_original_twelve_native_cases,
        "native_original_twelve_case_suite_completed":full_native is not None,
        "native_original_twelve_case_suite_report_sha256":(
            full_native["report_sha256"] if full_native is not None else None
        ),
        "original_native_canonical_receipt_verified_in_test":(
            original_native_positive is not None
        ),
        "real_native_I090_parent_candidate_hash216_signed_as_genesis":False,
        "real_native_signed_child_hash216_equals_I090_candidate_hash216_proven":False,
        "new_signed_mutation_api_created":False,
        "production_canonical_admission_verified":False,
        "authority":dict(TEST_ONLY_AUTHORITY),
        "no_floating_point_authority":True,
    }
    result["source_witness_sha256"]=sha256(_canonical(result)).hexdigest()
    return result
