# ============================================================================
# hhs_storage/runtime_state_store_v1.py
# HARMONICODE / HHS
# DETERMINISTIC RUNTIME PERSISTENCE ENGINE
#
# PURPOSE
# -------
# Canonical runtime persistence substrate for:
#
#   - deterministic runtime snapshots
#   - append-only event ledgers
#   - receipt-chain continuity
#   - replay-certified reconstruction
#   - branch/fork runtime topology
#   - distributed runtime synchronization
#   - v44.2 kernel continuity enforcement
#   - replay equivalence verification
#
# This layer is NOT generic storage.
#
# This layer is:
#
#   deterministic runtime continuity infrastructure
#
# ============================================================================

from __future__ import annotations

import copy
import hashlib
import json
import logging
import threading
import time
import uuid

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from hhs_python.runtime.hhs_runtime_state import (
    HHSRuntimeState,
    create_runtime_state,
    V44_KERNEL_AVAILABLE,
    AUTHORITATIVE_TRUST_POLICY_V44,
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_RUNTIME_STATE_STORE"
)

# ============================================================================
# SNAPSHOT
# ============================================================================

@dataclass
class HHSRuntimeSnapshot:

    snapshot_id: str

    runtime_id: str

    created_at_ns: int

    step: int

    receipt_hash72: str

    parent_receipt_hash72: str

    state_hash72: str

    replay_hash72: str

    branch_id: str

    schema_version: str

    runtime_state: Dict[str, Any]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# EVENT
# ============================================================================

@dataclass
class HHSRuntimeEvent:

    event_id: str

    created_at_ns: int

    event_type: str

    runtime_id: str

    receipt_hash72: str

    payload: Dict[str, Any]

    parent_event_id: Optional[str] = None

# ============================================================================
# BRANCH
# ============================================================================

@dataclass
class HHSRuntimeBranch:

    branch_id: str

    created_at_ns: int

    source_runtime_id: str

    source_receipt_hash72: str

    branch_head_receipt_hash72: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ============================================================================
# STORE
# ============================================================================

class HHSRuntimeStateStoreV1:

    """
    Canonical deterministic runtime persistence engine.
    """

    SCHEMA_VERSION = "v1"

    def __init__(self):

        self.lock = threading.RLock()

        self.events: List[
            HHSRuntimeEvent
        ] = []

        self.snapshots: Dict[
            str,
            HHSRuntimeSnapshot
        ] = {}

        self.runtime_heads: Dict[
            str,
            str
        ] = {}

        self.branches: Dict[
            str,
            HHSRuntimeBranch
        ] = {}

        self.runtime_timelines = defaultdict(list)

        self.event_subscribers = []

    # =====================================================================
    # HASH72
    # =====================================================================

    def compute_hash72(
        self,
        payload: Dict[str, Any],
    ) -> str:

        serialized = json.dumps(

            payload,

            sort_keys=True,

            separators=(",", ":"),
        )

        digest = hashlib.sha256(

            serialized.encode("utf-8")

        ).hexdigest()

        return digest[:72]

    # =====================================================================
    # EVENT EMISSION
    # =====================================================================

    def emit_runtime_event(
        self,
        event: HHSRuntimeEvent,
    ):

        for subscriber in self.event_subscribers:

            try:

                subscriber(event)

            except Exception as e:

                logger.error(
                    f"Runtime event subscriber failure: {e}"
                )

    # =====================================================================
    # SUBSCRIBE
    # =====================================================================

    def subscribe(self, callback):

        self.event_subscribers.append(
            callback
        )

    # =====================================================================
    # APPEND EVENT
    # =====================================================================

    def append_event(

        self,

        runtime_state: HHSRuntimeState,

        event_type: str,

        payload: Dict[str, Any],
    ) -> HHSRuntimeEvent:

        with self.lock:

            previous_event_id = None

            timeline = self.runtime_timelines[
                runtime_state.runtime_id
            ]

            if timeline:

                previous_event_id = (
                    timeline[-1]
                )

            event = HHSRuntimeEvent(

                event_id=str(uuid.uuid4()),

                created_at_ns=time.time_ns(),

                event_type=event_type,

                runtime_id=runtime_state.runtime_id,

                receipt_hash72=(
                    runtime_state.receipt_hash72
                ),

                payload=payload,

                parent_event_id=previous_event_id,
            )

            self.events.append(event)

            self.runtime_timelines[
                runtime_state.runtime_id
            ].append(event.event_id)

            self.runtime_heads[
                runtime_state.runtime_id
            ] = runtime_state.receipt_hash72

            self.emit_runtime_event(
                event
            )

            logger.info(
                f"Event appended: {event.event_id}"
            )

            return event

    # =====================================================================
    # SNAPSHOT CREATION
    # =====================================================================

    def create_snapshot(
        self,
        runtime_state: HHSRuntimeState,
        branch_id: str = "main",
    ) -> HHSRuntimeSnapshot:

        with self.lock:

            runtime_payload = json.loads(

                runtime_state.serialize_deterministic()
            )

            replay_hash = self.compute_hash72(
                runtime_payload
            )

            snapshot = HHSRuntimeSnapshot(

                snapshot_id=str(uuid.uuid4()),

                runtime_id=runtime_state.runtime_id,

                created_at_ns=time.time_ns(),

                step=runtime_state.step,

                receipt_hash72=(
                    runtime_state.receipt_hash72
                ),

                parent_receipt_hash72=(
                    runtime_state.prev_receipt_hash72
                ),

                state_hash72=(
                    runtime_state.state_hash72
                ),

                replay_hash72=replay_hash,

                branch_id=branch_id,

                schema_version=(
                    self.SCHEMA_VERSION
                ),

                runtime_state=runtime_payload,

                metadata={

                    "kernel_available":
                        V44_KERNEL_AVAILABLE,

                    "kernel_policy":
                        str(
                            AUTHORITATIVE_TRUST_POLICY_V44
                        )
                        if V44_KERNEL_AVAILABLE
                        else None,
                },
            )

            self.snapshots[
                snapshot.snapshot_id
            ] = snapshot

            logger.info(
                f"Snapshot created: "
                f"{snapshot.snapshot_id}"
            )

            return snapshot

    # =====================================================================
    # SNAPSHOT VERIFY
    # =====================================================================

    def verify_snapshot(
        self,
        snapshot: HHSRuntimeSnapshot,
    ) -> bool:

        replay_hash = self.compute_hash72(
            snapshot.runtime_state
        )

        valid = (

            replay_hash
            ==
            snapshot.replay_hash72
        )

        if not valid:

            logger.error(
                f"Snapshot verification failed: "
                f"{snapshot.snapshot_id}"
            )

        return valid

    # =====================================================================
    # RESTORE SNAPSHOT
    # =====================================================================

    def restore_snapshot(
        self,
        snapshot_id: str,
    ) -> HHSRuntimeState:

        snapshot = self.snapshots[
            snapshot_id
        ]

        valid = self.verify_snapshot(
            snapshot
        )

        if not valid:

            raise RuntimeError(
                "Snapshot verification failed."
            )

        state = HHSRuntimeState(
            **snapshot.runtime_state
        )

        logger.info(
            f"Snapshot restored: {snapshot_id}"
        )

        return state

    # =====================================================================
    # REHYDRATION
    # =====================================================================

    def rehydrate_runtime(
        self,
        runtime_id: str,
    ) -> HHSRuntimeState:

        snapshots = [

            s

            for s in self.snapshots.values()

            if s.runtime_id == runtime_id
        ]

        if not snapshots:

            raise RuntimeError(
                f"No snapshots for runtime: "
                f"{runtime_id}"
            )

        latest = sorted(

            snapshots,

            key=lambda x: x.created_at_ns,

            reverse=True,
        )[0]

        return self.restore_snapshot(
            latest.snapshot_id
        )

    # =====================================================================
    # REPLAY EQUIVALENCE
    # =====================================================================

    def verify_replay_equivalence(
        self,
        runtime_a: HHSRuntimeState,
        runtime_b: HHSRuntimeState,
    ) -> bool:

        serialized_a = (
            runtime_a.serialize_deterministic()
        )

        serialized_b = (
            runtime_b.serialize_deterministic()
        )

        equivalent = (
            serialized_a == serialized_b
        )

        if not equivalent:

            logger.error(
                "Replay equivalence failure."
            )

        return equivalent

    # =====================================================================
    # BRANCH FORK
    # =====================================================================

    def fork_runtime_branch(
        self,
        runtime_state: HHSRuntimeState,
        metadata: Optional[Dict] = None,
    ) -> HHSRuntimeBranch:

        branch = HHSRuntimeBranch(

            branch_id=str(uuid.uuid4()),

            created_at_ns=time.time_ns(),

            source_runtime_id=(
                runtime_state.runtime_id
            ),

            source_receipt_hash72=(
                runtime_state.receipt_hash72
            ),

            branch_head_receipt_hash72=(
                runtime_state.receipt_hash72
            ),

            metadata=metadata or {},
        )

        self.branches[
            branch.branch_id
        ] = branch

        logger.info(
            f"Runtime branch forked: "
            f"{branch.branch_id}"
        )

        return branch

    # =====================================================================
    # BRANCH MERGE
    # =====================================================================

    def merge_runtime_branch(

        self,

        base_runtime: HHSRuntimeState,

        branch_runtime: HHSRuntimeState,
    ) -> HHSRuntimeState:

        merged = copy.deepcopy(
            base_runtime
        )

        merged.transport_flux += (
            branch_runtime.transport_flux
        )

        merged.orientation_flux += (
            branch_runtime.orientation_flux
        )

        merged.constraint_flux += (
            branch_runtime.constraint_flux
        )

        merged.step = max(

            base_runtime.step,

            branch_runtime.step,
        )

        merged.timestamp_ns = time.time_ns()

        merged.state_hash72 = (
            merged.compute_state_hash72()
        )

        merged.receipt_hash72 = (
            merged.compute_state_hash72()
        )

        logger.info(
            f"Runtime branches merged."
        )

        return merged

    # =====================================================================
    # BRANCH COMPARISON
    # =====================================================================

    def compare_runtime_branches(

        self,

        runtime_a: HHSRuntimeState,

        runtime_b: HHSRuntimeState,
    ):

        return runtime_a.diff(
            runtime_b
        )

    # =====================================================================
    # SCHEMA EVOLUTION
    # =====================================================================

    def verify_schema_compatibility(
        self,
        snapshot: HHSRuntimeSnapshot,
    ) -> bool:

        return (
            snapshot.schema_version
            ==
            self.SCHEMA_VERSION
        )

    # =====================================================================
    # SNAPSHOT UPCAST
    # =====================================================================

    def upcast_snapshot(
        self,
        snapshot: HHSRuntimeSnapshot,
    ):

        if snapshot.schema_version == "v1":

            return snapshot

        raise RuntimeError(
            f"Unsupported schema version: "
            f"{snapshot.schema_version}"
        )

    # =====================================================================
    # STATE MIGRATION
    # =====================================================================

    def migrate_runtime_state(
        self,
        snapshot: HHSRuntimeSnapshot,
    ):

        upgraded = self.upcast_snapshot(
            snapshot
        )

        upgraded.schema_version = (
            self.SCHEMA_VERSION
        )

        return upgraded

    # =====================================================================
    # EVENT HELPERS
    # =====================================================================

    def append_receipt(
        self,
        runtime_state: HHSRuntimeState,
    ):

        return self.append_event(

            runtime_state,

            "receipt.commit",

            runtime_state.to_receipt_payload(),
        )

    # =====================================================================
    # SNAPSHOT EVENT
    # =====================================================================

    def emit_snapshot_event(
        self,
        snapshot: HHSRuntimeSnapshot,
    ):

        event_payload = {

            "snapshot_id":
                snapshot.snapshot_id,

            "runtime_id":
                snapshot.runtime_id,

            "receipt_hash72":
                snapshot.receipt_hash72,
        }

        logger.info(
            f"Snapshot event emitted: "
            f"{snapshot.snapshot_id}"
        )

        return event_payload

    # =====================================================================
    # REPLAY EVENT
    # =====================================================================

    def emit_replay_event(
        self,
        runtime_id: str,
    ):

        payload = {

            "runtime_id":
                runtime_id,

            "timeline_length":
                len(
                    self.runtime_timelines[
                        runtime_id
                    ]
                ),
        }

        logger.info(
            f"Replay event emitted: "
            f"{runtime_id}"
        )

        return payload

# ============================================================================
# GLOBAL STORE
# ============================================================================

runtime_state_store = (
    HHSRuntimeStateStoreV1()
)

# ============================================================================
# SELF TEST
# ============================================================================

def runtime_state_store_self_test():

    state = create_runtime_state()

    runtime_state_store.append_receipt(
        state
    )

    snapshot = (
        runtime_state_store.create_snapshot(
            state
        )
    )

    restored = (
        runtime_state_store.restore_snapshot(
            snapshot.snapshot_id
        )
    )

    equivalent = (
        runtime_state_store
        .verify_replay_equivalence(
            state,
            restored,
        )
    )

    branch = (
        runtime_state_store
        .fork_runtime_branch(
            state
        )
    )

    replay_event = (
        runtime_state_store
        .emit_replay_event(
            state.runtime_id
        )
    )

    print()

    print("SNAPSHOT")

    print(snapshot)

    print()

    print("RESTORED")

    print(restored)

    print()

    print("EQUIVALENT")

    print(equivalent)

    print()

    print("BRANCH")

    print(branch)

    print()

    print("REPLAY EVENT")

    print(replay_event)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    runtime_state_store_self_test()