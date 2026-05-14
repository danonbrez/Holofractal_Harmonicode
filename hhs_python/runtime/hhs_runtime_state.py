from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import copy
import time

from hhs_runtime.runtime_event_schema import (

    RuntimeEvent,

    RuntimeEventPayload,

    ReplayEvent,

    ReplayEventPayload,

    GraphEvent,

    GraphEventPayload,

    GraphNode,

    GraphEdge,

    TransportEvent,

    TransportEventPayload,

    ReceiptEvent,

    ReceiptEventPayload
)

# =========================================================
# Runtime Constants
# =========================================================

RUNTIME_STATUS_BOOTING = "booting"
RUNTIME_STATUS_ONLINE = "online"
RUNTIME_STATUS_HALTED = "halted"

# =========================================================
# Runtime Receipt
# =========================================================

@dataclass(slots=True)
class HHSRuntimeReceipt:

    receipt_hash72: str

    source_hash72: str

    operation: str

    timestamp_ns: int

    closure_class: str = "stable"

    converged: bool = True

    halted: bool = False

    witness_flags: int = 0

    # -----------------------------------------------------

    def to_event(
        self,
        *,
        sequence_id: int = 0
    ) -> ReceiptEvent:

        return ReceiptEvent.build(

            ReceiptEventPayload(

                receipt_hash72=
                    self.receipt_hash72,

                source_hash72=
                    self.source_hash72,

                operation=
                    self.operation,

                closure_class=
                    self.closure_class,

                witness_flags=
                    self.witness_flags,

                converged=
                    self.converged,

                halted=
                    self.halted
            ),

            sequence_id=
                sequence_id
        )

# =========================================================
# Runtime Graph
# =========================================================

@dataclass(slots=True)
class HHSRuntimeGraph:

    nodes: List[GraphNode] = field(

        default_factory=list
    )

    edges: List[GraphEdge] = field(

        default_factory=list
    )

    graph_tick: int = 0

    projection: str = (
        "runtime_topology"
    )

    # -----------------------------------------------------

    def to_event(
        self,
        *,
        sequence_id: int = 0
    ) -> GraphEvent:

        return GraphEvent.build(

            GraphEventPayload(

                graph_tick=
                    self.graph_tick,

                projection=
                    self.projection,

                nodes=
                    self.nodes,

                edges=
                    self.edges
            ),

            sequence_id=
                sequence_id
        )

# =========================================================
# Runtime Transport
# =========================================================

@dataclass(slots=True)
class HHSRuntimeTransport:

    transport_tick: int = 0

    transport_flux: float = 0.0

    throughput: float = 0.0

    continuity: str = "stable"

    orientation_phase: float = 0.0

    closure_pressure: float = 0.0

    # -----------------------------------------------------

    def to_event(
        self,
        *,
        sequence_id: int = 0
    ) -> TransportEvent:

        return TransportEvent.build(

            TransportEventPayload(

                transport_tick=
                    self.transport_tick,

                transport_flux=
                    self.transport_flux,

                continuity=
                    self.continuity,

                throughput=
                    self.throughput,

                orientation_phase=
                    self.orientation_phase,

                closure_pressure=
                    self.closure_pressure
            ),

            sequence_id=
                sequence_id
        )

# =========================================================
# Runtime Replay
# =========================================================

@dataclass(slots=True)
class HHSRuntimeReplay:

    replay_tick: int = 0

    replay_status: str = "stable"

    timeline_position: int = 0

    branch_id: str = "main"

    replay_mode: str = "live"

    replay_hash72: Optional[str] = None

    # -----------------------------------------------------

    def to_event(
        self,
        *,
        sequence_id: int = 0
    ) -> ReplayEvent:

        return ReplayEvent.build(

            ReplayEventPayload(

                replay_tick=
                    self.replay_tick,

                replay_status=
                    self.replay_status,

                timeline_position=
                    self.timeline_position,

                branch_id=
                    self.branch_id,

                replay_mode=
                    self.replay_mode,

                replay_hash72=
                    self.replay_hash72
            ),

            sequence_id=
                sequence_id
        )

# =========================================================
# Runtime State
# =========================================================

@dataclass(slots=True)
class HHSRuntimeState:

    runtime_id: str = (
        "hhs_runtime"
    )

    created_ns: int = field(

        default_factory=time.time_ns
    )

    updated_ns: int = field(

        default_factory=time.time_ns
    )

    runtime_status: str = (
        RUNTIME_STATUS_BOOTING
    )

    step: int = 0

    phase: str = "bootstrap"

    closure_state: str = "stable"

    transport_flux: float = 0.0

    orientation_flux: float = 0.0

    constraint_flux: float = 0.0

    entropy_delta: float = 0.0

    receipts: List[
        HHSRuntimeReceipt
    ] = field(

        default_factory=list
    )

    graph: HHSRuntimeGraph = field(

        default_factory=
            HHSRuntimeGraph
    )

    transport: HHSRuntimeTransport = field(

        default_factory=
            HHSRuntimeTransport
    )

    replay: HHSRuntimeReplay = field(

        default_factory=
            HHSRuntimeReplay
    )

    runtime_metadata: Dict[
        str,
        Any
    ] = field(

        default_factory=dict
    )

    # =====================================================
    # Runtime Lifecycle
    # =====================================================

    def set_online(
        self
    ) -> None:

        self.runtime_status = (
            RUNTIME_STATUS_ONLINE
        )

        self.updated_ns = (
            time.time_ns()
        )

    # -----------------------------------------------------

    def halt(
        self
    ) -> None:

        self.runtime_status = (
            RUNTIME_STATUS_HALTED
        )

        self.updated_ns = (
            time.time_ns()
        )

    # -----------------------------------------------------

    def advance_step(
        self,
        *,
        phase: Optional[str] = None
    ) -> None:

        self.step += 1

        if phase is not None:

            self.phase = phase

        self.updated_ns = (
            time.time_ns()
        )

    # =====================================================
    # Receipt Layer
    # =====================================================

    def append_receipt(
        self,
        receipt:
            HHSRuntimeReceipt
    ) -> None:

        self.receipts.append(
            receipt
        )

        self.updated_ns = (
            time.time_ns()
        )

    # -----------------------------------------------------

    def latest_receipt(
        self
    ) -> Optional[
        HHSRuntimeReceipt
    ]:

        if not self.receipts:

            return None

        return self.receipts[-1]

    # -----------------------------------------------------

    def verify_receipt_chain(
        self
    ) -> bool:

        if not self.receipts:

            return True

        for receipt in self.receipts:

            if not receipt.receipt_hash72:

                return False

            if not receipt.source_hash72:

                return False

        return True

    # =====================================================
    # Runtime Events
    # =====================================================

    def to_runtime_event(
        self,
        *,
        sequence_id: int = 0
    ) -> RuntimeEvent:

        latest = self.latest_receipt()

        return RuntimeEvent.build(

            RuntimeEventPayload(

                operation=
                    "runtime_state_update",

                runtime_status=
                    self.runtime_status,

                step=
                    self.step,

                phase=
                    self.phase,

                uptime=
                    time.time(),

                receipt_hash72=(
                    latest.receipt_hash72
                    if latest
                    else None
                ),

                source_hash72=(
                    latest.source_hash72
                    if latest
                    else None
                ),

                closure_state=
                    self.closure_state,

                transport_flux=
                    self.transport_flux,

                orientation_flux=
                    self.orientation_flux,

                constraint_flux=
                    self.constraint_flux,

                entropy_delta=
                    self.entropy_delta
            ),

            sequence_id=
                sequence_id
        )

    # -----------------------------------------------------

    def to_graph_event(
        self,
        *,
        sequence_id: int = 0
    ) -> GraphEvent:

        return self.graph.to_event(

            sequence_id=
                sequence_id
        )

    # -----------------------------------------------------

    def to_transport_event(
        self,
        *,
        sequence_id: int = 0
    ) -> TransportEvent:

        return self.transport.to_event(

            sequence_id=
                sequence_id
        )

    # -----------------------------------------------------

    def to_replay_event(
        self,
        *,
        sequence_id: int = 0
    ) -> ReplayEvent:

        return self.replay.to_event(

            sequence_id=
                sequence_id
        )

    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(
        self
    ) -> Dict[str, Any]:

        return {

            "runtime_id":
                self.runtime_id,

            "created_ns":
                self.created_ns,

            "updated_ns":
                self.updated_ns,

            "runtime_status":
                self.runtime_status,

            "step":
                self.step,

            "phase":
                self.phase,

            "closure_state":
                self.closure_state,

            "transport_flux":
                self.transport_flux,

            "orientation_flux":
                self.orientation_flux,

            "constraint_flux":
                self.constraint_flux,

            "entropy_delta":
                self.entropy_delta,

            "receipts": [

                asdict(receipt)

                for receipt
                in self.receipts
            ],

            "graph":
                asdict(
                    self.graph
                ),

            "transport":
                asdict(
                    self.transport
                ),

            "replay":
                asdict(
                    self.replay
                ),

            "runtime_metadata":
                self.runtime_metadata
        }

    # -----------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        payload: Dict[str, Any]
    ) -> "HHSRuntimeState":

        state = cls(

            runtime_id=
                payload.get(
                    "runtime_id",
                    "hhs_runtime"
                ),

            created_ns=
                payload.get(
                    "created_ns",
                    time.time_ns()
                ),

            updated_ns=
                payload.get(
                    "updated_ns",
                    time.time_ns()
                ),

            runtime_status=
                payload.get(
                    "runtime_status",
                    RUNTIME_STATUS_BOOTING
                ),

            step=
                payload.get(
                    "step",
                    0
                ),

            phase=
                payload.get(
                    "phase",
                    "bootstrap"
                ),

            closure_state=
                payload.get(
                    "closure_state",
                    "stable"
                ),

            transport_flux=
                payload.get(
                    "transport_flux",
                    0.0
                ),

            orientation_flux=
                payload.get(
                    "orientation_flux",
                    0.0
                ),

            constraint_flux=
                payload.get(
                    "constraint_flux",
                    0.0
                ),

            entropy_delta=
                payload.get(
                    "entropy_delta",
                    0.0
                )
        )

        for receipt_payload in payload.get(
            "receipts",
            []
        ):

            state.receipts.append(

                HHSRuntimeReceipt(
                    **receipt_payload
                )
            )

        return state

    # =====================================================
    # Runtime Snapshot
    # =====================================================

    def snapshot(
        self
    ) -> Dict[str, Any]:

        return copy.deepcopy(
            self.to_dict()
        )

    # -----------------------------------------------------

    def restore(
        self,
        snapshot:
            Dict[str, Any]
    ) -> None:

        restored = (
            HHSRuntimeState
                .from_dict(
                    snapshot
                )
        )

        self.__dict__.update(
            restored.__dict__
        )

    # =====================================================
    # Branching
    # =====================================================

    def fork(
        self
    ) -> "HHSRuntimeState":

        return copy.deepcopy(
            self
        )

    # -----------------------------------------------------

    def merge(
        self,
        other:
            "HHSRuntimeState"
    ) -> None:

        self.step = max(

            self.step,

            other.step
        )

        self.updated_ns = (
            max(

                self.updated_ns,

                other.updated_ns
            )
        )

        self.transport_flux = max(

            self.transport_flux,

            other.transport_flux
        )

        self.orientation_flux = max(

            self.orientation_flux,

            other.orientation_flux
        )

        self.constraint_flux = max(

            self.constraint_flux,

            other.constraint_flux
        )

        existing = {

            receipt.receipt_hash72

            for receipt
            in self.receipts
        }

        for receipt in other.receipts:

            if (
                receipt.receipt_hash72
                not in existing
            ):

                self.receipts.append(
                    receipt
                )

# =========================================================
# Runtime Factory
# =========================================================

def create_runtime_state(
    *,
    runtime_id: str = "hhs_runtime"
) -> HHSRuntimeState:

    state = HHSRuntimeState(

        runtime_id=
            runtime_id
    )

    state.set_online()

    return state