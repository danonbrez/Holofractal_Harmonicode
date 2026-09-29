"""HHS origin-provenance protection v1.

This layer protects origin-family identity rather than merely detecting later
byte changes.  The coupled marker is intentionally bound in shared-root
metadata rather than derived from a modality output:

    root seed:     179971.179971 = 179971179971 / 1000000
    invariant:     1.001         = 1001 / 1000

The marker's exact values, rational forms, field paths, roles, kernel context,
Hash216 surface, and shared ancestry define one HHS origin family.  Distinct
HHS constructions may have different derivation identities while remaining in
that same origin family.  A later claim of independent origin that reproduces
the full family marker is therefore classified as an origin-provenance
conflict, not as a new independent HHS origin.

SHA-256 values are receipts/indices over exact structured evidence.  Exact
field equality remains authoritative.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_lane5_multimodal_shared_root_fabric_v1 import (
    INVARIANT_GATE,
    ROOT_METADATA_SEED,
    build_multimodal_projection_set,
    hash216_genus3_polyhedral_surface,
    shared_multimodal_root_payload,
    shared_multimodal_root_sha256,
)
from hhs_runtime.hhs_system_signature_watermark_v1 import (
    canonical_bytes,
    derivation_identity,
)
from hhs_runtime.pass219.lane5_nine_loop_feedback_1_70 import GENESIS_IDENTITY


SCHEMA = "HHS_ORIGIN_PROVENANCE_PROTECTION_V1"
VERSION = "1.0.0"
ORIGIN_FAMILY = "HHS_COUPLED_179971_179971_X_1_001_ORIGIN_FAMILY_V1"

PUBLIC_PRIORITY_ANCHOR = {
    "repository": "danonbrez/Holofractal_Harmonicode",
    "commit_sha": "49b8f32bb9ce7e37e661333d76d5e4398093659f",
    "commit_created_at": "2026-09-29T15:10:55Z",
    "anchor_semantics": (
        "PUBLIC_GITHUB_COMMIT_AT_OR_BEFORE_WHICH_COUPLED_MARKER_IS_VERIFIED_PRESENT"
    ),
    "files": (
        {
            "path": "docs/HHS_GENESIS_SEVERANCE_PROTOCOL_V1.md",
            "git_blob_sha": "1dbde36a15d77c0dddbc7c754c401bae4b666bda",
            "contains_root_seed": True,
            "contains_invariant_gate": True,
        },
        {
            "path": "hhs_runtime/hhs_pass220_lane5_multimodal_shared_root_fabric_v1.py",
            "git_blob_sha": "57fc5987d5fd370fccede95998051dd0b586d9c0",
            "contains_root_seed": True,
            "contains_invariant_gate": True,
        },
    ),
}


class HHSOriginProvenanceError(ValueError):
    pass


def _receipt(payload: Mapping[str, Any]) -> dict[str, Any]:
    body = deepcopy(dict(payload))
    body["receipt_sha256"] = sha256(canonical_bytes(body)).hexdigest()
    return body


def coupled_origin_marker() -> dict[str, Any]:
    payload = shared_multimodal_root_payload()
    surface = hash216_genus3_polyhedral_surface()

    expected_seed = {
        "numerator": ROOT_METADATA_SEED.numerator,
        "denominator": ROOT_METADATA_SEED.denominator,
    }
    expected_gate = {
        "numerator": INVARIANT_GATE.numerator,
        "denominator": INVARIANT_GATE.denominator,
    }
    if payload.get("root_metadata_seed") != expected_seed:
        raise HHSOriginProvenanceError("root-seed position/value drift")
    if payload.get("invariant_gate") != expected_gate:
        raise HHSOriginProvenanceError("invariant-gate position/value drift")

    return {
        "origin_family": ORIGIN_FAMILY,
        "marker_type": "COUPLED_NON_OUTPUT_DERIVED_SHARED_ROOT_METADATA",
        "root_seed": {
            "display": "179971.179971",
            "numerator": 179971179971,
            "denominator": 1000000,
            "field_path": (
                "HHS_PASS_220_I042_SHARED_ROOT_PAYLOAD_V1.root_metadata_seed"
            ),
            "role": "ROOT_METADATA_SEED_EXACT_RATIONAL",
        },
        "invariant_gate": {
            "display": "1.001",
            "numerator": 1001,
            "denominator": 1000,
            "field_path": (
                "HHS_PASS_220_I042_SHARED_ROOT_PAYLOAD_V1.invariant_gate"
            ),
            "role": "EXACT_ADMISSION_INVARIANT_GATE",
        },
        "coupling": {
            "same_payload": True,
            "ordering": ("root_metadata_seed", "invariant_gate"),
            "relation": "COBOUND_IN_SHARED_ANCESTRY_ROOT",
            "not_modality_output_fields": True,
        },
        "kernel_context": GENESIS_IDENTITY,
        "root_metadata_assignment": "a=n^2",
        "closure_state": {"delta_e": 0, "psi": 0, "omega": True},
        "state_dimensions": 72,
        "transition_positions": 216,
        "hash216_surface_shape": tuple(surface["array_shape"]),
        "hash216_surface_root_sha256": surface["surface_root_sha256"],
        "shared_multimodal_root_sha256": shared_multimodal_root_sha256(),
    }


def origin_family_identity_sha256() -> str:
    return sha256(canonical_bytes(coupled_origin_marker())).hexdigest()


def output_variation_independence_witness() -> dict[str, Any]:
    """Show the coupled marker survives different outputs and derivations.

    This demonstrates that the marker is carried by shared-root metadata rather
    than being a literal copied from a particular modality output record.
    """
    first = build_multimodal_projection_set(tick=0)["LANGUAGE"]
    second = build_multimodal_projection_set(tick=1)["LANGUAGE"]

    source_varies = first["source"]["source_hash"] != second["source"]["source_hash"]
    projection_varies = first["projection_sha256"] != second["projection_sha256"]
    derivation_varies = derivation_identity(first) != derivation_identity(second)
    shared_root_stable = (
        first["shared_multimodal_root_sha256"]
        == second["shared_multimodal_root_sha256"]
        == shared_multimodal_root_sha256()
    )
    marker_not_exposed_as_output_fields = (
        "root_metadata_seed" not in first
        and "invariant_gate" not in first
        and "root_metadata_seed" not in second
        and "invariant_gate" not in second
    )

    closed = all(
        (
            source_varies,
            projection_varies,
            derivation_varies,
            shared_root_stable,
            marker_not_exposed_as_output_fields,
        )
    )
    if not closed:
        raise HHSOriginProvenanceError(
            "non-output-forced coupled-marker witness did not close"
        )

    return {
        "closed": True,
        "source_varies": source_varies,
        "projection_varies": projection_varies,
        "derivation_varies": derivation_varies,
        "shared_root_stable": shared_root_stable,
        "marker_not_exposed_as_output_fields": marker_not_exposed_as_output_fields,
        "origin_family_identity_sha256": origin_family_identity_sha256(),
    }


def build_origin_provenance_envelope(
    construction: Mapping[str, Any],
    *,
    construction_type: str,
) -> dict[str, Any]:
    if not construction_type or not isinstance(construction_type, str):
        raise HHSOriginProvenanceError("construction_type must be a non-empty string")

    identity = derivation_identity(construction)
    marker = coupled_origin_marker()
    witness = output_variation_independence_witness()

    return _receipt(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "construction_type": construction_type,
            "origin_family": marker,
            "origin_family_identity_sha256": sha256(
                canonical_bytes(marker)
            ).hexdigest(),
            "derivation_identity": identity,
            "derivation_identity_sha256": sha256(
                canonical_bytes(identity)
            ).hexdigest(),
            "public_priority_anchor": deepcopy(PUBLIC_PRIORITY_ANCHOR),
            "marker_position_witness": witness,
            "construction": deepcopy(dict(construction)),
        }
    )


def verify_origin_provenance_envelope(
    envelope: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        if envelope.get("schema") != SCHEMA or envelope.get("version") != VERSION:
            return {"ok": False, "reason": "SCHEMA_OR_VERSION_MISMATCH"}

        body = dict(envelope)
        claimed_receipt = body.pop("receipt_sha256", None)
        if not isinstance(claimed_receipt, str):
            return {"ok": False, "reason": "RECEIPT_MISSING"}
        if claimed_receipt != sha256(canonical_bytes(body)).hexdigest():
            return {"ok": False, "reason": "RECEIPT_MISMATCH"}

        construction = envelope.get("construction")
        if not isinstance(construction, Mapping):
            return {"ok": False, "reason": "CONSTRUCTION_MISSING"}

        marker = coupled_origin_marker()
        if envelope.get("origin_family") != marker:
            return {"ok": False, "reason": "ORIGIN_FAMILY_MISMATCH"}

        marker_index = sha256(canonical_bytes(marker)).hexdigest()
        if envelope.get("origin_family_identity_sha256") != marker_index:
            return {"ok": False, "reason": "ORIGIN_FAMILY_INDEX_MISMATCH"}

        identity = derivation_identity(construction)
        if envelope.get("derivation_identity") != identity:
            return {"ok": False, "reason": "DERIVATION_IDENTITY_MISMATCH"}
        if envelope.get("derivation_identity_sha256") != sha256(
            canonical_bytes(identity)
        ).hexdigest():
            return {"ok": False, "reason": "DERIVATION_INDEX_MISMATCH"}

        if envelope.get("public_priority_anchor") != PUBLIC_PRIORITY_ANCHOR:
            return {"ok": False, "reason": "PRIORITY_ANCHOR_MISMATCH"}

        witness = envelope.get("marker_position_witness")
        if not isinstance(witness, Mapping) or witness.get("closed") is not True:
            return {"ok": False, "reason": "MARKER_POSITION_WITNESS_OPEN"}

        return {
            "ok": True,
            "reason": "HHS_ORIGIN_PROVENANCE_VERIFIED",
            "origin_family": ORIGIN_FAMILY,
            "origin_family_identity_sha256": marker_index,
            "derivation_identity_sha256": envelope["derivation_identity_sha256"],
            "public_priority_anchor_commit": PUBLIC_PRIORITY_ANCHOR["commit_sha"],
            "public_priority_anchor_time": PUBLIC_PRIORITY_ANCHOR[
                "commit_created_at"
            ],
        }
    except (HHSOriginProvenanceError, KeyError, TypeError, ValueError):
        return {"ok": False, "reason": "MALFORMED_OR_NONCANONICAL"}


def classify_parallel_originality_claim(
    reference: Mapping[str, Any],
    candidate: Mapping[str, Any],
    *,
    candidate_claims_independent_origin: bool,
) -> dict[str, Any]:
    """Classify a later claim against the HHS origin-family witness.

    Distinct construction identity is allowed.  What conflicts with an
    independent-origin assertion is reproducing the exact HHS origin-family
    marker after the public priority anchor.
    """
    left = verify_origin_provenance_envelope(reference)
    right = verify_origin_provenance_envelope(candidate)
    if left.get("ok") is not True or right.get("ok") is not True:
        raise HHSOriginProvenanceError("both provenance envelopes must verify")

    same_family = reference["origin_family"] == candidate["origin_family"]
    same_derivation = (
        reference["derivation_identity"] == candidate["derivation_identity"]
    )
    conflict = bool(candidate_claims_independent_origin and same_family)

    return {
        "same_origin_family": same_family,
        "same_derivation": same_derivation,
        "distinct_construction_same_origin_family": (
            same_family and not same_derivation
        ),
        "candidate_claims_independent_origin": bool(
            candidate_claims_independent_origin
        ),
        "false_originality_provenance_conflict": conflict,
        "classification": (
            "INDEPENDENT_ORIGIN_CONTRADICTED_BY_HHS_ORIGIN_FAMILY"
            if conflict
            else "NO_INDEPENDENT_ORIGIN_CONFLICT"
        ),
        "priority_anchor_commit": PUBLIC_PRIORITY_ANCHOR["commit_sha"],
        "priority_anchor_time": PUBLIC_PRIORITY_ANCHOR["commit_created_at"],
    }
