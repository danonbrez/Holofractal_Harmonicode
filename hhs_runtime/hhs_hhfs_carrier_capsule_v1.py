"""
HHS HHFS Carrier Capsule v1
===========================

Pass 039 binds HHS witness state to legacy carrier files without creating a
parallel archive.  The capsule is carrier-native: it stores commitments,
witness metadata, transformation-history roots, and bounded error-correction
roots, but it never stores a duplicate payload or requires a sidecar/remote
resolver to remain valid.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload
from hhs_runtime.hhs_repo_paths_v1 import runtime_artifact_path
from hhs_runtime.hhs_genesis_severance_protocol_v1 import (
    GENESIS_SEVERED_PRIVACY,
    REDACTED_CONTINUITY,
    WITNESSED_CONTINUITY,
)


VERSION = "PASS_039_HHFS_CARRIER_CAPSULE_V1"
CAPSULE_SCHEMA = "HHS_HHFS_CARRIER_CAPSULE_V1"
ROOT_WITNESS_SCHEMA = "HHS_HHFS_ROOT_WITNESS_BLOCK_V1"
RESONATOR_CONSTANT_Q = "179971179971/1000000"
CLOSURE_CONSTANT_Q = "1001/1000"
DEFAULT_ROOT_MARKER = "2026-02-28T16:45:12"
HASH72_AUTHORITY = "HASH72_U72_C_KERNEL"

CARRIER_PROFILES: Dict[str, Dict[str, str]] = {
    "png": {
        "native_witness_lane": "png.private_ancillary_chunk",
        "legacy_behavior": "legacy_decoders_ignore_private_ancillary_chunk_and_display_image",
        "payload_view": "png.renderable_image_payload",
    },
    "jpeg": {
        "native_witness_lane": "jpeg.app1_exif_or_xmp_segment",
        "legacy_behavior": "legacy_decoders_display_image_and_ignore_unknown_metadata",
        "payload_view": "jpeg.renderable_image_payload",
    },
    "mp3": {
        "native_witness_lane": "id3v2.private_frame",
        "legacy_behavior": "legacy_players_ignore_private_frame_and_play_audio",
        "payload_view": "mp3.audible_audio_payload",
    },
    "wav": {
        "native_witness_lane": "riff.custom_chunk",
        "legacy_behavior": "riff_readers_skip_unknown_chunks_and_play_audio",
        "payload_view": "wav.audible_audio_payload",
    },
    "text": {
        "native_witness_lane": "text.canonical_witness_block",
        "legacy_behavior": "plain_text_remains_readable_with_visible_witness_block",
        "payload_view": "text.readable_symbolic_payload",
    },
}

ALLOWED_STORAGE_LANES = {
    "carrier_native_payload_commitment",
    "carrier_native_witness_capsule",
    "metadata_enhancement",
    "transformation_history",
    "error_correction",
}

ALLOWED_COMPUTATION_LANES = {
    "carrier_native_parse",
    "witness_verification",
    "transformation_history_append",
    "error_correction_reconstruction",
}

FORBIDDEN_STORAGE_LANES = {
    "external_sidecar",
    "sidecar_manifest",
    "remote_resolver",
    "shadow_archive",
    "parallel_archive",
    "duplicate_payload",
    "payload_copy",
    "raw_payload_copy",
    "external_database",
    "alternate_block_store",
}

FORBIDDEN_COMPUTATION_LANES = {
    "hidden_executor",
    "parallel_compute",
    "remote_only_resolver",
    "undeclared_runtime",
    "opaque_subroutine_inside_parent_manifold",
    "sidecar_computation",
}

FORBIDDEN_PAYLOAD_FIELDS = {
    "payload",
    "raw_payload",
    "payload_copy",
    "duplicate_payload",
    "parallel_archive_payload",
    "shadow_payload",
}

REJECT_UNSUPPORTED_CARRIER_PROFILE = "REJECT_UNSUPPORTED_CARRIER_PROFILE"
REJECT_EXTERNAL_SIDECAR_DEPENDENCY = "REJECT_EXTERNAL_SIDECAR_DEPENDENCY"
REJECT_DUPLICATE_PAYLOAD_STORAGE = "REJECT_DUPLICATE_PAYLOAD_STORAGE"
REJECT_PARALLEL_STORAGE_LANE = "REJECT_PARALLEL_STORAGE_LANE"
REJECT_PARALLEL_COMPUTATION_LANE = "REJECT_PARALLEL_COMPUTATION_LANE"
REJECT_MISSING_PAYLOAD_COMMITMENT = "REJECT_MISSING_PAYLOAD_COMMITMENT"
REJECT_TRANSFORMATION_HISTORY_REQUIRED = "REJECT_TRANSFORMATION_HISTORY_REQUIRED"
REJECT_CARRIER_NATIVE_WITNESS_LANE_MISMATCH = "REJECT_CARRIER_NATIVE_WITNESS_LANE_MISMATCH"
REJECT_HHFS_FLOAT_CONSTANT = "REJECT_HHFS_FLOAT_CONSTANT"
REJECT_INVALID_PHASE_BINDING = "REJECT_INVALID_PHASE_BINDING"
REJECT_CAPSULE_HASH_MISMATCH = "REJECT_CAPSULE_HASH_MISMATCH"
ADMIT_HHFS_CARRIER_CAPSULE = "ADMIT_HHFS_CARRIER_CAPSULE"

CANONICAL_CAPSULE_FIELD_ORDER: Tuple[str, ...] = (
    "schema",
    "version",
    "carrier_type",
    "carrier_native_witness_lane",
    "legacy_behavior",
    "modality_type",
    "payload_view",
    "payload_commitment",
    "metadata_enhancement_root",
    "transformation_trace_root",
    "error_correction_root",
    "root_witness_hash72",
    "storage_lanes",
    "computation_lanes",
    "phase_binding",
    "allows_error_correction",
    "requires_transformation_history",
    "payload_duplication_allowed",
    "external_dependency_allowed",
    "root_marker_declared",
    "resonator_constant_q",
    "closure_constant_q",
    "ring",
    "extended_ring",
    "loshu_anchor",
    "parity_required",
    "delta_e_required",
    "omega_required",
    "hash_authority",
)



def _pass039_ledger_path():
    return runtime_artifact_path("hhs_pass039_hhfs_udfp_ledger.json")


def _reject(status: str, reason: str, *, details: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {
        "schema": "HHS_HHFS_CARRIER_CAPSULE_REJECTION_V1",
        "ok": False,
        "status": status,
        "reason": reason,
        "details": dict(details or {}),
    }


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, Mapping):
        return any(_contains_float(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_contains_float(v) for v in value)
    return False


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def _normalize_list(values: Optional[Iterable[Any]]) -> List[str]:
    normalized: List[str] = []
    for value in values or []:
        text = str(value).strip()
        if text:
            normalized.append(text)
    return sorted(dict.fromkeys(normalized))


def _hash72(label: str, value: Any, *, width: int = 72) -> str:
    return make_hash72_kernel_witness(label, value, width=width).digest


def commit_payload_view(payload_canonical_view: Any, *, label: str = "HHS_HHFS_PAYLOAD_VIEW_COMMITMENT_V1") -> str:
    """Commit to the carrier-native payload view without storing a duplicate payload."""

    if _contains_float(payload_canonical_view):
        raise ValueError("HHFS payload commitments require exact symbolic/rational values; floats are rejected")
    return _hash72(label, payload_canonical_view, width=72)


def canonical_root_witness_fields(
    *,
    carrier_type: str,
    modality_type: str,
    payload_commitment: str,
    metadata_enhancement_root: str,
    transformation_trace_root: str,
    error_correction_root: str = "NO_ECC_ROOT_DECLARED",
    root_marker_declared: str = DEFAULT_ROOT_MARKER,
) -> Dict[str, Any]:
    carrier_type = str(carrier_type).lower().strip()
    if carrier_type not in CARRIER_PROFILES:
        raise ValueError(f"unsupported carrier_type: {carrier_type}")
    fields = {
        "schema": ROOT_WITNESS_SCHEMA,
        "version": VERSION,
        "carrier_type": carrier_type,
        "carrier_native_witness_lane": CARRIER_PROFILES[carrier_type]["native_witness_lane"],
        "modality_type": str(modality_type),
        "payload_commitment": str(payload_commitment),
        "metadata_enhancement_root": str(metadata_enhancement_root),
        "transformation_trace_root": str(transformation_trace_root),
        "error_correction_root": str(error_correction_root),
        "root_marker_declared": str(root_marker_declared),
        "resonator_constant_q": RESONATOR_CONSTANT_Q,
        "closure_constant_q": CLOSURE_CONSTANT_Q,
        "ring": "u^72",
        "extended_ring": "u^216",
        "loshu_anchor": 5,
        "parity_required": "Psi=0",
        "delta_e_required": "Delta_e=0",
        "omega_required": True,
        "hash_authority": HASH72_AUTHORITY,
    }
    if _contains_float(fields):
        raise ValueError("HHFS root witness fields cannot contain floats")
    return fields


def make_root_witness_hash72(**kwargs: Any) -> str:
    return _hash72("HHS_HHFS_ROOT_WITNESS_BLOCK_V1", canonical_root_witness_fields(**kwargs), width=72)


def canonical_capsule_fields(
    *,
    carrier_type: str,
    modality_type: str,
    payload_commitment: str,
    metadata_enhancement_root: str,
    transformation_trace_root: str,
    error_correction_root: str = "NO_ECC_ROOT_DECLARED",
    root_witness_hash72: Optional[str] = None,
    storage_lanes: Optional[Sequence[str]] = None,
    computation_lanes: Optional[Sequence[str]] = None,
    phase_binding: str = WITNESSED_CONTINUITY,
    root_marker_declared: str = DEFAULT_ROOT_MARKER,
) -> Dict[str, Any]:
    carrier_type = str(carrier_type).lower().strip()
    if carrier_type not in CARRIER_PROFILES:
        raise ValueError(f"unsupported carrier_type: {carrier_type}")
    profile = CARRIER_PROFILES[carrier_type]
    lanes = _normalize_list(storage_lanes or (
        "carrier_native_payload_commitment",
        "carrier_native_witness_capsule",
        "metadata_enhancement",
        "transformation_history",
        "error_correction",
    ))
    compute = _normalize_list(computation_lanes or (
        "carrier_native_parse",
        "witness_verification",
        "transformation_history_append",
        "error_correction_reconstruction",
    ))
    root_witness_hash72 = root_witness_hash72 or make_root_witness_hash72(
        carrier_type=carrier_type,
        modality_type=modality_type,
        payload_commitment=payload_commitment,
        metadata_enhancement_root=metadata_enhancement_root,
        transformation_trace_root=transformation_trace_root,
        error_correction_root=error_correction_root,
        root_marker_declared=root_marker_declared,
    )
    fields = {
        "schema": CAPSULE_SCHEMA,
        "version": VERSION,
        "carrier_type": carrier_type,
        "carrier_native_witness_lane": profile["native_witness_lane"],
        "legacy_behavior": profile["legacy_behavior"],
        "modality_type": str(modality_type),
        "payload_view": profile["payload_view"],
        "payload_commitment": str(payload_commitment),
        "metadata_enhancement_root": str(metadata_enhancement_root),
        "transformation_trace_root": str(transformation_trace_root),
        "error_correction_root": str(error_correction_root),
        "root_witness_hash72": str(root_witness_hash72),
        "storage_lanes": lanes,
        "computation_lanes": compute,
        "phase_binding": str(phase_binding),
        "allows_error_correction": True,
        "requires_transformation_history": True,
        "payload_duplication_allowed": False,
        "external_dependency_allowed": False,
        "root_marker_declared": str(root_marker_declared),
        "resonator_constant_q": RESONATOR_CONSTANT_Q,
        "closure_constant_q": CLOSURE_CONSTANT_Q,
        "ring": "u^72",
        "extended_ring": "u^216",
        "loshu_anchor": 5,
        "parity_required": "Psi=0",
        "delta_e_required": "Delta_e=0",
        "omega_required": True,
        "hash_authority": HASH72_AUTHORITY,
    }
    return {key: fields[key] for key in CANONICAL_CAPSULE_FIELD_ORDER}


@dataclass(frozen=True)
class HHFSCarrierCapsule:
    schema: str
    version: str
    canonical_capsule_fields: Dict[str, Any]
    capsule_hash72: str
    root_witness_hash72: str
    kernel_witness: Dict[str, Any]
    unified_ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_hhfs_carrier_capsule(capsule: Mapping[str, Any]) -> Dict[str, Any]:
    if _contains_float(capsule):
        return _reject(REJECT_HHFS_FLOAT_CONSTANT, "HHFS capsule fields must use exact symbolic/rational values, not floats.")

    for forbidden in FORBIDDEN_PAYLOAD_FIELDS:
        if forbidden in capsule:
            return _reject(REJECT_DUPLICATE_PAYLOAD_STORAGE, "HHFS capsules must not store raw or duplicate payload material.", details={"field": forbidden})

    fields = capsule.get("canonical_capsule_fields", capsule)
    if not isinstance(fields, Mapping):
        return _reject(REJECT_UNSUPPORTED_CARRIER_PROFILE, "HHFS capsule canonical fields are missing or invalid.")

    for forbidden in FORBIDDEN_PAYLOAD_FIELDS:
        if forbidden in fields:
            return _reject(REJECT_DUPLICATE_PAYLOAD_STORAGE, "HHFS canonical fields must contain commitments, not payload copies.", details={"field": forbidden})

    carrier_type = str(fields.get("carrier_type", "")).lower().strip()
    if carrier_type not in CARRIER_PROFILES:
        return _reject(REJECT_UNSUPPORTED_CARRIER_PROFILE, "Carrier profile is not HHFS-declared.", details={"carrier_type": carrier_type})

    profile = CARRIER_PROFILES[carrier_type]
    if fields.get("carrier_native_witness_lane") != profile["native_witness_lane"]:
        return _reject(
            REJECT_CARRIER_NATIVE_WITNESS_LANE_MISMATCH,
            "HHFS witness must be embedded through the declared carrier-native lane.",
            details={"expected": profile["native_witness_lane"], "actual": fields.get("carrier_native_witness_lane")},
        )

    if not fields.get("payload_commitment"):
        return _reject(REJECT_MISSING_PAYLOAD_COMMITMENT, "HHFS stores a payload commitment, not a duplicate payload copy.")
    if not fields.get("transformation_trace_root"):
        return _reject(REJECT_TRANSFORMATION_HISTORY_REQUIRED, "HHFS carriers require a transformation-history root.")

    external_dependencies = capsule.get("external_dependencies") or fields.get("external_dependencies")
    if external_dependencies or bool(fields.get("external_dependency_allowed")):
        return _reject(REJECT_EXTERNAL_SIDECAR_DEPENDENCY, "HHFS validity cannot require sidecars, remote resolvers, or external databases.")

    if bool(fields.get("payload_duplication_allowed")) or bool(capsule.get("duplicate_payload_storage")):
        return _reject(REJECT_DUPLICATE_PAYLOAD_STORAGE, "HHFS forbids duplicate payload storage outside bounded ECC.")

    storage_lanes = set(_normalize_list(fields.get("storage_lanes")))
    forbidden_storage = storage_lanes & FORBIDDEN_STORAGE_LANES
    if forbidden_storage:
        return _reject(REJECT_PARALLEL_STORAGE_LANE, "HHFS forbids parallel storage lanes.", details={"forbidden_lanes": sorted(forbidden_storage)})
    unknown_storage = storage_lanes - ALLOWED_STORAGE_LANES
    if unknown_storage:
        return _reject(REJECT_PARALLEL_STORAGE_LANE, "HHFS storage lanes must be explicitly declared and carrier-compatible.", details={"unknown_lanes": sorted(unknown_storage)})
    required_storage = {"carrier_native_payload_commitment", "carrier_native_witness_capsule", "transformation_history"}
    if not required_storage.issubset(storage_lanes):
        return _reject(REJECT_PARALLEL_STORAGE_LANE, "HHFS carrier capsule is missing required native/witness storage lanes.", details={"required": sorted(required_storage)})

    computation_lanes = set(_normalize_list(fields.get("computation_lanes")))
    forbidden_compute = computation_lanes & FORBIDDEN_COMPUTATION_LANES
    if forbidden_compute:
        return _reject(REJECT_PARALLEL_COMPUTATION_LANE, "HHFS forbids hidden or parallel computation lanes.", details={"forbidden_lanes": sorted(forbidden_compute)})
    unknown_compute = computation_lanes - ALLOWED_COMPUTATION_LANES
    if unknown_compute:
        return _reject(REJECT_PARALLEL_COMPUTATION_LANE, "HHFS computation lanes are limited to verification, trace append, carrier parse, and ECC reconstruction.", details={"unknown_lanes": sorted(unknown_compute)})

    phase = fields.get("phase_binding")
    if phase not in {WITNESSED_CONTINUITY, REDACTED_CONTINUITY, GENESIS_SEVERED_PRIVACY}:
        return _reject(REJECT_INVALID_PHASE_BINDING, "HHFS carrier capsule must bind to a declared phase domain.", details={"phase_binding": phase})
    if phase == GENESIS_SEVERED_PRIVACY and capsule.get("claims_parent_continuity"):
        return _reject(REJECT_INVALID_PHASE_BINDING, "Genesis-severed privacy carriers cannot claim parent continuity.")

    expected_hash = _hash72("HHS_HHFS_CARRIER_CAPSULE_V1", {key: fields.get(key) for key in CANONICAL_CAPSULE_FIELD_ORDER}, width=72)
    supplied_hash = capsule.get("capsule_hash72")
    if supplied_hash and supplied_hash != expected_hash:
        return _reject(REJECT_CAPSULE_HASH_MISMATCH, "HHFS capsule hash does not match canonical capsule fields.")

    record = {
        "schema": "HHS_HHFS_CARRIER_CAPSULE_VALIDATION_V1",
        "ok": True,
        "status": ADMIT_HHFS_CARRIER_CAPSULE,
        "admitted": True,
        "carrier_type": carrier_type,
        "carrier_native_witness_lane": profile["native_witness_lane"],
        "legacy_behavior": profile["legacy_behavior"],
        "capsule_hash72": expected_hash,
        "storage_lanes": sorted(storage_lanes),
        "computation_lanes": sorted(computation_lanes),
        "no_parallel_storage": True,
        "no_parallel_computation": True,
        "payload_duplication_allowed": False,
    }
    kernel = make_hash72_kernel_witness("HHS_HHFS_CARRIER_CAPSULE_VALIDATION_V1", record, width=72).to_dict()
    ledger = append_payload("HHFS_CARRIER_CAPSULE_VALIDATION", "hhs_hhfs_carrier_capsule_v1.validate_hhfs_carrier_capsule", {**record, "kernel_digest72": kernel.get("digest")}, ledger_path=_pass039_ledger_path())
    record["kernel_witness"] = kernel
    record["unified_ledger"] = {"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True}
    return record


def make_hhfs_carrier_capsule(**kwargs: Any) -> Dict[str, Any]:
    fields = canonical_capsule_fields(**kwargs)
    if _contains_float(fields):
        raise ValueError("HHFS capsule fields cannot contain floats")
    kernel = make_hash72_kernel_witness("HHS_HHFS_CARRIER_CAPSULE_V1", fields, width=72).to_dict()
    ledger = append_payload("HHFS_CARRIER_CAPSULE", "hhs_hhfs_carrier_capsule_v1.make_hhfs_carrier_capsule", {"canonical_capsule_fields": fields, "capsule_hash72": kernel.get("digest")}, ledger_path=_pass039_ledger_path())
    capsule = HHFSCarrierCapsule(
        schema=CAPSULE_SCHEMA,
        version=VERSION,
        canonical_capsule_fields=fields,
        capsule_hash72=str(kernel.get("digest")),
        root_witness_hash72=str(fields["root_witness_hash72"]),
        kernel_witness=kernel,
        unified_ledger={"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True},
    ).to_dict()
    validation = validate_hhfs_carrier_capsule(capsule)
    if not validation.get("ok"):
        raise ValueError(validation.get("status", "HHFS capsule validation failed"))
    capsule["validation"] = validation
    return capsule


def hhfs_carrier_capsule_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload_commitment = commit_payload_view({"carrier": "png", "view": "sample-pixels", "bytes_commitment_only": True})
    metadata_root = _hash72("HHFS_SAMPLE_METADATA_ROOT", {"capture": "sample"}, width=72)
    trace_root = _hash72("HHFS_SAMPLE_TRACE_ROOT", {"trace": ["capture"]}, width=72)
    ecc_root = _hash72("HHFS_SAMPLE_ECC_ROOT", {"ecc": "bounded"}, width=72)
    capsule = make_hhfs_carrier_capsule(
        carrier_type="png",
        modality_type="image",
        payload_commitment=payload_commitment,
        metadata_enhancement_root=metadata_root,
        transformation_trace_root=trace_root,
        error_correction_root=ecc_root,
    )
    valid = validate_hhfs_carrier_capsule(capsule)
    sidecar_fields = dict(capsule["canonical_capsule_fields"])
    sidecar_fields["storage_lanes"] = [*sidecar_fields["storage_lanes"], "external_sidecar"]
    sidecar_rejection = validate_hhfs_carrier_capsule({"canonical_capsule_fields": sidecar_fields})
    duplicate_rejection = validate_hhfs_carrier_capsule({**capsule, "payload_copy": "forbidden"})
    ok = bool(
        valid.get("status") == ADMIT_HHFS_CARRIER_CAPSULE
        and sidecar_rejection.get("status") == REJECT_PARALLEL_STORAGE_LANE
        and duplicate_rejection.get("status") == REJECT_DUPLICATE_PAYLOAD_STORAGE
        and valid.get("unified_ledger", {}).get("verified") is True
    )
    return {
        "schema": "HHS_HHFS_CARRIER_CAPSULE_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "valid_status": valid.get("status"),
        "sidecar_rejection_status": sidecar_rejection.get("status"),
        "duplicate_rejection_status": duplicate_rejection.get("status"),
        "carrier_count": len(CARRIER_PROFILES),
        "canonical_capsule_field_count": len(CANONICAL_CAPSULE_FIELD_ORDER),
        "capsule_hash72": capsule.get("capsule_hash72"),
        "ledger_verified": valid.get("unified_ledger", {}).get("verified") is True,
    }


if __name__ == "__main__":
    print(json.dumps(hhfs_carrier_capsule_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
