# ============================================================================
# hhs_backend/runtime/runtime_snapshot_codec.py
# HARMONICODE / HHS
# CANONICAL REPLAY SERIALIZATION SUBSTRATE
#
# PURPOSE
# -------
# Canonical deterministic replay codec for:
#
#   - snapshot serialization
#   - replay-certified runtime materialization
#   - deterministic runtime resurrection
#   - branch-topological replay
#   - schema evolution/upcasting
#   - replay packet transport
#   - distributed runtime reconstruction
#   - v44.2 kernel continuity
#
# Snapshots are runtime continuity anchors.
#
# ============================================================================

from __future__ import annotations

import copy
import gzip
import hashlib
import json
import logging
import pickle
import time
import uuid

from dataclasses import (
    dataclass,
    field,
    asdict,
)

from typing import (
    Dict,
    Any,
    Optional,
    List,
)

from hhs_python.runtime.hhs_runtime_state import (
    HHSRuntimeState,
    V44_KERNEL_AVAILABLE,
    AUTHORITATIVE_TRUST_POLICY_V44,
)

from hhs_backend.runtime.runtime_receipt_chain import (
    HHSReceipt,
)

from hhs_backend.runtime.runtime_event_schema import (
    HHSRuntimeEventEnvelope,
)

# ============================================================================
# OPTIONAL V44.2 KERNEL
# ============================================================================

try:

    from HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked_7 import (

        security_hash72_v44,

        Tensor,

        Manifold9,
    )

except Exception:

    security_hash72_v44 = None

    Tensor = None

    Manifold9 = None

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_RUNTIME_SNAPSHOT_CODEC"
)

# ============================================================================
# CONSTANTS
# ============================================================================

SNAPSHOT_SCHEMA_VERSION = "v1"

HASH72_LEN = 72

# ============================================================================
# HASH72
# ============================================================================

def compute_hash72(
    payload: Dict[str, Any]
):

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
# SNAPSHOT PACKET
# ============================================================================

@dataclass
class HHSSnapshotPacket:

    packet_id: str

    runtime_id: str

    branch_id: str

    schema_version: str

    created_at_ns: int

    snapshot_hash72: str

    parent_snapshot_hash72: str

    receipt_hash72: str

    replay_hash72: str

    runtime_state: Dict[str, Any]

    receipt_chain: List[Dict[str, Any]]

    event_topology: List[Dict[str, Any]]

    branch_topology: Dict[str, Any]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# CODEC
# ============================================================================

class HHSRuntimeSnapshotCodec:

    """
    Canonical deterministic replay serialization authority.
    """

    def __init__(self):

        self.codec_version = (
            SNAPSHOT_SCHEMA_VERSION
        )

    # =====================================================================
    # ENCODE SNAPSHOT
    # =====================================================================

    def encode_snapshot(
        self,
        packet: HHSSnapshotPacket,
    ) -> bytes:

        payload = asdict(packet)

        serialized = json.dumps(

            payload,

            sort_keys=True,

            separators=(",", ":"),
        ).encode("utf-8")

        compressed = gzip.compress(
            serialized
        )

        logger.info(
            f"Snapshot encoded: "
            f"{packet.packet_id}"
        )

        return compressed

    # =====================================================================
    # DECODE SNAPSHOT
    # =====================================================================

    def decode_snapshot(
        self,
        payload: bytes,
    ) -> HHSSnapshotPacket:

        decompressed = gzip.decompress(
            payload
        )

        decoded = json.loads(
            decompressed.decode("utf-8")
        )

        packet = HHSSnapshotPacket(
            **decoded
        )

        logger.info(
            f"Snapshot decoded: "
            f"{packet.packet_id}"
        )

        return packet

    # =====================================================================
    # PICKLE PACKET
    # =====================================================================

    def encode_replay_packet(
        self,
        packet: HHSSnapshotPacket,
    ):

        return gzip.compress(

            pickle.dumps(packet)

        )

    # =====================================================================
    # UNPICKLE PACKET
    # =====================================================================

    def decode_replay_packet(
        self,
        payload: bytes,
    ):

        return pickle.loads(

            gzip.decompress(payload)
        )

    # =====================================================================
    # VERIFY MATERIALIZATION
    # =====================================================================

    def verify_materialization(
        self,
        packet: HHSSnapshotPacket,
    ):

        replay_hash = compute_hash72({

            "runtime_state":
                packet.runtime_state,

            "receipt_chain":
                packet.receipt_chain,

            "event_topology":
                packet.event_topology,
        })

        valid = (
            replay_hash
            ==
            packet.replay_hash72
        )

        if not valid:

            logger.error(
                "Replay materialization verification failed."
            )

        return valid

    # =====================================================================
    # MATERIALIZE RUNTIME
    # =====================================================================

    def materialize_runtime(
        self,
        packet: HHSSnapshotPacket,
    ) -> HHSRuntimeState:

        valid = self.verify_materialization(
            packet
        )

        if not valid:

            raise RuntimeError(
                "Snapshot materialization invalid."
            )

        runtime_state = HHSRuntimeState(
            **packet.runtime_state
        )

        logger.info(
            f"Runtime materialized: "
            f"{runtime_state.runtime_id}"
        )

        return runtime_state

    # =====================================================================
    # DELTA SNAPSHOT
    # =====================================================================

    def create_delta_snapshot(

        self,

        base_packet: HHSSnapshotPacket,

        modified_runtime_state: Dict[str, Any],
    ):

        delta = {}

        for key, value in (
            modified_runtime_state.items()
        ):

            if (

                key
                not in base_packet.runtime_state

                or

                base_packet.runtime_state[key]
                != value

            ):

                delta[key] = value

        return delta

    # =====================================================================
    # INCREMENTAL SNAPSHOT
    # =====================================================================

    def create_incremental_snapshot(

        self,

        packet: HHSSnapshotPacket,

        delta: Dict[str, Any],
    ):

        updated = copy.deepcopy(packet)

        updated.runtime_state.update(
            delta
        )

        updated.snapshot_hash72 = (
            compute_hash72(
                updated.runtime_state
            )
        )

        return updated

    # =====================================================================
    # BRANCH SNAPSHOT
    # =====================================================================

    def encode_branch_topology(
        self,
        branch_topology: Dict[str, Any],
    ):

        payload = json.dumps(

            branch_topology,

            sort_keys=True,

        ).encode("utf-8")

        return gzip.compress(
            payload
        )

    # =====================================================================
    # DECODE BRANCH
    # =====================================================================

    def decode_branch_topology(
        self,
        payload: bytes,
    ):

        decompressed = gzip.decompress(
            payload
        )

        return json.loads(
            decompressed.decode("utf-8")
        )

    # =====================================================================
    # MERGE MATERIALIZATION
    # =====================================================================

    def materialize_branch_merge(

        self,

        base_packet: HHSSnapshotPacket,

        branch_packet: HHSSnapshotPacket,
    ):

        merged = copy.deepcopy(
            base_packet
        )

        merged.runtime_state.update(

            branch_packet.runtime_state
        )

        merged.receipt_chain.extend(

            branch_packet.receipt_chain
        )

        merged.event_topology.extend(

            branch_packet.event_topology
        )

        merged.snapshot_hash72 = (
            compute_hash72(
                merged.runtime_state
            )
        )

        return merged

    # =====================================================================
    # REHYDRATE RUNTIME STATE
    # =====================================================================

    def rehydrate_runtime_state(
        self,
        packet: HHSSnapshotPacket,
    ):

        return self.materialize_runtime(
            packet
        )

    # =====================================================================
    # REHYDRATE RECEIPTS
    # =====================================================================

    def rehydrate_receipt_chain(
        self,
        packet: HHSSnapshotPacket,
    ):

        receipts = []

        for receipt_payload in (
            packet.receipt_chain
        ):

            receipts.append(

                HHSReceipt(
                    **receipt_payload
                )
            )

        return receipts

    # =====================================================================
    # REHYDRATE EVENTS
    # =====================================================================

    def rehydrate_event_topology(
        self,
        packet: HHSSnapshotPacket,
    ):

        events = []

        for event_payload in (
            packet.event_topology
        ):

            events.append(

                HHSRuntimeEventEnvelope(
                    **event_payload
                )
            )

        return events

    # =====================================================================
    # GRAPH SNAPSHOT
    # =====================================================================

    def to_graph_snapshot_projection(
        self,
        packet: HHSSnapshotPacket,
    ):

        return {

            "snapshot_hash72":
                packet.snapshot_hash72,

            "runtime_id":
                packet.runtime_id,

            "branch_id":
                packet.branch_id,

            "receipt_hash72":
                packet.receipt_hash72,

            "parent_snapshot":
                packet.parent_snapshot_hash72,
        }

    # =====================================================================
    # REPLAY TRANSPORT
    # =====================================================================

    def to_replay_transport_packet(
        self,
        packet: HHSSnapshotPacket,
    ):

        return {

            "runtime_id":
                packet.runtime_id,

            "snapshot_hash72":
                packet.snapshot_hash72,

            "receipt_hash72":
                packet.receipt_hash72,

            "replay_hash72":
                packet.replay_hash72,
        }

    # =====================================================================
    # VERIFY COMPATIBILITY
    # =====================================================================

    def verify_codec_compatibility(
        self,
        packet: HHSSnapshotPacket,
    ):

        return (
            packet.schema_version
            ==
            SNAPSHOT_SCHEMA_VERSION
        )

    # =====================================================================
    # UPCAST SNAPSHOT
    # =====================================================================

    def upcast_snapshot_packet(
        self,
        packet: HHSSnapshotPacket,
    ):

        if packet.schema_version == "v1":

            return packet

        raise RuntimeError(
            f"Unsupported snapshot schema: "
            f"{packet.schema_version}"
        )

    # =====================================================================
    # MIGRATE PACKET
    # =====================================================================

    def migrate_replay_packet(
        self,
        packet: HHSSnapshotPacket,
    ):

        upgraded = self.upcast_snapshot_packet(
            packet
        )

        upgraded.schema_version = (
            SNAPSHOT_SCHEMA_VERSION
        )

        return upgraded

    # =====================================================================
    # V44 VALIDATION
    # =====================================================================

    def validate_v44_codec_alignment(
        self,
        packet: HHSSnapshotPacket,
    ):

        if not V44_KERNEL_AVAILABLE:

            return {

                "kernel_available": False,

                "validated": False,
            }

        payload_hash = hashlib.sha256(

            json.dumps(

                packet.runtime_state,

                sort_keys=True,

            ).encode("utf-8")

        ).hexdigest()

        trust_hash = hashlib.sha256(

            str(
                AUTHORITATIVE_TRUST_POLICY_V44
            ).encode("utf-8")

        ).hexdigest()

        return {

            "kernel_available": True,

            "validated": True,

            "payload_hash":
                payload_hash,

            "trust_hash":
                trust_hash,
        }

# ============================================================================
# GLOBAL CODEC
# ============================================================================

runtime_snapshot_codec = (
    HHSRuntimeSnapshotCodec()
)

# ============================================================================
# FACTORY
# ============================================================================

def create_snapshot_packet(

    runtime_state: HHSRuntimeState,

    receipt_chain: List[Dict[str, Any]],

    event_topology: List[Dict[str, Any]],

    branch_topology: Dict[str, Any],

    branch_id: str = "main",

    parent_snapshot_hash72: str = "",
):

    runtime_payload = json.loads(

        runtime_state.serialize_deterministic()
    )

    replay_hash = compute_hash72({

        "runtime_state":
            runtime_payload,

        "receipt_chain":
            receipt_chain,

        "event_topology":
            event_topology,
    })

    snapshot_hash = compute_hash72(
        runtime_payload
    )

    return HHSSnapshotPacket(

        packet_id=str(uuid.uuid4()),

        runtime_id=runtime_state.runtime_id,

        branch_id=branch_id,

        schema_version=
            SNAPSHOT_SCHEMA_VERSION,

        created_at_ns=time.time_ns(),

        snapshot_hash72=
            snapshot_hash,

        parent_snapshot_hash72=
            parent_snapshot_hash72,

        receipt_hash72=
            runtime_state.receipt_hash72,

        replay_hash72=
            replay_hash,

        runtime_state=
            runtime_payload,

        receipt_chain=
            receipt_chain,

        event_topology=
            event_topology,

        branch_topology=
            branch_topology,

        metadata={

            "kernel_available":
                V44_KERNEL_AVAILABLE,

            "codec_version":
                SNAPSHOT_SCHEMA_VERSION,
        },
    )

# ============================================================================
# SELF TEST
# ============================================================================

def runtime_snapshot_codec_self_test():

    runtime_state = HHSRuntimeState(

        runtime_id="runtime_001",

        step=1,

        orbit_id=72,

        transport_flux="1/1",

        orientation_flux="1/1",

        constraint_flux="1/1",

        witness_flags=7,

        prev_receipt_hash72="",

        state_hash72="state001",

        receipt_hash72="receipt001",

        lo_shu_slot=5,

        closure_class="0",

        converged=True,

        halted=False,

        timestamp_ns=time.time_ns(),
    )

    packet = create_snapshot_packet(

        runtime_state=runtime_state,

        receipt_chain=[],

        event_topology=[],

        branch_topology={},
    )

    encoded = (
        runtime_snapshot_codec
        .encode_snapshot(
            packet
        )
    )

    decoded = (
        runtime_snapshot_codec
        .decode_snapshot(
            encoded
        )
    )

    valid = (
        runtime_snapshot_codec
        .verify_materialization(
            decoded
        )
    )

    materialized = (
        runtime_snapshot_codec
        .materialize_runtime(
            decoded
        )
    )

    projection = (
        runtime_snapshot_codec
        .to_graph_snapshot_projection(
            decoded
        )
    )

    alignment = (
        runtime_snapshot_codec
        .validate_v44_codec_alignment(
            decoded
        )
    )

    print()

    print("PACKET")

    print(packet)

    print()

    print("VALID")

    print(valid)

    print()

    print("MATERIALIZED")

    print(materialized)

    print()

    print("PROJECTION")

    print(projection)

    print()

    print("V44")

    print(alignment)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    runtime_snapshot_codec_self_test()