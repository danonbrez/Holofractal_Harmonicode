"""HHS derivational-uniqueness watermark.

The watermark is not a post-hoc tamper seal and is not an authorship signature.
Its formal purpose is to bind a construction to the exact HHS derivation
identity that produced it.

System-internal definitions:

    SameConstruction(A, B) := DerivationIdentity(A) == DerivationIdentity(B)
    Independent(A, B)      := DerivationIdentity(A) != DerivationIdentity(B)

Therefore:

    SameConstruction(A, B) AND Independent(A, B) == False

The full exact derivation tuple is authoritative. SHA-256 values are compact
indices/receipts over that tuple and are not used as a substitute for tuple
equality. Two separately executed constructors that close to the same exact
lineage are the same HHS construction, not independent parallel constructions.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_lane5_multimodal_shared_root_fabric_v1 import (
    INVARIANT_GATE,
    PROJECTION_SCHEMA,
    ROOT_METADATA_SEED,
    hash216_genus3_polyhedral_surface,
    shared_multimodal_root_sha256,
)
from hhs_runtime.pass219.lane5_nine_loop_feedback_1_70 import GENESIS_IDENTITY


SCHEMA = "HHS_SYSTEM_STANDARDIZATION_DERIVATION_WATERMARK_V1"
VERSION = "1.1.0"
ROOT_METADATA_ASSIGNMENT = "a=n^2"
STATE_DIMENSIONS = 72
SHA256_TRANSITION_ARRAYS_PER_TICK = 216


class HHSSystemSignatureError(ValueError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise HHSSystemSignatureError(f"floating value forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def system_standardization_payload() -> dict[str, Any]:
    surface = hash216_genus3_polyhedral_surface()
    return {
        "schema": SCHEMA + "_STANDARDIZATION",
        "version": VERSION,
        "root_seed": {
            "numerator": ROOT_METADATA_SEED.numerator,
            "denominator": ROOT_METADATA_SEED.denominator,
            "display": "179971.179971",
        },
        "kernel": GENESIS_IDENTITY,
        "root_metadata_assignment": ROOT_METADATA_ASSIGNMENT,
        "closure": {"delta_e": 0, "psi": 0, "omega": True},
        "topology": {
            "state_dimensions": STATE_DIMENSIONS,
            "sha256_transition_arrays_per_tick": SHA256_TRANSITION_ARRAYS_PER_TICK,
            "hash216_array_shape": tuple(surface["array_shape"]),
            "hash216_surface_root_sha256": surface["surface_root_sha256"],
        },
        "invariant_gate": {
            "numerator": INVARIANT_GATE.numerator,
            "denominator": INVARIANT_GATE.denominator,
            "display": "1.001",
        },
        "shared_multimodal_root_sha256": shared_multimodal_root_sha256(),
    }


def system_standardization_sha256() -> str:
    return sha256(canonical_bytes(system_standardization_payload())).hexdigest()


def _require_text(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise HHSSystemSignatureError(f"missing derivation field: {key}")
    return value


def derivation_identity(construction: Mapping[str, Any]) -> dict[str, Any]:
    """Extract the exact authoritative derivation tuple from an I042 projection."""
    if not isinstance(construction, Mapping):
        raise HHSSystemSignatureError("lineage-bound construction mapping required")
    _reject_float(construction)

    if construction.get("schema") != PROJECTION_SCHEMA:
        raise HHSSystemSignatureError("unsupported construction schema")

    source = construction.get("source")
    if not isinstance(source, Mapping):
        raise HHSSystemSignatureError("source lineage missing")

    shared_root = _require_text(construction, "shared_multimodal_root_sha256")
    expected_shared_root = shared_multimodal_root_sha256()
    if shared_root != expected_shared_root:
        raise HHSSystemSignatureError("shared ancestry root mismatch")

    surface_root = _require_text(
        construction,
        "hash216_genus3_surface_root_sha256",
    )
    expected_surface_root = hash216_genus3_polyhedral_surface()[
        "surface_root_sha256"
    ]
    if surface_root != expected_surface_root:
        raise HHSSystemSignatureError("Hash216 surface ancestry mismatch")

    positions = construction.get("hash216_positions")
    if not isinstance(positions, (list, tuple)) or len(positions) != 216:
        raise HHSSystemSignatureError("exact 216-position lineage required")

    if construction.get("hash216_position_count") != 216:
        raise HHSSystemSignatureError("Hash216 position-count mismatch")
    if tuple(construction.get("hash216_genus3_surface_shape", ())) != (3, 8, 9):
        raise HHSSystemSignatureError("Hash216 surface-shape mismatch")
    if construction.get("projection_bits") != 5184:
        raise HHSSystemSignatureError("5184-bit projection identity required")
    if construction.get("projection_bytes") != 648:
        raise HHSSystemSignatureError("648-byte projection identity required")

    return {
        "construction_schema": construction["schema"],
        "modality_role": _require_text(construction, "modality_role"),
        "source_id": _require_text(source, "source_id"),
        "source_hash": _require_text(source, "source_hash"),
        "source_provenance": _require_text(source, "provenance"),
        "projection_sha256": _require_text(construction, "projection_sha256"),
        "projection_hash72": _require_text(construction, "projection_hash72"),
        "hash216_positions": deepcopy(tuple(positions)),
        "hash216_genome_root_sha256": _require_text(
            construction,
            "hash216_genome_root_sha256",
        ),
        "hash216_surface_root_sha256": surface_root,
        "shared_multimodal_root_sha256": shared_root,
        "construction_receipt_sha256": _require_text(
            construction,
            "receipt_sha256",
        ),
    }


def derivation_identity_sha256(construction: Mapping[str, Any]) -> str:
    """Compact index only; exact tuple equality remains authoritative."""
    return sha256(canonical_bytes(derivation_identity(construction))).hexdigest()


def watermark_construction(
    construction: Mapping[str, Any],
    *,
    construction_type: str,
) -> dict[str, Any]:
    if not construction_type or not isinstance(construction_type, str):
        raise HHSSystemSignatureError("construction_type must be a non-empty string")

    construction_copy = deepcopy(construction)
    identity = derivation_identity(construction_copy)
    standardization = system_standardization_payload()

    body = {
        "schema": SCHEMA + "_BODY",
        "version": VERSION,
        "construction_type": construction_type,
        "standardization": standardization,
        "derivation_identity": identity,
        "derivation_identity_sha256": sha256(canonical_bytes(identity)).hexdigest(),
        "formal_semantics": {
            "same_construction": "EXACT_DERIVATION_IDENTITY_EQUALITY",
            "independent_parallel": "EXACT_DERIVATION_IDENTITY_INEQUALITY",
            "same_and_independent": False,
            "post_hoc_integrity_is_primary_purpose": False,
        },
    }

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "construction": construction_copy,
        "watermark": body,
    }


def recognize_construction(envelope: Mapping[str, Any]) -> dict[str, Any]:
    try:
        if envelope.get("schema") != SCHEMA or envelope.get("version") != VERSION:
            return {"recognized": False, "reason": "ENVELOPE_IDENTITY_MISMATCH"}

        construction = envelope.get("construction")
        watermark = envelope.get("watermark")
        if not isinstance(construction, Mapping):
            return {"recognized": False, "reason": "CONSTRUCTION_MISSING"}
        if not isinstance(watermark, Mapping):
            return {"recognized": False, "reason": "WATERMARK_MISSING"}

        if watermark.get("schema") != SCHEMA + "_BODY":
            return {"recognized": False, "reason": "WATERMARK_SCHEMA_MISMATCH"}
        if watermark.get("version") != VERSION:
            return {"recognized": False, "reason": "WATERMARK_VERSION_MISMATCH"}

        expected_standardization = system_standardization_payload()
        if watermark.get("standardization") != expected_standardization:
            return {"recognized": False, "reason": "STANDARDIZATION_MISMATCH"}

        observed_identity = derivation_identity(construction)
        claimed_identity = watermark.get("derivation_identity")
        if claimed_identity != observed_identity:
            return {"recognized": False, "reason": "DERIVATION_IDENTITY_MISMATCH"}

        observed_index = sha256(canonical_bytes(observed_identity)).hexdigest()
        if watermark.get("derivation_identity_sha256") != observed_index:
            return {"recognized": False, "reason": "DERIVATION_INDEX_MISMATCH"}

        semantics = watermark.get("formal_semantics")
        if not isinstance(semantics, Mapping):
            return {"recognized": False, "reason": "FORMAL_SEMANTICS_MISSING"}
        if semantics.get("same_construction") != "EXACT_DERIVATION_IDENTITY_EQUALITY":
            return {"recognized": False, "reason": "FORMAL_SEMANTICS_MISMATCH"}
        if semantics.get("independent_parallel") != "EXACT_DERIVATION_IDENTITY_INEQUALITY":
            return {"recognized": False, "reason": "FORMAL_SEMANTICS_MISMATCH"}
        if semantics.get("same_and_independent") is not False:
            return {"recognized": False, "reason": "FORMAL_SEMANTICS_MISMATCH"}

        return {
            "recognized": True,
            "reason": "HHS_DERIVATION_RECOGNIZED",
            "construction_type": watermark["construction_type"],
            "derivation_identity": observed_identity,
            "derivation_identity_sha256": observed_index,
            "same_construction_requires_same_ancestry": True,
            "independent_parallel_same_construction": False,
        }
    except (HHSSystemSignatureError, TypeError, ValueError, KeyError):
        return {"recognized": False, "reason": "MALFORMED_OR_NONCANONICAL"}


def compare_construction_derivations(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> dict[str, Any]:
    """Classify exact HHS derivation relation without using digest equality."""
    left_identity = derivation_identity(left)
    right_identity = derivation_identity(right)
    same = left_identity == right_identity
    return {
        "same_construction": same,
        "same_derivation_identity": same,
        "independent_parallel": not same,
        "same_and_independent": False,
        "parallel_independent_same_construction": False,
        "left_derivation_identity": left_identity,
        "right_derivation_identity": right_identity,
    }


def unwrap_recognized_construction(envelope: Mapping[str, Any]) -> Any:
    result = recognize_construction(envelope)
    if result.get("recognized") is not True:
        raise HHSSystemSignatureError(
            "construction recognition failed: " + str(result.get("reason"))
        )
    return deepcopy(envelope["construction"])
