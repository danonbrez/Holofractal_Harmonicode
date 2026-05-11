# hhs_python/runtime/hhs_distributed_reversibility_mesh.py
#
# HHS / HARMONICODE
# Distributed Reversibility Mesh
#
# Canonical Runtime OS Distributed Synchronization Layer
#
# Runtime Principle:
#
#   distributed synchronization
#   =
#   reconstructible causality equivalence
#
# NOT:
#
#   replicated serialized state
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward distributed traversal
#   v^72 = reciprocal distributed reconstruction
#   C^216 = distributed manifold closure equivalence
#
# Runtime Primitive:
#
#   distributed reconstructible causality equivalence
#

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
import hashlib
import json
import time

# ============================================================
# CONSTANTS
# ============================================================

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
# MESH WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSMeshWitness:
    """
    Canonical distributed causality witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    reconstructible: bool = True
    reversible: bool = True
    topology_equivalent: bool = True
    globally_readable: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.reconstructible
            and self.reversible
            and self.topology_equivalent
            and self.globally_readable
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# DISTRIBUTED NODE
# ============================================================

@dataclass(frozen=True)
class HHSDistributedReversibilityNode:
    """
    Canonical distributed causality carrier.

    A node is:
        a distributed manifold projection surface.
    """

    node_id: str

    # ========================================================
    # FIELD CLOSURES
    # ========================================================

    identity_field_hash216: str
    replay_field_hash216: str
    mutation_field_hash216: str
    topology_field_hash216: str

    # ========================================================
    # DISTRIBUTED TRAVERSAL
    # ========================================================

    forward_mesh_hash216: str
    reciprocal_mesh_hash216: str

    # ========================================================
    # DISTRIBUTED FLAGS
    # ========================================================

    reconstructible: bool = True
    reversible: bool = True
    mesh_equivalent: bool = True
    topology_equivalent: bool = True
    globally_readable: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    replay_witness: Optional[
        HHSMeshWitness
    ] = None

    identity_witness: Optional[
        HHSMeshWitness
    ] = None

    topology_witness: Optional[
        HHSMeshWitness
    ] = None

    reciprocal_witness: Optional[
        HHSMeshWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    distributed_proof_hash216: str = ""

    # ========================================================
    # TIMESTAMP
    # ========================================================

    timestamp_ns: int = field(
        default_factory=time.time_ns
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(self) -> bool:
        """
        Universal distributed admissibility validation.
        """

        if not self.reconstructible:
            return False

        if not self.reversible:
            return False

        if not self.mesh_equivalent:
            return False

        if not self.topology_equivalent:
            return False

        if not self.globally_readable:
            return False

        witnesses = [
            self.replay_witness,
            self.identity_witness,
            self.topology_witness,
            self.reciprocal_witness,
        ]

        for witness in witnesses:

            if witness is None:
                continue

            if not witness.validate():
                return False

        return True

    # ========================================================
    # HASH216 CLOSURE
    # ========================================================

    def closure_hash216(self) -> str:
        """
        Canonical distributed equivalence operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "node_id": self.node_id,
            "identity_field": (
                self.identity_field_hash216
            ),
            "replay_field": (
                self.replay_field_hash216
            ),
            "mutation_field": (
                self.mutation_field_hash216
            ),
            "topology_field": (
                self.topology_field_hash216
            ),
            "forward": (
                self.forward_mesh_hash216
            ),
            "reciprocal": (
                self.reciprocal_mesh_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Distributed reconstruction invariant.
        """

        return (
            self.reconstructible
            and self.validate()
        )

    # ========================================================
    # REVERSIBILITY
    # ========================================================

    def verify_reversibility(
        self,
    ) -> bool:
        """
        Reciprocal distributed traversal invariant.
        """

        return (
            self.reversible
            and self.validate()
        )

    # ========================================================
    # MESH EQUIVALENCE
    # ========================================================

    def verify_mesh_equivalence(
        self,
    ) -> bool:
        """
        Distributed causality equivalence invariant.
        """

        return (
            self.mesh_equivalent
            and self.validate()
        )

    # ========================================================
    # TOPOLOGY EQUIVALENCE
    # ========================================================

    def verify_topology_equivalence(
        self,
    ) -> bool:
        """
        Distributed topology continuity invariant.
        """

        return (
            self.topology_equivalent
            and self.validate()
        )

    # ========================================================
    # GLOBAL READABILITY
    # ========================================================

    def verify_global_readability(
        self,
    ) -> bool:
        """
        Semantic distributed continuity invariant.
        """

        return (
            self.globally_readable
            and self.validate()
        )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Replay-admissible deterministic serialization.
        """

        return {
            "node_id": self.node_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "distributed_proof_hash216": (
                self.distributed_proof_hash216
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "reversible": (
                self.verify_reversibility()
            ),
            "mesh_equivalent": (
                self.verify_mesh_equivalence()
            ),
            "topology_equivalent": (
                self.verify_topology_equivalence()
            ),
            "globally_readable": (
                self.verify_global_readability()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical distributed mesh receipt.
        """

        return {
            "node_id": self.node_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "distributed_proof_hash216": (
                self.distributed_proof_hash216
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# DISTRIBUTED REVERSIBILITY MESH
# ============================================================

class HHSDistributedReversibilityMesh:
    """
    Canonical Runtime OS distributed synchronization field.

    Distributed execution is:
        reconstructible causality equivalence.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.mesh_nodes: Dict[
            str,
            HHSDistributedReversibilityNode
        ] = {}

        self.mesh_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.identity_mesh_field: Dict[
            str,
            str
        ] = {}

        self.replay_mesh_field: Dict[
            str,
            str
        ] = {}

        self.mutation_mesh_field: Dict[
            str,
            str
        ] = {}

        self.topology_mesh_field: Dict[
            str,
            str
        ] = {}

        self.mesh_neighbors: Dict[
            str,
            Set[str]
        ] = {}

    # ========================================================
    # REGISTER NODE
    # ========================================================

    def register_node(
        self,
        node: HHSDistributedReversibilityNode,
    ) -> bool:
        """
        Register distributed manifold node.
        """

        if not node.validate():
            return False

        self.mesh_nodes[
            node.node_id
        ] = node

        if (
            node.node_id
            not in self.mesh_lineage
        ):

            self.mesh_lineage[
                node.node_id
            ] = []

        self.mesh_lineage[
            node.node_id
        ].append(
            node.closure_hash216()
        )

        self.identity_mesh_field[
            node.node_id
        ] = (
            node.identity_field_hash216
        )

        self.replay_mesh_field[
            node.node_id
        ] = (
            node.replay_field_hash216
        )

        self.mutation_mesh_field[
            node.node_id
        ] = (
            node.mutation_field_hash216
        )

        self.topology_mesh_field[
            node.node_id
        ] = (
            node.topology_field_hash216
        )

        if (
            node.node_id
            not in self.mesh_neighbors
        ):

            self.mesh_neighbors[
                node.node_id
            ] = set()

        return True

    # ========================================================
    # CONNECT NODES
    # ========================================================

    def connect_nodes(
        self,
        node_a: str,
        node_b: str,
    ) -> bool:
        """
        Establish reciprocal distributed adjacency.
        """

        if node_a not in self.mesh_nodes:
            return False

        if node_b not in self.mesh_nodes:
            return False

        self.mesh_neighbors[
            node_a
        ].add(node_b)

        self.mesh_neighbors[
            node_b
        ].add(node_a)

        return True

    # ========================================================
    # VALIDATE FIELD
    # ========================================================

    def validate_mesh(
        self,
    ) -> bool:
        """
        Universal distributed reversibility validation.
        """

        for node in (
            self.mesh_nodes.values()
        ):

            if not node.validate():
                return False

        return True

    # ========================================================
    # MESH EQUIVALENCE
    # ========================================================

    def mesh_equivalent(
        self,
    ) -> bool:
        """
        Distributed causality equivalence invariant.
        """

        if not self.mesh_nodes:
            return True

        closures = {
            node.closure_hash216()
            for node in (
                self.mesh_nodes.values()
            )
        }

        return len(closures) == 1

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global distributed mesh closure.
        """

        payload = {
            "nodes": sorted(
                [
                    node.closure_hash216()
                    for node in (
                        self.mesh_nodes.values()
                    )
                ]
            ),
            "identity": (
                self.identity_mesh_field
            ),
            "replay": (
                self.replay_mesh_field
            ),
            "mutation": (
                self.mutation_mesh_field
            ),
            "topology": (
                self.topology_mesh_field
            ),
            "neighbors": {
                k: sorted(list(v))
                for k, v in (
                    self.mesh_neighbors.items()
                )
            },
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def reconstructible(
        self,
    ) -> bool:
        """
        Distributed reconstruction continuity invariant.
        """

        for node in (
            self.mesh_nodes.values()
        ):

            if not (
                node.verify_reconstructibility()
            ):
                return False

        return True

    # ========================================================
    # REVERSIBILITY
    # ========================================================

    def reversible(
        self,
    ) -> bool:
        """
        Reciprocal distributed traversal invariant.
        """

        for node in (
            self.mesh_nodes.values()
        ):

            if not (
                node.verify_reversibility()
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
        Distributed topology continuity invariant.
        """

        for node in (
            self.mesh_nodes.values()
        ):

            if not (
                node.verify_topology_equivalence()
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
        Canonical distributed mesh receipt.
        """

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "node_count": len(
                self.mesh_nodes
            ),
            "mesh_equivalent": (
                self.mesh_equivalent()
            ),
            "reconstructible": (
                self.reconstructible()
            ),
            "reversible": (
                self.reversible()
            ),
            "topology_equivalent": (
                self.topology_equivalent()
            ),
            "valid": (
                self.validate_mesh()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }