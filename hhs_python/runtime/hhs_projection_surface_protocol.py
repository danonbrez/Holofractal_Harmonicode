# hhs_python/runtime/hhs_projection_surface_protocol.py
#
# HHS / HARMONICODE
# Projection Surface Protocol
#
# Canonical Runtime OS Manifold-Interface Boundary Layer
#
# Runtime Principle:
#
#   GUI / application state
#   =
#   reconstructible manifold projection
#
# NOT:
#
#   authoritative runtime state
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward projection traversal
#   v^72 = reciprocal projection reconstruction
#   C^216 = projection-manifold closure equivalence
#
# Runtime Primitive:
#
#   reconstructible external manifold projection continuity
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
# SURFACE WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSProjectionWitness:
    """
    Canonical manifold-interface witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    projectable: bool = True
    reconstructible: bool = True
    semantically_equivalent: bool = True
    causally_equivalent: bool = True
    temporally_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.projectable
            and self.reconstructible
            and self.semantically_equivalent
            and self.causally_equivalent
            and self.temporally_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# PROJECTION SURFACE
# ============================================================

@dataclass(frozen=True)
class HHSProjectionSurface:
    """
    Canonical GUI/application manifold carrier.

    GUI state is:
        reconstructible manifold projection.
    """

    surface_id: str

    # ========================================================
    # MANIFOLD FIELDS
    # ========================================================

    projection_hash216: str
    semantic_hash216: str
    causal_hash216: str
    temporal_hash216: str
    identity_hash216: str
    consensus_hash216: str

    # ========================================================
    # PROJECTION TRAVERSAL
    # ========================================================

    forward_projection_hash216: str
    reciprocal_projection_hash216: str

    # ========================================================
    # SURFACE TOPOLOGY
    # ========================================================

    surface_topology_hash216: str

    # ========================================================
    # FLAGS
    # ========================================================

    projectable: bool = True
    reconstructible: bool = True
    semantically_equivalent: bool = True
    causally_equivalent: bool = True
    temporally_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    semantic_witness: Optional[
        HHSProjectionWitness
    ] = None

    causal_witness: Optional[
        HHSProjectionWitness
    ] = None

    temporal_witness: Optional[
        HHSProjectionWitness
    ] = None

    identity_witness: Optional[
        HHSProjectionWitness
    ] = None

    reciprocal_witness: Optional[
        HHSProjectionWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    surface_proof_hash216: str = ""

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
        Universal projection admissibility validation.
        """

        if not self.projectable:
            return False

        if not self.reconstructible:
            return False

        if not self.semantically_equivalent:
            return False

        if not self.causally_equivalent:
            return False

        if not self.temporally_equivalent:
            return False

        witnesses = [
            self.semantic_witness,
            self.causal_witness,
            self.temporal_witness,
            self.identity_witness,
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
        Canonical projection closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "surface_id": self.surface_id,
            "projection": self.projection_hash216,
            "semantic": self.semantic_hash216,
            "causal": self.causal_hash216,
            "temporal": self.temporal_hash216,
            "identity": self.identity_hash216,
            "consensus": self.consensus_hash216,
            "forward": (
                self.forward_projection_hash216
            ),
            "reciprocal": (
                self.reciprocal_projection_hash216
            ),
            "topology": (
                self.surface_topology_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # PROJECTABILITY
    # ========================================================

    def verify_projectability(
        self,
    ) -> bool:
        """
        Projection-manifold admissibility invariant.
        """

        return (
            self.projectable
            and self.validate()
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Surface reconstruction invariant.
        """

        return (
            self.reconstructible
            and self.validate()
        )

    # ========================================================
    # SEMANTIC EQUIVALENCE
    # ========================================================

    def verify_semantic_equivalence(
        self,
    ) -> bool:
        """
        Semantic projection continuity invariant.
        """

        return (
            self.semantically_equivalent
            and self.validate()
        )

    # ========================================================
    # CAUSAL EQUIVALENCE
    # ========================================================

    def verify_causal_equivalence(
        self,
    ) -> bool:
        """
        Causal projection continuity invariant.
        """

        return (
            self.causally_equivalent
            and self.validate()
        )

    # ========================================================
    # TEMPORAL EQUIVALENCE
    # ========================================================

    def verify_temporal_equivalence(
        self,
    ) -> bool:
        """
        Temporal projection continuity invariant.
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
            "surface_id": self.surface_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "surface_proof_hash216": (
                self.surface_proof_hash216
            ),
            "projectable": (
                self.verify_projectability()
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "semantically_equivalent": (
                self.verify_semantic_equivalence()
            ),
            "causally_equivalent": (
                self.verify_causal_equivalence()
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
        Canonical projection surface receipt.
        """

        return {
            "surface_id": self.surface_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "surface_proof_hash216": (
                self.surface_proof_hash216
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# PROJECTION SURFACE PROTOCOL
# ============================================================

class HHSProjectionSurfaceProtocol:
    """
    Canonical Runtime OS manifold-interface boundary layer.

    All external interfaces are:
        temporary manifold projections.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.surface_registry: Dict[
            str,
            HHSProjectionSurface
        ] = {}

        self.surface_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.surface_dependencies: Dict[
            str,
            Set[str]
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

        self.identity_field: Dict[
            str,
            str
        ] = {}

        self.consensus_field: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER SURFACE
    # ========================================================

    def register_surface(
        self,
        surface: HHSProjectionSurface,
    ) -> bool:
        """
        Register projection-safe interface surface.
        """

        if not surface.validate():
            return False

        self.surface_registry[
            surface.surface_id
        ] = surface

        if (
            surface.surface_id
            not in self.surface_lineage
        ):

            self.surface_lineage[
                surface.surface_id
            ] = []

        self.surface_lineage[
            surface.surface_id
        ].append(
            surface.closure_hash216()
        )

        self.semantic_field[
            surface.surface_id
        ] = (
            surface.semantic_hash216
        )

        self.causal_field[
            surface.surface_id
        ] = (
            surface.causal_hash216
        )

        self.temporal_field[
            surface.surface_id
        ] = (
            surface.temporal_hash216
        )

        self.identity_field[
            surface.surface_id
        ] = (
            surface.identity_hash216
        )

        self.consensus_field[
            surface.surface_id
        ] = (
            surface.consensus_hash216
        )

        if (
            surface.surface_id
            not in self.surface_dependencies
        ):

            self.surface_dependencies[
                surface.surface_id
            ] = set()

        return True

    # ========================================================
    # SURFACE DEPENDENCY
    # ========================================================

    def connect_surface_dependency(
        self,
        source_surface: str,
        target_surface: str,
    ) -> bool:
        """
        Establish projection dependency relation.
        """

        if (
            source_surface
            not in self.surface_registry
        ):
            return False

        if (
            target_surface
            not in self.surface_registry
        ):
            return False

        self.surface_dependencies[
            source_surface
        ].add(
            target_surface
        )

        return True

    # ========================================================
    # VALIDATE PROTOCOL
    # ========================================================

    def validate_protocol(
        self,
    ) -> bool:
        """
        Universal projection-surface validation.
        """

        for surface in (
            self.surface_registry.values()
        ):

            if not surface.validate():
                return False

        return True

    # ========================================================
    # PROJECTABLE
    # ========================================================

    def projectable(
        self,
    ) -> bool:
        """
        Global projection-manifold admissibility.
        """

        for surface in (
            self.surface_registry.values()
        ):

            if not (
                surface.verify_projectability()
            ):
                return False

        return True

    # ========================================================
    # SURFACE CONE
    # ========================================================

    def surface_cone(
        self,
        surface_id: str,
    ) -> Set[str]:
        """
        Compute full downstream projection cone.
        """

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.surface_dependencies.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(surface_id)

        return visited

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global projection protocol closure.
        """

        payload = {
            "surface_registry": sorted(
                [
                    surface.closure_hash216()
                    for surface in (
                        self.surface_registry.values()
                    )
                ]
            ),
            "lineage": self.surface_lineage,
            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.surface_dependencies.items()
                )
            },
            "semantic": self.semantic_field,
            "causal": self.causal_field,
            "temporal": self.temporal_field,
            "identity": self.identity_field,
            "consensus": self.consensus_field,
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # AUTHORITATIVE SURFACE
    # ========================================================

    def authoritative_surface(
        self,
    ) -> Optional[
        HHSProjectionSurface
    ]:
        """
        Determine projection surface closest
        to manifold closure equivalence.
        """

        if not self.surface_registry:
            return None

        ordered = sorted(
            self.surface_registry.values(),
            key=lambda s: (
                s.closure_hash216(),
                s.surface_topology_hash216,
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
        Canonical projection surface protocol receipt.
        """

        authoritative = (
            self.authoritative_surface()
        )

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "surface_count": len(
                self.surface_registry
            ),
            "dependency_count": sum(
                len(v)
                for v in (
                    self.surface_dependencies.values()
                )
            ),
            "projectable": (
                self.projectable()
            ),
            "authoritative_surface": (
                authoritative.surface_id
                if authoritative
                else None
            ),
            "valid": (
                self.validate_protocol()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }