"""Fail-closed registry-aware candidate admission for existing P modality bridges.

Native registry capability status is authoritative for codec discovery. This
inspector neither changes the provider registry nor grants VM81 admission.
"""
from __future__ import annotations
from hashlib import sha256
import json
from hhs_runtime.hhs_lane5_native_capability_provider_v1 import CAPABILITIES
from hhs_runtime.hhs_pass220_cross_modal_p_bridge_search_v1 import BridgeSearchError
from hhs_runtime.hhs_pass220_native_numpy_ieee_p_bridge_v1 import verify_ieee_p_bridge

SCHEMA = "HHS_PASS220_REGISTRY_AWARE_P_MODALITY_BRIDGE_V1"

def inspect_numpy_ieee_bridge(bits: int) -> dict:
    spec = CAPABILITIES.get("numpy")
    if spec is None or not spec.native_implemented or not spec.native_surfaces:
        raise BridgeSearchError("NATIVE_NUMPY_CAPABILITY_NOT_REGISTERED")
    evidence = verify_ieee_p_bridge(bits)
    if not evidence["raw_bits_roundtrip_verified"] or not evidence["type_codec_executed"]:
        raise BridgeSearchError("REGISTERED_CODEC_ROUNDTRIP_FAILED")
    record = {
        "schema": SCHEMA,
        "capability_id": spec.capability_id,
        "registered_native_surfaces": list(spec.native_surfaces),
        "provider_policy": "NATIVE_FIRST",
        "P_decimal": evidence["P_decimal"],
        "ieee_bridge_serialized_sha256": evidence["serialized_5184_sha256"],
        "exact_registered_codec_roundtrip": True,
        "external_fallback_used": False,
        "universal_modality_coverage_proven": False,
        "canonical_vm81_admission": False,
        "canonical_hash72_mint": False,
        "canonical_hash216_persistence": False,
    }
    record["receipt_sha256"] = sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":")
    ).encode("ascii")).hexdigest()
    return record


def require_registered_native_modality(capability_id: str) -> tuple[str, ...]:
    if not isinstance(capability_id, str) or not capability_id:
        raise BridgeSearchError("MODALITY_CAPABILITY_ID_REQUIRED")
    spec = CAPABILITIES.get(capability_id)
    if spec is None or not spec.native_implemented or not spec.native_surfaces:
        raise BridgeSearchError("MODALITY_HAS_NO_REGISTERED_NATIVE_PROVIDER")
    return spec.native_surfaces
