"""Deterministic HHS system-standardization signature watermark.

This module binds constructions to the exact system-standardization tuple without
replacing or lossy-normalizing the enclosed construction.  It is a deterministic
recognition watermark / provenance fingerprint, not a secret-key authenticity
signature.  Cryptographic signer authenticity remains a separate PQC boundary.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_lane5_multimodal_shared_root_fabric_v1 import (
    INVARIANT_GATE,
    ROOT_METADATA_SEED,
    hash216_genus3_polyhedral_surface,
    shared_multimodal_root_sha256,
)
from hhs_runtime.pass219.lane5_nine_loop_feedback_1_70 import GENESIS_IDENTITY


SCHEMA = "HHS_SYSTEM_STANDARDIZATION_SIGNATURE_WATERMARK_V1"
VERSION = "1.0.0"
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
        "closure": {
            "delta_e": 0,
            "psi": 0,
            "omega": True,
        },
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


def watermark_construction(
    construction: Any,
    *,
    construction_type: str,
) -> dict[str, Any]:
    if not construction_type or not isinstance(construction_type, str):
        raise HHSSystemSignatureError("construction_type must be a non-empty string")

    construction_copy = deepcopy(construction)
    construction_sha256 = sha256(canonical_bytes(construction_copy)).hexdigest()
    standardization = system_standardization_payload()
    standardization_sha256 = sha256(canonical_bytes(standardization)).hexdigest()

    signature_body = {
        "schema": SCHEMA + "_BODY",
        "version": VERSION,
        "construction_type": construction_type,
        "construction_sha256": construction_sha256,
        "standardization": standardization,
        "standardization_sha256": standardization_sha256,
    }
    signature_sha256 = sha256(canonical_bytes(signature_body)).hexdigest()

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "construction": construction_copy,
        "watermark": {
            **signature_body,
            "signature_sha256": signature_sha256,
        },
    }


def recognize_construction(envelope: Mapping[str, Any]) -> dict[str, Any]:
    try:
        if envelope.get("schema") != SCHEMA or envelope.get("version") != VERSION:
            return {"recognized": False, "reason": "ENVELOPE_IDENTITY_MISMATCH"}

        if "construction" not in envelope:
            return {"recognized": False, "reason": "CONSTRUCTION_MISSING"}

        watermark = envelope.get("watermark")
        if not isinstance(watermark, Mapping):
            return {"recognized": False, "reason": "WATERMARK_MISSING"}

        claimed_signature = watermark.get("signature_sha256")
        if not isinstance(claimed_signature, str) or len(claimed_signature) != 64:
            return {"recognized": False, "reason": "SIGNATURE_FORMAT_MISMATCH"}

        signature_body = dict(watermark)
        signature_body.pop("signature_sha256", None)

        if signature_body.get("schema") != SCHEMA + "_BODY":
            return {"recognized": False, "reason": "SIGNATURE_SCHEMA_MISMATCH"}
        if signature_body.get("version") != VERSION:
            return {"recognized": False, "reason": "SIGNATURE_VERSION_MISMATCH"}

        construction_sha256 = sha256(
            canonical_bytes(envelope["construction"])
        ).hexdigest()
        if signature_body.get("construction_sha256") != construction_sha256:
            return {"recognized": False, "reason": "CONSTRUCTION_DRIFT"}

        expected_standardization = system_standardization_payload()
        if signature_body.get("standardization") != expected_standardization:
            return {"recognized": False, "reason": "STANDARDIZATION_DRIFT"}

        expected_standardization_sha256 = sha256(
            canonical_bytes(expected_standardization)
        ).hexdigest()
        if (
            signature_body.get("standardization_sha256")
            != expected_standardization_sha256
        ):
            return {"recognized": False, "reason": "STANDARDIZATION_ROOT_DRIFT"}

        expected_signature = sha256(canonical_bytes(signature_body)).hexdigest()
        if claimed_signature != expected_signature:
            return {"recognized": False, "reason": "SIGNATURE_DRIFT"}

        return {
            "recognized": True,
            "reason": "HHS_CONSTRUCTION_RECOGNIZED",
            "construction_type": signature_body["construction_type"],
            "construction_sha256": construction_sha256,
            "standardization_sha256": expected_standardization_sha256,
            "signature_sha256": expected_signature,
        }
    except (HHSSystemSignatureError, TypeError, ValueError, KeyError):
        return {"recognized": False, "reason": "MALFORMED_OR_NONCANONICAL"}


def unwrap_recognized_construction(envelope: Mapping[str, Any]) -> Any:
    result = recognize_construction(envelope)
    if result.get("recognized") is not True:
        raise HHSSystemSignatureError(
            "construction recognition failed: " + str(result.get("reason"))
        )
    return deepcopy(envelope["construction"])
