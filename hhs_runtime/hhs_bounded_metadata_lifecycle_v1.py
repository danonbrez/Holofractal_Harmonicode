"""
HHS Bounded Metadata Lifecycle v1
=================================

Pass 043 lifecycle authority for expanded validation metadata. This module
coordinates validation, compaction, persistence as compact roots, and decay of
expanded states that do not propagate to a new Hash72/u^72 state.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_validation_residue_compactor_v1 import (
    compact_validation_residue,
    evict_expanded_metadata,
    verify_residue_reconstruction,
)
from hhs_runtime.hhs_expanded_state_decay_lifecycle_v1 import (
    register_expanded_state,
    mark_state_propagated,
    self_delete_expired_expanded_state,
)

VERSION = "PASS_043_KERNEL_DERIVED_RUNTIME_AUTOCOMPOSITION_V1"
LIFECYCLE_SCHEMA = "HHS_BOUNDED_METADATA_LIFECYCLE_V1"

VALID_STATES = [
    "EXPANDED_FOR_VALIDATION",
    "VALIDATED",
    "COMPACTED_TO_RESIDUE",
    "PERSISTED_AS_ROOT",
    "EVICTED_AFTER_COMPACTION",
    "RECONSTRUCTABLE_ON_DEMAND",
    "PROPAGATED_TO_HASH_STATE",
    "EXPANDED_STATE_SELF_DELETED",
]

REJECT_UNBOUNDED_METADATA_PERSISTENCE = "REJECT_UNBOUNDED_METADATA_PERSISTENCE"
REJECT_VALIDATED_METADATA_DUPLICATION = "REJECT_VALIDATED_METADATA_DUPLICATION"
REJECT_RESIDUE_WITHOUT_RECONSTRUCTION_RECIPE = "REJECT_RESIDUE_WITHOUT_RECONSTRUCTION_RECIPE"
REJECT_EXPANDED_STATE_WITHOUT_DECAY_POLICY = "REJECT_EXPANDED_STATE_WITHOUT_DECAY_POLICY"
REJECT_EXPANDED_STATE_PERSISTED_AFTER_DECAY = "REJECT_EXPANDED_STATE_PERSISTED_AFTER_DECAY"


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def transition_expanded_to_validated(expanded_state: Mapping[str, Any], *, expanded_state_id: str, source_surface_id: str, tick: int, decay_window_ticks: int = 3) -> Dict[str, Any]:
    handle = register_expanded_state(
        expanded_state_id,
        expanded_state,
        source_surface_id=source_surface_id,
        created_at_tick=tick,
        decay_window_ticks=decay_window_ticks,
    )
    return {
        "schema": "HHS_METADATA_LIFECYCLE_VALIDATED_STATE_V1",
        "version": VERSION,
        "lifecycle_state": "VALIDATED",
        "expanded_state_handle": handle,
        "expanded_state_root_hash72": handle.get("expanded_payload_root_hash72"),
        "validation_tick": int(tick),
    }


def transition_validated_to_compacted(validated_state: Mapping[str, Any], expanded_state: Mapping[str, Any]) -> Dict[str, Any]:
    handle = validated_state.get("expanded_state_handle") or {}
    residue = compact_validation_residue(
        expanded_state,
        source_id=str(handle.get("expanded_state_id", "expanded:unknown")),
    )
    residue = evict_expanded_metadata(residue)
    reconstruction = verify_residue_reconstruction(residue, expanded_state)
    return {
        "schema": "HHS_METADATA_LIFECYCLE_COMPACTED_STATE_V1",
        "version": VERSION,
        "lifecycle_state": "COMPACTED_TO_RESIDUE",
        "expanded_state_handle": handle,
        "compact_residue": residue,
        "reconstruction_decision": reconstruction,
    }


def persist_compact_root(compacted_state: Mapping[str, Any]) -> Dict[str, Any]:
    residue = compacted_state.get("compact_residue") or {}
    record = {
        "schema": "HHS_COMPACT_ROOT_PERSISTENCE_RECORD_V1",
        "version": VERSION,
        "lifecycle_state": "PERSISTED_AS_ROOT",
        "residue_root_hash72": residue.get("residue_root_hash72"),
        "recipe_hash72": (residue.get("reconstruction_recipe") or {}).get("recipe_hash72"),
        "expanded_payload_retained": bool(residue.get("expanded_payload_retained")),
        "persistence_mode": "ROOT_PLUS_RECONSTRUCTION_RECIPE_ONLY",
    }
    record["persistence_hash72"] = _hash72("HHS_COMPACT_ROOT_PERSISTENCE_RECORD_V1", record)
    return record


def propagate_or_decay(validated_state: Mapping[str, Any], *, propagated_hash72: str | None, current_tick: int) -> Dict[str, Any]:
    handle = validated_state.get("expanded_state_handle") or {}
    if propagated_hash72:
        return {
            "schema": "HHS_METADATA_LIFECYCLE_PROPAGATION_DECISION_V1",
            "version": VERSION,
            "status": "PROPAGATED_TO_HASH_STATE",
            "handle": mark_state_propagated(handle, propagated_hash72, tick=current_tick),
        }
    return self_delete_expired_expanded_state(handle, current_tick=current_tick)


def validate_metadata_lifecycle(record: Mapping[str, Any]) -> Dict[str, Any]:
    reasons = []
    state = str(record.get("lifecycle_state", ""))
    if state not in VALID_STATES:
        reasons.append("REJECT_UNKNOWN_METADATA_LIFECYCLE_STATE")
    if record.get("expanded_payload_retained") and state in {"PERSISTED_AS_ROOT", "EVICTED_AFTER_COMPACTION", "RECONSTRUCTABLE_ON_DEMAND"}:
        reasons.append(REJECT_UNBOUNDED_METADATA_PERSISTENCE)
    if state == "COMPACTED_TO_RESIDUE":
        residue = record.get("compact_residue") or {}
        if residue.get("expanded_payload_retained"):
            reasons.append(REJECT_VALIDATED_METADATA_DUPLICATION)
        if not residue.get("reconstruction_recipe"):
            reasons.append(REJECT_RESIDUE_WITHOUT_RECONSTRUCTION_RECIPE)
    if state == "EXPANDED_STATE_SELF_DELETED" and record.get("expanded_payload_retained"):
        reasons.append(REJECT_EXPANDED_STATE_PERSISTED_AFTER_DECAY)
    return {
        "schema": "HHS_METADATA_LIFECYCLE_DECISION_V1",
        "version": VERSION,
        "ok": not reasons,
        "status": "ADMIT_BOUNDED_METADATA_LIFECYCLE" if not reasons else "REJECT_INVALID_METADATA_LIFECYCLE",
        "lifecycle_state": state,
        "reasons": reasons,
    }


def bounded_metadata_lifecycle_self_test() -> Dict[str, Any]:
    expanded = {
        "schema": "HHS_TEST_EXPANDED_CONFORMANCE_FRAGMENT_V1",
        "surface_count": 2,
        "edges": [{"a": 1}, {"b": 2}],
        "surfaces": [{"surface_id": "service:test"}],
    }
    validated = transition_expanded_to_validated(
        expanded,
        expanded_state_id="expanded:pass043:lifecycle",
        source_surface_id="service:bounded_metadata_lifecycle.self_test",
        tick=100,
        decay_window_ticks=3,
    )
    compacted = transition_validated_to_compacted(validated, expanded)
    persisted = persist_compact_root(compacted)
    prop = propagate_or_decay(validated, propagated_hash72=None, current_tick=103)
    decisions = [
        validate_metadata_lifecycle(validated),
        validate_metadata_lifecycle(compacted),
        validate_metadata_lifecycle(persisted),
        validate_metadata_lifecycle({"lifecycle_state": "EXPANDED_STATE_SELF_DELETED", "expanded_payload_retained": False}),
    ]
    return {
        "schema": "HHS_BOUNDED_METADATA_LIFECYCLE_SELF_TEST_V1",
        "version": VERSION,
        "ok": all(d.get("ok") for d in decisions) and prop.get("ok"),
        "validated": validated,
        "compacted": compacted,
        "persisted": persisted,
        "decay_or_propagation": prop,
        "decisions": decisions,
    }


if __name__ == "__main__":
    print(bounded_metadata_lifecycle_self_test())
