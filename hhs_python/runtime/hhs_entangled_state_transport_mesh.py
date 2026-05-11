# hhs_python/runtime/hhs_entangled_state_transport_mesh.py
#
# HHS / HARMONICODE
# Entangled State Transport Mesh
#
# Canonical Runtime OS Distributed Manifold Transport Substrate
#
# Runtime Principle:
#
#   transport
#   =
#   reciprocal distributed topology entanglement
#
# NOT:
#
#   replicated distributed state
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward transport traversal
#   v^72 = reciprocal transport reconstruction
#   C^216 = distributed entangled transport closure
#
# Runtime Primitive:
#
#   distributed reciprocal manifold entanglement
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
# TRANSPORT WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSTransportWitness:
    """
    Canonical distributed transport witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    transportable: bool = True
    reconstructible: bool = True
    phase_entangled: bool = True
    origin_equivalent: bool = True
    temporally_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.transportable
            and self.reconstructible
            and self.phase_entangled
            and self.origin_equivalent
            and self.temporally_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# ENTANGLED TRANSPORT STATE
# ============================================================

@dataclass(frozen=True)
class HHSEntangledTransportState:
    """
    Canonical distributed manifold transport carrier.

    Transport is:
        reciprocal distributed topology entanglement.
    """

    transport_id: str

    # ========================================================
    # REGION FIELDS
    # ========================================================

    origin_hash216: str
    source_region_hash216: str
    target_region_hash216: str

    identity_hash216: str
    replay_hash216: str
    semantic_hash216: str
    causal_hash216: str
    temporal_hash216: str
    consensus_hash216: str
    multimodal_hash216: str
    governance_hash216: str

    # ========================================================
    # TRANSPORT TRAVERSAL
    # ========================================================

    forward_transport_hash216: str
    reciprocal_transport_hash216: str

    # ========================================================
    # TRANSPORT TOPOLOGY
    # ========================================================

    transport_topology_hash216: str

    # ========================================================
    # FLAGS
    # ========================================================

    transportable: bool = True
    reconstructible: bool = True
    phase_entangled: bool = True
    origin_equivalent: bool = True
    temporally_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    source_witness: Optional[
        HHSTransportWitness
    ] = None

    target_witness: Optional[
        HHSTransportWitness
    ] = None

    replay_witness: Optional[
        HHSTransportWitness
    ] = None

    governance_witness: Optional[
        HHSTransportWitness
    ] = None

    reciprocal_witness: Optional[
        HHSTransportWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    transport_proof_hash216: str = ""

    # ========================================================
    # TIME
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
        Universal distributed transport validation.
        """

        if not self.transportable:
            return False

        if not self.reconstructible:
            return False

        if not self.phase_entangled:
            return False

        if not self.origin_equivalent:
            return False

        if not self.temporally_equivalent:
            return False

        witnesses = [
            self.source_witness,
            self.target_witness,
            self.replay_witness,
            self.governance_witness,
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
        Canonical transport closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "transport_id": self.transport_id,
            "origin": self.origin_hash216,
            "source_region": (
                self.source_region_hash216
            ),
            "target_region": (
                self.target_region_hash216
            ),
            "identity": self.identity_hash216,
            "replay": self.replay_hash216,
            "semantic": self.semantic_hash216,
            "causal": self.causal_hash216,
            "temporal": self.temporal_hash216,
            "consensus": self.consensus_hash216,
            "multimodal": self.multimodal_hash216,
            "governance": self.governance_hash216,
            "forward": (
                self.forward_transport_hash216
            ),
            "reciprocal": (
                self.reciprocal_transport_hash216
            ),
            "topology": (
                self.transport_topology_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # TRANSPORTABLE
    # ========================================================

    def verify_transportable(
        self,
    ) -> bool:
        """
        Distributed transport admissibility invariant.
        """

        return (
            self.transportable
            and self.validate()
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
    # PHASE ENTANGLEMENT
    # ========================================================

    def verify_phase_entanglement(
        self,
    ) -> bool:
        """
        Reciprocal topology entanglement invariant.
        """

        return (
            self.phase_entangled
            and self.validate()
        )

    # ========================================================
    # ORIGIN EQUIVALENCE
    # ========================================================

    def verify_origin_equivalence(
        self,
    ) -> bool:
        """
        Distributed origin continuity invariant.
        """

        return (
            self.origin_equivalent
            and self.validate()
        )

    # ========================================================
    # TEMPORAL EQUIVALENCE
    # ========================================================

    def verify_temporal_equivalence(
        self,
    ) -> bool:
        """
        Distributed temporal continuity invariant.
        """

        return (
            self.temporally_equivalent
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
            "transport_id": self.transport_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "transport_proof_hash216": (
                self.transport_proof_hash216
            ),
            "transportable": (
                self.verify_transportable()
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "phase_entangled": (
                self.verify_phase_entanglement()
            ),
            "origin_equivalent": (
                self.verify_origin_equivalence()
            ),
            "temporally_equivalent": (
                self.verify_temporal_equivalence()
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
        Canonical entangled transport receipt.
        """

        return {
            "transport_id": self.transport_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "transport_proof_hash216": (
                self.transport_proof_hash216
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# ENTANGLED STATE TRANSPORT MESH
# ============================================================

class HHSEntangledStateTransportMesh:
    """
    Canonical Runtime OS distributed transport substrate.

    Transport is:
        reciprocal distributed topology entanglement.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.transport_registry: Dict[
            str,
            HHSEntangledTransportState
        ] = {}

        self.transport_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.transport_dependencies: Dict[
            str,
            Set[str]
        ] = {}

        self.origin_field: Dict[
            str,
            str
        ] = {}

        self.source_region_field: Dict[
            str,
            str
        ] = {}

        self.target_region_field: Dict[
            str,
            str
        ] = {}

        self.identity_field: Dict[
            str,
            str
        ] = {}

        self.replay_field: Dict[
            str,
            str
        ] = {}

        self.semantic_field: Dict[
            str,
            str
        ] = {}

        self.causal_field: Dict[
            str,
            str
        ] = {}

        self.temporal_field: Dict[
            str,
            str
        ] = {}

        self.consensus_field: Dict[
            str,
            str
        ] = {}

        self.multimodal_field: Dict[
            str,
            str
        ] = {}

        self.governance_field: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER TRANSPORT
    # ========================================================

    def register_transport(
        self,
        transport: HHSEntangledTransportState,
    ) -> bool:
        """
        Register distributed entangled transport.
        """

        if not transport.validate():
            return False

        self.transport_registry[
            transport.transport_id
        ] = transport

        if (
            transport.transport_id
            not in self.transport_lineage
        ):

            self.transport_lineage[
                transport.transport_id
            ] = []

        self.transport_lineage[
            transport.transport_id
        ].append(
            transport.closure_hash216()
        )

        self.origin_field[
            transport.transport_id
        ] = (
            transport.origin_hash216
        )

        self.source_region_field[
            transport.transport_id
        ] = (
            transport.source_region_hash216
        )

        self.target_region_field[
            transport.transport_id
        ] = (
            transport.target_region_hash216
        )

        self.identity_field[
            transport.transport_id
        ] = (
            transport.identity_hash216
        )

        self.replay_field[
            transport.transport_id
        ] = (
            transport.replay_hash216
        )

        self.semantic_field[
            transport.transport_id
        ] = (
            transport.semantic_hash216
        )

        self.causal_field[
            transport.transport_id
        ] = (
            transport.causal_hash216
        )

        self.temporal_field[
            transport.transport_id
        ] = (
            transport.temporal_hash216
        )

        self.consensus_field[
            transport.transport_id
        ] = (
            transport.consensus_hash216
        )

        self.multimodal_field[
            transport.transport_id
        ] = (
            transport.multimodal_hash216
        )

        self.governance_field[
            transport.transport_id
        ] = (
            transport.governance_hash216
        )

        if (
            transport.transport_id
            not in self.transport_dependencies
        ):

            self.transport_dependencies[
                transport.transport_id
            ] = set()

        return True

    # ========================================================
    # TRANSPORT DEPENDENCY
    # ========================================================

    def connect_transport_dependency(
        self,
        source_transport: str,
        target_transport: str,
    ) -> bool:
        """
        Establish distributed transport dependency.
        """

        if (
            source_transport
            not in self.transport_registry
        ):
            return False

        if (
            target_transport
            not in self.transport_registry
        ):
            return False

        self.transport_dependencies[
            source_transport
        ].add(
            target_transport
        )

        return True

    # ========================================================
    # VALIDATE MESH
    # ========================================================

    def validate_mesh(
        self,
    ) -> bool:
        """
        Universal distributed transport validation.
        """

        for transport in (
            self.transport_registry.values()
        ):

            if not transport.validate():
                return False

        return True

    # ========================================================
    # PHASE ENTANGLED
    # ========================================================

    def phase_entangled(
        self,
    ) -> bool:
        """
        Global reciprocal transport continuity.
        """

        for transport in (
            self.transport_registry.values()
        ):

            if not (
                transport.verify_phase_entanglement()
            ):
                return False

        return True

    # ========================================================
    # TRANSPORT CONE
    # ========================================================

    def transport_cone(
        self,
        transport_id: str,
    ) -> Set[str]:
        """
        Compute distributed transport dependency cone.
        """

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.transport_dependencies.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(transport_id)

        return visited

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global transport mesh closure.
        """

        payload = {
            "transport_registry": sorted(
                [
                    transport.closure_hash216()
                    for transport in (
                        self.transport_registry.values()
                    )
                ]
            ),
            "lineage": self.transport_lineage,
            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.transport_dependencies.items()
                )
            },
            "origin": self.origin_field,
            "source_region": (
                self.source_region_field
            ),
            "target_region": (
                self.target_region_field
            ),
            "identity": self.identity_field,
            "replay": self.replay_field,
            "semantic": self.semantic_field,
            "causal": self.causal_field,
            "temporal": self.temporal_field,
            "consensus": self.consensus_field,
            "multimodal": self.multimodal_field,
            "governance": self.governance_field,
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # AUTHORITATIVE TRANSPORT
    # ========================================================

    def authoritative_transport(
        self,
    ) -> Optional[
        HHSEntangledTransportState
    ]:
        """
        Determine transport closest
        to reciprocal distributed closure.
        """

        if not self.transport_registry:
            return None

        ordered = sorted(
            self.transport_registry.values(),
            key=lambda t: (
                t.closure_hash216(),
                t.transport_topology_hash216,
            ),
        )

        return ordered[0]

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical entangled transport mesh receipt.
        """

        authoritative = (
            self.authoritative_transport()
        )

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "transport_count": len(
                self.transport_registry
            ),
            "dependency_count": sum(
                len(v)
                for v in (
                    self.transport_dependencies.values()
                )
            ),
            "phase_entangled": (
                self.phase_entangled()
            ),
            "authoritative_transport": (
                authoritative.transport_id
                if authoritative
                else None
            ),
            "valid": (
                self.validate_mesh()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }