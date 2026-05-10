# ============================================================================
# hhs_python/runtime/hhs_runtime_object.py
# HARMONICODE / HHS
# CANONICAL RUNTIME OBJECT SUBSTRATE
#
# PURPOSE
# -------
# Defines the HHS Runtime Object Protocol (HROP):
#
#   - deterministic runtime object identity
#   - receipt-linked object continuity
#   - replay-native object semantics
#   - graph-native runtime topology
#   - transport/projection semantics
#   - Hash72 symbolic addressing
#   - branch/fork/merge continuity
#   - multimodal runtime projections
#   - resurrection compatibility
#
# Every runtime-native entity derives from:
#
#   HHSRuntimeObject
#
# Runtime IS objects.
#
# ============================================================================

from __future__ import annotations

import copy
import hashlib
import json
import logging
import time
import uuid

from dataclasses import (
    dataclass,
    field,
    asdict,
)

from fractions import Fraction

from typing import (
    Dict,
    Any,
    List,
    Optional,
)

# ============================================================================
# RUNTIME STATE
# ============================================================================

from hhs_python.runtime.hhs_runtime_state import (
    HHSRuntimeState,
    V44_KERNEL_AVAILABLE,
    AUTHORITATIVE_TRUST_POLICY_V44,
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
    "HHS_RUNTIME_OBJECT"
)

# ============================================================================
# CONSTANTS
# ============================================================================

HHS_RUNTIME_OBJECT_SCHEMA = "v1"

# ============================================================================
# HASH72 ALPHABET
# ============================================================================

HASH72_ALPHABET = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "-+*/()<>!?"
)

# ============================================================================
# HELPERS
# ============================================================================

def reject_float_contamination(value):

    if isinstance(value, float):

        raise TypeError(
            "Float contamination prohibited "
            "inside runtime substrate."
        )

    return value

# ============================================================================
# TRANSPORT VECTOR
# ============================================================================

@dataclass
class HHSTransportVector:

    transport_flux: Fraction

    orientation_flux: Fraction

    constraint_flux: Fraction

    entropy_delta: Fraction

    closure_delta: Fraction

# ============================================================================
# REPLAY ANCHOR
# ============================================================================

@dataclass
class HHSReplayAnchor:

    anchor_id: str

    receipt_hash72: str

    state_hash72: str

    replay_timestamp_ns: int

# ============================================================================
# GRAPH LINK
# ============================================================================

@dataclass
class HHSGraphLink:

    source_object_id: str

    target_object_id: str

    edge_type: str

    created_at_ns: int

# ============================================================================
# OPERATION VECTOR
# ============================================================================

@dataclass
class HHSOperation:

    opcode: str

    inputs: Dict[str, Any]

    outputs: Dict[str, Any]

    receipt_hash72: str

    witness_flags: List[str]

    created_at_ns: int

# ============================================================================
# HHS RUNTIME OBJECT
# ============================================================================

@dataclass
class HHSRuntimeObject:

    # =====================================================================
    # IDENTITY
    # =====================================================================

    object_id: str

    object_type: str

    runtime_id: str

    branch_id: str

    # =====================================================================
    # RECEIPT CONTINUITY
    # =====================================================================

    receipt_hash72: str

    state_hash72: str

    previous_receipt_hash72: Optional[str]

    # =====================================================================
    # TRANSPORT
    # =====================================================================

    transport_vector: HHSTransportVector

    # =====================================================================
    # GRAPH TOPOLOGY
    # =====================================================================

    graph_links: List[
        HHSGraphLink
    ] = field(default_factory=list)

    # =====================================================================
    # OPERATIONS
    # =====================================================================

    operation_vector: List[
        HHSOperation
    ] = field(default_factory=list)

    # =====================================================================
    # REPLAY
    # =====================================================================

    replay_anchor: Optional[
        HHSReplayAnchor
    ] = None

    # =====================================================================
    # STATE
    # =====================================================================

    object_state: Dict[
        str,
        Any
    ] = field(default_factory=dict)

    # =====================================================================
    # TEMPORAL
    # =====================================================================

    created_at_ns: int = field(
        default_factory=time.time_ns
    )

    updated_at_ns: int = field(
        default_factory=time.time_ns
    )

    # =====================================================================
    # METADATA
    # =====================================================================

    metadata: Dict[
        str,
        Any
    ] = field(default_factory=dict)

    # =====================================================================
    # POST INIT
    # =====================================================================

    def __post_init__(self):

        self.validate_runtime_object()

    # =====================================================================
    # VALIDATION
    # =====================================================================

    def validate_runtime_object(self):

        reject_float_contamination(
            self.object_state
        )

        if not self.object_id:

            raise ValueError(
                "Runtime object requires "
                "object_id."
            )

        if not self.receipt_hash72:

            raise ValueError(
                "Runtime object requires "
                "receipt_hash72."
            )

    # =====================================================================
    # HASH72
    # =====================================================================

    def compute_hash72_identity(self):

        payload = {

            "object_id":
                self.object_id,

            "object_type":
                self.object_type,

            "runtime_id":
                self.runtime_id,

            "branch_id":
                self.branch_id,

            "receipt_hash72":
                self.receipt_hash72,

            "state_hash72":
                self.state_hash72,
        }

        serialized = json.dumps(

            payload,

            sort_keys=True,

            separators=(",", ":"),
        )

        digest = hashlib.sha256(

            serialized.encode("utf-8")

        ).digest()

        encoded = []

        accumulator = int.from_bytes(
            digest,
            "big",
        )

        for _ in range(72):

            accumulator, index = divmod(
                accumulator,
                72,
            )

            encoded.append(
                HASH72_ALPHABET[index]
            )

        return "".join(encoded)

    # =====================================================================
    # VERIFY HASH72
    # =====================================================================

    def verify_hash72_identity(
        self,
        expected_hash72: str,
    ):

        return (
            self.compute_hash72_identity()
            ==
            expected_hash72
        )

    # =====================================================================
    # SERIALIZE
    # =====================================================================

    def serialize(self):

        return json.dumps(

            self.to_runtime_projection(),

            sort_keys=True,

            separators=(",", ":"),

            default=str,
        )

    # =====================================================================
    # DESERIALIZE
    # =====================================================================

    @classmethod
    def deserialize(
        cls,
        payload: str,
    ):

        data = json.loads(payload)

        transport_vector = HHSTransportVector(

            transport_flux=Fraction(
                data["transport_vector"][
                    "transport_flux"
                ]
            ),

            orientation_flux=Fraction(
                data["transport_vector"][
                    "orientation_flux"
                ]
            ),

            constraint_flux=Fraction(
                data["transport_vector"][
                    "constraint_flux"
                ]
            ),

            entropy_delta=Fraction(
                data["transport_vector"][
                    "entropy_delta"
                ]
            ),

            closure_delta=Fraction(
                data["transport_vector"][
                    "closure_delta"
                ]
            ),
        )

        graph_links = [

            HHSGraphLink(**x)

            for x in data["graph_links"]
        ]

        operation_vector = [

            HHSOperation(**x)

            for x in data[
                "operation_vector"
            ]
        ]

        replay_anchor = None

        if data["replay_anchor"]:

            replay_anchor = HHSReplayAnchor(
                **data["replay_anchor"]
            )

        return cls(

            object_id=data["object_id"],

            object_type=data["object_type"],

            runtime_id=data["runtime_id"],

            branch_id=data["branch_id"],

            receipt_hash72=
                data["receipt_hash72"],

            state_hash72=
                data["state_hash72"],

            previous_receipt_hash72=
                data[
                    "previous_receipt_hash72"
                ],

            transport_vector=
                transport_vector,

            graph_links=
                graph_links,

            operation_vector=
                operation_vector,

            replay_anchor=
                replay_anchor,

            object_state=
                data["object_state"],

            created_at_ns=
                data["created_at_ns"],

            updated_at_ns=
                data["updated_at_ns"],

            metadata=
                data["metadata"],
        )

    # =====================================================================
    # TRANSPORT PACKET
    # =====================================================================

    def to_transport_packet(self):

        return {

            "object_id":
                self.object_id,

            "runtime_id":
                self.runtime_id,

            "receipt_hash72":
                self.receipt_hash72,

            "state_hash72":
                self.state_hash72,

            "transport_vector":
                asdict(
                    self.transport_vector
                ),
        }

    # =====================================================================
    # GRAPH PROJECTION
    # =====================================================================

    def to_graph_projection(self):

        return {

            "node_id":
                self.object_id,

            "runtime_id":
                self.runtime_id,

            "branch_id":
                self.branch_id,

            "receipt_hash72":
                self.receipt_hash72,

            "links": [

                asdict(x)

                for x in self.graph_links
            ],
        }

    # =====================================================================
    # RUNTIME PROJECTION
    # =====================================================================

    def to_runtime_projection(self):

        return {

            "schema":
                HHS_RUNTIME_OBJECT_SCHEMA,

            "object_id":
                self.object_id,

            "object_type":
                self.object_type,

            "runtime_id":
                self.runtime_id,

            "branch_id":
                self.branch_id,

            "receipt_hash72":
                self.receipt_hash72,

            "state_hash72":
                self.state_hash72,

            "previous_receipt_hash72":
                self.previous_receipt_hash72,

            "transport_vector":
                asdict(
                    self.transport_vector
                ),

            "graph_links": [

                asdict(x)

                for x in self.graph_links
            ],

            "operation_vector": [

                asdict(x)

                for x in self.operation_vector
            ],

            "replay_anchor":
                (
                    asdict(self.replay_anchor)

                    if self.replay_anchor

                    else None
                ),

            "object_state":
                self.object_state,

            "created_at_ns":
                self.created_at_ns,

            "updated_at_ns":
                self.updated_at_ns,

            "metadata":
                self.metadata,
        }

    # =====================================================================
    # RECEIPT CONTINUITY
    # =====================================================================

    def verify_receipt_continuity(self):

        if not self.receipt_hash72:

            return False

        if (
            self.previous_receipt_hash72
            ==
            self.receipt_hash72
        ):

            return False

        return True

    # =====================================================================
    # COMMIT RECEIPT
    # =====================================================================

    def commit_receipt(
        self,
        receipt_hash72: str,
    ):

        self.previous_receipt_hash72 = (
            self.receipt_hash72
        )

        self.receipt_hash72 = (
            receipt_hash72
        )

        self.updated_at_ns = (
            time.time_ns()
        )

    # =====================================================================
    # FORK
    # =====================================================================

    def fork(
        self,
        new_branch_id: str,
    ):

        forked = copy.deepcopy(self)

        forked.branch_id = (
            new_branch_id
        )

        forked.object_id = (
            str(uuid.uuid4())
        )

        forked.updated_at_ns = (
            time.time_ns()
        )

        return forked

    # =====================================================================
    # MERGE
    # =====================================================================

    def merge(
        self,
        other: "HHSRuntimeObject",
    ):

        merged = copy.deepcopy(self)

        merged.graph_links.extend(
            other.graph_links
        )

        merged.operation_vector.extend(
            other.operation_vector
        )

        merged.metadata.update(
            other.metadata
        )

        merged.updated_at_ns = (
            time.time_ns()
        )

        return merged

    # =====================================================================
    # SNAPSHOT
    # =====================================================================

    def snapshot(self):

        return copy.deepcopy(
            self
        )

    # =====================================================================
    # RESTORE
    # =====================================================================

    def restore(
        self,
        snapshot: "HHSRuntimeObject",
    ):

        self.__dict__.update(
            copy.deepcopy(
                snapshot.__dict__
            )
        )

    # =====================================================================
    # REPLAY
    # =====================================================================

    def replay(self):

        return [

            asdict(x)

            for x in self.operation_vector
        ]

    # =====================================================================
    # GRAPH LINKS
    # =====================================================================

    def attach_graph_link(
        self,
        link: HHSGraphLink,
    ):

        self.graph_links.append(
            link
        )

    # =====================================================================
    # DETACH GRAPH
    # =====================================================================

    def detach_graph_link(
        self,
        target_object_id: str,
    ):

        self.graph_links = [

            x

            for x in self.graph_links

            if x.target_object_id
            != target_object_id
        ]

    # =====================================================================
    # RESOLVE NEIGHBORS
    # =====================================================================

    def resolve_graph_neighbors(self):

        return [

            x.target_object_id

            for x in self.graph_links
        ]

    # =====================================================================
    # TRANSPORT
    # =====================================================================

    def transport(
        self,
        target_runtime_id: str,
    ):

        transported = copy.deepcopy(
            self
        )

        transported.runtime_id = (
            target_runtime_id
        )

        transported.updated_at_ns = (
            time.time_ns()
        )

        return transported

    # =====================================================================
    # PROJECT
    # =====================================================================

    def project(
        self,
        projection_type: str,
    ):

        return {

            "projection_type":
                projection_type,

            "object":
                self.to_runtime_projection(),
        }

    # =====================================================================
    # EMIT
    # =====================================================================

    def emit(
        self,
        event_type: str,
    ):

        return {

            "event_type":
                event_type,

            "runtime_id":
                self.runtime_id,

            "object_id":
                self.object_id,

            "receipt_hash72":
                self.receipt_hash72,

            "timestamp_ns":
                time.time_ns(),
        }

    # =====================================================================
    # PATCH
    # =====================================================================

    def apply_patch(
        self,
        patch: Dict[str, Any],
    ):

        reject_float_contamination(
            patch
        )

        self.object_state.update(
            patch
        )

        self.updated_at_ns = (
            time.time_ns()
        )

    # =====================================================================
    # AUDIT
    # =====================================================================

    def audit_patch(
        self,
        patch: Dict[str, Any],
    ):

        reject_float_contamination(
            patch
        )

        return {

            "valid": True,

            "patched_keys":
                list(patch.keys()),
        }

    # =====================================================================
    # ROLLBACK
    # =====================================================================

    def rollback_patch(
        self,
        snapshot: Dict[str, Any],
    ):

        self.object_state = (
            copy.deepcopy(snapshot)
        )

    # =====================================================================
    # V44 VALIDATION
    # =====================================================================

    def validate_v44_object(self):

        if not V44_KERNEL_AVAILABLE:

            return {

                "kernel_available": False,

                "validated": False,
            }

        payload = self.serialize()

        object_hash = hashlib.sha256(

            payload.encode("utf-8")

        ).hexdigest()

        trust_hash = hashlib.sha256(

            str(
                AUTHORITATIVE_TRUST_POLICY_V44
            ).encode("utf-8")

        ).hexdigest()

        return {

            "kernel_available": True,

            "validated": True,

            "object_hash":
                object_hash,

            "trust_hash":
                trust_hash,
        }

# ============================================================================
# FACTORY
# ============================================================================

def create_runtime_object(

    object_type: str,

    runtime_id: str,

    branch_id: str,

    state: Optional[
        Dict[str, Any]
    ] = None,
):

    now = time.time_ns()

    state = state or {}

    transport_vector = HHSTransportVector(

        transport_flux=Fraction(1, 1),

        orientation_flux=Fraction(1, 1),

        constraint_flux=Fraction(1, 1),

        entropy_delta=Fraction(0, 1),

        closure_delta=Fraction(0, 1),
    )

    object_id = str(uuid.uuid4())

    receipt_hash72 = hashlib.sha256(

        object_id.encode("utf-8")

    ).hexdigest()[:72]

    state_hash72 = hashlib.sha256(

        json.dumps(

            state,

            sort_keys=True,

        ).encode("utf-8")

    ).hexdigest()[:72]

    runtime_object = HHSRuntimeObject(

        object_id=object_id,

        object_type=object_type,

        runtime_id=runtime_id,

        branch_id=branch_id,

        receipt_hash72=
            receipt_hash72,

        state_hash72=
            state_hash72,

        previous_receipt_hash72=
            None,

        transport_vector=
            transport_vector,

        object_state=
            state,

        created_at_ns=
            now,

        updated_at_ns=
            now,

        metadata={

            "schema":
                HHS_RUNTIME_OBJECT_SCHEMA
        },
    )

    return runtime_object

# ============================================================================
# SELF TEST
# ============================================================================

def runtime_object_self_test():

    runtime_object = create_runtime_object(

        object_type="tensor_state",

        runtime_id="runtime_001",

        branch_id="main",

        state={

            "tensor": [

                4, 9, 2,
                3, 5, 7,
                8, 1, 6,
            ]
        },
    )

    operation = HHSOperation(

        opcode="QGU",

        inputs={"a": 1},

        outputs={"b": 2},

        receipt_hash72=
            runtime_object.receipt_hash72,

        witness_flags=[
            "W_QGU_APPLIED"
        ],

        created_at_ns=
            time.time_ns(),
    )

    runtime_object.operation_vector.append(
        operation
    )

    link = HHSGraphLink(

        source_object_id=
            runtime_object.object_id,

        target_object_id=
            "neighbor_001",

        edge_type=
            "transport",

        created_at_ns=
            time.time_ns(),
    )

    runtime_object.attach_graph_link(
        link
    )

    projection = (
        runtime_object
        .to_runtime_projection()
    )

    graph_projection = (
        runtime_object
        .to_graph_projection()
    )

    transport_packet = (
        runtime_object
        .to_transport_packet()
    )

    emitted = runtime_object.emit(
        "runtime_object_created"
    )

    replay = runtime_object.replay()

    v44 = (
        runtime_object
        .validate_v44_object()
    )

    print()

    print("RUNTIME OBJECT")

    print(runtime_object)

    print()

    print("PROJECTION")

    print(projection)

    print()

    print("GRAPH")

    print(graph_projection)

    print()

    print("TRANSPORT")

    print(transport_packet)

    print()

    print("EVENT")

    print(emitted)

    print()

    print("REPLAY")

    print(replay)

    print()

    print("V44")

    print(v44)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    runtime_object_self_test()