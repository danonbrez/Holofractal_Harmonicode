"""
HHS Expanded State Decay Lifecycle v1
=====================================

Pass 043 metadata-metabolism rule: every expanded state is transient. It must
propagate into a new witnessed Hash72/u^72 state within its decay window or the
expanded payload self-deletes, leaving only a compact decay witness.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Optional

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness

VERSION = "PASS_043_KERNEL_DERIVED_RUNTIME_AUTOCOMPOSITION_V1"
DECAY_RECORD_SCHEMA = "HHS_EXPANDED_STATE_DECAY_RECORD_V1"

REJECT_EXPIRED_EXPANDED_STATE = "REJECT_EXPIRED_EXPANDED_STATE"
REJECT_EXPANDED_STATE_WITHOUT_DECAY_POLICY = "REJECT_EXPANDED_STATE_WITHOUT_DECAY_POLICY"
REJECT_EXPANDED_STATE_PERSISTED_AFTER_DECAY = "REJECT_EXPANDED_STATE_PERSISTED_AFTER_DECAY"
REJECT_DECAY_WITHOUT_WITNESS = "REJECT_DECAY_WITHOUT_WITNESS"
REJECT_STALLED_STATE_WITHOUT_PROPAGATION_OR_DELETION = "REJECT_STALLED_STATE_WITHOUT_PROPAGATION_OR_DELETION"
REJECT_UNBOUNDED_EXPANDED_STATE_LIFETIME = "REJECT_UNBOUNDED_EXPANDED_STATE_LIFETIME"

ACTIVE_STATES = {"EXPANDED_FOR_VALIDATION", "VALIDATED", "VALIDATION_STALLED"}
TERMINAL_STATES = {"PROPAGATED_TO_HASH_STATE", "EXPANDED_STATE_SELF_DELETED"}


@dataclass(frozen=True)
class ExpandedStateHandle:
    schema: str
    version: str
    expanded_state_id: str
    source_surface_id: str
    created_at_tick: int
    decay_window_ticks: int
    status: str
    expanded_payload_root_hash72: str
    propagated: bool = False
    propagated_hash72: Optional[str] = None
    deletion_tick: Optional[int] = None
    decay_root_hash72: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def register_expanded_state(
    expanded_state_id: str,
    expanded_payload: Mapping[str, Any],
    *,
    source_surface_id: str,
    created_at_tick: int,
    decay_window_ticks: int,
) -> Dict[str, Any]:
    if decay_window_ticks <= 0:
        return {
            "schema": "HHS_EXPANDED_STATE_DECAY_DECISION_V1",
            "version": VERSION,
            "ok": False,
            "status": REJECT_EXPANDED_STATE_WITHOUT_DECAY_POLICY,
            "reason": REJECT_UNBOUNDED_EXPANDED_STATE_LIFETIME,
        }
    handle = ExpandedStateHandle(
        schema="HHS_EXPANDED_STATE_HANDLE_V1",
        version=VERSION,
        expanded_state_id=str(expanded_state_id),
        source_surface_id=str(source_surface_id),
        created_at_tick=int(created_at_tick),
        decay_window_ticks=int(decay_window_ticks),
        status="EXPANDED_FOR_VALIDATION",
        expanded_payload_root_hash72=_hash72("HHS_EXPANDED_STATE_PAYLOAD_V1", expanded_payload),
    ).to_dict()
    handle["handle_hash72"] = _hash72("HHS_EXPANDED_STATE_HANDLE_V1", handle)
    return handle


def mark_state_propagated(handle: Mapping[str, Any], propagated_hash72: str, *, tick: Optional[int] = None) -> Dict[str, Any]:
    updated = dict(handle)
    updated["propagated"] = True
    updated["propagated_hash72"] = str(propagated_hash72)
    updated["status"] = "PROPAGATED_TO_HASH_STATE"
    updated["propagation_tick"] = int(tick if tick is not None else handle.get("created_at_tick", 0))
    updated["propagation_witness_hash72"] = _hash72("HHS_EXPANDED_STATE_PROPAGATION_V1", updated)
    return updated


def evaluate_decay_window(handle: Mapping[str, Any], *, current_tick: int) -> Dict[str, Any]:
    if handle.get("status") in TERMINAL_STATES:
        return {
            "schema": "HHS_EXPANDED_STATE_DECAY_WINDOW_DECISION_V1",
            "version": VERSION,
            "expired": False,
            "terminal": True,
            "status": handle.get("status"),
            "remaining_ticks": 0,
        }
    created = int(handle.get("created_at_tick", 0))
    window = int(handle.get("decay_window_ticks", 0))
    if window <= 0:
        return {
            "schema": "HHS_EXPANDED_STATE_DECAY_WINDOW_DECISION_V1",
            "version": VERSION,
            "expired": True,
            "terminal": False,
            "status": REJECT_EXPANDED_STATE_WITHOUT_DECAY_POLICY,
            "remaining_ticks": 0,
        }
    age = int(current_tick) - created
    expired = age >= window
    return {
        "schema": "HHS_EXPANDED_STATE_DECAY_WINDOW_DECISION_V1",
        "version": VERSION,
        "expired": expired,
        "terminal": False,
        "status": "DECAY_WINDOW_EXPIRED" if expired else "DECAY_WINDOW_OPEN",
        "age_ticks": age,
        "remaining_ticks": max(0, window - age),
    }


def build_decay_witness(handle: Mapping[str, Any], *, reason: str, current_tick: int) -> Dict[str, Any]:
    retained = {
        "decay_root_hash72": _hash72("HHS_EXPANDED_STATE_DECAY_ROOT_V1", {
            "expanded_state_id": handle.get("expanded_state_id"),
            "source_surface_id": handle.get("source_surface_id"),
            "expanded_payload_root_hash72": handle.get("expanded_payload_root_hash72"),
            "reason": reason,
            "current_tick": int(current_tick),
        }),
        "reason": reason,
        "reconstruction_available": False,
    }
    record = {
        "schema": DECAY_RECORD_SCHEMA,
        "version": VERSION,
        "expanded_state_id": handle.get("expanded_state_id"),
        "source_surface_id": handle.get("source_surface_id"),
        "created_at_tick": handle.get("created_at_tick"),
        "decay_window_ticks": handle.get("decay_window_ticks"),
        "propagated": bool(handle.get("propagated")),
        "propagated_hash72": handle.get("propagated_hash72"),
        "decay_status": "EXPANDED_STATE_SELF_DELETED",
        "deleted_at_tick": int(current_tick),
        "retained_residue": retained,
        "expanded_payload_retained": False,
        "kernel_authority": "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1",
    }
    record["decay_witness_hash72"] = _hash72(DECAY_RECORD_SCHEMA, record)
    return record


def self_delete_expired_expanded_state(handle: Mapping[str, Any], *, current_tick: int) -> Dict[str, Any]:
    decision = evaluate_decay_window(handle, current_tick=current_tick)
    if not decision.get("expired"):
        return {
            "schema": "HHS_EXPANDED_STATE_SELF_DELETE_DECISION_V1",
            "version": VERSION,
            "ok": False,
            "status": "DECAY_WINDOW_NOT_EXPIRED",
            "decision": decision,
            "handle": dict(handle),
        }
    witness = build_decay_witness(
        handle,
        reason="DECAY_WINDOW_EXPIRED_WITHOUT_PROPAGATION",
        current_tick=current_tick,
    )
    return {
        "schema": "HHS_EXPANDED_STATE_SELF_DELETE_DECISION_V1",
        "version": VERSION,
        "ok": True,
        "status": "EXPANDED_STATE_SELF_DELETED",
        "decision": decision,
        "decay_witness": witness,
        "expanded_payload": None,
    }


def verify_no_expired_expanded_states(handles: list[Mapping[str, Any]], *, current_tick: int) -> Dict[str, Any]:
    expired = []
    invalid = []
    for handle in handles:
        decision = evaluate_decay_window(handle, current_tick=current_tick)
        if decision.get("expired") and handle.get("status") != "EXPANDED_STATE_SELF_DELETED":
            expired.append(handle.get("expanded_state_id"))
        if int(handle.get("decay_window_ticks", 0)) <= 0:
            invalid.append(handle.get("expanded_state_id"))
    reasons = []
    if expired:
        reasons.append(REJECT_STALLED_STATE_WITHOUT_PROPAGATION_OR_DELETION)
    if invalid:
        reasons.append(REJECT_EXPANDED_STATE_WITHOUT_DECAY_POLICY)
    return {
        "schema": "HHS_EXPANDED_STATE_DECAY_AUDIT_V1",
        "version": VERSION,
        "ok": not reasons,
        "status": "ADMIT_NO_EXPIRED_EXPANDED_STATES" if not reasons else "REJECT_EXPIRED_EXPANDED_STATE_SET",
        "expired_expanded_states": expired,
        "invalid_decay_policy_states": invalid,
        "reasons": reasons,
    }


def expanded_state_decay_lifecycle_self_test() -> Dict[str, Any]:
    expanded = {"schema": "HHS_TEST_EXPANDED_STATE_V1", "value": "temporary-validation-fragment"}
    handle = register_expanded_state(
        "expanded:test:pass043",
        expanded,
        source_surface_id="service:kernel_runtime_autocomposer.self_test",
        created_at_tick=10,
        decay_window_ticks=3,
    )
    propagated = mark_state_propagated(handle, _hash72("HHS_NEW_HASH_STATE", {"state": 1}), tick=12)
    expired_decision = self_delete_expired_expanded_state(handle, current_tick=13)
    audit = verify_no_expired_expanded_states([propagated], current_tick=20)
    return {
        "schema": "HHS_EXPANDED_STATE_DECAY_LIFECYCLE_SELF_TEST_V1",
        "version": VERSION,
        "ok": propagated.get("status") == "PROPAGATED_TO_HASH_STATE" and expired_decision.get("ok") and audit.get("ok"),
        "registered": handle,
        "propagated": propagated,
        "expired_self_delete": expired_decision,
        "audit": audit,
    }


if __name__ == "__main__":
    print(expanded_state_decay_lifecycle_self_test())
