# ============================================================================
# hhs_backend/runtime/runtime_event_schema.py
# ============================================================================
#
# Canonical Runtime Event Algebra
#
# This module is the authoritative runtime transport schema
# for:
#
#   - websocket transport
#   - replay continuity
#   - graph projection
#   - runtime synchronization
#   - receipt lineage
#   - snapshot replay
#
# IMPORTANT
# ----------------------------------------------------------------------------
#
# DO NOT reintroduce PEP-526 runtime field declarations.
#
# Runtime event fields must remain constructor-bound
# to prevent parser/runtime divergence across:
#
#   - FastAPI
#   - uvicorn reload
#   - websocket serialization
#   - runtime replay projection
#
# ============================================================================

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid

from typing import Any
from typing import Dict
from typing import Optional

# ============================================================================
# Logging
# ============================================================================

logger = logging.getLogger(
    "HHS_RUNTIME_EVENT_SCHEMA"
)

# ============================================================================
# Constants
# ============================================================================

EVENT_SCHEMA_VERSION = "v1"

HASH72_LENGTH = 72

# ============================================================================
# Hash72
# ============================================================================

def compute_hash72(
    payload: Dict[str, Any]
) -> str:

    serialized = json.dumps(

        payload,

        sort_keys=True,

        separators=(",", ":"),

        ensure_ascii=False
    )

    digest = hashlib.sha256(

        serialized.encode("utf-8")

    ).hexdigest()

    return digest[:HASH72_LENGTH]

# ============================================================================
# Runtime Event Envelope
# ============================================================================

class HHSRuntimeEventEnvelope:

    """
    Canonical runtime event envelope.

    Constructor-bound fields intentionally avoid
    PEP-526 parser surfaces.
    """

    extra_field_defaults = {}

    # =====================================================================
    # Constructor
    # =====================================================================

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

        **extras: Any

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

        # -------------------------------------------------------------
        # Extended Fields
        # -------------------------------------------------------------

        for key, default_value in (

            self.extra_field_defaults.items()

        ):

            setattr(

                self,

                key,

                extras.pop(

                    key,

                    default_value
                )
            )

        # -------------------------------------------------------------
        # Remaining Extras
        # -------------------------------------------------------------

        for key, value in extras.items():

            setattr(

                self,

                key,

                value
            )

        # -------------------------------------------------------------
        # Hash72
        # -------------------------------------------------------------

        if not self.event_hash72:

            self.event_hash72 = (

                self.compute_event_hash72()
            )

    # =====================================================================
    # Hash72
    # =====================================================================

    def compute_event_hash72(
        self
    ) -> str:

        payload = {

            "event_id":
                self.event_id,

            "event_type":
                self.event_type,

            "runtime_id":
                self.runtime_id,

            "branch_id":
                self.branch_id,

            "schema_version":
                self.schema_version,

            "created_at_ns":
                self.created_at_ns,

            "parent_event_hash72":
                self.parent_event_hash72,

            "receipt_hash72":
                self.receipt_hash72,

            "payload":
                self.payload
        }

        return compute_hash72(
            payload
        )

    # =====================================================================
    # Verify
    # =====================================================================

    def verify_event_hash72(
        self
    ) -> bool:

        computed = (

            self.compute_event_hash72()
        )

        valid = (

            computed
            ==
            self.event_hash72
        )

        if not valid:

            logger.error(

                "Event Hash72 verification failure.",

                extra={

                    "computed":
                        computed,

                    "actual":
                        self.event_hash72
                }
            )

        return valid

    # =====================================================================
    # Serialization
    # =====================================================================

    def to_dict(
        self
    ) -> Dict[str, Any]:

        data = {

            "event_id":
                self.event_id,

            "event_type":
                self.event_type,

            "runtime_id":
                self.runtime_id,

            "branch_id":
                self.branch_id,

            "schema_version":
                self.schema_version,

            "created_at_ns":
                self.created_at_ns,

            "parent_event_hash72":
                self.parent_event_hash72,

            "receipt_hash72":
                self.receipt_hash72,

            "payload":
                self.payload,

            "event_hash72":
                self.event_hash72,

            "metadata":
                self.metadata
        }

        # -------------------------------------------------------------
        # Extended Fields
        # -------------------------------------------------------------

        for key in self.extra_field_defaults:

            data[key] = getattr(
                self,
                key
            )

        return data

    # -------------------------------------------------------------

    def serialize_event(
        self
    ) -> str:

        return json.dumps(

            self.to_dict(),

            sort_keys=True,

            separators=(",", ":"),

            ensure_ascii=False
        )

    # =====================================================================
    # Deserialization
    # =====================================================================

    @classmethod
    def deserialize_event(

        cls,

        serialized: str

    ):

        payload = json.loads(
            serialized
        )

        event_type = payload.get(
            "event_type",
            ""
        )

        event_class = (

            EVENT_SCHEMA_REGISTRY.get(

                event_type,

                cls
            )
        )

        return event_class(
            **payload
        )

    # =====================================================================
    # Websocket Projection
    # =====================================================================

    def to_websocket_payload(
        self
    ) -> Dict[str, Any]:

        return {

            "event":
                self.event_type,

            "event_type":
                self.event_type,

            "runtime_id":
                self.runtime_id,

            "branch_id":
                self.branch_id,

            "event_hash72":
                self.event_hash72,

            "parent_event_hash72":
                self.parent_event_hash72,

            "receipt_hash72":
                self.receipt_hash72,

            "timestamp_ns":
                self.created_at_ns,

            "payload":
                self.payload
        }

    # =====================================================================
    # Graph Projection
    # =====================================================================

    def to_graph_projection(
        self
    ) -> Dict[str, Any]:

        return {

            "node_id":
                self.event_hash72,

            "runtime_id":
                self.runtime_id,

            "parent":
                self.parent_event_hash72,

            "receipt_hash72":
                self.receipt_hash72,

            "event_type":
                self.event_type,

            "timestamp_ns":
                self.created_at_ns
        }

    # =====================================================================
    # Replay Packet
    # =====================================================================

    def to_replay_packet(
        self
    ) -> Dict[str, Any]:

        return {

            "event_hash72":
                self.event_hash72,

            "parent_event_hash72":
                self.parent_event_hash72,

            "runtime_id":
                self.runtime_id,

            "receipt_hash72":
                self.receipt_hash72,

            "payload":
                self.payload
        }

# ============================================================================
# Replay Event
# ============================================================================

class HHSReplayEvent(
    HHSRuntimeEventEnvelope
):

    extra_field_defaults = {

        "replay_step": 0,

        "replay_equivalent": True
    }

# ============================================================================
# Snapshot Event
# ============================================================================

class HHSSnapshotEvent(
    HHSRuntimeEventEnvelope
):

    extra_field_defaults = {

        "snapshot_id": "",

        "replay_hash72": ""
    }

# ============================================================================
# Cognition Event
# ============================================================================

class HHSCognitionEvent(
    HHSRuntimeEventEnvelope
):

    extra_field_defaults = {

        "cognition_task_id": "",

        "cognition_state": ""
    }

# ============================================================================
# Toolchain Event
# ============================================================================

class HHSToolchainEvent(
    HHSRuntimeEventEnvelope
):

    extra_field_defaults = {

        "toolchain_id": "",

        "execution_signature": ""
    }

# ============================================================================
# Consensus Event
# ============================================================================

class HHSConsensusEvent(
    HHSRuntimeEventEnvelope
):

    extra_field_defaults = {

        "proposal_id": "",

        "quorum_state": ""
    }

# ============================================================================
# Multimodal Event
# ============================================================================

class HHSMultimodalEvent(
    HHSRuntimeEventEnvelope
):

    extra_field_defaults = {

        "modality": "",

        "projection_hash72": ""
    }

# ============================================================================
# Registry
# ============================================================================

EVENT_SCHEMA_REGISTRY = {

    "replay":
        HHSReplayEvent,

    "snapshot":
        HHSSnapshotEvent,

    "cognition":
        HHSCognitionEvent,

    "toolchain":
        HHSToolchainEvent,

    "consensus":
        HHSConsensusEvent,

    "multimodal":
        HHSMultimodalEvent
}

# ============================================================================
# Factory
# ============================================================================

def create_runtime_event(

    event_type: str,

    runtime_id: str,

    receipt_hash72: str,

    payload: Dict[str, Any],

    branch_id: str = "main",

    parent_event_hash72: str = ""

):

    event_class = (

        EVENT_SCHEMA_REGISTRY.get(

            event_type,

            HHSRuntimeEventEnvelope
        )
    )

    return event_class(

        event_id=str(
            uuid.uuid4()
        ),

        event_type=event_type,

        runtime_id=runtime_id,

        branch_id=branch_id,

        schema_version=EVENT_SCHEMA_VERSION,

        created_at_ns=time.time_ns(),

        parent_event_hash72=parent_event_hash72,

        receipt_hash72=receipt_hash72,

        payload=payload
    )

# ============================================================================
# Schema Version
# ============================================================================

def verify_schema_version(

    event: HHSRuntimeEventEnvelope

) -> bool:

    return (

        event.schema_version
        ==
        EVENT_SCHEMA_VERSION
    )

# ============================================================================
# Upcast
# ============================================================================

def upcast_event(

    event: HHSRuntimeEventEnvelope

):

    if event.schema_version == "v1":

        return event

    raise RuntimeError(

        "Unsupported event schema version: "

        + event.schema_version
    )

# ============================================================================
# Projection Validation
# ============================================================================

def validate_transport_projection(

    event: HHSRuntimeEventEnvelope

):

    return {

        "websocket":
            event.to_websocket_payload(),

        "graph":
            event.to_graph_projection(),

        "replay":
            event.to_replay_packet()
    }

# ============================================================================
# Self Test
# ============================================================================

def runtime_event_schema_self_test():

    event = create_runtime_event(

        event_type="replay",

        runtime_id="runtime_001",

        receipt_hash72="abc123",

        payload={

            "step": 1,

            "trajectory": "stable"
        }
    )

    serialized = (

        event.serialize_event()
    )

    restored = (

        HHSRuntimeEventEnvelope
            .deserialize_event(
                serialized
            )
    )

    assert restored.verify_event_hash72()

    assert verify_schema_version(
        restored
    )

    projection = (

        validate_transport_projection(
            restored
        )
    )

    assert (
        projection["websocket"]["receipt_hash72"]
        ==
        "abc123"
    )

    assert (
        projection["graph"]["receipt_hash72"]
        ==
        "abc123"
    )

    assert (
        projection["replay"]["receipt_hash72"]
        ==
        "abc123"
    )

    return True

# ============================================================================
# Entry
# ============================================================================

if __name__ == "__main__":

    runtime_event_schema_self_test()

    print(
        "runtime_event_schema_self_test: PASS"
    )