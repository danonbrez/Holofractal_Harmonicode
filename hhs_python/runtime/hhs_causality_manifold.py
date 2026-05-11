# hhs_python/runtime/hhs_causality_manifold.py
#
# HHS / HARMONICODE
# Recursive Reversible Causality Manifold
#
# Canonical Runtime OS Topology Layer
#
# Runtime Principle:
#
#   local tensor excitation
#   →
#   cluster propagation
#   →
#   reciprocal validation
#   →
#   invariant reconciliation
#   →
#   reversibility validation
#   →
#   canonical manifold stabilization
#
# This file governs:
#
#   - recursive manifold evolution
#   - Tensor81 propagation
#   - HASH216 reciprocal closure field
#   - 41-channel Lo Shu entanglement topology
#   - distributed topology continuity
#   - replay-native causality evolution
#
# Runtime Primitive:
#
#   recursive reversible manifold excitation
#

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from fractions import Fraction
import hashlib
import json
import time

from hhs_python.runtime.hhs_multimodal_transition_tensor81 import (
    HHSMultimodalTransitionTensor81,
)

from hhs_python.runtime.hhs_global_reversibility_gate import (
    HHSGlobalReversibilityGate,
    HHSGateValidationResult,
)

# ============================================================
# CONSTANTS
# ============================================================

GRID_SIZE = 81
UNIQUE_CHANNELS = 41
OPERATIONAL_DIMENSIONS = 72
GLOBAL_INVARIANTS = 9

HASH216_WIDTH = 216


# ============================================================
# HASH216
# ============================================================

def _hash216(data: str) -> str:
    """
    Canonical HASH216 projection layer.
    """

    h1 = hashlib.sha512(data.encode()).hexdigest()
    h2 = hashlib.sha256(data.encode()).hexdigest()

    merged = h1 + h2

    return merged[:HASH216_WIDTH]


# ============================================================
# CAUSALITY NODE
# ============================================================

@dataclass(frozen=True)
class HHSCausalityNode:
    """
    Local reversible excitation inside the manifold.

    IMPORTANT:
        this is NOT a simple graph vertex.

    This is:
        a recursive topology excitation.
    """

    node_id: str

    tensor_hash216: str

    cluster_channels: Tuple[int, ...]

    reciprocal_neighbors: Tuple[str, ...]

    invariant_projection: Tuple[str, ...]

    active: bool = True

    readable: bool = True

    reversible: bool = True

    timestamp_ns: int = field(
        default_factory=time.time_ns
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.active
            and self.readable
            and self.reversible
        )


# ============================================================
# CLUSTER FIELD
# ============================================================

@dataclass
class HHSClusterField:
    """
    41-channel recursive Lo Shu entanglement field.
    """

    cluster_id: int

    active_nodes: Set[str] = field(
        default_factory=set
    )

    reciprocal_clusters: Set[int] = field(
        default_factory=set
    )

    cluster_hash216: str = ""

    stable: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:
        return self.stable


# ============================================================
# HASH216 FIELD
# ============================================================

@dataclass
class HHSHash216Field:
    """
    Global reciprocal closure field.

    Canonical identity:

        Hash216 = u^72 + v^72 = C^216
    """

    forward_orbit_hash: str

    reciprocal_orbit_hash: str

    closure_hash216: str

    stable: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.stable
            and bool(self.forward_orbit_hash)
            and bool(self.reciprocal_orbit_hash)
            and bool(self.closure_hash216)
        )


# ============================================================
# MANIFOLD EVENT
# ============================================================

@dataclass(frozen=True)
class HHSManifoldEvent:
    """
    Canonical manifold propagation event.
    """

    event_id: str

    source_tensor: str

    target_clusters: Tuple[int, ...]

    propagation_hash216: str

    reversible: bool = True

    topology_equivalent: bool = True

    timestamp_ns: int = field(
        default_factory=time.time_ns
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.reversible
            and self.topology_equivalent
        )


# ============================================================
# CAUSALITY MANIFOLD
# ============================================================

class HHSCausalityManifold:
    """
    Recursive reversible causality field.

    Runtime primitive:
        recursive manifold excitation propagation.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.reversibility_gate = (
            HHSGlobalReversibilityGate()
        )

        # tensor registry
        self.tensor_registry: Dict[
            str,
            HHSMultimodalTransitionTensor81
        ] = {}

        # causality nodes
        self.causality_nodes: Dict[
            str,
            HHSCausalityNode
        ] = {}

        # 41 recursive entanglement channels
        self.cluster_fields: Dict[
            int,
            HHSClusterField
        ] = {}

        # manifold events
        self.manifold_events: List[
            HHSManifoldEvent
        ] = []

        # replay-native transition lineage
        self.transition_chain: List[str] = []

        # distributed synchronization field
        self.distributed_field: Dict[
            str,
            str
        ] = {}

        # workspace projection field
        self.workspace_field: Dict[
            str,
            str
        ] = {}

        # transport propagation field
        self.transport_field: Dict[
            str,
            str
        ] = {}

        # HASH216 reciprocal closure field
        self.hash216_field = HHSHash216Field(
            forward_orbit_hash="",
            reciprocal_orbit_hash="",
            closure_hash216="",
        )

        # initialize 41 clusters
        self._initialize_clusters()

    # ========================================================
    # CLUSTER INIT
    # ========================================================

    def _initialize_clusters(self):

        for cluster_id in range(
            UNIQUE_CHANNELS
        ):

            self.cluster_fields[
                cluster_id
            ] = HHSClusterField(
                cluster_id=cluster_id
            )

    # ========================================================
    # REGISTER TENSOR
    # ========================================================

    def register_tensor(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> bool:
        """
        Register local manifold excitation.
        """

        result = (
            self.reversibility_gate
            .validate_tensor(tensor)
        )

        if not result.validate():

            return False

        tensor_hash = tensor.global_hash216()

        self.tensor_registry[
            tensor_hash
        ] = tensor

        node = HHSCausalityNode(
            node_id=tensor_hash,
            tensor_hash216=tensor_hash,
            cluster_channels=tuple(
                range(UNIQUE_CHANNELS)
            ),
            reciprocal_neighbors=tuple(),
            invariant_projection=tuple(
                inv.invariant_name
                for inv in tensor.invariant_cells
            ),
        )

        self.causality_nodes[
            tensor_hash
        ] = node

        self.transition_chain.append(
            tensor_hash
        )

        self._propagate_clusters(
            tensor
        )

        self._update_hash216_field()

        return True

    # ========================================================
    # PROPAGATION
    # ========================================================

    def _propagate_clusters(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ):
        """
        Recursive manifold excitation propagation.
        """

        tensor_hash = tensor.global_hash216()

        for channel in tensor.entanglement_channels:

            cluster_id = (
                channel.channel_id
            )

            if cluster_id not in self.cluster_fields:
                continue

            cluster = self.cluster_fields[
                cluster_id
            ]

            cluster.active_nodes.add(
                tensor_hash
            )

            cluster.cluster_hash216 = (
                self._cluster_hash(
                    cluster
                )
            )

            event = HHSManifoldEvent(
                event_id=_hash216(
                    tensor_hash
                    + str(cluster_id)
                ),
                source_tensor=tensor_hash,
                target_clusters=(
                    cluster_id,
                ),
                propagation_hash216=(
                    cluster.cluster_hash216
                ),
            )

            self.manifold_events.append(
                event
            )

    # ========================================================
    # HASH216 FIELD UPDATE
    # ========================================================

    def _update_hash216_field(
        self,
    ):
        """
        Canonical reciprocal closure update.

        Hash216 = u^72 + v^72 = C^216
        """

        forward = "".join(
            sorted(
                self.tensor_registry.keys()
            )
        )

        reciprocal = "".join(
            reversed(
                sorted(
                    self.tensor_registry.keys()
                )
            )
        )

        closure = _hash216(
            forward + reciprocal
        )

        self.hash216_field = (
            HHSHash216Field(
                forward_orbit_hash=_hash216(
                    forward
                ),
                reciprocal_orbit_hash=_hash216(
                    reciprocal
                ),
                closure_hash216=closure,
            )
        )

    # ========================================================
    # CLUSTER HASH
    # ========================================================

    def _cluster_hash(
        self,
        cluster: HHSClusterField,
    ) -> str:

        payload = {
            "cluster_id": cluster.cluster_id,
            "nodes": sorted(
                list(cluster.active_nodes)
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # GLOBAL VALIDATION
    # ========================================================

    def validate_manifold(
        self,
    ) -> bool:
        """
        Universal manifold admissibility.
        """

        if not self.hash216_field.validate():
            return False

        for node in (
            self.causality_nodes.values()
        ):

            if not node.validate():
                return False

        for cluster in (
            self.cluster_fields.values()
        ):

            if not cluster.validate():
                return False

        for event in self.manifold_events:

            if not event.validate():
                return False

        return True

    # ========================================================
    # MANIFOLD CLOSURE
    # ========================================================

    def manifold_hash216(
        self,
    ) -> str:
        """
        Global manifold closure identity.
        """

        payload = {
            "tensor_registry": sorted(
                self.tensor_registry.keys()
            ),
            "clusters": {
                k: sorted(
                    list(v.active_nodes)
                )
                for k, v in (
                    self.cluster_fields.items()
                )
            },
            "transition_chain": (
                self.transition_chain
            ),
            "hash216_field": (
                self.hash216_field.closure_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # GLOBAL READABILITY
    # ========================================================

    def globally_readable(
        self,
    ) -> bool:
        """
        Universal semantic readability invariant.
        """

        for tensor in (
            self.tensor_registry.values()
        ):

            if not tensor.globally_readable():
                return False

        return True

    # ========================================================
    # REVERSIBILITY
    # ========================================================

    def reversible(
        self,
    ) -> bool:
        """
        Universal manifold reversibility.
        """

        for tensor in (
            self.tensor_registry.values()
        ):

            if not tensor.reversible():
                return False

        return True

    # ========================================================
    # REPLAY CONTINUITY
    # ========================================================

    def replay_admissible(
        self,
    ) -> bool:
        """
        Replay-native causality continuity.
        """

        for tensor in (
            self.tensor_registry.values()
        ):

            if not (
                tensor
                .transition_proof
                .replay_admissible
            ):
                return False

        return True

    # ========================================================
    # TOPOLOGY EQUIVALENCE
    # ========================================================

    def topology_equivalent(
        self,
    ) -> bool:
        """
        Recursive topology continuity invariant.
        """

        for tensor in (
            self.tensor_registry.values()
        ):

            if not (
                tensor
                .topology_equivalent()
            ):
                return False

        return True

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical manifold causality receipt.
        """

        return {
            "manifold_hash216": (
                self.manifold_hash216()
            ),
            "tensor_count": len(
                self.tensor_registry
            ),
            "cluster_count": len(
                self.cluster_fields
            ),
            "event_count": len(
                self.manifold_events
            ),
            "globally_readable": (
                self.globally_readable()
            ),
            "reversible": (
                self.reversible()
            ),
            "replay_admissible": (
                self.replay_admissible()
            ),
            "topology_equivalent": (
                self.topology_equivalent()
            ),
            "valid": (
                self.validate_manifold()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }