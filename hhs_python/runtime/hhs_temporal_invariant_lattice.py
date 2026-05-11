# hhs_python/runtime/hhs_temporal_invariant_lattice.py
#
# HHS / HARMONICODE
# Temporal Invariant Lattice
#
# Canonical Runtime OS Temporal Geometry Layer
#
# Runtime Principle:
#
#   time
#   =
#   reconstructible invariant causality geometry
#
# NOT:
#
#   ordered execution sequence
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward temporal traversal
#   v^72 = reciprocal temporal reconstruction
#   C^216 = temporally invariant causal closure
#
# Runtime Primitive:
#
#   temporally invariant causal topology equivalence
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
# TEMPORAL WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSTemporalWitness:
    """
    Canonical temporal continuity witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    temporally_equivalent: bool = True
    causally_equivalent: bool = True
    reconstructible: bool = True
    reversible: bool = True
    topology_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.temporally_equivalent
            and self.causally_equivalent
            and self.reconstructible
            and self.reversible
            and self.topology_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# TEMPORAL PROJECTION
# ============================================================

@dataclass(frozen=True)
class HHSTemporalProjection:
    """
    Canonical temporal manifold carrier.

    Time is:
        reconstructible invariant causality geometry.
    """

    projection_id: str

    # ========================================================
    # MANIFOLD FIELDS
    # ========================================================

    causal_hash216: str
    replay_hash216: str
    identity_hash216: str
    semantic_hash216: str
    topology_hash216: str
    distributed_hash216: str

    # ========================================================
    # TEMPORAL TRAVERSAL
    # ========================================================

    forward_temporal_hash216: str
    reciprocal_temporal_hash216: str

    # ========================================================
    # TEMPORAL LATTICE
    # ========================================================

    temporal_lattice_hash216: str

    # ========================================================
    # FLAGS
    # ========================================================

    temporally_equivalent: bool = True
    causally_equivalent: bool = True
    reconstructible: bool = True
    reversible: bool = True
    topology_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    causal_witness: Optional[
        HHSTemporalWitness
    ] = None

    replay_witness: Optional[
        HHSTemporalWitness
    ] = None

    semantic_witness: Optional[
        HHSTemporalWitness
    ] = None

    topology_witness: Optional[
        HHSTemporalWitness
    ] = None

    reciprocal_witness: Optional[
        HHSTemporalWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    temporal_proof_hash216: str = ""

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
        Universal temporal admissibility validation.
        """

        if not self.temporally_equivalent:
            return False

        if not self.causally_equivalent:
            return False

        if not self.reconstructible:
            return False

        if not self.reversible:
            return False

        if not self.topology_equivalent:
            return False

        witnesses = [
            self.causal_witness,
            self.replay_witness,
            self.semantic_witness,
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
        Canonical temporal closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "projection_id": self.projection_id,
            "causal": self.causal_hash216,
            "replay": self.replay_hash216,
            "identity": self.identity_hash216,
            "semantic": self.semantic_hash216,
            "topology": self.topology_hash216,
            "distributed": self.distributed_hash216,
            "forward": self.forward_temporal_hash216,
            "reciprocal": (
                self.reciprocal_temporal_hash216
            ),
            "lattice": (
                self.temporal_lattice_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # TEMPORAL EQUIVALENCE
    # ========================================================

    def verify_temporal_equivalence(
        self,
    ) -> bool:
        """
        Temporal manifold equivalence invariant.
        """

        return (
            self.temporally_equivalent
            and self.validate()
        )

    # ========================================================
    # CAUSAL EQUIVALENCE
    # ========================================================

    def verify_causal_equivalence(
        self,
    ) -> bool:
        """
        Causal topology continuity invariant.
        """

        return (
            self.causally_equivalent
            and self.validate()
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Temporal reconstruction invariant.
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
        Reciprocal temporal traversal invariant.
        """

        return (
            self.reversible
            and self.validate()
        )

    # ========================================================
    # TOPOLOGY EQUIVALENCE
    # ========================================================

    def verify_topology_equivalence(
        self,
    ) -> bool:
        """
        Temporal topology continuity invariant.
        """

        return (
            self.topology_equivalent
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
            "projection_id": self.projection_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "temporal_proof_hash216": (
                self.temporal_proof_hash216
            ),
            "temporally_equivalent": (
                self.verify_temporal_equivalence()
            ),
            "causally_equivalent": (
                self.verify_causal_equivalence()
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "reversible": (
                self.verify_reversibility()
            ),
            "topology_equivalent": (
                self.verify_topology_equivalence()
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
        Canonical temporal projection receipt.
        """

        return {
            "projection_id": self.projection_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "temporal_proof_hash216": (
                self.temporal_proof_hash216
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# TEMPORAL INVARIANT LATTICE
# ============================================================

class HHSTemporalInvariantLattice:
    """
    Canonical Runtime OS temporal geometry field.

    Time is:
        temporally invariant causal topology.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.temporal_registry: Dict[
            str,
            HHSTemporalProjection
        ] = {}

        self.temporal_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.temporal_dependencies: Dict[
            str,
            Set[str]
        ] = {}

        self.causal_field: Dict[
            str,
            str
        ] = {}

        self.replay_field: Dict[
            str,
            str
        ] = {}

        self.identity_field: Dict[
            str,
            str
        ] = {}

        self.semantic_field: Dict[
            str,
            str
        ] = {}

        self.topology_field: Dict[
            str,
            str
        ] = {}

        self.distributed_field: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER
    # ========================================================

    def register_projection(
        self,
        projection: HHSTemporalProjection,
    ) -> bool:
        """
        Register temporally invariant manifold projection.
        """

        if not projection.validate():
            return False

        self.temporal_registry[
            projection.projection_id
        ] = projection

        if (
            projection.projection_id
            not in self.temporal_lineage
        ):

            self.temporal_lineage[
                projection.projection_id
            ] = []

        self.temporal_lineage[
            projection.projection_id
        ].append(
            projection.closure_hash216()
        )

        self.causal_field[
            projection.projection_id
        ] = (
            projection.causal_hash216
        )

        self.replay_field[
            projection.projection_id
        ] = (
            projection.replay_hash216
        )

        self.identity_field[
            projection.projection_id
        ] = (
            projection.identity_hash216
        )

        self.semantic_field[
            projection.projection_id
        ] = (
            projection.semantic_hash216
        )

        self.topology_field[
            projection.projection_id
        ] = (
            projection.topology_hash216
        )

        self.distributed_field[
            projection.projection_id
        ] = (
            projection.distributed_hash216
        )

        if (
            projection.projection_id
            not in self.temporal_dependencies
        ):

            self.temporal_dependencies[
                projection.projection_id
            ] = set()

        return True

    # ========================================================
    # TEMPORAL DEPENDENCY
    # ========================================================

    def connect_temporal_dependency(
        self,
        source_projection: str,
        target_projection: str,
    ) -> bool:
        """
        Establish temporal causality relation.
        """

        if (
            source_projection
            not in self.temporal_registry
        ):
            return False

        if (
            target_projection
            not in self.temporal_registry
        ):
            return False

        self.temporal_dependencies[
            source_projection
        ].add(
            target_projection
        )

        return True

    # ========================================================
    # VALIDATE LATTICE
    # ========================================================

    def validate_lattice(
        self,
    ) -> bool:
        """
        Universal temporal admissibility validation.
        """

        for projection in (
            self.temporal_registry.values()
        ):

            if not projection.validate():
                return False

        return True

    # ========================================================
    # TEMPORAL EQUIVALENCE
    # ========================================================

    def temporally_equivalent(
        self,
    ) -> bool:
        """
        Global temporal topology equivalence.
        """

        for projection in (
            self.temporal_registry.values()
        ):

            if not (
                projection
                .verify_temporal_equivalence()
            ):
                return False

        return True

    # ========================================================
    # CAUSAL EQUIVALENCE
    # ========================================================

    def causally_equivalent(
        self,
    ) -> bool:
        """
        Global causal topology equivalence.
        """

        for projection in (
            self.temporal_registry.values()
        ):

            if not (
                projection
                .verify_causal_equivalence()
            ):
                return False

        return True

    # ========================================================
    # TEMPORAL CONE
    # ========================================================

    def temporal_cone(
        self,
        projection_id: str,
    ) -> Set[str]:
        """
        Compute full downstream temporal cone.
        """

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.temporal_dependencies.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(projection_id)

        return visited

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global temporal lattice closure.
        """

        payload = {
            "temporal_registry": sorted(
                [
                    projection.closure_hash216()
                    for projection in (
                        self.temporal_registry.values()
                    )
                ]
            ),
            "lineage": self.temporal_lineage,
            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.temporal_dependencies.items()
                )
            },
            "causal": self.causal_field,
            "replay": self.replay_field,
            "identity": self.identity_field,
            "semantic": self.semantic_field,
            "topology": self.topology_field,
            "distributed": (
                self.distributed_field
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical temporal lattice receipt.
        """

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "projection_count": len(
                self.temporal_registry
            ),
            "temporally_equivalent": (
                self.temporally_equivalent()
            ),
            "causally_equivalent": (
                self.causally_equivalent()
            ),
            "valid": (
                self.validate_lattice()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }