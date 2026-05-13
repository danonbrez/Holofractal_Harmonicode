# hhs_python/runtime/hhs_runtime_orchestrator.py
#
# HHS / HARMONICODE
# Canonical Runtime Orchestrator
#
# Runtime Principle:
#
#   orchestration
#   =
#   deterministic runtime continuity coordination
#
# NOT:
#
#   application control logic
#

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import time
import uuid


# ============================================================
# IMPORT EXISTING AUTHORITIES
# ============================================================

# Canonical runtime state authority
from hhs_python.runtime.hhs_runtime_state import (
    HHSRuntimeState
)

# Canonical runtime object authority
from hhs_python.runtime.hhs_runtime_object import (
    HHSRuntimeObject
)

# Canonical runtime event authority
from hhs_python.runtime.hhs_event_schema import (
    HHSEvent,
    HHSEventType,
    HHSEventStream,
)

# ============================================================
# OPTIONAL AUTHORITIES
# ============================================================

# NOTE:
#
# These are intentionally soft-imported because the
# repository topology is still stabilizing.
#
# The orchestrator coordinates authorities;
# it does NOT redefine them.
#

try:

    from hhs_graph.hhs_multimodal_receipt_graph_v1 import (
        HHSMultimodalReceiptGraph
    )

except Exception:

    HHSMultimodalReceiptGraph = None


try:

    from hhs_python.runtime.hhs_ctypes_bridge import (
        HHSRuntimeBridge
    )

except Exception:

    HHSRuntimeBridge = None


# ============================================================
# ORCHESTRATOR CONFIG
# ============================================================

@dataclass
class HHSRuntimeOrchestratorConfig:

    runtime_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    enable_replay: bool = True
    enable_transport: bool = True
    enable_graph: bool = True
    enable_projection: bool = True
    enable_websocket_streams: bool = True

    auto_commit_receipts: bool = True
    auto_emit_events: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CANONICAL ORCHESTRATOR
# ============================================================

class HHSRuntimeOrchestrator:
    """
    Canonical runtime continuity coordinator.

    Coordinates existing runtime authorities.

    Does NOT redefine:
        - replay
        - graph
        - transport
        - receipts
        - runtime objects
        - VM execution
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self,
        config: Optional[
            HHSRuntimeOrchestratorConfig
        ] = None,
    ):

        self.config = (
            config
            or HHSRuntimeOrchestratorConfig()
        )

        # ----------------------------------------------------
        # Canonical runtime state
        # ----------------------------------------------------

        self.runtime_state = HHSRuntimeState(
            runtime_id=self.config.runtime_id
        )

        # ----------------------------------------------------
        # Canonical event stream
        # ----------------------------------------------------

        self.event_stream = HHSEventStream(
            runtime_id=self.config.runtime_id
        )

        # ----------------------------------------------------
        # Runtime objects
        # ----------------------------------------------------

        self.runtime_objects: Dict[
            str,
            HHSRuntimeObject
        ] = {}

        # ----------------------------------------------------
        # Graph authority
        # ----------------------------------------------------

        self.graph_runtime = None

        if (
            self.config.enable_graph
            and HHSMultimodalReceiptGraph
        ):
            try:

                self.graph_runtime = (
                    HHSMultimodalReceiptGraph()
                )

            except Exception:
                self.graph_runtime = None

        # ----------------------------------------------------
        # Runtime bridge
        # ----------------------------------------------------

        self.runtime_bridge = None

        if HHSRuntimeBridge:
            try:

                self.runtime_bridge = (
                    HHSRuntimeBridge()
                )

            except Exception:
                self.runtime_bridge = None

        # ----------------------------------------------------
        # Runtime init event
        # ----------------------------------------------------

        self.emit_event(
            HHSEventType.RUNTIME_INIT,
            {
                "runtime_id": (
                    self.config.runtime_id
                )
            },
        )

    # ========================================================
    # EVENT EMISSION
    # ========================================================

    def emit_event(
        self,
        event_type: HHSEventType,
        payload: Dict[str, Any],
    ) -> HHSEvent:

        event = HHSEvent(
            runtime_id=self.runtime_state.runtime_id,

            event_type=event_type,

            payload=payload,

            state_hash216=(
                self.runtime_state.state_hash216
            ),

            receipt_hash216=(
                self.runtime_state.receipt_hash216
            ),

            branch_id=(
                self.runtime_state.branch_id
            ),

            parent_branch_id=(
                self.runtime_state.parent_branch_id
            ),

            sequence=(
                self.runtime_state.event_sequence
            ),

            epoch=(
                self.runtime_state.epoch
            ),

            converged=(
                self.runtime_state.converged
            ),

            halted=(
                self.runtime_state.halted
            ),

            replayable=(
                self.runtime_state.replayable
            ),

            reconstructible=(
                self.runtime_state.reconstructible
            ),
        )

        event.compute_hashes()

        self.event_stream.append_event(
            event
        )

        self.runtime_state.event_sequence += 1

        return event

    # ========================================================
    # STEP EXECUTION
    # ========================================================

    def step_runtime(
        self,
        instruction: Optional[
            Dict[str, Any]
        ] = None,
    ):

        self.runtime_state.step += 1

        self.runtime_state.timestamp_ns = (
            time.time_ns()
        )

        # ----------------------------------------------------
        # Runtime bridge execution
        # ----------------------------------------------------

        if self.runtime_bridge:

            try:

                self.runtime_bridge.step(
                    instruction or {}
                )

            except Exception:
                pass

        # ----------------------------------------------------
        # Hash continuity
        # ----------------------------------------------------

        self.runtime_state.compute_hashes()

        # ----------------------------------------------------
        # Event continuity
        # ----------------------------------------------------

        if self.config.auto_emit_events:

            self.emit_event(
                HHSEventType.STEP,
                {
                    "step": (
                        self.runtime_state.step
                    ),

                    "instruction": (
                        instruction or {}
                    ),
                },
            )

        # ----------------------------------------------------
        # Receipt continuity
        # ----------------------------------------------------

        if self.config.auto_commit_receipts:

            self.commit_receipt()

    # ========================================================
    # RECEIPTS
    # ========================================================

    def commit_receipt(self):

        self.runtime_state.commit_receipt()

        self.emit_event(
            HHSEventType.RECEIPT_COMMIT,
            {
                "receipt_hash216": (
                    self.runtime_state
                    .receipt_hash216
                )
            },
        )

    # ========================================================
    # REPLAY
    # ========================================================

    def commit_replay(self):

        self.runtime_state.commit_replay()

        self.emit_event(
            HHSEventType.REPLAY_COMMIT,
            {
                "state_hash216": (
                    self.runtime_state
                    .state_hash216
                )
            },
        )

    # ========================================================
    # RUNTIME OBJECTS
    # ========================================================

    def register_runtime_object(
        self,
        runtime_object: HHSRuntimeObject,
    ):

        runtime_object.compute_hashes()

        self.runtime_objects[
            runtime_object.object_id
        ] = runtime_object

        self.runtime_state.add_runtime_object(
            runtime_object
        )

        self.emit_event(
            HHSEventType.OBJECT_ADD,
            {
                "object_id": (
                    runtime_object.object_id
                ),

                "object_type": (
                    runtime_object.object_type
                ),

                "state_hash216": (
                    runtime_object
                    .state_hash216
                ),
            },
        )

    def update_runtime_object(
        self,
        object_id: str,
        payload_delta: Dict[str, Any],
    ):

        if object_id not in (
            self.runtime_objects
        ):
            return

        obj = self.runtime_objects[
            object_id
        ]

        obj.revise(payload_delta)

        self.runtime_state.compute_hashes()

        self.emit_event(
            HHSEventType.OBJECT_ADD,
            {
                "object_id": obj.object_id,

                "revision": obj.revision,

                "state_hash216": (
                    obj.state_hash216
                ),
            },
        )

    # ========================================================
    # TRANSPORT
    # ========================================================

    def synchronize_transport(self):

        self.runtime_state.transport_state.synchronized = (
            True
        )

        self.runtime_state.compute_hashes()

        self.emit_event(
            HHSEventType.TRANSPORT_UPDATE,
            {
                "transport_hash216": (
                    self.runtime_state
                    .transport_hash216
                )
            },
        )

    # ========================================================
    # GRAPH
    # ========================================================

    def synchronize_graph(self):

        if not self.graph_runtime:
            return

        self.runtime_state.graph_sequence += 1

        self.runtime_state.compute_hashes()

        self.emit_event(
            HHSEventType.GRAPH_UPDATE,
            {
                "graph_hash216": (
                    self.runtime_state
                    .graph_hash216
                ),

                "graph_sequence": (
                    self.runtime_state
                    .graph_sequence
                ),
            },
        )

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot_runtime(self) -> Dict[str, Any]:

        snapshot = (
            self.runtime_state.snapshot()
        )

        self.emit_event(
            HHSEventType.SNAPSHOT,
            {
                "state_hash216": (
                    self.runtime_state
                    .state_hash216
                )
            },
        )

        return snapshot

    # ========================================================
    # RESTORE
    # ========================================================

    def restore_runtime(
        self,
        snapshot_payload: Dict[str, Any],
    ):

        self.runtime_state.restore(
            snapshot_payload
        )

        self.emit_event(
            HHSEventType.RESTORE,
            {
                "state_hash216": (
                    self.runtime_state
                    .state_hash216
                )
            },
        )

    # ========================================================
    # BRANCHING
    # ========================================================

    def fork_branch(
        self,
        branch_id: str,
    ):

        previous_branch = (
            self.runtime_state.branch_id
        )

        self.runtime_state.parent_branch_id = (
            previous_branch
        )

        self.runtime_state.branch_id = (
            branch_id
        )

        self.runtime_state.compute_hashes()

        self.emit_event(
            HHSEventType.BRANCH,
            {
                "branch_id": branch_id,

                "parent_branch_id": (
                    previous_branch
                ),
            },
        )

    def merge_branch(
        self,
        branch_id: str,
    ):

        self.runtime_state.branch_id = (
            branch_id
        )

        self.runtime_state.compute_hashes()

        self.emit_event(
            HHSEventType.REJOIN,
            {
                "branch_id": branch_id
            },
        )

    # ========================================================
    # PROJECTION
    # ========================================================

    def project_runtime(self) -> Dict[str, Any]:

        self.runtime_state.compute_hashes()

        projection = {
            "runtime_id": (
                self.runtime_state.runtime_id
            ),

            "state_hash216": (
                self.runtime_state
                .state_hash216
            ),

            "receipt_hash216": (
                self.runtime_state
                .receipt_hash216
            ),

            "step": (
                self.runtime_state.step
            ),

            "epoch": (
                self.runtime_state.epoch
            ),

            "event_sequence": (
                self.runtime_state
                .event_sequence
            ),

            "graph_sequence": (
                self.runtime_state
                .graph_sequence
            ),

            "runtime_objects": len(
                self.runtime_objects
            ),
        }

        self.emit_event(
            HHSEventType.PROJECTION_UPDATE,
            projection,
        )

        return projection

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate_runtime_state(
        self,
    ) -> bool:

        try:

            self.runtime_state.compute_hashes()

            for obj in (
                self.runtime_objects.values()
            ):
                obj.compute_hashes()

            return True

        except Exception:

            return False

    # ========================================================
    # STREAMING
    # ========================================================

    def stream_runtime_update(
        self,
    ) -> Dict[str, Any]:

        return {
            "runtime_projection": (
                self.project_runtime()
            ),

            "event_stream": (
                self.event_stream.serialize()
            ),

            "runtime_state": (
                self.runtime_state
                .receipt_summary()
            ),
        }

    # ========================================================
    # RESET
    # ========================================================

    def reset_runtime(self):

        runtime_id = (
            self.runtime_state.runtime_id
        )

        self.runtime_state = HHSRuntimeState(
            runtime_id=runtime_id
        )

        self.runtime_objects.clear()

        self.emit_event(
            HHSEventType.RUNTIME_RESET,
            {
                "runtime_id": runtime_id
            },
        )