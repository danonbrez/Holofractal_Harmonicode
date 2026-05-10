# ============================================================================
# hhs_python/runtime/runtime_object_registry.py
# HARMONICODE / HHS
# CANONICAL RUNTIME OBJECT AUTHORITY
#
# PURPOSE
# -------
# Canonical deterministic runtime object registry for:
#
#   - runtime object discovery
#   - Hash72 object addressing
#   - replay-aware object indexing
#   - graph-native object resolution
#   - distributed runtime synchronization
#   - transport-routed object projection
#   - namespace topology governance
#   - registry resurrection continuity
#   - v44.2 kernel continuity enforcement
#
# Runtime object discovery IS runtime continuity.
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
from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Dict,
    Any,
    List,
    Optional,
    Set,
)

# ============================================================================
# RUNTIME OBJECTS
# ============================================================================

from hhs_python.runtime.hhs_runtime_object import (

    HHSRuntimeObject,

    HHSGraphLink,

    HHSReplayAnchor,

)

# ============================================================================
# OPTIONAL V44.2 KERNEL
# ============================================================================

try:

    from HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked_7 import (

        AUTHORITATIVE_TRUST_POLICY_V44,

        security_hash72_v44,

        Tensor,

        Manifold9,
    )

    V44_KERNEL_AVAILABLE = True

except Exception:

    AUTHORITATIVE_TRUST_POLICY_V44 = None

    security_hash72_v44 = None

    Tensor = None

    Manifold9 = None

    V44_KERNEL_AVAILABLE = False

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(
    "HHS_RUNTIME_OBJECT_REGISTRY"
)

# ============================================================================
# CONSTANTS
# ============================================================================

REGISTRY_SCHEMA_VERSION = "v1"

# ============================================================================
# NAMESPACE
# ============================================================================

@dataclass
class HHSRuntimeNamespace:

    namespace_id: str

    namespace_type: str

    runtime_id: str

    branch_id: str

    object_ids: Set[str] = field(
        default_factory=set
    )

    created_at_ns: int = field(
        default_factory=time.time_ns
    )

# ============================================================================
# REGISTRY SNAPSHOT
# ============================================================================

@dataclass
class HHSRegistrySnapshot:

    snapshot_id: str

    registry_hash72: str

    object_count: int

    created_at_ns: int

    object_ids: List[str]

    namespace_ids: List[str]

# ============================================================================
# REGISTRY
# ============================================================================

class HHSRuntimeObjectRegistry:

    """
    Canonical deterministic runtime object authority.
    """

    def __init__(self):

        self.lock = threading.RLock()

        # ================================================================
        # OBJECT STORAGE
        # ================================================================

        self.objects: Dict[
            str,
            HHSRuntimeObject
        ] = {}

        # ================================================================
        # HASH72 INDEX
        # ================================================================

        self.hash72_index: Dict[
            str,
            str
        ] = {}

        # ================================================================
        # RUNTIME INDEX
        # ================================================================

        self.runtime_index = defaultdict(set)

        # ================================================================
        # BRANCH INDEX
        # ================================================================

        self.branch_index = defaultdict(set)

        # ================================================================
        # RECEIPT INDEX
        # ================================================================

        self.receipt_index = defaultdict(set)

        # ================================================================
        # SNAPSHOT INDEX
        # ================================================================

        self.snapshot_index = defaultdict(set)

        # ================================================================
        # REPLAY INDEX
        # ================================================================

        self.replay_anchor_index = {}

        # ================================================================
        # GRAPH TOPOLOGY
        # ================================================================

        self.graph_topology = defaultdict(set)

        # ================================================================
        # NAMESPACES
        # ================================================================

        self.namespaces: Dict[
            str,
            HHSRuntimeNamespace
        ] = {}

    # =====================================================================
    # REGISTER
    # =====================================================================

    def register_object(
        self,
        runtime_object: HHSRuntimeObject,
    ):

        with self.lock:

            self.objects[
                runtime_object.object_id
            ] = runtime_object

            object_hash72 = (
                runtime_object
                .compute_hash72_identity()
            )

            self.hash72_index[
                object_hash72
            ] = runtime_object.object_id

            self.runtime_index[
                runtime_object.runtime_id
            ].add(
                runtime_object.object_id
            )

            self.branch_index[
                runtime_object.branch_id
            ].add(
                runtime_object.object_id
            )

            self.receipt_index[
                runtime_object.receipt_hash72
            ].add(
                runtime_object.object_id
            )

            if runtime_object.replay_anchor:

                self.replay_anchor_index[
                    runtime_object
                    .replay_anchor
                    .anchor_id
                ] = runtime_object.object_id

            for link in runtime_object.graph_links:

                self.graph_topology[
                    runtime_object.object_id
                ].add(
                    link.target_object_id
                )

            logger.info(
                f"Runtime object registered: "
                f"{runtime_object.object_id}"
            )

            return object_hash72

    # =====================================================================
    # RESOLVE OBJECT
    # =====================================================================

    def resolve_object(
        self,
        object_id: str,
    ):

        return self.objects.get(
            object_id
        )

    # =====================================================================
    # RESOLVE HASH72
    # =====================================================================

    def resolve_hash72(
        self,
        hash72_identity: str,
    ):

        object_id = self.hash72_index.get(
            hash72_identity
        )

        if not object_id:

            return None

        return self.resolve_object(
            object_id
        )

    # =====================================================================
    # RESOLVE RUNTIME
    # =====================================================================

    def resolve_runtime(
        self,
        runtime_id: str,
    ):

        return [

            self.objects[x]

            for x in self.runtime_index[
                runtime_id
            ]
        ]

    # =====================================================================
    # RESOLVE BRANCH
    # =====================================================================

    def resolve_branch(
        self,
        branch_id: str,
    ):

        return [

            self.objects[x]

            for x in self.branch_index[
                branch_id
            ]
        ]

    # =====================================================================
    # RESOLVE REPLAY ANCHOR
    # =====================================================================

    def resolve_replay_anchor(
        self,
        anchor_id: str,
    ):

        object_id = (
            self.replay_anchor_index.get(
                anchor_id
            )
        )

        if not object_id:

            return None

        return self.resolve_object(
            object_id
        )

    # =====================================================================
    # RESOLVE RECEIPT LINEAGE
    # =====================================================================

    def resolve_receipt_lineage(
        self,
        receipt_hash72: str,
    ):

        object_ids = self.receipt_index[
            receipt_hash72
        ]

        return [

            self.objects[x]

            for x in object_ids
        ]

    # =====================================================================
    # RESOLVE SNAPSHOT
    # =====================================================================

    def resolve_snapshot_lineage(
        self,
        snapshot_hash72: str,
    ):

        object_ids = self.snapshot_index[
            snapshot_hash72
        ]

        return [

            self.objects[x]

            for x in object_ids
        ]

    # =====================================================================
    # GRAPH NEIGHBORS
    # =====================================================================

    def resolve_neighbors(
        self,
        object_id: str,
    ):

        neighbor_ids = self.graph_topology[
            object_id
        ]

        return [

            self.objects[x]

            for x in neighbor_ids

            if x in self.objects
        ]

    # =====================================================================
    # GRAPH CLUSTER
    # =====================================================================

    def resolve_graph_cluster(
        self,
        object_id: str,
    ):

        visited = set()

        queue = [object_id]

        cluster = []

        while queue:

            current = queue.pop(0)

            if current in visited:
                continue

            visited.add(current)

            cluster.append(current)

            neighbors = self.graph_topology[
                current
            ]

            queue.extend(neighbors)

        return [

            self.objects[x]

            for x in cluster

            if x in self.objects
        ]

    # =====================================================================
    # TRANSPORT ROUTES
    # =====================================================================

    def resolve_transport_routes(
        self,
        source_object_id: str,
    ):

        return list(

            self.graph_topology[
                source_object_id
            ]
        )

    # =====================================================================
    # DISTRIBUTED OBJECT
    # =====================================================================

    def resolve_distributed_object(
        self,
        object_id: str,
    ):

        return self.resolve_object(
            object_id
        )

    # =====================================================================
    # SYNCHRONIZE REGISTRY
    # =====================================================================

    def synchronize_registry(
        self,
        remote_registry: "HHSRuntimeObjectRegistry",
    ):

        synchronized = []

        for object_id, runtime_object in (
            remote_registry.objects.items()
        ):

            if object_id not in self.objects:

                self.register_object(
                    runtime_object
                )

                synchronized.append(
                    object_id
                )

        return synchronized

    # =====================================================================
    # VERIFY EQUIVALENCE
    # =====================================================================

    def verify_registry_equivalence(
        self,
        other_registry:
            "HHSRuntimeObjectRegistry",
    ):

        local_hash = (
            self.compute_registry_hash72()
        )

        remote_hash = (
            other_registry
            .compute_registry_hash72()
        )

        return (
            local_hash == remote_hash
        )

    # =====================================================================
    # CREATE NAMESPACE
    # =====================================================================

    def create_namespace(

        self,

        namespace_type: str,

        runtime_id: str,

        branch_id: str,
    ):

        namespace = HHSRuntimeNamespace(

            namespace_id=str(uuid.uuid4()),

            namespace_type=
                namespace_type,

            runtime_id=
                runtime_id,

            branch_id=
                branch_id,
        )

        self.namespaces[
            namespace.namespace_id
        ] = namespace

        return namespace

    # =====================================================================
    # ATTACH NAMESPACE
    # =====================================================================

    def attach_to_namespace(

        self,

        namespace_id: str,

        object_id: str,
    ):

        namespace = self.namespaces[
            namespace_id
        ]

        namespace.object_ids.add(
            object_id
        )

    # =====================================================================
    # TRANSPORT ROUTING
    # =====================================================================

    def route_transport_projection(
        self,
        object_id: str,
    ):

        runtime_object = (
            self.resolve_object(
                object_id
            )
        )

        if not runtime_object:

            return None

        return (
            runtime_object
            .to_transport_packet()
        )

    # =====================================================================
    # REPLAY ROUTING
    # =====================================================================

    def route_replay_projection(
        self,
        object_id: str,
    ):

        runtime_object = (
            self.resolve_object(
                object_id
            )
        )

        if not runtime_object:

            return None

        return runtime_object.replay()

    # =====================================================================
    # MULTIMODAL ROUTING
    # =====================================================================

    def route_multimodal_projection(
        self,
        object_id: str,
    ):

        runtime_object = (
            self.resolve_object(
                object_id
            )
        )

        if not runtime_object:

            return None

        return {

            "object_id":
                runtime_object.object_id,

            "object_type":
                runtime_object.object_type,

            "runtime_projection":
                runtime_object
                .to_runtime_projection(),

            "graph_projection":
                runtime_object
                .to_graph_projection(),
        }

    # =====================================================================
    # REPLAY VALIDATION
    # =====================================================================

    def verify_registry_replay(self):

        for runtime_object in (
            self.objects.values()
        ):

            if not (
                runtime_object
                .verify_receipt_continuity()
            ):

                return False

        return True

    # =====================================================================
    # RECONSTRUCT REGISTRY
    # =====================================================================

    def reconstruct_registry_state(self):

        return {

            object_id:

            runtime_object
            .to_runtime_projection()

            for object_id, runtime_object

            in self.objects.items()
        }

    # =====================================================================
    # REHYDRATE
    # =====================================================================

    def rehydrate_registry(
        self,
        payload: Dict[str, Any],
    ):

        for object_payload in (
            payload.values()
        ):

            runtime_object = (
                HHSRuntimeObject
                .deserialize(

                    json.dumps(
                        object_payload
                    )
                )
            )

            self.register_object(
                runtime_object
            )

    # =====================================================================
    # REGISTRY HASH72
    # =====================================================================

    def compute_registry_hash72(self):

        projection = (
            self.reconstruct_registry_state()
        )

        serialized = json.dumps(

            projection,

            sort_keys=True,

            separators=(",", ":"),
        )

        digest = hashlib.sha256(

            serialized.encode("utf-8")

        ).hexdigest()

        return digest[:72]

    # =====================================================================
    # SNAPSHOT
    # =====================================================================

    def snapshot_registry(self):

        registry_hash72 = (
            self.compute_registry_hash72()
        )

        return HHSRegistrySnapshot(

            snapshot_id=str(uuid.uuid4()),

            registry_hash72=
                registry_hash72,

            object_count=
                len(self.objects),

            created_at_ns=
                time.time_ns(),

            object_ids=
                list(self.objects.keys()),

            namespace_ids=
                list(self.namespaces.keys()),
        )

    # =====================================================================
    # REGISTRY PROJECTION
    # =====================================================================

    def to_registry_projection(self):

        return {

            "schema":
                REGISTRY_SCHEMA_VERSION,

            "object_count":
                len(self.objects),

            "namespace_count":
                len(self.namespaces),

            "registry_hash72":
                self.compute_registry_hash72(),
        }

    # =====================================================================
    # GRAPH REGISTRY
    # =====================================================================

    def to_graph_registry_projection(self):

        return {

            "nodes":
                list(self.objects.keys()),

            "edges": {

                k: list(v)

                for k, v in (
                    self.graph_topology.items()
                )
            },
        }

    # =====================================================================
    # TRANSPORT PACKET
    # =====================================================================

    def to_transport_registry_packet(self):

        return {

            "registry_hash72":
                self.compute_registry_hash72(),

            "object_count":
                len(self.objects),

            "runtime_ids":

                list(
                    self.runtime_index.keys()
                ),
        }

    # =====================================================================
    # V44 VALIDATION
    # =====================================================================

    def validate_v44_registry(self):

        if not V44_KERNEL_AVAILABLE:

            return {

                "kernel_available": False,

                "validated": False,
            }

        registry_hash = hashlib.sha256(

            json.dumps(

                self.to_registry_projection(),

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

            "registry_hash":
                registry_hash,

            "trust_hash":
                trust_hash,
        }

# ============================================================================
# GLOBAL REGISTRY
# ============================================================================

runtime_object_registry = (
    HHSRuntimeObjectRegistry()
)

# ============================================================================
# SELF TEST
# ============================================================================

def runtime_object_registry_self_test():

    from hhs_python.runtime.hhs_runtime_object import (
        create_runtime_object
    )

    runtime_object = create_runtime_object(

        object_type="tensor_field",

        runtime_id="runtime_001",

        branch_id="main",

        state={

            "field": [
                4, 9, 2,
                3, 5, 7,
                8, 1, 6,
            ]
        },
    )

    hash72 = (
        runtime_object_registry
        .register_object(
            runtime_object
        )
    )

    resolved = (
        runtime_object_registry
        .resolve_hash72(
            hash72
        )
    )

    namespace = (
        runtime_object_registry
        .create_namespace(

            namespace_type=
                "workspace",

            runtime_id=
                "runtime_001",

            branch_id=
                "main",
        )
    )

    runtime_object_registry.attach_to_namespace(

        namespace.namespace_id,

        runtime_object.object_id,
    )

    snapshot = (
        runtime_object_registry
        .snapshot_registry()
    )

    projection = (
        runtime_object_registry
        .to_registry_projection()
    )

    graph_projection = (
        runtime_object_registry
        .to_graph_registry_projection()
    )

    transport_packet = (
        runtime_object_registry
        .to_transport_registry_packet()
    )

    v44 = (
        runtime_object_registry
        .validate_v44_registry()
    )

    print()

    print("HASH72")

    print(hash72)

    print()

    print("RESOLVED")

    print(resolved)

    print()

    print("NAMESPACE")

    print(namespace)

    print()

    print("SNAPSHOT")

    print(snapshot)

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

    print("V44")

    print(v44)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    runtime_object_registry_self_test()