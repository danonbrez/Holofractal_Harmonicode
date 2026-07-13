"""
HHS Genesis Severance Protocol v1
=================================

Pass 038 formalizes lawful discontinuity for opaque/privacy-preserving
transformations.  A parent immutable manifold may witness that a Genesis
severance occurred, but it may not carry the opaque transform, reversible
mapping, child pointer, or parent-continuity claim into the privacy domain.

The boundary witness hash is generated through the existing Hash72/u^72 kernel
adapter so the severance record is bound to the same harmonic ring authority as
other runtime commitments.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
import copy
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload


VERSION = "PASS_038_GENESIS_SEVERANCE_PROTOCOL_V1"
BOUNDARY_WITNESS_SCHEMA = "HHS_PHASE_INVERSION_SEVERANCE_WITNESS_V1"
BOUNDARY_WITNESS_TYPE = "GENESIS_PRIVACY_SEVERANCE"
HASH72_AUTHORITY = "HASH72_U72_C_KERNEL"
DEFAULT_ROOT_MARKER = "2026-02-28T16:45:12"
CLOSURE_CONSTANT_Q = "1001/1000"
RESONATOR_CONSTANT_Q = "179971179971/1000000"

WITNESSED_CONTINUITY = "witnessed_continuity"
REDACTED_CONTINUITY = "redacted_continuity"
GENESIS_SEVERED_PRIVACY = "genesis_severed_privacy"
OPAQUE_UNLINKABLE = "opaque_unlinkable"

VALID_PARENT_COMMITMENT_POLICIES = {
    "none",
    "sealed_private_commitment",
    "escrowed_commitment",
    "public_redaction_commitment",
}

REJECT_OPAQUE_PRIVACY_INSIDE_SAME_UNIQUE_HISTORY = "REJECT_OPAQUE_PRIVACY_INSIDE_SAME_UNIQUE_HISTORY"
REJECT_OPAQUE_TRANSFORM_EMBEDDED_IN_IMMUTABLE_TRACE = "REJECT_OPAQUE_TRANSFORM_EMBEDDED_IN_IMMUTABLE_TRACE"
REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM = "REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM"
REJECT_HIDDEN_PARENT_POINTER_IN_PHASE_INVERTED_RECORD = "REJECT_HIDDEN_PARENT_POINTER_IN_PHASE_INVERTED_RECORD"
REJECT_REVERSIBLE_PARENT_MAPPING_IN_PHASE_INVERTED_RECORD = "REJECT_REVERSIBLE_PARENT_MAPPING_IN_PHASE_INVERTED_RECORD"
REJECT_CHILD_PUBLIC_POINTER_IN_OPAQUE_SEVERANCE = "REJECT_CHILD_PUBLIC_POINTER_IN_OPAQUE_SEVERANCE"
REJECT_BOUNDARY_FIELD_FLOAT_VALUE = "REJECT_BOUNDARY_FIELD_FLOAT_VALUE"
REJECT_INVALID_PARENT_COMMITMENT_POLICY = "REJECT_INVALID_PARENT_COMMITMENT_POLICY"


CANONICAL_BOUNDARY_FIELD_ORDER: Tuple[str, ...] = (
    "schema",
    "version",
    "witness_type",
    "phase_rule",
    "parent_phase",
    "child_phase",
    "severance_mode",
    "parent_record_commitment",
    "new_genesis_seed_commitment",
    "parent_commitment_policy",
    "severance_reason",
    "retained_semantic_constraints",
    "discarded_identity_fields",
    "root_marker_declared",
    "resonator_constant_q",
    "closure_constant_q",
    "ring",
    "extended_ring",
    "loshu_anchor",
    "parity_required",
    "delta_e_required",
    "omega_required",
    "parent_trace_continued",
    "opaque_transform_embedded",
    "child_public_pointer",
    "reversible_mapping_stored",
    "hidden_parent_pointer_stored",
    "parent_unique_history_exported",
    "boundary_hash_authority",
)

FORBIDDEN_PARENT_MANIFOLD_FIELDS = {
    "opaque_transform",
    "opaque_transform_recipe",
    "transform_recipe",
    "child_linkage_key",
    "reversible_mapping",
    "reversible_parent_mapping",
    "hidden_parent_pointer",
    "opaque_payload",
    "internal_privacy_trace",
    "parent_unique_history_export",
}


def _reject(status: str, reason: str, *, details: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {
        "schema": "HHS_GENESIS_SEVERANCE_REJECTION_V1",
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
    normalized = []
    for value in values or []:
        text = str(value).strip()
        if text:
            normalized.append(text)
    return sorted(dict.fromkeys(normalized))


def _hash72_digest(label: str, value: Any, *, width: int = 72) -> str:
    return make_hash72_kernel_witness(label, value, width=width).digest


def commit_value(value: Any, *, label: str = "hhs_genesis_severance_commitment_v1") -> str:
    """Return a 72-symbol Hash72/u^72 commitment for a canonical value."""

    if _contains_float(value):
        raise ValueError("HHS commitments must use exact symbolic/rational values; floats are rejected")
    return _hash72_digest(label, value, width=72)


@dataclass(frozen=True)
class PhaseInversionSeveranceWitness:
    schema: str
    version: str
    witness_type: str
    phase_rule: str
    parent_phase: str
    child_phase: str
    severance_mode: str
    parent_record_commitment: str
    new_genesis_seed_commitment: str
    parent_commitment_policy: str
    severance_reason: str
    retained_semantic_constraints: List[str]
    discarded_identity_fields: List[str]
    root_marker_declared: str
    resonator_constant_q: str
    closure_constant_q: str
    ring: str
    extended_ring: str
    loshu_anchor: int
    parity_required: str
    delta_e_required: str
    omega_required: bool
    parent_trace_continued: bool
    opaque_transform_embedded: bool
    child_public_pointer: Optional[str]
    reversible_mapping_stored: bool
    hidden_parent_pointer_stored: bool
    parent_unique_history_exported: bool
    boundary_hash_authority: str
    canonical_boundary_fields: Dict[str, Any]
    boundary_witness_hash72: str
    boundary_kernel_witness: Dict[str, Any]
    unified_ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def canonical_boundary_fields(
    *,
    parent_record_commitment: str,
    new_genesis_seed_commitment: str,
    severance_reason: str = "lawful opaque/privacy phase inversion",
    parent_commitment_policy: str = "sealed_private_commitment",
    retained_semantic_constraints: Optional[Sequence[str]] = None,
    discarded_identity_fields: Optional[Sequence[str]] = None,
    root_marker_declared: str = DEFAULT_ROOT_MARKER,
) -> Dict[str, Any]:
    """Return the exact field set hashed for a lawful Genesis severance.

    The returned mapping is field-complete and ordered by
    CANONICAL_BOUNDARY_FIELD_ORDER before Hash72 transport.  It deliberately
    stores commitments, not parent data, child pointers, opaque recipes, or
    reversible mappings.
    """

    if parent_commitment_policy not in VALID_PARENT_COMMITMENT_POLICIES:
        raise ValueError(f"invalid parent_commitment_policy: {parent_commitment_policy}")

    fields = {
        "schema": BOUNDARY_WITNESS_SCHEMA,
        "version": VERSION,
        "witness_type": BOUNDARY_WITNESS_TYPE,
        "phase_rule": "substrate_may_cross_identity_continuity_may_not_cross_unwitnessed",
        "parent_phase": WITNESSED_CONTINUITY,
        "child_phase": GENESIS_SEVERED_PRIVACY,
        "severance_mode": OPAQUE_UNLINKABLE,
        "parent_record_commitment": str(parent_record_commitment),
        "new_genesis_seed_commitment": str(new_genesis_seed_commitment),
        "parent_commitment_policy": parent_commitment_policy,
        "severance_reason": str(severance_reason),
        "retained_semantic_constraints": _normalize_list(
            retained_semantic_constraints
            or [
                "Delta_e=0",
                "Psi=0",
                "Omega=true",
                "no_parent_identity_continuity_claim",
            ]
        ),
        "discarded_identity_fields": _normalize_list(
            discarded_identity_fields
            or [
                "parent_trace_continuity",
                "parent_metadata_identity",
                "parent_observer_linkage",
                "reversible_parent_mapping",
                "child_public_pointer",
            ]
        ),
        "root_marker_declared": root_marker_declared,
        "resonator_constant_q": RESONATOR_CONSTANT_Q,
        "closure_constant_q": CLOSURE_CONSTANT_Q,
        "ring": "u^72",
        "extended_ring": "u^216",
        "loshu_anchor": 5,
        "parity_required": "Psi=0",
        "delta_e_required": "Delta_e=0",
        "omega_required": True,
        "parent_trace_continued": False,
        "opaque_transform_embedded": False,
        "child_public_pointer": None,
        "reversible_mapping_stored": False,
        "hidden_parent_pointer_stored": False,
        "parent_unique_history_exported": False,
        "boundary_hash_authority": HASH72_AUTHORITY,
    }
    return {key: fields[key] for key in CANONICAL_BOUNDARY_FIELD_ORDER}


def validate_boundary_fields(fields: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate a canonical boundary field mapping without ledger mutation."""

    missing = [field for field in CANONICAL_BOUNDARY_FIELD_ORDER if field not in fields]
    extra = [field for field in fields if field not in CANONICAL_BOUNDARY_FIELD_ORDER]
    if missing or extra:
        return _reject(
            "REJECT_NON_CANONICAL_BOUNDARY_FIELD_SET",
            "Boundary witness hash must be computed over the exact canonical field set.",
            details={"missing": missing, "extra": extra},
        )
    if _contains_float(fields):
        return _reject(
            REJECT_BOUNDARY_FIELD_FLOAT_VALUE,
            "Boundary witness fields must use exact symbolic/rational values; floats are forbidden.",
        )
    if fields.get("parent_commitment_policy") not in VALID_PARENT_COMMITMENT_POLICIES:
        return _reject(
            REJECT_INVALID_PARENT_COMMITMENT_POLICY,
            "Parent commitment policy is not one of the allowed severance policies.",
        )
    if fields.get("parent_phase") == fields.get("child_phase"):
        return _reject(
            REJECT_OPAQUE_PRIVACY_INSIDE_SAME_UNIQUE_HISTORY,
            "Opaque privacy cannot remain in the same phase class as the parent unique history.",
        )
    if fields.get("parent_trace_continued") is not False:
        return _reject(
            REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM,
            "Phase-inverted privacy requires parent_trace_continued=false.",
        )
    if fields.get("opaque_transform_embedded") is not False:
        return _reject(
            REJECT_OPAQUE_TRANSFORM_EMBEDDED_IN_IMMUTABLE_TRACE,
            "The parent manifold may not embed the opaque transformation.",
        )
    if fields.get("child_public_pointer") is not None:
        return _reject(
            REJECT_CHILD_PUBLIC_POINTER_IN_OPAQUE_SEVERANCE,
            "Opaque severance may not include a child public pointer in the parent witness.",
        )
    if fields.get("reversible_mapping_stored") is not False:
        return _reject(
            REJECT_REVERSIBLE_PARENT_MAPPING_IN_PHASE_INVERTED_RECORD,
            "Opaque severance may not store a reversible parent mapping.",
        )
    if fields.get("hidden_parent_pointer_stored") is not False:
        return _reject(
            REJECT_HIDDEN_PARENT_POINTER_IN_PHASE_INVERTED_RECORD,
            "Opaque severance may not store a hidden parent pointer.",
        )
    if fields.get("parent_unique_history_exported") is not False:
        return _reject(
            REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM,
            "Parent unique history cannot be exported into the phase-inverted privacy domain.",
        )
    return {
        "schema": "HHS_GENESIS_SEVERANCE_BOUNDARY_FIELD_VALIDATION_V1",
        "ok": True,
        "status": "BOUNDARY_FIELDS_VALID",
        "field_count": len(CANONICAL_BOUNDARY_FIELD_ORDER),
        "field_order": list(CANONICAL_BOUNDARY_FIELD_ORDER),
    }


def make_phase_inversion_severance_witness(
    *,
    parent_record: Any = None,
    new_genesis_seed: Any = None,
    parent_record_commitment: Optional[str] = None,
    new_genesis_seed_commitment: Optional[str] = None,
    severance_reason: str = "lawful opaque/privacy phase inversion",
    parent_commitment_policy: str = "sealed_private_commitment",
    retained_semantic_constraints: Optional[Sequence[str]] = None,
    discarded_identity_fields: Optional[Sequence[str]] = None,
    root_marker_declared: str = DEFAULT_ROOT_MARKER,
) -> Dict[str, Any]:
    """Create a lawful parent-manifold severance witness.

    The parent record and new Genesis seed may be supplied as raw values for
    commitment generation.  Raw values are never copied into the witness.  The
    witness stores only Hash72/u^72 commitments and canonical boundary fields.
    """

    if parent_record_commitment is None:
        if parent_record is None:
            raise ValueError("parent_record or parent_record_commitment is required")
        parent_record_commitment = commit_value(parent_record, label="hhs_parent_record_commitment_v1")
    if new_genesis_seed_commitment is None:
        if new_genesis_seed is None:
            raise ValueError("new_genesis_seed or new_genesis_seed_commitment is required")
        new_genesis_seed_commitment = commit_value(new_genesis_seed, label="hhs_new_genesis_seed_commitment_v1")

    fields = canonical_boundary_fields(
        parent_record_commitment=parent_record_commitment,
        new_genesis_seed_commitment=new_genesis_seed_commitment,
        severance_reason=severance_reason,
        parent_commitment_policy=parent_commitment_policy,
        retained_semantic_constraints=retained_semantic_constraints,
        discarded_identity_fields=discarded_identity_fields,
        root_marker_declared=root_marker_declared,
    )
    validation = validate_boundary_fields(fields)
    if not validation.get("ok"):
        return validation

    kernel = make_hash72_kernel_witness("HHS_PHASE_INVERSION_SEVERANCE_BOUNDARY_V1", fields, width=72).to_dict()
    boundary_hash72 = kernel["digest"]
    ledger = append_payload(
        "PHASE_INVERSION_SEVERANCE_WITNESS",
        "hhs_genesis_severance_protocol_v1.make_phase_inversion_severance_witness",
        {
            "schema": BOUNDARY_WITNESS_SCHEMA,
            "boundary_witness_hash72": boundary_hash72,
            "canonical_boundary_fields": fields,
            "kernel_digest72": boundary_hash72,
        },
    )
    witness = PhaseInversionSeveranceWitness(
        **fields,
        canonical_boundary_fields=copy.deepcopy(fields),
        boundary_witness_hash72=boundary_hash72,
        boundary_kernel_witness=kernel,
        unified_ledger={
            "entry_count": ledger.get("entry_count"),
            "tip_hash72": ledger.get("tip_hash72"),
            "ledger_hash72": ledger.get("ledger_hash72"),
            "verified": True,
        },
    ).to_dict()
    witness["validation"] = validation
    return witness


def validate_phase_inversion_severance_witness(witness: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate a built severance witness and recompute its boundary hash."""

    for forbidden in FORBIDDEN_PARENT_MANIFOLD_FIELDS:
        if forbidden in witness:
            return _reject(
                REJECT_OPAQUE_TRANSFORM_EMBEDDED_IN_IMMUTABLE_TRACE,
                f"Forbidden parent-manifold field present: {forbidden}",
                details={"forbidden_field": forbidden},
            )
    fields = witness.get("canonical_boundary_fields") or {key: witness.get(key) for key in CANONICAL_BOUNDARY_FIELD_ORDER}
    validation = validate_boundary_fields(fields)
    if not validation.get("ok"):
        return validation
    expected = make_hash72_kernel_witness("HHS_PHASE_INVERSION_SEVERANCE_BOUNDARY_V1", fields, width=72).digest
    actual = witness.get("boundary_witness_hash72")
    if actual != expected:
        return _reject(
            "REJECT_BOUNDARY_WITNESS_HASH_MISMATCH",
            "Boundary witness hash does not match canonical boundary fields.",
            details={"expected": expected, "actual": actual},
        )
    return {
        "schema": "HHS_PHASE_INVERSION_SEVERANCE_WITNESS_VALIDATION_V1",
        "ok": True,
        "status": "GENESIS_SEVERANCE_WITNESS_VALID",
        "boundary_witness_hash72": expected,
        "field_count": len(CANONICAL_BOUNDARY_FIELD_ORDER),
        "field_order": list(CANONICAL_BOUNDARY_FIELD_ORDER),
    }


def genesis_severance_protocol_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    parent = {
        "schema": "HHS_PARENT_RECORD_SAMPLE_V1",
        "phase": WITNESSED_CONTINUITY,
        "payload_commitment": "sample-parent-payload",
    }
    seed = {
        "schema": "HHS_NEW_GENESIS_SEED_SAMPLE_V1",
        "seed_material_commitment": "sample-seed-material",
        "exact_epoch_marker": DEFAULT_ROOT_MARKER,
    }
    witness = make_phase_inversion_severance_witness(parent_record=parent, new_genesis_seed=seed)
    validation = validate_phase_inversion_severance_witness(witness)
    tampered_fields = copy.deepcopy(witness["canonical_boundary_fields"])
    tampered_fields["parent_trace_continued"] = True
    tampered_validation = validate_boundary_fields(tampered_fields)
    ledger_status = witness.get("unified_ledger", {})
    ok = bool(
        validation.get("ok")
        and tampered_validation.get("status") == REJECT_PRIVACY_RECORD_WITH_PARENT_CONTINUITY_CLAIM
        and witness.get("parent_trace_continued") is False
        and witness.get("opaque_transform_embedded") is False
        and ledger_status.get("verified") is True
    )
    return {
        "schema": "HHS_GENESIS_SEVERANCE_PROTOCOL_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "canonical_boundary_field_count": len(CANONICAL_BOUNDARY_FIELD_ORDER),
        "canonical_boundary_fields": list(CANONICAL_BOUNDARY_FIELD_ORDER),
        "witness": witness,
        "validation": validation,
        "tampered_parent_trace_validation": tampered_validation,
        "ledger_verified": bool(ledger_status.get("verified")),
        "doctrine": "Opaque privacy requires topological phase inversion: a new Genesis seed outside the parent immutable manifold.",
    }


if __name__ == "__main__":
    print(json.dumps(genesis_severance_protocol_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
