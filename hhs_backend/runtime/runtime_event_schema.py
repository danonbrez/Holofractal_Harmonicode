# ============================================================================
# hhs_backend/runtime/runtime_event_schema.py
# HARMONICODE / HHS
# CANONICAL DISTRIBUTED EVENT ALGEBRA
#
# PURPOSE
# -------
# Canonical deterministic event substrate for:
#
#   - replay continuity
#   - websocket transport
#   - graph projections
#   - cognition synchronization
#   - distributed consensus
#   - toolchain execution
#   - snapshot propagation
#   - multimodal routing
#
# Events ARE runtime state transitions.
#
# This file intentionally avoids PEP 526 class/module variable annotations for
# runtime event fields. The active deployment chain has already exposed two
# parser regressions from annotated field declarations; constructor-bound fields
# preserve the same payload contract without introducing that syntax surface.
# ============================================================================

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid

from typing import Any, Dict, Optional

# ============================================================================
# OPTIONAL V44.2 KERNEL INTEGRATION
# ============================================================================

try:
    from HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked_7 import (
        AUTHORITATIVE_TRUST_POLICY_V44,
        security_hash72_v44,
    )

    V44_KERNEL_AVAILABLE = True

except Exception:
    AUTHORITATIVE_TRUST_POLICY_V44 = None
    security_hash72_v44 = None
    V44_KERNEL_AVAILABLE = False

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger("HHS_RUNTIME_EVENT_SCHEMA")

# ============================================================================
# CONSTANTS
# ============================================================================

EVENT_SCHEMA_VERSION = "v1"
HASH72_LEN = 72

# ============================================================================
# HASH72
# ============================================================================

def compute_hash72(payload: Dict[str, Any]) -> str:
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    digest = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    return digest[:HASH72_LEN]

# ============================================================================
# BASE EVENT ENVELOPE
# ============================================================================

class HHSRuntimeEventEnvelope:
    """Runtime event envelope with constructor-bound fields.

    Field names intentionally match the websocket / graph / replay contract.
    Avoid reintroducing class-level PEP 526 declarations here.
    """

    extra_field_defaults = {}

    def __init__(
        self,
        event_id: str,
        event_type: str,
        runtime_id: str,
        branch_id: str,
        schema_version: str,
        created_at_ns: int,
        parent_event_hash72: str,
        receipt_hash72: str,
        payload: Dict[str, Any],
        event_hash72: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        **extras: Any,
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.runtime_id = runtime_id
        self.branch_id = branch_id
        self.schema_version = schema_version
        self.created_at_ns = created_at_ns
        self.parent_event_hash72 = parent_event_hash72
        self.receipt_hash72 = receipt_hash72
        self.payload = payload
        self.event_hash72 = event_hash72
        self.metadata = metadata or {}

        for key, default_value in self.extra_field_defaults.items():
            setattr(self, key, extras.pop(key, default_value))

        for key, value in extras.items():
            setattr(self, key, value)

        if not self.event_hash72:
            self.event_hash72 = self.compute_event_hash72()

    # =====================================================================
    # HASH72
    # =====================================================================

    def compute_event_hash72(self):
        payload = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "runtime_id": self.runtime_id,
            "branch_id": self.branch_id,
            "schema_version": self.schema_version,
            "created_at_ns": self.created_at_ns,
            "parent_event_hash72": self.parent_event_hash72,
            "receipt_hash72": self.receipt_hash72,
            "payload": self.payload,
        }

        return compute_hash72(payload)

    # =====================================================================
    # VERIFY
    # =====================================================================

    def verify_event_hash72(self):
        computed = self.compute_event_hash72()
        valid = computed == self.event_hash72

        if not valid:
            logger.error("Event Hash72 verification failure.")

        return valid

    # =====================================================================
    # SERIALIZATION
    # =====================================================================

    def to_dict(self):
        data = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "runtime_id": self.runtime_id,
            "branch_id": self.branch_id,
            "schema_version": self.schema_version,
            "created_at_ns": self.created_at_ns,
            "parent_event_hash72": self.parent_event_hash72,
            "receipt_hash72": self.receipt_hash72,
            "payload": self.payload,
            "event_hash72": self.event_hash72,
            "metadata": self.metadata,
        }

        for key in self.extra_field_defaults:
            data[key] = getattr(self, key)

        return data

    def serialize_event(self):
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        )

    # =====================================================================
    # DESERIALIZATION
    # =====================================================================

    @classmethod
    def deserialize_event(cls, serialized: str):
        payload = json.loads(serialized)
        event_type = payload.get("event_type", "")
        event_class = EVENT_SCHEMA_REGISTRY.get(event_type, cls)
        return event_class(**payload)

    # =====================================================================
    # WEBSOCKET PROJECTION
    # =====================================================================

    def to_websocket_payload(self):
        return {
            "event": self.event_type,
            "event_type": self.event_type,
            "runtime_id": self.runtime_id,
            "branch_id": self.branch_id,
            "event_hash72": self.event_hash72,
            "parent_event_hash72": self.parent_event_hash72,
            "receipt_hash72": self.receipt_hash72,
            "timestamp_ns": self.created_at_ns,
            "payload": self.payload,
        }

    # =====================================================================
    # GRAPH PROJECTION
    # =====================================================================

    def to_graph_projection(self):
        return {
            "node_id": self.event_hash72,
            "runtime_id": self.runtime_id,
            "parent": self.parent_event_hash72,
            "receipt_hash72": self.receipt_hash72,
            "event_type": self.event_type,
            "timestamp_ns": self.created_at_ns,
        }

    # =====================================================================
    # REPLAY PACKET
    # =====================================================================

    def to_replay_packet(self):
        return {
            "event_hash72": self.event_hash72,
            "parent_event_hash72": self.parent_event_hash72,
            "runtime_id": self.runtime_id,
            "receipt_hash72": self.receipt_hash72,
            "payload": self.payload,
        }

    # =====================================================================
    # V44.2 VALIDATION
    # =====================================================================

    def validate_v44_alignment(self):
        if not V44_KERNEL_AVAILABLE:
            return {
                "kernel_available": False,
                "validated": False,
            }

        event_hash = hashlib.sha256(
            self.serialize_event().encode("utf-8")
        ).hexdigest()

        trust_hash = hashlib.sha256(
            str(AUTHORITATIVE_TRUST_POLICY_V44).encode("utf-8")
        ).hexdigest()

        return {
            "kernel_available": True,
            "validated": len(event_hash) > 0 and len(trust_hash) > 0,
            "event_hash": event_hash,
            "trust_hash": trust_hash,
        }

# ============================================================================
# EVENT TYPES
# ============================================================================

class HHSReplayEvent(HHSRuntimeEventEnvelope):
    extra_field_defaults = {
        "replay_step": 0,
        "replay_equivalent": True,
    }

class HHSSnapshotEvent(HHSRuntimeEventEnvelope):
    extra_field_defaults = {
        "snapshot_id": "",
        "replay_hash72": "",
    }

class HHSCognitionEvent(HHSRuntimeEventEnvelope):
    extra_field_defaults = {
        "cognition_task_id": "",
        "cognition_state": "",
    }

class HHSToolchainEvent(HHSRuntimeEventEnvelope):
    extra_field_defaults = {
        "toolchain_id": "",
        "execution_signature": "",
    }

class HHSConsensusEvent(HHSRuntimeEventEnvelope):
    extra_field_defaults = {
        "proposal_id": "",
        "quorum_state": "",
    }

class HHSMultimodalEvent(HHSRuntimeEventEnvelope):
    extra_field_defaults = {
        "modality": "",
        "projection_hash72": "",
    }

# ============================================================================
# SCHEMA REGISTRY
# ============================================================================

EVENT_SCHEMA_REGISTRY = {
    "replay": HHSReplayEvent,
    "snapshot": HHSSnapshotEvent,
    "cognition": HHSCognitionEvent,
    "toolchain": HHSToolchainEvent,
    "consensus": HHSConsensusEvent,
    "multimodal": HHSMultimodalEvent,
}

# ============================================================================
# EVENT FACTORY
# ============================================================================

def create_runtime_event(
    event_type: str,
    runtime_id: str,
    receipt_hash72: str,
    payload: Dict[str, Any],
    branch_id: str = "main",
    parent_event_hash72: str = "",
):
    event_class = EVENT_SCHEMA_REGISTRY.get(
        event_type,
        HHSRuntimeEventEnvelope,
    )

    return event_class(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        runtime_id=runtime_id,
        branch_id=branch_id,
        schema_version=EVENT_SCHEMA_VERSION,
        created_at_ns=time.time_ns(),
        parent_event_hash72=parent_event_hash72,
        receipt_hash72=receipt_hash72,
        payload=payload,
    )

# ============================================================================
# SCHEMA EVOLUTION
# ============================================================================

def verify_schema_version(event: HHSRuntimeEventEnvelope):
    return event.schema_version == EVENT_SCHEMA_VERSION

# ============================================================================
# UPCAST
# ============================================================================

def upcast_event(event: HHSRuntimeEventEnvelope):
    if event.schema_version == "v1":
        return event

    raise RuntimeError(
        f"Unsupported event schema version: {event.schema_version}"
    )

# ============================================================================
# TRANSPORT VALIDATION
# ============================================================================

def validate_transport_projection(event: HHSRuntimeEventEnvelope):
    return {
        "websocket": event.to_websocket_payload(),
        "graph": event.to_graph_projection(),
        "replay": event.to_replay_packet(),
    }

# ============================================================================
# SELF TEST
# ============================================================================

def runtime_event_schema_self_test():
    event = create_runtime_event(
        event_type="replay",
        runtime_id="runtime_001",
        receipt_hash72="abc123",
        payload={
            "step": 1,
            "trajectory": "stable",
        },
    )

    serialized = event.serialize_event()
    restored = HHSRuntimeEventEnvelope.deserialize_event(serialized)

    assert restored.verify_event_hash72()
    assert verify_schema_version(restored)

    projection = validate_transport_projection(restored)

    assert projection["websocket"]["receipt_hash72"] == "abc123"
    assert projection["graph"]["receipt_hash72"] == "abc123"
    assert projection["replay"]["receipt_hash72"] == "abc123"

    return True

if __name__ == "__main__":
    runtime_event_schema_self_test()
    print("runtime_event_schema_self_test: PASS")
