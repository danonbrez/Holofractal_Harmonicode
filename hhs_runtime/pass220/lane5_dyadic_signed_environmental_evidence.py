"""Read-only cross-check of dyadic candidate with inherited signed probe evidence.

A report digest and matching 648-byte frame are diagnostic evidence, NOT a
signature on the dyadic virtual address / exponent / phase / Pass159 binding.
Do not promote this audit to canonical admission or Hash216 proof authority.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any, Mapping

from hhs_runtime.pass219.vm81_rna_bigint_environment_admission_probe import (
    SCHEMA as INHERITED_SCHEMA,
    NEGATIVE_MODES,
    _digest as inherited_diagnostic_digest,
    VM81_FRAME_BYTES,
)


def cross_check_inherited_signed_environmental_evidence(
    native_fields: Mapping[str, Any],
    candidate_frame: bytes,
    inherited_report: Mapping[str, Any],
) -> dict[str, Any]:
    """Confirm inherited receipt covers exact bytes, without claiming dyadic binding."""
    if not isinstance(native_fields, Mapping) or native_fields.get("schema") != (
        "HHS_LANE5_DYADIC_NATIVE_CANDIDATE_ABI_FIELDS_V1"
    ):
        raise ValueError("lowered dyadic candidate fields required")
    if native_fields.get("candidate_only") is not True or native_fields.get("vm81_admitted") is not False:
        raise ValueError("native candidate authority escalation")
    if native_fields.get("canonical_hash_mutation", object()) is not None:
        raise ValueError("canonical mutation claim forbidden")
    from hhs_runtime.pass220.lane5_dyadic_virtual_register import (
        encode_address,
        _integer,
    )
    address = native_fields.get("radix72_address")
    if type(address) is not tuple:
        raise ValueError("ordered radix-72 address required")
    encode_address(address)
    exponent = _integer(native_fields.get("signed_dyadic_exponent_int64"), "exponent")
    if not -(1 << 63) < exponent < (1 << 63):
        raise ValueError("native exponent outside supported int64 range")
    phase = native_fields.get("phase_coordinate72")
    if type(phase) is not int or not 0 <= phase < 72:
        raise ValueError("native phase invalid")
    binding = native_fields.get("pass159_binding_sha256")
    if type(binding) is not str or len(binding) != 64 or not all(
        c in "0123456789abcdef" for c in binding
    ):
        raise ValueError("Pass159 binding reference invalid")
    if type(candidate_frame) is not bytes or len(candidate_frame) != VM81_FRAME_BYTES:
        raise ValueError("exact 648-byte VM81 frame required")
    if not isinstance(inherited_report, Mapping) or inherited_report.get("schema") != INHERITED_SCHEMA:
        raise ValueError("inherited signed environmental report required")
    report_root = inherited_report.get("report_sha256")
    core = {key: value for key, value in inherited_report.items() if key != "report_sha256"}
    if report_root != inherited_diagnostic_digest(core):
        raise ValueError("inherited diagnostic report root mismatch")
    admission = inherited_report.get("canonical_admission")
    negative = inherited_report.get("negative_admission")
    authority = inherited_report.get("authority")
    if not isinstance(admission, Mapping) or not isinstance(negative, Mapping) or not isinstance(authority, Mapping):
        raise ValueError("inherited receipt evidence incomplete")
    required_positive = (
        "provider_available", "committed_exact", "committed_bytes_equal_source",
        "reencoded_bigint_exact", "reencoded_metadata_exact",
        "parent_hash216_verified", "child_hash216_verified",
        "inherited_rna_authority_invoked", "canonical_receipt_minted",
        "transition_verified", "child_identity_matches", "signature_verified",
        "environment_verified", "authority_handoff_exact",
    )
    rows = admission.get("rows")
    if (admission.get("native_probe_supplied") is not True or
        admission.get("positive_case_count") != 12 or
        admission.get("all_twelve_signed_environmental_commits_exact") is not True or
        not isinstance(rows, list) or len(rows) != 12):
        raise ValueError("twelve inherited signed admission cases required")
    for row in rows:
        if not isinstance(row, Mapping) or type(row.get("status")) is not int or row["status"] != 0:
            raise ValueError("inherited signed admission status invalid")
        if any(row.get(flag) is not True for flag in required_positive):
            raise ValueError("inherited signed receipt incomplete")
        if type(row.get("signature_length")) is not int or row["signature_length"] <= 0:
            raise ValueError("inherited signature length missing")
        digest = row.get("committed_raw_sha256")
        if not isinstance(digest, str) or len(digest) != 64 or not all(
            c in "0123456789abcdef" for c in digest
        ):
            raise ValueError("inherited committed-frame digest invalid")
    negative_rows = negative.get("rows")
    if (negative.get("case_count") != len(NEGATIVE_MODES) or
        not isinstance(negative_rows, list) or
        {row.get("mode") for row in negative_rows if isinstance(row, Mapping)} != set(NEGATIVE_MODES) or
        len(negative_rows) != len(NEGATIVE_MODES)):
        raise ValueError("inherited negative admission matrix incomplete")
    for row in negative_rows:
        if (not isinstance(row, Mapping) or row.get("failed_closed") is not True or
            row.get("committed_frame_zero") is not True or
            row.get("canonical_receipt_minted") is not False):
            raise ValueError("inherited negative admission bypass")
    for key in ("new_canonical_mutation_authority", "new_canonical_receipt_authority",
                "hash72_minting_authority_added", "hash216_persistence_authority_added",
                "floating_point_authority", "ordered_pq_qp_collapse"):
        if authority.get(key) is not False:
            raise ValueError("inherited authority drift")
    if authority.get("existing_environmental_mutator_reused") is not True:
        raise ValueError("inherited environmental mutator not used")
    frame_digest = sha256(candidate_frame).hexdigest()
    matches = [row for row in rows if row["committed_raw_sha256"] == frame_digest]
    if len(matches) != 1:
        raise ValueError("exact signed committed frame not uniquely evidenced")
    return {
        "schema": "HHS_LANE5_DYADIC_SIGNED_ENVIRONMENTAL_CROSSCHECK_V1",
        "native_frame_sha256": frame_digest,
        "inherited_report_sha256": report_root,
        "inherited_committed_frame_match": True,
        "inherited_signed_environmental_probe_verified": True,
        "source_binding_sha256_reference": binding,
        "dyadic_address": tuple(address),
        "dyadic_exponent": exponent,
        "dyadic_phase": phase,
        "dyadic_metadata_cryptographically_bound_to_signed_instruction": False,
        "dyadic_full_master_equation_admitted": False,
        "canonical_dyadic_hash72_receipt_verified": False,
        "canonical_dyadic_hash216_receipt_verified": False,
        "new_canonical_mutation_authority": False,
        "candidate_only": True,
    }
