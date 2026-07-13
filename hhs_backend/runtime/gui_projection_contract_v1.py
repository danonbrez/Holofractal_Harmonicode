"""
HHS Live GUI Projection Contract v1
===================================

Pass 046 binds the browser GUI to the four authoritative FastAPI websocket
channels.  The GUI is a projection layer only: every live runtime panel state
must be traceable to a kernel-originated websocket payload or a witnessed
projection of one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping

VERSION = "PASS_046_LIVE_GUI_WEBSOCKET_BINDING_V1"
SCHEMA = "HHS_LIVE_GUI_PROJECTION_CONTRACT_V1"
AUTHORITY = "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1"

CHANNEL_BINDINGS: Dict[str, Dict[str, str]] = {
    "/ws/runtime": {
        "panel": "Runtime panel",
        "event_type": "runtime",
        "state_lane": "lastRuntimeEvent",
    },
    "/ws/replay": {
        "panel": "Replay panel",
        "event_type": "replay",
        "state_lane": "lastReplayEvent",
    },
    "/ws/graph": {
        "panel": "Graph panel",
        "event_type": "graph",
        "state_lane": "lastGraphEvent",
    },
    "/ws/transport": {
        "panel": "Transport panel",
        "event_type": "transport",
        "state_lane": "lastTransportEvent",
    },
}

REQUIRED_LIVE_FIELDS = (
    "event_type",
    "channel",
    "sequence_id",
    "kernel_tick",
    "event_hash72",
    "receipt_hash72",
    "runtime_state_hash72",
    "authority",
    "payload",
)

REJECTION_CODES = {
    "synthetic": "REJECT_GUI_SYNTHETIC_RUNTIME_PACKET",
    "no_kernel_packet": "REJECT_GUI_STATE_WITHOUT_KERNEL_PACKET",
    "node_event": "REJECT_NODE_GENERATED_RUNTIME_EVENT",
    "no_receipt": "REJECT_WEBSOCKET_PACKET_WITHOUT_RECEIPT",
    "sequence_drift": "REJECT_CHANNEL_SEQUENCE_DRIFT",
    "stale_state": "REJECT_STALE_GUI_RUNTIME_STATE",
}


def list_gui_channel_bindings() -> Dict[str, Any]:
    return {
        "schema": "HHS_LIVE_GUI_CHANNEL_BINDINGS_V1",
        "version": VERSION,
        "authority": AUTHORITY,
        "bindings": CHANNEL_BINDINGS,
        "doctrine": "GUI_PROJECTION_ONLY_FASTAPI_IS_RUNTIME_AUTHORITY",
    }


def validate_gui_projection_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate that a websocket payload can drive a live GUI panel."""

    missing = [field for field in REQUIRED_LIVE_FIELDS if payload.get(field) in (None, "")]
    channel = str(payload.get("channel") or "")
    binding = CHANNEL_BINDINGS.get(channel)
    reasons = []
    if missing:
        reasons.append("missing_live_kernel_fields:" + ",".join(missing))
    if not binding:
        reasons.append("unknown_channel")
    elif payload.get("event_type") != binding["event_type"]:
        reasons.append("event_type_channel_mismatch")
    if payload.get("authority") != AUTHORITY:
        reasons.append("non_fastapi_kernel_authority")
    if payload.get("node_generated_runtime_event"):
        reasons.append("node_generated_runtime_event")

    status = "ADMIT_LIVE_GUI_KERNEL_PROJECTION" if not reasons else "REJECT_GUI_PROJECTION_PACKET"
    rejection_code = None
    if reasons:
        if "node_generated_runtime_event" in reasons:
            rejection_code = REJECTION_CODES["node_event"]
        elif "receipt_hash72" in ",".join(missing):
            rejection_code = REJECTION_CODES["no_receipt"]
        else:
            rejection_code = REJECTION_CODES["no_kernel_packet"]

    return {
        "schema": "HHS_LIVE_GUI_PROJECTION_DECISION_V1",
        "version": VERSION,
        "ok": not reasons,
        "status": status,
        "rejection_code": rejection_code,
        "channel": channel,
        "event_type": payload.get("event_type"),
        "panel": binding.get("panel") if binding else None,
        "reasons": reasons,
        "event_hash72": payload.get("event_hash72"),
        "receipt_hash72": payload.get("receipt_hash72"),
        "runtime_state_hash72": payload.get("runtime_state_hash72"),
    }


def build_gui_projection_status(channel_payloads: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    decisions = [validate_gui_projection_payload(payload) for payload in channel_payloads]
    return {
        "schema": "HHS_LIVE_GUI_PROJECTION_STATUS_V1",
        "version": VERSION,
        "ok": all(decision["ok"] for decision in decisions) and len(decisions) == 4,
        "channel_count": len(decisions),
        "admitted_count": sum(1 for decision in decisions if decision["ok"]),
        "rejected_count": sum(1 for decision in decisions if not decision["ok"]),
        "decisions": decisions,
        "bindings": CHANNEL_BINDINGS,
    }


def live_gui_projection_contract_self_test() -> Dict[str, Any]:
    sample_payloads = []
    for sequence, channel in enumerate(CHANNEL_BINDINGS, start=1):
        event_type = CHANNEL_BINDINGS[channel]["event_type"]
        sample_payloads.append({
            "event_type": event_type,
            "channel": channel,
            "sequence_id": sequence,
            "kernel_tick": sequence,
            "event_hash72": "e" * 72,
            "receipt_hash72": "r" * 72,
            "runtime_state_hash72": "s" * 72,
            "authority": AUTHORITY,
            "payload": {"sample": True},
        })
    status = build_gui_projection_status(sample_payloads)
    rejected = validate_gui_projection_payload({
        "event_type": "runtime",
        "channel": "/ws/runtime",
        "payload": {"synthetic": True},
    })
    return {
        "schema": "HHS_LIVE_GUI_PROJECTION_CONTRACT_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(status["ok"] and not rejected["ok"]),
        "status": status,
        "rejected": rejected,
        "rejection_codes": REJECTION_CODES,
    }


if __name__ == "__main__":
    print(live_gui_projection_contract_self_test())
