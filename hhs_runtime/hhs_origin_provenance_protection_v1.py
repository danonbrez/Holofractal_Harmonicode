"""HHS origin-provenance protection v1.

The authoritative marker is not a pair of unexplained literals. It is an
ordered derivation genealogy whose endpoint includes:

    179971.179971 = 179971179971 / 1000000
    1.001         = 1001 / 1000

The genealogy preserves the HHS closed-interior/modular-shell construction,
the 101-harmonic prime-tensor lineage, the 179/971 reversal tensor, the
million-shell lift, exact structural positions, and shared-root ancestry.

This layer makes a bounded parallel-provenance claim: if two constructions
carry the exact same derived genealogy in the same comparison window, they
cannot simultaneously be classified as having different relevant initial
conditions. It does not assert unbounded impossibility of independently
developing the underlying information.

SHA-256 values are receipts/indices over exact structured evidence. Exact
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
VERSION = "1.2.0"
ORIGIN_FAMILY = "HHS_DERIVED_101_179971_X_1_001_ORIGIN_FAMILY_V2"
DERIVATION_GENEALOGY_SCHEMA = "HHS_101_MODULAR_SHELL_DERIVATION_GENEALOGY_V1"

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

HISTORICAL_DERIVATION_WITNESSES = (
    {
        "time": "2025-06-12",
        "witness": "FIRST_81_PRIMES_LO_SHU_RECURSIVE_TENSOR",
        "facts": (
            "101=10^2+1 at zero-based 9x9 coordinate [2,7], flat index 25",
            "179 prime-tensor cell identity: 13^2+16=179 at zero-based 9x9 coordinate [4,4], flat index 40",
        ),
    },
    {
        "time": "2026-07-20",
        "witness": "101_HARMONIC_KERNEL_CORRECTION",
        "facts": (
            "101 harmonic kernel directly generates 179; reversal/concatenation then generate 971 and 179971",
            "101=10^2+1",
            "10^6+1=101*9901",
        ),
    },
    {
        "time": "2026-09-29",
        "witness": "MODULAR_SHELL_GENEALOGY_CLARIFICATION",
        "facts": (
            "100=b^4(b^2+c^2=d^2)^2 with b^2=2,c^2=3,d^2=5",
            "101 is the modular shell/base over the closed 100 interior",
            "101/100=1.01",
            "1001=7*11*13 and 1001/1000=1.001",
            "1000001 is the million-position extension of the same shell logic",
        ),
    },
)


class HHSOriginProvenanceError(ValueError):
    pass


def _receipt(payload: Mapping[str, Any]) -> dict[str, Any]:
    body = deepcopy(dict(payload))
    body["receipt_sha256"] = sha256(canonical_bytes(body)).hexdigest()
    return body


def _reverse3(value: int) -> int:
    if value < 0 or value > 999:
        raise HHSOriginProvenanceError("three-digit reversal requires 0..999")
    return (
        (value % 10) * 100
        + ((value // 10) % 10) * 10
        + ((value // 100) % 10)
    )


def canonical_derivation_genealogy() -> dict[str, Any]:
    """Return and self-check the exact ordered origin genealogy.

    The 101 -> 179 relation is retained in its historical HHS form:
    101-harmonic kernel generation inside the Lo Shu prime tensor. This
    function deliberately does not invent a scalar shortcut that was not part
    of the recorded construction.
    """
    b2, c2, d2 = 2, 3, 5
    closed_100 = (b2**2) * ((b2 + c2) ** 2)
    shell_101 = closed_100 + 1
    shell_1001 = 1000 + 1
    factor_1001 = 7 * 11 * 13
    reversal_179 = 179
    reversal_971 = _reverse3(reversal_179)
    concat_179971 = reversal_179 * 1000 + reversal_971
    shell_1000001 = 1000000 + 1
    mirrored_integer = concat_179971 * shell_1000001

    required = (
        (b2 + c2 == d2, "b2+c2=d2"),
        (closed_100 == 100, "closed interior 100"),
        (shell_101 == 101, "modular shell 101"),
        (10**2 + 1 == 101, "101=10^2+1"),
        (shell_1001 == 1001, "1000+1=1001 modular shell"),
        (factor_1001 == shell_1001, "7*11*13=1001 factorization identity"),
        (13**2 + 16 == 179, "179=13^2+16"),
        (reversal_971 == 971, "reverse3(179)=971"),
        (concat_179971 == 179971, "179||971=179971"),
        (shell_1000001 == 1000001, "million shell"),
        (101 * 9901 == 1000001, "1000001=101*9901"),
        (mirrored_integer == 179971179971, "mirror lift integer"),
    )
    failures = [label for ok, label in required if not ok]
    if failures:
        raise HHSOriginProvenanceError(
            "canonical derivation genealogy failed: " + ",".join(failures)
        )

    initial_conditions = {
        "typed_constants": {
            "b2": b2,
            "c2": c2,
            "d2": d2,
            "pythagorean_projection": "b^2+c^2=d^2",
        },
        "closed_interior_constructor": "b^4(b^2+c^2=d^2)^2",
        "closed_interior": 100,
        "shell_operator": "S(B)=B+1",
        "shell_family_interiors": (100, 1000, 1000000),
        "base_101_modular_shell": 101,
        "prime_tensor_constructor": "FIRST_81_PRIMES_LO_SHU_RECURSIVE_3X3X3X3",
        "prime_tensor_mapping": "Tensor[i][j][k][l]=Prime(27i+9j+3k+l)",
    }

    stages = (
        {
            "ordinal": 0,
            "name": "CLOSED_INTERIOR_100",
            "input": {"b2": 2, "c2": 3, "d2": 5},
            "rule": "b^4(b^2+c^2=d^2)^2",
            "output": 100,
        },
        {
            "ordinal": 1,
            "name": "BASE_101_MODULAR_SHELL",
            "input": 100,
            "rule": "S(B)=B+1",
            "output": 101,
            "exact_normalized_projection": {
                "numerator": 101,
                "denominator": 100,
                "display": "1.01",
            },
        },
        {
            "ordinal": 2,
            "name": "LO_SHU_PRIME_TENSOR_101_CELL",
            "input": 101,
            "rule": "10^2+1",
            "zero_based_coordinate": (2, 7),
            "flat_index": 25,
            "output": 101,
        },
        {
            "ordinal": 3,
            "name": "1001_PRIME_FIBONACCI_SHELL_EXTENSION",
            "input": 1000,
            "rule": "S(B)=B+1",
            "factorization_identity": "7*11*13=1001",
            "prime_factors": (7, 11, 13),
            "fibonacci_prime": 13,
            "output": 1001,
            "exact_normalized_projection": {
                "numerator": 1001,
                "denominator": 1000,
                "display": "1.001",
            },
            "role": "LO_SHU_TENSOR_EXPANSION_SHELL",
        },
        {
            "ordinal": 4,
            "name": "101_HARMONIC_KERNEL_TO_179",
            "input": 101,
            "rule": "HHS_101_HARMONIC_KERNEL_GENERATION",
            "direct_relation_semantics": "RECORDED_DIRECT_DERIVATION_FROM_101_HARMONIC_SEED",
            "prime_tensor_output_identity": "13^2+16=179",
            "scalar_shortcut": "NOT_SUBSTITUTED_WHERE_HISTORICAL_EQUATION_IS_NOT_RECOVERED",
            "zero_based_coordinate": (4, 4),
            "flat_index": 40,
            "output": 179,
            "relation_class": "RECORDED_HHS_DERIVATION_NOT_AD_HOC_SCALAR_SHORTCUT",
        },
        {
            "ordinal": 5,
            "name": "REVERSAL_TENSOR_179_971",
            "input": 179,
            "rule": "DECIMAL_DIGIT_REVERSAL_WIDTH_3",
            "output": 971,
        },
        {
            "ordinal": 6,
            "name": "CONCATENATED_REVERSAL_SEED",
            "input": (179, 971),
            "rule": "179*1000+971",
            "output": 179971,
        },
        {
            "ordinal": 7,
            "name": "MILLION_POSITION_MODULAR_SHELL",
            "input": 1000000,
            "rule": "S(B)=B+1",
            "output": 1000001,
            "factorization_identity": "101*9901=1000001",
            "factorization": (101, 9901),
            "exact_normalized_projection": {
                "numerator": 1000001,
                "denominator": 1000000,
                "display": "1.000001",
            },
        },
        {
            "ordinal": 8,
            "name": "MIRROR_LIFT_ROOT_SEED",
            "input": (179971, 1000001),
            "rule": "179971*1000001",
            "integer_output": 179971179971,
            "exact_rational_output": {
                "numerator": 179971179971,
                "denominator": 1000000,
                "display": "179971.179971",
            },
            "serialization": "[179][971].[179][971]",
        },
    )

    return {
        "schema": DERIVATION_GENEALOGY_SCHEMA,
        "relevant_initial_conditions": initial_conditions,
        "ordered_stages": stages,
        "endpoint": {
            "root_seed": {
                "numerator": 179971179971,
                "denominator": 1000000,
                "display": "179971.179971",
            },
            "invariant_gate": {
                "numerator": 1001,
                "denominator": 1000,
                "display": "1.001",
            },
        },
        "historical_derivation_witnesses": HISTORICAL_DERIVATION_WITNESSES,
    }


def derivation_genealogy_identity_sha256() -> str:
    return sha256(canonical_bytes(canonical_derivation_genealogy())).hexdigest()


def relevant_initial_conditions() -> dict[str, Any]:
    return deepcopy(canonical_derivation_genealogy()["relevant_initial_conditions"])


def relevant_initial_conditions_identity_sha256() -> str:
    return sha256(canonical_bytes(relevant_initial_conditions())).hexdigest()


def coupled_origin_marker() -> dict[str, Any]:
    payload = shared_multimodal_root_payload()
    surface = hash216_genus3_polyhedral_surface()
    genealogy = canonical_derivation_genealogy()

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
    if genealogy["endpoint"]["root_seed"] != {
        **expected_seed,
        "display": "179971.179971",
    }:
        raise HHSOriginProvenanceError("genealogy/root-seed mismatch")
    if genealogy["endpoint"]["invariant_gate"] != {
        **expected_gate,
        "display": "1.001",
    }:
        raise HHSOriginProvenanceError("genealogy/invariant-gate mismatch")

    return {
        "origin_family": ORIGIN_FAMILY,
        "marker_type": "ORDERED_DERIVED_GENEALOGY_BOUND_SHARED_ROOT_METADATA",
        "derivation_genealogy": genealogy,
        "derivation_genealogy_identity_sha256": derivation_genealogy_identity_sha256(),
        "relevant_initial_conditions_identity_sha256": relevant_initial_conditions_identity_sha256(),
        "root_seed": {
            "display": "179971.179971",
            "numerator": 179971179971,
            "denominator": 1000000,
            "field_path": "HHS_PASS_220_I042_SHARED_ROOT_PAYLOAD_V1.root_metadata_seed",
            "role": "ROOT_METADATA_SEED_EXACT_RATIONAL",
        },
        "invariant_gate": {
            "display": "1.001",
            "numerator": 1001,
            "denominator": 1000,
            "field_path": "HHS_PASS_220_I042_SHARED_ROOT_PAYLOAD_V1.invariant_gate",
            "role": "EXACT_ADMISSION_INVARIANT_GATE",
        },
        "coupling": {
            "same_payload": True,
            "ordering": ("root_metadata_seed", "invariant_gate"),
            "relation": "COBOUND_IN_SHARED_ANCESTRY_ROOT",
            "not_modality_output_fields": True,
            "genealogy_required": True,
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
    """Show genealogy stays at the root while downstream outputs vary."""
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
    genealogy = canonical_derivation_genealogy()
    genealogy_closed = (
        genealogy["endpoint"]["root_seed"]["numerator"] == ROOT_METADATA_SEED.numerator
        and genealogy["endpoint"]["invariant_gate"]["numerator"] == INVARIANT_GATE.numerator
    )

    closed = all(
        (
            source_varies,
            projection_varies,
            derivation_varies,
            shared_root_stable,
            marker_not_exposed_as_output_fields,
            genealogy_closed,
        )
    )
    if not closed:
        raise HHSOriginProvenanceError("derived-genealogy origin witness did not close")

    return {
        "closed": True,
        "source_varies": source_varies,
        "projection_varies": projection_varies,
        "derivation_varies": derivation_varies,
        "shared_root_stable": shared_root_stable,
        "marker_not_exposed_as_output_fields": marker_not_exposed_as_output_fields,
        "genealogy_closed": genealogy_closed,
        "derivation_genealogy_identity_sha256": derivation_genealogy_identity_sha256(),
        "origin_family_identity_sha256": origin_family_identity_sha256(),
    }


def build_origin_provenance_envelope(
    construction: Mapping[str, Any],
    *,
    construction_type: str,
    parallel_window_id: str = "UNSPECIFIED_BOUNDED_WINDOW",
) -> dict[str, Any]:
    if not construction_type or not isinstance(construction_type, str):
        raise HHSOriginProvenanceError("construction_type must be a non-empty string")
    if not parallel_window_id or not isinstance(parallel_window_id, str):
        raise HHSOriginProvenanceError("parallel_window_id must be a non-empty string")

    identity = derivation_identity(construction)
    marker = coupled_origin_marker()
    witness = output_variation_independence_witness()

    return _receipt(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "construction_type": construction_type,
            "parallel_window_id": parallel_window_id,
            "origin_family": marker,
            "origin_family_identity_sha256": sha256(canonical_bytes(marker)).hexdigest(),
            "derivation_genealogy_identity_sha256": derivation_genealogy_identity_sha256(),
            "relevant_initial_conditions": relevant_initial_conditions(),
            "relevant_initial_conditions_identity_sha256": relevant_initial_conditions_identity_sha256(),
            "claim_scope": "PARALLEL_HUMAN_DERIVATION_WITHIN_DECLARED_WINDOW",
            "derivation_identity": identity,
            "derivation_identity_sha256": sha256(canonical_bytes(identity)).hexdigest(),
            "public_priority_anchor": deepcopy(PUBLIC_PRIORITY_ANCHOR),
            "marker_position_witness": witness,
            "construction": deepcopy(dict(construction)),
        }
    )


def verify_origin_provenance_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
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
        if envelope.get("derivation_genealogy_identity_sha256") != derivation_genealogy_identity_sha256():
            return {"ok": False, "reason": "GENEALOGY_INDEX_MISMATCH"}
        if envelope.get("relevant_initial_conditions") != relevant_initial_conditions():
            return {"ok": False, "reason": "INITIAL_CONDITIONS_MISMATCH"}
        if envelope.get("relevant_initial_conditions_identity_sha256") != relevant_initial_conditions_identity_sha256():
            return {"ok": False, "reason": "INITIAL_CONDITIONS_INDEX_MISMATCH"}
        if envelope.get("claim_scope") != "PARALLEL_HUMAN_DERIVATION_WITHIN_DECLARED_WINDOW":
            return {"ok": False, "reason": "CLAIM_SCOPE_MISMATCH"}

        identity = derivation_identity(construction)
        if envelope.get("derivation_identity") != identity:
            return {"ok": False, "reason": "DERIVATION_IDENTITY_MISMATCH"}
        if envelope.get("derivation_identity_sha256") != sha256(canonical_bytes(identity)).hexdigest():
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
            "derivation_genealogy_identity_sha256": derivation_genealogy_identity_sha256(),
            "relevant_initial_conditions_identity_sha256": relevant_initial_conditions_identity_sha256(),
            "derivation_identity_sha256": envelope["derivation_identity_sha256"],
            "parallel_window_id": envelope["parallel_window_id"],
            "public_priority_anchor_commit": PUBLIC_PRIORITY_ANCHOR["commit_sha"],
            "public_priority_anchor_time": PUBLIC_PRIORITY_ANCHOR["commit_created_at"],
        }
    except (HHSOriginProvenanceError, KeyError, TypeError, ValueError):
        return {"ok": False, "reason": "MALFORMED_OR_NONCANONICAL"}


def classify_parallel_originality_claim(
    reference: Mapping[str, Any],
    candidate: Mapping[str, Any],
    *,
    candidate_claims_independent_origin: bool,
) -> dict[str, Any]:
    """Classify a bounded parallel-origin claim against exact genealogy."""
    left = verify_origin_provenance_envelope(reference)
    right = verify_origin_provenance_envelope(candidate)
    if left.get("ok") is not True or right.get("ok") is not True:
        raise HHSOriginProvenanceError("both provenance envelopes must verify")

    same_family = reference["origin_family"] == candidate["origin_family"]
    same_genealogy = (
        reference["origin_family"]["derivation_genealogy"]
        == candidate["origin_family"]["derivation_genealogy"]
    )
    same_initial_conditions = (
        reference["relevant_initial_conditions"]
        == candidate["relevant_initial_conditions"]
    )
    same_parallel_window = reference["parallel_window_id"] == candidate["parallel_window_id"]
    same_derivation = reference["derivation_identity"] == candidate["derivation_identity"]
    conflict = bool(
        candidate_claims_independent_origin
        and same_parallel_window
        and same_genealogy
        and same_initial_conditions
    )

    return {
        "same_origin_family": same_family,
        "same_derived_genealogy": same_genealogy,
        "same_relevant_initial_conditions": same_initial_conditions,
        "same_parallel_window": same_parallel_window,
        "same_derivation": same_derivation,
        "distinct_construction_same_origin_family": same_family and not same_derivation,
        "candidate_claims_independent_origin": bool(candidate_claims_independent_origin),
        "false_originality_provenance_conflict": conflict,
        "classification": (
            "PARALLEL_INDEPENDENT_INITIAL_CONDITIONS_CONTRADICTED_BY_HHS_GENEALOGY"
            if conflict
            else "NO_PARALLEL_INITIAL_CONDITION_CONFLICT"
        ),
        "bounded_claim": True,
        "claim_scope": "PARALLEL_HUMAN_DERIVATION_WITHIN_DECLARED_WINDOW",
        "comparison_authority": "EXACT_STRUCTURED_GENEALOGY_AND_INITIAL_CONDITIONS",
        "information_impossibility_claimed": False,
        "computational_impossibility_claimed": False,
        "unbounded_impossibility_claimed": False,
        "priority_anchor_commit": PUBLIC_PRIORITY_ANCHOR["commit_sha"],
        "priority_anchor_time": PUBLIC_PRIORITY_ANCHOR["commit_created_at"],
    }
